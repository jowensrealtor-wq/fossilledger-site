// Operator-reported data path — for affiliates WITHOUT Open API access.
//
// TikTok shows affiliates the marketplace numbers (sold counts, commission
// rates) and their own performance in the Affiliate Center / creator tools
// UI, but does not grant most individual creators API credentials. This
// module lets the operator key in numbers they are reading off that screen.
//
// No-fabrication rules still hold, adapted to the source:
//   - every entry records where it was read from and when
//     (source: 'affiliate-center (operator-reported)')
//   - entries expire: data older than FRESHNESS_HOURS is refused for
//     script generation, not silently reused
//   - momentum still requires two real snapshots of the same product;
//     one entry = baseline, stated explicitly
//   - nothing is interpolated between entries, ever

import { readState, writeState } from './store.js';

export const FRESHNESS_HOURS = 72;
const SOURCE = 'affiliate-center (operator-reported)';

// Log one product snapshot as read from the Affiliate Center marketplace.
export function logProductSnapshot({ name, category, sold, commission, price, url }) {
  if (!name) throw new Error('product name is required');
  const soldN = Number(sold);
  if (!Number.isFinite(soldN)) {
    throw new Error('a real sold count from the Affiliate Center screen is required (--sold N). Refusing to log without it.');
  }
  const entry = {
    product_key: normalize(name),
    name,
    category: category || null,
    units_sold_total: soldN,
    commission_rate: commission != null ? Number(commission) : null,
    price: price != null ? Number(price) : null,
    url: url || null,
    source: SOURCE,
    logged_at: new Date().toISOString(),
  };
  const log = readState('manual', []);
  log.push(entry);
  while (log.length > 500) log.shift();
  writeState('manual', log);
  return entry;
}

// Latest entry per product, with staleness computed.
export function manualFeed() {
  const log = readState('manual', []);
  const latest = new Map();
  for (const e of log) latest.set(e.product_key, e); // log is chronological
  return [...latest.values()].map((e) => ({ ...e, ...staleness(e) }));
}

// All entries for one product, oldest first (for momentum diffing).
export function manualHistory(nameOrKey) {
  const key = normalize(nameOrKey);
  return readState('manual', []).filter(
    (e) => e.product_key === key || e.product_key.includes(key) || key.includes(e.product_key),
  );
}

export function findManualProduct(needle) {
  const feed = manualFeed();
  const n = normalize(needle);
  return feed.find((e) => e.product_key === n) || feed.find((e) => e.product_key.includes(n)) || null;
}

// Momentum across operator-reported snapshots: diff the two most recent
// entries per product. Products with a single entry are baselines.
export function manualMomentum(topN = 10) {
  const log = readState('manual', []);
  const byProduct = new Map();
  for (const e of log) {
    const list = byProduct.get(e.product_key) || [];
    list.push(e);
    byProduct.set(e.product_key, list);
  }
  const ranked = [];
  const baselines = [];
  for (const entries of byProduct.values()) {
    const cur = entries[entries.length - 1];
    const prev = entries.length > 1 ? entries[entries.length - 2] : null;
    const row = {
      product_id: cur.product_key,
      name: cur.name,
      category: cur.category,
      units_sold_total: cur.units_sold_total,
      commission_rate: cur.commission_rate,
      sources: [{ endpoint: cur.source, pulled_at: cur.logged_at }],
    };
    if (!prev) {
      baselines.push(row);
      continue;
    }
    row.units_delta = cur.units_sold_total - prev.units_sold_total;
    row.velocity = prev.units_sold_total > 0 ? row.units_delta / prev.units_sold_total : null;
    row.hours_between_snapshots =
      Math.round(((Date.parse(cur.logged_at) - Date.parse(prev.logged_at)) / 36e5) * 10) / 10;
    ranked.push(row);
  }
  ranked.sort((a, b) => (b.velocity ?? -Infinity) - (a.velocity ?? -Infinity));
  return { ranked: ranked.slice(0, topN), baselines };
}

export function staleness(entry) {
  const ageHours = (Date.now() - Date.parse(entry.logged_at)) / 36e5;
  return { age_hours: Math.round(ageHours * 10) / 10, stale: ageHours > FRESHNESS_HOURS };
}

function normalize(s) {
  return String(s || '').toLowerCase().trim().replace(/\s+/g, ' ');
}
