#pragma once
#include "simcore/sim/EventLog.h"
#include <cstdint>
#include <string>

namespace simcore {

// ── Resource categories ───────────────────────────────────────────────────
enum class ResourceCategory : uint8_t {
    Renewable  = 0,  // forest, wildlife, soil
    SemiRenewable,   // rare herbs, magic nodes
    Finite,          // ore, stone, artifacts
};

// ── Resource type tags ────────────────────────────────────────────────────
enum class ResourceTag : uint8_t {
    Generic = 0,
    FoodSource,
    WaterSource,
    BedSource,
    OreVein,
    Forest,
    WildlifePopulation,
    ShelterStructure,
};

/**
 * ResourceNode — A persistent, depleting, possibly regenerating world resource.
 *
 * Implements the WORLD_RESOURCE_MODEL.md spec:
 *   "If a forest is cut, it must matter."
 *   "If a mountain is mined, it must leave a scar."
 */
struct ResourceNode {
    ResourceID       id           = INVALID_RESOURCE_ID;
    ResourceTag      tag          = ResourceTag::Generic;
    ResourceCategory category     = ResourceCategory::Renewable;
    std::string      name;

    float quantity      = 100.0f;   // current amount
    float max_capacity  = 100.0f;   // ceiling
    float regen_rate    = 0.0f;     // units/SimStep (0 = finite/no regen)

    // World position (engine-agnostic — interpreted by adapter)
    float pos_x = 0.0f;
    float pos_y = 0.0f;
    float pos_z = 0.0f;

    bool  is_depleted() const { return quantity <= 0.0f; }
    bool  is_full()     const { return quantity >= max_capacity; }

    /// Consume up to `amount` from this node. Returns actual amount consumed.
    float consume(float amount, uint64_t step, EventLog& log,
                  AgentID consumer = INVALID_AGENT_ID);

    /// Apply one SimStep of regeneration.
    void  regen_tick(uint64_t step, EventLog& log);
};

} // namespace simcore

