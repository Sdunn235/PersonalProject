# context.py — GameContext: single owner of all DAOs
# Mirrors RPGDatabaseManager's GameContext class
from __future__ import annotations
import os
from Mechanics.data.dao import Dao


class GameContext:
    """Single point of data access. Owns all DAO instances.

    All game systems receive this via constructor injection instead of
    importing singleton functions.
    """

    def __init__(self, data_dir: str | None = None):
        if data_dir is None:
            data_dir = os.path.dirname(os.path.abspath(__file__))
        self._data_dir = data_dir
        self._entities = Dao(os.path.join(data_dir, "entities.json"))
        self._abilities = Dao(os.path.join(data_dir, "abilities.json"))
        self._items = Dao(os.path.join(data_dir, "items.json"))

    @property
    def entities(self) -> Dao:
        return self._entities

    @property
    def abilities(self) -> Dao:
        return self._abilities

    @property
    def items(self) -> Dao:
        return self._items

    def reload(self) -> None:
        self._entities.reload()
        self._abilities.reload()
        self._items.reload()

    def save(self) -> None:
        self._entities.save()
        self._abilities.save()
        self._items.save()
