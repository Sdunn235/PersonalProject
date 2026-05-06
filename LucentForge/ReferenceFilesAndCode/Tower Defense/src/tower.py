# tower.py
# Tower Defense Game - Tower Base Class
import pygame
import game_settings
from sprite_groups import enemies, projectiles
from image_utils import load_and_scale_image
from health_bar import HealthBar
from projectile import Projectile

class Tower(pygame.sprite.Sprite):
    def __init__(self, cell):
        super().__init__()

        self.cell = cell
        self.is_tower = True

        self.image = pygame.Surface((game_settings.COL_SIZE, game_settings.ROW_SIZE))
        self.image.fill((0, 255, 0))  # Default placeholder
        self.original_image = self.image.copy()

        self.rect = self.image.get_rect()
        self.rect.topleft = (cell[0] * game_settings.COL_SIZE, cell[1] * game_settings.ROW_SIZE)

        self.projectile_position = pygame.Vector2(self.rect.centerx, self.rect.centery)
        self.position = pygame.Vector2(self.rect.center)

        self.cost = 0
        self.range = 100
        self.fire_cd = 1.0
        self.tick_of_last_fire = 0
        self.original_fire_cd = self.fire_cd
        self.attack_damage = 10
        self.projectile_type = "arrow"

        self.max_hp = 100
        self.hp = self.max_hp
        self.can_be_destroyed = True
        self.allow_on_path = False

        self.health_bar = HealthBar(width=30, height=5)
        self.slow_effect_active = False
        self.slow_effect_end_time = 0
        self.overlay_surface = None

    def update(self):
        current_time = pygame.time.get_ticks()

        if current_time - self.tick_of_last_fire >= self.fire_cd * 1000:
            self.fire_at_closest_target()

        if self.slow_effect_active and current_time >= self.slow_effect_end_time:
            print(f"[Tower Slow Expired] fire_cd restored to {self.original_fire_cd}")
            self.fire_cd = self.original_fire_cd
            self.slow_effect_active = False
            self.image = self.original_image.copy()

    def apply_effect(self, effect_type, amount, duration):
        if effect_type == "slow":
            print(f"[Effect Applied] {effect_type} | Amount: {amount} | Duration: {duration}")
            if not self.slow_effect_active:
                self.original_fire_cd = self.fire_cd
                self.fire_cd *= amount
                self.slow_effect_active = True
            self.slow_effect_end_time = pygame.time.get_ticks() + duration * 1000

            self.image = self.original_image.copy()
            effect_surface = pygame.Surface(self.image.get_size(), pygame.SRCALPHA)
            mask = pygame.mask.from_surface(self.original_image)
            for y in range(mask.get_size()[1]):
                for x in range(mask.get_size()[0]):
                    if mask.get_at((x, y)):
                        effect_surface.set_at((x, y), (0, 0, 255, 50))
            for point in mask.outline():
                effect_surface.set_at(point, (0, 0, 255, 140))
            self.image.blit(effect_surface, (0, 0))

    def fire_at_closest_target(self):
        if enemies:
            enemy_sprites = enemies.sprites()
            closest_enemy = min(
                enemy_sprites,
                key=lambda e: self.projectile_position.distance_to(e.position)
            )
            if self.projectile_position.distance_to(closest_enemy.position) <= self.range:
                self.tick_of_last_fire = pygame.time.get_ticks()
                projectiles.add(Projectile(self, closest_enemy, owner=self, projectile_type=self.projectile_type))
                print(f"Tower fired at {pygame.time.get_ticks()}ms (Cooldown: {self.fire_cd}s)")

    def draw_health_bar(self, surface):
        self.health_bar.draw(surface, self.rect, self.hp, self.max_hp, position="top")

    def take_damage(self, amount):
        if not getattr(self, "can_be_destroyed", True):
            print("[Tower] Immune to damage")
            return
        self.hp -= amount
        if self.hp <= 0:
            self.kill()

    

    def cancel_placement(self):
        """
        Called when the tower fails to be placed (e.g., due to blocked tile or not enough money).
        Override in subclasses if needed.
        """
        print(f"[DEBUG] Placement cancelled for {self.__class__.__name__} at {self.cell}")

