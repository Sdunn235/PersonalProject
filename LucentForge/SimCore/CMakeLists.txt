cmake_minimum_required(VERSION 3.15)
project(LucentForge_SimCore
        VERSION 0.1.0
        DESCRIPTION "Engine-agnostic simulation core for Lucent Forge"
        LANGUAGES CXX)

# Project philosophy: portable, testable, deterministic
# No Unreal headers, no rendering, no physics
# Pure simulation logic that can run headless

# ============================================================================
# CONFIGURATION
# ============================================================================

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Output directories
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/bin")
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/lib")
set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/lib")

# ============================================================================
# CORE LIBRARY: SimCore
# ============================================================================

add_library(SimCore STATIC)

target_include_directories(SimCore
    PUBLIC
        ${CMAKE_CURRENT_SOURCE_DIR}/include
    PRIVATE
        ${CMAKE_CURRENT_SOURCE_DIR}/src
)

# Source files organized by module
target_sources(SimCore
    PRIVATE
        # Agent module
        src/modules/agent/Agent.cpp

        # World state module
        src/modules/world/WorldState.cpp

        # Needs system module
        src/modules/needs/NeedSystem.cpp

        # Traits module
        src/modules/traits/TraitSystem.cpp

        # Decision engine module
        src/modules/decision/DecisionEngine.cpp

        # Combat module (wraps iso_rpg_lab logic)
        src/modules/combat/CombatEngine.cpp

        # Dialogue module
        src/modules/dialogue/DialogueSystem.cpp

        # Memory system module
        src/modules/memory/MemorySystem.cpp
)

# Compiler flags for quality and warnings
if(MSVC)
    target_compile_options(SimCore PRIVATE /W4 /WX)
else()
    target_compile_options(SimCore PRIVATE -Wall -Wextra -Wpedantic -Werror)
endif()

# ============================================================================
# PYTHON BINDINGS (pybind11)
# ============================================================================

# Uncomment when pybind11 is added to externals/
# find_package(pybind11 CONFIG REQUIRED)
#
# pybind11_add_module(SimCore_py
#     src/python_bindings.cpp
# )
# target_link_libraries(SimCore_py PRIVATE SimCore)

# ============================================================================
# TESTS (GoogleTest)
# ============================================================================

enable_testing()

# For now, tests will be Python-based (pytest) calling wrapped SimCore
# C++ unit tests can be added via GoogleTest if needed

# ============================================================================
# INSTALLATION (Optional)
# ============================================================================

install(TARGETS SimCore
        LIBRARY DESTINATION lib
        ARCHIVE DESTINATION lib)

install(DIRECTORY include/
        DESTINATION include)

# ============================================================================
# SUMMARY
# ============================================================================

message(STATUS "LucentForge SimCore Configuration")
message(STATUS "  Build Type: ${CMAKE_BUILD_TYPE}")
message(STATUS "  C++ Standard: ${CMAKE_CXX_STANDARD}")
message(STATUS "  Modules: Agent | World | Needs | Traits | Decision | Combat | Dialogue | Memory")
message(STATUS "  Output: ${CMAKE_RUNTIME_OUTPUT_DIRECTORY}")

