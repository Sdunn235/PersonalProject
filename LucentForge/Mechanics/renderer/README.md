# renderer — Drawing layer

Pure presentation. Reads game state and draws it; it never mutates simulation state, and `ai/` / `world/` never depend on this module.

| File | Responsibility |
|---|---|
| `sprite.py` | `EntitySprite` — directional animated sprite + world-map stat-bar overlays |
| `health_bar.py` | `draw_stat_bar` / `draw_health_bar` — compact fixed-color bars (reused widely) |
| `hud.py` | `draw_hud` — per-entity needs panel (right margin, Tab-cycled) |
| `combat_scene.py` | `run_combat` — full-screen turn-based combat UI |
| `observation_panel.py` | `draw_observation_panel` — Heartbeat-6 world-overview panel (left margin, `O` toggle) |

`observation_panel.py` reuses `health_bar.draw_stat_bar` (threat + source bars) and `needs.get_priority_need`; its matching per-run CSV log lives in `../observation/`.
