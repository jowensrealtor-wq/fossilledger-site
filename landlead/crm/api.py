"""CRM: FastAPI app serving a JSON API + a Jinja2 dashboard.

Routes:
  GET  /                      dashboard (HTML)
  GET  /leads/{id}            lead detail (HTML)
  GET  /api/leads             filter/sort leads (JSON)
  GET  /api/leads/{id}        full lead profile (JSON)
  POST /api/leads/{id}/status advance pipeline stage
  POST /api/leads/{id}/notes  add a note
  POST /api/leads/{id}/skiptrace  run skip trace (if configured)
  GET  /api/export.csv        export leads (optionally filtered)
  POST /api/import            bulk import leads from CSV
  GET  /api/tasks             list tasks
  POST /api/tasks/{id}/complete
  GET  /api/mail              mail queue
  POST /api/pipeline/run      run scrape -> enrich -> followups on demand
"""
from __future__ import annotations

import csv
import io

from fastapi import FastAPI, Form, Query, Request, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path

from config.settings import get_settings
from db import repo
from db.database import init_db
from db.repo import PIPELINE
from enrichment.enrich import run_enrichment
from followup.mailmerge import queue_for_priority_leads, render_letter
from followup.tasks import build_tasks_for_priority_leads

BASE = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE / "templates"))

app = FastAPI(title="LandLead CRM", version="1.0")
app.mount("/static", StaticFiles(directory=str(BASE / "static")), name="static")


@app.on_event("startup")
def _startup() -> None:
    init_db()


# --------------------------------------------------------------------------- #
# HTML views
# --------------------------------------------------------------------------- #
@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request,
              status: str | None = None,
              state: str | None = None,
              county: str | None = None,
              min_score: int | None = None,
              priority: bool = False,
              sort: str = "lead_score",
              order: str = "desc",
              show_all: bool = False):
    # Default view = qualified buy-box leads only (vacant land in acreage band);
    # ?show_all=true reveals every record incl. bare auction/legal notices.
    leads = repo.query_leads(status=status, state=state, county=county,
                             min_score=min_score, priority_only=priority,
                             sort=sort, order=order,
                             qualified_only=not show_all)
    stats = repo.dashboard_stats()
    s = get_settings()
    # request-first signature: required by newer Starlette, supported since 0.29
    return templates.TemplateResponse(request, "dashboard.html", {
        "leads": leads, "stats": stats, "pipeline": PIPELINE,
        "buybox": {"min": s.LEAD_MIN_ACRES, "max": s.LEAD_MAX_ACRES},
        "filters": {"status": status, "state": state, "county": county,
                    "min_score": min_score, "priority": priority,
                    "sort": sort, "order": order, "show_all": show_all},
    })


@app.get("/leads/{lead_id}", response_class=HTMLResponse)
def lead_detail(request: Request, lead_id: int):
    lead = repo.get_lead(lead_id)
    if not lead:
        return HTMLResponse("Lead not found", status_code=404)
    _, letter_preview = render_letter(lead)
    return templates.TemplateResponse(request, "lead_detail.html", {
        "lead": lead,
        "contacts": repo.get_contacts(lead_id),
        "notes": repo.get_notes(lead_id),
        "tasks": repo.get_tasks(lead_id=lead_id),
        "history": repo.get_status_history(lead_id),
        "pipeline": PIPELINE,
        "letter_preview": letter_preview,
    })


# --------------------------------------------------------------------------- #
# JSON API
# --------------------------------------------------------------------------- #
@app.get("/api/leads")
def api_leads(status: str | None = None, state: str | None = None,
              county: str | None = None, min_score: int | None = None,
              priority: bool = False, sort: str = "lead_score",
              order: str = "desc", limit: int = 500):
    return repo.query_leads(status=status, state=state, county=county,
                            min_score=min_score, priority_only=priority,
                            sort=sort, order=order, limit=limit)


@app.get("/api/leads/{lead_id}")
def api_lead(lead_id: int):
    lead = repo.get_lead(lead_id)
    if not lead:
        return JSONResponse({"error": "not found"}, status_code=404)
    return {
        "lead": lead,
        "contacts": repo.get_contacts(lead_id),
        "notes": repo.get_notes(lead_id),
        "tasks": repo.get_tasks(lead_id=lead_id),
        "history": repo.get_status_history(lead_id),
    }


@app.post("/api/leads/{lead_id}/status")
def api_set_status(lead_id: int, status: str = Form(...)):
    if status not in PIPELINE:
        return JSONResponse({"error": f"invalid status; use one of {PIPELINE}"},
                            status_code=400)
    repo.update_status(lead_id, status)
    return {"ok": True, "lead_id": lead_id, "status": status}


@app.post("/api/leads/{lead_id}/notes")
def api_add_note(lead_id: int, body: str = Form(...), author: str = Form("user")):
    note_id = repo.add_note(lead_id, body, author)
    return {"ok": True, "note_id": note_id}


@app.post("/api/leads/{lead_id}/skiptrace")
def api_skiptrace(lead_id: int):
    from followup.skiptrace import SkipTraceError, skip_trace_lead
    try:
        results = skip_trace_lead(lead_id)
        return {"ok": True, "found": len(results), "results": results}
    except (SkipTraceError, NotImplementedError) as exc:
        return JSONResponse({"ok": False, "error": str(exc)}, status_code=400)


@app.post("/api/leads/{lead_id}/queue_mail")
def api_queue_mail(lead_id: int, template: str | None = Form(None)):
    from followup.mailmerge import queue_letter_for_lead
    mail_id = queue_letter_for_lead(lead_id, template)
    if mail_id is None:
        return JSONResponse({"ok": False, "error": "already queued or lead missing"},
                            status_code=400)
    return {"ok": True, "mail_id": mail_id}


# --------------------------------------------------------------------------- #
# tasks + mail
# --------------------------------------------------------------------------- #
@app.get("/api/tasks")
def api_tasks(status: str | None = "open"):
    return repo.get_tasks(status=status)


@app.post("/api/tasks/{task_id}/complete")
def api_complete_task(task_id: int, status: str = Form("done")):
    repo.complete_task(task_id, status)
    return {"ok": True}


@app.get("/api/mail")
def api_mail(status: str | None = "queued"):
    return repo.get_mail_queue(status=status)


@app.post("/api/mail/{mail_id}/sent")
def api_mail_sent(mail_id: int):
    repo.mark_mail_sent(mail_id)
    return {"ok": True}


# --------------------------------------------------------------------------- #
# CSV import / export
# --------------------------------------------------------------------------- #
EXPORT_COLUMNS = [
    "id", "apn", "county", "state", "owner_name", "owner_mailing_address",
    "property_address", "acreage", "land_value", "lead_score", "priority",
    "status", "tax_delinquent", "probate_signal", "absentee",
    "out_of_state_owner", "vacant_confirmed",
]


@app.get("/api/export.csv")
def api_export(status: str | None = None, state: str | None = None,
               min_score: int | None = None):
    leads = repo.query_leads(status=status, state=state, min_score=min_score,
                             limit=100000)
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=EXPORT_COLUMNS, extrasaction="ignore")
    writer.writeheader()
    for lead in leads:
        writer.writerow(lead)
    buf.seek(0)
    return StreamingResponse(
        iter([buf.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=leads.csv"},
    )


@app.post("/api/import")
async def api_import(file: UploadFile):
    """Bulk-import leads from CSV. Requires an `apn` column; other columns map
    onto the lead schema where names match."""
    content = (await file.read()).decode("utf-8", errors="replace")
    reader = csv.DictReader(io.StringIO(content))
    imported = 0
    skipped = 0
    for row in reader:
        apn = (row.get("apn") or row.get("APN") or "").strip()
        if not apn:
            skipped += 1
            continue
        data = {k: v for k, v in row.items() if k in repo.LEAD_MERGE_FIELDS and v != ""}
        for flag in ("tax_delinquent", "probate_signal", "absentee",
                     "out_of_state_owner", "vacant_confirmed", "code_violation"):
            if flag in data:
                data[flag] = str(data[flag]).strip().lower() in {"1", "true", "yes"}
        repo.upsert_lead(apn, "csv_import", data)
        imported += 1
    return {"ok": True, "imported": imported, "skipped": skipped}


# --------------------------------------------------------------------------- #
# on-demand pipeline
# --------------------------------------------------------------------------- #
@app.post("/api/pipeline/run")
def api_run_pipeline(state: str | None = None, scrape: bool = True):
    """Run the full pipeline on demand: (optional) scrape -> enrich -> followups."""
    summary: dict = {}
    if scrape:
        from scraper.registry import run_all
        results = run_all(only_state=state)
        summary["scrape"] = {
            src: [{"county": r.county, "status": r.status,
                   "records": len(r.records), "message": r.message} for r in runs]
            for src, runs in results.items()
        }
    summary["enrichment"] = run_enrichment()
    summary["tasks"] = build_tasks_for_priority_leads()
    summary["mail"] = queue_for_priority_leads()
    return summary


@app.get("/api/scrape_log")
def api_scrape_log(limit: int = 50):
    return repo.recent_scrape_log(limit)


@app.get("/health")
def health():
    return {"status": "ok"}
