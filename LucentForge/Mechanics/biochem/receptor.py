"""receptor.py — chemical → perceived-need receptors (needs/wants addendum §W6).

NPC decisions (IdleState, goblin behavior, patrol/relocate/raid exits) read need ZONES, not
chemicals. A receptor here turns a chemical level into a `perceived_pull` on a need, so the
chemical changes *what the NPC decides*, not just what the HUD shows.

Receptors: fatigue → sleep (a worn-out NPC beds down sooner) and affinity strain → every survival
need (a body taxed by hostile ground feels hunger, thirst and sleep sooner; fearful NPCs feel it
more). Pulls are fractions of each need's band and are capped together. Parity: chemicals at/below
their dead-bands → pull 0.

Interim bridge: biochem §B1 intends that the strongest drive decides (BACKLOG LF-043).
"""
from __future__ import annotations

import settings
from Mechanics.needs.need import NEED_FULL

# need_id the fatigue receptor targets (the sleep need; its chemical is `tiredness`).
FATIGUE_TARGET_NEED = "sleep"


def comfort_band(need) -> float:
    """Need-points between full and the need's WARNING line (authored per need in needs.json).
    Pulls are fractions of this band, so a fraction < 1 can never drag a full need into WARNING."""
    return max(0.0, NEED_FULL - need.warning_threshold)


def fatigue_sleep_pull(chemicals, need) -> float:
    """Need-points of perceived sleep loss: fatigue × FATIGUE_PULL_FRACTION of the sleep band."""
    fatigue = chemicals.get("fatigue")
    if fatigue <= settings.FATIGUE_ACTIVE_FLOOR:
        return 0.0
    return fatigue * settings.FATIGUE_PULL_FRACTION * comfort_band(need)


def strain_need_pull(chemicals, need, traits=None) -> float:
    """Need-points of perceived loss on any survival need from affinity strain (biochem §B7):
    strain × STRAIN_PULL_FRACTION × band, scaled up by fearfulness (the NPC's fear sensitivity)."""
    strain = chemicals.get("affinity_strain")
    if strain <= settings.STRAIN_ACTIVE_FLOOR:
        return 0.0
    fear = traits.fearfulness if traits is not None else 0.0
    felt = 1.0 + fear * settings.STRAIN_FEAR_WEIGHT
    return strain * settings.STRAIN_PULL_FRACTION * felt * comfort_band(need)


def apply_perceived_pulls(needs: list, chemicals, traits=None) -> None:
    """Write this frame's perceived pull onto each of the owner's needs.

    Pulls from every receptor are summed, then capped at PULL_CAP_FRACTION of the need's band (< 1),
    so no combination of pressures can make a just-satisfied need feel like WARNING."""
    for need in needs:
        total = strain_need_pull(chemicals, need, traits)
        if need.need_id == FATIGUE_TARGET_NEED:
            total += fatigue_sleep_pull(chemicals, need)
        need.perceived_pull = min(total, settings.PULL_CAP_FRACTION * comfort_band(need))
