# factory.py — Entity factory: spawns game entities from JSON data
# Reads entity definitions via GameContext (injected).
# Single point of entity creation (no hardcoding in main.py).
from __future__ import annotations
import settings
from Mechanics.data.context import GameContext
from Mechanics.entities.stats import Stats
from Mechanics.entities.traits import Traits
from Mechanics.ai.npc import NPC


def _build_stats(data: dict) -> Stats:
    """Build a Stats dataclass from a JSON stats sub-object."""
    s = data.get("stats", {})
    return Stats(
        STR=s.get("STR", 10),
        MAG=s.get("MAG", 0),
        LCK=s.get("LCK", 5),
        DEF=s.get("DEF", 5),
        RES=s.get("RES", 0),
        DEX=s.get("DEX", 5),
    )


def _build_traits(data: dict) -> Traits:
    """Build a Traits dataclass from a JSON traits sub-object."""
    t = data.get("traits", {})
    return Traits(
        curiosity=t.get("curiosity", 0.5),
        aggression=t.get("aggression", 0.3),
        fearfulness=t.get("fearfulness", 0.3),
        sociability=t.get("sociability", 0.5),
    )


def _spawn_position(data: dict) -> tuple[float, float]:
    """Convert grid spawn coords to pixel center position."""
    spawn = data.get("spawn", {"col": 0, "row": 0})
    x = settings.TILE_SIZE * spawn["col"] + settings.TILE_SIZE // 2
    y = settings.TILE_SIZE * spawn["row"] + settings.TILE_SIZE // 2
    return float(x), float(y)


def create_entity(ctx: GameContext, entity_id: str) -> NPC | None:
    """Create a single NPC/Player entity from its JSON definition.

    Returns None if the entity_id is not found in entities.json.
    """
    data = ctx.entities.get_by_id(entity_id)
    if data is None:
        return None

    x, y = _spawn_position(data)
    cycles_data = data.get("cycles", {})
    mp_data = data.get("mp", {})

    return NPC(
        entity_id=data["id"],
        name=data["name"],
        subtype=data.get("subtype", ""),
        stats=_build_stats(data),
        traits=_build_traits(data),
        hp=data.get("hp", 100),
        max_hp=data.get("max_hp", 100),
        x=x,
        y=y,
        is_enemy=data.get("is_enemy", True),
        cycles=cycles_data.get("start", 100),
        max_cycles=cycles_data.get("max", 100),
        mp=mp_data.get("start", 50),
        max_mp=mp_data.get("max", 50),
        equipment=data.get("equipment", {}),
    )


def create_all_npcs(ctx: GameContext) -> list[NPC]:
    """Create all NPC-type entities from entities.json.

    Returns a list of NPC objects (excludes the player entity).
    """
    npc_defs = ctx.entities.where(lambda e: e.get("type") == "npc")
    return [
        entity for d in npc_defs
        if (entity := create_entity(ctx, d["id"])) is not None
    ]


def create_player(ctx: GameContext) -> NPC | None:
    """Create the player entity from entities.json."""
    return create_entity(ctx, "player")


def get_sprite_path(ctx: GameContext, entity_id: str) -> str | None:
    """Look up the sprite asset path for an entity."""
    data = ctx.entities.get_by_id(entity_id)
    if data is None:
        return None
    return data.get("sprite")
