# m0001_initial_content.py — create the document tables and seed them from the
# canonical JSON files. Idempotent: CREATE TABLE IF NOT EXISTS + INSERT OR REPLACE.
from __future__ import annotations
import json
import sqlite3

from Mechanics.data.loader import load_json

# table name -> seed JSON filename (in Mechanics/data/)
COLLECTIONS = {
    "entities":  "entities.json",
    "abilities": "abilities.json",
    "items":     "items.json",
    "needs":     "needs.json",
    "sources":   "sources.json",
}


def migrate(conn: sqlite3.Connection) -> None:
    for table, filename in COLLECTIONS.items():
        # Table name is internal/fixed (not user input) — safe to interpolate.
        conn.execute(
            f"CREATE TABLE IF NOT EXISTS {table} "
            "(id TEXT PRIMARY KEY, data TEXT NOT NULL)"
        )
        rows = load_json(filename)
        for i, rec in enumerate(rows):
            pk = str(rec.get("id", f"{table}_{i}"))
            conn.execute(
                f"INSERT OR REPLACE INTO {table} (id, data) VALUES (?, ?)",
                (pk, json.dumps(rec, ensure_ascii=False)),
            )
        print(f"[DB] seeded {table}: {len(rows)} rows")
