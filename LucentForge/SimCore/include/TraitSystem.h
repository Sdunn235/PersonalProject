#ifndef LUCENTFORGE_TRAIT_SYSTEM_H
#define LUCENTFORGE_TRAIT_SYSTEM_H

#include <string>
#include <map>
#include <cmath>

namespace LucentForge {

/**
 * TraitSystem: Store and weight agent personality traits
 *
 * 8 core traits (normalized 0.0–1.0):
 * - aggression: tendency toward combat
 * - boldness: willingness to take risks
 * - curiosity: drive to explore/learn
 * - greed: desire for wealth/resources
 * - sociability: comfort with others
 * - loyalty: commitment to allies
 * - patience: tolerance for waiting
 * - risk_tolerance: comfort with danger
 *
 * Traits are STABLE (don't change during session)
 * Traits MODIFY decision priorities (not directly cause actions)
 */
class TraitSystem {
public:
    // Constructor: initialize all traits to 0.5 (neutral)
    TraitSystem();

    // Get/Set individual traits (0.0–1.0, clamped)
    double get_trait(const std::string& trait_name) const;
    void set_trait(const std::string& trait_name, double value);

    // Get modifier weight for a trait affecting a specific action
    // Example: get_modifier_weight("aggression", "attack") → 1.5 (amplifies)
    //          get_modifier_weight("patience", "attack") → 0.7 (dampens)
    double get_modifier_weight(const std::string& trait_name, const std::string& action_type) const;

    // JSON Serialization
    std::string to_json() const;
    static TraitSystem from_json(const std::string& json);

    // Utility: validate trait name
    bool is_valid_trait(const std::string& trait_name) const;

    // Get all trait names
    static const std::string trait_names[8];

private:
    // 8 core traits (0.0–1.0)
    double aggression = 0.5;
    double boldness = 0.5;
    double curiosity = 0.5;
    double greed = 0.5;
    double sociability = 0.5;
    double loyalty = 0.5;
    double patience = 0.5;
    double risk_tolerance = 0.5;

    // Clamp value to 0.0–1.0 range
    static double clamp(double value);
};

}  // namespace LucentForge

#endif  // LUCENTFORGE_TRAIT_SYSTEM_H

