# source_selector.py — Memory-weighted source selection (Heartbeat-3)
# Replaces pure nearest-distance logic with a weighted score:
#   distance (50%) + memory preference (40%) + novelty bonus (10%)
from __future__ import annotations
from Mechanics.needs.need_source import NeedSource
from Mechanics.ai.memory import Memory
from Mechanics.entities.traits import Traits
import settings


def select_source(need_id: str, sources: list[NeedSource],
                  from_x: float, from_y: float,
                  memory: Memory, traits: Traits,
                  contested: set[str] | None = None) -> NeedSource | None:
    """Pick the best source for a need, weighted by distance + memory + curiosity.

    Sources in the `contested` set (goblin-occupied) get a heavy penalty
    but aren't hard-blocked — desperate NPCs may still choose them.
    """
    candidates = [s for s in sources if s.need_id == need_id]
    if not candidates:
        return None

    # H5: filter out completely depleted finite sources — don't waste trips
    viable = [s for s in candidates if not s.is_finite or s.stock > 0]
    if viable:
        candidates = viable
    # else: all depleted — fall through with full list (desperate NPC may still try)

    if len(candidates) == 1:
        return candidates[0]

    max_dist = settings.MAX_MAP_DISTANCE
    best_source = None
    best_score = -1.0

    for source in candidates:
        dist = source.distance_from(from_x, from_y)
        distance_score = 1.0 - (dist / max_dist) if max_dist > 0 else 0.5

        memory_score = memory.get_source_preference(source.label)

        novelty_bonus = 0.0
        if memory.get_visit_count(source.label) == 0:
            novelty_bonus = traits.curiosity * 0.3

        # H5: stock availability — depleted sources are strongly avoided
        if source.is_finite:
            if source.stock <= 0:
                stock_score = 0.0
            else:
                stock_score = min(1.0, source.stock / (source.capacity * 0.3))
        else:
            stock_score = 1.0  # infinite sources always available

        score = (distance_score * settings.SOURCE_DIST_WEIGHT
                 + memory_score * settings.SOURCE_MEMORY_WEIGHT
                 + stock_score * settings.SOURCE_STOCK_WEIGHT
                 + novelty_bonus * settings.SOURCE_NOVELTY_WEIGHT)

        # Goblin-contested penalty (H4): heavily discourage but don't block
        if contested and source.label in contested:
            score *= 0.1

        if score > best_score:
            best_score = score
            best_source = source

    return best_source
