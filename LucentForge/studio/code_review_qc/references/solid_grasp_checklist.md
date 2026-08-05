# SOLID / GRASP Checklist (Implementation-stage reviews)

Apply this **only** at implementation/refactor stage — not to design notes.

## SOLID
- **S**ingle Responsibility — does each class/function do one thing? Watch god-functions (the
  493-line `main()` that became the Stage 4.6R refactor is the cautionary tale).
- **O**pen/Closed — can behavior extend without editing existing call sites? (The derivation-strategy
  layer and the compat-property pattern are how LucentForge does this.)
- **L**iskov — do subtypes honor the base contract? (TPH item/character hierarchies.)
- **I**nterface Segregation — no fat interfaces forcing unused deps.
- **D**ependency Inversion — depend on abstractions; watch cross-layer singletons and circular imports
  (the `Mechanics.world` __init__ import-chain trap).

## GRASP
- Information Expert — logic lives with the data it needs.
- Creator / Factory — see the `new_game()` / `create_*` bootstrap primitives and `_spawn_entities()`
  closure pattern.
- Low Coupling / High Cohesion — cross the sim↔view boundary with value objects (SimFrame events out,
  Commands in), never callbacks or shared mutable flags.
- Controller — input as `Command`s over a remappable binding table.

## LucentForge-specific implementation traps (from the reflection log)
- **Mock parity:** a test double must mirror the real class on exactly the surface under test — no
  extra attributes (the `MockCtrl.brain` case), no missing ones (the `_Room.id` case).
- **Debug prints after the operation they measure**, not before (the stale-value ROOM_DBG trap).
- **Trace execution order** where a sequence matters (overlay-wins region bounds; circular import on
  new module in a package).
- **Persistence layer awareness:** runtime may read from a SQLite blob seeded once, not from the JSON
  you edited (the affinity `None` stale-blob bug). Trace file → seed → deserialize → object.
