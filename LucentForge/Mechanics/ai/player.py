# player.py — Player entity driven by movement INTENT, with tile collision.
#
# The Ripple Kernel treats the player as one more agent (bible §RT): the sim never reads the keyboard.
# The shell (or an AI player / replay) sets `move_intent` each frame; update() turns it into movement.
# This module imports no pygame, so the kernel steps in a process with no display (LF-046).
import settings
from Mechanics.needs.needs_system import fill_need

# How far from the entity center to check for wall contact (slightly less than half tile)
_COLLISION_RADIUS = settings.TILE_SIZE // 2 - 2
# Distance within which the player can satisfy a need at a source
_SOURCE_REACH = settings.TILE_SIZE * 1.5


class PlayerController:
    def __init__(self, entity, tile_map=None, needs=None, sources=None) -> None:
        self.entity   = entity
        self.tile_map = tile_map
        self.needs    = needs   or []
        self.sources  = sources or []
        # (dx, dy) in [-1, 1] each: where the player wants to go this frame. Set by the shell from the
        # arrow keys (PresentationShell._apply_player_intent) or by any other driver.
        self.move_intent: tuple[float, float] = (0.0, 0.0)

    def _blocked(self, x: float, y: float) -> bool:
        """Return True if world position (x, y) sits inside a blocked tile."""
        if self.tile_map is None:
            return False
        col = int(x // settings.TILE_SIZE)
        row = int(y // settings.TILE_SIZE)
        return self.tile_map.is_blocked(col, row)

    def _hits_wall(self, cx: float, cy: float) -> bool:
        """Check the four corners of the player bounding box against the tile grid."""
        r = _COLLISION_RADIUS
        return (self._blocked(cx - r, cy - r) or
                self._blocked(cx + r, cy - r) or
                self._blocked(cx - r, cy + r) or
                self._blocked(cx + r, cy + r))

    def update(self, dt: float) -> None:
        speed = settings.NPC_SPEED * dt

        raw_dx, raw_dy = self.move_intent

        # Normalize diagonal movement to prevent sqrt(2) speed boost
        if raw_dx != 0 and raw_dy != 0:
            diag = 0.7071  # 1 / sqrt(2)
            raw_dx *= diag
            raw_dy *= diag

        dx = raw_dx * speed
        dy = raw_dy * speed

        half = _COLLISION_RADIUS

        # --- X axis ---
        new_x = self.entity.x + dx
        new_x = max(half, min(settings.SCREEN_W - half, new_x))
        if self._hits_wall(new_x, self.entity.y):
            new_x = self.entity.x      # blocked — revert horizontal movement
        self.entity.x = new_x

        # --- Y axis ---
        new_y = self.entity.y + dy
        new_y = max(half, min(settings.SCREEN_H - half, new_y))
        if self._hits_wall(self.entity.x, new_y):
            new_y = self.entity.y      # blocked — revert vertical movement
        self.entity.y = new_y

        # --- Source interaction: refill matching need when standing at a source ---
        for source in self.sources:
            if source.distance_from(self.entity.x, self.entity.y) <= _SOURCE_REACH:
                need = next((n for n in self.needs
                             if n.need_id == source.need_id), None)
                if need is not None and need.current_value < 100.0:
                    fill_need(need, dt, source=source)
