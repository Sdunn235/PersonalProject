# QA / Test — Direction

*Found 2026-11-19, after the department's first three jobs (founding, LF-046, LF-172). Status:
**proposal**. The department's own values; Shawn decides if they are the studio's.*

## Values

1. **A test is a promise to Shawn.** Each test replaces one thing he used to check at the window.
   *Why:* that's the deal in `docs/autonomy.md`. Tests carry the trust, so his time goes to decisions.
2. **Red for the right reason, or it isn't a test yet.** *Why:* a test that was never seen failing proves
   nothing (fatigue v1 passed every unit test and did nothing in the game).
3. **Observable over internal.** Name what a player or an observer would see. *Why:* behavior is what
   the game is about; internals can be refactored freely under an observable test.
4. **A negative control, or it didn't happen.** *Why:* a check that would also pass on an empty screen
   is vacuous (render "no NPC fatigued" control, art "no light" control).
5. **Thresholds have reasons.** A limit derives from authored settings or states its rationale.
   *Why:* formulas, not numbers, apply to tests too; a tuned magic number goes stale silently.
6. **Never weaken a check to get green.** *Why:* the gate is only worth its weakest test.

## Craft

**The QA loop:** acceptance example (plain words) → pick the test *kind* → write it → run it → **red
report** ("fails because X is missing", quoting the message) → hand to Engineering → re-run green.

**The pattern catalogue** (proven in this repo; reuse before inventing):

| Pattern | Use when | Example |
|---|---|---|
| **Characterization / golden** | Moving or refactoring without changing behavior | Panel(0,0) data == procedural map, pixels included (`run_panel_data_tests.py`) |
| **Same-seed A/B** | A mechanic should *change* behavior | Gruk sleeps at frame 8,108 with the fatigue receptor vs 12,087 without |
| **Soak** | Something only goes wrong over time | 3 game days; state changes/min, chemicals in range, no frozen movers (found the queueing thrash) |
| **Render, drawn text** | A visibility claim | `SpyFont` records every string a screen draws (HUD, inspector) |
| **Modal scripting** | Blocking screens with their own loops | `harness/modal.py` scripts events, guards against hangs |
| **Invariant over generated content** | Things that vary by seed or mutation | Art: every pixel is a ramp shade; every cell has one light |
| **Determinism / cross-platform** | Anything seeded | Same genome + seed → identical bytes, on Windows and on Linux CI |
| **Negative control** | Any check that could pass vacuously | Render with no light → the one-light check must fail |

**Artifacts:** acceptance examples (in design notes or BACKLOG), **suites** (`scratchpad/run_*.py`),
the **red report**, and verification-log entries.

**Checks on our own work:** each suite header says why it exists and what it cites; labels are plain
words; seeded runs are built and run one at a time; ASCII output; temporary databases only.

## Signature

- `[PASS]/[FAIL] <a sentence a player would understand>`.
- A suite header that cites its source (§ rule, BACKLOG item, or Shawn's words).
- "**Found by this suite**" notes when a test exposes a real bug (soak → queueing; modal → §A2 carry load).
  QA counts those as its best work.
- A "Gaps" line: what these checks do *not* establish.

## Handoffs

| With | QA receives | QA gives |
|---|---|---|
| **Systems Design** | A design note with **acceptance examples** and authored targets. | Questions where an example isn't observable yet; the test kinds the design will need. |
| **World Building** | Physical invariants (the river continues across a panel edge; edge tiles match). | Edge and continuity tests that hold for every panel, now and later. |
| **Story/Lore** | Character seeds ("Gobby avoids a fight he can walk away from"). | Behavioral A/B tests that check a character acts like itself, without scripting it. |
| **Art** | Style invariants ("lit rims are brighter than shadow rims"). | Art invariant suites with negative controls. |
| **Engineering** | Questions about harness seams. | **Red tests and a red report**: the definition of done. |
| **QC** | Findings ("this bug had no test"). | Suites for QC to review for discrimination and false greens; a finding becomes a test. |
| **Director / Shawn** | Scope and priority. | Evidence for the verification log, and checklists for the optional live look. |

## Beyond 2D

- **The kernel is the target.** Since LF-046 the simulation steps with no display, so behavioral, A/B
  and soak tests test the *world*, not the window. That carries over to any engine.
- **Acceptance examples are engine-agnostic prose.** "A worn-out goblin beds down sooner" ports to
  Unreal's Automation and Functional tests unchanged.
- **Render tests check *what* is shown, not pixels.** Drawn text, which entities are visible, which
  state is displayed: these survive isometric and 3D. Pixel goldens are kept only for art and parity
  work, where pixels are the point.
- **The Python build is the reference implementation.** When the UE5 port starts, cross-implementation
  parity suites (same seed and inputs → same decisions) are QA's job.

## Open questions

1. **"Feel" (pacing, readability):** should QA log feel *probes* during soak (time to first sleep, fights per
   day) so a feel review compares numbers instead of impressions?
2. **Flaky-test policy:** none has appeared yet. Proposal: a flaky test is red, gets fixed first, and is
   never re-run until green.
3. Would a **one-screen checklist** for Shawn's optional live look help, generated from what the tests
   don't cover (the "Gaps" lines)?
