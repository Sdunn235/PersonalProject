#include "simcore/agent/DecisionEngine.h"
#include "simcore/agent/DriveEngine.h"

namespace simcore {

ActionIntent DecisionEngine::decide(AgentID          agent_id,
                                    const NeedState& needs,
                                    const TraitSet&  traits,
                                    const WorldSnapshot& world) {
    ActionIntent intent;
    intent.agent_id = agent_id;

    // Safety override — always evaluated first regardless of other drives
    if (!world.is_safe) {
        float risk = traits[TraitType::RiskTolerance];
        float boldness = traits[TraitType::Boldness];
        // Flee if risk tolerance + boldness < 0.6 (coward threshold)
        if ((risk + boldness) < 0.6f) {
            intent.action_type  = ActionType::Flee;
            intent.need_context = NeedType::Safety;
            intent.priority     = 999.0f; // emergency priority
            return intent;
        }
    }

    // Get the highest-priority drive
    DriveScore top = DriveEngine::top_drive(needs, traits);

    if (top.need_type == NeedType::None || top.score <= 0.0f) {
        // No urgent need — idle
        intent.action_type = ActionType::Idle;
        intent.priority    = 0.0f;
        return intent;
    }

    // Check world snapshot for a source
    int idx = static_cast<int>(top.need_type);
    const WorldSnapshot::NearestSource& source = world.nearest[idx];

    if (source.is_valid && source.resource_id != INVALID_RESOURCE_ID) {
        intent.action_type  = ActionType::MoveToResource;
        intent.need_context = top.need_type;
        intent.target_id    = source.resource_id;
        intent.priority     = top.score;
    } else {
        // No source found — seek generically
        intent.action_type  = ActionType::Seek;
        intent.need_context = top.need_type;
        intent.target_id    = INVALID_RESOURCE_ID;
        intent.priority     = top.score;
    }

    return intent;
}

} // namespace simcore

