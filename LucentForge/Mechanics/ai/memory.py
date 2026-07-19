# memory.py — NPC source-quality memory (Heartbeat-3)
# Each NPC remembers how well past need-satisfaction went at each source.
# Memory size is bounded by source count (currently 3-8).
# If sources become dynamic, add an LRU cap (~20 entries).
from __future__ import annotations
from dataclasses import dataclass
import settings


@dataclass
class SourceMemory:
    source_label: str
    need_id: str
    visit_count: int = 0
    avg_satisfaction: float = 0.5
    last_visit_tick: int = 0


@dataclass
class RegionComfortMemory:
    """Learned affinity comfort for a region (biochem/affinity addendum §B4/§B6.5).

    Unlike SourceMemory (survival-satisfaction, defaults to neutral 0.5), region comfort
    is the affinity-comfort score in [-1, +1] and defaults to 0.0 (unknown = neutral).
    Two same-affinity beings diverge here by lived experience (Grace §14.2).
    """
    region_id: str
    avg_comfort: float = 0.0
    visit_count: int = 0
    last_visit_tick: int = 0


class Memory:
    def __init__(self):
        self._sources: dict[str, SourceMemory] = {}
        # Learned per-region affinity comfort (parallel to _sources, never entangled).
        self._regions: dict[str, RegionComfortMemory] = {}

    def record_outcome(self, source_label: str, need_id: str,
                       quality_score: float, tick: int) -> None:
        """Record or update memory for a source after satisfying a need."""
        entry = self._sources.get(source_label)
        if entry is None:
            entry = SourceMemory(source_label=source_label, need_id=need_id)
            self._sources[source_label] = entry

        alpha = settings.MEMORY_EMA_ALPHA
        if entry.visit_count == 0:
            entry.avg_satisfaction = quality_score
        else:
            entry.avg_satisfaction = (alpha * quality_score
                                      + (1.0 - alpha) * entry.avg_satisfaction)

        entry.visit_count += 1
        entry.last_visit_tick = tick

    def record_threat(self, source_label: str, tick: int) -> None:
        """Lower a source's memory preference when a goblin was encountered there.

        Uses the same EMA as record_outcome but blends in a low quality score
        (0.1) to represent the negative experience. If the source hasn't been
        visited before, initialize it as a bad memory.
        """
        entry = self._sources.get(source_label)
        if entry is None:
            entry = SourceMemory(source_label=source_label, need_id="unknown")
            self._sources[source_label] = entry

        threat_quality = 0.1  # bad experience — goblin encounter
        alpha = settings.MEMORY_EMA_ALPHA
        if entry.visit_count == 0:
            entry.avg_satisfaction = threat_quality
        else:
            entry.avg_satisfaction = (alpha * threat_quality
                                      + (1.0 - alpha) * entry.avg_satisfaction)
        entry.visit_count += 1
        entry.last_visit_tick = tick

    def get_source_preference(self, source_label: str) -> float:
        """Return avg_satisfaction for a source, or 0.5 (neutral) if unvisited."""
        entry = self._sources.get(source_label)
        if entry is None:
            return 0.5
        return entry.avg_satisfaction

    def get_visit_count(self, source_label: str) -> int:
        entry = self._sources.get(source_label)
        if entry is None:
            return 0
        return entry.visit_count

    # --- Region affinity comfort (biochem/affinity addendum §B4) ---

    def record_region_comfort(self, region_id: str, comfort: float,
                              tick: int) -> None:
        """Blend the current affinity-comfort reading into the region's EMA.

        Same EMA weight as source memory (settings.MEMORY_EMA_ALPHA); first exposure
        seeds the average directly so a single visit isn't diluted toward 0.
        """
        entry = self._regions.get(region_id)
        if entry is None:
            entry = RegionComfortMemory(region_id=region_id)
            self._regions[region_id] = entry

        alpha = settings.MEMORY_EMA_ALPHA
        if entry.visit_count == 0:
            entry.avg_comfort = comfort
        else:
            entry.avg_comfort = (alpha * comfort
                                 + (1.0 - alpha) * entry.avg_comfort)
        entry.visit_count += 1
        entry.last_visit_tick = tick

    def get_region_preference(self, region_id: str) -> float:
        """Return learned comfort for a region, or 0.0 (unknown = neutral) if unseen."""
        entry = self._regions.get(region_id)
        return entry.avg_comfort if entry is not None else 0.0

    def best_region(self) -> tuple[str, float] | None:
        """The (region_id, avg_comfort) with the highest learned comfort, or None.

        Only positive-comfort regions are worth relocating toward; a memory of only
        neutral/negative regions yields None so the relocate drive stays silent.
        """
        best: RegionComfortMemory | None = None
        for entry in self._regions.values():
            if entry.avg_comfort <= 0.0:
                continue
            if best is None or entry.avg_comfort > best.avg_comfort:
                best = entry
        return (best.region_id, best.avg_comfort) if best is not None else None

    def summary(self) -> str:
        if not self._sources:
            return "no memories"
        parts = []
        for e in self._sources.values():
            parts.append(f"{e.source_label}={e.avg_satisfaction:.2f}(x{e.visit_count})")
        return " | ".join(parts)
