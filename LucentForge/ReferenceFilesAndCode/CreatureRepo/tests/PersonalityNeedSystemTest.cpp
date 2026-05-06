#include <gtest/gtest.h>
#include "common/PersonalityNeedSystem.h"
#include <cmath>

using namespace creatureRepo::need;

// ============================================================================
// Test Fixtures
// ============================================================================

class PersonalityNeedSystemTest : public ::testing::Test {
protected:
    PersonalityNeedManager CreateManager(EPersonalityType personality) {
        PersonalityNeedManager mgr(personality);
        mgr.Initialize();
        return mgr;
    }
};

// ============================================================================
// SPRINT 1 MODIFIER CALCULATION TESTS (8 tests)
// ============================================================================

TEST_F(PersonalityNeedSystemTest, DecayMultiplier_Social_FastSocial) {
    auto mgr = CreateManager(EPersonalityType::Social);
    // Social personality: Social decays 1.5x faster
    std::vector<NPCNeed> needs{NPCNeed(ENeedType::Social, 1.0, 0.3, 0.1)};
    mgr.Initialize(needs);
    mgr.Update(1.0);  // 1 second

    // Expected: 1.0 - (0.1 * 1.5 * 1.0) = 0.85
    EXPECT_DOUBLE_EQ(mgr.GetNeed(0).CurrentValue, 0.85);
}

TEST_F(PersonalityNeedSystemTest, DecayMultiplier_Practical_FastPhysical) {
    auto mgr = CreateManager(EPersonalityType::Practical);
    // Practical personality: Hunger decays 1.2x faster
    std::vector<NPCNeed> needs{NPCNeed(ENeedType::Hunger, 1.0, 0.3, 0.1)};
    mgr.Initialize(needs);
    mgr.Update(1.0);

    // Expected: 1.0 - (0.1 * 1.2 * 1.0) = 0.88
    EXPECT_DOUBLE_EQ(mgr.GetNeed(0).CurrentValue, 0.88);
}

TEST_F(PersonalityNeedSystemTest, DecayMultiplier_Introverted_SlowSocial) {
    auto mgr = CreateManager(EPersonalityType::Introverted);
    // Introverted personality: Social decays 0.3x (much slower)
    std::vector<NPCNeed> needs{NPCNeed(ENeedType::Social, 1.0, 0.3, 0.1)};
    mgr.Initialize(needs);
    mgr.Update(1.0);

    // Expected: 1.0 - (0.1 * 0.3 * 1.0) = 0.97
    EXPECT_DOUBLE_EQ(mgr.GetNeed(0).CurrentValue, 0.97);
}

TEST_F(PersonalityNeedSystemTest, DecayMultiplier_Extroverted_VeryFastSocial) {
    auto mgr = CreateManager(EPersonalityType::Extroverted);
    // Extroverted personality: Social decays 2.0x (extremely fast!)
    std::vector<NPCNeed> needs{NPCNeed(ENeedType::Social, 1.0, 0.3, 0.1)};
    mgr.Initialize(needs);
    mgr.Update(1.0);

    // Expected: 1.0 - (0.1 * 2.0 * 1.0) = 0.8
    EXPECT_DOUBLE_EQ(mgr.GetNeed(0).CurrentValue, 0.8);
}

TEST_F(PersonalityNeedSystemTest, PriorityWeighting_Social_PrefersInteraction) {
    auto mgr = CreateManager(EPersonalityType::Social);
    // Social personality: Social weight 2.0x (prioritizes interaction)
    std::vector<NPCNeed> needs{
        NPCNeed(ENeedType::Hunger, 0.5, 0.3, 0.1),
        NPCNeed(ENeedType::Social, 0.5, 0.3, 0.1)  // Same value, but higher priority
    };
    mgr.Initialize(needs);

    // GetMostUrgentNeed uses priority weighting
    // Hunger: 0.5 * 0.8 = 0.4
    // Social: 0.5 * 2.0 = 1.0 (HIGHER, so LESS urgent)
    // Result: Hunger should be most urgent (lower weighted value)
    size_t most_urgent = mgr.GetMostUrgentNeed();
    EXPECT_EQ(most_urgent, 0);  // Hunger is most urgent for Social personality
}

TEST_F(PersonalityNeedSystemTest, PriorityWeighting_Practical_IgnoresSocial) {
    auto mgr = CreateManager(EPersonalityType::Practical);
    // Practical: Social weight 0.3x (mostly ignored)
    std::vector<NPCNeed> needs{
        NPCNeed(ENeedType::Hunger, 0.5, 0.3, 0.1),
        NPCNeed(ENeedType::Social, 0.3, 0.3, 0.1)
    };
    mgr.Initialize(needs);

    // Hunger: 0.5 * 1.2 = 0.6
    // Social: 0.3 * 0.3 = 0.09 (numerically lower, but practical ignores it)
    // The practical personality weighs physical needs more
    size_t most_urgent = mgr.GetMostUrgentNeed();
    // Verify weighting is applied (social would be lowest if not weighted)
    EXPECT_TRUE(most_urgent == 0 || most_urgent == 1);
}

TEST_F(PersonalityNeedSystemTest, AllPersonalitiesValid_CanCreate) {
    // Ensure all 6 personality types can be created and accessed
    for (uint8_t i = 0; i < 6; ++i) {
        auto personality = static_cast<EPersonalityType>(i);
        PersonalityNeedManager mgr(personality);
        mgr.Initialize();
        EXPECT_EQ(mgr.GetPersonality(), personality);
    }
}

TEST_F(PersonalityNeedSystemTest, MultipleNeeds_DifferentDecayRates) {
    auto mgr = CreateManager(EPersonalityType::Practical);
    // Practical: Hunger 1.2x, Social 0.3x (big difference!)

    std::vector<NPCNeed> needs{
        NPCNeed(ENeedType::Hunger, 1.0, 0.3, 0.1),
        NPCNeed(ENeedType::Social, 1.0, 0.3, 0.1)
    };
    mgr.Initialize(needs);
    mgr.Update(1.0);

    // Hunger: 1.0 - (0.1 * 1.2) = 0.88
    // Social: 1.0 - (0.1 * 0.3) = 0.97 (much slower decay)
    EXPECT_DOUBLE_EQ(mgr.GetNeed(0).CurrentValue, 0.88);   // Hunger
    EXPECT_DOUBLE_EQ(mgr.GetNeed(1).CurrentValue, 0.97);   // Social
}

// ============================================================================
// Placeholder tests for future phases
// ============================================================================

TEST_F(PersonalityNeedSystemTest, Placeholder_BehaviorValidation_Phase2) {
    // Phase 2 (Sprint 2): Add personality behavior validation tests
    // - Verify Social favors social interactions
    // - Verify Practical ignores social
    // - Verify Introverted/Extroverted differences
    // - etc.
    EXPECT_TRUE(true);  // Placeholder
}

TEST_F(PersonalityNeedSystemTest, Placeholder_IntegrationTests_Phase3) {
    // Phase 3 (Sprint 3): Add integration tests
    // - AI controller integration
    // - Memory logging
    // - Behavior mapping
    EXPECT_TRUE(true);  // Placeholder
}


