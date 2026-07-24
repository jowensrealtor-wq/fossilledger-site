"""Live parcel scraper for open Esri ArcGIS REST services.

Counties and states across the Eastern US publish parcel layers as ArcGIS
FeatureServer / MapServer endpoints designed for programmatic query (the
`/query` operation with `f=json`). Genuinely public open data — no scraping
tricks, just the documented REST API.

Buy-box filtering (vacant land, 5-100 acres — configurable):
1. Read layer metadata to discover the real field names (they vary by county).
2. Build a server-side `where` clause on acreage (or land square-footage) so a
   huge statewide layer returns only parcels in the acreage band — not millions.
3. Page through results.
4. Normalize each feature; compute acreage (from an acres field, or derived from
   a land-square-footage field / 43560).
5. Keep only VACANT parcels within [MIN, MAX] acres. Everything else is dropped
   at ingest, so the CRM shows targets, not noise.

Statewide layers (e.g. Florida Statewide Cadastral) carry each parcel's own
county, so we read county per-feature when available.

If the endpoint is dead/moved, or a `where` field guess is wrong, we degrade
gracefully (retry with `1=1`, filter client-side) and, worst case, the
BaseScraper logs it and the pipeline continues — never fatal.
"""
from __future__ import annotations

from typing import Iterable

from config.settings import get_settings, load_field_defaults
from scraper.base import BaseScraper, first_present

PAGE_SIZE = 1000
SQFT_PER_ACRE = 43560.0


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
        self.statewide = bool(parcels_cfg.get("statewide"))
        self.fields = load_field_defaults()
        s = get_settings()
        self.min_acres = s.LEAD_MIN_ACRES
        self.max_acres = s.LEAD_MAX_ACRES
        # Per-source override: some statewide layers lack reliable land-use
        # codes, so 5-100 acres alone is the target signal there. Defaults to
        # the global VACANT_ONLY setting.
        self.vacant_only = bool(parcels_cfg.get("require_vacant", s.VACANT_ONLY))
        self.max_features = s.MAX_FEATURES_PER_SOURCE
        # resolved at runtime from live metadata
        self._acre_field: str | None = None
        self._sqft_field: str | None = None

    # -- metadata / field discovery -----------------------------------------
    def _discover_fields(self) -> set[str]:
        resp = self.get(f"{self.base_url}?f=json")
        if resp is None or resp.status_code != 200:
            return set()
        names = {f["name"] for f in resp.json().get("fields", [])}
        lower = {n.lower(): n for n in names}
        for cand in self.fields.get("acreage_fields", []):
            if cand.lower() in lower:
                self._acre_field = lower[cand.lower()]
                break
        for cand in self.fields.get("acreage_sqft_fields", []):
            if cand.lower() in lower:
                self._sqft_field = lower[cand.lower()]
                break
        return names

    def _where_clause(self) -> str:
        """Server-side acreage filter when we found a usable numeric field."""
        if self._acre_field:
            return f"{self._acre_field} >= {self.min_acres} AND {self._acre_field} <= {self.max_acres}"
        if self._sqft_field:
            lo = self.min_acres * SQFT_PER_ACRE
            hi = self.max_acres * SQFT_PER_ACRE
            return f"{self._sqft_field} >= {lo} AND {self._sqft_field} <= {hi}"
        return "1=1"  # no numeric field found -> filter entirely client-side

    def _query_page(self, offset: int, where: str) -> tuple[list[dict], bool]:
        """Return (features, where_rejected). where_rejected=True means the
        server errored on our where clause (e.g. bad field guess)."""
        params = {
            "where": where, "outFields": "*", "f": "json",
            "returnGeometry": "true", "outSR": "4326",
            "resultOffset": offset, "resultRecordCount": PAGE_SIZE,
        }
        resp = self.get(f"{self.base_url}/query", params=params)
        if resp is None or resp.status_code != 200:
            return [], False
        data = resp.json()
        if "error" in data:
            if where != "1=1":
                return [], True   # signal caller to retry unfiltered
            raise RuntimeError(f"ArcGIS error: {data['error'].get('message')}")
        return data.get("features", []), False

    # -- normalization ------------------------------------------------------
    def _acreage(self, attrs: dict) -> float | None:
        acres = first_present(attrs, self.fields.get("acreage_fields", []))
        if acres is not None:
            try:
                return float(acres)
            except (TypeError, ValueError):
                pass
        sqft = first_present(attrs, self.fields.get("acreage_sqft_fields", []))
        if sqft is not None:
            try:
                return float(sqft) / SQFT_PER_ACRE
            except (TypeError, ValueError):
                pass
        return None

    def _is_vacant(self, attrs: dict) -> bool:
        code = first_present(attrs, self.fields.get("landuse_fields", []))
        if code is None:
            return False
        norm = str(code).strip().lstrip("0") or "0"
        if self.vacant_codes and norm in self.vacant_codes:
            return True
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
            return sum(p[1] for p in pts) / len(pts), sum(p[0] for p in pts) / len(pts)
        return None, None

    def _mailing(self, attrs: dict) -> str | None:
        """Owner mailing address: single field, or assembled from parts
        (FDOR-style OWN_ADDR1 / OWN_CITY / OWN_STATE / OWN_ZIPCD)."""
        single = first_present(attrs, self.fields.get("mailing_fields", []))
        if single:
            return str(single).strip()
        parts = [
            first_present(attrs, ["OWN_ADDR1", "OWNER_ADDR1", "MAIL_ADDR1"]),
            first_present(attrs, ["OWN_CITY", "OWNER_CITY", "MAIL_CITY"]),
            first_present(attrs, ["OWN_STATE", "OWNER_STATE", "MAIL_STATE"]),
            first_present(attrs, ["OWN_ZIPCD", "OWNER_ZIP", "MAIL_ZIP"]),
        ]
        parts = [str(p).strip() for p in parts if p not in (None, "", " ")]
        return ", ".join(parts) if parts else None

    def _situs(self, attrs: dict) -> str | None:
        single = first_present(attrs, self.fields.get("situs_fields", []))
        if single:
            return str(single).strip()
        parts = [
            first_present(attrs, ["PHY_ADDR1", "SITE_ADDR1"]),
            first_present(attrs, ["PHY_CITY", "SITE_CITY"]),
        ]
        parts = [str(p).strip() for p in parts if p not in (None, "", " ")]
        return ", ".join(parts) if parts else None

    def _county_of(self, attrs: dict) -> str | None:
        if not self.statewide:
            return self.county
        return (first_present(attrs, self.fields.get("county_fields", []))
                or self.county)

    def _normalize(self, feature: dict) -> dict | None:
        attrs = feature.get("attributes", {})
        apn = first_present(attrs, self.fields.get("apn_fields", []))
        if not apn:
            return None  # no canonical key -> unusable for dedup

        acreage = self._acreage(attrs)
        vacant = self._is_vacant(attrs)

        # Buy-box enforcement (client-side safety net over the server filter).
        if acreage is None or not (self.min_acres <= acreage <= self.max_acres):
            return None
        if self.vacant_only and not vacant:
            return None

        mailing = self._mailing(attrs)
        situs = self._situs(attrs)
        owner = first_present(attrs, self.fields.get("owner_fields", []))
        landval = first_present(attrs, self.fields.get("landval_fields", []))
        lat, lon = self._centroid(feature.get("geometry"))

        absentee = bool(mailing and situs
                        and str(mailing).strip().lower() != str(situs).strip().lower())
        st = (self.state or "").upper()
        out_of_state = bool(mailing and st and st not in str(mailing).upper())

        try:
            landval_val = float(landval) if landval is not None else None
        except (TypeError, ValueError):
            landval_val = None

        return {
            "apn": str(apn).strip(),
            "county": self._county_of(attrs),
            "owner_name": str(owner).strip() if owner else None,
            "owner_mailing_address": mailing,
            "property_address": situs,
            "acreage": round(acreage, 2),
            "land_value": landval_val,
            "latitude": lat,
            "longitude": lon,
            "absentee": absentee,
            "out_of_state_owner": out_of_state,
            "vacant_confirmed": vacant,
        }

    def fetch(self) -> Iterable[dict]:
        if not self.base_url:
            raise ValueError(f"No arcgis_url configured for {self.county}, {self.state}")

        self._discover_fields()   # dead/moved endpoint raises here -> logged
        where = self._where_clause()

        collected: list[dict] = []
        offset = 0
        while offset < self.max_features:
            page, where_rejected = self._query_page(offset, where)
            if where_rejected:
                # server didn't like our field guess; restart unfiltered
                where = "1=1"
                offset = 0
                collected.clear()
                continue
            if not page:
                break
            for feature in page:
                rec = self._normalize(feature)
                if rec:
                    collected.append(rec)
            if len(page) < PAGE_SIZE:
                break
            offset += PAGE_SIZE
        return collected
