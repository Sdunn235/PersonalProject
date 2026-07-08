# Mechanics/ai — AI Decision Layer

NPC decision loop, behavioral strategies, chemical/need response, proximity effects, zone-triggered stimuli, and event logging. The `ai/` package consumes data from `biochem/`, `needs/`, and `world/` but has no dependency on `renderer/`.

---

## Modules

| File | Purpose |
|---|---|
| `controller.py` | `NPCController` — NPC state machine entry point; owns state transitions, memory, behavior delegation |
| `player.py` | `PlayerController` — keyboard-driven movement + source-aware fill rates |
| `behavior.py` | `BehaviorStrategy` ABC + `HumanBehavior` / `GoblinBehavior` — faction-level strategy injected into `idle.py` |
| `interpreter.py` | `OutcomeInterpreter` — scores need-satisfaction outcomes 0.0–1.0 for memory recording |
| `memory.py` | `NPCMemory` — EMA-based source quality tracking per NPC; records threat encounters |
| `proximity.py` | Goblin proximity fear injection + contested-source detection (radius-based, every tick) |
| `npc_logger.py` | Event logging subscribers — `log_spatial_zone(event)` for `[ZONE]` console output |
| `npc.py` | Sprite subclass for NPC entities |
| `zone_ai.py` | `ZoneAIResponder` — zone-crossing chemical triggers (Phase 3.5) |

### states/ subpackage

| File | Purpose |
|---|---|
| `states/idle.py` | `IdleState` — evaluates needs, delegates to behavior strategy, selects source |
| `states/moving.py` | `MovingState` — BFS pathfinding movement toward a target tile |
| `states/satisfying.py` | `SatisfyingState` — source-specific fill + stock consumption; exits on depletion |
| `states/patrolling.py` | `PatrollingState` — goblin camp patrol (PASSIVE threat level) |
| `states/raiding.py` | `RaidingState` — goblin civilized-zone raid with stock occupation and retreat |

---

## ZoneAIResponder (Phase 3.5)

`zone_ai.py` — subscribes to `WorldSim.zone_tracker` via `main.py._register_zone_subscribers()`. Fires on every `ZoneCrossingEvent` that reaches a registered entity.

**Chemical triggers:**

| Condition | Effect |
|---|---|
| Goblin enters `SETTLEMENT`, `FARM`, or `STORAGE` | `anger` nudge +0.15 (capped at 1.0) |
| Non-goblin (human, player) enters `GOBLIN_TERRITORY` | `fear` nudge +0.20 via `chemicals.add_fear()` |
| All other crossings | No effect |

`getattr(entity, "subtype", None)` — player entity may not have `subtype`; `None` treated as non-goblin. `PlayerController` has no `brain` — the method returns early before any chemical call. Zone feedback for the player is the HUD room-name flash, not chemical injection.

`to_room=None` (crossing out-of-bounds) — silently returns. No injection on unknown destination.

---

## Proximity vs. Zone-AI: two independent fear pathways

| System | File | Trigger | Frequency |
|---|---|---|---|
| Proximity fear | `proximity.py` | Goblin within `GOBLIN_FEAR_RADIUS` tiles of non-goblin | Every simulation tick |
| Zone-entry fear | `zone_ai.py` | Non-goblin entity enters `GOBLIN_TERRITORY` room | Once per boundary crossing |

Both inject `fear` via the same `chemicals.add_fear()` pathway. They are additive and independent — zone-entry fires once; proximity fires every tick while in range.

---

## Behavior strategy pattern

`idle.py` does not decide how to behave. It delegates to `NPCController.behavior` (a `BehaviorStrategy` instance, injected at spawn via `bootstrap.py`).

| Strategy | Assigned to | Behavior |
|---|---|---|
| `HumanBehavior` | All human NPCs | Need-driven; avoids goblins; reads source quality from memory |
| `GoblinBehavior` | All goblin NPCs | Threat-driven; patrols when PASSIVE; raids when RAIDING/CROSSING |

---

## Design rules

- `ai/` has no import from `renderer/` — draw calls belong to the renderer layer.
- State transitions are owned by `NPCController.update()` — states return a next-state class, not a string.
- Memory is EMA-based: source quality decays toward neutral, threat memory decays separately.
- Zone subscribers must not block — keep `on_zone_cross` lightweight (chemical set/add only).
