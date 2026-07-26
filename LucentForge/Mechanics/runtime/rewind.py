"""rewind.py — in-memory sim time-scrub buffer (Glass Box A1b-ii).

Keeps the last N tick-states in RAM so the frozen sim can be stepped *backward*
(',' back-tick, mirroring '.' forward). Capture goes through the exact save/load
path (snapshot -> restore) against a private in-memory SQLite DB, so a rewound
state cannot diverge from the persistent save system — and because restore reuses
WorldSession.apply_save, it also restores controller behavioral state (A1b-i), a
true time-reversal rather than an IDLE reset. No disk I/O.
"""
from __future__ import annotations

from collections import deque

from Mechanics.data.db import Database
from Mechanics.data.save_manager import SaveManager


class RewindBuffer:
    """Ring buffer of recent session snapshots for scrub-back."""

    def __init__(self, ctx, maxlen: int = 120) -> None:
        self.ctx = ctx
        self._db = Database(":memory:")          # isolated; never touches the real save
        self._sm = SaveManager(self._db)
        self._states: deque = deque(maxlen=maxlen)

    def record(self, session) -> None:
        """Capture current session state — call once per advanced tick."""
        self._sm.snapshot_session(session, slot_id=0, verbose=False)
        self._states.append(self._sm.restore(slot_id=0))

    def can_back(self) -> bool:
        return len(self._states) >= 2

    def back(self, session) -> bool:
        """Step back one recorded tick (restore the previous state in place).
        Returns True if it stepped back, False if no earlier state is buffered."""
        if len(self._states) < 2:
            return False
        self._states.pop()                                             # drop current tick
        session.apply_save(self._states[-1], self.ctx, verbose=False)  # restore previous
        return True

    def clear(self) -> None:
        """Drop all history (on New Game / load — the timeline changed)."""
        self._states.clear()

    def close(self) -> None:
        self._db.close()
