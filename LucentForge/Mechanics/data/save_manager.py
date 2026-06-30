# save_manager.py — Facade for world-state save/load (Phase 1.5).
#
# Snapshots live runtime state to the 4 m0002 tables atomically and restores
# it on launch. Uses direct SQL (not SqliteDao document-store) because the
# runtime tables have proper relational structure.
#
# Slot architecture: slot_id column exists on all tables. Phase 1.5 uses
# slot_id=0 for autosave/manual/quit-save. Phase 1.6 adds a slot-picker UI.
from __future__ import annotations

import json
from datetime import datetime, timezone

from Mechanics.data.db import Database

_DEFAULT_SLOT = 0


class SaveManager:
    """Owns snapshot() and restore() for world runtime state."""

    def __init__(self, db: Database) -> None:
        self._db = db

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def has_save(self, slot_id: int = _DEFAULT_SLOT) -> bool:
        row = self._db.conn.execute(
            "SELECT 1 FROM world_state WHERE slot_id = ?", (slot_id,)
        ).fetchone()
        return row is not None

    def snapshot(
        self,
        world_sim,
        sources: list,
        controllers: list,
        player,
        player_needs: list,
        defeated_npcs: set,
        combat_cooldowns: dict,
        slot_id: int = _DEFAULT_SLOT,
    ) -> None:
        """Write full world state to the given slot in a single transaction."""
        conn = self._db.conn
        saved_at = datetime.now(timezone.utc).isoformat()

        with conn:
            # --- World sim ---
            conn.execute(
                "INSERT OR REPLACE INTO world_state "
                "(slot_id, tick_count, accumulator, threat_level, prev_stage, town_state, saved_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    slot_id,
                    world_sim.clock.tick_count,
                    world_sim.clock._accumulator,
                    world_sim.threat.threat_level,
                    world_sim.threat._prev_stage.name,
                    world_sim.town.state.name,
                    saved_at,
                ),
            )

            # --- Source stocks (finite only; infinite have no meaningful stock) ---
            conn.execute("DELETE FROM source_state WHERE slot_id = ?", (slot_id,))
            for src in sources:
                if src.is_finite:
                    conn.execute(
                        "INSERT INTO source_state (slot_id, label, stock) VALUES (?, ?, ?)",
                        (slot_id, src.label, src.stock),
                    )

            # --- Entity states ---
            conn.execute("DELETE FROM entity_state WHERE slot_id = ?", (slot_id,))

            # NPCs
            for ctrl in controllers:
                npc = ctrl.npc
                mem_data = {
                    label: {
                        "need_id": sm.need_id,
                        "visit_count": sm.visit_count,
                        "avg_satisfaction": sm.avg_satisfaction,
                        "last_visit_tick": sm.last_visit_tick,
                    }
                    for label, sm in ctrl.memory._sources.items()
                }
                conn.execute(
                    "INSERT INTO entity_state "
                    "(slot_id, entity_id, hp, x, y, cycles, mp, equipment, needs, "
                    "chemicals, traits, memory, ai_state, ai_data) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (
                        slot_id,
                        npc.entity_id,
                        npc.hp,
                        npc.x,
                        npc.y,
                        getattr(npc, "cycles", 0),
                        getattr(npc, "mp", 0),
                        json.dumps(getattr(npc, "equipment", {})),
                        json.dumps({n.need_id: n.current_value for n in ctrl.needs}),
                        json.dumps(ctrl.brain.chemicals.as_dict()),
                        json.dumps(ctrl.brain.traits.as_dict()),
                        json.dumps(mem_data),
                        ctrl.state,
                        json.dumps({}),
                    ),
                )

            # Player (ai_state="PLAYER" acts as sentinel for restore)
            p_traits = (player.traits.as_dict()
                        if hasattr(player.traits, "as_dict") else {})
            conn.execute(
                "INSERT INTO entity_state "
                "(slot_id, entity_id, hp, x, y, cycles, mp, equipment, needs, "
                "chemicals, traits, memory, ai_state, ai_data) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    slot_id,
                    player.entity_id,
                    player.hp,
                    player.x,
                    player.y,
                    getattr(player, "cycles", 0),
                    getattr(player, "mp", 0),
                    json.dumps(getattr(player, "equipment", {})),
                    json.dumps({n.need_id: n.current_value for n in player_needs}),
                    json.dumps({}),
                    json.dumps(p_traits),
                    json.dumps({}),
                    "PLAYER",
                    json.dumps({}),
                ),
            )

            # --- Game tracking ---
            conn.execute(
                "INSERT OR REPLACE INTO game_state (slot_id, defeated_npcs, combat_cooldowns) "
                "VALUES (?, ?, ?)",
                (
                    slot_id,
                    json.dumps(sorted(defeated_npcs)),
                    json.dumps(combat_cooldowns),
                ),
            )

        print(
            f"[SAVE] Snapshot slot={slot_id} tick={world_sim.clock.tick_count} "
            f"entities={len(controllers) + 1} at={saved_at}"
        )

    def restore(self, slot_id: int = _DEFAULT_SLOT) -> dict | None:
        """Return saved world data dict, or None if no save exists for this slot."""
        if not self.has_save(slot_id):
            return None

        conn = self._db.conn

        world_row = conn.execute(
            "SELECT * FROM world_state WHERE slot_id = ?", (slot_id,)
        ).fetchone()

        source_rows = conn.execute(
            "SELECT label, stock FROM source_state WHERE slot_id = ?", (slot_id,)
        ).fetchall()

        entity_rows = conn.execute(
            "SELECT * FROM entity_state WHERE slot_id = ?", (slot_id,)
        ).fetchall()

        game_row = conn.execute(
            "SELECT * FROM game_state WHERE slot_id = ?", (slot_id,)
        ).fetchone()

        return {
            "world": {
                "tick_count":   world_row["tick_count"],
                "accumulator":  world_row["accumulator"],
                "threat_level": world_row["threat_level"],
                "prev_stage":   world_row["prev_stage"],
                "town_state":   world_row["town_state"],
            },
            "sources": {row["label"]: row["stock"] for row in source_rows},
            "entities": {
                row["entity_id"]: {
                    "hp":        row["hp"],
                    "x":         row["x"],
                    "y":         row["y"],
                    "cycles":    row["cycles"],
                    "mp":        row["mp"],
                    "equipment": json.loads(row["equipment"]),
                    "needs":     json.loads(row["needs"]),
                    "chemicals": json.loads(row["chemicals"]),
                    "traits":    json.loads(row["traits"]),
                    "memory":    json.loads(row["memory"]),
                    "ai_state":  row["ai_state"],
                }
                for row in entity_rows
            },
            "game": {
                "defeated_npcs":    json.loads(game_row["defeated_npcs"]) if game_row else [],
                "combat_cooldowns": json.loads(game_row["combat_cooldowns"]) if game_row else {},
            },
        }

    def delete_save(self, slot_id: int = _DEFAULT_SLOT) -> None:
        conn = self._db.conn
        with conn:
            conn.execute("DELETE FROM world_state WHERE slot_id = ?",  (slot_id,))
            conn.execute("DELETE FROM source_state WHERE slot_id = ?", (slot_id,))
            conn.execute("DELETE FROM entity_state WHERE slot_id = ?", (slot_id,))
            conn.execute("DELETE FROM game_state WHERE slot_id = ?",   (slot_id,))
        print(f"[SAVE] Slot {slot_id} deleted.")
