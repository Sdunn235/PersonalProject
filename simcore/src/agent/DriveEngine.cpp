#include "simcore/agent/DriveEngine.h"
#include <algorithm>

namespace simcore {

namespace {
    inline float clampf(float v, float lo, float hi) {
        return v < lo ? lo : (v > hi ? hi : v);
    }
}

TraitType DriveEngine::need_to_trait_weight(NeedType nt) {
    // Maps each need to the trait that most influences how urgently
    // the agent reacts to it.
    switch (nt) {
        case NeedType::Hunger:        return TraitType::Patience;        // low patience → higher hunger urgency
        case NeedType::Thirst:        return TraitType::Patience;
        case NeedType::Sleep:         return TraitType::Patience;
        case NeedType::Health:        return TraitType::Boldness;        // bold agents tolerate lower health
        case NeedType::Stamina:       return TraitType::Boldness;
        case NeedType::Safety:        return TraitType::RiskTolerance;   // high risk tolerance → ignore safety longer
        case NeedType::Social:        return TraitType::Sociability;
        case NeedType::Entertainment: return TraitType::Curiosity;
        default:                      return TraitType::Patience;
    }
}

float DriveEngine::compute_score(const NeedRecord& need, float trait_value) {
    if (need.current_value > need.threshold) return 0.0f;

    // Normalized urgency: 1.0 when at threshold, approaches infinity at 0
    // Use a bounded form: (threshold - current) / max(threshold, 1)
    float gap = need.threshold - need.current_value;
    float base = gap / std::max(need.threshold, 1.0f);
    base = clampf(base, 0.0f, 1.0f);

    // Trait modifier: Patience reduces urgency (high patience = lower score)
    // Other traits increase urgency based on the mapping above.
    // We invert Patience (1 - patience) so a patient agent scores lower.
    float trait_weight = 1.0f;
    // For traits where high value = MORE urgency (Sociability, Curiosity, Greed):
    //   weight = 1 + trait_value
    // For traits where high value = LESS urgency (Patience, Boldness, RiskTolerance):
    //   weight = 2 - trait_value  (still 1.0 at neutral 0.5)
    TraitType tt = need_to_trait_weight(need.need_type);
    switch (tt) {
        case TraitType::Patience:
        case TraitType::Boldness:
        case TraitType::RiskTolerance:
            trait_weight = 2.0f - trait_value;
            break;
        default:
            trait_weight = 1.0f + trait_value;
            break;
    }

    return base * trait_weight;
}

std::vector<DriveScore> DriveEngine::evaluate(const NeedState& needs,
                                               const TraitSet&  traits) {
    std::vector<DriveScore> drives;
    drives.reserve(NEED_COUNT);

    for (int i = 1; i < NEED_COUNT; ++i) {  // skip None
        const NeedRecord& need = needs.needs[i];
        if (!NeedSystem::is_urgent(need)) continue;

        float trait_val = traits[need_to_trait_weight(need.need_type)];
        float score     = compute_score(need, trait_val);
        if (score <= 0.0f) continue;

        DriveScore ds;
        ds.need_type   = need.need_type;
        ds.score       = score;
        ds.is_critical = NeedSystem::is_critical(need);
        drives.push_back(ds);
    }

    // Sort: critical first, then by score descending
    // Replaces Blueprint SortNeedsByValue_BubbleSort
    std::sort(drives.begin(), drives.end(), [](const DriveScore& a, const DriveScore& b) {
        if (a.is_critical != b.is_critical) return a.is_critical > b.is_critical;
        return a.score > b.score;
    });

    return drives;
}

DriveScore DriveEngine::top_drive(const NeedState& needs, const TraitSet& traits) {
    auto drives = evaluate(needs, traits);
    if (drives.empty()) return { NeedType::None, 0.0f, false };
    return drives.front();
}

} // namespace simcore

