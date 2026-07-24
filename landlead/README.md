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

## Data sources (and their status)

**Live (public / open data):**
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

> County ArcGIS endpoints in `counties.yml` are real published services where
> known, but counties re-home them periodically. A dead endpoint is logged and
> skipped (never fatal); update the URL from the county's open-data portal.
> Check the run log at `GET /api/scrape_log` or the `scrape_log` table.

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
