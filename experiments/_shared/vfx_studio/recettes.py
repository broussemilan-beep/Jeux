"""
RECETTES du studio VFX : un effet est une DONNÉE, jouée par le moteur
d'aperçu (lab/moteur.js), puis compilée vers Roblox (à venir).

Une recette = un dict JSON :
- "duree" (s), "graine" ; "palette" (2-3 couleurs + blanc, CARNET §4b.2) ;
- "projectile" (optionnel) : {de, a, t0, t1, hauteur, acceleration, visuel}.
  C'est l'objet qui voyage. Il DISPARAÎT à t1 (collision), et les couches
  ancrées sur « impact » prennent le relais ;
- "couches" : une liste dont chaque élément a un "type" :
  - "particules" = ParticleEmitter. Émission (emit, ou rate +
    duree_emission), puis lifetime, speed, spread, drag, accel, orientation,
    size, transparency, squash (NumberSequence [[t, v, enveloppe]]), color
    (ColorSequence [[t, "#hex"]]), light_emission, flipbook, forme, zoffset ;
  - "mesh" = MeshPart + texture qui DÉFILE. Champs : mesh, texture,
    defilement [u/s, v/s], echelle, transparency, color, orientation
    ("sol" / "coup" / "direction"), inclinaison, rotation_vitesse, bord
    (fresnel) ;
  - "trail" (suit une ancre) / "beam" (Bézier de -> a) : largeur,
    transparency le long du ruban, texture, vitesse_texture ;
- "ancre" : {"pos", "dir"} / "projectile" / "impact" ;
- "bloom" : {"intensite": courbe sur la durée, "seuil", "taille"} = BloomEffect ;
- "flashs" : flash d'écran ; "secousses" : directionnelles, à graine fixe ;
- "gels" : [[t, durée]] = TimeScale 0 sur les particules (hitstop).

Les chiffres de départ viennent des mesures : pack 100 Combat VFX, doc
officielle, robloxIA, refs (fiches/VFX.md, RELECTURE_REFS_VFX). Ensuite,
c'est l'ŒIL qui décide (CARNET §1.9).
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def impact_couches(ancre="impact", coup=(0, 0, -1), palette=("#fff4d6", "#ffb23e", "#ff5a1f"), echelle=1.0, t0=0.0):
    """Explosion d'impact en couches (registre « monde 3D ») :
    flash -> onde (dôme + anneau au sol) -> éclats -> feu cel -> croissants
    de vent -> fumée qui reste. Timings tirés des refs (Stagnant Rage, 449,
    aafdc91d) et du pack : flash 0,1 s, onde 0,25-0,45 s, éclats ~0,4 s,
    feu 0,3-0,6 s, vent 0,3 s, fumée 1-1,6 s."""
    blanc, chaud, fonce = palette
    s = echelle
    return [
        # 1. flash : étoile à 4 branches + cœur, 1-2 images
        {"type": "particules", "nom": "flash", "t0": t0, "ancre": ancre, "texture": "flash", "emit": 1,
         "lifetime": [0.07, 0.07], "size": [[0, 9 * s], [1, 12 * s]], "transparency": [[0, 0], [0.6, 0.2], [1, 1]],
         "color": blanc, "light_emission": 1, "rotation": [0, 360], "zoffset": 2},
        {"type": "particules", "nom": "etoile", "t0": t0, "ancre": ancre, "texture": "etoile4", "emit": 1,
         "lifetime": [0.16, 0.16], "size": [[0, 14 * s], [1, 4 * s]], "transparency": [[0, 0], [1, 1]],
         "color": blanc, "light_emission": 1, "zoffset": 2.5},
        # 2. onde de choc : dôme qui grossit et devient transparent (bord fresnel)
        {"type": "mesh", "nom": "dome", "t0": t0 + 0.01, "duree": 0.32, "ancre": ancre, "mesh": "dome",
         "texture": "bruit_energie", "defilement": [0.8, 0.0], "echelle": [[0, 0.6 * s], [0.35, 4.5 * s], [1, 6.5 * s]],
         "transparency": [[0, 0.05], [0.5, 0.45], [1, 1]], "color": blanc, "bord": 1.0, "light_emission": 1},
        {"type": "mesh", "nom": "anneau_sol", "t0": t0, "duree": 0.42, "ancre": ancre, "mesh": "anneau_plat",
         "texture": "ruban", "echelle": [[0, 0.8 * s], [0.4, 6 * s], [1, 9 * s]], "transparency": [[0, 0], [0.6, 0.5], [1, 1]],
         "color": blanc, "decalage": [0, 0.05, 0], "light_emission": 1},
        # 3. éclats acérés, orientés par leur vitesse (VelocityParallel)
        {"type": "particules", "nom": "eclats", "t0": t0, "ancre": ancre, "texture": "eclat", "emit": 28,
         "lifetime": [0.22, 0.45], "speed": [40 * s, 75 * s], "spread": [180, 180], "drag": 7,
         "orientation": "VelocityParallel", "size": [[0, 2.2 * s, 0.6 * s], [1, 0.2 * s]],
         "transparency": [[0, 0], [0.7, 0.1], [1, 1]], "color": [[0, blanc], [1, chaud]], "light_emission": 1},
        # 4. feu cel peint (flipbook OneShot), multidirectionnel
        {"type": "particules", "nom": "feu", "t0": t0 + 0.01, "ancre": ancre, "texture": "feu_cel", "emit": 14,
         "flipbook": {"grille": 4, "mode": "OneShot"}, "lifetime": [0.35, 0.6], "speed": [16 * s, 28 * s],
         "spread": [180, 180], "drag": 6, "accel": [0, 4, 0], "size": [[0, 3.2 * s, 0.8 * s], [1, 5.5 * s, 1 * s]],
         "transparency": [[0, 0], [1, 0]], "color": "#ffffff", "light_emission": 0, "rotation": [0, 360],
         "rotspeed": [-60, 60], "forme": {"sphere": 0.6 * s}},
        # 5. AIR : croissants de vent qui tournent autour de l'impact
        {"type": "mesh", "nom": "vent_1", "t0": t0 + 0.02, "duree": 0.3, "ancre": ancre, "mesh": "croissant_3d",
         "texture": "bruit_energie", "defilement": [2.2, 0], "echelle": [[0, 2.2 * s], [1, 6.5 * s]],
         "transparency": [[0, 0.1], [0.7, 0.4], [1, 1]], "color": blanc, "rotation_vitesse": 520, "rotation": 0,
         "inclinaison": [18, 0, 8], "decalage": [0, 0.6 * s, 0], "light_emission": 1},
        {"type": "mesh", "nom": "vent_2", "t0": t0 + 0.05, "duree": 0.3, "ancre": ancre, "mesh": "croissant_3d",
         "texture": "bruit_energie", "defilement": [-2.0, 0], "echelle": [[0, 2.8 * s], [1, 7.5 * s]],
         "transparency": [[0, 0.2], [0.7, 0.5], [1, 1]], "color": blanc, "rotation_vitesse": -460, "rotation": 140,
         "inclinaison": [-24, 0, -12], "decalage": [0, 1.2 * s, 0], "light_emission": 1},
        {"type": "mesh", "nom": "vague", "t0": t0 + 0.02, "duree": 0.38, "ancre": ancre, "mesh": "vague_sol", "texture": "ruban",
         "echelle": [[0, [1.5 * s, 1.4 * s, 1.5 * s]], [1, [8 * s, 0.2, 8 * s]]],
         "transparency": [[0, 0.15], [1, 1]], "color": blanc, "light_emission": 1},
        # 6. fumée cel 2 tons qui reste (Serious Punch : la fumée dit la conséquence)
        {"type": "particules", "nom": "fumee", "t0": t0 + 0.04, "ancre": ancre, "texture": "fumee_cel", "emit": 12,
         "flipbook": {"grille": 4, "mode": "OneShot"}, "lifetime": [1.0, 1.6], "speed": [7 * s, 13 * s],
         "spread": [180, 55], "drag": 2.2, "accel": [0, 2.5, 0], "size": [[0, 4 * s, 1 * s], [1, 8 * s, 1.5 * s]],
         "transparency": [[0, 0], [1, 0]], "color": [[0, "#ffffff"], [1, "#b9b4ae"]], "light_emission": 0,
         "rotation": [0, 360], "forme": {"sphere": 1.0 * s}},
    ]


def orbe_impact():
    """Le scénario décrit par Milan (2026-09-25) : APPARITION rapide ->
    PROJECTION -> COLLISION. Le projectile disparaît, et une onde de choc (mesh
    qui grossit et devient transparent) + une explosion de particules
    multidirectionnelle prennent sa place."""
    t1 = 0.8
    pal = ("#fff4d6", "#ffb23e", "#ff5a1f")
    rec = {
        "nom": "orbe_impact", "titre": "Orbe : apparition, projection, collision",
        "duree": 2.6, "graine": 7, "palette": list(pal),
        "projectile": {"de": [0, 3.2, 7], "a": [0, 1.0, -7], "t0": 0.3, "t1": t1, "hauteur": 0.8, "acceleration": True,
                       # cœur plein : la 1re version (filaments seuls) était presque invisible
                       "visuel": {"mesh": "sphere", "echelle": 0.75, "color": pal[0], "brightness": 1.2,
                                  "transparency": 0, "light_emission": 1}},
        "couches": [
            # APPARITION (0 -> 0,3 s) : l'orbe se forme au point de départ
            {"type": "mesh", "nom": "naissance", "t0": 0.0, "duree": 0.3, "ancre": {"pos": [0, 3.2, 7]}, "mesh": "sphere",
             "texture": "bruit_energie", "defilement": [1.6, 0], "echelle": [[0, 0], [0.6, 1.2], [1, 0.9]],
             "color": pal[1], "brightness": 1.8, "bord": 0.6, "transparency": 0, "light_emission": 1},
            {"type": "particules", "nom": "naissance_etoile", "t0": 0.0, "ancre": {"pos": [0, 3.2, 7]}, "texture": "etoile4",
             "emit": 1, "lifetime": [0.3, 0.3], "size": [[0, 0], [0.4, 6], [1, 0]], "color": pal[0], "light_emission": 1},
            {"type": "particules", "nom": "aspiration", "t0": 0.0, "ancre": {"pos": [0, 3.2, 7]}, "texture": "eclat",
             "rate": 90, "duree_emission": 0.28, "lifetime": [0.18, 0.25], "speed": [-26, -18], "spread": [180, 180],
             "orientation": "VelocityParallel", "size": [[0, 1.2], [1, 0.3]], "color": pal[0], "light_emission": 1,
             "forme": {"sphere": 4.0}},
            # PROJECTION : coquille d'énergie qui tourne + halo autour du cœur
            {"type": "mesh", "nom": "coquille", "t0": 0.3, "duree": t1 - 0.3, "ancre": "projectile", "mesh": "sphere",
             "texture": "bruit_energie", "defilement": [2.4, 0], "echelle": 1.35, "color": pal[1], "brightness": 1.6,
             "bord": 0.8, "transparency": 0, "light_emission": 1},
            {"type": "particules", "nom": "halo_orbe", "t0": 0.3, "ancre": "projectile", "texture": "halo", "rate": 60,
             "duree_emission": t1 - 0.3, "lifetime": [0.06, 0.06], "size": [[0, 5.5], [1, 5.0]], "transparency": [[0, 0.35], [1, 0.6]],
             "color": pal[1], "light_emission": 1, "bloque_a_l_ancre": True, "gel": False},
            # traînée d'énergie + étincelles semées derrière
            {"type": "trail", "nom": "trainee", "t0": 0.3, "t1": t1, "ancre": "projectile", "lifetime": 0.22,
             "t1_ancre": t1, "largeur": [[0, 1.6], [1, 0]], "texture": "ruban", "segments": 24,
             "transparency": [[0, 0], [1, 1]], "color": [[0, pal[0]], [1, pal[2]]], "light_emission": 1},
            {"type": "particules", "nom": "semis", "t0": 0.3, "ancre": "projectile", "texture": "eclat", "rate": 90,   # 120 dépassait le plafond mobile (critique.py)
             "duree_emission": t1 - 0.3, "lifetime": [0.15, 0.3], "speed": [2, 6], "spread": [180, 180], "drag": 4,
             "orientation": "FacingCamera", "size": [[0, 0.7], [1, 0]], "color": pal[1], "light_emission": 1,
             "bloque_a_l_ancre": False},
        ] + impact_couches("impact", palette=pal, echelle=1.0, t0=t1),
        "bloom": {"intensite": [[0, 0.5], [t1 / 2.6, 0.7], [(t1 + 0.02) / 2.6, 1.8], [(t1 + 0.35) / 2.6, 0.7], [1, 0.5]],
                  "seuil": 0.72, "taille": 2.2},
        "flashs": [{"t0": t1, "duree": 0.035, "couleur": "#fff6e0", "transparency": [[0, 0.1], [1, 0.9]]}],
        "secousses": [{"t0": t1, "duree": 0.35, "amplitude": 0.55, "direction": [0, -1, -0.6], "graine": 3}],
        "gels": [[t1, 0.06]],
        # SON (sons.py) : le souffle est coupé net 60 ms avant la collision,
        # le vide avant l'impact mesuré dans les refs (critique_son)
        "sons": [
            {"son": "naissance_orbe", "t0": 0.0, "volume": 0.45},
            {"son": "aspiration", "t0": 0.0, "volume": 0.55},
            {"son": "souffle_projectile", "t0": 0.3, "volume": 0.75},
            {"son": "impact_lourd", "t0": t1, "volume": 0.85, "impact": True},
            {"son": "grondement", "t0": t1 + 0.01, "volume": 0.5},
            {"son": "vent_arc", "t0": t1 + 0.03, "volume": 0.35},
        ],
        "cameras": {"large": {"oeil": [15, 6, 9], "cible": [0, 2, -2], "fov": 50},
                    "jeu": {"oeil": [1.75, 5.2, 12], "cible": [1.75, 3.2, -2], "fov": 70},
                    "impact": {"oeil": [9, 3.2, -1.5], "cible": [0, 1.8, -7], "fov": 55}},
    }
    return rec


def impact_m1():
    """Tier 1 (coup de base), lisible en caméra de jeu, même petit
    (CARNET §4b.4, ref 449) : étoile blanche de 2 images, anneau fin qui
    grandit en 3-4 images, petit croissant sur la trajectoire."""
    anc = {"pos": [0, 3.1, -2.2], "dir": [0, 0, -1], "coup": [0, 0, -1]}
    return {
        "nom": "impact_m1", "titre": "Impact M1 (tier 1)", "duree": 0.8, "graine": 3, "palette": ["#ffffff", "#9fd8ff"],
        "couches": [
            {"type": "particules", "nom": "etoile", "t0": 0.2, "ancre": anc, "texture": "etoile4", "emit": 1,
             "lifetime": [0.05, 0.05], "size": [[0, 3.2], [1, 2.2]], "color": "#ffffff", "light_emission": 1, "zoffset": 1},
            {"type": "particules", "nom": "anneau", "t0": 0.2, "ancre": anc, "texture": "anneau", "emit": 1,
             "lifetime": [0.12, 0.12], "size": [[0, 0.6], [1, 4.2]], "transparency": [[0, 0], [1, 1]],
             "color": "#ffffff", "light_emission": 1, "orientation": "FacingCamera"},
            {"type": "particules", "nom": "croissant", "t0": 0.19, "ancre": anc, "texture": "croissant", "emit": 1,
             "lifetime": [0.09, 0.09], "size": [[0, 2.4], [1, 3.0]], "transparency": [[0, 0.1], [1, 1]],
             "color": "#ffffff", "light_emission": 1, "rotation": [-100, -80]},
            {"type": "particules", "nom": "eclats", "t0": 0.2, "ancre": anc, "texture": "eclat", "emit": 6,
             "lifetime": [0.1, 0.18], "speed": [22, 34], "spread": [60, 60], "drag": 8, "orientation": "VelocityParallel",
             "size": [[0, 0.9], [1, 0.1]], "color": "#ffffff", "light_emission": 1},
        ],
        "bloom": {"intensite": 0.7, "seuil": 0.75, "taille": 2},
        # le bras qui part puis le contact : 30 ms de vide (tier 1, court)
        "sons": [
            {"son": "fouet_m1", "t0": 0.07, "volume": 0.5},
            {"son": "frappe_m1", "t0": 0.2, "volume": 0.9, "impact": True, "vide": 0.025},
        ],
        "cameras": {"jeu": {"oeil": [1.75, 4.8, 8.5], "cible": [1.75, 3.2, -4], "fov": 70},
                    "large": {"oeil": [7, 4, 3], "cible": [0, 3, -2], "fov": 50}},
    }


RECETTES = {"orbe_impact": orbe_impact, "impact_m1": impact_m1}


def toutes():
    return {k: f() for k, f in RECETTES.items()}


if __name__ == "__main__":
    json.dump(toutes(), sys.stdout, indent=1, ensure_ascii=False)
