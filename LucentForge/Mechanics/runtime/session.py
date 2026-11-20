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

**Panels (Arc B, LF-010).** Entities are panel-local (`panel_x`/`panel_y`, default the home panel).
`panel_maps` holds one live `TileMap` per visited panel, loaded on first entry. `tile_map` is the map
of the panel the *player* is on (what the shell draws). NPCs keep their own controller's map, so the
panel the player leaves keeps simulating (§R6 BACKGROUND). `enter_panel()` moves the player.
"""
from __future__ import annotations

from dataclasses import dataclass, field

HOME_PANEL = (0, 0)          # where a new game starts and every NPC lives today (§R8: no migration yet)

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
    panel_maps: dict = field(default_factory=dict)       # (panel_x, panel_y) -> live TileMap
    _panel_sources: dict = field(default_factory=dict)   # (panel_x, panel_y) -> [NeedSource] (non-home)

    # ── panels (Arc B) ──────────────────────────────────────────────────────────
    @staticmethod
    def panel_of(entity) -> tuple[int, int]:
        return (getattr(entity, "panel_x", HOME_PANEL[0]), getattr(entity, "panel_y", HOME_PANEL[1]))

    @property
    def player_panel(self) -> tuple[int, int]:
        return self.panel_of(self.player)

    def map_for(self, panel: tuple[int, int]):
        """The live TileMap of `panel`, loaded from panel data on first use, chests stamped."""
        if panel not in self.panel_maps:
            from Mechanics.world.tile_map import TileMap
            tm = TileMap()
            tm.load_real_map(*panel)
            tm.place_chests(self.chests_on(panel))
            self.panel_maps[panel] = tm
        return self.panel_maps[panel]

    def sources_on(self, panel: tuple[int, int]) -> list:
        """Need sources of `panel`. The home panel's are the world-sim's tracked sources."""
        if panel == HOME_PANEL:
            return self.sources
        if panel not in self._panel_sources:
            self._panel_sources[panel] = self.map_for(panel).get_need_sources()
        return self._panel_sources[panel]

    def chests_on(self, panel: tuple[int, int]) -> dict:
        return {cid: c for cid, c in self.chest_reg.items()
                if (getattr(c, "panel_x", 0), getattr(c, "panel_y", 0)) == panel}

    def enter_panel(self, panel: tuple[int, int], ctx=None) -> None:
        """Put the player on `panel`: its map becomes the world the player walks and the shell draws."""
        self.player.panel_x, self.player.panel_y = panel
        self.tile_map = self.map_for(panel)
        self.player_controller.tile_map = self.tile_map
        self.player_controller.sources = self.sources_on(panel)
        if ctx is not None:
            ctx.current_panel = panel

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
        tile_map.place_chests({cid: c for cid, c in chest_reg.items()
                               if (c.panel_x, c.panel_y) == HOME_PANEL})

        session = cls(
            world_sim=world_sim, sources=sources, tile_map=tile_map,
            player=player, player_needs=player_needs,
            player_controller=player_controller, npc_list=npc_list,
            inv_svc=inv_svc, equip_svc=equip_svc, chest_reg=chest_reg,
            zone_ai=ZoneAIResponder(),
            panel_maps={HOME_PANEL: tile_map},
        )
        for npc, _ctrl in npc_list:
            npc.panel_x, npc.panel_y = HOME_PANEL
        player.panel_x, player.panel_y = HOME_PANEL
        session.wire_zone_observers()
        return session

    # ── Load adapter ───────────────────────────────────────────────────────────
    def apply_save(self, save_data, ctx, verbose: bool = True) -> None:
        """Patch this session in place from restore() data: sim/entity state via
        bootstrap.apply_save, item services + chest registry rebuilt, chests
        re-placed. Mirrors main.py's old load block (minus sprite kills, which
        stay in the shell). verbose=False silences the [SAVE] print (rewind ring)."""
        _apply_world_save(save_data, self.world_sim, self.sources,
                          self.npc_controllers, self.player, self.player_needs,
                          self.defeated_npcs, self.combat_cooldowns, verbose=verbose)
        rebuild_item_services(save_data, self.inv_svc, self.equip_svc, ctx.item_repo)
        self.chest_reg = rebuild_chest_registry(save_data, ctx.chests, ctx.item_repo)
        for panel, tm in self.panel_maps.items():
            tm.place_chests(self.chests_on(panel))
        # Arc B: put every entity back on the panel it was saved on (older saves: the home panel).
        saved = save_data.get("entities", {})
        for ent in [npc for npc, _ in self.npc_list] + [self.player]:
            e = saved.get(ent.entity_id, {})
            ent.panel_x, ent.panel_y = e.get("panel_x", HOME_PANEL[0]), e.get("panel_y", HOME_PANEL[1])
        self.enter_panel(self.player_panel, ctx)
