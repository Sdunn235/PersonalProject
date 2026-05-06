# main.py
# Tower Defense Game - Main Module

import pygame
import game_settings
import random
from level_data import level_one
from enemy_type import GoblinSpearman, GoblinArcher, GoblinAxeman, GoblinMage, GoblinKing
from sprite_groups import enemies, towers, projectiles
from image_utils import load_and_scale_image
from tower_type import GateTower, PitTile, BasicTower
from placement_manager import attempt_placement

pygame.init()
screen = pygame.display.set_mode((game_settings.GAME_WIDTH, game_settings.GAME_HEIGHT))
clock = pygame.time.Clock()

# Mouse Cursors
mouse_cursor_inactive = pygame.image.load("Tower Defense/src/images/cursor/inactive_cursor.png")
mouse_cursor_active = pygame.image.load("Tower Defense/src/images/cursor/active_cursor.png")

# Track which key is held down
held_key = None

running = True
background = pygame.Surface((screen.get_width(), screen.get_height()))
background.fill("#353535")

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Track key holds
        elif event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_g, pygame.K_p, pygame.K_t):
                held_key = event.key

        elif event.type == pygame.KEYUP:
            if event.key == held_key:
                held_key = None

        # Place tower only if a key is held AND mouse is clicked
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if held_key is not None:
                mouse_position = pygame.mouse.get_pos()
                col = mouse_position[0] // game_settings.COL_SIZE
                row = mouse_position[1] // game_settings.ROW_SIZE

                if 0 <= row < game_settings.NUM_OF_ROWS and 0 <= col < game_settings.NUM_OF_COLS:
                    cell = (col, row)
                    if held_key == pygame.K_g:
                        attempt_placement(GateTower, cell)
                    elif held_key == pygame.K_p:
                        attempt_placement(PitTile, cell)
                    elif held_key == pygame.K_t:
                        attempt_placement(BasicTower, cell)

    screen.blit(level_one.background, (0, 0))

    # Spawn enemies periodically
    if len(enemies) < game_settings.enemy_wave_size and pygame.time.get_ticks() - game_settings.tick_of_last_enemy_spawn > game_settings.enemy_spawn_interval:
        enemy_class = random.choice([GoblinSpearman, GoblinArcher, GoblinAxeman, GoblinMage, GoblinKing])
        enemies.add(enemy_class(level_one))

    # 🔁 Clear pit slow data before tower updates
    for enemy in enemies:
        enemy.pit_slow_sources = []

    towers.update()
    enemies.update()
    projectiles.update()

    towers.draw(screen)
    for tower in towers:
        tower.draw_health_bar(screen)

    enemies.draw(screen)
    for enemy in enemies:
        enemy.draw_health_bar(screen)
        enemy.draw_with_overlay(screen)

    projectiles.draw(screen)

    # Mouse cursor rendering
    mouse_position = pygame.mouse.get_pos()
    col = mouse_position[0] // game_settings.COL_SIZE
    row = mouse_position[1] // game_settings.ROW_SIZE
    if 0 <= row < game_settings.NUM_OF_ROWS and 0 <= col < game_settings.NUM_OF_COLS:
        mouse_cursor_position = pygame.Rect((col * game_settings.COL_SIZE, row * game_settings.ROW_SIZE),
                                            (game_settings.COL_SIZE, game_settings.ROW_SIZE))
        if level_one.blocked_tiles[row][col]:
            screen.blit(mouse_cursor_inactive, mouse_cursor_position)
        else:
            screen.blit(mouse_cursor_active, mouse_cursor_position)

    font = pygame.font.Font(pygame.font.get_default_font(), 24)
    text = font.render(f"${game_settings.player_money}", True, (255, 255, 255))
    screen.blit(text, (40, game_settings.GAME_HEIGHT - 60))

    pygame.display.flip()
    game_settings.dt = clock.tick(game_settings.fps) / 1000.0
