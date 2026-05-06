#include "NeedSystem.h"
#include <algorithm>
#include <cmath>

namespace creatureRepo::need {

// ============================================================================
// NeedManager Implementation
// ============================================================================

NeedManager::NeedManager() : initialized_(false) {}

void NeedManager::Initialize() {
    needs_.clear();

    // Create a default need for each need type
    for (uint8_t i = 0; i < static_cast<uint8_t>(ENeedType::Count); ++i) {
        needs_.emplace_back(
            static_cast<ENeedType>(i),
            1.0,    // Initial value: fully satisfied
            0.3,    // Threshold: becomes urgent at 30%
            0.1     // Decay rate: 10% per second
        );
    }

    initialized_ = true;
}

void NeedManager::Initialize(const std::vector<NPCNeed>& needs) {
    if (needs.empty()) {
        throw std::invalid_argument("Cannot initialize NeedManager with empty needs vector");
    }
    needs_ = needs;
    initialized_ = true;
}

void NeedManager::Update(double deltaSeconds) {
    if (!initialized_) {
        throw std::runtime_error("NeedManager not initialized. Call Initialize() first.");
    }

    if (deltaSeconds < 0.0) {
        throw std::invalid_argument("deltaSeconds cannot be negative");
    }

    // Apply time-based decay to each need
    // Formula: CurrentValue = max(0.0, CurrentValue - (DecayRatePerSecond * deltaSeconds))
    for (auto& need : needs_) {
        double decayAmount = need.DecayRatePerSecond * deltaSeconds;
        need.CurrentValue = Clamp(need.CurrentValue - decayAmount);
    }
}

std::vector<size_t> NeedManager::GetUrgentNeeds() const {
    if (!initialized_) {
        throw std::runtime_error("NeedManager not initialized. Call Initialize() first.");
    }

    std::vector<size_t> urgentIndices;

    for (size_t i = 0; i < needs_.size(); ++i) {
        if (needs_[i].IsUrgent()) {
            urgentIndices.push_back(i);
        }
    }

    return urgentIndices;
}

size_t NeedManager::GetMostUrgentNeed() const {
    if (!initialized_) {
        throw std::runtime_error("NeedManager not initialized. Call Initialize() first.");
    }

    if (needs_.empty()) {
        throw std::runtime_error("No needs to evaluate");
    }

    size_t mostUrgentIdx = 0;
    double lowestValue = needs_[0].CurrentValue;

    for (size_t i = 1; i < needs_.size(); ++i) {
        if (needs_[i].CurrentValue < lowestValue) {
            lowestValue = needs_[i].CurrentValue;
            mostUrgentIdx = i;
        }
    }

    return mostUrgentIdx;
}

const NPCNeed& NeedManager::GetNeed(size_t index) const {
    if (index >= needs_.size()) {
        throw std::out_of_range("Need index out of range");
    }
    return needs_[index];
}

const NPCNeed& NeedManager::GetNeedByType(ENeedType type) const {
    int32_t index = FindNeedIndexByType(type);
    if (index < 0) {
        throw std::runtime_error("Need type not found in manager");
    }
    return needs_[index];
}

NPCNeed& NeedManager::MutableNeed(size_t index) {
    if (index >= needs_.size()) {
        throw std::out_of_range("Need index out of range");
    }
    return needs_[index];
}

NPCNeed& NeedManager::MutableNeedByType(ENeedType type) {
    int32_t index = FindNeedIndexByType(type);
    if (index < 0) {
        throw std::runtime_error("Need type not found in manager");
    }
    return needs_[index];
}

void NeedManager::SatisfyNeed(size_t index) {
    if (index >= needs_.size()) {
        throw std::out_of_range("Need index out of range");
    }
    needs_[index].CurrentValue = 1.0;
}

void NeedManager::SatisfyNeedByType(ENeedType type) {
    int32_t index = FindNeedIndexByType(type);
    if (index < 0) {
        throw std::runtime_error("Need type not found in manager");
    }
    needs_[index].CurrentValue = 1.0;
}

size_t NeedManager::GetNeedCount() const {
    return needs_.size();
}

bool NeedManager::IsInitialized() const {
    return initialized_;
}

const std::vector<NPCNeed>& NeedManager::GetAllNeeds() const {
    return needs_;
}

int32_t NeedManager::FindNeedIndexByType(ENeedType type) const {
    for (size_t i = 0; i < needs_.size(); ++i) {
        if (needs_[i].NeedType == type) {
            return static_cast<int32_t>(i);
        }
    }
    return -1;
}

double NeedManager::Clamp(double value) {
    if (value < 0.0) return 0.0;
    if (value > 1.0) return 1.0;
    return value;
}

}  // namespace creatureRepo::need

