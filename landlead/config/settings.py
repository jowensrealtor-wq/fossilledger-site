"""Central configuration loader.

Reads environment (via .env if present) and the YAML county target list.
Everything has a safe default so the system runs with zero configuration.
"""
from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

import yaml

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:  # dotenv is optional
    pass

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_DIR = BASE_DIR / "config"


def _as_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


class Settings:
    # --- Database ---
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'landlead.db'}")

    # --- Scraper politeness ---
    USER_AGENT: str = os.getenv(
        "SCRAPER_USER_AGENT",
        "LandLeadBot/1.0 (+mailto:jowensrealtor@gmail.com)",
    )
    RATE_LIMIT_SECONDS: float = float(os.getenv("SCRAPER_RATE_LIMIT_SECONDS", "3.0"))
    TIMEOUT_SECONDS: int = int(os.getenv("SCRAPER_TIMEOUT_SECONDS", "30"))
    RESPECT_ROBOTS: bool = _as_bool(os.getenv("SCRAPER_RESPECT_ROBOTS"), True)

    # --- Optional / gated sources ---
    ENABLE_OBITUARY_ADAPTER: bool = _as_bool(os.getenv("ENABLE_OBITUARY_ADAPTER"), False)
    ENABLE_USPS_VACANCY: bool = _as_bool(os.getenv("ENABLE_USPS_VACANCY"), False)
    USPS_API_KEY: str = os.getenv("USPS_API_KEY", "")

    # --- Skip trace ---
    SKIPTRACE_PROVIDER: str = os.getenv("SKIPTRACE_PROVIDER", "").strip().lower()
    SKIPTRACE_KEYS: dict[str, str] = {
        "tlo": os.getenv("TLO_API_KEY", ""),
        "batchskiptracing": os.getenv("BATCHSKIPTRACING_API_KEY", ""),
        "idi": os.getenv("IDI_API_KEY", ""),
    }

    # --- Scheduler ---
    ENABLE_SCHEDULER: bool = _as_bool(os.getenv("ENABLE_SCHEDULER"), True)

    # --- Scoring / pipeline ---
    HIGH_PRIORITY_THRESHOLD: int = 70

    @property
    def sqlite_path(self) -> str | None:
        if self.DATABASE_URL.startswith("sqlite:///"):
            return self.DATABASE_URL.replace("sqlite:///", "", 1)
        return None


@lru_cache
def get_settings() -> Settings:
    return Settings()


@lru_cache
def load_counties() -> list[dict]:
    """Return the county target list with `defaults` merged into each entry."""
    path = CONFIG_DIR / "counties.yml"
    with open(path, "r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    defaults = data.get("defaults", {})
    counties = data.get("counties", [])
    for county in counties:
        county.setdefault("_field_map", defaults)
    return counties


@lru_cache
def load_field_defaults() -> dict:
    path = CONFIG_DIR / "counties.yml"
    with open(path, "r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    return data.get("defaults", {})
