#pragma once

#include "NeedSystem.h"
#include <array>

namespace creatureRepo::need {

/**
 * @enum EPersonalityType
 * @brief Enumeration of NPC personality types for Phase 4.
 *
 * Each personality modifies need decay rates, thresholds, and priorities.
 * Static for Phase 4; dynamic personality in Phase 5+.
 */
enum class EPersonalityType : uint8_t {
    Social = 0,         // Highly social, fast social decay, low threshold
    Practical = 1,      // Practical focus, fast physical decay, social ignored
    Introverted = 2,    // Needs alone time, prefers rest, social avoidant
    Extroverted = 3,    // Social butterfly, fast social decay, high priority
    Cautious = 4,       // Alert personality, low thresholds, heightened urgency
    Relaxed = 5,        // Laid-back, high thresholds, slower urgency
    Count = 6           // Total personality types
};

/**
 * @class PersonalityNeedManager
 * @brief Extends NeedManager with personality-based need modifiers (Phase 4).
 *
 * Applies personality-based multipliers to:
 * - Decay rates (how fast needs degrade over time)
 * - Urgency thresholds (when needs become urgent)
 * - Priority weighting (which needs are most important)
 *
 * Inheritance Pattern:
 *   NeedManager (Phase 3B base) → PersonalityNeedManager (Phase 4 extension)
 *
 * Static Personalities (Phase 4):
 *   Personality is set at construction and never changes.
 *   Dynamic in Phase 5+ based on NPC experiences.
 *
 * Migration to Dynamic (Phase 5):
 *   DynamicPersonalityManager extends PersonalityNeedManager
 *   with personality drift based on memory and experience.
 */
class PersonalityNeedManager : public NeedManager {
public:
    /**
     * @brief Constructor with personality type.
     *
     * @param personality The personality type for this NPC
     */
    explicit PersonalityNeedManager(EPersonalityType personality);

    /**
     * @brief Update all needs with personality-based decay modifiers.
     *
     * Overrides NeedManager::Update() to apply personality decay multipliers.
     * Formula: CurrentValue = max(0.0, CurrentValue - (BaseDecay * PersonalityMultiplier * deltaSeconds))
     *
     * @param deltaSeconds Time elapsed since last update, in seconds
     * @throws std::invalid_argument if deltaSeconds is negative
     * @throws std::runtime_error if manager not initialized
     */
    void Update(double deltaSeconds) override;

    /**
     * @brief Get the most urgent need with personality-based priority weighting.
     *
     * Overrides NeedManager::GetMostUrgentNeed() to apply priority weighting.
     * Selection: (CurrentValue * PriorityWeight) - lowest weighted value = most urgent
     *
     * @return Index of the most urgent need (weighted by personality)
     * @throws std::runtime_error if manager not initialized or no needs
     */
    size_t GetMostUrgentNeed() const override;

    /**
     * @brief Get this NPC's personality type.
     *
     * @return The EPersonalityType for this manager
     */
    EPersonalityType GetPersonality() const;

private:
    EPersonalityType personality_;

    /**
     * @brief Get decay rate multiplier for a need (0.5x to 2.0x).
     *
     * @param need_type The type of need
     * @return Multiplier: > 1.0 = decays faster, < 1.0 = decays slower
     */
    double GetDecayMultiplier(ENeedType need_type) const;

    /**
     * @brief Get urgency threshold multiplier (0.2x to 2.0x).
     *
     * Threshold is multiplied by this value.
     * < 1.0 = becomes urgent sooner, > 1.0 = takes longer to become urgent
     *
     * @param need_type The type of need
     * @return Threshold multiplier
     */
    double GetThresholdMultiplier(ENeedType need_type) const;

    /**
     * @brief Get priority weight for a need (0.1x to 2.0x).
     *
     * Used in GetMostUrgentNeed to weight needs by personality priority.
     * Higher weight = personality considers this more important
     *
     * @param need_type The type of need
     * @return Priority weight for GetMostUrgentNeed() calculation
     */
    double GetPriorityWeight(ENeedType need_type) const;

    // ========================================================================
    // Modifier Lookup Tables (Static, Approved for Phase 4)
    // ========================================================================

    /**
     * @brief Decay rate multipliers by personality and need type.
     *
     * Index: [personality][need_type]
     * Value: 0.5x = half speed, 2.0x = double speed
     * Approved values from Phase 4 Planning Charter
     */
    static constexpr std::array<std::array<double, 5>, 6> DECAY_MULTIPLIERS{{
        // Social personality: Hunger, Thirst, Rest, Social, Energy
        std::array<double, 5>{1.0, 1.0, 0.8, 1.5, 1.0},
        // Practical personality
        std::array<double, 5>{1.2, 1.2, 0.9, 0.3, 1.5},
        // Introverted personality
        std::array<double, 5>{1.0, 1.0, 1.2, 0.3, 1.0},
        // Extroverted personality
        std::array<double, 5>{1.0, 1.0, 0.8, 2.0, 1.2},
        // Cautious personality
        std::array<double, 5>{1.0, 1.0, 1.2, 0.5, 1.2},
        // Relaxed personality
        std::array<double, 5>{0.9, 0.9, 0.8, 1.0, 0.8}
    }};

    /**
     * @brief Threshold multipliers by personality and need type.
     *
     * Index: [personality][need_type]
     * Value: 0.2x = becomes urgent sooner, 2.0x = takes longer
     * Only Cautious and Relaxed have explicit multipliers
     * Others use 1.0x (base threshold)
     */
    static constexpr std::array<std::array<double, 5>, 6> THRESHOLD_MULTIPLIERS{{
        // Social: all 1.0x (no explicit threshold modification)
        std::array<double, 5>{1.0, 1.0, 1.0, 1.0, 1.0},
        // Practical: all 1.0x
        std::array<double, 5>{1.0, 1.0, 1.0, 1.0, 1.0},
        // Introverted: all 1.0x
        std::array<double, 5>{1.0, 1.0, 1.0, 1.0, 1.0},
        // Extroverted: all 1.0x
        std::array<double, 5>{1.0, 1.0, 1.0, 1.0, 1.0},
        // Cautious: lower thresholds (more alert, urgent sooner)
        std::array<double, 5>{0.4, 0.4, 0.5, 0.3, 0.4},
        // Relaxed: higher thresholds (less urgent)
        std::array<double, 5>{0.2, 0.2, 0.2, 0.6, 0.2}
    }};

    /**
     * @brief Priority weights by personality and need type.
     *
     * Index: [personality][need_type]
     * Value: Weight used in GetMostUrgentNeed() calculation
     * Higher = this personality considers this need more important
     */
    static constexpr std::array<std::array<double, 5>, 6> PRIORITY_WEIGHTS{{
        // Social: prioritizes social 2.0x over others
        std::array<double, 5>{0.8, 0.8, 0.8, 2.0, 0.8},
        // Practical: prioritizes physical needs, social 0.3x (ignored)
        std::array<double, 5>{1.2, 1.2, 1.0, 0.3, 1.2},
        // Introverted: needs rest, social 0.2x (avoided)
        std::array<double, 5>{1.0, 1.0, 1.2, 0.2, 1.0},
        // Extroverted: loves social 2.0x
        std::array<double, 5>{0.8, 0.8, 0.8, 2.0, 1.0},
        // Cautious: prioritizes rest and energy (alert personality)
        std::array<double, 5>{1.0, 1.0, 1.2, 0.5, 1.2},
        // Relaxed: balanced, slightly social-inclined
        std::array<double, 5>{0.8, 0.8, 0.6, 1.2, 0.7}
    }};
};

}  // namespace creatureRepo::need

