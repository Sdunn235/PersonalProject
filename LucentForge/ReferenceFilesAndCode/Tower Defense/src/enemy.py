# enemy.py
# Tower Defense Game - Enemy Base Class with Buff, Debuff, and Movement Logic

import pygame
import game_settings
import copy 
from level import Level
from sprite_groups import enemies, projectiles, towers
from image_utils import load_directional_frames
from health_bar import HealthBar
from projectile import Projectile
from projectile_config import PROJECTILE_STATS

class Enemy(pygame.sprite.Sprite):
    def __init__(self, level, sprite_path, frame_duration=100):
        super().__init__()

        self.frame_width = game_settings.COL_SIZE
        self.frame_height = game_settings.ROW_SIZE
        self.is_enemy = True
        self.health_bar = HealthBar(width=30, height=5)

        self.frames_by_direction = load_directional_frames(sprite_path, self.frame_width, self.frame_height)
        self.direction = "down"
        self.animation_frames = self.frames_by_direction[self.direction]
        self.current_frame_index = 0
        self.animation_timer = 0
        self.frame_duration = frame_duration
        self.animation_speed = 0.1

        self.image = self.animation_frames[self.current_frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (game_settings.GAME_WIDTH // 2, game_settings.GAME_HEIGHT // 2)

        self.waypoints = copy.deepcopy(level.enemy_waypoints)
        self.current_waypoint = 0
        self.position = self.waypoints[self.current_waypoint]
        self.speed = 50
        self.max_hp = 100
        self.hp = self.max_hp

        self.base_speed = self.speed
        self.speed_modifiers = {}

        self.buffed_by_king = False
        self.buff_overlay = None

        game_settings.tick_of_last_enemy_spawn = pygame.time.get_ticks()

    def fire_at_nearest_tower(self):
        now = pygame.time.get_ticks()
        cooldown_ms = self.attack_rate * 1000
        if now - self.last_attack_time < cooldown_ms or not towers:
            return

        closest_tower = min(towers, key=lambda t: self.position.distance_to(t.rect.center))
        if self.position.distance_to(closest_tower.rect.center) <= self.attack_range:
            self.last_attack_time = now
            projectile = Projectile(self, closest_tower, owner=self, projectile_type=self.projectile_type)
            projectiles.add(projectile)
            print(f"[{self.__class__.__name__}] fired {self.projectile_type} at {closest_tower.rect.center}")

    def recalculate_speed(self):
        self.speed = self.base_speed
        for modifier in self.speed_modifiers.values():
            self.speed *= modifier

    def update(self):
        # 🔁 This is cleared in main.py before tower updates
        # ✅ Stack pit slow modifiers before recalculating speed
        if hasattr(self, "pit_slow_sources") and self.pit_slow_sources:
            self.speed_modifiers["pit_tile"] = min(self.pit_slow_sources)
        else:
            self.speed_modifiers.pop("pit_tile", None)

        self.recalculate_speed()
        self.update_position()
        self.update_animation()
        self.rect.center = self.position

        if getattr(self, "behavior", None) in ["ranged", "aoe"]:
            self.fire_at_nearest_tower()

        if hasattr(self, "attack_damage") and hasattr(self, "max_attacks"):
            for tower in towers:
                if not hasattr(tower, "rect") or tower.rect is None:
                    continue
                if tower in self.attacked_towers:
                    continue

                x_diff = abs(self.rect.centerx - tower.rect.centerx)
                y_diff = abs(self.rect.centery - tower.rect.centery)

                if self.direction in ["left", "right"] and y_diff <= self.attack_range and x_diff <= self.frame_width:
                    tower.take_damage(self.attack_damage)
                    self.attacked_towers.add(tower)
                elif self.direction in ["up", "down"] and x_diff <= self.attack_range and y_diff <= self.frame_height:
                    tower.take_damage(self.attack_damage)
                    self.attacked_towers.add(tower)

                if len(self.attacked_towers) >= self.max_attacks:
                    break

        if hasattr(self, "buff_stats") and self.buff_stats:
            for enemy in enemies:
                if enemy is self:
                    continue
                if self.position.distance_to(enemy.position) <= self.buff_stats["buff_radius"]:
                    if not hasattr(enemy, "nearby_king_buffs"):
                        enemy.nearby_king_buffs = []
                    enemy.nearby_king_buffs.append(self.buff_stats)

        if not hasattr(self, "nearby_king_buffs"):
            self.nearby_king_buffs = []

        if self.nearby_king_buffs:
            self.apply_king_buff(self.nearby_king_buffs[0])
        else:
            self.remove_king_buff()

        self.nearby_king_buffs = []

        super().update()

    def apply_king_buff(self, buff_stats, color=(255, 215, 0)):
        self.speed_modifiers["king_buff"] = buff_stats["speed_buff"]
        self.attack_damage = self.base_damage * buff_stats["damage_buff"]
        self.attack_range = self.base_range * buff_stats["range_buff"]

        if not self.buffed_by_king:
            self.buffed_by_king = True
            mask = pygame.mask.from_surface(self.image)
            outline = mask.outline()
            glow_surface = pygame.Surface(self.image.get_size(), pygame.SRCALPHA)
            for point in outline:
                glow_surface.set_at(point, color)
            self.buff_overlay = glow_surface

    def remove_king_buff(self):
        if self.buffed_by_king:
            self.speed_modifiers.pop("king_buff", None)
            self.attack_damage = self.base_damage
            self.attack_range = self.base_range
            self.buffed_by_king = False
            self.buff_overlay = None

    def update_position(self):
        if self.current_waypoint < len(self.waypoints) - 1:
            target = self.waypoints[self.current_waypoint + 1]
            movement = target - self.position
            self.position.move_towards_ip(target, self.speed * game_settings.dt)

            if self.position == target:
                self.current_waypoint += 1

            self.direction = "right" if movement.x > 0 else "left" if abs(movement.x) > abs(movement.y) else "down" if movement.y > 0 else "up"
            self.animation_frames = self.frames_by_direction[self.direction]
        else:
            self.kill()

    def update_animation(self):
        self.current_frame_index += self.animation_speed
        if self.current_frame_index >= len(self.animation_frames):
            self.current_frame_index = 0
        self.image = self.animation_frames[int(self.current_frame_index)]

    def draw_health_bar(self, surface):
        self.health_bar.draw(surface, self.rect, self.hp, self.max_hp, position="top", scale=1.0)

    def take_damage(self, amount):
        self.hp -= amount
        if self.hp <= 0:
            game_settings.player_money += self.bounty
            if getattr(self, "behavior", None) == "boss":
                self.remove_king_buff()
            self.kill()

    def draw_with_overlay(self, screen):
        screen.blit(self.image, self.rect)
        if self.buff_overlay:
            screen.blit(self.buff_overlay, self.rect.topleft)
