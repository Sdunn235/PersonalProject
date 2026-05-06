#ifndef LUCENTFORGE_COMBAT_ENGINE_H
#define LUCENTFORGE_COMBAT_ENGINE_H

#include <string>
#include <vector>
#include <map>
#include <memory>
#include <cstdint>

namespace LucentForge {

// Forward declaration
class Agent;

/**
 * CombatEngine: Pure combat logic (wrapper around iso_rpg_lab)
 *
 * Responsible for:
 * - Simulating combat turns (attacks, abilities, items)
 * - Damage calculations, hit chance, crits
 * - Status effects (poison, etc.)
 * - Combat AI decision making
 *
 * Integrates iso_rpg_lab's:
 * - gameplay/combat.py (Fighter, take_turn, damage_roll)
 * - data/items.json, abilities.json, enemies.json
 * - gameplay/rules.py (constants)
 *
 * Result format matches iso_rpg_lab's take_turn() output
 * (deterministic for validation)
 */
class CombatEngine {
public:
    // Combat result from a single turn
    struct TurnResult {
        std::string type;  // "hit" | "miss" | "use_item" | "heal"
        int amount = 0;
        bool was_crit = false;
        std::string ability_id;
        std::string element;  // "neutral" | "fire" | "ice" | etc.
        std::string item_id;
        int cycles_restored = 0;
    };

    // RNG interface (for deterministic seeding)
    class RNG {
    public:
        virtual ~RNG() = default;
        virtual bool chance(double pct) = 0;  // 0–100
        virtual int range_int(int min, int max) = 0;
    };

    // Constructor
    CombatEngine();

    // Initialize from JSON data (items, abilities, enemies, rules)
    bool load_config(const std::string& data_path);

    // Simulate a single turn for `attacker` vs `defender`
    // Returns the action taken and its result
    TurnResult simulate_turn(
        std::shared_ptr<Agent> attacker,
        std::shared_ptr<Agent> defender,
        std::shared_ptr<RNG> rng
    );

    // Simulate a full combat encounter (multiple turns)
    // Returns list of turn results and final agent states
    struct CombatResult {
        std::vector<TurnResult> turn_history;
        std::shared_ptr<Agent> winner;  // nullptr if draw
        uint32_t total_turns = 0;
        uint64_t total_damage_dealt = 0;
    };

    CombatResult simulate_combat(
        std::shared_ptr<Agent> player,
        std::shared_ptr<Agent> enemy,
        std::shared_ptr<RNG> rng,
        uint32_t max_turns = 1000
    );

    // Damage calculation (exposed for testing)
    struct DamageCalcResult {
        int final_damage = 0;
        bool was_crit = false;
    };

    DamageCalcResult calculate_damage(
        std::shared_ptr<Agent> attacker,
        std::shared_ptr<Agent> defender,
        const std::string& ability_id,
        std::shared_ptr<RNG> rng
    );

    // Hit chance calculation (exposed for testing)
    bool check_hit(
        std::shared_ptr<Agent> attacker,
        std::shared_ptr<Agent> defender,
        std::shared_ptr<RNG> rng
    );

    // JSON Serialization of combat state
    std::string serialize_combat_state(
        std::shared_ptr<Agent> player,
        std::shared_ptr<Agent> enemy
    ) const;

    // Utility
    void set_seed(uint64_t seed);  // For reproducible testing
};

// Convenience: Default RNG implementation (seeded)
class SeededRNG : public CombatEngine::RNG {
public:
    explicit SeededRNG(uint64_t seed = 0);
    bool chance(double pct) override;
    int range_int(int min, int max) override;

private:
    uint64_t state;
    uint64_t next();
};

}  // namespace LucentForge

#endif  // LUCENTFORGE_COMBAT_ENGINE_H

