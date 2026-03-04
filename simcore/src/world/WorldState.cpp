#include "simcore/world/WorldState.h"
#include <cmath>
#include <optional>
#include <limits>

namespace simcore {

ResourceID WorldState::add_resource(ResourceNode node) {
    ResourceID id = m_next_resource_id++;
    node.id = id;
    m_resources.emplace(id, std::move(node));
    return id;
}

void WorldState::remove_resource(ResourceID id) {
    m_resources.erase(id);
}

ResourceNode* WorldState::find_resource(ResourceID id) {
    auto it = m_resources.find(id);
    return it != m_resources.end() ? &it->second : nullptr;
}

const ResourceNode* WorldState::find_resource(ResourceID id) const {
    auto it = m_resources.find(id);
    return it != m_resources.end() ? &it->second : nullptr;
}

ResourceTag WorldState::need_to_tag(NeedType need_type) {
    switch (need_type) {
        case NeedType::Hunger:  return ResourceTag::FoodSource;
        case NeedType::Thirst:  return ResourceTag::WaterSource;
        case NeedType::Sleep:   return ResourceTag::BedSource;
        case NeedType::Shelter: return ResourceTag::ShelterStructure;
        default:                return ResourceTag::Generic;
    }
}

float WorldState::dist2(float ax, float ay, float bx, float by) {
    float dx = ax - bx, dy = ay - by;
    return dx * dx + dy * dy;
}

std::optional<ResourceID> WorldState::find_nearest_for_need(
    NeedType need_type,
    float origin_x, float origin_y,
    float max_dist) const {

    ResourceTag target_tag = need_to_tag(need_type);
    float max_dist2 = max_dist * max_dist;
    float best_dist2 = std::numeric_limits<float>::max();
    ResourceID best_id = INVALID_RESOURCE_ID;

    for (const auto& [id, node] : m_resources) {
        if (node.tag != target_tag) continue;
        if (node.is_depleted()) continue;

        float d2 = dist2(origin_x, origin_y, node.pos_x, node.pos_y);
        if (d2 < max_dist2 && d2 < best_dist2) {
            best_dist2 = d2;
            best_id    = id;
        }
    }

    if (best_id == INVALID_RESOURCE_ID) return std::nullopt;
    return best_id;
}

void WorldState::tick(uint64_t current_step, EventLog& log) {
    for (auto& [id, node] : m_resources) {
        node.regen_tick(current_step, log);
    }
}

} // namespace simcore

