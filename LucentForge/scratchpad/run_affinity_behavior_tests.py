# run_affinity_behavior_tests.py — Affinity Behavioral Loop smoke (Phase A).
#
# Covers the biochem/affinity addendum §B6 testing doctrine: lattice_distance,
# comfort_score tiers, the emitter, stress->urgency, real-room-data comfort, and the
# end-to-end controller wiring. Runnable as a subprocess (exits 1 on any failure).
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
    def __init__(self, aff, inten):
        self.affinity, self.affinity_intensity = aff, inten

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

print("=" * 64)
if _fails:
    print(f"{len(_fails)} FAIL: " + "; ".join(_fails))
    sys.exit(1)
print("Affinity behavior smoke CLEAN — all §B6 checks pass")
