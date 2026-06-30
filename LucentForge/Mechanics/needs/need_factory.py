# need_factory.py — Builds needs from the GameContext data layer (SQLite-backed).
from __future__ import annotations
from Mechanics.data.context import GameContext
from Mechanics.needs.need import Need


class NeedFactory:
    """Creates Need lists from the `needs` collection."""

    def __init__(self, ctx: GameContext):
        self._dao = ctx.needs

    def create_all(self) -> list[Need]:
        """Build all needs defined in needs.json."""
        return [Need.from_dict(d) for d in self._dao.get_all()]

    def create_by_id(self, need_id: str) -> Need | None:
        """Build a single need by id."""
        d = self._dao.get_by_id(need_id)
        if d is None:
            return None
        return Need.from_dict(d)
