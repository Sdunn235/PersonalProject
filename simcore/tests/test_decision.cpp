#include <gtest/gtest.h>
#include "simcore/agent/DecisionEngine.h"
#include "simcore/agent/NeedSystem.h"
#include "simcore/agent/TraitSystem.h"

using namespace simcore;

static TraitSet neutral_traits() {
    return TraitSystem::derive(TraitSystem::make_neutral(), nullptr, 0, nullptr, 0);
}

static WorldSnapshot empty_world() {
    WorldSnapshot w;
    w.is_safe = true;
    return w;
}

static WorldSnapshot world_with_food(ResourceID food_id, float dist = 50.0f) {
    WorldSnapshot w;
    w.is_safe = true;
    int idx = static_cast<int>(NeedType::Hunger);
    w.nearest[idx].resource_id = food_id;
    w.nearest[idx].need_type   = NeedType::Hunger;
    w.nearest[idx].distance    = dist;
    w.nearest[idx].is_valid    = true;
    return w;
}

TEST(DecisionEngine, FullyFed_NoUrgency_Idles) {
    NeedState state  = NeedSystem::make_default_state(); // all 100
    TraitSet  traits = neutral_traits();

    ActionIntent intent = DecisionEngine::decide(1u, state, traits, empty_world());
    EXPECT_EQ(intent.action_type, ActionType::Idle);
}

TEST(DecisionEngine, HungryWithSource_MovesToResource) {
    NeedState state  = NeedSystem::make_default_state();
    TraitSet  traits = neutral_traits();

    state.get(NeedType::Hunger).current_value = 10.0f;

    ActionIntent intent = DecisionEngine::decide(1u, state, traits, world_with_food(42u));
    EXPECT_EQ(intent.action_type,   ActionType::MoveToResource);
    EXPECT_EQ(intent.need_context,  NeedType::Hunger);
    EXPECT_EQ(intent.target_id,     42u);
    EXPECT_GT(intent.priority,      0.0f);
}

TEST(DecisionEngine, HungryNoSource_Seeks) {
    NeedState state  = NeedSystem::make_default_state();
    TraitSet  traits = neutral_traits();

    state.get(NeedType::Hunger).current_value = 10.0f;

    ActionIntent intent = DecisionEngine::decide(1u, state, traits, empty_world());
    EXPECT_EQ(intent.action_type,  ActionType::Seek);
    EXPECT_EQ(intent.need_context, NeedType::Hunger);
}

TEST(DecisionEngine, Unsafe_CowardlyAgent_Flees) {
    NeedState state  = NeedSystem::make_default_state();

    // Very cowardly: low risk tolerance + low boldness
    BaseTraits coward_base = TraitSystem::make_neutral();
    coward_base[TraitType::RiskTolerance] = 0.1f;
    coward_base[TraitType::Boldness]      = 0.1f;
    TraitSet coward_traits = TraitSystem::derive(coward_base, nullptr, 0, nullptr, 0);

    WorldSnapshot danger;
    danger.is_safe        = false;
    danger.threat_distance = 30.0f;

    ActionIntent intent = DecisionEngine::decide(1u, state, coward_traits, danger);
    EXPECT_EQ(intent.action_type,  ActionType::Flee);
    EXPECT_EQ(intent.need_context, NeedType::Safety);
    EXPECT_FLOAT_EQ(intent.priority, 999.0f);
}

TEST(DecisionEngine, Unsafe_BoldAgent_DoesNotFlee) {
    NeedState state = NeedSystem::make_default_state();

    // Very bold: high risk tolerance + high boldness
    BaseTraits bold_base = TraitSystem::make_neutral();
    bold_base[TraitType::RiskTolerance] = 0.9f;
    bold_base[TraitType::Boldness]      = 0.9f;
    TraitSet bold_traits = TraitSystem::derive(bold_base, nullptr, 0, nullptr, 0);

    WorldSnapshot danger;
    danger.is_safe = false;

    ActionIntent intent = DecisionEngine::decide(1u, state, bold_traits, danger);
    EXPECT_NE(intent.action_type, ActionType::Flee);
}

TEST(DecisionEngine, AgentID_PropagatedToIntent) {
    NeedState state  = NeedSystem::make_default_state();
    TraitSet  traits = neutral_traits();

    ActionIntent intent = DecisionEngine::decide(77u, state, traits, empty_world());
    EXPECT_EQ(intent.agent_id, 77u);
}

TEST(DecisionEngine, CriticalNeed_HighPriority) {
    NeedState state  = NeedSystem::make_default_state();
    TraitSet  traits = neutral_traits();

    // Critical thirst — near zero
    state.get(NeedType::Thirst).current_value       = 1.0f;
    state.get(NeedType::Thirst).threshold           = 30.0f;
    state.get(NeedType::Thirst).critical_threshold  = 5.0f;

    ActionIntent intent = DecisionEngine::decide(1u, state, traits, empty_world());
    EXPECT_GT(intent.priority, 0.5f);
    EXPECT_EQ(intent.need_context, NeedType::Thirst);
}

