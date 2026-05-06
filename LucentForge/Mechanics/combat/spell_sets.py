# spell_sets.py — Per-entity spell loadouts (data-driven)
# Spells are abilities with category="spell" in the merged abilities.json.
from __future__ import annotations
from Mechanics.data.context import GameContext


def get_spells(ctx: GameContext, entity_id: str) -> list[dict]:
    """Return the spell list for an entity, loaded from JSON.

    Looks up the entity's spell id list in entities.json,
    then resolves each id against abilities.json (category=spell).
    Returns an empty list if the entity has no spells.
    """
    entity = ctx.entities.get_by_id(entity_id)
    if entity is None:
        return []

    spell_ids = entity.get("spells", [])
    return [
        sp for sp_id in spell_ids
        if (sp := ctx.abilities.get_by_id(sp_id)) is not None
    ]


def get_all_spells_for(ctx: GameContext, entity_id: str) -> list[dict]:
    """Return all spells for an entity. Used by AI action selection."""
    return get_spells(ctx, entity_id)
