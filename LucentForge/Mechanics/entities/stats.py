# stats.py — Combat stats dataclass
from dataclasses import dataclass, field


def clamp(v, lo, hi):
    return lo if v < lo else hi if v > hi else v


def u16(v: int) -> int:
    return v & 0xFFFF


@dataclass
class StatusFlags:
    bits: int = 0

    def set(self, i: int):        self.bits |= (1 << i)
    def clear(self, i: int):      self.bits &= ~(1 << i)
    def has(self, i: int) -> bool: return (self.bits >> i) & 1 == 1


@dataclass
class Stats:
    STR: int = 10
    MAG: int = 0
    LCK: int = 5
    DEF: int = 5
    RES: int = 0
    DEX: int = 5
    clamp_mode: str = "clamp"
    status: StatusFlags = field(default_factory=StatusFlags)

    def add(self, attr: str, delta: int):
        v = getattr(self, attr) + delta
        if self.clamp_mode == "wrap":
            setattr(self, attr, u16(v))
        else:
            setattr(self, attr, clamp(v, 0, 65535))
