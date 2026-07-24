"""Enrichment orchestrator: dedup -> score, in one call."""
from __future__ import annotations

from enrichment.dedup import run_dedup
from enrichment.scoring import score_all


def run_enrichment() -> dict:
    dedup_summary = run_dedup()
    score_summary = score_all()
    return {"dedup": dedup_summary, "scoring": score_summary}
