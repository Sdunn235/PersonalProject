# run_grace_tests.py — Grace Migration Arc smoke suite.
#
# Implements the affinity-doc §18 testing doctrine plus data-integration checks.
# Runnable as a subprocess: exits 1 on any failure (no silent PASS-print).
#
#   py scratchpad/run_grace_tests.py
import json
import os
import sys

# Repo root (parent of scratchpad/) on sys.path so Mechanics.* imports resolve.
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from Mechanics.entities.affinity import (  # noqa: E402
    Affinity, AffinityState, OntologicalTrait,
    is_primal, is_derived, parents_of, derived_between, adjacent_primals,
)

_fails: list[str] = []


def check(label: str, cond: bool) -> None:
    status = "PASS" if cond else "FAIL"
    print(f"[{status}] {label}")
    if not cond:
        _fails.append(label)


print("=" * 64)
print("Grace Migration smoke — affinity-doc §18 testing doctrine")
print("=" * 64)

# --- §18 doctrine ---
# 1. Exactly eight affinity enum values.
check("§18.1 exactly 8 affinity values", len(list(Affinity)) == 8)

# 2. Four primals and four Derived.
primals = [a for a in Affinity if is_primal(a)]
derived = [a for a in Affinity if is_derived(a)]
check("§18.2 four primals + four derived", len(primals) == 4 and len(derived) == 4)
check("§18.2 primal/derived partition the enum",
      set(primals) | set(derived) == set(Affinity)
      and not (set(primals) & set(derived)))

# 3. Each Derived has exactly two adjacent primal parents (both primal).
check("§18.3 each derived has 2 primal parents",
      all(len(parents_of(d)) == 2 and all(is_primal(p) for p in parents_of(d))
          for d in derived))

# 4-7. Canonical pair map (order-independent).
check("§18.4 Fire+Air = Plasma",
      derived_between(Affinity.FIRE, Affinity.AIR) == Affinity.PLASMA
      and derived_between(Affinity.AIR, Affinity.FIRE) == Affinity.PLASMA)
check("§18.5 Air+Water = Colloidal Dispersion",
      derived_between(Affinity.AIR, Affinity.WATER) == Affinity.COLLOIDAL_DISPERSION)
check("§18.6 Water+Earth = Non-Newtonian",
      derived_between(Affinity.WATER, Affinity.EARTH) == Affinity.NON_NEWTONIAN)
check("§18.7 Earth+Fire = Bingham Placidity",
      derived_between(Affinity.EARTH, Affinity.FIRE) == Affinity.BINGHAM_PLACIDITY)
check("§18.7b non-adjacent primals bridge to None (Fire+Water)",
      derived_between(Affinity.FIRE, Affinity.WATER) is None)
check("§18.7c adjacency is symmetric two-neighbor",
      adjacent_primals(Affinity.FIRE) == frozenset({Affinity.AIR, Affinity.EARTH}))

# 8. Light and Dark absent from the affinity enum.
check("§18.8 Light/Dark/Void absent from Affinity",
      not any(a.name in ("LIGHT", "DARK", "VOID") for a in Affinity))

# 9. Neutral is not Dark — neutral affinity is a legal, empty-effective state.
neutral = AffinityState()
check("§18.9 neutral state (innate=None) is legal and not Dark",
      neutral.innate is None and neutral.is_neutral()
      and neutral.effective() == frozenset())

# 10. Multiple effective primals do NOT auto-become a Derived.
plural = AffinityState(innate=Affinity.FIRE)
plural.grant(Affinity.AIR)
check("§18.10 plural primals do not auto-derive",
      plural.effective() == frozenset({Affinity.FIRE, Affinity.AIR}))

# 11. Serialization round-trips all eight values (+ None + trait).
round_trips = all(
    AffinityState.from_dict(AffinityState(innate=a).as_dict()).innate == a
    for a in Affinity
)
none_rt = AffinityState.from_dict(AffinityState(innate=None).as_dict()).innate is None
trait_rt = (AffinityState.from_dict(
    AffinityState(innate=None, trait=OntologicalTrait.LIGHT_TOUCHED).as_dict()
).trait is OntologicalTrait.LIGHT_TOUCHED)
check("§18.11 all 8 values + None + trait round-trip",
      round_trips and none_rt and trait_rt)

# 12. Legacy LIGHT/VOID fail visibly (no silent migration layer here).
def _legacy_raises(val: str) -> bool:
    try:
        AffinityState.from_dict({"innate": val})
        return False
    except ValueError:
        return True

check("§18.12 legacy LIGHT fails visibly", _legacy_raises("LIGHT"))
check("§18.12 legacy VOID fails visibly", _legacy_raises("VOID"))

# --- Data-integration checks (the Grace against real content) ---
print("-" * 64)
entities = json.load(open(os.path.join(_ROOT, "Mechanics", "data", "entities.json"),
                          encoding="utf-8"))
from Mechanics.entities.factory import _build_affinity  # noqa: E402

built_ok = True
for e in entities:
    try:
        _build_affinity(e)
    except Exception as ex:  # noqa: BLE001
        built_ok = False
        print(f"   build failed for {e.get('id')}: {ex}")
check("data: all entities build affinity without error", built_ok)

player = next(e for e in entities if e["id"] == "player")
p_state = _build_affinity(player)
check("data: player is neutral + LIGHT_TOUCHED",
      p_state.innate is None and p_state.trait is OntologicalTrait.LIGHT_TOUCHED)

check("data: no entity authors a legacy LIGHT/VOID affinity",
      all(e.get("affinity") not in ("LIGHT", "VOID") for e in entities))

from Mechanics.world.rooms import RoomRegistry  # noqa: E402
rooms = RoomRegistry.from_json(os.path.join(_ROOT, "Mechanics", "data", "rooms.json"))
check("data: rooms load; all room affinities are valid lattice values",
      all(r.affinity is None or isinstance(r.affinity, Affinity) for r in rooms._rooms))

print("=" * 64)
if _fails:
    print(f"{len(_fails)} FAIL: " + "; ".join(_fails))
    sys.exit(1)
print("Grace smoke CLEAN — all doctrine + data checks pass")
