// Persistent framework state. Everything the framework learns — pull
// snapshots, pattern weights, compliance incident log, script history —
// lives in intel/state/*.json and is committed to the repo, because remote
// sessions run in ephemeral containers: committing state IS the
// cross-session memory that lets the picture compound over time.

import fs from 'node:fs';
import path from 'node:path';
import { PATHS } from './config.js';

const FILES = {
  pulls: 'pulls.json', // daily pull snapshots (rolling, capped)
  patterns: 'pattern-weights.json', // script-engine behavioral weights
  incidents: 'compliance-incidents.json', // observed flags/removals + trigger
  scripts: 'script-history.json', // generated scripts + the data behind them
  competitive: 'competitive-cycles.json', // competitive sweep results
};

function fileFor(name) {
  if (!FILES[name]) throw new Error(`Unknown state store: ${name}`);
  return path.join(PATHS.state, FILES[name]);
}

export function readState(name, fallback) {
  const f = fileFor(name);
  if (!fs.existsSync(f)) return fallback;
  try {
    return JSON.parse(fs.readFileSync(f, 'utf8'));
  } catch {
    // A corrupt state file is surfaced, not silently regenerated — losing
    // learned weights should be a visible event.
    throw new Error(`State file ${f} is corrupt JSON. Fix or delete it explicitly.`);
  }
}

export function writeState(name, value) {
  fs.mkdirSync(PATHS.state, { recursive: true });
  fs.writeFileSync(fileFor(name), JSON.stringify(value, null, 2) + '\n');
}

// Append to a rolling log store, keeping the most recent `cap` entries.
export function appendState(name, entry, cap = 120) {
  const list = readState(name, []);
  list.push(entry);
  while (list.length > cap) list.shift();
  writeState(name, list);
  return list;
}
