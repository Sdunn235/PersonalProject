# renderer — Drawing layer

Pure presentation. Reads game state and draws it; it never mutates simulation state, and `ai/` / `world/` never depend on this module.

| File | Responsibility |
|---|---|
| `sprite.py` | `EntitySprite` — directional animated sprite + world-map stat-bar overlays |
| `health_bar.py` | `draw_stat_bar` / `draw_health_bar` — compact fixed-color bars (reused widely) |
| `hud.py` | `draw_hud` — per-entity needs panel (right margin, Tab-cycled) |
| `combat_scene.py` | `run_combat` — full-screen turn-based combat UI |
| `observation_panel.py` | `draw_observation_panel` — Heartbeat-6 world-overview panel (left margin, `O` toggle) |
| `save_menu.py` | `run_load_menu` / `run_save_menu` — Phase 1.6 save-slot picker modals |

`observation_panel.py` reuses `health_bar.draw_stat_bar` (threat + source bars) and `needs.get_priority_need`; its matching per-run CSV log lives in `../observation/`.

## Save slot UI (Phase 1.6)

Both `save_menu` functions follow the `combat_scene.py` modal sub-loop pattern — independent `while True:` loop, `clock.tick(FPS)`, return value to caller:

- **`run_load_menu(screen, clock, ctx, font)`** — always shown on launch. Lists `[Autosave]` (slot 0) + slots 1-3 + a "New Game" row. Returns `slot_id` to load or `None` for New Game / cancel.
- **`run_save_menu(screen, clock, ctx, font)`** — triggered by S key. Shows only slots 1-3 (slot 0 is autosave-only). Returns `slot_id` or `None` if cancelled.

Slot metadata comes from `ctx.save_manager.get_slot_info()` — lightweight, no full restore needed.
