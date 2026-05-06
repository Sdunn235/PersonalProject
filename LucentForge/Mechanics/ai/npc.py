# npc.py — NPC entity (extends Entity base)
from __future__ import annotations
from dataclasses import dataclass, field
from Mechanics.entities.base import Entity
from Mechanics.entities.stats import Stats
from Mechanics.entities.traits import Traits
from Mechanics.combat import rules


@dataclass
class NPC(Entity):
    is_enemy:   bool = True                      # can be engaged in combat
    cycles:     int  = rules.CYCLE_MAX_DEFAULT   # current stamina (persists between combats)
    max_cycles: int  = rules.CYCLE_MAX_DEFAULT
    mp:         int  = rules.MP_MAX_DEFAULT      # current mana (persists between combats)
    max_mp:     int  = rules.MP_MAX_DEFAULT
    equipment:  dict = field(default_factory=dict)  # equipped item ids {"weapon": "...", "armor": "..."}

    def update(self, dt: float) -> None:
        # Movement and needs are driven by NPCController.
        # This method is called by the game loop for any passive per-frame logic.
        pass
