# LandLead — Vacant-Land Lead Engine (Eastern US)

An autonomous, self-hosted pipeline that **sources → scores → deduplicates →
manages → follows up on** vacant-land seller leads, built entirely on **public
records and open data**. FastAPI backend, SQLite (Postgres-ready), Jinja2 CRM,
APScheduler.

> **Read [`COMPLIANCE.md`](./COMPLIANCE.md) first.** This tool aggregates public
> records for legitimate real-estate outreach. Several parts (contacting owners,
> skip tracing, licensed data) are regulated. The scrapers identify themselves
> honestly, honor `robots.txt`, and rate-limit; ToS-restricted and licensed
> sources ship **disabled by default**.

## Quick start

```bash
cd landlead
pip install -r requirements.txt

# Serve the CRM + background scheduler at http://localhost:8000
python main.py

# ...or one-shot the whole pipeline (scrape -> enrich -> follow-ups) and exit:
python main.py --pipeline
```

Or with Docker:

```bash
docker-compose up --build      # CRM at http://localhost:8000
```

No configuration is required to boot — every credential is optional. Open the
dashboard and click **▶ Run Pipeline**, or `POST /api/pipeline/run`.

## What it does

| Phase | Module | What ships |
|-------|--------|-----------|
| **1 — Acquisition** | `scraper/` | **Live** ArcGIS parcel scraper (open GIS REST), tax-deed/tax-lien auction harvester, RSS legal-notice reader, public probate-court + code-violation adapters. Obituary & USPS/NCOA are gated-off adapters. All fault-tolerant + logged. |
| **2 — Scoring/Enrich** | `enrichment/` | APN-keyed dedup + merge, transparent 1–100 lead score with per-signal breakdown, auto-flags priority (≥70). |
| **3 — CRM** | `crm/` | Sortable/filterable lead dashboard, full lead detail, `New→Contacted→Negotiating→Under Contract→Closed→Dead` pipeline, CSV import/export. |
| **4 — Follow-up** | `followup/` | Signal-matched merge-ready letters (motivated-seller / probate / tax), auto task assignment (call/mail/skip-trace), skip-trace connector hooks (TLO/Batch/IDI). |

## Architecture

```
main.py                  single entrypoint (API + scheduler + CLI jobs)
config/    counties.yml (10 seed counties, FL/GA/NC/SC/VA/PA/NY), settings, scheduler
db/        schema.sql, sqlite layer, repo (all SQL)
scraper/   base (robots + rate-limit + fault tolerance) + sources/ + registry
enrichment/ dedup (APN canonical key) + scoring
crm/       FastAPI api + Jinja2 templates + static
followup/  mailmerge + task engine + skiptrace hooks + letter_templates/
scheduler/ APScheduler cron jobs (also runnable via system cron: --job <id>)
```

**Scaling to all Eastern US counties:** add blocks to `config/counties.yml`.
No code changes — the registry runs each configured source per county. Add a new
*source type* by dropping a `BaseScraper` subclass in `scraper/sources/` and
registering one line in `scraper/registry.py`.

## Buy-box (what gets surfaced)

The pipeline targets **vacant land, 5–100 acres, Eastern US** — configurable via
`LEAD_MIN_ACRES` / `LEAD_MAX_ACRES` / `LEAD_VACANT_ONLY`. Parcels outside the
band (or improved, when vacant-only is on) are dropped at ingest, and the
dashboard defaults to buy-box matches only (`?show_all=true` reveals everything,
including bare auction/legal notices). The ArcGIS scraper pushes the acreage
filter into the server-side query, so a statewide layer returns just the
matching tracts — not millions of rows.

## Data sources (and their status)

**Live parcel sources — verified statewide services (cover whole states in one call):**
- **Florida** — DOR Statewide Cadastral (all 67 counties; owner, mailing, situs,
  DOR use code, land sq-ft, value). Vacant DOR codes 00/10/40/70.
- **New York** — NYS Tax Parcels Public (opt-in counties; property class 3xx = vacant).
- **Virginia** — VGIN statewide parcels (acreage-driven; no uniform state use code).

**Other live (public / open data):**
- Open Esri **ArcGIS parcel** REST services — designed for programmatic query.
- **Tax-deed / tax-lien auction** notice pages (treasurer/sheriff sales).
- **Legal notices** via RSS/Atom (estate, land sale, guardianship).
- **Probate court** + **code-violation** adapters (public records; add the
  county's endpoint to activate).

**Gated off (require your license/permission — see COMPLIANCE.md):**
- **Obituary aggregators** (Legacy.com, Newspapers.com) — ToS-restricted. Use the
  public probate-court + legal-notice sources instead.
- **USPS vacancy / NCOA** — licensed data, not public. The pipeline derives an
  `absentee` proxy from parcel mailing-vs-situs mismatch with no license needed.
- **Skip tracing** (TLO / BatchSkipTracing / IDI) — connector stubs; require an
  API key **and** a permissible purpose.

> Parcel endpoints in `counties.yml` are real published services, but agencies
> re-home them periodically and each state codes land use differently. A dead
> endpoint or bad field guess is logged and skipped (never fatal), and the
> scraper self-heals a bad server-side filter by retrying unfiltered. Add more
> states (GA, NC, SC, PA…) by dropping their verified statewide/county endpoint
> and vacant codes into `counties.yml`. Check `GET /api/scrape_log` for what ran.

## Key endpoints

- `GET  /` — dashboard · `GET /leads/{id}` — detail
- `GET  /api/leads?state=FL&min_score=70&priority=true&sort=lead_score`
- `POST /api/pipeline/run` — run scrape → enrich → follow-ups now
- `GET  /api/export.csv` · `POST /api/import` (CSV, needs `apn` column)
- `POST /api/leads/{id}/status` · `/notes` · `/skiptrace` · `/queue_mail`
- `GET  /api/tasks` · `GET /api/mail` · `GET /api/scrape_log`

## Scheduling

`config/scheduler.yml` drives APScheduler (starts with the app). For system
cron instead, call individual jobs:

```bash
python main.py --job parcels_ingest
python main.py --job score_and_dedup
```

## Config

Copy `.env.example` → `.env`. Everything is optional; see the file and
`COMPLIANCE.md` for what each gated integration requires.
