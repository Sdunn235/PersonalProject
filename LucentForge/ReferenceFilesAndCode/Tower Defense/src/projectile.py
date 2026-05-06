# projectile.py
import pygame
import os
import game_settings
from sprite_groups import projectiles
from image_utils import load_and_scale_image, rotate_image_to_velocity, get_placeholder_color
from projectile_config import PROJECTILE_STATS

class Projectile(pygame.sprite.Sprite):
    def __init__(self, source, target, owner=None, projectile_type="arrow"):
        super().__init__()

        self.owner = owner
        self.source = source
        self.target = target
        self.projectile_type = projectile_type

        stats = PROJECTILE_STATS.get(projectile_type, {})

        self.damage = stats.get("damage", getattr(source, "attack_damage", 10))
        self.effects = stats.get("effects", {})
        self.speed = stats.get("speed", 500)
        self.image_path = stats.get("image_path")

        self.position = pygame.Vector2(source.rect.center)
        self.velocity = pygame.Vector2(target.rect.center) - self.position
        if self.velocity.length_squared() != 0:
            self.velocity = self.velocity.normalize()
            self.velocity.scale_to_length(self.speed)
        else:
            self.velocity = pygame.Vector2(self.speed, 0)

        original_image = load_and_scale_image(
            self.image_path,
            (20, 20),
            get_placeholder_color(self.projectile_type)
        )

        self.image = rotate_image_to_velocity(original_image, self.velocity)
        self.rect = self.image.get_rect(center=self.position)

        self.time_to_live = 600
        self.tick_of_last_fired = pygame.time.get_ticks()

        projectiles.add(self)

    def update(self):
        self.update_position()
        self.rect.center = self.position

        if self.rect.colliderect(self.target.rect):
            # Skip if target is immune to damage
            if hasattr(self.target, "is_tower") and not getattr(self.target, "can_be_destroyed", True):
                print("[Projectile] Hit indestructible target – skipping damage/effects")
                self.kill()
                return

            if hasattr(self.target, "take_damage"):
                self.target.take_damage(self.damage)

            if hasattr(self.target, "apply_effect") and self.effects:
                for effect_type, effect_data in self.effects.items():
                    amount = effect_data.get("amount", 0)
                    duration = effect_data.get("duration", 0)
                    self.target.apply_effect(effect_type, amount, duration)

            self.kill()

    def update_position(self):
        if pygame.time.get_ticks() - self.tick_of_last_fired < self.time_to_live:
            self.position += self.velocity * game_settings.dt
        else:
            self.kill()
