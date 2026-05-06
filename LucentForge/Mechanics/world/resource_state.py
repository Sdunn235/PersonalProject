# resource_state.py — Settlement resource tracking (Heartbeat-5: source-based economy)
from __future__ import annotations


class ResourceState:
    """Tracks shared settlement resources by aggregating actual source stocks.

    H5 refactor: food_total is now a live sum of all hunger-source stocks,
    not a flat production/consumption formula. Regeneration is ticked per-source.
    """

    def __init__(self, sources: list | None = None):
        self._sources = sources or []

    def set_sources(self, sources: list) -> None:
        """Late-bind sources (for when sources are created after ResourceState)."""
        self._sources = sources

    @property
    def food_total(self) -> float:
        """Sum of all hunger-source stocks (finite sources only).

        Infinite hunger sources contribute their capacity as a baseline.
        """
        total = 0.0
        for s in self._sources:
            if s.need_id == "hunger":
                if s.is_finite:
                    total += s.stock
                else:
                    total += s.capacity if s.capacity > 0 else 100.0
        return total

    def update(self, living_npc_count: int) -> None:
        """Tick regeneration on all finite sources."""
        for s in self._sources:
            if s.is_finite:
                s.regenerate()
