#include "simcore/agent/NeedSystem.h"
#include <algorithm>

namespace simcore {

namespace {
    inline float clampf(float v, float lo, float hi) {
        return v < lo ? lo : (v > hi ? hi : v);
    }
}

void NeedSystem::tick(NeedState& state, float delta_seconds) {
    for (auto& record : state.needs) {
        if (record.need_type == NeedType::None) continue;

        // Matches Blueprint UpdateNeeds:
        //   Subtract_DoubleDouble(CurrentValue, decay * deltaTime)
        //   FClamp(result, 0.0, 100.0)
        float decayed = record.current_value - (record.decay_rate_per_sec * delta_seconds);
        record.current_value = clampf(decayed, 0.0f, 100.0f);
    }
}

bool NeedSystem::is_urgent(const NeedRecord& need) {
    return need.current_value <= need.threshold;
}

bool NeedSystem::is_critical(const NeedRecord& need) {
    return need.current_value <= need.critical_threshold;
}

void NeedSystem::satisfy(NeedRecord& need, float amount) {
    need.current_value = std::min(need.current_value + amount, 100.0f);
}

NeedRecord NeedSystem::make_default(NeedType type) {
    NeedRecord r;
    r.need_type = type;
    r.current_value = 100.0f;

    // Defaults tuned from Blueprint S_NPCNeed observed values
    switch (type) {
        case NeedType::Hunger:
            r.threshold = 30.0f; r.critical_threshold = 10.0f; r.decay_rate_per_sec = 0.5f; break;
        case NeedType::Thirst:
            r.threshold = 30.0f; r.critical_threshold = 5.0f;  r.decay_rate_per_sec = 0.8f; break;
        case NeedType::Sleep:
            r.threshold = 25.0f; r.critical_threshold = 5.0f;  r.decay_rate_per_sec = 0.3f; break;
        case NeedType::Health:
            r.threshold = 20.0f; r.critical_threshold = 5.0f;  r.decay_rate_per_sec = 0.0f; break;
        case NeedType::Stamina:
            r.threshold = 20.0f; r.critical_threshold = 5.0f;  r.decay_rate_per_sec = 0.2f; break;
        case NeedType::Mana:
            r.threshold = 20.0f; r.critical_threshold = 0.0f;  r.decay_rate_per_sec = 0.1f; break;
        case NeedType::Temperature:
            r.threshold = 30.0f; r.critical_threshold = 10.0f; r.decay_rate_per_sec = 0.2f; break;
        case NeedType::Comfort:
            r.threshold = 20.0f; r.critical_threshold = 5.0f;  r.decay_rate_per_sec = 0.1f; break;
        case NeedType::Shelter:
            r.threshold = 25.0f; r.critical_threshold = 5.0f;  r.decay_rate_per_sec = 0.1f; break;
        case NeedType::Social:
            r.threshold = 25.0f; r.critical_threshold = 5.0f;  r.decay_rate_per_sec = 0.2f; break;
        case NeedType::Entertainment:
            r.threshold = 20.0f; r.critical_threshold = 5.0f;  r.decay_rate_per_sec = 0.15f; break;
        case NeedType::Hygiene:
            r.threshold = 20.0f; r.critical_threshold = 5.0f;  r.decay_rate_per_sec = 0.1f; break;
        case NeedType::Safety:
            r.threshold = 30.0f; r.critical_threshold = 5.0f;  r.decay_rate_per_sec = 0.0f; break;
        default:
            r.threshold = 30.0f; r.critical_threshold = 10.0f; r.decay_rate_per_sec = 0.5f; break;
    }
    return r;
}

NeedState NeedSystem::make_default_state() {
    NeedState state;
    for (int i = 1; i < NEED_COUNT; ++i) { // skip None (0)
        NeedType t = static_cast<NeedType>(i);
        state.get(t) = make_default(t);
    }
    return state;
}

} // namespace simcore

