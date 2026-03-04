#pragma once
#include "simcore/agent/NeedSystem.h"
#include "simcore/agent/TraitSystem.h"
#include "simcore/sim/EventLog.h"
#include <cstdint>
#include <string>

namespace simcore {

// ── Action types ─────────────────────────────────────────────────────────
enum class ActionType : uint8_t {
    Idle = 0,
    MoveToResource,   // navigate to a resource location
    ConsumeResource,  // interact with/consume from a resource node
    Socialize,        // social need satisfaction
    Seek,             // generic seek behavior
    Flee,             // safety override
    Rest,             // sleep/stamina recovery
    Custom,
};

// ── World snapshot ────────────────────────────────────────────────────────
// Minimal read-only view of the world fed into the decision engine.
// Provided by the Adapter Layer — SimCore never queries the world directly.
struct WorldSnapshot {
    struct NearestSource {
        ResourceID  resource_id = INVALID_RESOURCE_ID;
        NeedType    need_type   = NeedType::None;
        float       distance    = 0.0f;    // sim-space units
        bool        is_valid    = false;
    };

    NearestSource nearest[NEED_COUNT]{};   // one candidate per need type
    bool          is_safe = true;          // threat presence near agent
    float         threat_distance = 999.f; // distance to nearest threat
};

// ── Action intent ─────────────────────────────────────────────────────────
// Output of DecisionEngine. Executed by the Adapter/Engine layer.
// DecisionEngine only DECIDES. It never mutates world state.
struct ActionIntent {
    ActionType  action_type  = ActionType::Idle;
    NeedType    need_context = NeedType::None;  // which need drives this
    AgentID     agent_id     = INVALID_AGENT_ID;
    ResourceID  target_id    = INVALID_RESOURCE_ID;
    float       priority     = 0.0f;
};

/**
 * DecisionEngine — Pure decision layer.
 *
 * Takes AgentState (need + trait) + WorldSnapshot → produces ActionIntent.
 * No world mutation occurs here. No engine types. No Actor references.
 */
class DecisionEngine {
public:
    /// Produce an ActionIntent for the agent this SimStep.
    static ActionIntent decide(AgentID          agent_id,
                               const NeedState& needs,
                               const TraitSet&  traits,
                               const WorldSnapshot& world);
};

} // namespace simcore

