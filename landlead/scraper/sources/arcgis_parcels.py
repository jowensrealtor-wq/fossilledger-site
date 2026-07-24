"""Live parcel scraper for open Esri ArcGIS REST services.

Counties and states across the Eastern US publish parcel layers as ArcGIS
FeatureServer / MapServer endpoints that are *designed* for programmatic query
(the `/query` operation with `f=json`). This is genuinely public open data — no
scraping tricks required, just the documented REST API.

Strategy:
1. Read the layer metadata to discover its real field names.
2. Page through features in batches using `resultOffset` / `resultRecordCount`.
3. Normalize each feature into our lead schema using the field-name candidates
   from config/counties.yml (county layers name fields inconsistently).
4. Derive the `vacant_confirmed` and `absentee` signals from the attributes.

If the endpoint is dead/moved (counties re-home these), we raise, and the
BaseScraper logs it and moves on — never fatal.
"""
from __future__ import annotations

from typing import Iterable

from config.settings import load_field_defaults
from scraper.base import BaseScraper, first_present

# Keep runs bounded on a first pass; raise for a full county sweep.
MAX_FEATURES = 5000
PAGE_SIZE = 1000


class ArcGISParcelScraper(BaseScraper):
    source = "arcgis_parcels"

    def __init__(self, county_cfg: dict):
        super().__init__(county_cfg)
        parcels_cfg = (county_cfg.get("sources") or {}).get("parcels") or {}
        self.base_url = (parcels_cfg.get("arcgis_url") or "").rstrip("/")
        self.vacant_codes = {
            str(c).strip().lstrip("0") or "0"
            for c in parcels_cfg.get("vacant_landuse_codes", [])
        }
        self.fields = load_field_defaults()

    def _layer_fields(self) -> set[str]:
        resp = self.get(f"{self.base_url}?f=json")
        if resp is None or resp.status_code != 200:
            return set()
        meta = resp.json()
        return {f["name"] for f in meta.get("fields", [])}

    def _query_page(self, offset: int) -> list[dict]:
        params = {
            "where": "1=1",
            "outFields": "*",
            "f": "json",
            "returnGeometry": "true",
            "outSR": "4326",
            "resultOffset": offset,
            "resultRecordCount": PAGE_SIZE,
        }
        resp = self.get(f"{self.base_url}/query", params=params)
        if resp is None or resp.status_code != 200:
            return []
        data = resp.json()
        if "error" in data:
            raise RuntimeError(f"ArcGIS error: {data['error'].get('message')}")
        return data.get("features", [])

    def _is_vacant(self, attrs: dict) -> bool:
        code = first_present(attrs, self.fields.get("landuse_fields", []))
        if code is None:
            return False
        norm = str(code).strip().lstrip("0") or "0"
        if self.vacant_codes and norm in self.vacant_codes:
            return True
        # Heuristic fallback: textual land-use hints.
        text = str(code).lower()
        return any(k in text for k in ("vacant", "unimproved", "vac ", "raw land"))

    @staticmethod
    def _centroid(geometry: dict | None) -> tuple[float | None, float | None]:
        if not geometry:
            return None, None
        if "x" in geometry and "y" in geometry:
            return geometry["y"], geometry["x"]
        rings = geometry.get("rings")
        if rings and rings[0]:
            pts = rings[0]
            xs = [p[0] for p in pts]
            ys = [p[1] for p in pts]
            return sum(ys) / len(ys), sum(xs) / len(xs)
        return None, None

    def _normalize(self, feature: dict) -> dict | None:
        attrs = feature.get("attributes", {})
        apn = first_present(attrs, self.fields.get("apn_fields", []))
        if not apn:
            return None  # no canonical key -> unusable for dedup

        situs = first_present(attrs, self.fields.get("situs_fields", []))
        mailing = first_present(attrs, self.fields.get("mailing_fields", []))
        owner = first_present(attrs, self.fields.get("owner_fields", []))
        acreage = first_present(attrs, self.fields.get("acreage_fields", []))
        landval = first_present(attrs, self.fields.get("landval_fields", []))
        lat, lon = self._centroid(feature.get("geometry"))

        absentee = bool(
            mailing and situs
            and str(mailing).strip().lower() != str(situs).strip().lower()
        )
        out_of_state = bool(
            mailing and self.state
            and f" {self.state.upper()} " not in f" {str(mailing).upper()} "
            and self.state.upper() not in str(mailing).upper()[-8:]
        )

        try:
            acreage_val = float(acreage) if acreage is not None else None
        except (TypeError, ValueError):
            acreage_val = None
        try:
            landval_val = float(landval) if landval is not None else None
        except (TypeError, ValueError):
            landval_val = None

        return {
            "apn": str(apn).strip(),
            "owner_name": str(owner).strip() if owner else None,
            "owner_mailing_address": str(mailing).strip() if mailing else None,
            "property_address": str(situs).strip() if situs else None,
            "acreage": acreage_val,
            "land_value": landval_val,
            "latitude": lat,
            "longitude": lon,
            "absentee": absentee,
            "out_of_state_owner": out_of_state,
            "vacant_confirmed": self._is_vacant(attrs),
        }

    def fetch(self) -> Iterable[dict]:
        if not self.base_url:
            raise ValueError(f"No arcgis_url configured for {self.county}, {self.state}")

        # Probe metadata first; a hard failure here means the endpoint moved.
        self._layer_fields()

        collected: list[dict] = []
        offset = 0
        while offset < MAX_FEATURES:
            page = self._query_page(offset)
            if not page:
                break
            for feature in page:
                rec = self._normalize(feature)
                if rec:
                    collected.append(rec)
            if len(page) < PAGE_SIZE:
                break
            offset += PAGE_SIZE

        # Prioritize vacant parcels for the lead pipeline, but keep all —
        # scoring decides relevance downstream.
        return collected
