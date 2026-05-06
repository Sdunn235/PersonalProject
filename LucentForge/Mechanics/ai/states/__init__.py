# states — NPC AI state pattern
from __future__ import annotations
from typing import Protocol, runtime_checkable


@runtime_checkable
class IState(Protocol):
    """Protocol for NPC AI states."""

    def enter(self, controller) -> None: ...
    def update(self, controller, dt: float) -> None: ...
