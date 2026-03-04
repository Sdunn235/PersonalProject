#pragma once
#include <array>
#include <cstdint>

namespace simcore {

// ── Trait types ──────────────────────────────────────────────────────────
enum class TraitType : uint8_t {
    Aggression    = 0,
    Boldness      = 1,
    Curiosity     = 2,
    Greed         = 3,
    Sociability   = 4,
    Loyalty       = 5,
    Patience      = 6,
    RiskTolerance = 7,

    COUNT         = 8
};

static constexpr int TRAIT_COUNT = static_cast<int>(TraitType::COUNT);

// ── Flat modifiers ────────────────────────────────────────────────────────
// Ported from iso_rpg_lab/gameplay/derive.py — FlatMods pattern.
// Applied additively on top of base trait values.
struct TraitMods {
    float delta[TRAIT_COUNT] = {};

    float& operator[](TraitType t) { return delta[static_cast<int>(t)]; }
    float  operator[](TraitType t) const { return delta[static_cast<int>(t)]; }
};

// ── Timed effect ─────────────────────────────────────────────────────────
// Ported from iso_rpg_lab/gameplay/derive.py — Effect pattern.
struct TraitEffect {
    TraitMods mods;
    int       duration_steps = 0; // remaining SimSteps; 0 = expired
};

// ── Base trait values ────────────────────────────────────────────────────
struct BaseTraits {
    float values[TRAIT_COUNT] = {};

    float& operator[](TraitType t) { return values[static_cast<int>(t)]; }
    float  operator[](TraitType t) const { return values[static_cast<int>(t)]; }
};

// ── Derived trait set ────────────────────────────────────────────────────
// Result of applying gear/effects to base.
struct TraitSet {
    float values[TRAIT_COUNT] = {};

    float& operator[](TraitType t) { return values[static_cast<int>(t)]; }
    float  operator[](TraitType t) const { return values[static_cast<int>(t)]; }
};

/**
 * TraitSystem — Derives current traits from base + modifiers + effects.
 *
 * Ported from iso_rpg_lab/gameplay/derive.py:
 *   derive_stats(base, gear_mods, effects) → Stats
 *
 * Traits influence need tolerance, decision weighting, fear response,
 * economic behavior, and social behavior. They do NOT directly cause actions.
 */
class TraitSystem {
public:
    /// Derive the current effective trait set.
    static TraitSet derive(const BaseTraits& base,
                           const TraitMods*  permanent_mods, int num_mods,
                           const TraitEffect* effects,       int num_effects);

    /// Tick down effect durations. Caller should remove expired effects.
    static void tick_effects(TraitEffect* effects, int count);

    /// Build a neutral BaseTraits (all values = 0.5, mid-point of 0–1 range).
    static BaseTraits make_neutral();

    /// Clamp all derived values to [0, 1].
    static TraitSet clamp(const TraitSet& ts);
};

} // namespace simcore

