# need.py — Data-driven Need system
# String-based need_id replaces NeedType enum. All thresholds/rates from JSON.
from __future__ import annotations
from enum import Enum
from dataclasses import dataclass
import settings


class NeedZone(Enum):
    FINE     = "FINE"
    WARNING  = "WARNING"
    CRITICAL = "CRITICAL"


@dataclass
class Need:
    need_id: str                       # "hunger", "thirst", "sleep", etc.
    label: str = ""
    current_value: float = 100.0
    warning_threshold: float = 60.0
    critical_threshold: float = 30.0
    decay_rate: float = 0.0            # per tick
    fill_rate: float = 0.0             # per real second at source
    hp_drain_rate: float = 0.0         # per real second when at zero
    sleep_decay_mult: float = 0.20     # decay multiplier while sleeping
    chemical: str = ""                 # chemical key in biochem system

    @staticmethod
    def from_dict(d: dict) -> Need:
        """Build a Need from a needs.json entry, computing tick rates from day rates."""
        sim_day = settings.SIM_DAY_SECONDS
        fps = settings.FPS
        decay_per_day = d.get("decay_per_day", 0.0)
        fill_rate_sec = d.get("fill_rate_sec", 8.0)
        hp_drain_per_day = d.get("hp_drain_per_day", 0.0)
        return Need(
            need_id=d["id"],
            label=d.get("label", d["id"]),
            warning_threshold=d.get("warning_threshold", 60.0),
            critical_threshold=d.get("critical_threshold", 30.0),
            decay_rate=(decay_per_day / sim_day) / fps,
            fill_rate=80.0 / (fps * fill_rate_sec),
            hp_drain_rate=hp_drain_per_day / sim_day,
            sleep_decay_mult=d.get("sleep_decay_mult", 0.20),
            chemical=d.get("chemical", ""),
        )

    @property
    def zone(self) -> NeedZone:
        if self.current_value <= self.critical_threshold:
            return NeedZone.CRITICAL
        if self.current_value <= self.warning_threshold:
            return NeedZone.WARNING
        return NeedZone.FINE

    @property
    def is_urgent(self) -> bool:
        return self.zone != NeedZone.FINE

    @property
    def is_zero(self) -> bool:
        return self.current_value <= 0.0

    @property
    def urgency_score(self) -> float:
        if not self.is_urgent:
            return 0.0
        return max(0.0, 1.0 - (self.current_value / self.warning_threshold))

    @property
    def zone_color(self) -> tuple[int, int, int]:
        if self.zone == NeedZone.CRITICAL: return settings.COLOR_CRITICAL
        if self.zone == NeedZone.WARNING:  return settings.COLOR_WARNING
        return settings.COLOR_FINE

    # --- Backward compatibility ---
    @property
    def need_type(self):
        """Returns self for backward compat where code checked need.need_type."""
        return self.need_id


# Backward-compat alias: NeedType is now just a string.
# Old code using NeedType.HUNGER etc. should migrate to string "hunger".
class NeedType:
    HUNGER = "hunger"
    THIRST = "thirst"
    SLEEP  = "sleep"


def make_default_needs() -> list[Need]:
    """Build default needs from needs.json if available, else hardcoded fallback."""
    try:
        from Mechanics.data.dao import Dao
        import os
        data_dir = os.path.dirname(os.path.abspath(__file__))
        needs_path = os.path.join(data_dir, "..", "data", "needs.json")
        needs_path = os.path.normpath(needs_path)
        if os.path.isfile(needs_path):
            dao = Dao(needs_path)
            return [Need.from_dict(d) for d in dao.get_all()]
    except Exception:
        pass
    # Hardcoded fallback matching old behavior
    return [
        Need(need_id="hunger", label="Hunger",
             warning_threshold=settings.HUNGER_WARNING,
             critical_threshold=settings.HUNGER_CRITICAL,
             decay_rate=settings.HUNGER_DECAY_PER_TICK,
             fill_rate=settings.HUNGER_FILL_RATE,
             hp_drain_rate=settings.HUNGER_HP_DRAIN),
        Need(need_id="thirst", label="Thirst",
             warning_threshold=settings.THIRST_WARNING,
             critical_threshold=settings.THIRST_CRITICAL,
             decay_rate=settings.THIRST_DECAY_PER_TICK,
             fill_rate=settings.THIRST_FILL_RATE,
             hp_drain_rate=settings.THIRST_HP_DRAIN),
        Need(need_id="sleep", label="Sleep",
             warning_threshold=settings.SLEEP_WARNING,
             critical_threshold=settings.SLEEP_CRITICAL,
             decay_rate=settings.SLEEP_DECAY_PER_TICK,
             fill_rate=settings.SLEEP_FILL_RATE,
             hp_drain_rate=settings.SLEEP_HP_DRAIN,
             sleep_decay_mult=1.0),
    ]
