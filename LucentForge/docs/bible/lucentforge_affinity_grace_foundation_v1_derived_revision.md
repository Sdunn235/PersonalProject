# Lucent Forge Affinity and Grace Foundation v1

**Status:** Canon-ready expansion draft  
**Authority target:** Lucent Forge Bible  
**Primary concern:** Affinity physics, combinations, resonance, environments, beings, materials, culture, and implementation boundaries  
**Companion document:** `lucentforge_cosmology_foundation_v1_expanded.md`

> Affinities describe how created reality behaves. They are not merely spell schools, damage colors, or personality labels.

---

## 0. Canon Integration Notice

The current Stage 4 implementation uses six enum values:

`EARTH, FIRE, AIR, WATER, VOID, LIGHT`

The Grace supersedes that final model.

The canonical affinity structure is:

### Four Primal Affinities
- Fire
- Air
- Water
- Earth

### Four Derived Affinities
- Plasma — Fire + Air
- Colloidal Dispersion — Air + Water
- Non-Newtonian — Water + Earth
- Bingham Placidity — Earth + Fire

### Ontological States, Not Affinities
- Light / White / Creation
- Dark / Black / absence

“Derived” means a state produced between two adjacent primal affinities. It does **not** mean morally, spiritually, or mechanically superior.

The current code’s Light and Void values are legacy scaffolding and require a later migration.

---

# 1. Purpose

This document defines the affinity grammar that should eventually govern:

- creatures;
- materials;
- magic;
- environments;
- weather;
- alchemy;
- biology;
- equipment;
- architecture;
- culture;
- religion;
- perception;
- AI preferences;
- combat;
- transformation;
- resonance;
- world simulation.

It protects the affinity system from collapsing into an ordinary elemental weakness chart.

---

# 2. The Affinity Lattice

## 2.1 Standard Orientation

The standard Grace orientation proceeds clockwise:

1. Fire — red
2. Plasma — magenta
3. Air — yellow
4. Colloidal Dispersion — violet
5. Water — blue
6. Non-Newtonian — capri
7. Earth — green
8. Bingham Placidity — amber
9. Return to Fire

This ordering makes each Derived Affinity the bridge between two adjacent primals.

## 2.2 Canonical Pair Map

| Primal A | Primal B | Derived Affinity |
|---|---|---|
| Fire | Air | Plasma |
| Air | Water | Colloidal Dispersion |
| Water | Earth | Non-Newtonian |
| Earth | Fire | Bingham Placidity |

Order does not change the resulting affinity, though direction may matter in processes, rituals, or transformations.

## 2.3 Derived Does Not Mean Stronger

Derived Affinities are not upgrades unlocked after mastering primal affinities.

They are emergent conditions produced when two primal behaviors coexist in a stable or meaningful relationship.

A being may be born with a Derived Affinity. A region may naturally express one. A material may embody one without ever passing through a visible “combination spell.”

## 2.4 Adjacent and Nonadjacent Relationships

The Grace directly defines adjacent combinations. Nonadjacent primal pairs require separate doctrine.

Do not invent additional affinity enum values for every mixture.

A nonadjacent interaction may produce:

- conflict;
- cancellation;
- layered coexistence;
- unstable alternation;
- a temporary phenomenon;
- a compound carrying multiple affinities;
- a cultural name rather than a new fundamental affinity.

The eight affinities remain the canonical lattice unless a future Bible revision proves another stable state necessary.

---

# 3. Canonical Colors

| Category | Affinity | Color Name | Hex |
|---|---|---|---|
| Primal | Fire | Red | `#FE0000` |
| Derived | Plasma | Magenta | `#FF0090` |
| Primal | Air | Yellow | `#F7FF00` |
| Derived | Colloidal Dispersion | Violet | `#AD008D` |
| Primal | Water | Blue | `#0B00FF` |
| Derived | Non-Newtonian | Capri | `#00BEFF` |
| Primal | Earth | Green | `#2A9D20` |
| Derived | Bingham Placidity | Amber | `#FFBB00` |

Related cosmological colors:

| Concept | Color | Hex |
|---|---|---|
| Veil | Iridescent Green | `#01FE47` |
| Light / Creation | White | `#FFFFFF` |
| Dark / absence | Black | `#000000` |

Color is an authoritative visual identifier, but affinity is not literally pigment. Color may be invisible, culturally represented differently, or perceived only through the Gift.

---

# 4. Primal Affinities

## 4.1 Fire

**Color:** Red — `#FE0000`

Fire expresses energetic release, transformation, acceleration, consumption, excitation, and irreversible change.

Fire is not limited to flame.

Potential expressions include:

- heat;
- combustion;
- rapid metabolism;
- aggression of reaction;
- forging;
- purification through transformation;
- explosive growth;
- decomposition through energy;
- momentum toward change.

Fire is not inherently destructive. Cooking, warmth, industry, digestion, passion, and renewal may all carry Fire behavior.

### Fire Design Verbs
- ignite;
- accelerate;
- transform;
- consume;
- radiate;
- catalyze;
- release.

## 4.2 Air

**Color:** Yellow — `#F7FF00`

Air expresses motion, propagation, distribution, exchange, pressure difference, distance, and transmission.

Air is not limited to wind.

Potential expressions include:

- sound;
- breath;
- communication;
- diffusion;
- speed;
- lift;
- dispersal;
- circulation;
- transmission of scent, spores, heat, or ideas.

### Air Design Verbs
- move;
- carry;
- spread;
- separate;
- connect across distance;
- redirect;
- circulate.

## 4.3 Water

**Color:** Blue — `#0B00FF`

Water expresses continuity, flow, adaptation, cohesion, dissolution, memory of path, and transfer through contact.

Water is not limited to liquid water.

Potential expressions include:

- blood;
- sap;
- solvents;
- healing circulation;
- erosion;
- emotional continuity;
- storage through volume;
- cooling;
- gradual reshaping.

### Water Design Verbs
- flow;
- join;
- dissolve;
- carry within;
- equalize;
- cool;
- reshape gradually.

## 4.4 Earth

**Color:** Green — `#2A9D20`

Earth expresses stability, mass, boundary, support, persistence, density, structure, and resistance to change.

Earth is not limited to soil or stone.

Potential expressions include:

- bone;
- architecture;
- armor;
- crystal;
- roots;
- stored pressure;
- territory;
- physical memory;
- load-bearing form.

### Earth Design Verbs
- anchor;
- support;
- contain;
- endure;
- harden;
- preserve shape;
- resist.

---

# 5. Derived Affinities

## 5.1 Plasma — Fire + Air

**Color:** Magenta — `#FF0090`

Plasma arises where Fire’s excitation and transformation meet Air’s motion, propagation, and separation.

It represents matter or magical pattern driven into an energized, mobile, highly responsive state.

Potential expressions:

- lightning-like discharge;
- aurora;
- stellar or solar phenomena;
- charged wind;
- radiant arcs;
- living electrical conduction;
- high-energy spell channels;
- rapid communication through energized fields.

### Plasma Design Verbs
- ionize;
- arc;
- charge;
- flash;
- conduct;
- leap;
- radiate through motion.

### Plasma Is Not
- simply “stronger fire”;
- a universal lightning damage school;
- automatically technological;
- necessarily hot in every magical expression.

## 5.2 Colloidal Dispersion — Air + Water

**Color:** Violet — `#AD008D`

Colloidal Dispersion arises where Air’s distribution and suspended separation meet Water’s continuity and carrying medium.

It represents one substance distributed through another without fully dissolving or settling.

Potential expressions:

- mist;
- fog;
- smoke suspended in moisture;
- emulsions;
- aerosols;
- clouds;
- medicinal suspensions;
- spores;
- pigments;
- living fluids carrying particles;
- distributed magical fields.

### Colloidal Design Verbs
- suspend;
- disperse;
- veil;
- carry particles;
- diffuse without dissolving;
- stabilize mixture;
- obscure while remaining present.

### Colloidal Dispersion Is Not
- merely poison;
- “purple magic”;
- identical to ordinary Air or Water mixing;
- always visible.

## 5.3 Non-Newtonian — Water + Earth

**Color:** Capri — `#00BEFF`

Non-Newtonian affinity arises where Water’s flow and adaptation meet Earth’s resistance, structure, and load response.

It represents matter whose behavior changes according to applied force, time, rate, or pressure.

Potential expressions:

- shear-thickening armor;
- shear-thinning fluids;
- impact-reactive tissues;
- quicksand-like traps;
- adaptive biological gels;
- protective coatings;
- movement-dependent terrain;
- magic that becomes rigid when struck and fluid when handled gently.

### Non-Newtonian Design Verbs
- adapt to force;
- thicken;
- thin;
- absorb impact;
- yield selectively;
- remember stress rate;
- change behavior under motion.

### Non-Newtonian Is Not
- generic shapeshifting;
- simply mud;
- automatically defensive;
- an excuse for effects without consistent force rules.

## 5.4 Bingham Placidity — Earth + Fire

**Color:** Amber — `#FFBB00`

**Canonical world term:** Bingham Placidity  
**Scientific inspiration:** Bingham plastic behavior

Bingham Placidity arises where Earth’s structure and resistance meet Fire’s transformation and release.

It represents a material or pattern that behaves as a stable solid until sufficient stress crosses a yield threshold, after which it flows or transforms.

Potential expressions:

- lava;
- clay;
- paste;
- molten metal;
- magical seals that hold until overwhelmed;
- emotional or biochemical states with threshold release;
- fortress wards;
- pressure-triggered transformation;
- controlled forging.

### Bingham Design Verbs
- hold;
- accumulate stress;
- yield at threshold;
- flow after release;
- reset or harden;
- preserve stillness until forced.

### Bingham Placidity Is Not
- ordinary Earth resistance;
- generic molten Fire;
- passive calmness without a threshold model;
- automatically stronger than either primal.

---

# 6. The Meaning of Combination

## 6.1 Combination Is Relationship

A Derived Affinity is not created by adding two color values or casting two spells simultaneously.

Combination means the behaviors of two primal affinities coexist in a way that produces a stable third behavior.

## 6.2 Multiple Paths to the Same State

Plasma may emerge through:

- natural weather;
- a creature’s body;
- ritual;
- engineered magical equipment;
- a Fire-aligned caster using an Air-saturated environment;
- birth conditions;
- a persistent regional field.

The origin may affect intensity, stability, control, and side effects without changing the affinity’s identity.

## 6.3 Transformation vs Coexistence

An entity can carry Fire and Air as separate effective affinities without automatically becoming Plasma.

The system must distinguish:

- **plural affinity state:** Fire + Air both present;
- **Derived expression:** Plasma behavior emerges;
- **temporary interaction:** one Plasma-like event occurs;
- **innate Derived Affinity:** Plasma is the being’s baseline nature.

This distinction prevents every multi-affinity creature from collapsing into a derived type.

## 6.4 Emergence Conditions

Future mechanics may require:

- sufficient intensity;
- compatible pattern;
- environmental support;
- skill;
- resonance;
- duration;
- pressure;
- catalyst;
- biological capacity.

The exact formula is deferred, but the conceptual distinction is canon.

---

# 7. Affinity in Beings

## 7.1 Innate Affinity

Every living or created being may possess an innate affinity representing its baseline relationship to created behavior.

An innate affinity may be Primal or Derived.

## 7.2 Mutable Affinity State

The existing set-based structure remains useful:

- innate;
- granted;
- suppressed;
- effective.

However, it should eventually support:

- intensity;
- stability;
- source;
- duration;
- confidence of identification;
- expressed state vs latent state;
- conditions for Derived emergence.

## 7.3 Affinity Is Not Personality

A Fire-affinity person is not automatically angry. An Earth-affinity person is not automatically stubborn.

Affinity may influence:

- bodily regulation;
- magical comfort;
- sensory bias;
- environmental response;
- likely cultural metaphor;
- stress expression;
- recovery;
- resonance.

Personality still emerges from traits, memory, needs, social position, and lived outcomes.

## 7.4 Racial Tendency Is Not Racial Determinism

Races or species may have affinity distributions shaped by evolution, creation, homeland, or culture.

Do not make every member of a race share one affinity.

Variation supports individuality and prevents affinity from becoming fantasy biological essentialism.

## 7.5 Birth and Creation Conditions

Future affinity generation may consider:

- parent affinities;
- region;
- season;
- Veil conditions;
- ambient Bits;
- ritual;
- constructed purpose;
- chance;
- rare anomalies.

Authored values remain acceptable during the prototype.

---

# 8. Affinity in Environments

## 8.1 Regional Fields

Rooms, regions, panels, weather systems, structures, and resources may carry affinity and intensity.

A region’s field should influence more than damage:

- recovery;
- Bit regeneration;
- Byte conversion;
- perception;
- creature comfort;
- plant growth;
- material behavior;
- memory interpretation;
- emotional chemistry;
- spell stability;
- AI destination choice.

## 8.2 Neutrality

`None` should mean no dominant affinity, not absence of affinity in the Dark sense.

A neutral town still exists inside Creation and contains all normal created processes. It simply lacks a strong local bias.

## 8.3 Saturation

Affinity intensity may range from subtle to saturated.

Possible bands:

- trace;
- present;
- dominant;
- saturated;
- unstable;
- transformative.

Exact numeric thresholds are implementation details.

## 8.4 Environmental Conversion

A region near the boundary of two primal fields may develop a Derived field if conditions support stable emergence.

Examples:

- Fire + Air region → Plasma storms;
- Air + Water region → fog and suspended fields;
- Water + Earth region → force-reactive marsh or living gel;
- Earth + Fire region → yield-threshold volcanic terrain.

These should emerge from geography and simulation, not merely be painted as biome labels.

---

# 9. Affinity in Materials and Biology

## 9.1 Materials

A material may possess:

- dominant affinity;
- secondary affinities;
- Derived behavior;
- intensity;
- resonance;
- threshold conditions;
- memory of treatment.

## 9.2 Biology

Affinity may affect:

- metabolism;
- circulation;
- bone and tissue behavior;
- healing;
- adaptation;
- sensory organs;
- reproduction;
- aging;
- disease;
- response to magical fields.

## 9.3 Medicine

Medical traditions may classify illness by Grace behavior:

- runaway Fire transformation;
- failed Air circulation;
- stagnant Water continuity;
- brittle Earth structure;
- unstable Plasma conduction;
- dangerous Colloidal suspension;
- maladaptive Non-Newtonian response;
- Bingham threshold lock or release.

These are worldbuilding directions, not current medical mechanics.

## 9.4 Ecology

Species and ecosystems may create feedback loops:

- plants alter regional affinity;
- predators follow affinity-rich prey;
- rivers distribute Water and Colloidal fields;
- volcanic zones create Bingham materials;
- storms generate Plasma;
- settlement construction concentrates Earth.

---

# 10. Affinity and the Gift

## 10.1 Bits

Bits are raw created potential and may be influenced by environmental affinity.

## 10.2 Bytes

Bytes are structured patterns. Affinity affects what structure is efficient, stable, intuitive, or costly.

## 10.3 Casting Identity

Bit casting should feel direct and field-sensitive.

Byte casting should feel structured and pattern-dependent.

Neither mode owns specific affinities.

## 10.4 Affinity Match

Alignment among caster, spell, focus, and region may improve:

- efficiency;
- stability;
- precision;
- conversion;
- persistence;
- control.

Mismatch should not always mean a flat penalty. It may instead change cost, behavior, risk, or required technique.

## 10.5 Derived Casting

A Derived spell may require:

- innate Derived Affinity;
- simultaneous primal access;
- environmental combination;
- a focus that stabilizes the state;
- a learned Byte pattern;
- a Bit improvisation under rare conditions.

Different cultures may develop different routes.

---

# 11. Resonance

## 11.1 Definition

Resonance is the degree to which two or more created patterns reinforce one another.

It is not limited to weapons and not merely a MAG multiplier.

## 11.2 Resonance Domains

Resonance may occur among:

- being and spell;
- being and region;
- being and item;
- two beings;
- ritual participants;
- structure and weather;
- memory and location;
- culture and symbol;
- primal pair and Derived emergence.

## 11.3 Positive, Negative, and Complex Resonance

Resonance may:

- amplify;
- stabilize;
- distort;
- interfere;
- create feedback;
- trigger transformation;
- expose hidden affinity;
- lower or raise thresholds.

“More resonance” is not always beneficial.

## 11.4 Weapon and Focus Resonance

The existing weapon resonance mechanic may remain a narrow implementation layer, but the Bible should treat it as one expression of a broader law.

---

# 12. Opposition, Tension, and Balance

## 12.1 Retiring the Old Opposition Matrix

The old pairs:

- Fire ↔ Water
- Earth ↔ Air
- Light ↔ Void

are not sufficient as final doctrine.

Light and Dark are not affinities, so their pair must be removed.

The remaining primal tensions may still matter, but not as a universal Pokémon-style weakness table.

## 12.2 Geometric Relationships

The Grace provides several relationship types:

- adjacency;
- derived bridge;
- separation across the lattice;
- shared primal parent;
- rotational counterpart;
- environmental coexistence.

Future mechanics should derive behavior from relationship type rather than one hardcoded opposite function.

## 12.3 Tension Is Contextual

Fire and Water may:

- oppose;
- create steam-like phenomena;
- regulate one another;
- produce destructive pressure;
- support cooking or industry;
- coexist in living systems.

Earth and Air may:

- oppose stability and motion;
- create erosion;
- support rooted growth;
- form dust;
- create pressure systems.

The result depends on intensity, sequence, environment, and structure.

---

# 13. Combat Implications

Combat is one consequence of affinity, not its primary purpose.

## 13.1 Avoid Flat Type Charts

Do not reduce the system to:

- +25% against opposite color;
- -25% against same color;
- eight icons with fixed weakness arrows.

## 13.2 Behavioral Effects

Affinity may affect combat through:

- force transmission;
- movement;
- area persistence;
- armor response;
- healing;
- status behavior;
- terrain;
- resource cost;
- conversion risk;
- threshold mechanics;
- visibility;
- interruption.

## 13.3 Examples

- Fire may accelerate damage over time or consume fuel.
- Air may redirect projectiles or spread effects.
- Water may carry, cool, connect, or erode.
- Earth may anchor, block, or preserve structure.
- Plasma may arc between conductive targets.
- Colloidal effects may suspend hazards or obscure space.
- Non-Newtonian armor may harden under fast impact but remain vulnerable to slow pressure.
- Bingham wards may resist until a yield threshold, then collapse or flow.

These examples are doctrine-compatible, not mandatory final abilities.

---

# 14. Affinity and Autonomous NPCs

## 14.1 Affinity as Perceived Experience

NPCs may experience fields as:

- comfort;
- irritation;
- clarity;
- fatigue;
- hunger change;
- memory association;
- spiritual presence;
- bodily pressure.

## 14.2 Preference Formation

Repeated experiences may cause two beings with the same innate affinity to develop different preferences.

One Fire-affinity NPC may love a forge because it means safety and work. Another may fear it because of trauma.

## 14.3 Cultural Interpretation

NPC behavior should consider belief:

- “This place is sacred.”
- “This color is cursed.”
- “Plasma is divine speech.”
- “Colloidal fog carries ancestors.”
- “The Veil is thinning.”
- “Bingham people cannot be trusted.”

Belief may influence decisions even when objectively incorrect.

## 14.4 Goal Formation

Affinity may eventually contribute to goals:

- seek a compatible region;
- escape saturation;
- acquire a focus;
- perform a ritual;
- study an anomaly;
- protect a sacred Grace;
- challenge a doctrine;
- alter one’s own affinity.

---

# 15. Culture, Religion, and Technology

## 15.1 Shared Grace, Divergent Civilizations

The same lattice may support radically different civilizations.

A culture may center:

- one primal;
- one Derived;
- the Source;
- the Veil;
- the whole white circle;
- the outer worlds;
- the radial Gift lines.

## 15.2 Derived Social Meaning

Derived Affinities may be viewed as:

- children of paired gods;
- proof of unity;
- impure mixtures;
- advanced science;
- sacred marriages;
- unstable anomalies;
- specialist castes;
- natural transitional states.

No interpretation is universally correct.

## 15.3 Technology

Grace-based technology may include:

- field sensors;
- affinity-reactive materials;
- Bit collectors;
- Byte storage;
- conversion engines;
- threshold locks;
- force-reactive armor;
- suspended medicines;
- Plasma conductors;
- environmental stabilizers.

## 15.4 Architecture

Buildings may use Grace geometry to:

- distribute fields;
- stabilize mixed affinities;
- protect against Veil phenomena;
- channel the Gift;
- symbolize legitimacy;
- shape occupant behavior.

---

# 16. Data Model Direction

This section is architectural guidance, not authorization to implement.

## 16.1 Suggested Enum

```python
class Affinity(Enum):
    FIRE = "FIRE"
    PLASMA = "PLASMA"
    AIR = "AIR"
    COLLOIDAL_DISPERSION = "COLLOIDAL_DISPERSION"
    WATER = "WATER"
    NON_NEWTONIAN = "NON_NEWTONIAN"
    EARTH = "EARTH"
    BINGHAM_PLACIDITY = "BINGHAM_PLACIDITY"
```

Do not include `LIGHT` or `DARK` in this enum.

## 16.2 Separate Ontology Enum if Needed

If code needs Light/Dark state, define a separate concept such as:

```python
class OntologicalState(Enum):
    CREATED = "CREATED"
    UNMADE = "UNMADE"
```

Most ordinary entities should never be assigned `UNMADE`; an unmade entity does not behave like a normal entity with a status effect.

## 16.3 Relationship Authority

Replace `opposite(el)` as the sole relationship authority with a richer lattice API:

- `adjacent_primals(affinity)`
- `derived_between(primal_a, primal_b)`
- `parents_of(derived)`
- `is_primal(affinity)`
- `is_higher_state(affinity)`
- `lattice_distance(a, b)` if later useful

Do not implement speculative formulas until a phase plan approves them.

## 16.4 Affinity State Expansion

Future `AffinityState` may include:

```text
innate
granted
suppressed
intensity
latent
expressed
temporary_modifiers
sources
```

Keep the first migration minimal.

---

# 17. Persistence Migration Guidance

The current implementation may contain saved values for `LIGHT` and `VOID`.

A future migration must decide:

- which entities currently using Light receive a Primal or Derived Affinity;
- which uses were placeholders;
- whether any Light-aligned entity should instead carry a rare cosmological trait;
- whether Void-aligned entities become affinity-suppressed, field-disrupted, culturally “Void,” or are re-authored entirely;
- how room fields are converted;
- how old saves are preserved.

Do not map:

- `LIGHT` → all eight affinities;
- `VOID` → Dark;
- `VOID` → no affinity

without entity-by-entity design review.

---

# 18. Testing Doctrine

Tests should verify:

1. Exactly eight affinity enum values.
2. Four primals and four Derived Affinities.
3. Each Derived has exactly two adjacent primal parents.
4. Fire + Air resolves to Plasma.
5. Air + Water resolves to Colloidal Dispersion.
6. Water + Earth resolves to Non-Newtonian.
7. Earth + Fire resolves to Bingham Placidity.
8. Light and Dark are absent from the affinity enum.
9. Neutral regions are not treated as Dark.
10. Multiple effective primals do not automatically become a Derived without emergence conditions.
11. Serialization round-trips all eight values.
12. Legacy values fail visibly or pass through an explicit migration layer.

---

# 19. Design Constraints — What Future Developers Must Not Do

The affinity system is not:

- rock-paper-scissors;
- a Pokémon type chart;
- eight unrelated spell schools;
- a class-selection wheel;
- a personality horoscope;
- a moral alignment;
- a racial caste system;
- a palette swap;
- a set of arbitrary resist percentages;
- permission to invent endless combination enums;
- a replacement for traits, memory, needs, or culture;
- a reason to make every Fire character angry;
- a reason to treat Derived Affinity as superior evolution;
- a reason to classify Light or Dark as ordinary affinity values.

---

# 20. Naming Notes

## 20.1 Veil

Use **Veil** for the cosmological boundary unless a culture intentionally spells or names it differently.

## 20.2 Non-Newtonian

Canonical English spelling: **Non-Newtonian**.

A world-native name may later replace or accompany it if the real-world scientific term feels too modern for in-world speech.

## 20.3 Bingham Placidity

Preserve **Bingham Placidity** as Shawn’s canonical term in this draft.

Because the scientific inspiration is Bingham plastic behavior, the Bible may later decide among:

- Bingham Placidity — world/lore term;
- Bingham Plasticity — scholarly translation;
- a fully world-native name.

Do not silently rename it in code.

## 20.4 Colloidal Dispersion

The full formal term is canonical. Cultures may shorten it differently.

---

# 21. Open Questions

1. Can Derived Affinity be innate, or must it emerge after birth? This draft allows innate Derived Affinity.
2. Can an entity have no affinity while remaining alive?
3. Do affinity intensities combine linearly?
4. Is lattice position directional?
5. What happens when opposite or nonadjacent primals coexist?
6. Are there unstable transient states not granted enum status?
7. How do affinity and race-generation interact?
8. Can affinity be permanently changed without destroying identity?
9. Can the Veil suppress affinity?
10. Is “Bingham Placidity” the final formal name?
11. Do cultures know all four Derived relationships?
12. Are the outer worlds governed by the same lattice?

These questions require future planning, not improvisation during implementation.

---

# 22. Canonical Summary

- Four Primal affinities: Fire, Air, Water, Earth.
- Four Derived Affinities occupy the points between adjacent primals.
- Fire + Air = Plasma.
- Air + Water = Colloidal Dispersion.
- Water + Earth = Non-Newtonian.
- Earth + Fire = Bingham Placidity.
- Derived means emergent combination, not superiority.
- Light and Dark are ontological states, not affinities.
- Affinity describes behavior of created reality.
- Affinity may belong to beings, materials, environments, spells, structures, and cultures.
- Multiple affinities do not automatically collapse into a Derived.
- Resonance is broader than a combat multiplier.
- Combat must express behavior, not a flat weakness chart.
- Culture and belief mediate how intelligent beings understand the Grace.
- The eight-affinity lattice is a foundation for physics, magic, biology, ecology, religion, and technology.

---

# 23. Required Bible and Code Follow-Up

After Shawn accepts this doctrine, the next planning session should prepare a bounded migration that:

1. Adds these two documents to `docs/bible/`.
2. Updates `docs/bible/README.md`.
3. Revises Foundation §7.
4. Revises Stats & Magic Addendum §M5–§M6 and deferred §M9 language.
5. Revises terminology map §8.2.
6. Updates `Mechanics/entities/affinity.py`.
7. Re-authors provisional entity and room affinities.
8. Adds save compatibility and tests.
9. Defers broad combat behavior until the lattice data model is stable.
10. Records the Grace image as canonical visual reference with source attribution to Shawn.

The Bible is the authority. Code follows it through an approved phase, not the other way around.
