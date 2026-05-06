# need_source.py — Need source nodes on the map (data-driven)
from __future__ import annotations
from dataclasses import dataclass, field
import settings


@dataclass
class NeedSource:
    need_id: str                       # "hunger", "thirst", "sleep", etc.
    grid_col: int
    grid_row: int
    label: str
    color: tuple[int, int, int] = (255, 255, 255)
    tiles: list[tuple[int, int]] = field(default_factory=list)
    satisfaction_amount: float = 80.0
    interaction_time: float = 8.0
    # Heartbeat-5: Resource Economy — finite source stock
    stock: float = -1.0                # current units available (-1 = infinite)
    capacity: float = -1.0             # max units (-1 = infinite)
    regen_rate: float = 0.0            # units restored per sim tick

    @property
    def is_finite(self) -> bool:
        return self.capacity > 0

    def consume(self, amount: float) -> float:
        """Subtract amount from stock. Returns actual amount consumed.
        Infinite sources always return the full amount."""
        if not self.is_finite:
            return amount
        actual = min(amount, max(0.0, self.stock))
        self.stock -= actual
        if self.stock <= 0 and actual > 0:
            self.stock = 0.0
            print(f"[ECON] {self.label} DEPLETED (capacity={self.capacity:.0f})")
        return actual

    def regenerate(self) -> None:
        """Add regen_rate to stock, clamped to capacity. Logs at milestones."""
        if not self.is_finite or self.regen_rate <= 0:
            return
        old_pct = self.stock / self.capacity if self.capacity > 0 else 0.0
        self.stock = min(self.capacity, self.stock + self.regen_rate)
        new_pct = self.stock / self.capacity
        for milestone in (0.25, 0.50, 0.75, 1.0):
            if old_pct < milestone <= new_pct:
                print(f"[ECON] {self.label} regen {milestone * 100:.0f}% "
                      f"({self.stock:.0f}/{self.capacity:.0f})")

    # Backward compat
    @property
    def need_type(self) -> str:
        return self.need_id

    @staticmethod
    def from_dict(d: dict) -> NeedSource:
        color = d.get("color", [255, 255, 255])
        return NeedSource(
            need_id=d["need_id"],
            grid_col=d["grid_col"],
            grid_row=d["grid_row"],
            label=d.get("label", ""),
            color=tuple(color),
            satisfaction_amount=d.get("satisfaction_amount", 80.0),
            interaction_time=d.get("interaction_time", 8.0),
            stock=d.get("stock", -1.0),
            capacity=d.get("capacity", -1.0),
            regen_rate=d.get("regen_rate", 0.0),
        )

    @property
    def world_x(self) -> float:
        if self.tiles:
            return sum(c * settings.TILE_SIZE + settings.TILE_SIZE // 2
                       for c, _ in self.tiles) / len(self.tiles)
        return self.grid_col * settings.TILE_SIZE + settings.TILE_SIZE // 2

    @property
    def world_y(self) -> float:
        if self.tiles:
            return sum(r * settings.TILE_SIZE + settings.TILE_SIZE // 2
                       for _, r in self.tiles) / len(self.tiles)
        return self.grid_row * settings.TILE_SIZE + settings.TILE_SIZE // 2

    def distance_from(self, x: float, y: float) -> float:
        if self.tiles:
            best = float("inf")
            for c, r in self.tiles:
                tx = c * settings.TILE_SIZE + settings.TILE_SIZE // 2
                ty = r * settings.TILE_SIZE + settings.TILE_SIZE // 2
                d = ((tx - x) ** 2 + (ty - y) ** 2) ** 0.5
                if d < best:
                    best = d
            return best
        dx = self.world_x - x
        dy = self.world_y - y
        return (dx * dx + dy * dy) ** 0.5


def find_source_by_need(need_id: str, sources: list[NeedSource],
                        from_x: float, from_y: float) -> NeedSource | None:
    """Returns the nearest source matching the need_id."""
    candidates = [s for s in sources if s.need_id == need_id]
    if not candidates:
        return None
    return min(candidates, key=lambda s: s.distance_from(from_x, from_y))


def make_default_sources() -> list[NeedSource]:
    """Load sources from sources.json if available, else hardcoded fallback."""
    try:
        from Mechanics.data.dao import Dao
        import os
        data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
        sources_path = os.path.normpath(os.path.join(data_dir, "sources.json"))
        if os.path.isfile(sources_path):
            dao = Dao(sources_path)
            return [NeedSource.from_dict(d) for d in dao.get_all()]
    except Exception:
        pass
    return [
        NeedSource("hunger", grid_col=3,  grid_row=3,  label="FOOD",  color=settings.FOOD_COLOR),
        NeedSource("thirst", grid_col=18, grid_row=3,  label="WATER", color=settings.WATER_COLOR),
        NeedSource("sleep",  grid_col=3,  grid_row=14, label="BED",   color=settings.SLEEP_COLOR),
    ]
