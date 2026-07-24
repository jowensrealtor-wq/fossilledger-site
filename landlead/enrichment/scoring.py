"""Lead scoring (1-100) with a transparent, auditable breakdown.

The score is a weighted sum of motivated-seller signals, clamped to 1-100. Every
lead stores its `score_breakdown` so you can see *why* it scored what it did —
no black box. Tune the weights below to match your buy-box.
"""
from __future__ import annotations

from config.settings import get_settings

# Signal -> (points, human label). Weights are deliberately explicit.
WEIGHTS = {
    "tax_delinquent":     (25, "Tax delinquent / in tax sale"),
    "probate_signal":     (20, "Probate / estate signal"),
    "absentee":           (15, "Absentee owner (mailing != property)"),
    "out_of_state_owner": (12, "Out-of-state owner"),
    "code_violation":     (10, "Code violation (overgrown/nuisance lot)"),
    "vacant_confirmed":   (10, "Confirmed vacant / unimproved"),
}


def _acreage_points(acreage: float | None) -> tuple[int, str]:
    if not acreage:
        return 0, ""
    if acreage >= 20:
        return 8, f"Large parcel ({acreage:.1f} ac)"
    if acreage >= 5:
        return 5, f"Sizable parcel ({acreage:.1f} ac)"
    if acreage >= 1:
        return 3, f"Buildable acreage ({acreage:.1f} ac)"
    return 1, f"Small lot ({acreage:.2f} ac)"


def _staleness_points(last_sale_date: str | None) -> tuple[int, str]:
    """Longer hold since last transaction => higher motivation potential."""
    if not last_sale_date:
        return 0, ""
    year = None
    for token in str(last_sale_date).replace("-", "/").split("/"):
        if token.isdigit() and len(token) == 4:
            year = int(token)
            break
    if year is None:
        return 0, ""
    from datetime import date
    held = date.today().year - year
    if held >= 20:
        return 8, f"Held {held}+ yrs"
    if held >= 10:
        return 5, f"Held {held} yrs"
    if held >= 5:
        return 2, f"Held {held} yrs"
    return 0, ""


def score_lead(lead: dict) -> tuple[int, bool, dict]:
    """Return (score 1-100, is_priority, breakdown)."""
    settings = get_settings()
    breakdown: dict[str, int] = {}
    total = 0

    for field, (pts, label) in WEIGHTS.items():
        if lead.get(field):
            total += pts
            breakdown[label] = pts

    a_pts, a_label = _acreage_points(lead.get("acreage"))
    if a_pts:
        total += a_pts
        breakdown[a_label] = a_pts

    s_pts, s_label = _staleness_points(lead.get("last_sale_date"))
    if s_pts:
        total += s_pts
        breakdown[s_label] = s_pts

    # Multi-source corroboration bonus.
    sources = lead.get("sources")
    if isinstance(sources, str):
        n_sources = sources.count(",") + sources.count("+") + 1 if sources else 0
    elif isinstance(sources, list):
        n_sources = len(sources)
    else:
        n_sources = 0
    if n_sources >= 2:
        total += 5
        breakdown["Corroborated by 2+ sources"] = 5

    score = max(1, min(100, total))
    is_priority = score >= settings.HIGH_PRIORITY_THRESHOLD
    return score, is_priority, breakdown


def score_all() -> dict:
    """Score every lead in the DB. Returns a summary."""
    from db import repo
    leads = repo.all_leads()
    scored = 0
    promoted = 0
    for lead in leads:
        score, priority, breakdown = score_lead(lead)
        repo.set_score(lead["id"], score, priority, breakdown)
        scored += 1
        if priority:
            promoted += 1
    return {"scored": scored, "high_priority": promoted}
