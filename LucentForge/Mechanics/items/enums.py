from enum import IntEnum, IntFlag


class SlotType(IntFlag):
    MAIN_HAND = 1
    OFF_HAND  = 2
    HEAD      = 4
    CHEST     = 8
    LEGS      = 16
    FEET      = 32
    HANDS     = 64        # gauntlets — body armor, not a held-item slot
    ANY_HAND  = MAIN_HAND | OFF_HAND


class BodySlot(IntEnum):
    HEAD      = 0
    CHEST     = 1
    LEGS      = 2
    FEET      = 3
    HANDS     = 4         # gauntlet slot; distinct from held-item slots
    MAIN_HAND = 5
    OFF_HAND  = 6


class WeaponType(IntEnum):
    SWORD  = 0
    AXE    = 1
    MACE   = 2
    BOW    = 3
    STAFF  = 4
    DAGGER = 5
    SPEAR  = 6


class ArmorWeight(IntEnum):
    LIGHT  = 0
    MEDIUM = 1
    HEAVY  = 2


class ConsumableEffect(IntEnum):
    NONE          = 0
    HEAL          = 1
    RESTORE_SP    = 2
    RESTORE_MP    = 3     # bridge — restores the Byte pool (§M4); retained for old items
    UNLOCK        = 4     # §A1 capability grant; mechanic deferred to Stage 3
    RESTORE_BITS  = 5     # Stage 4 (§M4) — restores the Bit pool
    RESTORE_BYTES = 6     # Stage 4 (§M4) — restores the Byte pool


class TrapType(IntFlag):
    NONE       = 0
    MECHANICAL = 1        # Stage 2 scope: physical dart/spike
    MAGICAL    = 2        # future — requires Intuition check (§A3)
    POISON     = 4        # future — ongoing DoT on trigger
    ELECTRIC   = 8        # future — instant paralysis on trigger


def body_slot_to_eligible(slot: BodySlot) -> SlotType:
    _MAP = {
        BodySlot.HEAD:      SlotType.HEAD,
        BodySlot.CHEST:     SlotType.CHEST,
        BodySlot.LEGS:      SlotType.LEGS,
        BodySlot.FEET:      SlotType.FEET,
        BodySlot.HANDS:     SlotType.HANDS,
        BodySlot.MAIN_HAND: SlotType.ANY_HAND,
        BodySlot.OFF_HAND:  SlotType.ANY_HAND,
    }
    return _MAP[slot]
