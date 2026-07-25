// Weekly / monthly competitive intelligence report.
// Assembled entirely from persisted state (pulls, competitive cycles,
// incidents, script history) — the report never invents a benchmark a
// pull didn't record.

import { readState } from './store.js';
import { getWeights } from './patterns.js';

export function buildReport({ cadence = 'weekly', category = null } = {}) {
  const days = cadence === 'monthly' ? 30 : 7;
  const since = new Date(Date.now() - days * 24 * 60 * 60 * 1000).toISOString();

  const cycles = readState('competitive', []).filter((c) => c.at >= since && (!category || c.category === category));
  const incidents = readState('incidents', []).filter((i) => i.at >= since && (!category || i.category === category));
  const scripts = readState('scripts', []).filter((s) => s.generated_at >= since);
  const pulls = readState('pulls', []).filter((p) => p.generated_at >= since);

  const observations = cycles.filter((c) => c.observation).map((c) => c.observation);
  const rankedObs = observations
    .filter((o) => o.views)
    .sort((a, b) => engRate(b) - engRate(a))
    .slice(0, 10);

  const L = [];
  L.push(`# Competitive Intelligence Report — ${cadence}, generated ${new Date().toISOString()}`);
  if (category) L.push(`Category scope: ${category}`);
  L.push('');

  L.push('## Competitive landscape');
  if (!rankedObs.length) {
    L.push(`- No measured competitor observations in the last ${days} days. ` +
      'Ranking requires logged observations with engagement data (intel observe). ' +
      'Per-video competitor conversion is not API-observable; engagement rate is the ranking basis.');
  } else {
    L.push(`Top observed competitor videos by engagement rate (${rankedObs.length} of ${observations.length} logged):`);
    for (const o of rankedObs) {
      L.push(`- ${o.video_url} [${o.category}] hook=${o.hook_type} proof=${o.proof_type} — ${o.views} views, eng-rate ${(engRate(o) * 100).toFixed(2)}%`);
    }
  }
  L.push('');

  L.push('## Compliance incident log');
  if (!incidents.length) L.push('- no incidents recorded this cycle');
  for (const i of incidents) {
    L.push(`- ${i.at} ${i.video_url} → ${i.status}${i.trigger_phrase ? ` (trigger: "${i.trigger_phrase}" — now suppressed in generation)` : ' (trigger unknown)'}`);
  }
  L.push('');

  L.push('## Your scripts this cycle');
  const shipped = scripts.filter((s) => s.status === 'SCRIPT_READY' || s.status === 'BRIEF_READY');
  if (!shipped.length) L.push('- no scripts generated this cycle');
  for (const s of shipped) {
    L.push(`- ${s.generated_at} "${s.brief?.product}" [${s.brief?.category}] hook=${s.brief?.pattern?.hook_type} proof=${s.brief?.pattern?.proof_type} (${s.status})`);
  }
  L.push('', '### Relative performance');
  const latestPull = pulls[pulls.length - 1];
  if (!latestPull?.sections?.engagement_to_conversion?.length) {
    L.push('- Gap: side-by-side CTR/conversion comparison requires at least one daily pull with attributed video data this cycle. Run `intel daily-pull` after videos post.');
  } else {
    for (const c of latestPull.sections.engagement_to_conversion) {
      L.push(`- ${c.category}: your CTR ${pct(c.ctr)}, conversion ${pct(c.conversion)} across ${c.videos} videos (source: ${c.sources[0].endpoint} @ ${c.sources[0].pulled_at})`);
    }
    if (rankedObs.length) {
      L.push('- Competitor comparison basis: engagement rate only (conversion not observable). ' +
        `Observed competitor mean eng-rate: ${(rankedObs.reduce((s, o) => s + engRate(o), 0) / rankedObs.length * 100).toFixed(2)}%.`);
    }
  }
  L.push('');

  L.push('## Micro-adjustments (current pattern weights)');
  const cats = category ? [category] : [...new Set([...observations.map((o) => o.category), ...shipped.map((s) => s.brief?.category)].filter(Boolean))];
  if (!cats.length) L.push('- no categories with activity this cycle');
  for (const c of cats) {
    const w = getWeights(c);
    const hooks = Object.entries(w.hooks).sort((a, b) => b[1] - a[1]);
    const proofs = Object.entries(w.proofs).sort((a, b) => b[1] - a[1]);
    L.push(`- ${c}: lead hook → ${hooks[0][0]} (${hooks[0][1]}), lead proof → ${proofs[0][0]} (${proofs[0][1]})` +
      (w.suppressed_phrases.length ? `; ${w.suppressed_phrases.length} suppressed phrase(s)` : ''));
    if (!w.updated_at) L.push(`  (weights are still defaults — no measured evidence yet for ${c}; recommendations activate after the first significant analysis cycle)`);
  }

  return L.join('\n');
}

function engRate(o) {
  const v = Number(o.views) || 0;
  if (!v) return 0;
  return ((Number(o.likes) || 0) + (Number(o.shares) || 0) * 3 + (Number(o.comments) || 0) * 2) / v;
}
function pct(x) {
  return x == null ? 'n/a' : `${(x * 100).toFixed(2)}%`;
}
