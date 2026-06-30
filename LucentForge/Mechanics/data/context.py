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
        self._save_manager = SaveManager(self._db)

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

    def reload(self) -> None:
        self._entities.reload()
        self._abilities.reload()
        self._items.reload()
        self._needs.reload()
        self._sources.reload()

    def save(self) -> None:
        self._entities.save()
        self._abilities.save()
        self._items.save()
        self._needs.save()
        self._sources.save()
