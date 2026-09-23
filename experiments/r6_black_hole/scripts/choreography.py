"""
Trou noir -- choregraphie du personnage, reconstruite avec le cerveau
d'animateur (experiments/_shared/animator_brain, voir son README).

Pourquoi une refonte complete (2026-09-23, retour "pourquoi tout a l'air
mecanique dans tes rendus ?") -- audit chiffre de la version precedente
(output/motion_audit_avant.*) : 7/30 criteres, et 4 defauts de fond que
AUCUNE capture fixe ne montrait :
  1. POSES INVERSEES. describe_pose() : le "crouch torse plie vers
     l'avant" penchait le personnage 70 deg en ARRIERE ; les "bras ecartes
     a l'horizontale" croisaient les mains devant la poitrine ; climax,
     release, landing : penches en arriere au lieu d'en avant. Cause :
     convention d'axes supposee (Torso X+ = avant) jamais verifiee --
     c'est l'inverse (X+ = ARRIERE, prouve par poses.conventions_selftest).
  2. PIEDS QUI GLISSENT : 2.96 studs pendant le crouch (bassin fixe en
     x/z, jambes rigides pivotees a la main) -- calibrate.py ne mesurait
     que la hauteur des pieds.
  3. TOUT LE CORPS CLE A LA MEME FRAME : zero chevauchement, arrets
     simultanes (graphe "chaine de pics").
  4. SYMETRIE + METRONOME : gauche = miroir exact de droite, colonne sur
     un seul axe, boucles en sinus pur (purete de frequence 0.99).

Construction de cette version (chaque point -> un outil du cerveau) :
  - poses cles relues EN MOTS (describe_pose) contre la reference ;
  - poses au sol resolues en IK (plant_pose_at_height) : pieds plantes a
    l'erreur ~1e-9 stud, equilibre verifie (centre de masse au-dessus des
    appuis) ; passe foot_lock sur CHAQUE echantillon pendant les appuis ;
  - pistes par membre + decalages de cles par phase (overlap, sens de la
    chaine de pilotage de CHAQUE geste -- voir OVERLAP_RULES) ;
  - cycles d'attente/vol organiques (organic_keys, graine par membre) ;
  - ressorts de mouvement secondaire differencies par membre ;
  - regard contraint (look_at_pass) pour le coup d'oeil final.

Beats tires de la reference (frames extraites, lues une par une) :
  11      garde, sourire, tete legerement tournee
  12      armement : torsion, un bras part en arriere, l'autre croise
  13-14   accroupissement profond : torse plie, un bras haut derriere,
          l'autre replie devant, tete rentree et inclinee
  16-17   decollage : bras LANCES vers le haut l'un APRES l'autre (un
          vertical au-dessus de la tete, l'autre en diagonale), corps
          etire, tete en arriere
  18-20   vol : bras en V, jambes pendantes ramenees ("assis dans le vide")
  21-22   RECROQUEVILLEMENT EN L'AIR : bras croises devant la poitrine,
          genoux montes, tete baissee (le beat que la version precedente
          n'avait pas du tout)
  23      FLASH -- le corps s'ouvre d'un coup
  24-25   bras en T, jambes tendues, etincelles
  -> ici le flash du VFX (disk_form.t0) est cale PILE sur l'ouverture du
     corps (BURST_T) : c'est le geste qui declenche le flash, pas l'inverse.

Repere : AVANT = -Z, DROITE = +X (decal "face" du rig sur Face=5 =
Front). BLACK_HOLE_CENTER est a z=+1.6 = DERRIERE et au-dessus du
personnage (le commentaire d'origine disait "devant" -- meme erreur de
convention) ; conserve volontairement : camera de face, le personnage se
decoupe devant le vortex (comme les frames 23-24 de la reference), et le
climax devient une LUTTE lisible (aspire vers l'arriere, il resiste
penche en avant) puis l'implosion le projette vers l'avant.
"""
import math
import os
import sys

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "..", "..", "_shared"))

import r6_rig  # noqa: E402
from animator_brain import constraints as C  # noqa: E402
from animator_brain import organic as O  # noqa: E402
from animator_brain import tracks as TR  # noqa: E402
from animator_brain.rig_math import Rig  # noqa: E402

RIG = Rig.from_module(r6_rig)
PARTS = list(r6_rig.PART_ORDER)
REST = (0.0, 0.0, 0.0)


def _fr(n):
    return n / 30.0


# =======================================================================
# Chronologie. Les ancres historiques (RISE_T, HOLD_END_T, CLIMAX_T,
# RELEASE_T, LAND_T...) sont INCHANGEES : black_hole_track.py (VFX), la
# camera du lecteur et calibrate.py en dependent. Les nouveaux beats sont
# inseres entre elles.
# =======================================================================
T0_END = _fr(30)                    # 1.000  fin du plan d'etablissement
INHALE_T = T0_END + _fr(3)          # 1.100  contre-anticipation (se grandit avant de descendre)
WIND_T = T0_END + _fr(9)            # 1.300  armement (torsion, bras qui partent)
CROUCH_T = T0_END + _fr(15)         # 1.500  accroupissement atteint
CROUCH_HOLD_T = CROUCH_T + _fr(9)   # 1.800  fin du hold (qui continue de se tasser)
PUSH_T = CROUCH_HOLD_T + _fr(2)     # 1.867  mi-poussee (torse a moitie deroule)
TOE_OFF_T = CROUCH_HOLD_T + _fr(4)  # 1.933  jambes tendues sous lui (deja en l'air, voir CONTACTS)
RISE_T = CROUCH_HOLD_T + _fr(11)    # 2.167  extreme du lancer (corps etire, bras en l'air)
V_T = RISE_T + _fr(10)              # 2.500  bras qui se posent en V
HOLD_END_T = RISE_T + 3.4           # 5.567  debut de l'aspiration
CLIMAX_T = HOLD_END_T + _fr(20)     # 6.233  lutte maximale
RELEASE_T = CLIMAX_T + _fr(6)       # 6.433  implosion -> projete vers l'avant
LAND_T = RELEASE_T + _fr(14)        # 6.900  contact au sol
ABSORB_T = LAND_T + _fr(4)          # 7.033  amorti le plus bas
RECOVER_T = LAND_T + _fr(10)        # 7.233  se redresse
IDLE_OUT_END = RECOVER_T + _fr(30)  # 8.233
TOTAL_DURATION = IDLE_OUT_END

VFX_EVENTS = {
    "debris_launch": {"t0": RISE_T, "t1": RISE_T + 0.8},
    "debris_gather": {"t0": RISE_T + 0.8, "t1": HOLD_END_T},
    "disk_form": {"t0": HOLD_END_T - 0.6, "t1": HOLD_END_T + 0.5},
    "climax": {"t0": CLIMAX_T - 0.3, "t1": CLIMAX_T + 0.3},
    "collapse": {"t0": RELEASE_T, "t1": LAND_T},  # borne a LAND_T (verifie par calibrate.py)
}
BURST_T = VFX_EVENTS["disk_form"]["t0"]  # 4.967 -- l'ouverture du corps EST le flash
CURL_IN_T = BURST_T - _fr(17)            # 4.400  commence a se replier
CURL_T = BURST_T - _fr(8)                # 4.700  recroqueville
CURL_HOLD_T = BURST_T - _fr(2)           # 4.900  serre encore (hold vivant), puis explose
T_SETTLE_T = BURST_T + _fr(7)            # 5.200  bras qui se posent en T

AIRBORNE_WINDOW = {"t0": RISE_T, "t1": LAND_T}

# =======================================================================
# Appuis. Garde legerement large ("power stance") -- valeur tiree de la
# recherche d'equilibre (voir README) : pieds cote a cote, un peu plus
# ecartes que le repos, c'est la configuration ou un R6 a jambes rigides
# peut s'accroupir profondement SANS glisser ET avec le centre de masse
# au-dessus des pieds. Leger decalage avant/arriere (asymetrie).
# =======================================================================
FEET_START = {"Right Leg": (0.77, 0.0, -0.03), "Left Leg": (-0.77, 0.0, 0.03)}
# Atterrissage : projete vers l'avant par l'implosion, il retombe un peu
# devant son point de depart, le pied droit legerement en avant.
FEET_LAND = {"Right Leg": (0.74, 0.0, -0.52), "Left Leg": (-0.76, 0.0, -0.40)}
_LG = {"Right Leg": (20.0, 0.0, 3.0), "Left Leg": (20.0, 0.0, -3.0)}

CONTACTS = [
    # DECOLLAGE R6 : les pieds quittent le sol a PUSH_T, jambes encore
    # flechies -- le personnage JAILLIT du crouch et les jambes s'etendent
    # EN L'AIR. Une jambe R6 est rigide (pas de genou) : pivotant sur un
    # pied plante, la hanche decrit un ARC dont la vitesse verticale tombe
    # a zero pres de la verticale (tout le mouvement devient horizontal).
    # Garder les pieds au sol jusqu'a pleine extension imposait au bassin
    # 0.55 stud de balayage horizontal en UNE frame (mesure, trace du
    # solveur) ; une poussee verticale acceleree jusqu'a l'extension est
    # geometriquement impossible sans genou. C'est aussi ce que montre la
    # reference (frames 15-16 : deja en l'air, jambes qui trainent).
    # blend_out=0 : a PUSH_T la pose cle est resolue par l'IK, la
    # correction y est nulle -> aucune discontinuite.
    {"leg": "Right Leg", "t0": 0.0, "t1": PUSH_T, "target": FEET_START["Right Leg"], "blend_out": 0.0,
     "leg_release_blend": _fr(5)},
    {"leg": "Left Leg", "t0": 0.0, "t1": PUSH_T, "target": FEET_START["Left Leg"], "blend_out": 0.0,
     "leg_release_blend": _fr(4)},
    {"leg": "Right Leg", "t0": LAND_T, "t1": IDLE_OUT_END + 1.0, "target": FEET_LAND["Right Leg"]},
    {"leg": "Left Leg", "t0": LAND_T + _fr(3), "t1": IDLE_OUT_END + 1.0, "target": FEET_LAND["Left Leg"],
     "blend_in": _fr(3)},
]

GROUNDED_REPORT = {}
BALANCE_TOL = 0.08


def _grounded(name, torso, depth, xz_guess, feet, upper, support=None):
    """Pose au sol construite comme avec un rig a jambes IK :
    - `depth` = de combien le bassin descend SOUS sa hauteur maximale
      atteignable pour ce torse et ces appuis (0 = jambes tendues) --
      calculee par pelvis_height_range, jamais une hauteur absolue devinee ;
    - pieds plantes exactement (IK), bassin place par le solveur ;
    - EQUILIBRE OBLIGATOIRE : centre de masse au-dessus des appuis a
      BALANCE_TOL pres, sinon erreur (jamais une pose qui "tombe").
    Toute violation leve une erreur -- jamais une pose silencieusement fausse.
    NB torsion (Torso Y) volontairement faible au sol : en R6 le torse EST
    le bassin (pas d'articulation de colonne) ; tordre le torse tord les
    hanches, et avec les pieds plantes le bassin part en diagonale (mesure :
    1.36 stud de derive laterale a -8 deg). L'asymetrie passe par les bras,
    la tete et l'inclinaison laterale."""
    rng = C.pelvis_height_range(RIG, torso, feet, step=0.01)
    if rng is None:
        raise ValueError(f"{name}: aucune hauteur de bassin atteignable pour torse={torso}")
    pelvis_y = rng[1] - depth
    root, legs, info = C.plant_pose_at_height(RIG, torso, pelvis_y, xz_guess, feet, _LG)
    if not info["feasible"] or max(info["foot_error"].values()) > 1e-4:
        raise ValueError(f"{name}: pose au sol infaisable : torse={torso} bassin={pelvis_y:.2f} ({info})")
    rots = {"Torso": torso, **legs, **upper}
    # `support` : appuis a considerer pour l'equilibre. Par defaut les pieds
    # au sol. Une pose DYNAMIQUE (instant de contact d'un atterrissage :
    # un seul pied pose, l'autre arrive 2 frames plus tard) declare
    # explicitement la base d'appui qu'elle rejoint -- exception
    # documentee, jamais un controle desactive en silence.
    grounded_legs = support or [l for l in feet if feet[l][1] <= 0.01]
    if support:
        feet_eval = {l: (feet[l][0], 0.0, feet[l][2]) for l in feet}
        _, legs_eval, _ = C.plant_pose_at_height(RIG, torso, pelvis_y, xz_guess, feet_eval, _LG)
        margin = C.balance_margin(RIG, {"Torso": torso, **legs_eval, **upper}, root, grounded_legs)
    else:
        margin = C.balance_margin(RIG, rots, root, grounded_legs)
    if margin is not None and margin > BALANCE_TOL:
        raise ValueError(f"{name}: hors equilibre de {margin:.2f} stud (CdM hors des appuis)")
    GROUNDED_REPORT[name] = {"pelvis_y": round(pelvis_y, 3), "pelvis_max": round(rng[1], 3),
                             "root": tuple(round(v, 3) for v in root), "balance_margin": round(margin or 0.0, 3)}
    return {"root_pos": root, **rots}


# =======================================================================
# POSES CLES -- chaque valeur relue avec describe_pose() (sortie dans le
# README). Conventions : Torso/Head X- = vers l'avant/le bas ; bras X+ =
# vers l'avant puis le haut ; Right Arm Z+ / Left Arm Z- = ecarte ;
# Right Arm Z- / Left Arm Z+ = croise devant.
# =======================================================================
# -- ref 11 : garde vivante, tete un peu tournee, bras pas symetriques
P_IDLE = _grounded("IDLE", (-3, 1.5, -2), 0.03, (0.0, 0.0), FEET_START,
                   {"Head": (-2, 7, 3), "Right Arm": (4, 0, 5), "Left Arm": (-3, 0, -7)})
# -- contre-anticipation : il se grandit, inspire, avant de plonger
P_INHALE = _grounded("INHALE", (5, 1, -1), 0.0, (0.0, 0.0), FEET_START,
                     {"Head": (9, 3, 2), "Right Arm": (9, 0, 11), "Left Arm": (5, 0, -13)})
# -- ref 12 : armement -- bras droit part en arriere/haut, bras gauche
# croise devant, tete qui s'incline, torse qui commence a plonger
P_WIND = _grounded("WIND", (-32, -3, 3), 0.25, (0.0, 0.2), FEET_START,
                   {"Head": (-10, -9, 14), "Right Arm": (-72, 0, 24), "Left Arm": (48, 0, 22)})
# -- ref 13-14 : accroupissement profond, torse plie, bras droit HAUT
# derriere, bras gauche replie devant, tete rentree et inclinee
P_CROUCH = _grounded("CROUCH", (-64, 0, 4), 0.12, (0.0, 0.0), FEET_START,
                     {"Head": (-14, -8, 18), "Right Arm": (-128, 0, 18), "Left Arm": (30, 0, 30)})
# -- hold VIVANT : continue de se tasser (jamais un gel plat)
P_CROUCH_HOLD = _grounded("CROUCH_HOLD", (-69, -2, 5), 0.16, (0.0, 0.0), FEET_START,
                          {"Head": (-17, -9, 20), "Right Arm": (-136, 0, 20), "Left Arm": (24, 0, 34)})
# -- mi-poussee (cle resolue par la meme IK que les autres) : sans elle, le
# bassin cle montait "en ligne droite" pendant que le torse se deroulait --
# or en R6 les hanches sont 1 stud SOUS le pivot du torse : deplier le
# torse de -69 a -18 deg les fait descendre de 0.6 stud, l'IK devait
# compenser en pleine poussee -> vitesse du bassin 9.5 -> 5.3 -> 8.4
# studs/s (mesure : a-coup de 3 frames). Avec une cle intermediaire
# coherente avec la geometrie, la poussee accelere d'un seul tenant.
P_PUSH = _grounded("PUSH", (-44, 0, 3), 0.36, (0.0, 0.0), FEET_START,
                   {"Head": (-12, -4, 12), "Right Arm": (-95, 0, 40), "Left Arm": (62, 0, 8)})
# -- extension EN L'AIR (les pieds ont quitte le sol a PUSH_T, voir
# CONTACTS) : jambes qui se deplient sous lui (X+ pour compenser le torse
# encore penche : jambes quasi verticales dans le monde), le haut du corps
# se deroule ; le bras GAUCHE mene le lancer (ref 16-17), le droit suit.
# Le bassin CONTINUE sa trajectoire vers l'apogee (x/z interpoles
# PUSH -> RISE) -- la version "jambes tendues AU SOL" de cette cle lui
# imposait un detour horizontal (20 studs/s mesures).
P_TOE_OFF = {"root_pos": (-0.23, 2.99, 0.39), "Torso": (-18, 2, 0),
             "Head": (-4, 0, 4), "Right Arm": (-35, 0, 72), "Left Arm": (118, 0, -12),
             "Right Leg": (14, 0, 3), "Left Leg": (17, 0, -3)}

STAND_Y = 3.03                 # bassin jambes tendues, pieds au sol
LEV_Y = STAND_Y + 2.4          # hauteur de vol (clearance ~2.4 studs, comme avant)

# -- ref 16-17 : extreme du lancer -- corps ETIRE (poitrine ouverte, tete
# en arriere), bras gauche vertical au-dessus de la tete, bras droit en
# diagonale haute sur le cote, jambes pendantes serrees qui trainent
P_RISE = {"root_pos": (0.0, LEV_Y + 0.25, 0.05), "Torso": (14, 14, -8), "Head": (22, -6, -6),
          "Right Arm": (20, 0, 118), "Left Arm": (170, 0, -8),
          "Right Leg": (-10, 0, -2), "Left Leg": (-6, 0, 3)}
# -- ref 18-20 : bras en V (legerement asymetriques, un peu devant),
# jambes ramenees vers l'avant ("assis dans le vide")
P_V = {"root_pos": (0.0, LEV_Y, 0.0), "Torso": (5, 6, 4), "Head": (4, 3, -5),
       "Right Arm": (18, 0, 128), "Left Arm": (12, 0, -121),
       "Right Leg": (36, 0, 7), "Left Leg": (20, 0, -6)}
# -- ref 21-22 : recroquevillement -- bras croises devant la poitrine,
# genoux montes, dos rond, tete baissee
P_CURL = {"root_pos": (0.0, LEV_Y - 0.15, 0.05), "Torso": (-22, 10, 5), "Head": (-20, 0, 5),
          "Right Arm": (88, 0, -38), "Left Arm": (84, 0, 42),
          "Right Leg": (58, 0, 6), "Left Leg": (64, 0, -4)}
P_CURL_HOLD = {"root_pos": (0.0, LEV_Y - 0.25, 0.05), "Torso": (-27, 13, 6), "Head": (-24, 0, 6),
               "Right Arm": (90, 0, -44), "Left Arm": (86, 0, 48),
               "Right Leg": (64, 0, 6), "Left Leg": (70, 0, -4)}
# -- ref 23-24 : OUVERTURE (= le flash) -- poitrine projetee, bras jetes
# au-dela du T (un peu en arriere et au-dessus), jambes qui se detendent
P_BURST = {"root_pos": (0.0, LEV_Y + 0.4, 0.1), "Torso": (16, -8, -4), "Head": (14, 0, 0),
           "Right Arm": (-12, 0, 100), "Left Arm": (-14, 0, -97),
           "Right Leg": (-6, 0, 9), "Left Leg": (-8, 0, -8)}
# -- ref 25 : T pose tenue, tete inclinee (le sourire en coin), bras pas
# parfaitement a la meme hauteur
P_T = {"root_pos": (0.0, LEV_Y + 0.15, 0.05), "Torso": (4, -3, -5), "Head": (2, 5, 7),
       "Right Arm": (0, 0, 88), "Left Arm": (2, 0, -93),
       "Right Leg": (4, 0, 2), "Left Leg": (2, 0, -3)}
# -- debut de l'aspiration (le vortex est DERRIERE-au-dessus) : il
# commence a resister, bras qui reviennent devant
P_PULL = {"root_pos": (0.0, LEV_Y - 0.1, 0.15), "Torso": (-8, 6, -3), "Head": (-8, -3, 2),
          "Right Arm": (40, 0, 60), "Left Arm": (35, 0, -55),
          "Right Leg": (-8, 0, 4), "Left Leg": (-4, 0, -5)}
# -- CLIMAX : lutte -- penche en avant contre l'aspiration, bras jetes
# devant en appui, jambes aspirees vers l'arriere, tete qui force
P_CLIMAX = {"root_pos": (0.0, STAND_Y + 1.5, 0.45), "Torso": (-24, 14, -9), "Head": (-16, -8, 4),
            "Right Arm": (68, 0, 22), "Left Arm": (58, 0, -34),
            "Right Leg": (-34, 0, 6), "Left Leg": (-26, 0, -9)}
# -- RELEASE : implosion, l'aspiration cesse d'un coup -> projete vers
# l'avant ; le torse fouette, la tete et les bras restent en arriere
# (ils suivront -- overlap), les jambes passent devant
P_RELEASE = {"root_pos": (0.0, STAND_Y + 0.6, -0.2), "Torso": (-40, -12, 8), "Head": (10, 4, -3),
             "Right Arm": (-55, 0, 45), "Left Arm": (-48, 0, -52),
             "Right Leg": (24, 0, 5), "Left Leg": (30, 0, -6)}
# -- LAND / ABSORB / RECOVER : au sol, IK sur les appuis d'atterrissage ;
# bras ouverts devant pour l'equilibre, puis relachement, poids qui se
# pose, bras droit encore un peu leve (echo du geste).
# (pied gauche encore 5 cm en l'air a LAND_T : il se pose 3 frames apres
# le droit, transfert de poids progressif -- un atterrissage n'est jamais
# sur les deux pieds a la meme frame. 14 cm au premier essai : avec des
# jambes rigides, le poser a hauteur de bassin fixe forcait 0.6 stud de
# glissement lateral du bassin en 2 frames.)
P_LAND = _grounded("LAND", (-35, 2, -3), 0.35, (0.0, 0.0),
                   {"Right Leg": FEET_LAND["Right Leg"], "Left Leg": (-0.76, 0.05, -0.40)},
                   {"Head": (-6, 4, 0), "Right Arm": (35, 0, 40), "Left Arm": (48, 0, -30)},
                   support=["Right Leg", "Left Leg"])
P_ABSORB = _grounded("ABSORB", (-42, 3, -4), 0.45, (0.0, 0.0), FEET_LAND,
                     {"Head": (-10, 5, 2), "Right Arm": (22, 0, 30), "Left Arm": (30, 0, -22)})
# (RECOVER encore 0.16 sous l'extension : il finit de se redresser PENDANT
# la respiration jusqu'a P_END -- s'arreter net a 0.08 faisait stopper les
# jambes IK en 2 frames, pres de l'extension l'IK amplifie toute
# deceleration du bassin : discontinuite mesuree par l'audit.)
P_RECOVER = _grounded("RECOVER", (-10, 2, 4), 0.16, (0.0, 0.0), FEET_LAND,
                      {"Head": (-4, 10, -3), "Right Arm": (14, 0, 16), "Left Arm": (2, 0, -5)})
P_END = _grounded("END", (-4, 1, 3), 0.03, (0.0, 0.0), FEET_LAND,
                  {"Head": (-2, 12, -2), "Right Arm": (6, 0, 8), "Left Arm": (0, 0, -5)})

KEY_POSES = [
    (INHALE_T, P_INHALE), (WIND_T, P_WIND), (CROUCH_T, P_CROUCH), (CROUCH_HOLD_T, P_CROUCH_HOLD),
    (PUSH_T, P_PUSH), (TOE_OFF_T, P_TOE_OFF), (RISE_T, P_RISE), (V_T, P_V),
    (CURL_IN_T, None),  # fin du cycle de vol organique (valeur = fin du cycle)
    (CURL_T, P_CURL), (CURL_HOLD_T, P_CURL_HOLD), (BURST_T, P_BURST), (T_SETTLE_T, P_T),
    (HOLD_END_T, P_PULL), (CLIMAX_T, P_CLIMAX), (RELEASE_T, P_RELEASE),
    (LAND_T, P_LAND), (ABSORB_T, P_ABSORB), (RECOVER_T, P_RECOVER),
]

# =======================================================================
# Cycles organiques (moving holds) -- amplitudes en deg (studs pour la
# racine), frequences en Hz. Chaque membre a SA frequence et SA graine :
# jamais deux membres en phase, jamais un sinus pur.
# =======================================================================
IDLE_CYCLE = {
    "root": [{"amp": 0.02, "freq": 0.21}, {"amp": 0.012, "freq": 0.33}, {"amp": 0.015, "freq": 0.17}],
    "Torso": [{"amp": 1.4, "freq": 0.32}, {"amp": 1.6, "freq": 0.21}, {"amp": 1.0, "freq": 0.27}],
    "Head": [{"amp": 2.0, "freq": 0.40}, {"amp": 3.0, "freq": 0.23}, {"amp": 1.5, "freq": 0.30}],
    "Right Arm": [{"amp": 2.5, "freq": 0.35}, {"amp": 1.2, "freq": 0.47}, {"amp": 1.8, "freq": 0.58}],
    "Left Arm": [{"amp": 2.2, "freq": 0.41}, None, {"amp": 1.8, "freq": 0.33}],
}
HOVER_CYCLE = {
    "root": [{"amp": 0.07, "freq": 0.23}, {"amp": 0.22, "freq": 0.55}, {"amp": 0.08, "freq": 0.19}],
    "Torso": [{"amp": 3.0, "freq": 0.50}, {"amp": 3.5, "freq": 0.31}, {"amp": 2.5, "freq": 0.43}],
    "Head": [{"amp": 3.0, "freq": 0.47}, {"amp": 5.0, "freq": 0.26}, {"amp": 3.0, "freq": 0.38}],
    "Right Arm": [{"amp": 6.0, "freq": 0.58}, None, {"amp": 7.0, "freq": 0.52}],
    "Left Arm": [{"amp": 5.0, "freq": 0.63}, None, {"amp": 8.0, "freq": 0.49}],
    "Right Leg": [{"amp": 7.0, "freq": 0.44}, None, {"amp": 3.0, "freq": 0.37}],
    "Left Leg": [{"amp": 6.0, "freq": 0.51}, None, {"amp": 3.0, "freq": 0.41}],
}
T_CYCLE = {
    "root": [None, {"amp": 0.06, "freq": 0.9}, None],
    "Right Arm": [{"amp": 2.0, "freq": 1.1}, None, {"amp": 2.5, "freq": 0.95}],
    "Left Arm": [{"amp": 2.0, "freq": 1.25}, None, {"amp": 2.0, "freq": 1.05}],
    "Head": [{"amp": 1.5, "freq": 0.8}, {"amp": 2.0, "freq": 0.6}, None],
}
BREATH_CYCLE = {  # fin : essouffle -> respiration plus ample que la garde
    "root": [{"amp": 0.02, "freq": 0.19}, {"amp": 0.03, "freq": 0.62}, {"amp": 0.02, "freq": 0.15}],
    "Torso": [{"amp": 3.0, "freq": 0.62}, {"amp": 1.5, "freq": 0.2}, {"amp": 1.2, "freq": 0.28}],
    "Head": [{"amp": 1.5, "freq": 0.62}, None, {"amp": 1.2, "freq": 0.3}],
    "Right Arm": [{"amp": 2.0, "freq": 0.62}, None, {"amp": 1.5, "freq": 0.34}],
    "Left Arm": [{"amp": 1.8, "freq": 0.66}, None, {"amp": 1.5, "freq": 0.29}],
}


def _cycle_tracks(t0, t1, pose0, pose1, spec, seed, ramp_s=0.3):
    """Pistes organiques entre deux poses (derive lineaire pose0 -> pose1
    + cycle par membre). Les membres absents du spec restent sur une
    interpolation simple pose0 -> pose1."""
    out = {}
    for i, part in enumerate(PARTS):
        key = "root" if part == "HumanoidRootPart" else part
        if part == "HumanoidRootPart":
            continue
        a = pose0.get(part, REST)
        b = pose1.get(part, REST)
        chans = spec.get(part)
        if chans:
            out[part] = O.organic_keys(t0, t1, a, chans, seed=seed + 17 * i, ramp_s=ramp_s, base_end=b)
        else:
            out[part] = [(t0, tuple(a)), (t1, tuple(b))]
    ra, rb = pose0["root_pos"], pose1["root_pos"]
    if spec.get("root"):
        out[TR.ROOT_POS] = O.organic_keys(t0, t1, ra, spec["root"], seed=seed + 999, ramp_s=ramp_s, base_end=rb)
    else:
        out[TR.ROOT_POS] = [(t0, tuple(ra)), (t1, tuple(rb))]
    out["HumanoidRootPart"] = [(t0, REST), (t1, REST)]
    return out


def _pose_tracks(t, pose):
    out = {p: [(t, tuple(pose.get(p, REST)))] for p in PARTS if p != "HumanoidRootPart"}
    out["HumanoidRootPart"] = [(t, REST)]
    out[TR.ROOT_POS] = [(t, tuple(pose["root_pos"]))]
    return out


def _cat(*chunks):
    out = {}
    for ch_ in chunks:
        for k, v in ch_.items():
            out.setdefault(k, []).extend(v)
    for k in out:
        dedup = {}
        for t, v in out[k]:
            dedup[round(t, 6)] = (t, v)
        out[k] = sorted(dedup.values(), key=lambda kv: kv[0])
    return out


# pose de fin du vol en V, juste avant de se replier (derive : les bras
# commencent a descendre, le corps se tasse d'un rien -- anticipation du
# recroquevillement)
P_V_END = dict(P_V, **{"root_pos": (0.0, LEV_Y - 0.05, 0.02), "Torso": (0, 1, 1),
                        "Right Arm": (30, 0, 112), "Left Arm": (26, 0, -106)})

# =======================================================================
# OVERLAP -- decalages de cles en frames (30 fps), par phase. Positif = en
# retard sur le reste du corps. Le sens depend de QUI MENE le geste :
#  - au sol / armement : le bassin mene (IK), le torse +1, la tete +2,
#    le bras qui "traine" +3 ;
#  - decollage : bassin/torse menent, bras GAUCHE mene le lancer (+1),
#    bras droit +3, tete +3, jambes +3 (dernieres a quitter le sol) ;
#  - ouverture (BURST) : ce sont les BRAS qui menent (l'energie sort par
#    eux) : bras 0/+1, torse +1, tete +2, jambes +2 ;
#  - aspiration/implosion : torse mene, tete +2, bras +2/+3, jambes +3
#    (trainees par l'aspiration) ;
#  - atterrissage : les PIEDS menent (contact), torse +1, tete +2, bras
#    +3/+4 (ils continuent sur leur elan).
# Les cycles organiques (garde, vol, T, respiration) ont deja leur propre
# desynchronisation -> pas de decalage supplementaire.
# =======================================================================
OVERLAP_RULES = [
    {"t0": T0_END - 0.01, "t1": CROUCH_HOLD_T - 0.001,
     "frames": {"Torso": 1, "Head": 2, "Right Arm": 3, "Left Arm": 2}},
    {"t0": CROUCH_HOLD_T - 0.001, "t1": V_T + 0.001,
     "frames": {"Head": 3, "Left Arm": 1, "Right Arm": 3, "Right Leg": 3, "Left Leg": 2}},
    {"t0": CURL_T - 0.001, "t1": CURL_HOLD_T + 0.001,
     "frames": {"Head": 1, "Right Arm": 2, "Left Arm": 1, "Right Leg": 3, "Left Leg": 1}},
    {"t0": BURST_T - 0.001, "t1": T_SETTLE_T + 0.001,
     "frames": {"Torso": 1, "Head": 2, "Right Arm": 1, "Right Leg": 1, "Left Leg": 3}},
    {"t0": HOLD_END_T - 0.001, "t1": LAND_T - 0.001,
     "frames": {"Head": 2, "Right Arm": 3, "Left Arm": 2, "Right Leg": 4, "Left Leg": 2}},
    {"t0": LAND_T - 0.001, "t1": RECOVER_T + 0.001,
     "frames": {"Head": 2, "Right Arm": 4, "Left Arm": 3}},
]


def character_tracks():
    """Pistes finales (apres decalages d'overlap) + journal des ajustements."""
    chunks = [
        _cycle_tracks(0.0, T0_END - _fr(3), P_IDLE, P_IDLE, IDLE_CYCLE, seed=11, ramp_s=0.25),
        _cycle_tracks(V_T, CURL_IN_T, P_V, P_V_END, HOVER_CYCLE, seed=23, ramp_s=0.35),
        _cycle_tracks(T_SETTLE_T, HOLD_END_T, P_T, P_T, T_CYCLE, seed=37, ramp_s=0.12),
        _cycle_tracks(RECOVER_T, IDLE_OUT_END, P_RECOVER, P_END, BREATH_CYCLE, seed=41, ramp_s=0.3),
    ]
    for t, pose in KEY_POSES:
        if pose is not None:
            chunks.append(_pose_tracks(t, pose))
    tracks = _cat(*chunks)
    return TR.offset_tracks(tracks, OVERLAP_RULES)


# =======================================================================
# Mouvement secondaire (ressorts analytiques, anim_engine._spring_chase) --
# differencies par membre (jamais deux bras identiques) : le bras droit,
# plus "lache", depasse plus et plus longtemps. Jambes seulement a partir
# du decollage (au sol elles sont tenues par l'IK des appuis).
# =======================================================================
SECONDARY_MOTION = {
    # Torse : ressort seulement une fois en l'air -- au sol il fait partie
    # du systeme porteur (bassin + torse + jambes resolus ensemble par
    # l'IK) ; un torse qui "traine" pendant la poussee forcait l'IK a
    # tirer le bassin de 0.85 stud vers le bas au decollage (mesure).
    "Torso": {"channels": (0, 1, 2), "stiffness": 320.0, "damping_ratio": 0.55, "t_min": TOE_OFF_T,
              "t_max": LAND_T - _fr(6), "blend_out": _fr(6)},
    "Head": {"channels": (0, 1, 2), "stiffness": 230.0, "damping_ratio": 0.42, "t_min": T0_END},
    "Right Arm": {"channels": (0, 1, 2), "stiffness": 135.0, "damping_ratio": 0.30, "t_min": T0_END},
    "Left Arm": {"channels": (0, 1, 2), "stiffness": 165.0, "damping_ratio": 0.36, "t_min": T0_END},
    "Right Leg": {"channels": (0, 2), "stiffness": 110.0, "damping_ratio": 0.34, "t_min": TOE_OFF_T},
    "Left Leg": {"channels": (0, 2), "stiffness": 125.0, "damping_ratio": 0.38, "t_min": TOE_OFF_T},
}

# Point central du trou noir : au-dessus et DERRIERE le personnage (z>0,
# voir docstring de module sur le repere).
BLACK_HOLE_CENTER = np.array([0.0, LEV_Y + 4.0, 1.6])

# Regard : apres l'atterrissage, il se retourne a moitie vers l'endroit
# ou etait le vortex (derriere lui) -- dernier beat d'acting.
LOOK_WINDOWS = [
    # cible derriere-GAUCHE (x<0 = sa gauche) : un coup d'oeil "par-dessus
    # l'epaule" a un cote ; une cible pile derriere est ambigue (voir
    # constraints.head_look_angles).
    {"t0": RECOVER_T + _fr(4), "t1": IDLE_OUT_END + 1.0,
     "target": tuple(BLACK_HOLE_CENTER + np.array([-3.5, -3.0, 0.0])), "weight": 0.8},
]


def post_local(local_samples):
    """Contraintes appliquees sur les echantillons (voir anim_engine.sample) :
    pieds plantes pendant les appuis, puis regard. Retourne le journal."""
    log = C.foot_lock_pass(local_samples, RIG, CONTACTS, blend_s=_fr(2), release_eps=0.002)
    C.look_at_pass(local_samples, RIG, LOOK_WINDOWS)
    return log


# Fenetres pour l'audit (audit_motion.py)
AUDIT_LOOP_WINDOWS = {
    "idle": (0.15, T0_END - _fr(4)),
    "hover": (V_T + 0.3, CURL_IN_T - 0.05),
    "idle_out": (RECOVER_T + 0.25, IDLE_OUT_END),
}
AUDIT_CHART_WINDOW = (T0_END - 0.1, V_T + 0.3)
# jambes libres (ni appui, ni approche/decollage) : overlap et symetrie des
# jambes mesures seulement ici (voir animator_brain.audit.overlap_report)
AUDIT_FREE_LEG_WINDOWS = [(TOE_OFF_T + 0.1, LAND_T - 0.05)]
# SNAPS VOULUS (declares, jamais deduits apres coup) : le jaillissement hors
# du crouch et l'ouverture du corps au flash sont des snaps de 1-2 frames
# par choix d'animation (impact) ; toute autre discontinuite est un defaut.
AUDIT_INTENDED_SNAPS = [(CROUCH_HOLD_T - _fr(1), PUSH_T), (CURL_HOLD_T - _fr(1), BURST_T + _fr(2))]
