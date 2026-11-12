# Agentic AI Business Opportunities — Market Scan & Top-5 Blueprints

**Research date:** 2026-11-12 · **Scope:** US market, solo/small-team founders, autonomy-first businesses
**Prepared for:** FossilLedger / LandLead owner

---

## How to read this document

Every number carries one of three tags:

| Tag | Meaning |
|---|---|
| **[V]** | **Verified:** taken from a named source, with the source's date. "Verified" means *I found it in that source*. It does **not** mean the source is neutral. Vendor-written sources are marked *(vendor)*. |
| **[U]** | **Unverified or conflicting:** sources disagree, the source is secondhand, or I could not open the primary document. Use it for direction only. |
| **[E]** | **My estimate:** a projection or assumption, with the basis stated. Change these to fit your own situation. |

Source IDs like (S12) point to the **Sources** table at the end. All sources were accessed on 2026-11-12. Where a page shows its own date, that date is listed.

**Research limits you should know about:**
- I could not open Crunchbase, PitchBook, G2 review data, LinkedIn, X/Twitter or Reddit threads directly. Funding and "Reddit consensus" figures come from secondary sources that cite them, and are tagged as such.
- Google Trends cannot be queried from this environment, so the search-interest claims are secondhand **[U]**.
- **Domain checks were run live** against the authoritative Verisign .com registry (RDAP): 106 names checked. **Social handles and trademarks could not be checked by machine.** Social sites block automated lookups, and USPTO's search sits behind a bot challenge. For trademarks I ran web-search conflict screens, which are weaker than a USPTO search. Each name table says exactly what was and wasn't verified.

---

## Executive summary

1. **Agentic AI demand is real and growing, but horizontal agent products are crowded and failing at high rates.** Gartner expects over 40% of agentic AI projects to be canceled by the end of 2027 and estimates that only about 130 of "thousands" of agentic vendors are real (S1, 2025-06-25) **[V]**. AI SDR tools report 50–70% annual churn (S15, S16, 2026) **[U, vendor-sourced]**. Capital is concentrating in fewer, larger deals: agentic application-layer round counts fell about 38% year over year in early 2026 (S7, 2026-04-07) **[U]**.
2. **The gaps are in narrow, unglamorous workflows where the product is a finished outcome rather than a chatbot.** Typical examples: "here are this week's 37 new pool permits in your county," or "these 4 subcontractors' insurance expires in 30 days and we've already emailed them." A generic agency selling "AI automation" is described as saturated. Specialists still find work (S28, 2026-07-02) **[U, vendor synthesis of Reddit]**.
3. **The top 5, in ranked order:**
   1. **Permit-triggered lead feeds for specific trades** (score 4.05/5)
   2. **Buy-box vacant-land seller lead feeds, built on your existing LandLead engine** (4.00)
   3. **Trade-specific state and local government bid-match agent** (3.95)
   4. **Subcontractor insurance-certificate (COI) compliance agent** (3.90)
   5. **B2B accounts-receivable follow-up agent for trades and distributors** (3.85)
4. **Strategic insight:** #1, #2 and #3 are the same machine pointed at different public datasets: **ingest public records → score with an LLM → deliver a ready-to-use feed.** You have already built that machine in `landlead/`. Build the shared core once and launch the three as separate brands on one stack. Marginal startup cost for #1 and #3 then drops to about $100–$300 each **[E]**.
5. **The binding constraint is distribution, not technology.** Every top-5 idea can be built for under $1,500 in cash. All of them struggle to reach buyers cheaply. Each blueprint therefore puts as much detail into autonomous customer acquisition as into the agent itself.
6. **Recommended sequence:**
   - Launch #2 first (about 80% built, in your professional domain).
   - Add #1 on the same core in month 2.
   - Evaluate #3 in month 3–4.
   - Run #4/#5 only if you want a non-real-estate SaaS line, because they need more trust-building per sale.

---

## Part 0 — Market context (what the evidence says)

### Market size and spending
- Analysts' 2026 market-size estimates differ widely because they define "agentic AI" differently. Standalone software estimates for 2026 cluster around **$9–12B**: Fortune Business Insights $9.14B, Precedence $10.86B, Analytics Insight $12.13B (S4, 2026) **[U, secondary roundup]**.
- MarketsandMarkets projects **$7.06B (2025) → $93.20B (2032), a 44.6% CAGR** (S3, 2026) **[V, press release]**.
- Gartner's broader *spending* figure is **$201.9B in 2026**, as cited by a Feb 2026 roundup (S2, 2026-02-26) **[U, secondary]**.
- Gartner: **33% of enterprise software apps will include agentic AI by 2028, up from under 1% in 2024** (S1, 2025-06-25) **[V]**.

### Demand signals
- **Freelance demand:** Upwork's In-Demand Skills 2026 report says demand for AI-related skills grew **+109% year over year vs +23% for other skills**. **AI integration grew +178%** and **AI chatbot development +71%** (S5, Feb 2026) **[V]**. As of Oct 2026, "AI agent developer" is among Upwork's fastest-growing search terms (S6, 2026-10) **[V, search data, not hiring data]**.
- **SMB adoption is broad but shallow:**
  - General AI use: 46–76% depending on the survey (S10, 2026-07-14; S9) **[U, definitions vary]**.
  - Agent use specifically is low. One April 2026 survey found **7% of small businesses use AI agents in marketing** (S11, 2026-04) **[V, single survey]**.
  - 70% of SMB respondents say they need more training (S10) **[V]**.
  - **Implication:** SMBs want results, not tools to operate. That favors done-for-you feeds and agents over self-serve builders.
- **Search interest:** "AI agents" searches rose about 900% over 12 months into 2025. One 2026 SEO report charts a peak in early 2026 followed by about a −40% decline (S28: Rankability PDF) **[U]**. If accurate, the novelty premium on the *word* "agent" is fading. Sell outcomes, not "AI agents."

### Competition and capital signals
- Agentic application-layer funding: **$2.66B across 44 rounds YTD as of early April 2026; deal count down about 38%** (S7, 2026-04-07) **[U, secondary to Crunchbase/Tracxn]**. Q1 2026 AI venture funding was about $242B, dominated by foundation-model mega-rounds (S8, 2026-04-14) **[U]**.
- YC: secondary analyses estimate that about 60–80% of W26 companies are AI startups (S28: Extruct W26), and that about 70% of the Spring 2026 batch builds agents (S28: Mika Reyes) **[U]**. **VC-funded competition concentrates on horizontal and enterprise categories.** Small local and vertical data niches attract far fewer funded entrants, which is why they appear at the top of this ranking.
- Agent directories list thousands of agents. One count cites 2,105+ on a single directory (S28: RNWY 2026) **[U]**. One analysis counts **104,000+ agents across 15 registries** (S28: AgentMarketCap 2026-04-11) **[U]**.

### A new competition signal from this research (live data, verified today)
I checked 106 candidate .com names for the five businesses against the Verisign registry. **54 of the 106 (51%) were first registered in 2025 or 2026.** Some were registered within the last few weeks:
- permitcast.com and groundbreakleads.com: 2026-10-24
- certrove.com: 2026-10-12
- certcairn.com: 2026-10-15
- paidcadence.com: 2026-11-10

**[V, RDAP registry data, 2026-11-12]**

Of 16 permit-themed names, 12 are already registered, 10 of them since 2024. Domain registrations are not products, and many are speculative. Still, this is a fresh, hard signal that **builders are converging on permit and COI niches right now.** The window for "low competition" in these niches is measured in quarters, not years.

---

## Part 1 — Ten candidate businesses

Scoring scale: 1 = worst, 5 = best. Competition and Cost are scored so that **5 = lowest competition / lowest cost**. Autonomy measures how fully it runs without you.

### 1. AI receptionist / missed-call agent for home-service trades
- **Demand: high.** Trades lose revenue to missed calls, and dozens of vendors market to exactly this pain (S12, S13, S14, 2026).
- **Competition: very high.**
  - Product roundups compare 8–9 dedicated tools: Marlie AI and Trillet from $49/mo, Smith.ai paid plans from $150/mo, Goodcall, Rosie, Avoca at an estimated $1–3K/mo (S12, S14, S13, 2026) **[V, vendor/affiliate]**.
  - Field-service platforms (Housecall Pro, Jobber, ServiceTitan) integrate or bundle similar features.
- **Startup cost: low–moderate.** Voice costs about $0.07–0.33/min all-in on Vapi/Retell (S27: Dupple 2026) **[U]**. Each client needs call-flow setup, plus telephony and 10DLC fees.
- **Autonomy: medium.** Per-client onboarding, escalations, and "the bot said something wrong" support.
- **Verdict:** excluded. It's a race to a $49/mo floor against funded vendors.

### 2. Outbound "AI SDR" lead-gen service
- **Demand: falling.** Reported 50–70% annual churn. Reports say 11x and Artisan customers reverted to hybrid models, and domain reputations collapsed within about 90 days (S15, S16, 2026) **[U, vendor-written]**.
- **Competition: very high,** with well-funded incumbents.
- **Cost: moderate.** Sending domains, inbox warmup, data.
- **Autonomy: low.** Deliverability and reply handling need constant attention.
- **Verdict:** excluded.

### 3. Review-response / Google Business Profile agent
- **Demand: moderate.** Responding to reviews matters for local SEO, but willingness to pay is low. Tools range from **$5/mo Chrome extensions to $299/mo platforms**. One Capterra listing is $9.99/year (S17, 2026) **[V]**.
- **Competition: very high.** Birdeye, Podium and others bundle it.
- **Cost: very low. Autonomy: high.**
- **Verdict:** excluded. Commoditized, and the price ceiling is too low to be worth the acquisition cost.

### 4. Grant discovery and drafting agent for small nonprofits
- **Demand: solid,** with a large grant-seeking market.
- **Competition: high.**
  - Grantable: free tier, paid plans from about $50/mo.
  - Granted AI: from $29/mo.
  - Instrumentl: $179–$999/mo (figures conflict).
  - Source: S18, 2026 **[U, vendor comparisons]**.
- **Cost: very low.**
- **Autonomy: low–medium.** Proposals need human judgment, tailoring and relationships. A bad draft costs the client a funder relationship.
- **Verdict:** excluded on autonomy and competition.

### 5. B2B accounts-receivable follow-up agent (trades, distributors, agencies)
- **Demand: high and universal.** Late B2B payments are a perennial SMB problem.
- **Competition: medium–high and rising.**
  - Chaser: $45–399/mo.
  - Billabex, Paidnice, Monk, and Daylit (launched AR agents, reported 2026-09-26).
  - Enterprise vendors: HighRadius at $50K–$200K/yr.
  - Sources: S19, 2026 **[U, vendor comparison]**.
  - QuickBooks Online now includes a native **Intuit Assist Payments Agent** that drafts reminders for approval, on the Essentials tier and above (S20, 2026) **[V]**.
- **Cost: very low. Autonomy: high** once integrated with the accounting system.
- **Verdict:** retained as #5. Viable only as a sharp vertical wedge (see blueprint), because QuickBooks is moving into the basic version.

### 6. Subcontractor COI (certificate of insurance) compliance agent
- **Demand: established.** GCs and property managers must track subcontractor insurance. A single project can involve 40+ subcontractors (S21, 2026) **[V, vendor]**.
- **Competition: medium.** Many vendors exist: myCOI, Jones, BCS, TrustLayer, Certificial, CertCove, PaperBoss, Wardly, SubDoc. Pricing ranges:
  - Self-service: about $3–$10 per vendor per year.
  - Managed: about $10–$30 per vendor per year.
  - myCOI is cited at $400–800/mo (by a competitor).
  - Sources: S21, 2026 **[U, vendor]**.
  - Small GCs (5–50 subcontractors) are under-served by enterprise tools.
- **Cost: very low. Autonomy: high.** Document extraction plus scheduled email chasing is ideal agent work.
- **Verdict:** retained as #4.

### 7. Trade-specific state and local government ("SLED") bid-match agent
- **Demand: high.** State and local procurement is commonly cited at **about $1.5T/yr**. Procurement-addressable estimates are closer to $0.9–1T (S22, 2026) **[U, vendor-sourced]**. Small contractors struggle with fragmentation: 90,000+ buying entities (S22) **[U]**.
- **Competition: medium.** Horizontal alert services exist:
  - BidNet Direct: $599/yr for one state, $1,999/yr national (captured 2026-08-26).
  - BidPrime: about $1K–$10K/yr (estimates conflict).
  - GovSpend: quote-only.
  - Also Govly, HigherGov, GovBidWire, and others.
  - **New entrant:** Hubexo launched **Bid Ocean**, a trade-focused bid alert platform, in July 2026.
  - Sources: S22 **[V for BidNet capture and Bid Ocean launch; U for the rest]**.
- **Cost: very low. Autonomy: medium–high.** Portal scrapers break and need maintenance.
- **Verdict:** retained as #3.

### 8. Buy-box vacant-land seller lead feed (LandLead)
- **Demand: proven spend, unquantified size.**
  - Investors pay for PropStream ($99–$699/mo; Essentials $99, Pro $199, Elite $699; free skip-tracing on Pro/Elite) (S24, 2026-05-15 / Aug 2026) **[U, plan prices conflict across sources]**.
  - Done-for-you land lead services charge far more. Land AI is listed at **$3,575/mo for 50 leads/mo** (S24, Capterra, undated) **[U]**.
  - Land market tailwind: realtor.com launched land price estimates in April 2026, noting that the land market lags (S24, 2026-04-22) **[V]**.
  - **I found no reliable count of US land investors** **[unverified gap]**.
- **Competition: medium–low in the "scored, buy-box-filtered, mail-ready" middle.** PropStream, Propwire, BatchLeads and PropertyRadar are DIY list tools. Few products sit between $99 DIY and $3,575 done-for-you.
- **Cost: lowest of all,** because the engine already exists in this repo. **Autonomy: high.**
- **Verdict:** retained as #2.

### 9. Permit-triggered lead feeds for specific trades
- **Demand: high.**
  - Contractors already pay **$15–$120+ per *shared* lead** on Angi/HomeAdvisor. Roofing runs $40–$120, HVAC $35–$100 (S23, 2026) **[U, agency blogs; no official Angi pricing]**.
  - With 8–15% close rates, the effective cost per booked job is **about $400–$800+** (S23) **[U]**.
  - A permit is a hard, dated buying signal: a new pool, new construction, a reroof.
- **Competition: medium–low at the trade and metro level.**
  - Shovels is the national player. Its paid tiers are reported at $599/$999/mo, but its own pricing page contradicts itself (S23, 2026) **[U]**.
  - Apify lists 15+ permit scraper actors at **$3–$50 per 1,000 records** (S23, 2026) **[V]**. These are raw data for technical buyers, not ready-to-work trade lists.
  - Domain-registration activity shows new entrants arriving (Part 0).
- **Cost: very low.** Many cities publish permits on daily-updated open data portals: Chicago, NYC, Austin, SF (S23, 2026) **[V for Chicago "updated daily"; U for the others]**. **Autonomy: high.**
- **Verdict:** retained as #1.

### 10. Tax-sale surplus-funds lead feed for recovery specialists
- **Demand: niche but motivated.** Excess Elite charges **$300/mo for a Florida package** (S25, undated) **[U]**. Tax Sale Resources sells overage lists behind a membership (S25) **[V, no prices shown]**.
- **Competition: low–medium.**
- **Cost: very low. Autonomy: medium.** Many counties publish surplus lists as PDFs with inconsistent formats.
- **Legal: high.** Several states cap or restrict finder fees and claim-assignment practices. The buyer pool is small and changes often.
- **Verdict:** 6th place. Close, but demand is narrow and regulatory risk is high.

**Also screened and dropped early:**
- **Property-tax appeal agent.** Ownwell raised a $50M Series B in Feb 2026 (S26, 2026-02-25) **[V]**, and some states license tax consultants.
- **New-business-filing lead feeds.** Commoditized: Apify actors sell from $1.25 per 1,000 filings (S28: Apify listing) **[V]**.

---

## Part 2 — Ranking: why these five beat the other five

### Method
- **Weighted score** = Demand × 0.30 + Competition (inverted) × 0.30 + Cost (inverted) × 0.20 + Autonomy × 0.20.
- Demand and competition get the most weight because you asked for those first. Autonomy carries 20%, and any idea scoring ≤2.5 on autonomy is excluded outright because it's a core requirement.
- Scores are **my judgments [E]** based on the cited evidence above. The weights are a choice. Change them and re-rank if your priorities differ.

| # | Idea | Demand | Competition (5=low) | Cost (5=low) | Autonomy | **Score** | Result |
|---|---|---|---|---|---|---|---|
| 9 | Permit-triggered trade leads | 4 | 3.5 | 5 | 4 | **4.05** | **#1** |
| 8 | Vacant-land buy-box feed (LandLead) | 3.5 | 3.5 | 5 | 4.5 | **4.00** | **#2** |
| 7 | SLED bid-match by trade | 4 | 3.5 | 5 | 3.5 | **3.95** | **#3** |
| 6 | COI compliance agent | 4 | 3 | 5 | 4 | **3.90** | **#4** |
| 5 | B2B AR follow-up agent | 5 | 2 | 5 | 3.75 | **3.85** | **#5** |
| 10 | Surplus-funds feed | 2.5 | 4 | 5 | 3.5 | 3.65 | 6th |
| 1 | AI receptionist (trades) | 5 | 1 | 4 | 3 | 3.20 | out |
| 3 | Review-response agent | 3 | 1 | 5 | 5 | 3.20 | out |
| 4 | Grant writing agent | 4 | 2 | 5 | 2 | 3.20 | out (autonomy) |
| 2 | AI SDR service | 3 | 1 | 3 | 2 | 2.20 | out (autonomy) |

### Why the top five win
- **They sell a finished outcome on a schedule.** The customer gets a list, an alert or a chased certificate. They don't operate an agent. That fits the evidence that SMBs adopt AI broadly but rarely run agents themselves (S10, S11).
- **The agent does work that is boring for humans and easy to check.** Classifying a permit or bid, extracting fields from a COI, and sending a reminder are all checkable. Errors are low-stakes and visible, so the system can run with spot checks instead of a human in every loop.
- **Unit costs are tiny.** LLM classification of a few thousand records per month costs single-digit dollars (see blueprints). The main costs are your time and customer acquisition.
- **They avoid the two failure modes that sink the bottom five:**
  - Head-to-head competition with funded horizontal vendors: receptionist, SDR, reviews.
  - Work that needs a human in every loop: grants, SDR reply handling.

### Why the order is #1 > #2 > #3 > #4 > #5
- **#1 vs #2 is close.** Permits have clearer, priced demand (contractors already pay $15–$120 per shared lead). Land investor demand is real but unquantified. LandLead wins on cost and autonomy because it is already built, but loses on demand evidence.
  - **Ranking says permits first. Sequencing says land first,** because land is about 80% done and in your field. Both are true. The ranking answers "which opportunity is better in the abstract." The sequencing answers "what should *you* do Monday."
- **#3 trails on autonomy.** Government portals vary, change layouts, and sometimes require vendor registration to download documents. Bid Ocean's July 2026 launch shows a funded incumbent moving into "trade-focused bid alerts."
- **#4 trails on competition.** There are many COI vendors. Small GCs are under-served, but you'd be selling against established names, and trust matters for compliance software.
- **#5 has the best demand but the worst competition.** QuickBooks now ships a Payments Agent natively (S20). It survives only as a narrow vertical wedge.

### Honest critique of the whole list
- **"Low competition" usually means "harder distribution."** These niches are uncrowded partly because buyers are fragmented: thousands of small contractors and investors who don't browse Product Hunt. Your startup cost is low, but your **customer acquisition cost (CAC)** is the real unknown. Each blueprint has kill criteria tied to CAC.
- **Data-feed businesses face substitution risk.** If Shovels or PropStream drop prices or add the same scoring, your margin compresses. The defenses are local exclusivity, trade-specific scoring, and speed. None of them is permanent.
- **Your best unfair advantage is existing relationships, not code.** A realtor knows contractors, investors, property managers and title companies. Use your network for the first 10 customers of every blueprint before any automated acquisition.

---

## Shared foundation (used by Blueprints 1–3; parts reused by 4–5)

Build this once. It generalizes what `landlead/` already does.

```
          ┌─────────────── Scheduler (APScheduler / cron) ───────────────┐
          │                                                               │
 Sources ─┤  Ingest adapters (ArcGIS, Socrata, RSS, HTML, PDF)            │
 (public  │      ↓ robots.txt + rate limit + per-source health check      │
  data)   │  Normalize → canonical record (APN / permit # / bid ID)       │
          │      ↓                                                        │
          │  Dedup + merge  →  SQLite/Postgres                            │
          │      ↓                                                        │
          │  LLM agent step (classify, extract, score, summarize)         │
          │      ↓ confidence < threshold → review queue                  │
          │  Per-customer filters (buy-box / trade / geography)           │
          │      ↓                                                        │
          │  Delivery: email digest, CSV, Google Sheet, webhook/Zapier    │
          │      ↓                                                        │
          │  Billing (Stripe) · Usage metering · Health alerts to you     │
          └───────────────────────────────────────────────────────────────┘
```

**Autonomy mechanisms built into the core:**
1. **Source health monitor.** Every adapter reports its record count per run. If a source returns 0 records, or fewer than 30% of its trailing average, the run is marked degraded, you get an alert, and customers' digests note "County X delayed." Silent data loss is the #1 killer of data businesses.
2. **Confidence-gated review queue.** The LLM returns a confidence score. Records below threshold (for example 0.7) go to a queue that you clear in 10 minutes a week, instead of reaching customers.
3. **Self-serve everything:** Stripe Checkout, Stripe Customer Portal for plan changes and cancellations, and a filter preferences form. No human is needed to sign up, change or cancel.
4. **Weekly self-report to you:** records ingested, sources degraded, review queue size, MRR, churn, top customer complaints (LLM-summarized from replies).
5. **Auto-replies:** customer email replies go through an LLM triage. FAQs get answered automatically, and anything else is forwarded to you.

**Shared monthly platform cost [E]:**
- VPS (Hetzner/DigitalOcean class): $6–$24
- Transactional email (Postmark/Resend class): $0–$20
- Backups/object storage: $1–$5
- Uptime monitor: $0–$10
- LLM (see per-blueprint): under $10–$40
- **Total: about $15–$100/mo for all three data products combined**

The basis for these is typical published pricing from these vendor classes as I understand it. I did **not** verify these specific vendors' prices today, so confirm before buying.

**Model cost basis:**
- Claude Haiku 4.5 at $1 / $5 per million input/output tokens, with batch processing about 50% off (S27: MetaCTO 2026) **[V, corroborated across sources]**.
- Newer model generations may be cheaper per token, but third-party figures conflict (S27) **[U]**.
- Per-record classification at about 1,500 input + 200 output tokens costs about $0.0025 per record on Haiku-class pricing **[E: arithmetic on the token prices above]**.

---

# Blueprint 1 — Permit-triggered lead feeds for specific trades

## 1.1 Problem, customer, offer

**Problem.** Contractors buy shared leads from Angi/HomeAdvisor at $15–$120+ each, with 8–15% close rates (S23) **[U]**. These leads go to 3–5 competing contractors at once. Meanwhile, public permit records announce, days to weeks ahead, who is about to need adjacent work:
- A new pool permit means the owner needs a pool fence, landscaping, outdoor lighting, a patio and screening.
- A new single-family construction permit means the builder needs blinds, security, landscaping, gutters and a garage door.
- A reroof permit means the owner may need gutters, solar or attic insulation.
- An electrical service upgrade may mean an EV charger, a generator or solar.

Nobody packages these signals by trade, cleaned, with owner mailing addresses, in a form a small contractor can act on Monday morning.

**Target customer.** Owner-operated companies (1–20 employees) in **adjacent trades** that sell to a homeowner or builder *after* a primary permit:
- Pool fence and enclosure installers
- Landscapers and hardscapers
- Gutter companies
- Window treatment and blinds dealers
- Security and low-voltage installers
- Solar installers
- Residential cleaning companies (post-construction clean)
- Mortgage, insurance and home-warranty agents (new construction)

Start with **one metro and two trades.**

**Offer.**
- **"Fresh Permit Feed — [Trade], [Metro]":** every Monday and Thursday, a digest of new permits matching the trade.
- Each lead includes: permit type, issue date, project value, address, owner name, owner *mailing* address (from the parcel record), contractor of record, an LLM-written "why this is a lead for you" line, and a 1–100 fit score.
- Delivery formats: email, CSV, Google Sheet, and optional Zapier/webhook into their CRM.
- **Exclusivity option:** a limited number of subscribers per trade per ZIP cluster, which is the core moat.
- Optional add-on: print-ready mail-merge file plus suggested postcard copy.

## 1.2 How the agentic system operates

**Pipeline (runs twice weekly, plus a daily ingest):**
1. **Ingest.** Pull permits from each city or county open data endpoint. Many cities use Socrata (SODA) APIs with daily updates; Chicago documents daily updates (S23) **[V]**. For counties without an API, scrape HTML/PDF permit reports at polite rates, honoring robots.txt, using the LandLead `BaseScraper`.
2. **Normalize** into a canonical schema: permit_id, jurisdiction, issued_at, type, subtype, description, valuation, address, parcel_id, contractor.
3. **Enrich.** Join to parcel data (ArcGIS/statewide cadastral, which LandLead already does) for owner name and mailing address, and flag absentee owners (mailing address ≠ site address).
4. **Agent step (LLM):** read the free-text permit description and classify it against a trade taxonomy. For example, "NEW INGROUND POOL W/ SPA 18X36" maps to pool → leads for fence, landscape, lighting, screen. It also extracts the project scale and writes the one-line "why you" text. Confidence below 0.7 goes to the review queue.
5. **Score per trade** using a transparent formula: recency, project value, trade-relevance confidence, owner-occupied vs builder, and distance from the customer's service area.
6. **Route** to subscribers according to their filters and exclusivity territory.
7. **Deliver** the digest, sheet and webhook. Log opens and clicks.
8. **Feedback loop:** each lead has 👍/👎 links, and the clicks tune the scoring weights per customer monthly. An "LLM reviews its own misses" job re-reads permits flagged 👎 and suggests taxonomy fixes for you to approve.

**Tools and platforms [E: recommended stack]:**
- Python, FastAPI and APScheduler (reuse the `landlead/` structure)
- Postgres (or SQLite to start)
- Claude Haiku-class model via API for classification, with batch mode for cost
- Socrata SODA API, ArcGIS REST
- Postmark/Resend for email
- Stripe Checkout + Customer Portal
- Google Sheets API for sheet delivery
- Zapier/Make webhook for CRM delivery
- Lob/PostGrid for an optional automated postcard add-on (verify pricing)

**Revenue model [E]:**
- Starter: one trade, one metro, non-exclusive, **$99/mo**
- Pro: one trade, one metro, up to 3 subscribers per ZIP cluster, owner mailing addresses and score, **$199/mo**
- Exclusive: sole subscriber for the trade in chosen ZIPs, **$399–$599/mo**
- Postcard autopilot: pass-through mail cost + 25%

**Rationale:** one booked job from the feed covers months of subscription, because shared-lead costs are about $400–$800 per booked job (S23) **[U]**. Pricing sits well below Shovels' reported $599+ entry tier, which is built for data teams (S23) **[U]**.

## 1.3 Startup cost (itemized)

| Item | Cost | Basis |
|---|---|---|
| LLC formation | $50–$500 one-time | **[E]** State filing fees vary. Check your state's Secretary of State. |
| Registered agent | $0–$125/yr | **[E]** $0 if you serve as your own. |
| Domain (.com) | ~$11–$20/yr | **[E]** Typical registrar pricing. |
| Business email (Google Workspace class) | ~$7–$8/mo | **[E]** Confirm current pricing. |
| Shared core build (if not reusing LandLead) | $0 cash; ~40–60 hrs | **[E]** You already have most of it. |
| Permit adapters for first metro (3–6 jurisdictions) | $0 cash; ~10–20 hrs | **[E]** Socrata is quick; HTML/PDF sources are slower. |
| Landing page + Stripe setup | $0–$50 | **[E]** Static site on Cloudflare Pages (your repo already deploys via Wrangler). |
| Legal: ToS, privacy, data-use restrictions | $0 (template) – $1,500 (attorney) | **[E]** Recommended: a 1-hour attorney review of the data-use clauses (see 1.5). |
| Tech E&O / cyber insurance (optional at launch) | $35–$110/mo | **[V]** Averages of $60–$67/mo; sole-proprietor quotes from about $25–$35/mo (S27: TechInsurance, MoneyGeek, 2026). |
| Sample-feed outreach mailing (100 postcards to target contractors) | ~$60–$120 | **[E]** About $0.60–$1.20 each, all-in, via a print-and-mail API. |
| **Total cash to launch** | **~$150–$700** (more if you add an attorney and first-year insurance) | **[E]** |

**Ongoing monthly [E]:**
- Platform share: $15–$40
- LLM: for 3,000 permits/mo × $0.0025 = **about $7.50**, or about $4 with batch mode
- Email: $0–$15
- Stripe fees: about 2.9% + $0.30 per charge (standard US card pricing; confirm)
- Insurance (if carried): $35–$110
- **Total: about $60–$180/mo** before marketing

**Break-even:** 1–2 Pro subscribers **[E]**.

## 1.4 Running autonomously

| Function | Automated how | Human time |
|---|---|---|
| Data ingest | Scheduled adapters, health monitor, auto-retry | 0 unless a source breaks |
| Classification and scoring | LLM with a confidence gate | ~10 min/wk reviewing the queue |
| Delivery | Scheduled digests, sheet sync, webhooks | 0 |
| Signup, billing, cancellation, territory selection | Stripe Checkout/Portal; a territory map shows exclusive ZIPs already taken | 0 |
| Support | LLM triages replies, answers FAQs, escalates the rest | ~15 min/wk |
| Acquisition | See below | 1–3 hrs/wk at first, then trending to ~0 |
| Source maintenance | Health alerts → you fix the adapter | ~1–2 hrs/month per metro (**[E]**: city portals change a few times a year) |

**Autonomous acquisition engine:**
1. **Free weekly teaser.** Anyone can subscribe to a weekly "Top 5 new [trade] permits in [metro]" email with addresses partially redacted. The full feed is one click away. This is the main funnel.
2. **Programmatic SEO pages,** for example "New pool permits in [County] — updated weekly," with aggregate counts and charts per jurisdiction and permit type. These are generated from your own data, so they're unique content, which makes them more likely to rank than generic AI pages.
3. **Contractor list from the data itself.** Permits list the contractor of record. Primary-trade contractors (pool builders, GCs) are *referral partners*. Offer them a free feed of their own competitors' activity in exchange for a link or intro, or a revenue share for referring adjacent trades.
4. **Lead magnet postcards** to adjacent-trade contractors, with a QR code linking to a free week of the feed. Postcards are low-volume, permission-free and have no deliverability risk. **Avoid cold-email blasts:** AI SDR deliverability collapse is documented (S16) **[U]**.

**Where human oversight is still needed, and why:**
- **Source breakage.** Only a human can judge whether a city changed its portal or stopped publishing. The monitor detects the problem; you fix it.
- **Taxonomy changes.** Approve suggested taxonomy changes so the LLM doesn't drift. Its classifications *are* the product.
- **Exclusivity disputes and refunds.** These are rare, but they involve judgment and money.
- **Compliance decisions:** new jurisdictions or data types (see 1.5).

## 1.5 Risks and compliance (read before launch)
- **Terms of use.** Socrata/open-data portals generally permit reuse, but check each portal's terms. Some county portals prohibit commercial redistribution. Prefer official open data. For HTML scraping, honor robots.txt and ToS, as `landlead/COMPLIANCE.md` already requires.
- **How customers contact owners.** Mail is the safest channel. Phone outreach by your customers falls under the TCPA and Do-Not-Call rules. AI-voice calls require prior express consent under the FCC's Feb 2024 ruling (S27: FCC, 2024-02-08) **[V]**. Put a ToS clause making customers responsible for contact-law compliance, and don't sell phone numbers at launch.
- **FCRA.** Prohibit any use of the data for credit, insurance, employment or tenancy eligibility decisions. That keeps you clear of consumer-reporting-agency status. Get a lawyer to confirm the wording.
- **Competition.** New domains in this exact niche were registered in Oct 2026 (Part 0). Move fast to lock up exclusivity territories.

**Kill criteria [E]:**
- Fewer than 3 paying subscribers in a metro after 60 days and 300 postcards / 1,000 teaser subscribers' worth of effort.
- Monthly churn above 15% after month 3.

## 1.6 Names: availability checks

| Name | .com status (live RDAP, 2026-11-12) | Web conflict screen | Notes |
|---|---|---|---|
| **PermitWake** | **Not registered** **[V]** | No matching products found **[V, web search]** | Evokes "wake of the permit." Distinctive. My top pick. |
| **PermitJolt** | **Not registered** **[V]** | No matches **[V, web search]** | Energetic, slightly gimmicky. |
| **PermitRoost** | **Not registered** **[V]** | No matches **[V, web search]** | Softer, community feel. |
| **BreakGround Leads** (breakgroundleads.com) | **Not registered** **[V]** | No matches **[V, web search]** | Descriptive. Note that *groundbreakleads.com* was registered 2026-10-24, a likely competitor. |
| Taken (for reference) | permitping (2025-06-28), permitsignal (2025-06-22), permitpulse (2024), permitdrop (2026-01), permitcast (**2026-10-24**), permitbeat (2026-03), permitlode (2026-10-01), freshpermit (2026-08), permitharbor (2026-08), firstpermit (2003), permitfirst (2019) **[V]** | — | Evidence of a crowding name space. |

**You must confirm yourself:**
- Instagram, X, Facebook, LinkedIn and TikTok handles. I could not check these: social sites block automated lookups.
- A USPTO trademark search at tmsearch.uspto.gov, in classes **035** (advertising/business info) and **042** (SaaS). The USPTO tool blocked scripted queries, so my screen was web-search only, which misses unpublished filings and common-law users.
- The .co/.io/.ai variants (not checked).

## 1.7 Branding

- **Positioning statement:** *"Know who's building before your competitors do. Fresh permits, sorted for your trade, twice a week."*
- **Against Angi:** "Not shared. Not stale. From the public record, the day it's issued."
- **Tone:** plainspoken, contractor-to-contractor, numbers-forward. No "AI" in the headline. The AI is the engine, not the pitch, because search interest in the word is fading (Part 0).
- **Visual direction:** jobsite utility.
  - Palette: **Safety Orange #F26B1D** (accent), **Blueprint Navy #12263A** (primary), **Concrete #E7E5E0** (background), **Rebar Gray #5B6166** (text-secondary).
  - Typography: a condensed industrial sans for headlines (e.g., *Barlow Condensed* or *Oswald*), with *Inter* for body text.
- **Logo concepts:**
  1. A permit-card rectangle with a corner fold, plus a small sunrise arc (the "wake").
  2. A survey-stake flag with a ripple line behind it.
  3. A wordmark with the "W" built from two roofline chevrons.
  - All three must work as a 32px favicon and on a truck magnet.
- **Signature asset:** the twice-weekly digest itself. A clean table, an orange "NEW" tag, and a score badge. It's the product and the brand at the same time.

---

# Blueprint 2 — Buy-box vacant-land seller lead feed (built on LandLead)

## 2.1 Problem, customer, offer

**Problem.** Land investors buy raw lists (PropStream Essentials from about $99/mo, Pro about $199/mo, Elite about $699/mo, with free skip-tracing on Pro/Elite) (S24) **[U, prices conflict]**. Then they spend hours each week list-stacking, filtering acreage and vacancy, removing improved parcels, deduping, and spotting tax-delinquent or probate signals.

The done-for-you alternative is expensive: Land AI is listed at $3,575/mo for 50 leads (S24) **[U]**. **The middle is empty:** a weekly, scored, mail-ready list of buy-box tracts, built from public records, at a few hundred dollars.

**Target customer:**
- Small land-flipping operators (1–5 people) running direct-mail campaigns in Eastern US counties
- Land-investing course graduates (a large, active, course-driven community; size unquantified **[unverified gap]**)
- Land brokers and realtors who prospect for listings

**Offer.**
- **"Weekly Buy-Box List":** each week, every vacant parcel of 5–100 acres (configurable) in the customer's chosen counties that newly shows a motivation signal (tax delinquency, tax-deed auction listing, probate filing, code violation, absentee or out-of-state owner, long hold period).
- Each record is scored 1–100 with a per-signal breakdown, deduped across sources by APN, and delivered as mail-merge-ready CSV plus a matching letter template.
- **County exclusivity** is available, because investors hate competing with the same list.
- Add-ons:
  - Skip-tracing pass-through via the existing connector hooks, at cost + margin. PropStream's reference rate is $0.12/contact on Essentials (S24) **[V, vendor]**.
  - Automated mail via a print API.
  - A "comps snapshot" per county from public sales data.

**What already exists in this repo:**
- `landlead/` already scrapes statewide parcel layers (FL, NY, VA, plus others configured).
- It already harvests tax-deed/tax-lien auctions, legal notices, probate and code violations.
- It already scores, dedups by APN, enforces the 5–100-acre vacant buy-box, and generates signal-matched letters.
- **What's missing:** multi-tenant customer filters, delivery, billing and the acquisition funnel. This is why startup cost is lowest here.

## 2.2 How the agentic system operates

1. **Ingest** (existing): statewide cadastral layers, auction calendars, RSS legal notices, probate and code-violation adapters.
2. **Agent step (new):** LLM reads unstructured legal notices and auction PDFs. It extracts APN, owner, amounts and dates; maps them to parcels; and writes a one-line "motivation summary" (e.g., "Out-of-state heirs; 3 years delinquent; 22 ac wooded, road frontage"). Records below the confidence threshold go to review.
3. **Score** (existing transparent 1–100 score), plus a new "freshness" boost for signals that appeared this week.
4. **Per-customer slicing:** counties, acreage band, minimum score, exclusions (wetlands/flood if layers are available), and suppression of records already sent to that customer.
5. **Deliver** every Monday: CSV, Google Sheet and letter merge file. Optional auto-mail drop via print API, with customer approval for each batch.
6. **Feedback:** customers mark "deal / dead / wrong data." The monthly re-weighting suggests score changes, which you approve.

**Revenue model [E]:**
- Per county cluster (up to 3 counties), non-exclusive: **$149/mo**
- Exclusive county: **$399/mo per county**
- Done-for-you mail autopilot: mail pass-through + 20–30% margin
- Skip-trace pass-through: cost + $0.05/record
- **Positioning:** costs about the same as PropStream Pro, but saves 5–10 hours a week of list work **[E]**. Costs about 1/10th of done-for-you services.

**Optional second revenue stream (your domain):** as a licensed realtor, you can work the leads that customers *pass on* in non-exclusive counties, or refer listing opportunities. **Caution:** disclose this dual role and keep exclusive customers' records off-limits. Otherwise you undermine trust in the product. Check your state's real-estate commission rules on lead resale and referral fees before doing this.

## 2.3 Startup cost (itemized)

| Item | Cost | Basis |
|---|---|---|
| Engine (scrape/score/dedup/letters) | **$0 — already built** | This repo |
| Multi-tenant filters + delivery + Stripe | $0 cash; ~25–40 hrs | **[E]** |
| LLC, domain, email | ~$70–$650 | **[E]** Same basis as Blueprint 1 |
| Hosting (VPS; the repo already has Docker) | $6–$24/mo | **[E]** |
| LLM extraction (about 5,000 notices/mo × $0.0025) | ~$12.50/mo (~$6 batch) | **[E]** Arithmetic on S27 rates |
| Attorney review of data-use ToS + skip-trace resale terms | $0–$1,500 | **[E]** Recommended because skip-trace data licenses restrict resale |
| Launch marketing (see below) | $0–$300 | **[E]** |
| **Total cash to launch** | **~$100–$600** (more with an attorney) | **[E]** |

**Ongoing monthly [E]:** about $40–$150 (hosting, LLM, email, Stripe fees, optional insurance). **Break-even: 1 subscriber.**

## 2.4 Running autonomously

- **Already autonomous:** the pipeline runs on APScheduler with fault-tolerant adapters (see `landlead/README.md`).
- **To add:**
  - The source health monitor from the shared core
  - A self-serve county picker with an exclusivity map
  - Stripe Portal
  - LLM reply triage
  - Weekly owner report

**Autonomous acquisition:**
1. **Free "County Land Pulse" report.** A monthly auto-generated public page per county: count of delinquent vacant tracts by acreage band, auction calendar, median $/acre where available. This is SEO plus credibility, and land investors search by county.
2. **Sample list.** Ten free scored records for any county, delivered instantly after email capture. This is the highest-converting "show, don't tell" asset for data products **[E]**.
3. **Community presence.** Land investors gather in course communities and forums (e.g., BiggerPockets land forums, Facebook and Skool groups). Post the County Land Pulse charts, never spam. This is a human task, about 1 hr/week, and the least autonomous part. Treat it as a launch phase, not a permanent job.
4. **Affiliate program.** Land course creators and coaches get 20–30% recurring. Their students need lists on day one.

**Human oversight still needed:**
- **Adapter breakage:** state GIS endpoints change. This already happened with your ArcGIS robots.txt and VA host fix in commit `2130e60`. About 1–2 hrs/month **[E]**.
- **Approving letter-template and score changes:** the content goes out under customers' names.
- **Compliance gatekeeping** for any newly enabled restricted source. `COMPLIANCE.md` keeps ToS-restricted and licensed sources disabled by default; keep it that way.
- **Exclusivity and refund decisions.**

## 2.5 Risks and compliance
- **Shared lists lose value.** If 5 investors mail the same owner, response rates fall and customers churn. **County exclusivity is the product's core defense.** Cap non-exclusive seats per county (e.g., 3).
- **Skip-trace data** comes under vendor license terms and permissible-purpose rules. Pass it through under the vendor's terms; don't warehouse and resell it without a license that allows that.
- **Mail and phone.** Mail is safest. Customers' calling falls under TCPA/DNC, so include it in the ToS (as in 1.5).
- **Real-estate license:** see the dual-role caution in 2.2.

**Kill criteria [E]:** fewer than 5 paying counties after 90 days, or monthly churn above 12%.

## 2.6 Names: availability checks

| Name | .com status (live RDAP, 2026-11-12) | Web conflict screen | Notes |
|---|---|---|---|
| **AcreFeed** | **Not registered** **[V]** | No product found; adjacent brands exist: AcreValue, Acres.com **[V, web search]** | Clear and descriptive. Moderate confusion risk with "Acre-" land-data brands. Have a trademark attorney weigh in. |
| **TractFeed** | **Not registered** **[V]** | No matches **[V, web search]** | Less crowded prefix. My top pick. |
| **OwnerLode** | **Not registered** **[V]** | No matches **[V, web search]** | "Lode" = rich vein. Memorable, less literal. |
| **BuyBox Land** (buyboxland.com) | **Not registered** **[V]** | Not screened | Speaks investor jargon. Weaker as a long-term brand. |
| **AcreQuarry** | **Not registered** **[V]** | Not screened | Backup. |
| Taken | acresignal (2025-09), tractscout (2026-07), deedline (2025-06), acrewire (2026-02), acrecast (2026-08), acreledger (2026-07), landlode (2026-05), parcelpulse (2020), parcelhound (2017) **[V]** | — | — |

**Brand-architecture note:** you already own the *FossilLedger* brand (this repo). Consider "TractFeed by FossilLedger," with FossilLedger as the parent data company for Blueprints 1–3. That gives one trust anchor and one legal entity.

**You must confirm yourself:** social handles; USPTO classes 035/036 (real-estate info)/042; .co/.io variants.

## 2.7 Branding
- **Positioning:** *"Your buy-box, already filtered. Every Monday."* Or, against PropStream: "Lists are cheap. Clean lists are rare."
- **Tone:** quiet confidence, investor-literate. Use their vocabulary (buy-box, list-stacking, APN, blind offer). Be dry, factual and transparent about scoring. Investors distrust hype.
- **Visual direction:** survey-plat / topographic.
  - Palette: **Topo Green #2F5D50** (primary), **Field Tan #D9C9A3** (background accent), **Ink #1D1F21** (text), **Survey Red #B23A2E** (score/priority accent).
  - Typography: a slab serif for the wordmark (e.g., *Roboto Slab* or *Zilla Slab*), suggesting deeds and plats, with *IBM Plex Sans* for data tables.
- **Logo concepts:**
  1. A parcel outline (irregular polygon) inside a topographic contour.
  2. A "T" whose crossbar is a surveyed property line with corner pins.
  3. A stacked-paper icon (the "list") with a contour line on the top sheet.
- **Signature asset:** the per-signal score breakdown chip ("Tax-delinq +25 · Absentee +15 · 3yr hold +10"). It makes the scoring legible and differentiates from black-box lists.

---

# Blueprint 3 — Trade-specific state and local bid-match agent

## 3.1 Problem, customer, offer

**Problem.** Small contractors (paving, roofing, janitorial, landscaping, HVAC service, fencing, painting, demolition) could win state and local government work. The market is commonly cited at about $1.5T/yr, with procurement-addressable spending about $0.9–1T (S22) **[U]**. But opportunities are scattered across about 90,000 buying entities (S22) **[U]**: state eProcurement portals, county purchasing pages, school districts, utilities, housing authorities.

Horizontal alert services use keyword matching across everything: BidNet Direct at $599/yr per state, $1,999/yr national (S22, captured 2026-08-26) **[V]**. The result is noisy, and the contractor still has to read 40-page bid packets to decide bid or no-bid.

**Target customer.** Trade contractors with $500K–$10M revenue, in one state or region, who have the capacity for public work but no estimator or capture person to monitor portals. Start with **one trade and one state**; janitorial or paving are good first choices.

**Offer.**
- **"Daily Bid Brief — [Trade], [State]":** only relevant bids. Each one includes:
  - A 5-line LLM brief: scope, quantities, location, due date and time, pre-bid meeting (and whether it's mandatory), bonding and insurance requirements, licensing/certification requirements, set-asides.
  - A **bid/no-bid fit score** against the customer's profile (capacity, bonding limit, service radius, certifications).
  - Link to the official source and a calendar file (.ics) for deadlines.
- **Weekly "awards" digest:** who won similar bids and at what price, where agencies publish it. This is competitive intelligence that horizontal tools treat as an upsell.

## 3.2 How the agentic system operates

1. **Source registry:** a curated list of public procurement pages for the state. Start with the state eProcurement portal's public listings plus the 20–40 largest counties, cities and school districts. Build adapters for RSS/JSON where offered and polite HTML scraping elsewhere.
2. **Ingest** new solicitations daily. Download bid documents only where public and permitted.
3. **Agent step:**
   - (a) Classify relevance to each trade taxonomy.
   - (b) Extract structured fields from the solicitation text and PDF, using a Sonnet-class model for long documents and a Haiku-class model for triage.
   - (c) Compare against the customer profile and compute the fit score.
   - (d) Write the brief.
   - (e) Flag "mandatory pre-bid" items prominently, since missing one disqualifies the bidder.
4. **Deliver** the daily email, .ics and dashboard.
5. **Awards tracker:** re-check closed solicitations for award notices and tabulations, extract winner and price, and build a per-agency pricing history over time. This becomes your moat.
6. **Feedback:** "Bidding / Not for us / Won / Lost" buttons. Outcomes refine the fit model and drive testimonials.

**LLM cost [E]:**
- Triage of 3,000 solicitations/mo on Haiku-class: about $7.50.
- Deep extraction of about 300 relevant packets × 20K tokens on Sonnet-class ($3/$15 per M (S27) **[V]**): about $18–$25.
- **Total about $30/mo per state.**

**Revenue model [E]:**
- Solo trade, one state: **$79/mo**
- Team (3 users, profile tuning, awards history): **$149/mo**
- Multi-state: +$49/state
- **Rationale:** cheaper than or equal to BidNet single-state ($599/yr ≈ $50/mo), but trade-tuned with briefs and fit scores. That's the "save 5 hours of reading a week" value. Undercut BidPrime and GovSpend, which reportedly run $1K–$24K+/yr (S22) **[U]**.

## 3.3 Startup cost (itemized)

| Item | Cost | Basis |
|---|---|---|
| Shared core (from Blueprints 1–2) | $0 incremental | Reuse |
| Source adapters, one state (~25–40 sources) | $0 cash; ~30–50 hrs | **[E]** The largest build item. |
| PDF extraction pipeline | $0 cash; ~10 hrs | **[E]** |
| LLC/domain/email (if a separate brand) | $0 (under the parent LLC) – ~$70 | **[E]** |
| LLM during build and test | ~$20–$50 one-time | **[E]** |
| Launch outreach: postcards to 200 trade contractors from state license lists | ~$120–$240 | **[E]** |
| **Total cash** | **~$150–$400** | **[E]** |

**Ongoing [E]:** about $50–$150/mo (LLM about $30, hosting share, email, insurance share). **Break-even: 1–2 subscribers.**

## 3.4 Running autonomously
- **Fully automated:** ingest, triage, extraction, briefs, delivery, billing and FAQ support (same core).
- **Autonomous acquisition:**
  1. **Public "Open Bids for [Trade] in [State]" pages,** updated daily, with summaries teased and full briefs gated. These pages capture long-tail search ("janitorial bids [county]").
  2. **License-list postcards.** State contractor-license databases are public in many states (verify per state). Send them a QR code linking to a free 14-day brief.
  3. **Partners:**
    - Surety bond agents: their clients need bids to bond.
    - Small Business Development Centers / PTAC (APEX Accelerator) counselors, who refer small firms to tools.
    - Trade associations, which can resell it as a member benefit.
- **Human oversight still needed:**
  - **Source maintenance** is the heaviest of the five: government sites change and some add logins. Budget about 2–4 hrs/month per state **[E]**.
  - **Spot-check briefs weekly.** A wrong due date or a missed mandatory pre-bid is the one error that destroys trust. Show the source excerpt next to every extracted deadline, and add a disclaimer: "verify all requirements in the official solicitation."
  - **ToS judgment** for each new source (below).

## 3.5 Risks and compliance
- **Portal terms.** Some aggregator networks (e.g., BidNet) are themselves commercial and restrict scraping and redistribution. **Ingest only from the agencies' own public pages and official open-data feeds.** Link to the official documents rather than re-hosting them.
- **Liability for missed details.** Disclaim this in the ToS. Errors-and-omissions insurance is more relevant here than in any other blueprint.
- **Competition is moving.** Hubexo's Bid Ocean (July 2026) targets trade-focused bid alerts (S22) **[V]**, and GovBidWire aggregates 45+ state and local portals (S22) **[V, listing]**. Differentiate on depth in one state and one trade, with briefs, fit scores and awards pricing history.

**Kill criteria [E]:** fewer than 5 subscribers within 90 days in the first state and trade, or source upkeep above 6 hrs/month.

## 3.6 Names: availability checks

| Name | .com status (live RDAP, 2026-11-12) | Web conflict screen | Notes |
|---|---|---|---|
| **LocalBidHQ** | **Not registered** **[V]** | No matches **[V, web search]** | Clear, SEO-friendly. A little generic. |
| **BidSextant** | **Not registered** **[V]** | No matches **[V, web search]** | Navigation metaphor ("find your bearing"). Distinctive. My top pick. |
| **BidMarrow** | **Not registered** **[V]** | Not screened | "Get to the marrow of the bid." Odd, but memorable. |
| **RFPcairn** (rfpcairn.com) | **Not registered** **[V]** | Not screened | Cairn = trail marker. "RFP" is the wrong term for many construction bids (IFB/ITB). |
| **Avoid:** TradeBidWire / CivicBidWire | Not registered **[V]** | **GovBidWire exists** in this exact category **[V, web search]** | Too close. Likely confusion. |
| Taken | bidhound (2005), countybid (2005), bidbeacon (2017), tenderhound (2019), sledbids (2026-05), bidscout (2026-03), bidbrief (2026-03), bidfitter (2026-01), bidlantern (2026-03), bidgrove (2026-01), bidkeel (2026-08), bidcairn (2026-09), bidquill (2026-06), bidtrellis (2026-09), rfpharbor (2026-08) **[V]** | — | Heavy 2026 registration activity. |

**You must confirm yourself:** social handles; USPTO classes 035/042; a check that no state-specific "LocalBid" programs exist (some agencies brand their own portals).

## 3.7 Branding
- **Positioning:** *"Every public bid for your trade in [State]. Read for you. Scored for you."* Against keyword alerts: "Fewer alerts. Better bids."
- **Tone:** competent, civic, precise, like a good estimator. Deadlines are sacred, so the brand promises reliability, not excitement.
- **Visual direction:** navigational and civic.
  - Palette: **Capitol Blue #1F3A5F** (primary), **Brass #B08D57** (accent; the sextant), **Paper #F7F5F0** (background), **Deadline Red #C0392B** (used only for due-date alerts).
  - Typography: *Source Serif* for headlines (civic gravitas), *Source Sans* for body text.
- **Logo concepts:**
  1. A minimal sextant arc with a single star point, the star doubling as a map pin.
  2. A capitol dome reduced to an arc, crossed by a compass needle.
  3. A wordmark with the "x" in Sextant drawn as crosshairs.
- **Signature asset:** the brief card, with a fit-score dial, a red deadline strip, and a "Mandatory pre-bid" flag.

---

# Blueprint 4 — Subcontractor COI compliance agent

## 4.1 Problem, customer, offer

**Problem.**
- General contractors and property managers must hold current certificates of insurance (ACORD 25) from every subcontractor and vendor, with the right limits, additional-insured status, waiver of subrogation and policy dates.
- Lapses can shift liability to the GC. For example, an uninsured sub's injury claim can fall on the GC's policy (S21, 2026) **[V, vendor guidance]**.
- Small GCs track this in spreadsheets, and certificates expire silently.
- Enterprise tools are priced for large firms: myCOI is cited at $400–800/mo by a competitor (S21) **[U]**. Many small-firm tools still require manual data entry (S21) **[U, vendor opinion]**.

**Target customer:**
- Residential and light-commercial GCs and remodelers with 10–80 active subs.
- Small and mid property-management firms (vendors and contractors entering their buildings).
- Event venues.
- **Your network fit:** property managers and builders you know through real estate.

**Offer.** "Forward it and forget it" COI compliance:
1. The customer (or their sub) emails COIs to a dedicated inbox (e.g., coi@customer.yourdomain).
2. The agent extracts all fields and checks them against the customer's requirement template.
3. It emails the sub (and the sub's insurance agent) about deficiencies or upcoming expirations at 30/14/7/0 days, using escalating templates.
4. It maintains a live compliance dashboard, plus a weekly "who's non-compliant" report for the GC, to use before releasing payments.

**Pricing [E]:**
- **$49/mo up to 25 vendors**, **$99/mo up to 75**, **$199/mo up to 200**.
- That's about $8–$24/vendor/yr. It sits inside the cited self-service ($3–$10) to managed ($10–$30) range (S21) **[U]**, at the managed end because the agent does the chasing.

## 4.2 How the agentic system operates
1. **Inbound email** via a parsing provider or IMAP polling. Attachments go to storage.
2. **Extraction:** a vision-capable LLM reads the ACORD 25 PDF or image and returns JSON with: insured, producer (agent) contact, each policy (type, carrier, number, effective and expiration dates, limits), additional insured / waiver checkboxes, certificate holder, and the description of operations. Confidence below threshold, or an unreadable scan, goes to review.
3. **Rules engine (deterministic, not LLM):** compare against the customer's template, for example GL $1M/$2M, auto $1M, WC statutory, umbrella $1M, AI + waiver required, holder name exact. **Keep compliance judgments in code, not in the model.** It's auditable and repeatable.
4. **Chasing agent:** sends deficiency and renewal emails from the customer's branded subdomain. It parses replies, re-checks attachments when a new COI arrives, and stops chasing once the sub is compliant.
5. **Endorsement caveat handling.** An ACORD 25 is evidence of coverage, not the coverage contract. Additional-insured status actually lives in policy endorsements. The template can require the endorsement page, and the agent requests it automatically.
6. **Dashboard and reports:** status per vendor; an audit trail of every email and document (useful for insurance audits); CSV export.

**LLM cost [E]:** about 300 certificates/mo across customers × about 3K tokens of vision input ≈ under $5/mo on Haiku-class; replies triage under $5. Negligible.

## 4.3 Startup cost (itemized)

| Item | Cost | Basis |
|---|---|---|
| App (inbound email, extraction, rules, chasing, dashboard) | $0 cash; ~60–90 hrs | **[E]** Largest net-new build of the five. Reuses only the delivery/billing core. |
| LLC/domain/email | ~$70–$650 | **[E]** |
| Inbound email parsing / sending | $0–$20/mo | **[E]** |
| Secure document storage (encrypted object storage) | $1–$10/mo | **[E]** |
| Tech E&O + cyber insurance (**recommended before the first customer**: you're holding insurance documents and making compliance flags) | $35–$110/mo | **[V]** (S27) |
| Attorney: ToS (not insurance advice; customer remains responsible), DPA | $500–$1,500 | **[E]** Strongly recommended here. |
| Sample-certificate test set (collect 50 real, redacted COIs from friendly GCs) | $0 | **[E]** Your network. |
| **Total cash** | **~$600–$2,300** (the attorney and insurance drive the range) | **[E]** |

**Ongoing [E]:** about $60–$170/mo. **Break-even: 2–3 customers.**

## 4.4 Running autonomously
- **Automated:** intake, extraction, rule checks, chasing schedules, reply parsing, re-verification, reports, billing, and onboarding (a template wizard with common presets).
- **Autonomous acquisition:**
  1. **Free "COI Checker":** upload one certificate, get an instant compliance read against a standard template. The lead magnet demonstrates the product in 10 seconds.
  2. **Viral loop:** every chasing email to a sub carries a footer ("Compliance handled by [Brand] — free for subcontractors to track their own certificates"). Subs often are GCs on other jobs.
  3. **Partners:** insurance agents and brokers who serve contractors. Their clients' compliance headaches become their service calls. Offer a white-label or referral fee.
  4. **Your network:** property managers and builders. Pitch "I'll set it up free for 60 days."
- **Human oversight still needed:**
  - **Review queue** for low-confidence extractions (blurry scans, non-standard forms). About 15–30 min/week at 10–20 customers **[E]**.
  - **Template edge cases:** unusual contract requirements need a human to translate them into rules once.
  - **Disputes** where a sub's agent insists they're covered. The system should hand these to the customer, not decide coverage questions. Never give coverage advice.

## 4.5 Risks
- **Liability perception:** customers may assume you guarantee coverage. Mitigate with clear ToS, "evidence review only" language in the UI, E&O insurance, and an audit trail.
- **Competition:** many incumbents (S21), and new domains registered in 2026 (Part 0). Compete on price, zero data entry and speed of setup for small firms. Don't compete on enterprise features.
- **Sales cycle:** compliance tools need trust. Expect 2–6 week cycles even for small firms **[E]**. That's why it ranks #4.

**Kill criteria [E]:** fewer than 5 paying accounts in 120 days, or review-queue time above 2 hrs/week at 10 accounts.

## 4.6 Names: availability checks

| Name | .com status (live RDAP, 2026-11-12) | Web conflict screen | Notes |
|---|---|---|---|
| **CertBastion** | **Not registered** **[V]** | No matches **[V, web search]** | Strong "protection" connotation. My top pick. |
| **COIwarden** | **Not registered** **[V]** | **"Cert Warden"** exists (an ACME/SSL certificate manager, a different product) **[V, web search]** | Some confusion risk ("cert" + "warden" in software). Get a trademark opinion. |
| **COIquill** | **Not registered** **[V]** | Not screened | Lighter, paperwork feel. |
| **InsureWarden** | **Not registered** **[V]** | No matches **[V, web search]** | Could imply you're an insurer, which is a regulatory optics risk. Avoid. |
| Taken | certsentry (2011), coiwatch (**2026-06**), lapseguard (2025-10), subsure (2023), coverwatch (2012), certchase (**2026-06**), coisentry (**2026-02**), certkeep (2015), lapsewatch (**2026-05**), certwarden (2024), subwarden (2023), certrove (**2026-10**), lapseless (2026-04), coitally (2023), certcairn (**2026-10**), certcadence (2026-08) **[V]** | — | Very active name space: likely new competitors. |

**You must confirm yourself:** social handles; USPTO classes 035/042 and 036 (insurance-related services). Ask the trademark attorney about class 036 specifically, since "insurance" marks get extra scrutiny.

## 4.7 Branding
- **Positioning:** *"Every sub covered, every certificate current — without typing a single policy number."* For GCs: "Know before you pay."
- **Tone:** calm authority, risk-manager voice. Reassuring, never alarmist; precise about what is and isn't verified.
- **Visual direction:** fortification meets paperwork.
  - Palette: **Bastion Slate #2E3A46** (primary), **Verified Green #2E8B57** (compliant), **Amber #E0A100** (expiring), **Alert Red #B3261E** (non-compliant), **White Paper #FAFAF7** (background).
  - Typography: *Manrope* or *Inter* (clean SaaS), with tabular numerals for dates and limits.
- **Logo concepts:**
  1. A shield whose inner shape is a folded certificate.
  2. A bastion (star-fort) outline as a five-pointed check mark.
  3. A monogram "CB" set inside a seal with perforated edges like a certificate.
- **Signature asset:** a single-color traffic-light status column (green / amber / red) that a GC can read in 3 seconds before cutting checks.

---

# Blueprint 5 — B2B accounts-receivable follow-up agent (vertical wedge)

## 5.1 Problem, customer, offer

**Problem.** Small B2B firms carry overdue invoices because nobody has time to chase them politely and persistently. Generic tools exist: Chaser at $45–399/mo, plus Billabex, Paidnice, Monk and Daylit (S19) **[U]**. QuickBooks now drafts reminders with its Payments Agent (S20) **[V]**.

**What generic tools don't do well is vertical context**, for example:
- Lien-deadline awareness for construction subs and suppliers. Preliminary-notice and mechanics'-lien deadlines are a strong payment lever, and they vary by state.
- Retainage tracking.
- Pay-app cycles.
- Matching reminders to how a specific trade gets paid.

**Target customer (wedge):** construction subcontractors and building-material suppliers with $1M–$20M revenue, invoicing GCs on QuickBooks Online. They have the most painful AR (slow pay, retainage), and they intersect your real-estate and construction network.

**Offer.**
- **"Collections autopilot for subs":** connect QuickBooks once.
- The agent sends escalating, professional follow-ups from the customer's own domain.
- It reads and answers replies ("resend invoice," "paid Friday," "need W-9/lien waiver"), logs promises to pay, and stops when payment posts.
- **The differentiator:** it tracks each job's state lien and notice deadlines **as a calendar reminder for the customer and their attorney.** The agent never files or threatens liens itself.

**Pricing [E]:** **$99/mo up to 50 open invoices; $199/mo up to 200; $349/mo unlimited with multi-entity.**
- **Flat fee, deliberately not a percentage of amounts collected.** Contingency-fee collection can trigger state collection-agency licensing. Keep this a creditor's own software tool (see 5.5).

## 5.2 How the agentic system operates
1. **QuickBooks Online OAuth connection:** read customers, invoices, payments, and job/class/project fields. Xero is a later addition.
2. **Daily sync:** compute aging. Generate a sequence per invoice based on customer-chosen policy: friendly (−3 days), due today, +7, +15 firm, +30 escalation to the owner, +45 "account review."
3. **Drafting agent (LLM)** writes each message using invoice context, job name, prior thread and tone policy. It sends after an **auto-approval policy**: routine steps are auto-sent, and escalation steps can require one-click owner approval at first. That mirrors QuickBooks' review-before-send default (S20) **[V]**, but lets the customer lift the requirement once they trust it.
4. **Reply agent:** classifies inbound replies (paid / promise / dispute / document request / wrong contact). It auto-handles document requests (attaches the invoice PDF and W-9 from a doc vault) and wrong-contact updates. It **routes disputes to the human owner and pauses the sequence.**
5. **Lien-deadline tracker:** per job, the customer enters the project state and first-furnishing date. A deterministic rules table (maintained per state and reviewed by an attorney) computes notice and lien windows and sends reminders to the customer. **Rules live in code, not in the LLM.**
6. **Weekly cash report:** expected inflows from promises, DSO trend, and top 5 slow payers.

**LLM cost [E]:** about 2,000 drafts plus replies per month across customers × about 2K tokens ≈ under $10/mo on Haiku-class.

## 5.3 Startup cost (itemized)

| Item | Cost | Basis |
|---|---|---|
| App (QBO OAuth, sequencing, drafting, reply handling, dashboard) | $0 cash; ~70–100 hrs | **[E]** |
| Intuit developer app + production review | $0 fee (time for security questionnaire) | **[E]** Verify current Intuit app-review requirements. |
| Per-customer sending domain setup (SPF/DKIM via email provider) | $0–$20/mo | **[E]** |
| State lien-deadline rules table: attorney review for your first 3–5 states | $750–$2,500 | **[E]** Essential. Wrong deadlines are a liability. |
| Tech E&O + cyber | $35–$110/mo | **[V]** (S27) |
| ToS / privacy / DPA | $0–$1,000 | **[E]** |
| SMS (optional, later): Twilio 10DLC brand $4.50 (sole prop) or $46 (standard) one-time, $15 campaign vetting, about $1.50–$10/mo campaign, $0.0083/SMS + carrier fees | ~$20–$75 setup | **[V]** (S27: Twilio support; getkanal, 2026) |
| **Total cash** | **~$900–$4,000** (driven by legal) | **[E]** |

**Ongoing [E]:** about $60–$180/mo. **Break-even: 1–2 customers** (excluding legal amortization).

## 5.4 Running autonomously
- **Automated:** sync, sequencing, drafting, sending, reply classification, document fulfillment, stop-on-payment, reports, billing and onboarding.
- **Autonomous acquisition:**
  1. **Free "Lien Deadline Calculator" per state:** a highly searched, practical tool for subs and suppliers. It captures emails and converts to "track all your jobs automatically."
  2. **QuickBooks App Store listing:** where buyers already look. Verify listing requirements.
  3. **Construction-accountant and bookkeeper partners:** they manage many subs' books. Offer a partner dashboard and revenue share.
  4. **Supply-house and association partnerships:** for example, a co-branded offer through a local builders' exchange.
- **Human oversight still needed:**
  - **Disputes and payment-plan negotiations:** always routed to the customer. These involve relationships and legal positions.
  - **Approving new message templates and tone policies** before they go live.
  - **Annual attorney refresh of lien rules:** statutes change.
  - **Deliverability monitoring:** it's automated, but a human acts on bounce and complaint spikes.

## 5.5 Risks and compliance
- **Collection-law boundary.** The FDCPA generally regulates *third-party* collectors of *consumer* debts. You'll send **B2B** reminders **in the creditor's own name** as a software tool. Some states' laws reach further: for example, some cover first-party creditors on consumer debts, and some license anyone collecting "for others." So:
  - (a) restrict to B2B invoices in the ToS and the product;
  - (b) never collect money or take a percentage of amounts collected;
  - (c) no threatening language;
  - (d) have counsel confirm before launch.
  - **This is general information, not legal advice.**
- **Platform risk:** Intuit is building this natively (S20). The defense is the construction-specific lien and retainage workflow, which a horizontal accounting vendor is unlikely to prioritize **[E, a judgment]**.
- **Competition:** crowded horizontally (S19). That's why it's #5. Do not launch it as generic "AI collections."

**Kill criteria [E]:** fewer than 5 customers within 120 days, or more than one serious deliverability or complaint incident per month.

## 5.6 Names: availability checks

| Name | .com status (live RDAP, 2026-11-12) | Web conflict screen | Notes |
|---|---|---|---|
| **SettleWarden** | **Not registered** **[V]** | No matches **[V, web search]** | "Settle" fits AR. "Warden" is used by unrelated crypto/agent projects (Warden Protocol), so low risk in this class. |
| **ARwarden** | **Not registered** **[V]** | Near match "ArcWarden" (a hackathon project) **[V, web search]** | Short, and "AR" is jargon buyers know. |
| **CollectWarden** | **Not registered** **[V]** | No matches **[V, web search]** | **Avoid:** "Collect" may make you sound like a collection agency, which is a regulatory optics risk. |
| **GetPaidAgent** | **Not registered** **[V]** | No matches **[V, web search]** | Literal. Good for SEO and ads, weak as a brand. |
| Taken | duesly (2025-03), paidpilot (2023), invoicenudge (2025-04), collectcalm (2026-07), nudgepay (2017), dueflow (2023), paidsteady (2026-10), duenudge (2025-10), invoicebutler (2020), duekeeper (2026-05), invoicewarden (2026-03), paidward (2026-09), tallyback (2026-06), settlepilot (2025-10), paidtide (2026-05), nudgeledger (2026-03), duecairn (2026-09), **paidcadence (2026-11-10)**, invoicequill (2026-03), cashcairn (2026-07), duequill (2026-08) **[V]** | — | The most crowded name space of the five, which matches the competition evidence. |

**Construction-specific alternatives** (not checked, since they came up after the live run):
- *RetainageRx*
- *LienLine* (likely taken)
- *PayAppPilot*

Check these at a registrar.

**You must confirm yourself:** social handles; USPTO classes 035/036/042; QuickBooks App Store name rules.

## 5.7 Branding
- **Positioning:** *"Get paid for the work you already did — on autopilot, without burning the GC relationship."*
- **Tone:** firm but courteous, like a seasoned office manager. Respect the relationship; never sound like a collection agency.
- **Visual direction:** ledger and hardware.
  - Palette: **Ledger Green #1E5631** (primary), **Brass #C9A227** (accent), **Graphite #2B2B2B** (text), **Receipt White #FFFDF8** (background).
  - Typography: *DM Serif Display* for the wordmark, *DM Sans* for UI.
- **Logo concepts:**
  1. A key-and-ledger mark (warden's key whose bit forms a check mark).
  2. A stylized "paid" stamp ring with a hardhat silhouette.
  3. An "S" drawn as a stretched invoice curl.
- **Signature asset:** the weekly "Cash coming in" card, showing promised payments as a mini timeline.

---

## Part 3 — 90-day execution plan [E]

| Weeks | Action | Exit test |
|---|---|---|
| 1–2 | Multi-tenant filters, Stripe and delivery on LandLead (Blueprint 2); source health monitor; register the chosen domain(s) and handles; form the LLC; trademark search | First paying land customer from your network |
| 3–4 | County Land Pulse pages, free sample list, affiliate outreach to 5 land coaches | 3 paying counties |
| 5–8 | Add permit adapters for one metro (Blueprint 1); free weekly teaser; postcards to 100 adjacent-trade contractors | 3 permit subscribers |
| 9–10 | Review CAC and churn per product against the kill criteria | Decide: scale, fix or kill |
| 11–13 | If both work: begin Blueprint 3 adapters for one state and trade. If one fails: pour time into the winner | — |

Blueprints 4 and 5 are separate SaaS products with heavier legal and trust requirements. Start them only after the data products are self-running (owner time under 3 hrs/week).

---

## Part 4 — What I verified vs what you must confirm

**Verified live today (2026-11-12):**
- .com registration status for all 106 names listed, via the authoritative Verisign RDAP registry, including first-registration dates.
- Every **[V]** claim, in the cited source (not necessarily independently true; vendor sources are flagged).

**Not verifiable from here; you must confirm:**
1. **Social handles** on Instagram, X, Facebook, LinkedIn and TikTok for your chosen names. Automated lookups are blocked. Use the platforms directly or a handle-check site.
2. **Trademarks.** Search USPTO at tmsearch.uspto.gov (classes 035, 042, plus 036 for Blueprints 4–5) and your state's trademark registry. My screens were web searches only. A 1-hour trademark attorney clearance for the final pick is cheap insurance (about $300–$800 **[E]**).
3. **Current pricing** for every vendor cited (PropStream, Shovels, BidNet, Chaser, n8n, Twilio, Claude API). Several sources conflict. Vendor prices moved repeatedly in 2026.
4. **State-specific law:** LLC fees, real-estate commission rules on lead referral (Blueprint 2), collection-agency licensing (Blueprint 5), lien statutes (Blueprint 5), and contractor-license list availability (Blueprint 3).
5. **Data-source terms** for each jurisdiction and portal before you onboard it.
6. **Domain availability at purchase time.** Names in these niches are being registered weekly (Part 0). Register your top picks the same day you decide.

**Known evidence gaps (unverified everywhere I looked):**
- The number of active US land investors.
- Independent (non-vendor) churn and recovery-rate data for AI AR tools.
- An authoritative small-business share of state and local procurement.
- Shovels' current price list (its own page is reported as contradictory).

---

## Sources

All accessed 2026-11-12. "Vendor" = the source sells a product in the category it describes.

| ID | Source | Page date | Used for |
|---|---|---|---|
| S1 | [Gartner press release: over 40% of agentic AI projects canceled by end of 2027](https://www.gartner.com/en/newsroom/press-releases/2025-06-25-gartner-predicts-over-40-percent-of-agentic-ai-projects-will-be-canceled-by-end-of-2027) | 2025-06-25 | Cancellations, agent-washing, 33% of apps by 2028 |
| S2 | [Software Strategies Blog: roundup of agentic AI forecasts 2026](https://softwarestrategiesblog.com/2026/02/26/roundup-of-agentic-ai-forecasts-and-market-estimates-2026/) | 2026-02-26 | Gartner $201.9B spending (secondary) |
| S3 | [MarketsandMarkets via press release: agentic AI $93.20B by 2032](https://pr.valleytimes.news/article/Agentic-AI-Market-Surges-to-dollar9320-billion-at-a-CAGR-446percent-by-2032-or-Report-by-MarketsandMarketstm/6a83183ee2557832e110f1b8) | 2026 | Market size |
| S4 | [Hostinger: agentic AI statistics 2026](https://www.hostinger.com/in/tutorials/agentic-ai-statistics/) | 2026 | Analyst estimate roundup |
| S5 | [Upwork In-Demand Skills 2026 press release](https://www.upwork.com/press/releases/upworks-in-demand-skills-2026-demand-for-top-ai-skills-more-than-doubles-as-ai-is-embedded-into-everyday-work) / [report](https://upwork.com/research/in-demand-skills-2026) | Feb 2026 | Freelance AI demand |
| S6 | [Allwork.Space: businesses hiring for AI jobs](https://allwork.space/2026/10/businesses-are-hiring-for-ai-jobs-most-workers-werent-doing-a-year-ago/) | Oct 2026 | Upwork search trends: AI agent developer |
| S7 | [AgentMarketCap: AI agent funding Q2 2026](https://agentmarketcap.ai/blog/2026/04/07/ai-agent-funding-deceleration-q2-2026-crescendo-crunchbase) | 2026-04-07 | Agentic funding and deal counts (secondary) |
| S8 | [AgentMarketCap: Q1 2026 AI funding $242B](https://agentmarketcap.ai/blog/2026/04/14/q1-2026-ai-venture-funding-242b-doubles-2025) | 2026-04-14 | AI VC concentration (secondary) |
| S9 | [Upwork: State of AI within SMBs 2026](https://www.upwork.com/resources/state-of-ai-in-smbs) | 2026 | SMB agent adoption |
| S10 | [CPA Practice Advisor: AI adoption rises, 70% need training](https://www.cpapracticeadvisor.com/2026/07/14/ai-adoption-continues-to-rise-but-70-say-they-need-more-training/186565/) | 2026-07-14 | SMB adoption, training gap |
| S11 | [NP Digital: AI agent adoption stats](https://neilpatel.com/marketing-stats/ai-agent-adoption/) | Apr 2026 | 7% SMB marketing agent adoption |
| S12 | [Techloy: best AI receptionists for home services 2026](https://www.techloy.com/8-best-ai-receptionists-for-home-services-in-2026/) | 2026 | Receptionist competition and pricing |
| S13 | [NextPhone: best AI receptionist for plumbers (vendor)](https://www.getnextphone.com/blog/best-ai-receptionist-for-plumbers) | 2026 | Receptionist pricing |
| S14 | [Trillet: AI answering for trades (vendor)](https://trillet.ai/blogs/best-ai-answering-service-for-trades-2026) | 2026 | Receptionist pricing |
| S15 | [Kapex: AI SDR market churn (vendor)](https://getkapex.ai/blog/ai-sdr-market-churn-memory-gap-2026) | 2026 | AI SDR churn |
| S16 | [The AI Pipe: autonomous AI SDRs failing 2026](https://the-ai-pipe.pages.dev/blog/fully-autonomous-ai-sdrs-failing-2026/) | 2026 | AI SDR reversion, deliverability |
| S17 | [AI review response tools roundup](https://ai-review-responder-mu.vercel.app/blog/best-ai-review-response-tools) · [Capterra listing](https://www.capterra.com/p/10033946/AI-Review-Response-Generator/) | 2026 | Review-tool pricing |
| S18 | [Dupple: best AI for grant writing](https://dupple.com/learn/best-ai-for-grant-writing) · [Grantable: Instrumentl alternatives (vendor)](https://grantable.co/best-instrumentl-alternatives) · [Granted AI comparison (vendor)](https://grantedai.com/blog/granted-ai-vs-grantable-comparison) | May–Jul 2026 | Grant-tool competition |
| S19 | [Boostly: best AI debt collection software (vendor)](https://invoice.boostly.com/blog/best-ai-debt-collection-software) · [Beancount: Daylit AR agents](https://beancount.io/blog/2026/09/26/daylit-ai-agents-automated-collections-accounts-receivable-guide) · [Monk: AR automation for SMB (vendor)](https://monk.com/blog/best-ar-automation-for-small-business) | 2026 (Daylit: 2026-09-26) | AR competition and pricing |
| S20 | [QuickBooks Help: Payments Agent](https://quickbooks.intuit.com/learn-support/en-us/help-article/intuit-assist/get-started-payments-agent/L0FyKj9NL_US_en_US) · [Carly: QuickBooks AI tiers 2026](https://www.usecarly.com/blog/quickbooks-ai) | 2026 | Native QBO reminder agent |
| S21 | [Billy: best COI tracking for construction (vendor)](https://billyforinsurance.com/resources/best-coi-tracking-software-construction/) · [Vertikal: COI software cost (vendor)](https://vertikalrms.com/article/how-much-does-coi-tracking-software-cost-2025-pricing-guide/) · [DEV/Crawde: COI tracking 2026 (vendor)](https://dev.to/crawde/coi-tracking-software-in-2026-what-actually-works-and-whats-a-waste-of-money-3dg1) · [BCS: comparing COI vendors (vendor)](https://www.getbcs.com/blog/comparing-subcontractor-insurance-tracking-solutions-bcs-mycoi-getjones-and-trustlayer) | 2026 | COI demand, competition, pricing |
| S22 | [Civic IQ: BidNet Direct pricing (vendor)](https://civiciq.com/blog/civic-iq-bidnet-direct-pricing) · [GovContractFinder pricing guide (vendor)](https://govcontractfinder.com/tools/government-contracting-software-pricing-guide) · [FedBizAccess: SLED 101](https://fedbizaccess.com/sled-contracting-101-how-to-win-state-and-local-government-contracts-in-2026/) · [SLED AI statistics 2026 (vendor)](https://sledai.com/blog/sled-contracting-statistics-2026/) · [Hubexo Bid Ocean launch](https://www.newswire.com/news/hubexo-north-america-launches-bid-ocean-a-new-lead-generation-platform-designed) · [GovBidWire listing](https://www.softwareadvice.com.au/software/693570/GovBidWire) | 2026 (BidNet capture 2026-08-26; Bid Ocean Jul 2026) | SLED market, competition, pricing |
| S23 | [MaxIntel: building permit OSINT guide 2026 (Shovels pricing)](https://maxintel.org/building-permit-osint-guide-2026.html) · [Apify permit lead scraper](https://apify.com/samstorm/building-permit-lead-scraper) · [Apify scored permit leads](https://apify.com/oldbie/construction-permit-leads) · [Chicago building permits dataset](https://chicago.gov/city/en/depts/bldgs/dataset/building_permits.html) · [DEV: free permit data from open data](https://dev.to/salimsquared/how-to-get-building-permit-data-for-any-us-city-free-from-official-open-data-3ehc) · [Valley Marketing: Angi cost per lead 2026](https://thevalleymarketinggroup.com/blog/homeadvisor-angi-cost-per-lead-contractors-2026/) · [WBOC: Angi leads for roofers 2026](https://www.wboc.com/online_features/press_releases/angi-and-homeadvisor-leads-for-roofers-their-real-cost-per-booked-job-2026/article_8a1352fb-2e25-598e-934c-6f7b3f710a79.html) | 2026 | Permit data access, competition, lead pricing |
| S24 | [PropStream: how much does PropStream cost (vendor)](https://www.propstream.com/news/how-much-does-propstream-cost) · [REsimpli: PropStream pricing](https://resimpli.com/blog/propstream-pricing/) · [Capterra: Land AI](https://www.capterra.com/p/10039259/Land-AI/alternatives/) · [HouseCanary: PropStream alternatives (vendor)](https://www.housecanary.com/blog/propstream-alternative) · [Inman: realtor.com land price estimates](https://news2.inman.com/2026/04/22/realtor-com-launches-land-price-estimates-as-market-lags/) | 2026-05-15; May 2026; 2026-04-22 | Land-lead competition and market |
| S25 | [Excess Elite](https://excesselite.com) · [Tax Sale Resources: overages](https://taxsaleresources.com/solutions/tax-sale-overages) · [Flatnine FastLien changelog](https://changelog.flatnine.co/fastlien/overages-excess-proceeds-search) | undated | Surplus-funds competition |
| S26 | [Inman: Ownwell raises $50M](https://news.inman.com/2026/02/25/ownwell-raises-50m-to-grow-its-property-tax-appeal-fintech/) | 2026-02-25 | Property-tax appeal competition |
| S27 | [Dupple: Vapi vs Retell cost](https://dupple.com/learn/vapi-vs-retell-ai) · [Jet Admin: n8n pricing](https://www.jetadmin.io/blog/n8n-pricing/) · [Twilio: A2P 10DLC fees](https://support.twilio.com/hc/en-us/articles/1260803965530) · [Kanal: Twilio SMS pricing 2026](https://getkanal.com/blog/twilio-sms-pricing) · [MetaCTO: Claude API pricing 2026](https://metacto.com/blogs/anthropic-api-pricing-a-full-breakdown-of-costs-and-integration) · [TechInsurance: E&O cost](https://www.techinsurance.com/ask-us/business-insurance-costs/cost-of-errors-and-omissions-insurance/) · [MoneyGeek: E&O cost](https://www.moneygeek.com/insurance/business/professional-liability/errors-and-omissions/cost/) · [Apify: actor monetization](https://docs.apify.com/academy/actor-marketing-playbook/store-basics/how-actor-monetization-works) · [FCC: AI-generated voices in robocalls illegal](https://WWW.FCC.GOV/document/fcc-makes-ai-generated-voices-robocalls-illegal) | 2026 (Jet Admin 2026-09-26; FCC 2024-02-08) | Cost inputs, compliance |
| S28 | [Ciela: is the AI agency market saturated (vendor)](https://ciela.ai/blogs/is-ai-agency-market-saturated-reddit) · [RNWY: where to list an AI agent](https://rnwy.com/blog/where-to-list-ai-agent) · [AgentMarketCap: 104,000+ agents](https://agentmarketcap.ai/blog/2026/04/11/ai-agent-marketplaces-discovery-2026) · [Extruct: YC W26](https://www.extruct.ai/research/ycw26/) · [Mika Reyes: YC Spring 2026](https://mikareyes.com/ai/yc-spring-2026-batch-trends) · [Rankability: where SEO is going 2026](https://www.rankability.com/assets/where-seo-is-going-2026.pdf) · [Apify: US new business filings](https://apify.com/lergassy/us-business-filings) | 2026 (Ciela 2026-07-02; AgentMarketCap 2026-04-11) | Saturation, directories, YC, search trends, filings |
| — | Verisign .com RDAP registry (rdap.verisign.com), queried live | 2026-11-12 | All domain availability and registration dates |
