"""Legal-notice scraper via RSS/Atom feeds (feedparser).

State press associations and many papers publish public legal notices as feeds
(estate notices, land sales, guardianship/conservatorship filings). These are
published *for the purpose of public notice*, so consuming the feed is exactly
their intended use.

We parse each entry, classify a coarse notice type, extract an APN if the
notice text happens to include one, and flag probate/estate signals. Notices
without an APN are still stored as raw records (they enrich existing leads by
owner-name match downstream) but cannot themselves create a deduped lead.
"""
from __future__ import annotations

import re
from typing import Iterable

from scraper.base import BaseScraper

APN_RE = re.compile(r"\b(?:APN|Parcel(?:\s*(?:No|ID|#))?)\s*[:#]?\s*([0-9A-Za-z\-\.]{6,})", re.I)
PROBATE_KEYWORDS = ("estate of", "probate", "administrat", "executor",
                    "heirs", "decedent", "conservator", "guardian")
LANDSALE_KEYWORDS = ("land sale", "acreage", "vacant lot", "real property",
                     "tract of land", "parcel of land")


class LegalNoticesScraper(BaseScraper):
    source = "legal_notices"

    def __init__(self, county_cfg: dict):
        super().__init__(county_cfg)
        cfg = (county_cfg.get("sources") or {}).get("legal_notices") or {}
        self.rss = cfg.get("rss")

    @staticmethod
    def _classify(text: str) -> tuple[str, bool, bool]:
        low = text.lower()
        probate = any(k in low for k in PROBATE_KEYWORDS)
        landsale = any(k in low for k in LANDSALE_KEYWORDS)
        if probate:
            ntype = "probate/estate"
        elif landsale:
            ntype = "land sale"
        else:
            ntype = "other"
        return ntype, probate, landsale

    def fetch(self) -> Iterable[dict]:
        if not self.rss:
            raise ValueError(f"No legal_notices.rss configured for {self.county}")

        try:
            import feedparser
        except ImportError as exc:
            raise PermissionError(f"feedparser not installed; skipping RSS ({exc})")

        # feedparser fetches the URL itself; route it through our polite GET so
        # robots + rate-limit still apply, then hand the bytes to the parser.
        resp = self.get(self.rss)
        if resp is None or resp.status_code != 200:
            raise RuntimeError(f"Feed returned status {getattr(resp, 'status_code', 'n/a')}")

        parsed = feedparser.parse(resp.content)
        out: list[dict] = []
        for entry in parsed.entries:
            title = getattr(entry, "title", "") or ""
            summary = getattr(entry, "summary", "") or ""
            text = f"{title}\n{summary}"
            ntype, probate, _landsale = self._classify(text)
            apn_match = APN_RE.search(text)
            out.append({
                "apn": apn_match.group(1) if apn_match else None,
                "notice_type": ntype,
                "probate_signal": probate,
                "title": title,
                "summary": summary,
                "link": getattr(entry, "link", None),
                "published": getattr(entry, "published", None),
            })
        return out
