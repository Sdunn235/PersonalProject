# observation/ — Heartbeat-6 Observation Layer

Makes emergence **legible**: watch a town survive or collapse live, and prove it after the fact.

Two halves:
- **Live panel** — `renderer/observation_panel.py:draw_observation_panel()` draws a world-overview panel in the left margin (WORLD / SOURCES / NPCS). Toggle with `O` (default on).
- **Run-log** — `run_logger.py:RunLogger` records world + per-NPC state to CSV every `settings.RUN_LOG_INTERVAL` sim-ticks, and writes an emergence summary at exit.

## RunLogger

| Method | Purpose |
|---|---|
| `__init__(base_dir)` | Creates `logs/run_<timestamp>/`, opens `world.csv` + `npcs.csv` with headers. |
| `sample(world_sim, sources, npc_list, defeated, tick)` | Appends one world row + one row per living NPC; accumulates run stats (min food, peak threat, worst town, raid count via goblin→RAIDING transitions). |
| `finalize(world_sim, npc_list, defeated)` | Prints + writes `summary.txt`, closes files. |

Output per run (under `logs/`, gitignored):
- `world.csv` — tick, day, phase, food_total, threat, stage, town, source stocks
- `npcs.csv` — tick, name, subtype, state, priority need + value + zone, target, hp
- `summary.txt` — min food, peak threat, raid count, worst town state, final NPC state

## Wiring (`main.py`)
Instantiated after world setup; `sample()` gated exactly like the console status line
(`sim_ticks > 0 and clock.tick_count % RUN_LOG_INTERVAL == 0`); `finalize()` after the game loop.

The panel reuses `renderer/health_bar.py:draw_stat_bar` and `needs/needs_system.py:get_priority_need` — it only reads simulation state, never mutates it.
