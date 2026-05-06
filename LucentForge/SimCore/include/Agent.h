#ifndef LUCENTFORGE_AGENT_H
#define LUCENTFORGE_AGENT_H

#include <string>
#include <vector>
#include <map>
#include <memory>
#include <cstdint>

namespace LucentForge {

// Forward declaration
struct Trait;
struct Need;
struct MemoryEvent;

/**
 * Agent: Core entity for all NPCs and players in LucentForge
 *
 * Stores:
 * - Identity (name, role, ID)
 * - Traits (stable personality modifiers)
 * - Needs (dynamic urgency states)
 * - Skills (competency levels)
 * - Memory (events, relationships, experiences)
 * - Social Graph (faction, reputation, relationships)
 * - Inventory (items, wealth)
 * - Current Intent (what they want to do next)
 *
 * Serializes to/from JSON per DATA_CONTRACTS.md
 */
class Agent {
public:
    // Identity
    std::string agent_id;
    std::string name;
    std::string role;  // merchant|warrior|farmer|scholar|adventurer

    // Traits (0.0–1.0, stable)
    struct TraitSet {
        double aggression = 0.5;
        double boldness = 0.5;
        double curiosity = 0.5;
        double greed = 0.5;
        double sociability = 0.5;
        double loyalty = 0.5;
        double patience = 0.5;
        double risk_tolerance = 0.5;
    } traits;

    // Needs (0.0–1.0, dynamic)
    struct NeedState {
        double hunger = 0.0;
        double thirst = 0.1;
        double sleep = 0.2;
        double safety = 0.0;
        double social = 0.3;
        double wealth = 0.5;
        double power = 0.2;
        double curiosity = 0.4;
    } needs;

    // Skills (0–10 scale)
    std::map<std::string, int> skills;

    // Inventory
    struct InventoryItem {
        std::string item_id;
        int quantity = 1;
    };
    std::vector<InventoryItem> inventory;
    int wealth = 0;

    // Ownership
    struct Ownership {
        std::string location_id;
        std::string ownership_type;  // land|building|business
        int income_per_cycle = 0;
    };
    std::vector<Ownership> owned_locations;

    // Memory (events, relationships, experience)
    struct Memory {
        std::vector<MemoryEvent> events;
        std::map<std::string, struct RelationshipStatus> relationships;
        int success_count = 0;
        std::vector<std::string> trauma;
    } memory;

    // Social Graph
    struct SocialGraph {
        std::string faction;
        int reputation = 0;
        std::map<std::string, int> debt;  // owed_to -> amount
        std::vector<std::string> oaths;
    } social_graph;

    // Current Intent
    struct Intent {
        std::string action_type;  // travel|work|trade|interact|rest|attack
        std::string target_id;    // agent|location|item
        struct Position {
            double x = 0.0;
            double y = 0.0;
        } target_location;
        double priority = 0.0;
        std::string need_context;  // which need is driving this?
    } current_intent;

    // Constructor
    Agent();
    Agent(const std::string& id, const std::string& agent_name, const std::string& agent_role);

    // Lifecycle
    void tick();  // Update needs, memory, intent
    void refresh_stats();  // Derive current effective stats

    // JSON Serialization
    std::string to_json() const;
    static Agent from_json(const std::string& json);

    // Utility
    double get_trait(const std::string& trait_name) const;
    double get_need(const std::string& need_name) const;
    void set_need(const std::string& need_name, double value);
};

// Relationship Status (for memory)
struct RelationshipStatus {
    double trust = 0.5;
    double fear = 0.0;
    double loyalty = 0.5;
};

// Memory Event
struct MemoryEvent {
    std::string event_id;
    std::string event_type;  // combat|dialogue|trade|injury|success
    uint64_t timestamp_cycle = 0;
    std::string related_agent;
    std::map<std::string, std::string> details;
};

}  // namespace LucentForge

#endif  // LUCENTFORGE_AGENT_H

