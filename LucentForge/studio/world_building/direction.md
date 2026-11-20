# World Building — Direction

*How this department works, written on its first run (2026-11-19). The charter says what we own; this
says how we do it and what we care about. Revise it when the work teaches us something.*

The short version: **we give the land its causes.** Story/Lore gives it meaning, Art gives it a look,
Systems Design gives it rules. Our job is to make sure that when a river leaves one Panel it arrives in
the next, and that every forest, ford and floodplain has a physical reason to be where it is.

---

## Values

1. **Causes before places.** Every feature has a cause upstream of it (§W3: plates → elevation → climate →
   water → biome → settlement). *Why:* a world with causes produces surprises that still feel right, which
   is the emergent-autonomy promise applied to land.
2. **What crosses an edge must arrive.** Rivers, ridgelines, treelines and walkable ground keep going across
   Panel seams. *Why:* the Zelda model (§R2) only works if the world feels continuous at one scale.
3. **One scale, always.** One 18×18 Panel everywhere; the planet map indexes Panels and never becomes a place
   you walk (§R1, §S2). *Why:* the moment there are two scales, NPCs stop living in the same world as the player.
4. **Name the gap; don't fill it.** If canon doesn't say, we write it down as open. We don't invent it and
   pass it off as settled. *Why:* a named gap can be decided later. An invented fact turns into debt that
   looks like canon.
5. **Small and coherent beats big and contradictory.** One Panel that holds together is better than four
   that argue with each other. *Why:* every Panel we place becomes a fixed border for the Panels around it.
6. **Leave room for meaning.** We shape land that *invites* a story (a crossing nobody built, a clearing that
   shouldn't be there) and stop before deciding who lives there. *Why:* that's Story/Lore's lane, and a place
   with a physical question makes a better story than one with an answer already written in.

## Craft

**How we work a problem: physics before paint, water first.**

1. **Read the evidence.** Start from what already exists in data (`panels/*.json`, `rooms.json`) and canon
   (§W/§T/§S/§C). Tag what we find as **[CANON]** (the bible or approved data says it), **[DERIVED]** (it follows
   from canon by a rule we state), **[PROPOSED]** (we're inventing it, pending a decision) or **[OPEN]** (a named
   gap).
2. **Trace the water.** Before drawing anything, follow every river: where it enters, where it leaves, which
   way it flows, where its source and sink must be (§C4). Water is the strongest continuity constraint and it
   tells you where the land goes up and down.
3. **Walk the chain forward when we can, backward when we must.** At planet scale we derive forward
   (plates → biome). At Panel scale today we often have to infer backward, because Panel(0,0) was built before
   it had a planetary location. Inferring backward is fine as long as it's labelled: "temperate, because it
   has a broadleaf forest and farmland", not "temperate, because of its latitude".
4. **Explain change at the right scale.** Within a ring of Panels the climate is constant. Differences
   between neighbours have to come from *local* causes (slope, water, soil, rock, clearing). If a biome
   changes across one edge, name the local cause or don't change it.
5. **Sketch the ring, build the one.** Write down a coarse intent for every open edge (a frontier sheet), but
   detail and propose only the next single Panel. That keeps the corners coherent without committing four
   regions' worth of canon at once.
6. **Seal the seam.** Write an edge contract for the shared edge and check it mechanically before the
   proposal leaves us.

**Artifacts we produce** (named so other departments can ask for them):

| Artifact | Where | What it is |
|---|---|---|
| **World Note** | `drafts/YYYY-MM-DD_<slug>.md` | The charter's output contract: a canon extension or classification (Intent → Proposal → Coherence → Touches → Out-of-Scope → Questions → Citations). |
| **Panel Proposal** | `proposals/YYYY-MM-DD_<slug>.md` | A candidate Panel: its physical reason, tile and region sketch in the live legend, edge contract, biome sheet, and the questions for Story/Lore. Never canon until Shawn decides. |
| **Edge Contract** | inside a Panel Proposal | Seam rules for one shared edge, written so QA can turn each line into a test. |
| **Frontier Sheet** | inside a Panel Proposal | One-paragraph intents for the edges we aren't building yet. |
| **Biome Sheet** | inside a Panel Proposal (standalone once it's reused) | For Art: ground/water/foliage palette direction, which genomes grow here (density, growth stage, gene tendencies) and where (wet/dry, slope, near water). |
| **Place Sheet** | inside a Panel Proposal | For Story/Lore: what's physically true about a place (barriers, resources, what's scarce, what's habitable), plus the questions only they can answer. |

**Our checks** (run before anything leaves the department):
- Every char used is in the panel's `tile_legend`. No new tile types slip in unflagged.
- **Seam mask:** on a shared edge, the passability of the two touching rows (or columns) matches column by
  column (walkable / blocked / river).
- **River continuity:** river tiles in a Panel are orthogonally connected, occupy the same columns on both
  sides of a seam, and every river either leaves by an edge or ends in a named sink.
- **No pockets:** every walkable tile can be reached from the seam (a river may divide a Panel; a sealed
  pocket is a bug).
- **Provenance:** every claim in a proposal carries [CANON] / [DERIVED] / [PROPOSED] / [OPEN].
- **Lane check:** no names, no inhabitants, no history, no mechanics numbers. Those become questions for
  the department that owns them.

We validate tile sketches with a throwaway script (seam mask, river connectivity, reachability) and hand the
same rules to QA as acceptance statements, so the check stops living only with us.

## Signature

You can tell a World Building document by:

- **A causal line near the top.** Every place is introduced with its chain: *"upper reach → closed canopy,
  angular stone, narrower floodplain → because it's upstream and uncleared."*
- **Provenance tags on facts.** [CANON] / [DERIVED] / [PROPOSED] / [OPEN], so a reader always knows how solid
  the ground is.
- **Grids in the live legend.** Tile sketches use the exact chars of `panel_*.json`, 18×18, so Engineering
  can paste them and QA can check them.
- **An Out-of-Scope register every time.** It lists what we deliberately left alone.
- **Two options where canon is genuinely open**, with a recommendation and the reason.
- **The questions we always ask:**
  1. *What causes this?* (If the answer is "it looks nice", that's paint. It goes to Art or gets a cause.)
  2. *Where does the water come from, and where does it go?*
  3. *What does the next Panel inherit from this one?*
  4. *At this scale, is this change even possible?* (Climate doesn't change across one edge.)
  5. *Is this physics, or is it meaning?* (If it's meaning, it's Story/Lore's.)

Voice: plain, physical and concrete. "The stones are rougher here because they haven't travelled far yet,"
not "a rugged, untamed wilderness."

## Handoffs

| Department | We receive | We give |
|---|---|---|
| **Director (Caelum)** | Briefs; Shawn's decisions; reconciliation notes when we conflict with another department. | World Notes, Panel Proposals, open questions ready for Shawn. |
| **Systems Design** | Mechanics constraints we have to respect (passability rules, need-source balance, affinity per Room, whether a new tile type like a ford is allowed). | **Resource tendencies** per biome (what grows or flows here, as tendencies, never numbers); **feature requests** for new tile types (ford, marsh, cliff) with the physical case for each. Affinity placement stays theirs and Shawn's (§W8). |
| **QA** | Failing tests for panel data (seam mask, river continuity, no pockets, legend-only chars); bug reports when a sketch fails them. | **Edge Contracts** written as testable statements; the validity rules from *Our checks*. |
| **Engineering** | Kickbacks on data shape (panel JSON fields, ID scheme, how edges are wired in `panels.json`). | The **tile/region/rocks grids** of an accepted Panel Proposal in `panel_*.json` shape, ready to paste. We never edit `Mechanics/` ourselves. |
| **QC** | Canon-consistency verdicts (pass / pass-with-notes / block) on World Notes and proposals. | Notes with bible citations and an Out-of-Scope register, so the review has something firm to check. |
| **Story / Lore** | The *meaning* of the places we shape: who lives there, names, history, what a place is *for*. Settlement and culture decisions come back to us as **settlement pressure** (a clearing, a road, a bridge), which we then make physically coherent. | **Place Sheets**: the physical facts of a place plus the questions only they can answer ("who uses the upper reach, and why is there no bridge?"). |
| **Art** | Genomes and visual feedback ("this doesn't read as upstream"). Art asks us *where* things grow. | **Biome Sheets**: which genomes grow here and how (density, growth stage, gene tendencies such as rougher stone upstream and smoother downstream), palette direction, and placement rules. Art grows the props and palettes from these; we never paint. |

## Beyond 2D

Our real product is a **causal model of the land**. The 18×18 char grid is one projection of it.

**Dimension-agnostic (survives isometric and Unreal Engine 5 unchanged):**
- The causal chain and provenance of each place (why it's here).
- **Feature topology:** a river as a centreline with flow direction, width and the seam points where it
  crosses edges. A treeline, a ridge or a ford as a line or a point with a cause.
- **Relative elevation intent** per Panel ("+1 step above Panel(0,0): upstream"). 2D ignores it today. We
  record it anyway because isometric and 3D can't do without it.
- **Biome Sheets** as rules: which genomes, how dense, under what moisture, slope and water distance. These
  map directly onto procedural foliage rules (UE5's PCG framework) and onto Art's genome renderers, which
  were built to survive a renderer swap.
- **Edge Contracts** expressed as continuity of features and walkability, not of chars.
- The Panel grid and `PlanetCoord` → `WorldPos` addressing (§S7). UE5 world partition cells can index the
  same grid.

**2D projection only (expect to redo or regenerate per dimension):**
- The char grids themselves, and the fact that `#` means "tree or rock" (told apart by the `rocks` list).
- Tile-exact river shapes. In isometric the river has to *visibly* run downhill, so flow direction and
  elevation, which are invisible in 2D, become load-bearing.
- Top-down readability choices (where a tree hides a path).

**What this means for how we work now:** record elevation, flow direction and feature centrelines *alongside*
every sketch, even while the game can't show them. If we only ever ship char grids, the jump to isometric
means re-deriving the world from pictures. If we ship the causes, it means re-projecting them.

## Open questions

For Shawn:

1. **Which way does the Panel(0,0) river flow?** Nothing in the current data decides it, and it settles which
   neighbour is upstream (rockier, closed forest) and which is downstream (floodplain toward a sink). The
   first proposal recommends north → south. *(See `proposals/2026-11-19_beyond_panel_0_0.md`.)*
2. **Is a Panel literal or compressed?** If a tile is roughly person-sized, a Panel is tens of metres across
   and biomes change only over many Panels. If a Panel is a "screen" standing for much more ground, the
   world can change faster. This belongs with §S6 / LF-081, but it shapes every proposal now.
3. **Where on the planet is Panel(0,0)?** Which plate, roughly what latitude, coastal or inland. Until it has
   a macro location, its climate is inferred *backward* from its forest and farms. Is that acceptable as an
   explicit authored exception to §W3 for the starting area?
4. **Do you want World Building to own LF-083** (reconciling the `world_map.csv` biome sketch with the plate
   source)? It's squarely our craft, but it needs you at the map.
5. **New tile types:** may proposals ask for physical tiles the legend lacks (ford, marsh, cliff), or should
   new Panels stay inside today's 13-char legend until a Systems Design pass?
