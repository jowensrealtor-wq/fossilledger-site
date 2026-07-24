"""Deduplication + merge of raw records into canonical leads, keyed on APN.

APN (Assessor Parcel Number) is the canonical key. We normalize it (strip
separators, uppercase) so the same parcel written `12-34-567` and `1234567`
collapses to one lead. Records without an APN cannot anchor a lead on their own;
they are retained as raw records and folded in by owner-name match where a
lead with that owner already exists.
"""
from __future__ import annotations

from db import repo
from db.database import db, loads
from db.repo import normalize_apn  # canonical dedup key lives with the repo

SIGNAL_FIELDS = ("tax_delinquent", "probate_signal", "code_violation",
                 "vacant_confirmed", "absentee", "out_of_state_owner")
COPY_FIELDS = ("owner_name", "owner_mailing_address", "property_address",
               "acreage", "land_value", "assessed_value", "latitude",
               "longitude", "last_sale_date", "last_sale_price",
               "tax_delinquent_amount")


def _unprocessed_raw() -> list[dict]:
    """All raw records; dedup is idempotent so reprocessing is safe."""
    with db() as conn:
        rows = conn.execute("SELECT * FROM raw_records ORDER BY id ASC").fetchall()
    out = []
    for r in rows:
        d = {k: r[k] for k in r.keys()}
        d["payload"] = loads(d["payload"], {})
        out.append(d)
    return out


def run_dedup() -> dict:
    """Fold raw records into canonical leads. Returns a small summary."""
    raw = _unprocessed_raw()

    apn_records: dict[str, list[dict]] = {}
    orphan_by_owner: list[dict] = []

    for rec in raw:
        payload = rec["payload"]
        norm = normalize_apn(rec.get("apn") or payload.get("apn"))
        if norm:
            apn_records.setdefault(norm, []).append(rec)
        elif payload.get("owner_name") or payload.get("decedent"):
            orphan_by_owner.append(rec)

    created_or_updated = 0
    for norm_apn, recs in apn_records.items():
        merged: dict = {"county": None, "state": None}
        contributing_sources: list[str] = []
        for rec in recs:
            payload = rec["payload"]
            contributing_sources.append(rec["source"])
            merged["county"] = merged["county"] or rec.get("county") or payload.get("county")
            merged["state"] = merged["state"] or rec.get("state") or payload.get("state")
            for f in COPY_FIELDS:
                val = payload.get(f)
                if val not in (None, "", 0):
                    merged.setdefault(f, val)
            for f in SIGNAL_FIELDS:
                if payload.get(f):
                    merged[f] = True
        # Use the original (unnormalized) APN from the first record for display.
        display_apn = recs[0].get("apn") or recs[0]["payload"].get("apn") or norm_apn
        repo.upsert_lead(display_apn, "+".join(sorted(set(contributing_sources))), merged)
        created_or_updated += 1

    # Fold APN-less signal records (obits, some legal notices) into existing
    # leads by exact owner-name match.
    orphan_folded = _fold_orphans_by_owner(orphan_by_owner)

    return {
        "raw_records": len(raw),
        "unique_apns": len(apn_records),
        "leads_upserted": created_or_updated,
        "orphans_folded": orphan_folded,
    }


def _fold_orphans_by_owner(orphans: list[dict]) -> int:
    folded = 0
    all_leads = repo.all_leads()
    by_owner: dict[str, list[int]] = {}
    for lead in all_leads:
        name = (lead.get("owner_name") or "").strip().lower()
        if name:
            by_owner.setdefault(name, []).append(lead["id"])

    for rec in orphans:
        payload = rec["payload"]
        name = (payload.get("owner_name") or payload.get("decedent") or "").strip().lower()
        if not name or name not in by_owner:
            continue
        for lead_id in by_owner[name]:
            if payload.get("probate_signal"):
                _set_flag(lead_id, "probate_signal")
            note = payload.get("summary") or payload.get("context") or payload.get("title")
            if note:
                repo.add_note(lead_id, f"[{rec['source']}] {note}", author="enrichment")
            folded += 1
    return folded


def _set_flag(lead_id: int, flag: str) -> None:
    if flag not in SIGNAL_FIELDS:
        return
    with db() as conn:
        conn.execute(
            f"UPDATE leads SET {flag} = 1, updated_at = datetime('now') WHERE id = ?",
            (lead_id,),
        )
