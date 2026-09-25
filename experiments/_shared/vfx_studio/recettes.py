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


def impact_couches(ancre="impact", coup=(0, 0, -1), palette=("#fff4d6", "#ffb23e", "#ff5a1f"), echelle=1.0, t0=0.0, sol=True):
    """Explosion d'impact en couches (registre « monde 3D ») :
    flash -> onde (dôme + anneau au sol) -> éclats -> feu cel -> croissants
    de vent -> fumée qui reste. Timings tirés des refs (Stagnant Rage, 449,
    aafdc91d) et du pack : flash 0,1 s, onde 0,25-0,45 s, éclats ~0,4 s,
    feu 0,3-0,6 s, vent 0,3 s, fumée 1-1,6 s."""
    blanc, chaud, fonce = palette
    s = echelle
    couches = [
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
    if sol:
        # 7. DÉBRIS (Stagnant Rage : des blocs de sol qui volent partout ;
        #    écart n°1 de l'auto-évaluation) : blocs peints qui jaillissent en
        #    cône, retombent (gravité) en tournoyant, + gravillons plus fins
        roc = {"type": "particules", "texture": "roches_cel", "ancre": ancre, "light_emission": 0, "t0": t0,
               "flipbook": {"grille": 2, "mode": "Loop", "fps": 1, "depart_aleatoire": True},
               "rotation": [0, 360], "transparency": [[0, 0], [0.85, 0], [1, 1]], "color": "#ffffff"}
        couches += [
            dict(roc, nom="debris", emit=16, lifetime=[0.9, 1.4], speed=[24 * s, 44 * s], spread=[38, 38], drag=0.5,
                 accel=[0, -62 * s, 0], size=[[0, 1.2 * s], [1, 1.0 * s]], rotspeed=[-420, 420]),
            dict(roc, nom="gravillons", emit=26, lifetime=[0.6, 1.0], speed=[16 * s, 34 * s], spread=[65, 65], drag=0.8,
                 accel=[0, -55 * s, 0], size=[[0, 0.42 * s], [1, 0.36 * s]], rotspeed=[-600, 600]),
        ]
    if not sol:
        # EN L'AIR : pas d'anneau ni de vague au sol ; le dôme devient une
        # coquille orientée dans le sens du coup
        couches = [c for c in couches if c["nom"] not in ("anneau_sol", "vague")]
        for c in couches:
            if c["nom"] in ("dome", "vent_1", "vent_2"):
                c["orientation"] = "coup"
    return couches


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


# ============================================================ POING DU DRAGON
# Briques paramétrées, appelées par r6_poing_dragon/scripts/staging.py avec
# les positions de la scène (repère de l'attaquant au lancement, -Z devant).
# Palette du Dragon : or + or profond + blanc chaud (CARNET §4b.2).
DRAGON = ("#fff6dc", "#ffc53d", "#ff8a1f")


def impact_palier(pos, coup, tier=1, palette=DRAGON, t0=0.0, echelle=1.0, hauteur=1.0):
    """Impact de la rafale, proportionnel au coup (CARNET §4b.4, hiérarchie
    v6) : tier 1 = étoile 2 images + anneau fin + petit croissant + éclats ;
    tier 2 = + dôme court, croissant de vent, plus d'éclats. Rend (couches,
    sons) ; les temps sont relatifs au début de la recette."""
    blanc, chaud, _f = palette
    # ZOffset (Roblox : décalage vers la caméra, en studs) : en caméra de jeu,
    # derrière l'épaule, le contact est souvent CACHÉ par le corps de
    # l'attaquant (vu à f40, 1er essai à 1) ; l'éclat doit passer devant
    anc = {"pos": list(pos), "dir": list(coup), "coup": list(coup)}
    s = echelle
    c = [
        {"type": "particules", "nom": "etoile", "t0": t0, "ancre": anc, "texture": "etoile4", "emit": 1,
         "lifetime": [2 / 60, 2 / 60] if tier == 1 else [0.08, 0.08], "size": [[0, 3.4 * s], [1, 2.4 * s]], "color": "#ffffff",
         "light_emission": 1, "zoffset": 2.5},
        {"type": "particules", "nom": "anneau", "t0": t0, "ancre": anc, "texture": "anneau", "emit": 1,
         "lifetime": [0.12, 0.12], "size": [[0, 0.6 * s], [1, 4.6 * s]], "transparency": [[0, 0], [1, 1]],
         "color": blanc, "light_emission": 1, "zoffset": 2},
        {"type": "particules", "nom": "croissant", "t0": max(0.0, t0 - 1 / 60), "ancre": anc, "texture": "croissant",
         "emit": 1, "lifetime": [0.09, 0.09], "size": [[0, 2.6 * s], [1, 3.2 * s]], "transparency": [[0, 0.1], [1, 1]],
         "color": "#ffffff", "light_emission": 1, "rotation": [-100, -80], "zoffset": 2},
        {"type": "particules", "nom": "eclats", "t0": t0, "ancre": anc, "texture": "eclat", "emit": 6 if tier == 1 else 14,
         "lifetime": [0.1, 0.2], "speed": [24 * s, 38 * s], "spread": [55, 55], "drag": 8, "orientation": "VelocityParallel",
         "size": [[0, 1.0 * s], [1, 0.1]], "color": [[0, "#ffffff"], [1, chaud]], "light_emission": 1},
    ]
    # `hauteur` varie d'un coup à l'autre : le même son rejoué à l'identique
    # fait « mitraillette »
    sons = [{"son": "fouet_m1", "t0": round(max(0.0, t0 - 0.13), 4), "volume": 0.45, "hauteur": hauteur},
            {"son": "frappe_m1", "t0": t0, "volume": 0.85, "impact": True, "vide": 0.025, "hauteur": hauteur}]
    if tier >= 2:
        c += [
            {"type": "mesh", "nom": "dome", "t0": t0, "duree": 0.2, "ancre": anc, "mesh": "dome", "orientation": "coup",
             "texture": "bruit_energie", "defilement": [1.2, 0], "echelle": [[0, 0.4 * s], [0.4, 1.8 * s], [1, 2.4 * s]],
             "transparency": [[0, 0.1], [0.5, 0.5], [1, 1]], "color": blanc, "bord": 1.0, "light_emission": 1},
            {"type": "mesh", "nom": "vent", "t0": t0 + 0.01, "duree": 0.22, "ancre": anc, "mesh": "croissant_3d",
             "orientation": "coup", "texture": "bruit_energie", "defilement": [2.2, 0],
             "echelle": [[0, 1.2 * s], [1, 3.6 * s]], "transparency": [[0, 0.1], [0.7, 0.4], [1, 1]], "color": blanc,
             "rotation_vitesse": 480, "light_emission": 1},
        ]
        sons.append({"son": "impact_lourd", "t0": t0, "volume": 0.35, "hauteur": 1.25})
    return c, sons


def sillage(chemin, palette=DRAGON, largeur=1.4, fumee=False, t_fin=None, lignes=True):
    """Le VFX d'AIR (CARNET §4b.3 : l'air vend la vitesse) : un ruban qui suit
    un chemin (poing qui plonge, victime projetée), des lignes de vitesse
    semées DERRIÈRE (vitesse négative le long du mouvement), et en option de
    la fumée qui reste en l'air."""
    blanc, chaud, fonce = palette
    t0, t1 = chemin[0][0], t_fin if t_fin is not None else chemin[-1][0]
    anc = {"chemin": chemin}
    c = [{"type": "trail", "nom": "sillage", "t0": t0, "t1": t1, "ancre": anc, "lifetime": 0.3,
          "largeur": [[0, largeur], [1, 0]], "texture": "ruban", "transparency": [[0, 0], [1, 1]],
          "color": [[0, blanc], [1, chaud]], "light_emission": 1}]
    if lignes:
        # « éclat » étiré (Squash) : ligne_vitesse est dessinée à l'horizontale,
        # et VelocityParallel aligne le HAUT de la texture sur la vitesse (1er
        # essai : des tirets en travers du mouvement)
        c.append({"type": "particules", "nom": "lignes", "t0": t0, "ancre": anc, "texture": "eclat",
                  "rate": 70, "duree_emission": t1 - t0, "lifetime": [0.12, 0.2], "speed": [-30, -18],
                  "spread": [12, 12], "orientation": "VelocityParallel", "size": [[0, 1.6], [1, 0.3]],
                  "squash": [[0, 1.3], [1, 1.3]],
                  "transparency": [[0, 0.1], [1, 1]], "color": "#ffffff", "light_emission": 1,
                  "forme": {"sphere": 0.9}})
    if fumee:
        c.append({"type": "particules", "nom": "fumee_sillage", "t0": t0, "ancre": anc, "texture": "fumee_cel",
                  "rate": 28, "duree_emission": t1 - t0, "flipbook": {"grille": 4, "mode": "OneShot"},
                  "lifetime": [0.6, 1.0], "speed": [0.5, 2], "spread": [180, 180], "drag": 2,
                  "size": [[0, 1.8, 0.4], [1, 3.6, 0.6]], "transparency": [[0, 0], [1, 0]],
                  "color": [[0, "#ffffff"], [1, "#b9b4ae"]], "light_emission": 0, "rotation": [0, 360]})
    return c


VERT_OFA = "#6dff8a"   # vert One For All (Izuku)


def serpent(images, t0, duree, largeur=None, naissance=0.25, mort=None, tete=True, vitesse=1.5, taille_tete=(4.4, 2.2),
            couleur="#ffffff", modele="dragon", echelle=0.7):
    """Corps de DRAGON (fiches/AURA_DRAGON.md) : `images` = [[t, [[x,y,z]...]]]
    (t en temps de RECETTE, pas relatif à t0 : piège de la v10a)
    (tête en premier), temps relatifs à la recette. Naît de la tête vers la
    queue en `naissance` (fraction de la durée) ; `mort` = (début, "tete" |
    "queue") : se dissout depuis ce bout-là."""
    tete_v = [[0, 0], [1, 0]]
    queue_v = [[0, 0.02], [naissance, 1], [1, 1]]
    if mort:
        debut, bout = mort
        if bout == "tete":
            tete_v = [[0, 0], [debut, 0], [1, 1]]
        else:
            queue_v = [[0, 0.02], [min(naissance, debut * 0.99), 1], [debut, 1], [1, 0]]
    L = {"type": "serpent", "nom": "dragon", "t0": t0, "duree": duree, "images": images, "texture": "dragon_ecailles",
         "largeur": largeur or [[0, 1.3], [0.08, 1.5], [0.5, 1.1], [0.85, 0.6], [1, 0.1]], "vitesse_texture": vitesse,
         "tete_visible": tete_v, "queue_visible": queue_v, "light_emission": 0, "color": couleur}
    if modele:
        # DRAGON 3D riggé (modeles/dragon.py) ; le ruban + la carte restent le
        # repli si le modèle manque (Roblox : FBX pas encore importé)
        L["modele"], L["echelle"] = modele, echelle
        # abscisse (0-1) de chaque os le long du corps : Tete puis la colonne
        d = json.load(open(os.path.join(HERE, "modeles", f"{modele}.json")))
        L["os_s"] = [0.0] + [round(x / d["longueur"], 4) for x in d["os_x"]]
    if tete:
        L["tete"] = {"texture": "dragon_tete", "texture_miroir": "dragon_tete_miroir", "taille": list(taille_tete), "cou": 0.1}
    return L


def _interp(seq_, a):
    """Valeur d'une séquence [[t, v], ...] (t dans 0-1) en a."""
    if a <= seq_[0][0]:
        return seq_[0][1]
    for (t0, v0), (t1, v1) in zip(seq_, seq_[1:]):
        if a <= t1:
            return v0 + (v1 - v0) * ((a - t0) / (t1 - t0) if t1 > t0 else 1.0)
    return seq_[-1][1]


def _point_abscisse(pts, s):
    """Point à l'abscisse curviligne s (0 = tête, 1 = queue) d'une polyligne."""
    import numpy as np
    P = np.asarray(pts, float)
    seg = np.linalg.norm(np.diff(P, axis=0), axis=1)
    cum = np.concatenate([[0.0], np.cumsum(seg)])
    x = s * cum[-1]
    i = int(min(len(seg) - 1, np.searchsorted(cum, x, side="right") - 1))
    u = (x - cum[i]) / seg[i] if seg[i] > 1e-9 else 0.0
    return P[i] + (P[i + 1] - P[i]) * u


def flammes_corps(L, n=7, rate=16, palette=("#fff4c8", "#ffb02e", "#ff4d12"), halo=True):
    """Feu qui COULE le long du dragon (fiches/AURA_DRAGON.md §0 bis ; le
    GIF 7a2b4ae8 : le dragon sort d'un tourbillon de feu et en reste nimbé).
    Un modèle 3D nu se lit comme une statue dorée ; les refs le montrent
    ENVELOPPÉ d'énergie. `n` émetteurs, chacun sur un CHEMIN = le point
    d'abscisse s_k du corps à chaque image : c'est de la donnée, les trois
    moteurs le jouent sans code nouveau (Roblox : n Attachments déplacés à
    chaque image, les particules gardent leur vitesse de naissance -> les
    flammes TRAÎNENT derrière le corps en mouvement). Chaque émetteur ne
    brûle que pendant que son bout de corps est visible (naissance, mort)."""
    images, t0, duree = L["images"], L["t0"], L["duree"]
    k_ech = L.get("echelle", 0.7)
    blanc, chaud, fonce = palette
    out = []
    for k in range(n):
        s = 0.06 + 0.84 * k / max(1, n - 1)
        chemin, vis = [], []
        for t, pts in images:
            a = (t - t0) / duree
            s0 = _interp(L.get("tete_visible", [[0, 0], [1, 0]]), a)
            s1 = _interp(L.get("queue_visible", [[0, 1], [1, 1]]), a)
            p = _point_abscisse(pts, s)
            chemin.append([round(t, 4)] + [round(float(v), 3) for v in p])
            if s0 <= s <= s1:
                vis.append(t)
        if len(vis) < 2:
            continue
        ta, tb = max(t0, vis[0]), min(t0 + duree, vis[-1])
        taille = 2.6 * k_ech * (1.15 - 0.6 * s)          # plus gros au cou, fin vers la queue
        out.append({"type": "particules", "nom": f"flamme_corps_{k}", "t0": round(ta, 4),
                    "duree_emission": round(tb - ta, 4), "rate": rate, "ancre": {"chemin": chemin},
                    "texture": "flamme_aura", "flipbook": {"grille": 4, "mode": "Loop", "fps": 24, "depart_aleatoire": True},
                    "lifetime": [0.28, 0.5], "speed": [0.6 * k_ech, 2.2 * k_ech], "spread": [180, 180], "drag": 2.5,
                    "accel": [0, 5 * k_ech, 0], "size": [[0, 0.5 * taille], [0.35, taille], [1, 0.25 * taille]],
                    "transparency": [[0, 0.35], [0.25, 0.05], [1, 1]],
                    "color": [[0, blanc], [0.45, chaud], [1, fonce]], "light_emission": 1,
                    "rotation": [-25, 25], "rotspeed": [-40, 40], "zoffset": 0.3})
        if halo and k % 2 == 0:
            # lueur douce autour du corps (le bloom que Roblox ajoute au Neon)
            out.append({"type": "particules", "nom": f"lueur_corps_{k}", "t0": round(ta, 4),
                        "duree_emission": round(tb - ta, 4), "rate": 6, "ancre": {"chemin": chemin},
                        "texture": "halo", "lifetime": [0.3, 0.45], "speed": [0, 0.3], "spread": [180, 180],
                        "size": [[0, 2.2 * taille], [1, 2.8 * taille]], "transparency": [[0, 0.7], [0.4, 0.6], [1, 1]],
                        "color": chaud, "light_emission": 1})
    return out


def eclairs(ancre, t0, duree, rayon=1.2, nombre=6, longueur=(0.9, 2.0), couleur=VERT_OFA, largeur=0.38, periode=0.05,
            nom="eclairs"):
    """Éclairs One For All (Izuku) qui crépitent autour d'une ancre."""
    return {"type": "eclairs", "nom": nom, "t0": t0, "duree": duree, "ancre": ancre, "rayon": rayon, "nombre": nombre,
            "longueur": list(longueur), "brisures": 5, "periode": periode, "largeur": largeur, "texture": "eclair",
            "color": couleur, "light_emission": 1, "transparency": [[0, 0], [0.85, 0], [1, 1]]}


def spirale(centre, axe, rayon, hauteur, tours, n, phase=0.0, rayon_fin=None):
    """Points d'une hélice (tête = premier point, en haut)."""
    import numpy as np
    c, ax = np.array(centre, float), np.array(axe, float)
    ax /= np.linalg.norm(ax)
    ref = np.array([1.0, 0, 0]) if abs(ax[0]) < 0.9 else np.array([0, 0, 1.0])
    e1 = np.cross(ax, ref); e1 /= np.linalg.norm(e1)
    e2 = np.cross(ax, e1)
    out = []
    for k in range(n):
        u = k / (n - 1)
        r = rayon + ((rayon_fin if rayon_fin is not None else rayon) - rayon) * u
        a = phase + 2 * np.pi * tours * u
        p = c + ax * hauteur * (1 - u) + r * (np.cos(a) * e1 + np.sin(a) * e2)
        out.append([round(float(x), 3) for x in p])
    return out


def dragon_aura_demo():
    """Aperçu labo : le dragon s'enroule autour d'un axe vertical (le perso)
    et ondule ; éclairs verts autour. Réglage du rendu avant le Dragon."""
    imgs = [[round(k / 30, 3), spirale([0, 1, 0], [0, 1, 0], 2.4, 6.5, 1.3, 28, phase=0.9 * k / 30, rayon_fin=1.6)]
            for k in range(0, 61)]
    # (éclairs verts retirés : Milan voulait la POSE d'Izuku, pas ses éclairs)
    c = [serpent(imgs, 0.0, 2.0, naissance=0.3, mort=(0.8, "queue"))]
    c += flammes_corps(c[0])
    r = recette("dragon_aura_demo", c, titre="Dragon : aura (démo)")
    r["cameras"] = {"large": {"oeil": [11, 6, 9], "cible": [0, 3.5, 0], "fov": 50},
                    "proche": {"oeil": [3.5, 8.8, 7.5], "cible": [1.5, 7.0, 1.0], "fov": 45},
                    "jeu": {"oeil": [1.75, 5.5, 11], "cible": [1.75, 3.5, -4], "fov": 70}}
    return r


def fin_couche(L):
    if L["type"] == "particules":
        return L["t0"] + L.get("duree_emission", 0) + L["lifetime"][1]
    if L["type"] in ("serpent", "eclairs"):
        return L["t0"] + L["duree"]
    if L["type"] == "trail":
        return L["t1"] + L.get("lifetime", 0.3)
    return L["t0"] + L.get("duree", 0)


_DUREES_SONS = None


def duree_son(nom):
    """Durée du WAV (sons/catalogue.json, écrit par sons.py)."""
    global _DUREES_SONS
    if _DUREES_SONS is None:
        cat = json.load(open(os.path.join(HERE, "sons", "catalogue.json")))
        _DUREES_SONS = {x["nom"]: x["duree"] for x in cat["sons"]}
    return _DUREES_SONS[nom]


def recette(nom, couches, sons=(), duree=None, bloom=None, titre=None):
    """Assemble une recette ; la durée couvre la dernière couche ET le
    dernier son (sinon le moteur Roblox détruit les Sound en nettoyant)."""
    fin = max([fin_couche(L) for L in couches] + [s["t0"] + duree_son(s["son"]) / s.get("hauteur", 1) for s in sons] + [0.0])
    return {"nom": nom, "titre": titre or nom, "duree": round(duree or fin + 0.05, 3), "graine": 5, "couches": couches,
            "sons": list(sons), **({"bloom": bloom} if bloom else {})}


def souffle_avant(t_contact, volume=0.8, vide=0.06, duree_son=0.44):
    """Le souffle qui ARRIVE sur le contact, coupé `vide` s avant (le vide
    avant l'impact, ECOUTE_REFS_SFX)."""
    return {"son": "souffle_projectile", "t0": round(max(0.0, t_contact - vide - duree_son), 4), "volume": volume}


def dragon_impact_aerien():
    """Aperçu labo du contact aérien du Dragon (en l'air, poing vers le bas)."""
    anc = {"pos": [0, 6, -3], "dir": [0, -1, -0.3], "coup": [0, -0.9, -0.4]}
    c = impact_couches(anc, palette=DRAGON, echelle=1.1, t0=0.2, sol=False)
    r = recette("dragon_impact_aerien", c, [{"son": "impact_lourd", "t0": 0.2, "volume": 0.9, "impact": True}],
                titre="Dragon : contact aérien")
    r["cameras"] = {"large": {"oeil": [12, 7, 6], "cible": [0, 5, -3], "fov": 50},
                    "jeu": {"oeil": [1.75, 7.5, 9], "cible": [1.75, 5.5, -6], "fov": 70}}
    return r


def dragon_plongee():
    """Aperçu labo du sillage de la plongée : le poing descend de 12 studs en
    0,37 s."""
    ch = [[0.2 + 0.37 * k / 10, 0.3 * k / 10, 14 - 12 * (k / 10) ** 1.6, -2 - 3 * k / 10] for k in range(11)]
    r = recette("dragon_plongee", sillage(ch, largeur=1.5), [souffle_avant(ch[-1][0])],
                titre="Dragon : sillage de la plongée")
    r["cameras"] = {"large": {"oeil": [14, 8, 8], "cible": [0, 7, -3], "fov": 50}}
    return r


RECETTES = {"orbe_impact": orbe_impact, "impact_m1": impact_m1,
            "dragon_impact_aerien": dragon_impact_aerien, "dragon_plongee": dragon_plongee,
            "dragon_aura_demo": dragon_aura_demo}


def toutes():
    return {k: f() for k, f in RECETTES.items()}


if __name__ == "__main__":
    json.dump(toutes(), sys.stdout, indent=1, ensure_ascii=False)
