# abilities.py — Stat derivation (BaseStats, FlatMods, Effect, derive_stats)
# Legacy load_abilities/load_items removed — use GameContext instead.
from __future__ import annotations
from dataclasses import dataclass, field
from Mechanics.entities.stats import Stats, StatusFlags


@dataclass
class BaseStats:
    VIT: int = 20; STR: int = 20; DEX: int = 8
    MAG: int = 0;  WIS: int = 0;  LCK: int = 8


@dataclass
class FlatMods:
    STR: int = 0; DEX: int = 0; MAG: int = 0
    WIS: int = 0; LCK: int = 0; DEF: int = 0; RES: int = 0


@dataclass
class Effect:
    flat: FlatMods
    duration: int   # rounds remaining


def derive_stats(base: BaseStats, gear_mods: list[FlatMods],
                 effects: list[Effect], mode: str = "clamp") -> Stats:
    from Mechanics.entities.stats import clamp, u16
    STR = base.STR; DEX = base.DEX; MAG = base.MAG
    WIS = base.WIS; LCK = base.LCK; DEF = 0; RES = 0
    for g in gear_mods:
        STR += g.STR; DEX += g.DEX; MAG += g.MAG
        WIS += g.WIS; LCK += g.LCK; DEF += g.DEF; RES += g.RES
    for e in effects:
        STR += e.flat.STR; DEX += e.flat.DEX; MAG += e.flat.MAG
        WIS += e.flat.WIS; LCK += e.flat.LCK; DEF += e.flat.DEF; RES += e.flat.RES
    cap = (lambda v: max(0, min(65535, v))) if mode == "clamp" else (lambda v: u16(v))
    return Stats(STR=cap(STR), MAG=cap(MAG), LCK=cap(LCK),
                 DEF=cap(DEF), RES=cap(RES), DEX=cap(DEX), clamp_mode=mode)


