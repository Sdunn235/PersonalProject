# assets/maps/tools/

Authoring scripts for the macro **biome** sketch (`../world_map.csv`, 14 tokens, see
`../world_map_legend.md`). This is separate from the tectonic plate source in `../world_map/`
(BACKLOG LF-083 reconciles the two).

| Script | What it does |
|---|---|
| `rework_world_map.py` | **Rewrites `world_map.csv` in place** — carves oceans, adds archipelagos, applies coasts, enforces climate bands — then rebuilds `world_map_visual_aid.xlsx` (Map / Legend / Notes sheets). Prints token counts. |

**Careful:** the rework edits the CSV it reads, so running it twice is not a no-op. Commit or copy
`world_map.csv` before re-running. Kept out of `scratchpad/` on purpose: `run_all_tests.py` runs
every script there, and this one would change the map on every test run.

Run: `py assets/maps/tools/rework_world_map.py` (the paths inside are absolute to the workspace clone).
