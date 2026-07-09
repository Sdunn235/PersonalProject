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
    # Bits/Bytes magic pools (§M3). bit_pool goes live in 4.3 (Intuition x
    # Constitution); byte_pool is the mp successor at parity until 4.5.
    bit_pool:      int = 0
    max_bit_pool:  int = 0
    byte_pool:     int = rules.MP_MAX_DEFAULT
    max_byte_pool: int = rules.MP_MAX_DEFAULT
    equipment:  dict = field(default_factory=dict)  # equipped item ids {"weapon": "...", "armor": "..."}

    # `mp`/`max_mp` alias the Byte pool during the 4.3 parity phase, so combat and
    # consumable code that still reads/writes `.mp` transparently uses Bytes. The
    # alias retires in 4.5 when the Fighter itself splits into bit/byte pools.
    @property
    def mp(self) -> int: return self.byte_pool

    @mp.setter
    def mp(self, v): self.byte_pool = v

    @property
    def max_mp(self) -> int: return self.max_byte_pool

    @max_mp.setter
    def max_mp(self, v): self.max_byte_pool = v

    def update(self, dt: float) -> None:
        # Movement and needs are driven by NPCController.
        # This method is called by the game loop for any passive per-frame logic.
        pass
