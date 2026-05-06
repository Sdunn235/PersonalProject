from enum import Enum
import settings


class TimePhase(Enum):
    DAY = "day"
    NIGHT = "night"


class SimulationClock:
    """Single source of temporal truth for the world simulation."""

    def __init__(self):
        self.tick_count: int = 0
        self._accumulator: float = 0.0

    @property
    def day(self) -> float:
        if settings.TICKS_PER_DAY <= 0:
            return 0.0
        return self.tick_count / settings.TICKS_PER_DAY

    @property
    def day_number(self) -> int:
        return int(self.day)

    @property
    def time_phase(self) -> TimePhase:
        if settings.TICKS_PER_DAY <= 0:
            return TimePhase.DAY
        progress = (self.tick_count % settings.TICKS_PER_DAY) / settings.TICKS_PER_DAY
        return TimePhase.DAY if progress < settings.DAY_PHASE_RATIO else TimePhase.NIGHT

    def update(self, dt: float) -> int:
        """Accumulate real time and return number of sim ticks elapsed."""
        self._accumulator += dt * settings.SIM_TICK_RATE
        ticks = int(self._accumulator)
        if ticks > 0:
            self._accumulator -= ticks
            self.tick_count += ticks
        return ticks
