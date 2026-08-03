# Lucent Forge World + Genesis Bible Expansion Handoff

**Repository:** `Sdunn235/PersonalProject`  
**Target root:** `LucentForge/`  
**Canonical Bible:** `LucentForge/docs/bible/`  
**Default branch:** `master`  
**Status:** Proposed expansion and Claude implementation handoff

## Purpose

This package integrates Shawn's handcrafted plate map and the Genesis world-generation direction into the existing Lucent Forge authority structure.

It does **not** create a separate competing Planet Bible.

The intended split is:

- `docs/bible/` defines canonical truths and requirements for Lucent Forge's home world.
- `docs/genesis/` defines the technical architecture for generating worlds.
- `assets/maps/world_map/` stores source map assets, exported layers, registries, and machine-readable map data.
- Genesis must cite the Bible when generating the canonical home world, but it must remain capable of generating other worlds from other configurations.

## Existing authority discovered

The repository Bible README states that the Bible is the canonical design authority, that its documents are requirements rather than casual reference, and that new Bible documents require a Caelum planning session.

The existing Bible uses:

- versioned filenames;
- named addenda;
- explicit authority statements;
- section IDs such as `§R1` and `§M1`;
- out-of-scope registers;
- staged implementation guidance;
- cross-document citations.

The proposed documents in this package follow that style.

## Primary deliverables for Claude

1. Audit the current repository and reconcile this proposal with any newer files.
2. Add world-foundation documents to the existing Bible.
3. Add Genesis architecture documents outside the Bible.
4. Add map asset documentation beside the existing map assets.
5. Preserve all current Bible files and existing map work.
6. Create a draft pull request; do not merge.

## Core rules

> Extend canon; do not shadow canon.

> Handcrafted world truth belongs to the Bible. Generator implementation belongs to Genesis.

> A map pixel is an index into layered world data, not automatically a fully simulated gameplay panel.
