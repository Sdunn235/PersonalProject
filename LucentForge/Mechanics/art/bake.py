"""bake.py — write genome renders to assets/generated/ and record them in assets/registry.json.

    py -m Mechanics.art.bake            # bake every genome in Mechanics/data/art/
    py -m Mechanics.art.bake gobby grom # bake some

Never writes to assets/images/ (Shawn's art). Each baked file is registered with its genome id and seed,
so provenance is automatic.
"""
from __future__ import annotations

import json
import os
import sys

import pygame

from Mechanics.art.genome import Genome, load_all
from Mechanics.art.render import render

_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT_DIR = os.path.join(_ROOT, "assets", "generated")
REGISTRY = os.path.join(_ROOT, "assets", "registry.json")


def _load_registry() -> dict:
    if os.path.isfile(REGISTRY):
        with open(REGISTRY, encoding="utf-8") as f:
            return json.load(f)
    return {"assets": []}


def _save_registry(reg: dict) -> None:
    reg["assets"].sort(key=lambda e: e["path"])
    with open(REGISTRY, "w", encoding="utf-8", newline="\n") as f:
        json.dump(reg, f, indent=2)
        f.write("\n")


def bake(genome: Genome, registry: dict) -> str:
    os.makedirs(OUT_DIR, exist_ok=True)
    rel = f"assets/generated/{genome.id}.png"
    pygame.image.save(render(genome), os.path.join(_ROOT, rel))
    entry = {"path": rel, "kind": genome.kind, "source": "generated",
             "licence": "project-owned (generated from an art genome)",
             "genome": genome.id, "seed": genome.seed}
    registry["assets"] = [e for e in registry["assets"] if e["path"] != rel] + [entry]
    return rel


def main(ids: list[str]) -> int:
    pygame.init()
    if pygame.display.get_surface() is None:
        pygame.display.set_mode((1, 1))
    genomes = [g for g in load_all() if not ids or g.id in ids]
    registry = _load_registry()
    for g in genomes:
        print(f"baked {bake(g, registry)}")
    _save_registry(registry)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
