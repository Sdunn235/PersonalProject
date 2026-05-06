# interpreter.py — Outcome quality scoring (Heartbeat-3)
# After an NPC satisfies a need, this scores how well it went (0.0-1.0).
from __future__ import annotations
from Mechanics.needs.need import NeedZone
from Mechanics.entities.traits import Traits
import settings


def interpret_outcome(need_zone_at_decision: NeedZone,
                      distance_traveled: float,
                      was_interrupted: bool,
                      traits: Traits) -> float:
    """Score a completed need-satisfaction from 0.0 (terrible) to 1.0 (ideal)."""
    base = 0.7

    # Zone penalty/bonus — how urgent was the need when we decided to act?
    if need_zone_at_decision == NeedZone.CRITICAL:
        base -= 0.3
    elif need_zone_at_decision == NeedZone.FINE:
        base += 0.1

    # Distance penalty — farther sources reduce quality
    max_dist = settings.MAX_MAP_DISTANCE
    if max_dist > 0:
        distance_penalty = min(0.3, distance_traveled / max_dist * 0.3)
        base -= distance_penalty

    # Interruption penalty — getting re-routed mid-path is a bad sign
    if was_interrupted:
        base -= 0.2

    # Trait filters
    # Fearful NPCs remember bad outcomes as slightly worse
    base -= traits.fearfulness * 0.1 * max(0.0, 0.7 - base)
    # Curious NPCs shrug off bad outcomes slightly
    base += traits.curiosity * 0.05 * max(0.0, 0.7 - base)

    return max(0.0, min(1.0, base))
