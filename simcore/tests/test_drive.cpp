#include <gtest/gtest.h>
#include "simcore/agent/DriveEngine.h"
#include "simcore/agent/NeedSystem.h"
#include "simcore/agent/TraitSystem.h"

using namespace simcore;

static TraitSet neutral_traits() {
    return TraitSystem::derive(TraitSystem::make_neutral(), nullptr, 0, nullptr, 0);
}

TEST(DriveEngine, NoUrgentNeeds_ReturnsEmpty) {
    NeedState state = NeedSystem::make_default_state(); // all at 100
    TraitSet  traits = neutral_traits();

    auto drives = DriveEngine::evaluate(state, traits);
    EXPECT_TRUE(drives.empty());
}

TEST(DriveEngine, SingleUrgentNeed_ReturnsOne) {
    NeedState state = NeedSystem::make_default_state();
    TraitSet  traits = neutral_traits();

    state.get(NeedType::Hunger).current_value = 20.0f; // below threshold of 30

    auto drives = DriveEngine::evaluate(state, traits);
    EXPECT_EQ(drives.size(), 1u);
    EXPECT_EQ(drives[0].need_type, NeedType::Hunger);
    EXPECT_GT(drives[0].score, 0.0f);
}

TEST(DriveEngine, MultipleUrgentNeeds_SortedByScore) {
    NeedState state = NeedSystem::make_default_state();
    TraitSet  traits = neutral_traits();

    // Hunger: just below threshold (mild urgency)
    state.get(NeedType::Hunger).current_value  = 28.0f;
    state.get(NeedType::Hunger).threshold      = 30.0f;

    // Thirst: near zero (high urgency)
    state.get(NeedType::Thirst).current_value  = 2.0f;
    state.get(NeedType::Thirst).threshold      = 30.0f;

    auto drives = DriveEngine::evaluate(state, traits);
    ASSERT_GE(drives.size(), 2u);
    EXPECT_EQ(drives[0].need_type, NeedType::Thirst); // more urgent first
}

TEST(DriveEngine, CriticalNeed_FloatsToTop) {
    NeedState state = NeedSystem::make_default_state();
    TraitSet  traits = neutral_traits();

    // Hunger just below threshold — some urgency
    state.get(NeedType::Hunger).current_value   = 25.0f;
    state.get(NeedType::Hunger).threshold       = 30.0f;
    state.get(NeedType::Hunger).critical_threshold = 10.0f;

    // Sleep critical (below critical_threshold)
    state.get(NeedType::Sleep).current_value    = 3.0f;
    state.get(NeedType::Sleep).threshold        = 25.0f;
    state.get(NeedType::Sleep).critical_threshold = 5.0f;

    auto drives = DriveEngine::evaluate(state, traits);
    ASSERT_GE(drives.size(), 2u);
    EXPECT_TRUE(drives[0].is_critical);
    EXPECT_EQ(drives[0].need_type, NeedType::Sleep);
}

TEST(DriveEngine, TopDrive_ReturnsHighestPriority) {
    NeedState state = NeedSystem::make_default_state();
    TraitSet  traits = neutral_traits();

    state.get(NeedType::Thirst).current_value = 5.0f;
    state.get(NeedType::Hunger).current_value = 20.0f;

    DriveScore top = DriveEngine::top_drive(state, traits);
    // Thirst should be more urgent (lower value relative to threshold)
    EXPECT_EQ(top.need_type, NeedType::Thirst);
}

TEST(DriveEngine, TopDrive_NoUrgency_ReturnsNone) {
    NeedState state = NeedSystem::make_default_state(); // all 100
    TraitSet  traits = neutral_traits();

    DriveScore top = DriveEngine::top_drive(state, traits);
    EXPECT_EQ(top.need_type, NeedType::None);
    EXPECT_FLOAT_EQ(top.score, 0.0f);
}

TEST(DriveEngine, HighPatience_ReducesHungerUrgency) {
    NeedState state = NeedSystem::make_default_state();

    // Impatient agent
    BaseTraits impatient_base = TraitSystem::make_neutral();
    impatient_base[TraitType::Patience] = 0.1f; // very impatient
    TraitSet impatient = TraitSystem::derive(impatient_base, nullptr, 0, nullptr, 0);

    // Patient agent
    BaseTraits patient_base = TraitSystem::make_neutral();
    patient_base[TraitType::Patience] = 0.9f; // very patient
    TraitSet patient = TraitSystem::derive(patient_base, nullptr, 0, nullptr, 0);

    state.get(NeedType::Hunger).current_value = 20.0f;

    auto impatient_drives = DriveEngine::evaluate(state, impatient);
    auto patient_drives   = DriveEngine::evaluate(state, patient);

    ASSERT_FALSE(impatient_drives.empty());
    ASSERT_FALSE(patient_drives.empty());
    // Impatient agent should score hunger higher
    EXPECT_GT(impatient_drives[0].score, patient_drives[0].score);
}

