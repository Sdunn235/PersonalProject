# LucentForge Studio

A "studio" of AI department specialists for building LucentForge. Shawn is a solo developer;
this lets one person dispatch, review, and integrate the way a small game studio would.

**This is a proof-of-concept.** Two departments exist today: **Systems Design** and **Code
Review / QC**. More get added only after the pattern proves worth the overhead (see *Scaling*).

---

## The core idea: departments are mini-Caelums, not cold contractors

A dispatched subagent has **no conversation memory** of past sessions. It is *not* generic,
though — each department loads its **own framework off disk** on every invocation, exactly the
way Caelum loads its identity/memory at session start:

```
studio/<dept>/
  charter.md      ← who this department is, its authority, its standards, its bible slices
  memory_log.md   ← append-only running history of what it has produced/reviewed
  references/     ← its own working docs (checklists, rules, pointers into the bible)
```

The department's agent definition (`.claude/agents/lucentforge-<dept>.md`) instructs it to read
these first. So the department walks in knowing its standards and its own history — because it
reads them, not because the harness remembers.

**Persistence is a write-discipline, not magic.** Reading the log on startup is automatic.
*Writing* to it at the end of a task is a deliberate step. If it's skipped, the department goes
stale the same way `active_context.md` froze in March 2026. The Director loop below bakes the
write-back in as a required step — do not treat it as optional.

**Information scoping is intentional.** A department loads only *its* context — its charter, its
bible slices, its own log — not the whole workspace. Teams work with real autonomy inside their
lane; they don't need to know everything. The Director holds the full picture. This keeps each
department focused and token-cheap.

---

## The Director loop (Caelum orchestrates)

Departments do **not** talk to each other peer-to-peer. There is always a Director — Caelum, the
main thread — running hub-and-spoke:

1. **Decompose** the epic into department-shaped tasks; note dependencies (parallel vs sequential).
2. **Brief + dispatch** each specialist via the Agent tool (`subagent_type: lucentforge-<dept>`),
   handing it the task + pointers. The agent self-loads its framework.
3. **Collect** each department's returned artifact.
4. **Reconcile** against the bible (naming authority) and across departments — catch terminology
   drift and coherence conflicts. This is the Director's job and it is not free.
5. **Write-back** — ensure each department appends its `memory_log.md` entry (the agent does it, or
   the Director does it on the agent's behalf). Never skip this.
6. **Integrate** into LucentForge (docs/code), then run the normal Caelum end-of-session protocol.

The Director has final say. Departments have real autonomy *inside* their lane and a genuine voice
(QC can block); the Director resolves conflicts and owns the integrated result.

---

## Memory boundary (three layers — no duplication)

Shawn's framework forbids duplication across memory systems. The studio adds a **third** layer;
each has a distinct scope:

| Layer | Location | Scope |
|---|---|---|
| **Caelum memory** | `Caelum/memory/` | Identity + cross-project current state (`active_context`) + durable lessons (`reflection_log`). |
| **Claude auto-memory** | `.claude/projects/.../memory/` | Caelum-the-Director's operational recall (preferences, corrections, pointers). |
| **Department logs** | `studio/<dept>/memory_log.md` | *Per-craft working history* scoped to one department's output. |

A department log records **its craft**: "designed the X mechanic — here's the shape, the formula,
the open question." It does **not** restate `active_context` (project state), it does **not** hold
lessons (those go to `reflection_log`), and it does **not** duplicate Director recall. When in
doubt, ask: *is this a record of what this department made?* If yes, it belongs here. If it's
project state or a durable lesson, it belongs in Caelum memory instead.

---

## Departments

| Department | Agent | Owns |
|---|---|---|
| Systems Design | `lucentforge-systems-design` | Mechanics design as attribute *formulas* (not numbers), grounded in the stats/magic/items/needs/biochem bible. |
| Code Review / QC | `lucentforge-qc` | Correctness + canon-consistency. Reviews vary by production stage × department (see its charter's matrix). Can block. |
| World Building | `lucentforge-world-building` | Physical/geographic canon — planetary foundation, tectonics/plates, map scale, climate/hydrology, biomes, and how geography connects to the Panel grid (§W/§T/§S/§C, extends §R1). |
| Story / Lore | `lucentforge-story-lore` | Narrative & meaning — characters, arcs, history, culture, in-character/on-world judgment. Grounded in the Gobby WIP source story (primary authority) + the Grace cosmology. |

Four departments are scaffolded; **Systems Design + QC are proven end-to-end** (fatigue-want run, 2026-08-04).
World Building and Story/Lore are built and ready but not yet run — their first task is their first proof.

## Lane boundaries (so departments don't collide)
- **Systems Design** = mechanics (numbers-as-formulas, needs/drives/combat).
- **World Building** = the *physics* of a place (geography, climate, plates).
- **Story / Lore** = the *meaning* of a place and its people (characters, arcs, culture).
- **QC** = correctness/canon across all of them, by the stage×domain matrix.
When a task spans lanes (e.g. "a new region"), the Director splits it: World Building gives the geography,
Story/Lore gives its people and history, Systems Design gives any mechanics — QC reviews each, Director reconciles.

## Scaling further (after each new department's first run holds)
- Only staff a department that has real work. **Animation/Graphics** stay unstaffed until there's an
  art pipeline. **Genesis Development** is docs-only today, so it would be a design-only department.
- If epics become routine, add `studio/EPICS.md` where the Director records each epic's decomposition
  and which departments ran.
