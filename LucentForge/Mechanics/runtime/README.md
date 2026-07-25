# Mechanics/runtime/ — application & session lifecycle

The boundary between the **simulation** (headless, pygame-free) and the
**presentation** (the pygame shell). Introduced by the Stage 4.6R runtime refactor
to move the app/session lifecycle out of `main.py`'s single 493-line `main()`.

This directory is built up incrementally, one behavior-preserving stage per commit
(R1–R6). Each stage keeps `scratchpad/run_all_tests.py` green.

## Contents

| File | Stage | Role |
|------|-------|------|
| `session.py` | **R1 (C0052)** | `WorldSession` — the live object graph as a **pygame-free** dataclass: world_sim, sources, tile_map, player (+needs/controller), `npc_list` of `(entity, controller)` pairs, defeated/cooldown bookkeeping, item + chest services. `new_game()` is a Factory over the existing `bootstrap.create_*` primitives; `apply_save()` folds the load sequence (apply-save + item/chest rebuild + chest placement) into one call. |
| `kernel.py` | **R2 (C0053)** | `SimulationKernel` — owns a `WorldSession` + `GameContext`; `step(dt, now) -> SimFrame` advances the sim with **no pygame** (no render, no persistence, no console I/O). Returns a `SimFrame` of events (`combat_trigger`, `trap_hints`, `panel_edge`, `sim_ticks`). Lifecycle `new_session()/start_new_session()/load()/save()` wraps R1. |
| `shell.py` | R4 (planned) | `PresentationShell` — pygame view: screen/clock/fonts, the sprite-per-entity map, HUD, and the `RuntimeMode` state machine. Currently the shell lives inline in `main.py`. |

## Design rules

- **`WorldSession` is pygame-free.** Sprites, screen, and rendering never live here —
  that is why a future headless kernel can own and step a session with no display.
  Today the sprite layer is a proto-shell inside `main.py` (a `sprites` dict keyed by
  `entity_id`); R4 lifts it into `shell.py`.
- **`GameContext` (the service locator) stays separate** from the session. `new_game()`
  / `apply_save()` take `ctx` as a parameter rather than storing it.
- **Reuse, don't reinvent.** `new_game()`/`apply_save()` call the existing
  `bootstrap.create_*`/`rebuild_*`/`apply_save` and `SaveManager` primitives verbatim.

## Adapters elsewhere

- `SaveManager.snapshot_session(session, slot_id=...)` (in `Mechanics/data/save_manager.py`)
  is the snapshot adapter — derives controllers + bag/equipment/chest serialization from
  a `WorldSession`, collapsing `main.py`'s three repeated 10-arg snapshot calls.

## Combat & orchestration boundary (R2)

- **Combat is detected in the kernel, run by the shell.** `step()` returns
  `SimFrame.combat_trigger` (the entity to fight); the shell runs the blocking
  `run_combat` modal and, on a win, applies the defeat back onto the session
  (`defeated_npcs.add` + sprite kill). R4 formalizes this as a `COMBAT` mode.
- **Periodic orchestration stays in the shell.** Autosave, run-log sampling, and
  the status-line print are policies driven by `SimFrame.sim_ticks` — they are not
  simulation, so `step()` stays free of DB writes, file I/O, and console output.
- **`now` is passed in.** The combat cooldown is wall-clock based; the shell passes
  `pygame.time.get_ticks() / 1000` so the kernel never imports pygame.

## Verification

`WorldSession.new_game()` + the save/apply adapters are pinned headlessly by
`scratchpad/run_runtime_tests.py` (**[F]**, **[G]**); `SimulationKernel.step()` +
combat/panel-edge detection + lifecycle by **[H]** (steps 200 frames with no
display). The full `run_all_tests.py` gate must stay green after each stage.
