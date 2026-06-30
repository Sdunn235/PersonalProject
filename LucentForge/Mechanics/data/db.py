# db.py — SQLite connection + hand-written migrations runner (Phase 1 backbone).
#
# Document-style storage: each content collection is one table of
# (id TEXT PRIMARY KEY, data TEXT) where `data` is the JSON for one record.
# The JSON files in this directory remain the CANONICAL seed; lucentforge.db is
# a gitignored runtime artifact rebuilt by migration 0001. To reseed after
# editing a JSON file, delete lucentforge.db and re-run.
from __future__ import annotations
import os
import sqlite3

_DATA_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_DB_PATH = os.path.join(_DATA_DIR, "lucentforge.db")


class Database:
    """Owns the SQLite connection and applies versioned migrations once, in order.

    Mirrors TheForge's hand-edited-migration discipline: each migration is an
    explicit, ordered step recorded in `schema_migrations`.
    """

    def __init__(self, db_path: str | None = None):
        self.path = db_path or DEFAULT_DB_PATH
        self.conn = sqlite3.connect(self.path)
        self.conn.row_factory = sqlite3.Row
        self.apply_migrations()

    def apply_migrations(self) -> None:
        from Mechanics.data.migrations import MIGRATIONS

        self.conn.execute(
            "CREATE TABLE IF NOT EXISTS schema_migrations "
            "(version INTEGER PRIMARY KEY, applied_at TEXT NOT NULL)"
        )
        applied = {row["version"] for row in
                   self.conn.execute("SELECT version FROM schema_migrations")}
        for version, name, migrate in MIGRATIONS:
            if version in applied:
                continue
            migrate(self.conn)
            self.conn.execute(
                "INSERT INTO schema_migrations (version, applied_at) "
                "VALUES (?, datetime('now'))",
                (version,),
            )
            self.conn.commit()
            print(f"[DB] migration {version:04d} applied: {name}")

    def close(self) -> None:
        self.conn.close()
