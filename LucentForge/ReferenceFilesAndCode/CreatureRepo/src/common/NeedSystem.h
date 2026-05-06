#pragma once

#include <cstdint>
#include <vector>
#include <stdexcept>

namespace creatureRepo::need {

/**
 * @enum ENeedType
 * @brief Enumeration of possible need types for NPCs.
 *
 * Mirrors Unreal's E_NPCNeedType enum for compatibility.
 * Extensible for Phase 4 personality-driven modifiers.
 */
enum class ENeedType : uint8_t {
    Hunger = 0,
    Thirst = 1,
    Rest = 2,
    Social = 3,
    Energy = 4,
    // Extensible for future needs
    Count = 5  // Total number of need types
};

/**
 * @struct NPCNeed
 * @brief Represents a single need for an NPC.
 *
 * Mirrors Unreal's S_NPCNeed struct. Each need tracks:
 * - The type of need (hunger, thirst, etc.)
 * - Current satisfaction level (0.0 = critical, 1.0 = fully satisfied)
 * - Threshold at which satisfaction is triggered (urgency point)
 * - Decay rate per second (how fast the need grows over time)
 *
 * Note: CurrentValue DECREASES over time (decay subtracts from it),
 * so lower values = more urgent. This matches Unreal Blueprint logic.
 */
struct NPCNeed {
    ENeedType NeedType;
    double CurrentValue;           // Range: [0.0, 1.0], 0=critical
    double Threshold;              // Urgency trigger point
    double DecayRatePerSecond;     // How fast need decays (subtracts per second)

    /**
     * @brief Constructor with default values.
     *
     * @param type The type of need
     * @param initialValue Starting value (typically 1.0 for satisfied)
     * @param threshold Urgency threshold (typically 0.3-0.5)
     * @param decayRate Decay rate in units per second
     */
    NPCNeed(ENeedType type = ENeedType::Hunger,
            double initialValue = 1.0,
            double threshold = 0.3,
            double decayRate = 0.1)
        : NeedType(type),
          CurrentValue(initialValue),
          Threshold(threshold),
          DecayRatePerSecond(decayRate) {}

    /**
     * @brief Check if this need has exceeded its urgency threshold.
     *
     * @return true if CurrentValue <= Threshold, false otherwise
     */
    bool IsUrgent() const {
        return CurrentValue <= Threshold;
    }
};

/**
 * @class NeedManager
 * @brief Manages a collection of needs for an NPC instance.
 *
 * The NeedManager maintains the lifecycle of an NPC's needs:
 * - Initialization with default or custom need values
 * - Time-based decay updates (subtract decay * deltaTime each frame)
 * - Threshold checking (identify which needs are urgent)
 * - Array mutation and persistence
 *
 * This is the core engine of the NeedSystem. Each NPC character should
 * have one NeedManager instance that persists for the character's lifetime.
 *
 * Blueprint analog: Instance variable "Needs" array on BP_NPC_Parent
 */
class NeedManager {
public:
    /**
     * @brief Default constructor. Creates an empty manager.
     */
    NeedManager();

    /**
     * @brief Initialize needs with default values for all need types.
     *
     * Creates a need for each ENeedType with sensible defaults:
     * - CurrentValue: 1.0 (fully satisfied)
     * - Threshold: 0.3 (30% urgency threshold)
     * - DecayRatePerSecond: 0.1 (loses 10% per 10 seconds)
     *
     * Matches Unreal Blueprint's InitializeNeeds function behavior.
     */
    void Initialize();

    /**
     * @brief Initialize needs with custom values.
     *
     * @param needs Vector of NPCNeed structs to populate the manager with.
     * @throws std::invalid_argument if needs vector is empty
     */
    void Initialize(const std::vector<NPCNeed>& needs);

    /**
     * @brief Update all needs based on elapsed time.
     *
     * Applies time-based decay to each need using the formula:
     *   CurrentValue = max(0.0, CurrentValue - (DecayRatePerSecond * deltaSeconds))
     *
     * This is the core update loop. Matches Unreal's UpdateNeeds function.
     *
     * @param deltaSeconds Time elapsed since last update, in seconds
     * @throws std::invalid_argument if deltaSeconds is negative
     * @throws std::runtime_error if manager not initialized
     */
    void Update(double deltaSeconds);

    /**
     * @brief Get all needs that exceed their urgency threshold.
     *
     * Identifies which needs require immediate attention by checking
     * if CurrentValue <= Threshold for each need.
     *
     * Matches Unreal's ProcessNeedsLoop function logic.
     *
     * @return Vector of indices of urgent needs (empty if none)
     * @throws std::runtime_error if manager not initialized
     */
    std::vector<size_t> GetUrgentNeeds() const;

    /**
     * @brief Get the most urgent need (lowest CurrentValue).
     *
     * Useful for prioritizing which need to satisfy first.
     *
     * @return Index of the most urgent need
     * @throws std::runtime_error if manager not initialized or has no needs
     */
    size_t GetMostUrgentNeed() const;

    /**
     * @brief Get a specific need by index.
     *
     * @param index The index of the need to retrieve
     * @return Const reference to the NPCNeed
     * @throws std::out_of_range if index is invalid
     */
    const NPCNeed& GetNeed(size_t index) const;

    /**
     * @brief Get a specific need by type.
     *
     * @param type The type of need to retrieve
     * @return Const reference to the NPCNeed
     * @throws std::runtime_error if need type not found
     */
    const NPCNeed& GetNeedByType(ENeedType type) const;

    /**
     * @brief Get mutable access to a specific need by index.
     *
     * Allows direct modification of need values (e.g., satisfaction).
     *
     * @param index The index of the need to modify
     * @return Reference to the NPCNeed
     * @throws std::out_of_range if index is invalid
     */
    NPCNeed& MutableNeed(size_t index);

    /**
     * @brief Get mutable access to a specific need by type.
     *
     * @param type The type of need to modify
     * @return Reference to the NPCNeed
     * @throws std::runtime_error if need type not found
     */
    NPCNeed& MutableNeedByType(ENeedType type);

    /**
     * @brief Satisfy a need (set CurrentValue to 1.0).
     *
     * Typically called when the NPC completes an action to satisfy the need.
     *
     * @param index The index of the need to satisfy
     * @throws std::out_of_range if index is invalid
     */
    void SatisfyNeed(size_t index);

    /**
     * @brief Satisfy a need by type.
     *
     * @param type The type of need to satisfy
     * @throws std::runtime_error if need type not found
     */
    void SatisfyNeedByType(ENeedType type);

    /**
     * @brief Get the total number of needs.
     *
     * @return Number of needs in this manager
     */
    size_t GetNeedCount() const;

    /**
     * @brief Check if the manager has been initialized.
     *
     * @return true if Initialize() has been called, false otherwise
     */
    bool IsInitialized() const;

    /**
     * @brief Get all needs.
     *
     * @return Const reference to the internal needs array
     */
    const std::vector<NPCNeed>& GetAllNeeds() const;

private:
    std::vector<NPCNeed> needs_;
    bool initialized_;

    /**
     * @brief Helper to find a need by type.
     *
     * @param type The need type to search for
     * @return Index of the need, or -1 if not found
     */
    int32_t FindNeedIndexByType(ENeedType type) const;

    /**
     * @brief Clamp a value to [0.0, 1.0] range.
     *
     * @param value The value to clamp
     * @return Clamped value
     */
    static double Clamp(double value);
};

}  // namespace creatureRepo::need

