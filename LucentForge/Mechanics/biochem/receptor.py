"""receptor.py — chemical → perceived-need receptors (needs/wants addendum §W6).

NPC decisions (IdleState, goblin behavior, patrol/relocate/raid exits) read need ZONES, not
chemicals. A receptor here turns a chemical level into a `perceived_pull` on a need, so the
chemical changes *what the NPC decides*, not just what the HUD shows.

First receptor: fatigue → sleep. A worn-out NPC perceives its sleep need as lower than it is
and crosses the sleep WARNING line sooner. Parity: fatigue at/below the dead-band → pull 0.
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


def apply_perceived_pulls(needs: list, chemicals) -> None:
    """Write this frame's perceived pulls onto the owner's needs (all others reset to 0)."""
    for need in needs:
        need.perceived_pull = (fatigue_sleep_pull(chemicals, need)
                               if need.need_id == FATIGUE_TARGET_NEED else 0.0)
