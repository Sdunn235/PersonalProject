"""Phase 2.4 damage parity test — run before and after the stat-derivation swap.

Usage (from LucentForge root):
    py scratchpad/test_combat_parity.py

Unarmored avg must match within ±1 pre- and post-swap.
Armored avg must be LOWER than unarmored avg after Phase 2.4.
"""
import random
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Mechanics.combat.abilities import BaseStats, FlatMods, derive_stats
from Mechanics.combat.fighter import build_fighter
from Mechanics.combat.damage_resolver import DamageResolver
from Mechanics.combat.rng import SimpleRng
from Mechanics.entities.stats import Stats

N = 20
SEED = 42

resolver = DamageResolver()


def _make_fighter(name: str, base: BaseStats, weapon: dict | None,
                  gear_mods: list | None = None) -> object:
    stats = derive_stats(base, gear_mods or [], [])
    f = build_fighter(name=name, hp=100, max_hp=100, stats=stats)
    f.weapon = weapon
    f.loadout.gear_mods = gear_mods or []
    return f


def run_trial(att, defn, n: int, seed: int) -> float:
    random.seed(seed)
    rng = SimpleRng()
    total = 0
    for _ in range(n):
        dmg, _ = resolver.damage_roll(att, defn, rng)
        total += dmg
    return total / n


# --- Baseline stats ---
base = BaseStats(VIT=20, STR=20, DEX=8, MAG=0, WIS=0, LCK=8)
iron_sword = {"id": "iron_sword", "name": "Iron Sword", "atk": 8}

# Unarmored matchup (no gear)
att   = _make_fighter("Attacker", base, iron_sword)
defn  = _make_fighter("Defender", base, None)
avg_unarmored = run_trial(att, defn, N, SEED)
print(f"Unarmored avg ({N} rounds, seed={SEED}): {avg_unarmored:.2f}")

# Armored matchup (defender has armor DEF via gear_mods)
armor_gear = [FlatMods(DEF=10)]
att_a  = _make_fighter("Attacker", base, iron_sword)
defn_a = _make_fighter("Armored Defender", base, None, gear_mods=armor_gear)
avg_armored = run_trial(att_a, defn_a, N, SEED)
print(f"Armored  avg ({N} rounds, seed={SEED}): {avg_armored:.2f}  (DEF=10)")

if avg_armored < avg_unarmored:
    print("PASS — armor is reducing damage.")
else:
    print("FAIL — armor not reducing damage. Check gear_mods wiring.")
