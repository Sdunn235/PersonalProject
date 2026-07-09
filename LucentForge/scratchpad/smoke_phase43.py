"""Phase 4.3 smoke — Bits/Bytes pool split (parity path).

Run from LucentForge directory: py scratchpad/smoke_phase43.py
No pygame display required.
"""
import os
import sys
import tempfile

sys.path.insert(0, os.path.abspath("."))
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from Mechanics.bootstrap import create_game_context  # noqa: E402
from Mechanics.entities.factory import create_player, create_all_npcs  # noqa: E402
from Mechanics.entities.derivation import bit_capacity, BITS_PER_BYTE  # noqa: E402
from Mechanics.items.enums import ConsumableEffect  # noqa: E402
from Mechanics.renderer.inventory_menu import _apply_consumable  # noqa: E402

passed = failed = 0


def check(label, cond, detail=""):
    global passed, failed
    if cond:
        print(f"  PASS  {label}"); passed += 1
    else:
        print(f"  FAIL  {label}" + (f" -- {detail}" if detail else "")); failed += 1


db = os.path.join(tempfile.gettempdir(), "lf_pool_smoke.db")
if os.path.exists(db):
    os.remove(db)
ctx = create_game_context(db_path=db)
player = create_player(ctx)
npcs = create_all_npcs(ctx)
everyone = [player] + npcs

print("\n[1] canonical ratio")
check("1 Byte = 8 Bits", BITS_PER_BYTE == 8)

print("\n[2] Bit pool = Intuition x Constitution (live)")
for e in everyone:
    want = e.attributes.intuition * e.attributes.constitution
    check(f"{e.entity_id}: bit_pool max == Int*Con ({want})",
          e.max_bit_pool == want and e.bit_pool == want, f"got {e.max_bit_pool}")

print("\n[3] Byte pool = mp-parity (unchanged budgets)")
EXPECTED_BYTE = {"player": 50, "npc_01": 50, "npc_02": 50, "npc_03": 50,
                 "npc_04": 50, "goblin_01": 0, "goblin_02": 0, "dragon_01": 80}
for e in everyone:
    check(f"{e.entity_id}: byte max == old mp ({EXPECTED_BYTE[e.entity_id]})",
          e.max_byte_pool == EXPECTED_BYTE[e.entity_id], f"got {e.max_byte_pool}")

print("\n[4] mp compat property aliases the Byte pool")
check("player.mp == byte_pool", player.mp == player.byte_pool)
check("player.max_mp == max_byte_pool", player.max_mp == player.max_byte_pool)
player.mp = 17
check("writing .mp writes byte_pool", player.byte_pool == 17)
player.byte_pool = 33
check("writing byte_pool reflects in .mp", player.mp == 33)

print("\n[5] consumables route to the right pool")
player.bit_pool = 0
player.byte_pool = 0
player.max_bit_pool = 40
player.max_byte_pool = 50
_apply_consumable(player, ConsumableEffect.RESTORE_BITS, 10)
check("RESTORE_BITS fills bit_pool", player.bit_pool == 10 and player.byte_pool == 0)
_apply_consumable(player, ConsumableEffect.RESTORE_BYTES, 15)
check("RESTORE_BYTES fills byte_pool", player.byte_pool == 15 and player.bit_pool == 10)
_apply_consumable(player, ConsumableEffect.RESTORE_MP, 5)
check("RESTORE_MP (bridge) fills byte_pool", player.byte_pool == 20)
_apply_consumable(player, ConsumableEffect.RESTORE_BITS, 999)
check("bit_pool caps at max", player.bit_pool == 40)

print("\n[6] migration m0007 added pool columns")
cols = [r[1] for r in ctx._db.conn.execute("PRAGMA table_info(entity_state)").fetchall()]
check("entity_state has bit_pool", "bit_pool" in cols)
check("entity_state has byte_pool", "byte_pool" in cols)

print("\n[7] DB round-trip on the 17-column entity_state INSERT")
conn = ctx._db.conn
conn.execute(
    "INSERT INTO entity_state "
    "(slot_id, entity_id, hp, x, y, cycles, mp, bit_pool, byte_pool, equipment, needs, "
    "chemicals, traits, memory, ai_state, ai_data, bag) "
    "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
    (9, "probe", 100, 1.0, 2.0, 80, 42, 7, 42, "{}", "{}", "{}", "{}", "{}", "IDLE", "{}", "[]"),
)
row = conn.execute("SELECT bit_pool, byte_pool FROM entity_state WHERE entity_id='probe'").fetchone()
check("round-trip bit_pool", row["bit_pool"] == 7)
check("round-trip byte_pool", row["byte_pool"] == 42)

print(f"\n{'='*50}")
print(f"  {passed} PASS  |  {failed} FAIL")
if failed:
    sys.exit(1)
print("  Phase 4.3 smoke CLEAN")
