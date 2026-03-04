#include <gtest/gtest.h>
#include "simcore/world/ResourceNode.h"
#include "simcore/world/WorldState.h"
#include "simcore/sim/EventLog.h"

using namespace simcore;

// ── ResourceNode tests ───────────────────────────────────────────────────────

TEST(ResourceNode, Consume_ReducesQuantity) {
    ResourceNode node;
    node.id       = 1u;
    node.quantity = 100.0f;
    node.name     = "TestFood";

    EventLog log;
    float consumed = node.consume(30.0f, 1, log, 99u);
    EXPECT_FLOAT_EQ(consumed,      30.0f);
    EXPECT_FLOAT_EQ(node.quantity, 70.0f);
}

TEST(ResourceNode, Consume_CapsAtAvailable) {
    ResourceNode node;
    node.id       = 1u;
    node.quantity = 10.0f;
    node.name     = "SmallFood";

    EventLog log;
    float consumed = node.consume(50.0f, 1, log);
    EXPECT_FLOAT_EQ(consumed,      10.0f); // can't consume more than available
    EXPECT_FLOAT_EQ(node.quantity, 0.0f);
}

TEST(ResourceNode, Consume_LogsEvent) {
    ResourceNode node;
    node.id       = 1u;
    node.quantity = 80.0f;
    node.name     = "Food";

    EventLog log;
    node.consume(20.0f, 5, log, 42u);

    EXPECT_EQ(log.size(), 1u);
    EXPECT_EQ(log.entries()[0].type,       EventType::ResourceConsumed);
    EXPECT_EQ(log.entries()[0].agent_id,   42u);
    EXPECT_EQ(log.entries()[0].resource_id, 1u);
    EXPECT_FLOAT_EQ(log.entries()[0].value, 20.0f);
}

TEST(ResourceNode, Consume_LogsDepletedEvent) {
    ResourceNode node;
    node.id       = 1u;
    node.quantity = 5.0f;
    node.name     = "TinyFood";

    EventLog log;
    node.consume(5.0f, 2, log);

    // Should have Consumed + Depleted
    EXPECT_EQ(log.size(), 2u);
    bool has_depleted = false;
    for (const auto& e : log.entries())
        if (e.type == EventType::ResourceDepleted) has_depleted = true;
    EXPECT_TRUE(has_depleted);
}

TEST(ResourceNode, IsDepleted_WhenZero) {
    ResourceNode node;
    node.quantity = 0.0f;
    EXPECT_TRUE(node.is_depleted());
}

TEST(ResourceNode, RegenTick_IncreasesQuantity) {
    ResourceNode node;
    node.id           = 1u;
    node.quantity     = 40.0f;
    node.max_capacity = 100.0f;
    node.regen_rate   = 5.0f;
    node.name         = "Forest";

    EventLog log;
    node.regen_tick(10, log);
    EXPECT_FLOAT_EQ(node.quantity, 45.0f);
}

TEST(ResourceNode, RegenTick_CapsAtMaxCapacity) {
    ResourceNode node;
    node.id           = 1u;
    node.quantity     = 98.0f;
    node.max_capacity = 100.0f;
    node.regen_rate   = 5.0f;
    node.name         = "Forest";

    EventLog log;
    node.regen_tick(1, log);
    EXPECT_FLOAT_EQ(node.quantity, 100.0f);
}

TEST(ResourceNode, RegenTick_ZeroRate_NoChange) {
    ResourceNode node;
    node.quantity   = 50.0f;
    node.regen_rate = 0.0f;
    node.name       = "OreVein";

    EventLog log;
    node.regen_tick(1, log);
    EXPECT_FLOAT_EQ(node.quantity, 50.0f);
    EXPECT_EQ(log.size(), 0u);
}

// ── WorldState tests ─────────────────────────────────────────────────────────

TEST(WorldState, AddResource_AssignsID) {
    WorldState ws;
    ResourceNode node;
    node.tag      = ResourceTag::FoodSource;
    node.quantity = 100.0f;
    node.name     = "Apple Tree";

    ResourceID id = ws.add_resource(node);
    EXPECT_NE(id, INVALID_RESOURCE_ID);
    EXPECT_NE(ws.find_resource(id), nullptr);
}

TEST(WorldState, FindNearest_ReturnsClosest) {
    WorldState ws;

    ResourceNode far_food;
    far_food.tag      = ResourceTag::FoodSource;
    far_food.quantity = 50.0f;
    far_food.pos_x    = 1000.0f;
    far_food.name     = "FarFood";
    ws.add_resource(far_food);

    ResourceNode near_food;
    near_food.tag      = ResourceTag::FoodSource;
    near_food.quantity = 50.0f;
    near_food.pos_x    = 10.0f;
    near_food.name     = "NearFood";
    ResourceID near_id = ws.add_resource(near_food);

    auto result = ws.find_nearest_for_need(NeedType::Hunger, 0.0f, 0.0f);
    ASSERT_TRUE(result.has_value());
    EXPECT_EQ(result.value(), near_id);
}

TEST(WorldState, FindNearest_SkipsDepleted) {
    WorldState ws;

    ResourceNode depleted;
    depleted.tag      = ResourceTag::FoodSource;
    depleted.quantity = 0.0f; // depleted
    depleted.pos_x    = 5.0f;
    depleted.name     = "DepletedFood";
    ws.add_resource(depleted);

    auto result = ws.find_nearest_for_need(NeedType::Hunger, 0.0f, 0.0f);
    EXPECT_FALSE(result.has_value());
}

TEST(WorldState, FindNearest_WrongTag_ReturnsNull) {
    WorldState ws;

    ResourceNode water;
    water.tag      = ResourceTag::WaterSource;
    water.quantity = 100.0f;
    water.name     = "River";
    ws.add_resource(water);

    // Looking for food — water won't match
    auto result = ws.find_nearest_for_need(NeedType::Hunger, 0.0f, 0.0f);
    EXPECT_FALSE(result.has_value());
}

TEST(WorldState, Tick_RegensAllNodes) {
    WorldState ws;
    EventLog log;

    ResourceNode node;
    node.tag          = ResourceTag::Forest;
    node.quantity     = 50.0f;
    node.max_capacity = 100.0f;
    node.regen_rate   = 2.0f;
    node.name         = "TreeCluster";
    ResourceID id = ws.add_resource(node);

    ws.tick(1, log);
    EXPECT_FLOAT_EQ(ws.find_resource(id)->quantity, 52.0f);
}

TEST(WorldState, RemoveResource) {
    WorldState ws;
    ResourceNode node;
    node.name = "Temp";
    ResourceID id = ws.add_resource(node);

    ws.remove_resource(id);
    EXPECT_EQ(ws.find_resource(id), nullptr);
}

