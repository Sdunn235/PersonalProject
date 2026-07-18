# affinity.py — The Grace: eight-affinity lattice (§M5, Grace docs).
#
# Four Primal affinities (Fire/Air/Water/Earth) and four Derived affinities that sit
# between adjacent primals (Plasma/Colloidal Dispersion/Non-Newtonian/Bingham Placidity).
# "Derived" means emergent combination, NOT superiority (Grace §2.3).
#
# Light and Dark are ONTOLOGICAL STATES (Creation / absence), not affinities — they are
# deliberately absent from this enum (Grace §0, §16.1). A rare cosmological marker lives in
# the separate `OntologicalTrait` enum (Grace §16.2), never inside `Affinity`.
#
# Relationship authority is the lattice API below (Grace §16.3). The old six-element
# `opposite()` / Light↔Void opposition matrix is retired — affinity combat behavior is
# deferred until the lattice data model is stable (§M6, Grace §12–§13).
from __future__ import annotations
import enum
from dataclasses import dataclass, field


class Affinity(enum.Enum):
    # Ordered to match the Grace lattice clockwise (Grace §2.1):
    # Fire → Plasma → Air → Colloidal → Water → Non-Newtonian → Earth → Bingham → Fire.
    FIRE                 = "FIRE"
    PLASMA               = "PLASMA"                # Fire + Air
    AIR                  = "AIR"
    COLLOIDAL_DISPERSION = "COLLOIDAL_DISPERSION"  # Air + Water
    WATER                = "WATER"
    NON_NEWTONIAN        = "NON_NEWTONIAN"         # Water + Earth
    EARTH                = "EARTH"
    BINGHAM_PLACIDITY    = "BINGHAM_PLACIDITY"     # Earth + Fire


class OntologicalTrait(enum.Enum):
    """Rare cosmological markers, kept SEPARATE from Affinity (Grace §16.2).

    `LIGHT_TOUCHED` marks a being touched by Creation/the Source — the player carries it
    (the sole former `LIGHT`-affinity entity, re-authored as neutral affinity + this trait).
    This is a marker only; the full Creation/Unmade ontology stays deferred.
    """
    LIGHT_TOUCHED = "LIGHT_TOUCHED"


# --- The four Primal affinities ---
_PRIMALS: frozenset[Affinity] = frozenset({
    Affinity.FIRE, Affinity.AIR, Affinity.WATER, Affinity.EARTH,
})

# --- Derived → its two adjacent primal parents (Grace §2.2) ---
_DERIVED_PARENTS: dict[Affinity, frozenset[Affinity]] = {
    Affinity.PLASMA:               frozenset({Affinity.FIRE,  Affinity.AIR}),
    Affinity.COLLOIDAL_DISPERSION: frozenset({Affinity.AIR,   Affinity.WATER}),
    Affinity.NON_NEWTONIAN:        frozenset({Affinity.WATER, Affinity.EARTH}),
    Affinity.BINGHAM_PLACIDITY:    frozenset({Affinity.EARTH, Affinity.FIRE}),
}

# Reverse index: {primal_a, primal_b} → Derived
_PARENTS_TO_DERIVED: dict[frozenset[Affinity], Affinity] = {
    parents: derived for derived, parents in _DERIVED_PARENTS.items()
}


# --- Lattice relationship API (Grace §16.3) ---

def is_primal(a: Affinity) -> bool:
    """True if `a` is one of the four Primal affinities."""
    return a in _PRIMALS


def is_derived(a: Affinity) -> bool:
    """True if `a` is one of the four Derived affinities."""
    return a in _DERIVED_PARENTS


def parents_of(derived: Affinity) -> frozenset[Affinity]:
    """The two adjacent primal parents of a Derived affinity.

    Raises ValueError if `derived` is not a Derived affinity.
    """
    try:
        return _DERIVED_PARENTS[derived]
    except KeyError:
        raise ValueError(f"{derived} is not a Derived affinity")


def derived_between(primal_a: Affinity, primal_b: Affinity) -> Affinity | None:
    """The Derived affinity bridging two adjacent primals, or None if they are not
    adjacent (or either is not primal). Order-independent (Grace §2.2)."""
    return _PARENTS_TO_DERIVED.get(frozenset({primal_a, primal_b}))


def adjacent_primals(primal: Affinity) -> frozenset[Affinity]:
    """The two primals that share a Derived bridge with `primal`.

    Fire ↔ Air (Plasma) and Fire ↔ Earth (Bingham), etc. Raises ValueError if not primal.
    """
    if not is_primal(primal):
        raise ValueError(f"{primal} is not a Primal affinity")
    neighbors: set[Affinity] = set()
    for parents in _DERIVED_PARENTS.values():
        if primal in parents:
            neighbors |= set(parents)
    neighbors.discard(primal)
    return frozenset(neighbors)


# The eight lattice positions in clockwise ring order (Grace §2.1). The enum is
# already declared in this order, so index == ring position.
_RING: list[Affinity] = list(Affinity)


def lattice_distance(a: Affinity, b: Affinity) -> int:
    """Shortest step-distance between two affinities on the 8-position Grace ring.

    Returns 0..4 (0 iff a == b, 4 = directly across). Symmetric. This is the Grace
    §16.3 `lattice_distance` — built now that affinity comfort needs it. Behavior is
    derived from relationship *type* (ring distance), not a hardcoded opposite (§12.2).
    """
    i, j = _RING.index(a), _RING.index(b)
    d = abs(i - j)
    return min(d, len(_RING) - d)


# Ring-distance → comfort scalar (§B3 of the biochem/affinity addendum).
_RING_COMFORT: dict[int, float] = {0: 1.0, 1: 0.5, 2: 0.2, 3: -0.4, 4: -0.8}


def comfort_score(effective: "frozenset[Affinity]",
                  region: Affinity | None, intensity: float) -> float:
    """Affinity comfort in [-1, +1] for an entity standing in a region's field.

    The best (most comfortable) pairing across the entity's `effective` affinities and
    the `region` affinity, by lattice distance (§B3), scaled by region `intensity`.
    Neutral entity (empty effective set) or neutral region (None) or zero intensity → 0.0.
    """
    if region is None or not effective or intensity <= 0.0:
        return 0.0
    best = max(_RING_COMFORT[lattice_distance(aff, region)] for aff in effective)
    return best * intensity


@dataclass
class AffinityState:
    """An entity's affinity attunement (§M5, the Grace).

    `innate` may be a single Primal or Derived affinity (Derived-innate is allowed,
    Grace §21.1), or **None** = neutral/unaligned (a legal state, Grace §21.2). A permanent
    grant/suppress layer makes affinities mutable and plural. Timed modifiers are a seeded
    hook (add an expiry-tracked variant when the first temporary effect lands).

    `trait` carries a rare ontological marker (see `OntologicalTrait`) kept separate from the
    affinity enum — colocated here only for minimal, single-home serialization.

    NOTE: plural effective primals do NOT auto-collapse into a Derived affinity — Derived
    *emergence* is a separate, deferred mechanic (Grace §6.3).
    """
    innate:     Affinity | None = None
    granted:    set[Affinity] = field(default_factory=set)
    suppressed: set[Affinity] = field(default_factory=set)
    trait:      OntologicalTrait | None = None

    def effective(self) -> frozenset[Affinity]:
        """The affinities this entity is currently attuned to (empty set = neutral)."""
        base: set[Affinity] = {self.innate} if self.innate is not None else set()
        return frozenset((base | self.granted) - self.suppressed)

    def is_neutral(self) -> bool:
        """True if the entity has no effective affinity (neutral — NOT Dark)."""
        return len(self.effective()) == 0

    def has(self, a: Affinity) -> bool:
        return a in self.effective()

    def grant(self, a: Affinity) -> None:
        """Permanently add an affinity (blessing/spell)."""
        self.granted.add(a)
        self.suppressed.discard(a)

    def suppress(self, a: Affinity) -> None:
        """Permanently remove an affinity — even the innate one (curse)."""
        self.suppressed.add(a)
        self.granted.discard(a)

    def reset_mods(self) -> None:
        """Clear all modifiers, returning to the innate affinity only."""
        self.granted.clear()
        self.suppressed.clear()

    def as_dict(self) -> dict:
        return {
            "innate":     self.innate.value if self.innate is not None else None,
            "granted":    sorted(a.value for a in self.granted),
            "suppressed": sorted(a.value for a in self.suppressed),
            "trait":      self.trait.value if self.trait is not None else None,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "AffinityState":
        # Legacy LIGHT/VOID strings fail visibly here (ValueError) — no silent remap (Grace §17).
        innate_raw = data.get("innate")
        trait_raw = data.get("trait")
        return cls(
            innate=(Affinity(innate_raw) if innate_raw is not None else None),
            granted={Affinity(a) for a in data.get("granted", [])},
            suppressed={Affinity(a) for a in data.get("suppressed", [])},
            trait=(OntologicalTrait(trait_raw) if trait_raw is not None else None),
        )
