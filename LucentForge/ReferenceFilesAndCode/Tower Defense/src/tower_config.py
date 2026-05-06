# tower_config.py
# Tower Defense Game - Tower Configuration Module

TOWER_STATS = {
    "BasicTower": {
        "cost": 0,
        "range": 150,
        "damage": 10,
        "fire_cd": 1.0,
        "hp": 100,
        "projectile_type": "arrow",
        "image_path": "Tower Defense/src/images/towers/tower_basic.png"
    },
    "GateTower": {
        "cost": 0,
        "range": 180,
        "damage": 15,
        "fire_cd": 2.0,
        "hp": 999999999999,
        "projectile_type": "arrow",
        "image_path": "Tower Defense/src/images/towers/gate_tower.png",
        "allow_on_path": True,
        "image_path": None,  # Explicitly show fallback needed
        "placeholder_color": (0, 255, 0)  # Unique for debugging visuals
    },
    "PitTile": {
        "cost": 0,
        "range": 0,
        "damage": 0,
        "fire_cd": 9999,  # No firing, just a pit
        "hp": 1,
        "projectile_type": None,
        "can_be_destroyed": False,
        "image_path": "Tower Defense/src/images/towers/pit_tile.png",
        "allow_on_path": True,
        "image_path": None,  # Explicitly show fallback needed
        "placeholder_color": (255, 0, 0),  # Unique for debugging visuals
        "slow_effect": {
            "amount": 0.5  # 50% speed reduction
        }
    }
}
