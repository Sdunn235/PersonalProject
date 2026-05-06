# services — Service Protocol interfaces
from __future__ import annotations
from typing import Protocol, runtime_checkable


@runtime_checkable
class ICombatService(Protocol):
    """Interface for combat operations."""

    def process_turn(self, attacker, defender, rng,
                     forced_ability: dict | None = None) -> dict: ...


@runtime_checkable
class INeedsService(Protocol):
    """Interface for needs system operations."""

    def create_needs(self) -> list: ...
    def update(self, needs: list, is_sleeping: bool = False) -> None: ...
    def get_priority(self, needs: list): ...
    def fill(self, need, dt: float) -> bool: ...


@runtime_checkable
class IEntityFactory(Protocol):
    """Interface for entity creation."""

    def create_player(self): ...
    def create_all_npcs(self) -> list: ...
    def get_sprite_path(self, entity_id: str) -> str | None: ...
