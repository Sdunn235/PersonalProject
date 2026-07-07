# LucentForge Rooms & Panels Addendum v1

**Created:** 2026-07-06 | **Stage:** 3.0 | **Authority:** LucentForge Bible (Foundation v1 + this addendum)

---

## Purpose

This addendum defines the Room, Panel, and Zone-crossing architecture for Stage 3 of the TheForge Combine Arc. It establishes the terminology, data model, event system, and world-coordinate system that all Stage 3+ phases build on. Cite this addendum alongside the Foundation when implementing room/panel/zone features.

Section numbering: §R1–§R8.

---

## §R1 — Room, Panel, and Region: Three Distinct Concepts

These three terms are related but not interchangeable. Getting them right is the foundation of the Stage 3 architecture.

### Panel

> A Panel is the fundamental unit of the world grid. It is one 18×18 tile map — the same fixed scale everywhere in the world.

- The current map (introduced in Heartbeat-2) is **Panel(0, 0)**.
- Panels are addressed by a two-integer grid coordinate: `(panel_x, panel_y)`.
- The world expands by defining adjacent panels at `(panel_x ± 1, panel_y)` or `(panel_x, panel_y ± 1)`.
- Every piece of world content — chests, entities, sources, rooms — lives in a specific panel via `(panel_x, panel_y)` coordinates.
- Panels do not have internal scale variation. An 18×18 panel in the forest is the same tile size as an 18×18 panel in the town. This is a design invariant.

### Room

> A Room is a named semantic zone within a panel. It is the game-meaningful grouping of tiles that carries identity, type, and behavior.

- A Room has: an `id` (unique string), a `name` (display string), a `RoomType`, a `description` (text, rendered Stage 5+), `(panel_x, panel_y)` to identify which panel it belongs to, and `tile_bounds` defining its tile rectangle.
- Rooms are defined in `Mechanics/data/rooms.json` and loaded by `Mechanics/world/rooms.py`.
- A Room is NOT a visual object. It is a semantic tag that tiles resolve to.
- Multiple Rooms may exist in one Panel. All tiles in Panel(0,0) that return a non-null region belong to exactly one Room.

### Region

> A Region is the raw string tag returned by `TileMap.get_region(col, row)`.

- Regions are Python implementation detail. They exist in `tile_map.py._assign_regions()` and were defined in the Heartbeat arc.
- Regions (`forest`, `town_center`, etc.) map 1:1 to Rooms in Stage 3. The Region tag is how the runtime finds which Room a tile belongs to.
- Stage 3 does NOT rename or restructure regions. The Region → Room mapping is expressed in `rooms.json` via `tile_bounds`.

### Summary

| Concept | Scale | Defined by | Carries semantics? |
|---|---|---|---|
| Panel | 18×18 tile map unit | `panels.json`, world grid | Location only |
| Room | Named zone within a panel | `rooms.json`, `RoomRegistry` | Yes — type, name, description |
| Region | Raw tile tag | `tile_map._assign_regions()` | Implementation detail only |

---

## §R2 — Multi-Panel World Model (Zelda Pre-N64)

### Design model: Zelda pre-N64, not Final Fantasy

LucentForge's world is a continuous flat grid of 18×18 panels. There is no world map. There is no zoom change. The world exists at one scale, always.

- Walk to the east edge of Panel(0,0) → the east edge of Panel(1,0) becomes visible (future arc).
- The resolution, tile size, and perspective do not change.
- Both the player and NPCs exist at the same tile scale at all times.
- **This is the Zelda pre-N64 model.** Not Zelda: A Link to the Past (same) — but specifically the philosophy that the overworld and sub-areas share one continuous scale, not the Final Fantasy model (world map at macro scale, then zoom into dungeon at different scale).

### Panel coordinate system

```
(panel_x - 1, panel_y)    (panel_x, panel_y)    (panel_x + 1, panel_y)
       WEST                    CURRENT                    EAST

(panel_x, panel_y - 1) = NORTH
(panel_x, panel_y + 1) = SOUTH
```

Panel coordinates use standard screen-space origin (0,0) at top-left. Panel (0,0) = the current starting area.

### World coordinate

The canonical locator for any object in the world is:

```python
WorldPos(panel_x: int, panel_y: int, col: int, row: int)
```

- `panel_x, panel_y` — which panel
- `col, row` — tile position within that panel (0–17)
- All current content in Panel(0,0) has `panel_x=0, panel_y=0`.

### Stage 3 scope boundary

Stage 3 establishes the **architecture** for the multi-panel world:
- Data model (Rooms, Panels, WorldPos)
- Database coordinates (m0006: panel_x/panel_y columns on chests/entities/sources)
- Zone entry/exit events
- PanelLoader stub (proves the transition model compiles)

**Stage 3 does NOT define any new panel content.** No Panel(1,0) is created. The transition stub returns `False` — no transitions actually fire. The architecture is proven; the content is Stage 3.5+.

---

## §R3 — RoomType Taxonomy

> RoomType captures the semantic character of a zone. It drives AI behavioral responses, future event triggers, and world-simulation classification.

### Values

| RoomType | Region mapped | Meaning | Stage 3 AI trigger |
|---|---|---|---|
| `WILDERNESS` | `forest` | Untamed land outside civilization | None |
| `SETTLEMENT` | `town_center`, `homes`, `town_outskirts` | Civilized, inhabited zone | Goblins entering → threat nudge |
| `GOBLIN_TERRITORY` | `goblin_camp` | Claimed goblin zone | Humans entering → fear injection |
| `BRIDGE` | `bridge` | River crossing — contested neutral ground | None (Stage 3) |
| `FARM` | `farm` | Agricultural production zone | Goblins entering → threat nudge |
| `STORAGE` | `storage` | Silo and stockpile zone | Goblins entering → threat nudge |
| `RIVER` | `river` | Water access — non-traversable except at bridge tiles | None |

### One region → one room → one RoomType

In Panel(0,0), every named region maps to exactly one Room, and each Room has exactly one RoomType. Future panels may define Rooms with the same RoomType in different locations — RoomType is the semantic class, not the identity.

### RoomType and AI

The AI behavioral triggers are defined in §R4 and implemented in Phase 3.5. Stage 3's RoomType does not change any existing AI logic until Phase 3.5.

---

## §R4 — ZoneCrossing Event Model

> A ZoneCrossing event fires when an entity's `current_room` changes. It is the integration point between the world data layer and every system that needs to react to movement.

### Event definition

```python
@dataclass
class ZoneCrossingEvent:
    entity_name: str
    from_room: RoomDefinition | None   # None = starting position (first tick)
    to_room: RoomDefinition | None     # None = entity outside any defined room
    tick: int
```

### ZoneTracker (Observer pattern)

`ZoneTracker` owns the crossing detection and notification:

```
ZoneTracker
  _current_rooms: dict[str, RoomDefinition | None]   # per entity
  subscribe(callback)
  check_and_fire(entities, tile_map, rooms, panel_x, panel_y, tick)
```

- `check_and_fire` is called once per tick from `WorldSim.update()`.
- For each entity: query `RoomRegistry.get_room_for_tile(panel_x, panel_y, col, row)`.
- If the result differs from `_current_rooms[entity_name]`: fire all subscribed callbacks with a `ZoneCrossingEvent`, then update `_current_rooms`.
- The event fires **edge-triggered** (once on change), not level-triggered (not every tick while in the room).

### Consumers (progressive, Phases 3.3–3.5)

| Consumer | Trigger | Phase |
|---|---|---|
| `npc_logger.py` | `[ZONE] Entity entered Room (tick N)` | Phase 3.3 |
| Observation panel ZONE section | Player's current room name | Phase 3.4 |
| HUD zone flash | Room name appears at top-center on player crossing | Phase 3.4 |
| `ZoneAIResponder` | Chemical injection on zone entry | Phase 3.5 |

### Player tracking

The player entity is tracked by `ZoneTracker` alongside NPCs. `check_and_fire` accepts any entity list that includes player. Player zone crossings fire the same event type — they're just subscribed by the HUD flash and observation panel in addition to the logger.

---

## §R5 — TheForge Reconciliation (Room/Panel Layer)

TheForge (`ConsoleRpgEntities/Models/Containers/Room.cs`) has an existing Room model. This section records how its concepts map to LucentForge's Stage 3 architecture.

| TheForge concept | LucentForge Python (Stage 3) | Notes |
|---|---|---|
| `Room.GridX: int?` | `panel_x: int` in `WorldPos` | The grid coordinate of a panel, not a tile |
| `Room.GridY: int?` | `panel_y: int` in `WorldPos` | Same |
| `Room.Description: string` | `RoomDefinition.description: str` | Seeded in Stage 3; rendered in Stage 5+ (dialogue arc) |
| `Room.Name: string` | `RoomDefinition.name: str` | Display name of the zone |
| `Door` (bidirectional) | `PanelEdge` + `PanelTransition` | A Door between rooms → walking off a panel edge. Stub in Stage 3. |
| `Room.Characters` | `entity.panel_x/panel_y` | Entities track their own panel coords via m0006 columns |
| `Room.DoorsAsA/B / AllDoors` | `PanelLoader.get_adjacent_panel(...)` | The transition graph is in `panels.json` + `PanelLoader`. Stub in Stage 3. |
| Items on the floor | Stage 4+ | Room-as-Container for floor loot is a Stage 4 arc item (§R8) |
| Room TPH (Room is a Container) | Stage 4+ | Container semantics deferred; `RoomDefinition` is not a container in Stage 3 |

### Why the mapping works

TheForge's `Room.GridX/GridY` indexed rooms in a discrete room graph. LucentForge treats the world as a continuous panel grid — `GridX/GridY` become `panel_x/panel_y` in the coordinate system. The room graph becomes the panel adjacency graph in `panels.json`. This is structurally equivalent at the model level; the difference is scale (TheForge = small discrete rooms; LucentForge = 18×18 panel tiles).

---

## §R6 — Background Simulation Blueprint (Stage 3.5+)

Stage 3 ships active-panel-only simulation: entities tick and render only in the currently loaded panel. This section documents the future arc design so Stage 3's stubs are pointed in the right direction.

### Simulation scope model

```python
class SimulationScope(enum.Enum):
    ACTIVE     = "active"      # full tick + sprite rendering
    BACKGROUND = "background"  # tick-only, no sprites, no display
```

### Design intent (future arc)

- When multiple panels are defined and adjacent panels are loaded, off-screen panels run at `BACKGROUND` scope.
- Entities in `BACKGROUND` panels tick their needs, AI states, and world interactions — but no sprites are rendered.
- On panel transition, the arriving panel upgrades to `ACTIVE` and the departing panel downgrades to `BACKGROUND`.
- The swap must happen within a single tick to avoid state corruption.

### Stage 3 contract

Stage 3's `PanelLoader` stub contains the `SimulationScope` blueprint in comments. No runtime switching is implemented. Stage 3 ships `SimulationScope.ACTIVE` only — the enum exists as documentation, not as a runtime switch.

When Stage 3.5 implements real panel loading, it will:
1. Add `SimulationScope` as a runtime field on `PanelConfig`
2. Make `WorldSim.update()` scope-check before ticking entities
3. Make `main.py` render-check before drawing sprites

---

## §R7 — History Tracking Seed (Stage 4+)

> This section documents a hook, not an implementation. The data design is recorded here so Stage 4 has a known starting point.

### Concept

LucentForge entities should accumulate a history of where they've been and what they've done there. This history is a simulation artifact — it answers questions like "has Gruk been to town_center before?" and "what happened the last time Elara entered the goblin_camp?"

### Planned data shape (Stage 4+)

```python
# On entity:
entity.visited_rooms: set[str]   # room IDs visited at least once

# New DB table (Stage 4 migration):
zone_outcomes(
    entity_id TEXT,
    room_id    TEXT,
    tick       INTEGER,
    outcome    TEXT              # e.g. "fled", "fought", "foraged"
)
```

### Stage 3 contract

Stage 3 does NOT implement visited rooms or zone_outcomes. The `ZoneCrossingEvent` fires and logs — that log is the evidence that the plumbing works. The history system builds on those events in Stage 4.

---

## §R8 — Out-of-Scope Register

These features are intentionally deferred. This list is the authority on what Stage 3 does NOT include.

| Feature | Deferred to | Reason |
|---|---|---|
| Floor loot (items on the ground in a room) | Stage 4+ | Depends on the Room-as-Container model from TheForge; Stage 4 items arc |
| Room descriptions in UI | Stage 5+ | `RoomDefinition.description` field is seeded; rendered during dialogue arc |
| Full history tracking (visited_rooms, zone_outcomes table) | Stage 4+ | §R7 documents the design; Stage 3 only fires the ZoneCrossing events that feed it |
| Multi-panel content | Stage 3.5+ | Panel(0,0) is the only defined panel in Stage 3; new panels are Stage 3.5+ content |
| Background simulation (off-screen tick) | Stage 3.5+ | §R6 blueprints the design; Stage 3 ships ACTIVE-only |
| Camera scrolling | Future arc | Panel grid model defers this cleanly; not needed until panels exceed screen size |
| World death / respawn | Stage 4+ | Traps still clamp HP to 1; death + respawn is a Stage 4 arc item (§A8 from items addendum) |
| Panel-to-panel NPC migration (NPCs crossing panel edges) | Stage 3.5+ | Entities are always panel-local in Stage 3; migration routing needs background sim |
| Trap type escalation (MAGICAL, POISON, ELECTRIC) | Stage 4+ | TrapType enum has these values; mechanics are Stage 4+ |

---

## Extension Protocol

When Stage 3.5+ adds new panel or room concepts:

1. Extend `rooms.json` with new panel definitions and room entries.
2. Extend `panels.json` with new panel edges and adjacency definitions.
3. Update this addendum with new §R sections if behavioral doctrine changes.
4. Update `lucentforge_terminology_map_v_1.md` with any new reconciled terms.
5. Run the terminology reconciliation pass before implementation (same protocol as Stage 2).
