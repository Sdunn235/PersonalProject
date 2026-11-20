# Lore Note — Beyond Panel(0,0): who lives past the starting panel (v1, DRAFT — pending QC)

> **PROPOSAL — not canon until Shawn decides.**
> Story/Lore, 2026-11-19, first run. This note covers people, history and meaning. Terrain is World
> Building's call, made in parallel. Every claim is tagged **[SOURCED: file]** or **[PROPOSED]**.
> Source files are in `Personal Project/Gobby_the_Goblin/`. "Worldbuilding", "Characters" and
> "Outline" mean the three `Gobby The Goblin WIP  *.csv` files. `brain_dump.docx` is actually plain
> UTF-8 text and reads fine (see §6).

---

## 1. Intent

Arc B opens the world past the starting panel (LF-010 step 2). Before a second panel exists, the
first one needs a *story reason* for its layout: a river, a goblin camp hard against the west bank,
and a farm town with two bridges on the east. This note does three things:

1. Says what Panel(0,0) **is** in Gobby's world, and whose land it is.
2. Offers three candidate neighbours, each with its people, what they want, and their tension with
   Panel(0,0). Each comes with the *character seeds* (needs, wants, thresholds, affinity leanings)
   the sim would need.
3. Recommends one to open first.

Why it matters to the simulation: today **GoblinThreat** (micro-sim §Goblin Threat System) is a
number that rises over time. This note gives it a *people* with hunger, grievance and a home. The
threat can then rise and fall for reasons the sim can model, with or without a player.

---

## 2. The narrative

### 2.1 What Panel(0,0) is: the hamlet at the woods' edge

**The forest (west)** is the human-facing edge of **the Azure Woods**, "a natural boundary between
the civilized human lands and the wild territories claimed by various goblin tribes"
[SOURCED: Worldbuilding, The Azure Woods]. The art genomes already put us here (`azure_oak.json`
`_lore`: "A broadleaf of the Azure Woods").

**The river** is a reach of the **Azure River Valley** waterways where they leave the woods
[PROPOSED placement]. The valley "flows through the middle of the woods" [SOURCED: The Beginning],
and the woods are cut by "numerous waterways" [SOURCED: Worldbuilding, Azure Woods].
`river_stone.json` `_lore` already says "Azure River banks".

**The town, farm, homes and silo (east)** form a **frontier farm hamlet**. It is one of the
"carefully managed farmland and settlements that supply the city's diverse dietary needs" around
**Alexandrite** [SOURCED: Worldbuilding, Alexandrite]. The hamlet itself, and its tie to
Alexandrite, are [PROPOSED]. Its silo and storage fit a place that grows food for somewhere else.

**The goblin camp (SW, rows 13–14, right on the west bank)** is a **river-clan outpost**: one of the
"smaller outposts for hunting and surveillance" that the River Tribes keep around their primary
camps [SOURCED: Worldbuilding, River Goblin Tribes, Headquarters]. "River banks throughout the woods
show signs of habitation, with crude shelters and territorial markers" [SOURCED: Worldbuilding,
Azure Woods]. Reading *this* camp as one of those outposts is [PROPOSED].

**Whose land is it? Contested, and the source explains why.** The River Tribes "maintain control over
their ancestral waterways and surrounding territories" [SOURCED]. They were "originally peaceful
fishing clans" who "evolved into more aggressive groups following increased encroachment on their
territories by expanding human settlements" [SOURCED: Worldbuilding, River Goblin Tribes, History].
**The hamlet is that encroachment.** It is the clans' history written onto one panel
[PROPOSED reading of a SOURCED history].

- **Why the camp sits *across* the river from the town:** water is the clans' wall. Their dwellings
  are "accessible primarily by water" [SOURCED], and Beetle "moves with surprising quickness in
  water" [SOURCED: Characters, Beetle]. The outpost keeps the river between itself and the people it
  watches.
- **The two bridges (rows 4–5 and 11–12)** are the hamlet's crossings into clan water. They are the
  most contested tiles in the panel [PROPOSED]. To the clan, every crossing is a trespass. To the
  hamlet, every crossing is a road.
- **The people already living here.** Gruk (grunt) and Skrix (scout) read naturally as the outpost
  watch: "scout" matches "surveillance". On the hamlet side, Alder (ranger) and Grom (fighter) read
  as its own watch, and Sylva and Elara as its two Gift-users [PROPOSED readings of
  `entities.json`]. Gruk and Skrix carry EARTH affinity. A river people with an Earth-leaning
  individual is allowed, since racial tendency is not determinism (affinity_grace §7.4). Whether
  they are river-clan at all is an open question (§6).

**Panel(0,0)'s Unwatched Day [PROPOSED].** The hamlet farms, carts grain to the silo, and its watch
walks the near bank. The outpost fishes and watches the bridges. When the clan upriver goes hungry,
because the fish ran thin or the hamlet fenced the shallows, the outpost crosses a bridge after
grain. GoblinThreat rises because the clan is hungry and aggrieved, not because a timer ticked.

### 2.2 Candidate A: along the river into the woods. The clan's home water.

*Geography fit:* WB's "follow the river" candidate. In the source, the woods' north edge meets the
Great Plains [SOURCED: The Beginning], and Panel(0,0) faces human land to the east. So the valley's
heart most likely lies **north, upriver**. Which way the river actually flows is WB's call.

**Who lives there: the river clan's primary camp** [SOURCED pattern, PROPOSED placement]. It is
"marked by distinctive totems made from fish bones and river stones". Its dwellings "blend natural
cave systems with constructed wooden structures, often hidden beneath overhanging trees". Its borders
are "marked by skeletal totems and painted warnings, though boundaries between tribes remain fluid
and contested" [SOURCED: Worldbuilding, River Goblin Tribes, HQ]. Blue-tinted skin and beaver pelts
[SOURCED: Worldbuilding; The Beginning]. This is **Bog and Beetle's people**: "Born and raised in the
river goblin tribes near the Azure Woods" [SOURCED: Characters, Beetle]. Bog is a "prominent warrior"
known along "the waterways his tribe controls" [SOURCED: Characters, Bog].

**What they want** [SOURCED: Worldbuilding, River Goblin Tribes, Goals]:
- Hold their ancestral waters.
- Live by "hunting, fishing, and occasional raiding of travelers and caravans".
- Prove strength against neighbouring tribes and outsiders.
- Resist integration.

"Some tribes maintain limited trade relations with other forest inhabitants" [SOURCED].

**The clan's Gobby [PROPOSED, grounded in SOURCED history]: the fishers.** These are the agents who
still answer hunger with a net rather than a raid. They carry the older "peaceful fishing clan"
identity the history describes. They are the clan's dissenters and its possible traders.

**Their Grace reading [PROPOSED].** Cosmology §8.5 offers two unassigned examples that fit here:
goblin traditions held "orally as paths, camps, hunger, fire, and boundary", and aquatic cultures
that "draw the Veil as a membrane". The proposal: **the clan holds that the river's surface is the
Veil, and gives its dead to the water.** That makes the river sacred ground, not just territory.
Hamlet waste or nets in the river become desecration, and the clan fights harder over water than over
land. This is a folk interpretation under the layered canon rule (§9.1). It is not cosmological
truth.

**Tension with Panel(0,0):** the outpost belongs to the clan. Raids run downstream into the hamlet
and retreats run back up. Caravans on the merchant trails are prey.

**Character seeds** (leanings, not stats):

| Seed | Hunger (T1) | Want (T2/T3) | Wound | Threshold | Affinity leaning | Traits |
|---|---|---|---|---|---|---|
| **Clan warrior** (the Bog type) [SOURCED disposition] | meat: fish, game, raid spoils | Status and dominance. "Might makes right" [SOURCED: Bog]. Destructive compulsion: violence (§W3). | Generations of encroachment. The hamlet *is* the wound. | An insult to his strength, or a prize taken from him, leads to violence. | Water; river-mud Non-Newtonian [PROPOSED tendency] | aggression high, fearfulness low, sociable only within the clan |
| **Fisher** (the dissenter) [PROPOSED] | fish | Routine; belonging to the clan as it used to be | The same history, remembered differently | Fights only at the water's edge, in defense | Water | aggression low, fearfulness moderate, curiosity toward outsiders moderate |
| **The clan as a whole** (People Sheet) | Clan food stock | Hold the water. Grievance rises with human bridge traffic. | Encroachment | Hunger plus grievance over a threshold leads to a raid | — | — |

**Ripple filter:** passes. The clan fishes, sleeps, fights over rank and goes hungry with no player
anywhere.

**Lore Acceptance Examples for QA:**
- With no player present, river-clan agents end every night within a short distance of water.
- Raids into Panel(0,0) are rarer when the clan is fed than when it is hungry.
- Across a soak run, at least one clan agent never starts a raid.

### 2.3 Candidate B: into the woods (west). "The Dark Boundary".

*Geography fit:* WB's "deeper forest" candidate.

**The place** [SOURCED: Worldbuilding, The Azure Woods]: "eternal twilight"; "a perpetual mist clings
to the forest floor, giving the woods their signature azure tint"; "luminescent fungi" on fallen logs;
"thorny undergrowth conceals countless burrows and hidden paths"; "sudden ravines, steep hills"; "few
dare to venture deep into its interior without significant protection". Its other name is
**"The Dark Boundary"** [SOURCED].

> **Cosmology check:** in this world Dark is ontological absence (cosmology §2.3), not shade. "Dark
> Boundary" should stand as a **folk name** born of twilight and fear (layered canon §9.1). It should
> not be read as a real thinning of the Veil unless Shawn wants that.
>
> **Grace hook [PROPOSED, WB to confirm physics]:** the azure mist reads naturally as a
> **Colloidal Dispersion** field ("Air + Water region → fog and suspended fields", affinity_grace
> §8.4). The bible even lists "Colloidal fog carries ancestors" as a sample NPC belief (§14.3).

**Who lives there:**
- **A forest tribe.** Bog's first guess on finding Gobby was "I thought you were from the forest
  tribe" [SOURCED: The Beginning], so one lives near the river clans' land. The source gives nothing
  of its character. Gobby himself is "a forest goblin", and his father is "the forest Goblin
  warlord" [SOURCED: brain_dump, Vol 1]. Forest goblins are **not** a peaceful people. Gobby's home
  camp had "huts packed so tight that waste and debris collected", a "rage full father", and "peers
  who constantly beat and belittled him" [SOURCED: The Beginning]. Gobby is the exception.
- **Inter-tribe distrust:** "he knew why the tribes didn't trust each other" [SOURCED: The Beginning].
  The River Tribes compete "against other river tribes and outside forces" [SOURCED].
- **Hobs:** a goblin with "the innate spark of Talent" becomes a hob [SOURCED: The Beginning]. The
  father's army is "Goblin and Hobgoblin" [SOURCED: brain_dump]. Bible: Hobs own a `bp` pool
  (needs addendum §W4), and the spark is deferred to genetics (LF-037).
- **Predators** "in the wood" [SOURCED, unspecified]. *Ignarix the dragon* spawns at forest tile
  (1,8) in `entities.json`, but the source never mentions dragons. See §6.

**Tension with Panel(0,0):** the deep woods are what both the hamlet and the outpost fear. A
forest-tribe band moving through would hit the river clan's borders before it hit the hamlet
[PROPOSED].

**Where Gobby enters.** This is his road. Act 1 opens with him walking through the Azure Woods toward
Alexandrite, starving, following the smell of spiced smoke [SOURCED: Outline, Act 1 "The Azure
Woods"; The Beginning].

**Character seeds:**

| Seed | Hunger (T1) | Want (T2/T3) | Wound | Threshold | Affinity / Gift | Traits |
|---|---|---|---|---|---|---|
| **Gobby** [SOURCED unless noted] | Starving, and "no gatherer": a few handfuls "took him the better part of the day". Weak forager. | Belonging (Alexandrite, acceptance). He is the named test case for the Social Belonging want (LF-031). | Exiled by his father. He once pleaded with his father to stop a raid. | Non-violent until he **witnesses harm to someone helpless**. Then he acts whatever the odds (stabs Beetle while outnumbered). | **Not a Hob** ("lacked innate spark of Talent"). A weak Gift he can later train (brain_dump: sorceress and druid teach "the basic of magic"). Innate affinity is **unsourced**: ask Shawn. | aggression low, fearfulness high but overridden at his threshold, sociability toward outsiders high |
| **Forest-tribe goblin** [mostly PROPOSED] | game, scavenge | Status through strength. "Goblins only listen to those with strength" [SOURCED: The Beginning]. | The Great Divide's hero-company raids [SOURCED pattern] | Weakness seen in others leads to contempt and harassment | unknown | aggression high |

**Gobby's drift** [SOURCED both ends]: toward **mediator** (Outline, "A Place Among Others") or toward
**warlord**, "exactly what he once swore he'd never be" (brain_dump, Vol 3). The world state when he
arrives should decide which way he leans. This is the vision's "Gobby-as-stone".

**Ripple filter:** passes for the place and the tribe. Gobby needs the hunger, want and threshold
seeds above in order to *be* an agent rather than a cutscene.

### 2.4 Candidate C: out of the woods (east). The merchant trail and Alexandrite's frontier.

*Geography fit:* WB's "open land east" candidate.

**The place** [SOURCED pattern, PROPOSED placement]:
- "Well-worn but dangerous merchant trails skirt the woods' edges" [Worldbuilding, Azure Woods].
- Alexandrite is a crossroads of trade routes, and "watchtowers maintain vigilance against potential
  raids" [Worldbuilding, Alexandrite].
- "Recent goblin raids have made the city cautious" [Outline, "Gates of Alexandrite"].

**Who lives there:**
- **A watchtower crew** [PROPOSED placement; watchtowers SOURCED]. The hamlet looks to it for
  protection.
- **The Bear Company**, monster hunters "patrolling the dangerous territories between civilized
  lands" [SOURCED: Characters, Rhiener]. The party: a red-haired knight; "the largest of the trio", a
  gargantuan warrior who weeps on rescuing the girl; a sorceress; a druid [SOURCED: The Beginning;
  brain_dump]. Hero companies "often made little distinction between hostile raiders and peaceful
  goblin communities", which "led to retaliatory cycles of violence" [SOURCED: Worldbuilding, The
  Great Divide].
- **Caravans**: Clara's merchant father [SOURCED: Outline, "Unlikely Allies"].
- **Bandits**: Clara was "separated from her caravan during a bandit attack" [SOURCED: Outline]. These
  are human raiders, and they are the source's proof that the woods' edge isn't dangerous only
  because of goblins.

**Tension with Panel(0,0):** the hamlet supplies the city and relies on its patrols. A Bear Company
patrol that clears the outpost would, by the Great Divide's own logic, raise the clan's grievance
upriver. Panel(0,0) would then sit **between two pressures**, which is exactly the micro-sim's "town
survives or collapses" test.

**Character seeds:**

| Seed | Hunger | Want | Wound | Threshold | Affinity | Traits |
|---|---|---|---|---|---|---|
| **The knight** [SOURCED] | — | Duty, protecting the innocent | Years of monster hunting | **Prejudice against Mons, "especially against goblins"**, which he can revise when "presented with evidence that challenges his preconceptions" | unsourced | aggression moderate and disciplined, fearfulness low |
| **Druid** [SOURCED: brain_dump] | — | Purpose: reads events as fate | — | Argues for mercy when she sees a sign | unsourced | curiosity high |
| **Sorceress** [SOURCED: brain_dump] | — | Knowledge: "remains neutral, simply observing" | — | Rarely intervenes | unsourced | curiosity high, sociability low |
| **Bandit** [SOURCED existence, PROPOSED seeds] | food, coin | Wealth | — | A weak caravan leads to a raid | — | aggression high, fearfulness moderate |
| **Caravan merchant** [PROPOSED seeds] | — | Wealth, safety of kin | — | Losing kin brings everything he can buy to bear on the search (Outline: he organizes a search party) | — | — |

**Emergent hook [PROPOSED]: misattribution.** A bandit raid on a caravan or the hamlet, seen by
nobody, gets remembered as "goblins did it". The hamlet's *perceived* goblin threat rises while the
real raiders were human. Cosmology §14.2 separates what happened from what the NPC believes
happened. This is the source's "blurred morality" theme turned into a sim rule.

**The knight's drift:** prejudice is a belief value (cosmology §14.1, "affinity prejudice" and its
racial cousin). Witnessing a goblin act against type should move it, slowly. That is the
heartbeat vision's Interpretation + Drift Loop.

**Ripple filter:** passes. Patrols, caravans and bandits all run on their own wants. **Risk:** this
puts Shawn's named characters on the board early, and in the source the knight is the hand that
kills Bog. See §6, question 3.

### 2.5 Where Gobby's story touches each candidate

| Candidate | Story contact | Source |
|---|---|---|
| A: clan home water | Bog and Beetle's tribe. Beetle survives the stabbing and brings "reinforcements from his river tribe" for revenge. | Outline Act 1, "The Price of Mercy"; brain_dump Vol 1 (war party at the gates) |
| B: deep woods | Gobby's road and his fall down the hill. The forest tribe. His father's people at the woods' north edge by the Great Plains. | The Beginning; brain_dump Vol 1 and "Alexandria Under Siege" |
| C: trail and frontier | The Bear Company's patrol, Clara's caravan and the bandits, the gates of Alexandrite. | Outline Act 1, chapters 2–4; Characters, Rhiener |

### 2.6 Recommendation: open **Candidate A** (the clan's home water) first

1. **Best sourced.** The River Goblin Tribes row is the most complete *people* in the source: goals,
   history, headquarters, look. Almost nothing needs inventing.
2. **It explains what's already on Panel(0,0).** The camp, the river, the bridges and GoblinThreat
   stop being props and become a people with hunger and grievance.
3. **It's the strongest ripple test.** Clan agents travel between the outpost and home with no
   player, so the second panel and the off-screen sim (LF-010 step 2, LF-120) get real traffic to
   carry.
4. **It sets the stage for Gobby without spending Shawn's characters.** The clan home can start with
   *unnamed* clan agents. Bog and Beetle wait for Shawn's answer on question 3.

**Then C** (pressure from the human side, so Panel(0,0) sits between two forces). **Then B**, when
Gobby enters as an agent. If WB's geography makes the river end at Panel(0,0)'s edge, A can't open,
and C is the next ready choice.

---

## 3. Source basis

**Established (cited inline):** the Azure Woods as a boundary, its sensory facts, and its folk name
"The Dark Boundary". The River Tribes' goals, history, headquarters and look. Alexandrite's farmland
and watchtowers. The Great Divide's retaliation cycle. Gobby's hunger, exile, threshold and lack of
the Hob spark. Bog's and Beetle's dispositions. The knight's prejudice and capacity to reassess. The
bandits and the caravan. Bog's "forest tribe" line. Gobby as a forest goblin and his father as the
forest warlord.

**Proposed (ours):** Panel(0,0) as an Alexandrite supply hamlet. The camp as a river-clan outpost.
The bridges as contested tiles. The clan home placed upriver. The fishers as the clan's dissenters.
The river surface as the Veil. The mist as a Colloidal field. The watchtower placement.
Misattribution as an emergent hook. All seed values in the tables marked PROPOSED.

**Canon conflicts found (source vs source, source vs data). None are resolved here; they need Shawn:**

| # | Conflict | Sources |
|---|---|---|
| 1 | The knight's name: **Rhiener** vs **Roland** vs **Reihner** | Characters: Name "Rhiener", Other Names "Sir Rhiener of the Bear Company", but Background "Sir Roland". Outline: "Sir Roland". brain_dump: "Reihner". Unnamed in The Beginning (red-haired). |
| 2 | The rescued woman: **Clara, a merchant's daughter**, vs **a princess** | Outline "Unlikely Allies": Clara, merchant father. brain_dump Vol 1: "a human princess". The Beginning: "At last the princess is safe", "royal charge". Characters: "position of some social standing". |
| 3 | The arc's direction: hopeful mediator vs warlord descent. Alexandrite "monster quarter" vs "second-class citizens" and servitude. | Outline Acts 5–6; Worldbuilding, Monster Races; brain_dump Vols 1–3. *(The second half may be layered rather than contradictory: official tolerance alongside lived oppression, per cosmology §9.1.)* |
| 4 | Beetle's fate after the first fight | Outline: leads reinforcements in "The Price of Mercy", outcome unstated. brain_dump: leads a war party at the gates and is killed with Gobby's help. |
| 5 | **Grom: goblin or human?** | `Mechanics/data/art/grom.json` `_lore`: "tanky goblin". `entities.json` npc_03: `subtype: "human"`, fighter, spawns in town. |
| 6 | The memory note `project_gobby_world` says **"Forest Goblins: … more peaceful"** | Not supported by the source. Gobby is the exception, and his forest people are warlike (The Beginning; brain_dump "forest Goblin warlord"). The same note and BACKLOG **LF-005** say `brain_dump.docx` is unreadable. It is plain UTF-8 text with a `.docx` extension (`file` reports "Unicode text"). |
| 7 | City name: "Alexandrite" vs "Alexandria" | brain_dump uses "Alexandria" in the "Alexandria Under Siege" section. Likely a typo. |

*Out-of-lane observation for QC:* `needs_wants_drives_addendum` and `world_foundation` both use
`§W1…` section labels. "§W3" is ambiguous.

---

## 4. Ripple-filter check

The Panel(0,0) reading, Candidate A and Candidate C all pass. Hunger, grievance, duty, greed and
prejudice drive every group, and none of them needs a player. Candidate B passes for its place and
tribe. Gobby passes only if he gets the hunger, want and threshold seeds; as a set piece he would
fail. The one thing this note refuses is a scripted Act 1. If the hill, the pine and the knight
happen, they should happen because the seeds lined up.

---

## 5. Simulation hooks

| Hook | System it touches | Status |
|---|---|---|
| GoblinThreat driven by clan hunger and grievance, not time | micro-sim GoblinThreat; Tier 1 hunger | Systems Design to formalize |
| River clans comfortable near water and strained away from it, which makes raids short | Affinity Behavioral Loop (region affinity → comfort/strain → relocate) | Exists. Needs a water-leaning field on river regions (WB and Systems Design). |
| Bridge crossings raise clan grievance | RoomType `BRIDGE` + ZoneCrossing (§R3–§R4) + `zone_outcomes` (§R7) | Design |
| Gobby's threshold: witnessed harm to the helpless overrides low aggression | drives / traits | Design (pairs with LF-035) |
| Gobby's poor foraging | forage tiles `g` + Tier 1 hunger | Exists (forage); per-agent skill is design |
| Misattributed raids | belief vs fact (cosmology §14.1–14.2) | Design, later arc |
| Knight's prejudice drifts with witnessed evidence | Interpretation + Drift Loop (heartbeat vision) | Design, later arc |
| Clan agents moving between outpost and home | LF-010 step 2, LF-120 | Arc B |

---

## 6. Open questions (for Shawn, via the Director)

1. **Which version is authority** where the Outline and brain_dump disagree (conflicts 1–4)?
2. **Story timeline:** does the sim start before Act 1, with Gobby still walking? (Recommended.)
3. **Named characters as live agents:** may Bog, Beetle, the knight and Clara be on the board with
   sim fates that can differ from the story's?
4. **Gruk and Skrix:** river-clan or another tribe? **Grom:** human or goblin (conflict 5)?
5. **Ignarix:** does the Gobby world have dragons? The source is silent, and Ignarix spawns in the
   forest.
6. **Gobby's innate affinity:** unsourced. Shawn's to give.
7. **The darkness limit:** the source opens on a sexual assault, and the needs addendum lists sex and
   violence among the destructive compulsions. How much of that may a sim agent carry?
8. **Names:** the hamlet and the clan are unnamed. Should we propose names, or wait for Shawn's?

---

## 7. Citations

- `Gobby_the_Goblin/Gobby The Goblin WIP  Worldbuilding.csv`: The Azure Woods; Alexandrite; The
  River Goblin Tribes; The Monster Races; The Great Divide; The Mounted Warrior's Arrival.
- `Gobby_the_Goblin/Gobby The Goblin WIP  Characters.csv`: Gobby; Bog; Beetle; The Unconscious
  Human Woman; Rhiener.
- `Gobby_the_Goblin/Gobby The Goblin WIP  Outline.csv`: Act 1, all six chapter rows.
- `Gobby_the_Goblin/The Beginning.docx`: the opening prose.
- `Gobby_the_Goblin/brain_dump.docx` (plain text): Vol 1–3; Themes.
- `design/lucentforge_vision.md`: the guiding principle.
- `docs/bible/lucentforge_cosmology_foundation_v1_derived_revision.md` §2.3, §8.5, §9.1, §14.1–14.4.
- `docs/bible/lucentforge_affinity_grace_foundation_v1_derived_revision.md` §7.4, §8.4, §14.3.
- `docs/bible/lucentforge_needs_wants_drives_addendum_v1.md` §W1, §W3, §W4.
- `docs/bible/lucentforge_rooms_panels_addendum_v1.md` §R2, §R3, §R4, §R6, §R7.
- `docs/bible/lucentforge_micro_simulation_v_1.md`: Goblin Threat System.
- `docs/bible/heartbeat_convergence_vision.md`: Interpretation + Drift Loop.
- `docs/bible/lucentforge_terminology_map_v_1.md` §7.5 (Panel(0,0) regions).
- `Mechanics/data/panels/panel_0_0.json`; `Mechanics/data/entities.json`;
  `Mechanics/data/art/{gobby,grom,azure_oak,river_stone}.json` `_lore`.
