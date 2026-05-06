# behavior.py — Faction behavior strategies (Heartbeat-4)
#
# BehaviorStrategy defines how an NPC decides what to do when idle.
# HumanBehavior uses the default need-satisfaction loop.
# GoblinBehavior reads the shared GoblinThreat to pick patrol/raid states.
from __future__ import annotations
from abc import ABC, abstractmethod

from Mechanics.world.goblin_threat import GoblinThreat, ThreatStage


class BehaviorStrategy(ABC):
    """Decides what state an NPC should enter when idle."""

    @abstractmethod
    def decide(self, controller, priority_need) -> str | None:
        """Return a state name to transition to, or None for default behavior."""


class HumanBehavior(BehaviorStrategy):
    """Default behavior: satisfy needs via the standard decision loop."""

    def decide(self, controller, priority_need) -> str | None:
        return None  # fall through to normal IdleState logic


class GoblinBehavior(BehaviorStrategy):
    """Threat-driven behavior: patrol at low threat, raid at high threat.

    Goblins still satisfy critical needs normally (hunger/thirst/sleep),
    but when needs aren't urgent, their behavior is shaped by the
    shared GoblinThreat level rather than idle wandering.
    """

    def __init__(self, threat: GoblinThreat):
        self.threat = threat

    def decide(self, controller, priority_need) -> str | None:
        # If a need is WARNING or CRITICAL, let the normal loop handle it
        # (goblins still eat, drink, sleep like anyone else)
        if priority_need is not None and priority_need.is_urgent:
            return None

        stage = self.threat.stage

        if stage == ThreatStage.PASSIVE:
            return "PATROLLING"
        else:
            # RAIDING or CROSSING — go raid civilized sources
            return "RAIDING"
