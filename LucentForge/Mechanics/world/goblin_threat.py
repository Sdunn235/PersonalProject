from enum import Enum
import settings


class ThreatStage(Enum):
    PASSIVE = "passive"
    RAIDING = "raiding"
    CROSSING = "crossing"


class GoblinThreat:
    """Hunger-driven external pressure source for the settlement.

    Threat rises when goblins are hungry (forage depleted) and decays
    slightly when they're fed. This replaces the flat growth_rate timer
    from Heartbeat-1 with an organic, simulation-driven escalation.
    """

    def __init__(self,
                 threat_level: float = settings.THREAT_INITIAL):
        self.threat_level = threat_level
        self._prev_stage: ThreatStage = self.stage

    @property
    def stage(self) -> ThreatStage:
        if self.threat_level < settings.THREAT_PASSIVE_MAX:
            return ThreatStage.PASSIVE
        if self.threat_level < settings.THREAT_RAIDING_MAX:
            return ThreatStage.RAIDING
        return ThreatStage.CROSSING

    def update(self, avg_goblin_hunger_pct: float = 1.0) -> ThreatStage | None:
        """Grow or decay threat based on average goblin hunger.

        Args:
            avg_goblin_hunger_pct: Average hunger value (0-100) as fraction
                of max (0.0 = starving, 1.0 = full). When goblins are hungry,
                this value is LOW, and threat grows FAST.

        Returns:
            The new ThreatStage if a stage transition occurred, else None.
        """
        # Hunger pressure: low hunger_pct means goblins are starving → high growth
        hunger_pressure = (1.0 - avg_goblin_hunger_pct)
        delta = (hunger_pressure * settings.GOBLIN_HUNGER_THREAT_WEIGHT
                 - settings.GOBLIN_THREAT_NATURAL_DECAY)

        self.threat_level = max(0.0,
                                min(self.threat_level + delta,
                                    settings.THREAT_MAX))

        # Detect stage transitions for logging
        new_stage = self.stage
        if new_stage != self._prev_stage:
            old_stage = self._prev_stage
            self._prev_stage = new_stage
            print(f"[THREAT] Stage: {old_stage.value.upper()} -> "
                  f"{new_stage.value.upper()} "
                  f"(threat={self.threat_level:.1f}, "
                  f"hunger={avg_goblin_hunger_pct:.0%})")
            return new_stage
        return None

    def reduce(self, amount: float) -> None:
        """Reduce threat (e.g. from successful NPC defense)."""
        self.threat_level = max(0.0, self.threat_level - amount)
