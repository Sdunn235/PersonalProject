# attributes.py — Core Attributes (bible §4.1), the primary character layer.
#
# Stage 4 (§M2): the 7 bible attributes are the authored source of truth. Combat
# `Stats` are DERIVED from them via `to_stats()` — attributes are primary, Stats
# are the derived combat-facing layer.
#
# Wired this stage:  Physique→STR, Reflexes→DEX, Luck→LCK, Intellect→MAG,
#                    Constitution→DEF. (Intuition drives Bit-pool capacity + trap
#                    perception — not a combat Stat; wired in 4.2/4.3.)
# Inert this stage:  Linguistic (defined, no mechanic until Stage 5+).
#
# RES (elemental resistance) is NOT attribute-derived yet: today's data has DEF
# and RES independent per entity, and RES's real home is the deferred §7 per-element
# resist model. It is carried as a pass-through `resist` value until then (§M2).
from __future__ import annotations
from dataclasses import dataclass
from Mechanics.entities.stats import Stats

# Attribute defaults are chosen to reproduce the old Stats() defaults when a JSON
# block omits a field, so parity holds for partially-specified entities.
_DEF_PHYSIQUE     = 10   # → STR default 10
_DEF_REFLEXES     = 5    # → DEX default 5
_DEF_LUCK         = 5    # → LCK default 5
_DEF_INTELLECT    = 0    # → MAG default 0
_DEF_CONSTITUTION = 5    # → DEF default 5
_DEF_INTUITION    = 5    # new — neutral baseline
_DEF_LINGUISTIC   = 5    # new — inert this stage


@dataclass
class Attributes:
    """The 7 core attributes (bible §4.1). Primary layer; feeds `to_stats()`."""
    physique:     int = _DEF_PHYSIQUE
    reflexes:     int = _DEF_REFLEXES
    constitution: int = _DEF_CONSTITUTION
    intellect:    int = _DEF_INTELLECT
    intuition:    int = _DEF_INTUITION
    linguistic:   int = _DEF_LINGUISTIC
    luck:         int = _DEF_LUCK

    def to_stats(self, resist: int = 0, clamp_mode: str = "clamp") -> Stats:
        """Derive the combat-facing Stats from these attributes (§M2 mapping).

        `resist` is the pass-through elemental-resistance value (RES), which is
        not attribute-derived until the §7 resist model lands.
        """
        return Stats(
            STR=self.physique,
            DEX=self.reflexes,
            LCK=self.luck,
            MAG=self.intellect,
            DEF=self.constitution,
            RES=resist,
            clamp_mode=clamp_mode,
        )

    def as_dict(self) -> dict:
        return {
            "physique":     self.physique,
            "reflexes":     self.reflexes,
            "constitution": self.constitution,
            "intellect":    self.intellect,
            "intuition":    self.intuition,
            "linguistic":   self.linguistic,
            "luck":         self.luck,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Attributes":
        return cls(
            physique=data.get("physique", _DEF_PHYSIQUE),
            reflexes=data.get("reflexes", _DEF_REFLEXES),
            constitution=data.get("constitution", _DEF_CONSTITUTION),
            intellect=data.get("intellect", _DEF_INTELLECT),
            intuition=data.get("intuition", _DEF_INTUITION),
            linguistic=data.get("linguistic", _DEF_LINGUISTIC),
            luck=data.get("luck", _DEF_LUCK),
        )
