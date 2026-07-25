# LucentForge Runtime Architecture Addendum v1

**Status:** Canon. Established by the Stage 4.6R Runtime Ownership Refactor (C0051–C0058, 2026-07-25).
**Authority:** Primary authority for the application/session **lifecycle** — how the game boots, owns
its object graph, advances the simulation, and presents it. Cite alongside the Simulation Foundation
(the *what* of the world) whenever touching the run loop, session ownership, save/load orchestration,
input, or the future SimCore / Unreal port.

This addendum governs *ownership and orchestration*, not domain behavior. The NPC AI, needs, biochem,
affinity, combat, items, and world-sim systems are unchanged by it; the refactor that produced it was
**behavior-preserving** (proven by a golden-master net, `scratchpad/run_all_tests.py`, green before and
after every stage).

---

## §RT1 — The problem: change concentration

Before Stage 4.6R, `main.py` was a single 493-line `main()` owning ~15 responsibilities: the pygame
loop, composition, session state (as ~18 loose locals), input dispatch, every modal menu, save/load/
new-game, event-subscriber wiring, the world/NPC/player update drivers, combat transition, panel-edge
detection, rendering, and shutdown. Nearly every future feature (dialogue, crafting, weather, quests,
background sim) had a reason to edit that one file. The domain systems were already well-separated inside
`Mechanics/`; the missing boundary was the **application/session lifecycle**.

**Rule (§RT1).** The runtime is split into three owners plus the existing service locator. No single file
owns the loop *and* the object graph *and* the view. New runtime responsibilities attach to the owner
whose concern they match (§RT2), never to a god-loop.

---

## §RT2 — The three layers (+ the service locator)

```
GameContext (Mechanics/data/context.py)   Service Locator — DB, DAOs, repos, SaveManager, rooms/panels.
   │                                        Distinct from the session; passed in, never owned by it.
   │
SimulationKernel (Mechanics/runtime/kernel.py)   NO pygame — headless-authoritative.
   owns WorldSession + GameContext
   new_session / start_new_session / load / save        (wrap the bootstrap primitives)
   step(dt, now) -> SimFrame                             sense → think → emit an event frame
   resolve_combat(entity, result, now) -> died           model side of the combat handoff
   │
   └── WorldSession (Mechanics/runtime/session.py)   the object graph as data — NO pygame.
          world_sim, sources, tile_map, player (+ needs, controller),
          npc_list of (entity, controller), defeated_npcs, combat_cooldowns,
          inv_svc, equip_svc, chest_reg, zone_ai
          new_game()  — Factory over bootstrap create_* (no new creation logic)
          apply_save() — load adapter (apply-save + item/chest rebuild + chest placement)
          wire_zone_observers() — sim-side zone observers (logging + zone AI)

PresentationShell (Mechanics/runtime/shell.py)   pygame — the swappable view.
   owns screen/clock/fonts, sprite-per-entity map + group, HUD state, zone-flash countdown, RuntimeMode
   run(kernel): input → Command → kernel.step(dt, now) → react to SimFrame → render
   handle_event(evt) -> Command   ;   execute(command)   ;   _render(frame)
```

**Rule (§RT2.1).** `WorldSession` and `SimulationKernel` are **pygame-free**. No sprites, no screen, no
`pygame.*` calls, no rendering, no blocking modal, no console/file I/O inside `step()`. This is the
headless line (§RT6); it is what lets the simulation run and be tested with no window attached.

**Rule (§RT2.2).** The **shell owns the view**: sprites (a per-entity map keyed by `entity_id`, synced to
entity state each frame), HUD, and all pygame. Model mutation lives kernel-side; view reaction lives
shell-side (Model/View). The defeated-sprite kill is a shell reaction to a kernel outcome, never a
session concern.

**Rule (§RT2.3).** `GameContext` (the service locator) stays distinct from the session. Lifecycle methods
take `ctx` as a parameter; the session does not store it. "No manager forest" — the only runtime owners
are Kernel, Session, Shell.

---

## §RT3 — The SimFrame contract

`step(dt, now)` returns a `SimFrame`: the small, explicit set of **events** the shell reacts to.

| Field | Meaning | Shell reaction |
|---|---|---|
| `sim_ticks` | world ticks advanced this frame | drives periodic policy (autosave, run-log, status print) |
| `combat_trigger` | entity to fight, or None | run the `run_combat` modal (COMBAT mode) |
| `trap_hints` | perception hint strings | print |
| `panel_edge` | edge message, or None | print |
| `zone_flash` | room name the **player** entered, or None | set the HUD flash countdown |

**Rule (§RT3).** Anything the shell must *do* in response to a tick crosses the boundary as a `SimFrame`
field, not as a callback into the shell or a shared mutable flag. New sim→view signals (deaths, spawns,
weather, dialogue prompts) are added as `SimFrame` fields.

---

## §RT4 — The Ripple Kernel (the synthesis worth naming)

LucentForge NPCs already run **Sense → Think → Act over a Blackboard (`Brain.chemicals`) with Utility
drives** (`Drive.compute_urgency` max-vote). Stage 4.6R makes the *whole runtime a fractal of that shape*:

- The **kernel senses** — elapsed time plus player intent (a `Command`, already applied to the player
  controller).
- The **kernel thinks** — it steps the authoritative simulation (world, AI, physiology) and emits an
  event frame.
- The **shell acts** — it renders and persists.

The player is therefore **just another agent injecting intent** into a kernel that runs *with or without a
shell attached*. This is the executable form of the world vision's "player as ripple / the world simulates
without the player": the stone (Gobby and the world's own agents) makes the ripples; the player is one more
ripple, not the center.

**Rule (§RT4).** The kernel is authoritative and shell-independent. Detaching, replacing, or running
multiple shells (or none — a headless server, a background-sim panel, a test harness) must never change
simulation outcomes. If a behavior only works when a shell is attached, it is misplaced; move it kernel-side.

---

## §RT5 — RuntimeMode (State) and Command

- **RuntimeMode** (State pattern) — `WORLD / COMBAT / PAUSED / INVENTORY / CHEST / SAVE_MENU` labels the
  shell's interaction context, mirroring the `NPCController` string-keyed state machine one level up.
  WORLD is the persistent gameplay mode; the others are modal dialogs entered from it. The dialogs remain
  the existing blocking sub-loops (behavior-preserving); the modes name *which* context is active and, for
  COMBAT, formalize the handoff: **WORLD detects → COMBAT runs `run_combat` → `kernel.resolve_combat`
  applies the model change → shell kills the sprite → WORLD.**
- **Command** — `handle_event(evt) -> Command` then `execute(command)`, over a remappable
  `physical-key → Command` binding table (`commands.py`). Extends the codebase's "menu returns an action
  string" convention up to the input layer. Buys **remap** (edit the bindings) and **replay** (feed
  Commands to `execute()` with no pygame events — deterministic input tests).

**Rule (§RT5).** Input is expressed as intents (`Command`), not physical keys, above the binding table.
Interaction contexts are named `RuntimeMode` states, not ad-hoc booleans.

---

## §RT6 — The headless line and the port contract

Because the kernel + session are pygame-free, the simulation is testable **without a window** — which
lifts the long-standing "`py main.py` is the only verification" ceiling. `scratchpad/run_runtime_tests.py`
steps the kernel N frames with no display and asserts New-Game reset, save/load fidelity, zone-subscriber
survival, combat detection + resolution, panel-edge detection, and item/chest round-trips.

This boundary is also the **SimCore / Unreal port contract** (Simulation Foundation §11): the C++/Unreal
port reimplements the *kernel + session* (the authoritative model) and attaches a new *shell* (the
Unreal view). `WorldSession` is the serialization/ownership surface; `SimFrame` is the model→view event
protocol; `Command` is the view→model intent protocol.

**Rule (§RT6).** The kernel/session boundary is the port seam. Keep it free of pygame and of Python-only
conveniences that would not survive a reimplementation. When in doubt, ask: "could a C++ kernel emit this,
and could an Unreal shell consume it?"

---

## §RT7 — Invariants (must hold)

1. `WorldSession` and `SimulationKernel` import no pygame and perform no rendering, blocking, or I/O in
   `step()`. (Enforced by review + the headless tests.)
2. World-scope `tile_map` + `sources` are **reused** across New Game, never recreated; only `world_sim` +
   entities rebuild. (New Game = `start_new_session()`.)
3. Every stage of any future runtime change keeps `scratchpad/run_all_tests.py` green — behavior
   preservation is proven, not asserted.
4. Sim→view signals cross as `SimFrame` fields; view→model intents cross as `Command`s; combat outcomes
   cross via `kernel.resolve_combat`. No shared mutable flags across the boundary.

---

## §RT8 — Deferred / future (not in scope of v1)

- **ECS / component entity model** — its own later arc; the runtime split is a prerequisite, not a part.
- **Non-blocking modal modes** — the blocking menus (pause/inventory/chest/save/load) could become true
  enter/handle/render `RuntimeMode` states; deferred as a pure-view refactor with no behavioral payoff yet.
- **Replay-driven determinism** — record a `Command` + `dt` stream and replay it headless for regression
  proof; the `Command` layer makes this possible but the recorder is future work.
- **Remap configuration surface** — `commands.py::DEFAULT_KEY_BINDINGS` is data; a settings UI to edit it
  is future work.
- **Headless background-sim / multi-panel** — running the kernel for off-screen panels (Foundation's
  "world simulates without the player") now has an architecture; the content/scheduling is future work.

---

*Migration record: Stage 4.6R shipped R0 (characterization net, C0051) → R1 WorldSession (C0052) → R2
SimulationKernel + SimFrame (C0053) → R3 zone-observer lifecycle (C0054) → R4 PresentationShell +
RuntimeMode (C0055) → R5 Commands (C0057), each a behavior-preserving commit with the golden-master gate
green. `main.py` went 493 → 46 lines.*
