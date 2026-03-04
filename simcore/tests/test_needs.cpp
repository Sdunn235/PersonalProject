#include <gtest/gtest.h>
#include "simcore/agent/NeedSystem.h"

using namespace simcore;

TEST(NeedSystem, Tick_DecaysValue) {
    NeedState state = NeedSystem::make_default_state();
    NeedRecord& hunger = state.get(NeedType::Hunger);
    hunger.current_value    = 100.0f;
    hunger.decay_rate_per_sec = 2.0f;

    NeedSystem::tick(state, 1.0f);
    EXPECT_FLOAT_EQ(hunger.current_value, 98.0f);
}

TEST(NeedSystem, Tick_ClampsAtZero) {
    NeedState state = NeedSystem::make_default_state();
    NeedRecord& r = state.get(NeedType::Hunger);
    r.current_value     = 1.0f;
    r.decay_rate_per_sec = 10.0f;

    NeedSystem::tick(state, 1.0f);
    EXPECT_FLOAT_EQ(r.current_value, 0.0f);
}

TEST(NeedSystem, Tick_NeverExceeds100) {
    NeedState state = NeedSystem::make_default_state();
    NeedRecord& r = state.get(NeedType::Thirst);
    r.current_value     = 100.0f;
    r.decay_rate_per_sec = -5.0f; // negative decay = healing

    NeedSystem::tick(state, 1.0f);
    EXPECT_FLOAT_EQ(r.current_value, 100.0f);
}

TEST(NeedSystem, IsUrgent_BelowThreshold) {
    NeedRecord r = NeedSystem::make_default(NeedType::Hunger);
    r.current_value = 25.0f;
    r.threshold     = 30.0f;
    EXPECT_TRUE(NeedSystem::is_urgent(r));
}

TEST(NeedSystem, IsUrgent_AtThreshold) {
    NeedRecord r = NeedSystem::make_default(NeedType::Hunger);
    r.current_value = 30.0f;
    r.threshold     = 30.0f;
    EXPECT_TRUE(NeedSystem::is_urgent(r));
}

TEST(NeedSystem, IsUrgent_AboveThreshold) {
    NeedRecord r = NeedSystem::make_default(NeedType::Hunger);
    r.current_value = 50.0f;
    r.threshold     = 30.0f;
    EXPECT_FALSE(NeedSystem::is_urgent(r));
}

TEST(NeedSystem, IsCritical) {
    NeedRecord r = NeedSystem::make_default(NeedType::Thirst);
    r.current_value      = 4.0f;
    r.critical_threshold = 5.0f;
    EXPECT_TRUE(NeedSystem::is_critical(r));
}

TEST(NeedSystem, Satisfy_AddsValue) {
    NeedRecord r = NeedSystem::make_default(NeedType::Hunger);
    r.current_value = 20.0f;
    NeedSystem::satisfy(r, 30.0f);
    EXPECT_FLOAT_EQ(r.current_value, 50.0f);
}

TEST(NeedSystem, Satisfy_ClampsAt100) {
    NeedRecord r = NeedSystem::make_default(NeedType::Hunger);
    r.current_value = 90.0f;
    NeedSystem::satisfy(r, 50.0f);
    EXPECT_FLOAT_EQ(r.current_value, 100.0f);
}

TEST(NeedSystem, MakeDefaultState_AllNeedsStart100) {
    NeedState state = NeedSystem::make_default_state();
    for (int i = 1; i < NEED_COUNT; ++i) {
        EXPECT_FLOAT_EQ(state.needs[i].current_value, 100.0f)
            << "Need index " << i << " did not start at 100";
    }
}

TEST(NeedSystem, MakeDefaultState_CorrectNeedTypes) {
    NeedState state = NeedSystem::make_default_state();
    EXPECT_EQ(state.get(NeedType::Hunger).need_type,  NeedType::Hunger);
    EXPECT_EQ(state.get(NeedType::Thirst).need_type,  NeedType::Thirst);
    EXPECT_EQ(state.get(NeedType::Safety).need_type,  NeedType::Safety);
}

// Regression: matches Blueprint UpdateNeeds formula
// new_value = FClamp(CurrentValue - DecayRate * DeltaTime, 0, 100)
TEST(NeedSystem, MatchesBlueprintDecayFormula) {
    NeedRecord r;
    r.need_type           = NeedType::Hunger;
    r.current_value       = 80.0f;
    r.decay_rate_per_sec  = 3.5f;

    NeedState state;
    state.get(NeedType::Hunger) = r;
    NeedSystem::tick(state, 2.0f); // 2-second SimStep (matches Blueprint 2s timer)

    float expected = 80.0f - 3.5f * 2.0f; // = 73.0
    EXPECT_FLOAT_EQ(state.get(NeedType::Hunger).current_value, expected);
}

