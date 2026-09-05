"""
Geometrie STATIQUE du decor destructible de l'arene de combat : un
pilier de pierre en ruine, meme famille visuelle que les textures
ruin_wall/stone_ground DEJA utilisees par le lecteur de r6_hit_combo
(copiees telles quelles dans ce prototype, voir textures/ -- l'arene du
combo de poing etait deja une ruine, ce pilier s'y integre plutot que
d'introduire un nouveau style). Meme schema de Part que props.py
(voir sa docstring de module pour le detail des champs "mat"/"material").

Deux etats de geometrie, jamais melanges par une simulation physique
(choregraphie entierement scriptee, pas de temps reel -- voir
choreography.py) :

  - pillar_parts(center) : le pilier INTACT, visible de t=0 jusqu'a
    choreography.PILLAR_HIT_T.
  - pillar_debris_parts(center, seed) : les fragments eclates, generes
    de facon DETERMINISTE (random.Random(seed) -- jamais random.random()
    nu, un seed fixe donne toujours la meme scene de debris,
    reproductible d'une capture a l'autre, meme discipline que le reste
    du depot pour les seeds -- voir CLAUDE.md), visibles a partir de ce
    meme instant (le lecteur bascule les deux groupes de Parts
    ensemble, voir build_viewer.py).

`center` n'est PAS redefini ici : appele avec choreography.PILLAR_POS,
un seul point de verite pour la position du pilier dans l'arene.
"""
import math
import random

from export_model import SHAPE_CYLINDER

# Meme constante que throne_crown/scripts/props.py (fichier independant,
# convention du depot -- voir docstring de module) : un Part Shape=
# Cylinder a par defaut son axe long (la longueur, Size.X) le long de
# l'axe LOCAL X, faces rondes aux deux bouts -- pour un fut de colonne
# DEBOUT (faces rondes en haut/bas, longueur verticale), il faut donc
# amener cet axe local X sur le monde Y, exactement ce que fait cette
# rotation (deja verifiee sur les anneaux de couronne/trone).
_ROT_Z90 = [[0.0, -1.0, 0.0], [1.0, 0.0, 0.0], [0.0, 0.0, 1.0]]

# Pierre claire de ruine exterieure (soleil), distincte du gris froid
# STONE de throne_crown.props (salle interieure) -- meme logique de
# palette-par-lieu que le reste du depot.
PILLAR_STONE = (150, 138, 116)
PILLAR_STONE_DARK = (108, 98, 80)
DEBRIS_STONE = (96, 88, 72)

PILLAR_BASE_SIZE = (2.4, 0.6, 2.4)
PILLAR_SHAFT_RADIUS = 0.9
PILLAR_SHAFT_H = 5.2
PILLAR_DRUM_N = 5          # colonne "cannelee" -- tambours empiles, silhouette de ruine antique (coherente avec le style deja etabli du trone/couronne) plutot qu'un cylindre plein
PILLAR_CAP_SIZE = (2.0, 0.5, 2.0)

PILLAR_TOTAL_H = PILLAR_BASE_SIZE[1] + PILLAR_SHAFT_H + PILLAR_CAP_SIZE[1]


def pillar_parts(center):
    """center = (x, y_sol, z), y_sol = 0.0 normalement (voir
    choreography.PILLAR_POS)."""
    cx, cy, cz = center
    parts = []
    y = cy

    parts.append({"name": "PillarBase", "size": PILLAR_BASE_SIZE,
                  "pos": (cx, y + PILLAR_BASE_SIZE[1] / 2.0, cz),
                  "color_rgb": PILLAR_STONE_DARK, "mat": "stone", "material": "Granite"})
    y += PILLAR_BASE_SIZE[1]

    drum_h = PILLAR_SHAFT_H / PILLAR_DRUM_N
    for k in range(PILLAR_DRUM_N):
        tone = PILLAR_STONE if k % 2 == 0 else PILLAR_STONE_DARK
        parts.append({"name": f"PillarDrum_{k}", "shape": SHAPE_CYLINDER,
                      "size": (drum_h, PILLAR_SHAFT_RADIUS * 2, PILLAR_SHAFT_RADIUS * 2),
                      "pos": (cx, y + drum_h / 2.0, cz), "rot": _ROT_Z90,
                      "color_rgb": tone, "mat": "stone", "material": "Slate"})
        y += drum_h

    # -- le sommet est deja EBRECHE avant meme l'impact (une ruine, pas
    # une colonne neuve) : le chapiteau est incomplet, coupe en biais --
    # lisible comme "va se briser", pas juste un decor neutre.
    parts.append({"name": "PillarCap",
                  "size": (PILLAR_CAP_SIZE[0], PILLAR_CAP_SIZE[1], PILLAR_CAP_SIZE[2] * 0.7),
                  "pos": (cx, y + PILLAR_CAP_SIZE[1] / 2.0, cz - PILLAR_CAP_SIZE[2] * 0.15),
                  "color_rgb": PILLAR_STONE, "mat": "stone", "material": "Granite"})
    return parts


def pillar_debris_parts(center, seed=6):
    """N fragments anguleux, disperses de facon DETERMINISTE (voir
    docstring de module). Le pilier "explose" surtout a l'horizontale
    (angle plein 0-2*pi -- Rival percute le fut de plein fouet, la
    direction d'impact n'a pas un sens privilegie unique une fois le
    fut brise), avec un nuage d'eclats plus petits en plus des gros
    blocs pour vendre l'impact (pas juste 2-3 boites qui se separent)."""
    rng = random.Random(seed)
    cx, cy, cz = center
    parts = []

    n_big = 6
    for i in range(n_big):
        ang = rng.uniform(0, 2 * math.pi)
        dist = rng.uniform(0.8, 2.6)
        size = (rng.uniform(0.5, 1.1), rng.uniform(0.5, 1.3), rng.uniform(0.5, 1.1))
        pos = (cx + math.cos(ang) * dist, cy + rng.uniform(0.2, 1.6), cz + math.sin(ang) * dist)
        parts.append({"name": f"Debris_{i}", "size": size, "pos": pos,
                      "color_rgb": DEBRIS_STONE if i % 2 == 0 else PILLAR_STONE_DARK,
                      "mat": "stone", "material": "Rock"})

    n_small = 10
    for i in range(n_small):
        ang = rng.uniform(0, 2 * math.pi)
        dist = rng.uniform(1.5, 4.0)
        s = rng.uniform(0.15, 0.35)
        pos = (cx + math.cos(ang) * dist, cy + rng.uniform(0.05, 0.5), cz + math.sin(ang) * dist)
        parts.append({"name": f"Rubble_{i}", "size": (s, s, s), "pos": pos,
                      "color_rgb": DEBRIS_STONE, "mat": "stone", "material": "Rock"})
    return parts
