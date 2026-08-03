# LucentForge World Foundation v1

**Created:** 2026-08-02 | **Stage:** World / Planetary (Arc B foundation) | **Authority:** LucentForge Bible (Foundation v1 + this document)
**Status:** Draft for Shawn approval — requirements with known gaps (see §W8 Out-of-Scope)
**Section IDs:** §W1–§W8

---

## Purpose

This document defines the physical identity and authoring principles of LucentForge's canonical home world. It establishes the requirements from which tectonics, terrain, climate, ecology, civilizations, affinities, and local panel content may develop.

It does **not** define a generator implementation. Generation architecture lives in `docs/genesis/` and is subordinate to this document. Cite this document alongside the Foundation when establishing planetary, continental, or world-scale truth.

---

## §W1 — Purpose

This document defines the physical identity and authoring principles of LucentForge's canonical home world. It establishes requirements from which tectonics, terrain, climate, ecology, civilizations, affinities, and local panel content may develop.

It does not define a generator implementation.

## §W2 — Canonical Home World and Generated Worlds

LucentForge has **one** handcrafted canonical home world.

Genesis may eventually generate additional worlds. A generated world is not automatically canonical merely because it follows the same physical rules.

The canonical world may be represented by handcrafted inputs, generated intermediate layers, or a hybrid process. **Shawn's approved world data remains the final authority.**

## §W3 — Simulation-First Geography

Geography should have causes. Preferred causal chain:

```text
planet parameters
→ tectonic plates and movement
→ elevation and ocean basins
→ atmosphere and currents
→ rainfall and temperature
→ hydrology
→ biomes and resources
→ settlement pressures
→ culture and history
```

Authored exceptions are permitted, particularly where fantasy cosmology or the Grace changes physical behavior, but exceptions must be explicit (see §W3 relationship to the Grace in `lucentforge_cosmology_foundation_v1_derived_revision.md`).

## §W4 — Approaching Supercontinent State

The canonical world is in a geologically unusual period **approaching a supercontinent configuration**.

The major land and plate systems are converging toward the Central Plate, but the world has not completed assembly.

Consequences may include:

- broad collision belts;
- active mountain building;
- closing ocean basins;
- squeezed oceanic crust;
- frequent earthquakes;
- volcanic island arcs;
- fragmented interior seas;
- young and unstable terrain beside ancient continental cores.

This condition must produce **varied** geography rather than one uniform landmass.

## §W5 — Central World Spine

The Central Plate is the convergence focus. Its canonical design intent includes:

- extremely high relief;
- a major mountain system;
- one mythically exceptional central peak or massif;
- limited low coast;
- steep escarpments and difficult approaches;
- geological and cultural importance.

The entire plate does **not** need to be one mountain. Habitable valleys, elevated basins, plateaus, passes, and interior waters may exist where supported by later design.

## §W6 — Ocean and Archipelago Identity

The Deep Ocean Plate is a closing and deforming oceanic system under pressure from Greaterlands and Lessorland.

The Northern and Southern Archipelago Plates are major island-producing systems, analogous in broad behavior to active terrestrial volcanic arcs, but they should develop **distinct identities** rather than mirror one another.

## §W7 — Memorable Game Geography

Physical plausibility supports, but does not erase, visual identity. Each major continental or island system should have:

- a recognizable silhouette;
- at least one signature geological feature;
- meaningful travel barriers;
- internal environmental variety;
- reasons for civilizations to develop differently.

## §W8 — Out-of-Scope Register

This foundation does **not yet** canonize:

- planet radius or circumference;
- day length, axial tilt, moons, or orbital parameters;
- final coastlines;
- final plate-boundary types;
- continent, ocean, or mountain names;
- civilization placement;
- affinity-field placement;
- exact pixel-to-distance scale;
- exact number of panels represented by one map pixel.

Those require explicit follow-up decisions. See the open decision register in the archived world-genesis handoff and the recommended next workshop (boundary-pair classification).

---

## Related documents

- `lucentforge_planetary_tectonics_addendum_v1.md` (§T1–§T10) — plate structure and boundary-classification requirement
- `lucentforge_world_map_scale_addendum_v1.md` (§S1–§S9) — reconciles planetary maps with the Panel doctrine
- `lucentforge_climate_hydrology_addendum_v1.md` (§C1–§C8) — climate/biome derivation rules
- `lucentforge_rooms_panels_addendum_v1.md` (§R1) — the one-scale Panel invariant this world layers above
- `../genesis/` — generator architecture (subordinate to this document)
