from __future__ import annotations
import json
import sqlite3


def migrate(conn: sqlite3.Connection) -> None:
    try:
        conn.execute(
            "ALTER TABLE entity_state ADD COLUMN bag TEXT NOT NULL DEFAULT '[]'"
        )
    except sqlite3.OperationalError:
        pass  # column already exists — idempotent

    lockpick = {
        "id": "lockpick", "name": "Lockpick", "type": "consumable",
        "slot": "", "description": "A slender tool for opening locks.",
        "value": 8, "weight": 1, "effect": "UNLOCK", "potency": 1, "effects": {},
    }
    conn.execute(
        "INSERT OR REPLACE INTO items (id, data) VALUES (?, ?)",
        ("lockpick", json.dumps(lockpick, ensure_ascii=False)),
    )
    conn.commit()
    print("[DB] m0004: bag column added to entity_state; lockpick seeded")
