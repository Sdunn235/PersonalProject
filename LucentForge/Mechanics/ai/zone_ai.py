# zone_ai.py — Zone-entry behavioral triggers (Phase 3.5).
# No new AI states; chemicals only. Goblin anger nudge on civilized entry;
# human fear nudge on goblin-territory entry.
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from Mechanics.world.zone_events import ZoneCrossingEvent

from Mechanics.world.rooms import RoomType

_CIVILIZED   = frozenset({RoomType.SETTLEMENT, RoomType.FARM, RoomType.STORAGE})
_GOBLIN_ZONE = frozenset({RoomType.GOBLIN_TERRITORY})

_GOBLIN_ANGER_NUDGE = 0.15   # anger bump: goblin enters civilized territory
_HUMAN_FEAR_NUDGE   = 0.20   # fear bump: non-goblin enters goblin territory


class ZoneAIResponder:
    """Zone-crossing behavioral triggers — chemical injection, no state transitions."""

    def on_zone_cross(self, event: "ZoneCrossingEvent", entity, ctrl) -> None:
        room = event.to_room
        if room is None:
            return
        if not hasattr(ctrl, "brain"):
            return
        rt  = room.room_type
        sub = getattr(entity, "subtype", None)

        if sub == "goblin" and rt in _CIVILIZED:
            ctrl.brain.chemicals.set(
                "anger",
                min(1.0, ctrl.brain.chemicals.get("anger") + _GOBLIN_ANGER_NUDGE),
            )
        elif sub != "goblin" and rt in _GOBLIN_ZONE:
            ctrl.brain.chemicals.add_fear(_HUMAN_FEAR_NUDGE)
