# Mechanics/data — Data Layer (SQLite-backed, Phase 1)

Data access layer modeled after RPGDatabaseManager's `GameContext` + `IEntityDao` pattern. **Phase 1** moved storage from flat JSON to a real **SQLite** database; the query API is unchanged, so consumers don't care where the data lives.

## Architecture

```
data/
  db.py            — Database: SQLite connection + hand-written migrations runner
  migrations/      — Ordered, versioned migrations (m####_<name>.py); 0001 creates + seeds tables
  context.py       — GameContext: owns the Database + one SqliteDao per collection
  dao.py           — Dao (JSON, legacy/fallback) + SqliteDao (LINQ-style query API over a table)
  loader.py        — Generic JSON loader (used by the seed migration)
  protocols.py     — IEntityDao / IContext Protocols
  models.py        — Typed dataclasses (AbilityDef, ItemDef, EntityDef)
  *.json           — Canonical seed content (see below)
  lucentforge.db   — Runtime SQLite store (GITIGNORED; rebuilt from JSON by migration 0001)
```

### Collections (one document table each)

`entities` · `abilities` (includes spells) · `items` · `needs` · `sources`

Each table is `(id TEXT PRIMARY KEY, data TEXT)` where `data` is the JSON for one record. On `reload()`, `SqliteDao` loads every row's `data` back into dicts, so the lambda-based query methods run in memory exactly as before.

## Data flow

```
*.json (canonical seed)
   │  migration 0001 (once)
   ▼
lucentforge.db  ──reload()──►  SqliteDao (in-memory dicts)  ──►  consumers
   ▲                                                              factory.py (spawning)
   └─ GameContext opens DB + runs migrations on startup          ability_sets / spell_sets / equip / items (combat)
                                                                  need_factory.py (needs)
```

## DAO query methods (Python LINQ equivalents — same on `Dao` and `SqliteDao`)

| Method | LINQ Equivalent | Example |
|---|---|---|
| `get_all()` | `.ToList()` | `ctx.abilities.get_all()` |
| `get_by_id(id)` | `.FirstOrDefault(x => x.Id == id)` | `ctx.abilities.get_by_id("strike")` |
| `where(predicate)` | `.Where(pred).ToList()` | `ctx.entities.where(lambda e: e["type"] == "npc")` |
| `first_or_default(pred)` | `.FirstOrDefault(pred)` | `ctx.entities.first_or_default(lambda e: e["is_enemy"])` |
| `select(transform)` | `.Select(fn).ToList()` | `ctx.abilities.select(lambda a: a["name"])` |
| `any(predicate)` | `.Any(pred)` | `ctx.entities.any(lambda e: e["is_enemy"])` |
| `count(predicate)` | `.Count(pred)` | `ctx.abilities.count(lambda a: a["kind"] == "attack")` |

`add` / `update` / `delete` / `save` on `SqliteDao` write through to the table (keyed on `id`).

## Editing content (JSON stays canonical)

1. Edit the relevant `*.json` file (`id` is the primary key).
2. **Delete `lucentforge.db`** and re-run — migration `0001` recreates and reseeds the tables.

> The `.db` is a gitignored runtime artifact. The JSON files are the version-controlled source of truth. Runtime world-state save/load (NPC positions, source stocks, etc.) is **Phase 1.5** and will live only in the DB.

## Migrations

`db.py` records applied versions in `schema_migrations` and runs pending ones in order on startup (idempotent). Add a new step as `migrations/m####_<name>.py` exposing `migrate(conn)`, then register it in `migrations/__init__.py`. Hand-edit migrations deliberately (TheForge discipline) — review before relying on them.

## SOLID

- **S**: `db.py` connects/migrates, `dao.py` queries, JSON seeds, migrations evolve schema.
- **O**: new content via JSON; new schema via a new migration file — no edits to existing code.
- **L**: `Dao` and `SqliteDao` are interchangeable behind `IEntityDao`.
- **I**: consumers depend only on the small DAO query surface.
- **D**: systems depend on `GameContext` / DAO abstractions, not on storage details.
