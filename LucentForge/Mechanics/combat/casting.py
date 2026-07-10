# casting.py — Bit/Byte spell typing + formula-derived costs (§M4).
#
# A spell's magic_kind (BIT | BYTE) selects which pool it spends; its cost is
# derived from power (heals use amount_pct * HEAL_POWER_SCALE as pseudo-power)
# times a per-pool knob. One dial per pool, not per-spell tuning (§M4 / formulas).
from __future__ import annotations
import settings
from Mechanics.entities.derivation import BITS_PER_BYTE


def convert_amount(bits: int, bytes_cur: int, bytes_max: int,
                   rate_bits: int) -> tuple[int, int, int]:
    """Convert up to rate_bits Bits into Bytes at the canonical 8:1 (§M4, §M6.5).

    Capped by available Bits and remaining Byte headroom. Returns
    (bits_after, bytes_after, bytes_gained). Deterministic this stage — overburn
    (risky in-combat conversion) is a disabled hook (4.6+/Stage 5).
    """
    byte_room   = max(0, bytes_max - bytes_cur)
    convertible = min(rate_bits, bits, byte_room * BITS_PER_BYTE)
    gained      = convertible // BITS_PER_BYTE
    spent       = gained * BITS_PER_BYTE
    return bits - spent, bytes_cur + gained, gained


def spell_pool_and_cost(ability: dict) -> tuple[str, int]:
    """Return (pool, cost) where pool is 'bit' or 'byte'.

    Bit-spells (primal/direct) spend the Bit pool; Byte-spells (structured) spend the
    Byte pool. Untyped entries (basic attacks, stamina abilities) return ('byte', 0) —
    they cost no magic pool.
    """
    kind = str(ability.get("magic_kind", "")).upper()
    if kind not in ("BIT", "BYTE"):
        return "byte", 0

    power = ability.get("power")
    if power is None:  # heals carry amount_pct instead of power
        power = ability.get("amount_pct", 0.0) * settings.HEAL_POWER_SCALE

    if kind == "BIT":
        return "bit", max(1, round(power * settings.BIT_COST_PER_POWER))
    return "byte", max(1, round(power * settings.BYTE_COST_PER_POWER))
