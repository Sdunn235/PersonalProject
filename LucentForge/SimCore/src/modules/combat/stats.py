from dataclasses import dataclass, field

def clamp(v, lo, hi): return lo if v < lo else hi if v > hi else v
def u16(v: int) -> int: return v & 0xFFFF  # wrap helper if you want it
def u32(v: int) -> int: return v & 0xFFFFFFFF

@dataclass
class StatusFlags:
    bits: int = 0
    def set(self, i: int):   self.bits |= (1 << i)
    def clear(self, i: int): self.bits &= ~(1 << i)
    def has(self, i: int) -> bool: return (self.bits >> i) & 1 == 1

@dataclass
class Stats:
    # Player-visible base stats (16-bit flavor)
    STR: int = 10
    MAG: int = 0
    LCK: int = 5
    DEF: int = 5
    RES: int = 0
    DEX: int = 5
    # Internal headroom (32-bit math)
    clamp_mode: str = "clamp"  # "clamp" or "wrap"
    status: StatusFlags = field(default_factory=StatusFlags)

    def add_str(self, delta: int):
        v = self.STR + delta
        if self.clamp_mode == "wrap":
            self.STR = u16(v)
        else:
            self.STR = clamp(v, 0, 65535)

    # same pattern for MAG/LCK/DEF/RES if needed
