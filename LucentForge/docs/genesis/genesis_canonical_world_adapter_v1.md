# Genesis Canonical World Adapter v1

**Authority:** Technical architecture; subordinate to Bible canon.
**Status:** Stub — intentionally thin. Detail is deferred until the plate registry and boundary table are approved.

---

## Purpose

This document names the seam by which LucentForge's **handcrafted home world** enters Genesis as authored input, so that generation fills unresolved layers *around* Shawn's approved work rather than overwriting it. It exists so the seam is not invented ad hoc in code.

## Entry point

The adapter is the `mode = authored_canonical` path described in `genesis_generation_pipeline_v1.md`. It consumes the handcrafted source under `assets/maps/world_map/` and the registries under `assets/maps/world_map/registries/`.

## What the adapter locks (proposed, pending approval)

- **Plate identity and geometry** — the 10 plates and their source shapes (`../bible/lucentforge_planetary_tectonics_addendum_v1.md` §T2).
- **Plate motion vectors** — Shawn's approved directions (Layer2), once confirmed absolute vs. relative.
- **Protected landmarks** — e.g. the central mythic peak/massif (`../bible/lucentforge_world_foundation_v1.md` §W5).

## What the adapter leaves generable

- Crust type, elevation, coastlines, climate, hydrology, biomes, resources, affinity fields, ecology, civilization — the derived layers, filled by the pipeline under Bible rules.

## Contract

- Every locked input and every override is recorded in provenance (`genesis_data_contracts_v1.md` artifact header).
- Any generated result that would alter a locked input raises `CANON_CONFLICT` (`genesis_validation_strategy_v1.md`) — never a silent rewrite.

## Deferred

This adapter does not yet specify:

- which exact layers are locked vs. generable (awaits Shawn's approval of the registry);
- the file/serialization format of the authored bundle;
- whether the canonical world must be *bit-for-bit* reproducible from Genesis or only *consistent* with it (open decision).

---

## Related

- `genesis_generation_pipeline_v1.md` (authored_canonical mode), `genesis_data_contracts_v1.md`, `genesis_validation_strategy_v1.md`
- `../bible/lucentforge_world_foundation_v1.md`, `../bible/lucentforge_planetary_tectonics_addendum_v1.md`
