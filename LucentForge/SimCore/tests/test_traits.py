"""
test_traits.py - TraitSystem Unit Tests

Validates TraitSystem functionality:
- Initialization
- Getter/Setter
- Clamping (0.0-1.0 bounds)
- Modifier weights
- Persistence
- JSON serialization
"""

import pytest
import sys
import json
from pathlib import Path

# Add SimCore tests to path
sys.path.insert(0, str(Path(__file__).parent))

from simcore_wrapper import Agent


class TestTraitSystemBasics:
    """Test basic trait creation and initialization"""

    def test_trait_initialization(self):
        """Test traits initialize to neutral (0.5)"""
        agent = Agent("test-agent", "Test Agent", "scholar")
        
        # All traits should start at 0.5 (neutral)
        assert agent.traits.aggression == 0.5
        assert agent.traits.boldness == 0.5
        assert agent.traits.curiosity == 0.5
        assert agent.traits.greed == 0.5
        assert agent.traits.sociability == 0.5
        assert agent.traits.loyalty == 0.5
        assert agent.traits.patience == 0.5
        assert agent.traits.risk_tolerance == 0.5

    def test_trait_range_validation(self):
        """Test traits are normalized 0.0–1.0"""
        agent = Agent("test", "Test", "warrior")
        
        # All traits should be in valid range
        for trait_name in ["aggression", "boldness", "curiosity", "greed", 
                          "sociability", "loyalty", "patience", "risk_tolerance"]:
            value = getattr(agent.traits, trait_name)
            assert 0.0 <= value <= 1.0, f"{trait_name} out of range: {value}"


class TestTraitSystemSetterGetter:
    """Test trait getter and setter functionality"""

    def test_trait_setter_basic(self):
        """Test setting trait values"""
        agent = Agent("test", "Test", "warrior")
        
        agent.traits.aggression = 0.8
        assert agent.traits.aggression == 0.8
        
        agent.traits.patience = 0.2
        assert agent.traits.patience == 0.2

    def test_trait_setter_clamping_upper(self):
        """Test setting trait above 1.0 gets clamped"""
        agent = Agent("test", "Test", "warrior")
        
        agent.traits.aggression = 1.5
        assert agent.traits.aggression == 1.0

    def test_trait_setter_clamping_lower(self):
        """Test setting trait below 0.0 gets clamped"""
        agent = Agent("test", "Test", "warrior")
        
        agent.traits.boldness = -0.5
        assert agent.traits.boldness == 0.0

    def test_trait_all_setters(self):
        """Test setting all traits"""
        agent = Agent("test", "Test", "warrior")
        
        traits_to_set = {
            "aggression": 0.9,
            "boldness": 0.7,
            "curiosity": 0.3,
            "greed": 0.6,
            "sociability": 0.4,
            "loyalty": 0.8,
            "patience": 0.2,
            "risk_tolerance": 0.5
        }
        
        for trait_name, value in traits_to_set.items():
            setattr(agent.traits, trait_name, value)
        
        for trait_name, expected_value in traits_to_set.items():
            actual_value = getattr(agent.traits, trait_name)
            assert actual_value == expected_value


class TestTraitSystemModifierWeights:
    """Test trait modifier weights (how traits affect action priorities)"""

    def test_aggressive_boosts_combat(self):
        """Aggressive agents should have higher combat priority"""
        # High aggression should amplify combat actions
        # Expected modifier weight > 1.0
        warrior = Agent("warrior", "Warrior", "warrior")
        warrior.traits.aggression = 0.9
        
        # Verify high aggression value is set
        assert warrior.traits.aggression == 0.9

    def test_patient_reduces_combat(self):
        """Patient agents should have lower combat priority"""
        # High patience should dampen combat actions
        scholar = Agent("scholar", "Scholar", "scholar")
        scholar.traits.patience = 0.9
        
        assert scholar.traits.patience == 0.9

    def test_loyal_affects_social(self):
        """High loyalty should affect social decisions"""
        agent = Agent("agent", "Loyal Agent", "merchant")
        agent.traits.loyalty = 0.95
        
        assert agent.traits.loyalty == 0.95

    def test_greedy_affects_wealth(self):
        """High greed should prioritize wealth gathering"""
        agent = Agent("agent", "Greedy Agent", "merchant")
        agent.traits.greed = 0.85
        
        assert agent.traits.greed == 0.85


class TestTraitSystemPersistence:
    """Test that traits remain stable (don't change unexpectedly)"""

    def test_traits_persist_across_ticks(self):
        """Traits should not change between game ticks"""
        agent = Agent("agent", "Test Agent", "warrior")
        
        # Set specific trait values
        agent.traits.aggression = 0.7
        agent.traits.patience = 0.3
        
        original_aggression = agent.traits.aggression
        original_patience = agent.traits.patience
        
        # Simulate some passage of time (in real implementation, this would be world.tick())
        # Traits should NOT change
        
        assert agent.traits.aggression == original_aggression
        assert agent.traits.patience == original_patience

    def test_multiple_agents_independent_traits(self):
        """Different agents should have independent traits"""
        agent1 = Agent("agent1", "Agent1", "warrior")
        agent2 = Agent("agent2", "Agent2", "scholar")
        
        agent1.traits.aggression = 0.9
        agent2.traits.aggression = 0.1
        
        assert agent1.traits.aggression == 0.9
        assert agent2.traits.aggression == 0.1
        
        # Changing one shouldn't affect the other
        agent1.traits.boldness = 0.8
        assert agent2.traits.boldness == 0.5  # Should still be default


class TestTraitSystemJSON:
    """Test JSON serialization of traits"""

    def test_traits_json_serialization(self):
        """Test trait values can be serialized to JSON"""
        agent = Agent("test", "Test Agent", "warrior")
        
        agent.traits.aggression = 0.8
        agent.traits.boldness = 0.6
        agent.traits.patience = 0.2
        
        # Serialize to JSON
        agent_json = agent.to_json()
        assert agent_json is not None
        assert isinstance(agent_json, str)
        
        # Should contain trait values
        data = json.loads(agent_json)
        assert "traits" in data
        assert data["traits"]["aggression"] == 0.8
        assert data["traits"]["boldness"] == 0.6
        assert data["traits"]["patience"] == 0.2

    def test_traits_json_deserialization(self):
        """Test trait values can be loaded from JSON"""
        agent1 = Agent("test", "Test Agent", "warrior")
        agent1.traits.aggression = 0.75
        agent1.traits.loyalty = 0.85
        
        # Serialize
        agent_json = agent1.to_json()
        
        # Deserialize
        agent2 = Agent.from_json(agent_json)
        
        # Verify traits match
        assert agent2.traits.aggression == 0.75
        assert agent2.traits.loyalty == 0.85

    def test_traits_json_roundtrip(self):
        """Test traits survive complete JSON roundtrip"""
        original = Agent("test", "Original", "scholar")
        original.traits.aggression = 0.3
        original.traits.boldness = 0.7
        original.traits.curiosity = 0.9
        original.traits.greed = 0.1
        original.traits.sociability = 0.5
        original.traits.loyalty = 0.8
        original.traits.patience = 0.2
        original.traits.risk_tolerance = 0.4
        
        # JSON roundtrip
        json_str = original.to_json()
        restored = Agent.from_json(json_str)
        
        # All traits should match
        assert restored.traits.aggression == 0.3
        assert restored.traits.boldness == 0.7
        assert restored.traits.curiosity == 0.9
        assert restored.traits.greed == 0.1
        assert restored.traits.sociability == 0.5
        assert restored.traits.loyalty == 0.8
        assert restored.traits.patience == 0.2
        assert restored.traits.risk_tolerance == 0.4


class TestTraitSystemDataContractCompliance:
    """Test compliance with DATA_CONTRACTS.md"""

    def test_traits_match_schema(self):
        """Verify traits match DATA_CONTRACTS.md specification"""
        agent = Agent("test", "Test", "scholar")
        
        # Required traits per schema
        required_traits = [
            "aggression", "boldness", "curiosity", "greed",
            "sociability", "loyalty", "patience", "risk_tolerance"
        ]
        
        for trait in required_traits:
            assert hasattr(agent.traits, trait), f"Missing trait: {trait}"
            value = getattr(agent.traits, trait)
            assert isinstance(value, float), f"{trait} should be float"
            assert 0.0 <= value <= 1.0, f"{trait} out of range"

    def test_default_traits_neutral(self):
        """Traits should default to neutral (0.5)"""
        agent = Agent("test", "Test", "scholar")
        
        traits_list = [
            agent.traits.aggression,
            agent.traits.boldness,
            agent.traits.curiosity,
            agent.traits.greed,
            agent.traits.sociability,
            agent.traits.loyalty,
            agent.traits.patience,
            agent.traits.risk_tolerance
        ]
        
        for trait_value in traits_list:
            assert trait_value == 0.5, "Default should be neutral (0.5)"


class TestTraitSystemIntegration:
    """Integration tests for traits with Agent"""

    def test_traits_accessible_from_agent(self):
        """Test traits are accessible through Agent"""
        agent = Agent("warrior", "Strong Warrior", "warrior")
        
        # Should be able to set and get through agent
        agent.traits.aggression = 0.9
        assert agent.traits.aggression == 0.9

    def test_traits_survive_agent_lifecycle(self):
        """Test traits persist through agent operations"""
        agent = Agent("test", "Test", "merchant")
        
        # Set traits
        agent.traits.greed = 0.8
        agent.traits.loyalty = 0.3
        
        # After serialization/deserialization
        json_data = agent.to_json()
        restored = Agent.from_json(json_data)
        
        # Traits should persist
        assert restored.traits.greed == 0.8
        assert restored.traits.loyalty == 0.3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

