cmake_minimum_required(VERSION 3.16)
project(SimCore VERSION 0.1.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# ── SimCore static library ────────────────────────────────────────────────────
add_library(simcore STATIC
    src/sim/SimRNG.cpp
    src/sim/TimeManager.cpp
    src/sim/EventLog.cpp
    src/agent/NeedSystem.cpp
    src/agent/TraitSystem.cpp
    src/agent/DriveEngine.cpp
    src/agent/DecisionEngine.cpp
    src/agent/AgentRegistry.cpp
    src/world/ResourceNode.cpp
    src/world/WorldState.cpp
    src/adapter/IWorldQuery.cpp
)

target_include_directories(simcore PUBLIC
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
    $<INSTALL_INTERFACE:include>
)

# ── Tests ─────────────────────────────────────────────────────────────────────
enable_testing()

# Fetch GoogleTest if not present
include(FetchContent)
FetchContent_Declare(
    googletest
    GIT_REPOSITORY https://github.com/google/googletest.git
    GIT_TAG        v1.14.0
)
set(gtest_force_shared_crt ON CACHE BOOL "" FORCE)
FetchContent_MakeAvailable(googletest)

add_executable(simcore_tests
    tests/test_rng.cpp
    tests/test_needs.cpp
    tests/test_traits.cpp
    tests/test_drive.cpp
    tests/test_decision.cpp
    tests/test_resources.cpp
    tests/test_time.cpp
    tests/test_eventlog.cpp
    tests/test_integration.cpp
)

target_link_libraries(simcore_tests
    simcore
    GTest::gtest_main
)

include(GoogleTest)
gtest_discover_tests(simcore_tests)


