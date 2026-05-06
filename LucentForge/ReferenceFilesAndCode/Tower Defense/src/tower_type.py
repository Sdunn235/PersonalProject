# tower_type.py
# Tower Defense Game - Tower Subclasses

import pygame
from tower import Tower
import game_settings
from image_utils import load_and_scale_image
from tower_config import TOWER_STATS
from sprite_groups import enemies

class BasicTower(Tower):
    def __init__(self, cell):
        super().__init__(cell)
        stats = TOWER_STATS["BasicTower"]
        self.cost = stats["cost"]
        self.range = stats["range"]
        self.attack_damage = stats["damage"]
        self.fire_cd = stats["fire_cd"]
        self.max_hp = stats["hp"]
        self.hp = self.max_hp
        self.projectile_type = stats["projectile_type"]
        self.allow_on_path = stats.get("allow_on_path", False)
        self.image = load_and_scale_image(
            stats.get("image_path"),
            (game_settings.COL_SIZE, game_settings.ROW_SIZE),
            stats.get("placeholder_color", (255, 0, 255))
        )
        self.original_image = self.image.copy()

class GateTower(Tower):
    def __init__(self, cell):
        super().__init__(cell)
        stats = TOWER_STATS["GateTower"]
        self.cost = stats["cost"]
        self.range = stats["range"]
        self.attack_damage = stats["damage"]
        self.fire_cd = stats["fire_cd"]
        self.max_hp = stats["hp"]
        self.hp = self.max_hp
        self.projectile_type = stats["projectile_type"]
        self.allow_on_path = stats.get("allow_on_path", True)
        self.image = load_and_scale_image(
            stats.get("image_path"),
            (game_settings.COL_SIZE * 3, game_settings.ROW_SIZE),
            stats.get("placeholder_color", (255, 0, 255))
        )
        self.original_image = self.image.copy()
        self.rect = self.image.get_rect()
        self.projectile_position = pygame.Vector2(self.rect.centerx, self.rect.centery)
        self.position = pygame.Vector2(self.rect.center)

    def set_orientation(self, direction, cell):
        col, row = cell
        if direction == "horizontal":
            self.image = pygame.transform.rotate(self.original_image, 0)
            self.rect = self.image.get_rect()
            self.rect.topleft = ((col - 1) * game_settings.COL_SIZE, row * game_settings.ROW_SIZE)
        elif direction == "vertical":
            self.image = pygame.transform.rotate(self.original_image, 90)
            self.rect = self.image.get_rect()
            self.rect.topleft = (col * game_settings.COL_SIZE, (row - 1) * game_settings.ROW_SIZE)
        self.original_image = self.image.copy()
        self.projectile_position = pygame.Vector2(self.rect.centerx, self.rect.centery)
        self.position = pygame.Vector2(self.rect.center)

class PitTile(Tower):
    def __init__(self, cell):
        super().__init__(cell)
        stats = TOWER_STATS["PitTile"]
        self.cost = stats["cost"]
        self.range = stats["range"]
        self.attack_damage = stats["damage"]
        self.fire_cd = stats["fire_cd"]
        self.max_hp = stats["hp"]
        self.hp = self.max_hp
        self.can_be_destroyed = stats.get("can_be_destroyed", True)
        self.projectile_type = stats.get("projectile_type")
        self.allow_on_path = stats.get("allow_on_path", True)
        self.image = load_and_scale_image(
            stats.get("image_path"),
            (game_settings.COL_SIZE, game_settings.ROW_SIZE),
            stats.get("placeholder_color", (255, 0, 255))
        )
        self.original_image = self.image.copy()
        self.slow_multiplier = stats.get("slow_effect", {}).get("amount", 1.0)

    def update(self):
        for enemy in enemies:
            if self.rect.colliderect(enemy.rect):
                if not hasattr(enemy, "pit_slow_sources"):
                    enemy.pit_slow_sources = []
                enemy.pit_slow_sources.append(self.slow_multiplier)
