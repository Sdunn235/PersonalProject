"""Phase 4.2 smoke — passive Intuition trap perception (§M8).

Run from LucentForge directory: py scratchpad/smoke_phase42.py
No pygame display required (dummy SDL).
"""
import os
import sys
import tempfile

sys.path.insert(0, os.path.abspath("."))
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame  # noqa: E402
import settings  # noqa: E402
from Mechanics.bootstrap import create_game_context  # noqa: E402
from Mechanics.entities.factory import create_player, create_all_npcs  # noqa: E402
from Mechanics.items.containers import Chest  # noqa: E402
from Mechanics.items.enums import TrapType  # noqa: E402
from Mechanics.services.perception import perceive_traps  # noqa: E402
from Mechanics.renderer.trap_overlay import draw_trap_markers  # noqa: E402

passed = failed = 0


def check(label, cond, detail=""):
    global passed, failed
    if cond:
        print(f"  PASS  {label}"); passed += 1
    else:
        print(f"  FAIL  {label}" + (f" -- {detail}" if detail else "")); failed += 1


def at_tile(entity, col, row):
    entity.x = col * settings.TILE_SIZE + settings.TILE_SIZE / 2
    entity.y = row * settings.TILE_SIZE + settings.TILE_SIZE / 2


db = os.path.join(tempfile.gettempdir(), "lf_perc_smoke.db")
if os.path.exists(db):
    os.remove(db)
ctx = create_game_context(db_path=db)
player = create_player(ctx)
npcs = create_all_npcs(ctx)
gruk = next(n for n in npcs if n.entity_id == "goblin_01")  # intuition 4

print("\n[0] preconditions")
check("player intuition == 6", player.attributes.intuition == 6)
check("gruk intuition == 4", gruk.attributes.intuition == 4)

# Fresh chest registry each test (perception mutates state).
def make_reg():
    trapped = Chest(id="goblin_hoard", col=2, row=14, is_trapped=True,
                    trap_type=TrapType.MECHANICAL, trap_damage=15)
    safe = Chest(id="town_supply", col=11, row=8, is_trapped=False)
    return {"goblin_hoard": trapped, "town_supply": safe}

print("\n[1] out of radius -> not perceived")
reg = make_reg()
at_tile(player, 10, 10)  # Manhattan dist to (2,14) = 12
hints = perceive_traps(player, reg)
check("no hint out of range", hints == [])
check("chest not perceived", reg["goblin_hoard"].trap_perceived is False)

print("\n[2] adjacent + high intuition -> perceived (4+6 >= 10)")
reg = make_reg()
at_tile(player, 2, 13)  # dist 1
hints = perceive_traps(player, reg)
check("one hint fired", len(hints) == 1)
check("chest now perceived", reg["goblin_hoard"].trap_perceived is True)
check("hint text mentions trap", "trap" in hints[0].lower())

print("\n[3] idempotent -> no re-fire once perceived")
hints2 = perceive_traps(player, reg)
check("no new hint on second pass", hints2 == [])

print("\n[4] safe chest never perceived")
check("non-trapped chest untouched", reg["town_supply"].trap_perceived is False)

print("\n[5] adjacent + low intuition -> NOT perceived (4+4 < 10)")
reg = make_reg()
at_tile(gruk, 2, 13)
hints = perceive_traps(gruk, reg)
check("low-intuition entity misses trap", hints == [])
check("chest stays hidden", reg["goblin_hoard"].trap_perceived is False)

print("\n[6] opened chest is ignored")
reg = make_reg()
reg["goblin_hoard"].is_opened = True
at_tile(player, 2, 13)
check("opened trapped chest not perceived", perceive_traps(player, reg) == [])

print("\n[7] overlay renders without error")
pygame.init()
pygame.font.init()
surf = pygame.Surface((576, 576))
font = pygame.font.SysFont("consolas", 18)
reg = make_reg()
reg["goblin_hoard"].trap_perceived = True
try:
    draw_trap_markers(surf, reg, font)
    check("draw_trap_markers ran", True)
except Exception as exc:  # noqa: BLE001
    check("draw_trap_markers ran", False, str(exc))

print(f"\n{'='*50}")
print(f"  {passed} PASS  |  {failed} FAIL")
if failed:
    sys.exit(1)
print("  Phase 4.2 smoke CLEAN")
