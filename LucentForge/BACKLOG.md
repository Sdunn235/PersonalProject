# LucentForge — Backlog

Every idea we've had, in one place, with a link back to where it came from. Built 2026-11-17 from
`session_state.md`, the bible's deferred lists, Caelum session logs, Claude memory, Studio logs, and
`docs/Ideas For How Character stats work.txt`.

- **What already shipped:** [CHANGELOG.md](CHANGELOG.md)
- **Design authority:** the bible ([docs/bible/README.md](docs/bible/README.md)). A backlog line is a
  pointer, not a spec — the linked § is the requirement.

**Keys** — Size: `S` an evening · `M` a session or two · `L` several sessions · `Arc` a planned
multi-phase arc. Status: `ready` (can start now) · `blocked` (needs something first) · `design`
(needs a design pass or Shawn's decision first) · `idea` (not yet scoped).

**Keeping it current** — when an item ships, delete it here and add it to the CHANGELOG under its
commit. New ideas get the next free `LF-###`; IDs are never reused.

---

## Where you left off (2026-11-17)

1. **Last real work (2026-08-09):** the Rest/Fatigue want was built and passed QC, then sat
   uncommitted. Its live test on 2026-11-17 **failed** (fatigue never rises — a tuning bug), so it's
   parked on branch `wip/fatigue-want` (LF-001). `master` is **23/23 green**.
2. **Arc B "The World Opens" is next on the roadmap.** Its world foundation (bible §W/§T/§S/§C) is
   written; nothing runnable has been built yet.
3. **The Studio** (department agents) works for Systems Design, QC and Engineering. World Building and
   Story/Lore have never been run.

**Recommended first pick when you have an evening:** LF-001 (fix fatigue — the cause and fix are
already written down, so it's a short, satisfying win), then LF-002 (live spot-checks, ~30 min), then LF-010 (map loader). If you'd rather do design than code, try LF-004 (a first World Building or
Story/Lore task).

---

## Now — quick wins and loose ends

| ID | Item | Size | Status | Source |
|---|---|---|---|---|
| LF-001 | **Fix the fatigue want, then live-gate + merge** — code is on branch `wip/fatigue-want`. Details below the table. | S–M | ready | branch `wip/fatigue-want`, `studio/engineering/memory_log.md` |
| LF-002 | **Unconfirmed July live checks**: goblin relocates home (`RELO`) when stressed; region comfort survives save → reload; Grace entities build (player neutral + LIGHT_TOUCHED). Never eyeballed in a window. | S | ready | session_state (Affinity / Grace sections) |
| LF-003 | **Decide the unmerged `agent/alignment-genesis-bootstrap` branch** (one 2026-07-26 commit: `docs/architecture/README.md`, which proposes a bible → decisions → architecture → roadmap → research authority order). Merge, adapt, or delete. | S | design | `origin/agent/alignment-genesis-bootstrap` |
| LF-004 | **First real job for World Building and Story/Lore** — their first task is their proof (e.g., the §T3 workshop prep for World Building; Gobby's Act 1 people for Story/Lore). | M | ready | `studio/README.md` |
| LF-005 | Re-save `Gobby_the_Goblin/brain_dump.docx` in Word — the file isn't a valid docx, so it's unreadable. | S | ready | memory `project_gobby_world` |

**LF-001 — why the 2026-11-17 live gate failed.** Each tick, fatigue gains `FATIGUE_BASE_GAIN ÷
endurance` (0.0003 ÷ 6–23) while natural decay removes `0.0002 × FATIGUE_DECAY_MULT` = 0.00005 —
*including while exerting*. Every NPC has endurance ≥ 6, so gain ≤ decay and fatigue stays 0 (Gruk and
Elara exactly cancel; Ignarix gains a quarter of its decay). The 17 tests passed because they test
emitter and decay separately with low test attributes.
- **Fix options:** (a) tuning — raise `FATIGUE_BASE_GAIN` about 10× (≈0.003), so even endurance 23 nets
  positive; re-check the sleep invariant (`FATIGUE_SLEEP_BOOST` < 0.001) still holds. (b) structural —
  skip natural decay while in an exerting state (a design change → Systems Design + QC pass).
- **Add the missing test:** every real NPC from `entities.json`, ticked through the full
  emitter + `Chemicals.tick` path in an exerting state for thousands of ticks, must reach a
  visible fatigue (e.g. > 0.1).
- **Legibility (live check 3):** a working fatigue still moves about 0.0005 per tick, invisible at the
  inspector's 2 decimals. Show 4 decimals or a per-tick delta for chemicals in the `V` inspector.
- Then: re-run the live gate → merge the branch into master → move to CHANGELOG.

---

## Roadmap arcs (agreed 2026-07-25: A → B → C)

| ID | Item | Size | Status | Source |
|---|---|---|---|---|
| LF-010 | **Arc B — data-driven map loader:** existing zones become real panels with transitions (`PanelLoader.can_transition`, `panels.json`). | Arc | ready | session_state Arc A "Next"; §R1–§R8 |
| LF-011 | **Arc B — dialogue / choice system** (greenfield). TheMaze Java dialog in `ReferenceFilesAndCode/` is a pattern source. | Arc | design | session_state Arc A "Next" |
| LF-012 | **Arc B — first Forge story-arc panels** (TheForge dungeon: Inn → Erasmus, 7 rooms, as one region of the Gobby world). | L | blocked by LF-010 | memory `project_gobby_world` |
| LF-013 | **Arc C "Living Violence" — real-time ATB combat:** cooldowns gated by SP + Bytes, mouse point-and-click + hotbar, reusing the damage/ability/cost resolvers. | Arc | blocked by Arc B | Caelum `lucentforge_active.md` (Arc A entry) |
| LF-014 | **Arc C — autonomous NPC-vs-NPC combat in the kernel** (no shell needed). | L | blocked by LF-013 | same |

---

## Simulation · biochem · wants

| ID | Item | Size | Status | Source |
|---|---|---|---|---|
| LF-030 | **Fatigue Arc 2 — exertion drains SP** (the physical, self-destructive layer; interacts with SP regen and combat costs). | M | blocked by LF-001 | fatigue design note, Director Q3 |
| LF-031 | **Social Belonging want** (Tier 2) — belonging-comfort near familiar entities, loneliness when isolated. Gobby is the test case. | Arc | design | §W7 needs/wants/drives addendum |
| LF-032 | **Knowledge / curiosity want** (Tier 3) — novelty exposure builds curiosity; weight from the `curiosity` trait. | M | design | §W7 |
| LF-033 | **Power want** (Tier 3) — control or defeat others; weight from `aggression`; stress spike under bad odds. | M | design | §W7 |
| LF-034 | **Addiction / self-destructive compulsion** — euphoria source that drains HP/SP; susceptibility from fearfulness + low resilience. | M | idea | §W7 |
| LF-035 | **Gobby's resolve / hope / moral-weight chemical** — what sets him apart from the swarm; he remembers social encounters. | M | design | memory `project_lucentforge_vision` |
| LF-036 | **Chemical reactions** (`r1 + r2 → p1 + p2`) — the next Creatures layer. | L | design | §B8, §B1 |
| LF-037 | **Heritable genetics / Hob "innate spark"** — affinity and Talent from DNA at birth. | Arc | design | §B8, §M5 |
| LF-038 | **Legacy-injector retrofit** — re-express `proximity.py` fear and `zone_ai.py` nudges as emitters; parity-gated, own phase. | M | ready | §B8, §B2 |
| LF-039 | **Goblin scout → swarm escalation** — lone goblins scout; success draws more; swarms are the threat. | L | design | memory `project_goblin_lore` |
| LF-040 | **Talent read by the Brain** — gifted-ness influences behavior. | M | idea | §M9 (§M3 seam) |

---

## Stats · magic · combat depth

| ID | Item | Size | Status | Source |
|---|---|---|---|---|
| LF-050 | **Affinity combat** — like-affinity amplification and lattice-derived tension in `damage_resolver.py`, not a flat weakness chart. | L | design | §M6, §M9, §B8 |
| LF-051 | **Attribute progression & ascension** — learn-by-use `attribute_bit`/`attribute_byte`, doubling cost, cap 255, reincarnate to ascend. Fully designed. | Arc | ready | §M9.1, memory `project_lucentforge_bit_byte` |
| LF-052 | **Skills & ability progression** — skills from stat combos, unlocking abilities; "lackluster until mastered". | Arc | design | §M9, ideas doc |
| LF-053 | **Status effects** — `StatusFlags` stub exists; only poison ticks today. | M | ready | §M9 |
| LF-054 | **Elemental resistances, finish the job** — the multiplier works in `damage_resolver.py`, but only one entity has data; the full per-element model waits on §7 pattern-physics. | S→L | ready | session_state known issues #12, §M9 |
| LF-055 | **Buff / shield spells** — none exist yet. | M | ready | session_state known issues #10 |
| LF-056 | **Spell learning during play** — no way to learn new spells. | M | design | session_state known issues #11 |
| LF-057 | **Focus channeling + external focus storage** (staff/rod/tome banks Bytes; battlemage weapon magic). | L | design | §M9, §M4, §M7 |
| LF-058 | **Overburn / collapse** — hook exists but is disabled. | M | design | §M9, §M4 |
| LF-059 | **§7 emergent pattern-physics** — hybrid combinations, elements define behavior. | Arc | idea | §M9, §M5 |
| LF-060 | **Derived-affinity emergence + birth-generation affinity rolls**. | L | design | §B8, Grace §6.3–§6.4, §7.5 |
| LF-061 | **Resonance beyond weapons** (being / region / item / ritual). | L | idea | §B8, §M7, Grace §11 |
| LF-062 | **Full Creation/Unmade ontology** — Veil, Source, Dark-as-absence as live mechanics. | Arc | idea | §M9, Grace §16.2 |
| LF-063 | **World death + respawn** (traps still clamp HP to 1) and **durability wear** (the field exists, no decay). | M | design | §M9, §A8, known issues #13–14 |
| LF-064 | **Stamina pool formula** (Physique × Constitution) and physical action costs by weapon and attack type. | M | design | §M9.1 |
| LF-065 | **Linguistic attribute mechanics** — currently inert. | M | idea | §M2 |
| LF-066 | **Light/Void legacy migration** — convert any leftover six-element data. | S | ready | §B8, Grace §17 |

---

## World · Genesis · geography

| ID | Item | Size | Status | Source |
|---|---|---|---|---|
| LF-080 | **§T3 boundary-classification workshop** — classify plate boundaries one segment at a time off the composite map (needs Shawn at the map). | M | ready | §T3, Caelum session 2026-08-02 |
| LF-081 | **§S6 planet-scale numbers** — circumference, km per pixel, tile size, Panels per macro pixel, polar behavior. Chosen together. | M | design | §S6 |
| LF-082 | **Genesis milestone 1 — plumbing core:** data contract, deterministic RNG, stage ordering, provenance, a no-op stage, validation, raster import/export. Not tectonics yet. | L | blocked by LF-081 | `docs/genesis/` |
| LF-083 | **Reconcile the biome sketch with the plate map** — `assets/maps/world_map.csv` (14-token biome map, rework script in `assets/maps/tools/`) vs `assets/maps/world_map/` (tectonic source). | M | design | memory `project_lucentforge_world_genesis` |
| LF-084 | **Gobby-world geography sketch** — Azure Woods, Alexandrite, Azure River Valley, Great Plains placed on the world map. | M | ready | memory `project_lucentforge_vision` |
| LF-085 | **Climate / hydrology canonization** (§C has rules, nothing canonized). | L | blocked by LF-081 | §C |

---

## Economy · settlement · NPC life
Legacy items from session_state's old known-issues list, each checked against the code on 2026-11-17.

| ID | Item | Size | Status | Source |
|---|---|---|---|---|
| LF-100 | **Storage / silo** — the SILO tile is visual only; no storage overflow or food retrieval. | M | ready | known issues #5 |
| LF-101 | **NPC cultivation** — NPCs work the farm to boost output. | M | design | known issues #6 |
| LF-102 | **Shops / buy-sell economy** — items come only from chests today. | L | design | known issues #15 |
| LF-103 | **Civilized-side FOOD source** — humans walk to the forest for food because it's closest. | S | design | known issues #2 |
| LF-104 | **Human idle wander / fidget** — humans stand still during cooldown (goblins already patrol). | S | ready | known issues #3 |
| LF-105 | **Threat-pacing tune** — check against current numbers before changing anything. | S | design | known issues #7 |
| LF-106 | **Agriculture gates civilization** — nomads → settlements; survival feels different in towns. | Arc | idea | ideas doc |
| LF-107 | **Faction system** — depth is an open decision. | Arc | design | `design/design_decisions_log.md` |

---

## Runtime · tooling · testing

| ID | Item | Size | Status | Source |
|---|---|---|---|---|
| LF-120 | **Headless background sim for off-screen panels** — "the world simulates without the player". | L | blocked by LF-010 | §RT8 |
| LF-121 | **Replay determinism** — record a `Command` + `dt` stream and replay it headless as a regression test. | M | ready | §RT8 |
| LF-122 | **`--ai-player` mode** — a state machine plays while you watch. | M | design | memory `project_lucentforge_vision` (Option 3) |
| LF-123 | **Periodic JSON state export** for long-run analysis. | S | ready | same (Option 4) |
| LF-124 | **Non-blocking modal modes** (pause/inventory/chest/save as true `RuntimeMode` states). | M | idea | §RT8 |
| LF-125 | **Key-remap settings UI** (bindings are already data). | S | idea | §RT8 |
| LF-126 | **ECS / component entity model**. | Arc | idea | §RT8 |
| LF-127 | **Camera scrolling + bigger grid** for larger maps (check against the Panel doctrine first). | L | design | known issues #8–9 |
| LF-128 | **Memory-scaling architecture** for many NPCs over long runs. | L | design | `design/design_decisions_log.md` |

---

## Long-term direction

| ID | Item | Size | Status | Source |
|---|---|---|---|---|
| LF-140 | **Isometric art (64×32) + Z-layers** (−1 underground, 0 surface, +1 elevated; `WorldPos` gains `z`). | Arc | idea | memory `project_lucentforge_vision` |
| LF-141 | **SimCore / Unreal Engine 5 port** through the kernel seam. | Arc | idea | §RT, `design/port_strategy.md` |

---

## Icebox — big ideas, not yet shaped
From `docs/Ideas For How Character stats work.txt`. Keep these in mind when designing; none is a task yet.

- **LF-160** Many ways to solve any problem (snuff the candle: water, wind, breath, hand).
- **LF-161** Event-driven world — some events happen once, some repeat, some need a specific build or a
  chain of other events (SAO / Shangri-La Frontier style).
- **LF-162** No character level — attributes, skills and abilities have scores, the character doesn't.
- **LF-163** Specialization trade-offs — pushing one area weakens another (a bodybuilder isn't a sprinter).
- **LF-164** Failure has consequences — fail badly enough and something bad happens.
- **LF-165** Weight, style, type and stats all feed every action's speed, power and cost — easy to
  learn, hard to master.

---

## Open decisions (Shawn)
These shape the items above. Also logged in Caelum `feedback/questions_for_shawn.md`.

- **D1** Is the planet map ever a **navigable zoom** level? Today §S says no — it only extends §R1's
  single Panel scale. If yes, §S needs revisiting before LF-010/LF-081.
- **D2** Merge the agent-branch authority order (`docs/decisions`, `docs/architecture`,
  `docs/roadmap`) → LF-003. If adopted, this BACKLOG could move to `docs/roadmap/`.
- **D3** Faction-system depth (LF-107) and memory-scaling approach (LF-128).
- **D4** Git-LFS for the large map PSDs.

## Housekeeping
- **H2** Session 7–12 memories still sit in the old `~/.claude/projects/C--Users-Shawn-Documents/`
  memory folder (pre-workspace). Their history is now captured in the CHANGELOG Prehistory section; the
  folder can be archived.
