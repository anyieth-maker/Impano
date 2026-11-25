"""Database connection layer.

This is the ONLY module that talks to sqlite3 directly. Every repository
receives a ``Database`` object and calls its helper methods, which keeps the
SQL connection details separate from the rest of the application.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any, Iterable, List, Optional

SCHEMA_PATH = Path(__file__).with_name("schema.sql")
DEFAULT_DB_PATH = Path(__file__).resolve().parents[2] / "impano.db"


class Database:
    """Thin wrapper around a SQLite connection."""

    def __init__(self, path: str | Path = DEFAULT_DB_PATH) -> None:
        self.path = str(path)
        self.conn = sqlite3.connect(self.path)
        self.conn.row_factory = sqlite3.Row          # rows behave like dicts
        self.conn.execute("PRAGMA foreign_keys = ON")  # enforce relationships

    # ---------------------------------------------------------------- setup
    def init_schema(self) -> None:
        """Create all tables if they do not exist yet."""
        self.conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
        self.conn.commit()

    # -------------------------------------------------------------- queries
    def execute(self, sql: str, params: Iterable[Any] = ()) -> sqlite3.Cursor:
        """Run an INSERT / UPDATE / DELETE and commit it."""
        cursor = self.conn.execute(sql, tuple(params))
        self.conn.commit()
        return cursor

    def insert(self, sql: str, params: Iterable[Any] = ()) -> int:
        """Run an INSERT and return the new row id."""
        return int(self.execute(sql, params).lastrowid)

    def fetch_one(self, sql: str, params: Iterable[Any] = ()) -> Optional[sqlite3.Row]:
        return self.conn.execute(sql, tuple(params)).fetchone()

    def fetch_all(self, sql: str, params: Iterable[Any] = ()) -> List[sqlite3.Row]:
        return self.conn.execute(sql, tuple(params)).fetchall()

    def scalar(self, sql: str, params: Iterable[Any] = ()) -> Any:
        row = self.fetch_one(sql, params)
        return row[0] if row else None

    def close(self) -> None:
        self.conn.close()
