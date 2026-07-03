"""smoke_test.py — Headless Phase 1.5 round-trip verification.

Runs the simulation for N ticks, snapshots, re-initializes from restore(),
and asserts that key values match. Also verifies fresh-seed still works.

Usage:
    $env:SDL_VIDEODRIVER='dummy'; python scratchpad/smoke_test.py
"""
import os
import sys
import json

# Ensure project root is on path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
pygame.init()
pygame.display.set_mode((1, 1))

# ─── Imports ─────────────────────────────────────────────────────────────────
from Mechanics.bootstrap import (
    create_game_context, create_needs, create_npc_controller,
    create_world_sim, apply_save,
)
from Mechanics.entities.factory import create_player, create_all_npcs
from Mechanics.world.tile_map import TileMap
from Mechanics.ai.player import PlayerController

_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        "Mechanics", "data", "lucentforge.db")

# ─── Helpers ─────────────────────────────────────────────────────────────────

def _build_game(db_path=None):
    ctx = create_game_context(db_path=db_path)
    tile_map = TileMap()
    tile_map.load_real_map()
    sources = tile_map.get_need_sources()
    world_sim = create_world_sim(sources)

    npc_list = []
    for npc in create_all_npcs(ctx):
        ctrl = create_npc_controller(npc, ctx, sources, tile_map, world_sim=world_sim)
        npc_list.append((npc, ctrl))

    player = create_player(ctx)
    player_needs = create_needs(ctx)
    PlayerController(player, tile_map=tile_map, needs=player_needs, sources=sources)

    defeated_npcs: set[str] = set()
    combat_cooldowns: dict[str, float] = {}
    return ctx, world_sim, sources, npc_list, player, player_needs, defeated_npcs, combat_cooldowns


def _tick_n(world_sim, npc_list, defeated_npcs, n=500):
    """Run N sim ticks worth of world updates (no rendering)."""
    import settings
    dt_per_tick = 1.0 / settings.SIM_TICK_RATE if settings.SIM_TICK_RATE > 0 else 1.0 / 60.0
    for _ in range(n):
        goblin_hungers = []
        for npc_e, npc_c in npc_list:
            if npc_e.entity_id not in defeated_npcs and npc_e.subtype == "goblin":
                h = next((x for x in npc_c.needs if x.need_id == "hunger"), None)
                if h:
                    goblin_hungers.append(h.current_value / 100.0)
        avg = sum(goblin_hungers) / len(goblin_hungers) if goblin_hungers else 1.0
        world_sim.tick(dt_per_tick, len(npc_list) - len(defeated_npcs), avg)


# ─── Test 1: Fresh-seed — no save present ────────────────────────────────────

def test_fresh_seed():
    import tempfile
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        tmp_db = f.name
    try:
        ctx, world_sim, sources, npc_list, player, player_needs, d_npcs, cooldowns = \
            _build_game(db_path=tmp_db)

        assert not ctx.save_manager.has_save(), "Expected no save on fresh DB"
        assert world_sim.clock.tick_count == 0, "Expected tick_count=0 on fresh start"
        print("[TEST 1 PASS] Fresh seed — no save, tick_count=0")
    finally:
        ctx.db.close()
        os.unlink(tmp_db)


# ─── Test 2: Snapshot → restore round-trip ────────────────────────────────────

def test_round_trip():
    import tempfile
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        tmp_db = f.name
    ctx = ctx2 = None
    try:
        ctx, world_sim, sources, npc_list, player, player_needs, d_npcs, cooldowns = \
            _build_game(db_path=tmp_db)

        # Run 500 sim ticks to evolve state
        controllers = [ctrl for _, ctrl in npc_list]
        _tick_n(world_sim, npc_list, d_npcs, n=500)

        # Record key values before snapshot
        pre_tick    = world_sim.clock.tick_count
        pre_threat  = world_sim.threat.threat_level
        pre_town    = world_sim.town.state.name
        pre_npc0_x  = npc_list[0][0].x
        pre_npc0_hp = npc_list[0][0].hp
        # Record first NPC's first need value
        pre_npc0_need = npc_list[0][1].needs[0].current_value
        # Record finite source stock
        finite_src = next((s for s in sources if s.is_finite), None)
        pre_stock = finite_src.stock if finite_src else None

        # Snapshot
        ctx.save_manager.snapshot(
            world_sim, sources, controllers,
            player, player_needs, d_npcs, cooldowns,
        )
        assert ctx.save_manager.has_save(), "Expected save to exist after snapshot"

        # Restore into a fresh game built on the same DB
        ctx2, ws2, src2, npc2, player2, pn2, d2, c2 = _build_game(db_path=tmp_db)
        controllers2 = [ctrl for _, ctrl in npc2]
        save_data = ctx2.save_manager.restore()
        assert save_data is not None, "restore() returned None unexpectedly"

        apply_save(save_data, ws2, src2, controllers2, player2, pn2, d2, c2)

        # Assert round-trip fidelity
        assert ws2.clock.tick_count == pre_tick, \
            f"tick_count mismatch: {ws2.clock.tick_count} != {pre_tick}"
        assert abs(ws2.threat.threat_level - pre_threat) < 0.001, \
            f"threat_level mismatch: {ws2.threat.threat_level} != {pre_threat}"
        assert ws2.town.state.name == pre_town, \
            f"town_state mismatch: {ws2.town.state.name} != {pre_town}"

        npc0_restored = npc2[0][0]
        assert abs(npc0_restored.x - pre_npc0_x) < 0.001, \
            f"npc[0].x mismatch: {npc0_restored.x} != {pre_npc0_x}"
        assert npc0_restored.hp == pre_npc0_hp, \
            f"npc[0].hp mismatch: {npc0_restored.hp} != {pre_npc0_hp}"

        restored_need_val = controllers2[0].needs[0].current_value
        assert abs(restored_need_val - pre_npc0_need) < 0.001, \
            f"need[0] value mismatch: {restored_need_val} != {pre_npc0_need}"

        if finite_src and pre_stock is not None:
            restored_stock = next(
                (s.stock for s in src2 if s.label == finite_src.label), None
            )
            assert restored_stock is not None and abs(restored_stock - pre_stock) < 0.001, \
                f"source stock mismatch: {restored_stock} != {pre_stock}"

        print(f"[TEST 2 PASS] Round-trip tick={pre_tick} threat={pre_threat:.2f} "
              f"npc0_x={pre_npc0_x:.1f} need0={pre_npc0_need:.2f} "
              + (f"stock={pre_stock:.1f}" if pre_stock is not None else ""))

    finally:
        if ctx:  ctx.db.close()
        if ctx2: ctx2.db.close()
        os.unlink(tmp_db)


# ─── Test 3: Autosave fires at correct interval ───────────────────────────────

def test_autosave_interval():
    import tempfile, settings
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        tmp_db = f.name
    ctx = None
    try:
        ctx, world_sim, sources, npc_list, player, player_needs, d_npcs, cooldowns = \
            _build_game(db_path=tmp_db)
        controllers = [ctrl for _, ctrl in npc_list]

        # Manually drive to AUTOSAVE_INTERVAL ticks
        target = settings.AUTOSAVE_INTERVAL
        _tick_n(world_sim, npc_list, d_npcs, n=target)

        # Simulate the autosave check from main.py
        if (settings.AUTOSAVE_INTERVAL > 0
                and world_sim.clock.tick_count % settings.AUTOSAVE_INTERVAL == 0):
            ctx.save_manager.snapshot(
                world_sim, sources, controllers,
                player, player_needs, d_npcs, cooldowns,
            )

        assert ctx.save_manager.has_save(), \
            f"Expected autosave at tick {target}"
        print(f"[TEST 3 PASS] Autosave at tick {target} — AUTOSAVE_INTERVAL={target}")
    finally:
        if ctx: ctx.db.close()
        os.unlink(tmp_db)


# ─── Test 4: Slot isolation — get_slot_info / list_all_slots ─────────────────

def test_slot_isolation():
    import tempfile
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        tmp_db = f.name
    ctx = None
    try:
        ctx, world_sim, sources, npc_list, player, player_needs, d_npcs, cooldowns = \
            _build_game(db_path=tmp_db)
        controllers = [ctrl for _, ctrl in npc_list]

        # Write different tick counts to slots 0, 1, 2
        for slot, ticks in [(0, 100), (1, 200), (2, 300)]:
            _tick_n(world_sim, npc_list, d_npcs, n=ticks - world_sim.clock.tick_count)
            ctx.save_manager.snapshot(
                world_sim, sources, controllers,
                player, player_needs, d_npcs, cooldowns, slot_id=slot,
            )

        # Verify get_slot_info per slot
        info0 = ctx.save_manager.get_slot_info(0)
        info1 = ctx.save_manager.get_slot_info(1)
        info2 = ctx.save_manager.get_slot_info(2)
        info3 = ctx.save_manager.get_slot_info(3)   # never written

        assert info0 is not None and info0["tick_count"] == 100, f"slot 0: {info0}"
        assert info1 is not None and info1["tick_count"] == 200, f"slot 1: {info1}"
        assert info2 is not None and info2["tick_count"] == 300, f"slot 2: {info2}"
        assert info3 is None, f"slot 3 should be empty, got: {info3}"
        assert "town_state" in info0 and "saved_at" in info0

        # Verify list_all_slots
        all_infos = ctx.save_manager.list_all_slots([0, 1, 2, 3])
        assert len(all_infos) == 4
        assert all_infos[0]["tick_count"] == 100
        assert all_infos[1]["tick_count"] == 200
        assert all_infos[2]["tick_count"] == 300
        assert all_infos[3] is None

        print("[TEST 4 PASS] Slot isolation — slots 0/1/2 independent, slot 3 empty, list_all_slots correct")
    finally:
        if ctx: ctx.db.close()
        os.unlink(tmp_db)


# ─── Run ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("Phase 1.5 / 1.6 — Save/Load Smoke Tests")
    print("=" * 60)
    test_fresh_seed()
    test_round_trip()
    test_autosave_interval()
    test_slot_isolation()
    print("=" * 60)
    print("All tests passed.")
    print("=" * 60)
    pygame.quit()
