# items.py — Combat item definitions (data-driven)
# Loads item templates from items.json via GameContext.
# Builds inventory stacks from entity bag definitions in entities.json.
from __future__ import annotations
from Mechanics.data.context import GameContext


def get_item(ctx: GameContext, item_id: str) -> dict | None:
    """Look up a single item template by id."""
    return ctx.items.get_by_id(item_id)


def get_item_as_combat(ctx: GameContext, item_id: str) -> dict | None:
    """Return an item dict in the flat format the combat engine expects.

    Combat engine expects keys like 'heal', 'restore_sp', 'restore_mp'
    at the top level. This flattens the 'effects' sub-dict.
    """
    raw = get_item(ctx, item_id)
    if raw is None:
        return None
    flat = {"id": raw["id"], "name": raw["name"]}
    flat.update(raw.get("effects", {}))
    return flat


def build_bag(ctx: GameContext, entity_id: str) -> list:
    """Build the combat inventory for an entity from entities.json bag field.

    Returns a list of InvStack objects ready for the Fighter dataclass.
    """
    from Mechanics.combat.combat import InvStack

    entity = ctx.entities.get_by_id(entity_id)
    if entity is None:
        return []

    bag_defs = entity.get("bag", [])
    stacks = []
    for entry in bag_defs:
        item = get_item_as_combat(ctx, entry["item_id"])
        if item is not None:
            stacks.append(InvStack(item=item, qty=entry.get("qty", 1)))
    return stacks


def starter_bag(ctx: GameContext) -> list:
    """Default player combat inventory — loaded from entities.json 'player' bag."""
    return build_bag(ctx, "player")
