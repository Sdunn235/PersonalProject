# LucentForge Planetary Tectonics Addendum v1

**Created:** 2026-08-02 | **Stage:** World / Planetary (Arc B foundation) | **Authority:** LucentForge Bible (Foundation v1 + World Foundation v1 + this addendum)
**Status:** Draft for Shawn approval — the plate *registry* is source intent; boundary *classifications* are NOT canon (see §T3, §T10)
**Section IDs:** §T1–§T10

---

## Purpose

This addendum defines the canonical planetary plate structure of LucentForge's home world and the **requirement** that every plate boundary eventually be classified. It does not classify boundaries itself. Cite this addendum alongside `lucentforge_world_foundation_v1.md` for tectonic, plate, or boundary work.

---

## §T1 — Source Map

The current source consists of:

- a plate-boundary layer (Layer1);
- a plate-direction layer (Layer2);
- ten named plate layers (Layer3–Layer12) plus a background layer (Layer13);
- a color-key CSV;
- Shawn's plate-design notes;
- a layered PSD and exported PNG layers.

Source artwork lives under `assets/maps/world_map/` (see `docs/maps/map_layer_standard_v1.md` for the source-of-truth order). **The artwork is canonical source intent only after Shawn approves the associated registry** (`assets/maps/world_map/registries/plate_registry.csv`).

## §T2 — Plate Registry

| Layer | Plate | Source color (RGBA) | Current intent |
|---|---|---|---|
| 3 | Central Plate | `F5FF0083` | Convergence focus; extreme mountain building |
| 4 | Northern Archipelago Plate | `00FFE483` | Northern island arcs / island continents |
| 5 | Southern Archipelago Plate | `AA00FF83` | Southern active island system |
| 6 | Deep Ocean Plate | `0014FF83` | Closing ocean basin being divided |
| 7 | Midlands Plate | `833A7383` | Geography unresolved |
| 8 | Westlands Plate | `57F50083` | Geography unresolved |
| 9 | Greaterlands Plate | `FF008083` | Major converging plate; pressures Deep Ocean |
| 10 | Northern Plate | `F5000083` | Northern/polar system; geography unresolved |
| 11 | Lessorland Plate | `FF720083` | Converging plate; pressures Deep Ocean |
| 12 | Southern Plate | `33F35683` | Southern/polar system; geography unresolved |

The source CSV contained a malformed quote in the Greaterlands row (missing closing quote). The corrected machine-readable copy lives at `assets/maps/world_map/registries/plate_registry.csv`; the original source CSV is preserved unchanged under `assets/maps/world_map/source/notes/`.

Stable plate IDs (`PLATE-CENTRAL`, `PLATE-ARCH-N`, `PLATE-ARCH-S`, `PLATE-DEEP`, `PLATE-MID`, `PLATE-WEST`, `PLATE-GREATER`, `PLATE-NORTH`, `PLATE-LESSOR`, `PLATE-SOUTH`) are the identity of record. Hex color identifies a plate **only through the registry** — do not embed meaning solely in color.

## §T3 — Boundary Classification Requirement

Every shared boundary must eventually record:

- adjacent plates;
- local relative-motion vectors;
- boundary type;
- which plate subducts, when applicable;
- expected uplift;
- expected volcanism;
- expected earthquake behavior;
- confidence level;
- approved exceptions.

Boundary type options: convergent; divergent; transform; diffuse/complex; inactive or uncertain.

This is a **requirement**, not a completed table. See §T10.

## §T4 — Central Convergence

Not every Central Plate edge must be identical. To avoid a physically repetitive ring:

- some sectors may be continent-continent collision;
- some may be oceanic subduction;
- some may be oblique convergence;
- some may be transform-dominated;
- small wedges or microplates may absorb complex motion.

The mythic central mountain (§W5) must be supported by a larger regional uplift story.

## §T5 — Deep Ocean Closure

Greaterlands and Lessorland compress the Deep Ocean Plate. The visible split in Deep Ocean motion may represent:

- an active spreading ridge within a closing basin;
- tearing or segmentation of the oceanic plate;
- two sub-plates moving around a resistant block;
- a microplate boundary;
- rollback around separate subduction zones.

This remains an **open geological decision.** Do not canonize one explanation without review.

## §T6 — Archipelago Systems

Both archipelago plates should support chains of islands, volcanic arcs, submerged ridges, trenches, and larger continental fragments.

Recommended differentiation (proposal, not yet canon):

- **Northern Archipelago:** older, eroded, cooler, with larger stable fragments.
- **Southern Archipelago:** younger, hotter, more volcanic, with rapidly changing islands.

## §T7 — Plate Versus Continent

Plate boundaries do not equal coastlines. A plate may contain oceanic crust, continental crust, multiple continents or island groups, submerged shelves, internal rifts, and ancient stable cores.

Continents are drawn **after** crust type and elevation are established.

## §T8 — Fantasy Exceptions

The Grace and other canonical forces may alter material behavior, uplift persistence, erosion, volcanism, affinity concentration, and survivability at extreme elevation.

Any exception must state whether it is objective physics, cultural interpretation, game approximation, or temporary prototype shortcut.

## §T9 — Versioning

Never overwrite source plate history. Recommended asset version progression (see `docs/maps/map_layer_standard_v1.md` naming):

```text
plate_layout_v001
plate_motion_v002
boundary_types_v003
crust_types_v004
elevation_v005
coastlines_v006
```

## §T10 — Out-of-Scope

No final boundary classification is assigned by this draft. The next design session should produce a **boundary-pair table** from the actual composite map (plate fills + boundaries + arrows + numbered boundary segments), reviewed one segment at a time rather than assigning one type to an entire plate edge.

---

## Related documents

- `lucentforge_world_foundation_v1.md` (§W4–§W6) — supercontinent state, central spine, archipelago identity
- `docs/maps/map_layer_standard_v1.md` — asset naming, layer stack, registry fields
- `assets/maps/world_map/registries/plate_registry.csv` — machine-readable plate registry
