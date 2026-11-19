# run_kernel_headless_tests.py — the Ripple Kernel runs with no display (bible §RT, BACKLOG LF-046).
#
# QA acceptance examples (written before the fix, red on 2026-11-19):
#   1. A fresh process that never initializes pygame can build a game and step the kernel.
#   2. The player moves only by INTENT (set by the shell from keys, or by an AI player), never by the sim
#      reading the keyboard: intent (1, 0) moves the player right; intent (0, 0) leaves them still.
#   3. The player controller module does not import pygame.
# Runs the scenario in a subprocess so no earlier pygame.init() can mask a dependency.
#
#   py scratchpad/run_kernel_headless_tests.py
import os
import subprocess
import sys
import textwrap

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_fails: list[str] = []


def check(label: str, cond: bool, detail: str = "") -> None:
    print(f"[{'PASS' if cond else 'FAIL'}] {label}" + (f"  ({detail})" if detail and not cond else ""))
    if not cond:
        _fails.append(label)


SCENARIO = textwrap.dedent(r"""
    import os, sys, tempfile, contextlib, io
    sys.path.insert(0, os.getcwd())
    import settings
    from Mechanics.bootstrap import create_game_context
    from Mechanics.runtime.kernel import SimulationKernel
    from Mechanics.world.tile_map import TileMap
    with contextlib.redirect_stdout(io.StringIO()):
        ctx = create_game_context(db_path=os.path.join(tempfile.mkdtemp(), "k.db"))
        tm = TileMap(); tm.load_real_map()
        k = SimulationKernel.new_session(ctx, tm, tm.get_need_sources())
        dt, now = 1.0 / settings.FPS, 0.0
        for _ in range(120):
            now += dt; k.step(dt, now)
        p, pc = k.session.player, k.session.player_controller
        x0 = p.x
        pc.move_intent = (0.0, 0.0)
        for _ in range(30):
            now += dt; k.step(dt, now)
        x_still = p.x
        pc.move_intent = (1.0, 0.0)
        for _ in range(30):
            now += dt; k.step(dt, now)
        x_moved = p.x
    import pygame
    print("RESULT", pygame.display.get_init(), x0, x_still, x_moved)
""")

print("=" * 64)
print("Kernel headless tests - no display, player moves by intent")
print("=" * 64)
env = dict(os.environ)
env.pop("SDL_VIDEODRIVER", None)          # a real headless process: no video driver hint either
proc = subprocess.run([sys.executable, "-c", SCENARIO], cwd=ROOT, env=env, capture_output=True, text=True)
result = next((l for l in proc.stdout.splitlines() if l.startswith("RESULT")), None)
check("kernel builds and steps in a process that never initialized a display",
      proc.returncode == 0 and result is not None,
      (proc.stderr.strip().splitlines() or ["no output"])[-1])
if result:
    _, display_init, x0, x_still, x_moved = result.split()
    check("no display was initialized along the way", display_init == "False")
    check("intent (0, 0): the player stays put", float(x_still) == float(x0), f"{x0} -> {x_still}")
    check("intent (1, 0): the player moves right", float(x_moved) > float(x_still),
          f"{x_still} -> {x_moved}")

src = open(os.path.join(ROOT, "Mechanics", "ai", "player.py"), encoding="utf-8").read()
check("Mechanics/ai/player.py does not import pygame",
      "import pygame" not in src and "from pygame" not in src)

print("=" * 64)
if _fails:
    print(f"{len(_fails)} FAIL: " + "; ".join(_fails))
    sys.exit(1)
print("Kernel headless tests CLEAN")
