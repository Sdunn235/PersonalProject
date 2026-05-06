# Session State — Last updated: 2026-04-07 (Session 22 — Heartbeat-5 Resource Economy + Fixes)

## Current status: STABLE — NEEDS VISUAL TEST

## What works right now
- `python main.py` — 1024x768 window, 576x576 level centered with border zones
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

## Heartbeat Arc Status
| Phase | Status |
|-------|--------|
| Heartbeat-1: World Orchestration | **Complete** |
| Heartbeat-2: Map Enhancement | **Complete** |
| Heartbeat-3: NPC Decision Loop | **Complete** |
| Heartbeat-4: Goblin Behavior | **Complete** |
| Heartbeat-5: Resource Economy | **Complete** |
| Heartbeat-6: Observation Layer | Next |

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
11. **Equip UI** — no in-game menu to swap equipment
12. **Spell learning** — no way to learn new spells during gameplay
13. **Element resistances** — elements on spells but no resistance system on entities

## How to run
```
cd "C:\Users\Shawn\Documents\Workspace\Personal Project\LucentForge"
python main.py
```
Arrow keys = move player
Walk into any NPC to trigger combat
Tab = cycle right-side HUD between entities

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

## Bible reference
- `docs/bible/lucentforge_simulation_foundation_v_1.md` — philosophical constitution
- `docs/bible/lucentforge_sim_core_schema_v_1.md` — structural schema
- `docs/bible/lucentforge_micro_simulation_v_1.md` — prototype spec
- `docs/bible/heartbeat_convergence_vision.md` — arc vision + alignment analysis
