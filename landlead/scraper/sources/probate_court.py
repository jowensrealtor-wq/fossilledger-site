"""Public probate-court record adapter.

County probate/surrogate court record indexes ARE public records and are the
compliant way to source probate/estate signals (as opposed to scraping
ToS-restricted obituary aggregators — see obituary_adapter.py and COMPLIANCE.md).

Because every county exposes these differently (some have an open case-search
JSON endpoint, many only a search form, some nothing online), this ships as an
adapter with a documented contract. Configure a county with either:

  sources:
    probate_court:
      json_url: "https://<county-court>/api/cases?type=estate"   # ideal
      # -- or --
      results_url: "https://<county-court>/estate-notices"        # HTML list

If neither is configured, the adapter records a clean 'skipped' — it never
invents data. Fill in the real endpoint from the county's court portal.
"""
from __future__ import annotations

import re
from typing import Iterable

from bs4 import BeautifulSoup

from scraper.base import BaseScraper

APN_RE = re.compile(r"\b(?:APN|Parcel)\s*[:#]?\s*([0-9A-Za-z\-\.]{6,})", re.I)


class ProbateCourtScraper(BaseScraper):
    source = "probate_court"

    def __init__(self, county_cfg: dict):
        super().__init__(county_cfg)
        cfg = (county_cfg.get("sources") or {}).get("probate_court") or {}
        self.json_url = cfg.get("json_url")
        self.results_url = cfg.get("results_url")

    def fetch(self) -> Iterable[dict]:
        if not (self.json_url or self.results_url):
            raise PermissionError(
                f"No probate_court endpoint configured for {self.county}, "
                f"{self.state}. Add sources.probate_court.json_url or "
                f".results_url from the county court portal."
            )
        if self.json_url:
            return list(self._fetch_json())
        return list(self._fetch_html())

    def _fetch_json(self) -> Iterable[dict]:
        resp = self.get(self.json_url)
        if resp is None or resp.status_code != 200:
            raise RuntimeError(f"Probate JSON returned "
                               f"{getattr(resp, 'status_code', 'n/a')}")
        data = resp.json()
        cases = data if isinstance(data, list) else data.get("cases", data.get("results", []))
        out = []
        for case in cases:
            out.append({
                "apn": case.get("apn") or case.get("parcel"),
                "probate_signal": True,
                "decedent": case.get("decedent") or case.get("name"),
                "case_number": case.get("case_number") or case.get("caseNumber"),
                "filed": case.get("filed") or case.get("filing_date"),
                "owner_name": case.get("decedent") or case.get("name"),
            })
        return out

    def _fetch_html(self) -> Iterable[dict]:
        resp = self.get(self.results_url)
        if resp is None or resp.status_code != 200:
            raise RuntimeError(f"Probate page returned "
                               f"{getattr(resp, 'status_code', 'n/a')}")
        soup = BeautifulSoup(resp.text, "html.parser")
        out = []
        for block in soup.find_all(["tr", "li", "article", "div"]):
            text = " ".join(block.get_text(" ", strip=True).split())
            low = text.lower()
            if not text or not any(k in low for k in ("estate", "probate", "administrat")):
                continue
            apn_match = APN_RE.search(text)
            out.append({
                "apn": apn_match.group(1) if apn_match else None,
                "probate_signal": True,
                "context": text[:400],
            })
        return out
