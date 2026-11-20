# run_panel_transition_tests.py — the world opens: walking off an edge into the next panel (Arc B, LF-010 step 2).
#
# Canon (Shawn, 2026-11-19): the river flows north to south, and the upper reach, Panel(0,-1), opens first.
# Panel content is World Building's upper-reach proposal; the seam rules are its edge contract (EC1-EC6),
# checked here straight from the data, independent of engine code. Behavior follows the bible:
#   - entities are panel-local (§R8 scope table: NPCs don't migrate yet);
#   - the panel the player leaves keeps simulating (§R6 BACKGROUND scope: "tick-only, no sprites");
#   - nothing reaches across a panel edge (no combat, no blocking between panels).
#
#   py scratchpad/run_panel_transition_tests.py
import json
import os
import sys
from collections import deque

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness.headless import (headless_shell, new_kernel, quiet, render_text, save_frame,  # noqa: E402
                              step)

import pygame  # noqa: E402
import settings  # noqa: E402
from Mechanics.world.tile_map import TileMap  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "Mechanics", "data")
T, ROWS, COLS = settings.TILE_SIZE, settings.ROWS, settings.COLS
_fails: list[str] = []


def check(label: str, cond: bool, detail: str = "") -> None:
    print(f"[{'PASS' if cond else 'FAIL'}] {label}" + (f"  ({detail})" if detail and not cond else ""))
    if not cond:
        _fails.append(label)


def bail() -> None:
    print("=" * 64)
    print(f"{len(_fails)} FAIL: " + "; ".join(_fails))
    sys.exit(1)


print("=" * 64)
print("Panel transition tests - the edge contract and walking upriver")
print("=" * 64)
pygame.init()

# ── 1. The world data: Panel(0,-1) exists and the seams obey the edge contract ──────────────────
panels = json.load(open(os.path.join(DATA, "panels.json"), encoding="utf-8"))
by_id = {p["id"]: p for p in panels}
by_xy = {(p["panel_x"], p["panel_y"]): p for p in panels}
check("Panel(0,-1), the upper reach, is defined", (0, -1) in by_xy)
check("Panel(0,0)'s NORTH edge leads to Panel(0,-1)",
      by_xy.get((0, 0), {}).get("edges", {}).get("NORTH") == by_xy.get((0, -1), {}).get("id", "?"))
if (0, -1) not in by_xy:
    bail()

OFFSET = {"NORTH": (0, -1), "SOUTH": (0, 1), "EAST": (1, 0), "WEST": (-1, 0)}
OPPOSITE = {"NORTH": "SOUTH", "SOUTH": "NORTH", "EAST": "WEST", "WEST": "EAST"}
maps, data = {}, {}
with quiet():
    for p in panels:
        tm = TileMap()
        tm.load_real_map(p["panel_x"], p["panel_y"])
        maps[(p["panel_x"], p["panel_y"])] = tm
        data[(p["panel_x"], p["panel_y"])] = json.load(open(os.path.join(DATA, p["map"]), encoding="utf-8"))


def seam(xy, edge):
    """The tile positions along one edge of a panel, in seam order (west->east or north->south)."""
    if edge == "NORTH":
        return [(c, 0) for c in range(COLS)]
    if edge == "SOUTH":
        return [(c, ROWS - 1) for c in range(COLS)]
    if edge == "WEST":
        return [(0, r) for r in range(ROWS)]
    return [(COLS - 1, r) for r in range(ROWS)]


def tile_name(xy, c, r):
    d = data[xy]
    return d["tile_legend"][d["tiles"][r][c]]


def region_name(xy, c, r):
    d = data[xy]
    return d["region_legend"][d["regions"][r][c]]


# EC3 compatible region pairs (World Building proposal §8; a new tag declares its pairs).
COMPATIBLE = {frozenset(p) for p in (("river", "river"), ("forest", "forest"), ("forest", "town_outskirts"),
                                     ("town_outskirts", "town_outskirts"))}
for p in panels:
    xy = (p["panel_x"], p["panel_y"])
    d = data[xy]
    check(f"{p['id']}: {ROWS} rows x {COLS} tiles", len(d["tiles"]) == ROWS and all(len(r) == COLS for r in d["tiles"]))
    check(f"{p['id']} EC6: every char is in its legends",
          all(ch in d["tile_legend"] for r in d["tiles"] for ch in r)
          and all(ch in d["region_legend"] for r in d["regions"] for ch in r))
    for edge, nid in p["edges"].items():
        if nid is None:
            continue
        q = by_id.get(nid)
        check(f"{p['id']} {edge}: neighbour {nid} exists", q is not None)
        if q is None:
            continue
        nxy = (q["panel_x"], q["panel_y"])
        dx, dy = OFFSET[edge]
        check(f"{p['id']} {edge}: {nid} sits at the matching coordinate", nxy == (xy[0] + dx, xy[1] + dy))
        check(f"{p['id']} {edge}: {nid} leads back ({OPPOSITE[edge]})", q["edges"].get(OPPOSITE[edge]) == p["id"])
        a, b = seam(xy, edge), seam(nxy, OPPOSITE[edge])
        check(f"{p['id']}|{nid} EC1: the river crosses at the same places",
              [tile_name(xy, *t) == "river" for t in a] == [tile_name(nxy, *t) == "river" for t in b])
        check(f"{p['id']}|{nid} EC2: blocked and walkable line up along the seam",
              [maps[xy].is_blocked(*t) for t in a] == [maps[nxy].is_blocked(*t) for t in b],
              f"{[i for i, (s, t) in enumerate(zip(a, b)) if maps[xy].is_blocked(*s) != maps[nxy].is_blocked(*t)]}")
        bad = sorted({(region_name(xy, *s), region_name(nxy, *t)) for s, t in zip(a, b)
                      if frozenset((region_name(xy, *s), region_name(nxy, *t))) not in COMPATIBLE})
        check(f"{p['id']}|{nid} EC3: regions across the seam are compatible", not bad, str(bad))

    # EC4: river tiles orthogonally connected; every component touches an edge.
    # A bridge is river with a crossing over it, so it counts for the river's continuity.
    river = {(c, r) for r in range(ROWS) for c in range(COLS) if tile_name(xy, c, r) in ("river", "bridge")}
    seen, ok4 = set(), True
    for start in river:
        if start in seen:
            continue
        comp, q = {start}, deque([start])
        while q:
            c, r = q.popleft()
            for n in ((c + 1, r), (c - 1, r), (c, r + 1), (c, r - 1)):
                if n in river and n not in comp:
                    comp.add(n)
                    q.append(n)
        seen |= comp
        if not any(c in (0, COLS - 1) or r in (0, ROWS - 1) for c, r in comp):
            ok4 = False
    check(f"{p['id']} EC4: the river reaches an edge (no stranded water)", ok4)

    # EC5: every walkable tile is reachable from a seam that leads somewhere.
    if xy != (0, 0):
        tm = maps[xy]
        walk = {(c, r) for r in range(ROWS) for c in range(COLS) if not tm.is_blocked(c, r)}
        starts = [t for e, n in p["edges"].items() if n for t in seam(xy, e) if t in walk]
        reach, q = set(starts), deque(starts)
        while q:
            c, r = q.popleft()
            for n in ((c + 1, r), (c - 1, r), (c, r + 1), (c, r - 1)):
                if n in walk and n not in reach:
                    reach.add(n)
                    q.append(n)
        check(f"{p['id']} EC5: no sealed pockets (every walkable tile reachable from a seam)",
              reach == walk, f"{len(walk - reach)} unreachable")

# Every region a panel uses has a Room on that panel (zones, comfort and the inspector need it).
rooms = json.load(open(os.path.join(DATA, "rooms.json"), encoding="utf-8"))
for p in panels:
    xy = (p["panel_x"], p["panel_y"])
    used = {region_name(xy, c, r) for r in range(ROWS) for c in range(COLS)}
    have = {r["region_tag"] for r in rooms if (r["panel_x"], r["panel_y"]) == xy}
    check(f"{p['id']}: every region it uses has a Room", used <= have, f"missing {sorted(used - have)}")

# ── 2. Walking upriver (headless kernel) ─────────────────────────────────────────────────────────
ctx, kernel = new_kernel()
s = kernel.session
home_map = s.tile_map
P = s.player
crossable = [c for c in range(COLS) if not maps[(0, 0)].is_blocked(c, 0) and not maps[(0, -1)].is_blocked(c, ROWS - 1)
             and not maps[(0, 0)].is_blocked(c, 1) and not maps[(0, -1)].is_blocked(c, ROWS - 2)]
check("there is a walkable crossing on the north seam", bool(crossable))
if not crossable:
    bail()
col = crossable[len(crossable) // 2]


def place(entity, c, r):
    entity.x, entity.y = c * T + T / 2, r * T + T / 2


def panel_of(entity):
    return (getattr(entity, "panel_x", 0), getattr(entity, "panel_y", 0))


def walk(intent, frames, until_cross=True):
    """Hold an intent for up to `frames` frames; return the SimFrames' panel-change events. Stops on
    the frame the player crosses (so "arrives" means the arrival tile, before walking on)."""
    events = []
    dt = 1.0 / settings.FPS
    with quiet():
        for _ in range(frames):
            s_ = kernel.session
            s_.player_controller.move_intent = intent
            step.now += dt
            f = kernel.step(dt, step.now)
            if getattr(f, "panel_changed", None):
                events.append(f.panel_changed)
                if until_cross:
                    break
    return events


place(P, col, 0)
walk((0, 0), 30)
check("standing on the north edge without pushing north does not cross", panel_of(P) == (0, 0))

place(P, COLS - 1, 8 if not maps[(0, 0)].is_blocked(COLS - 1, 8) else 9)
walk((1, 0), 30)
check("the east edge has no neighbour: pushing east stays on Panel(0,0)", panel_of(P) == (0, 0))

npcs_before = {e.entity_id: (e.x, e.y, [round(n.current_value, 4) for n in c.needs]) for e, c in s.npc_list}
place(P, col, 0)
events = walk((0, -1), 20)
s = kernel.session
check("walking north off Panel(0,0) arrives on Panel(0,-1)", panel_of(P) == (0, -1), str(panel_of(P)))
check("the kernel reports the crossing once (a panel_changed event)", events == [(0, -1)], str(events))
check("the game's current panel follows the player", tuple(ctx.current_panel) == (0, -1))
pc, pr = int(P.x // T), int(P.y // T)
check(f"the player arrives on the south edge in the same column (col {col})", (pc, pr) == (col, ROWS - 1), str((pc, pr)))
check("the world now shows the upper reach's map", s.tile_map.grid == maps[(0, -1)].grid)
check("the player now collides with the upper reach's map", s.player_controller.tile_map is s.tile_map)

# The villagers stay home and keep living (§R6 BACKGROUND).
check("every NPC is still on Panel(0,0)", all(panel_of(e) == (0, 0) for e, _ in s.npc_list))
check("every NPC still walks on Panel(0,0)'s map", all(c.tile_map is home_map for _, c in s.npc_list))
walk((0, 0), 600)
moved = sum(1 for e, c in s.npc_list if (e.x, e.y) != npcs_before[e.entity_id][:2])
needs_moved = sum(1 for e, c in s.npc_list
                  if [round(n.current_value, 4) for n in c.needs] != npcs_before[e.entity_id][2])
check(f"Panel(0,0) keeps living while the player is away ({moved} NPCs moved, {needs_moved} needs changed)",
      moved >= 1 and needs_moved >= len(s.npc_list) // 2)

# Nothing reaches across a panel edge: an NPC at the player's exact x/y on another panel can't fight.
gruk = next(e for e, _ in s.npc_list if e.name == "Gruk")
s.combat_cooldowns.clear()
gruk.x, gruk.y = P.x, P.y
with quiet():
    f = kernel.step(1.0 / settings.FPS, step.now + 100)
check("no combat with an NPC on another panel, even at the same x/y", f.combat_trigger is None)

# Coming home: walk south off the upper reach.
place(P, col, ROWS - 1)
events = walk((0, 1), 20)
check("walking south off Panel(0,-1) returns to Panel(0,0)", panel_of(P) == (0, 0), str(panel_of(P)))
check("the player arrives on Panel(0,0)'s north edge, same column",
      (int(P.x // T), int(P.y // T)) == (col, 0), str((int(P.x // T), int(P.y // T))))
check("home is the same live map the villagers use (not a reload)", kernel.session.tile_map is home_map)
s.combat_cooldowns.clear()
gruk.x, gruk.y = P.x, P.y
with quiet():
    f = kernel.step(1.0 / settings.FPS, step.now + 200)
check("positive control: on the same panel, the same overlap does start a fight", f.combat_trigger is gruk)

# ── 3. Saves remember the panel ─────────────────────────────────────────────────────────────────
place(P, col, 0)
walk((0, -1), 20)
up_tile = (int(P.x // T), int(P.y // T))
with quiet():
    kernel.save(1)
place(P, col, ROWS - 1)
walk((0, 1), 20)
check("(setup) back on Panel(0,0) before loading", panel_of(P) == (0, 0))
with quiet():
    kernel.load(ctx.save_manager.restore(1))
s = kernel.session
check("loading a save made upriver puts the player back on Panel(0,-1)", panel_of(s.player) == (0, -1))
check("... on the same tile", (int(s.player.x // T), int(s.player.y // T)) == up_tile)
check("... with the upper reach's map and current panel",
      s.tile_map.grid == maps[(0, -1)].grid and tuple(ctx.current_panel) == (0, -1)
      and s.player_controller.tile_map is s.tile_map)
# Regions identify a panel's map (chest tiles are stamped onto the live grid, regions never change).
check("... and the villagers still on Panel(0,0)'s map", all(c.tile_map.regions == maps[(0, 0)].regions
                                                             for _, c in s.npc_list))

# ── 4. What the player sees upriver ────────────────────────────────────────────────────────────
# Which entities the shell actually draws: every drawn sprite gets its overlays (bars, name) drawn, so
# recording draw_overlays per sprite names exactly what was on screen. Positive control: at home, the
# villagers are recorded.
kernel.session.player_controller.move_intent = (0, 0)   # hands off the keys (the last walk pushed south)
shell = headless_shell(ctx, kernel)
step(kernel, 2, shell)
drawn_entities: list[str] = []
for sp in shell.sprites.values():
    orig = sp.draw_overlays
    sp.draw_overlays = (lambda o, n: (lambda *a, **k: (drawn_entities.append(n), o(*a, **k))[1]))(orig, sp.entity.name)
names = [e.name for e, _ in kernel.session.npc_list]


def drawn_names():
    drawn_entities.clear()
    render_text(shell, subject=kernel.session.player.name, obs=False)
    return set(drawn_entities)


upriver = drawn_names()
check("upriver, the player is drawn", kernel.session.player.name in upriver, str(upriver))
check("upriver, no Panel(0,0) villager is drawn", not (upriver & set(names)), str(sorted(upriver & set(names))))
save_frame(shell, "20_upper_reach")
place(kernel.session.player, col, ROWS - 1)
walk((0, 1), 20)
step(kernel, 2, shell)
home = drawn_names()
check("back home, the villagers are drawn again (positive control)", bool(set(names) & home),
      str(sorted(home)))
save_frame(shell, "21_back_home")

# New Game starts at home.
with quiet():
    place(kernel.session.player, col, 0)
    walk((0, -1), 20)
    kernel.start_new_session()
check("New Game starts on Panel(0,0) with the home map",
      panel_of(kernel.session.player) == (0, 0) and tuple(ctx.current_panel) == (0, 0)
      and kernel.session.tile_map.regions == maps[(0, 0)].regions)

print("=" * 64)
if _fails:
    bail()
print("Panel transition tests CLEAN")
