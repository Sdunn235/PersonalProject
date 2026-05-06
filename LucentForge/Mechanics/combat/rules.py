# rules.py — Combat tuning constants
# Ported from iso_rpg_lab/gameplay/rules.py

DAMAGE_CAP      = 99_999
DAMAGE_CAP_MODE = "clamp"   # "clamp" or "wrap"

HIT_BASE        = 88        # base hit chance %
HIT_PER_DEX_DIFF = 1        # % per point (attacker.DEX - defender.DEX)
HIT_MIN         = 50
HIT_MAX         = 98

ITEM_HEAL_THRESHOLD       = 0.50
HEAL_MIN_EFFICIENCY       = 0.60
ENEMY_ITEM_HEAL_THRESHOLD = 0.35
ENEMY_HEAL_MIN_EFFICIENCY = 0.70

HEAL_COOLDOWN_ROUNDS = 2
HEAL_MAX_PER_BATTLE  = 2

CYCLE_MAX_DEFAULT    = 100
CYCLE_REGEN_PER_TURN = 5

MP_MAX_DEFAULT    = 50
MP_REGEN_PER_TURN = 3

CRIT_MULTIPLIER   = 1.5
CRIT_CAP          = 60.0
POISON_TICK_PCT   = 0.02


def apply_damage_cap(dmg: int) -> int:
    if dmg < 0:
        return 0
    if DAMAGE_CAP_MODE == "wrap":
        return dmg % (DAMAGE_CAP + 1)
    return min(dmg, DAMAGE_CAP)
