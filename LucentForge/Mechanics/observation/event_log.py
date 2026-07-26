"""event_log.py — in-memory emergence event feed (Glass Box A3).

A small ring buffer of notable events (behavioral state changes, zone crossings,
need targeting, combat) so emergence is visible on-screen (bottom strip, toggle L)
instead of only in the console. A module-level singleton `EVENTS` is appended to
from a few high-value points across the sim; the shell renders `EVENTS.tail(n)`.

The kernel stamps the current tick each step via `set_tick`, so append sites deep
in the sim (which don't all have the tick handy) can just call `append(category,
text)` and get the right timestamp for free.
"""
from __future__ import annotations

from collections import deque

_CATEGORY_COLORS = {
    "STATE":  (150, 200, 255),
    "ZONE":   (150, 150, 170),
    "NEED":   (242, 200, 100),
    "COMBAT": (229, 90, 90),
    "RAID":   (229, 140, 60),
}
_DEFAULT_COLOR = (200, 200, 210)


class EventLog:
    """Ring buffer of (tick, category, text) emergence events."""

    def __init__(self, maxlen: int = 200) -> None:
        self._events: deque = deque(maxlen=maxlen)
        self._tick = 0

    def set_tick(self, tick: int) -> None:
        """Kernel calls this once per step so appends get the current timestamp."""
        self._tick = tick

    def append(self, category: str, text: str, tick: int | None = None) -> None:
        self._events.append((self._tick if tick is None else tick, category, text))

    def tail(self, n: int) -> list:
        return list(self._events)[-n:]

    def clear(self) -> None:
        self._events.clear()

    @staticmethod
    def color(category: str):
        return _CATEGORY_COLORS.get(category, _DEFAULT_COLOR)


# Module-level singleton — the sim appends here, the shell reads here.
EVENTS = EventLog()
