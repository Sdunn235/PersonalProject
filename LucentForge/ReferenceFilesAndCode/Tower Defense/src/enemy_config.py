# enemy_config.py
# Centralized configuration for enemy stats and behavior

ENEMY_STATS = {
    "GoblinSpearman": {
        "hp": 40,
        "damage": 10,
        "speed": 60,
        "bounty": 5,
        "attacks": 1,
        "range": 36,
        "cooldown": 0,
        "ranged": False,
        "behavior": "melee"
    },
    "GoblinAxeman": {
        "hp": 60,
        "damage": 20,
        "speed": 40,
        "bounty": 8,
        "attacks": 1,
        "range": 36,
        "cooldown": 0,
        "ranged": False,
        "behavior": "melee"
    },
    "GoblinArcher": {
        "hp": 35,
        "damage": 8,
        "speed": 70,
        "bounty": 6,
        "attacks": 1,
        "range": 120,
        "cooldown": 1,
        "ranged": True,
        "behavior": "ranged",
        "projectile_type": "arrow"
    },
    "GoblinMage": {
        "hp": 50,
        "damage": 15,
        "speed": 50,
        "bounty": 10,
        "attacks": 1,
        "range": 100,
        "cooldown": 3,
        "aoe_radius": 80,
        "effects": {
            "slow": {
                "amount": 2.0,
                "duration": 5
            }
        },
        "ranged": True,
        "behavior": "aoe",
        "projectile_type": "magic"
    },
    "GoblinKing": {
        "hp": 100,
        "damage": 25,
        "speed": 45,
        "bounty": 25,
        "attacks": 2,
        "range": 36,
        "cooldown": 1,
        "ranged": True,
        "behavior": "ranged",
        "projectile_type": "king_buff",
        "buff_stats": {
            "buff_radius": 100,
            "hp_buff": 20,
            "damage_buff": 1.5,
            "speed_buff": 1.2,
            "cooldown_buff": 0.8,
            "range_buff": 1.3
        }
    }

    
}
# Add more enemy types as needed