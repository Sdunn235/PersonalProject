# ability_sets.py — Per-entity ability loadouts (data-driven)
# Loads ability definitions from abilities.json via GameContext.
# Each entity's ability list is defined in entities.json.
from __future__ import annotations
from Mechanics.data.context import GameContext


def get_abilities(ctx: GameContext, entity_id: str) -> list[dict]:
    """Return the ability list for an entity, loaded from JSON.

    Looks up the entity's ability id list in entities.json,
    then resolves each id against abilities.json.
    Falls back to a basic attack if entity or abilities not found.
    """
    entity = ctx.entities.get_by_id(entity_id)
    if entity is None:
        return [_fallback_basic()]

    ability_ids = entity.get("abilities", [])
    abilities = [
        ab for ab_id in ability_ids
        if (ab := ctx.abilities.get_by_id(ab_id)) is not None
        and ab.get("category") != "basic"
    ]

    return abilities if abilities else [_fallback_basic()]


def get_basic_attack(ctx: GameContext) -> dict:
    """Return the basic 'strike' ability from JSON, or a hardcoded fallback."""
    strike = ctx.abilities.get_by_id("strike")
    if strike is not None:
        return dict(strike)
    return _fallback_basic()


def get_all_abilities_for(ctx: GameContext, entity_id: str) -> list[dict]:
    """Return ALL abilities for an entity including basic strike."""
    entity = ctx.entities.get_by_id(entity_id)
    if entity is None:
        return [_fallback_basic()]

    ability_ids = entity.get("abilities", [])
    return [
        ab for ab_id in ability_ids
        if (ab := ctx.abilities.get_by_id(ab_id)) is not None
    ] or [_fallback_basic()]


def _fallback_basic() -> dict:
    return {
        "id": "_basic", "name": "Basic", "kind": "attack",
        "power": 1.0, "cost_cycles": 0, "category": "ability",
    }
