// Daily Intelligence Dashboard — the on-demand "daily pull".
//
// Affiliate mode (default): intelligence comes from the affiliate
// marketplace feed (commission rates, point-in-time sold counts), the
// creator's showcase, and the creator's own affiliate orders. Momentum is
// derived by diffing today's sold counts against the previous stored
// snapshot — the first pull establishes a baseline and says so.
//
// Seller mode: shop analytics endpoints provide windowed product/video
// performance directly.
//
// Every section either carries sourced numbers or an explicit gap entry
// saying exactly which pull failed or which metric the API does not expose.

import {
  dateWindows,
  rankByMomentum,
  rankByMomentumSnapshots,
  findBreakouts,
  engagementToConversion,
} from './metrics.js';
import { categorySensitivity } from './compliance.js';
import { appendState, readState } from './store.js';

export async function dailyPull(client, now = new Date()) {
  const gate = client.credentialGap();
  if (gate) {
    return {
      generated_at: now.toISOString(),
      mode: client.cfg.role,
      status: 'NO_DATA',
      gaps: [{ what: 'entire daily pull', why: gate.detail, missing: gate.missing }],
      sections: null,
    };
  }
  return client.cfg.role === 'affiliate' ? affiliatePull(client, now) : sellerPull(client, now);
}

async function affiliatePull(client, now) {
  const w = dateWindows(now);
  const toEpoch = (d) => Math.floor(Date.parse(d) / 1000);

  const [marketplace, showcase, orders30] = await Promise.all([
    client.marketplaceProducts({}),
    client.showcaseProducts({}),
    client.affiliateOrders({ createTimeGe: toEpoch(w.last30d.start), createTimeLt: toEpoch(w.today) + 86400 }),
  ]);

  // Previous affiliate snapshot for the sold-count diff.
  const prevSnap = [...readState('pulls', [])]
    .reverse()
    .find((p) => p.mode === 'affiliate' && p.snapshot_products?.length);

  const momentum = rankByMomentumSnapshots(
    marketplace,
    prevSnap ? { pulled_at: prevSnap.generated_at, products: prevSnap.snapshot_products } : null,
    10,
  );

  // Breakouts: new-to-feed products already selling, or velocity spikes,
  // measured across snapshots taken ≤48h apart.
  const breakouts = (momentum.all || momentum.baseline || [])
    .filter((p) => p.breakout || ((p.velocity ?? 0) >= 0.5 && (p.hours_between_snapshots ?? 999) <= 48))
    .slice(0, 10);

  const gaps = [...momentum.gaps];
  if (!showcase.ok) gaps.push({ what: 'showcase products', why: showcase.detail, endpoint: showcase.endpoint });
  if (!orders30.ok) gaps.push({ what: 'affiliate orders / commission (30d)', why: orders30.detail, endpoint: orders30.endpoint });
  gaps.push({
    what: 'engagement → conversion by category',
    why: 'Per-video CTR/conversion is not exposed to affiliate-creator API credentials (it is a seller analytics scope). ' +
      'Your own video engagement can be logged from the TikTok app analytics screen via `intel observe` to fill this section manually.',
    structural: true,
  });

  const surfaced = [...momentum.ranked, ...breakouts];
  const seen = new Map();
  for (const p of surfaced) if (!seen.has(p.product_id)) seen.set(p.product_id, p);
  const complianceFlags = [...seen.values()]
    .map((p) => ({ product_id: p.product_id, name: p.name, ...categorySensitivity(p.category || p.name) }))
    .filter((f) => f.level !== 'LOW');

  const commission = summarizeOrders(orders30);

  const snapshot = {
    generated_at: now.toISOString(),
    mode: 'affiliate',
    status: gaps.some((g) => !g.structural && g.what !== 'momentum baseline') ? 'PARTIAL' : 'OK',
    windows: w,
    sections: {
      top10_momentum: momentum.ranked,
      breakout_skus_48h: breakouts,
      commission_30d: commission,
      showcase: showcase.ok
        ? { count: (showcase.data?.products || []).length, source: { endpoint: showcase.endpoint, pulled_at: showcase.pulled_at } }
        : null,
      compliance_flags: complianceFlags,
    },
    // Full sold-count snapshot persisted for the next pull's diff.
    snapshot_products: momentum.all || momentum.baseline || [],
    gaps,
  };
  appendState('pulls', snapshot);
  return snapshot;
}

function summarizeOrders(pull) {
  if (!pull.ok) return null;
  const orders = pull.data?.orders || [];
  let gmv = 0;
  let commission = 0;
  let units = 0;
  for (const o of orders) {
    gmv += Number(o.pay_amount?.amount ?? o.order_amount ?? 0);
    commission += Number(o.estimated_commission?.amount ?? o.commission_amount ?? 0);
    units += Number(o.quantity ?? 1);
  }
  return {
    orders: orders.length,
    units,
    gmv,
    estimated_commission: commission,
    source: { endpoint: pull.endpoint, pulled_at: pull.pulled_at },
  };
}

async function sellerPull(client, now) {
  const w = dateWindows(now);
  const [recent7, prior7, recent48, videos30] = await Promise.all([
    client.productPerformanceList({ startDateGe: w.last7d.start, endDateLt: w.last7d.end }),
    client.productPerformanceList({ startDateGe: w.prior7d.start, endDateLt: w.prior7d.end }),
    client.productPerformanceList({ startDateGe: w.last48h.start, endDateLt: w.last48h.end }),
    client.videoList({ startDateGe: w.last30d.start, endDateLt: w.last30d.end }),
  ]);

  const momentum = rankByMomentum(recent7, prior7, 10);
  const breakouts = findBreakouts(recent48);
  const e2c = engagementToConversion(videos30);

  const seen = new Map();
  for (const p of [...momentum.ranked, ...breakouts.breakouts]) {
    if (!seen.has(p.product_id)) seen.set(p.product_id, p);
  }
  const complianceFlags = [...seen.values()]
    .map((p) => ({ product_id: p.product_id, name: p.name, ...categorySensitivity(p.category || p.name) }))
    .filter((f) => f.level !== 'LOW');

  const snapshot = {
    generated_at: now.toISOString(),
    mode: 'seller',
    status: momentum.gaps.length || breakouts.gaps.length || e2c.gaps.length ? 'PARTIAL' : 'OK',
    windows: w,
    sections: {
      top10_momentum: momentum.ranked,
      breakout_skus_48h: breakouts.breakouts.slice(0, 10),
      engagement_to_conversion: e2c.byCategory,
      compliance_flags: complianceFlags,
    },
    gaps: [...momentum.gaps, ...breakouts.gaps, ...e2c.gaps],
  };
  appendState('pulls', snapshot);
  return snapshot;
}

export function renderDashboard(snap) {
  const L = [];
  L.push(`# Daily Intelligence Dashboard — ${snap.generated_at} (${snap.mode} mode)`);
  L.push(`Status: ${snap.status}`);

  if (snap.gaps?.length) {
    L.push('', '## Data gaps (no substitutes provided)');
    for (const g of snap.gaps) L.push(`- ${g.what}: ${g.why}${g.endpoint ? ` [${g.endpoint}]` : ''}`);
  }
  if (!snap.sections) return L.join('\n');
  const s = snap.sections;

  L.push('', '## Top 10 by momentum');
  if (!s.top10_momentum.length) L.push('- no rankable products (see gaps — first pull establishes the baseline)');
  for (const p of s.top10_momentum) {
    const v = p.velocity != null ? `${(p.velocity * 100).toFixed(1)}%` : `n/a (${p.velocity_note ?? 'no baseline'})`;
    const extra = p.commission_rate != null ? `, commission ${p.commission_rate}%` : '';
    const units = p.units_delta != null ? `${p.units_delta} units since last snapshot` : `${p.units_recent ?? p.units_sold_total ?? '?'} units`;
    L.push(`- ${p.name ?? p.product_id}: velocity ${v}, ${units}${extra}`);
  }

  L.push('', '## Breakout SKUs (last 48h)');
  if (!s.breakout_skus_48h.length) L.push('- none detected');
  for (const p of s.breakout_skus_48h) {
    L.push(`- ${p.name ?? p.product_id}: ${p.units_48h ?? p.units_delta ?? p.units_sold_total ?? '?'} units${p.commission_rate != null ? `, commission ${p.commission_rate}%` : ''}`);
  }

  if (s.commission_30d) {
    L.push('', '## Your affiliate performance (30d)');
    L.push(`- ${s.commission_30d.orders} orders, ${s.commission_30d.units} units, GMV ${s.commission_30d.gmv.toLocaleString()}, est. commission ${s.commission_30d.estimated_commission.toLocaleString()}`);
    L.push(`  (source: ${s.commission_30d.source.endpoint} @ ${s.commission_30d.source.pulled_at})`);
  }

  if (s.engagement_to_conversion) {
    L.push('', '## Engagement → conversion by category (30d video attribution)');
    if (!s.engagement_to_conversion.length) L.push('- no attributed video data in window');
    for (const c of s.engagement_to_conversion) {
      L.push(`- ${c.category}: CTR ${pct(c.ctr)}, conversion ${pct(c.conversion)} (${c.videos} videos, ${c.orders} orders)`);
    }
  }

  L.push('', '## Compliance flags');
  if (!s.compliance_flags.length) L.push("- no elevated-sensitivity products in today's surface");
  for (const f of s.compliance_flags) {
    L.push(`- ${f.name ?? f.product_id} [${f.level}]: ${f.why}`);
  }
  return L.join('\n');
}

function pct(x) {
  return x == null ? 'n/a' : `${(x * 100).toFixed(2)}%`;
}
