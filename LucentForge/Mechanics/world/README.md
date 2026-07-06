# Mechanics/world — World Simulation Layer

Simulation objects + tile map. `world/` has no dependency on `renderer/` or `ai/`.
WorldSim ticks drive the simulation; `tile_map.py` owns the spatial grid.

## Modules

| File | Contents |
|---|---|
| `world_sim.py` | `WorldSim` — orchestrator ticking clock, resources, threat, town in bible-prescribed order |
| `simulation_clock.py` | `SimulationClock` — tick-based time, day count, DAY/NIGHT phase |
| `resource_state.py` | `ResourceState` — aggregates food_total from finite source stocks; ticks regen |
| `goblin_threat.py` | `GoblinThreat` — hunger-driven 0-100 threat, PASSIVE/RAIDING/CROSSING stage transitions |
| `town.py` | `Town` — STABLE/STRAINED/COLLAPSING derived from food, population, threat |
| `tile_map.py` | Procedural 18×18 tile map, river, bridges, region tags, obstacle placement, `place_chests()`; tile constants include `CHEST=12` (Stage 2, Phase 2.7) |
| `pathfinder.py` | `bfs_path()` — 8-directional BFS used by NPC controllers |

## Tile constants

| Constant | Value | Notes |
|---|---|---|
| `WALL` | 1 | Impassable obstacle |
| `RIVER` | 2 | Water — blocks movement |
| `RBANK` | 3 | River bank — walkable thirst source |
| `BRIDGE` | 4 | Walkable water crossing |
| `CHEST` | 12 | Chest tile — blocks movement; interactable via `E` key (Phase 2.7) |

## Design rules

- `WorldSim` is the only tick entry point — no caller should tick sub-objects directly.
- `TileMap.get_need_sources()` returns the authoritative list of `NeedSource` objects.
- `place_chests()` stamps `CHEST` tiles at seeded positions; `BFS_BLOCKED` set includes `CHEST` so pathfinder treats chests as impassable.
- `ROWS = 18`, `COLS = 18` — grid expansion is a future arc item.
