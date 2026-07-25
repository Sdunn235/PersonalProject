"""session.py — WorldSession: the runtime object graph as data (Stage 4.6R / R1).

`WorldSession` owns the ~dozen live objects that used to be loose locals inside
`main()`: the world sim, the map/sources, the player + its needs/controller, the
NPC (entity, controller) pairs, the defeated/cooldown bookkeeping, and the item +
chest services. It is deliberately **pygame-free** — no sprites, no screen, no
rendering — so a future headless `SimulationKernel` (R2) can own and step it with
no display attached. The presentation shell keeps its own sprite-per-entity layer.

`new_game()` is a Factory that reuses the existing `bootstrap.create_*` primitives
verbatim (no new creation logic). `apply_save()` is the load adapter that folds the
apply-save + item-rebuild + chest-rebuild + chest-placement sequence into one call.
`GameContext` (the service locator) stays separate and is passed in where needed.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from Mechanics.bootstrap import (
    create_world_sim, create_needs, create_npc_controller,
    create_item_services, create_chest_registry, rebuild_item_services,
    rebuild_chest_registry, apply_save as _apply_world_save,
)
from Mechanics.entities.factory import create_player, create_all_npcs
from Mechanics.ai.player import PlayerController
from Mechanics.ai.npc_logger import log_spatial_zone
from Mechanics.ai.zone_ai import ZoneAIResponder


@dataclass
class WorldSession:
    """The live simulation object graph (pygame-free)."""

    world_sim: object
    sources: list
    tile_map: object
    player: object
    player_needs: list
    player_controller: object
    npc_list: list                     # [(entity, controller)]
    inv_svc: object
    equip_svc: object
    chest_reg: dict
    defeated_npcs: set = field(default_factory=set)
    combat_cooldowns: dict = field(default_factory=dict)
    zone_ai: object = None   # ZoneAIResponder — sim-side zone behavior (R3)

    @property
    def npc_controllers(self) -> list:
        """The NPC controllers alone — the shape SaveManager/apply_save expect."""
        return [ctrl for _, ctrl in self.npc_list]

    # ── zone observers (R3) ─────────────────────────────────────────────────────
    def wire_zone_observers(self) -> None:
        """Subscribe the SIM-side zone observers (logging + AI behavior) on the
        current world_sim.zone_tracker. Called by new_game() so a fresh tracker
        always gets them — this makes the New-Game re-subscribe fix (C0026)
        automatic. The player zone-flash is NOT wired here: the kernel surfaces it
        as a SimFrame event for the shell (Model/View split)."""
        self.world_sim.zone_tracker.subscribe(log_spatial_zone)
        self.world_sim.zone_tracker.subscribe(self._dispatch_zone_ai)

    def _dispatch_zone_ai(self, event) -> None:
        """Resolve a zone-crossing event's entity to (entity, controller) and let
        the ZoneAIResponder react. Skips defeated NPCs."""
        entity = ctrl = None
        for npc, c in self.npc_list:
            if npc.name == event.entity_name and npc.entity_id not in self.defeated_npcs:
                entity, ctrl = npc, c
                break
        if entity is None and self.player.name == event.entity_name:
            entity, ctrl = self.player, self.player_controller
        if entity is not None and ctrl is not None:
            self.zone_ai.on_zone_cross(event, entity, ctrl)

    # ── Factory ───────────────────────────────────────────────────────────────
    @classmethod
    def new_game(cls, ctx, tile_map, sources) -> "WorldSession":
        """Fresh session: fresh world_sim, entities, controllers, item + chest
        services, and chest placement. Reuses the bootstrap `create_*` primitives
        verbatim. Mirrors main.py's old `_spawn_entities()` + item/chest setup,
        minus all pygame/sprite construction (that lives in the shell)."""
        world_sim = create_world_sim(sources)

        npc_list = []
        for npc in create_all_npcs(ctx):
            ctrl = create_npc_controller(npc, ctx, sources, tile_map,
                                         world_sim=world_sim)
            npc_list.append((npc, ctrl))

        player = create_player(ctx)
        player_needs = create_needs(ctx)
        player_controller = PlayerController(player, tile_map=tile_map,
                                             needs=player_needs, sources=sources)

        inv_svc, equip_svc = create_item_services(ctx)
        chest_reg = create_chest_registry(ctx)
        tile_map.place_chests(chest_reg)

        session = cls(
            world_sim=world_sim, sources=sources, tile_map=tile_map,
            player=player, player_needs=player_needs,
            player_controller=player_controller, npc_list=npc_list,
            inv_svc=inv_svc, equip_svc=equip_svc, chest_reg=chest_reg,
            zone_ai=ZoneAIResponder(),
        )
        session.wire_zone_observers()
        return session

    # ── Load adapter ───────────────────────────────────────────────────────────
    def apply_save(self, save_data, ctx) -> None:
        """Patch this session in place from restore() data: sim/entity state via
        bootstrap.apply_save, item services + chest registry rebuilt, chests
        re-placed. Mirrors main.py's old load block (minus sprite kills, which
        stay in the shell)."""
        _apply_world_save(save_data, self.world_sim, self.sources,
                          self.npc_controllers, self.player, self.player_needs,
                          self.defeated_npcs, self.combat_cooldowns)
        rebuild_item_services(save_data, self.inv_svc, self.equip_svc, ctx.item_repo)
        self.chest_reg = rebuild_chest_registry(save_data, ctx.chests, ctx.item_repo)
        self.tile_map.place_chests(self.chest_reg)
