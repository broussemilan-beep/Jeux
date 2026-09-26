"""
Geometrie STATIQUE de la roche (etat intact) et de ses fragments (etat
d'impact final), comme suite de Parts Roblox -- meme schema que
r6_battle_throne/scripts/props_battle.py (name/size/pos/shape/rot/
color_rgb/mat/material, voir export_model.py).

La roche n'est PAS une sphere unique : un cluster de spheres de tailles
et decalages LEGEREMENT irreguliers (seed fixe -- voir CLAUDE.md sur la
reproductibilite) donne un aspect de bloc erode/anguleux plutot qu'une
bille parfaitement lisse, plus credible pour "une enorme roche".
`rock_parts(center, radius)` doit rester inscriptible dans une sphere
de rayon `radius` (c'est CETTE sphere qui sert de reference de collision
dans choreography.py/rock_track.py -- ne pas faire deborder le cluster
visuel au-dela sous peine de desynchroniser l'aspect visuel du point de
contact deja calibre).
"""
import math
import random

from export_model import SHAPE_BALL

ROCK_STONE = (104, 96, 82)
ROCK_STONE_DARK = (68, 62, 52)
DEBRIS_STONE = (86, 78, 64)


def rock_parts(center, radius, seed=11):
    """Cluster de spheres INSCRIT dans la sphere de collision (rayon
    `radius`, voir docstring de module) -- une sphere centrale pleine
    (rayon proche de `radius`) plus quelques bosses/aretes en surface
    pour casser la silhouette parfaitement ronde."""
    rng = random.Random(seed)
    cx, cy, cz = center
    parts = []

    core_r = radius * 0.92
    parts.append({"name": "RockCore", "size": (core_r * 2, core_r * 2, core_r * 2),
                  "shape": SHAPE_BALL, "pos": (cx, cy, cz),
                  "color_rgb": ROCK_STONE, "mat": "stone", "material": "Rock"})

    n_bumps = 9
    for i in range(n_bumps):
        theta = rng.uniform(0, 2 * math.pi)
        phi = rng.uniform(0.15, math.pi - 0.15)
        bump_r = radius * rng.uniform(0.30, 0.48)
        # centre de la bosse LEGEREMENT a l'interieur de la surface de
        # collision (pas au-dela) -- garde le cluster inscrit dans
        # `radius` comme l'exige la docstring de module.
        dist = radius - bump_r * rng.uniform(0.35, 0.55)
        ox = dist * math.sin(phi) * math.cos(theta)
        oy = dist * math.cos(phi)
        oz = dist * math.sin(phi) * math.sin(theta)
        tone = ROCK_STONE if i % 2 == 0 else ROCK_STONE_DARK
        parts.append({"name": f"RockBump_{i}", "size": (bump_r * 2, bump_r * 2, bump_r * 2),
                      "shape": SHAPE_BALL, "pos": (cx + ox, cy + oy, cz + oz),
                      "color_rgb": tone, "mat": "stone", "material": "Granite"})
    return parts


def rock_debris_parts(center, radius, seed=17):
    """Fragments eclates a l'impact final (voir rock_track.py, phase
    "impact") -- meme discipline seed fixe/deterministe que
    r6_battle_throne/scripts/props_battle.py.pillar_debris_parts()."""
    rng = random.Random(seed)
    cx, cy, cz = center
    parts = []

    n_big = 7
    for i in range(n_big):
        ang = rng.uniform(0, 2 * math.pi)
        dist = rng.uniform(radius * 0.4, radius * 1.6)
        size = (rng.uniform(0.5, 1.3), rng.uniform(0.5, 1.3), rng.uniform(0.5, 1.3))
        pos = (cx + math.cos(ang) * dist, rng.uniform(0.2, radius * 0.9), cz + math.sin(ang) * dist)
        parts.append({"name": f"RockDebris_{i}", "size": size, "pos": pos,
                      "color_rgb": DEBRIS_STONE if i % 2 == 0 else ROCK_STONE_DARK,
                      "mat": "stone", "material": "Rock"})

    n_small = 14
    for i in range(n_small):
        ang = rng.uniform(0, 2 * math.pi)
        dist = rng.uniform(radius * 0.8, radius * 2.6)
        s = rng.uniform(0.12, 0.32)
        pos = (cx + math.cos(ang) * dist, rng.uniform(0.05, 0.5), cz + math.sin(ang) * dist)
        parts.append({"name": f"RockRubble_{i}", "size": (s, s, s), "pos": pos,
                      "color_rgb": DEBRIS_STONE, "mat": "stone", "material": "Rock"})
    return parts
