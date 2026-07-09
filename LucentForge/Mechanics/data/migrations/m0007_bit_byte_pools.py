# m0007_bit_byte_pools.py — Stage 4.3: split the magic pool into Bits and Bytes.
#
# entity_state gains `bit_pool` and `byte_pool` current-value columns. The legacy
# `mp` column is left in place and backfilled into `byte_pool` (parity: the Byte
# pool is mp's successor, §M3). Pool maxima are NOT persisted — they recompute from
# attributes at spawn (like max_mp always did).
from __future__ import annotations
import sqlite3


def migrate(conn: sqlite3.Connection) -> None:
    for col in ("bit_pool", "byte_pool"):
        try:
            conn.execute(f"ALTER TABLE entity_state ADD COLUMN {col} INTEGER DEFAULT 0")
        except sqlite3.OperationalError:
            pass  # column already exists — idempotent

    # Backfill: legacy mp becomes the Byte pool for existing saves (parity).
    try:
        conn.execute("UPDATE entity_state SET byte_pool = mp WHERE byte_pool = 0")
    except sqlite3.OperationalError:
        pass

    conn.commit()
    print("[DB] m0007: bit_pool/byte_pool added to entity_state; byte_pool backfilled from mp")
