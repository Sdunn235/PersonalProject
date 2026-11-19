# chemical.py — Dict-based chemical registry (Creatures-inspired)
# Extensible: chemicals keyed by need_id string, not hardcoded fields.
from __future__ import annotations
import settings


class Chemicals:
    """Dict-based chemical store. Each key is a chemical name (often matching need.chemical)."""

    _DECAY = 0.0002
    _SLEEP_DECAY = _DECAY * 5   # tiredness drop per frame while the sleep need is not urgent

    def __init__(self):
        # Need-driven chemicals (populated dynamically from need definitions)
        self._levels: dict[str, float] = {}
        # Reactive chemicals (still built-in)
        self._levels["pain"] = 0.0
        self._levels["fear"] = 0.0
        self._levels["anger"] = 0.0
        self._levels["loneliness"] = 0.0
        # Affinity comfort chemicals (biochem/affinity addendum §B4) — written by the
        # affinity comfort emitter; decay naturally like the other reactive chemicals.
        self._levels["comfort"] = 0.0
        self._levels["stress"] = 0.0
        # Slow-accumulating strain from sustained hostile-affinity exposure (§B7).
        # Boosts perceived urgency of survival needs; parity: strain=0 → no effect.
        self._levels["affinity_strain"] = 0.0
        # Activity-driven fatigue (needs/wants §W6) — written by the ExertionEmitter;
        # boosts ONLY the sleep chemical (`tiredness`). Parity: fatigue=0 → no effect.
        self._levels["fatigue"] = 0.0

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
                    self.set(chem_key, max(0.0, current - self._SLEEP_DECAY))
                else:
                    self.set(chem_key, current + (target - current) * 0.03)
            else:
                self.set(chem_key, current + (target - current) * 0.05)

        # Natural decay for reactive chemicals
        for key, decay_mult in [("pain", 1.0), ("fear", 1.0),
                                ("anger", 0.5), ("loneliness", 0.3),
                                ("comfort", 0.7), ("stress", 0.7)]:
            val = self.get(key)
            if val > 0:
                self.set(key, max(0.0, val - self._DECAY * decay_mult))
        # Fatigue and strain fade at DERIVED per-frame rates (settings: solved from authored
        # game-term targets, §W6.1 / §B7), not hand-set multipliers.
        for key, fade in (("fatigue", settings.FATIGUE_FADE_PER_FRAME),
                          ("affinity_strain", settings.STRAIN_FADE_PER_FRAME)):
            val = self.get(key)
            if val > 0:
                self.set(key, max(0.0, val - fade))

        # Affinity strain → perceived need urgency (§B7). Additive: strain=0 → no effect.
        strain = self.get("affinity_strain")
        if strain > settings.STRAIN_ACTIVE_FLOOR:
            boost = strain * settings.AFFINITY_STRAIN_BOOST_FRACTION * self._SLEEP_DECAY
            for need in needs:
                chem_key = getattr(need, "chemical", "") or need.need_id + "_chem"
                self.set(chem_key, min(1.0, self.get(chem_key) + boost))

        # Fatigue → perceived SLEEP urgency (needs/wants §W6). Unlike strain (which boosts
        # every survival chemical), fatigue is specifically about rest, so it boosts ONLY
        # `tiredness` (the sleep need's chemical). Additive with the strain boost above and
        # clamped by set() → no runaway. Parity: fatigue=0 → no effect.
        #
        # ORDERING NOTE (QC major): `tiredness` has a dedicated sleep-decay branch in the
        # need loop above (hard-decays at _SLEEP_DECAY while NOT urgent, i.e. sleeping).
        # This boost runs AFTER that branch, so it ADDS back. It is expressed as a FRACTION of
        # _SLEEP_DECAY (settings.FATIGUE_TIREDNESS_BOOST_FRACTION); keeping that fraction plus
        # strain's share below 1 is what guarantees a sleeping, fatigued NPC still nets
        # `tiredness` DOWNWARD (asserted in run_fatigue_tests.py §3).
        fatigue = self.get("fatigue")
        if fatigue > settings.FATIGUE_ACTIVE_FLOOR:
            self.set("tiredness", min(1.0, self.get("tiredness")
                                      + fatigue * settings.FATIGUE_TIREDNESS_BOOST_FRACTION
                                      * self._SLEEP_DECAY))

    def add_pain(self, amount: float) -> None:
        self.set("pain", min(1.0, self.get("pain") + amount))

    def add_fear(self, amount: float) -> None:
        self.set("fear", min(1.0, self.get("fear") + amount))

    def as_dict(self) -> dict:
        return {k: round(v, 3) for k, v in sorted(self._levels.items())}
