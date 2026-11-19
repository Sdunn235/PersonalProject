"""headless.py — shared harness for render, behavior and soak tests (docs/testing.md).

Not a suite: it lives in a subfolder, so `run_all_tests.py` (which runs scratchpad/*.py) never
executes it directly. Suites import it:

    from harness.headless import new_kernel, headless_shell, step, render_text

What it gives a test:
- a seeded, isolated game (temporary DB, fixed RNG seed) built exactly like `main.py` builds one;
- a real `PresentationShell` drawing to an off-screen surface (SDL dummy video driver);
- `SpyFont`, which records every string the world frame draws, so a test can assert what the
  player would *see* (HUD rows, panel suffixes, inspector lines) without a human at the window;
- PNG capture of rendered frames as review evidence (`save_frame`).
"""
from __future__ import annotations

import contextlib
import io
import os
import random
import sys
import tempfile

_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame  # noqa: E402
import settings  # noqa: E402

SEED = 1234                         # the seed every same-seed A/B test in the repo uses
SCREENS_DIR = os.path.join(_ROOT, "logs", "screens", "latest")   # gitignored (logs/)


class SpyFont:
    """Wraps a pygame Font; records each rendered string in `drawn`, forwards everything else."""

    def __init__(self, real) -> None:
        self._real = real
        self.drawn: list[str] = []

    def render(self, text, *args, **kwargs):
        self.drawn.append(str(text))
        return self._real.render(text, *args, **kwargs)

    def __getattr__(self, name):
        return getattr(self._real, name)


@contextlib.contextmanager
def quiet():
    """Silence the game's console logging inside a test."""
    with contextlib.redirect_stdout(io.StringIO()):
        yield


def new_kernel(seed: int = SEED):
    """A fresh, seeded game: (ctx, kernel). Same construction as main.py, temporary DB."""
    from Mechanics.bootstrap import create_game_context
    from Mechanics.runtime.kernel import SimulationKernel
    from Mechanics.world.tile_map import TileMap
    random.seed(seed)
    # The kernel needs no display (LF-046 fixed 2026-11-19: the player moves by intent, set by the shell).
    with quiet():
        ctx = create_game_context(db_path=os.path.join(tempfile.mkdtemp(), "lf_test.db"))
        tile_map = TileMap()
        tile_map.load_real_map()
        kernel = SimulationKernel.new_session(ctx, tile_map, tile_map.get_need_sources())
    return ctx, kernel


def headless_shell(ctx, kernel):
    """A real PresentationShell attached to `kernel`, drawing off-screen, with a SpyFont."""
    from Mechanics.runtime.shell import PresentationShell
    pygame.init()
    with quiet():
        shell = PresentationShell(ctx)
        shell._kernel = kernel
        shell._build_sprites()
        shell._rebuild_hud_subjects()
    shell.font = SpyFont(shell.font)
    return shell


def step(kernel, frames: int, shell=None, record: bool = True) -> None:
    """Advance the sim `frames` frames at the real frame rate. With a shell, keep sprites in sync
    and feed the rewind ring like the live loop does (combat modals are never opened)."""
    dt = 1.0 / settings.FPS
    with quiet():
        for _ in range(frames):
            step.now += dt
            frame = kernel.step(dt, step.now)
            if shell is not None:
                if record and frame.sim_ticks > 0:
                    shell._rewind.record(shell.session)
                shell.sprite_group.update()


step.now = 0.0


def subject_index(shell, name: str) -> int:
    """HUD/inspector subject index of the entity called `name` (TAB order)."""
    for i, (entity, _ctrl, _lbl) in enumerate(shell._hud_subjects):
        if entity.name == name:
            return i
    raise KeyError(name)


def controller_of(kernel, name: str):
    for entity, ctrl in kernel.session.npc_list:
        if entity.name == name:
            return ctrl
    raise KeyError(name)


def render_text(shell, subject: str | None = None, obs: bool = True,
                inspect: bool = False) -> list[str]:
    """Render one full world frame and return every string it drew, in draw order."""
    if subject is not None:
        shell.hud_index = subject_index(shell, subject)
    shell.obs_visible = obs
    shell._inspect = inspect
    shell.font.drawn.clear()
    with quiet():
        shell._render()
    return list(shell.font.drawn)


def save_frame(shell, name: str) -> str:
    """Save the last rendered frame as review evidence; returns the PNG path."""
    os.makedirs(SCREENS_DIR, exist_ok=True)
    path = os.path.join(SCREENS_DIR, f"{name}.png")
    pygame.image.save(shell.screen, path)
    return path
