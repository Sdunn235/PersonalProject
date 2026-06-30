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
from Mechanics.world.goblin_threat import ThreatStage
from Mechanics.world.town import TownState
from Mechanics.ai.memory import SourceMemory


def create_game_context(data_dir: str | None = None,
                        db_path: str | None = None) -> GameContext:
    """Create the single GameContext owning all DAOs."""
    return GameContext(data_dir, db_path=db_path)


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


def apply_save(
    save_data: dict,
    world_sim: WorldSim,
    sources: list,
    controllers: list,
    player,
    player_needs: list,
    defeated_npcs: set,
    combat_cooldowns: dict,
) -> None:
    """Patch live game objects with data restored from a save slot.

    All collections are mutated in place so the caller's references stay valid.
    NPCs drop to IDLE on load — the AI re-evaluates within 1-2 seconds.
    """
    # Restore world sim
    w = save_data["world"]
    world_sim.clock.tick_count  = w["tick_count"]
    world_sim.clock._accumulator = w["accumulator"]
    world_sim.threat.threat_level = w["threat_level"]
    world_sim.threat._prev_stage  = ThreatStage[w["prev_stage"]]
    world_sim.town.state          = TownState[w["town_state"]]

    # Restore source stocks
    saved_stocks = save_data["sources"]
    for src in sources:
        if src.label in saved_stocks:
            src.stock = saved_stocks[src.label]

    # Build NPC lookup
    ctrl_by_id = {ctrl.npc.entity_id: ctrl for ctrl in controllers}
    entity_data = save_data["entities"]

    # Restore NPC entities
    for entity_id, edata in entity_data.items():
        if edata["ai_state"] == "PLAYER":
            continue

        ctrl = ctrl_by_id.get(entity_id)
        if ctrl is None:
            continue

        npc = ctrl.npc
        npc.hp = edata["hp"]
        npc.x  = edata["x"]
        npc.y  = edata["y"]
        if hasattr(npc, "cycles"):
            npc.cycles = edata["cycles"]
        if hasattr(npc, "mp"):
            npc.mp = edata["mp"]
        if hasattr(npc, "equipment"):
            npc.equipment = edata["equipment"]

        # Needs
        needs_map = {n.need_id: n for n in ctrl.needs}
        for need_id, value in edata["needs"].items():
            if need_id in needs_map:
                needs_map[need_id].current_value = float(value)

        # Traits (brain.traits IS npc.traits — same object; update once)
        for axis, val in edata["traits"].items():
            if hasattr(ctrl.brain.traits, axis):
                setattr(ctrl.brain.traits, axis, float(val))

        # Chemicals
        for key, val in edata["chemicals"].items():
            ctrl.brain.chemicals.set(key, float(val))

        # Memory
        ctrl.memory._sources.clear()
        for label, mem_entry in edata["memory"].items():
            ctrl.memory._sources[label] = SourceMemory(
                source_label=label,
                need_id=mem_entry["need_id"],
                visit_count=mem_entry["visit_count"],
                avg_satisfaction=float(mem_entry["avg_satisfaction"]),
                last_visit_tick=mem_entry["last_visit_tick"],
            )

    # Restore player entity
    if player.entity_id in entity_data:
        pdata = entity_data[player.entity_id]
        player.hp = pdata["hp"]
        player.x  = pdata["x"]
        player.y  = pdata["y"]
        if hasattr(player, "cycles"):
            player.cycles = pdata["cycles"]
        if hasattr(player, "mp"):
            player.mp = pdata["mp"]

        needs_map = {n.need_id: n for n in player_needs}
        for need_id, value in pdata["needs"].items():
            if need_id in needs_map:
                needs_map[need_id].current_value = float(value)

    # Restore game tracking (mutate in place so caller references stay valid)
    gdata = save_data["game"]
    defeated_npcs.clear()
    defeated_npcs.update(gdata["defeated_npcs"])
    combat_cooldowns.clear()
    combat_cooldowns.update(gdata["combat_cooldowns"])

    print(
        f"[SAVE] Restored tick={world_sim.clock.tick_count} "
        f"threat={world_sim.threat.threat_level:.1f} "
        f"defeated={len(defeated_npcs)}"
    )


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
