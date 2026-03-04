#include "simcore/sim/EventLog.h"
#include <algorithm>

namespace simcore {

void EventLog::record(uint64_t step, EventType type,
                      AgentID agent_id, ResourceID res_id,
                      float value, const std::string& note) {
    m_entries.push_back({ step, type, agent_id, res_id, value, note });
}

std::vector<EventRecord> EventLog::events_for_agent(AgentID id) const {
    std::vector<EventRecord> result;
    for (const auto& e : m_entries)
        if (e.agent_id == id) result.push_back(e);
    return result;
}

std::vector<EventRecord> EventLog::events_of_type(EventType t) const {
    std::vector<EventRecord> result;
    for (const auto& e : m_entries)
        if (e.type == t) result.push_back(e);
    return result;
}

std::vector<EventRecord> EventLog::events_in_range(uint64_t from, uint64_t to) const {
    std::vector<EventRecord> result;
    for (const auto& e : m_entries)
        if (e.step >= from && e.step <= to) result.push_back(e);
    return result;
}

} // namespace simcore

