# Genesis — World Generation Architecture

**Status:** Design documentation only. **No generator code exists yet.**
**Authority:** Technical architecture, **subordinate to the LucentForge Bible.**

---

## What Genesis is

Genesis is the architecture for **generating validated initial world state** from a seed, a world configuration, accepted rules, and optional authored inputs. It is a *separate project in tandem with* LucentForge: its output serves LucentForge, but Genesis must remain capable of generating other worlds from other configurations.

These documents currently live inside `LucentForge/docs/genesis/` for discoverability during design. The implementation may spin out into its own project later without moving this design authority.

## The canon relationship

- The **Bible** defines canonical truth for LucentForge's home world:
  - `../bible/lucentforge_world_foundation_v1.md` (§W)
  - `../bible/lucentforge_planetary_tectonics_addendum_v1.md` (§T)
  - `../bible/lucentforge_world_map_scale_addendum_v1.md` (§S)
  - `../bible/lucentforge_climate_hydrology_addendum_v1.md` (§C)
- **Genesis must cite the Bible when generating the canonical home world**, but it stays able to generate procedural worlds.
- Genesis does **not** redefine canon. When a generated result conflicts with canon, validation reports a `CANON_CONFLICT` — it never silently rewrites the Bible.

> Handcrafted world truth belongs to the Bible. Generator implementation belongs to Genesis.
> A map pixel is an index into layered world data, not automatically a fully simulated gameplay panel.

## Documents

| File | Purpose |
|---|---|
| `genesis_architecture_v1.md` | Components, stage contract, determinism, authored-input support, runtime separation |
| `genesis_generation_pipeline_v1.md` | The G00–G18 pipeline, iteration/feedback, authored-canonical vs procedural modes, first milestone |
| `genesis_data_contracts_v1.md` | Artifact headers, artifact types, macrocell record, panel-conversion contract |
| `genesis_validation_strategy_v1.md` | Validation classes, severity levels, visual diagnostics |
| `genesis_canonical_world_adapter_v1.md` | How the handcrafted home world enters Genesis as locked/authored input |

## Not in scope here

No generator code, no chosen implementation language commitment, no tectonic simulation. The first implementable milestone is a plumbing core (contract + deterministic RNG + stage ordering + provenance + a no-op stage + validation + a raster import/export), per `genesis_generation_pipeline_v1.md`.
