# derivation.py — polymorphic pool-capacity formulas (§M3).
#
# "Capacity is a formula, not a coefficient." Pool maxima are attribute products,
# expressed as swappable strategies so the system stays a living, extensible force.
# Because attributes will eventually grow and ascend (§M9.1), always recompute from
# CURRENT attribute values — never freeze a pool max at spawn.
from __future__ import annotations
from typing import Protocol
from Mechanics.entities.attributes import Attributes

# 1 Byte = 8 Bits — canonical structural ratio (§M3). Also the Bits->Bytes
# conversion ratio (4.5) and the attribute-XP granularity (§M9.1).
BITS_PER_BYTE = 8


class CapacityFormula(Protocol):
    """A pool-capacity strategy: attributes -> max pool size. Polymorphic seam so
    4.5+ can register new formulas (or per-race variants) without touching callers."""
    def __call__(self, attrs: Attributes) -> int: ...


def bit_capacity(attrs: Attributes) -> int:
    """Bit pool max = Intuition x Constitution (§M3). LIVE in 4.3."""
    return attrs.intuition * attrs.constitution


def byte_capacity_formula(attrs: Attributes) -> int:
    """Target Byte pool max = Intuition x Constitution x Intellect (§M3).

    NOT active in 4.3 (parity path). 4.5 swaps this in, normalizing the
    multiplicative growth and retuning spell costs.
    """
    return attrs.intuition * attrs.constitution * attrs.intellect


def byte_capacity_parity(legacy_mp_max: int) -> int:
    """4.3 parity strategy: the Byte pool inherits the authored mp budget so combat
    magic is unchanged. Swapped for byte_capacity_formula in 4.5."""
    return legacy_mp_max
