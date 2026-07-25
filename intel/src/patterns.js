// Pattern-weight feedback loop.
//
// Weights are per-category behavioral priors for the script engine:
// hook technique, proof-point structure, and CTA construction. They are
// updated ONLY from measured performance (competitive cycles and the
// shop's own video analytics) — never from vibes — and they decay, so a
// technique that stops earning data loses its seat.

import { readState, writeState } from './store.js';

export const HOOK_TYPES = ['stat-lead', 'curiosity-gap', 'contradiction', 'social-proof-volume', 'personal-outcome'];
export const PROOF_TYPES = ['data-fact', 'testimonial', 'live-demo', 'social-proof-volume'];

const DEFAULT_WEIGHTS = () => ({
  hooks: Object.fromEntries(HOOK_TYPES.map((h) => [h, 1.0])),
  proofs: Object.fromEntries(PROOF_TYPES.map((p) => [p, 1.0])),
  cta_bias: 0, // index bias into COMPLIANT_CTAS, earned by conversion data
  suppressed_phrases: [], // language seen in flagged/removed videos — never emit
  evidence: [], // every weight change records the measurement that caused it
  updated_at: null,
});

const DECAY = 0.9; // applied each cycle before new evidence lands
const MAX_EVIDENCE = 40;

export function getWeights(category) {
  const all = readState('patterns', {});
  return all[normalize(category)] || DEFAULT_WEIGHTS();
}

// Apply one analysis cycle's findings for a category.
// findings: [{ kind: 'hook'|'proof', name, lift, sample, source }]
// suppress: [{ phrase, reason, source }]
export function updateWeights(category, findings = [], suppress = []) {
  const key = normalize(category);
  const all = readState('patterns', {});
  const w = all[key] || DEFAULT_WEIGHTS();

  // Decay first: yesterday's winner has to keep earning it.
  for (const k of Object.keys(w.hooks)) w.hooks[k] = round(1 + (w.hooks[k] - 1) * DECAY);
  for (const k of Object.keys(w.proofs)) w.proofs[k] = round(1 + (w.proofs[k] - 1) * DECAY);

  for (const f of findings) {
    if (f.lift == null || !f.source) continue; // unmeasured observation = noise, discard
    const table = f.kind === 'hook' ? w.hooks : f.kind === 'proof' ? w.proofs : null;
    if (!table || !(f.name in table)) continue;
    table[f.name] = round(Math.max(0.2, table[f.name] + f.lift));
    w.evidence.push({
      at: new Date().toISOString(),
      kind: f.kind,
      name: f.name,
      lift: f.lift,
      sample: f.sample ?? null,
      source: f.source,
    });
  }

  for (const s of suppress) {
    if (!s.phrase) continue;
    if (!w.suppressed_phrases.some((p) => p.phrase === s.phrase)) {
      w.suppressed_phrases.push({ phrase: s.phrase, reason: s.reason, source: s.source, at: new Date().toISOString() });
    }
  }

  while (w.evidence.length > MAX_EVIDENCE) w.evidence.shift();
  w.updated_at = new Date().toISOString();
  all[key] = w;
  writeState('patterns', all);
  return w;
}

export function topHook(weights) {
  return best(weights.hooks);
}
export function topProof(weights) {
  return best(weights.proofs);
}

function best(table) {
  return Object.entries(table).sort((a, b) => b[1] - a[1])[0];
}
function normalize(c) {
  return String(c || 'general').toLowerCase().trim();
}
function round(n) {
  return Math.round(n * 1000) / 1000;
}
