"""LandLead — single entrypoint.

Usage:
  python main.py                 # init DB, start scheduler, serve CRM at :8000
  python main.py --no-scheduler  # serve API only
  python main.py --job <id>      # run one pipeline job now and exit (cron mode)
  python main.py --pipeline      # run a full scrape->enrich->followup pass, exit
  python main.py --init-db       # create tables and exit

Job ids: parcels_ingest, auctions_ingest, legal_notices_ingest,
         score_and_dedup, build_followups
"""
from __future__ import annotations

import argparse
import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s | %(message)s",
)
log = logging.getLogger("landlead")


def _run_full_pipeline():
    from scraper.registry import run_all
    from enrichment.enrich import run_enrichment
    from followup.tasks import build_tasks_for_priority_leads
    from followup.mailmerge import queue_for_priority_leads

    log.info("Scraping all configured sources across all counties…")
    scrape = run_all()
    for src, runs in scrape.items():
        ok = sum(1 for r in runs if r.status == "ok")
        rec = sum(len(r.records) for r in runs)
        log.info("  %-18s runs=%d ok=%d records=%d", src, len(runs), ok, rec)
    log.info("Enriching (dedup + score)…")
    log.info("  %s", run_enrichment())
    log.info("Building follow-ups…")
    log.info("  tasks=%s", build_tasks_for_priority_leads())
    log.info("  mail=%s", queue_for_priority_leads())


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="LandLead land-lead system")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--no-scheduler", action="store_true",
                        help="do not start the background scheduler")
    parser.add_argument("--job", help="run a single scheduler job now and exit")
    parser.add_argument("--pipeline", action="store_true",
                        help="run a full scrape->enrich->followup pass and exit")
    parser.add_argument("--init-db", action="store_true",
                        help="create database tables and exit")
    args = parser.parse_args(argv)

    from db.database import init_db
    init_db()
    log.info("Database ready.")

    if args.init_db:
        return 0

    if args.job:
        from scheduler.jobs import run_job_once
        log.info("Running job %s…", args.job)
        result = run_job_once(args.job)
        log.info("Result: %s", result)
        return 0

    if args.pipeline:
        _run_full_pipeline()
        return 0

    # Serve the CRM (and, by default, the scheduler).
    from config.settings import get_settings
    settings = get_settings()

    import uvicorn
    from crm.api import app

    if settings.ENABLE_SCHEDULER and not args.no_scheduler:
        from scheduler.jobs import build_scheduler
        scheduler = build_scheduler()
        scheduler.start()
        log.info("Scheduler started.")

    log.info("Serving CRM at http://%s:%d", args.host, args.port)
    # ws="none": the CRM uses no websockets, and skipping the ws protocol
    # avoids uvicorn/websockets version-mismatch ImportErrors on user machines
    # (e.g. "cannot import name 'ServerProtocol' from 'websockets.server'").
    uvicorn.run(app, host=args.host, port=args.port, log_level="info", ws="none")
    return 0


if __name__ == "__main__":
    sys.exit(main())
