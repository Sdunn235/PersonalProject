from __future__ import annotations
import enum
import json
import os
from dataclasses import dataclass


class PanelEdge(enum.Enum):
    NORTH = "NORTH"
    SOUTH = "SOUTH"
    EAST  = "EAST"
    WEST  = "WEST"


@dataclass(frozen=True)
class WorldPos:
    panel_x: int
    panel_y: int
    col:     int
    row:     int


@dataclass
class PanelConfig:
    id:      str
    name:    str
    panel_x: int
    panel_y: int
    north:   str | None
    south:   str | None
    east:    str | None
    west:    str | None


class PanelLoader:
    """Panel registry and transition stub. Stage 3: Panel(0,0) only, all edges null.

    # TODO Stage 3.5+: load tile map, sources, entities for adjacent panel.
    """

    def __init__(self) -> None:
        self._panels: dict[tuple[int, int], PanelConfig] = {}

    @classmethod
    def from_json(cls, path: str) -> "PanelLoader":
        loader = cls()
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        for entry in data:
            edges = entry.get("edges", {})
            cfg = PanelConfig(
                id=entry["id"],
                name=entry["name"],
                panel_x=entry["panel_x"],
                panel_y=entry["panel_y"],
                north=edges.get("NORTH"),
                south=edges.get("SOUTH"),
                east=edges.get("EAST"),
                west=edges.get("WEST"),
            )
            loader._panels[(cfg.panel_x, cfg.panel_y)] = cfg
        return loader

    def can_transition(self, panel_x: int, panel_y: int, edge: PanelEdge) -> bool:
        """True if an adjacent panel is defined in this direction.

        # TODO Stage 3.5+: load tile map, sources, entities for adjacent panel.
        """
        cfg = self._panels.get((panel_x, panel_y))
        if cfg is None:
            return False
        return getattr(cfg, edge.value.lower()) is not None

    def get_adjacent_panel(
        self, panel_x: int, panel_y: int, edge: PanelEdge
    ) -> "PanelConfig | None":
        """Return the adjacent PanelConfig or None if no transition defined.

        # TODO Stage 3.5+: load tile map, sources, entities for adjacent panel.
        """
        cfg = self._panels.get((panel_x, panel_y))
        if cfg is None:
            return None
        adj_id = getattr(cfg, edge.value.lower())
        if adj_id is None:
            return None
        return next((p for p in self._panels.values() if p.id == adj_id), None)
