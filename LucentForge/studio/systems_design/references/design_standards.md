# Systems Design — References & Standards

Quick pointers the department loads. The bible is the authority; this file just routes you to it.

## Bible slices (in `docs/bible/`)
| Concern | File | Use for |
|---|---|---|
| **Naming authority** | `lucentforge_terminology_map_v_1.md` | Every term you use. If your name disagrees with the map, the map wins. |
| Stats & magic | `lucentforge_stats_magic_addendum_v1.md` | Attributes, derivation layer, bits/bytes pools, §M9.1 progression/ascension. |
| Items & equipment | `lucentforge_items_addendum_v_1.md` | Slots, containers, verbs, equipment effects. |
| Needs / wants / drives | `lucentforge_needs_wants_drives_addendum_v1.md` | The three-tier Needs Model (§9), wants-as-citizens, urgency. |
| Biochem / affinity | `lucentforge_biochem_affinity_addendum_v1.md` | Emitter/receptor substrate, comfort/stress/strain, affinity_strain (§B). |
| Cosmology / Grace | `lucentforge_affinity_grace_foundation_v1_derived_revision.md`, `lucentforge_cosmology_foundation_v1_derived_revision.md` | The 8-affinity Grace lattice, ontological states — only if the mechanic touches affinity. |

## The three hard rules (full text in charter, condensed here)
1. **Formulas not numbers** — derive from current attributes via the polymorphic layer; pools recompute,
   never freeze at spawn.
2. **Wants are citizens** — add instances to brain → chemical → drive → urgency; don't build a parallel system.
3. **Bits/Bytes firewall** — `bit_pool`/`byte_pool` (magic) vs `attribute_bit`/`attribute_byte` (XP);
   shared ratio only (1 Byte = 8 Bits).

## Substrate map (code you design against — verify against the live repo)
- `Mechanics/biochem/` — chemical layer.
- `Mechanics/needs/` — need.py, need_factory.py, need_source.py, needs_system.py, source_selector.py.
- `Mechanics/ai/` — controller.py, behavior.py, memory.py, states/, interpreter.py.
- `design/` (top-level) — npc_mind_architecture.md, design_decisions_log.md, world_simulation_design.md.

## Prior-art lessons worth remembering
- A large design *document* often maps to a *small* code change — size the work from the code surface
  (grep the real consumers), not the doc's ambition.
- Reserved-but-unconsumed seams are common; the work is often to *use* what's there, not to add.
