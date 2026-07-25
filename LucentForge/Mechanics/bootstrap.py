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
from Mechanics.ai.memory import SourceMemory, RegionComfortMemory


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
        if hasattr(npc, "byte_pool"):
            npc.byte_pool = edata.get("byte_pool", edata.get("mp", npc.byte_pool))
            _bp = edata.get("bit_pool")
            npc.bit_pool = _bp if _bp else npc.max_bit_pool  # legacy save -> full
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

        # Memory — nested {sources, regions} blob. Legacy saves are the flat
        # sources dict; detect and upgrade (source labels are uppercase and
        # never collide with the "sources"/"regions" wrapper keys).
        ctrl.memory._sources.clear()
        ctrl.memory._regions.clear()
        mem_blob = edata["memory"]
        if "sources" in mem_blob or "regions" in mem_blob:
            sources_blob = mem_blob.get("sources", {})
            regions_blob = mem_blob.get("regions", {})
        else:  # legacy flat format (pre-C0049 saves)
            sources_blob = mem_blob
            regions_blob = {}
        for label, mem_entry in sources_blob.items():
            ctrl.memory._sources[label] = SourceMemory(
                source_label=label,
                need_id=mem_entry["need_id"],
                visit_count=mem_entry["visit_count"],
                avg_satisfaction=float(mem_entry["avg_satisfaction"]),
                last_visit_tick=mem_entry["last_visit_tick"],
            )
        for rid, reg_entry in regions_blob.items():
            ctrl.memory._regions[rid] = RegionComfortMemory(
                region_id=rid,
                avg_comfort=float(reg_entry["avg_comfort"]),
                visit_count=reg_entry["visit_count"],
                last_visit_tick=reg_entry["last_visit_tick"],
            )

    # Restore player entity
    if player.entity_id in entity_data:
        pdata = entity_data[player.entity_id]
        player.hp = pdata["hp"]
        player.x  = pdata["x"]
        player.y  = pdata["y"]
        if hasattr(player, "cycles"):
            player.cycles = pdata["cycles"]
        if hasattr(player, "byte_pool"):
            player.byte_pool = pdata.get("byte_pool", pdata.get("mp", player.byte_pool))
            _pbp = pdata.get("bit_pool")
            player.bit_pool = _pbp if _pbp else player.max_bit_pool

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
                          behavior=behavior, rooms=ctx.rooms)


def create_item_services(ctx: GameContext):
    """Seed InventoryService + EquipmentService from entities.json starting kits.
    For the save-load path, call rebuild_item_services() after apply_save() instead.
    Returns (InventoryService, EquipmentService).
    """
    from Mechanics.services.inventory_service import InventoryService
    from Mechanics.services.equipment_service import EquipmentService
    from Mechanics.items.containers import Inventory, EquipmentSet, ItemStack

    inv_svc   = InventoryService()
    equip_svc = EquipmentService(ctx.item_repo)

    for entity_def in ctx.entities.get_all():
        entity_id = entity_def["id"]
        stacks = [
            ItemStack(item, entry.get("qty", 1))
            for entry in entity_def.get("bag", [])
            if (item := ctx.item_repo.find_by_id(entry["item_id"]))
        ]
        inv_svc.register(entity_id, Inventory(entity_id, stacks))

        equip_set = EquipmentSet(entity_id)
        for slot_name, item_id in entity_def.get("equipment", {}).items():
            item = ctx.item_repo.find_by_id(item_id)
            if item:
                equip_set.put_slot(slot_name, item)
        equip_svc.register(entity_id, equip_set)

    return inv_svc, equip_svc


def create_chest_registry(ctx: GameContext) -> dict:
    """New-game: build chest_reg from chest_content with fresh loot."""
    from Mechanics.items.containers import Chest, ItemStack
    from Mechanics.items.enums import TrapType

    chest_reg = {}
    for cdef in ctx.chests.get_all():
        loot_stacks = [
            ItemStack(item, e.get("qty", 1))
            for e in cdef.get("loot", [])
            if (item := ctx.item_repo.find_by_id(e["item_id"]))
        ]
        chest = Chest(
            id=cdef["id"],
            col=cdef["col"],
            row=cdef["row"],
            locked=cdef.get("locked", False),
            lock_dc=cdef.get("lock_dc", 0),
            required_key_id=cdef.get("required_key_id"),
            is_trapped=cdef.get("is_trapped", False),
            trap_type=TrapType(cdef.get("trap_type", 0)),
            trap_damage=cdef.get("trap_damage", 0),
            is_opened=False,
            contents=loot_stacks,
        )
        chest_reg[chest.id] = chest
    return chest_reg


def rebuild_chest_registry(save_data: dict, ctx_chests, item_repo) -> dict:
    """Load: restore chest_reg from save_data['chests'] + chest_content definitions."""
    from Mechanics.items.containers import Chest, ItemStack
    from Mechanics.items.enums import TrapType

    saved_chests = save_data.get("chests", {})
    chest_reg = {}
    for cdef in ctx_chests.get_all():
        cid = cdef["id"]
        if cid in saved_chests:
            sc = saved_chests[cid]
            contents = [
                ItemStack(item, e.get("qty", 1))
                for e in sc.get("contents", [])
                if (item := item_repo.find_by_id(e["item_id"]))
            ]
            chest = Chest(
                id=cid,
                col=cdef["col"],
                row=cdef["row"],
                locked=cdef.get("locked", False),
                lock_dc=cdef.get("lock_dc", 0),
                required_key_id=cdef.get("required_key_id"),
                is_trapped=cdef.get("is_trapped", False),
                trap_type=TrapType(cdef.get("trap_type", 0)),
                trap_damage=cdef.get("trap_damage", 0),
                is_opened=sc.get("is_opened", False),
                contents=contents,
            )
        else:
            loot_stacks = [
                ItemStack(item, e.get("qty", 1))
                for e in cdef.get("loot", [])
                if (item := item_repo.find_by_id(e["item_id"]))
            ]
            chest = Chest(
                id=cid,
                col=cdef["col"],
                row=cdef["row"],
                locked=cdef.get("locked", False),
                lock_dc=cdef.get("lock_dc", 0),
                required_key_id=cdef.get("required_key_id"),
                is_trapped=cdef.get("is_trapped", False),
                trap_type=TrapType(cdef.get("trap_type", 0)),
                trap_damage=cdef.get("trap_damage", 0),
                is_opened=False,
                contents=loot_stacks,
            )
        chest_reg[cid] = chest
    return chest_reg


def rebuild_item_services(save_data: dict, inv_svc, equip_svc, item_repo) -> None:
    """Rebuild InventoryService + EquipmentService from a restored save dict.
    Call immediately after apply_save() on the load path.
    """
    from Mechanics.items.containers import Inventory, EquipmentSet, ItemStack

    for entity_id, edata in save_data["entities"].items():
        stacks = [
            ItemStack(item, e.get("qty", 1))
            for e in edata.get("bag", [])
            if (item := item_repo.find_by_id(e["item_id"]))
        ]
        inv_svc.register(entity_id, Inventory(entity_id, stacks))

        equip_set = EquipmentSet(entity_id)
        for slot_name, item_id in edata.get("equipment", {}).items():
            item = item_repo.find_by_id(item_id)
            if item:
                equip_set.put_slot(slot_name, item)
        equip_svc.register(entity_id, equip_set)
