# m0002_runtime_state.py — Phase 1.5: runtime world-state save/load tables.
#
# These tables store live simulation state (clock, threat, source stocks,
# per-entity vitals/needs/personality). They are RUNTIME ARTIFACTS — kept in
# the gitignored lucentforge.db — NOT content tables. Do not seed from JSON.
#
# slot_id is built in from the start so Phase 1.6 can add a slot-picker UI
# without schema changes. Phase 1.5 uses slot_id=0 exclusively.


def migrate(conn) -> None:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS world_state (
            slot_id      INTEGER NOT NULL DEFAULT 0,
            tick_count   INTEGER NOT NULL,
            accumulator  REAL    NOT NULL DEFAULT 0.0,
            threat_level REAL    NOT NULL DEFAULT 0.0,
            prev_stage   TEXT    NOT NULL DEFAULT 'PASSIVE',
            town_state   TEXT    NOT NULL DEFAULT 'STABLE',
            saved_at     TEXT    NOT NULL,
            PRIMARY KEY (slot_id)
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS source_state (
            slot_id  INTEGER NOT NULL DEFAULT 0,
            label    TEXT    NOT NULL,
            stock    REAL    NOT NULL,
            PRIMARY KEY (slot_id, label)
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS entity_state (
            slot_id    INTEGER NOT NULL DEFAULT 0,
            entity_id  TEXT    NOT NULL,
            hp         INTEGER NOT NULL,
            x          REAL    NOT NULL,
            y          REAL    NOT NULL,
            cycles     INTEGER NOT NULL DEFAULT 0,
            mp         INTEGER NOT NULL DEFAULT 0,
            equipment  TEXT    NOT NULL DEFAULT '{}',
            needs      TEXT    NOT NULL DEFAULT '{}',
            chemicals  TEXT    NOT NULL DEFAULT '{}',
            traits     TEXT    NOT NULL DEFAULT '{}',
            memory     TEXT    NOT NULL DEFAULT '{}',
            ai_state   TEXT    NOT NULL DEFAULT 'IDLE',
            ai_data    TEXT    NOT NULL DEFAULT '{}',
            PRIMARY KEY (slot_id, entity_id)
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS game_state (
            slot_id          INTEGER NOT NULL DEFAULT 0,
            defeated_npcs    TEXT    NOT NULL DEFAULT '[]',
            combat_cooldowns TEXT    NOT NULL DEFAULT '{}',
            PRIMARY KEY (slot_id)
        )
    """)
    conn.commit()
