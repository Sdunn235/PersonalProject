# Lucent Forge Architecture

This directory explains how Lucent Forge's canonical design doctrine becomes maintainable software architecture.

It does **not** replace `docs/bible/`. The bible remains the primary design authority. Architecture documents interpret dependency boundaries, data flow, ownership, and implementation seams while citing the bible that authorizes them.

## Authority order

1. `docs/bible/` — canonical world and simulation doctrine
2. `docs/decisions/` — accepted architecture decisions and tradeoffs
3. `docs/architecture/` — current subsystem boundaries and data flow
4. `docs/roadmap/` — sequencing and active scope
5. `docs/research/` — evidence, experiments, and unresolved possibilities
6. code and tests — implementation of the accepted doctrine

When code and the bible disagree, the disagreement must be surfaced. Do not silently rewrite either side.

## Working rule

> Extend canon; do not shadow canon.

Before creating a new document, determine whether the material belongs in an existing bible section, an addendum, an architecture decision record, research notes, or temporary experiment output.
