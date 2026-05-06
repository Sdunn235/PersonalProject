# bootstrap.py — Composition root: wires up all game systems via DI
from __future__ import annotations
from Mechanics.data.context import GameContext
from Mechanics.combat.turn_processor import TurnProcessor
from Mechanics.combat.rng import SimpleRng
from Mechanics.needs.need import make_default_needs
from Mechanics.needs.need_factory import NeedFactory
from Mechanics.needs.need_source import NeedSource, make_default_sources
from Mechanics.biochem.brain import Brain
from Mechanics.entities.factory import create_player, create_all_npcs, get_sprite_path
from Mechanics.ai.controller import NPCController
from Mechanics.ai.behavior import HumanBehavior, GoblinBehavior
from Mechanics.world.tile_map import TileMap
from Mechanics.world.world_sim import WorldSim


def create_game_context(data_dir: str | None = None) -> GameContext:
    """Create the single GameContext owning all DAOs."""
    return GameContext(data_dir)


def create_combat_service() -> TurnProcessor:
    """Create the combat turn processor."""
    return TurnProcessor()


def create_rng() -> SimpleRng:
    """Create the RNG instance."""
    return SimpleRng()


def create_needs(ctx: GameContext) -> list:
    """Create needs from JSON data."""
    factory = NeedFactory(ctx)
    needs = factory.create_all()
    return needs if needs else make_default_needs()


def create_world_sim(sources: list | None = None) -> WorldSim:
    """Create the world-level simulation orchestrator.

    H5: accepts sources list so ResourceState can aggregate real stocks.
    """
    return WorldSim(sources)


def create_npc_controller(npc, ctx: GameContext,
                          sources: list[NeedSource],
                          tile_map: TileMap,
                          world_sim: WorldSim | None = None) -> NPCController:
    """Create an NPCController fully wired with needs, brain, sources.

    Goblins get GoblinBehavior (threat-driven), others get HumanBehavior.
    """
    needs = create_needs(ctx)
    brain = Brain(npc.traits)
    if npc.subtype == "goblin" and world_sim is not None:
        behavior = GoblinBehavior(world_sim.threat)
    else:
        behavior = HumanBehavior()
    return NPCController(npc, needs, brain, sources, tile_map,
                          behavior=behavior)
