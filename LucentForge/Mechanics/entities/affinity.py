# affinity.py — Elemental affinity model (§M5–M6).
#
# Six elements. Every creature is born with a single innate affinity; a grant/suppress
# modifier layer lets spells/events/curses/blessings add, remove, or change affinities
# over time (so affinities can become plural). effective() = ({innate} | granted) - suppressed.
#
# Opposition pairs live here as the data authority (§M6); combat consumes them in 4.6.
from __future__ import annotations
import enum
from dataclasses import dataclass, field


class Affinity(enum.Enum):
    EARTH = "EARTH"
    FIRE  = "FIRE"
    AIR   = "AIR"
    WATER = "WATER"
    VOID  = "VOID"
    LIGHT = "LIGHT"


# Opposition pairs (§M6): fire<->water, earth<->air, light<->void. Total over all 6.
_OPPOSITES = {
    Affinity.FIRE:  Affinity.WATER,
    Affinity.WATER: Affinity.FIRE,
    Affinity.EARTH: Affinity.AIR,
    Affinity.AIR:   Affinity.EARTH,
    Affinity.LIGHT: Affinity.VOID,
    Affinity.VOID:  Affinity.LIGHT,
}


def opposite(el: Affinity) -> Affinity:
    """Return the opposing element (§M6). Used by affinity combat in 4.6."""
    return _OPPOSITES[el]


@dataclass
class AffinityState:
    """An entity's elemental affinity (§M5).

    Single innate affinity at birth, mutable via a permanent grant/suppress layer.
    Timed (temporary) modifiers are a SEEDED hook — when a temporary effect lands
    (4.6+/Stage 5), add an expiry-tracked variant that clears on tick. Permanent
    grant/suppress works now.
    """
    innate:     Affinity
    granted:    set[Affinity] = field(default_factory=set)
    suppressed: set[Affinity] = field(default_factory=set)

    def effective(self) -> frozenset[Affinity]:
        """The elements this entity is currently attuned to."""
        return frozenset(({self.innate} | self.granted) - self.suppressed)

    def has(self, el: Affinity) -> bool:
        return el in self.effective()

    def grant(self, el: Affinity) -> None:
        """Permanently add an affinity (blessing/spell)."""
        self.granted.add(el)
        self.suppressed.discard(el)

    def suppress(self, el: Affinity) -> None:
        """Permanently remove an affinity — even the innate one (curse)."""
        self.suppressed.add(el)
        self.granted.discard(el)

    def reset_mods(self) -> None:
        """Clear all modifiers, returning to the innate affinity only."""
        self.granted.clear()
        self.suppressed.clear()

    def as_dict(self) -> dict:
        return {
            "innate":     self.innate.value,
            "granted":    sorted(a.value for a in self.granted),
            "suppressed": sorted(a.value for a in self.suppressed),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "AffinityState":
        return cls(
            innate=Affinity(data["innate"]),
            granted={Affinity(a) for a in data.get("granted", [])},
            suppressed={Affinity(a) for a in data.get("suppressed", [])},
        )
