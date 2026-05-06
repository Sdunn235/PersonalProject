# placement_manager.py
import game_settings
from sprite_groups import towers
from level_data import level_one
import pygame

def attempt_placement(tower_class, cell):
    tower = tower_class(cell)

    row, col = cell[1], cell[0]
    is_blocked = level_one.blocked_tiles[row][col]
    is_path = level_one.path_tiles[row][col]
    allow_on_path = getattr(tower, "allow_on_path", False)
    multi_tile = getattr(tower, "multi_tile", False)
    affordable = game_settings.player_money >= tower.cost

    # --- Custom rules for GateTower ---
    if tower_class.__name__ == "GateTower":
        if not is_path or not affordable:
            tower.cancel_placement()
            return False

        horizontal_clear = (
            col - 1 >= 0 and col + 1 < game_settings.NUM_OF_COLS and
            not level_one.blocked_tiles[row][col - 1] and
            not level_one.blocked_tiles[row][col + 1]
        )
        vertical_clear = (
            row - 1 >= 0 and row + 1 < game_settings.NUM_OF_ROWS and
            not level_one.blocked_tiles[row - 1][col] and
            not level_one.blocked_tiles[row + 1][col]
        )

        if horizontal_clear:
            tower.set_orientation("horizontal", cell)
            for offset in [-1, 0, 1]:
                level_one.add_cell_to_tiles((row, col + offset), level_one.blocked_tiles)

        elif vertical_clear:
            tower.set_orientation("vertical", cell)
            for offset in [-1, 0, 1]:
                level_one.add_cell_to_tiles((row + offset, col), level_one.blocked_tiles)

        else:
            tower.cancel_placement()
            return False

        towers.add(tower)
        game_settings.player_money -= tower.cost
        return True

    # --- Custom rules for PitTile ---
    elif tower_class.__name__ == "PitTile":
        if not is_path or not affordable:
            tower.cancel_placement()
            return False

        towers.add(tower)
        game_settings.player_money -= tower.cost
        level_one.add_cell_to_tiles((row, col), level_one.blocked_tiles)
        return True

    # --- Default placement rules ---
    if (not is_blocked or allow_on_path) and affordable:
        towers.add(tower)
        game_settings.player_money -= tower.cost

        if multi_tile:
            for offset in [-1, 0, 1]:
                blocked_col = col + offset
                if 0 <= blocked_col < game_settings.NUM_OF_COLS:
                    level_one.add_cell_to_tiles((row, blocked_col), level_one.blocked_tiles)
        else:
            level_one.add_cell_to_tiles((row, col), level_one.blocked_tiles)

        return True

    tower.cancel_placement()
    return False


def handle_input_placement(keys, mouse_buttons, cell):
    if mouse_buttons[0]:
        if keys[pygame.K_t]:
            attempt_placement("BasicTower", cell)
        elif keys[pygame.K_g]:
            attempt_placement("GateTower", cell)
        elif keys[pygame.K_p]:
            attempt_placement("PitTile", cell)
