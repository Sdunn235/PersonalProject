from __future__ import annotations
from Mechanics.world.simulation_clock import SimulationClock
from Mechanics.world.resource_state import ResourceState
from Mechanics.world.goblin_threat import GoblinThreat
from Mechanics.world.town import Town


class WorldSim:
    """World-level simulation orchestrator.

    Owns the four Heartbeat-1 objects and coordinates their
    per-tick update in the order prescribed by the bible schema:
        1. Advance clock
        2. Update resources (H5: regenerate finite sources)
        3. Update goblin threat
        4. Evaluate town state
    """

    def __init__(self, sources: list | None = None):
        self.clock = SimulationClock()
        self.resources = ResourceState(sources)
        self.threat = GoblinThreat()
        self.town = Town()
        self._last_logged_tick: int = -1

    def tick(self, dt: float, living_npc_count: int,
             avg_goblin_hunger_pct: float = 1.0) -> int:
        """Run one frame's worth of simulation updates.

        Args:
            avg_goblin_hunger_pct: Average goblin hunger (0.0=starving, 1.0=full).
                Drives threat escalation in Heartbeat-4.

        Returns the number of sim ticks that actually fired this frame.
        """
        ticks = self.clock.update(dt)
        for _ in range(ticks):
            self.resources.update(living_npc_count)
            self.threat.update(avg_goblin_hunger_pct)
            self.town.evaluate(self.resources, living_npc_count, self.threat)
        return ticks

    def status_line(self) -> str:
        """One-line summary for console output."""
        return (
            f"[WORLD] Day {self.clock.day:.2f} ({self.clock.time_phase.value}) | "
            f"Food {self.resources.food_total:.1f} | "
            f"Threat {self.threat.threat_level:.1f} ({self.threat.stage.value}) | "
            f"Town: {self.town.state.value}"
        )
