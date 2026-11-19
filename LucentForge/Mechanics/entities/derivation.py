# derivation.py — polymorphic pool-capacity formulas (§M3).
#
# "Capacity is a formula, not a coefficient." Pool maxima are attribute products,
# expressed as swappable strategies so the system stays a living, extensible force.
# Because attributes will eventually grow and ascend (§M9.1), always recompute from
# CURRENT attribute values — never freeze a pool max at spawn.
from __future__ import annotations
from typing import Protocol
import settings
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
    """Raw structured capacity = Intuition x Constitution x Intellect (§M3).

    This is the total structured *bit-equivalent* capacity; normalize to Bytes via
    byte_capacity(). Intellect 0 (e.g. goblins) -> 0: pure Bit-casters, on-theme.
    """
    return attrs.intuition * attrs.constitution * attrs.intellect


def byte_capacity(attrs: Attributes) -> int:
    """Byte pool max = raw structured capacity / (1 Byte = 8 Bits), §M3/§M4 (LIVE 4.5).

    Dividing the bit-equivalent triple product by BITS_PER_BYTE expresses it in Bytes
    using the canonical ratio (no arbitrary constant). player 180/8=22, dragon 2160/8=270.
    """
    return byte_capacity_formula(attrs) // BITS_PER_BYTE


def endurance(attrs: Attributes) -> float:
    """Stamina resistance = Constitution×CON_WEIGHT + Physique×PHY_WEIGHT (§W6/§M3).

    A capacity-style polymorphic strategy beside bit/byte_capacity: the ExertionEmitter
    reads this (via fatigue_gain) to scale fatigue accrual.
    Constitution (durability) leads, Physique (raw strength) is secondary. Clamped to
    ENDURANCE_MIN so effective_gain never divides by <1. Recompute from CURRENT attributes
    each tick — never freeze at spawn (§M9.1). When a dedicated Stamina attribute lands,
    re-register this strategy without touching the emitter."""
    raw = (attrs.constitution * settings.ENDURANCE_CON_WEIGHT
           + attrs.physique * settings.ENDURANCE_PHY_WEIGHT)
    return max(settings.ENDURANCE_MIN, raw)


def fatigue_gain(attrs: Attributes) -> float:
    """Per-frame fatigue accrual rate for this entity (§W6.1).

    The authored reference rate (settings.FATIGUE_REF_GAIN_PER_FRAME, solved from the reference
    human's plateau + half-time) scaled by how this entity's endurance compares to that reference:
    endurance 2× the reference → tires half as fast. Recomputed from live attributes every call."""
    return (settings.FATIGUE_REF_GAIN_PER_FRAME
            * settings.ENDURANCE_REFERENCE / endurance(attrs))


def byte_capacity_parity(legacy_mp_max: int) -> int:
    """4.3 parity strategy (retired in 4.5): the Byte pool inherited the authored mp
    budget so combat magic was unchanged. Kept for reference / legacy callers."""
    return legacy_mp_max
