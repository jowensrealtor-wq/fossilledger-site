"""APScheduler wiring. Loads config/scheduler.yml and registers cron jobs.

Every job is wrapped so an exception is logged and swallowed — a failed run
never stops the scheduler or the API. Jobs are cron-compatible; the same
callables can be driven from system cron instead (see main.py --job).
"""
from __future__ import annotations

import logging

import yaml
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from config.settings import CONFIG_DIR
from enrichment.enrich import run_enrichment
from followup.mailmerge import queue_for_priority_leads
from followup.tasks import build_tasks_for_priority_leads
from scraper.registry import run_source

log = logging.getLogger("landlead.scheduler")


def job_parcels_ingest():
    return run_source("parcels")


def job_auctions_ingest():
    return run_source("tax_deed_auctions")


def job_legal_notices_ingest():
    return [
        *run_source("legal_notices"),
        *run_source("probate_court"),
        *run_source("code_violations"),
    ]


def job_score_and_dedup():
    return run_enrichment()


def job_build_followups():
    return {"tasks": build_tasks_for_priority_leads(),
            "mail": queue_for_priority_leads()}


JOB_FUNCS = {
    "parcels_ingest": job_parcels_ingest,
    "auctions_ingest": job_auctions_ingest,
    "legal_notices_ingest": job_legal_notices_ingest,
    "score_and_dedup": job_score_and_dedup,
    "build_followups": job_build_followups,
}


def _safe(func):
    def wrapped():
        try:
            result = func()
            log.info("job %s ok: %s", func.__name__, result)
        except Exception as exc:  # never let a job crash the scheduler
            log.exception("job %s failed: %s", func.__name__, exc)
    return wrapped


def build_scheduler() -> BackgroundScheduler:
    with open(CONFIG_DIR / "scheduler.yml", "r", encoding="utf-8") as fh:
        cfg = yaml.safe_load(fh) or {}
    scheduler = BackgroundScheduler(timezone="UTC")
    for job in cfg.get("jobs", []):
        func = JOB_FUNCS.get(job["id"])
        if not func:
            log.warning("no callable for scheduled job id=%s", job.get("id"))
            continue
        cron_kwargs = {k: v for k, v in job.items()
                       if k in {"minute", "hour", "day", "month", "day_of_week"}}
        scheduler.add_job(_safe(func), CronTrigger(**cron_kwargs), id=job["id"],
                          replace_existing=True, misfire_grace_time=3600)
        log.info("scheduled %s (%s)", job["id"], cron_kwargs)
    return scheduler


def run_job_once(job_id: str):
    """Cron-compatible entrypoint: run a single job now (for system cron)."""
    func = JOB_FUNCS.get(job_id)
    if not func:
        raise ValueError(f"Unknown job: {job_id}. Options: {list(JOB_FUNCS)}")
    return func()
