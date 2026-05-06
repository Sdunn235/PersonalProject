# damage_resolver.py — Hit check and damage calculation
from __future__ import annotations
from Mechanics.combat import rules


class DamageResolver:
    """Handles hit/miss rolls and damage calculation."""

    def hit_check(self, att, defn, rng) -> bool:
        diff = att.stats.DEX - defn.stats.DEX
        pct = rules.HIT_BASE + diff * rules.HIT_PER_DEX_DIFF
        pct = max(rules.HIT_MIN, min(rules.HIT_MAX, pct))
        return rng.chance(pct)

    def damage_roll(self, att, defn, rng) -> tuple[int, bool]:
        use_mag = att.ability and att.ability.get("stat") == "MAG"
        base = att.stats.MAG if use_mag else att.stats.STR
        wep = att.weapon["atk"] if att.weapon else 0
        if use_mag:
            wep += att.weapon.get("mag", 0) if att.weapon else 0
        power = att.ability.get("power", 1.0) if att.ability else 1.0
        raw = int((base + wep) * power)
        spread = max(1, raw // 10)
        raw += rng.range_int(-spread, spread)
        crit_bonus = att.weapon.get("crit_bonus", 0) if att.weapon else 0
        crit_chance = min(rules.CRIT_CAP, att.stats.LCK + crit_bonus)
        was_crit = rng.chance(crit_chance)
        if was_crit:
            raw = int(raw * rules.CRIT_MULTIPLIER)
        elem = att.ability.get("element", "neutral") if att.ability else "neutral"
        mult = float(defn.resistances.get(elem, 1.0))
        raw = int(raw * mult)
        return rules.apply_damage_cap(max(1, raw - defn.stats.DEF)), was_crit
