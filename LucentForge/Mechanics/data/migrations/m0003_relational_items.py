# m0003_relational_items.py — re-seed the items table with canonical field values.
# items.json now carries flat typed fields (attack_power, weapon_type, body_slot, etc.)
# alongside the backward-compat effects dict (removed Phase 2.4).
# Idempotent: INSERT OR REPLACE overwrites any row seeded by m0001.
from __future__ import annotations
import json
import sqlite3

from Mechanics.data.loader import load_json


def migrate(conn: sqlite3.Connection) -> None:
    items = load_json("items.json")
    for item in items:
        conn.execute(
            "INSERT OR REPLACE INTO items (id, data) VALUES (?, ?)",
            (item["id"], json.dumps(item, ensure_ascii=False)),
        )
    conn.commit()
    print(f"[DB] m0003: re-seeded items: {len(items)} rows with canonical fields")
