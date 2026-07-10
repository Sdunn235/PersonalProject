"""Phase 4.5a smoke — Bit/Byte casting economy (typing, pools, formula costs, spending).

Run from LucentForge directory: py scratchpad/smoke_phase45a.py
No pygame display required.
"""
import os
import sys
import tempfile

sys.path.insert(0, os.path.abspath("."))
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import settings  # noqa: E402
from Mechanics.bootstrap import create_game_context  # noqa: E402
from Mechanics.entities.factory import create_player, create_all_npcs  # noqa: E402
from Mechanics.entities.derivation import byte_capacity, bit_capacity  # noqa: E402
from Mechanics.combat.casting import spell_pool_and_cost  # noqa: E402
from Mechanics.combat.spell_sets import get_spells  # noqa: E402
from Mechanics.combat.fighter import build_fighter  # noqa: E402
from Mechanics.combat.ability_resolver import AbilityResolver  # noqa: E402
from Mechanics.entities.stats import Stats  # noqa: E402

passed = failed = 0


def check(label, cond, detail=""):
    global passed, failed
    if cond:
        print(f"  PASS  {label}"); passed += 1
    else:
        print(f"  FAIL  {label}" + (f" -- {detail}" if detail else "")); failed += 1


db = os.path.join(tempfile.gettempdir(), "lf_cast_smoke.db")
if os.path.exists(db):
    os.remove(db)
ctx = create_game_context(db_path=db)
player = create_player(ctx)
npcs = {n.entity_id: n for n in create_all_npcs(ctx)}

print("\n[1] Byte pool = (Int x Con x Intellect) / 8 (formula LIVE)")
check("player byte == 22", player.max_byte_pool == 22, f"got {player.max_byte_pool}")
check("dragon byte == 270", npcs['dragon_01'].max_byte_pool == 270, f"got {npcs['dragon_01'].max_byte_pool}")
check("goblin byte == 0 (Intellect 0 -> pure Bit-caster)", npcs['goblin_01'].max_byte_pool == 0)
check("player bit == 30 (Int x Con)", player.max_bit_pool == 30, f"got {player.max_bit_pool}")

print("\n[2] spell typing + formula costs")
EXPECT = {  # (pool, cost) with K_bit=5, K_byte=3, heal pseudo=amount_pct*10
    "fireball":   ("bit", round(1.4 * settings.BIT_COST_PER_POWER)),
    "ice_shard":  ("bit", round(1.2 * settings.BIT_COST_PER_POWER)),
    "lightning":  ("bit", round(1.6 * settings.BIT_COST_PER_POWER)),
    "heal_light": ("byte", round(0.20 * settings.HEAL_POWER_SCALE * settings.BYTE_COST_PER_POWER)),
}
for sid, want in EXPECT.items():
    sp = ctx.abilities.get_by_id(sid)
    check(f"{sid} carries magic_kind", "magic_kind" in sp, "STRIPPED by loader!")
    check(f"{sid} -> {want}", spell_pool_and_cost(sp) == want, f"got {spell_pool_and_cost(sp)}")

print("\n[3] get_spells preserves magic_kind through the DAO")
psp = {s["id"]: s for s in get_spells(ctx, "player")}
check("player spells loaded", len(psp) >= 2)
check("fireball magic_kind survives get_spells", psp.get("fireball", {}).get("magic_kind") == "BIT")

print("\n[4] combat spending routes to the correct pool")
res = AbilityResolver()
f = build_fighter("T", 100, Stats(), mp=20, max_mp=20, bits=30, max_bits=30)
res.validate_and_pay(f, ctx.abilities.get_by_id("fireball"))   # BIT, cost 7
check("BIT spell drained bits", f.bits == 30 - 7 and f.mp == 20, f"bits={f.bits} mp={f.mp}")
res.validate_and_pay(f, ctx.abilities.get_by_id("heal_light"))  # BYTE, cost 6
check("BYTE spell drained bytes (mp)", f.mp == 20 - 6 and f.bits == 23, f"bits={f.bits} mp={f.mp}")

print("\n[5] unaffordable -> basic fallback, no pool spent")
f2 = build_fighter("T2", 100, Stats(), mp=0, max_mp=20, bits=2, max_bits=30)
out = res.validate_and_pay(f2, ctx.abilities.get_by_id("lightning"))  # BIT cost 8 > 2
check("falls back to basic", out["id"] == "_basic")
check("no bits spent on fallback", f2.bits == 2)

print(f"\n{'='*52}")
print(f"  {passed} PASS  |  {failed} FAIL")
if failed:
    sys.exit(1)
print("  Phase 4.5a smoke CLEAN")
