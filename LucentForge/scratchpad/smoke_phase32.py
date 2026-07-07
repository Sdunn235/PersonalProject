"""Phase 3.2 smoke test — world coordinate system + m0006 migration.

Run from LucentForge directory: py smoke_phase32.py
"""
import sys
import os
sys.path.insert(0, os.path.abspath("."))

passed = 0
failed = 0

def check(label, condition, detail=""):
    global passed, failed
    if condition:
        print(f"  PASS  {label}")
        passed += 1
    else:
        print(f"  FAIL  {label}" + (f" — {detail}" if detail else ""))
        failed += 1


# ── Group 1: WorldPos dataclass ──────────────────────────────────────────────
print("\n[1] WorldPos")
from Mechanics.world.world_coord import WorldPos, PanelEdge, PanelConfig, PanelLoader

pos = WorldPos(0, 0, 5, 10)
check("panel_x", pos.panel_x == 0)
check("panel_y", pos.panel_y == 0)
check("col",     pos.col == 5)
check("row",     pos.row == 10)
check("frozen — cannot mutate", True)  # raises FrozenInstanceError if tried; just confirm type
try:
    pos.col = 99  # type: ignore
    check("frozen actually frozen", False, "no FrozenInstanceError raised")
except Exception:
    check("frozen actually frozen", True)

# ── Group 2: PanelEdge enum ──────────────────────────────────────────────────
print("\n[2] PanelEdge")
check("NORTH value", PanelEdge.NORTH.value == "NORTH")
check("SOUTH value", PanelEdge.SOUTH.value == "SOUTH")
check("EAST  value", PanelEdge.EAST.value  == "EAST")
check("WEST  value", PanelEdge.WEST.value  == "WEST")
check("4 members",   len(list(PanelEdge)) == 4)

# ── Group 3: PanelLoader.from_json ──────────────────────────────────────────
print("\n[3] PanelLoader.from_json")
panels_path = os.path.join("Mechanics", "data", "panels.json")
check("panels.json exists", os.path.isfile(panels_path), panels_path)
loader = PanelLoader.from_json(panels_path)
check("panel (0,0) registered", (0, 0) in loader._panels)
cfg = loader._panels.get((0, 0))
check("panel id",      cfg is not None and cfg.id == "panel_0_0")
check("panel name",    cfg is not None and cfg.name == "Starting Area")
check("panel_x == 0", cfg is not None and cfg.panel_x == 0)
check("panel_y == 0", cfg is not None and cfg.panel_y == 0)
check("north == None", cfg is not None and cfg.north is None)
check("south == None", cfg is not None and cfg.south is None)
check("east  == None", cfg is not None and cfg.east is None)
check("west  == None", cfg is not None and cfg.west is None)

# ── Group 4: can_transition / get_adjacent_panel ─────────────────────────────
print("\n[4] PanelLoader transitions")
for edge in PanelEdge:
    check(f"can_transition(0,0,{edge.value}) == False", not loader.can_transition(0, 0, edge))
    check(f"get_adjacent(0,0,{edge.value}) is None",    loader.get_adjacent_panel(0, 0, edge) is None)
check("unknown panel can_transition False",    not loader.can_transition(1, 0, PanelEdge.WEST))
check("unknown panel get_adjacent_panel None", loader.get_adjacent_panel(1, 0, PanelEdge.WEST) is None)

# ── Group 5: m0006 migration — DB column checks ───────────────────────────────
print("\n[5] m0006 DB columns")
import sqlite3
db_path = os.path.join("Mechanics", "data", "lucentforge.db")
if not os.path.isfile(db_path):
    # Trigger migration by creating GameContext
    from Mechanics.data.context import GameContext
    ctx_tmp = GameContext()
    del ctx_tmp

if os.path.isfile(db_path):
    conn = sqlite3.connect(db_path)

    cur = conn.execute("PRAGMA table_info(entity_state)")
    cols = {row[1] for row in cur.fetchall()}
    check("entity_state.panel_x", "panel_x" in cols, f"cols={cols}")
    check("entity_state.panel_y", "panel_y" in cols)

    cur = conn.execute("PRAGMA table_info(source_state)")
    cols = {row[1] for row in cur.fetchall()}
    check("source_state.panel_x", "panel_x" in cols)
    check("source_state.panel_y", "panel_y" in cols)

    # chest_content stores JSON blobs — verify panel_x is in the data payload
    cur = conn.execute("SELECT data FROM chest_content LIMIT 1")
    row = cur.fetchone()
    if row:
        import json
        cdata = json.loads(row[0])
        check("chest_content data has panel_x", "panel_x" in cdata)
        check("chest_content data has panel_y", "panel_y" in cdata)
        check("chest panel_x == 0", cdata["panel_x"] == 0)
    else:
        check("chest_content has rows", False, "no rows")

    conn.close()
else:
    check("DB exists", False, "lucentforge.db not found even after GameContext init")

# ── Group 6: GameContext wiring ───────────────────────────────────────────────
print("\n[6] GameContext")
from Mechanics.data.context import GameContext
ctx = GameContext()
check("ctx.current_panel == (0,0)", ctx.current_panel == (0, 0), str(ctx.current_panel))
check("ctx.panel_loader is PanelLoader", isinstance(ctx.panel_loader, PanelLoader))
check("ctx.panel_loader can_transition False", not ctx.panel_loader.can_transition(0, 0, PanelEdge.NORTH))
check("ctx.rooms still works", ctx.rooms is not None)
check("ctx.entities still works", ctx.entities is not None)

# ── Summary ───────────────────────────────────────────────────────────────────
print(f"\n{'='*48}")
print(f"  {passed} PASS  |  {failed} FAIL")
if failed:
    sys.exit(1)
print("  Phase 3.2 smoke CLEAN")
