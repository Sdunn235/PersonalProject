#pragma once
#include "simcore/world/ResourceNode.h"
#include "simcore/agent/NeedSystem.h"
#include <unordered_map>
#include <vector>
#include <optional>

namespace simcore {

/**
 * WorldState — The authoritative, persistent state of the simulation world.
 *
 * Contains all resource nodes, regions, and global variables.
 * Must be serializable. Replaces engine-side GetAllActorsWithTag queries.
 *
 * The Adapter Layer populates/syncs WorldState from Unreal actors on init.
 * After that, SimCore mutates WorldState directly.
 */
class WorldState {
public:
    WorldState() = default;

    // ── Resource management ───────────────────────────────────────────────

    /// Register a resource node. Returns the node's ID.
    ResourceID add_resource(ResourceNode node);

    /// Remove a resource node by ID.
    void remove_resource(ResourceID id);

    ResourceNode*       find_resource(ResourceID id);
    const ResourceNode* find_resource(ResourceID id) const;

    /// Find the nearest resource node satisfying a need type, within max_dist.
    /// Returns nullopt if none found.
    std::optional<ResourceID> find_nearest_for_need(NeedType need_type,
                                                     float origin_x, float origin_y,
                                                     float max_dist = 99999.0f) const;

    /// All resource nodes.
    const std::unordered_map<ResourceID, ResourceNode>& resources() const { return m_resources; }

    // ── World tick ────────────────────────────────────────────────────────

    /// Advance all resource regen/depletion by one SimStep.
    void tick(uint64_t current_step, EventLog& log);

    // ── Stats ─────────────────────────────────────────────────────────────
    size_t resource_count() const { return m_resources.size(); }

private:
    std::unordered_map<ResourceID, ResourceNode> m_resources;
    ResourceID m_next_resource_id = 1u;

    /// Map NeedType to ResourceTag for source lookup.
    static ResourceTag need_to_tag(NeedType need_type);

    static float dist2(float ax, float ay, float bx, float by);
};

} // namespace simcore

