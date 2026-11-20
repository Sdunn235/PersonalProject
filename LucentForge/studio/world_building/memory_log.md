# World Building — Memory Log

Append-only history of world canon this department has extended or classified. Newest at the top.

**Entry format:**
```
## YYYY-MM-DD — <what was extended/classified>
- **Intent:** one line.
- **Added:** the structural canon added (plates, boundary segments, climate/biome rule).
- **Coherence:** the consistency check that held (or the conflict flagged).
- **Touches:** bible §§ / asset files.
- **QC verdict:** pass / pass-with-notes / block.
- **Status:** accepted / revised / superseded / needs-Shawn-at-map.
- **Open / Out-of-Scope left:** the honest gaps.
```

Keep entries short — this is a craft ledger, not project state (`active_context.md`) and not a lesson
(`reflection_log.md`).

---

## 2026-11-19 — First run: direction + "beyond Panel(0,0)" proposal
- **Intent:** Find the department's working groove (`direction.md`) and propose what lies past Panel(0,0)'s null edges (LF-010 step 2).
- **Added:** `direction.md` (values, craft, artifacts: World Note / Panel Proposal / Edge Contract / Frontier Sheet / Biome Sheet / Place Sheet; provenance tags [CANON]/[DERIVED]/[PROPOSED]/[OPEN]). `proposals/2026-11-19_beyond_panel_0_0.md`: recommends **one** neighbour, Panel(0,-1) as the upstream river reach (assuming N→S flow), with full tile/region/rocks sketch in the live legend; option B Panel(0,1) as the floodplain; frontier intents for E/W; Edge Contract EC1–EC6; biome sheets (upstream stone rougher, downstream smoother); place-sheet questions for Story/Lore.
- **Coherence:** Both sketches pass seam passability match against (0,0)'s real edge rows, river orthogonal connectivity, no sealed pockets, legend-only chars (throwaway script). Climate held constant across the ring (no climate change across one Panel edge); differences come only from local causes (position on the river, flooding, clearing).
- **Touches:** none yet (proposal only). If accepted: `panels.json`, a new `panels/panel_0_*.json`, `rooms.json`, terminology §7.5 (option B's new region tag), §R8 status.
- **QC verdict:** not yet reviewed.
- **Status:** needs-Shawn (river flow direction, first edge, Panel scale, seam rule).
- **Open / Out-of-Scope left:** river source/sink; Panel(0,0) has no planetary location, so its climate is inferred backward (§W3 tension); Panel span (§S6/LF-081); negative-coordinate panel ID scheme; names ("Azure River/Woods" live only in art `_lore` notes); need sources, affinity, new tile types.
