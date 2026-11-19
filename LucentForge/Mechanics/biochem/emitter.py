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
from Mechanics.entities.derivation import fatigue_gain, strain_gain

# Active-exertion loci (needs/wants addendum §W6, Director Q1 2026-08-09). While the
# controller is in one of these AI states, effort accrues `fatigue`. SATISFYING and IDLE
# are neutral (fatigue only naturally decays) — EXCEPT satisfying at a sleep/bed source,
# which the emitter treats as the one restful locus (pulls fatigue toward 0). Eating/
# drinking is NOT exertion: the travel to food is already captured by MOVING.
EXERTING_STATES = frozenset({"MOVING", "RAIDING", "RELOCATING", "PATROLLING"})


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
        # Affinity strain — slow-building cost of sustained hostile exposure (§B7). Rate is the
        # entity's derived strain_gain (authored reference half-time × resilience); entities
        # without attributes (stubs) use the reference rate.
        # score >= 0 → strain_target = 0 → approach decays existing strain toward 0.
        strain_target = max(0.0, -score)
        attrs = getattr(entity, "attributes", None)
        gain = strain_gain(attrs) if attrs is not None else settings.STRAIN_REF_GAIN_PER_FRAME
        _approach(chemicals, "affinity_strain", strain_target, gain)
        return score


class ExertionEmitter:
    """Emits `fatigue` from the entity's current activity locus (needs/wants §W6).

    Mirrors AffinityComfortEmitter/§B7 strain precisely: samples a locus (the AI state)
    each tick and pushes a chemical toward a gain-controlled target. Exerting loci push
    fatigue up toward EXERTION_TARGET_MAX; resting at a bed pulls it toward 0; every other
    locus is neutral (the emitter leaves fatigue for Chemicals.tick natural decay).

    Accrual gain is attribute-derived (formula, not coefficient): a hardy NPC (high
    endurance) tires slower. Recomputed from CURRENT attributes every tick — never frozen.
    """

    def emit(self, chemicals, attrs, state: str, at_bed: bool) -> float:
        """Push `fatigue` toward the locus target for this tick.

        `attrs` — the entity's live Attributes (endurance recomputed each tick).
        `state` — the controller's current AI state (the locus).
        `at_bed` — True iff SATISFYING at a sleep/bed source (the one restful locus).
        Returns the current `fatigue` level for logging/observability.
        """
        effective_gain = fatigue_gain(attrs)
        if state in EXERTING_STATES:
            _approach(chemicals, "fatigue", settings.EXERTION_TARGET_MAX, effective_gain)
        elif at_bed:
            # Restful locus: actively pull fatigue toward 0 (on top of natural decay).
            _approach(chemicals, "fatigue", 0.0, effective_gain)
        # else: neutral locus (IDLE, or SATISFYING at a non-bed source) — natural decay
        # in Chemicals.tick handles relaxation; no active push.
        return chemicals.get("fatigue")
