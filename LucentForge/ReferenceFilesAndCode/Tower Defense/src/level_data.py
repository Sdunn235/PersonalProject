# level_data.py
# Tower Defense Game - Level Data Module
import pygame
import game_settings
from level import Level

level_one = Level()
level_one.background = pygame.image.load("Tower Defense/src/images/maps/Level 01/level01.png")

# Load path tiles
path_grid = level_one.get_grid_from_csv("Tower Defense/src/images/maps/Level 01/level01._Pathway.csv")
level_one.add_grid_to_path_tiles(path_grid)  # ← Added this
level_one.add_grid_to_tiles(path_grid, level_one.blocked_tiles)

# Load other blocked elements
props_grid = level_one.get_grid_from_csv("Tower Defense/src/images/maps/Level 01/level01._Props.csv")
level_one.add_grid_to_tiles(props_grid, level_one.blocked_tiles)

trees_shrubs_1_grid = level_one.get_grid_from_csv("Tower Defense/src/images/maps/Level 01/level01._Trees & Shrubs 1.csv")
level_one.add_grid_to_tiles(trees_shrubs_1_grid, level_one.blocked_tiles)

trees_shrubs_2_grid = level_one.get_grid_from_csv("Tower Defense/src/images/maps/Level 01/level01._Tree & Shrubs 2.csv")
level_one.add_grid_to_tiles(trees_shrubs_2_grid, level_one.blocked_tiles)

# Waypoints
level_one.create_waypoint_vector([
    (14, -1),
    (14, 9),
    (8, 9),
    (8, 1),
    (1, 1),
    (1, 6),
    (5, 6),
    (5, 12),
    (12, 12),
    (12, 15),
    (18, 15),
])
