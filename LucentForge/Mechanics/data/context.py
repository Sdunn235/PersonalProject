# context.py — GameContext: single owner of the database + all DAOs.
# Mirrors RPGDatabaseManager's GameContext / IContext.
#
# Phase 1: data now lives in SQLite (lucentforge.db), seeded from the canonical
# JSON files via migrations. The DAO query API is unchanged, so callers don't care.
from __future__ import annotations
import os
from Mechanics.data.db import Database
from Mechanics.data.dao import SqliteDao
from Mechanics.data.save_manager import SaveManager
from Mechanics.items.repos import ItemRepository


class GameContext:
    """Single point of data access. Owns the Database and all collection DAOs.

    All game systems receive this via constructor injection instead of
    importing singleton functions.
    """

    def __init__(self, data_dir: str | None = None, db_path: str | None = None):
        if data_dir is None:
            data_dir = os.path.dirname(os.path.abspath(__file__))
        self._data_dir = data_dir
        # Opening the Database runs pending migrations (creates + seeds on first run).
        self._db = Database(db_path)
        self._entities = SqliteDao(self._db, "entities")
        self._abilities = SqliteDao(self._db, "abilities")
        self._items = SqliteDao(self._db, "items")
        self._needs = SqliteDao(self._db, "needs")
        self._sources = SqliteDao(self._db, "sources")
        self._chests = SqliteDao(self._db, "chest_content")
        self._save_manager = SaveManager(self._db)
        self._item_repo = ItemRepository(self._items)
        # Deferred imports — Mechanics.world.__init__ pulls tile_map which
        # would create a circular dependency if imported at module level.
        from Mechanics.world.rooms import RoomRegistry
        self._rooms = RoomRegistry.from_json(os.path.join(data_dir, "rooms.json"))
        from Mechanics.world.world_coord import PanelLoader
        self._panel_loader = PanelLoader.from_json(os.path.join(data_dir, "panels.json"))
        self.current_panel: tuple[int, int] = (0, 0)

    @property
    def db(self) -> Database:
        return self._db

    @property
    def save_manager(self) -> SaveManager:
        return self._save_manager

    @property
    def entities(self) -> SqliteDao:
        return self._entities

    @property
    def abilities(self) -> SqliteDao:
        return self._abilities

    @property
    def items(self) -> SqliteDao:
        return self._items

    @property
    def needs(self) -> SqliteDao:
        return self._needs

    @property
    def sources(self) -> SqliteDao:
        return self._sources

    @property
    def item_repo(self) -> ItemRepository:
        return self._item_repo

    @property
    def chests(self) -> SqliteDao:
        return self._chests

    @property
    def rooms(self):
        return self._rooms

    @property
    def panel_loader(self):
        return self._panel_loader

    def reload(self) -> None:
        self._entities.reload()
        self._abilities.reload()
        self._items.reload()
        self._needs.reload()
        self._sources.reload()
        self._chests.reload()

    def save(self) -> None:
        self._entities.save()
        self._abilities.save()
        self._items.save()
        self._needs.save()
        self._sources.save()
        self._chests.save()
