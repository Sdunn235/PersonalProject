# loader.py — Generic JSON file loader
# Modeled after RPGDatabaseManager's GameContext:
#   - Reads JSON files from a configurable base path
#   - Returns typed Python dicts/lists
#   - Single point of entry for all data loading
from __future__ import annotations
import json
import os

# Resolve data directory relative to this file
_DATA_DIR = os.path.dirname(os.path.abspath(__file__))


def _resolve(filename: str) -> str:
    """Resolve a filename relative to the data directory."""
    return os.path.join(_DATA_DIR, filename)


def load_json(filename: str) -> list[dict]:
    """Load a JSON array file and return as list of dicts.

    Returns an empty list if the file does not exist.
    """
    path = _resolve(filename)
    if not os.path.isfile(path):
        return []
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError(f"{filename}: expected JSON array, got {type(data).__name__}")
    return data


def save_json(filename: str, data: list[dict]) -> None:
    """Write a list of dicts back to a JSON file (pretty-printed)."""
    path = _resolve(filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


