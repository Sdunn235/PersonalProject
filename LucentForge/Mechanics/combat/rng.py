# rng.py — Thin random wrapper satisfying the combat engine's rng interface
import random


class SimpleRng:
    def chance(self, pct: float) -> bool:
        """Return True with probability pct (0-100)."""
        return random.random() * 100 < pct

    def range_int(self, lo: int, hi: int) -> int:
        """Return a random int in [lo, hi] inclusive."""
        return random.randint(lo, hi)
