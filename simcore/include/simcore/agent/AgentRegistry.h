#pragma once
#include "simcore/agent/NeedSystem.h"
#include "simcore/agent/TraitSystem.h"
#include "simcore/agent/DecisionEngine.h"
#include "simcore/sim/EventLog.h"
#include <unordered_map>
#include <vector>
#include <memory>

namespace simcore {

// ── Full agent state ──────────────────────────────────────────────────────
struct AgentState {
    AgentID      id           = INVALID_AGENT_ID;
    NeedState    needs;
    BaseTraits   base_traits;
    TraitSet     derived_traits;
    ActionIntent current_intent;
    bool         is_alive = true;
};

/**
 * AgentRegistry — Owns and manages all agents in the simulation.
 *
 * Central authority for agent lifecycle:
 *   spawn → tick → death → removal
 *
 * The registry does NOT know about Unreal. Actors register an AgentID via
 * the Adapter Layer, which maps Actor → AgentID.
 */
class AgentRegistry {
public:
    AgentRegistry() = default;

    /// Spawn a new agent and return its ID.
    AgentID spawn(const BaseTraits& base_traits, const NeedState& initial_needs);

    /// Remove a dead agent.
    void remove(AgentID id);

    /// Tick all living agents: decay needs, re-derive traits, run decision.
    /// Returns all intents produced this tick.
    std::vector<ActionIntent> tick_all(float delta_seconds,
                                       const WorldSnapshot& world_snap,
                                       EventLog& log,
                                       uint64_t current_step);

    AgentState*       find(AgentID id);
    const AgentState* find(AgentID id) const;

    size_t count() const { return m_agents.size(); }

    const std::unordered_map<AgentID, AgentState>& all() const { return m_agents; }

private:
    std::unordered_map<AgentID, AgentState> m_agents;
    AgentID m_next_id = 1u;
};

} // namespace simcore

