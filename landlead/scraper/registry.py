"""Maps source keys -> scraper classes, and runs them across the county list.

Adding a new source = add a class in scraper/sources/ and one line here.
"""
from __future__ import annotations

from config.settings import load_counties
from scraper.base import ScrapeResult
from scraper.sources.arcgis_parcels import ArcGISParcelScraper
from scraper.sources.code_violations import CodeViolationScraper
from scraper.sources.legal_notices import LegalNoticesScraper
from scraper.sources.obituary_adapter import ObituaryAdapter
from scraper.sources.probate_court import ProbateCourtScraper
from scraper.sources.tax_deed_auctions import TaxDeedAuctionScraper
from scraper.sources.usps_vacancy import USPSVacancyAdapter

# config key under a county's `sources:` -> scraper class
SCRAPERS = {
    "parcels": ArcGISParcelScraper,
    "tax_deed_auctions": TaxDeedAuctionScraper,
    "legal_notices": LegalNoticesScraper,
    "probate_court": ProbateCourtScraper,
    "code_violations": CodeViolationScraper,
    "obituary": ObituaryAdapter,
    "usps_vacancy": USPSVacancyAdapter,
}


def run_source(source_key: str, only_state: str | None = None) -> list[ScrapeResult]:
    """Run one source type across every county that configures it."""
    cls = SCRAPERS.get(source_key)
    if not cls:
        raise ValueError(f"Unknown source: {source_key}")

    results: list[ScrapeResult] = []
    for county in load_counties():
        if only_state and county.get("state") != only_state:
            continue
        if source_key not in (county.get("sources") or {}):
            continue
        scraper = cls(county)
        results.append(scraper.run())  # fault-tolerant; never raises
    return results


def run_all(only_state: str | None = None) -> dict[str, list[ScrapeResult]]:
    """Run every configured source across every county. Nothing fatal."""
    summary: dict[str, list[ScrapeResult]] = {}
    for source_key in SCRAPERS:
        summary[source_key] = run_source(source_key, only_state=only_state)
    return summary
