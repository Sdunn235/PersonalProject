#include <gtest/gtest.h>
#include "simcore/sim/TimeManager.h"

using namespace simcore;

TEST(TimeManager, NoAdvance_ZeroSteps) {
    TimeManager tm;
    EXPECT_EQ(tm.total_steps(), 0u);
    EXPECT_EQ(tm.world_day(),   0u);
}

TEST(TimeManager, Advance_ExactOneStep) {
    TimeManager::Config cfg;
    cfg.sim_step_seconds = 1.0f;
    TimeManager tm(cfg);

    int steps = tm.advance(1.0f);
    EXPECT_EQ(steps,          1);
    EXPECT_EQ(tm.total_steps(), 1u);
}

TEST(TimeManager, Advance_MultipleSteps) {
    TimeManager::Config cfg;
    cfg.sim_step_seconds = 0.5f;
    TimeManager tm(cfg);

    int steps = tm.advance(2.0f);
    EXPECT_EQ(steps,            4);
    EXPECT_EQ(tm.total_steps(), 4u);
}

TEST(TimeManager, Advance_Accumulates_SubStep) {
    TimeManager::Config cfg;
    cfg.sim_step_seconds = 1.0f;
    TimeManager tm(cfg);

    tm.advance(0.4f);
    EXPECT_EQ(tm.total_steps(), 0u); // not enough for a full step
    EXPECT_NEAR(tm.accumulator(), 0.4f, 0.0001f);

    tm.advance(0.7f);
    EXPECT_EQ(tm.total_steps(), 1u); // 0.4 + 0.7 = 1.1 → 1 step, 0.1 leftover
    EXPECT_NEAR(tm.accumulator(), 0.1f, 0.0001f);
}

TEST(TimeManager, DayRollover) {
    TimeManager::Config cfg;
    cfg.sim_step_seconds = 1.0f;
    cfg.steps_per_day    = 5;
    cfg.days_per_season  = 100;
    TimeManager tm(cfg);

    for (int i = 0; i < 5; ++i) tm.advance(1.0f);
    EXPECT_EQ(tm.world_day(), 1u);
}

TEST(TimeManager, SeasonRollover) {
    TimeManager::Config cfg;
    cfg.sim_step_seconds = 1.0f;
    cfg.steps_per_day    = 1;
    cfg.days_per_season  = 3;
    cfg.seasons_per_year = 4;
    cfg.years_per_gen    = 100;
    TimeManager tm(cfg);

    for (int i = 0; i < 3; ++i) tm.advance(1.0f); // 3 days = 1 season
    EXPECT_EQ(tm.season(), 1u);
}

TEST(TimeManager, YearRollover) {
    TimeManager::Config cfg;
    cfg.sim_step_seconds = 1.0f;
    cfg.steps_per_day    = 1;
    cfg.days_per_season  = 1;
    cfg.seasons_per_year = 4;
    cfg.years_per_gen    = 100;
    TimeManager tm(cfg);

    for (int i = 0; i < 4; ++i) tm.advance(1.0f); // 4 seasons = 1 year
    EXPECT_EQ(tm.year(), 1u);
    EXPECT_EQ(tm.season(), 0u); // season wraps back
}

TEST(TimeManager, GenerationRollover) {
    TimeManager::Config cfg;
    cfg.sim_step_seconds = 1.0f;
    cfg.steps_per_day    = 1;
    cfg.days_per_season  = 1;
    cfg.seasons_per_year = 1;
    cfg.years_per_gen    = 3;
    TimeManager tm(cfg);

    for (int i = 0; i < 3; ++i) tm.advance(1.0f);
    EXPECT_EQ(tm.generation(), 1u);
}

TEST(TimeManager, StepSecondsAccessor) {
    TimeManager::Config cfg;
    cfg.sim_step_seconds = 2.5f;
    TimeManager tm(cfg);
    EXPECT_FLOAT_EQ(tm.step_seconds(), 2.5f);
}

