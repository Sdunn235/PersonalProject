/**
 * simcore.h — Convenience umbrella header.
 * Include this to pull in the full SimCore public API.
 *
 * The Adapter Layer in Unreal should include only this header
 * (plus simcore/adapter/IWorldQuery.h).
 */
#pragma once

// Simulation clock & utilities
#include "simcore/sim/SimRNG.h"
#include "simcore/sim/TimeManager.h"
#include "simcore/sim/EventLog.h"

// Agent systems
#include "simcore/agent/NeedSystem.h"
#include "simcore/agent/TraitSystem.h"
#include "simcore/agent/DriveEngine.h"
#include "simcore/agent/DecisionEngine.h"
#include "simcore/agent/AgentRegistry.h"

// World systems
#include "simcore/world/ResourceNode.h"
#include "simcore/world/WorldState.h"

// Adapter interfaces (pure virtual — implemented by engine layer)
#include "simcore/adapter/IWorldQuery.h"

