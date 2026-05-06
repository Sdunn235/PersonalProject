# Mechanics/data — JSON Data Layer

Data access layer modeled after RPGDatabaseManager's GameContext + IEntityDao pattern.

## Architecture

```
data/
  loader.py       — Generic JSON file loader (reads/writes JSON arrays)
  dao.py          — Generic DAO with LINQ-style query methods
  entities.json   — Entity definitions (player + NPCs: stats, traits, spawn, abilities, bag)
  abilities.json  — All ability definitions (attack, heal, basic, spells)
  items.json      — Item templates (consumables, gear)
  spells.json     — Spell definitions (4 spells: fireball, ice_shard, lightning, heal_light)
```

## Data Flow

```
JSON files  -->  loader.py (read)  -->  dao.py (query)  -->  consumers
                                                              |
                                                  ability_sets.py (combat abilities)
                                                  spell_sets.py (combat spells)
                                                  equip.py (equipment stat mods)
                                                  items.py (combat inventory)
                                                  factory.py (entity spawning)
                                                  combat_scene.py (UI)
```

## DAO Query Methods (Python LINQ equivalents)

| Method | LINQ Equivalent | Example |
|---|---|---|
| `get_all()` | `.ToList()` | `dao.get_all()` |
| `get_by_id(id)` | `.FirstOrDefault(x => x.Id == id)` | `dao.get_by_id("strike")` |
| `where(predicate)` | `.Where(pred).ToList()` | `dao.where(lambda a: a["kind"] == "heal")` |
| `first_or_default(pred)` | `.FirstOrDefault(pred)` | `dao.first_or_default(lambda e: e["type"] == "npc")` |
| `select(transform)` | `.Select(fn).ToList()` | `dao.select(lambda a: a["name"])` |
| `any(predicate)` | `.Any(pred)` | `dao.any(lambda e: e["is_enemy"])` |
| `count(predicate)` | `.Count(pred)` | `dao.count(lambda a: a["kind"] == "attack")` |

## Adding New Content

- **New entity**: Add an entry to `entities.json` with `id`, `type`, `stats`, etc.
- **New ability**: Add to `abilities.json`, then reference its `id` in entity's `abilities` array.
- **New item**: Add to `items.json`, then reference its `id` in entity's `bag` array.
- **New spell**: Add to `spells.json`, then reference its `id` in entity's `spells` array. Spells cost MP and scale off MAG stat.
- **New equipment**: Add to `items.json` with `type: "weapon"/"armor"`, `slot`, and `effects`. Reference id in entity's `equipment` object.

No code changes needed for new content — just edit JSON.

## SOLID Principles Applied

- **S**: Each file has one job (loader loads, dao queries, JSON stores data)
- **O**: New entities/abilities/items added via JSON, not code changes
- **L**: Dao works identically for any JSON content type
- **I**: Consumers only import what they need (get_abilities_dao, get_items_dao, etc.)
- **D**: Combat system depends on DAO abstractions, not hardcoded dicts
