# run_affinity_behavior_tests.py — Affinity Behavioral Loop smoke (Phases A + B).
#
# Covers the biochem/affinity addendum §B6 testing doctrine: lattice_distance,
# comfort_score tiers, the emitter, stress->urgency, real-room-data comfort, end-to-end
# controller wiring (Phase A), and the learned region-comfort EMA + comfort-relocate
# drive (Phase B, §B6.5). Runnable as a subprocess (exits 1 on any failure).
#
#   py scratchpad/run_affinity_behavior_tests.py
import os
import sys
import tempfile

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from Mechanics.entities.affinity import (  # noqa: E402
    Affinity as A, AffinityState, lattice_distance, comfort_score)
from Mechanics.biochem.chemical import Chemicals  # noqa: E402
from Mechanics.biochem.emitter import AffinityComfortEmitter  # noqa: E402
from Mechanics.biochem.drive import Drive  # noqa: E402
from Mechanics.entities.traits import Traits  # noqa: E402

_fails: list[str] = []


def check(label: str, cond: bool) -> None:
    print(f"[{'PASS' if cond else 'FAIL'}] {label}")
    if not cond:
        _fails.append(label)


print("=" * 64)
print("Affinity Behavioral Loop smoke — addendum §B6")
print("=" * 64)

# §B6.2 — lattice_distance symmetric, [0,4], 0 iff equal
dist_ok = True
for a in A:
    if lattice_distance(a, a) != 0:
        dist_ok = False
    for b in A:
        d = lattice_distance(a, b)
        if not (0 <= d <= 4) or d != lattice_distance(b, a):
            dist_ok = False
check("§B6.2 lattice_distance symmetric, 0..4, 0 iff equal", dist_ok)
check("§B6.2 ring geometry (Fire-Water across=4, Fire-Plasma=1, Fire-Air=2)",
      lattice_distance(A.FIRE, A.WATER) == 4
      and lattice_distance(A.FIRE, A.PLASMA) == 1
      and lattice_distance(A.FIRE, A.AIR) == 2)

# §B6.1 — comfort_score tiers + intensity scaling + neutral
fs = frozenset({A.FIRE})
check("§B6.1 same=+1.0, dist1=+0.5, dist2=+0.2, across=-0.8",
      comfort_score(fs, A.FIRE, 1.0) == 1.0
      and comfort_score(fs, A.PLASMA, 1.0) == 0.5
      and abs(comfort_score(fs, A.AIR, 1.0) - 0.2) < 1e-9
      and comfort_score(fs, A.WATER, 1.0) == -0.8)
check("§B6.1 intensity scales; best-of across plural affinities",
      abs(comfort_score(fs, A.FIRE, 0.5) - 0.5) < 1e-9
      and comfort_score(frozenset({A.FIRE, A.WATER}), A.WATER, 1.0) == 1.0)
check("§B6.1 neutral entity / neutral region / zero intensity -> 0.0",
      comfort_score(frozenset(), A.FIRE, 1.0) == 0.0
      and comfort_score(fs, None, 1.0) == 0.0
      and comfort_score(fs, A.FIRE, 0.0) == 0.0)

# §B6.3 — emitter moves chemicals toward target, stays [0,1]
class _Stub:
    def __init__(self, aff):
        self.affinity = AffinityState(innate=aff)
class _Room:
    # Mirror the real RoomDefinition fields the controller reads (affinity, intensity,
    # and id — the controller records region comfort keyed by room.id in Phase B).
    def __init__(self, aff, inten, room_id="_test_room"):
        self.affinity, self.affinity_intensity = aff, inten
        self.id = room_id

ch = Chemicals()
em = AffinityComfortEmitter(comfort_gain=0.5, stress_gain=0.5)
for _ in range(50):
    em.emit(ch, _Stub(A.FIRE), _Room(A.WATER, 1.0))   # clash -> stress
check("§B6.3 clash builds stress, not comfort; in [0,1]",
      ch.get("stress") > 0.5 and ch.get("comfort") < 0.05
      and 0.0 <= ch.get("stress") <= 1.0)
for _ in range(50):
    em.emit(ch, _Stub(A.FIRE), _Room(A.FIRE, 1.0))    # match -> comfort
check("§B6.3 match builds comfort, stress relaxes",
      ch.get("comfort") > 0.5 and ch.get("stress") < 0.1)

# §B6.4 — stress raises drive urgency monotonically; stress=0 is the pre-arc value
traits = Traits()
traits.fearfulness = 0.8
d = Drive("Test", "hunger", "hunger_chem", base_weight=1.0)
c0 = Chemicals(); c0.set("hunger_chem", 0.5)
u0 = d.compute_urgency(c0, traits)
c1 = Chemicals(); c1.set("hunger_chem", 0.5); c1.set("stress", 0.5)
u1 = d.compute_urgency(c1, traits)
check("§B6.4 stress increases urgency; stress=0 unchanged",
      u1 > u0 and abs(u0 - min(1.0, 0.5 * (1.0 + 0.8 * 0.0))) < 1e-9)

# §B6.5 — real rooms.json data: forest (EARTH 0.5) comforts an EARTH being, stresses AIR
from Mechanics.world.rooms import RoomRegistry  # noqa: E402
rooms = RoomRegistry.from_json(os.path.join(_ROOT, "Mechanics", "data", "rooms.json"))
forest = rooms.get_by_id("panel00_forest")
check("real data: forest room is EARTH-attuned",
      forest is not None and forest.affinity == A.EARTH and forest.affinity_intensity > 0)
check("real data: EARTH being comforted, AIR being stressed in forest",
      comfort_score(frozenset({A.EARTH}), forest.affinity, forest.affinity_intensity) > 0
      and comfort_score(frozenset({A.AIR}), forest.affinity, forest.affinity_intensity) < 0)

# Integration: controller wiring (temp DB, no window). Proves bootstrap passes the
# RoomRegistry, _current_room maps region->room, and the emitter runs off the controller.
print("-" * 64)
try:
    from Mechanics.bootstrap import (create_game_context, create_npc_controller,
                                     create_world_sim)
    from Mechanics.needs.need_source import make_default_sources
    from Mechanics.entities.factory import create_all_npcs
    from Mechanics.world.tile_map import TileMap

    tmp_db = os.path.join(tempfile.gettempdir(), "lf_affinity_smoke.db")
    if os.path.exists(tmp_db):
        os.remove(tmp_db)
    ctx = create_game_context(db_path=tmp_db)
    sources = make_default_sources()
    world_sim = create_world_sim(sources)
    npcs = create_all_npcs(ctx)
    earth_npc = next(n for n in npcs if n.affinity.effective() == frozenset({A.EARTH}))
    ctrl = create_npc_controller(earth_npc, ctx, sources, TileMap(), world_sim)

    # (1) bootstrap wiring: controller got the RoomRegistry
    check("integration: bootstrap injects RoomRegistry into controller",
          ctrl.rooms is ctx.rooms)

    # (2) _current_room maps a region tag -> room via the registry (fake tile_map)
    class _FakeTM:
        def world_to_grid(self, x, y):
            return (1, 1)
        def get_region(self, c, r):
            return "forest"   # EARTH-attuned room in rooms.json
    ctrl.tile_map = _FakeTM()
    resolved = ctrl._current_room()
    check("integration: _current_room resolves region tag -> forest (EARTH)",
          resolved is not None and resolved.affinity == A.EARTH)

    # (3) the controller's own emitter builds comfort off real room data
    for _ in range(60):
        ctrl.affinity_comfort = ctrl._affinity_emitter.emit(
            ctrl.brain.chemicals, earth_npc, resolved)
    check("integration: EARTH npc in forest builds comfort via the controller emitter",
          ctrl.affinity_comfort > 0 and ctrl.brain.chemicals.get("comfort") > 0.0)
    if hasattr(ctx, "close"):
        ctx.close()
except Exception as ex:  # noqa: BLE001
    import traceback
    traceback.print_exc()
    check(f"integration: controller wiring (exception: {ex})", False)

# §B6.6 — full-loop dynamics: comfort accumulates under the REAL ctrl.update() loop
# (decay-then-emit ordering, needs tick, state machine all live — not a bare emit), and
# tracks region changes (motion). The pinned _current_room isolates loop dynamics from
# region resolution, which §B6.5 + the integration block already cover.
print("-" * 64)
try:
    from Mechanics.bootstrap import (create_game_context, create_npc_controller,
                                     create_world_sim)
    from Mechanics.needs.need_source import make_default_sources
    from Mechanics.entities.factory import create_all_npcs
    from Mechanics.world.tile_map import TileMap

    _GAIN = 0.05                          # AffinityComfortEmitter default comfort_gain
    _DECAY = Chemicals._DECAY * 0.7       # comfort/stress decay in Chemicals.tick

    def _steady(target):                  # fixed point of decay-then-emit per tick
        return 0.0 if target <= 0.0 else target - _DECAY * (1.0 / _GAIN - 1.0)

    tmp_db2 = os.path.join(tempfile.gettempdir(), "lf_affinity_fullloop.db")
    if os.path.exists(tmp_db2):
        try:
            os.remove(tmp_db2)
        except OSError:
            pass
    ctx2 = create_game_context(db_path=tmp_db2)
    sources2 = make_default_sources()
    world2 = create_world_sim(sources2)
    npcs2 = create_all_npcs(ctx2)
    npc2 = next(n for n in npcs2 if n.affinity.effective() == frozenset({A.EARTH}))
    ctrl2 = create_npc_controller(npc2, ctx2, sources2, TileMap(), world2)

    forest2 = ctx2.rooms.get_by_id("panel00_forest")   # EARTH @ 0.5 — strong match for EARTH
    river2 = ctx2.rooms.get_by_id("panel00_river")      # WATER @ 0.7 — dist-2, mild + for EARTH
    # No EARTH-clashing region exists in rooms.json (only EARTH + WATER rooms, which are
    # lattice-dist 2 apart). Construct one so the true match->clash motion can be asserted.
    clash2 = _Room(A.AIR, 1.0)                          # dist-4 from EARTH -> score -0.8

    def _drive(room, ticks):
        ctrl2._current_room = lambda: room              # pin locus; emitter re-samples each tick
        for _ in range(ticks):
            ctrl2.update(1 / 60)
        c = ctrl2.brain.chemicals
        return c.get("comfort"), c.get("stress")

    # (A) #1 — comfort accumulates in the live loop to the predicted steady state
    cA, sA = _drive(forest2, 300)
    check("§B6.6 live ctrl.update() accumulates comfort to predicted steady (match)",
          abs(cA - _steady(0.5)) < 0.01 and sA < 0.02)

    # (B) #2 — motion from a matching region into a clashing one: comfort falls, stress rises
    cB, sB = _drive(clash2, 300)
    check("§B6.6 motion match->clash: comfort falls toward 0 and stress rises",
          cB < cA and cB < 0.02 and sB > 0.5)

    # (C) real-data region tracking: into the river (mild + for EARTH) — comfort settles low+, stress relaxes
    cC, sC = _drive(river2, 300)
    check("§B6.6 motion into milder real region (river): comfort tracks to lower positive, stress relaxes",
          abs(cC - _steady(0.2 * river2.affinity_intensity)) < 0.02 and cC < cA and sC < 0.05)

    if hasattr(ctx2, "close"):
        ctx2.close()
except Exception as ex:  # noqa: BLE001
    import traceback
    traceback.print_exc()
    check(f"§B6.6 full-loop dynamics (exception: {ex})", False)

# ===========================================================================
# Phase B — learned region comfort (EMA) + comfort-relocate drive (§B4/§B6.5)
# ===========================================================================
print("-" * 64)
from Mechanics.ai.memory import Memory  # noqa: E402

# §B6.5 (a) — region-comfort memory is an EMA that rises with repeat exposure.
mem = Memory()
mem.record_region_comfort("r_warm", 0.1, 0)          # unlucky first read
prefs = [mem.get_region_preference("r_warm")]
for t in range(1, 30):
    mem.record_region_comfort("r_warm", 0.6, t)      # region really is comfortable
    prefs.append(mem.get_region_preference("r_warm"))
mono = all(prefs[i] <= prefs[i + 1] + 1e-9 for i in range(len(prefs) - 1))
check("§B6.5 region-comfort EMA rises monotonically toward the comfort value",
      mono and prefs[0] == 0.1 and prefs[-1] > 0.55)

# §B6.5 (b) — best_region picks the highest positive; ignores neutral/negative.
mem.record_region_comfort("r_cold", -0.4, 0)
mem.record_region_comfort("r_mild", 0.2, 0)
best = mem.best_region()
check("§B6.5 best_region returns the highest-comfort region",
      best is not None and best[0] == "r_warm")
mem_neg = Memory()
mem_neg.record_region_comfort("r_neutral", 0.0, 0)
mem_neg.record_region_comfort("r_bad", -0.5, 0)
check("§B6.5 best_region is None when only neutral/negative regions are known",
      mem_neg.best_region() is None)

# §B6.5 (c) — relocate drive fires (and its parity twin doesn't) on a real controller.
print("-" * 64)
try:
    from Mechanics.bootstrap import (create_game_context, create_npc_controller,
                                     create_world_sim)
    from Mechanics.entities.factory import create_all_npcs
    from Mechanics.world.tile_map import TileMap

    tmp_db3 = os.path.join(tempfile.gettempdir(), "lf_relocate.db")
    if os.path.exists(tmp_db3):
        try:
            os.remove(tmp_db3)
        except OSError:
            pass
    ctx3 = create_game_context(db_path=tmp_db3)
    tmap = TileMap()
    tmap.load_real_map()
    sources3 = tmap.get_need_sources()
    world3 = create_world_sim(sources3)
    npcs3 = create_all_npcs(ctx3)
    villager = next(n for n in npcs3 if n.name == "Alder")   # HumanBehavior, neutral spawn
    ctrl3 = create_npc_controller(villager, ctx3, sources3, tmap, world3)

    comfy_id = "panel00_forest"                              # a region Alder is NOT in
    for t in range(5):
        ctrl3.memory.record_region_comfort(comfy_id, 0.5, t)

    # Pin to goblin_camp (EARTH/0.5) so AIR-affinity Alder is uncomfortable
    # (lattice-dist 3 → score -0.2 < COMFORT_CONTENT_THRESHOLD). Without this,
    # C0045 made town_center AIR/0.4, making Alder exactly content there (score=+0.4
    # == threshold), which correctly suppresses relocate but breaks the test.
    goblin_camp_room = ctx3.rooms.get_by_id("panel00_goblin_camp")
    ctrl3._current_room = lambda: goblin_camp_room

    # Relocate FIRES: stressed + non-urgent + a better remembered region -> RELOCATING.
    ctrl3.brain.chemicals.set("stress", 0.6)
    ctrl3._set_state("IDLE")
    ctrl3.update(1 / 60)
    check("§B6.5 stressed idle villager with a remembered-comfortable region relocates",
          ctrl3.state == "RELOCATING"
          and ctrl3.relocate_target_region == comfy_id
          and len(ctrl3.path) > 0)

    # PARITY: stress=0 -> relocate is a no-op -> stays IDLE with no target (pre-Phase-B).
    ctrl3._set_state("IDLE")
    ctrl3.path = []
    ctrl3.relocate_target_region = None
    ctrl3.brain.chemicals.set("stress", 0.0)
    ctrl3.update(1 / 60)
    check("§B6.5 parity: an unstressed villager does not relocate (stays IDLE)",
          ctrl3.state == "IDLE" and ctrl3.relocate_target_region is None)

    if hasattr(ctx3, "close"):
        ctx3.close()
except Exception as ex:  # noqa: BLE001
    import traceback
    traceback.print_exc()
    check(f"§B6.5 relocate drive (exception: {ex})", False)

# ===========================================================================
# Phase C — affinity_strain → perceived need urgency (§B7)
# ===========================================================================
print("-" * 64)
from Mechanics.needs.need import Need  # noqa: E402
import settings as _settings           # noqa: E402

# §B7 (a) — strain builds under sustained discomfort; stays 0 under comfort/neutral.
ch_strain = Chemicals()
em_strain = AffinityComfortEmitter()

for _ in range(600):
    em_strain.emit(ch_strain, _Stub(A.FIRE), _Room(A.WATER, 1.0))  # hostile: score=-0.8
check("§B7 strain builds under sustained discomfort (600 hostile ticks)",
      ch_strain.get("affinity_strain") > 0.05)

ch_neutral = Chemicals()
for _ in range(600):
    em_strain.emit(ch_neutral, _Stub(A.FIRE), _Room(A.FIRE, 1.0))  # comfortable: score=+1.0
check("§B7 parity: strain stays 0 under comfort (score>=0 -> strain_target=0)",
      ch_neutral.get("affinity_strain") < 1e-9)

# §B7 (b) — strain decays when entity moves to comfortable region.
ch_decay = Chemicals()
for _ in range(2400):
    em_strain.emit(ch_decay, _Stub(A.FIRE), _Room(A.WATER, 1.0))  # build strain
strain_peak = ch_decay.get("affinity_strain")
# Comfortable region: emitter approaches strain_target=0 at gain 0.0003/tick.
# After 2400 ticks strain drops to ~49% of peak (0.0003 gain × 2400 = -72% via e^-0.72).
for _ in range(2400):
    em_strain.emit(ch_decay, _Stub(A.FIRE), _Room(A.FIRE, 1.0))   # now comfortable
check("§B7 strain decays when entity moves to comfortable region (2400 ticks each)",
      ch_decay.get("affinity_strain") < strain_peak * 0.7)

# §B7 (c) — need chemical boost under strain; boost=0 when strain=0 (parity).
class _MockNeed:
    def __init__(self, nid, val):
        self.need_id = nid
        self.current_value = val
        self.chemical = nid + "_chem"
    @property
    def is_urgent(self): return self.current_value < 60

needs_list = [_MockNeed("hunger", 80), _MockNeed("thirst", 80)]

ch_boosted = Chemicals()
ch_boosted.set("hunger_chem", 0.20)
ch_boosted.set("thirst_chem", 0.20)
ch_boosted.set("affinity_strain", 0.50)  # inject strain directly
ch_boosted.tick(needs_list)
boost_delta = ch_boosted.get("hunger_chem") - 0.20

ch_parity = Chemicals()
ch_parity.set("hunger_chem", 0.20)
ch_parity.set("thirst_chem", 0.20)
ch_parity.tick(needs_list)  # strain=0 → no boost

check("§B7 strain>0 boosts need chemicals in tick()",
      boost_delta > 0)
check("§B7 parity: strain=0 -> no boost -> need chemicals converge same as pre-arc",
      abs(ch_parity.get("hunger_chem") - ch_boosted.get("hunger_chem")
          + boost_delta) < 1e-6)

# ===========================================================================
# Phase D — region-comfort memory persistence across save/load (C0049)
# Exercises the REAL SaveManager.snapshot()/restore() + apply_save() pipeline,
# not a replicated blob, so it verifies production serialization end-to-end.
# ===========================================================================
print("-" * 64)
try:
    from Mechanics.bootstrap import (create_game_context, create_npc_controller,
                                     create_world_sim, apply_save)
    from Mechanics.entities.factory import create_all_npcs, create_player
    from Mechanics.needs.need import make_default_needs
    from Mechanics.world.tile_map import TileMap

    tmp_db4 = os.path.join(tempfile.gettempdir(), "lf_region_persist.db")
    if os.path.exists(tmp_db4):
        try:
            os.remove(tmp_db4)
        except OSError:
            pass
    ctx4 = create_game_context(db_path=tmp_db4)
    tmap4 = TileMap()
    tmap4.load_real_map()
    sources4 = tmap4.get_need_sources()
    world4 = create_world_sim(sources4)
    npcs4 = create_all_npcs(ctx4)
    villager4 = next(n for n in npcs4 if n.name == "Alder")
    ctrl4 = create_npc_controller(villager4, ctx4, sources4, tmap4, world4)
    player4 = create_player(ctx4)
    player_needs4 = make_default_needs()

    # Seed learned region comfort: forest strongly positive, camp negative.
    for t in range(3):
        ctrl4.memory.record_region_comfort("panel00_forest", 0.5, t)
    ctrl4.memory.record_region_comfort("panel00_goblin_camp", -0.3, 3)
    pre_best = ctrl4.memory.best_region()
    pre_forest = ctrl4.memory.get_region_preference("panel00_forest")

    # Snapshot through the real SaveManager, then wipe live region memory to
    # simulate a fresh load — if restore doesn't repopulate it, asserts fail.
    ctx4.save_manager.snapshot(
        world4, sources4, [ctrl4], player4, player_needs4, set(), {})
    ctrl4.memory._regions.clear()
    save_data4 = ctx4.save_manager.restore()
    apply_save(save_data4, world4, sources4, [ctrl4], player4,
               player_needs4, set(), {})

    post_best = ctrl4.memory.best_region()
    post_forest = ctrl4.memory.get_region_preference("panel00_forest")
    check("§D region-comfort EMA survives snapshot/restore round-trip",
          abs(post_forest - pre_forest) < 1e-9 and post_forest > 0.49)
    check("§D best_region matches pre/post round-trip (forest)",
          post_best is not None and pre_best is not None
          and post_best[0] == pre_best[0] == "panel00_forest"
          and abs(post_best[1] - pre_best[1]) < 1e-9)
    check("§D negative region (goblin_camp) restored, excluded from best_region",
          abs(ctrl4.memory.get_region_preference("panel00_goblin_camp") + 0.3) < 1e-9)

    # Legacy flat blob (pre-C0049) still restores _sources, leaves _regions empty.
    legacy = {
        "world": save_data4["world"],
        "sources": save_data4["sources"],
        "entities": {
            eid: {**edata, "memory": {
                "RIVER": {"need_id": "thirst", "visit_count": 4,
                          "avg_satisfaction": 0.7, "last_visit_tick": 12}}}
            for eid, edata in save_data4["entities"].items()
        },
        "game": save_data4["game"],
        "chests": save_data4["chests"],
    }
    ctrl4.memory._sources.clear()
    ctrl4.memory._regions.clear()
    apply_save(legacy, world4, sources4, [ctrl4], player4,
               player_needs4, set(), {})
    check("§D legacy flat memory blob restores _sources, _regions stays empty",
          "RIVER" in ctrl4.memory._sources
          and abs(ctrl4.memory.get_source_preference("RIVER") - 0.7) < 1e-9
          and len(ctrl4.memory._regions) == 0)

    if hasattr(ctx4, "close"):
        ctx4.close()
except Exception as ex:  # noqa: BLE001
    import traceback
    traceback.print_exc()
    check(f"§D region persistence (exception: {ex})", False)

print("=" * 64)
if _fails:
    print(f"{len(_fails)} FAIL: " + "; ".join(_fails))
    sys.exit(1)
print("Affinity behavior smoke CLEAN — all §B6+§B7+§D checks pass")
