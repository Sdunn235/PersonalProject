"""genome.py — art genomes: the data a world object's look grows from (studio/art charter).

Art is GROWN, not painted. A genome is a kind (creature / tree / rock), a seed, a growth stage and a set
of bounded genes plus a palette. The renderer (render.py) reads only this. Mutation and growth are
first-class so the look of the world can vary and evolve (the biology seed — Creatures DNA, biochem §B1).

Every gene has bounds and a default, so adding a gene never breaks an older genome file.
"""
from __future__ import annotations

import copy
import json
import os
from dataclasses import dataclass, field

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "art")

KINDS = ("creature", "tree", "rock")

# name: (min, max, default). Values are fractions of a 32-px cell unless noted; renderers derive pixels.
_GENES = {
    "creature": {
        "height":      (0.45, 0.95, 0.75),   # figure height at full growth, fraction of the cell
        "body_width":  (0.25, 0.70, 0.40),   # torso width, fraction of the cell
        "head_size":   (0.20, 0.45, 0.32),   # head diameter, fraction of figure height
        "ear_length":  (0.00, 0.40, 0.10),   # pointed ears, fraction of the cell (goblins: long)
        "limb_length": (0.15, 0.40, 0.28),   # legs, fraction of figure height
        "arm_length":  (0.20, 0.50, 0.32),   # arms, fraction of figure height
        "stoop":       (0.00, 0.25, 0.05),   # forward hunch, fraction of the cell (side views)
        "eye_size":    (0.05, 0.15, 0.08),   # fraction of the cell
        "skin_marks":  (0.0, 4.0, 2.0),      # mottling spots on the head (rounded count; goblins mottle)
    },
    "tree": {
        "trunk_height":  (0.20, 0.60, 0.35),
        "trunk_width":   (0.08, 0.30, 0.15),
        "canopy_radius": (0.15, 0.45, 0.32),
        "canopy_lumps":  (2.0, 7.0, 4.0),    # count of canopy lobes (rounded)
        "lean":          (-0.20, 0.20, 0.0),  # canopy offset, fraction of the cell
    },
    "rock": {
        "size":      (0.30, 0.95, 0.65),     # width, fraction of the cell
        "roughness": (0.00, 0.50, 0.20),     # outline jitter
        "flatness":  (0.00, 0.60, 0.30),     # squash of the height
        "facets":    (5.0, 12.0, 8.0),       # outline points (rounded)
    },
}
# Base material colors per kind (defaults). A genome's palette may only name these; every other shade
# (shadow, light, outline) is grown from them by the house style (style.py), never stored.
MATERIALS = {
    "creature": {"skin": (96, 140, 70), "cloth": (110, 84, 60), "eye": (250, 230, 120)},
    "tree": {"bark": (100, 72, 48), "leaf": (60, 120, 56)},
    "rock": {"stone": (128, 126, 120)},
}

GENE_BOUNDS = {k: {g: (lo, hi) for g, (lo, hi, _d) in genes.items()} for k, genes in _GENES.items()}
GENE_DEFAULTS = {k: {g: d for g, (_lo, _hi, d) in genes.items()} for k, genes in _GENES.items()}

# Growth: a newborn is this fraction of its adult size; size-like features scale linearly to 1.0.
GROWTH_NEWBORN_SCALE = 0.5


@dataclass
class Genome:
    id: str
    kind: str
    seed: int
    stage: float = 1.0                       # 0 = newborn / sapling / pebble, 1 = grown
    species: str = ""                        # who it is (Story/Lore): "goblin", "human", "oak" ...
    parent: str = ""                         # the genome id this one was grown from (lineage), or ""
    genes: dict = field(default_factory=dict)
    palette: dict = field(default_factory=dict)

    @property
    def growth_scale(self) -> float:
        return GROWTH_NEWBORN_SCALE + (1.0 - GROWTH_NEWBORN_SCALE) * max(0.0, min(1.0, self.stage))

    @staticmethod
    def from_dict(d: dict) -> "Genome":
        kind = d["kind"]
        if kind not in KINDS:
            raise ValueError(f"unknown art kind {kind!r}")
        genes = dict(GENE_DEFAULTS[kind])
        for name, value in d.get("genes", {}).items():
            if name not in genes:
                raise ValueError(f"{d['id']}: unknown gene {name!r} for {kind}")
            lo, hi = GENE_BOUNDS[kind][name]
            if not lo <= float(value) <= hi:
                raise ValueError(f"{d['id']}: gene {name}={value} outside [{lo}, {hi}]")
            genes[name] = float(value)
        palette = {}
        for role, rgb in d.get("palette", {}).items():
            if role not in MATERIALS[kind]:
                raise ValueError(f"{d['id']}: palette role {role!r} is not a {kind} material "
                                 f"{sorted(MATERIALS[kind])} (shades are derived by style.py)")
            palette[role] = tuple(int(c) for c in rgb)
        return Genome(id=d["id"], kind=kind, seed=int(d.get("seed", 0)),
                      stage=float(d.get("stage", 1.0)), species=str(d.get("species", "")),
                      parent=str(d.get("parent", "")), genes=genes, palette=palette)

    def to_dict(self) -> dict:
        return {"id": self.id, "kind": self.kind, "seed": self.seed, "stage": self.stage,
                "species": self.species, "parent": self.parent,
                "genes": dict(self.genes), "palette": {k: list(v) for k, v in self.palette.items()}}


def load(path: str) -> Genome:
    with open(path, encoding="utf-8") as f:
        return Genome.from_dict(json.load(f))


def load_all(data_dir: str = DATA_DIR) -> list[Genome]:
    """Every genome in data_dir. A genome's `parent` must be another genome there, of the same kind."""
    files = sorted(f for f in os.listdir(data_dir) if f.endswith(".json"))
    genomes = [load(os.path.join(data_dir, f)) for f in files]
    kinds = {g.id: g.kind for g in genomes}
    for g in genomes:
        if g.parent and kinds.get(g.parent) != g.kind:
            raise ValueError(f"{g.id}: parent {g.parent!r} is not a {g.kind} genome in {data_dir}")
    return genomes


def mutate(genome: Genome, rng, rate: float) -> Genome:
    """A child genome: each gene nudged by a normal step of rate × (half its range), clamped to bounds;
    palette colors drift a little. rate 0 → an identical copy."""
    child = copy.deepcopy(genome)
    if rate <= 0:
        return child
    for name, value in child.genes.items():
        lo, hi = GENE_BOUNDS[child.kind][name]
        child.genes[name] = min(hi, max(lo, value + rng.gauss(0.0, rate * (hi - lo) * 0.5)))
    for role, rgb in child.palette.items():
        child.palette[role] = tuple(min(255, max(0, int(c + rng.gauss(0.0, rate * 24)))) for c in rgb)
    return child


def grow(genome: Genome, stage: float) -> Genome:
    """The same individual at another growth stage (0..1)."""
    child = copy.deepcopy(genome)
    child.stage = max(0.0, min(1.0, stage))
    return child
