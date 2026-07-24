"""Data-access layer. All SQL lives here so the rest of the app stays clean."""
from __future__ import annotations

import re
from typing import Any

from db.database import db, dumps, loads, row_to_dict, rows_to_dicts

# Canonical pipeline stages, in order.
PIPELINE = ["New", "Contacted", "Negotiating", "Under Contract", "Closed", "Dead"]


def normalize_apn(apn: str | None) -> str | None:
    """Canonical dedup key: strip all separators/whitespace, uppercase.

    So '12-34-567', '12345 67', and '1234567' all collapse to one lead. This is
    THE canonical key — every entry path (scrape, CSV import, manual) runs
    through upsert_lead, which normalizes here, so dedup is guaranteed.
    """
    if not apn:
        return None
    cleaned = re.sub(r"[^0-9A-Za-z]", "", str(apn)).upper()
    return cleaned or None


# --------------------------------------------------------------------------- #
# raw records
# --------------------------------------------------------------------------- #
def insert_raw(source: str, county: str | None, state: str | None,
               apn: str | None, payload: dict) -> int:
    with db() as conn:
        cur = conn.execute(
            "INSERT INTO raw_records (source, county, state, apn, payload) "
            "VALUES (?, ?, ?, ?, ?)",
            (source, county, state, apn, dumps(payload)),
        )
        return cur.lastrowid


def iter_raw(apn: str | None = None) -> list[dict]:
    q = "SELECT * FROM raw_records"
    params: tuple = ()
    if apn:
        q += " WHERE apn = ?"
        params = (apn,)
    with db() as conn:
        rows = conn.execute(q, params).fetchall()
    out = rows_to_dicts(rows)
    for r in out:
        r["payload"] = loads(r["payload"], {})
    return out


# --------------------------------------------------------------------------- #
# scrape log
# --------------------------------------------------------------------------- #
def log_start(source: str, county: str | None, state: str | None) -> int:
    with db() as conn:
        cur = conn.execute(
            "INSERT INTO scrape_log (source, county, state, status) "
            "VALUES (?, ?, ?, 'running')",
            (source, county, state),
        )
        return cur.lastrowid


def log_finish(log_id: int, status: str, records_found: int = 0,
               message: str | None = None) -> None:
    with db() as conn:
        conn.execute(
            "UPDATE scrape_log SET finished_at = datetime('now'), status = ?, "
            "records_found = ?, message = ? WHERE id = ?",
            (status, records_found, message, log_id),
        )


def recent_scrape_log(limit: int = 50) -> list[dict]:
    with db() as conn:
        rows = conn.execute(
            "SELECT * FROM scrape_log ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
    return rows_to_dicts(rows)


# --------------------------------------------------------------------------- #
# leads
# --------------------------------------------------------------------------- #
LEAD_MERGE_FIELDS = [
    "county", "state", "owner_name", "owner_mailing_address", "property_address",
    "latitude", "longitude", "acreage", "land_value", "assessed_value",
    "last_sale_date", "last_sale_price", "absentee", "out_of_state_owner",
    "tax_delinquent", "tax_delinquent_amount", "probate_signal",
    "code_violation", "vacant_confirmed",
]


def upsert_lead(apn: str, source: str, data: dict) -> int:
    """Insert a lead keyed on APN, or merge new signal into an existing one.

    Merge policy: non-empty new values win for descriptive fields; boolean
    signal flags are OR-ed so a positive signal from any source sticks.
    """
    apn = (apn or "").strip()
    apn_key = normalize_apn(apn)
    if not apn_key:
        raise ValueError("upsert_lead requires a non-empty APN")

    with db() as conn:
        existing = conn.execute(
            "SELECT * FROM leads WHERE apn_key = ?", (apn_key,)
        ).fetchone()

        if existing is None:
            cols = ["apn", "apn_key", "sources"] + LEAD_MERGE_FIELDS
            vals = [apn, apn_key, dumps([source])] + [data.get(f) for f in LEAD_MERGE_FIELDS]
            placeholders = ", ".join(["?"] * len(cols))
            cur = conn.execute(
                f"INSERT INTO leads ({', '.join(cols)}) VALUES ({placeholders})",
                vals,
            )
            return cur.lastrowid

        row = row_to_dict(existing)
        merged: dict[str, Any] = {}
        for f in LEAD_MERGE_FIELDS:
            new_val = data.get(f)
            old_val = row.get(f)
            if f in {"absentee", "out_of_state_owner", "tax_delinquent",
                     "probate_signal", "code_violation", "vacant_confirmed"}:
                merged[f] = 1 if (old_val or new_val) else 0
            else:
                merged[f] = new_val if new_val not in (None, "", 0) else old_val

        sources = loads(row.get("sources"), [])
        if source not in sources:
            sources.append(source)

        set_clause = ", ".join(f"{f} = ?" for f in LEAD_MERGE_FIELDS)
        conn.execute(
            f"UPDATE leads SET {set_clause}, sources = ?, updated_at = datetime('now') "
            f"WHERE id = ?",
            [merged[f] for f in LEAD_MERGE_FIELDS] + [dumps(sources), row["id"]],
        )
        return row["id"]


def set_score(lead_id: int, score: int, priority: bool, breakdown: dict) -> None:
    with db() as conn:
        conn.execute(
            "UPDATE leads SET lead_score = ?, priority = ?, score_breakdown = ?, "
            "updated_at = datetime('now') WHERE id = ?",
            (score, 1 if priority else 0, dumps(breakdown), lead_id),
        )


def get_lead(lead_id: int) -> dict | None:
    with db() as conn:
        row = conn.execute("SELECT * FROM leads WHERE id = ?", (lead_id,)).fetchone()
    lead = row_to_dict(row)
    if lead:
        lead["sources"] = loads(lead.get("sources"), [])
        lead["score_breakdown"] = loads(lead.get("score_breakdown"), {})
    return lead


def all_leads() -> list[dict]:
    with db() as conn:
        rows = conn.execute("SELECT * FROM leads").fetchall()
    return rows_to_dicts(rows)


def query_leads(status: str | None = None, state: str | None = None,
                county: str | None = None, min_score: int | None = None,
                priority_only: bool = False, sort: str = "lead_score",
                order: str = "desc", limit: int = 500) -> list[dict]:
    clauses: list[str] = []
    params: list[Any] = []
    if status:
        clauses.append("status = ?"); params.append(status)
    if state:
        clauses.append("state = ?"); params.append(state)
    if county:
        clauses.append("county = ?"); params.append(county)
    if min_score is not None:
        clauses.append("lead_score >= ?"); params.append(min_score)
    if priority_only:
        clauses.append("priority = 1")

    allowed_sort = {"lead_score", "created_at", "updated_at", "acreage",
                    "land_value", "county", "state", "status"}
    sort = sort if sort in allowed_sort else "lead_score"
    order = "ASC" if order.lower() == "asc" else "DESC"

    where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
    q = f"SELECT * FROM leads {where} ORDER BY {sort} {order} LIMIT ?"
    params.append(limit)
    with db() as conn:
        rows = conn.execute(q, params).fetchall()
    return rows_to_dicts(rows)


def update_status(lead_id: int, new_status: str) -> None:
    with db() as conn:
        row = conn.execute("SELECT status FROM leads WHERE id = ?", (lead_id,)).fetchone()
        old = row["status"] if row else None
        conn.execute(
            "UPDATE leads SET status = ?, updated_at = datetime('now') WHERE id = ?",
            (new_status, lead_id),
        )
        conn.execute(
            "INSERT INTO status_history (lead_id, from_status, to_status) VALUES (?, ?, ?)",
            (lead_id, old, new_status),
        )


# --------------------------------------------------------------------------- #
# notes / contacts / tasks / mail / history
# --------------------------------------------------------------------------- #
def add_note(lead_id: int, body: str, author: str = "system") -> int:
    with db() as conn:
        cur = conn.execute(
            "INSERT INTO notes (lead_id, body, author) VALUES (?, ?, ?)",
            (lead_id, body, author),
        )
        return cur.lastrowid


def get_notes(lead_id: int) -> list[dict]:
    with db() as conn:
        rows = conn.execute(
            "SELECT * FROM notes WHERE lead_id = ? ORDER BY id DESC", (lead_id,)
        ).fetchall()
    return rows_to_dicts(rows)


def add_contact(lead_id: int, **kw) -> int:
    with db() as conn:
        cur = conn.execute(
            "INSERT INTO contacts (lead_id, name, phone, email, mailing_address, "
            "provider, confidence) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (lead_id, kw.get("name"), kw.get("phone"), kw.get("email"),
             kw.get("mailing_address"), kw.get("provider"), kw.get("confidence")),
        )
        return cur.lastrowid


def get_contacts(lead_id: int) -> list[dict]:
    with db() as conn:
        rows = conn.execute(
            "SELECT * FROM contacts WHERE lead_id = ? ORDER BY id DESC", (lead_id,)
        ).fetchall()
    return rows_to_dicts(rows)


def add_task(lead_id: int, type_: str, due_date: str | None, detail: str | None) -> int:
    with db() as conn:
        cur = conn.execute(
            "INSERT INTO tasks (lead_id, type, due_date, detail) VALUES (?, ?, ?, ?)",
            (lead_id, type_, due_date, detail),
        )
        return cur.lastrowid


def open_task_exists(lead_id: int, type_: str) -> bool:
    with db() as conn:
        row = conn.execute(
            "SELECT 1 FROM tasks WHERE lead_id = ? AND type = ? AND status = 'open' LIMIT 1",
            (lead_id, type_),
        ).fetchone()
    return row is not None


def get_tasks(lead_id: int | None = None, status: str | None = None) -> list[dict]:
    clauses, params = [], []
    if lead_id is not None:
        clauses.append("lead_id = ?"); params.append(lead_id)
    if status:
        clauses.append("status = ?"); params.append(status)
    where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
    with db() as conn:
        rows = conn.execute(
            f"SELECT * FROM tasks {where} ORDER BY due_date IS NULL, due_date ASC", params
        ).fetchall()
    return rows_to_dicts(rows)


def complete_task(task_id: int, status: str = "done") -> None:
    with db() as conn:
        conn.execute(
            "UPDATE tasks SET status = ?, completed_at = datetime('now') WHERE id = ?",
            (status, task_id),
        )


def queue_mail(lead_id: int, template: str, rendered: str) -> int:
    with db() as conn:
        cur = conn.execute(
            "INSERT INTO mail_queue (lead_id, template, rendered) VALUES (?, ?, ?)",
            (lead_id, template, rendered),
        )
        return cur.lastrowid


def mail_queued_exists(lead_id: int) -> bool:
    with db() as conn:
        row = conn.execute(
            "SELECT 1 FROM mail_queue WHERE lead_id = ? AND status = 'queued' LIMIT 1",
            (lead_id,),
        ).fetchone()
    return row is not None


def get_mail_queue(status: str | None = "queued") -> list[dict]:
    if status:
        with db() as conn:
            rows = conn.execute(
                "SELECT * FROM mail_queue WHERE status = ? ORDER BY id DESC", (status,)
            ).fetchall()
    else:
        with db() as conn:
            rows = conn.execute("SELECT * FROM mail_queue ORDER BY id DESC").fetchall()
    return rows_to_dicts(rows)


def mark_mail_sent(mail_id: int) -> None:
    with db() as conn:
        conn.execute(
            "UPDATE mail_queue SET status = 'sent', sent_at = datetime('now') WHERE id = ?",
            (mail_id,),
        )


def get_status_history(lead_id: int) -> list[dict]:
    with db() as conn:
        rows = conn.execute(
            "SELECT * FROM status_history WHERE lead_id = ? ORDER BY id DESC", (lead_id,)
        ).fetchall()
    return rows_to_dicts(rows)


# --------------------------------------------------------------------------- #
# dashboard stats
# --------------------------------------------------------------------------- #
def dashboard_stats() -> dict:
    with db() as conn:
        total = conn.execute("SELECT COUNT(*) c FROM leads").fetchone()["c"]
        priority = conn.execute(
            "SELECT COUNT(*) c FROM leads WHERE priority = 1"
        ).fetchone()["c"]
        by_status = {
            r["status"]: r["c"]
            for r in conn.execute(
                "SELECT status, COUNT(*) c FROM leads GROUP BY status"
            ).fetchall()
        }
        open_tasks = conn.execute(
            "SELECT COUNT(*) c FROM tasks WHERE status = 'open'"
        ).fetchone()["c"]
        queued_mail = conn.execute(
            "SELECT COUNT(*) c FROM mail_queue WHERE status = 'queued'"
        ).fetchone()["c"]
    return {
        "total_leads": total,
        "priority_leads": priority,
        "by_status": {s: by_status.get(s, 0) for s in PIPELINE},
        "open_tasks": open_tasks,
        "queued_mail": queued_mail,
    }
