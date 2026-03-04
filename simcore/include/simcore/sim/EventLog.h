#pragma once
#include <cstdint>
#include <string>
#include <vector>

namespace simcore {

using AgentID    = uint32_t;
using ResourceID = uint32_t;

static constexpr AgentID    INVALID_AGENT_ID    = 0u;
static constexpr ResourceID INVALID_RESOURCE_ID = 0u;

// ── Event types ───────────────────────────────────────────────────────────────
enum class EventType : uint8_t {
    NeedSatisfied = 0,
    NeedCritical,
    AgentSpawned,
    AgentDied,
    ResourceDepleted,
    ResourceConsumed,
    ResourceRegened,
    OwnershipChanged,
    TradeOccurred,
    CustomMilestone,
};

// ── Single event record ───────────────────────────────────────────────────────
struct EventRecord {
    uint64_t   step;          // SimStep this occurred
    EventType  type;
    AgentID    agent_id;      // 0 if world-level event
    ResourceID resource_id;   // 0 if not resource-related
    float      value;         // context-dependent magnitude
    std::string note;         // optional human-readable detail
};

/**
 * EventLog — Append-only simulation event journal.
 *
 * Enables history, memory systems, debug replay, and audit.
 * Lives in SimCore — no engine dependencies.
 */
class EventLog {
public:
    EventLog() = default;

    void record(uint64_t step, EventType type,
                AgentID agent_id    = INVALID_AGENT_ID,
                ResourceID res_id   = INVALID_RESOURCE_ID,
                float value         = 0.0f,
                const std::string& note = {});

    const std::vector<EventRecord>& entries() const { return m_entries; }

    /// Return all events for a specific agent (linear scan — for debug use).
    std::vector<EventRecord> events_for_agent(AgentID id) const;

    /// Return all events of a given type.
    std::vector<EventRecord> events_of_type(EventType t) const;

    /// Return events in step range [from, to] inclusive.
    std::vector<EventRecord> events_in_range(uint64_t from, uint64_t to) const;

    void clear() { m_entries.clear(); }
    size_t size() const { return m_entries.size(); }

private:
    std::vector<EventRecord> m_entries;
};

} // namespace simcore

