#include "simcore/adapter/IWorldQuery.h"
#include "simcore/world/WorldState.h"
#include <cmath>

namespace simcore {

WorldSnapshot WorldStateWorldQuery::query_snapshot(AgentID agent_id,
                                                    float origin_x,
                                                    float origin_y,
                                                    float origin_z) const {
    WorldSnapshot snap;
    snap.is_safe = true;
    snap.threat_distance = 999.0f;

    // For each need type, find the nearest valid resource node
    for (int i = 1; i < NEED_COUNT; ++i) {
        NeedType nt = static_cast<NeedType>(i);
        auto opt = m_world.find_nearest_for_need(nt, origin_x, origin_y);

        if (opt.has_value()) {
            const ResourceNode* node = m_world.find_resource(opt.value());
            if (node) {
                float dx = origin_x - node->pos_x;
                float dy = origin_y - node->pos_y;
                float dz = origin_z - node->pos_z;
                float dist = std::sqrt(dx*dx + dy*dy + dz*dz);

                snap.nearest[i].resource_id = node->id;
                snap.nearest[i].need_type   = nt;
                snap.nearest[i].distance    = dist;
                snap.nearest[i].is_valid    = true;
            }
        }
    }

    return snap;
}

} // namespace simcore

