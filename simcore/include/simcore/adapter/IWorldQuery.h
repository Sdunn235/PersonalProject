#pragma once
#include "simcore/agent/DecisionEngine.h"
#include "simcore/world/WorldState.h"

namespace simcore {

/**
 * IWorldQuery — Pure interface: Adapter Layer → SimCore.
 *
 * The Adapter Layer implements this using Unreal's GetAllActorsWithTag or
 * a WorldState spatial index. SimCore only sees this interface.
 *
 * Replaces the direct GetAllActorsWithTag call in FindSourceByNeed Blueprint.
 */
class IWorldQuery {
public:
    virtual ~IWorldQuery() = default;

    /// Build a WorldSnapshot for the given agent at the given position.
    virtual WorldSnapshot query_snapshot(AgentID agent_id,
                                         float origin_x,
                                         float origin_y,
                                         float origin_z) const = 0;
};

/**
 * IActionExecutor — Pure interface: SimCore → Adapter Layer.
 *
 * The Adapter Layer implements this to translate ActionIntent into
 * engine-specific calls (MovetoNeedTarget, BeginInteractionAtNeedSource, etc).
 *
 * SimCore produces intents. The engine executes them.
 */
class IActionExecutor {
public:
    virtual ~IActionExecutor() = default;

    /// Execute an action intent for the given agent.
    virtual void execute(const ActionIntent& intent) = 0;
};

/**
 * WorldStateWorldQuery — Default IWorldQuery backed by SimCore's WorldState.
 *
 * Used in headless tests and when the Adapter is not present.
 */
class WorldStateWorldQuery final : public IWorldQuery {
public:
    explicit WorldStateWorldQuery(const WorldState& ws) : m_world(ws) {}

    WorldSnapshot query_snapshot(AgentID agent_id,
                                 float origin_x,
                                 float origin_y,
                                 float origin_z) const override;

private:
    const WorldState& m_world;
};

} // namespace simcore

