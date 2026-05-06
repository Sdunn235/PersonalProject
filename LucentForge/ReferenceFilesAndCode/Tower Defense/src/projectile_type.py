# projectile_type.py
# Tower Defense Game - Centralized Projectile Type Factory and Placeholder Logic

from projectile_config import PROJECTILE_STATS
from projectile import Projectile
import pygame


def create_projectile(projectile_type, source, target, owner=None):
    """
    Factory method for creating projectiles with dynamic logic,
    effects, visuals, and behavior.
    """
    stats = PROJECTILE_STATS.get(projectile_type, {})

    return Projectile(
        source=source,
        target=target,
        owner=owner,
        projectile_type=projectile_type
    )



