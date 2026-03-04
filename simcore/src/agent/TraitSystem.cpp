#include "simcore/agent/TraitSystem.h"
#include <algorithm>

namespace simcore {

namespace {
    inline float clampf(float v, float lo, float hi) {
        return v < lo ? lo : (v > hi ? hi : v);
    }
}

TraitSet TraitSystem::derive(const BaseTraits& base,
                              const TraitMods*  permanent_mods, int num_mods,
                              const TraitEffect* effects,        int num_effects) {
    // Start from base values — matches iso_rpg_lab derive_stats pattern
    float values[TRAIT_COUNT]{};
    for (int i = 0; i < TRAIT_COUNT; ++i)
        values[i] = base.values[i];

    // Apply permanent gear/status mods (additive)
    for (int m = 0; m < num_mods; ++m)
        for (int i = 0; i < TRAIT_COUNT; ++i)
            values[i] += permanent_mods[m].delta[i];

    // Apply active timed effects (additive)
    for (int e = 0; e < num_effects; ++e) {
        if (effects[e].duration_steps <= 0) continue;
        for (int i = 0; i < TRAIT_COUNT; ++i)
            values[i] += effects[e].mods.delta[i];
    }

    TraitSet ts;
    for (int i = 0; i < TRAIT_COUNT; ++i)
        ts.values[i] = clampf(values[i], 0.0f, 1.0f);
    return ts;
}

void TraitSystem::tick_effects(TraitEffect* effects, int count) {
    for (int i = 0; i < count; ++i) {
        if (effects[i].duration_steps > 0)
            --effects[i].duration_steps;
    }
}

BaseTraits TraitSystem::make_neutral() {
    BaseTraits bt;
    for (int i = 0; i < TRAIT_COUNT; ++i)
        bt.values[i] = 0.5f;
    return bt;
}

TraitSet TraitSystem::clamp(const TraitSet& ts) {
    TraitSet result = ts;
    for (int i = 0; i < TRAIT_COUNT; ++i)
        result.values[i] = clampf(ts.values[i], 0.0f, 1.0f);
    return result;
}

} // namespace simcore

