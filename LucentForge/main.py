# main.py — LucentForge PyGame prototype entry point
# Run: python main.py
import sys
import os
import math

# Ensure project root is on the path
sys.path.insert(0, os.path.dirname(__file__))

# noinspection PyPackageRequirements
import pygame
import settings

from Mechanics.bootstrap import create_game_context
from Mechanics.runtime.session import WorldSession
from Mechanics.renderer.save_menu import run_load_menu, run_save_menu
from Mechanics.renderer.pause_menu import run_pause_menu
from Mechanics.entities.factory import get_sprite_path
from Mechanics.needs.needs_system import apply_health_drain, apply_regen, update_needs
from Mechanics.world.tile_map import TileMap
from Mechanics.world.world_coord import PanelEdge
from Mechanics.renderer.sprite import EntitySprite
from Mechanics.renderer.hud import draw_hud
from Mechanics.renderer.trap_overlay import draw_trap_markers
from Mechanics.renderer.health_bar import draw_stat_bar
from Mechanics.services.perception import perceive_traps
from Mechanics.combat.casting import convert_amount
from Mechanics.renderer.observation_panel import draw_observation_panel
from Mechanics.observation.run_logger import RunLogger
from Mechanics.renderer.combat_scene import run_combat
from Mechanics.ai.proximity import update_proximity_fear
from Mechanics.ai.npc_logger import log_spatial_zone
from Mechanics.ai.zone_ai import ZoneAIResponder

COMBAT_TRIGGER_DIST = settings.TILE_SIZE * 1.2


def main():
    pygame.init()
    screen = pygame.display.set_mode((settings.WINDOW_W, settings.WINDOW_H))
    pygame.display.set_caption("LucentForge — NPC Needs Prototype")
    clock = pygame.time.Clock()
    font  = pygame.font.SysFont(None, 16)

    print("=" * 60)
    print("LucentForge — NPC Needs & Biochem Prototype")
    print(f"Sim day = {settings.SIM_DAY_SECONDS}s  |  FPS={settings.FPS}")
    print(f"Decay rates:  HUNGER={settings.HUNGER_DECAY_RATE:.5f}/tick  "
          f"THIRST={settings.THIRST_DECAY_RATE:.5f}/tick  "
          f"SLEEP={settings.SLEEP_DECAY_RATE:.5f}/tick")
    print("=" * 60)

    # --- Composition root: wire everything via bootstrap ---
    ctx = create_game_context()

    # --- World setup (sources first — H5 needs them for ResourceState) ---
    tile_map = TileMap()
    tile_map.load_real_map()
    sources  = tile_map.get_need_sources()

    # --- Presentation sprite layer (proto-shell; R4 formalizes into the shell) ---
    # The WorldSession is pygame-free — sprites live here, keyed by entity_id.
    def _build_sprites(sess):
        _sprites = {}
        for _npc, _ in sess.npc_list:
            _sprites[_npc.entity_id] = EntitySprite(
                _npc, image_path=get_sprite_path(ctx, _npc.entity_id),
                size=settings.TILE_SIZE - 2)
            print(f"[SPAWN] {_npc.name} at ({int(_npc.x)}, {int(_npc.y)})")
        _sprites[sess.player.entity_id] = EntitySprite(
            sess.player, image_path=get_sprite_path(ctx, sess.player.entity_id),
            size=settings.TILE_SIZE - 2)
        print(f"[SPAWN] Player at ({int(sess.player.x)}, {int(sess.player.y)})  "
              f"[Arrow keys to move]")
        _group = pygame.sprite.Group(*_sprites.values())
        return _sprites, _group

    # --- Build the fresh session + its sprite layer ---
    session = WorldSession.new_game(ctx, tile_map, sources)
    sprites, sprite_group = _build_sprites(session)

    print(f"\n[WORLD SIM] Heartbeat-1 active | "
          f"Food={session.world_sim.resources.food_total:.0f} | "
          f"Threat={session.world_sim.threat.threat_level:.0f} | "
          f"Town={session.world_sim.town.state.value}")
    print("[MAP] Heartbeat-2 active | River barrier, region zones, bridge crossings")
    # Phase 3.4: player room-name flash — fires when player crosses a room boundary.
    # zone_flash[0] = (room_name, frames_remaining) | None
    zone_flash: list = [None]

    def _on_player_zone_cross(event) -> None:
        if event.entity_name == session.player.name:
            room_name = event.to_room.name if event.to_room else "Unknown"
            zone_flash[0] = (room_name, settings.ZONE_LABEL_DURATION)

    # Phase 3.5: zone-entry AI behavioral triggers.
    zone_ai = ZoneAIResponder()

    def _zone_ai_event(event) -> None:
        entity = ctrl = None
        for npc, c in session.npc_list:
            if npc.name == event.entity_name and npc.entity_id not in session.defeated_npcs:
                entity, ctrl = npc, c
                break
        if entity is None and session.player.name == event.entity_name:
            entity, ctrl = session.player, session.player_controller
        if entity is not None and ctrl is not None:
            zone_ai.on_zone_cross(event, entity, ctrl)

    def _register_zone_subscribers() -> None:
        """Re-subscribe all ZoneTracker observers on the current world_sim.zone_tracker.
        Called at startup and on New Game so a fresh tracker gets all callbacks."""
        zone_flash[0] = None
        session.world_sim.zone_tracker.subscribe(log_spatial_zone)
        session.world_sim.zone_tracker.subscribe(_on_player_zone_cross)
        session.world_sim.zone_tracker.subscribe(_zone_ai_event)

    _register_zone_subscribers()

    print("[H4] Goblin behavior active | Hunger-driven threat, patrol/raid states, proximity fear")
    finite_sources = [s for s in session.sources if s.is_finite]
    print(f"[H5] Resource economy active | {len(finite_sources)} finite sources: "
          + ", ".join(f"{s.label}({s.stock:.0f}/{s.capacity:.0f})" for s in finite_sources))
    print()

    # --- Phase 1.6: launch slot-picker — always shown so New Game is reachable ---
    _chosen_slot = run_load_menu(screen, clock, ctx, font)
    if _chosen_slot is not None:
        _save_data = ctx.save_manager.restore(slot_id=_chosen_slot)
        if _save_data:
            session.apply_save(_save_data, ctx)
            for _npc, _ in session.npc_list:
                if _npc.entity_id in session.defeated_npcs:
                    sprites[_npc.entity_id].kill()
            print(f"[SAVE] Session resumed from slot {_chosen_slot}.")
        else:
            print(f"[SAVE] Slot {_chosen_slot} empty — starting fresh.")
    else:
        print("[SAVE] New Game — starting fresh.")

    # Heartbeat-6: per-run CSV log + emergence summary
    run_logger = RunLogger(settings.RUN_LOG_DIR)

    # --- Source label font ---
    label_font = pygame.font.SysFont(None, 18)

    # --- HUD cycle state (Tab key) ---
    _hud_subjects = [
        (session.player, None, "Player"),
    ] + [
        (npc, ctrl, None) for npc, ctrl in session.npc_list
    ]
    hud_index = 0
    obs_visible = True   # Heartbeat-6 observation panel (toggle with 'O')

    # --- Game loop ---
    running         = True
    in_combat       = False
    COMBAT_COOLDOWN = 4.0
    _paused_quit    = False
    _last_at_edge: PanelEdge | None = None   # Phase 3.6: edge-triggered panel detection

    while running:
        dt = clock.tick(settings.FPS) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    _result = run_pause_menu(
                        screen, clock, ctx, font,
                        session.world_sim, session.sources, session.npc_controllers,
                        session.player, session.player_needs, session.defeated_npcs,
                        session.combat_cooldowns,
                        inv_svc=session.inv_svc, equip_svc=session.equip_svc,
                        chest_reg=session.chest_reg,
                    )
                    if _result == "quit":
                        _paused_quit = True
                        running = False
                    elif _result == "new_game":
                        session = WorldSession.new_game(ctx, tile_map, sources)
                        sprites, sprite_group = _build_sprites(session)
                        _register_zone_subscribers()
                        _last_at_edge = None
                        _hud_subjects = [(session.player, None, "Player")] + [
                            (npc, ctrl, None) for npc, ctrl in session.npc_list
                        ]
                        hud_index = 0
                        run_logger = RunLogger(settings.RUN_LOG_DIR)
                    elif _result.startswith("load:"):
                        _slot_id = int(_result.split(":")[1])
                        _save_data = ctx.save_manager.restore(slot_id=_slot_id)
                        if _save_data:
                            for _npc, _ in session.npc_list:
                                sprite_group.add(sprites[_npc.entity_id])
                            session.apply_save(_save_data, ctx)
                            for _npc, _ in session.npc_list:
                                if _npc.entity_id in session.defeated_npcs:
                                    sprites[_npc.entity_id].kill()
                            print(f"[SAVE] Session resumed from slot {_slot_id}.")
                    # else "resume" — continue
                elif event.key == pygame.K_TAB:
                    hud_index = (hud_index + 1) % len(_hud_subjects)
                elif event.key == pygame.K_i:
                    from Mechanics.renderer.inventory_menu import run_inventory_menu
                    run_inventory_menu(screen, clock, ctx, font,
                                       session.inv_svc, session.equip_svc, session.player)
                elif event.key == pygame.K_o:
                    obs_visible = not obs_visible
                elif event.key == pygame.K_s:
                    _slot = run_save_menu(screen, clock, ctx, font)
                    if _slot is not None:
                        ctx.save_manager.snapshot_session(session, slot_id=_slot)
                elif event.key == pygame.K_e:
                    pcol = int(session.player.x // settings.TILE_SIZE)
                    prow = int(session.player.y // settings.TILE_SIZE)
                    _adj_chest = None
                    for _dc, _dr in ((0, -1), (0, 1), (-1, 0), (1, 0)):
                        _adj_chest = next(
                            (c for c in session.chest_reg.values()
                             if c.col == pcol + _dc and c.row == prow + _dr),
                            None,
                        )
                        if _adj_chest:
                            break
                    if _adj_chest:
                        from Mechanics.renderer.chest_menu import run_chest_menu
                        from Mechanics.services.outcome import OutcomeResolver
                        run_chest_menu(screen, clock, font, _adj_chest, session.player,
                                       session.inv_svc, session.equip_svc, ctx.item_repo,
                                       OutcomeResolver())
                elif event.key == pygame.K_c:
                    # Phase 4.5b: reliable out-of-combat Bits->Bytes conversion (§M4).
                    # Rest structures all available Bits into Bytes (fills the Byte pool).
                    _player = session.player
                    _b, _byt, _g = convert_amount(_player.bit_pool, _player.byte_pool,
                                                  _player.max_byte_pool, _player.bit_pool)
                    if _g > 0:
                        _player.bit_pool, _player.byte_pool = _b, _byt
                        print(f"[CONVERT] {_g * 8} Bits -> {_g} Bytes  "
                              f"(BP {_b}/{_player.max_bit_pool}, BYP {_byt}/{_player.max_byte_pool})")

        if not in_combat:
            # --- World simulation tick ---
            living_count = len(session.npc_list) - len(session.defeated_npcs)

            # Compute average goblin hunger for threat escalation (H4)
            goblin_hungers = []
            for npc_e, npc_c in session.npc_list:
                if (npc_e.entity_id not in session.defeated_npcs
                        and npc_e.subtype == "goblin"):
                    h = next((n for n in npc_c.needs
                              if n.need_id == "hunger"), None)
                    if h:
                        goblin_hungers.append(h.current_value / 100.0)
            avg_goblin_hunger = (sum(goblin_hungers) / len(goblin_hungers)
                                 if goblin_hungers else 1.0)

            sim_ticks = session.world_sim.tick(dt, living_count, avg_goblin_hunger)
            if sim_ticks > 0 and session.world_sim.clock.tick_count % 30 == 0:
                print(session.world_sim.status_line())

            # Phase 3.3: zone crossing detection (player + all living NPCs)
            if sim_ticks > 0:
                _zone_entities = (
                    [e for e, _ in session.npc_list if e.entity_id not in session.defeated_npcs]
                    + [session.player]
                )
                session.world_sim.zone_tracker.check_and_fire(
                    _zone_entities, tile_map, ctx.rooms,
                    ctx.current_panel[0], ctx.current_panel[1],
                    session.world_sim.clock.tick_count,
                )

            # Phase 1.5: periodic autosave
            if (sim_ticks > 0
                    and settings.AUTOSAVE_INTERVAL > 0
                    and session.world_sim.clock.tick_count % settings.AUTOSAVE_INTERVAL == 0):
                ctx.save_manager.snapshot_session(session)

            # Heartbeat-6: sample world + NPC state to the run-log
            if (sim_ticks > 0
                    and session.world_sim.clock.tick_count % settings.RUN_LOG_INTERVAL == 0):
                run_logger.sample(session.world_sim, session.sources, session.npc_list,
                                  session.defeated_npcs, session.world_sim.clock.tick_count)

            def _grid(entity):
                return tile_map.world_to_grid(entity.x, entity.y)

            all_entities = (
                [e for e, _ in session.npc_list if e.entity_id not in session.defeated_npcs]
                + [session.player]
            )
            occupied_by: dict[str, tuple[int, int]] = {
                e.entity_id: _grid(e) for e in all_entities
            }

            # Proximity fear + contested sources (H4)
            contested = update_proximity_fear(session.npc_list, session.defeated_npcs)

            for npc_entity, npc_ctrl in session.npc_list:
                if npc_entity.entity_id not in session.defeated_npcs:
                    others = {
                        pos for eid, pos in occupied_by.items()
                        if eid != npc_entity.entity_id
                    }
                    npc_ctrl.contested_sources = contested
                    npc_ctrl.update(dt, occupied_tiles=others)
                    apply_health_drain(npc_ctrl.needs, npc_entity, dt)
                    apply_regen(npc_ctrl.needs, npc_entity, dt)
                    npc_entity.update(dt)

            session.player_controller.update(dt)
            session.player.update(dt)
            update_needs(session.player_needs)
            apply_health_drain(session.player_needs, session.player, dt)
            apply_regen(session.player_needs, session.player, dt)
            sprite_group.update()

            # Phase 4.2: passive Intuition trap perception (§M8)
            for _hint in perceive_traps(session.player, session.chest_reg):
                print(_hint)

            # Phase 3.6: panel edge detection — fires once per edge entry (edge-triggered)
            _pcol = int(session.player.x // settings.TILE_SIZE)
            _prow = int(session.player.y // settings.TILE_SIZE)
            _edge_now: PanelEdge | None = None
            if _prow <= 0:
                _edge_now = PanelEdge.NORTH
            elif _prow >= settings.ROWS - 1:
                _edge_now = PanelEdge.SOUTH
            elif _pcol <= 0:
                _edge_now = PanelEdge.WEST
            elif _pcol >= settings.COLS - 1:
                _edge_now = PanelEdge.EAST
            if _edge_now is not None and _edge_now is not _last_at_edge:
                _px, _py = ctx.current_panel
                if not ctx.panel_loader.can_transition(_px, _py, _edge_now):
                    print(f"[PANEL] Player at {_edge_now.value.lower()} edge of "
                          f"Panel({_px},{_py}) — no adjacent panel defined.")
            _last_at_edge = _edge_now

            now = pygame.time.get_ticks() / 1000.0
            for npc_entity, _ in session.npc_list:
                if npc_entity.entity_id in session.defeated_npcs:
                    continue
                since_last = now - session.combat_cooldowns.get(npc_entity.entity_id, -999)
                if since_last < COMBAT_COOLDOWN:
                    continue
                dist = math.hypot(session.player.x - npc_entity.x,
                                  session.player.y - npc_entity.y)
                if dist < COMBAT_TRIGGER_DIST:
                    in_combat = True
                    result = run_combat(screen, clock, font, session.player, npc_entity, ctx,
                                       inv_svc=session.inv_svc, equip_svc=session.equip_svc)
                    in_combat = False
                    session.combat_cooldowns[npc_entity.entity_id] = pygame.time.get_ticks() / 1000.0
                    if result == "win":
                        session.defeated_npcs.add(npc_entity.entity_id)
                        sprites[npc_entity.entity_id].kill()
                        print(f"[COMBAT] Player defeated {npc_entity.name}!")
                    elif result == "lose":
                        print("[COMBAT] Player was defeated — game over.")
                        running = False
                    break

        # Draw
        screen.fill(settings.BG_COLOR)
        tile_map.draw(screen)
        draw_trap_markers(screen, session.chest_reg, font)  # Phase 4.2 (§M8)

        # Zone labels already rendered by tile_map.draw(); skip source labels
        # that duplicate a zone label (FARM overlaps "Farm" zone).
        _zone_label_names = {"FARM"}  # source labels that match zone labels
        for src in session.sources:
            if src.label in _zone_label_names:
                continue
            lbl = label_font.render(f"[{src.label}]", True, (255, 255, 255))
            screen.blit(lbl, (src.world_x + settings.LEVEL_X - lbl.get_width() // 2,
                              src.world_y + settings.LEVEL_Y - lbl.get_height() // 2))

        # H5: source stock bars for finite sources
        for src in session.sources:
            if src.is_finite:
                bar_x = src.world_x + settings.LEVEL_X
                bar_y = src.world_y + settings.LEVEL_Y + settings.SOURCE_BAR_OFFSET_Y
                ratio = src.stock / src.capacity if src.capacity > 0 else 1.0
                color = ((68, 206, 27) if ratio > 0.5
                         else (242, 161, 52) if ratio > 0.15
                         else (229, 31, 31))
                draw_stat_bar(screen, bar_x, bar_y,
                              int(src.stock), int(src.capacity),
                              color, (30, 30, 30),
                              width=settings.SOURCE_BAR_WIDTH,
                              height=settings.SOURCE_BAR_HEIGHT)

        sprite_group.draw(screen)
        for sprite in sprite_group:
            sprite.draw_overlays(screen)

        _e, _ctrl, _lbl = _hud_subjects[hud_index]
        _needs = session.player_needs if _ctrl is None else _ctrl.needs
        _state = _lbl               if _ctrl is None else _ctrl.state
        draw_hud(screen, _e, _needs, _state, font, controller=_ctrl)

        # Heartbeat-6: world-overview observation panel (left margin)
        if obs_visible:
            draw_observation_panel(screen, session.world_sim, session.sources,
                                   session.npc_list, session.defeated_npcs, font,
                                   player=session.player)

        # Phase 3.4: zone-crossing room-name flash (centered above tile map)
        if zone_flash[0] is not None:
            flash_name, flash_frames = zone_flash[0]
            flash_surf = font.render(f"[ {flash_name} ]", True, (220, 210, 255))
            flash_x = settings.LEVEL_X + (settings.LEVEL_W - flash_surf.get_width()) // 2
            flash_y = settings.LEVEL_Y - 18
            screen.blit(flash_surf, (flash_x, flash_y))
            zone_flash[0] = (flash_name, flash_frames - 1) if flash_frames > 1 else None

        # Level border outline
        pygame.draw.rect(screen, (80, 80, 100),
                         pygame.Rect(settings.LEVEL_X - 2, settings.LEVEL_Y - 2,
                                     settings.LEVEL_W + 4, settings.LEVEL_H + 4), 2)

        day = session.world_sim.clock.day
        _player = session.player
        info_txt = font.render(
            f"Day {day:.2f}   HP {_player.hp:.0f}/{_player.max_hp}"
            f"   SP {_player.cycles}/{_player.max_cycles}"
            f"   BP {_player.bit_pool}/{_player.max_bit_pool}"
            f"   BYP {_player.byte_pool}/{_player.max_byte_pool}",
            True, settings.TEXT_COLOR)
        screen.blit(info_txt, (settings.LEVEL_X, 10))

        pygame.display.flip()

    # Phase 1.5: save-on-quit (window-close path only; pause-menu quit saves internally)
    if settings.SAVE_ON_QUIT and not _paused_quit:
        ctx.save_manager.snapshot_session(session)

    run_logger.finalize(session.world_sim, session.npc_list, session.defeated_npcs)
    pygame.quit()
    print("\n[EXIT] Session ended.")


if __name__ == "__main__":
    main()
