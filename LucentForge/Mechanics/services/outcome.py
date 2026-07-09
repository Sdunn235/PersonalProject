from __future__ import annotations
import random
from dataclasses import dataclass
from enum import IntEnum

import settings


class Degree(IntEnum):
    CRITICAL_FAILURE = 0
    FAILURE          = 1
    SUCCESS          = 2
    CRITICAL_SUCCESS = 3


@dataclass(frozen=True)
class OutcomeCheck:
    base_value:  int
    difficulty:  int
    skill:       int = 0
    attributes:  int = 0   # pre-computed via attribute_term()
    context:     int = 0


@dataclass(frozen=True)
class OutcomeResult:
    success:  bool
    degree:   Degree
    score:    int
    margin:   int
    variance: int


def attribute_term(attributes, attr_name: str) -> int:
    """§12.2 attribute term for outcome checks (§M2).

    Stage 4: reads real Attributes objects (the shim is retired — see §A5 / §M2).
    `attributes` is a Mechanics.entities.attributes.Attributes instance.
    """
    val = {
        "physique":     attributes.physique,
        "reflexes":     attributes.reflexes,
        "constitution": attributes.constitution,
        "intellect":    attributes.intellect,
        "intuition":    attributes.intuition,
        "linguistic":   attributes.linguistic,
        "luck":         attributes.luck,
    }.get(attr_name.lower(), 0)
    return val * settings.ATTR_SCALE


class OutcomeResolver:
    """§12.2 bounded-variance outcome check engine.

    Pass rng=random.Random(seed).randint for deterministic tests.
    """

    def __init__(self, rng=None):
        self._rng = rng or random.randint

    def resolve(self, check: OutcomeCheck) -> OutcomeResult:
        deterministic = (check.base_value + check.skill
                         + check.attributes + check.context)
        det_margin = deterministic - check.difficulty

        # §12.2: overwhelming advantage/disadvantage cannot be flipped by variance
        if abs(det_margin) > settings.OUTCOME_VARIANCE_MAX:
            variance = 0
        else:
            variance = self._rng(-settings.OUTCOME_VARIANCE_MAX,
                                  settings.OUTCOME_VARIANCE_MAX)

        score  = deterministic + variance
        margin = score - check.difficulty

        if margin >= settings.OUTCOME_CRIT_MARGIN:
            degree = Degree.CRITICAL_SUCCESS
        elif margin >= 0:
            degree = Degree.SUCCESS
        elif margin <= -settings.OUTCOME_CRIT_MARGIN:
            degree = Degree.CRITICAL_FAILURE
        else:
            degree = Degree.FAILURE

        return OutcomeResult(success=margin >= 0, degree=degree,
                             score=score, margin=margin, variance=variance)
