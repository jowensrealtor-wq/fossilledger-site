// Competitive Intelligence Layer.
//
// Honesty constraint, stated up front and enforced in code: TikTok's
// APIs do NOT expose other creators' per-video CTR or conversion rates.
// What IS legitimately observable through permitted sources:
//   - affiliate marketplace: open collaborations, commission rates, and
//     creator-level aggregate performance for products in your categories
//   - your own category benchmarks from shop analytics
//   - public engagement signals (views, likes, shares) on discoverable
//     videos — engagement only, not conversion
// The framework analyzes what it can measure and files everything else
// as an explicit gap. A hook observed without engagement data is
// discarded as noise (rule: no unmeasured observations enter weights).
//
// Technique observations (hook type, proof structure, CTA phrasing,
// compliance incidents) are captured via the `observe` command: the
// operator/agent logs what a competing video did together with its
// public engagement numbers and video URL. Those observations join the
// API-side benchmarks in the analysis cycle.

import { appendState, readState } from './store.js';
import { updateWeights, HOOK_TYPES, PROOF_TYPES } from './patterns.js';
import { lintScript } from './compliance.js';
import { significanceCheck } from './metrics.js';

// Full monitoring sweep for a category.
export async function competitivePull(client, category) {
  const gate = client.credentialGap();
  const cycle = {
    at: new Date().toISOString(),
    category,
    api: {},
    observations: pendingObservations(category),
    gaps: [],
  };

  if (gate) {
    cycle.gaps.push({ what: 'affiliate/analytics API pulls', why: gate.detail, missing: gate.missing });
  } else {
    const collabs = await client.affiliateOpenCollaborations({});
    if (collabs.ok) {
      cycle.api.open_collaborations = {
        endpoint: collabs.endpoint,
        pulled_at: collabs.pulled_at,
        data: collabs.data,
      };
    } else {
      cycle.gaps.push({ what: 'affiliate open collaborations', why: collabs.detail, endpoint: collabs.endpoint });
    }
  }

  // Structural gap that no credential fixes — recorded every cycle so it
  // can never be silently papered over:
  cycle.gaps.push({
    what: "competitor per-video CTR / conversion",
    why: 'Not exposed by TikTok Shop or TikTok for Business APIs for videos you do not own. ' +
      'Analysis uses public engagement signals + affiliate aggregates; conversion comparisons are limited to your own videos vs category benchmarks.',
    structural: true,
  });

  appendState('competitive', cycle, 60);
  return cycle;
}

// Log a manually-observed competitor video. Refuses observations with no
// engagement numbers (unmeasured technique = noise, per mandate).
export function logObservation(obs) {
  const required = ['category', 'video_url', 'hook_type', 'proof_type'];
  const missing = required.filter((k) => !obs[k]);
  if (missing.length) throw new Error(`Observation missing: ${missing.join(', ')}`);
  if (!HOOK_TYPES.includes(obs.hook_type)) throw new Error(`hook_type must be one of: ${HOOK_TYPES.join(', ')}`);
  if (!PROOF_TYPES.includes(obs.proof_type)) throw new Error(`proof_type must be one of: ${PROOF_TYPES.join(', ')}`);
  if (obs.views == null && obs.likes == null && obs.shares == null) {
    throw new Error('Refusing to log: no engagement metrics attached. A technique observed without measurable engagement data is noise — discarded.');
  }
  const entry = { ...obs, logged_at: new Date().toISOString() };
  appendState('competitive', { at: entry.logged_at, category: obs.category, observation: entry, gaps: [] }, 60);

  // Compliance incident path: flagged/removed competitor videos feed the
  // suppression list immediately.
  if (obs.compliance_status && obs.compliance_status !== 'clean') {
    const trigger = obs.trigger_phrase || null;
    appendState('incidents', {
      at: entry.logged_at,
      category: obs.category,
      video_url: obs.video_url,
      status: obs.compliance_status, // 'reduced-distribution' | 'warning' | 'removed'
      trigger_phrase: trigger,
    });
    if (trigger) {
      updateWeights(obs.category, [], [{ phrase: trigger, reason: obs.compliance_status, source: obs.video_url }]);
    }
  }
  return entry;
}

function pendingObservations(category) {
  const cycles = readState('competitive', []);
  return cycles
    .filter((c) => c.observation && c.category === category)
    .map((c) => c.observation);
}

// Analysis cycle: turn observed engagement data into pattern-weight
// updates, per category. Uses share-of-engagement lift vs the category's
// observed mean; declines to update when the sample is insignificant.
export function runAnalysisCycle(category) {
  const obs = pendingObservations(category);
  const measured = obs.filter((o) => o.views != null && Number(o.views) > 0);
  const sig = significanceCheck({
    videos: measured.length,
    views: measured.reduce((s, o) => s + Number(o.views), 0),
    orders: Number.POSITIVE_INFINITY, // conversion not observable for competitors; checked separately for own videos
  });
  if (!sig.significant) {
    return {
      updated: false,
      reason: `Insufficient competitive sample for ${category}: ${sig.failures.join('; ')}. ` +
        'Log more observations (intel observe) or wait for more cycles before weights move.',
      sample: measured.length,
    };
  }

  const meanEng = measured.reduce((s, o) => s + engagementRate(o), 0) / measured.length;
  const findings = [];
  for (const kind of ['hook', 'proof']) {
    const field = kind === 'hook' ? 'hook_type' : 'proof_type';
    const groups = new Map();
    for (const o of measured) {
      const g = groups.get(o[field]) || [];
      g.push(o);
      groups.set(o[field], g);
    }
    for (const [name, g] of groups) {
      const rate = g.reduce((s, o) => s + engagementRate(o), 0) / g.length;
      findings.push({
        kind,
        name,
        lift: round((rate - meanEng) / (meanEng || 1)),
        sample: g.length,
        source: `observed engagement, ${g.length} videos in ${category}`,
      });
    }
  }
  const weights = updateWeights(category, findings, []);
  return { updated: true, findings, weights };
}

// Guard used by the script engine: no pattern from the incident log may
// be recommended, regardless of historical performance.
export function incidentPhrases(category) {
  return readState('incidents', [])
    .filter((i) => !category || i.category === category)
    .map((i) => i.trigger_phrase)
    .filter(Boolean);
}

export function checkAgainstIncidents(text, category) {
  const hits = incidentPhrases(category).filter((p) => text.toLowerCase().includes(p.toLowerCase()));
  const lint = lintScript(text, category);
  return { incident_hits: hits, lint };
}

function engagementRate(o) {
  const views = Number(o.views) || 0;
  if (!views) return 0;
  return ((Number(o.likes) || 0) + (Number(o.shares) || 0) * 3 + (Number(o.comments) || 0) * 2) / views;
}
function round(n) {
  return Math.round(n * 1000) / 1000;
}
