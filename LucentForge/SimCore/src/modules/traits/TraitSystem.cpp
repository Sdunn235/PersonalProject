// TraitSystem.cpp - Agent personality traits implementation
#include "TraitSystem.h"
#include <algorithm>
#include <nlohmann/json.hpp>

namespace LucentForge {

using json = nlohmann::json;

// Static trait names
const std::string TraitSystem::trait_names[8] = {
    "aggression", "boldness", "curiosity", "greed",
    "sociability", "loyalty", "patience", "risk_tolerance"
};

// Constructor: Initialize all traits to neutral (0.5)
TraitSystem::TraitSystem()
    : aggression(0.5), boldness(0.5), curiosity(0.5), greed(0.5),
      sociability(0.5), loyalty(0.5), patience(0.5), risk_tolerance(0.5) {}

// Get trait value by name (0.0-1.0)
double TraitSystem::get_trait(const std::string& trait_name) const {
    if (trait_name == "aggression") return aggression;
    if (trait_name == "boldness") return boldness;
    if (trait_name == "curiosity") return curiosity;
    if (trait_name == "greed") return greed;
    if (trait_name == "sociability") return sociability;
    if (trait_name == "loyalty") return loyalty;
    if (trait_name == "patience") return patience;
    if (trait_name == "risk_tolerance") return risk_tolerance;
    return 0.5;  // Default fallback
}

// Set trait value by name (with clamping to 0.0-1.0)
void TraitSystem::set_trait(const std::string& trait_name, double value) {
    double clamped = clamp(value);

    if (trait_name == "aggression") aggression = clamped;
    else if (trait_name == "boldness") boldness = clamped;
    else if (trait_name == "curiosity") curiosity = clamped;
    else if (trait_name == "greed") greed = clamped;
    else if (trait_name == "sociability") sociability = clamped;
    else if (trait_name == "loyalty") loyalty = clamped;
    else if (trait_name == "patience") patience = clamped;
    else if (trait_name == "risk_tolerance") risk_tolerance = clamped;
}

// Get how much a trait affects a specific action
// Example: aggression amplifies combat, patience dampens it
double TraitSystem::get_modifier_weight(const std::string& trait_name, const std::string& action_type) const {
    double trait_value = get_trait(trait_name);

    // Modifier formula: (trait_value - 0.5) * 2.0 + 1.0
    // This maps 0.0-1.0 to 0.0-2.0, with 0.5 (neutral) mapping to 1.0
    double modifier = (trait_value - 0.5) * 2.0 + 1.0;

    // Some traits may have inverse effects on certain actions
    if (trait_name == "patience" && (action_type == "attack" || action_type == "combat")) {
        // Patient agents REDUCE combat priority
        return 1.0 / modifier;  // Inverse: 0.0->2.0, 0.5->1.0, 1.0->0.5
    }

    if (trait_name == "boldness" && (action_type == "rest" || action_type == "hide")) {
        // Bold agents reduce resting/hiding
        return 1.0 / modifier;
    }

    // Default: direct correlation (high trait = amplified action)
    return modifier;
}

// Check if a trait name is valid
bool TraitSystem::is_valid_trait(const std::string& trait_name) const {
    for (int i = 0; i < 8; ++i) {
        if (trait_names[i] == trait_name) return true;
    }
    return false;
}

// Clamp value to 0.0-1.0 range
double TraitSystem::clamp(double value) {
    return std::max(0.0, std::min(1.0, value));
}

// Serialize to JSON
std::string TraitSystem::to_json() const {
    json j;
    j["aggression"] = aggression;
    j["boldness"] = boldness;
    j["curiosity"] = curiosity;
    j["greed"] = greed;
    j["sociability"] = sociability;
    j["loyalty"] = loyalty;
    j["patience"] = patience;
    j["risk_tolerance"] = risk_tolerance;

    return j.dump();
}

// Deserialize from JSON
TraitSystem TraitSystem::from_json(const std::string& json_str) {
    TraitSystem traits;

    try {
        json j = json::parse(json_str);

        if (j.contains("aggression")) traits.aggression = clamp(j["aggression"].get<double>());
        if (j.contains("boldness")) traits.boldness = clamp(j["boldness"].get<double>());
        if (j.contains("curiosity")) traits.curiosity = clamp(j["curiosity"].get<double>());
        if (j.contains("greed")) traits.greed = clamp(j["greed"].get<double>());
        if (j.contains("sociability")) traits.sociability = clamp(j["sociability"].get<double>());
        if (j.contains("loyalty")) traits.loyalty = clamp(j["loyalty"].get<double>());
        if (j.contains("patience")) traits.patience = clamp(j["patience"].get<double>());
        if (j.contains("risk_tolerance")) traits.risk_tolerance = clamp(j["risk_tolerance"].get<double>());
    } catch (const std::exception& e) {
        // JSON parse failed, return default traits
        traits = TraitSystem();
    }

    return traits;
}

}  // namespace LucentForge

