// Script Generation Engine.
//
// Pipeline for a product input:
//   1. Pull live metrics for the product (7d + 30d performance, video
//      attribution). If the product has no data above significance
//      thresholds, STOP and surface the nearest trending alternative —
//      never write a script on empty numbers.
//   2. Load category pattern weights + compliance incident suppressions.
//   3. Assemble a SCRIPT BRIEF: verified data points (each with source),
//      the weighted hook/proof/CTA selections, and hard language
//      constraints.
//   4. Generate prose: via the Claude API when ANTHROPIC_API_KEY is set,
//      otherwise emit the brief for the operating agent to voice.
//   5. Lint the result. HIGH flags or incident-phrase hits fail the
//      generation — the engine rewrites or returns the brief with the
//      failure attached. It never ships a flagged script silently.

import { dateWindows, significanceCheck } from './metrics.js';
import { getWeights, topHook, topProof } from './patterns.js';
import { lintScript, COMPLIANT_CTAS, categorySensitivity } from './compliance.js';
import { checkAgainstIncidents } from './competitive.js';
import { appendState } from './store.js';

export async function generateScript(client, cfg, { product, category }) {
  const w = dateWindows();

  // ---- 1. Live data or nothing ----
  const gate = client.credentialGap();
  if (gate) {
    return fail('DATA_UNAVAILABLE', gate.detail, { product, category });
  }

  const affiliate = client.cfg.role === 'affiliate';

  let p; // product record with live metrics
  let attributed = []; // seller mode only: attributed videos
  let sourcePull;

  if (affiliate) {
    const feed = await client.marketplaceProducts({ keyword: product });
    if (!feed.ok) return fail('PRODUCT_DATA_UNAVAILABLE', `Marketplace pull failed for "${product}": ${feed.detail}`, { product, category });
    const products = feed.data?.products || [];
    p = products.find((x) => matches(x, product));
    if (!p) {
      const alt = products[0] || (await bestAlternative(client));
      return fail(
        'PRODUCT_DATA_UNAVAILABLE',
        `No marketplace listing matching "${product}". ` +
          (alt
            ? `Closest trending alternative with real data: "${alt.title || alt.name}" (${alt.units_sold ?? alt.sold_count} sold, ${alt.commission_rate}% commission). Re-run with that product to script it.`
            : 'No alternative could be surfaced either — the marketplace feed returned nothing.'),
        { product, category },
      );
    }
    sourcePull = feed;
    const sold = Number(p.units_sold ?? p.sold_count ?? 0);
    if (sold < 100) {
      const alt =
        products.find((x) => x !== p && Number(x.units_sold ?? x.sold_count ?? 0) >= 100) ||
        (await bestAlternative(client));
      return fail(
        'BELOW_SIGNIFICANCE',
        `"${product}" is listed but has only ${sold} recorded sales — too thin to build a data-led script on. ` +
          (alt ? `Closest trending alternative above threshold: "${alt.title || alt.name}" (${alt.units_sold ?? alt.sold_count} sold).` : ''),
        { product, category },
      );
    }
  } else {
    const [recent7, videos30, list7] = await Promise.all([
      findProduct(client, product, w.last7d),
      client.videoList({ startDateGe: w.last30d.start, endDateLt: w.last30d.end }),
      client.productPerformanceList({ startDateGe: w.last7d.start, endDateLt: w.last7d.end }),
    ]);
    if (!recent7.ok) {
      const alt = list7.ok ? (list7.data?.products || [])[0] : null;
      return fail(
        'PRODUCT_DATA_UNAVAILABLE',
        `No live metrics found for "${product}": ${recent7.detail}. ` +
          (alt
            ? `Closest trending alternative with real data: "${alt.name}" (${alt.units_sold} units this week). Re-run with that product to script it.`
            : 'No alternative could be surfaced either — the product-performance pull failed.'),
        { product, category },
      );
    }
    p = recent7.product;
    sourcePull = recent7;
    attributed = videos30.ok
      ? (videos30.data?.videos || []).filter((v) => (v.products || []).some((pp) => matches(pp, product)))
      : [];
    const sig = significanceCheck({
      videos: attributed.length || 1,
      views: attributed.reduce((s, v) => s + (Number(v.views) || 0), 0) || Number(p.units_sold) * 100,
      orders: Number(p.units_sold) || 0,
    });
    if (!sig.significant) {
      const alt = list7.ok ? (list7.data?.products || []).find((x) => !matches(x, product)) : null;
      return fail(
        'BELOW_SIGNIFICANCE',
        `"${product}" has live data but below thresholds: ${sig.failures.join('; ')}. ` +
          (alt ? `Closest trending alternative above threshold: "${alt.name}" (${alt.units_sold} units/7d).` : ''),
        { product, category },
      );
    }
  }

  // ---- 2. Weights + suppressions ----
  const cat = category || p.category || 'general';
  const weights = getWeights(cat);
  const [hookType] = topHook(weights);
  const [proofType] = topProof(weights);
  const sens = categorySensitivity(cat);
  const cta = COMPLIANT_CTAS[Math.min(weights.cta_bias, COMPLIANT_CTAS.length - 1)];

  // ---- 3. Brief: every claim traces to a pull ----
  const dataPoints = affiliate
    ? [
        point(`${p.units_sold ?? p.sold_count} sold on TikTok Shop`, sourcePull),
        p.price != null ? point(`priced at ${fmtMoney(p.price?.amount ?? p.price, p.price?.currency)}`, sourcePull) : null,
        // Commission rate is creator-side intel: it informs product choice
        // and CTA energy but must never be spoken in the video.
        p.commission_rate != null ? { ...point(`commission: ${p.commission_rate}% (INTERNAL — never say on camera)`, sourcePull), internal: true } : null,
      ].filter(Boolean)
    : [
        point(`${p.units_sold} units sold in the last 7 days`, sourcePull),
        point(`${fmtMoney(p.gmv?.amount, p.gmv?.currency)} GMV in the last 7 days`, sourcePull),
        ...attributed.slice(0, 3).map((v) =>
          point(`an attributed video pulled ${v.views} views with ${v.units_sold ?? v.orders ?? '?'} orders`, sourcePull),
        ),
      ];

  const brief = {
    product: p.title || p.name,
    category: cat,
    data_points: dataPoints.filter((d) => d.claim && !d.claim.includes('null') && !d.claim.includes('undefined')),
    pattern: {
      hook_type: hookType,
      proof_type: proofType,
      cta,
      weights_updated_at: weights.updated_at,
    },
    constraints: {
      sensitivity: sens,
      suppressed_phrases: weights.suppressed_phrases.map((s) => s.phrase),
      style: [
        'talking-head/explainer only: no scenes, no B-roll callouts, no lifestyle narration',
        'hook in first 2-3 seconds built on one of the data_points above',
        'no "In today\'s video", no "Let\'s dive in", no lists read aloud',
        'vary sentence rhythm: short punches mixed with longer explanatory lines',
        'every numeric claim must come verbatim from non-internal data_points — no other numbers may appear',
        'data_points marked internal are for the creator only and must never appear in the script',
        'soft native-commerce CTA only',
        ...(affiliate
          ? ['affiliate disclosure required: the script must work with a visible "commission paid" / paid-partnership label — never deny or obscure the affiliate relationship']
          : []),
      ],
    },
  };

  // ---- 4/5. Prose + lint ----
  let script = null;
  let lintResult = null;
  if (cfg.anthropicApiKey) {
    script = await proseFromBrief(cfg, brief);
    const incidents = checkAgainstIncidents(script, cat);
    lintResult = incidents.lint;
    if (!lintResult.clean || incidents.incident_hits.length) {
      // One rewrite attempt with the violations spelled out, then hard fail.
      script = await proseFromBrief(cfg, brief, { violations: lintResult.flags, incident_hits: incidents.incident_hits });
      const recheck = checkAgainstIncidents(script, cat);
      lintResult = recheck.lint;
      if (!lintResult.clean || recheck.incident_hits.length) {
        return fail('COMPLIANCE_FAIL', 'Generated prose failed compliance lint twice; returning brief only.', { product, category: cat, brief, flags: lintResult.flags });
      }
    }
  }

  const result = {
    status: script ? 'SCRIPT_READY' : 'BRIEF_READY',
    generated_at: new Date().toISOString(),
    brief,
    script,
    lint: lintResult,
    note: script
      ? null
      : 'ANTHROPIC_API_KEY not set — brief emitted for the operating agent to voice. All numbers in data_points are live and sourced; use them verbatim.',
  };
  appendState('scripts', result, 200);
  return result;
}

// Affiliate fallback: top of the unfiltered marketplace feed.
async function bestAlternative(client) {
  const feed = await client.marketplaceProducts({});
  return feed.ok ? (feed.data?.products || [])[0] || null : null;
}

async function findProduct(client, needle, win) {
  const res = await client.productPerformanceList({ startDateGe: win.start, endDateLt: win.end });
  if (!res.ok) return res;
  const hit = (res.data?.products || []).find((p) => matches(p, needle));
  if (!hit) return { ok: false, endpoint: res.endpoint, error: 'NOT_FOUND', detail: `no product matching "${needle}" in performance window ${win.start}..${win.end}` };
  return { ...res, product: hit };
}

function matches(p, needle) {
  const n = String(needle).toLowerCase();
  return (
    String(p.id || p.product_id || '').toLowerCase() === n ||
    String(p.name || p.title || '').toLowerCase().includes(n) ||
    String(p.sku || '').toLowerCase() === n
  );
}

function point(claim, pull) {
  return { claim, source: { endpoint: pull.endpoint, pulled_at: pull.pulled_at } };
}

function fail(code, detail, extra = {}) {
  return { status: code, detail, ...extra, generated_at: new Date().toISOString() };
}

function fmtMoney(x, cur) {
  return x == null ? null : `${Number(x).toLocaleString()} ${cur || ''}`.trim();
}

// Claude API call for prose generation. Model: latest generally available.
async function proseFromBrief(cfg, brief, retryContext = null) {
  const sys =
    'You write TikTok Shop talking-head scripts. Voice: a real person who uses TikTok daily — direct, conversational, varied rhythm, zero AI cadence. ' +
    'Hard rules: use ONLY the numeric claims in data_points, verbatim; obey every entry in constraints; never use suppressed_phrases; ' +
    'hook in the first line from a data point; end with the given CTA phrased naturally. Output the script text only.';
  const user = retryContext
    ? `Rewrite — the previous draft violated compliance: ${JSON.stringify(retryContext)}.\nBrief:\n${JSON.stringify(brief, null, 2)}`
    : `Brief:\n${JSON.stringify(brief, null, 2)}`;

  const res = await fetch('https://api.anthropic.com/v1/messages', {
    method: 'POST',
    headers: {
      'content-type': 'application/json',
      'x-api-key': cfg.anthropicApiKey,
      'anthropic-version': '2023-06-01',
    },
    body: JSON.stringify({
      model: 'claude-sonnet-5',
      max_tokens: 1024,
      system: sys,
      messages: [{ role: 'user', content: user }],
    }),
  });
  const json = await res.json();
  if (!res.ok) throw new Error(`Claude API error: ${json.error?.message || res.status}`);
  return json.content.map((b) => b.text || '').join('');
}
