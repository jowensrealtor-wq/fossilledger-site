# Compliance & Responsible-Use Notes

LandLead aggregates **public records** to support legitimate real-estate
outreach (direct mail and follow-up). Public-records marketing is a mainstream,
lawful activity — but several parts of it are regulated. Read this before
enabling optional sources or contacting anyone.

## Scraping conduct (built in)

- **Honest identification.** The crawler sends a single, truthful `User-Agent`
  with a contact address (`SCRAPER_USER_AGENT`). It does **not** rotate
  user-agents or masquerade as a browser to defeat bot protection. Rotating
  identities specifically to evade a site's access controls can implicate the
  CFAA and virtually always breaches site terms — this project deliberately
  does not do it.
- **robots.txt.** Honored for **HTML page scrapers** (auction/probate/code/RSS):
  a page disallowed by robots.txt is skipped and logged, not fetched.
  **Documented open-data REST APIs** (the ArcGIS parcel `/query` endpoints) are
  treated as APIs, not crawlable pages — robots.txt is the Robots Exclusion
  Protocol for crawlers indexing site pages, and these endpoints are published
  by the agencies specifically for programmatic query (every GIS client uses
  them). They are queried directly, still under rate-limiting and an honest UA.
  Set `SCRAPER_RESPECT_ROBOTS=false` to disable robots globally if you prefer.
- **Rate limiting.** A minimum per-host delay (`SCRAPER_RATE_LIMIT_SECONDS`)
  is enforced so a source is never hammered.
- **Fault tolerance.** A failing source logs the error to `scrape_log` and the
  pipeline continues; one bad county never crashes a run.

## Sources that ship LIVE (public records / open data)

- **Open GIS / parcel REST services** (Esri ArcGIS FeatureServer/MapServer).
  These are published by counties/states specifically for programmatic query.
- **Public tax-deed / tax-lien auction notices** and **treasurer/sheriff sale
  postings** — published for public notice.
- **Newspaper & court legal notices via RSS/Atom** (`feedparser`) — published
  for public notice.
- **Public probate court record indexes** where a county exposes them.

## Sources that are GATED OFF by default

These require your own license/permission. They are implemented as adapters
that **raise a clear error unless explicitly enabled**, and no default
credentials are shipped.

- **Obituary aggregators (Legacy.com, Newspapers.com).** These sites' Terms of
  Service generally prohibit scraping; Newspapers.com is a paid subscription
  service. Use the **official public probate court records** already supported
  instead, or obtain written permission / a licensed feed. `ENABLE_OBITUARY_ADAPTER`.
- **USPS vacancy / NCOA-adjacent data.** NCOA and USPS vacancy indicators are
  **not free public data** — they are distributed only through licensed USPS
  partners under contract. `ENABLE_USPS_VACANCY` + a real licensee integration.

## Contacting owners — your responsibility

- **Skip tracing** (`followup/skiptrace.py`) is a placeholder for licensed
  providers (TLO, BatchSkipTracing, IDI). Locating a person's contact info from
  regulated sources requires a **permissible purpose** under GLBA/DPPA/FCRA.
  Confirm your purpose with the vendor and your counsel before enabling.
- **Direct mail** must follow state marketing rules. Some jurisdictions
  regulate solicitations tied to tax-delinquency, foreclosure, or probate —
  check state law before mailing those segments.
- **Phone calls / texts** are governed by the **TCPA** and state do-not-call /
  do-not-text rules. Scrub against the DNC registry; get consent for texts.
- **Email** is governed by **CAN-SPAM** (honest headers, physical address,
  working opt-out).
- **Tone.** Probate/estate outreach targets recently bereaved people. Templates
  in this project are written to be professional and respectful, not to exploit
  distress. Keep it that way.

## Data handling

- Owner PII lives in your local database. Secure it, restrict access, and honor
  deletion / opt-out requests. Do not resell records in violation of the source
  terms you obtained them under.

Nothing here is legal advice. You are responsible for compliance in every
county and state you operate in.
