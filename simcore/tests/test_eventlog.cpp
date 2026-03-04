#include <gtest/gtest.h>
#include "simcore/sim/EventLog.h"

using namespace simcore;

TEST(EventLog, Record_AppendsEntry) {
    EventLog log;
    log.record(1, EventType::NeedSatisfied, 10u, INVALID_RESOURCE_ID, 50.0f, "hunger");
    EXPECT_EQ(log.size(), 1u);
}

TEST(EventLog, EventsForAgent_Filters) {
    EventLog log;
    log.record(1, EventType::NeedSatisfied, 1u);
    log.record(2, EventType::NeedCritical,  2u);
    log.record(3, EventType::NeedSatisfied, 1u);

    auto agent1 = log.events_for_agent(1u);
    EXPECT_EQ(agent1.size(), 2u);
    for (const auto& e : agent1)
        EXPECT_EQ(e.agent_id, 1u);
}

TEST(EventLog, EventsOfType_Filters) {
    EventLog log;
    log.record(1, EventType::ResourceConsumed, INVALID_AGENT_ID, 5u, 10.0f);
    log.record(2, EventType::ResourceDepleted, INVALID_AGENT_ID, 5u, 0.0f);
    log.record(3, EventType::ResourceConsumed, INVALID_AGENT_ID, 6u, 5.0f);

    auto consumed = log.events_of_type(EventType::ResourceConsumed);
    EXPECT_EQ(consumed.size(), 2u);
}

TEST(EventLog, EventsInRange_Filters) {
    EventLog log;
    log.record(1,  EventType::AgentSpawned);
    log.record(5,  EventType::NeedCritical, 1u);
    log.record(10, EventType::AgentDied,    1u);
    log.record(15, EventType::TradeOccurred);

    auto range = log.events_in_range(4, 11);
    EXPECT_EQ(range.size(), 2u);
    EXPECT_EQ(range[0].step, 5u);
    EXPECT_EQ(range[1].step, 10u);
}

TEST(EventLog, Clear_EmptiesLog) {
    EventLog log;
    log.record(1, EventType::AgentSpawned);
    log.record(2, EventType::AgentSpawned);
    log.clear();
    EXPECT_EQ(log.size(), 0u);
}

TEST(EventLog, EntryFields_CorrectlyStored) {
    EventLog log;
    log.record(42, EventType::ResourceConsumed, 7u, 3u, 25.5f, "wheat");
    const EventRecord& e = log.entries()[0];
    EXPECT_EQ(e.step,        42u);
    EXPECT_EQ(e.type,        EventType::ResourceConsumed);
    EXPECT_EQ(e.agent_id,    7u);
    EXPECT_EQ(e.resource_id, 3u);
    EXPECT_FLOAT_EQ(e.value, 25.5f);
    EXPECT_EQ(e.note,        "wheat");
}

