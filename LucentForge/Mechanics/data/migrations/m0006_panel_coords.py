from __future__ import annotations
import json
import os
import sqlite3

_DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")


def migrate(conn: sqlite3.Connection) -> None:
    # entity_state: panel coordinates (where each entity was saved)
    try:
        conn.execute("ALTER TABLE entity_state ADD COLUMN panel_x INTEGER DEFAULT 0")
    except sqlite3.OperationalError:
        pass  # column already exists — idempotent

    try:
        conn.execute("ALTER TABLE entity_state ADD COLUMN panel_y INTEGER DEFAULT 0")
    except sqlite3.OperationalError:
        pass

    # source_state: panel coordinates (sources are panel-local)
    try:
        conn.execute("ALTER TABLE source_state ADD COLUMN panel_x INTEGER DEFAULT 0")
    except sqlite3.OperationalError:
        pass

    try:
        conn.execute("ALTER TABLE source_state ADD COLUMN panel_y INTEGER DEFAULT 0")
    except sqlite3.OperationalError:
        pass

    # chest_content stores data as a JSON blob — re-seed from chests.json so
    # each chest definition gains panel_x/panel_y in its data payload.
    chests_path = os.path.join(_DATA_DIR, "chests.json")
    with open(chests_path, encoding="utf-8") as f:
        chests = json.load(f)
    for chest in chests:
        conn.execute(
            "INSERT OR REPLACE INTO chest_content (id, data) VALUES (?, ?)",
            (chest["id"], json.dumps(chest, ensure_ascii=False)),
        )

    conn.commit()
    print("[DB] m0006: panel_x/panel_y added to entity_state + source_state; chests re-seeded with panel coords")
