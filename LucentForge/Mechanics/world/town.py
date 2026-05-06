from enum import Enum
import settings
from Mechanics.world.resource_state import ResourceState
from Mechanics.world.goblin_threat import GoblinThreat


class TownState(Enum):
    STABLE = "stable"
    STRAINED = "strained"
    COLLAPSING = "collapsing"


class Town:
    """Settlement entity — reflects truth, doesn't own logic."""

    def __init__(self):
        self.state: TownState = TownState.STABLE

    def evaluate(self, resources: ResourceState, living_npc_count: int,
                 threat: GoblinThreat) -> None:
        """Derive town state from world pressures."""
        if (resources.food_total < settings.TOWN_FOOD_COLLAPSE
                or living_npc_count < settings.TOWN_MIN_POP):
            self.state = TownState.COLLAPSING
        elif (resources.food_total < settings.TOWN_FOOD_STRAIN
              or threat.threat_level > settings.TOWN_THREAT_STRAIN):
            self.state = TownState.STRAINED
        else:
            self.state = TownState.STABLE
