# TikTok Shop Intelligence Agent

A self-contained, zero-dependency Node.js framework that turns live TikTok
Shop performance data into policy-safe, high-converting talking-head video
scripts — plus a competitive intelligence layer that learns from measured
creator performance and feeds pattern weights back into generation.

**Built for the affiliate side**: the default role is affiliate creator.
The data layer reads the affiliate marketplace (commission rates, sold
counts, open collaborations) and your own affiliate orders — no shop
ownership required. A seller mode (`TTS_ROLE=seller`) exists for operators
who also run the shop and unlocks the windowed shop-analytics endpoints.

Requires Node 18+ (built-in `fetch`). No npm install needed.

## No API access? Start here

Most individual affiliates don't have Open API credentials — TikTok shows
you the numbers in the **Affiliate Center UI** but doesn't hand creators
API keys. The framework runs fully in that situation on
**operator-reported readings**: you read the real numbers off your
Affiliate Center screen and log them.

```sh
# Daily ritual (2 minutes): open the Affiliate Center marketplace,
# log the products you're tracking with today's numbers:
node intel/cli.js log-product --name "collagen gummies" --category supplements \
     --sold 48200 --commission 20 --price 19.99

node intel/cli.js daily-pull          # momentum activates from the 2nd reading
node intel/cli.js script "collagen gummies"
```

The honesty rules adapt but don't relax: every entry records that it was
operator-reported and when; readings older than **72 hours are refused**
for script generation (re-read the screen, don't reuse); momentum needs
two real readings of the same product; a sold count is mandatory to log
at all. If you later obtain API credentials, the same commands switch to
live pulls automatically — nothing else changes.

## Hard rules the code enforces

1. **Only source: TikTok Shop's own APIs** (Partner/Open API at
   `open-api.tiktokglobalshop.com`). No third-party aggregators, no
   synthetic benchmarks — there is deliberately no demo mode.
2. **No fabricated metrics, ever.** A failed or missing pull produces an
   explicit `DATA_UNAVAILABLE` gap entry, never an estimate. Every number
   surfaced anywhere carries provenance (`endpoint` + `pulled_at`).
3. **Significance gates.** Products/categories below sample thresholds get
   "not enough data" plus the closest trending alternative — not a script.
4. **Compliance boundary.** Scripts are linted against an encoded ruleset
   of TikTok Shop claim policies. HIGH-severity flags block shipping;
   phrases from the compliance-incident log are permanently suppressed
   regardless of how well they converted.
5. **Weights only move on evidence.** Pattern weights update from measured
   engagement/conversion data with decay; unmeasured observations are
   rejected at the door.

## Setup

```sh
cp intel/.env.example intel/.env   # then fill in and export, or set in CI
```

Credentials come from TikTok Shop Partner Center
(<https://partner.tiktokshop.com>): create an app with the **Affiliate
Creator** scopes, complete creator authorization, and export:

| Variable | What it is |
|---|---|
| `TTS_APP_KEY` / `TTS_APP_SECRET` | Partner app credentials (secret signs every request — HMAC-SHA256) |
| `TTS_ACCESS_TOKEN` | Creator-authorized access token |
| `TTS_ROLE` | `affiliate` (default) or `seller` |
| `TTS_SHOP_CIPHER` | Seller mode only — shop cipher from shop authorization |
| `ANTHROPIC_API_KEY` | Optional — in-engine prose generation; otherwise the engine emits a grounded brief |

> Endpoint version segments (e.g. `/analytics/202405/…`) rotate as TikTok
> ships API versions. If a pull returns a path error, update
> `ENDPOINTS` in `src/client.js` from the current Partner Center docs.

## Commands

```sh
node intel/cli.js status                      # credential + state overview
node intel/cli.js daily-pull                  # Daily Intelligence Dashboard
node intel/cli.js script "collagen gummies" --category supplements
node intel/cli.js competitive-pull supplements
node intel/cli.js observe --category supplements --url https://tiktok.com/... \
     --hook stat-lead --proof data-fact --views 84000 --likes 9100 --shares 420
node intel/cli.js analyze supplements         # run analysis cycle → update weights
node intel/cli.js report weekly --category supplements
```

### Daily pull
Refreshes the data layer and returns: top 10 marketplace products by
**momentum**, breakout SKUs, your 30-day affiliate order/commission
summary, and compliance flags for every surfaced product.

Affiliate momentum works by **snapshot diffing**: the marketplace API
reports cumulative sold counts, so the first pull establishes a baseline
(and says so explicitly) and every subsequent pull ranks products by
sold-count growth since the previous stored snapshot. Run it daily — the
picture compounds. Engagement→conversion per category is a seller-scope
metric and is reported as a structural gap in affiliate mode; log your own
video numbers from the app's analytics screen via `observe` to fill it.
(Seller mode computes 7d-vs-prior-7d velocity directly from windowed
analytics.)

### Script generation
`script <product|SKU>` searches the live marketplace feed for the product,
loads the category's current pattern weights and suppression list, and
builds a **script brief**: verified data points (each with its source
pull), the weighted hook/proof/CTA selection, and hard style constraints
(talking-head only, hook in the first 2–3 seconds built on a real metric,
no AI cadence, soft native-commerce CTA, affiliate-disclosure-safe). The
commission rate rides along as an **internal** data point — it informs
product choice but is constrained never to be spoken on camera. With
`ANTHROPIC_API_KEY` set it generates the prose, lints it, retries once on
violations, and refuses to ship anything that still fails. Products with
under 100 recorded sales are declined with the closest trending
alternative offered instead.

### Competitive layer
What TikTok's APIs actually expose about competitors is limited — and the
framework says so instead of pretending:

- **API-observable:** affiliate marketplace open collaborations and
  commission benchmarks; your own category-level analytics as the
  comparison baseline.
- **Operator-observable:** competing videos' technique (hook/proof/CTA)
  and *public engagement* — logged via `observe`, which **rejects any
  observation without engagement numbers** (unmeasured technique = noise).
- **Not observable:** competitor per-video CTR/conversion. Recorded as a
  structural gap in every cycle; comparisons are engagement-based.

`analyze <category>` converts logged observations into weight updates
(with decay) once the sample clears significance thresholds. Videos logged
with `--compliance removed|reduced-distribution --trigger "phrase"` land
in the incident log and their trigger phrases are suppressed from all
future generation.

### Reports
`report weekly|monthly` assembles the landscape summary, incident log,
your scripts' relative performance, and current per-category pattern
weights — entirely from persisted state.

## State & cross-session memory

All learned state lives in `intel/state/*.json` (pull snapshots, pattern
weights, incidents, script history, competitive cycles). **Commit it** —
remote sessions run in ephemeral containers, so committed state is the
mechanism that lets the picture compound across sessions.
