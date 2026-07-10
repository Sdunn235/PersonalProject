# base.py — Abstract Entity base class
from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from .stats import Stats
from .traits import Traits
from .attributes import Attributes
from .affinity import Affinity, AffinityState


@dataclass
class Entity(ABC):
    entity_id: str
    name: str
    subtype: str = ""
    # Attributes are the primary layer (§M2); `stats` is derived from them by the
    # factory. Both are carried on the entity so combat/overworld code reads `stats`
    # unchanged while `attributes` powers checks (§12.2) and magic pools (§M3).
    attributes: Attributes = field(default_factory=Attributes)
    stats: Stats = field(default_factory=Stats)
    traits: Traits = field(default_factory=Traits)
    # Innate elemental affinity, mutable via grant/suppress (§M5).
    affinity: AffinityState = field(default_factory=lambda: AffinityState(innate=Affinity.EARTH))
    hp: int = 100
    max_hp: int = 100

    # World position in pixels
    x: float = 0.0
    y: float = 0.0

    @property
    def alive(self) -> bool:
        return self.hp > 0

    @abstractmethod
    def update(self, dt: float) -> None:
        """Called each frame. dt = seconds since last frame."""

    def take_damage(self, amount: int) -> int:
        actual = max(1, amount - self.stats.DEF)
        self.hp = max(0, self.hp - actual)
        return actual

    def heal(self, amount: int) -> int:
        before = self.hp
        self.hp = min(self.max_hp, self.hp + amount)
        return self.hp - before

    def grid_pos(self, tile_size: int) -> tuple[int, int]:
        """Return (col, row) grid position from pixel position."""
        return int(self.x // tile_size), int(self.y // tile_size)
