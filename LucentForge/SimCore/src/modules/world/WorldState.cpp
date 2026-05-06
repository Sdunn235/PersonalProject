// WorldState.cpp - Stub implementation of WorldState class
// Full implementation will follow in Phase 3

#include "WorldState.h"

namespace LucentForge {

WorldState::WorldState() = default;

void WorldState::tick() {
    // TODO: Advance time, tick all agents (Phase 3)
}

void WorldState::advance_time() {
    // TODO: Move to next cycle/phase (Phase 3)
}

std::shared_ptr<Agent> WorldState::find_agent(const std::string& agent_id) const {
    auto it = agents.find(agent_id);
    if (it != agents.end()) {
        return it->second;
    }
    return nullptr;
}

WorldState::Location* WorldState::find_location(const std::string& location_id) {
    for (auto& loc : locations) {
        if (loc.location_id == location_id) {
            return &loc;
        }
    }
    return nullptr;
}

WorldState::Item* WorldState::find_item(const std::string& item_id) {
    for (auto& item : items) {
        if (item.item_id == item_id) {
            return &item;
        }
    }
    return nullptr;
}

std::vector<std::shared_ptr<Agent>> WorldState::get_agents_at(const std::string& location_id) const {
    std::vector<std::shared_ptr<Agent>> result;
    // TODO: Return agents at location (Phase 3)
    return result;
}

std::vector<WorldState::Item*> WorldState::get_items_at(const std::string& location_id) const {
    std::vector<WorldState::Item*> result;
    // TODO: Return items at location (Phase 3)
    return result;
}

std::vector<std::string> WorldState::find_path(const std::string& from_id, const std::string& to_id) const {
    std::vector<std::string> result;
    // TODO: Implement pathfinding (Phase 3+)
    return result;
}

std::string WorldState::to_json() const {
    // TODO: Serialize to JSON (Phase 3)
    return "{}";
}

WorldState WorldState::from_json(const std::string& json) {
    // TODO: Deserialize from JSON (Phase 3)
    return WorldState();
}

std::string WorldState::get_phase_name() const {
    switch (time.phase) {
        case TimeState::MORNING:    return "morning";
        case TimeState::AFTERNOON:  return "afternoon";
        case TimeState::EVENING:    return "evening";
        case TimeState::NIGHT:      return "night";
        default:                    return "unknown";
    }
}

std::string WorldState::get_weather_name() const {
    switch (time.weather) {
        case TimeState::CLEAR:  return "clear";
        case TimeState::RAIN:   return "rain";
        case TimeState::STORM:  return "storm";
        default:                return "unknown";
    }
}

}  // namespace LucentForge

