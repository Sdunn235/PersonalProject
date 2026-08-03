# Genesis Architecture v1 — Proposed Technical Document

**Target:** `LucentForge/docs/genesis/genesis_architecture_v1.md`  
**Authority:** Technical architecture; subordinate to Bible canon

## Mission

Genesis transforms a seed, world configuration, accepted rules, and optional authored inputs into a validated initial world state.

## Non-mission

Genesis does not:

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

For a fixed:

- Genesis version;
- stage versions;
- configuration;
- seed;
- authored input versions;

the result should be reproducible unless a stage explicitly declares permitted nondeterminism.

## Authored-input support

Stages may consume:

- handcrafted plate map;
- handcrafted plate vectors;
- locked coastlines;
- protected landmarks;
- canonical overrides.

Every override must be recorded in provenance.

## Separation from runtime

Genesis produces initial state and static/slow-changing layers.

The simulation runtime advances that state after world creation.
