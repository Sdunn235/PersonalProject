# World Resource & Environmental Model
Lucent Forge

---

## 1. Principle

The world is materially persistent.

Resources are not decoration.
They are economic drivers.

---

## 2. Resource Node Types

### Renewable
- Forest clusters
- Wildlife populations
- Soil fertility
- Fish stocks

### Semi-Renewable
- Rare herbs
- Magical energy nodes

### Finite
- Ore veins
- Stone deposits
- Unique artifacts

---

## 3. Resource Structure

Each ResourceNode contains:

- ResourceID
- Type
- Quantity
- MaxCapacity
- RegenerationRate
- Location
- OwnershipStatus

---

## 4. Terrain Mutation

Actions may:

- Reduce quantity
- Change terrain type
- Modify fertility
- Modify biome
- Increase erosion risk

World mutation must be persistent.

---

## 5. Settlement Interaction

Settlements:

- Consume resources
- Increase demand
- Increase deforestation
- Increase mining
- Increase wildlife displacement

Abandoned settlements:

- Trigger regrowth
- Reduce demand
- Shift wildlife patterns

---

## 6. Economic Impact

Resource scarcity drives:

- Trade routes
- Conflict
- Migration
- Political instability

Resource abundance drives:

- Wealth concentration
- Military power
- Expansion

---

## 7. Regional Simulation LOD

Distant regions:

- Simulate aggregated consumption
- Regenerate using statistical models

Active regions:

- Simulate per-node detail

---

## 8. Long-Term Change

Mountains:
- Finite ore layers
- Mining depth tracked
- Multi-lifetime depletion

Forests:
- Age cycles
- Density models
- Regrowth probability

World evolves even without player presence.

---

## 9. Persistence

WorldState must:

- Store resource changes
- Allow rollback/debug replay
- Support large-scale world maps

---

## 10. Guiding Rule

If a forest is cut,
it must matter.

If a mountain is mined,
it must leave a scar.