# emitter.py — Creatures-style biochem emitters (biochem/affinity addendum §B2).
#
# An emitter samples a locus (a world/body/relationship state) each tick and pushes a
# chemical toward a target concentration, gain-controlled. This is the missing half of
# the Creatures emitter/receptor model — `Drive.compute_urgency` is already the receptor.
#
# Kept intentionally minimal: affinity comfort is the first (and, this phase, only)
# emitter. The legacy ad-hoc injectors (proximity fear, zone_ai anger/fear) will be
# re-expressed as emitters in a later parity-gated phase — do NOT grow a manager forest.
from __future__ import annotations

import settings
from Mechanics.entities.affinity import comfort_score


def _approach(chemicals, key: str, target: float, gain: float) -> None:
    """Move a chemical a `gain` fraction toward `target` (clamped by Chemicals.set)."""
    cur = chemicals.get(key)
    chemicals.set(key, cur + (target - cur) * gain)


class AffinityComfortEmitter:
    """Emits `comfort`/`stress` from the affinity match between an entity and the region
    it currently occupies (the Grace lattice). Samples the locus (current room) each tick.

    Positive comfort_score → drives `comfort` up (and lets `stress` relax); negative →
    drives `stress` up. A neutral entity or neutral region yields score 0 → both relax.
    """

    def __init__(self, comfort_gain: float = 0.05, stress_gain: float = 0.05) -> None:
        self.comfort_gain = comfort_gain
        self.stress_gain = stress_gain

    def emit(self, chemicals, entity, room) -> float:
        """Push comfort/stress toward the current affinity-comfort target.

        `room` is the RoomDefinition the entity currently occupies (or None = neutral
        ground). Returns the raw comfort_score in [-1, +1] for logging/observability.
        """
        if room is None:
            score = 0.0
        else:
            score = comfort_score(entity.affinity.effective(),
                                  room.affinity, room.affinity_intensity)
        comfort_target = max(0.0, score)    # positive part
        stress_target  = max(0.0, -score)   # negative part
        _approach(chemicals, "comfort", comfort_target, self.comfort_gain)
        _approach(chemicals, "stress",  stress_target,  self.stress_gain)
        # Affinity strain — slow-building cost of sustained hostile exposure (§B7).
        # Approaches the same magnitude as stress but 167× slower (0.0003 vs 0.05).
        # score >= 0 → strain_target = 0 → approach decays existing strain toward 0.
        strain_target = max(0.0, -score)
        _approach(chemicals, "affinity_strain", strain_target, settings.AFFINITY_STRAIN_GAIN)
        return score
