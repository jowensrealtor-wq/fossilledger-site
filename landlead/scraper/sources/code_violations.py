"""Municipal code-violation adapter (overgrown-lot / nuisance-abatement notices).

Many municipalities publish code-enforcement cases on open-data portals
(Socrata, ArcGIS, or a search page). Overgrown-lot and nuisance-abatement
notices tied to a vacant parcel are a strong distress signal.

Configure per county:

  sources:
    code_violations:
      socrata_url: "https://data.<city>.gov/resource/<dataset>.json"  # open data
      # -- or --
      results_url: "https://<city>/code-enforcement/cases"            # HTML list

Unconfigured -> clean skip. Never fabricates records.
"""
from __future__ import annotations

import re
from typing import Iterable

from bs4 import BeautifulSoup

from scraper.base import BaseScraper

APN_RE = re.compile(r"\b(?:APN|Parcel)\s*[:#]?\s*([0-9A-Za-z\-\.]{6,})", re.I)
VACANT_LOT_KEYWORDS = ("overgrown", "tall grass", "weeds", "nuisance",
                       "vacant lot", "unimproved", "lot clearing", "abatement",
                       "high grass", "debris")


class CodeViolationScraper(BaseScraper):
    source = "code_violations"

    def __init__(self, county_cfg: dict):
        super().__init__(county_cfg)
        cfg = (county_cfg.get("sources") or {}).get("code_violations") or {}
        self.socrata_url = cfg.get("socrata_url")
        self.results_url = cfg.get("results_url")

    def fetch(self) -> Iterable[dict]:
        if not (self.socrata_url or self.results_url):
            raise PermissionError(
                f"No code_violations endpoint configured for {self.county}, "
                f"{self.state}. Add sources.code_violations.socrata_url or "
                f".results_url."
            )
        if self.socrata_url:
            return list(self._fetch_socrata())
        return list(self._fetch_html())

    def _fetch_socrata(self) -> Iterable[dict]:
        resp = self.get(self.socrata_url)
        if resp is None or resp.status_code != 200:
            raise RuntimeError(f"Socrata returned "
                               f"{getattr(resp, 'status_code', 'n/a')}")
        rows = resp.json()
        out = []
        for row in rows:
            blob = " ".join(str(v).lower() for v in row.values())
            if not any(k in blob for k in VACANT_LOT_KEYWORDS):
                continue
            out.append({
                "apn": row.get("apn") or row.get("parcel") or row.get("parcel_id"),
                "code_violation": True,
                "property_address": row.get("address") or row.get("location"),
                "violation": row.get("violation") or row.get("description")
                             or row.get("case_type"),
            })
        return out

    def _fetch_html(self) -> Iterable[dict]:
        resp = self.get(self.results_url)
        if resp is None or resp.status_code != 200:
            raise RuntimeError(f"Code page returned "
                               f"{getattr(resp, 'status_code', 'n/a')}")
        soup = BeautifulSoup(resp.text, "lxml")
        out = []
        for block in soup.find_all(["tr", "li", "div"]):
            text = " ".join(block.get_text(" ", strip=True).split())
            low = text.lower()
            if not text or not any(k in low for k in VACANT_LOT_KEYWORDS):
                continue
            apn_match = APN_RE.search(text)
            out.append({
                "apn": apn_match.group(1) if apn_match else None,
                "code_violation": True,
                "context": text[:400],
            })
        return out
