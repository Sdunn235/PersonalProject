# fighter.py — Fighter composition: Identity + Loadout + State
# Replaces the monolithic Fighter from combat.py
from __future__ import annotations
from dataclasses import dataclass, field
from Mechanics.entities.stats import Stats
from Mechanics.combat import rules
from Mechanics.combat.abilities import BaseStats, FlatMods, Effect, derive_stats


@dataclass
class InvStack:
    item: dict
    qty: int = 1


@dataclass
class CombatIdentity:
    """Who this fighter is — immutable during combat."""
    name: str
    is_enemy: bool = False
    resistances: dict = field(default_factory=lambda: {"neutral": 1.0})


@dataclass
class CombatLoadout:
    """What this fighter has equipped — set at combat start."""
    weapon: dict | None = None
    abilities: list[dict] | None = None
    spells: list[dict] | None = None
    bag: list[InvStack] = field(default_factory=list)
    base: BaseStats = field(default_factory=BaseStats)
    gear_mods: list[FlatMods] = field(default_factory=list)


@dataclass
class CombatState:
    """Mutable combat state — changes every turn."""
    hp: int = 0
    max_hp: int = 0
    cycles: int = rules.CYCLE_MAX_DEFAULT
    max_cycles: int = rules.CYCLE_MAX_DEFAULT
    mp: int = 0
    max_mp: int = 0
    cooldowns: dict = field(default_factory=dict)
    heals_used: int = 0
    effects: list[Effect] = field(default_factory=list)
    cycle_regen: int = rules.CYCLE_REGEN_PER_TURN


@dataclass
class Fighter:
    """Composed fighter — delegates to Identity, Loadout, State."""
    identity: CombatIdentity
    loadout: CombatLoadout
    state: CombatState
    stats: Stats = field(default_factory=Stats)
    ability: dict | None = None   # current ability being used this turn

    def __post_init__(self):
        if self.state.max_hp <= 0:
            self.state.max_hp = self.state.hp
        if self.state.max_mp <= 0:
            self.state.max_mp = rules.MP_MAX_DEFAULT
            self.state.mp = self.state.max_mp

    # --- Convenience properties for backward compatibility ---
    @property
    def name(self) -> str: return self.identity.name
    @property
    def is_enemy(self) -> bool: return self.identity.is_enemy
    @property
    def resistances(self) -> dict: return self.identity.resistances
    @property
    def weapon(self) -> dict | None: return self.loadout.weapon
    @weapon.setter
    def weapon(self, v): self.loadout.weapon = v
    @property
    def abilities(self) -> list[dict] | None: return self.loadout.abilities
    @abilities.setter
    def abilities(self, v): self.loadout.abilities = v
    @property
    def spells(self) -> list[dict] | None: return self.loadout.spells
    @spells.setter
    def spells(self, v): self.loadout.spells = v
    @property
    def bag(self) -> list[InvStack]: return self.loadout.bag
    @bag.setter
    def bag(self, v): self.loadout.bag = v
    @property
    def base(self) -> BaseStats: return self.loadout.base
    @property
    def gear_mods(self) -> list[FlatMods]: return self.loadout.gear_mods
    @property
    def hp(self) -> int: return self.state.hp
    @hp.setter
    def hp(self, v): self.state.hp = v
    @property
    def max_hp(self) -> int: return self.state.max_hp
    @max_hp.setter
    def max_hp(self, v): self.state.max_hp = v
    @property
    def cycles(self) -> int: return self.state.cycles
    @cycles.setter
    def cycles(self, v): self.state.cycles = v
    @property
    def max_cycles(self) -> int: return self.state.max_cycles
    @max_cycles.setter
    def max_cycles(self, v): self.state.max_cycles = v
    @property
    def mp(self) -> int: return self.state.mp
    @mp.setter
    def mp(self, v): self.state.mp = v
    @property
    def max_mp(self) -> int: return self.state.max_mp
    @max_mp.setter
    def max_mp(self, v): self.state.max_mp = v
    @property
    def cooldowns(self) -> dict: return self.state.cooldowns
    @property
    def heals_used(self) -> int: return self.state.heals_used
    @heals_used.setter
    def heals_used(self, v): self.state.heals_used = v
    @property
    def effects(self) -> list[Effect]: return self.state.effects
    @property
    def cycle_regen(self) -> int: return self.state.cycle_regen

    def refresh_stats(self):
        self.stats = derive_stats(self.base, self.gear_mods, self.effects,
                                  mode=self.stats.clamp_mode)

    def tick_cooldowns(self):
        for k in list(self.cooldowns):
            self.cooldowns[k] = max(0, self.cooldowns[k] - 1)
            if self.cooldowns[k] == 0:
                del self.cooldowns[k]


def build_fighter(name: str, hp: int, stats: Stats, *,
                  is_enemy: bool = False, max_hp: int = 0,
                  cycles: int = 0, max_cycles: int = 0,
                  mp: int = 0, max_mp: int = 0,
                  resistances: dict | None = None) -> Fighter:
    """Factory function to build a Fighter from flat parameters."""
    return Fighter(
        identity=CombatIdentity(
            name=name, is_enemy=is_enemy,
            resistances=resistances or {"neutral": 1.0},
        ),
        loadout=CombatLoadout(),
        state=CombatState(
            hp=hp, max_hp=max_hp or hp,
            cycles=cycles or rules.CYCLE_MAX_DEFAULT,
            max_cycles=max_cycles or rules.CYCLE_MAX_DEFAULT,
            mp=mp, max_mp=max_mp,
        ),
        stats=stats,
    )
