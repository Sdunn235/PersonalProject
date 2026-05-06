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
                                 create_npc_controller, create_world_sim)
from Mechanics.entities.factory import create_player, create_all_npcs, get_sprite_path
from Mechanics.needs.needs_system import apply_health_drain, apply_regen, update_needs
from Mechanics.world.tile_map import TileMap
from Mechanics.ai.player import PlayerController
from Mechanics.renderer.sprite import EntitySprite
from Mechanics.renderer.hud import draw_hud
from Mechanics.renderer.health_bar import draw_stat_bar
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

    # --- Spawn NPCs from entities.json ---
    npc_list = []  # each entry: (entity, controller, sprite)
    for npc in create_all_npcs(ctx):
        controller = create_npc_controller(npc, ctx, sources, tile_map,
                                              world_sim=world_sim)
        sprite     = EntitySprite(npc, image_path=get_sprite_path(ctx, npc.entity_id),
                                  size=settings.TILE_SIZE - 2)
        npc_list.append((npc, controller, sprite))
        print(f"[SPAWN] {npc.name} at ({int(npc.x)}, {int(npc.y)})")

    defeated_npcs: set[str] = set()

    # --- Spawn player from entities.json ---
    player = create_player(ctx)
    player_needs = create_needs(ctx)
    player_controller = PlayerController(player, tile_map=tile_map,
                                         needs=player_needs, sources=sources)
    player_sprite     = EntitySprite(player, image_path=get_sprite_path(ctx, player.entity_id),
                                     size=settings.TILE_SIZE - 2)
    print(f"[SPAWN] Player at ({int(player.x)}, {int(player.y)})  [Arrow keys to move]")
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

    sprite_group = pygame.sprite.Group(
        *[s for _, _, s in npc_list], player_sprite
    )

    # --- Source label font ---
    label_font = pygame.font.SysFont(None, 18)

    # --- HUD cycle state (Tab key) ---
    _hud_subjects = [
        (player, None, "Player"),
    ] + [
        (npc, ctrl, None) for npc, ctrl, _ in npc_list
    ]
    hud_index = 0

    # --- Game loop ---
    running          = True
    in_combat        = False
    combat_cooldowns: dict[str, float] = {}
    COMBAT_COOLDOWN  = 4.0

    while running:
        dt = clock.tick(settings.FPS) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_TAB:
                    hud_index = (hud_index + 1) % len(_hud_subjects)

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

    pygame.quit()
    print("\n[EXIT] Session ended.")


if __name__ == "__main__":
    main()
