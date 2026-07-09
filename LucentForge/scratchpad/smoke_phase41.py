"""Phase 4.1 smoke — attribute layer through the real GameContext + factory.

Run from LucentForge directory: py scratchpad/smoke_phase41.py
No pygame display required.
"""
import os
import sys
import tempfile

sys.path.insert(0, os.path.abspath("."))
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from Mechanics.bootstrap import create_game_context           # noqa: E402
from Mechanics.entities.factory import create_player, create_all_npcs  # noqa: E402
from Mechanics.services.outcome import attribute_term          # noqa: E402

passed = failed = 0


def check(label, cond, detail=""):
    global passed, failed
    if cond:
        print(f"  PASS  {label}"); passed += 1
    else:
        print(f"  FAIL  {label}" + (f" -- {detail}" if detail else "")); failed += 1


# Pre-4.1 authored combat stats (STR, MAG, LCK, DEF, RES, DEX) — parity target.
EXPECTED = {
    "player":    (10, 6, 5, 5, 0, 8),
    "npc_01":    (12, 0, 5, 4, 0, 6),
    "npc_02":    (8, 14, 5, 3, 3, 9),
    "npc_03":    (14, 0, 4, 6, 0, 5),
    "npc_04":    (6, 12, 6, 3, 4, 10),
    "goblin_01": (8, 0, 3, 2, 0, 6),
    "goblin_02": (10, 0, 5, 3, 0, 8),
    "dragon_01": (22, 18, 8, 12, 8, 6),
}

db = os.path.join(tempfile.gettempdir(), "lf_attr_smoke.db")
if os.path.exists(db):
    os.remove(db)

print("\n[1] GameContext + factory spawn (real DB seed)")
ctx = create_game_context(db_path=db)
player = create_player(ctx)
npcs = create_all_npcs(ctx)
check("player spawned", player is not None)
check("all npcs spawned", len(npcs) == 7, f"got {len(npcs)}")

everyone = [player] + npcs

print("\n[2] Every entity has a populated Attributes layer")
for e in everyone:
    check(f"{e.entity_id}: has .attributes", hasattr(e, "attributes") and e.attributes is not None)

print("\n[3] Derived Stats reproduce pre-4.1 combat numbers (parity)")
for e in everyone:
    s = e.stats
    got = (s.STR, s.MAG, s.LCK, s.DEF, s.RES, s.DEX)
    check(f"{e.entity_id}: stats parity", got == EXPECTED[e.entity_id],
          f"got={got} want={EXPECTED[e.entity_id]}")

print("\n[4] Attribute->Stats mapping is internally consistent (M2)")
for e in everyone:
    a = e.attributes
    check(f"{e.entity_id}: physique->STR", a.physique == e.stats.STR)
    check(f"{e.entity_id}: reflexes->DEX", a.reflexes == e.stats.DEX)
    check(f"{e.entity_id}: intellect->MAG", a.intellect == e.stats.MAG)
    check(f"{e.entity_id}: constitution->DEF", a.constitution == e.stats.DEF)

print("\n[5] attribute_term reads real attributes (Intuition no longer hard-zero)")
check("reflexes term == player.reflexes (ATTR_SCALE=1)",
      attribute_term(player.attributes, "reflexes") == player.attributes.reflexes)
check("intuition term is now real (>0 for player)",
      attribute_term(player.attributes, "intuition") == player.attributes.intuition
      and player.attributes.intuition > 0)

print(f"\n{'='*50}")
print(f"  {passed} PASS  |  {failed} FAIL")
if failed:
    sys.exit(1)
print("  Phase 4.1 smoke CLEAN")
