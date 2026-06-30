# dao.py — Generic Data Access Object
# Modeled after RPGDatabaseManager's IEntityDao<T>:
#   - get_by_id, get_all, where, first_or_default
#   - Python LINQ equivalents via list comprehensions and generators
from __future__ import annotations
import json
import os
from typing import Callable


class Dao:
    """Generic read-only DAO over a JSON array file.

    Provides LINQ-style query methods (where, select, first_or_default, etc.)
    using Python list comprehensions and generators.

    Accepts either a bare filename (resolved relative to the data directory)
    or an absolute path (used by GameContext injection).
    """

    def __init__(self, path: str):
        if os.path.isabs(path):
            self._path = path
        else:
            data_dir = os.path.dirname(os.path.abspath(__file__))
            self._path = os.path.join(data_dir, path)
        self._data: list[dict] = []
        self.reload()

    def reload(self) -> None:
        """(Re)load data from the JSON file."""
        if not os.path.isfile(self._path):
            self._data = []
            return
        with open(self._path, encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, list):
            raise ValueError(f"{self._path}: expected JSON array, got {type(data).__name__}")
        self._data = data

    # --- LINQ-style query methods ---

    def get_all(self) -> list[dict]:
        """Return all records (like LINQ .ToList())."""
        return list(self._data)

    def get_by_id(self, record_id: str) -> dict | None:
        """Find a single record by its 'id' field (like LINQ .FirstOrDefault(x => x.Id == id))."""
        return next((r for r in self._data if r.get("id") == record_id), None)

    def where(self, predicate: Callable[[dict], bool]) -> list[dict]:
        """Filter records (like LINQ .Where(predicate).ToList())."""
        return [r for r in self._data if predicate(r)]

    def first_or_default(self, predicate: Callable[[dict], bool]) -> dict | None:
        """Return first matching record or None (like LINQ .FirstOrDefault())."""
        return next((r for r in self._data if predicate(r)), None)

    def select(self, transform: Callable[[dict], object]) -> list:
        """Project each record (like LINQ .Select(transform).ToList())."""
        return [transform(r) for r in self._data]

    def any(self, predicate: Callable[[dict], bool]) -> bool:
        """Check if any record matches (like LINQ .Any())."""
        return any(predicate(r) for r in self._data)

    def count(self, predicate: Callable[[dict], bool] | None = None) -> int:
        """Count records, optionally filtered (like LINQ .Count())."""
        if predicate is None:
            return len(self._data)
        return sum(1 for r in self._data if predicate(r))

    # --- Mutation (for runtime state changes, e.g. saving player progress) ---

    def add(self, record: dict) -> None:
        self._data.append(record)

    def update(self, record_id: str, updates: dict) -> bool:
        """Merge updates into an existing record. Returns True if found."""
        rec = self.get_by_id(record_id)
        if rec is None:
            return False
        rec.update(updates)
        return True

    def delete(self, record_id: str) -> bool:
        """Remove a record by id. Returns True if found and removed."""
        before = len(self._data)
        self._data = [r for r in self._data if r.get("id") != record_id]
        return len(self._data) < before

    def save(self) -> None:
        """Persist current state back to the JSON file."""
        with open(self._path, "w", encoding="utf-8") as f:
            json.dump(self._data, f, indent=2, ensure_ascii=False)
            f.write("\n")


class SqliteDao:
    """DAO backed by a SQLite document table (id TEXT PK, data JSON).

    Same query API as Dao (lambda-based, evaluated in memory over dicts), so all
    existing call sites are unchanged. SQLite is only the store/seed: reload()
    loads every row's `data` column back into dicts; queries run in Python.
    Satisfies the IEntityDao protocol in protocols.py.
    """

    def __init__(self, database, table: str):
        self._db = database
        self._table = table          # internal/fixed name — safe to interpolate
        self._data: list[dict] = []
        self.reload()

    def reload(self) -> None:
        """(Re)load all rows from the table into memory as dicts (JSON file order)."""
        cur = self._db.conn.execute(f"SELECT data FROM {self._table} ORDER BY rowid")
        self._data = [json.loads(row["data"]) for row in cur.fetchall()]

    # --- LINQ-style query methods (identical semantics to Dao) ---

    def get_all(self) -> list[dict]:
        return list(self._data)

    def get_by_id(self, record_id: str) -> dict | None:
        return next((r for r in self._data if r.get("id") == record_id), None)

    def where(self, predicate: Callable[[dict], bool]) -> list[dict]:
        return [r for r in self._data if predicate(r)]

    def first_or_default(self, predicate: Callable[[dict], bool]) -> dict | None:
        return next((r for r in self._data if predicate(r)), None)

    def select(self, transform: Callable[[dict], object]) -> list:
        return [transform(r) for r in self._data]

    def any(self, predicate: Callable[[dict], bool]) -> bool:
        return any(predicate(r) for r in self._data)

    def count(self, predicate: Callable[[dict], bool] | None = None) -> int:
        if predicate is None:
            return len(self._data)
        return sum(1 for r in self._data if predicate(r))

    # --- Mutation: write through to SQLite (keyed on record["id"]) ---

    def add(self, record: dict) -> None:
        self._data.append(record)
        self._db.conn.execute(
            f"INSERT OR REPLACE INTO {self._table} (id, data) VALUES (?, ?)",
            (str(record.get("id")), json.dumps(record, ensure_ascii=False)))
        self._db.conn.commit()

    def update(self, record_id: str, updates: dict) -> bool:
        rec = self.get_by_id(record_id)
        if rec is None:
            return False
        rec.update(updates)
        self._db.conn.execute(
            f"UPDATE {self._table} SET data = ? WHERE id = ?",
            (json.dumps(rec, ensure_ascii=False), str(record_id)))
        self._db.conn.commit()
        return True

    def delete(self, record_id: str) -> bool:
        before = len(self._data)
        self._data = [r for r in self._data if r.get("id") != record_id]
        if len(self._data) == before:
            return False
        self._db.conn.execute(f"DELETE FROM {self._table} WHERE id = ?", (str(record_id),))
        self._db.conn.commit()
        return True

    def save(self) -> None:
        """Upsert all in-memory rows back to the table (keyed on id)."""
        with self._db.conn:
            for rec in self._data:
                self._db.conn.execute(
                    f"INSERT OR REPLACE INTO {self._table} (id, data) VALUES (?, ?)",
                    (str(rec.get("id")), json.dumps(rec, ensure_ascii=False)))
