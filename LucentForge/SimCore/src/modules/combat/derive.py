# gameplay/derive.py
from dataclasses import dataclass
from .stats import Stats, clamp, u16

@dataclass
class BaseStats:
    VIT:int=20; STR:int=20; DEX:int=8; MAG:int=0; WIS:int=0; LCK:int=8

@dataclass
class FlatMods:
    STR:int=0; DEX:int=0; MAG:int=0; WIS:int=0; LCK:int=0; DEF:int=0; RES:int=0

@dataclass
class Effect:  # simple timed buff/debuff
    flat: FlatMods
    duration: int  # in rounds; reduce elsewhere

def derive_stats(base: BaseStats, gear_mods: list[FlatMods], effects: list[Effect], mode="clamp") -> Stats:
    STR = base.STR; DEX = base.DEX; MAG = base.MAG; WIS = base.WIS; LCK = base.LCK
    DEF = 0; RES = 0

    # add gear flats
    for g in gear_mods:
        STR += g.STR; DEX += g.DEX; MAG += g.MAG; WIS += g.WIS; LCK += g.LCK
        DEF += g.DEF; RES += g.RES

    # add active effects
    for e in effects:
        STR += e.flat.STR; DEX += e.flat.DEX; MAG += e.flat.MAG; WIS += e.flat.WIS; LCK += e.flat.LCK
        DEF += e.flat.DEF; RES += e.flat.RES

    # cap/wrap behavior delegated to Stats later; we clamp here for safety
    def cap(v): return max(0, min(65535, v)) if mode=="clamp" else u16(v)
    return Stats(STR=cap(STR), MAG=cap(MAG), LCK=cap(LCK), DEF=cap(DEF), RES=cap(RES), DEX=cap(DEX), clamp_mode=mode)
