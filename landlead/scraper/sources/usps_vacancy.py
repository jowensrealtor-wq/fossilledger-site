"""USPS vacancy / NCOA-adjacent adapter — GATED OFF by default.

Important: NCOA (National Change of Address) and USPS vacancy indicators are
NOT free public data. They are distributed only through licensed USPS partners
under contract, with strict usage rules. There is no compliant "public"
scraping path for this signal.

This adapter therefore does not scrape anything. It defines the seam for a
licensed integration and refuses to run unless `ENABLE_USPS_VACANCY=true` and a
real licensee endpoint + key are supplied. Absent that, the `absentee` signal we
already derive from parcel mailing-vs-situs mismatch (see arcgis_parcels.py) is
the compliant, no-license proxy the pipeline relies on.
"""
from __future__ import annotations

from typing import Iterable

from scraper.base import BaseScraper


class USPSVacancyAdapter(BaseScraper):
    source = "usps_vacancy"

    def __init__(self, county_cfg: dict):
        super().__init__(county_cfg)
        cfg = (county_cfg.get("sources") or {}).get("usps_vacancy") or {}
        self.licensee_url = cfg.get("licensee_url")

    def fetch(self) -> Iterable[dict]:
        if not self.settings.ENABLE_USPS_VACANCY:
            raise PermissionError(
                "USPS vacancy adapter is disabled. NCOA/vacancy data is licensed, "
                "not public. Rely on the mailing-vs-situs 'absentee' signal, or "
                "enable this only with a USPS licensee integration. See COMPLIANCE.md."
            )
        if not (self.licensee_url and self.settings.USPS_API_KEY):
            raise PermissionError(
                "USPS vacancy enabled but licensee_url / USPS_API_KEY missing."
            )
        # Placeholder for a real licensee API call. Shape depends on the vendor.
        raise NotImplementedError(
            "Wire your USPS licensee API here; response should yield records with "
            "an `apn` and a `vacant` boolean."
        )
        # pragma: no cover
        return []  # noqa: unreachable — documents the expected return shape
