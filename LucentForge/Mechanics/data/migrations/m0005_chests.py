from __future__ import annotations
import json
import os
import sqlite3

_DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")


def migrate(conn: sqlite3.Connection) -> None:
    # 1. Seed new items (iron_helm, travel_boots, brass_key) from items.json
    items_path = os.path.join(_DATA_DIR, "items.json")
    new_ids = {"iron_helm", "travel_boots", "brass_key"}
    with open(items_path, encoding="utf-8") as f:
        all_items = json.load(f)
    for item in all_items:
        if item["id"] in new_ids:
            conn.execute(
                "INSERT OR IGNORE INTO items (id, data) VALUES (?, ?)",
                (item["id"], json.dumps(item, ensure_ascii=False)),
            )

    # 2. Chest content table — doc-style (id TEXT PK, data TEXT)
    conn.execute(
        """CREATE TABLE IF NOT EXISTS chest_content (
               id   TEXT PRIMARY KEY,
               data TEXT NOT NULL
           )"""
    )

    # 3. Chest runtime-state table — per save-slot
    conn.execute(
        """CREATE TABLE IF NOT EXISTS chest_state (
               slot_id    INTEGER NOT NULL,
               chest_id   TEXT    NOT NULL,
               is_opened  INTEGER NOT NULL DEFAULT 0,
               contents   TEXT    NOT NULL DEFAULT '[]',
               PRIMARY KEY (slot_id, chest_id)
           )"""
    )

    # 4. Seed chest_content from chests.json
    chests_path = os.path.join(_DATA_DIR, "chests.json")
    with open(chests_path, encoding="utf-8") as f:
        chests = json.load(f)
    for chest in chests:
        conn.execute(
            "INSERT OR IGNORE INTO chest_content (id, data) VALUES (?, ?)",
            (chest["id"], json.dumps(chest, ensure_ascii=False)),
        )

    conn.commit()
    print("[DB] m0005: chest_content + chest_state created; 3 chests + 3 items seeded")
