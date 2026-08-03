# Repository Authority Audit

## Confirmed Bible authority

`LucentForge/docs/bible/README.md` defines the Bible as the canonical design authority. Implementation must satisfy the Bible rather than retroactively redefining it.

The existing document set already includes:

- simulation philosophy;
- simulation schema;
- micro-simulation behavior;
- terminology reconciliation;
- items;
- rooms, panels, and zone crossings;
- attributes and magic;
- Grace cosmology;
- Grace affinities;
- biochemistry and affinity behavior;
- needs, wants, and drives;
- runtime architecture.

## Existing world-scale constraint that must be reconciled

The Rooms & Panels Addendum currently states:

- a Panel is one fixed 18x18 tile map;
- panels exist on a continuous panel grid;
- the canonical locator is `WorldPos(panel_x, panel_y, col, row)`;
- the current doctrine rejects a Final Fantasy-style temporary world-map zoom.

The new planetary map must not silently replace that doctrine.

### Recommended reconciliation

The planetary map is an **authoring, indexing, and simulation-partition layer**, not a separate player movement scale.

The player and NPCs still inhabit fixed-scale panels.

A planetary macrocell may reference:

- a collection of panel coordinates;
- an unresolved/generated panel region;
- background simulation state;
- biome, elevation, plate, climate, and affinity metadata.

This preserves the one-scale lived world while allowing a global planning map.

## Proposed authority split

| Subject | Authority |
|---|---|
| What the canonical planet is | Bible world addendum |
| What a Panel is | Existing Rooms & Panels Addendum |
| How planetary coordinates map to panel space | New Bible map-scale addendum |
| How maps are stored and exported | `docs/maps/` or asset README |
| How Genesis generates data | `docs/genesis/` |
| Current source artwork | `assets/maps/world_map/` |
| Experimental algorithms | Genesis research/prototypes |
| Accepted implementation decisions | ADRs / decisions |

## Required conflict rule

When a new world document conflicts with an existing Bible section:

1. identify the conflict explicitly;
2. cite both sections;
3. decide whether the new document extends, revises, or supersedes the old rule;
4. update the Bible index;
5. do not let code choose the answer accidentally.
