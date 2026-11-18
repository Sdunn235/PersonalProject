# LucentForge — Changelog

What has shipped, arc by arc, newest first. Commit IDs (`C####`) match `git log` in the
`Personal Project` repo. Each arc lists *why* it happened, then what was **Added / Changed / Fixed**
and which **Docs** became authority.

- **What's next** lives in [BACKLOG.md](BACKLOG.md).
- **Live working state** lives in [context/session_state.md](context/session_state.md).
- **Design authority** is the bible: [docs/bible/README.md](docs/bible/README.md).

Format loosely follows [Keep a Changelog](https://keepachangelog.com/). The prototype has no version
numbers — arcs are the release unit.

---

## [Unreleased]
Nothing yet.

---

## C0069–C0073 — Return from break + the Rest/Fatigue want (2026-11-17 → 11-18)
After three months away: a full project review, then the first new behavior since July.

### Review + sync (C0069, C0071)
**Added:** this CHANGELOG, `BACKLOG.md`, `design/README.md`, `assets/maps/tools/` (biome-map rework
script, kept out of `scratchpad/` because the test runner would execute it and it rewrites the map).
**Changed:** session_state current-state header; known-issues list moved to BACKLOG (checked against the
code); CLAUDE.md directory table; next-session prompt from the Caelum template. Now tracked: the biome
map files and `Gobby_the_Goblin/`.

### Rest/Fatigue want v1.1 (C0070 built 2026-08-09 → C0072 fix → C0073 merge)
The first feature to go through the full Studio pipeline (Systems Design → QC → **Engineering** → QC),
then fixed after its first live test failed. Exertion builds a slow `fatigue` chemical; fatigue makes
the sleep need *feel* lower, so worn-out NPCs go to bed sooner. No new need, bed, or migration.

**Added**
- `fatigue` chemical and an `ExertionEmitter` (`biochem/emitter.py`). MOVING, RAIDING, RELOCATING and
  PATROLLING exert; sleeping at a bed pulls fatigue toward 0; IDLE and eating/drinking are neutral.
- `endurance(attrs)` polymorphic derivation (`entities/derivation.py`) — Constitution leads, Physique
  secondary, recomputed live. Per-frame gain = `FATIGUE_BASE_GAIN / endurance`.
- **Perceived-need receptor** (`biochem/receptor.py`): `Need.perceived_pull = fatigue × FATIGUE_SLEEP_PULL`
  on sleep. `Need.zone`, `urgency_score` and priority sorting read `perceived_value`, so every decision
  path (idle pick, goblin behavior, patrol/relocate/raid exits) agrees. Max pull 30 → no bed loop.
- Legibility: HUD Fatigue row, `V` inspector (chemicals now 4 decimals; needs show `actual>felt`),
  `O` panel suffix `f0.xx`, `npcs.csv` column.
- `scratchpad/run_fatigue_tests.py` — 38 checks, including an integrated real-roster accrual test and a
  same-seed headless kernel day with vs without the receptor (goblins sleep ~⅕ day sooner).
- **Studio: Engineering department** (`studio/engineering/` + workspace agent `lucentforge-engineering`)
  — implements a *locked* design, kicks back rather than redesigning, does not commit.

**Fixed (C0072, after the 2026-11-17 live test failed)**
- Fatigue never rose: the controller runs per frame, and natural decay (0.00005/frame) beat the gain
  (0.0003 ÷ endurance) for every NPC. `FATIGUE_BASE_GAIN` 0.0003 → 0.0015, derived from "a human
  (endurance 10) reaches 0.5 in about half a day".
- Even when tuned, fatigue could not change behavior: decisions read need zones, never chemicals. The
  receptor above is the fix.

**Changed:** HP/SP regen pauses while sleep *feels* urgent (exhaustion halts recovery).
**Docs:** bible needs/wants §W6 code-reality note + §W6.1; biochem §B7 code-gap note (strain has the same
inert-boost problem → BACKLOG LF-042); READMEs biochem, ai, new `Mechanics/needs/README.md`.
**Gate:** `run_all_tests.py` 23/23 green; live gate passed (all six checks; run-log: Gruk peak fatigue
0.71, Skrix 0.62, both falling while asleep).

---

## C0068 — LucentForge Studio: department agents (2026-08-04)
A way for a solo developer to dispatch AI "department" specialists. Caelum is the Director:
decompose → dispatch → collect → reconcile against the bible → write back to each department's log.

**Added**
- `studio/` with four departments, each with its own on-disk framework (`charter.md`, `memory_log.md`,
  `references/`): **Systems Design** and **Code Review/QC** (proven end-to-end), plus **World Building**
  and **Story/Lore** (scaffolded, not yet run).
- Workspace agent definitions `.claude/agents/lucentforge-*.md`. They are thin routers; the on-disk
  framework does the work.
- QC as a **stage × domain matrix**, not one checklist.
- Proof-of-concept run: the Rest/Fatigue want design (accepted, PASS WITH NOTES).

**Docs:** `studio/README.md` pins the three-layer memory boundary (Caelum / Claude / department logs).

## C0067 — Arc B foundation: World & Genesis bible expansion (2026-08-02)
Arc B "The World Opens" started with its world *foundation*, not a map loader. This integrated GPT
Caelum's worldbuilding handoff. Documentation only; runtime untouched.

**Docs (new authority)**
- `lucentforge_world_foundation_v1.md` (§W) — the home world and its central spine.
- `lucentforge_planetary_tectonics_addendum_v1.md` (§T) — 10-plate registry with stable `PLATE-*` IDs
  and a boundary-classification *requirement* (not yet filled).
- `lucentforge_world_map_scale_addendum_v1.md` (§S) — the planet map **extends** the Panel doctrine
  (§R1); `PlanetCoord` wraps `WorldPos`.
- `lucentforge_climate_hydrology_addendum_v1.md` (§C) — derivation rules, nothing canonized.
- `docs/genesis/` — a separate-but-tandem world-generator project (pipeline G00–G18, data contracts,
  validation). Design only.
- `docs/maps/` — layer standard and projection docs.

**Changed**
- `assets/maps/world_map/` reorganized into `source/ exported_layers/ registries/ working/ generated/`.
- `plate_registry.csv` repaired (malformed Greaterlands quote).

## C0059–C0066 — Arc A "The Glass Box": observability + time control (2026-07-25 → 07-26)
First arc of the post-refactor roadmap (A Glass Box → B World Opens → C Living Violence). Debug
tooling built on the new runtime seams; the simulation itself was untouched.

**Added**
- `P` freeze the sim / `.` step one tick (C0059).
- `V` full-screen deep mind inspector — every chemical, drives + the winning drive, memory, affinity,
  traits (C0060, `renderer/inspector.py`).
- `,` step one tick **back** — true time reversal through an in-memory snapshot ring that uses the
  exact save/restore path (C0062, `runtime/rewind.py`).
- `L` emergence event feed — state changes, zone crossings, needs, combat (C0063,
  `observation/event_log.py`).

**Fixed**
- **NPCs no longer snap to IDLE on load.** `apply_save` restores controller state, target and path
  (C0061).
- Back-tick now moves sprites together with the bars; rewind capture is silent (C0065).

**Docs:** runtime README + session_state closeout (C0064, C0066).

## C0051–C0058 — Stage 4.6R: runtime ownership refactor (2026-07-25)
`main.py`'s 493-line god-function became a 46-line composition root. Eight behavior-preserving
commits; the golden-master gate stayed green after each one.

**Changed**
- `Mechanics/runtime/kernel.py` — **SimulationKernel**: headless, imports no pygame;
  `step(dt, now) -> SimFrame` (C0053).
- `runtime/session.py` — **WorldSession**, the pygame-free object graph (C0052). Zone observers now
  wire through the session lifecycle (C0054).
- `runtime/shell.py` — **PresentationShell** + `RuntimeMode` state machine (C0055).
- `runtime/commands.py` — input as remappable `Command`s (C0057).

**Added:** `scratchpad/run_runtime_tests.py` characterization net and the `run_all_tests.py` master
runner (C0051). The sim is now testable without a window.

**Fixed:** dead "New Game" row in pause → Load; the Load menu shows only saved games (C0056).

**Docs:** `lucentforge_runtime_architecture_addendum_v1.md` (§RT1–§RT8) — the **Ripple Kernel**
(player = one more agent; the world sims without a shell) and the SimCore/Unreal port seam (C0058).

## C0040–C0050 — Affinity Behavioral Loop: affinity drives behavior (2026-07-18 → 07-24)
GPT Caelum's "Priority 3": make affinity *do* something, Creatures-style. Region affinity → emitter →
chemicals → drives → behavior, legible on every surface, persisted.

**Added**
- `AffinityComfortEmitter` → `comfort` / `stress` chemicals. Stress joins the drive-urgency multiplier
  (C0040, test C0041).
- Learned per-region comfort memory (EMA) and a new **RELOCATING** state — stressed NPCs drift back to
  ground that felt good (C0042).
- `affinity_strain` — sustained hostile exposure raises perceived need urgency (C0046).
- HUD biochem detail section on the Tab-cycled NPC panel (C0047).
- Region-comfort memory survives save/load via a nested memory blob, with no migration (C0049).

**Changed:** affinity added to 4 town regions so comfort is visible in town (C0045).

**Fixed:** comfort always reading +0.0 — stale SQLite entity blobs seeded before the Grace migration.
Delete the DB to reseed; any `entities.json` edit needs a DB delete (C0044).

**Docs:** `lucentforge_biochem_affinity_addendum_v1.md` (§B1–§B8, deferred seams in §B8),
`lucentforge_needs_wants_drives_addendum_v1.md` (§9 tiers → biochem, open wants in §W7) (C0048, C0050).

## C0037–C0039 — Grace Migration: affinity re-foundation (2026-07-18)
GPT Caelum reworked the cosmology into **the Grace**, superseding the six-element model from C0034.

**Changed**
- 8 affinities: Primal `FIRE/AIR/WATER/EARTH` + Derived `PLASMA / COLLOIDAL_DISPERSION / NON_NEWTONIAN /
  BINGHAM_PLACIDITY`.
- Light/Dark are now *ontological states*, not affinities.
- `opposite()` retired for a lattice API (`is_primal`, `parents_of`, `derived_between`, …).
- The player is neutral (`innate=None`) + `LIGHT_TOUCHED` trait (C0038).

**Added:** `scratchpad/run_grace_tests.py` (20 checks) (C0039).

**Docs:** cosmology + affinity Grace foundations, the source drawing, revised §M5–§M6 (C0037).

## C0029–C0036 — Stage 4: attributes, Bits/Bytes magic, affinity (2026-07-08 → 07-09)
A bounded foundation from the stats/magic bible. Progression, status effects and world-death were
deliberately deferred (§M9).

**Added**
- Real 7-attribute layer (Physique, Reflexes, Constitution, Intellect, Intuition, Linguistic, Luck);
  combat stats are *derived* (C0031).
- Intuition trap perception — passive danger-sense with a red `!` marker (C0032).
- Bits/Bytes pool split; polymorphic `derivation.py`; `1 Byte = 8 Bits`; m0007; 4-bar HUD (C0033).
- Affinity model, six-element (superseded by the Grace) (C0034).
- Bit/Byte casting economy — spell typing, pools, formula costs (C0035).
- Bits→Bytes conversion (`C` key) + regen asymmetry (C0036).

**Fixed:** `PlayerController` has no brain → `ZoneAIResponder` AttributeError (C0029).

**Docs:** `lucentforge_stats_magic_addendum_v1.md` (§M1–§M9.1) + terminology map §8 (C0030).

## C0021–C0028 — Stage 3: rooms as zones, multi-panel world (2026-07-06 → 07-07)
The "Zelda pre-N64" model: the current 18×18 map is Panel(0,0) and the world grows panel by panel at
the same scale. Architecture only, no new panel content.

**Added**
- `world/rooms.py` + `rooms.json` — RoomType, RoomDefinition, RoomRegistry (C0022).
- `world/world_coord.py` — `WorldPos`, `PanelEdge`, `PanelLoader`, `panels.json`, m0006 panel coords
  (C0023).
- `ZoneTracker` observer + `ZoneCrossingEvent` (C0024).
- `O`-panel ZONE section + HUD room-name flash (C0025).
- `ZoneAIResponder` — goblins anger in civilized zones, humans fear goblin ground (C0026).
- Panel-edge detection + `load_panel` (C0027).
- Stage 3 smoke suite (C0028).

**Docs:** `lucentforge_rooms_panels_addendum_v1.md` (§R1–§R8) + terminology map §7 (C0021).

## C0010–C0020 — Stage 2: items & equipment (2026-07-04 → 07-06)
First import from the TheForge C# capstone. TheForge is the structural blueprint; the bible is the
naming authority.

**Added**
- TheForge vendored as a read-only reference (C0011).
- `Mechanics/items/` domain (enums, item hierarchy) (C0013).
- m0003 relational schema + `ItemRepository` (C0014).
- `InventoryService` / `EquipmentService` + bag persistence (C0015).
- `I` inventory/equipment modal (C0017).
- §12.2 `OutcomeResolver` — bounded-variance checks (C0018).
- Chests, locks, traps and keys on the map with `E` interaction (C0019).

**Changed / Fixed:** combat now uses the services; fixed the NPC-bag bug, armor DEF never applying,
and the weapon dict (C0016). Equipment no longer duplicates on save/load (C0017).

**Docs:** terminology map + items addendum (§A1–§A8) (C0012). Planning (C0010). Closeout + smoke suite
(C0020).

## C0003–C0009 — Stage 1: SQLite persistence + game menus (2026-06-29 → 07-04)
**Added**
- SQLite backbone behind the existing DAO API. JSON stays canonical; the DB is a reseedable runtime
  artifact (C0003).
- World-state save/load, `S` save, autosave, save-on-quit (C0005).
- 4-slot save/load menus (C0006).
- Pause menu (C0007).
- Load + New Game from pause (C0008).

**Docs:** session_state updates (C0004, C0009).

## C0002 + Heartbeat 1–6 — the living town (2026-04-05 → 06-27)
The "heartbeat" arc made the map a small simulated settlement.

**Added**
- **H1** world orchestration — clock, day/night, resources, goblin threat, town state.
- **H2** procedural region map — river barrier, bridges, zones.
- **H3** NPC decision loop — EMA source memory, outcome scoring, 4-weight source selection, trait
  drift.
- **H4** goblin behavior — behavior strategies, hunger-driven threat, patrol/raid states, proximity
  fear.
- **H5** resource economy — finite stocks, regen, raids drain food, stock bars.
- **H6** observation layer — `O` world panel, per-run CSV run-log, de-duplicated depletion log (C0002).

**Also:** 1024×768 window expansion (Apr 5); bible convergence analysis (Apr 6). Restructure: Creatures
repo extracted, phase docs added (C0001, 2026-05-05).

## Prehistory — Sessions 1–12 (2026-03-04 → 03-21)
Before commit numbering. Initial workspace commit (2026-03-04), then a burst of sessions on 2026-03-17:
- AI NeedSimulator merged in; deconstruct-and-rebuild; entity separation fixes.
- Combat expansion — nested ACTIONS menu, SP/MP, backpack, Tab-cycled HUD.
- Bar colors, player source interaction, world-map stat bars.
- **Data-driven JSON + DAO + entity factory** (Session 10).
- **Spell system** (MP + MAG), Grom and Elara, basic equipment (Session 11).
- **SOLID refactor** (Session 12, 03-21) — GameContext DI, Fighter composition, combat decomposition,
  NPC state pattern, data-driven needs.

---

## Reference: how the project grew
- **Test safety net:** 3-test smoke (Jun) → per-stage smoke suites → 92-check runtime characterization
  + `run_all_tests.py` (**23 suites, all green** as of 2026-11-18).
- **Controls today:** arrows move · `TAB` cycle HUD · `I` inventory · `E` chest · `C` convert
  Bits→Bytes · `O` world panel · `S` save · `ESC` pause · `P` freeze · `.` step · `,` rewind ·
  `V` inspector · `L` event feed.
- **Run:** `py main.py` (pygame-ce, Python 3.14). Headless gate: `py scratchpad/run_all_tests.py`.
