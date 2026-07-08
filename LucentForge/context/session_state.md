# Session State — Last updated: 2026-07-06 (Stage 3 Phase 3.3 COMPLETE — zone crossing Observer)

## Forge-Combine Arc (TheForge → LucentForge) — Stage 1 COMPLETE, Stage 2 COMPLETE, Stage 3 IN PROGRESS

### Stage 3 Summary (Rooms as Zones / Multi-Panel World)

**Approved plan:** `C:\Users\Shawn\.claude\plans\caelum-session-start-date-groovy-bunny.md`

| Phase | Commit | Description | Status |
|-------|--------|-------------|--------|
| Phase 3.0 | C0021 | Rooms/Panels addendum + terminology map §7 + session_state update (doc-only) | COMPLETE |
| Phase 3.1 | C0022 | `Mechanics/world/rooms.py` — RoomType, RoomDefinition, RoomRegistry; `Mechanics/data/rooms.json` | COMPLETE |
| Phase 3.2 | C0023 | `Mechanics/world/world_coord.py` — WorldPos, PanelEdge, PanelConfig, PanelLoader stub; panels.json; m0006 additive migration (panel_x/panel_y on entity_state + source_state + chests.json) | COMPLETE |
| Phase 3.3 | C0024 | `Mechanics/world/zone_events.py` — ZoneCrossingEvent, ZoneTracker Observer; WorldSim owns zone_tracker; npc_logger.log_spatial_zone subscriber; main.py check_and_fire in game loop | COMPLETE |
| Phase 3.4 | C0025 | `settings.py` ZONE_LABEL_DURATION; O-panel ZONE section (player + per-NPC room); HUD room-name flash subscriber; main.py zone_flash countdown | COMPLETE |
| Phase 3.5 | C0026 | `Mechanics/ai/zone_ai.py` ZoneAIResponder (anger nudge: goblin→civilized; fear: human→goblin_territory); main.py `_register_zone_subscribers()` helper (fixes New-Game tracker re-subscribe gap; wires log_spatial_zone + flash + zone_ai) | COMPLETE |
| Phase 3.6 | — | PanelLoader architecture stub; edge detection in main.py; panels.json | — |
| Phase 3.7 | — | Stage 3 closeout — docs, smoke suite, full regression | — |

**Stage 3 key decisions:**
- Zelda pre-N64 model: current 18×18 map = Panel(0,0); world expands by walking off panel edges (same scale everywhere)
- Stage 3 = architecture only — no new panel content; PanelLoader.can_transition() returns False
- m0006 is additive (ALTER TABLE ADD COLUMN panel_x/panel_y DEFAULT 0) — no delete-DB needed
- World-global coordinates: `WorldPos(panel_x, panel_y, col, row)` for all content
- Entry/exit output: console [ZONE] + observation panel + HUD flash + light AI response (progressive phases 3.3–3.5)
- TheForge Room-as-Container (floor loot) → Stage 4+; Room.Description → Stage 5+

**Stage 3 new files (planned):**
- `Mechanics/world/rooms.py` — RoomType enum, RoomDefinition dataclass, RoomRegistry
- `Mechanics/data/rooms.json` — 9 room definitions for Panel(0,0)
- `Mechanics/world/world_coord.py` — WorldPos dataclass, PanelEdge enum, PanelLoader stub
- `Mechanics/data/panels.json` — panel registry seed (Panel(0,0), 4 null edges)
- `Mechanics/data/migrations/m0006_panel_coords.py` — additive column adds
- `Mechanics/world/zone_events.py` — ZoneCrossingEvent, ZoneTracker
- `Mechanics/ai/zone_ai.py` — ZoneAIResponder
- `scratchpad/run_stage3_tests.py` — Stage 3 smoke suite

**Stage 3 new bible docs (Phase 3.0, C0021):**
- `docs/bible/lucentforge_rooms_panels_addendum_v1.md` — §R1–§R8 (Room/Panel/ZoneCrossing doctrine)
- `docs/bible/lucentforge_terminology_map_v_1.md` §7 — Stage 3 term reconciliation (Panel, Room, RoomType, WorldPos, PanelEdge, ZoneCrossing, ZoneTracker, PanelLoader)

## Forge-Combine Arc (TheForge → LucentForge) — Stage 1 COMPLETE, Stage 2 COMPLETE

### Stage 2 Summary
| Phase | Commit | Description | Status |
|-------|--------|-------------|--------|
| Phase 2.0 | C0012 | Terminology map + items bible addendum (doc-only) | COMPLETE |
| Phase 2.1 | C0013 | `Mechanics/items/` domain package (enums, models) | COMPLETE |
| Phase 2.2 | C0014 | m0003 relational schema + ItemRepository | COMPLETE |
| Phase 2.3 | C0015 | Services + persistence (InventoryService, EquipmentService) | COMPLETE |
| Phase 2.4 | C0016 | Combat refactor + defect fixes (NPC bag bug, armor-DEF, weapon-dict) | COMPLETE |
| Phase 2.5 | C0017 | Inventory UI modal (I key + pause menu integration) | COMPLETE |
| Phase 2.6 | C0018 | §12.2 outcome resolver (OutcomeResolver, OutcomeCheck) | COMPLETE |
| Phase 2.7 | C0019 | Chests, locks, traps, keys on map (E key interaction) | COMPLETE |
| Phase 2.8 | C0020 | Stage 2 closeout — docs, smoke suite, full regression | COMPLETE |

**Stage 2 key decisions:**
- TheForge = structural blueprint, bible = naming/semantics authority; every import reconciled against terminology map
- Services NOT in GameContext (decision 13) — held in `main.py` local vars
- No world death in Stage 2 — traps clamp HP to 1 (`max(1, hp - trap_damage)`)
- Stage 2 requires a fresh `lucentforge.db` — delete DB and relaunch to apply m0003+ migrations
  (JSON stays canonical; delete `lucentforge.db` = reseed; no save-transform path)

**Stage 2 key bindings:**
- `I` — Opens inventory/equipment modal (also reachable from pause menu)
- `E` — Interact with orthogonally adjacent chest (open, pick lock, disarm trap, use key, loot)
- `O` — Toggle observation panel (Heartbeat-6)
- `S` — Manual save
- `TAB` — Cycle right-side HUD between entities
- `ESC` — Pause menu (Resume / Inventory / Save / Load / New Game / Quit)

**Approved plan:** `C:\Users\Shawn\.claude\plans\caelum-session-start-zesty-tome.md` (Phases 2.0–2.8) — COMPLETE.

### Stage 1 Summary
| Phase | Commit | Description | Status |
|-------|--------|-------------|--------|
| Phase 1 | C0003 | SQLite persistence backbone (DAO swap, migrations, seeding) | COMPLETE |
| Phase 1.5 | C0005 | World-state save/load (SaveManager, apply_save, autosave) | COMPLETE |
| Phase 1.6 | C0006 | Save slot UI (run_load_menu + run_save_menu modals, 4 slots) | COMPLETE |
| Phase 1.7 | C0007 | Pause menu modal (Resume / Save / Quit, _paused_quit flag) | COMPLETE |
| Phase 1.8 | C0008 | Load + New Game from pause (_spawn_entities closure, sprite revival) | COMPLETE |

---

Heartbeat arc is closed. Stage 1 (SQLite/persistence/UI) is complete as of 2026-07-04.

### Phase 1 — SQLite Persistence Backbone — COMPLETE (2026-06-29, C0003)
- Storage swapped from flat JSON to **SQLite** behind the existing DAO API — the game runs identically.
- `Mechanics/data/db.py`: `Database` — sqlite3 connection + idempotent migrations runner (`schema_migrations` tracks applied versions).
- `Mechanics/data/migrations/m0001_initial_content.py`: creates 5 document tables (`entities`, `abilities`, `items`, `needs`, `sources` — each `id TEXT PK, data JSON`) and seeds them from the canonical JSON files.
- `Mechanics/data/dao.py`: new `SqliteDao` (same lambda query API as `Dao`; rows load into memory as dicts so **no call site changed**; `add/update/delete/save` write through). JSON `Dao` kept for hardcoded fallbacks.
- `Mechanics/data/context.py`: `GameContext` opens the DB, runs migrations, owns DAOs for all 5 collections.
- `Mechanics/needs/need_factory.py`: uses `ctx.needs`. `.gitignore`: `*.db`.
- **DB is a gitignored runtime artifact; JSON stays canonical.** Reseed = delete `lucentforge.db` + rerun.
- Verified: fresh-seed, idempotent re-run, JSON round-trip, 36k-tick regression crash-free; confirmed in-game.

### Phase 1.5 — World-State Save/Load — COMPLETE (2026-06-30)
- **`m0002_runtime_state.py`**: 4 new tables (`world_state`, `source_state`, `entity_state`, `game_state`), all with `slot_id INTEGER` for Phase 1.6 slot-picker UI. Migration registered in `migrations/__init__.py`.
- **`Mechanics/data/save_manager.py`**: `SaveManager` Facade — `snapshot()` (single atomic transaction), `restore()` (returns `dict | None`), `has_save()`, `delete_save()`. Owned by `GameContext` as `ctx.save_manager`.
- **`Mechanics/bootstrap.py`**: `apply_save()` — patches live `WorldSim`, sources, `NPCController` list, player, `defeated_npcs`, `combat_cooldowns` in place from restore data. NPCs drop to IDLE on load (re-evaluate within 1–2 ticks). Full state machine restore is Phase 1.6+.
- **`main.py`**: restore on launch → `apply_save()` → kill sprites of defeated NPCs. `S` key = manual save. Autosave every `AUTOSAVE_INTERVAL` (1800) sim ticks. `SAVE_ON_QUIT=True` writes final snapshot before exit.
- **What is saved**: clock tick/accumulator, threat level/stage, town state, finite source stocks, per-entity hp/x/y/cycles/mp/equipment/needs/traits/chemicals/memory, defeated NPC set, combat cooldowns.
- **Boundary preserved**: m0001 content tables untouched; JSON stays canonical. Delete `lucentforge.db` → fresh game.
- **Verified**: 3-test headless smoke suite (`scratchpad/smoke_test.py`) — fresh-seed, round-trip (500 ticks → snapshot → restore → assert), autosave interval. All PASS. Live DB migrated cleanly.
## Current status: STABLE — Stage 1 COMPLETE, Stage 2 COMPLETE, Stage 3 NEXT (rooms-as-zones)

## What works right now
- `py main.py` (Windows PowerShell) — 1024x768 window, 576x576 level centered with border zones
- **Grid**: 18x18 tiles, 32px — procedural region-colored map (no background image)
- **River barrier**: 28 river tiles winding cols 4-7, blocks all movement
- **Two 2x2 bridges**: North (rows 4-5) and south (rows 11-12) — walkable crossings
- **Region grid**: Every tile tagged (forest, town_center, town_outskirts, homes, farm, storage, goblin_camp, river, bridge)
- **Zone labels**: "Town", "Homes", "Farm", "Goblins", "Forest", "Silo" rendered at zone centers
- **Hand-placed obstacles**: 30 trees/rocks placed to fit zone layout
- **River = water source**: Bridge tiles serve as thirst/water source (8 tiles)
- **Need sources**: FOOD (1,1) forest, FARM (14,3) civilized NE, WATER via bridges, BED (11,11) town center, CAMP (2,15) wild SW, FORAGE (0,13) goblin camp
- **Spawns**: Player (8,1), Alder (12,7), Sylva (13,16), Grom (10,10), Elara (16,12), Gruk (2,13), Skrix (3,14), Ignarix (1,8)
- **Player collision**: arrow-key movement checks tile grid; cannot walk through obstacles or river
- **Entity separation**: NPCs check occupied tiles each frame
- **NPCs pathfind around obstacles** via 8-directional BFS (river blocking is automatic)
- **Directional walking animation**: all sprites animate (down/left/right/up), idle on first frame
- **Combat**: walk into NPC -> full-screen RPG combat, nested menus
- **Spell system**: MP cost, MAG scaling, elemental types
- **Equipment system**: weapon + armor from items.json
- **HP/SP/MP persistence**: carry over between combats
- **HUD**: Tab key cycles right-side panel, top-left day/HP/SP/MP display
- **World-map stat bars**: all sprites show 3 stacked bars above them
- **Persistent inventory** — items survive between combats and save/load (Stage 2, Phase 2.3)
- **Equipment UI** — `I` key opens modal; equip/unequip from world and pause menu (Phase 2.5)
- **Armor mitigation** — gear mods reach damage calculation; fights run longer vs armored targets (Phase 2.4)
- **NPCs use potions** — Alder/Grom draw from their bags in combat; consumables are finite (Phase 2.4)
- **Chests on map** — 3 seeded chests (town_supply col 11/row 8, forest_cache 2/4, goblin_hoard 2/14) (Phase 2.7)
- **Lockpicking** — DEX-based §12.2 check; lockpick consumed on failure (Phase 2.7)
- **Trap disarm** — DEX check; trap fires on failure then opens anyway — no softlock (Phase 2.7)
- **Key items** — brass_key gates goblin_hoard; travel_boots + iron_helm acquirable in-world (Phase 2.7)

## Heartbeat-1 (World Orchestration Layer)
- **SimulationClock**: tick-based time, day count, DAY/NIGHT phase
- **ResourceState**: H5 refactored — aggregates food_total from actual source stocks
- **GoblinThreat**: 0-100 threat_level, PASSIVE/RAIDING/CROSSING stage derivation
- **Town**: read-derived STABLE/STRAINED/COLLAPSING from food, population, threat
- **WorldSim**: orchestrator ticking all four objects in bible-prescribed order each frame
- **Console output**: heartbeat status line every 30 sim ticks, NPC names on all event logs

## Heartbeat-2 (Map Enhancement)
- **Procedural map**: region-colored ground tiles replaced Tower Defense level01.png + obstacle CSVs
- **Winding river**: 2-tile wide barrier, wild (west) / civilized (east) geography
- **Two bridges**: 2x2 crossings, north near town, south near wild food source
- **Region tags**: metadata grid — forest, town_center, homes, farm, storage, goblin_camp, river, bridge, town_outskirts
- **Zone labels**: rendered at region centers with semi-transparent background
- **River as water**: bridge tiles are the thirst source — NPCs path to bridges to drink

## Heartbeat-3 (NPC Decision Loop)
- **NPC Memory** (`ai/memory.py`): EMA-based source quality tracking per NPC. Records outcome quality after each need satisfaction.
- **Outcome Interpretation** (`ai/interpreter.py`): Scores 0.0-1.0 based on need urgency at decision time, distance traveled, interruptions, and personality filters.
- **Source Selection** (`needs/source_selector.py`): Weighted scoring: 40% distance + 30% memory + 20% stock + 10% novelty.
- **Trait Drift** (`entities/traits.py`): `drift()` shifts traits on outcomes, `decay_toward_neutral()` prevents runaway. Clamped [0.05, 0.95].
- **Source Variety**: FARM (food, civilized NE, tiles 14-15,3-4) and CAMP (rough rest, wild SW, tiles 2-3,15-16) added as secondary sources.
- **Console logging**: `[DONE]` lines now include quality score and memory preference.
- **Headless-verified**: 18000-tick simulation confirmed memory accumulates, quality varies, traits drift, no crashes.

## Heartbeat-4 (Goblin Behavior)
- **Entity subtype** (`entities/base.py`): `subtype` field on Entity base class — goblins, humans, dragons distinguishable in code.
- **Behavior strategy** (`ai/behavior.py`): BehaviorStrategy ABC with HumanBehavior (default) and GoblinBehavior (threat-driven). Clean SOLID pattern, extensible to future factions.
- **Hunger-driven threat** (`world/goblin_threat.py`): GoblinThreat now driven by average goblin hunger, not a flat timer. Starving goblins = rising threat, fed goblins = slight decay. Stage transitions logged to console.
- **FORAGE source**: Weak food source at goblin_camp (0,13). Satisfaction=40 (vs 80 for FOOD), interaction_time=15s (vs 8s). Goblins eat here when passive.
- **PatrollingState** (`ai/states/patrolling.py`): PASSIVE behavior. Goblins wander goblin_camp, pause at waypoints, occasionally lurk near south bridge (20% chance). Transitions to IDLE on urgent needs or threat escalation.
- **RaidingState** (`ai/states/raiding.py`): RAIDING/CROSSING behavior. Goblins path to civilized food sources (FOOD at RAIDING, FOOD or FARM at CROSSING). Occupy source tile for `GOBLIN_RAID_DURATION` seconds, then retreat. **H5: now consumes source stock during occupation and partially feeds the goblin.**
- **Proximity fear** (`ai/proximity.py`): Goblins within `GOBLIN_FEAR_RADIUS` tiles of non-goblin NPCs inject fear chemical. Fear multiplies need urgency through fearfulness trait.
- **Source blocking**: Sources with a goblin standing on them are "contested" — score penalty of 90% in source selector. NPCs strongly avoid but aren't hard-blocked.
- **Threat memory** (`ai/memory.py`): `record_threat()` lowers source preference when NPC encounters a goblin near a source. Decays naturally via EMA.

## Heartbeat-5 (Resource Economy) — NEW
- **Finite food sources**: FOOD (200 capacity, 0.15/tick regen), FARM (300/0.25), FORAGE (80/0.05). WATER and BED remain infinite.
- **Source stock fields** (`needs/need_source.py`): `stock`, `capacity`, `regen_rate` on NeedSource. `is_finite` property, `consume()` and `regenerate()` methods.
- **Source-specific fill rates** (`needs/needs_system.py`): `fill_need()` now uses source's `satisfaction_amount` and `interaction_time` instead of generic `need.fill_rate`. Finite sources consume stock during fill.
- **Mid-depletion handling** (`ai/states/satisfying.py`): If a source depletes while an NPC is eating, NPC returns to IDLE and re-evaluates. Creates visible "searching for food" behavior.
- **Goblin raid consumption** (`ai/states/raiding.py`): Raiders consume source stock during occupation. Partially feeds goblin hunger (0.5x efficiency). Creates feedback loop: raids drain town food but reduce goblin threat.
- **Stock-weighted source selection** (`needs/source_selector.py`): 4-weight system — distance(40%) + memory(30%) + stock(20%) + novelty(10%). Depleted sources get stock_score=0.0, strongly avoided.
- **ResourceState refactored** (`world/resource_state.py`): food_total is now a live sum of all hunger-source stocks. `update()` calls `regenerate()` on all finite sources per sim tick.
- **Source stock bars**: Finite sources show a colored bar above their map position. Green > 50%, orange > 15%, red below. Uses existing `draw_stat_bar()`.
- **Silo placeholder**: SILO tile type at (11,9)-(12,9) in storage region. Visual only — storage mechanics deferred to Phase 6.
- **Layout tweak**: BED moved from (10,15) to (11,11) — closer to town center and farm area. Homes region updated.
- **Console logging**: `[ECON]` for depletion/regen milestones, `[DEPLETED]` for mid-meal interruptions, `[DONE]` includes stock info, `[WORLD]` food_total reflects real stocks.
- **Headless-verified**: 36000-tick simulation (2 days) — Town STABLE, threat reaches RAIDING (22.6), goblins escalate. No crashes.

## Heartbeat-5 Fixes (post-implementation)
- **Riverbank water access**: RBANK tile type — 7 walkable tiles adjacent to river as thirst sources. "RIVER" source label. Player and NPCs can drink at riverbank.
- **Depleted source spam fix**: Source selector filters depleted sources. IdleState cooldown (3-5s) prevents IDLE→MOVE→DEPLETED loop.
- **Retuned economy**: FOOD regen 1.5/tick (~450/day), FARM 3.5/tick (~1050/day), FORAGE 0.08/tick (~24/day). FARM sustains town. FORAGE depletes fast.
- **Faster threat escalation**: PASSIVE threshold 30→20, hunger threat weight 0.05→0.12. Goblins reach RAIDING by day 2.
- **Player source-aware fill**: PlayerController uses source-specific fill rates.

## Heartbeat-6 (Observation Layer) — NEW (2026-06-27)
- **Observation panel** (`renderer/observation_panel.py`): world-overview in the left margin — WORLD (day/town/food/threat+bar), SOURCES (finite stock bars), NPCS (per-character state + priority need + target). Toggle with `O` (default on).
- **Run-log** (`observation/run_logger.py`): `RunLogger` writes `logs/run_<timestamp>/world.csv` + `npcs.csv` every `RUN_LOG_INTERVAL` (30) sim-ticks, plus `summary.txt` (min food, peak threat, raid count, worst town, final NPC state) on exit.
- **Depletion-log de-dupe** (`needs/need_source.py`): `[ECON] … DEPLETED` is now edge-triggered (logs once on stock→0, re-arms only after >10% recovery). 86→6 lines over a 2-day run.
- **Settings/ignore**: `OBS_PANEL_*`, `TOWN_STATE_COLORS`, `RUN_LOG_INTERVAL`, `RUN_LOG_DIR`; new `.gitignore` (`logs/`).
- **Verified**: headless 36k-tick run crash-free (run-log cadence correct, panel render path exercised, summary written) + visual confirm by Shawn. **Heartbeat arc COMPLETE.**
- **Env**: Python 3.14.6 + pygame-ce 2.5.7; run `py main.py` (Windows PowerShell — `python3` unavailable).

## Heartbeat Arc Status
| Phase | Status |
|-------|--------|
| Heartbeat-1: World Orchestration | **Complete** |
| Heartbeat-2: Map Enhancement | **Complete** |
| Heartbeat-3: NPC Decision Loop | **Complete** |
| Heartbeat-4: Goblin Behavior | **Complete** |
| Heartbeat-5: Resource Economy | **Complete** |
| Heartbeat-6: Observation Layer | **Complete** |

## Known issues / next session work
1. **Visual test needed** — Heartbeat-5 + fixes passed headless tests but needs live visual verification (stock bars, silo tile, BED relocation, riverbank tiles, raid behavior)
2. **Humans eat from wild-side FOOD** — FOOD source at (1,1) is in forest. Human NPCs path there because it's closest. Realistic but may want FOOD on civilized side too.
3. **NPC idle wander** — NPCs stand still during cooldown when no food. Could add a wander/fidget behavior for visual polish.
4. **Heartbeat-6** — Observation Layer: UI panels, town stats, source stocks, threat/economy graphs
5. **Storage mechanics** — Phase 6: silo tile is placed but non-functional. Storage overflow, NPC food retrieval.
6. **NPC cultivation** — Phase 7: NPCs work the farm to boost production.
7. **Threat escalation pacing** — Threat went 10→15.7 in 1 day. Still PASSIVE. May want faster escalation or lower FORAGE to force raids sooner.
8. **Grid expansion** — 18x18 may be too small for individual buildings, farm plots. Separate future task.
9. **Camera scrolling** — Shawn wants scroll/pan for larger maps. Future phase.
10. **Buff spells** — barrier/shield spells not yet implemented
11. **Spell learning** — no way to learn new spells during gameplay
12. **Element resistances** — elements on spells but no resistance system on entities
13. **World death deferred** — traps clamp HP to 1; full death + respawn is a Stage 4+ arc item (§A8)
14. **Durability decay deferred** — `durability` field exists on DurableItem; wear mechanics are Stage 4+
15. **Shops deferred** — no buy/sell economy yet; items only acquirable from chests

## How to run
```powershell
cd "C:\Users\Shawn\Documents\Workspace\Personal Project\LucentForge"
py main.py
```
Requires **pygame-ce** (`pip install pygame-ce`) — vanilla `pygame` fails to build on Python 3.14.
Arrow keys = move player; walk into NPC to trigger combat; `Tab` = cycle HUD; `I` = inventory; `E` = chest; `ESC` = pause.

## Architecture to preserve
- `Mechanics/` structure — do not flatten
- `Mechanics/data/` — JSON data layer, all content defined here
- `Mechanics/world/` — world simulation objects + tile map + region grid
- `needs/`, `biochem/`, `ai/` separation — keep separate
- `ReferenceFilesAndCode/` — read only forever

## Key file index
| File | Purpose |
|---|---|
| `main.py` | Game loop, WorldSim integration, combat trigger, proximity fear, stock bar rendering |
| `settings.py` | Display/simulation/world-sim/H3/H4/H5 tuning constants |
| `Mechanics/bootstrap.py` | Composition root — DI wiring including behavior strategy |
| `Mechanics/world/world_sim.py` | World orchestrator (clock, resources, threat, town) |
| `Mechanics/world/simulation_clock.py` | Tick-based time, day/night phase |
| `Mechanics/world/resource_state.py` | Source-based food aggregation + regen ticking |
| `Mechanics/world/goblin_threat.py` | Hunger-driven threat system with stage transitions |
| `Mechanics/world/town.py` | Settlement state evaluation |
| `Mechanics/world/tile_map.py` | Procedural map, river, regions, obstacles, zone rendering, source stock config |
| `Mechanics/world/pathfinder.py` | 8-directional BFS |
| `Mechanics/data/dao.py` | LINQ-style DAO |
| `Mechanics/data/entities.json` | Entity definitions (spawn positions, subtypes) |
| `Mechanics/data/abilities.json` | 12 ability definitions |
| `Mechanics/data/items.json` | Item templates |
| `Mechanics/ai/behavior.py` | BehaviorStrategy ABC + HumanBehavior + GoblinBehavior |
| `Mechanics/ai/controller.py` | NPC state machine + memory + decision tracking + behavior |
| `Mechanics/ai/memory.py` | NPC source-quality memory (EMA) + threat memory |
| `Mechanics/ai/interpreter.py` | Outcome quality scoring |
| `Mechanics/ai/proximity.py` | Goblin proximity fear injection + contested source detection |
| `Mechanics/ai/npc_logger.py` | Zone change + event logging (with NPC names) |
| `Mechanics/ai/states/idle.py` | Idle state with behavior strategy delegation |
| `Mechanics/ai/states/moving.py` | Pathfinding movement state |
| `Mechanics/ai/states/satisfying.py` | Need satisfaction with source-specific fill rates + stock consumption |
| `Mechanics/ai/states/patrolling.py` | Goblin camp patrol state |
| `Mechanics/ai/states/raiding.py` | Goblin raid state with source occupation + stock consumption |
| `Mechanics/needs/need_source.py` | NeedSource with stock/capacity/regen fields + consume/regenerate |
| `Mechanics/needs/source_selector.py` | 4-weight source selection (distance + memory + stock + novelty) |
| `Mechanics/entities/traits.py` | Personality traits with drift + decay |
| `Mechanics/combat/turn_processor.py` | Combat turn orchestrator |
| `Mechanics/renderer/combat_scene.py` | Full-screen combat UI |
| `Mechanics/renderer/health_bar.py` | draw_stat_bar + draw_health_bar (used for entity + source bars) |
| `Mechanics/needs/needs_system.py` | Need decay, source-aware fill, health drain, regen |
| `Mechanics/biochem/brain.py` | Chemical/drive system |
| `Mechanics/items/enums.py` | SlotType, BodySlot, WeaponType, ArmorWeight, ConsumableEffect, TrapType |
| `Mechanics/items/models.py` | Item TPH hierarchy (DurableItem → Weapon/Armor/Shield; Consumable) |
| `Mechanics/items/containers.py` | ItemStack, Inventory, EquipmentSet, Chest dataclass |
| `Mechanics/items/repos.py` | ItemRepository — typed SQLite access via `ctx.item_repo` |
| `Mechanics/services/inventory_service.py` | InventoryService — get_inventory, take_from, use_consumable, carry_weight |
| `Mechanics/services/equipment_service.py` | EquipmentService — equip/unequip, gear_mods(), weapon_profile() |
| `Mechanics/services/outcome.py` | OutcomeResolver, OutcomeCheck, OutcomeResult (§12.2 bounded-variance check) |
| `Mechanics/renderer/inventory_menu.py` | run_inventory_menu — I-key modal (Phase 2.5) |
| `Mechanics/renderer/chest_menu.py` | run_chest_menu — E-key chest/lock/trap/loot modal (Phase 2.7) |
| `Mechanics/bootstrap.py` | Composition root — create_item_services, create_chest_registry, rebuild_chest_registry |

## Bible reference
- `docs/bible/lucentforge_simulation_foundation_v_1.md` — philosophical constitution (§numbers = requirements)
- `docs/bible/lucentforge_sim_core_schema_v_1.md` — structural schema
- `docs/bible/lucentforge_micro_simulation_v_1.md` — prototype spec
- `docs/bible/heartbeat_convergence_vision.md` — arc vision + alignment analysis
- `docs/bible/lucentforge_terminology_map_v_1.md` — three-way reconciliation (Bible | TheForge | Python); cite before every Stage 2 import
- `docs/bible/lucentforge_items_addendum_v_1.md` — Stage 2 items doctrine (§A1–A8); cite alongside Foundation §sections
