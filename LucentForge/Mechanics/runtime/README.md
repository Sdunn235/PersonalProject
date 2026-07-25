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
| `kernel.py` | R2 (planned) | `SimulationKernel.step(dt) -> SimFrame` — the headless-authoritative line; owns a `WorldSession` + `GameContext`. |
| `shell.py` | R4 (planned) | `PresentationShell` — pygame view: screen/clock/fonts, the sprite-per-entity map, HUD, and the `RuntimeMode` state machine. |

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

## Verification

`WorldSession.new_game()` + the save/apply adapters are pinned headlessly by
`scratchpad/run_runtime_tests.py` (tests **[F]** and **[G]**).
