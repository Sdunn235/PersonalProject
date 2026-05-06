# equip.py — Equipment resolver (data-driven)
# Resolves entity equipment slots to flat stat modifiers for combat.
from __future__ import annotations
from Mechanics.data.context import GameContext


def resolve_equipment(ctx: GameContext, entity_id: str) -> dict:
    """Load an entity's equipped items and return combined stat modifiers.

    Returns a flat dict like {"atk": 5, "def": 3, "mag": 4}.
    Keys match the effects fields in items.json.
    """
    entity = ctx.entities.get_by_id(entity_id)
    if entity is None:
        return {}

    equipment = entity.get("equipment", {})
    mods = {}

    for slot, item_id in equipment.items():
        item = ctx.items.get_by_id(item_id)
        if item is None:
            continue
        for stat, value in item.get("effects", {}).items():
            mods[stat] = mods.get(stat, 0) + value

    return mods
