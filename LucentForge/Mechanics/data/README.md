# Mechanics/data — Data Layer (SQLite-backed, Phase 1 + Phase 1.5)

Data access layer modeled after RPGDatabaseManager's `GameContext` + `IEntityDao` pattern. **Phase 1** moved storage from flat JSON to a real **SQLite** database; the query API is unchanged, so consumers don't care where the data lives. **Phase 1.5** added world-state save/load via `SaveManager` and migration `m0002`.

## Architecture

```
data/
  db.py            — Database: SQLite connection + hand-written migrations runner
  migrations/      — Ordered, versioned migrations (m####_<name>.py)
    m0001_initial_content.py  — creates + seeds 5 content tables from JSON
    m0002_runtime_state.py    — creates 4 runtime-state tables (Phase 1.5)
    m0003_items_table.py      — relational items schema (Stage 2, Phase 2.2)
    m0004_bag_column.py       — bag JSON column + lockpick seed (Stage 2, Phase 2.3)
    m0005_chests.py           — chest_content + chest_state tables (Stage 2, Phase 2.7)
    m0006_panel_coords.py     — additive panel_x/panel_y columns on entity_state + source_state; chests re-seeded with panel coords (Stage 3, Phase 3.2)
  save_manager.py  — SaveManager: snapshot() + restore() for world runtime state
  context.py       — GameContext: owns Database, 5 SqliteDao instances, and SaveManager
  dao.py           — Dao (JSON, legacy/fallback) + SqliteDao (LINQ-style query API over a table)
  loader.py        — Generic JSON loader (used by the seed migration)
  protocols.py     — IEntityDao / IContext Protocols
  models.py        — Typed dataclasses (AbilityDef, ItemDef, EntityDef)
  *.json           — Canonical seed content (entities, abilities, items, needs, sources, chests)
  chests.json      — Stage 2 chest seed definitions (3 chests: supply, forest_cache, goblin_hoard)
  rooms.json       — Stage 3 room definitions (9 rooms for Panel(0,0)); loaded by RoomRegistry (Phase 3.1)
  panels.json      — Stage 3 panel registry (Panel(0,0) = Starting Area, 4 null edges); loaded by PanelLoader (Phase 3.2)
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

> The `.db` is a gitignored runtime artifact. The JSON files are the version-controlled source of truth. Delete `lucentforge.db` for a complete fresh start (m0001 + m0002 re-run on next launch).

## Migrations

`db.py` records applied versions in `schema_migrations` and runs pending ones in order on startup (idempotent). Add a new step as `migrations/m####_<name>.py` exposing `migrate(conn)`, then register it in `migrations/__init__.py`. Hand-edit migrations deliberately (TheForge discipline) — review before relying on them.

## Phase 1.5 — World-State Save/Load

`SaveManager` (`save_manager.py`) writes/reads runtime simulation state using the 4 tables from `m0002`:

| Table | Key | What it stores |
|-------|-----|----------------|
| `world_state` | `slot_id` | Clock tick, goblin threat, town state |
| `source_state` | `(slot_id, label)` | Finite source stock levels |
| `entity_state` | `(slot_id, entity_id)` | HP, position, needs, traits, chemicals, memory |
| `game_state` | `slot_id` | Defeated NPCs, combat cooldowns |

The `memory` column is a nested JSON blob `{sources, regions}` (C0049): source-quality memory plus per-region affinity-comfort EMA. Legacy flat blobs (`{label: {…}}`) are detected and upgraded on restore. `chemicals` (including `affinity_strain`) serializes generically, so new chemicals persist without a schema change.

All tables include a `slot_id INTEGER` column — Phase 1.5 uses slot 0; Phase 1.6 adds a slot-picker UI without schema changes.

**API (via `ctx.save_manager`):**

```python
ctx.save_manager.snapshot(world_sim, sources, controllers, player, player_needs,
                           defeated_npcs, combat_cooldowns, slot_id=0)   # write a slot
ctx.save_manager.restore(slot_id=0)     # -> dict | None (None = no save in that slot)
ctx.save_manager.has_save(slot_id=0)    # -> bool
ctx.save_manager.delete_save(slot_id=0)

# Phase 1.6 — lightweight display queries for the slot-picker UI
ctx.save_manager.get_slot_info(slot_id)          # -> {slot_id, tick_count, town_state, saved_at} | None
ctx.save_manager.list_all_slots([0, 1, 2, 3])    # -> list[dict | None], parallel to slot_ids
```

**Boundary rule:** `m0002`–`m0005` runtime tables are never seeded from JSON. `chest_content`/`chest_state` (m0005) are seeded from `chests.json` at game init via `create_chest_registry()`. Delete `lucentforge.db` for a clean slate; Stage 2 migrations require a fresh DB (no save-transform path).

**Integration in main.py:**
- Launch: `restore()` → `apply_save()` if save exists; sprites of defeated NPCs removed
- `S` key: manual snapshot
- Autosave: every `AUTOSAVE_INTERVAL` sim ticks (default 1800, ~5 sim-minutes)
- Quit: `SAVE_ON_QUIT=True` writes final snapshot before exit

## SOLID

- **S**: `db.py` connects/migrates, `dao.py` queries, JSON seeds, migrations evolve schema.
- **O**: new content via JSON; new schema via a new migration file — no edits to existing code.
- **L**: `Dao` and `SqliteDao` are interchangeable behind `IEntityDao`.
- **I**: consumers depend only on the small DAO query surface.
- **D**: systems depend on `GameContext` / DAO abstractions, not on storage details.
