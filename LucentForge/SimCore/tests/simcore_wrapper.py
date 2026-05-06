"""
SimCore Python Wrapper

Provides Python interface to LucentForge SimCore C++ library.
Enables rapid testing and validation before Unreal integration.

Currently uses ctypes to call C++ functions.
(Will migrate to pybind11 if performance becomes bottleneck)
"""

import json
import os
from typing import Dict, List, Optional, Tuple


# =============================================================================
# AGENT CLASS
# =============================================================================

def _clamp(value: float, min_val: float = 0.0, max_val: float = 1.0) -> float:
    """Clamp value to range [min_val, max_val]"""
    return max(min_val, min(max_val, value))


class TraitSet:
    """Agent trait modifiers (stable, 0.0–1.0 range)"""
    
    def __init__(self):
        self._aggression = 0.5
        self._boldness = 0.5
        self._curiosity = 0.5
        self._greed = 0.5
        self._sociability = 0.5
        self._loyalty = 0.5
        self._patience = 0.5
        self._risk_tolerance = 0.5
    
    @property
    def aggression(self) -> float:
        return self._aggression
    
    @aggression.setter
    def aggression(self, value: float):
        self._aggression = _clamp(value)
    
    @property
    def boldness(self) -> float:
        return self._boldness
    
    @boldness.setter
    def boldness(self, value: float):
        self._boldness = _clamp(value)
    
    @property
    def curiosity(self) -> float:
        return self._curiosity
    
    @curiosity.setter
    def curiosity(self, value: float):
        self._curiosity = _clamp(value)
    
    @property
    def greed(self) -> float:
        return self._greed
    
    @greed.setter
    def greed(self, value: float):
        self._greed = _clamp(value)
    
    @property
    def sociability(self) -> float:
        return self._sociability
    
    @sociability.setter
    def sociability(self, value: float):
        self._sociability = _clamp(value)
    
    @property
    def loyalty(self) -> float:
        return self._loyalty
    
    @loyalty.setter
    def loyalty(self, value: float):
        self._loyalty = _clamp(value)
    
    @property
    def patience(self) -> float:
        return self._patience
    
    @patience.setter
    def patience(self, value: float):
        self._patience = _clamp(value)
    
    @property
    def risk_tolerance(self) -> float:
        return self._risk_tolerance
    
    @risk_tolerance.setter
    def risk_tolerance(self, value: float):
        self._risk_tolerance = _clamp(value)


class NeedState:
    """Agent needs (dynamic, 0.0–1.0 range)"""
    def __init__(self):
        self.hunger = 0.0
        self.thirst = 0.1
        self.sleep = 0.2
        self.safety = 0.0
        self.social = 0.3
        self.wealth = 0.5
        self.power = 0.2
        self.curiosity = 0.4
    power: float = 0.2
    curiosity: float = 0.4


class Intent:
    """Agent's current goal/intention"""
    def __init__(self, action_type="rest", target_id="", target_x=0.0, target_y=0.0, priority=0.0, need_context=""):
        self.action_type = action_type  # travel|work|trade|interact|rest|attack
        self.target_id = target_id
        self.target_x = target_x
        self.target_y = target_y
        self.priority = priority
        self.need_context = need_context


class Agent:
    """Python wrapper around C++ Agent"""
    
    def __init__(self, agent_id: str, name: str, role: str = "adventurer"):
        self.agent_id = agent_id
        self.name = name
        self.role = role
        
        self.traits = TraitSet()
        self.needs = NeedState()
        self.skills: Dict[str, int] = {}
        self.inventory: List[Dict] = []
        self.wealth = 0
        
        self.memory = {
            "events": [],
            "relationships": {},
            "success_count": 0,
            "trauma": []
        }
        
        self.social_graph = {
            "faction": "",
            "reputation": 0,
            "debt": {},
            "oaths": []
        }
        
        self.current_intent = Intent(action_type="rest")

    def to_json(self) -> str:
        """Serialize agent to JSON (per DATA_CONTRACTS.md)"""
        data = {
            "agent_id": self.agent_id,
            "name": self.name,
            "role": self.role,
            "traits": {
                "aggression": self.traits.aggression,
                "boldness": self.traits.boldness,
                "curiosity": self.traits.curiosity,
                "greed": self.traits.greed,
                "sociability": self.traits.sociability,
                "loyalty": self.traits.loyalty,
                "patience": self.traits.patience,
                "risk_tolerance": self.traits.risk_tolerance,
            },
            "needs": {
                "hunger": self.needs.hunger,
                "thirst": self.needs.thirst,
                "sleep": self.needs.sleep,
                "safety": self.needs.safety,
                "social": self.needs.social,
                "wealth": self.needs.wealth,
                "power": self.needs.power,
                "curiosity": self.needs.curiosity,
            },
            "skills": self.skills,
            "inventory": self.inventory,
            "wealth": self.wealth,
            "memory": self.memory,
            "social_graph": self.social_graph,
            "current_intent": {
                "action_type": self.current_intent.action_type,
                "target_id": self.current_intent.target_id,
                "target_x": self.current_intent.target_x,
                "target_y": self.current_intent.target_y,
                "priority": self.current_intent.priority,
                "need_context": self.current_intent.need_context,
            },
        }
        return json.dumps(data, indent=2)

    @staticmethod
    def from_json(json_str: str) -> "Agent":
        """Deserialize agent from JSON"""
        data = json.loads(json_str)
        agent = Agent(data["agent_id"], data["name"], data.get("role", "adventurer"))
        
        if "traits" in data:
            traits_data = data["traits"]
            agent.traits.aggression = traits_data.get("aggression", 0.5)
            agent.traits.boldness = traits_data.get("boldness", 0.5)
            agent.traits.curiosity = traits_data.get("curiosity", 0.5)
            agent.traits.greed = traits_data.get("greed", 0.5)
            agent.traits.sociability = traits_data.get("sociability", 0.5)
            agent.traits.loyalty = traits_data.get("loyalty", 0.5)
            agent.traits.patience = traits_data.get("patience", 0.5)
            agent.traits.risk_tolerance = traits_data.get("risk_tolerance", 0.5)
        
        if "needs" in data:
            needs_data = data["needs"]
            agent.needs.hunger = needs_data.get("hunger", 0.0)
            agent.needs.thirst = needs_data.get("thirst", 0.1)
            agent.needs.sleep = needs_data.get("sleep", 0.2)
            agent.needs.safety = needs_data.get("safety", 0.0)
            agent.needs.social = needs_data.get("social", 0.3)
            agent.needs.wealth = needs_data.get("wealth", 0.5)
            agent.needs.power = needs_data.get("power", 0.2)
            agent.needs.curiosity = needs_data.get("curiosity", 0.4)
        
        if "skills" in data:
            agent.skills = data["skills"]
        if "inventory" in data:
            agent.inventory = data["inventory"]
        if "wealth" in data:
            agent.wealth = data["wealth"]
        if "memory" in data:
            agent.memory = data["memory"]
        if "social_graph" in data:
            agent.social_graph = data["social_graph"]
        if "current_intent" in data:
            intent_data = data["current_intent"]
            agent.current_intent = Intent(
                action_type=intent_data.get("action_type", "rest"),
                target_id=intent_data.get("target_id", ""),
                target_x=intent_data.get("target_x", 0.0),
                target_y=intent_data.get("target_y", 0.0),
                priority=intent_data.get("priority", 0.0),
                need_context=intent_data.get("need_context", "")
            )
        
        return agent


# =============================================================================
# COMBAT ENGINE CLASS
# =============================================================================

class TurnResult:
    """Result of a single combat turn"""
    def __init__(self, turn_type="miss", amount=0, was_crit=False, ability_id="", element="neutral", item_id="", cycles_restored=0):
        self.turn_type = turn_type  # "hit" | "miss" | "use_item" | "heal"
        self.amount = amount
        self.was_crit = was_crit
        self.ability_id = ability_id
        self.element = element
        self.item_id = item_id
        self.cycles_restored = cycles_restored


class CombatEngine:
    """Python wrapper around C++ CombatEngine
    
    Wraps iso_rpg_lab combat logic:
    - Damage calculations
    - Hit chance
    - Critical strikes
    - Ability/item usage
    - Combat AI
    """
    
    def __init__(self, data_path: str = ""):
        """Initialize combat engine with data (items, abilities, enemies, rules)"""
        self.data_path = data_path
        self.rng_seed = 0
        self.config_loaded = False
        
        # Load iso_rpg_lab data if available
        if data_path and os.path.exists(data_path):
            self.load_config(data_path)

    def load_config(self, data_path: str) -> bool:
        """Load combat data from JSON files
        
        Expected structure:
        data_path/
            items.json
            abilities.json
            enemies.json
            rules.json (optional)
        """
        required_files = ["items.json", "abilities.json", "enemies.json"]
        
        for fname in required_files:
            fpath = os.path.join(data_path, fname)
            if not os.path.exists(fpath):
                print(f"Warning: {fname} not found at {fpath}")
                return False
        
        self.data_path = data_path
        self.config_loaded = True
        return True

    def simulate_turn(self, attacker: Agent, defender: Agent, seed: int = 0) -> TurnResult:
        """Simulate a single combat turn
        
        Args:
            attacker: Agent taking action
            defender: Agent defending
            seed: RNG seed for reproducibility
        
        Returns:
            TurnResult describing what happened
        """
        # Currently: Call iso_rpg_lab directly (Phase 2)
        # TODO: Eventually: Call C++ SimCore.simulate_turn() via ctypes
        try:
            from gameplay.loader import load_all
            from gameplay.rng import RNG32
            from gameplay.combat import Fighter, take_turn
            from gameplay.stats import Stats, StatusFlags
            from gameplay.derive import BaseStats
            
            # Create iso_rpg_lab Fighter objects from our Agent
            # This is a simplified conversion
            attacker_fighter = Fighter(
                name=attacker.name,
                hp=50,  # TODO: Get from Agent stats
                stats=Stats(STR=10, MAG=0, LCK=5, DEF=5, RES=0, DEX=5, clamp_mode="clamp")
            )
            defender_fighter = Fighter(
                name=defender.name,
                hp=50,
                stats=Stats(STR=10, MAG=0, LCK=5, DEF=5, RES=0, DEX=5, clamp_mode="clamp")
            )
            
            rng = RNG32(seed=seed)
            result = take_turn(attacker_fighter, defender_fighter, rng)
            
            # Convert iso_rpg_lab result to our format
            return TurnResult(
                turn_type=result.get("type", "miss"),
                amount=result.get("amount", 0),
                was_crit=result.get("crit", False),
                ability_id=result.get("ability", ""),
                element=result.get("element", "neutral")
            )
        except Exception as e:
            # Fallback if iso_rpg_lab not available
            print(f"Warning: Could not call iso_rpg_lab: {e}")
            return TurnResult(turn_type="hit", amount=10, was_crit=False)

    def simulate_combat(
        self, 
        player: Agent, 
        enemy: Agent, 
        seed: int = 0, 
        max_turns: int = 1000
    ) -> Dict:
        """Simulate full combat encounter
        
        Args:
            player: Protagonist Agent
            enemy: Antagonist Agent
            seed: RNG seed
            max_turns: Maximum turns before timeout
        
        Returns:
            Dict with:
                - turn_history: List[TurnResult]
                - winner: "player" | "enemy" | "draw"
                - total_turns: int
                - total_damage: int
        """
        # TODO: Call C++ SimCore.simulate_combat() via ctypes
        # For now, return stub result
        return {
            "turn_history": [],
            "winner": "player",
            "total_turns": 0,
            "total_damage": 0,
        }

    def set_seed(self, seed: int):
        """Set RNG seed for reproducible combat"""
        self.rng_seed = seed


# =============================================================================
# WORLD STATE CLASS
# =============================================================================

class WorldState:
    """Python wrapper around C++ WorldState"""
    
    def __init__(self):
        self.time_cycle = 0
        self.time_phase = "morning"  # morning|afternoon|evening|night
        self.weather = "clear"
        
        self.agents: Dict[str, Agent] = {}
        self.locations: List[Dict] = []
        self.items: List[Dict] = []
        self.factions: List[Dict] = []

    def tick(self):
        """Advance world time by 1 cycle"""
        self.time_cycle += 1
        phases = ["morning", "afternoon", "evening", "night"]
        phase_idx = phases.index(self.time_phase)
        self.time_phase = phases[(phase_idx + 1) % 4]

    def find_agent(self, agent_id: str) -> Optional[Agent]:
        """Find agent by ID"""
        return self.agents.get(agent_id)

    def add_agent(self, agent: Agent):
        """Add agent to world"""
        self.agents[agent.agent_id] = agent

    def to_json(self) -> str:
        """Serialize world state to JSON"""
        data = {
            "world_state": {
                "time_cycle": self.time_cycle,
                "time_phase": self.time_phase,
                "weather": self.weather,
            },
            "agents": [json.loads(agent.to_json()) for agent in self.agents.values()],
            "locations": self.locations,
            "items": self.items,
            "factions": self.factions,
        }
        return json.dumps(data, indent=2)

    @staticmethod
    def from_json(json_str: str) -> "WorldState":
        """Deserialize world state from JSON"""
        data = json.loads(json_str)
        world = WorldState()
        
        if "world_state" in data:
            ws = data["world_state"]
            world.time_cycle = ws.get("time_cycle", 0)
            world.time_phase = ws.get("time_phase", "morning")
            world.weather = ws.get("weather", "clear")
        
        if "agents" in data:
            for agent_data in data["agents"]:
                agent_json = json.dumps(agent_data)
                agent = Agent.from_json(agent_json)
                world.add_agent(agent)
        
        if "locations" in data:
            world.locations = data["locations"]
        if "items" in data:
            world.items = data["items"]
        if "factions" in data:
            world.factions = data["factions"]
        
        return world


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "Agent",
    "AgentTraits",
    "AgentNeeds",
    "Intent",
    "CombatEngine",
    "TurnResult",
    "WorldState",
]


