#include <gtest/gtest.h>
#include "common/NeedSystem.h"
#include <cmath>

using namespace creatureRepo::need;

// ============================================================================
// Test Fixtures
// ============================================================================

class NeedSystemTest : public ::testing::Test {
protected:
    NeedManager manager;
};

class NeedStructTest : public ::testing::Test {
protected:
    NPCNeed need{ENeedType::Hunger, 1.0, 0.3, 0.1};
};

// ============================================================================
// NPCNeed Struct Tests
// ============================================================================

TEST_F(NeedStructTest, DefaultConstructor) {
    NPCNeed defaultNeed;
    EXPECT_EQ(defaultNeed.NeedType, ENeedType::Hunger);
    EXPECT_EQ(defaultNeed.CurrentValue, 1.0);
    EXPECT_EQ(defaultNeed.Threshold, 0.3);
    EXPECT_EQ(defaultNeed.DecayRatePerSecond, 0.1);
}

TEST_F(NeedStructTest, CustomConstructor) {
    NPCNeed customNeed(ENeedType::Thirst, 0.5, 0.2, 0.15);
    EXPECT_EQ(customNeed.NeedType, ENeedType::Thirst);
    EXPECT_EQ(customNeed.CurrentValue, 0.5);
    EXPECT_EQ(customNeed.Threshold, 0.2);
    EXPECT_EQ(customNeed.DecayRatePerSecond, 0.15);
}

TEST_F(NeedStructTest, IsUrgent_BelowThreshold) {
    need.CurrentValue = 0.2;
    need.Threshold = 0.3;
    EXPECT_TRUE(need.IsUrgent());
}

TEST_F(NeedStructTest, IsUrgent_AtThreshold) {
    need.CurrentValue = 0.3;
    need.Threshold = 0.3;
    EXPECT_TRUE(need.IsUrgent());  // <= comparison
}

TEST_F(NeedStructTest, IsUrgent_AboveThreshold) {
    need.CurrentValue = 0.4;
    need.Threshold = 0.3;
    EXPECT_FALSE(need.IsUrgent());
}

TEST_F(NeedStructTest, IsUrgent_Satisfied) {
    need.CurrentValue = 1.0;
    need.Threshold = 0.3;
    EXPECT_FALSE(need.IsUrgent());
}

// ============================================================================
// NeedManager Initialization Tests
// ============================================================================

TEST_F(NeedSystemTest, DefaultInitialization) {
    EXPECT_FALSE(manager.IsInitialized());
    manager.Initialize();
    EXPECT_TRUE(manager.IsInitialized());
    EXPECT_EQ(manager.GetNeedCount(), static_cast<size_t>(ENeedType::Count));
}

TEST_F(NeedSystemTest, InitializeWithCustomNeeds) {
    std::vector<NPCNeed> customNeeds{
        NPCNeed(ENeedType::Hunger, 0.8, 0.2, 0.12),
        NPCNeed(ENeedType::Thirst, 0.9, 0.25, 0.08),
    };

    manager.Initialize(customNeeds);
    EXPECT_TRUE(manager.IsInitialized());
    EXPECT_EQ(manager.GetNeedCount(), 2);
    EXPECT_EQ(manager.GetNeed(0).NeedType, ENeedType::Hunger);
    EXPECT_EQ(manager.GetNeed(1).NeedType, ENeedType::Thirst);
}

TEST_F(NeedSystemTest, InitializeWithEmpty_ThrowsException) {
    std::vector<NPCNeed> emptyNeeds;
    EXPECT_THROW(manager.Initialize(emptyNeeds), std::invalid_argument);
}

TEST_F(NeedSystemTest, DefaultInitializationCreatesAllNeeds) {
    manager.Initialize();

    // Check all need types are created
    for (uint8_t i = 0; i < static_cast<uint8_t>(ENeedType::Count); ++i) {
        ENeedType type = static_cast<ENeedType>(i);
        const NPCNeed& need = manager.GetNeedByType(type);
        EXPECT_EQ(need.NeedType, type);
        EXPECT_EQ(need.CurrentValue, 1.0);
        EXPECT_EQ(need.Threshold, 0.3);
        EXPECT_EQ(need.DecayRatePerSecond, 0.1);
    }
}

// ============================================================================
// Time-Based Decay Tests (Critical for Blueprint Compatibility)
// ============================================================================

TEST_F(NeedSystemTest, UpdateWithNoTime) {
    manager.Initialize();
    const NPCNeed& beforeNeed = manager.GetNeed(0);
    double beforeValue = beforeNeed.CurrentValue;

    manager.Update(0.0);

    const NPCNeed& afterNeed = manager.GetNeed(0);
    EXPECT_EQ(afterNeed.CurrentValue, beforeValue);
}

TEST_F(NeedSystemTest, UpdateWithPositiveDelta) {
    std::vector<NPCNeed> needs{
        NPCNeed(ENeedType::Hunger, 1.0, 0.3, 0.1),
    };
    manager.Initialize(needs);

    // After 1 second with decay rate 0.1: 1.0 - (0.1 * 1.0) = 0.9
    manager.Update(1.0);
    EXPECT_DOUBLE_EQ(manager.GetNeed(0).CurrentValue, 0.9);
}

TEST_F(NeedSystemTest, UpdateMultipleSteps) {
    std::vector<NPCNeed> needs{
        NPCNeed(ENeedType::Hunger, 1.0, 0.3, 0.1),
    };
    manager.Initialize(needs);

    // After 5 seconds: 1.0 - (0.1 * 5.0) = 0.5
    manager.Update(5.0);
    EXPECT_DOUBLE_EQ(manager.GetNeed(0).CurrentValue, 0.5);

    // After another 5 seconds: 0.5 - (0.1 * 5.0) = 0.0
    manager.Update(5.0);
    EXPECT_DOUBLE_EQ(manager.GetNeed(0).CurrentValue, 0.0);
}

TEST_F(NeedSystemTest, UpdateClampsBelowZero) {
    std::vector<NPCNeed> needs{
        NPCNeed(ENeedType::Hunger, 0.05, 0.3, 0.1),
    };
    manager.Initialize(needs);

    // 0.05 - (0.1 * 1.0) = -0.05, should be clamped to 0.0
    manager.Update(1.0);
    EXPECT_DOUBLE_EQ(manager.GetNeed(0).CurrentValue, 0.0);
}

TEST_F(NeedSystemTest, UpdateClampsAboveOne) {
    // Manually set a need above 1.0 (shouldn't happen in normal use)
    std::vector<NPCNeed> needs{
        NPCNeed(ENeedType::Hunger, 1.5, 0.3, 0.1),
    };
    manager.Initialize(needs);

    // This shouldn't decay below the clamped value
    manager.Update(0.1);
    EXPECT_LE(manager.GetNeed(0).CurrentValue, 1.0);
}

TEST_F(NeedSystemTest, UpdateNegativeDelta_ThrowsException) {
    manager.Initialize();
    EXPECT_THROW(manager.Update(-1.0), std::invalid_argument);
}

TEST_F(NeedSystemTest, UpdateNotInitialized_ThrowsException) {
    EXPECT_THROW(manager.Update(1.0), std::runtime_error);
}

TEST_F(NeedSystemTest, UpdateMultipleNeeds) {
    std::vector<NPCNeed> needs{
        NPCNeed(ENeedType::Hunger, 1.0, 0.3, 0.1),
        NPCNeed(ENeedType::Thirst, 1.0, 0.3, 0.2),
        NPCNeed(ENeedType::Rest, 1.0, 0.3, 0.05),
    };
    manager.Initialize(needs);

    manager.Update(1.0);

    // Hunger: 1.0 - 0.1 = 0.9
    EXPECT_DOUBLE_EQ(manager.GetNeed(0).CurrentValue, 0.9);
    // Thirst: 1.0 - 0.2 = 0.8
    EXPECT_DOUBLE_EQ(manager.GetNeed(1).CurrentValue, 0.8);
    // Rest: 1.0 - 0.05 = 0.95
    EXPECT_DOUBLE_EQ(manager.GetNeed(2).CurrentValue, 0.95);
}

TEST_F(NeedSystemTest, DecayWithSmallDeltaTime) {
    std::vector<NPCNeed> needs{
        NPCNeed(ENeedType::Hunger, 1.0, 0.3, 1.0),
    };
    manager.Initialize(needs);

    // 1.0 - (1.0 * 0.01) = 0.99
    manager.Update(0.01);
    EXPECT_DOUBLE_EQ(manager.GetNeed(0).CurrentValue, 0.99);
}

// ============================================================================
// Threshold Detection Tests
// ============================================================================

TEST_F(NeedSystemTest, GetUrgentNeeds_None) {
    manager.Initialize();
    // All needs start at 1.0, threshold 0.3, so none are urgent
    auto urgent = manager.GetUrgentNeeds();
    EXPECT_TRUE(urgent.empty());
}

TEST_F(NeedSystemTest, GetUrgentNeeds_One) {
    std::vector<NPCNeed> needs{
        NPCNeed(ENeedType::Hunger, 0.2, 0.3, 0.1),
        NPCNeed(ENeedType::Thirst, 0.8, 0.3, 0.1),
    };
    manager.Initialize(needs);

    auto urgent = manager.GetUrgentNeeds();
    EXPECT_EQ(urgent.size(), 1);
    EXPECT_EQ(urgent[0], 0);  // Hunger is urgent
}

TEST_F(NeedSystemTest, GetUrgentNeeds_Multiple) {
    std::vector<NPCNeed> needs{
        NPCNeed(ENeedType::Hunger, 0.2, 0.3, 0.1),
        NPCNeed(ENeedType::Thirst, 0.25, 0.3, 0.1),
        NPCNeed(ENeedType::Rest, 0.8, 0.3, 0.1),
    };
    manager.Initialize(needs);

    auto urgent = manager.GetUrgentNeeds();
    EXPECT_EQ(urgent.size(), 2);
    EXPECT_EQ(urgent[0], 0);
    EXPECT_EQ(urgent[1], 1);
}

TEST_F(NeedSystemTest, GetUrgentNeeds_NotInitialized_ThrowsException) {
    EXPECT_THROW(manager.GetUrgentNeeds(), std::runtime_error);
}

TEST_F(NeedSystemTest, GetMostUrgentNeed) {
    std::vector<NPCNeed> needs{
        NPCNeed(ENeedType::Hunger, 0.5, 0.3, 0.1),
        NPCNeed(ENeedType::Thirst, 0.1, 0.3, 0.1),  // Most urgent
        NPCNeed(ENeedType::Rest, 0.3, 0.3, 0.1),
    };
    manager.Initialize(needs);

    size_t mostUrgent = manager.GetMostUrgentNeed();
    EXPECT_EQ(mostUrgent, 1);  // Thirst is most urgent
}

TEST_F(NeedSystemTest, GetMostUrgentNeed_NotInitialized_ThrowsException) {
    EXPECT_THROW(manager.GetMostUrgentNeed(), std::runtime_error);
}

// ============================================================================
// Accessor Tests
// ============================================================================

TEST_F(NeedSystemTest, GetNeedByIndex) {
    manager.Initialize();
    const NPCNeed& need = manager.GetNeed(0);
    EXPECT_EQ(need.NeedType, ENeedType::Hunger);
}

TEST_F(NeedSystemTest, GetNeedByIndex_OutOfRange_ThrowsException) {
    manager.Initialize();
    EXPECT_THROW(manager.GetNeed(100), std::out_of_range);
}

TEST_F(NeedSystemTest, GetNeedByType) {
    manager.Initialize();
    const NPCNeed& thirstNeed = manager.GetNeedByType(ENeedType::Thirst);
    EXPECT_EQ(thirstNeed.NeedType, ENeedType::Thirst);
}

TEST_F(NeedSystemTest, GetNeedByType_NotFound_ThrowsException) {
    std::vector<NPCNeed> needs{
        NPCNeed(ENeedType::Hunger, 1.0, 0.3, 0.1),
    };
    manager.Initialize(needs);
    EXPECT_THROW(manager.GetNeedByType(ENeedType::Thirst), std::runtime_error);
}

TEST_F(NeedSystemTest, MutableNeedByIndex) {
    manager.Initialize();
    NPCNeed& need = manager.MutableNeed(0);
    need.CurrentValue = 0.5;
    EXPECT_DOUBLE_EQ(manager.GetNeed(0).CurrentValue, 0.5);
}

TEST_F(NeedSystemTest, MutableNeedByType) {
    manager.Initialize();
    NPCNeed& need = manager.MutableNeedByType(ENeedType::Hunger);
    need.CurrentValue = 0.5;
    EXPECT_DOUBLE_EQ(manager.GetNeedByType(ENeedType::Hunger).CurrentValue, 0.5);
}

// ============================================================================
// Need Satisfaction Tests
// ============================================================================

TEST_F(NeedSystemTest, SatisfyNeed) {
    std::vector<NPCNeed> needs{
        NPCNeed(ENeedType::Hunger, 0.2, 0.3, 0.1),
    };
    manager.Initialize(needs);

    manager.SatisfyNeed(0);
    EXPECT_DOUBLE_EQ(manager.GetNeed(0).CurrentValue, 1.0);
}

TEST_F(NeedSystemTest, SatisfyNeedByType) {
    manager.Initialize();
    NPCNeed& hunger = manager.MutableNeedByType(ENeedType::Hunger);
    hunger.CurrentValue = 0.2;

    manager.SatisfyNeedByType(ENeedType::Hunger);
    EXPECT_DOUBLE_EQ(manager.GetNeedByType(ENeedType::Hunger).CurrentValue, 1.0);
}

TEST_F(NeedSystemTest, SatisfyNeed_InvalidIndex_ThrowsException) {
    manager.Initialize();
    EXPECT_THROW(manager.SatisfyNeed(100), std::out_of_range);
}

TEST_F(NeedSystemTest, SatisfyNeedByType_NotFound_ThrowsException) {
    std::vector<NPCNeed> needs{
        NPCNeed(ENeedType::Hunger, 0.5, 0.3, 0.1),
    };
    manager.Initialize(needs);
    EXPECT_THROW(manager.SatisfyNeedByType(ENeedType::Thirst), std::runtime_error);
}

// ============================================================================
// State Queries
// ============================================================================

TEST_F(NeedSystemTest, GetNeedCount) {
    manager.Initialize();
    EXPECT_EQ(manager.GetNeedCount(), static_cast<size_t>(ENeedType::Count));
}

TEST_F(NeedSystemTest, GetAllNeeds) {
    manager.Initialize();
    const auto& allNeeds = manager.GetAllNeeds();
    EXPECT_EQ(allNeeds.size(), manager.GetNeedCount());
}

// ============================================================================
// Persistence and Instance Variable Tests
// ============================================================================

TEST_F(NeedSystemTest, PersistenceAcrossUpdates) {
    // Simulates an NPC maintaining its need state across multiple frames
    manager.Initialize();

    // Initial state
    EXPECT_DOUBLE_EQ(manager.GetNeed(0).CurrentValue, 1.0);

    // Frame 1: 1 second passes
    manager.Update(1.0);
    EXPECT_DOUBLE_EQ(manager.GetNeed(0).CurrentValue, 0.9);

    // Frame 2: 2 more seconds pass
    manager.Update(2.0);
    EXPECT_DOUBLE_EQ(manager.GetNeed(0).CurrentValue, 0.7);

    // Satisfy the need
    manager.SatisfyNeed(0);
    EXPECT_DOUBLE_EQ(manager.GetNeed(0).CurrentValue, 1.0);

    // Frame 3: decay resumes from satisfied state
    manager.Update(1.5);
    EXPECT_DOUBLE_EQ(manager.GetNeed(0).CurrentValue, 0.85);
}

TEST_F(NeedSystemTest, CompleteLifecycle) {
    // Simulate complete NPC need cycle: init -> decay -> urgent -> satisfy -> repeat
    manager.Initialize();

    // Stage 1: All needs satisfied
    for (size_t i = 0; i < manager.GetNeedCount(); ++i) {
        EXPECT_FALSE(manager.GetNeed(i).IsUrgent());
    }
    auto urgent = manager.GetUrgentNeeds();
    EXPECT_TRUE(urgent.empty());

    // Stage 2: Decay until hunger becomes urgent (need to drop from 1.0 to <= 0.3)
    // With decay rate 0.1, need 7 seconds to go from 1.0 to 0.3
    manager.Update(7.0);
    EXPECT_TRUE(manager.GetNeed(0).IsUrgent());
    urgent = manager.GetUrgentNeeds();
    EXPECT_FALSE(urgent.empty());

    // Stage 3: Satisfy the urgent need
    manager.SatisfyNeed(0);
    EXPECT_FALSE(manager.GetNeed(0).IsUrgent());

    // Stage 4: Verify all needs return to normal
    urgent = manager.GetUrgentNeeds();
    // All others should still be satisfied (haven't decayed below threshold)
    EXPECT_LE(urgent.size(), manager.GetNeedCount() - 1);
}

// ============================================================================
// Integration Tests (Blueprint Compatibility)
// ============================================================================

TEST_F(NeedSystemTest, BlueprintSimulationWith2SecondTimer) {
    // Simulates Unreal Blueprint's ProcessNeedsLoop with 2-second timer
    manager.Initialize();

    // Simulate 10 seconds of game time (5 timer ticks at 2 seconds each)
    for (int tick = 0; tick < 5; ++tick) {
        manager.Update(2.0);
        auto urgent = manager.GetUrgentNeeds();

        if (tick == 3) {
            // After 6 seconds: 1.0 - (0.1 * 6) = 0.4
            EXPECT_FALSE(urgent.empty()) << "Should have urgent needs at tick " << tick;
        }
    }

    // After 10 seconds: 1.0 - (0.1 * 10) = 0.0
    EXPECT_DOUBLE_EQ(manager.GetNeed(0).CurrentValue, 0.0);
}

TEST_F(NeedSystemTest, EnumCoverage) {
    // Verify all enum values are handled
    manager.Initialize();
    EXPECT_EQ(manager.GetNeedCount(), 5);

    // Check each need type can be accessed
    manager.GetNeedByType(ENeedType::Hunger);
    manager.GetNeedByType(ENeedType::Thirst);
    manager.GetNeedByType(ENeedType::Rest);
    manager.GetNeedByType(ENeedType::Social);
    manager.GetNeedByType(ENeedType::Energy);
}

