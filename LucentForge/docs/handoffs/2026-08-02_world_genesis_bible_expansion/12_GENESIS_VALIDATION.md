# Genesis Validation Strategy v1

## Validation classes

### Structural

- dimensions match;
- projection metadata exists;
- IDs resolve;
- wrap rules are valid;
- required artifacts are present.

### Tectonic

- every pixel has one plate ID;
- no unexplained gaps or overlaps;
- boundary graph agrees with raster adjacency;
- motion vectors exist where required;
- boundary classifications are valid.

### Geographic

- rivers generally descend;
- rivers terminate correctly;
- coastlines separate land and water;
- ocean basins are connected or intentionally enclosed;
- mountains correspond to uplift logic or explicit exceptions.

### Climate

- temperature broadly responds to latitude/elevation;
- rainfall reacts to ocean access and barriers;
- biome assignments match climate envelopes or documented affinity exceptions.

### Canonical

- protected plate geometry remains unchanged;
- protected landmarks remain present;
- locked names and IDs are preserved;
- overrides are reported;
- Bible contradictions are surfaced.

### Runtime conversion

- panel coordinates are unique;
- generated panel manifests resolve;
- active/background simulation partitions are valid;
- save/load serialization round trips.

## Validation severity

- INFO
- WARNING
- ERROR
- CANON_CONFLICT

A canonical conflict must never be silently downgraded.

## Visual diagnostics

Every major raster stage should be viewable independently.

Visualizers do not mutate source data.
