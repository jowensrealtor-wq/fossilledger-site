// Metrics engine: turns raw API envelopes into the intelligence layer.
// Rules enforced here:
//   - every derived number keeps a `sources` array of endpoint+timestamp
//   - a gap in the underlying pull produces an explicit `gaps` entry,
//     never an interpolated value
//   - momentum = velocity of growth (recent window vs prior window),
//     not raw volume

export function isoDate(d) {
  return d.toISOString().slice(0, 10);
}

export function dateWindows(now = new Date()) {
  const day = 24 * 60 * 60 * 1000;
  const at = (n) => isoDate(new Date(now.getTime() - n * day));
  return {
    today: isoDate(now),
    last24h: { start: at(1), end: at(0) },
    last48h: { start: at(2), end: at(0) },
    last7d: { start: at(7), end: at(0) },
    prior7d: { start: at(14), end: at(7) },
    last30d: { start: at(30), end: at(0) },
  };
}

// Growth velocity: (recent - prior) / prior. Requires a real prior-window
// value; if prior is 0 or missing the product is marked "new/insufficient
// baseline" instead of getting an infinite score.
export function velocity(recent, prior) {
  if (prior == null || recent == null) return { value: null, reason: 'missing window data' };
  if (prior === 0) {
    return recent > 0
      ? { value: null, reason: 'no prior baseline (new SKU)', breakout: recent > 0 }
      : { value: 0 };
  }
  return { value: (recent - prior) / prior };
}

// Ranks products by sales-growth velocity given two product-performance
// pulls (recent window, prior window). Both must be successful envelopes.
export function rankByMomentum(recentPull, priorPull, topN = 10) {
  const gaps = [];
  for (const [label, pull] of [['recent window', recentPull], ['prior window', priorPull]]) {
    if (!pull.ok) gaps.push({ what: `product performance (${label})`, why: pull.detail, endpoint: pull.endpoint });
  }
  if (gaps.length) return { ranked: [], gaps };

  const index = new Map();
  for (const p of priorPull.data?.products || []) index.set(p.id, p);

  const ranked = [];
  for (const p of recentPull.data?.products || []) {
    const prior = index.get(p.id);
    const unitsRecent = num(p.units_sold);
    const unitsPrior = prior ? num(prior.units_sold) : null;
    const v = velocity(unitsRecent, unitsPrior);
    ranked.push({
      product_id: p.id,
      name: p.name || null,
      units_recent: unitsRecent,
      units_prior: unitsPrior,
      gmv_recent: num(p.gmv?.amount),
      currency: p.gmv?.currency || null,
      velocity: v.value,
      velocity_note: v.reason || null,
      breakout: Boolean(v.breakout),
      sources: [
        { endpoint: recentPull.endpoint, pulled_at: recentPull.pulled_at },
        { endpoint: priorPull.endpoint, pulled_at: priorPull.pulled_at },
      ],
    });
  }
  ranked.sort((a, b) => (b.velocity ?? -Infinity) - (a.velocity ?? -Infinity));
  return { ranked: ranked.slice(0, topN), gaps };
}

// Affiliate-mode momentum: the marketplace API reports point-in-time
// cumulative sold counts, not windowed history. Velocity is derived by
// diffing today's pull against the most recent stored snapshot — which is
// only possible with real prior pulls. First pull = explicit "baseline
// established, momentum available from next pull", never an estimate.
export function rankByMomentumSnapshots(currentPull, previousSnapshot, topN = 10) {
  const gaps = [];
  if (!currentPull.ok) {
    return { ranked: [], gaps: [{ what: 'marketplace products (current)', why: currentPull.detail, endpoint: currentPull.endpoint }] };
  }
  const products = currentPull.data?.products || [];
  if (!previousSnapshot) {
    return {
      ranked: [],
      gaps: [{
        what: 'momentum baseline',
        why: 'First stored pull — cumulative sold counts have no prior snapshot to diff against. Baseline established now; momentum ranks appear from the next pull onward.',
      }],
      baseline: products.map((p) => snapshotRow(p, currentPull)),
    };
  }

  const prior = new Map((previousSnapshot.products || []).map((p) => [p.product_id, p]));
  const hoursBetween = (Date.parse(currentPull.pulled_at) - Date.parse(previousSnapshot.pulled_at)) / 36e5;
  const ranked = [];
  for (const p of products) {
    const row = snapshotRow(p, currentPull);
    const prev = prior.get(row.product_id);
    if (!prev) {
      row.velocity = null;
      row.velocity_note = 'new to feed since last snapshot';
      row.breakout = row.units_sold_total > 0;
    } else {
      const delta = row.units_sold_total != null && prev.units_sold_total != null
        ? row.units_sold_total - prev.units_sold_total
        : null;
      row.units_delta = delta;
      row.velocity = delta != null && prev.units_sold_total > 0 ? delta / prev.units_sold_total : null;
      if (row.velocity == null) row.velocity_note = 'missing sold-count on one side of the diff';
      row.hours_between_snapshots = Math.round(hoursBetween * 10) / 10;
    }
    ranked.push(row);
  }
  ranked.sort((a, b) => (b.velocity ?? -Infinity) - (a.velocity ?? -Infinity));
  return { ranked: ranked.slice(0, topN), gaps, all: ranked };
}

function snapshotRow(p, pull) {
  return {
    product_id: p.id ?? p.product_id,
    name: p.title || p.name || null,
    category: p.category || p.category_name || null,
    units_sold_total: num(p.units_sold ?? p.sold_count ?? p.sales),
    price: num(p.price?.amount ?? p.price),
    currency: p.price?.currency || null,
    commission_rate: num(p.commission_rate),
    sources: [{ endpoint: pull.endpoint, pulled_at: pull.pulled_at }],
  };
}

// Breakout SKUs: units in the last 24-48h with no meaningful baseline, or
// velocity above threshold in that window.
export function findBreakouts(recent48hPull, threshold = 1.0) {
  if (!recent48hPull.ok) {
    return { breakouts: [], gaps: [{ what: 'breakout scan (48h)', why: recent48hPull.detail, endpoint: recent48hPull.endpoint }] };
  }
  const breakouts = (recent48hPull.data?.products || [])
    .filter((p) => num(p.units_sold) > 0)
    .map((p) => ({
      product_id: p.id,
      name: p.name || null,
      units_48h: num(p.units_sold),
      gmv_48h: num(p.gmv?.amount),
      sources: [{ endpoint: recent48hPull.endpoint, pulled_at: recent48hPull.pulled_at }],
    }))
    .sort((a, b) => b.units_48h - a.units_48h);
  return { breakouts, gaps: [], threshold };
}

// Engagement-to-conversion by category, from the video analytics pull.
export function engagementToConversion(videoPull) {
  if (!videoPull.ok) {
    return { byCategory: [], gaps: [{ what: 'video engagement/conversion', why: videoPull.detail, endpoint: videoPull.endpoint }] };
  }
  const byCat = new Map();
  for (const v of videoPull.data?.videos || []) {
    const cat = v.category || 'uncategorized';
    const row = byCat.get(cat) || { category: cat, views: 0, clicks: 0, orders: 0, videos: 0 };
    row.views += num(v.views) ?? 0;
    row.clicks += num(v.product_page_views ?? v.clicks) ?? 0;
    row.orders += num(v.orders ?? v.units_sold) ?? 0;
    row.videos += 1;
    byCat.set(cat, row);
  }
  const byCategory = [...byCat.values()].map((r) => ({
    ...r,
    ctr: r.views > 0 ? r.clicks / r.views : null,
    conversion: r.clicks > 0 ? r.orders / r.clicks : null,
    sources: [{ endpoint: videoPull.endpoint, pulled_at: videoPull.pulled_at }],
  }));
  return { byCategory, gaps: [] };
}

// Minimum sample sizes below which the framework declines to draw
// conclusions rather than reporting noise as signal.
export const SIGNIFICANCE = {
  minVideosPerCategory: 8,
  minViewsPerVideo: 500,
  minOrdersForConversionClaim: 10,
};

export function significanceCheck({ videos = 0, views = 0, orders = 0 }) {
  const failures = [];
  if (videos < SIGNIFICANCE.minVideosPerCategory)
    failures.push(`${videos} videos in category (need ≥${SIGNIFICANCE.minVideosPerCategory})`);
  if (views < SIGNIFICANCE.minViewsPerVideo)
    failures.push(`${views} views (need ≥${SIGNIFICANCE.minViewsPerVideo})`);
  if (orders < SIGNIFICANCE.minOrdersForConversionClaim)
    failures.push(`${orders} attributed orders (need ≥${SIGNIFICANCE.minOrdersForConversionClaim})`);
  return { significant: failures.length === 0, failures };
}

function num(x) {
  if (x == null) return null;
  const n = Number(x);
  return Number.isFinite(n) ? n : null;
}