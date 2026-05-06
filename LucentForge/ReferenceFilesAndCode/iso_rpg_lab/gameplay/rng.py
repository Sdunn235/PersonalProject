class RNG32:
    # Simple LCG: deterministic + fast for sims (not crypto)
    def __init__(self, seed: int = 123456789):
        self.state = seed & 0xFFFFFFFF

    def next_u32(self) -> int:
        self.state = (1664525 * self.state + 1013904223) & 0xFFFFFFFF
        return self.state

    def range_int(self, lo: int, hi: int) -> int:
        # inclusive lo..hi
        r = self.next_u32() / 0x100000000
        return lo + int(r * (hi - lo + 1))

    def chance(self, percent: float) -> bool:
        return self.range_int(0, 9999) < int(percent * 100)
