# casting.py — Bit/Byte spell typing + formula-derived costs (§M4).
#
# A spell's magic_kind (BIT | BYTE) selects which pool it spends; its cost is
# derived from power (heals use amount_pct * HEAL_POWER_SCALE as pseudo-power)
# times a per-pool knob. One dial per pool, not per-spell tuning (§M4 / formulas).
from __future__ import annotations
import settings


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
