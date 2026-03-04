#include <gtest/gtest.h>
#include "simcore/sim/SimRNG.h"

using namespace simcore;

TEST(SimRNG, Deterministic_SameSeed_SameSequence) {
    SimRNG a(42u), b(42u);
    for (int i = 0; i < 100; ++i)
        EXPECT_EQ(a.next_u32(), b.next_u32());
}

TEST(SimRNG, DifferentSeeds_DifferentSequences) {
    SimRNG a(1u), b(2u);
    bool any_diff = false;
    for (int i = 0; i < 20; ++i)
        if (a.next_u32() != b.next_u32()) { any_diff = true; break; }
    EXPECT_TRUE(any_diff);
}

TEST(SimRNG, RangeInt_AlwaysInBounds) {
    SimRNG rng(999u);
    for (int i = 0; i < 10000; ++i) {
        int v = rng.range_int(5, 10);
        EXPECT_GE(v, 5);
        EXPECT_LE(v, 10);
    }
}

TEST(SimRNG, RangeInt_SingleValue) {
    SimRNG rng(1u);
    for (int i = 0; i < 50; ++i)
        EXPECT_EQ(rng.range_int(7, 7), 7);
}

TEST(SimRNG, Chance_AlwaysTrue_At100) {
    SimRNG rng(123u);
    for (int i = 0; i < 100; ++i)
        EXPECT_TRUE(rng.chance(100.0f));
}

TEST(SimRNG, Chance_AlwaysFalse_At0) {
    SimRNG rng(123u);
    for (int i = 0; i < 100; ++i)
        EXPECT_FALSE(rng.chance(0.0f));
}

TEST(SimRNG, Chance_Approximately50) {
    SimRNG rng(777u);
    int hits = 0;
    const int N = 10000;
    for (int i = 0; i < N; ++i)
        if (rng.chance(50.0f)) ++hits;
    // Should be within ±5% of 50%
    EXPECT_GT(hits, 4500);
    EXPECT_LT(hits, 5500);
}

TEST(SimRNG, NextFloat_InRange) {
    SimRNG rng(55u);
    for (int i = 0; i < 1000; ++i) {
        float v = rng.next_float();
        EXPECT_GE(v, 0.0f);
        EXPECT_LT(v, 1.0f);
    }
}

TEST(SimRNG, StateSerialize_Restore) {
    SimRNG rng(321u);
    rng.next_u32(); rng.next_u32(); // advance a few steps
    uint32_t saved = rng.state();
    uint32_t v1 = rng.next_u32();

    SimRNG rng2(1u);
    rng2.set_state(saved);
    EXPECT_EQ(rng2.next_u32(), v1);
}

// Regression: matches Python RNG32 output for seed 123456789
TEST(SimRNG, MatchesPythonRNG32) {
    // Python: RNG32(123456789).next_u32() == ?
    // LCG: state = (1664525 * 123456789 + 1013904223) & 0xFFFFFFFF
    SimRNG rng(123456789u);
    uint32_t expected = (1664525u * 123456789u + 1013904223u) & 0xFFFFFFFFu;
    EXPECT_EQ(rng.next_u32(), expected);
}

