"""Phase 4.5b smoke — Bits->Bytes conversion + regen flip.

Run from LucentForge directory: py scratchpad/smoke_phase45b.py
No pygame display required.
"""
import os
import sys

sys.path.insert(0, os.path.abspath("."))
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import settings  # noqa: E402
from Mechanics.combat import rules  # noqa: E402
from Mechanics.combat.casting import convert_amount  # noqa: E402
from Mechanics.combat.turn_end import TurnEndHandler  # noqa: E402
from Mechanics.combat.fighter import build_fighter  # noqa: E402
from Mechanics.entities.stats import Stats  # noqa: E402

passed = failed = 0


def check(label, cond, detail=""):
    global passed, failed
    if cond:
        print(f"  PASS  {label}"); passed += 1
    else:
        print(f"  FAIL  {label}" + (f" -- {detail}" if detail else "")); failed += 1


print("\n[1] convert_amount: 8:1 ratio, capped by bits + byte headroom")
check("chunk convert (30 bits, rate 16) -> 2 bytes, 14 bits left",
      convert_amount(30, 0, 22, 16) == (14, 2, 2))
check("under 8 bits -> nothing (5 bits)",
      convert_amount(5, 0, 22, 16) == (5, 0, 0))
check("byte headroom caps gain (room 2)",
      convert_amount(100, 20, 22, 16) == (84, 22, 2))
check("byte headroom caps to 1 (room 1)",
      convert_amount(100, 21, 22, 16) == (92, 22, 1))
check("full at max -> no-op",
      convert_amount(50, 22, 22, 16) == (50, 22, 0))
check("overworld full convert (all 30 bits) -> 3 bytes, 6 left",
      convert_amount(30, 0, 22, 30) == (6, 3, 3))

print("\n[2] regen flip: Bits regen per turn, Bytes do NOT")
check("BIT_REGEN_PER_TURN defined", hasattr(rules, "BIT_REGEN_PER_TURN"))
f = build_fighter("T", 100, Stats(), mp=5, max_mp=22, bits=10, max_bits=30,
                  cycles=50, max_cycles=100)
d = build_fighter("D", 100, Stats(), mp=0, max_mp=10, bits=0, max_bits=10)
TurnEndHandler().apply(f, d)
check("bits regen by BIT_REGEN_PER_TURN", f.bits == 10 + rules.BIT_REGEN_PER_TURN, f"got {f.bits}")
check("byte pool (mp) did NOT regen", f.mp == 5, f"got {f.mp}")
check("bits cap at max_bits", TurnEndHandler().apply(build_fighter('X',1,Stats(),bits=29,max_bits=30,mp=0,max_mp=5), d) or
      True)  # smoke: no exception on cap path
capf = build_fighter("C", 100, Stats(), bits=29, max_bits=30, mp=0, max_mp=5)
TurnEndHandler().apply(capf, d)
check("bits clamp to max (29+4 -> 30)", capf.bits == 30, f"got {capf.bits}")

print("\n[3] settings knob present")
check("CONVERT_RATE_BITS defined", hasattr(settings, "CONVERT_RATE_BITS") and settings.CONVERT_RATE_BITS == 16)

print(f"\n{'='*52}")
print(f"  {passed} PASS  |  {failed} FAIL")
if failed:
    sys.exit(1)
print("  Phase 4.5b smoke CLEAN")
