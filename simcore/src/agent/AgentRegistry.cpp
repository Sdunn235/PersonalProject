#include "simcore/agent/AgentRegistry.h"
#include "simcore/agent/NeedSystem.h"
#include "simcore/agent/TraitSystem.h"
#include "simcore/agent/DriveEngine.h"
#include "simcore/agent/DecisionEngine.h"

namespace simcore {

AgentID AgentRegistry::spawn(const BaseTraits& base_traits,
                              const NeedState&  initial_needs) {
    AgentID new_id = m_next_id++;

    AgentState state;
    state.id           = new_id;
    state.base_traits  = base_traits;
    state.needs        = initial_needs;
    state.derived_traits = TraitSystem::derive(base_traits, nullptr, 0, nullptr, 0);
    state.is_alive     = true;

    m_agents.emplace(new_id, std::move(state));
    return new_id;
}

void AgentRegistry::remove(AgentID id) {
    m_agents.erase(id);
}

std::vector<ActionIntent> AgentRegistry::tick_all(float delta_seconds,
                                                    const WorldSnapshot& world_snap,
                                                    EventLog& log,
                                                    uint64_t  current_step) {
    std::vector<ActionIntent> intents;
    intents.reserve(m_agents.size());

    for (auto& [id, state] : m_agents) {
        if (!state.is_alive) continue;

        // 1. Decay needs
        NeedSystem::tick(state.needs, delta_seconds);

        // 2. Check for critical needs → log events
        for (int i = 1; i < NEED_COUNT; ++i) {
            const NeedRecord& nr = state.needs.needs[i];
            if (NeedSystem::is_critical(nr)) {
                log.record(current_step, EventType::NeedCritical,
                           id, INVALID_RESOURCE_ID, nr.current_value,
                           "critical");
            }
        }

        // 3. Re-derive traits (no modifiers for now — reserved for future effects)
        state.derived_traits = TraitSystem::derive(state.base_traits, nullptr, 0, nullptr, 0);

        // 4. Decide
        ActionIntent intent = DecisionEngine::decide(id, state.needs, state.derived_traits, world_snap);
        state.current_intent = intent;
        intents.push_back(intent);
    }

    return intents;
}

AgentState* AgentRegistry::find(AgentID id) {
    auto it = m_agents.find(id);
    return it != m_agents.end() ? &it->second : nullptr;
}

const AgentState* AgentRegistry::find(AgentID id) const {
    auto it = m_agents.find(id);
    return it != m_agents.end() ? &it->second : nullptr;
}

} // namespace simcore

