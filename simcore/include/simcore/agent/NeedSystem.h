#pragma once
#include <cstdint>
#include <array>

namespace simcore {

// ── Need types ─────────────────────────────────────────────────────────────
// Mirrors E_NPCNeedType from Unreal Blueprint (E_NPCNeedType.E_NPCNeedType).
// SimCore is the authoritative source; Unreal must mirror this enum.
enum class NeedType : uint8_t {
    None        = 0,
    Hunger      = 1,
    Thirst      = 2,
    Sleep       = 3,
    Health      = 4,
    Stamina     = 5,
    Mana        = 6,
    Temperature = 7,
    Comfort     = 8,
    Shelter     = 9,
    Social      = 10,
    Entertainment = 11,
    Hygiene     = 12,
    Safety      = 13,

    COUNT       = 14   // keep last
};

static constexpr int NEED_COUNT = static_cast<int>(NeedType::COUNT);

// ── Single need record ────────────────────────────────────────────────────
// Direct translation of S_NPCNeed Blueprint struct.
struct NeedRecord {
    NeedType need_type          = NeedType::None;
    float    current_value      = 100.0f; // 0–100, 100 = fully satisfied
    float    threshold          = 30.0f;  // below this → drive fires
    float    critical_threshold = 10.0f;  // below this → emergency override
    float    decay_rate_per_sec = 1.0f;   // units lost per SimStep second
};

// ── NeedState — all needs for one agent ─────────────────────────────────
struct NeedState {
    std::array<NeedRecord, NEED_COUNT> needs{};

    NeedRecord&       get(NeedType t)       { return needs[static_cast<int>(t)]; }
    const NeedRecord& get(NeedType t) const { return needs[static_cast<int>(t)]; }
};

/**
 * NeedSystem — Agent need decay and threshold evaluation.
 *
 * Ported from:
 *   BP_NPC_Parent__Function__UpdateNeeds.bp.txt
 *   BP_NPC_Parent__Function__ProcessNeedsLoop.bp.txt
 *
 * Decay formula: new_value = clamp(current - decay_rate * delta_time, 0, 100)
 * Matches the Blueprint's: Subtract_DoubleDouble → FClamp(0, 100)
 */
class NeedSystem {
public:
    /// Apply time-based decay to all needs.
    /// delta_seconds is one SimStep duration.
    static void tick(NeedState& state, float delta_seconds);

    /// Returns true if the need has dropped at or below its threshold.
    static bool is_urgent(const NeedRecord& need);

    /// Returns true if the need has dropped at or below its critical threshold.
    static bool is_critical(const NeedRecord& need);

    /// Satisfy a need by adding the given amount (clamped to 100).
    static void satisfy(NeedRecord& need, float amount);

    /// Initialize a NeedRecord with standard defaults for a given type.
    static NeedRecord make_default(NeedType type);

    /// Create a fully initialized NeedState with defaults for all needs.
    static NeedState make_default_state();
};

} // namespace simcore

