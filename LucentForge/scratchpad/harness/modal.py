"""modal.py — drive the blocking modal screens (pause, inventory, chest, save/load, combat) headlessly.

Modals run their own `while True` loops, read `pygame.event.get()` and create their own fonts with
`pygame.font.SysFont`. `capture_modal` patches both for the duration of one call:
- `pygame.event.get` returns a script: a few empty frames (so the screen draws), then the exit events;
  if the script runs out, it keeps sending QUIT, and a frame guard raises instead of hanging forever.
- `pygame.font.SysFont` hands out `SpyFont`s that record every string drawn.

    drawn, result = capture_modal(run_pause_menu, args..., exit_events=[key(K_ESCAPE)])
"""
from __future__ import annotations

import contextlib

import pygame

from harness.headless import SpyFont, quiet

MAX_FRAMES = 600            # a modal that hasn't exited after 10 s of scripted frames is hung


def key(k: int) -> pygame.event.Event:
    return pygame.event.Event(pygame.KEYDOWN, key=k, mod=0, unicode="", scancode=0)


@contextlib.contextmanager
def _patched(script: list[list], spies: list[SpyFont]):
    real_get, real_sysfont = pygame.event.get, pygame.font.SysFont
    frames = {"n": 0}

    def scripted_get(*_a, **_k):
        frames["n"] += 1
        if frames["n"] > MAX_FRAMES:
            raise RuntimeError("modal did not exit within MAX_FRAMES scripted frames")
        if script:
            return script.pop(0)
        return [pygame.event.Event(pygame.QUIT)]

    def spy_sysfont(*a, **k):
        spy = SpyFont(real_sysfont(*a, **k))
        spies.append(spy)
        return spy

    pygame.event.get, pygame.font.SysFont = scripted_get, spy_sysfont
    try:
        yield
    finally:
        pygame.event.get, pygame.font.SysFont = real_get, real_sysfont


def capture_modal(fn, *args, exit_events=None, warmup_frames: int = 2, shell_font=None, **kwargs):
    """Run modal `fn(*args, **kwargs)`; return (strings drawn, the modal's return value)."""
    spies: list[SpyFont] = []
    if shell_font is not None:
        shell_font.drawn.clear()
    script = [[] for _ in range(warmup_frames)] + [list(exit_events or [])]
    with _patched(script, spies), quiet():
        result = fn(*args, **kwargs)
    drawn = [s for spy in spies for s in spy.drawn]
    if shell_font is not None:
        drawn += shell_font.drawn
    return drawn, result
