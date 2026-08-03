# Genesis Architecture v1

**Authority:** Technical architecture; subordinate to Bible canon.
**Status:** Proposed. Component names are conceptual until accepted through an architecture decision.

---

## Mission

Genesis transforms a **seed, world configuration, accepted rules, and optional authored inputs** into a **validated initial world state.**

## Non-mission

Genesis does **not**:

- redefine canon;
- advance the live world indefinitely;
- render the game;
- own player interaction;
- require every world to match the canonical home world;
- replace handcrafted work.

## Core components

```text
GenesisOrchestrator
  ├── ConfigurationLoader
  ├── StageRegistry
  ├── DependencyPlanner
  ├── RandomSourceFactory
  ├── ArtifactStore
  ├── ValidatorRegistry
  ├── ProvenanceRecorder
  └── ProgressReporter
```

Names are conceptual until accepted through an architecture decision.

## Stage contract

Each stage should define:

- stable stage ID;
- version;
- prerequisites;
- consumed artifacts;
- produced artifacts;
- configuration schema;
- deterministic random streams;
- validation rules;
- diagnostic outputs;
- failure semantics.

## Determinism

For a fixed Genesis version, stage versions, configuration, seed, and authored-input versions, the result should be **reproducible** unless a stage explicitly declares permitted nondeterminism.

## Authored-input support

Stages may consume: handcrafted plate map; handcrafted plate vectors; locked coastlines; protected landmarks; canonical overrides. **Every override must be recorded in provenance.** See `genesis_canonical_world_adapter_v1.md`.

## Separation from runtime

Genesis produces **initial state and static/slow-changing layers.** The simulation runtime (`../bible/lucentforge_runtime_architecture_addendum_v1.md`, the Ripple Kernel) advances that state after world creation. Genesis does not own the run loop.

---

## Related

- `genesis_generation_pipeline_v1.md` — the stage sequence
- `genesis_data_contracts_v1.md` — artifact shapes the stages exchange
- `genesis_validation_strategy_v1.md` — how produced state is checked
