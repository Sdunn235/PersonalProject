"""run_runtime_tests.py — Stage 4.6R / R0 characterization safety net.

Pins the CURRENT behavior of the runtime-lifecycle logic that is about to be
refactored (Stage 4.6R: extract SimulationKernel + WorldSession + PresentationShell
from main.py). Today that logic lives as inline closures inside main()'s event loop
and has ~zero automated coverage:

  (a) New Game reset          main.py L200-214
  (b) repeated save/load      (drift across a double round-trip)
  (c) zone-subscriber wiring  main.py L125-133  (the C0026 re-subscribe fix)
  (d) defeated -> sprite kill  main.py L301/332/399-402
  (e) item + chest round-trip main.py L242-249 / bootstrap create_*/rebuild_*

These tests pin behavior at the PRIMITIVE level the refactor will extract to, so the
same assertions survive the move (R1 WorldSession.new_game(), R2 kernel.step, R3
subscriber lifecycle, R4 shell death-reaction). Green here is the golden master:
run it before and after every stage to prove behavior was preserved.

Headless. Usage (Windows PowerShell):
    $env:SDL_VIDEODRIVER='dummy'; py scratchpad/run_runtime_tests.py
"""
import os
import sys
import tempfile
import py_compile

# Project root on path (mirrors smoke_test.py).
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

# noinspection PyPackageRequirements
import pygame
pygame.init()
pygame.display.set_mode((1, 1))

import settings
from Mechanics.bootstrap import (
    create_game_context, create_needs, create_npc_controller, create_world_sim,
    apply_save, create_item_services, rebuild_item_services,
    create_chest_registry, rebuild_chest_registry,
)
from Mechanics.entities.factory import create_player, create_all_npcs
from Mechanics.world.tile_map import TileMap
from Mechanics.ai.player import PlayerController
from Mechanics.ai.npc_logger import log_spatial_zone
from Mechanics.runtime.session import WorldSession  # R1 seam under test
from Mechanics.runtime.kernel import SimulationKernel, SimFrame, COMBAT_COOLDOWN  # R2 seam

# Reuse smoke_test's tick harness verbatim (DRY — same pygame-free driver).
from smoke_test import _tick_n

# ─── check harness (matches the smoke_phase*/parity suite conventions) ────────
_passed = 0
_failed = 0


def check(cond, label, detail=""):
    global _passed, _failed
    if cond:
        _passed += 1
        print(f"  PASS  {label}")
    else:
        _failed += 1
        print(f"  FAIL  {label}" + (f" -- {detail}" if detail else ""))


def _build_full(db_path=None):
    """Build a full headless game and ALSO return tile_map (which
    smoke_test._build_game hides). Mirrors that helper otherwise.

    Returns: ctx, world_sim, sources, tile_map, npc_list[(npc, ctrl)],
             player, player_needs, defeated_npcs, combat_cooldowns
    """
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
    return (ctx, world_sim, sources, tile_map, npc_list, player, player_needs,
            set(), {})


# ─── (a) New Game reset ───────────────────────────────────────────────────────

def test_new_game_reset():
    print("[A] New Game reset — fresh world_sim identity, cleared state, all NPCs alive")
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        tmp_db = f.name
    ctx = None
    try:
        (ctx, world_sim, sources, tile_map, npc_list, player, player_needs,
         defeated, cooldowns) = _build_full(db_path=tmp_db)

        # Evolve + dirty the session so the reset is meaningful.
        _tick_n(world_sim, npc_list, defeated, n=200)
        first_id = npc_list[0][0].entity_id
        defeated.add(first_id)
        cooldowns[first_id] = 1.0
        old_world_id = id(world_sim)
        check(world_sim.clock.tick_count > 0, "pre-reset world advanced (tick_count > 0)",
              f"tick={world_sim.clock.tick_count}")

        # --- New Game primitive sequence (mirror main.py L200-214) ---
        new_world = create_world_sim(sources)
        new_npcs = [
            (npc, create_npc_controller(npc, ctx, sources, tile_map, world_sim=new_world))
            for npc in create_all_npcs(ctx)
        ]
        new_defeated: set[str] = set()
        new_cooldowns: dict[str, float] = {}

        check(id(new_world) != old_world_id, "world_sim is a distinct object after New Game")
        check(new_world.clock.tick_count == 0, "fresh world_sim tick_count == 0",
              f"got {new_world.clock.tick_count}")
        check(new_defeated == set(), "defeated_npcs cleared to empty set")
        check(new_cooldowns == {}, "combat_cooldowns cleared to empty dict")
        expected_count = len(create_all_npcs(ctx))
        check(len(new_npcs) == expected_count,
              f"all NPCs respawned (count == {expected_count})", f"got {len(new_npcs)}")
        check(all(npc.entity_id not in new_defeated for npc, _ in new_npcs),
              "no NPC is in the fresh defeated set (all alive)")
    finally:
        if ctx:
            ctx.db.close()
        os.unlink(tmp_db)


# ─── (b) Repeated save -> load -> save -> load, no drift ───────────────────────

def _snapshot_vals(world_sim, sources, npc_list):
    src = next((s for s in sources if s.is_finite), None)
    return (
        world_sim.clock.tick_count,
        round(world_sim.threat.threat_level, 4),
        world_sim.town.state.name,
        round(npc_list[0][0].x, 3),
        npc_list[0][0].hp,
        round(npc_list[0][1].needs[0].current_value, 3),
        round(src.stock, 3) if src else None,
    )


def test_double_round_trip():
    print("[B] Double save/load round-trip — no state drift across two cycles")
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        tmp_db = f.name
    ctxs = []
    try:
        (ctx, world_sim, sources, tile_map, npc_list, player, player_needs,
         defeated, cooldowns) = _build_full(db_path=tmp_db)
        ctxs.append(ctx)
        controllers = [c for _, c in npc_list]
        _tick_n(world_sim, npc_list, defeated, n=400)
        original = _snapshot_vals(world_sim, sources, npc_list)

        ctx.save_manager.snapshot(world_sim, sources, controllers,
                                  player, player_needs, defeated, cooldowns)

        # Cycle 1: restore into a fresh build.
        (ctx2, ws2, src2, tm2, npc2, p2, pn2, d2, c2) = _build_full(db_path=tmp_db)
        ctxs.append(ctx2)
        ctrls2 = [c for _, c in npc2]
        apply_save(ctx2.save_manager.restore(), ws2, src2, ctrls2, p2, pn2, d2, c2)
        cycle1 = _snapshot_vals(ws2, src2, npc2)

        # Save again from the restored state, then restore a second time.
        ctx2.save_manager.snapshot(ws2, src2, ctrls2, p2, pn2, d2, c2)
        (ctx3, ws3, src3, tm3, npc3, p3, pn3, d3, c3) = _build_full(db_path=tmp_db)
        ctxs.append(ctx3)
        ctrls3 = [c for _, c in npc3]
        apply_save(ctx3.save_manager.restore(), ws3, src3, ctrls3, p3, pn3, d3, c3)
        cycle2 = _snapshot_vals(ws3, src3, npc3)

        check(cycle1 == original, "round-trip 1 matches original", f"{cycle1} != {original}")
        check(cycle2 == original, "round-trip 2 matches original (no drift)",
              f"{cycle2} != {original}")
    finally:
        for c in ctxs:
            c.db.close()
        os.unlink(tmp_db)


# ─── (c) Zone-subscriber survival across a fresh world_sim ─────────────────────

def test_zone_subscriber_wiring():
    print("[C] Zone subscribers — fresh tracker empty, re-subscribe, all fire on cross")
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        tmp_db = f.name
    ctx = None
    try:
        (ctx, world_sim, sources, tile_map, npc_list, player, player_needs,
         defeated, cooldowns) = _build_full(db_path=tmp_db)

        # A New-Game fresh world_sim must start with NO callbacks (the gap the
        # main.py _register_zone_subscribers() re-close fixes on New Game / C0026).
        fresh = create_world_sim(sources)
        check(len(fresh.zone_tracker._callbacks) == 0,
              "fresh world_sim.zone_tracker has 0 callbacks",
              f"got {len(fresh.zone_tracker._callbacks)}")

        # Re-subscribe 3 observers (log_spatial_zone + 2 counting sentinels).
        hits = {"a": 0, "b": 0}

        def _sentinel_a(_evt):
            hits["a"] += 1

        def _sentinel_b(_evt):
            hits["b"] += 1

        fresh.zone_tracker.subscribe(log_spatial_zone)
        fresh.zone_tracker.subscribe(_sentinel_a)
        fresh.zone_tracker.subscribe(_sentinel_b)
        check(len(fresh.zone_tracker._callbacks) == 3,
              "3 callbacks registered after re-subscribe",
              f"got {len(fresh.zone_tracker._callbacks)}")

        # Find two grid cells that resolve to DIFFERENT rooms.
        px, py = ctx.current_panel[0], ctx.current_panel[1]
        cell_by_room = {}
        for col in range(settings.COLS):
            for row in range(settings.ROWS):
                region = tile_map.get_region(col, row)
                room = ctx.rooms.get_room_for_region(px, py, region)
                if room is not None and id(room) not in cell_by_room:
                    cell_by_room[id(room)] = (col, row)
        check(len(cell_by_room) >= 2, "map has >= 2 distinct rooms to cross between",
              f"got {len(cell_by_room)}")
        (cell_a, cell_b) = list(cell_by_room.values())[:2]

        # First call initializes the entity's room cache silently (no event);
        # moving to a different room and re-checking fires all 3 callbacks once.
        player.x, player.y = tile_map.grid_to_world_center(*cell_a)
        fresh.zone_tracker.check_and_fire([player], tile_map, ctx.rooms, px, py, 1)
        player.x, player.y = tile_map.grid_to_world_center(*cell_b)
        events = fresh.zone_tracker.check_and_fire([player], tile_map, ctx.rooms, px, py, 2)

        check(len(events) == 1, "exactly one zone-crossing event fired", f"got {len(events)}")
        check(hits["a"] == 1 and hits["b"] == 1,
              "both sentinel subscribers fired exactly once", f"hits={hits}")
    finally:
        if ctx:
            ctx.db.close()
        os.unlink(tmp_db)


# ─── (d) Defeated set drives sprite kill (data level, headless) ───────────────

def test_defeated_drives_kill():
    print("[D] Defeated set -> sprite-kill selection + living-entity filter (data level)")
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        tmp_db = f.name
    ctx = None
    try:
        (ctx, world_sim, sources, tile_map, npc_list, player, player_needs,
         defeated, cooldowns) = _build_full(db_path=tmp_db)

        ids = [npc.entity_id for npc, _ in npc_list]
        victim = ids[0]
        defeated.add(victim)

        # main.py idiom L399-402: kill sprite when entity_id in defeated_npcs.
        should_kill = {eid for eid in ids if eid in defeated}
        check(should_kill == {victim}, "exactly the defeated entity is selected for kill",
              f"{should_kill}")

        # main.py idiom L301/332: living-entity filter excludes defeated.
        living = [npc for npc, _ in npc_list if npc.entity_id not in defeated]
        check(len(living) == len(npc_list) - 1, "living filter drops exactly one entity",
              f"{len(living)} of {len(npc_list)}")
        check(all(npc.entity_id != victim for npc in living),
              "defeated entity absent from living set")
    finally:
        if ctx:
            ctx.db.close()
        os.unlink(tmp_db)


# ─── (e) Bags + equipment + chest is_opened round-trip ────────────────────────

def test_item_chest_round_trip():
    print("[E] Bags + equipment + chest is_opened survive save/load")
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        tmp_db = f.name
    ctxs = []
    try:
        (ctx, world_sim, sources, tile_map, npc_list, player, player_needs,
         defeated, cooldowns) = _build_full(db_path=tmp_db)
        ctxs.append(ctx)
        controllers = [c for _, c in npc_list]
        inv_svc, equip_svc = create_item_services(ctx)
        chest_reg = create_chest_registry(ctx)

        # Flip one chest to opened so we have a mutation to round-trip.
        opened_id = next(iter(chest_reg))
        chest_reg[opened_id].is_opened = True

        bags_before = inv_svc.serialize_all()
        equip_before = equip_svc.serialize_all()
        check(any(v for v in bags_before.values()), "at least one non-empty bag (test is meaningful)")
        check(any(v for v in equip_before.values()), "at least one equipped entity (test is meaningful)")

        ctx.save_manager.snapshot(
            world_sim, sources, controllers, player, player_needs, defeated, cooldowns,
            bags=bags_before, equipment=equip_before, chests=chest_reg,
        )

        # Restore into a fresh build and rebuild item + chest state.
        (ctx2, ws2, src2, tm2, npc2, p2, pn2, d2, c2) = _build_full(db_path=tmp_db)
        ctxs.append(ctx2)
        ctrls2 = [c for _, c in npc2]
        save_data = ctx2.save_manager.restore()
        apply_save(save_data, ws2, src2, ctrls2, p2, pn2, d2, c2)
        inv2, equip2 = create_item_services(ctx2)
        rebuild_item_services(save_data, inv2, equip2, ctx2.item_repo)
        chest_reg2 = rebuild_chest_registry(save_data, ctx2.chests, ctx2.item_repo)

        check(inv2.serialize_all() == bags_before, "bags round-trip identical")
        check(equip2.serialize_all() == equip_before, "equipment round-trip identical")
        check(chest_reg2[opened_id].is_opened is True,
              "opened chest stays opened after reload")
        others = [cid for cid in chest_reg2 if cid != opened_id]
        check(all(not chest_reg2[cid].is_opened for cid in others),
              "un-opened chests stay closed after reload")
    finally:
        for c in ctxs:
            c.db.close()
        os.unlink(tmp_db)


# ─── (f) WorldSession seam (R1) — new_game + snapshot/apply_save adapters ──────

def test_world_session():
    print("[F] WorldSession (R1) — new_game() + snapshot_session/apply_save adapters")
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        tmp_db = f.name
    ctxs = []
    try:
        ctx = create_game_context(db_path=tmp_db)
        ctxs.append(ctx)
        tile_map = TileMap()
        tile_map.load_real_map()
        sources = tile_map.get_need_sources()

        session = WorldSession.new_game(ctx, tile_map, sources)
        expected_npcs = len(create_all_npcs(ctx))
        check(session.world_sim.clock.tick_count == 0, "new_game world_sim tick_count == 0")
        check(session.defeated_npcs == set() and session.combat_cooldowns == {},
              "new_game defeated/cooldowns empty")
        check(len(session.npc_list) == expected_npcs,
              f"new_game npc_list count == {expected_npcs}", f"got {len(session.npc_list)}")
        check(len(session.npc_controllers) == expected_npcs,
              "npc_controllers property matches npc_list length")
        check(all(len(pair) == 2 for pair in session.npc_list),
              "npc_list holds (entity, controller) 2-tuples (pygame-free)")
        check(bool(session.chest_reg) and session.inv_svc is not None
              and session.equip_svc is not None, "item + chest services present")

        # Round-trip through the R1 adapters: snapshot_session -> apply_save.
        _tick_n(session.world_sim, session.npc_list, session.defeated_npcs, n=300)
        pre = (session.world_sim.clock.tick_count, session.npc_list[0][0].hp,
               round(session.npc_list[0][0].x, 3))
        ctx.save_manager.snapshot_session(session)

        ctx2 = create_game_context(db_path=tmp_db)
        ctxs.append(ctx2)
        tm2 = TileMap()
        tm2.load_real_map()
        src2 = tm2.get_need_sources()
        session2 = WorldSession.new_game(ctx2, tm2, src2)
        session2.apply_save(ctx2.save_manager.restore(), ctx2)
        post = (session2.world_sim.clock.tick_count, session2.npc_list[0][0].hp,
                round(session2.npc_list[0][0].x, 3))
        check(post == pre, "snapshot_session -> apply_save round-trip preserves state",
              f"{post} != {pre}")
    finally:
        for c in ctxs:
            c.db.close()
        os.unlink(tmp_db)


def test_main_compiles():
    print("[G] main.py compiles (headless import/syntax check — window blocks a live run)")
    main_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                             "main.py")
    ok = True
    try:
        py_compile.compile(main_path, doraise=True)
    except py_compile.PyCompileError as e:
        ok = False
        print(f"  (compile error) {e}")
    check(ok, "main.py compiles clean")


# ─── (h) SimulationKernel (R2) — the headless line ────────────────────────────

def test_kernel_headless():
    print("[H] SimulationKernel (R2) — step(dt, now) advances the sim with no pygame render")
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        tmp_db = f.name
    ctxs = []
    try:
        ctx = create_game_context(db_path=tmp_db)
        ctxs.append(ctx)
        tile_map = TileMap()
        tile_map.load_real_map()
        sources = tile_map.get_need_sources()

        kernel = SimulationKernel.new_session(ctx, tile_map, sources)
        check(kernel.session.world_sim.clock.tick_count == 0, "kernel starts at tick 0")

        # Step N frames headless; the sim clock must advance and each step returns a SimFrame.
        dt = 1.0 / settings.SIM_TICK_RATE if settings.SIM_TICK_RATE > 0 else 1.0 / 60.0
        last = None
        for i in range(200):
            last = kernel.step(dt, now=float(i) * dt)
        check(isinstance(last, SimFrame), "step() returns a SimFrame")
        check(kernel.session.world_sim.clock.tick_count > 0,
              "sim clock advanced after stepping headless",
              f"tick={kernel.session.world_sim.clock.tick_count}")

        # Combat detection: put the player on top of an NPC, past cooldown -> trigger.
        s = kernel.session
        target = s.npc_list[0][0]
        s.player.x, s.player.y = target.x, target.y
        trig = kernel._detect_combat(now=1_000_000.0)
        check(trig is target, "combat detected for the co-located NPC past cooldown")
        # Same NPC, still on cooldown -> no trigger.
        s.combat_cooldowns[target.entity_id] = 1_000_000.0
        check(kernel._detect_combat(now=1_000_000.0 + COMBAT_COOLDOWN - 0.1) is None,
              "no combat while the NPC is on cooldown")

        # Panel-edge detection: player at the north edge -> a [PANEL] message once.
        s.player.x = settings.TILE_SIZE * 5
        s.player.y = 0.0
        kernel._last_at_edge = None
        msg = kernel._detect_panel_edge()
        check(msg is not None and "north" in msg, "north panel edge detected", f"{msg}")
        check(kernel._detect_panel_edge() is None,
              "edge is edge-triggered (no repeat while still at same edge)")

        # Lifecycle: start_new_session resets; load restores through the kernel.
        s.defeated_npcs.add(target.entity_id)
        kernel.save(slot_id=3)
        kernel.start_new_session()
        check(kernel.session.world_sim.clock.tick_count == 0
              and kernel.session.defeated_npcs == set()
              and kernel._last_at_edge is None,
              "start_new_session() gives a fresh session + reset edge state")
        kernel.load(ctx.save_manager.restore(slot_id=3))
        check(target.entity_id in kernel.session.defeated_npcs,
              "kernel.load() restores the saved defeated set")
    finally:
        for c in ctxs:
            c.db.close()
        os.unlink(tmp_db)


# ─── (i) Zone observer lifecycle (R3) — auto-wire + player flash as SimFrame ───

def test_zone_lifecycle():
    print("[I] Zone observers (R3) — new_game auto-wires sim observers; player flash = SimFrame")
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        tmp_db = f.name
    ctx = None
    try:
        ctx = create_game_context(db_path=tmp_db)
        tile_map = TileMap()
        tile_map.load_real_map()
        sources = tile_map.get_need_sources()

        kernel = SimulationKernel.new_session(ctx, tile_map, sources)
        s = kernel.session
        # new_game() wired exactly the 2 SIM-side observers (log + zone AI).
        check(len(s.world_sim.zone_tracker._callbacks) == 2,
              "new_game auto-wires 2 sim-side zone observers",
              f"got {len(s.world_sim.zone_tracker._callbacks)}")
        check(s.zone_ai is not None, "session owns a ZoneAIResponder")

        # New Game re-wires on the fresh tracker (C0026 fix, now automatic).
        kernel.start_new_session()
        check(len(kernel.session.world_sim.zone_tracker._callbacks) == 2,
              "start_new_session re-wires 2 observers on the fresh tracker",
              f"got {len(kernel.session.world_sim.zone_tracker._callbacks)}")

        # Player crossing surfaces as a SimFrame event (not a UI subscriber).
        s = kernel.session
        px, py = ctx.current_panel[0], ctx.current_panel[1]
        cell_by_room = {}
        for col in range(settings.COLS):
            for row in range(settings.ROWS):
                room = ctx.rooms.get_room_for_region(px, py, tile_map.get_region(col, row))
                if room is not None and id(room) not in cell_by_room:
                    cell_by_room[id(room)] = (col, row, room.name)
        (ca, cb) = list(cell_by_room.values())[:2]
        dt = 1.0 / settings.SIM_TICK_RATE if settings.SIM_TICK_RATE > 0 else 1.0 / 60.0

        s.player.x, s.player.y = tile_map.grid_to_world_center(ca[0], ca[1])
        kernel.step(dt, now=0.0)                     # caches the player's room (no flash)
        s.player.x, s.player.y = tile_map.grid_to_world_center(cb[0], cb[1])
        frame = kernel.step(dt, now=dt)              # crossing -> zone_flash event
        check(frame.zone_flash == cb[2],
              "player crossing surfaces as frame.zone_flash", f"{frame.zone_flash} != {cb[2]}")
    finally:
        if ctx:
            ctx.db.close()
        os.unlink(tmp_db)


# ─── Run ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 66)
    print("Stage 4.6R / R0 — Runtime Characterization Safety Net")
    print("=" * 66)
    test_new_game_reset()
    test_double_round_trip()
    test_zone_subscriber_wiring()
    test_defeated_drives_kill()
    test_item_chest_round_trip()
    test_world_session()
    test_main_compiles()
    test_kernel_headless()
    test_zone_lifecycle()
    print("=" * 66)
    print(f"  {_passed} PASS  |  {_failed} FAIL")
    print("=" * 66)
    pygame.quit()
    sys.exit(0 if _failed == 0 else 1)
