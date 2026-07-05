# main.py — LucentForge PyGame prototype entry point
# Run: python main.py
import sys
import os
import math

# Ensure project root is on the path
sys.path.insert(0, os.path.dirname(__file__))

import pygame
import settings

from Mechanics.bootstrap import (create_game_context, create_needs,
                                 create_npc_controller, create_world_sim,
                                 apply_save, create_item_services,
                                 rebuild_item_services)
from Mechanics.renderer.save_menu import run_load_menu, run_save_menu
from Mechanics.renderer.pause_menu import run_pause_menu
from Mechanics.entities.factory import create_player, create_all_npcs, get_sprite_path
from Mechanics.needs.needs_system import apply_health_drain, apply_regen, update_needs
from Mechanics.world.tile_map import TileMap
from Mechanics.ai.player import PlayerController
from Mechanics.renderer.sprite import EntitySprite
from Mechanics.renderer.hud import draw_hud
from Mechanics.renderer.health_bar import draw_stat_bar
from Mechanics.renderer.observation_panel import draw_observation_panel
from Mechanics.observation.run_logger import RunLogger
from Mechanics.renderer.combat_scene import run_combat
from Mechanics.ai.proximity import update_proximity_fear

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
    world_sim = create_world_sim(sources)

    # --- Inner helper: spawn fresh NPCs, player, controllers, sprites ---
    # Closure reads world_sim at call time — rebind world_sim before calling for New Game.
    def _spawn_entities():
        _npc_list = []
        for npc in create_all_npcs(ctx):
            controller = create_npc_controller(npc, ctx, sources, tile_map,
                                               world_sim=world_sim)
            sprite = EntitySprite(npc, image_path=get_sprite_path(ctx, npc.entity_id),
                                  size=settings.TILE_SIZE - 2)
            _npc_list.append((npc, controller, sprite))
            print(f"[SPAWN] {npc.name} at ({int(npc.x)}, {int(npc.y)})")
        _player = create_player(ctx)
        _player_needs = create_needs(ctx)
        _player_ctrl = PlayerController(_player, tile_map=tile_map,
                                        needs=_player_needs, sources=sources)
        _player_sprite = EntitySprite(_player,
                                      image_path=get_sprite_path(ctx, _player.entity_id),
                                      size=settings.TILE_SIZE - 2)
        print(f"[SPAWN] Player at ({int(_player.x)}, {int(_player.y)})  [Arrow keys to move]")
        _defeated: set[str] = set()
        _cooldowns: dict[str, float] = {}
        _ctrls = [ctrl for _, ctrl, _ in _npc_list]
        _group = pygame.sprite.Group(*[s for _, _, s in _npc_list], _player_sprite)
        return (_npc_list, _player, _player_needs, _player_ctrl,
                _player_sprite, _group, _ctrls, _defeated, _cooldowns)

    (npc_list, player, player_needs, player_controller, player_sprite,
     sprite_group, _npc_controllers, defeated_npcs, combat_cooldowns) = _spawn_entities()
    inv_svc, equip_svc = create_item_services(ctx)

    print(f"\n[WORLD SIM] Heartbeat-1 active | "
          f"Food={world_sim.resources.food_total:.0f} | "
          f"Threat={world_sim.threat.threat_level:.0f} | "
          f"Town={world_sim.town.state.value}")
    print("[MAP] Heartbeat-2 active | River barrier, region zones, bridge crossings")
    print("[H4] Goblin behavior active | Hunger-driven threat, patrol/raid states, proximity fear")
    finite_sources = [s for s in sources if s.is_finite]
    print(f"[H5] Resource economy active | {len(finite_sources)} finite sources: "
          + ", ".join(f"{s.label}({s.stock:.0f}/{s.capacity:.0f})" for s in finite_sources))
    print()

    # --- Phase 1.6: launch slot-picker — always shown so New Game is reachable ---
    _chosen_slot = run_load_menu(screen, clock, ctx, font)
    if _chosen_slot is not None:
        _save_data = ctx.save_manager.restore(slot_id=_chosen_slot)
        if _save_data:
            apply_save(_save_data, world_sim, sources, _npc_controllers,
                       player, player_needs, defeated_npcs, combat_cooldowns)
            rebuild_item_services(_save_data, inv_svc, equip_svc, ctx.item_repo)
            for _npc_e, _, _npc_sprite in npc_list:
                if _npc_e.entity_id in defeated_npcs:
                    _npc_sprite.kill()
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
        (player, None, "Player"),
    ] + [
        (npc, ctrl, None) for npc, ctrl, _ in npc_list
    ]
    hud_index = 0
    obs_visible = True   # Heartbeat-6 observation panel (toggle with 'O')

    # --- Game loop ---
    running         = True
    in_combat       = False
    COMBAT_COOLDOWN = 4.0
    _paused_quit    = False

    while running:
        dt = clock.tick(settings.FPS) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    _result = run_pause_menu(
                        screen, clock, ctx, font,
                        world_sim, sources, _npc_controllers,
                        player, player_needs, defeated_npcs, combat_cooldowns,
                        inv_svc=inv_svc,
                    )
                    if _result == "quit":
                        _paused_quit = True
                        running = False
                    elif _result == "new_game":
                        world_sim = create_world_sim(sources)
                        (npc_list, player, player_needs, player_controller,
                         player_sprite, sprite_group, _npc_controllers,
                         defeated_npcs, combat_cooldowns) = _spawn_entities()
                        inv_svc, equip_svc = create_item_services(ctx)
                        _hud_subjects = [(player, None, "Player")] + [
                            (npc, ctrl, None) for npc, ctrl, _ in npc_list
                        ]
                        hud_index = 0
                        run_logger = RunLogger(settings.RUN_LOG_DIR)
                    elif _result.startswith("load:"):
                        _slot_id = int(_result.split(":")[1])
                        _save_data = ctx.save_manager.restore(slot_id=_slot_id)
                        if _save_data:
                            for _, _, _npc_s in npc_list:
                                sprite_group.add(_npc_s)
                            apply_save(_save_data, world_sim, sources, _npc_controllers,
                                       player, player_needs, defeated_npcs, combat_cooldowns)
                            rebuild_item_services(_save_data, inv_svc, equip_svc, ctx.item_repo)
                            for _npc_e, _, _npc_s in npc_list:
                                if _npc_e.entity_id in defeated_npcs:
                                    _npc_s.kill()
                            print(f"[SAVE] Session resumed from slot {_slot_id}.")
                    # else "resume" — continue
                elif event.key == pygame.K_TAB:
                    hud_index = (hud_index + 1) % len(_hud_subjects)
                elif event.key == pygame.K_o:
                    obs_visible = not obs_visible
                elif event.key == pygame.K_s:
                    _slot = run_save_menu(screen, clock, ctx, font)
                    if _slot is not None:
                        ctx.save_manager.snapshot(
                            world_sim, sources, _npc_controllers,
                            player, player_needs, defeated_npcs, combat_cooldowns,
                            slot_id=_slot,
                            bags=inv_svc.serialize_all(),
                        )

        if not in_combat:
            # --- World simulation tick ---
            living_count = len(npc_list) - len(defeated_npcs)

            # Compute average goblin hunger for threat escalation (H4)
            goblin_hungers = []
            for npc_e, npc_c, _ in npc_list:
                if (npc_e.entity_id not in defeated_npcs
                        and npc_e.subtype == "goblin"):
                    h = next((n for n in npc_c.needs
                              if n.need_id == "hunger"), None)
                    if h:
                        goblin_hungers.append(h.current_value / 100.0)
            avg_goblin_hunger = (sum(goblin_hungers) / len(goblin_hungers)
                                 if goblin_hungers else 1.0)

            sim_ticks = world_sim.tick(dt, living_count, avg_goblin_hunger)
            if sim_ticks > 0 and world_sim.clock.tick_count % 30 == 0:
                print(world_sim.status_line())

            # Phase 1.5: periodic autosave
            if (sim_ticks > 0
                    and settings.AUTOSAVE_INTERVAL > 0
                    and world_sim.clock.tick_count % settings.AUTOSAVE_INTERVAL == 0):
                ctx.save_manager.snapshot(
                    world_sim, sources, _npc_controllers,
                    player, player_needs, defeated_npcs, combat_cooldowns,
                )

            # Heartbeat-6: sample world + NPC state to the run-log
            if (sim_ticks > 0
                    and world_sim.clock.tick_count % settings.RUN_LOG_INTERVAL == 0):
                run_logger.sample(world_sim, sources, npc_list,
                                  defeated_npcs, world_sim.clock.tick_count)

            def _grid(entity):
                return tile_map.world_to_grid(entity.x, entity.y)

            all_entities = (
                [e for e, _, _ in npc_list if e.entity_id not in defeated_npcs]
                + [player]
            )
            occupied_by: dict[str, tuple[int, int]] = {
                e.entity_id: _grid(e) for e in all_entities
            }

            # Proximity fear + contested sources (H4)
            contested = update_proximity_fear(npc_list, defeated_npcs)

            for npc_entity, npc_ctrl, _ in npc_list:
                if npc_entity.entity_id not in defeated_npcs:
                    others = {
                        pos for eid, pos in occupied_by.items()
                        if eid != npc_entity.entity_id
                    }
                    npc_ctrl.contested_sources = contested
                    npc_ctrl.update(dt, occupied_tiles=others)
                    apply_health_drain(npc_ctrl.needs, npc_entity, dt)
                    apply_regen(npc_ctrl.needs, npc_entity, dt)
                    npc_entity.update(dt)

            player_controller.update(dt)
            player.update(dt)
            update_needs(player_needs)
            apply_health_drain(player_needs, player, dt)
            apply_regen(player_needs, player, dt)
            sprite_group.update()

            now = pygame.time.get_ticks() / 1000.0
            for npc_entity, _, npc_sprite in npc_list:
                if npc_entity.entity_id in defeated_npcs:
                    continue
                since_last = now - combat_cooldowns.get(npc_entity.entity_id, -999)
                if since_last < COMBAT_COOLDOWN:
                    continue
                dist = math.hypot(player.x - npc_entity.x,
                                  player.y - npc_entity.y)
                if dist < COMBAT_TRIGGER_DIST:
                    in_combat = True
                    result = run_combat(screen, clock, font, player, npc_entity, ctx)
                    in_combat = False
                    combat_cooldowns[npc_entity.entity_id] = pygame.time.get_ticks() / 1000.0
                    if result == "win":
                        defeated_npcs.add(npc_entity.entity_id)
                        npc_sprite.kill()
                        print(f"[COMBAT] Player defeated {npc_entity.name}!")
                    elif result == "lose":
                        print("[COMBAT] Player was defeated — game over.")
                        running = False
                    break

        # Draw
        screen.fill(settings.BG_COLOR)
        tile_map.draw(screen)

        # Zone labels already rendered by tile_map.draw(); skip source labels
        # that duplicate a zone label (FARM overlaps "Farm" zone).
        _zone_label_names = {"FARM"}  # source labels that match zone labels
        for src in sources:
            if src.label in _zone_label_names:
                continue
            lbl = label_font.render(f"[{src.label}]", True, (255, 255, 255))
            screen.blit(lbl, (src.world_x + settings.LEVEL_X - lbl.get_width() // 2,
                              src.world_y + settings.LEVEL_Y - lbl.get_height() // 2))

        # H5: source stock bars for finite sources
        for src in sources:
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
        _needs = player_needs if _ctrl is None else _ctrl.needs
        _state = _lbl         if _ctrl is None else _ctrl.state
        draw_hud(screen, _e, _needs, _state, font)

        # Heartbeat-6: world-overview observation panel (left margin)
        if obs_visible:
            draw_observation_panel(screen, world_sim, sources, npc_list,
                                   defeated_npcs, font)

        # Level border outline
        pygame.draw.rect(screen, (80, 80, 100),
                         pygame.Rect(settings.LEVEL_X - 2, settings.LEVEL_Y - 2,
                                     settings.LEVEL_W + 4, settings.LEVEL_H + 4), 2)

        day = world_sim.clock.day
        info_txt = font.render(
            f"Day {day:.2f}   HP {player.hp:.0f}/{player.max_hp}"
            f"   SP {player.cycles}/{player.max_cycles}"
            f"   MP {player.mp}/{player.max_mp}",
            True, settings.TEXT_COLOR)
        screen.blit(info_txt, (settings.LEVEL_X, 10))

        pygame.display.flip()

    # Phase 1.5: save-on-quit (window-close path only; pause-menu quit saves internally)
    if settings.SAVE_ON_QUIT and not _paused_quit:
        ctx.save_manager.snapshot(
            world_sim, sources, _npc_controllers,
            player, player_needs, defeated_npcs, combat_cooldowns,
            bags=inv_svc.serialize_all(),
        )

    run_logger.finalize(world_sim, npc_list, defeated_npcs)
    pygame.quit()
    print("\n[EXIT] Session ended.")


if __name__ == "__main__":
    main()
