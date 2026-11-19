"""render.py — genome → pixels (studio/art charter).

Reads only a Genome (genome.py) and its own seed (a private random.Random — never the global RNG or the
clock), so the same genome always renders the same pixels. Creatures render as the game's 3×4 walk sheet
(rows down/left/right/up, 3 frames, 32-px cells); trees and rocks as one 32-px tile. Proportions come from
genes; the only constants here are drawing conventions (outline width, frame offsets).

Kept separate from genome.py so another renderer (isometric 64×32, the long-term target) can read the
same genes.
"""
from __future__ import annotations

import math
import random

import pygame

import settings
from Mechanics.art.genome import Genome

T = settings.TILE_SIZE
DIRECTIONS = ("down", "left", "right", "up")      # sheet rows, as EntitySprite slices them
FRAMES = 3                                       # frame 0 = idle, 1/2 = alternate steps

_DEFAULT_PALETTE = {
    "creature": {"skin": (96, 140, 70), "skin_shadow": (64, 100, 48), "cloth": (110, 84, 60),
                 "cloth_shadow": (80, 60, 44), "outline": (24, 22, 20), "eye": (250, 230, 120)},
    "tree": {"bark": (100, 72, 48), "bark_shadow": (70, 50, 34), "leaf": (60, 120, 56),
             "leaf_shadow": (38, 86, 40), "leaf_light": (96, 156, 80), "outline": (22, 30, 20)},
    "rock": {"stone": (128, 126, 120), "stone_shadow": (92, 90, 86), "stone_light": (170, 168, 160),
             "outline": (40, 40, 40)},
}


def _colors(genome: Genome) -> dict:
    pal = dict(_DEFAULT_PALETTE[genome.kind])
    pal.update(genome.palette)
    return {k: (*v[:3], 255) for k, v in pal.items()}


def render(genome: Genome) -> pygame.Surface:
    if genome.kind == "creature":
        return render_creature_sheet(genome)
    if genome.kind == "tree":
        return render_tree(genome)
    return render_rock(genome)


# ── creatures ───────────────────────────────────────────────────────────────────────────────────────
def render_creature_sheet(genome: Genome) -> pygame.Surface:
    sheet = pygame.Surface((FRAMES * T, len(DIRECTIONS) * T), pygame.SRCALPHA)
    for row, facing in enumerate(DIRECTIONS):
        for frame in range(FRAMES):
            cell = pygame.Surface((T, T), pygame.SRCALPHA)
            _draw_creature(cell, genome, facing, frame)
            sheet.blit(cell, (frame * T, row * T))
    return sheet


def _ellipse(surf, color, outline, rect: pygame.Rect) -> None:
    pygame.draw.ellipse(surf, outline, rect.inflate(2, 2))
    pygame.draw.ellipse(surf, color, rect)


def _draw_creature(surf: pygame.Surface, g: Genome, facing: str, frame: int) -> None:
    c = _colors(g)
    gn = g.genes
    scale = g.growth_scale
    height = max(8.0, gn["height"] * T * scale)                  # figure height in px
    head_d = max(4.0, gn["head_size"] * height)
    leg = max(2.0, gn["limb_length"] * height)
    arm = max(2.0, gn["arm_length"] * height)
    body_w = max(4.0, gn["body_width"] * T * scale)
    body_h = max(3.0, height - leg - head_d * 0.85)
    side = {"left": -1, "right": 1}.get(facing, 0)               # facing sign for side views
    stoop = gn["stoop"] * T * scale * side

    feet_y = T - 2
    bob = 1 if frame else 0                                      # body dips mid-step
    hip_y = feet_y - leg + bob
    shoulder_y = hip_y - body_h
    cx = T / 2

    # Legs: front/back views alternate leg length; side views swing the legs apart.
    leg_w = max(2, int(body_w * 0.28))
    for i, lx in enumerate((-1, 1)):
        x = cx + lx * body_w * 0.22 - leg_w / 2
        lift = 0
        swing = 0
        if frame:
            stepping = (i == 0) == (frame == 1)
            if side == 0:
                lift = 2 if stepping else 0
            else:
                swing = (2 if stepping else -2) * side
                x = cx - leg_w / 2
        rect = pygame.Rect(int(x + swing), int(hip_y), leg_w, max(1, int(feet_y - hip_y - lift)))
        pygame.draw.rect(surf, c["outline"], rect.inflate(2, 2))
        pygame.draw.rect(surf, c["cloth_shadow"], rect)

    # Body.
    body = pygame.Rect(0, 0, int(body_w), int(body_h))
    body.midbottom = (int(cx + stoop * 0.3), int(hip_y + 2))
    _ellipse(surf, c["cloth"], c["outline"], body)

    # Arms swing opposite the legs.
    arm_w = max(1, int(body_w * 0.18))
    swing = (2 if frame == 1 else -2 if frame == 2 else 0)
    for i, ax in enumerate((-1, 1)):
        if side and ax != side:
            continue                                             # far arm hidden in side view
        dy = swing if i == 0 else -swing
        x = cx + ax * (body_w / 2) - (arm_w if ax < 0 else 0) + stoop * 0.3
        rect = pygame.Rect(int(x), int(shoulder_y + 2 + dy * 0.5), arm_w, int(arm))
        pygame.draw.rect(surf, c["outline"], rect.inflate(2, 2))
        pygame.draw.rect(surf, c["skin"], rect)

    # Head, with goblin ears.
    head_cx = cx + stoop
    head_cy = shoulder_y - head_d * 0.35
    ear = gn["ear_length"] * T * scale
    if ear >= 1.0:
        for ex in (-1, 1):
            if side and ex == side:
                continue                                         # near ear hidden behind the head
            base_x = head_cx + ex * head_d * 0.40
            tip = (base_x + ex * ear, head_cy - head_d * 0.25)
            pts = [(base_x, head_cy - head_d * 0.15), (base_x, head_cy + head_d * 0.15), tip]
            pygame.draw.polygon(surf, c["outline"], pts)
            inner = [(base_x, head_cy - head_d * 0.08), (base_x, head_cy + head_d * 0.08),
                     (tip[0] - ex, tip[1] + 1)]
            pygame.draw.polygon(surf, c["skin"], inner)
    head = pygame.Rect(0, 0, int(head_d), int(head_d))
    head.center = (int(head_cx), int(head_cy))
    _ellipse(surf, c["skin"], c["outline"], head)

    # Spots: deterministic per individual (its seed), same in every frame.
    rng = random.Random(g.seed)
    for _ in range(2):
        sx = head.left + 1 + rng.random() * max(1, head.width - 3)
        sy = head.top + 1 + rng.random() * max(1, head.height * 0.4)
        surf.set_at((int(sx), int(sy)), c["skin_shadow"])

    # Eyes: none from behind; one in profile; two facing the viewer.
    eye = max(1, int(gn["eye_size"] * T * scale * 0.5))
    if facing == "down":
        for ex in (-1, 1):
            pygame.draw.circle(surf, c["eye"], (int(head_cx + ex * head_d * 0.2), int(head_cy)), eye)
    elif side:
        pygame.draw.circle(surf, c["eye"], (int(head_cx + side * head_d * 0.25), int(head_cy)), eye)


# ── props ───────────────────────────────────────────────────────────────────────────────────────────
def render_tree(g: Genome) -> pygame.Surface:
    surf = pygame.Surface((T, T), pygame.SRCALPHA)
    c = _colors(g)
    gn = g.genes
    s = g.growth_scale
    rng = random.Random(g.seed)
    trunk_h = max(2, int(gn["trunk_height"] * T * s))
    trunk_w = max(2, int(gn["trunk_width"] * T * s))
    base_y = T - 1
    trunk = pygame.Rect(0, 0, trunk_w, trunk_h)
    trunk.midbottom = (T // 2, base_y)
    pygame.draw.rect(surf, c["outline"], trunk.inflate(2, 2))
    pygame.draw.rect(surf, c["bark"], trunk)
    pygame.draw.line(surf, c["bark_shadow"], trunk.topright, trunk.bottomright)
    radius = max(2.0, gn["canopy_radius"] * T * s)
    ccx = T / 2 + gn["lean"] * T * s
    ccy = trunk.top - radius * 0.55
    lumps = int(round(gn["canopy_lumps"]))
    blobs = [(ccx, ccy, radius * 0.75)]
    for i in range(lumps):
        ang = 2 * math.pi * (i / lumps) + rng.random() * 0.6
        blobs.append((ccx + math.cos(ang) * radius * 0.45, ccy + math.sin(ang) * radius * 0.35,
                      radius * (0.45 + rng.random() * 0.2)))
    for (x, y, r) in blobs:
        pygame.draw.circle(surf, c["outline"], (int(x), int(y)), int(r) + 1)
    for (x, y, r) in blobs:
        pygame.draw.circle(surf, c["leaf_shadow"], (int(x), int(y)), int(r))
    for (x, y, r) in blobs:
        pygame.draw.circle(surf, c["leaf"], (int(x - 1), int(y - 1)), max(1, int(r) - 1))
    pygame.draw.circle(surf, c["leaf_light"], (int(ccx - radius * 0.3), int(ccy - radius * 0.3)),
                       max(1, int(radius * 0.25)))
    return surf


def render_rock(g: Genome) -> pygame.Surface:
    surf = pygame.Surface((T, T), pygame.SRCALPHA)
    c = _colors(g)
    gn = g.genes
    s = g.growth_scale
    rng = random.Random(g.seed)
    rx = max(2.0, gn["size"] * T * s / 2)
    ry = max(2.0, rx * (1.0 - gn["flatness"]))
    cx, cy = T / 2, T - 1 - ry
    n = int(round(gn["facets"]))
    pts = []
    for i in range(n):
        ang = 2 * math.pi * i / n
        jitter = 1.0 - gn["roughness"] * rng.random()
        pts.append((cx + math.cos(ang) * rx * jitter, cy + math.sin(ang) * ry * jitter))
    pygame.draw.polygon(surf, c["outline"], [(x, y) for x, y in pts], 0)
    inner = [(cx + (x - cx) * 0.9, cy + (y - cy) * 0.9) for x, y in pts]
    pygame.draw.polygon(surf, c["stone"], inner)
    shade = [(x, y) for x, y in inner if y >= cy]
    if len(shade) >= 3:
        pygame.draw.polygon(surf, c["stone_shadow"], shade)
    light = [(cx + (x - cx) * 0.5 - rx * 0.15, cy + (y - cy) * 0.5 - ry * 0.25) for x, y in inner]
    pygame.draw.polygon(surf, c["stone_light"], light)
    return surf
