#include "PersonalityNeedSystem.h"

namespace creatureRepo::need {

// ============================================================================
// PersonalityNeedManager Implementation
// ============================================================================

PersonalityNeedManager::PersonalityNeedManager(EPersonalityType personality)
    : NeedManager(), personality_(personality) {}

void PersonalityNeedManager::Update(double deltaSeconds) {
    if (!IsInitialized()) {
        throw std::runtime_error("NeedManager not initialized. Call Initialize() first.");
    }

    if (deltaSeconds < 0.0) {
        throw std::invalid_argument("deltaSeconds cannot be negative");
    }

    // Get mutable access to needs for updating
    auto& all_needs = const_cast<std::vector<NPCNeed>&>(GetAllNeeds());

    // Apply personality-modified decay to each need
    // Formula: CurrentValue = max(0.0, CurrentValue - (BaseDecay * PersonalityMultiplier * deltaSeconds))
    for (auto& need : all_needs) {
        double multiplier = GetDecayMultiplier(need.NeedType);
        double decayAmount = need.DecayRatePerSecond * multiplier * deltaSeconds;

        // Clamp to [0.0, 1.0]
        need.CurrentValue = need.CurrentValue - decayAmount;
        if (need.CurrentValue < 0.0) need.CurrentValue = 0.0;
        if (need.CurrentValue > 1.0) need.CurrentValue = 1.0;
    }
}

size_t PersonalityNeedManager::GetMostUrgentNeed() const {
    if (!IsInitialized()) {
        throw std::runtime_error("NeedManager not initialized. Call Initialize() first.");
    }

    const auto& needs = GetAllNeeds();
    if (needs.empty()) {
        throw std::runtime_error("No needs to evaluate");
    }

    // Find need with lowest (CurrentValue * PriorityWeight)
    // Higher weight = personality considers this more urgent
    size_t most_urgent_idx = 0;
    double lowest_weighted_urgency =
        needs[0].CurrentValue * GetPriorityWeight(needs[0].NeedType);

    for (size_t i = 1; i < needs.size(); ++i) {
        double weighted_urgency =
            needs[i].CurrentValue * GetPriorityWeight(needs[i].NeedType);

        if (weighted_urgency < lowest_weighted_urgency) {
            lowest_weighted_urgency = weighted_urgency;
            most_urgent_idx = i;
        }
    }

    return most_urgent_idx;
}

EPersonalityType PersonalityNeedManager::GetPersonality() const {
    return personality_;
}

double PersonalityNeedManager::GetDecayMultiplier(ENeedType need_type) const {
    uint8_t p_idx = static_cast<uint8_t>(personality_);
    uint8_t n_idx = static_cast<uint8_t>(need_type);

    if (p_idx >= 6 || n_idx >= 5) {
        return 1.0;  // Default multiplier if out of range
    }

    return DECAY_MULTIPLIERS[p_idx][n_idx];
}

double PersonalityNeedManager::GetThresholdMultiplier(ENeedType need_type) const {
    uint8_t p_idx = static_cast<uint8_t>(personality_);
    uint8_t n_idx = static_cast<uint8_t>(need_type);

    if (p_idx >= 6 || n_idx >= 5) {
        return 1.0;  // Default multiplier if out of range
    }

    return THRESHOLD_MULTIPLIERS[p_idx][n_idx];
}

double PersonalityNeedManager::GetPriorityWeight(ENeedType need_type) const {
    uint8_t p_idx = static_cast<uint8_t>(personality_);
    uint8_t n_idx = static_cast<uint8_t>(need_type);

    if (p_idx >= 6 || n_idx >= 5) {
        return 1.0;  // Default weight if out of range
    }

    return PRIORITY_WEIGHTS[p_idx][n_idx];
}

}  // namespace creatureRepo::need

