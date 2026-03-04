#pragma once
#include "simcore/agent/NeedSystem.h"
#include "simcore/agent/TraitSystem.h"
#include <array>
#include <vector>

namespace simcore {

// ── Drive score ──────────────────────────────────────────────────────────
struct DriveScore {
    NeedType need_type  = NeedType::None;
    float    score      = 0.0f;  // higher = more urgent
    bool     is_critical = false;
};

/**
 * DriveEngine — Computes and prioritizes agent drives from need state.
 *
 * Replaces:
 *   BP_NPC_Parent__Function__SortNeedsByValue_BubbleSort.bp.txt
 *   BP_NPC_Parent__Function__ProcessNeedsLoop.bp.txt (threshold check)
 *
 * Drive formula:
 *   base_score = (threshold - current_value) / threshold   → 0 when at threshold, 1 when empty
 *   trait_weight = trait modifier for this need type (e.g. Patience reduces food urgency)
 *   final_score = base_score * (1 + trait_weight)
 *
 * Scores are sorted descending (highest = most urgent).
 * Critical needs are always floated to the top regardless of score.
 */
class DriveEngine {
public:
    /// Evaluate all needs and return a sorted list of active drives.
    /// Only needs at or below threshold are included.
    /// Trait modifiers adjust urgency weights.
    static std::vector<DriveScore> evaluate(const NeedState&  needs,
                                             const TraitSet&   traits);

    /// Return the single highest-priority drive, or {NeedType::None, 0} if none.
    static DriveScore top_drive(const NeedState& needs, const TraitSet& traits);

private:
    /// Map a NeedType to the TraitType that modifies its urgency.
    static TraitType need_to_trait_weight(NeedType nt);

    static float compute_score(const NeedRecord& need, float trait_value);
};

} // namespace simcore

