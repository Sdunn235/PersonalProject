#include <gtest/gtest.h>
#include "simcore/agent/TraitSystem.h"

using namespace simcore;

TEST(TraitSystem, MakeNeutral_AllHalf) {
    BaseTraits bt = TraitSystem::make_neutral();
    for (int i = 0; i < TRAIT_COUNT; ++i)
        EXPECT_FLOAT_EQ(bt.values[i], 0.5f);
}

TEST(TraitSystem, Derive_NoMods_EqualsBase) {
    BaseTraits base = TraitSystem::make_neutral();
    base[TraitType::Aggression] = 0.8f;

    TraitSet ts = TraitSystem::derive(base, nullptr, 0, nullptr, 0);
    EXPECT_FLOAT_EQ(ts[TraitType::Aggression], 0.8f);
    EXPECT_FLOAT_EQ(ts[TraitType::Boldness],   0.5f);
}

TEST(TraitSystem, Derive_PermanentMods_Additive) {
    BaseTraits base = TraitSystem::make_neutral(); // all 0.5
    TraitMods mod;
    mod[TraitType::Greed] = 0.2f;

    TraitSet ts = TraitSystem::derive(base, &mod, 1, nullptr, 0);
    EXPECT_FLOAT_EQ(ts[TraitType::Greed], 0.7f);
}

TEST(TraitSystem, Derive_Clamped_At1) {
    BaseTraits base = TraitSystem::make_neutral();
    TraitMods mod;
    mod[TraitType::Curiosity] = 0.8f; // 0.5 + 0.8 = 1.3 → clamped to 1.0

    TraitSet ts = TraitSystem::derive(base, &mod, 1, nullptr, 0);
    EXPECT_FLOAT_EQ(ts[TraitType::Curiosity], 1.0f);
}

TEST(TraitSystem, Derive_Clamped_At0) {
    BaseTraits base = TraitSystem::make_neutral();
    TraitMods mod;
    mod[TraitType::Loyalty] = -0.9f; // 0.5 - 0.9 = -0.4 → clamped to 0.0

    TraitSet ts = TraitSystem::derive(base, &mod, 1, nullptr, 0);
    EXPECT_FLOAT_EQ(ts[TraitType::Loyalty], 0.0f);
}

TEST(TraitSystem, Derive_TimedEffect_Applied) {
    BaseTraits base = TraitSystem::make_neutral();
    TraitEffect effect;
    effect.mods[TraitType::Boldness] = 0.3f;
    effect.duration_steps = 5;

    TraitSet ts = TraitSystem::derive(base, nullptr, 0, &effect, 1);
    EXPECT_FLOAT_EQ(ts[TraitType::Boldness], 0.8f);
}

TEST(TraitSystem, Derive_ExpiredEffect_Ignored) {
    BaseTraits base = TraitSystem::make_neutral();
    TraitEffect effect;
    effect.mods[TraitType::Boldness] = 0.3f;
    effect.duration_steps = 0; // expired

    TraitSet ts = TraitSystem::derive(base, nullptr, 0, &effect, 1);
    EXPECT_FLOAT_EQ(ts[TraitType::Boldness], 0.5f); // unchanged
}

TEST(TraitSystem, TickEffects_DecreasesDuration) {
    TraitEffect effects[2];
    effects[0].duration_steps = 3;
    effects[1].duration_steps = 1;

    TraitSystem::tick_effects(effects, 2);
    EXPECT_EQ(effects[0].duration_steps, 2);
    EXPECT_EQ(effects[1].duration_steps, 0);
}

TEST(TraitSystem, TickEffects_DoesNotGoBelowZero) {
    TraitEffect effect;
    effect.duration_steps = 0;
    TraitSystem::tick_effects(&effect, 1);
    EXPECT_EQ(effect.duration_steps, 0);
}

TEST(TraitSystem, MultipleMods_Additive) {
    BaseTraits base = TraitSystem::make_neutral(); // 0.5
    TraitMods mods[2];
    mods[0][TraitType::Patience] = 0.1f;
    mods[1][TraitType::Patience] = 0.1f;

    TraitSet ts = TraitSystem::derive(base, mods, 2, nullptr, 0);
    EXPECT_FLOAT_EQ(ts[TraitType::Patience], 0.7f);
}

