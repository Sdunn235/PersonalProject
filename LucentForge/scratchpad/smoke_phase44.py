"""Phase 4.4 smoke — affinity model (enum, opposition, mutable state, authoring).

Run from LucentForge directory: py scratchpad/smoke_phase44.py
No pygame display required.
"""
import os
import sys
import tempfile

sys.path.insert(0, os.path.abspath("."))
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from Mechanics.entities.affinity import Affinity, AffinityState, opposite  # noqa: E402
from Mechanics.bootstrap import create_game_context  # noqa: E402
from Mechanics.entities.factory import create_player, create_all_npcs  # noqa: E402
from Mechanics.world.rooms import RoomRegistry  # noqa: E402

passed = failed = 0


def check(label, cond, detail=""):
    global passed, failed
    if cond:
        print(f"  PASS  {label}"); passed += 1
    else:
        print(f"  FAIL  {label}" + (f" -- {detail}" if detail else "")); failed += 1


print("\n[1] Affinity enum + opposition (M6)")
check("6 elements", len(list(Affinity)) == 6)
pairs = {(Affinity.FIRE, Affinity.WATER), (Affinity.EARTH, Affinity.AIR),
         (Affinity.LIGHT, Affinity.VOID)}
check("fire<->water", opposite(Affinity.FIRE) == Affinity.WATER and opposite(Affinity.WATER) == Affinity.FIRE)
check("earth<->air", opposite(Affinity.EARTH) == Affinity.AIR and opposite(Affinity.AIR) == Affinity.EARTH)
check("light<->void", opposite(Affinity.LIGHT) == Affinity.VOID and opposite(Affinity.VOID) == Affinity.LIGHT)
check("opposite is total + involutive",
      all(opposite(opposite(e)) == e for e in Affinity))

print("\n[2] AffinityState: innate + grant/suppress")
st = AffinityState(innate=Affinity.FIRE)
check("effective starts as innate only", st.effective() == frozenset({Affinity.FIRE}))
st.grant(Affinity.WATER)
check("grant adds (plural now)", st.effective() == frozenset({Affinity.FIRE, Affinity.WATER}))
st.suppress(Affinity.FIRE)
check("suppress removes even innate", st.effective() == frozenset({Affinity.WATER}))
st.grant(Affinity.FIRE)
check("grant un-suppresses", st.effective() == frozenset({Affinity.FIRE, Affinity.WATER}))
st.reset_mods()
check("reset_mods returns to innate", st.effective() == frozenset({Affinity.FIRE}))

print("\n[3] AffinityState dict round-trip")
st2 = AffinityState(innate=Affinity.AIR)
st2.grant(Affinity.LIGHT)
st2.suppress(Affinity.AIR)
back = AffinityState.from_dict(st2.as_dict())
check("round-trip effective matches", back.effective() == st2.effective())

print("\n[4] entity innate affinities (provisional mapping)")
db = os.path.join(tempfile.gettempdir(), "lf_affinity_smoke.db")
if os.path.exists(db):
    os.remove(db)
ctx = create_game_context(db_path=db)
player = create_player(ctx)
npcs = {n.entity_id: n for n in create_all_npcs(ctx)}
EXPECTED = {
    "player": Affinity.LIGHT, "npc_01": Affinity.AIR, "npc_02": Affinity.WATER,
    "npc_03": Affinity.EARTH, "npc_04": Affinity.AIR, "goblin_01": Affinity.EARTH,
    "goblin_02": Affinity.EARTH, "dragon_01": Affinity.FIRE,
}
check("player affinity == LIGHT", player.affinity.innate == Affinity.LIGHT)
for eid, want in EXPECTED.items():
    if eid == "player":
        continue
    got = npcs[eid].affinity.innate
    check(f"{eid} affinity == {want.value}", got == want, f"got {got}")

print("\n[5] region affinities (rooms.json)")
reg = RoomRegistry.from_json(os.path.join("Mechanics", "data", "rooms.json"))
REGIONS = {
    "forest": (Affinity.EARTH, 0.5), "river": (Affinity.WATER, 0.7),
    "farm": (Affinity.EARTH, 0.4), "goblin_camp": (Affinity.EARTH, 0.5),
}
for tag, (el, inten) in REGIONS.items():
    room = reg.get_room_for_region(0, 0, tag)
    check(f"{tag} = {el.value} @ {inten}",
          room is not None and room.affinity == el and abs(room.affinity_intensity - inten) < 1e-9)
# Neutral regions carry no affinity.
for tag in ("town_center", "homes", "storage", "bridge", "town_outskirts"):
    room = reg.get_room_for_region(0, 0, tag)
    check(f"{tag} neutral (no affinity)", room is not None and room.affinity is None)

print(f"\n{'='*50}")
print(f"  {passed} PASS  |  {failed} FAIL")
if failed:
    sys.exit(1)
print("  Phase 4.4 smoke CLEAN")
