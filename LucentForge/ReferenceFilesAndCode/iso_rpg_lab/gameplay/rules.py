# gameplay/rules.py
# Global tuning knobs you can change without touching formulas.

# Max damage shown/applied per hit (classic JRPG vibe)
DAMAGE_CAP = 99_999
DAMAGE_CAP_MODE = "clamp"  # "clamp" or "wrap"

# Hit chance baseline & scaling (simple, readable)
HIT_BASE = 88          # %
HIT_PER_DEX_DIFF = 1   # % per point (att.DEX - def.DEX)
HIT_MIN = 50           # %
HIT_MAX = 98           # %

# When to use a healing item (fraction of max HP)
ITEM_HEAL_THRESHOLD = 0.50    
HEAL_MIN_EFFICIENCY = 0.60     # only heal if missing_hp >= 60% of heal amount

ENEMY_ITEM_HEAL_THRESHOLD = 0.35      # enemies heal later
ENEMY_HEAL_MIN_EFFICIENCY = 0.70      # and only when it’s really worth it

# Cooldown & per-battle cap
HEAL_COOLDOWN_ROUNDS = 2        # lock healing actions for 2 rounds after a heal
HEAL_MAX_PER_BATTLE   = 2       # each unit can heal at most 2 times per battle

# Ability economy
CYCLE_MAX_DEFAULT     = 100     # default MP
CYCLE_REGEN_PER_TURN  = 5       # regen each turn

def apply_damage_cap(dmg: int) -> int:
    if dmg < 0:
        return 0
    if DAMAGE_CAP_MODE == "wrap":
        return dmg % (DAMAGE_CAP + 1)
    # default clamp
    return min(dmg, DAMAGE_CAP)
