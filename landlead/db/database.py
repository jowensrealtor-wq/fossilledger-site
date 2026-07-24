"""SQLite connection helpers + schema initialization.

Kept deliberately thin (stdlib sqlite3, row factory -> dict). The whole app
talks to the DB through `get_conn()` / the small helpers here, so swapping in
Postgres later means changing only this module.
"""
from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

from config.settings import get_settings

SCHEMA_PATH = Path(__file__).resolve().parent / "schema.sql"


def _db_path() -> str:
    settings = get_settings()
    path = settings.sqlite_path
    if not path:
        raise RuntimeError(
            "Only SQLite is wired up in this reference build. Set DATABASE_URL "
            "to a sqlite:/// path, or extend db/database.py for Postgres."
        )
    return path


def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(_db_path(), timeout=30, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    return conn


@contextmanager
def db() -> Iterator[sqlite3.Connection]:
    conn = get_conn()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db() -> None:
    """Create tables if they do not exist. Idempotent."""
    with open(SCHEMA_PATH, "r", encoding="utf-8") as fh:
        ddl = fh.read()
    with db() as conn:
        conn.executescript(ddl)


def row_to_dict(row: sqlite3.Row | None) -> dict[str, Any] | None:
    if row is None:
        return None
    return {k: row[k] for k in row.keys()}


def rows_to_dicts(rows) -> list[dict[str, Any]]:
    return [row_to_dict(r) for r in rows]


# --- small JSON-column helpers ------------------------------------------------
def dumps(value: Any) -> str:
    return json.dumps(value, default=str)


def loads(value: str | None, default: Any = None) -> Any:
    if not value:
        return default
    try:
        return json.loads(value)
    except (json.JSONDecodeError, TypeError):
        return default
