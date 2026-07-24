"""Task engine: auto-assign follow-up tasks based on score + recency.

Rules (tune freely):
- Priority lead (score >= threshold) with no contact info yet -> skip_trace task.
- Priority lead with a mailing address and no queued mail -> mail task.
- Priority lead with contact info -> call task.
- Any 'New' priority lead is auto-advanced to nothing; status stays New until a
  human acts, but the tasks make the next action obvious.

Idempotent: it never creates a second open task of the same type for a lead.
"""
from __future__ import annotations

from datetime import date, timedelta

from config.settings import get_settings
from db import repo


def _due(days: int) -> str:
    return (date.today() + timedelta(days=days)).isoformat()


def build_tasks_for_priority_leads() -> dict:
    settings = get_settings()
    leads = repo.query_leads(min_score=settings.HIGH_PRIORITY_THRESHOLD, limit=10000)

    created = {"skip_trace": 0, "mail": 0, "call": 0}
    for lead in leads:
        lead_id = lead["id"]
        contacts = repo.get_contacts(lead_id)
        has_contact = any(c.get("phone") or c.get("email") for c in contacts)

        if not has_contact and not repo.open_task_exists(lead_id, "skip_trace"):
            repo.add_task(lead_id, "skip_trace", _due(2),
                          "Locate current phone/email for owner (permissible purpose required).")
            created["skip_trace"] += 1

        has_mailing = bool(lead.get("owner_mailing_address"))
        if has_mailing and not repo.mail_queued_exists(lead_id) \
                and not repo.open_task_exists(lead_id, "mail"):
            repo.add_task(lead_id, "mail", _due(3),
                          "Queue/print first-touch letter (signal-matched template).")
            created["mail"] += 1

        if has_contact and not repo.open_task_exists(lead_id, "call"):
            repo.add_task(lead_id, "call", _due(1),
                          "Call owner. Scrub against DNC first (TCPA).")
            created["call"] += 1

    return {"priority_leads": len(leads), "tasks_created": created}
