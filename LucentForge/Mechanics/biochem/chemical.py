# chemical.py — Dict-based chemical registry (Creatures-inspired)
# Extensible: chemicals keyed by need_id string, not hardcoded fields.
from __future__ import annotations


class Chemicals:
    """Dict-based chemical store. Each key is a chemical name (often matching need.chemical)."""

    _DECAY = 0.0002

    def __init__(self):
        # Need-driven chemicals (populated dynamically from need definitions)
        self._levels: dict[str, float] = {}
        # Reactive chemicals (still built-in)
        self._levels["pain"] = 0.0
        self._levels["fear"] = 0.0
        self._levels["anger"] = 0.0
        self._levels["loneliness"] = 0.0

    def get(self, key: str) -> float:
        return self._levels.get(key, 0.0)

    def set(self, key: str, value: float) -> None:
        self._levels[key] = max(0.0, min(1.0, value))

    def tick(self, needs: list) -> None:
        """Update chemicals from current need states and apply natural decay."""
        for need in needs:
            chem_key = getattr(need, "chemical", "") or need.need_id + "_chem"
            target = max(0.0, 1.0 - need.current_value / 100.0)
            current = self.get(chem_key)

            if need.need_id == "sleep":
                if not need.is_urgent:
                    self.set(chem_key, max(0.0, current - self._DECAY * 5))
                else:
                    self.set(chem_key, current + (target - current) * 0.03)
            else:
                self.set(chem_key, current + (target - current) * 0.05)

        # Natural decay for reactive chemicals
        for key, decay_mult in [("pain", 1.0), ("fear", 1.0),
                                ("anger", 0.5), ("loneliness", 0.3)]:
            val = self.get(key)
            if val > 0:
                self.set(key, max(0.0, val - self._DECAY * decay_mult))

    def add_pain(self, amount: float) -> None:
        self.set("pain", min(1.0, self.get("pain") + amount))

    def add_fear(self, amount: float) -> None:
        self.set("fear", min(1.0, self.get("fear") + amount))

    def as_dict(self) -> dict:
        return {k: round(v, 3) for k, v in sorted(self._levels.items())}
