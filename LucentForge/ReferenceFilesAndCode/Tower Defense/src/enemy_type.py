# enemy_type.py
# Tower Defense Game - Enemy Types Module

import pygame
from sprite_groups import enemies, projectiles
import game_settings
from enemy import Enemy
import os
from enemy_config import ENEMY_STATS

# Path to enemy sprites
ENEMY_IMG_DIR = os.path.join("Tower Defense", "src", "images", "enemies")

# GoblinSpearman: Fast, fragile, melee attacker
class GoblinSpearman(Enemy):
    def __init__(self, level):
        super().__init__(level, os.path.join(ENEMY_IMG_DIR, "goblin_spearman.png"))
        stats = ENEMY_STATS["GoblinSpearman"]
        self.max_hp = stats["hp"]
        self.hp = self.max_hp
        self.speed = stats["speed"]
        self.bounty = stats["bounty"]
        self.attack_damage = stats["damage"]
        self.attack_range = stats["range"]
        self.max_attacks = stats["attacks"]
        self.behavior = stats["behavior"]
        self.attacked_towers = set()
        self.base_speed = self.speed
        self.base_damage = self.attack_damage
        self.base_range = self.attack_range

# GoblinAxeman: Slow, tanky melee attacker
class GoblinAxeman(Enemy):
    def __init__(self, level):
        super().__init__(level, os.path.join(ENEMY_IMG_DIR, "goblin_axeman.png"))
        stats = ENEMY_STATS["GoblinAxeman"]
        self.max_hp = stats["hp"]
        self.hp = self.max_hp
        self.speed = stats["speed"]
        self.bounty = stats["bounty"]
        self.attack_damage = stats["damage"]
        self.attack_range = stats["range"]
        self.max_attacks = stats["attacks"]
        self.behavior = stats["behavior"]
        self.attacked_towers = set()
        self.base_speed = self.speed
        self.base_damage = self.attack_damage
        self.base_range = self.attack_range

# GoblinArcher: Fast, ranged attacker
class GoblinArcher(Enemy):
    def __init__(self, level):
        super().__init__(level, os.path.join(ENEMY_IMG_DIR, "goblin_archer.png"))
        stats = ENEMY_STATS["GoblinArcher"]
        self.max_hp = stats["hp"]
        self.hp = self.max_hp
        self.speed = stats["speed"]
        self.bounty = stats["bounty"]
        self.attack_damage = stats["damage"]
        self.attack_range = stats["range"]
        self.attack_rate = stats["cooldown"]
        self.behavior = stats["behavior"]
        self.last_attack_time = 0
        self.projectile_type = stats["projectile_type"]
        self.base_speed = self.speed
        self.base_damage = self.attack_damage
        self.base_range = self.attack_range

# GoblinMage: AoE attacker with slowing effect
class GoblinMage(Enemy):
    def __init__(self, level):
        super().__init__(level, os.path.join(ENEMY_IMG_DIR, "goblin_mage.png"))
        stats = ENEMY_STATS["GoblinMage"]
        self.max_hp = stats["hp"]
        self.hp = self.max_hp
        self.speed = stats["speed"]
        self.bounty = stats["bounty"]
        self.attack_damage = stats["damage"]
        self.attack_range = stats["range"]
        self.attack_rate = stats["cooldown"]
        self.behavior = stats["behavior"]
        self.last_attack_time = 0
        self.aoe_radius = stats["aoe_radius"]
        self.effects = stats.get("effects", {})
        self.projectile_type = stats["projectile_type"]
        self.base_speed = self.speed
        self.base_damage = self.attack_damage
        self.base_range = self.attack_range

# GoblinKing: Boss enemy with buff aura
class GoblinKing(Enemy):
    def __init__(self, level):
        super().__init__(level, os.path.join(ENEMY_IMG_DIR, "goblin_king.png"))
        stats = ENEMY_STATS["GoblinKing"]
        self.max_hp = stats["hp"]
        self.hp = self.max_hp
        self.speed = stats["speed"]
        self.bounty = stats["bounty"]
        self.attack_damage = stats["damage"]
        self.attack_range = stats["range"]
        self.attack_rate = stats["cooldown"]
        self.behavior = stats["behavior"]
        self.max_attacks = stats.get("attacks", 2)
        self.buff_stats = stats.get("buff_stats", {})
        self.projectile_type = stats.get("projectile_type", None)
        self.last_attack_time = 0
        self.attacked_towers = set()
        self.base_speed = self.speed
        self.base_damage = self.attack_damage
        self.base_range = self.attack_range
