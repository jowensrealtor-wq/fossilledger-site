"""Obituary aggregator adapter — GATED OFF by default.

Legacy.com and Newspapers.com generally PROHIBIT scraping in their Terms of
Service, and Newspapers.com is a paid subscription product. This project will
not scrape them by default.

The COMPLIANT path for probate/estate signals is `probate_court.py`
(public court records) plus `legal_notices.py` (published estate notices) —
both ship live.

This adapter exists only as a well-defined seam so that, IF you obtain a
licensed data feed or written permission, you can plug it in. It refuses to run
unless `ENABLE_OBITUARY_ADAPTER=true` AND you supply a real feed URL you are
permitted to use. It ships with NO endpoint and does nothing on its own.
"""
from __future__ import annotations

from typing import Iterable

from scraper.base import BaseScraper


class ObituaryAdapter(BaseScraper):
    source = "obituary_adapter"

    def __init__(self, county_cfg: dict):
        super().__init__(county_cfg)
        cfg = (county_cfg.get("sources") or {}).get("obituary") or {}
        # ONLY a feed you are licensed/permitted to consume. No default.
        self.licensed_feed_url = cfg.get("licensed_feed_url")

    def fetch(self) -> Iterable[dict]:
        if not self.settings.ENABLE_OBITUARY_ADAPTER:
            raise PermissionError(
                "Obituary adapter is disabled. Scraping Legacy.com / "
                "Newspapers.com violates their ToS. Use probate_court + "
                "legal_notices (public records) instead, or enable this only "
                "with a licensed feed. See COMPLIANCE.md."
            )
        if not self.licensed_feed_url:
            raise PermissionError(
                "Obituary adapter enabled but no licensed_feed_url configured. "
                "Supply only a feed you are permitted to consume."
            )
        import feedparser
        resp = self.get(self.licensed_feed_url)
        if resp is None or resp.status_code != 200:
            raise RuntimeError(f"Licensed feed returned "
                               f"{getattr(resp, 'status_code', 'n/a')}")
        parsed = feedparser.parse(resp.content)
        out = []
        for entry in parsed.entries:
            out.append({
                "apn": None,  # obits rarely carry a parcel; used for name-match enrichment
                "probate_signal": True,
                "decedent": getattr(entry, "title", None),
                "summary": getattr(entry, "summary", None),
                "published": getattr(entry, "published", None),
            })
        return out
