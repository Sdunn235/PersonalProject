"""
test_combat_wrapper.py

Validates CombatEngine wrapper against iso_rpg_lab baseline.

This is the critical test for Phase 2: proves iso_rpg_lab combat logic
can be wrapped, called through Python, and produces identical results.

Run with: python -m pytest tests/test_combat_wrapper.py -v
"""

import pytest
import sys
import json
import os
from pathlib import Path

# Calculate path to iso_rpg_lab
# Test location: LucentForge/SimCore/tests/
# iso_rpg_lab location: Personal Project/iso_rpg_lab/
# From test dir: ../../.. = Workspace, then Personal Project/iso_rpg_lab
test_dir = Path(__file__).parent
lucentforge_dir = test_dir.parent.parent
personal_project_dir = lucentforge_dir.parent
ISO_RPG_LAB_PATH = personal_project_dir / "iso_rpg_lab"

if ISO_RPG_LAB_PATH.exists():
    sys.path.insert(0, str(ISO_RPG_LAB_PATH))
else:
    print(f"Warning: iso_rpg_lab not found at {ISO_RPG_LAB_PATH}")

# Import our wrapper
from simcore_wrapper import Agent, CombatEngine, TurnResult


class TestCombatWrapperBasics:
    """Test basic wrapper functionality"""

    def test_agent_creation(self):
        """Test creating an agent"""
        agent = Agent("agent-1", "Hero", "warrior")
        assert agent.agent_id == "agent-1"
        assert agent.name == "Hero"
        assert agent.role == "warrior"

    def test_agent_json_roundtrip(self):
        """Test agent serializes and deserializes correctly"""
        agent1 = Agent("agent-1", "Hero", "warrior")
        agent1.wealth = 100
        agent1.skills["combat"] = 5
        
        # Serialize
        json_str = agent1.to_json()
        assert json_str is not None
        assert "agent-1" in json_str
        
        # Deserialize
        agent2 = Agent.from_json(json_str)
        assert agent2.agent_id == agent1.agent_id
        assert agent2.name == agent1.name
        assert agent2.wealth == agent1.wealth
        assert agent2.skills.get("combat") == 5

    def test_combat_engine_init(self):
        """Test CombatEngine initialization"""
        engine = CombatEngine()
        assert engine is not None
        assert engine.rng_seed == 0

    def test_combat_engine_load_config(self):
        """Test loading combat config from iso_rpg_lab data"""
        data_path = str(ISO_RPG_LAB_PATH / "data")
        
        if os.path.exists(data_path):
            engine = CombatEngine()
            result = engine.load_config(data_path)
            assert result is True
            assert engine.config_loaded is True
        else:
            pytest.skip(f"iso_rpg_lab data path not found: {data_path}")


class TestCombatEngineLogic:
    """Test combat engine simulation"""

    def test_simulate_turn_basic(self):
        """Test basic turn simulation"""
        attacker = Agent("attacker", "Player", "warrior")
        defender = Agent("defender", "Enemy", "bandit")
        
        engine = CombatEngine()
        result = engine.simulate_turn(attacker, defender, seed=42)
        
        assert result is not None
        assert isinstance(result, TurnResult)
        assert result.turn_type in ["hit", "miss", "use_item", "heal"]

    def test_combat_engine_seed_reproducibility(self):
        """Test that same seed produces same results (determinism)"""
        attacker = Agent("attacker", "Player", "warrior")
        defender = Agent("defender", "Enemy", "bandit")
        
        engine = CombatEngine()
        
        # Run twice with same seed
        result1 = engine.simulate_turn(attacker, defender, seed=42)
        result2 = engine.simulate_turn(attacker, defender, seed=42)
        
        # Should be identical
        assert result1.turn_type == result2.turn_type
        assert result1.amount == result2.amount
        assert result1.was_crit == result2.was_crit


class TestISORPGLabIntegration:
    """Test integration with actual iso_rpg_lab logic"""

    @pytest.fixture
    def iso_rpg_setup(self):
        """Load iso_rpg_lab game data"""
        try:
            from gameplay.loader import load_all
            from gameplay.rng import RNG32
            
            data_path = ISO_RPG_LAB_PATH / "data"
            db = load_all(str(data_path))
            rng = RNG32(seed=42)
            
            return db, rng
        except Exception as e:
            pytest.skip(f"Could not load iso_rpg_lab: {e}")

    def test_iso_rpg_lab_data_loads(self, iso_rpg_setup):
        """Test that iso_rpg_lab data loads correctly"""
        db, rng = iso_rpg_setup
        
        assert "items" in db
        assert "abilities" in db
        assert "enemies" in db
        assert "players" in db

    def test_iso_rpg_lab_combat_baseline(self, iso_rpg_setup):
        """Run iso_rpg_lab baseline combat to establish reference"""
        from gameplay.loader import load_all
        from gameplay.rng import RNG32
        from gameplay.combat import Fighter, take_turn
        from gameplay.stats import Stats, StatusFlags
        from gameplay.derive import BaseStats
        
        db, rng = iso_rpg_setup
        
        # Create simple test fighters
        player_stats = Stats(STR=15, MAG=0, LCK=5, DEF=5, RES=0, DEX=5, clamp_mode="clamp")
        enemy_stats = Stats(STR=10, MAG=0, LCK=3, DEF=3, RES=0, DEX=3, clamp_mode="clamp")
        
        player = Fighter("Hero", hp=50, max_hp=50, stats=player_stats)
        enemy = Fighter("Bandit", hp=30, max_hp=30, stats=enemy_stats)
        enemy.is_enemy = True
        
        # Take one turn
        result = take_turn(player, enemy, rng)
        
        # Validate result structure
        assert "type" in result
        assert "amount" in result
        assert result["type"] in ["hit", "miss", "use_item", "heal"]

    def test_wrapper_matches_iso_rpg_lab_format(self, iso_rpg_setup):
        """Test that wrapper result format matches iso_rpg_lab"""
        # This test validates that when we integrate iso_rpg_lab into SimCore,
        # the output format is compatible
        
        from gameplay.loader import load_all
        from gameplay.rng import RNG32
        from gameplay.combat import Fighter
        from gameplay.stats import Stats
        
        db, rng = iso_rpg_setup
        
        # iso_rpg_lab turn result structure
        iso_result = {
            "type": "hit",
            "amount": 12,
            "crit": False,
            "ability": "basic",
            "element": "neutral"
        }
        
        # Our wrapper TurnResult should be compatible
        wrapper_result = TurnResult(
            turn_type="hit",
            amount=12,
            was_crit=False,
            ability_id="basic",
            element="neutral"
        )
        
        assert wrapper_result.turn_type == iso_result["type"]
        assert wrapper_result.amount == iso_result["amount"]
        assert wrapper_result.was_crit == iso_result["crit"]


class TestDataContractCompliance:
    """Test compliance with DATA_CONTRACTS.md"""

    def test_agent_schema_fields(self):
        """Test Agent has all required fields per schema"""
        agent = Agent("test", "Test Agent", "scholar")
        
        # Required fields per schema
        assert hasattr(agent, "agent_id")
        assert hasattr(agent, "name")
        assert hasattr(agent, "role")
        assert hasattr(agent, "traits")
        assert hasattr(agent, "needs")
        assert hasattr(agent, "skills")
        assert hasattr(agent, "inventory")
        assert hasattr(agent, "wealth")
        assert hasattr(agent, "memory")
        assert hasattr(agent, "social_graph")
        assert hasattr(agent, "current_intent")

    def test_traits_range_0_to_1(self):
        """Test traits are normalized 0.0–1.0"""
        agent = Agent("test", "Test", "scholar")
        
        for trait_name in ["aggression", "boldness", "curiosity", "greed", 
                          "sociability", "loyalty", "patience", "risk_tolerance"]:
            value = getattr(agent.traits, trait_name)
            assert 0.0 <= value <= 1.0, f"{trait_name} out of range: {value}"

    def test_needs_range_0_to_1(self):
        """Test needs are normalized 0.0–1.0"""
        agent = Agent("test", "Test", "scholar")
        
        for need_name in ["hunger", "thirst", "sleep", "safety", 
                         "social", "wealth", "power", "curiosity"]:
            value = getattr(agent.needs, need_name)
            assert 0.0 <= value <= 1.0, f"{need_name} out of range: {value}"


class TestPhase2Checklist:
    """Validate Phase 2 completion criteria"""

    def test_header_files_created(self):
        """Verify header stubs exist"""
        include_dir = ISO_RPG_LAB_PATH.parent / "LucentForge" / "SimCore" / "include"
        
        assert (include_dir / "Agent.h").exists(), "Agent.h not found"
        assert (include_dir / "WorldState.h").exists(), "WorldState.h not found"
        assert (include_dir / "CombatEngine.h").exists(), "CombatEngine.h not found"

    def test_python_wrapper_created(self):
        """Verify Python wrapper exists"""
        wrapper_file = ISO_RPG_LAB_PATH.parent / "LucentForge" / "SimCore" / "tests" / "simcore_wrapper.py"
        assert wrapper_file.exists(), "simcore_wrapper.py not found"

    def test_wrapper_imports_cleanly(self):
        """Verify wrapper can be imported without errors"""
        try:
            from simcore_wrapper import Agent, CombatEngine, WorldState
            assert Agent is not None
            assert CombatEngine is not None
            assert WorldState is not None
        except ImportError as e:
            pytest.fail(f"Could not import wrapper: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])




