"""Mail-merge: render a letter template for a lead and queue it for mailing.

Templates live in followup/letter_templates/*.txt and use Jinja2 placeholders.
Template selection is signal-driven: probate signal -> probate letter,
tax-delinquent -> tax letter, otherwise the general motivated-seller letter.
The rendered, merge-ready text is stored in `mail_queue` for printing/sending.
"""
from __future__ import annotations

from datetime import date
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from db import repo

TEMPLATE_DIR = Path(__file__).resolve().parent / "letter_templates"

_env = Environment(
    loader=FileSystemLoader(str(TEMPLATE_DIR)),
    autoescape=select_autoescape(enabled_extensions=(), default=False),
    keep_trailing_newline=True,
)

# Your signature block. Override via crm API / config as you like.
AGENT = {
    "agent_name": "J. Owens",
    "agent_company": "Owens Land Group",
    "agent_phone": "(555) 555-0123",
    "agent_email": "jowensrealtor@gmail.com",
}


def choose_template(lead: dict) -> str:
    if lead.get("probate_signal"):
        return "probate_heir.txt"
    if lead.get("tax_delinquent"):
        return "tax_delinquent.txt"
    return "motivated_seller.txt"


def _salutation(owner_name: str | None) -> str:
    if not owner_name:
        return "Property Owner"
    # "SMITH JOHN A" or "John Smith" -> a reasonable salutation
    name = owner_name.strip()
    if "," in name:                       # "SMITH, JOHN"
        last = name.split(",")[0].strip().title()
        return last or "Property Owner"
    parts = name.split()
    return parts[-1].title() if parts else "Property Owner"


def render_letter(lead: dict, template: str | None = None) -> tuple[str, str]:
    template = template or choose_template(lead)
    tpl = _env.get_template(template)
    acreage = lead.get("acreage")
    ctx = {
        "date": date.today().strftime("%B %d, %Y"),
        "owner_name": lead.get("owner_name") or "Property Owner",
        "owner_name_salutation": _salutation(lead.get("owner_name")),
        "owner_mailing_address": lead.get("owner_mailing_address") or "",
        "property_address": lead.get("property_address") or "(address on file)",
        "apn": lead.get("apn") or "",
        "county": lead.get("county") or "",
        "state": lead.get("state") or "",
        "acreage_phrase": f"{acreage:.2f}-acre " if acreage else "",
        **AGENT,
    }
    return template, tpl.render(**ctx)


def queue_letter_for_lead(lead_id: int, template: str | None = None) -> int | None:
    lead = repo.get_lead(lead_id)
    if not lead:
        return None
    if repo.mail_queued_exists(lead_id):
        return None  # don't double-queue
    tpl, rendered = render_letter(lead, template)
    return repo.queue_mail(lead_id, tpl, rendered)


def queue_for_priority_leads() -> dict:
    """Queue a first-touch letter for every high-priority lead not yet queued."""
    leads = repo.query_leads(priority_only=True, limit=10000)
    queued = 0
    for lead in leads:
        if repo.mail_queued_exists(lead["id"]):
            continue
        full = repo.get_lead(lead["id"])
        tpl, rendered = render_letter(full)
        repo.queue_mail(lead["id"], tpl, rendered)
        queued += 1
    return {"queued": queued, "eligible_priority": len(leads)}
