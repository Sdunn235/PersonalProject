# Mechanics/runtime/ — application & session lifecycle

The boundary between the **simulation** (headless, pygame-free) and the
**presentation** (the pygame shell). Introduced by the Stage 4.6R runtime refactor
to move the app/session lifecycle out of `main.py`'s single 493-line `main()`
(now 46 lines — a thin composition root).

**Canonical doctrine:** `docs/bible/lucentforge_runtime_architecture_addendum_v1.md`
(§RT1–§RT8) — the requirements this package satisfies, including the **Ripple Kernel**
pattern: the kernel *senses* (time + player intent as a `Command`), *thinks* (steps the
authoritative sim), and emits a `SimFrame`; the shell *acts* (renders/persists). The
player is just another agent injecting intent into a kernel that runs **with or without
a shell attached** — the same Sense→Think→Act shape the NPC brains use, one level up.
This boundary is also the SimCore / Unreal port seam.

Built incrementally, one behavior-preserving stage per commit (R1–R6); each keeps
`scratchpad/run_all_tests.py` green.

## Contents

| File | Stage | Role |
|------|-------|------|
| `session.py` | **R1 (C0052)** / **R3 (C0054)** | `WorldSession` — the live object graph as a **pygame-free** dataclass: world_sim, sources, tile_map, player (+needs/controller), `npc_list` of `(entity, controller)` pairs, defeated/cooldown bookkeeping, item + chest services, a `ZoneAIResponder`. `new_game()` is a Factory over the existing `bootstrap.create_*` primitives; `apply_save()` folds the load sequence (apply-save + item/chest rebuild + chest placement) into one call. **R3:** `new_game()` also wires the sim-side zone observers (`log_spatial_zone` + `_dispatch_zone_ai`) via `wire_zone_observers()` — so a fresh tracker always gets them (the C0026 re-subscribe fix, now automatic). |
| `kernel.py` | **R2 (C0053)** | `SimulationKernel` — owns a `WorldSession` + `GameContext`; `step(dt, now) -> SimFrame` advances the sim with **no pygame** (no render, no persistence, no console I/O). Returns a `SimFrame` of events (`combat_trigger`, `trap_hints`, `panel_edge`, `zone_flash`, `sim_ticks`). Lifecycle `new_session()/start_new_session()/load()/save()` wraps R1. |
| `shell.py` | **R4 (C0055)** / **R5 (C0057)** | `PresentationShell` — the pygame view over a kernel: owns screen/clock/fonts, the sprite-per-entity map + group, HUD state (tab index, obs toggle), and the zone-flash countdown. `run(kernel)` is the driver loop (input → `kernel.step` → react to the `SimFrame` → render). A `RuntimeMode` enum (WORLD/COMBAT/PAUSED/INVENTORY/CHEST/SAVE_MENU) labels the interaction context, mirroring the `NPCController` state machine. **R5:** input is Commands — `handle_event(evt) -> Command` then `execute(command)`, over a remappable `self._bindings` table. |
| `commands.py` | **R5 (C0057)** / **Arc A** | `Command` enum + `DEFAULT_KEY_BINDINGS` (physical key → Command). Decouples keys from intents: enables remap and replay (feed Commands to `shell.execute()` with no pygame events). Arc A added PAUSE_SIM/STEP_SIM/REWIND/INSPECT/FEED. |
| `rewind.py` | **Arc A / A1b (C0062)** | `RewindBuffer` — an in-memory ring (deque) of session snapshots for scrub-back (`,`). Captures via the exact save/load path (snapshot → restore) against a **private in-memory SQLite DB**, so rewound state can't diverge from the persistent save system; no disk I/O. Faithful because A1b-i made save/restore capture controller behavioral state. |

### Glass Box — observability & sim time control (Arc A, C0059–C0063)

Debug/inspection tooling layered on the runtime seams (view + input + a read-only
event sink; the sim is untouched). Controls:

| Key | Command | What |
|-----|---------|------|
| `P` | PAUSE_SIM | freeze / unfreeze the whole simulation |
| `.` | STEP_SIM | advance exactly one tick while frozen (sub-stepped, smooth) |
| `,` | REWIND | step one tick **back** while frozen (`rewind.py` ring) |
| `V` | INSPECT | full-screen deep mind inspector on the TAB-selected NPC (`renderer/inspector.py`) |
| `L` | FEED | bottom-strip emergence event feed (`observation/event_log.py`) |

`observation/event_log.py::EVENTS` is a module singleton the sim appends to (state
transitions via `controller._set_state`, zone crossings, need targeting, combat) and
the shell renders. **A1b-i** (C0061) also fixed the long-standing "NPCs reset to IDLE
on load" gap — `apply_save` now restores `ai_state`/`ai_data` (state + target + path).

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
  `SimFrame.combat_trigger` (the entity to fight); in `COMBAT` mode the shell runs
  the blocking `run_combat` modal, then reports the result to
  `kernel.resolve_combat(entity, result, now)` — the kernel applies the model
  change (records the cooldown, marks the entity defeated on a win) and returns
  whether it died; the shell reacts by killing the sprite (view). Then back to WORLD.
- **`main.py` is a thin composition root** — `pygame.init()` → build ctx / world
  scope / `SimulationKernel` / `PresentationShell` → `shell.run(kernel)`.
- **Periodic orchestration stays in the shell.** Autosave, run-log sampling, and
  the status-line print are policies driven by `SimFrame.sim_ticks` — they are not
  simulation, so `step()` stays free of DB writes, file I/O, and console output.
- **`now` is passed in.** The combat cooldown is wall-clock based; the shell passes
  `pygame.time.get_ticks() / 1000` so the kernel never imports pygame.
- **Zone observers split sim from view (R3).** The sim-side observers (console
  logging + zone AI behavior) are wired into the session at `new_game()` and run
  inside `check_and_fire` during `step()`. The one UI observer — the player's
  room-name flash — is *not* a subscriber; the kernel reads the player's crossing
  from `check_and_fire`'s return and surfaces it as `SimFrame.zone_flash`, which the
  shell turns into its HUD countdown.

## Verification

`WorldSession.new_game()` + the save/apply adapters are pinned headlessly by
`scratchpad/run_runtime_tests.py` (**[F]**, **[G]**); `SimulationKernel.step()` +
combat/panel-edge detection + lifecycle by **[H]** (steps 200 frames with no
display). The full `run_all_tests.py` gate must stay green after each stage.
