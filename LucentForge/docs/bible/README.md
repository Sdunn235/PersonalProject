# LucentForge Bible Documents

The canonical design authority for LucentForge. These documents are requirements, not reference.
Implementation must satisfy the bible; the bible does not merely describe the implementation.

---

## Documents

| File | Purpose | Authority |
|---|---|---|
| `lucentforge_simulation_foundation_v_1.md` | Philosophical constitution — the world's core laws | Primary authority for all systems |
| `lucentforge_sim_core_schema_v_1.md` | Structural schema — entity/system relationships | Architecture reference |
| `lucentforge_micro_simulation_v_1.md` | Prototype specification — simulation behavior details | Behavior reference |
| `heartbeat_convergence_vision.md` | Arc vision — Heartbeat arc design + Claude/GPT Caelum alignment analysis | Historical design record |
| `lucentforge_terminology_map_v_1.md` | Three-way term reconciliation — Bible / TheForge C# / LucentForge Python | Cite before every TheForge import |
| `lucentforge_items_addendum_v_1.md` | Stage 2 items doctrine — behavioral rules for items, slots, containers, economy | Cite alongside Foundation §sections for Stage 2 work |
| `lucentforge_rooms_panels_addendum_v1.md` | Stage 3 doctrine — Room/Panel/ZoneCrossing architecture, Zelda world model, TheForge Room reconciliation | Cite alongside Foundation for all Stage 3+ room/panel/zone work |
| `lucentforge_stats_magic_addendum_v1.md` | Stage 4 doctrine — attribute layer, Bits/Bytes magic, affinity axis, resonance, Intuition→trap perception. **§M5–§M6 revised by the Grace (2026-07-18): 8-affinity lattice, no opposition matrix.** | Cite alongside Foundation for all Stage 4+ attribute/magic/affinity work |
| `lucentforge_cosmology_foundation_v1_derived_revision.md` | **The Grace — cosmology.** Light/Dark as ontological states (Creation/absence), the Veil, the Source, the Gift. Supersedes Foundation §7 Light/Void. | Primary cosmology authority (Grace Migration Arc) |
| `lucentforge_affinity_grace_foundation_v1_derived_revision.md` | **The Grace — affinities.** 8-affinity lattice (4 Primal + 4 Derived), lattice relationships, resonance, environments, beings, migration doctrine. Supersedes the 6-element model. | Primary affinity authority (Grace Migration Arc) |
| `lucentforge_biochem_affinity_addendum_v1.md` | **Affinity Behavioral Loop doctrine** — Creatures-style emitter/receptor biochem; lattice-tiered affinity comfort → chemicals → drive urgency → behavior + region learning. Reactions + genetics deferred. | Cite for affinity-behavioral / biochem work |

Source drawing: `docs/bible/affinity_grace/` (`affinity_grace.png` / `.jpeg`) — canonical visual reference, by Shawn.

> **The Grace supersedes the six-element affinity model** (`EARTH/FIRE/AIR/WATER/VOID/LIGHT` + Light↔Void opposition) that Stage 4.4 shipped. Light and Dark are ontological states, not affinities. Affinity is now an eight-position lattice. `stats_magic_addendum` §M5–§M6, Foundation §7, and terminology_map §8.2 are revised to match.

---

## How to Use

**Before implementing a Stage 2 feature:**
1. Check `lucentforge_terminology_map_v_1.md` — confirm the field/enum name is reconciled
2. Check `lucentforge_items_addendum_v_1.md` (§A1–A8) — confirm behavioral doctrine is satisfied
3. Check `lucentforge_simulation_foundation_v_1.md` (the specific §section) — confirm the implementation is in service of the foundation's laws

**Before implementing a Stage 3+ feature:**
1. Check `lucentforge_terminology_map_v_1.md` §7 — confirm room/panel/zone term is reconciled
2. Check `lucentforge_rooms_panels_addendum_v1.md` (§R1–§R8) — confirm behavioral doctrine is satisfied
3. Check `lucentforge_simulation_foundation_v_1.md` as above

**Before implementing a Stage 4+ feature:**
1. Check `lucentforge_terminology_map_v_1.md` §1, §2, §8 — confirm attribute/pool/affinity term is reconciled
2. Check `lucentforge_stats_magic_addendum_v1.md` (§M1–§M9) — confirm behavioral doctrine is satisfied (esp. §M9 deferred list)
3. Check `lucentforge_simulation_foundation_v_1.md` (§4.1, §5, §6, §7, §11, §12.2) as above

**Citing sections:** Use `§X.X` notation for Foundation sections, `§AX` notation for addendum sections.
Example: "Carry capacity is a §4.1 (Physique) constraint governed by the §A2 formula."

**Extending the bible:**
- `lucentforge_terminology_map_v_1.md` has an Extension Protocol (Section 6) — follow it when new TheForge concepts are imported
- New addendum documents (`lucentforge_items_addendum_v2.md`, etc.) when Stage 2's doctrine needs expansion
- New bible documents require a Caelum planning session — they are requirements, not notes

---

## Stage Reference

| Stage | Bible sections cited | New docs |
|---|---|---|
| Stage 1 (SQLite) | §2.2 (simulation state), §10.2 (equipment threshold) | None |
| Stage 2 (Items/Equipment) | §4.1, §6.6, §7, §10.2, §12.2, §15, §18 | `lucentforge_terminology_map_v_1.md`, `lucentforge_items_addendum_v_1.md` |
| Stage 3 (Rooms as Zones) | §R1–§R8 (rooms_panels_addendum), §7 (terminology_map §7) | `lucentforge_rooms_panels_addendum_v1.md`, terminology_map §7 |
| Stage 4 (Attributes / Bits & Bytes / Affinity) | §M1–§M9 (stats_magic_addendum), §8 (terminology_map §8); Foundation §4.1, §5, §6, §7, §11, §12.2 | `lucentforge_stats_magic_addendum_v1.md`, terminology_map §8 |
| Grace Migration Arc (affinity re-foundation) | Grace cosmology + affinity drafts; addendum §M5–§M6 (revised), Foundation §7 (revised), terminology_map §8.2 (revised) | `lucentforge_cosmology_foundation_v1_derived_revision.md`, `lucentforge_affinity_grace_foundation_v1_derived_revision.md` |
| Stage 5+ | TBD | TBD |
