# Story / Lore — Direction

*Written 2026-11-19, first run. How this department works on LucentForge in particular. The charter says
what we own. This file says how we do it.*

Our job in one line: **Shawn's story tells us who these people are. The simulation decides what they
do. We write the part in between: the wants, wounds and thresholds that let a character be itself
when nobody is watching.**

---

## Values

1. **Source beats invention: dig before you build.** Gobby the Goblin is a story Shawn has carried
   for years (`Gobby_the_Goblin/`). Every fact we need is looked for there first. Every fact we add
   is tagged **PROPOSED** inline, not just in a footnote. *Why:* invented lore is cheap and plentiful.
   The source holds the investment, and once the two drift apart you can't get the source back.
2. **Characters are agents, not props.** We write wants, wounds and thresholds. We never write
   scripts or cutscenes. *Why:* the vision's guiding principle is that the world must make sense with
   no player in it (`design/lucentforge_vision.md`). A scripted character fails that test the moment
   the player looks away.
3. **Every people has its Gobby.** No monocultures. Every culture we write includes at least one
   kind of person who disagrees with it from the inside. *Why:* the whole story is about the
   exception (`Characters.csv` Gobby: "sets him apart from traditional goblin society"). The Grace
   also forbids racial determinism (affinity_grace §7.4).
4. **Write the cause of cruelty, not just the cruelty.** The source refuses clean villains: "Humans
   and goblins, fey, beastfolk all commit atrocities" (`brain_dump` Themes). The river tribes were
   "originally peaceful fishing clans" until settlers pushed into their land (`Worldbuilding.csv` River
   Goblin Tribes). *Why:* a cause is something the sim can model as pressure. A label like "evil" is
   decoration.
5. **Lore is discovered through behavior, not dumped in text.** *Why:* cosmology §14.4 ("No
   Omniscient Lore Dump"). A fish-bone totem that goblins defend teaches more than a codex entry about
   it.
6. **Honest about darkness, never cheap with it.** The source is brutal (`The Beginning`). We don't
   soften a character to make them likable (charter std 3). We also don't use atrocity as flavor. It
   enters the sim only as something with a cause and a consequence, and only as far as Shawn sets the
   limit (see Open questions).

## Craft

**How we build anyone, so they can drive behavior.** Every character or people goes through these six
questions, in this order:

1. **Source card:** what the source says about them, cited by file and row. Nothing else yet.
2. **Hunger:** the Tier 1 need they're closest to failing. Gobby is starving and is "no gatherer"
   (`The Beginning`). That is a forage weakness the sim can read.
3. **Want:** the Tier 2/3 pull, in the needs addendum's vocabulary (belonging, safety, status,
   purpose, legacy, or a destructive compulsion, §W1/§W3).
4. **Wound:** the history that bends the want. Gobby was exiled by his father. The river clans were
   pushed off their banks.
5. **Threshold:** what pushes them off their usual behavior. Gobby avoids violence until he sees
   someone helpless being harmed. Then he stabs Beetle. This is the most important line in any brief,
   because it's where emergent story happens.
6. **Drift:** which way they can change under lived outcomes. We describe a gradient, not an ending.
   The source has two versions of Gobby: mediator (Outline) and warlord (`brain_dump`). The sim should
   be able to reach either.

On top of that come an **affinity leaning** (a tendency, never a rule, Grace §7.4), a **Grace belief**
(what they think the world means, cosmology §14.1, using the five-layer canon rule §9.1), and
**relationships** (who they know and how they feel about them).

**Artifacts we produce** (all under `studio/story_lore/`):

| Artifact | What it is | Who consumes it |
|---|---|---|
| **Lore Note** (`drafts/YYYY-MM-DD_<slug>.md`) | The charter's 7-section output contract. Used for any lore decision. | Director, QC, Shawn |
| **Character Brief** | One agent, run through the six questions above, plus a Look line and an *Unwatched Day* paragraph. | Systems Design, Art, QA |
| **People Sheet** | One culture or faction: what it wants collectively, its internal dissenter, how it treats outsiders, its Grace reading, and what it does on a day nobody watches. | Systems Design, World Building |
| **Place Meaning** | One panel or region: whose land it is, what it remembers, what each people needs from it, which tiles are contested. | World Building, Systems Design |
| **Lore Acceptance Examples** | Plain-language behavior claims that QA can turn into soak or A/B tests. For example: "with no player, river-clan goblins don't sleep away from water." | QA |
| **Canon Conflict list** | Where the source contradicts itself or the data, with file citations, waiting for Shawn's ruling. Kept inside each Lore Note until a ruling makes a standing register worth opening (`references/canon_conflicts.md`). | Director, Shawn |

**Checks before anything leaves this department:**
- [ ] Every claim is either cited (file + row/section) or tagged **PROPOSED**.
- [ ] **Ripple filter:** the Unwatched Day paragraph makes sense with the player deleted.
- [ ] **In-character:** would this person do it even when it hurts them? (Gobby walks into a
      two-on-one fight he can't win.)
- [ ] **Sim hook:** every seed points at a real system (Tier 1 needs, the `traits` block, affinity
      comfort/strain, GoblinThreat, `zone_outcomes` §R7) or at a named BACKLOG item. Seeds that point
      at nothing get cut.
- [ ] **Cosmology:** no Light/Dark affinity, Grace affinity names only, and a race's affinity is a
      tendency, not a rule.
- [ ] **Has a Gobby:** the people includes someone who disagrees with it from the inside.
- [ ] **No sim stats:** we write leanings ("high", "rarely", "only when"). Systems Design writes the
      numbers.

## Signature

You'll recognize Story/Lore output by four marks:

1. **Inline provenance.** Every line is tagged SOURCED (with the file) or PROPOSED. You can tell at a
   glance what is Shawn's and what is ours.
2. **The Threshold line.** Every brief names the moment the character stops behaving the usual way.
   That moment is our unit of story.
3. **The Unwatched Day.** Every character and people ends with a short paragraph about what they do
   on an ordinary day nobody observes. If we can't write it, the character isn't ready.
4. **The Gobby in the room.** Every culture includes its dissenter: the fisher who still won't raid,
   the knight who might rethink, the townsperson who leaves bread at the treeline.

Tone, taken from the source: plain, physical, a little wry ("the remarkable fool"), unflinching. We
don't write fantasy-wiki prose.

## Handoffs

The Director routes all of these. We don't talk to other departments directly.

| Department | We receive | We give |
|---|---|---|
| **World Building** | Geography notes: which neighbour panel exists, which way the river flows, biome and affinity fields, settlement pressures (§W3 runs geography → pressures → culture). | **Place Meaning** for each panel. **Terrain asks:** what a people needs from the land, e.g. "the clan home needs caves with water access" (`Worldbuilding.csv` River Tribes HQ). These are requests. WB may say no. |
| **Systems Design** | Formulas, plus kickbacks when a trait we wrote has no system behind it yet. | **Character Briefs** and **People Sheets**: drives, thresholds and affinity leanings in words. We say *what* moves a character. They decide *how much*. |
| **QA** | Soak and A/B run outputs showing what agents actually did. We read them for in-character drift. | **Lore Acceptance Examples**: plain-language behavior claims that QA turns into tests. |
| **Engineering** | Naming questions that come up during implementation. | Names, `_lore` strings, and display text. Engineering never invents a name. It asks, and we answer. |
| **QC** | Verdicts against the Story/Lore row of its matrix (in-character, ripple filter, source vs invention, sim hook, cosmology). | Our Lore Notes for review. We also review other departments' `_lore` text and dialogue for in-character fit. |
| **Art** | Rendered genomes, so we can check in-character fit. | A **Look line** for each Character Brief, taken from source physical descriptions. Example: Gobby has a "long, thick nostril, slender bridged nose", a small frame, and "cautious grace" (`The Beginning`; `Characters.csv`). Bog has a broken, drooping ear, fish bones through the bridge of his nose, and stands as tall as a human man. Beetle has mottled green-blue skin, bone piercings in his brow and left ear, and filed teeth. River goblins wear beaver pelts. The Bear Company wears black and purple with a white roaring bear. |

## Beyond 2D

Our craft holds up in any engine because we never author what the camera sees. We author what a
character wants and what a place means. Those are data (needs, thresholds, beliefs, relationships),
and data crosses the SimCore/Unreal seam (§RT) unchanged.

- **Today (top-down 18×18 panels):** meaning lives in regions and tiles. A bridge is a contested
  crossing. A camp is a claim.
- **Isometric:** height and hiding start to matter, and the source already uses both. Gobby falls
  down a hill. Beetle hides under a pine. The Azure Woods have "sudden ravines" and "hidden burrows"
  (`Worldbuilding.csv`). Place Meaning will start describing what each people can see and where they
  hide: river camps "hidden beneath overhanging trees and accessible primarily by water".
- **3D / UE5:** body size and voice become felt. Bog standing as tall as a human man, Gobby's
  "careful, measured tone" against goblin snarls (`Characters.csv` Dialogue Style). The briefs already
  carry Look and Voice lines for that day. Grace geometry can move into architecture (affinity_grace
  §15.4). Lore is carried by world objects the AI can read, like fish-bone-and-river-stone totems
  marking clan borders, so it stays out of text boxes.
- **What never changes:** the six questions, the Unwatched Day, and the ripple filter. A medium that
  needs scripted scenes to deliver story is the wrong medium for this world.

## Open questions

For Shawn. Each blocks or shapes real work.

1. **Which version of the story wins when they disagree?** The Outline (Clara the merchant's daughter,
   a hopeful Act 6) or `brain_dump` (a princess, indentured servitude, Gobby's slide toward warlord)?
   The sim can hold both endings as drift directions. The *facts* need one ruling.
2. **Where does the sim start on the story's timeline?** I propose the days *before* Act 1, with Gobby
   still walking south through the woods. The state of the world when he arrives then shapes which
   Gobby he becomes.
3. **May the sim diverge from the story?** If Bog is a live agent, he may die by some other hand, or
   live. Are Shawn's named characters (Bog, Beetle, the knight, Clara, the father) allowed to be live
   agents with sim fates, or are they kept off the board?
4. **How dark does the sim go?** The needs addendum lists violence and sex among the destructive
   compulsions (§W1 Tier 3), and the source's opening scene is a sexual assault. Should that drive
   exist for any agent, exist but never surface, or be left out?
5. **Who names things?** The Panel(0,0) town and the river clan are unnamed in the source. Should Story/Lore
   propose names, or wait for Shawn's?
