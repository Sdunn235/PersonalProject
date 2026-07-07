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
| `rooms.py` | `RoomType` enum, `RoomDefinition` dataclass, `RoomRegistry` — Stage 3 room data layer (Phase 3.1) |
| `world_coord.py` | `WorldPos` dataclass, `PanelEdge` enum, `PanelConfig` dataclass, `PanelLoader` stub — Stage 3 world coordinate + panel registry (Phase 3.2) |

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

## World coordinate system (Stage 3, Phase 3.2+)

`world_coord.py` introduces multi-panel world addressing on top of the room layer.

| Type | Purpose |
|---|---|
| `WorldPos(panel_x, panel_y, col, row)` | Fully-qualified tile address in the multi-panel world |
| `PanelEdge` | Transition direction enum: `NORTH`, `SOUTH`, `EAST`, `WEST` |
| `PanelConfig` | Panel definition (id, name, panel_x, panel_y, edge adjacency) |
| `PanelLoader` | Panel registry; `can_transition()` / `get_adjacent_panel()` stubs returning False/None in Stage 3 |

`ctx.panel_loader` — `PanelLoader` instance (loaded from `Mechanics/data/panels.json`) owned by `GameContext`.
`ctx.current_panel` — `(panel_x, panel_y)` tuple tracking the active panel (always `(0, 0)` in Stage 3).

**Transition stub:** `PanelLoader.can_transition()` always returns `False`; `get_adjacent_panel()` always returns `None`. Panel(0,0) defines four `null` edges in `panels.json`. Stage 3.5+ wires real transitions.

## Room system (Stage 3, Phase 3.1+)

`rooms.py` introduces the semantic room layer on top of the tile grid.

| Concept | Lives in | Purpose |
|---|---|---|
| Region | `tile_map._assign_regions()` | Raw tile tag (`"forest"`, `"goblin_camp"`, etc.) — implementation detail |
| Room | `rooms.py` + `rooms.json` | Named semantic zone: `RoomDefinition(id, name, room_type, description, tile_bounds, region_tag)` |
| RoomType | `rooms.py` | `WILDERNESS`, `SETTLEMENT`, `GOBLIN_TERRITORY`, `BRIDGE`, `FARM`, `STORAGE`, `RIVER` |

**Lookup strategy:**
- `RoomRegistry.get_room_for_region(panel_x, panel_y, region_tag)` — O(1) accurate lookup; use in `ZoneTracker` (Phase 3.3+)
- `RoomRegistry.get_room_for_tile(panel_x, panel_y, col, row)` — bounding-box approximation (smallest rooms first); accurate for rectangular overlay zones, approximate for winding river/bridge boundaries
- `ctx.rooms` — `RoomRegistry` instance owned by `GameContext`
