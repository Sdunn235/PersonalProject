#include "simcore/world/ResourceNode.h"
#include <algorithm>

namespace simcore {

float ResourceNode::consume(float amount, uint64_t step, EventLog& log,
                             AgentID consumer) {
    float actual = std::min(amount, quantity);
    quantity -= actual;

    if (actual > 0.0f) {
        log.record(step, EventType::ResourceConsumed,
                   consumer, id, actual, name);
    }

    if (is_depleted()) {
        log.record(step, EventType::ResourceDepleted,
                   INVALID_AGENT_ID, id, 0.0f, name + " depleted");
    }

    return actual;
}

void ResourceNode::regen_tick(uint64_t step, EventLog& log) {
    if (regen_rate <= 0.0f) return;
    if (is_full()) return;

    float before = quantity;
    quantity = std::min(quantity + regen_rate, max_capacity);

    float gained = quantity - before;
    if (gained > 0.0f) {
        log.record(step, EventType::ResourceRegened,
                   INVALID_AGENT_ID, id, gained, name);
    }
}

} // namespace simcore

