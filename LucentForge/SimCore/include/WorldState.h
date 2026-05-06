#ifndef LUCENTFORGE_WORLD_STATE_H
#define LUCENTFORGE_WORLD_STATE_H

#include <string>
#include <vector>
#include <map>
#include <memory>
#include <cstdint>
#include "Agent.h"

namespace LucentForge {

/**
 * WorldState: Complete simulation state
 *
 * Tracks:
 * - Time (cycle number, phase: morning|afternoon|evening|night, weather)
 * - All agents currently in world
 * - All locations with connectivity
 * - All items available
 * - All factions and their state
 *
 * Provides query interface:
 * - Find agent by ID
 * - Find items at location
 * - Find agents at location
 * - Pathfinding between locations
 *
 * Serializes to/from JSON per DATA_CONTRACTS.md
 */
class WorldState {
public:
    // Time
    struct TimeState {
        uint64_t cycle = 0;
        enum Phase { MORNING, AFTERNOON, EVENING, NIGHT } phase = MORNING;
        enum Weather { CLEAR, RAIN, STORM } weather = CLEAR;
    } time;

    // Location
    struct Location {
        std::string location_id;
        std::string name;
        enum Type { SETTLEMENT, FARM, DUNGEON, WILDERNESS, LANDMARK } type = SETTLEMENT;

        struct Position {
            double x = 0.0;
            double y = 0.0;
        } position;

        std::vector<std::string> agents_present;  // agent IDs

        struct Resources {
            int food = 0;
            int water = 0;
            double safety_level = 0.8;
        } resources;

        struct Connection {
            std::string destination_id;
            int travel_time_cycles = 1;
        };
        std::vector<Connection> connections;
    };

    // Item
    struct Item {
        std::string item_id;
        std::string name;
        enum Category { WEAPON, ARMOR, TOOL, CONSUMABLE, MATERIAL } category = TOOL;
        enum Rarity { COMMON, UNCOMMON, RARE, LEGENDARY } rarity = COMMON;

        std::map<std::string, double> properties;  // damage, durability, weight, etc.
        int value = 0;
    };

    // Faction
    struct Faction {
        std::string faction_id;
        std::string name;
        std::vector<std::string> members;  // agent IDs
        int treasury = 0;
    };

    // Container: all agents
    std::map<std::string, std::shared_ptr<Agent>> agents;

    // Container: all locations
    std::vector<Location> locations;

    // Container: all items
    std::vector<Item> items;

    // Container: all factions
    std::vector<Faction> factions;

    // Constructor
    WorldState();

    // Lifecycle
    void tick();  // Advance time, tick all agents
    void advance_time();  // Move to next cycle/phase

    // Query interface
    std::shared_ptr<Agent> find_agent(const std::string& agent_id) const;
    Location* find_location(const std::string& location_id);
    Item* find_item(const std::string& item_id);

    // Agents at location
    std::vector<std::shared_ptr<Agent>> get_agents_at(const std::string& location_id) const;

    // Items at location
    std::vector<Item*> get_items_at(const std::string& location_id) const;

    // Path finding (stub)
    std::vector<std::string> find_path(const std::string& from_id, const std::string& to_id) const;

    // JSON Serialization
    std::string to_json() const;
    static WorldState from_json(const std::string& json);

    // Utility
    std::string get_phase_name() const;
    std::string get_weather_name() const;
};

}  // namespace LucentForge

#endif  // LUCENTFORGE_WORLD_STATE_H

