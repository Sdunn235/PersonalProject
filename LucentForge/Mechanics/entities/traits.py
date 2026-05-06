# traits.py — Personality trait weights (0.0 – 1.0)
# Heartbeat-3 adds drift() and decay_toward_neutral() for earned personality.
from dataclasses import dataclass
import settings


_AXES = ("curiosity", "aggression", "fearfulness", "sociability")


@dataclass
class Traits:
    curiosity:    float = 0.5   # willingness to explore vs stay near known sources
    aggression:   float = 0.3   # likelihood to engage in combat unprovoked
    fearfulness:  float = 0.3   # urgency multiplier when pain/fear chemicals are high
    sociability:  float = 0.5   # desire for company; amplifies loneliness drive

    def drift(self, axis: str, amount: float) -> None:
        """Shift a trait axis by amount, clamped to [TRAIT_MIN, TRAIT_MAX]."""
        current = getattr(self, axis)
        new_val = max(settings.TRAIT_MIN, min(settings.TRAIT_MAX, current + amount))
        setattr(self, axis, new_val)

    def decay_toward_neutral(self) -> None:
        """Slowly pull all traits toward 0.5 to prevent runaway drift."""
        rate = settings.TRAIT_DECAY_RATE
        for axis in _AXES:
            current = getattr(self, axis)
            delta = (0.5 - current) * rate
            setattr(self, axis, current + delta)

    def as_dict(self) -> dict:
        return {
            "curiosity":   self.curiosity,
            "aggression":  self.aggression,
            "fearfulness": self.fearfulness,
            "sociability": self.sociability,
        }
