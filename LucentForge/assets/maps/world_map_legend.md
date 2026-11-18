# World Map Legend

This file defines the token set used by `world_map.csv`.

The map is a macro fantasy geography sketch for LucentForge, not the current 18×18 runtime panel map.
It is intended to show continent shape, climate flow, rivers, rain shadows, and biome placement that
would make sense on a living world.

## Tokens

| Token | Meaning | Notes |
|---|---|---|
| `O` | Ocean | Deep water / open sea |
| `C` | Coast | Shoreline and shallow edge tiles |
| `B` | Bluff | Steep coastal escarpment, cliff, or drop-off |
| `R` | River | Major inland river or channel |
| `W` | Wetland | Marsh, floodplain, lake edge, or river mouth |
| `V` | Valley | Fertile mountain valley or river valley |
| `P` | Plains | Open temperate lowlands and grassland |
| `F` | Forest | Dense woodland or temperate forest |
| `S` | Savannah | Open warm grassland / dry grass plains |
| `D` | Drylands | Desert, scrub, badlands, or arid interior |
| `J` | Jungle | Hot, wet tropical growth |
| `H` | Highlands | Foothills, plateaus, or upland terrain |
| `M` | Mountains | Major mountain massifs and peaks |
| `I` | Ice | Polar ice cap / frozen sea |

## Reading Notes

- Rivers should originate in high, wet terrain and descend toward oceans, lakes, or wetlands.
- Mountain valleys can still be green and fertile when they receive enough water.
- Deserts form in dry interiors and rain shadows, not randomly beside jungles.
- Jungles belong in warm, wet regions, especially equatorial or monsoon belts.
- Savannah should sit between forest and desert climates.
- Bluffs are most useful on steep coastlines and sharp terrain transitions.
- Coast and wetland tiles are transitional, so they often sit between major biomes.
