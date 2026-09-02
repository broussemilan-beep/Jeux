"""
Geometrie STATIQUE du trone et de la couronne, comme suite de Parts
Roblox (voir export_model.py), dans le MEME repere que le personnage R6
(studs, -Z = avant, sol = Y 0, personnage debout : pieds a Y=0, hanches/
HumanoidRootPart a Y=3 -- valeurs lues sur rig/r6_rig.json, pas devinees,
voir le calcul dans README.md).

Le trone repose desormais sur une estrade SURELEVEE (PLATFORM_H studs
au-dessus du sol reel), a laquelle mene un escalier (`staircase_parts`)
-- ajoute pour la montee "sombre mais fiere" avant l'assise (voir
choreography.full_scene). Toutes les coordonnees du trone ci-dessous
restent ecrites comme avant (assise du siege a +2.0 studs au-dessus de
SA PROPRE estrade -- hanche a Y=3 moins la moitie de la hauteur du
torse) puis DECALEES de +PLATFORM_H par `_lift()` avant d'etre
retournees : un seul nombre a changer si la hauteur de l'estrade change,
jamais besoin de retoucher chaque Part a la main.

Chaque Part porte deux champs de rendu DISTINCTS et INDEPENDANTS :
  - "mat" : categorie utilisee par le LECTEUR HTML pour choisir son
    modele d'eclairage stylise (stone/gold/gem/royal, voir
    dump_scene_data.py -> throne_crown_viewer.html).
  - "material" : le vrai `Enum.Material` de Roblox (voir
    export_model.MATERIAL_BY_NAME), ecrit dans le .rbxmx livre. Les deux
    ne coincident pas toujours (ex. CrownCushion : "mat"="gem" pour la
    teinte chaude du lecteur, "material"="Fabric" cote Roblox, un coussin
    n'est pas une gemme) -- ne pas les confondre en modifiant l'un en
    pensant changer l'autre.
"""
import math

from export_model import SHAPE_BLOCK, SHAPE_CYLINDER, SHAPE_BALL

STONE = (110, 108, 116)
STONE_DARK = (70, 68, 74)
GOLD = (196, 160, 60)
GOLD_LIGHT = (224, 190, 90)
GEM_RED = (150, 25, 30)

_ROT_Z90 = [[0.0, -1.0, 0.0], [1.0, 0.0, 0.0], [0.0, 0.0, 1.0]]  # local X -> monde Y

PLATFORM_H = 2.0     # hauteur de l'estrade au-dessus du sol reel (Y=0)
STAIR_N = 4           # nombre de marches
STAIR_RISER = PLATFORM_H / STAIR_N    # 0.5 stud/marche
STAIR_TREAD = 1.2     # profondeur d'une marche
STAIR_WIDTH = 6.0

# Bord avant de l'estrade (cote escalier), AVANT decalage +PLATFORM_H --
# c'est aussi le point d'arrivee de la derniere marche (voir
# choreography.climb_stairs, qui doit rester coherent avec ce nombre).
_DAIS_FRONT_Z = 1.4 - 5.5 / 2.0   # -1.35


def _lift(parts, dy=PLATFORM_H):
    return [{**p, "pos": (p["pos"][0], p["pos"][1] + dy, p["pos"][2])} for p in parts]


def staircase_parts():
    """Escalier menant du sol (Y=0) au dessus de l'estrade (Y=PLATFORM_H).
    Chaque marche est une boite pleine du sol jusqu'a SON propre sommet
    (pas juste une marche flottante) -- silhouette d'escalier plein,
    pas de marches en porte-a-faux. La marche la plus proche du trone
    (la plus haute) affleure exactement le bord avant de l'estrade."""
    parts = []
    for k in range(1, STAIR_N + 1):
        h = k * STAIR_RISER
        z_near = _DAIS_FRONT_Z - (STAIR_N - k) * STAIR_TREAD
        z_far = z_near - STAIR_TREAD
        z_center = (z_near + z_far) / 2.0
        # Ton alterne (clair/fonce) par marche : a plat, une teinte pierre
        # unique rendait l'escalier illisible en vue 3/4 (les aretes ne
        # se detachaient pas assez dans un rendu sombre) -- trouve par
        # capture d'ecran reelle, pas suppose.
        tone = STONE if k % 2 == 0 else STONE_DARK
        # Meme alternance sur le vrai Material Roblox que sur la teinte :
        # Slate/Cobblestone plutot que deux fois le meme materiau, pour
        # que l'alternance se voie aussi hors du lecteur HTML (import
        # reel dans Roblox Studio).
        material = "Slate" if k % 2 == 0 else "Cobblestone"
        parts.append({"name": f"Step_{k}", "size": (STAIR_WIDTH, h, STAIR_TREAD),
                      "pos": (0.0, h / 2.0, z_center), "color_rgb": tone, "mat": "stone",
                      "material": material})
    return parts


def throne_parts():
    parts = []

    # Estrade -- dessus a Y=0 AVANT decalage (devient PLATFORM_H apres
    # `_lift`), exactement au niveau du sommet de la derniere marche.
    parts.append({"name": "Dais", "size": (7.0, 0.6, 5.5), "pos": (0.0, -0.3, 1.4),
                  "color_rgb": STONE_DARK, "mat": "stone", "material": "Slate"})

    # 4 pieds sous le siege, du dais (Y=0) jusqu'au dessous du siege (Y=1.7).
    for x in (-1.9, 1.9):
        for z in (-0.4, 2.1):
            parts.append({"name": f"Leg_{x}_{z}", "size": (0.5, 1.7, 0.5),
                          "pos": (x, 0.85, z), "color_rgb": STONE_DARK, "mat": "stone",
                          "material": "Slate"})

    # Siege -- dessus a Y=2.0 (hanche assise moins demi-hauteur du torse).
    # Marbre poli plutot qu'ardoise brute : c'est la surface que le
    # personnage touche en s'asseyant, plus "premium" que le reste de la
    # pierre structurelle.
    parts.append({"name": "Seat", "size": (4.4, 0.6, 3.6), "pos": (0.0, 1.7, 0.9),
                  "color_rgb": STONE, "mat": "stone", "material": "Marble"})

    # Dossier -- derriere le siege (+Z), monte bien au-dessus de la tete
    # (tete du personnage debout : sommet a Y=5, voir README).
    parts.append({"name": "Backrest", "size": (4.4, 6.4, 0.6), "pos": (0.0, 5.0, 3.0),
                  "color_rgb": STONE, "mat": "stone", "material": "Slate"})

    # Accoudoirs -- entre siege et dossier, hauteur confortable au-dessus
    # du siege (Y=3.0 au sommet).
    for x in (-2.6, 2.6):
        parts.append({"name": f"Armrest_{x}", "size": (0.8, 1.0, 3.2),
                      "pos": (x, 2.5, 0.9), "color_rgb": GOLD, "mat": "gold",
                      "material": "Metal"})

    # Coussin ou repose la couronne avant que le personnage ne la saisisse
    # -- position CALIBREE (voir calibrate.py) pour coincider avec le
    # point exact ou la main droite se pose au repos assis (Right Arm =
    # (0,0,55), torso -14) : main a (2.516, 3.048, -0.012), AVANT
    # decalage d'estrade (voir cushion_top_pos() pour la version monde).
    # "mat"="gem" pour la teinte chaude du lecteur, mais "material"=
    # "Fabric" cote Roblox -- c'est un coussin, pas une gemme (voir note
    # de module sur la distinction mat/material).
    parts.append({"name": "CrownCushion", "size": (0.9, 0.3, 0.9),
                  "pos": (2.5, 2.93, 0.0), "color_rgb": GEM_RED, "mat": "gem",
                  "material": "Fabric"})

    # Bande doree au sommet du dossier + fleurons.
    parts.append({"name": "BackrestTrim", "size": (4.6, 0.5, 0.8), "pos": (0.0, 8.0, 3.0),
                  "color_rgb": GOLD, "mat": "gold", "material": "Metal"})
    for x in (-2.1, 0.0, 2.1):
        h = 0.9 if x == 0.0 else 0.6
        parts.append({"name": f"Finial_{x}", "size": (0.6, h, 0.6), "shape": SHAPE_BALL,
                      "pos": (x, 8.25 + h / 2.0, 3.0), "color_rgb": GOLD_LIGHT, "mat": "gold",
                      "material": "Metal"})

    return _lift(parts)


def cushion_top_pos():
    """Position monde (post-estrade) du dessus du coussin -- calculee
    depuis throne_parts() plutot que redupliquee en constante a part,
    pour ne jamais pouvoir diverger du fichier reellement exporte."""
    spec = next(p for p in throne_parts() if p["name"] == "CrownCushion")
    x, y, z = spec["pos"]
    return (x, y + spec["size"][1] / 2.0, z)


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
                  "pos": (0.0, 0.0, 0.0), "rot": _ROT_Z90, "color_rgb": GOLD, "mat": "gold",
                  "material": "Metal"})

    for name, x, z, h in crown_points():
        parts.append({"name": name, "size": (0.32, h, 0.32),
                      "pos": (x, band_h / 2.0 + h / 2.0, z), "color_rgb": GOLD_LIGHT, "mat": "gold",
                      "material": "Metal"})
        # Neon plutot que Glass : "la couronne brille" doit rester vrai
        # une fois importe dans Roblox, pas seulement dans le lecteur
        # HTML -- Neon EMET une lueur (pas besoin de PointLight separe),
        # c'est le materiau le plus proche d'un "ca brille vraiment" que
        # le moteur Roblox propose nativement.
        parts.append({"name": f"{name}_Gem", "size": (0.22, 0.22, 0.22), "shape": SHAPE_BALL,
                      "pos": (x, band_h / 2.0 + h + 0.05, z), "color_rgb": GEM_RED, "mat": "gem",
                      "material": "Neon"})

    return parts
