"""Base scraper: polite HTTP with robots.txt, rate limiting, and honest UA.

Design choices (see COMPLIANCE.md):
- ONE honest, identifying User-Agent. We do not rotate UAs to evade bot
  protection. If a site blocks an honest, rate-limited crawler, that's a signal
  to stop and seek permission or a licensed feed, not to disguise ourselves.
- robots.txt is honored by default.
- A minimum per-host delay is enforced.
- Every scraper is fault-tolerant: `.run()` catches, logs, and returns cleanly
  so one failing source never crashes a pipeline run.
"""
from __future__ import annotations

import threading
import time
import urllib.robotparser
from dataclasses import dataclass, field
from typing import Any, Iterable
from urllib.parse import urlparse

import requests

from config.settings import get_settings
from db import repo

_LAST_REQUEST: dict[str, float] = {}
_LOCK = threading.Lock()
_ROBOTS_CACHE: dict[str, urllib.robotparser.RobotFileParser] = {}


@dataclass
class ScrapeResult:
    source: str
    county: str | None = None
    state: str | None = None
    records: list[dict] = field(default_factory=list)
    status: str = "ok"          # ok | error | skipped
    message: str | None = None


class BaseScraper:
    """Subclass and implement `fetch()` -> iterable of normalized record dicts.

    A normalized record SHOULD include, where available:
      apn, county, state, owner_name, owner_mailing_address, property_address,
      acreage, land_value, latitude, longitude, plus any signal flags
      (tax_delinquent, probate_signal, code_violation, vacant_confirmed).
    """

    source: str = "base"

    def __init__(self, county_cfg: dict | None = None):
        self.settings = get_settings()
        self.county_cfg = county_cfg or {}
        self.county = self.county_cfg.get("name")
        self.state = self.county_cfg.get("state")
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": self.settings.USER_AGENT})

    # -- politeness helpers --------------------------------------------------
    def _robots_ok(self, url: str) -> bool:
        if not self.settings.RESPECT_ROBOTS:
            return True
        parsed = urlparse(url)
        root = f"{parsed.scheme}://{parsed.netloc}"
        rp = _ROBOTS_CACHE.get(root)
        if rp is None:
            rp = urllib.robotparser.RobotFileParser()
            rp.set_url(f"{root}/robots.txt")
            try:
                rp.read()
            except Exception:
                # If robots.txt is unreachable, be conservative but not blocked:
                # allow, since many county servers 404 their robots file.
                rp = None
            _ROBOTS_CACHE[root] = rp  # type: ignore[assignment]
        if rp is None:
            return True
        return rp.can_fetch(self.settings.USER_AGENT, url)

    def _throttle(self, url: str) -> None:
        host = urlparse(url).netloc
        with _LOCK:
            last = _LAST_REQUEST.get(host, 0.0)
            wait = self.settings.RATE_LIMIT_SECONDS - (time.time() - last)
            if wait > 0:
                time.sleep(wait)
            _LAST_REQUEST[host] = time.time()

    def get(self, url: str, **kwargs) -> requests.Response | None:
        """Rate-limited, robots-aware GET. Returns None if disallowed/blocked."""
        if not self._robots_ok(url):
            raise PermissionError(f"robots.txt disallows fetching {url}")
        self._throttle(url)
        kwargs.setdefault("timeout", self.settings.TIMEOUT_SECONDS)
        return self.session.get(url, **kwargs)

    # -- contract ------------------------------------------------------------
    def fetch(self) -> Iterable[dict]:
        raise NotImplementedError

    def run(self) -> ScrapeResult:
        """Execute the scraper with full fault tolerance + run logging."""
        log_id = repo.log_start(self.source, self.county, self.state)
        result = ScrapeResult(source=self.source, county=self.county, state=self.state)
        try:
            records = list(self.fetch())
            for rec in records:
                rec.setdefault("county", self.county)
                rec.setdefault("state", self.state)
                repo.insert_raw(
                    source=self.source,
                    county=rec.get("county"),
                    state=rec.get("state"),
                    apn=rec.get("apn"),
                    payload=rec,
                )
            result.records = records
            result.status = "ok"
            repo.log_finish(log_id, "ok", records_found=len(records))
        except PermissionError as exc:
            result.status = "skipped"
            result.message = str(exc)
            repo.log_finish(log_id, "skipped", message=str(exc))
        except Exception as exc:  # never crash the pipeline
            result.status = "error"
            result.message = f"{type(exc).__name__}: {exc}"
            repo.log_finish(log_id, "error", message=result.message)
        return result


def first_present(record: dict, candidates: list[str]) -> Any:
    """Case-insensitive lookup of the first present, non-empty field."""
    lower = {k.lower(): v for k, v in record.items()}
    for cand in candidates:
        val = lower.get(cand.lower())
        if val not in (None, "", " "):
            return val
    return None
