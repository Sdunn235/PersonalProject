"""receptor.py — chemical → perceived-need receptors (needs/wants addendum §W6).

NPC decisions (IdleState, goblin behavior, patrol/relocate/raid exits) read need ZONES, not
chemicals. A receptor here turns a chemical level into a `perceived_pull` on a need, so the
chemical changes *what the NPC decides*, not just what the HUD shows.

First receptor: fatigue → sleep. A worn-out NPC perceives its sleep need as lower than it is
and crosses the sleep WARNING line sooner. Parity: fatigue at/below the dead-band → pull 0.
"""
from __future__ import annotations

import settings

# need_id the fatigue receptor targets (the sleep need; its chemical is `tiredness`).
FATIGUE_TARGET_NEED = "sleep"


def fatigue_sleep_pull(chemicals) -> float:
    """Need-points of perceived sleep loss for the current fatigue level."""
    fatigue = chemicals.get("fatigue")
    if fatigue <= settings.FATIGUE_ACTIVE_FLOOR:
        return 0.0
    return fatigue * settings.FATIGUE_SLEEP_PULL


def apply_perceived_pulls(needs: list, chemicals) -> None:
    """Write this frame's perceived pulls onto the owner's needs (all others reset to 0)."""
    sleep_pull = fatigue_sleep_pull(chemicals)
    for need in needs:
        need.perceived_pull = sleep_pull if need.need_id == FATIGUE_TARGET_NEED else 0.0
