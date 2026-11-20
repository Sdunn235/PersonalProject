# PROPOSAL — not canon until Shawn decides

# Beyond Panel(0,0): the first neighbour

**From:** World Building (first run) · **Date:** 2026-11-19 · **For:** the Director → Shawn
**Feeds:** BACKLOG LF-010 step 2 (a second panel + real edge transitions), which is waiting on WB + Lore.
**Status:** v1 DRAFT, pending QC and Shawn. Story/Lore is working the people and meaning of the same land in
parallel; nothing here decides who lives anywhere.

Provenance tags: **[CANON]** = bible or approved data says so · **[DERIVED]** = follows from canon by a stated
rule · **[PROPOSED]** = our invention, pending a decision · **[OPEN]** = a named gap.

---

## 1. Intent

`panels.json` holds one Panel with four `null` edges. LF-010 step 2 needs a second Panel and a working edge
transition. This proposal says **which edge to open first, what physically lies beyond it, and the rules the
shared seam must obey.** It extends §R1/§R2 (new Panel content, explicitly deferred to "Stage 3.5+" by §R8)
using the climate/hydrology rules of §C4/§C6. It does not touch plates, planet scale or names.

## 2. What Panel(0,0) already tells us (the evidence)

From `Mechanics/data/panels/panel_0_0.json` and `rooms.json`, all **[CANON]** (approved data):

| Edge | Edge row/column (as tiles) | What crosses it |
|---|---|---|
| **North** (row 0) | `#..#..~~,.......#.` | **The river** (cols 6–7), forest west of it, open outskirts east. |
| **South** (row 17) | `#..#..~~#.......#.` | **The river** (cols 6–7), forest west, outskirts east. |
| **West** (col 0, top→bottom) | `#.#..#.#..#..gg#.#` | Forest. The goblin forage patch (`g`, rows 13–14) touches this edge. |
| **East** (col 17, top→bottom) | `...#......#.......` | Open town outskirts, almost entirely walkable. |

- The river runs the full height of the Panel, 2 tiles wide, and **leaves by both the north and the south
  edge**. Neither end is a source or a sink, so **both (0,-1) and (0,1) must carry it on** (§C4: a river needs a
  source and a terminus). **[DERIVED]**
- It is crossed only at two bridges (rows 4–5 and 11–12). §R3 makes the river non-traversable except at
  bridge tiles. **[CANON]**
- The Panel holds a closed broadleaf forest (the `azure_oak` genome is a broadleaf), a perennial river,
  cultivated fields and stored grain. That points to a **humid temperate** climate: wet enough for continuous
  woodland and a year-round river, mild enough for field crops, and no sign of arid, tropical or polar cover.
  **[DERIVED backward from local evidence; see §3 caveat]**
- `rooms.json` calls the outskirts "the *eastern fringe* of civilized territory", which implies settled land
  thins out to the east. **[CANON, descriptive text]**

## 3. The scale caveat (it governs everything below)

Panel(0,0) has **no planetary location**: no plate, latitude or `PlanetCoord` (§S7 is a proposed wrapper,
§S6 values aren't chosen). So we can't derive its climate *forward* from the planet as §W3 asks. We can only
infer it *backward* from what's on it. **[OPEN — question Q3]**

Second, a Panel is 18 tiles of person-scale ground (§R1, §S2: player and NPCs live in the tiles directly).
Unless a Panel is heavily compressed (question Q2), **the climate band can't change across one edge.** So
every neighbour below is the *same* humid temperate valley, and any difference from Panel(0,0) has to come from
a **local** cause: position along the river, slope, stone, flooding, or whether anyone has cleared it.
**[DERIVED from §C1/§C6 + §R1]**

## 4. One neighbour or a ring of four? → **One.**

**Recommendation: open one neighbour now, and sketch intents (not tiles) for the other three edges.** We
call this "sketch the ring, build the one".

Why one:
1. **Every Panel is a permanent constraint.** Its edges fix what the next Panels must match. Four Panels
   commit four regions' worth of seams, plus four diagonal corners (±1,±1) that will later be constrained on
   two sides each, before the edge contract has been proven once.
2. **LF-010 step 2 is an engineering proof**: load a neighbour, move entities across, then (LF-120) keep it
   ticking. One seam proves all of that. Four seams prove it four times and cost four times the Story/Lore
   decisions.
3. **Story/Lore can't answer four "who lives here?" questions as well as one.** The first answer will teach
   us all something.
4. **The risk of one is a corridor world.** We mitigate it with the frontier sheet (§7), which records a
   coherent intent for every open edge, so the ring still adds up when it's built.

## 5. Which one? Two decisions, two options each

### Decision A — which way does the river flow? [OPEN, needs Shawn]

Nothing in Panel(0,0) settles it. No elevation data, and the bridges and riverbanks are symmetric.

- **Option A1 (recommended): flows north → south.** The source is somewhere north (wet highlands, §C4);
  (0,-1) is **upstream**; (0,1) is **downstream**, toward the sink.
- **Option A2: flows south → north.** The labels swap. The upstream sketch below becomes (0,1) (rows mirrored)
  and the downstream sketch becomes (0,-1).

Why A1: it's physically a coin flip. We recommend it only because "up the map = uphill toward the source"
reads intuitively for players and leaves the south open for the eventual sink (floodplain → lake/wetland/sea).
Either way, **decide before the second Panel ships.** Once a Panel exists, flow direction is canon by
implication: rounded vs angular stone, floodplain vs gorge.

### Decision B — which edge first?

| Candidate | Physics constraint | Engineering cost | Story/Lore load | Verdict |
|---|---|---|---|---|
| **North (0,-1)**, the river's upstream reach under A1 | **High**: river continuity across the seam | Medium: the seam is split by the river | Low–medium: wild land, few decisions | **Recommended** |
| South (0,1), the downstream reach | High: river continuity | Medium | Medium: floodplain = good farmland = settlement pressure | Option B |
| East (1,0), beyond the town | Low: open ground, nothing crosses | **Lowest**: col 17 is 16/18 walkable | **High**: what lies beyond the town is mostly a Story decision | Good for engineering, weak as a world proof |
| West (-1,0), the deep forest | Low–medium | Medium | **High**: it's the goblins' hinterland (the camp's forage touches this edge) | Hold until Lore has spoken |

**Recommendation: Panel(0,-1), the upstream reach.** Reasons:
1. **It proves the hardest seam first.** The river is the one feature that *must* continue. If the edge
   contract holds there, it holds everywhere.
2. **No new tile types.** It can be built entirely from today's 13-char legend (`#` trees and `#`-as-rock via
   the `rocks` list, `~`, `,`, `.`), so LF-010 isn't blocked on Systems Design or Art.
3. **Art already has its genomes.** `azure_oak` and `river_stone` are exactly what an upstream woodland
   reach is made of. Art varies genes; it doesn't need a new species.
4. **It walks the causal chain the right way.** Going upstream moves toward the river's source, which §C4
   says has to exist. Going downstream moves toward a sink we'd have to invent sooner.
5. **It keeps Panel(0,0)'s central drama.** The river divides the wild west bank from the cleared east bank,
   and the new Panel inherits that divide without deciding who is on either side.

**Option B (if Shawn prefers to go downstream, or picks A2):** Panel(0,1), the floodplain. It's fully
sketched in §6.2. It's the better pick if Story/Lore wants farmland and settlement pressure early. It costs a
new grass/reed genome kind for Art and probably a new region tag.

---

## 6. The proposed Panels

### 6.1 Panel(0,-1): the upper reach (RECOMMENDED)

**Causal line:** *upstream, uncleared → closed canopy on both banks, angular stone in the river margins, same
2-tile channel, no crossing → because it's higher up the same valley and nobody has cleared it yet.*
**[PROPOSED]**

- **Region / biome:** humid-temperate **riverine broadleaf woodland**, the same climate band as (0,0).
  **[DERIVED, §3]**
- **Terrain:** a gentle rise, **+1 relative elevation step** above (0,0) (not shown in 2D; recorded for
  isometric/3D). **[PROPOSED]**
- **River:** enters from (0,0) at cols 6–7 (the seam), shifts east as it climbs (cols 7–8, then 8–9), and
  leaves by the north edge at cols 8–9 toward (0,-2). It stays 2 tiles wide: at tens of metres the channel
  doesn't visibly change. **No bridge**, so the river splits this Panel into a west and an east half, joined
  only through Panel(0,0)'s bridges. **[PROPOSED]**
- **Stone:** five river-margin rocks (rocks list below). Upstream stone is **less worn**: rougher and more
  angular than (0,0)'s. **[DERIVED: stones round as they travel downstream]**
- **What grows:** broadleaf woodland, roughly twice the obstacle density of (0,0)'s forest (57 vs 27 `#`
  tiles), because the canopy closes in away from cleared land. The east bank opens near the seam (the cleared
  outskirts carry over a few rows) and closes into woodland to the north. **[PROPOSED]**
- **Water access:** 8 riverbank `,` tiles (Panel(0,0) has 7). These are thirst sources, so the count is a
  Systems Design balance call. **[PROPOSED, flagged]**
- **Need sources:** none placed (no `F`/`f`/`S`/`s`/`g`/`O`/`C`). Food, sleep and chests are Systems Design and
  Story/Lore decisions. **[OPEN]**

**Tile sketch** (illustrative, live legend; row 17 is the seam with Panel(0,0) row 0):
```
#..#.#..~~..#..#.#    0  ← north edge, faces (0,-2); river leaves at cols 8–9
..#...#.~~,...#...    1
#..#....~~#..#...#    2
..#..#.,~~....#...    3
#....#..~~..#...#.    4
..##....~~,.....#.    5
#....#.#~~#..#....    6
..#....~~...#...#.    7
#...#..~~#........    8
..#...,~~...#...#.    9
#..#...~~.........   10
..#..#.~~,.....#..   11
#.....~~#.........   12
..##..~~.....#....   13
#.....~~,........#   14
..#.#.~~.....#....   15
#.....~~..........   16
#..#.,~~,.......#.   17  ← seam: same passability as (0,0) row 0, column by column
```
`rocks` (col, row): `[[10,2],[7,6],[10,6],[9,8],[8,12]]`. Every other `#` is a tree.

**Region sketch** (reuses (0,0)'s legend: `c` forest, `f` river, `i` town_outskirts):
```
ccccccccffcccccccc   rows 0–6
cccccccffccccccccc   rows 7–11
ccccccffcccccccccc   row 12
ccccccffiiiiiiiiii   rows 13–17  (outskirts carry 5 rows across the seam, then woodland)
```
Whether the outskirts really reach across the seam, and whether the east-bank woodland is the *same* Room
as the west-bank forest, is for Story/Lore and Engineering (one region → one Room, §R3). **[OPEN]**

**Checked:** seam passability matches (0,0) row 0 exactly · river orthogonally connected, touching both the
north edge and the seam · every walkable tile reachable from the seam (no sealed pockets) · only legend chars.

### 6.2 Panel(0,1): the lower reach / floodplain (OPTION B)

**Causal line:** *downstream, floods seasonally → the river widens to 3, the banks open into meadow, trees
pull back to the margins, stone is smaller and smoother → because it's lower in the valley, where the river
slows and spreads.* **[PROPOSED]**

- **Region / biome:** humid-temperate **floodplain meadow** with woodland margins, the same climate band.
  The local cause of the change is flooding: seasonal inundation keeps trees off the low banks.
  **[DERIVED from §C4 + §C6 transitional zones]**
- **Terrain:** **−1 relative elevation step** below (0,0). **[PROPOSED]**
- **River:** enters at cols 6–7, widens to 3 tiles by row 5 (a slower, broader reach), drifts east, and
  leaves by the south edge at cols 10–12 toward (0,2) and eventually a sink. **[PROPOSED]** The sink
  (lake, wetland or coast) is **[OPEN]** and depends on where (0,0) sits on the planet (Q3).
- **What grows:** grass and meadow on the east bank, thinning woodland on the west bank. 32 `#` tiles.
- **Water access:** 9 riverbank tiles (Systems Design balance call).

**Tile sketch** (row 0 is the seam with Panel(0,0) row 17):
```
#..#.,~~#.......#.    0  ← seam: same passability as (0,0) row 17
..#...~~,.....#...    1
#.....,~~.........    2
..#.#..~~.....#...    3
#.......~~.......#    4
...#....~~~,......    5
#.......~~~...#...    6
..#.#...~~~.......    7
#.......,~~~...#..    8
...#.....~~~......    9
#........~~~..#...   10
..#......~~~,.....   11
#........,~~~.....   12
...#......~~~..#..   13
#.........~~~,....   14
..#.#.....~~~.....   15
#.........~~~..#..   16
...#......~~~,....   17  ← south edge, faces (0,2)
```
`rocks`: `[[8,0]]` (smaller, smoother `river_stone` variant).
**Region sketch:** `c` west bank, `f` river, `i` outskirts on the east bank for rows 0–4, then **`m` = a new
open-ground tag** for rows 5–17 east. Calling a floodplain meadow "forest" would be a misnomer. The tag name
and its RoomType (probably `WILDERNESS`) need the terminology-map protocol (§7.5 / Extension Protocol).
**[PROPOSED, needs naming]**
**Checked:** seam mask matches · river connected · no pockets · legend chars only.

---

## 7. Frontier sheet: the edges we are *not* building yet

Intents only, no tiles. These keep the ring coherent when it's built.

- **North of the upper reach, (0,-2) and beyond:** the valley keeps climbing toward the river's source in
  wetter, higher ground (§C4). Expect steeper, rockier Panels and eventually a confluence or headwater. A
  cliff/rapids tile will probably be needed there, which is a Systems Design call. **[PROPOSED]**
- **East, (1,0):** leaving cleared land. Physically it's the same climate, a little farther from the river,
  so drier ground: woodland regrowth, scrub or pasture, depending on whether anyone keeps it cleared. That
  "whether" is **settlement pressure, which is Story/Lore's**. The cheapest edge for Engineering (16 of 18
  walkable). **[PROPOSED intent / OPEN content]**
- **West, (-1,0):** the forest continues away from both river and town: the deepest, least-disturbed
  woodland in the ring. The goblin camp's forage patch touches this edge (col 0, rows 13–14), so whatever is
  out there physically connects to the camp. What the goblins use it for is Story/Lore's. **[PROPOSED intent]**
- **Corners (±1,±1):** never entered directly (§R2 is orthogonal), but each is bound by two neighbours.
  Build orthogonals first and corners last.

## 8. Edge contract (for QA, in testable form)

For any two orthogonally adjacent Panels A and B, with A's edge line *a* touching B's edge line *b*:

- **EC1 Feature continuity.** River `~` tiles occupy identical columns (or rows, for E/W seams) in *a* and *b*.
  **Hard.**
- **EC2 Passability match.** For every position along the seam, `blocked(a[i]) == blocked(b[i])`, where
  blocked = `#`, `~`, `C`. So a crossing never lands an entity in a wall or the river, in either direction.
  **Hard.** *Looser alternative for Systems Design/Engineering to choose instead:* allow a mismatch and have
  the transition refuse to fire at that position.
- **EC3 Region continuity.** Region classes across the seam are compatible: river↔river, forest↔forest or
  outskirts, outskirts↔outskirts or forest. A new tag declares its compatible pairs. **Soft** (an
  allowed-pairs table).
- **EC4 River integrity.** Within a Panel, `~` tiles are orthogonally connected, and each river component
  touches an edge or a named sink. **Hard.**
- **EC5 No pockets.** Every walkable tile is reachable from at least one seam. A river may divide a Panel.
  **Hard.**
- **EC6 Legend only.** Every char is in the Panel's `tile_legend`. **Hard.**

Both sketches above pass EC1, EC2, EC4, EC5 and EC6 against Panel(0,0)'s real edge rows. We checked them
with a throwaway script; QA should own the real test.

## 9. Biome sheets (for Art)

**Upper reach, (0,-1).** Art grows the props and palette from this; we don't paint.
- **Trees:** `azure_oak` base, mature growth stage (an uncut stand). Tendencies: slightly larger
  `trunk_height` and `canopy_radius` than (0,0)'s; riverside trees `lean` toward the water. Density about
  twice (0,0)'s forest.
- **Stone:** `river_stone` variant that is **less worn**: `roughness` ↑, `facets` ↑, `flatness` ↓, `size` ↑
  (the stone hasn't travelled far).
- **Ground:** forest floor, shadier than (0,0): palette leaning toward `leaf_shadow`.
- **Water:** same river palette. A riffle/white-water accent is optional and needs no new tile.
- **New genomes needed:** none for v1. Nice-to-have: understory shrub, moss on stone.

**Floodplain, (0,1) (option B).**
- **Ground cover:** meadow grass and reeds. This needs a **new genome kind** (only creature/tree/rock exist
  today), which is Art's call.
- **Stone:** `river_stone` variant that is **well worn**: `roughness` ↓, `flatness` ↑, `size` ↓.
- **Trees:** sparse, flood-tolerant broadleaf on the margins (an `azure_oak` variant or a new species,
  Art's call).

## 10. Place sheets (for Story/Lore): physical facts plus the questions that are theirs

**Upper reach, (0,-1).** Facts: dense woodland on both banks, no crossing, the river as a barrier, water
everywhere, angular stone, and the outskirts fading into woods within a few rows.
Questions for Story/Lore:
1. Who, if anyone, uses the upper reach? Woodcutters, goblins, hunters, nobody?
2. Is either bank *claimed*?
3. Why has nobody bridged it here? (Physically it's bridgeable. The absence is a story fact.)
4. Is this river the "Azure River", and is this forest the "Azure Woods"? Art's genome `_lore` notes already
   use those names, but no bible doc or terminology entry does (§W8 leaves names open).
5. Does anything here feel feared, sacred or remembered?

**Floodplain, (0,1).** Facts: open fertile ground, seasonal flooding, a wide slow river, easy water access.
Questions: Is it farmed or grazed (that's settlement pressure, and would change its physical state)? Does the
town use it? Who controls the downstream route?

---

## 11. What this touches (if accepted)

- `Mechanics/data/panels.json`: a new entry plus the `NORTH` (or `SOUTH`) edge of `panel_0_0` (Engineering).
- `Mechanics/data/panels/panel_0_-1.json` (or `_0_1`): **the ID/filename scheme for negative coordinates is
  undefined**. `panel_0_-1` vs `panel_0_n1` is an Engineering call. **[OPEN]**
- `Mechanics/data/rooms.json`: new Rooms for the Panel (IDs, names and descriptions come after Story/Lore).
- Terminology map §7.5: any new region tag (option B's `m`).
- `rooms_panels` §R8: "Multi-panel content" moves from deferred to in progress.
- Affinity on the new Rooms: (0,0) uses forest EARTH 0.5 and river WATER 0.7. Continuity suggests the same,
  but affinity-field placement is out of scope under §W8 and belongs to Systems Design. **[OPEN]**

## 12. Out-of-Scope register

Deliberately **not** decided here: the river's source and sink; planetary location, plate and latitude of the
valley; Panel physical span (§S6); all names; inhabitants, ownership, history and culture; need-source and
chest placement; affinity values; new tile types (ford, marsh, cliff); diagonal-corner Panels; seasons; the
`m` region tag's name.

## 13. Open questions (for Shawn, via the Director)

1. **River flow:** north → south (recommended) or south → north?
2. **First edge:** upstream (0,-1) as recommended, or downstream (0,1) / east (1,0)?
3. **Panel scale:** literal (tens of metres; biomes change slowly) or compressed? (§S6 / LF-081)
4. **Panel(0,0)'s planetary location:** accept "inferred backward from its contents" as an explicit authored
   exception to §W3 for the starting area, until §S6 and the plate work place it?
5. **Seam rule:** strict passability match (EC2) or refuse-to-cross at mismatches?

## 14. Bible citations

§R1, §R2, §R3, §R8 (`lucentforge_rooms_panels_addendum_v1.md`) · §W3, §W8 (`lucentforge_world_foundation_v1.md`)
· §S2, §S6, §S7 (`lucentforge_world_map_scale_addendum_v1.md`) · §C1, §C4, §C6, §C7 (`lucentforge_climate_hydrology_addendum_v1.md`)
· terminology map §7.5 + Extension Protocol · data: `Mechanics/data/panels.json`, `panels/panel_0_0.json`,
`rooms.json`, `Mechanics/data/art/azure_oak.json`, `river_stone.json`.
