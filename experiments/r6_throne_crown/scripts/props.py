"""
Geometrie STATIQUE du trone et de la couronne, comme suite de Parts
Roblox (voir export_model.py), dans le MEME repere que le personnage R6
(studs, -Z = avant, sol = Y 0, personnage debout : pieds a Y=0, hanches/
HumanoidRootPart a Y=3 -- valeurs lues sur rig/r6_rig.json, pas devinees,
voir le calcul dans README.md).

Le trone est positionne pour qu'un personnage assis (choreography.sit_
and_crown(), HumanoidRootPart a Y=3 pendant toute l'assise -- seules les
jambes tournent, la hanche ne descend pas, exactement le mecanisme de
l'assise R6 par defaut de Roblox faute de genou) s'y encastre : assise du
siege a Y=2.0 (= hanche a Y=3 moins la moitie de la hauteur du torse,
c'est le point d'attache reel des jambes sur le torse).
"""
import math

from export_model import SHAPE_BLOCK, SHAPE_CYLINDER, SHAPE_BALL

STONE = (110, 108, 116)
STONE_DARK = (70, 68, 74)
GOLD = (196, 160, 60)
GOLD_LIGHT = (224, 190, 90)
GEM_RED = (150, 25, 30)

_ROT_Z90 = [[0.0, -1.0, 0.0], [1.0, 0.0, 0.0], [0.0, 0.0, 1.0]]  # local X -> monde Y


def throne_parts():
    parts = []

    # Estrade au sol -- purement decorative, dessus a Y=0 (niveau des
    # pieds du personnage debout).
    parts.append({"name": "Dais", "size": (7.0, 0.6, 5.5), "pos": (0.0, -0.3, 1.4),
                  "color_rgb": STONE_DARK})

    # 4 pieds sous le siege, du dais (Y=0) jusqu'au dessous du siege (Y=1.7).
    for x in (-1.9, 1.9):
        for z in (-0.4, 2.1):
            parts.append({"name": f"Leg_{x}_{z}", "size": (0.5, 1.7, 0.5),
                          "pos": (x, 0.85, z), "color_rgb": STONE_DARK})

    # Siege -- dessus a Y=2.0 (hanche assise moins demi-hauteur du torse).
    parts.append({"name": "Seat", "size": (4.4, 0.6, 3.6), "pos": (0.0, 1.7, 0.9),
                  "color_rgb": STONE})

    # Dossier -- derriere le siege (+Z), monte bien au-dessus de la tete
    # (tete du personnage debout : sommet a Y=5, voir README).
    parts.append({"name": "Backrest", "size": (4.4, 6.4, 0.6), "pos": (0.0, 5.0, 3.0),
                  "color_rgb": STONE})

    # Accoudoirs -- entre siege et dossier, hauteur confortable au-dessus
    # du siege (Y=3.0 au sommet).
    for x in (-2.6, 2.6):
        parts.append({"name": f"Armrest_{x}", "size": (0.8, 1.0, 3.2),
                      "pos": (x, 2.5, 0.9), "color_rgb": GOLD})

    # Coussin ou repose la couronne avant que le personnage ne la saisisse
    # -- position CALIBREE (voir calibrate.py) pour coincider avec le
    # point exact ou la main droite se pose au repos assis (Right Arm =
    # (0,0,55), torso -14) : main a (2.516, 3.048, -0.012).
    parts.append({"name": "CrownCushion", "size": (0.9, 0.3, 0.9),
                  "pos": (2.5, 2.93, 0.0), "color_rgb": GEM_RED})

    # Bande doree au sommet du dossier + fleurons.
    parts.append({"name": "BackrestTrim", "size": (4.6, 0.5, 0.8), "pos": (0.0, 8.0, 3.0),
                  "color_rgb": GOLD})
    for x in (-2.1, 0.0, 2.1):
        h = 0.9 if x == 0.0 else 0.6
        parts.append({"name": f"Finial_{x}", "size": (0.6, h, 0.6), "shape": SHAPE_BALL,
                      "pos": (x, 8.25 + h / 2.0, 3.0), "color_rgb": GOLD_LIGHT})

    return parts


def crown_points(n=5, radius=0.75, band_top_y=0.25, base_h=0.9, front_h=1.35,
                  front_axis_deg=180.0):
    """n pointes reparties autour d'un cercle de rayon `radius` dans le
    plan XZ (le crown est defini dans son PROPRE repere local, origine =
    centre vertical de la bande -- voir note de module). La pointe a
    front_axis_deg (def. 180 = -Z, "avant" du personnage) est la plus
    haute, celle en face (0 deg, +Z) la plus basse -- silhouette de
    couronne classique, pas symetrique partout."""
    pts = []
    for i in range(n):
        angle = math.radians(front_axis_deg + i * 360.0 / n)
        x, z = radius * math.sin(angle), radius * math.cos(angle)
        # la pointe la plus proche de l'avant est la plus haute, celle
        # la plus proche de l'arriere la plus basse, interpolation lineaire
        # sur cos(angle - avant) entre les deux.
        cos_front = math.cos(angle - math.radians(front_axis_deg))
        h = base_h + (front_h - base_h) * max(0.0, cos_front)
        pts.append((f"Point_{i}", x, z, h))
    return pts


def crown_parts():
    """Couronne dans son repere LOCAL (origine = centre de la bande, qui
    vient se poser au sommet de la tete a l'execution -- voir
    choreography.py / compute_crown_track.py pour le placement monde
    dynamique). Rayon de bande 0.75 stud : legerement plus large que
    l'empreinte de la tete du rig (Head = 1x1 stud en XZ, rayon ~0.7 en
    diagonale), pour reposer dessus comme un vrai couvre-chef plutot que
    de l'encastrer."""
    parts = []
    band_h = 0.4
    parts.append({"name": "Band", "size": (band_h, 1.5, 1.5), "shape": SHAPE_CYLINDER,
                  "pos": (0.0, 0.0, 0.0), "rot": _ROT_Z90, "color_rgb": GOLD})

    for name, x, z, h in crown_points():
        parts.append({"name": name, "size": (0.32, h, 0.32),
                      "pos": (x, band_h / 2.0 + h / 2.0, z), "color_rgb": GOLD_LIGHT})
        parts.append({"name": f"{name}_Gem", "size": (0.22, 0.22, 0.22), "shape": SHAPE_BALL,
                      "pos": (x, band_h / 2.0 + h + 0.05, z), "color_rgb": GEM_RED})

    return parts
