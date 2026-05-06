# projectile_config.py
# Centralized configuration for all projectile types

PROJECTILE_STATS = {
    "arrow": {
        "damage": 10,
        "speed": 500,
        "image_path": "Tower Defense/src/images/projectiles/projectile_arrow.png",
        "effects": {}
    },
    "fire_arrow": {
        "damage": 12,
        "speed": 500,
        "image_path": "Tower Defense/src/images/projectiles/projectile_fire_arrow.png",
        "effects": {
            "burn": {
                "amount": 3,
                "duration": 5
            }
        }
    },
    "ice_arrow": {
        "damage": 8,
        "speed": 500,
        "image_path": "Tower Defense/src/images/projectiles/projectile_ice_arrow.png",
        "effects": {
            "slow": {
                "amount": 2.0,
                "duration": 4
            }
        }
    },
    "magic": {
        "damage": 15,
        "speed": 450,
        "image_path": "Tower Defense/src/images/projectiles/projectile_magic.png",
        "effects": {
            "slow": {
                "amount": 2.0,
                "duration": 5
            }
        }
    },
    "king_buff": {
        "damage": 25,
        "speed": 500,
        "image_path": None,
        "effects": {
            "buff": {
                "amount": 0,
                "duration": 0  # This is just a visual projectile for flavor
            }
        }
    }
}