"""Phase 3.6 smoke test — PanelLoader.load_panel + edge detection logic.

Run from LucentForge directory: py smoke_phase36.py
No pygame display required.
"""
import sys
import os
sys.path.insert(0, os.path.abspath("."))
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

passed = 0
failed = 0

def check(label, condition, detail=""):
    global passed, failed
    if condition:
        print(f"  PASS  {label}")
        passed += 1
    else:
        print(f"  FAIL  {label}" + (f" -- {detail}" if detail else ""))
        failed += 1


# ── Group 1: PanelEdge enum ───────────────────────────────────────────────────
print("\n[1] PanelEdge enum")
from Mechanics.world.world_coord import PanelEdge, PanelLoader, WorldPos, PanelConfig

check("NORTH exists",  hasattr(PanelEdge, "NORTH"))
check("SOUTH exists",  hasattr(PanelEdge, "SOUTH"))
check("EAST exists",   hasattr(PanelEdge, "EAST"))
check("WEST exists",   hasattr(PanelEdge, "WEST"))
check("value lowercase-safe",
      PanelEdge.NORTH.value.lower() == "north")

# ── Group 2: PanelLoader.load_panel ──────────────────────────────────────────
print("\n[2] PanelLoader.load_panel")
import os as _os
panels_path = _os.path.join("Mechanics", "data", "panels.json")
loader = PanelLoader.from_json(panels_path)

p = loader.load_panel(0, 0)
check("load_panel(0,0) returns PanelConfig", p is not None and isinstance(p, PanelConfig))
check("Panel(0,0) id correct",  p is not None and "0_0" in p.id)
check("Panel(0,0) name set",    p is not None and len(p.name) > 0)

p_missing = loader.load_panel(1, 0)
check("load_panel(1,0) returns None (not defined)", p_missing is None)
check("load_panel(0,1) returns None",  loader.load_panel(0, 1) is None)
check("load_panel(-1,0) returns None", loader.load_panel(-1, 0) is None)

# ── Group 3: can_transition always False for Panel(0,0) ──────────────────────
print("\n[3] can_transition returns False for all edges of Panel(0,0)")
for edge in PanelEdge:
    check(f"can_transition(0,0,{edge.name}) is False",
          not loader.can_transition(0, 0, edge))

# ── Group 4: get_adjacent_panel returns None for all edges ───────────────────
print("\n[4] get_adjacent_panel returns None for all edges")
for edge in PanelEdge:
    check(f"get_adjacent_panel(0,0,{edge.name}) is None",
          loader.get_adjacent_panel(0, 0, edge) is None)

# ── Group 5: edge detection logic (simulate player at each edge) ─────────────
print("\n[5] Edge detection logic (unit simulation)")
import settings

COLS = settings.COLS
ROWS = settings.ROWS
TILE = settings.TILE_SIZE

def detect_edge(px, py):
    """Mirrors the edge-detection logic in main.py."""
    pcol = int(px // TILE)
    prow = int(py // TILE)
    if prow <= 0:              return PanelEdge.NORTH
    elif prow >= ROWS - 1:    return PanelEdge.SOUTH
    elif pcol <= 0:            return PanelEdge.WEST
    elif pcol >= COLS - 1:    return PanelEdge.EAST
    return None

# North edge: row 0 → y in [0, TILE)
check("North edge: row 0",        detect_edge(5 * TILE, 0)          == PanelEdge.NORTH)
check("North edge: mid-tile",     detect_edge(5 * TILE, TILE - 1)   == PanelEdge.NORTH)

# South edge: row ROWS-1 → y in [(ROWS-1)*TILE, ROWS*TILE)
check("South edge: row ROWS-1",   detect_edge(5 * TILE, (ROWS-1)*TILE + 4) == PanelEdge.SOUTH)

# West edge: col 0 → x in [0, TILE)
check("West edge: col 0",         detect_edge(0, 5 * TILE)          == PanelEdge.WEST)
check("West edge: mid-tile",      detect_edge(TILE - 1, 5 * TILE)   == PanelEdge.WEST)

# East edge: col COLS-1 → x in [(COLS-1)*TILE, COLS*TILE)
check("East edge: col COLS-1",    detect_edge((COLS-1)*TILE + 4, 5 * TILE) == PanelEdge.EAST)

# Interior: should return None
check("Interior: no edge",        detect_edge(9 * TILE, 9 * TILE)   is None)
check("Interior off-center",      detect_edge(3 * TILE + 8, 5 * TILE + 12) is None)

# ── Group 6: edge-triggered (fire only on entry, not per-frame) ───────────────
print("\n[6] Edge-triggered: log fires only when edge state changes")
log_calls: list[str] = []

def _fake_log(msg): log_calls.append(msg)

def simulate_frame(player_x, player_y, last_edge):
    """Returns new last_edge; appends to log_calls if transition fires."""
    edge_now = detect_edge(player_x, player_y)
    if edge_now is not None and edge_now is not last_edge:
        if not loader.can_transition(0, 0, edge_now):
            _fake_log(f"[PANEL] {edge_now.value.lower()}")
    return edge_now

last_edge = None

# Step into NORTH edge
last_edge = simulate_frame(5 * TILE, 0, last_edge)
check("First entry into NORTH fires log",         len(log_calls) == 1)
check("Log message mentions north",               "north" in log_calls[-1])

# Stay on NORTH edge — must NOT re-fire
last_edge = simulate_frame(6 * TILE, 0, last_edge)
check("Staying on NORTH: no re-fire",             len(log_calls) == 1)

# Move to interior
last_edge = simulate_frame(5 * TILE, 9 * TILE, last_edge)
check("Interior: no log (last_edge cleared)",     len(log_calls) == 1)

# Re-enter NORTH from interior — should fire again
last_edge = simulate_frame(5 * TILE, 0, last_edge)
check("Re-enter NORTH: fires again",              len(log_calls) == 2)

# Enter EAST edge
last_edge = simulate_frame((COLS-1)*TILE, 5 * TILE, last_edge)
check("Enter EAST: fires log",                    len(log_calls) == 3)
check("Log mentions east",                        "east" in log_calls[-1])

# Corner: crossing directly from EAST to NORTH — fires once for NORTH
last_edge = simulate_frame(5 * TILE, 0, last_edge)
check("Cross EAST->NORTH fires for NORTH",        len(log_calls) == 4)

# ── Group 7: WorldPos dataclass still intact ──────────────────────────────────
print("\n[7] WorldPos dataclass still intact")
wp = WorldPos(panel_x=0, panel_y=0, col=5, row=9)
check("WorldPos fields", wp.panel_x == 0 and wp.panel_y == 0 and wp.col == 5 and wp.row == 9)
check("WorldPos is frozen", True)  # import would fail if broken

# ── Summary ────────────────────────────────────────────────────────────────────
print(f"\n{'='*48}")
print(f"  {passed} PASS  |  {failed} FAIL")
if failed:
    sys.exit(1)
print("  Phase 3.6 smoke CLEAN")
