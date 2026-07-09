// TikTok Shop policy compliance layer.
//
// Philosophy: maximum persuasive force INSIDE the policy boundary. The
// linter's job is to catch claim structures that cross it — not to
// water scripts down. Anything flagged HIGH must be rewritten before a
// script ships; MEDIUM flags get an auto-suggested compliant alternative.
//
// Sources of truth: TikTok Shop Prohibited Products & Restricted Content
// policies and TikTok's branded-content/commerce ad policies. This
// ruleset is a working encoding, not the policy itself — recheck Seller
// Center policy pages when TikTok announces changes.

export const CATEGORY_SENSITIVITY = {
  supplements: {
    level: 'HIGH',
    why: 'Health claims: no disease treatment/prevention/cure language, no guaranteed physical outcomes.',
    adjust: 'Frame around routine, taste, convenience, and demand data ("40k sold this month") — never bodily results.',
  },
  beauty: {
    level: 'HIGH',
    why: 'Before/after implications and exaggerated cosmetic results draw enforcement.',
    adjust: 'Describe texture, application, wear-time; use sales/engagement volume as the proof, not transformation claims.',
  },
  electronics: {
    level: 'MEDIUM',
    why: 'Spec claims must be substantiated; battery life, capacity, and certification claims are checked.',
    adjust: 'Quote only manufacturer-listed specs; anchor persuasion in sell-through and review volume.',
  },
  cleaning: {
    level: 'MEDIUM',
    why: '"Kills 99.9%"-style efficacy claims require substantiation.',
    adjust: 'Show demand and repeat-purchase signals instead of lab-style efficacy claims.',
  },
  food: {
    level: 'MEDIUM',
    why: 'Nutrition and weight-related implications are restricted.',
    adjust: 'Taste, ritual, volume sold. No weight or health outcomes.',
  },
  default: {
    level: 'LOW',
    why: 'Standard prohibited-claims rules apply.',
    adjust: null,
  },
};

// Claim patterns that cross the line. Each carries severity and, where
// possible, a compliant reframe that keeps the persuasive intent.
const CLAIM_RULES = [
  { re: /\b(cure[sd]?|heal[sed]*|treat[sed]*|prevent[sed]*)\b.*\b(disease|illness|condition|acne|anxiety|pain|infection)\b/i,
    severity: 'HIGH', tag: 'health-claim',
    fix: 'Remove the medical outcome entirely; replace with demand data (units sold, repeat-buy rate).' },
  { re: /\b(lose|burn|melt|shed)\b.{0,20}\b(weight|fat|pounds|lbs|kg)\b/i,
    severity: 'HIGH', tag: 'weight-claim',
    fix: 'Weight outcomes are prohibited. Pivot to routine/energy framing with zero outcome promise.' },
  { re: /\b(guarantee[ds]?|promise[ds]?|100%|risk[- ]free|no side effects)\b/i,
    severity: 'HIGH', tag: 'guarantee-language',
    fix: 'Convert guarantee to social proof: "X units sold in Y days" says it without promising it.' },
  { re: /\b(make|earn|made)\b.{0,25}\$\s?[\d,]+|\bpassive income\b|\bget rich\b/i,
    severity: 'HIGH', tag: 'income-claim',
    fix: 'Income claims are prohibited. Cut entirely.' },
  { re: /\bbefore\s+(and|&)\s+after\b|\bresults\s+in\s+\d+\s+(days?|weeks?)\b/i,
    severity: 'HIGH', tag: 'before-after',
    fix: 'Timed-results framing implies guaranteed outcomes. Replace with "why people keep reordering" + real reorder data.' },
  { re: /\b(buy now|order now|don'?t wait|act now|last chance|hurry)\b/i,
    severity: 'MEDIUM', tag: 'hard-sell-cta',
    fix: 'Hard-sell CTAs trigger over-push filters. Use native commerce language: "it\'s in the shop tab", "link\'s on my profile".' },
  { re: /\bonly \d+ left\b|\bselling out\b|\bwon'?t restock\b/i,
    severity: 'MEDIUM', tag: 'unverified-scarcity',
    fix: 'Scarcity must be true and verifiable from inventory data. If stock data confirms it, keep it and cite it; otherwise cut.' },
  { re: /\b(best|#1|number one)\b.{0,20}\b(on tiktok|in the world|ever)\b/i,
    severity: 'MEDIUM', tag: 'superlative',
    fix: 'Unverifiable superlative. Replace with a rank you can source: "top 10 in its category this week" (from the momentum pull).' },
  { re: /\bFDA[- ]approved\b|\bclinically proven\b/i,
    severity: 'HIGH', tag: 'regulatory-claim',
    fix: 'Only usable with documentation on file with TikTok Shop. Cut unless the seller has filed substantiation.' },
];

export function categorySensitivity(category) {
  const key = String(category || '').toLowerCase();
  for (const k of Object.keys(CATEGORY_SENSITIVITY)) {
    if (k !== 'default' && key.includes(k)) return { category: k, ...CATEGORY_SENSITIVITY[k] };
  }
  return { category: key || 'unknown', ...CATEGORY_SENSITIVITY.default };
}

// Lint a script (or any promotional copy). Returns flags sorted by
// severity. An empty array means the copy is inside the boundary as far
// as this ruleset can tell — it is not a legal guarantee.
export function lintScript(text, category) {
  const flags = [];
  for (const rule of CLAIM_RULES) {
    const m = text.match(rule.re);
    if (m) {
      flags.push({
        severity: rule.severity,
        tag: rule.tag,
        matched: m[0],
        fix: rule.fix,
      });
    }
  }
  const sens = categorySensitivity(category);
  if (sens.level === 'HIGH' && !flags.some((f) => f.severity === 'HIGH')) {
    flags.push({
      severity: 'INFO',
      tag: 'sensitive-category',
      matched: sens.category,
      fix: sens.adjust,
    });
  }
  const order = { HIGH: 0, MEDIUM: 1, INFO: 2 };
  flags.sort((a, b) => order[a.severity] - order[b.severity]);
  return { flags, sensitivity: sens, clean: !flags.some((f) => f.severity === 'HIGH') };
}

// CTA constructions ranked safest-first. The script engine picks from
// this list (weighted by pattern data) and never invents new CTA shapes
// that haven't been through the linter.
export const COMPLIANT_CTAS = [
  "it's in the shop tab if you want to look",
  "I linked it on my profile",
  "check it in the shop — that's where I got mine",
  "the orange cart has it if you're curious",
  "it's pinned in the shop if you want the one I have",
];
