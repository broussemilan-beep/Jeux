"""
Scene complete de combat (Hero vs Rival, deux rigs R6 INDEPENDANTS ET
ACTIFS -- pas un attaquant contre un mannequin statique) puis, une fois
Hero vainqueur, raccord SANS COUPURE vers la sequence trone/couronne de
`r6_throne_crown` (`throne_sequence.py`, copie telle quelle, importee ici
et decalee en temps + hauteur d'estrade).

Demande utilisateur explicite : "fais moi une scene complete d'un combat
entre les deux d'au moins 30s avec plus que du combo poing et je veux de
la puissance du fluide et du decors qui se casse entre les 2 rig puis le
gagnant marche et tu mets l'animation en cohérence du trone et de la
couronne."

Strategie de reutilisation (pas de recalibrage inutile) :
  - Le combo jab/cross/hook de `r6_hit_combo` (`punch_combo.py`, copie
    telle quelle) est un bloc COMPLETEMENT calibre et verifie (ecarts de
    contact 0.493/0.366/0.380 stud, placement des pieds mesure, axes de
    jambes distincts par coup) -- le reutiliser demande seulement une
    TRANSLATION uniforme en Z et en temps, jamais une nouvelle mesure :
    translater un point de contact deja calibre par un vecteur constant
    donne un point de contact TOUJOURS calibre (la geometrie relative ne
    change pas). Voir OFFSET_Z plus bas.
  - Pour le premier echange (Rival attaque, Hero encaisse), les POSES
    LOCALES (Torso/Head/Arms/Legs) de punch_combo sont reutilisees
    TELLES QUELLES dans l'autre sens : une rotation locale ne depend pas
    du yaw (HumanoidRootPart) du personnage qui la porte, donc le meme
    "JAB_HIT_TORSO" lit correctement un coup encaisse de face, que le
    personnage fasse face a +Z ou -Z dans le monde. Seule la position
    (root_pos.Z) doit etre REFLETEE (miroir), pas les poses -- voir
    _mirror_z().

Disposition de l'arene (studs, Y=0 = sol reel, meme repere que
`r6_throne_crown`) : le combat se deroule loin du trone (Z tres negatif),
Hero cote "trone" (Z le moins negatif des deux), Rival plus loin (Z le
plus negatif) -- pour qu'apres sa victoire, Hero n'ait qu'a AVANCER en +Z
(jamais reculer) pour rejoindre le pied de l'escalier
(`throne_sequence._CLIMB_Z0 = -7.2`).
"""
import math

import numpy as np

import props
import punch_combo as pc
import throne_sequence as ts
from r6_rig import JOINTS, PART_SIZES, joint_for_part

REST = (0.0, 0.0, 0.0)
GROUND_Y = 3.0
SNAP = 1 / 30


def _fr(n):
    return n / 30.0


# ---------------------------------------------------------------------
# Cinematique directe partagee (copiee de punch_combo.py -- module
# independant, garde volontairement sans dependance croisee entre
# prototypes isoles, voir CLAUDE.md/convention du depot).
def _euler_xyz_matrix(rx_deg, ry_deg, rz_deg):
    rx, ry, rz = math.radians(rx_deg), math.radians(ry_deg), math.radians(rz_deg)
    cx, sx = math.cos(rx), math.sin(rx)
    cy, sy = math.cos(ry), math.sin(ry)
    cz, sz = math.cos(rz), math.sin(rz)
    Rx = np.array([[1, 0, 0], [0, cx, -sx], [0, sx, cx]])
    Ry = np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]])
    Rz = np.array([[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]])
    return Rx @ Ry @ Rz


def grounded_root_y(torso_rot, leg_rot, leg_part, target_y=0.0):
    joint = joint_for_part(leg_part)
    c0 = np.array(JOINTS[joint]["C0"]["pos"])
    c1 = np.array(JOINTS[joint]["C1"]["pos"])
    r_torso = _euler_xyz_matrix(*torso_rot)
    r_leg_local = _euler_xyz_matrix(*leg_rot)
    leg_local_pos = c0 - r_leg_local @ c1
    r_leg_world = r_torso @ r_leg_local
    half = PART_SIZES[leg_part][1] / 2.0
    tip_offset_y = (r_torso @ leg_local_pos + r_leg_world @ np.array([0.0, -half, 0.0]))[1]
    return target_y - tip_offset_y


def grounded_root_y_balanced(torso_rot, left_rot, right_rot, target_y=0.0):
    y_left = grounded_root_y(torso_rot, left_rot, "Left Leg", target_y)
    y_right = grounded_root_y(torso_rot, right_rot, "Right Leg", target_y)
    return (y_left + y_right) / 2.0


def lerp3(a, b, f):
    return tuple(a[i] + f * (b[i] - a[i]) for i in range(3))


def lerp_legs(a, b, f):
    return {k: lerp3(a[k], b[k], f) for k in a}


def _kf(time, root_pos=(0.0, 3.0, 0.0), HumanoidRootPart=REST, Torso=REST,
        Head=REST, **legs_arms):
    d = {"time": time, "root_pos": root_pos, "HumanoidRootPart": HumanoidRootPart,
         "Torso": Torso, "Head": Head}
    d.update(legs_arms)
    return d


def _shift_kf(kf, dz, dt, root_part_override=None):
    """Copie d'une keyframe de punch_combo, translatee en temps (+dt) et
    en Z (+dz) -- JAMAIS en pose (Torso/Head/jambes/bras inchanges) ni en
    Y (deja calee par grounded_root_y() dans punch_combo, une translation
    Z ne change pas la hauteur du pied)."""
    nk = dict(kf)
    nk["time"] = kf["time"] + dt
    x, y, z = kf["root_pos"]
    nk["root_pos"] = (x, y, z + dz)
    if root_part_override is not None:
        nk["HumanoidRootPart"] = root_part_override
    return nk


def _mirror_kf(kf, reflect_c, dt, root_part_override):
    """Comme _shift_kf, mais REFLETE root_pos.Z (Z' = reflect_c - Z) au
    lieu de le translater -- pour rejouer une pose de punch_combo sur un
    personnage qui regarde dans l'AUTRE sens (HumanoidRootPart Y=180).
    Les poses locales (Torso/Head/jambes/bras) restent inchangees : une
    rotation locale ne depend pas du yaw du personnage qui la porte (voir
    docstring de module)."""
    nk = dict(kf)
    nk["time"] = kf["time"] + dt
    x, y, z = kf["root_pos"]
    nk["root_pos"] = (x, y, reflect_c - z)
    nk["HumanoidRootPart"] = root_part_override
    return nk


# -- Attente vivante (transfert de poids pied a pied, leger balancement
# du buste) -- retour utilisateur explicite : "ça manque de fluidite...
# les pieds tjrs trop encre dans le sol et pas en mouvement avec les
# geste". Un hold-and-snap plat (2 keyframes identiques tenues plusieurs
# secondes, comme l'ancien Beat 0/flex de victoire) est juste pour une
# CHARGE DE COUP (le principe reste valable, voir la lecon "hold-and-
# snap" du combo de poing) -- mais un combattant qui ATTEND (garde avant
# l'echange, pose de victoire tenue) n'est jamais parfaitement immobile,
# il bouge en continu (bounce sur les appuis, leger balancement) meme
# sans rien "faire". Deux vocabulaires distincts, pas une contradiction :
# un coil de frappe reste un vrai gel (tension qui monte), une attente
# est une oscillation continue de faible amplitude.
def _idle_stance_kf(t, root_pos, humanoid_root_part, base_torso, base_head, base_legs, base_arms, phase,
                     amp_leg=3.0, amp_torso=2.0):
    s, c = math.sin(phase), math.cos(phase)
    legs = {
        "Right Leg": (base_legs["Right Leg"][0], base_legs["Right Leg"][1], base_legs["Right Leg"][2] + amp_leg * s),
        "Left Leg": (base_legs["Left Leg"][0], base_legs["Left Leg"][1], base_legs["Left Leg"][2] - amp_leg * s),
    }
    torso = (base_torso[0], base_torso[1] + amp_torso * c, base_torso[2])
    root_y = grounded_root_y_balanced(torso, legs["Left Leg"], legs["Right Leg"])
    x, _, z = root_pos
    return _kf(t, root_pos=(x, root_y, z), HumanoidRootPart=humanoid_root_part,
               Torso=torso, Head=base_head, **legs, **base_arms)


def _idle_stance_span(t0, t1, root_pos, humanoid_root_part, base_torso, base_head, base_legs, base_arms,
                       period=0.55, phase0=0.0, amp_leg=3.0, amp_torso=2.0):
    """Genere une suite de keyframes (une par demi-cycle, soit ~period/2
    secondes) entre t0 et t1 au lieu d'un hold plat a 2 keyframes --
    voir note ci-dessus. `phase0` desynchronise Hero/Rival : deux
    combattants qui respirent exactement au meme rythme liraient comme
    un reflet l'un de l'autre plutot que deux individus."""
    # -- la PREMIERE et la DERNIERE keyframe reviennent exactement a la
    # pose de base (amplitude nulle), seul l'interieur du span oscille :
    # ce qui precede/suit un span d'attente est toujours la pose de base
    # a l'identique (arrivee sur la garde, garde de depart d'un echange,
    # etc.) -- sans ce bornage, le raccord ferait un petit saut visible a
    # la phase ou l'oscillation se trouvait par hasard.
    kfs = []
    half_period = period / 2.0
    n = max(1, round((t1 - t0) / half_period))
    for i in range(n + 1):
        t = t0 + (t1 - t0) * i / n
        phase = phase0 + (t - t0) / period * 2 * math.pi
        a_leg, a_torso = (0.0, 0.0) if i in (0, n) else (amp_leg, amp_torso)
        kfs.append(_idle_stance_kf(t, root_pos, humanoid_root_part, base_torso, base_head, base_legs, base_arms,
                                    phase, a_leg, a_torso))
    return kfs


# =======================================================================
# Disposition de l'arene
# =======================================================================
HOME_GAP = 5.4                              # identique a l'ecart attaquant/mannequin de punch_combo (reutilisation exacte, voir docstring)
HERO_HOME_Z = -14.0                         # cote trone (Z le moins negatif)
RIVAL_HOME_Z = HERO_HOME_Z - HOME_GAP       # -19.4, plus loin du trone

OFFSET_Z = HERO_HOME_Z - pc.ATTACKER_Z0     # -12.8 : translation qui envoie TOUT punch_combo (attaquant ET mannequin) dans l'arene, sans recalibrage (voir docstring)
REFLECT_C = RIVAL_HOME_Z + pc.ATTACKER_Z0   # -20.6 : reflexion qui envoie une pose de punch_combo "a l'envers" (Rival, yaw=180) en gardant le meme ecart de contact

RIVAL_FACE = (0, 180, 0)

PILLAR_X = 3.4
PILLAR_Z = RIVAL_HOME_Z - 2.2
PILLAR_POS = (PILLAR_X, 0.0, PILLAR_Z)   # base au sol -- voir props_battle.py pour la geometrie


# =======================================================================
# Beat 0 -- garde, face a face (T0_END secondes)
# =======================================================================
T0_END = _fr(150)   # 5.0s -- vraie tension avant l'echange, pas un simple point de passage


def _beat0():
    # -- garde tenue 5s : jamais un hold plat (voir _idle_stance_span) --
    # Hero et Rival bougent en continu, a des cadences legerement
    # differentes (0.58s/0.50s) et des phases opposees, pour ne pas
    # lire comme deux miroirs synchronises.
    hero = _idle_stance_span(0.00, T0_END, (0, 0, HERO_HOME_Z), REST,
                              pc._READY_TORSO, pc._READY_HEAD, pc._READY_LEGS, pc._READY_ARMS,
                              period=0.58, phase0=0.0)
    rival = _idle_stance_span(0.00, T0_END, (0, 0, RIVAL_HOME_Z), RIVAL_FACE,
                               pc._READY_TORSO, pc._READY_HEAD, pc._READY_LEGS, pc._READY_ARMS,
                               period=0.50, phase0=math.pi)
    return hero, rival


# =======================================================================
# Beat 1 -- Rival ouvre avec un jab (reutilise punch_combo, REFLETE --
# voir _mirror_kf) ; Hero encaisse et secoue la tete (reutilise la
# reaction du mannequin de punch_combo, REFLETEE elle aussi -- voir
# docstring de module : REFLECT_C envoie punch_combo.ATTACKER_Z0 sur
# RIVAL_HOME_Z ET punch_combo.DUMMY_Z sur HERO_HOME_Z simultanement,
# aucune mesure separee necessaire).
# =======================================================================
BEAT1_START = T0_END
BEAT1_SPAN = pc.CROSS_WINDUP_T           # reutilise le rythme jab->retract de punch_combo tel quel
BEAT1_END = BEAT1_START + BEAT1_SPAN
RECOVERY1 = 1.0
BEAT2_START = BEAT1_END + RECOVERY1


def _beat1():
    atk_kf = pc.attacker_combo()[0]
    dum_kf = pc.dummy_combo_reaction()[0]

    rival = [_mirror_kf(k, REFLECT_C, BEAT1_START, RIVAL_FACE)
             for k in atk_kf if k["time"] <= pc.CROSS_WINDUP_T + 1e-9]
    hero = [_mirror_kf(k, REFLECT_C, BEAT1_START, REST)
            for k in dum_kf if k["time"] <= pc.JAB_T + 0.16 + 1e-9]
    return hero, rival


# =======================================================================
# Beat 2 -- Hero repond avec le combo complet jab/cross/hook (reutilise
# punch_combo tel quel, TRANSLATE de OFFSET_Z -- jamais miroir : Hero et
# le mannequin d'origine regardent deja dans le meme sens, voir docstring
# de module). AUCUNE valeur de pose ni de contact n'est redevinee : cette
# section est le combo deja calibre/verifie de r6_hit_combo, juste
# deplace dans l'arene.
# =======================================================================
def _beat2():
    atk_kf = pc.attacker_combo()[0]
    dum_kf = pc.dummy_combo_reaction()[0]
    hero = [_shift_kf(k, OFFSET_Z, BEAT2_START) for k in atk_kf]
    rival = [_shift_kf(k, OFFSET_Z, BEAT2_START) for k in dum_kf]
    # -- pc.dummy_combo_reaction() tient sa pose DAZED_* finale a Y=
    # GROUND_Y plat (jamais calee par cinematique directe -- ecrite pour
    # un mannequin statique, jamais scrutinee cote pieds, voir
    # DAZED_GROUNDED_ROOT_Y ci-dessus) : Rival est ici un combattant
    # actif qui TIENT cette pose plusieurs secondes, on regrounde donc
    # seulement ce hold final (le reste du combo -- jab/cross/hook,
    # whiplash -- reste intact, translation pure, calibration inchangee).
    for k in rival:
        if k["Torso"] == pc.DAZED_TORSO:
            x, _, z = k["root_pos"]
            k["root_pos"] = (x, DAZED_GROUNDED_ROOT_Y, z)
    return hero, rival


BEAT2_END = BEAT2_START + pc.DURATION


# =======================================================================
# Beat R -- Rival se relance (encaisse encore le hook -- DAZED_* -- tenu
# reellement, se retourne, se replace en garde) pendant que Hero se
# rerepositionne a distance de combat (HERO_HOME_Z) : AUCUN contact a
# calibrer ici (aucun coup ne part), seulement du placement/de la pose --
# donne au combat une vraie respiration entre deux echanges plutot qu'un
# enchainement mecanique beat-apres-beat, et sert de mise en garde
# commune avant le grand crochet de Beat 3 (la pose finale de Rival ET
# celle de Hero coincident exactement avec le premier keyframe de chacun
# dans _beat3(), voir plus bas -- raccord verifie, pas suppose).
# =======================================================================
REGROUP_START = BEAT2_END + 0.3
REGROUP_HOLD_T = REGROUP_START + 0.7
REGROUP_TURN_T = REGROUP_HOLD_T + 0.5
REGROUP_SQUARE_T = REGROUP_TURN_T + 0.4

REGROUP_RIVAL_TURN_TORSO = (10, 0, -8)
REGROUP_RIVAL_TURN_HEAD = (6, 10, 0)
REGROUP_RIVAL_TURN_LEGS = {"Right Leg": (4, 0, 4), "Left Leg": (4, 0, -4)}
REGROUP_RIVAL_TURN_ARMS = {"Right Arm": (20, 0, 10), "Left Arm": (20, 0, -10)}
REGROUP_RIVAL_TURN_Z = -20.5   # revient partiellement vers Hero en se retournant, pas encore a RIVAL_HOME_Z

# -- pc.DAZED_* est utilise a l'origine (r6_hit_combo) par un MANNEQUIN
# statique jamais scrutine pour le placement des pieds (foot_check.py de
# r6_hit_combo ne verifie QUE l'attaquant, jamais le mannequin -- voir
# calibrate_battle.py/foot_check_battle.py de ce prototype, qui l'a
# revele : ~0.28-0.35 stud de flottement avec le root_pos.Y=GROUND_Y
# fixe d'origine). Rival est ici un combattant ACTIF dont les appuis se
# voient tenus plusieurs secondes (retour recurrent de l'utilisateur sur
# le jeu de jambes) : on regrounde cette pose par cinematique directe
# plutot que de reutiliser le Y plat d'origine.
DAZED_GROUNDED_ROOT_Y = grounded_root_y_balanced(pc.DAZED_TORSO, pc.DAZED_LEGS["Left Leg"], pc.DAZED_LEGS["Right Leg"])


def _beat_regroup():
    hero = [
        _kf(REGROUP_START, root_pos=(0, pc.FINAL_ROOT_Y, -19.2033), Torso=pc.FINAL_TORSO,
            Head=pc.FINAL_HEAD, **pc._READY_LEGS, **{"Left Arm": (10, 0, 12), "Right Arm": (10, 0, -12)}),
        _kf(REGROUP_HOLD_T, root_pos=(0, pc.FINAL_ROOT_Y, -16.5), Torso=pc.FINAL_TORSO,
            Head=pc.FINAL_HEAD, **pc._READY_LEGS, **{"Left Arm": (10, 0, 12), "Right Arm": (10, 0, -12)}),
        _kf(REGROUP_TURN_T, root_pos=(0, pc._READY_ROOT_Y, HERO_HOME_Z), Torso=pc._READY_TORSO,
            Head=pc._READY_HEAD, **pc._READY_LEGS, **pc._READY_ARMS),
        _kf(REGROUP_SQUARE_T, root_pos=(0, pc._READY_ROOT_Y, HERO_HOME_Z), Torso=pc._READY_TORSO,
            Head=pc._READY_HEAD, **pc._READY_LEGS, **pc._READY_ARMS),
    ]
    # -- hebete, Rival TITUBE plutot que de rester fige (meme retour
    # utilisateur que Beat 0/flex : jamais un hold plat) -- amplitude et
    # cadence plus marquees qu'une attente normale, ca doit lire comme un
    # vacillement, pas une garde.
    rival = _idle_stance_span(REGROUP_START, REGROUP_HOLD_T, (0, 0, -22.4), (0, 140, 0),
                               pc.DAZED_TORSO, pc.DAZED_HEAD, pc.DAZED_LEGS, pc.DAZED_ARMS,
                               period=0.40, phase0=0.0, amp_leg=5.0, amp_torso=4.0)
    rival += [
        _kf(REGROUP_TURN_T, root_pos=(0, GROUND_Y, REGROUP_RIVAL_TURN_Z), HumanoidRootPart=RIVAL_FACE,
            Torso=REGROUP_RIVAL_TURN_TORSO, Head=REGROUP_RIVAL_TURN_HEAD,
            **REGROUP_RIVAL_TURN_LEGS, **REGROUP_RIVAL_TURN_ARMS),
        _kf(REGROUP_SQUARE_T, root_pos=(0, pc._READY_ROOT_Y, RIVAL_HOME_Z), HumanoidRootPart=RIVAL_FACE,
            Torso=pc._READY_TORSO, Head=pc._READY_HEAD, **pc._READY_LEGS, **pc._READY_ARMS),
    ]
    return hero, rival


# =======================================================================
# Beat 3 -- Rival charge un grand crochet telegraphie (hold-and-snap,
# amplitude la plus grande du combat -- il doit se lire comme "en train
# de rater"), Hero ESQUIVE (pas de contact a calibrer, juste s'assurer
# que le poing NE touche PAS), puis contre-attaque au COUP DE PIED
# circulaire (nouveau type de coup -- "plus que du combo poing", retour
# utilisateur) qui projette Rival contre le PILIER destructible.
# =======================================================================
BEAT3_START = REGROUP_SQUARE_T + 0.3

HM_WINDUP_T = BEAT3_START + 0.35
HM_COIL_T = BEAT3_START + 0.75
HM_HOLD_T = BEAT3_START + 1.10          # hold telegraphe -- lisible, cf. lecon "hold-and-snap"
HM_STRIKE_T = HM_HOLD_T + 0.12          # lacher plus lent qu'un vrai coup (grand crochet sauvage, pas un jab)
RIVAL_HAYMAKER_LUNGE_Z = HERO_HOME_Z - 1.0   # depasse legerement la position de Hero -- Rival est en extension, expose

HM_COIL_TORSO = (18, 60, 6)             # charge large (Y positif, bras droit) -- plus grand que le hook (46) : un vrai grand crochet, pas un coup mesure
HM_COIL_HEAD = (10, 30, 0)
HM_COIL_LEGS = {"Right Leg": (-16, 0, -20), "Left Leg": (16, 0, 22)}
HM_COIL_RIGHT_ARM = (95, 0, -30)
HM_COIL_LEFT_ARM = (20, 0, 30)
HM_COIL_ROOT_Y = grounded_root_y_balanced(HM_COIL_TORSO, HM_COIL_LEGS["Left Leg"], HM_COIL_LEGS["Right Leg"])

HM_STRIKE_TORSO = (-16, -62, -4)
HM_STRIKE_HEAD = (14, -28, 0)
HM_STRIKE_LEGS = {"Right Leg": (12, 0, 18), "Left Leg": (-14, 0, -16)}
HM_STRIKE_RIGHT_ARM = (100, 0, 40)      # grand balayage complet -- Z bascule de -30 a 40, meme principe de renversement que le combo
HM_STRIKE_LEFT_ARM = (18, 0, -32)
HM_STRIKE_ROOT_Y = grounded_root_y_balanced(HM_STRIKE_TORSO, HM_STRIKE_LEGS["Left Leg"], HM_STRIKE_LEGS["Right Leg"])

# -- Esquive de Hero : pas chasse lateral + buste qui se derobe, tenu
# pendant TOUT le telegraphe + le lacher (le coup passe dans le vide) --
DODGE_START_T = HM_COIL_T - 0.10
DODGE_HOLD_T = HM_STRIKE_T + 0.15
DODGE_RECOVER_T = DODGE_HOLD_T + 0.25
DODGE_X = 2.4
DODGE_TORSO = (14, 0, -18)   # se derobe lateralement + leger buste bas
DODGE_HEAD = (10, 8, -10)
DODGE_LEGS = {"Right Leg": (18, 0, 22), "Left Leg": (-6, 0, -10)}
DODGE_ARMS = {"Right Arm": (30, 0, -14), "Left Arm": (30, 0, 14)}
DODGE_ROOT_Y = grounded_root_y_balanced(DODGE_TORSO, DODGE_LEGS["Left Leg"], DODGE_LEGS["Right Leg"])

# -- Coup de pied circulaire (Right Leg) : chambrage puis extension
# laterale complete, snap bref comme les coups de poing (meme principe,
# nouvelle articulation). Jambe d'appui (Left) calee au sol par
# grounded_root_y (elle seule porte le poids, la jambe qui frappe quitte
# le sol -- pas de moyenne ici).
KICK_WINDUP_T = DODGE_RECOVER_T + 0.05
KICK_HOLD_T = KICK_WINDUP_T + 0.22
KICK_STRIKE_T = KICK_HOLD_T + _fr(2)

KICK_WINDUP_TORSO = (8, -10, -10)
KICK_WINDUP_HEAD = (6, -6, 0)
KICK_WINDUP_LEGS = {"Right Leg": (58, 0, -24), "Left Leg": (2, 0, -4)}
KICK_WINDUP_ARMS = {"Right Arm": (20, 0, -16), "Left Arm": (34, 0, 20)}
KICK_WINDUP_ROOT_Y = grounded_root_y(KICK_WINDUP_TORSO, KICK_WINDUP_LEGS["Left Leg"], "Left Leg")

# Jambe qui frappe : X=120 (au-dela de l'horizontale -- coup de pied
# haut, cote/tronc), Z bascule de -24 (chambre vers l'interieur) a +4
# (balaie vers l'exterieur) -- meme PRINCIPE de renversement d'axe que
# le reste du projet, mais amplitude de renversement volontairement
# REDUITE (comme pour les jambes du combo de poing, retour "axes des
# jambes" -- voir README de r6_hit_combo) : une recherche numerique
# (voir calibrate_battle.py et le README, section "Calibration du coup
# de pied") a balaye Torso/jambe d'appui/jambe frappante/avancee pour
# trouver l'ecart de contact minimal SOUS la contrainte du renversement
# de signe -- ecart plancher mesure ~0.80 stud (vs 0.37-0.49 pour les
# poings : une jambe sans genou, sans avancee du bassin, ne peut pas
# egaler la precision d'un bras, ecart documente, pas cache).
KICK_STRIKE_TORSO = (20, 20, -5)
KICK_STRIKE_HEAD = (16, 16, 0)
KICK_STRIKE_LEGS = {"Right Leg": (120, 0, 4), "Left Leg": (15, 0, 0)}
KICK_STRIKE_ARMS = {"Right Arm": (26, 0, -20), "Left Arm": (40, 0, 26)}
# Avancee calibree par mesure directe (voir calibrate_battle.py) : le
# meilleur ecart trouve n'exige AUCUNE avancee (KICK_LUNGE_Z=HERO_HOME_Z)
# -- toute la portee vient de l'extension de la jambe, pas d'un pas en
# plus (coherent avec Rival deja en extension/expose a 1 stud seulement,
# voir RIVAL_HAYMAKER_LUNGE_Z).
KICK_LUNGE_Z = HERO_HOME_Z
KICK_STRIKE_ROOT_Y = grounded_root_y(KICK_STRIKE_TORSO, KICK_STRIKE_LEGS["Left Leg"], "Left Leg")

# -- Reaction de Rival au coup de pied : projete lateralement (X) ET en
# profondeur (Z) jusqu'au pilier -- vol bref (hop en Y, meme principe que
# HOOK_HOP_Y du combo), le pilier se brise au moment exact de l'impact
# (cote lecteur, voir PILLAR_HIT_T plus bas).
KICK_HIT_TORSO = (-22, -50, 30)
KICK_HIT_HEAD = (-28, -40, 10)
KICK_HIT_LEGS = {"Right Leg": (-24, 0, 30), "Left Leg": (18, 0, -26)}
KICK_HIT_ARMS = {"Right Arm": (140, 0, -60), "Left Arm": (150, 0, 80)}
KICK_FLIGHT_TORSO = (-26, -55, 34)
KICK_FLIGHT_HEAD = (-30, -44, 12)
KICK_HOP_Y = GROUND_Y + 0.55
CRUMPLE_TORSO = (48, -30, 20)
CRUMPLE_HEAD = (30, -20, 10)
CRUMPLE_LEGS = {"Right Leg": (70, 0, 24), "Left Leg": (60, 0, -30)}
CRUMPLE_ARMS = {"Right Arm": (60, 0, -20), "Left Arm": (56, 0, 24)}
CRUMPLE_ROOT_Y = 1.55   # affaisse pres du pilier -- pas au sol plat (le rig n'a pas de genou pour s'aplatir), voir README

PILLAR_HIT_T = KICK_STRIKE_T + 0.42   # instant ou Rival atteint le pilier -- le lecteur y declenche le bris


def _beat3():
    hero = [
        _kf(HM_WINDUP_T, root_pos=(0, pc._READY_ROOT_Y, HERO_HOME_Z), Torso=pc._READY_TORSO,
            Head=pc._READY_HEAD, **pc._READY_LEGS, **pc._READY_ARMS),
        _kf(DODGE_START_T, root_pos=(DODGE_X, DODGE_ROOT_Y, HERO_HOME_Z), Torso=DODGE_TORSO,
            Head=DODGE_HEAD, **DODGE_LEGS, **DODGE_ARMS),
        _kf(DODGE_HOLD_T, root_pos=(DODGE_X, DODGE_ROOT_Y, HERO_HOME_Z), Torso=DODGE_TORSO,
            Head=DODGE_HEAD, **DODGE_LEGS, **DODGE_ARMS),
        _kf(DODGE_RECOVER_T, root_pos=(0.6, pc._READY_ROOT_Y, HERO_HOME_Z), Torso=pc._READY_TORSO,
            Head=pc._READY_HEAD, **pc._READY_LEGS, **pc._READY_ARMS),
        _kf(KICK_WINDUP_T, root_pos=(0, KICK_WINDUP_ROOT_Y, HERO_HOME_Z), Torso=KICK_WINDUP_TORSO,
            Head=KICK_WINDUP_HEAD, **KICK_WINDUP_LEGS, **KICK_WINDUP_ARMS),
        _kf(KICK_HOLD_T, root_pos=(0, KICK_WINDUP_ROOT_Y, HERO_HOME_Z), Torso=KICK_WINDUP_TORSO,
            Head=KICK_WINDUP_HEAD, **KICK_WINDUP_LEGS, **KICK_WINDUP_ARMS),
        _kf(KICK_STRIKE_T, root_pos=(0, KICK_STRIKE_ROOT_Y, KICK_LUNGE_Z), Torso=KICK_STRIKE_TORSO,
            Head=KICK_STRIKE_HEAD, **KICK_STRIKE_LEGS, **KICK_STRIKE_ARMS),
        _kf(PILLAR_HIT_T, root_pos=(0, GROUND_Y, KICK_LUNGE_Z + 0.3), Torso=pc.RECOVER_TORSO,
            Head=pc.RECOVER_HEAD, **pc._READY_LEGS,
            **{"Right Arm": pc.RECOVER_RIGHT_ARM, "Left Arm": pc.RECOVER_LEFT_ARM}),
    ]
    rival = [
        _kf(HM_WINDUP_T, root_pos=(0, pc._READY_ROOT_Y, RIVAL_HOME_Z), HumanoidRootPart=RIVAL_FACE,
            Torso=pc._READY_TORSO, Head=pc._READY_HEAD, **pc._READY_LEGS, **pc._READY_ARMS),
        _kf(HM_COIL_T, root_pos=(0, HM_COIL_ROOT_Y, RIVAL_HOME_Z), HumanoidRootPart=RIVAL_FACE,
            Torso=HM_COIL_TORSO, Head=HM_COIL_HEAD, **HM_COIL_LEGS,
            **{"Right Arm": HM_COIL_RIGHT_ARM, "Left Arm": HM_COIL_LEFT_ARM}),
        _kf(HM_HOLD_T, root_pos=(0, HM_COIL_ROOT_Y, RIVAL_HOME_Z), HumanoidRootPart=RIVAL_FACE,
            Torso=HM_COIL_TORSO, Head=HM_COIL_HEAD, **HM_COIL_LEGS,
            **{"Right Arm": HM_COIL_RIGHT_ARM, "Left Arm": HM_COIL_LEFT_ARM}),
        _kf(HM_STRIKE_T, root_pos=(0, HM_STRIKE_ROOT_Y, RIVAL_HAYMAKER_LUNGE_Z), HumanoidRootPart=RIVAL_FACE,
            Torso=HM_STRIKE_TORSO, Head=HM_STRIKE_HEAD, **HM_STRIKE_LEGS,
            **{"Right Arm": HM_STRIKE_RIGHT_ARM, "Left Arm": HM_STRIKE_LEFT_ARM}),
        # -- encaisse le coup de pied : snap, puis projection (hop en Y,
        # deplacement X+Z) jusqu'au pilier --
        _kf(KICK_STRIKE_T, root_pos=(0, GROUND_Y, RIVAL_HAYMAKER_LUNGE_Z), HumanoidRootPart=RIVAL_FACE,
            Torso=KICK_HIT_TORSO, Head=KICK_HIT_HEAD, **KICK_HIT_LEGS, **KICK_HIT_ARMS),
        _kf(KICK_STRIKE_T + 0.10, root_pos=((PILLAR_X + RIVAL_HAYMAKER_LUNGE_Z * 0) * 0 + PILLAR_X * 0.35,
                                              KICK_HOP_Y, RIVAL_HAYMAKER_LUNGE_Z - (RIVAL_HAYMAKER_LUNGE_Z - PILLAR_Z) * 0.35),
            HumanoidRootPart=RIVAL_FACE, Torso=KICK_FLIGHT_TORSO, Head=KICK_FLIGHT_HEAD,
            **KICK_HIT_LEGS, **KICK_HIT_ARMS),
        _kf(PILLAR_HIT_T, root_pos=(PILLAR_X, CRUMPLE_ROOT_Y, PILLAR_Z), HumanoidRootPart=RIVAL_FACE,
            Torso=CRUMPLE_TORSO, Head=CRUMPLE_HEAD, **CRUMPLE_LEGS, **CRUMPLE_ARMS),
        _kf(PILLAR_HIT_T + 0.55, root_pos=(PILLAR_X, CRUMPLE_ROOT_Y, PILLAR_Z), HumanoidRootPart=RIVAL_FACE,
            Torso=CRUMPLE_TORSO, Head=CRUMPLE_HEAD, **CRUMPLE_LEGS, **CRUMPLE_ARMS),
    ]
    return hero, rival


BEAT3_END = PILLAR_HIT_T + 0.55


# =======================================================================
# Beat 4 -- Rival se redresse en titubant vers le centre (retour a X=0,
# plus pres de Hero), Hero acheve avec un dernier coup (vocabulaire du
# hook, relance -- le "finisher") -- Rival s'effondre, KO, pour le reste
# de la scene.
# =======================================================================
BEAT4_START = BEAT3_END + 0.6
STUMBLE_T = BEAT4_START + 0.85
RIVAL_STUMBLE_Z = RIVAL_HOME_Z + 1.5   # se rapproche un peu du centre en titubant

FINISH_WINDUP_T = STUMBLE_T + 0.30
FINISH_COIL_T = FINISH_WINDUP_T + 0.30
FINISH_HOLD_T = FINISH_COIL_T + _fr(6)
FINISH_STRIKE_T = FINISH_HOLD_T + _fr(3) - SNAP + SNAP  # snap final (1 frame apres hipdrive, cf. hip-drive ci-dessous)
FINISH_HIPDRIVE_T = FINISH_HOLD_T + _fr(2)
FINISH_STRIKE_T = FINISH_HOLD_T + _fr(3)

FINISH_WINDUP_TORSO = (10, 20, -2)
FINISH_WINDUP_HEAD = (6, 12, 0)
FINISH_WINDUP_LEGS = {"Right Leg": (10, 0, 10), "Left Leg": (12, 0, -10)}
FINISH_WINDUP_LEFT_ARM = (55, 0, 20)
FINISH_WINDUP_RIGHT_ARM = (60, 0, -12)
FINISH_WINDUP_ROOT_Y = grounded_root_y_balanced(FINISH_WINDUP_TORSO, FINISH_WINDUP_LEGS["Left Leg"], FINISH_WINDUP_LEGS["Right Leg"])

FINISH_COIL_TORSO = (16, -46, -6)
FINISH_COIL_HEAD = (10, -26, 0)
FINISH_COIL_LEGS = {"Right Leg": (16, 0, 15), "Left Leg": (9, 0, -16)}
FINISH_COIL_LEFT_ARM = (80, 0, -84)
FINISH_COIL_RIGHT_ARM = (28, 0, -18)
FINISH_COIL_ROOT_Y = grounded_root_y_balanced(FINISH_COIL_TORSO, FINISH_COIL_LEGS["Left Leg"], FINISH_COIL_LEGS["Right Leg"])

FINISH_STRIKE_TORSO = (-12, 52, 3)
FINISH_STRIKE_HEAD = (14, 25, 0)
FINISH_STRIKE_LEGS = {"Right Leg": (9, 0, -12), "Left Leg": (15, 0, 14)}
FINISH_STRIKE_LEFT_ARM = (90, 0, 95)
FINISH_STRIKE_RIGHT_ARM = (16, 0, -22)
# Avancee calibree (voir calibrate_battle.py) contre la position de
# titubation de Rival (RIVAL_STUMBLE_Z), pas devinee.
FINISH_LUNGE_Z = -16.9

_FF_BODY, _FF_ARM = 0.90, 0.18
FINISH_HIPDRIVE_TORSO = lerp3(FINISH_COIL_TORSO, FINISH_STRIKE_TORSO, _FF_BODY)
FINISH_HIPDRIVE_HEAD = lerp3(FINISH_COIL_HEAD, FINISH_STRIKE_HEAD, _FF_BODY)
FINISH_HIPDRIVE_LEGS = lerp_legs(FINISH_COIL_LEGS, FINISH_STRIKE_LEGS, _FF_BODY)
FINISH_HIPDRIVE_LEFT_ARM = lerp3(FINISH_COIL_LEFT_ARM, FINISH_STRIKE_LEFT_ARM, _FF_ARM)
FINISH_HIPDRIVE_RIGHT_ARM = lerp3(FINISH_COIL_RIGHT_ARM, FINISH_STRIKE_RIGHT_ARM, _FF_BODY)
FINISH_HIPDRIVE_ROOT_Z = HERO_HOME_Z + _FF_BODY * (FINISH_LUNGE_Z - HERO_HOME_Z)
FINISH_HIPDRIVE_ROOT_Y = grounded_root_y(FINISH_HIPDRIVE_TORSO, FINISH_HIPDRIVE_LEGS["Left Leg"], "Left Leg")

KO_HIT_TORSO = (-26, 55, -14)
KO_HIT_HEAD = (-34, 60, -8)
KO_HIT_LEGS = {"Right Leg": (-22, 0, 24), "Left Leg": (-10, 0, -26)}
KO_HIT_ARMS = {"Right Arm": (160, 0, 75), "Left Arm": (155, 0, -90)}

COLLAPSE_TORSO = (72, 10, -8)
COLLAPSE_HEAD = (40, 6, 0)
COLLAPSE_LEGS = {"Right Leg": (78, 0, 10), "Left Leg": (74, 0, -14)}
COLLAPSE_ARMS = {"Right Arm": (50, 0, 18), "Left Arm": (46, 0, -20)}
COLLAPSE_ROOT_Y = 1.35   # effondre -- torse et jambes pitches vers l'avant (pas de genou pour s'aplatir au sol, voir README)


def _beat4():
    hero = [
        _kf(FINISH_WINDUP_T, root_pos=(0, FINISH_WINDUP_ROOT_Y, HERO_HOME_Z), Torso=FINISH_WINDUP_TORSO,
            Head=FINISH_WINDUP_HEAD, **FINISH_WINDUP_LEGS,
            **{"Left Arm": FINISH_WINDUP_LEFT_ARM, "Right Arm": FINISH_WINDUP_RIGHT_ARM}),
        _kf(FINISH_COIL_T, root_pos=(0, FINISH_COIL_ROOT_Y, HERO_HOME_Z), Torso=FINISH_COIL_TORSO,
            Head=FINISH_COIL_HEAD, **FINISH_COIL_LEGS,
            **{"Left Arm": FINISH_COIL_LEFT_ARM, "Right Arm": FINISH_COIL_RIGHT_ARM}),
        _kf(FINISH_HOLD_T, root_pos=(0, FINISH_COIL_ROOT_Y, HERO_HOME_Z), Torso=FINISH_COIL_TORSO,
            Head=FINISH_COIL_HEAD, **FINISH_COIL_LEGS,
            **{"Left Arm": FINISH_COIL_LEFT_ARM, "Right Arm": FINISH_COIL_RIGHT_ARM}),
        _kf(FINISH_HIPDRIVE_T, root_pos=(0, FINISH_HIPDRIVE_ROOT_Y, FINISH_HIPDRIVE_ROOT_Z), Torso=FINISH_HIPDRIVE_TORSO,
            Head=FINISH_HIPDRIVE_HEAD, **FINISH_HIPDRIVE_LEGS,
            **{"Left Arm": FINISH_HIPDRIVE_LEFT_ARM, "Right Arm": FINISH_HIPDRIVE_RIGHT_ARM}),
        _kf(FINISH_STRIKE_T, root_pos=(0, GROUND_Y, FINISH_LUNGE_Z), Torso=FINISH_STRIKE_TORSO,
            Head=FINISH_STRIKE_HEAD, **FINISH_STRIKE_LEGS,
            **{"Left Arm": FINISH_STRIKE_LEFT_ARM, "Right Arm": FINISH_STRIKE_RIGHT_ARM}),
    ]
    rival = [
        _kf(BEAT4_START, root_pos=(PILLAR_X, CRUMPLE_ROOT_Y, PILLAR_Z), HumanoidRootPart=RIVAL_FACE,
            Torso=CRUMPLE_TORSO, Head=CRUMPLE_HEAD, **CRUMPLE_LEGS, **CRUMPLE_ARMS),
        _kf(STUMBLE_T, root_pos=(0, DAZED_GROUNDED_ROOT_Y, RIVAL_STUMBLE_Z), HumanoidRootPart=RIVAL_FACE,
            Torso=pc.DAZED_TORSO, Head=pc.DAZED_HEAD, **pc.DAZED_LEGS, **pc.DAZED_ARMS),
        _kf(FINISH_STRIKE_T - 0.03, root_pos=(0, DAZED_GROUNDED_ROOT_Y, RIVAL_STUMBLE_Z), HumanoidRootPart=RIVAL_FACE,
            Torso=pc.DAZED_TORSO, Head=pc.DAZED_HEAD, **pc.DAZED_LEGS, **pc.DAZED_ARMS),
        _kf(FINISH_STRIKE_T, root_pos=(0, GROUND_Y, RIVAL_STUMBLE_Z), HumanoidRootPart=RIVAL_FACE,
            Torso=KO_HIT_TORSO, Head=KO_HIT_HEAD, **KO_HIT_LEGS, **KO_HIT_ARMS),
        _kf(FINISH_STRIKE_T + 0.30, root_pos=(0, GROUND_Y, RIVAL_STUMBLE_Z - 1.6), HumanoidRootPart=(0, 160, 0),
            Torso=KO_HIT_TORSO, Head=KO_HIT_HEAD, **KO_HIT_LEGS, **KO_HIT_ARMS),
        _kf(FINISH_STRIKE_T + 0.60, root_pos=(0, COLLAPSE_ROOT_Y, RIVAL_STUMBLE_Z - 2.1), HumanoidRootPart=(0, 150, 0),
            Torso=COLLAPSE_TORSO, Head=COLLAPSE_HEAD, **COLLAPSE_LEGS, **COLLAPSE_ARMS),
    ]
    return hero, rival


BEAT4_END = FINISH_STRIKE_T + 0.60


# =======================================================================
# Beat 5 -- victoire (flex tenu), demi-tour, puis marche vers le trone.
# Le demi-tour REUTILISE explicitement la meme technique en 3 etapes que
# throne_sequence.climb_stairs() (tete en avance/"spotting", rotation du
# corps pendant que la jambe libre est encore en l'air, jambe replantee
# puis torse qui rattrape en dernier) : c'est la coherence de style
# demandee par l'utilisateur ("mets l'animation en cohérence du trone et
# de la couronne"), pas une redecouverte independante. Meme principe pour
# la marche : bras FIGES pendant toute la locomotion (climb_stairs ne les
# fait jamais osciller), pour que le raccord avec le premier keyframe de
# climb_stairs() soit un vrai prolongement de la meme grammaire de
# mouvement, pas juste une position qui coincide par hasard.
# =======================================================================
BREATH_T = FINISH_STRIKE_T + 0.35   # tient le lacher du finisher un instant -- le combat s'arrete net, pas de retour immediat au calme
SETTLE_T = BREATH_T + 0.35
FLEX_T = SETTLE_T + 0.30
FLEX_HOLD_T = FLEX_T + 3.50          # vrai hold (cf. lecon "hold-and-snap") -- le flex doit se lire, pas juste passer

SETTLE_TORSO = (-4, 0, 0)
SETTLE_HEAD = (-3, 0, 0)
SETTLE_LEGS = {"Right Leg": (4, 0, 6), "Left Leg": (5, 0, -5)}
SETTLE_LEFT_ARM = (30, 0, 14)
SETTLE_RIGHT_ARM = (34, 0, -12)
SETTLE_ROOT_Y = grounded_root_y_balanced(SETTLE_TORSO, SETTLE_LEGS["Left Leg"], SETTLE_LEGS["Right Leg"])

FLEX_TORSO = (-16, 0, 0)
FLEX_HEAD = (-12, 0, 0)
FLEX_LEGS = {"Right Leg": (-4, 0, 10), "Left Leg": (-4, 0, -10)}
FLEX_LEFT_ARM = (150, 0, 20)
FLEX_RIGHT_ARM = (150, 0, -20)

# -- bras de marche, IDENTIQUES a ceux de climb_stairs() pendant toute la
# locomotion (montee ET demi-tour) -- jamais d'oscillation de bras, meme
# convention reprise a l'identique ici.
WALK_ARMS = {"Right Arm": (2, 0, -5), "Left Arm": (2, 0, 5)}
WALK_TORSO_X = -6    # identique au Torso.X de climb_stairs (_PROUD_TORSO_X) -- meme port de tete/epaules
WALK_HEAD = (-6, 0, 0)   # identique a throne_sequence._PROUD_HEAD

TURN_SPAN = ts.TURN_T
TURN_START = FLEX_HOLD_T
TURN_T1 = TURN_START + TURN_SPAN * 0.28
TURN_T2 = TURN_START + TURN_SPAN * 0.62
TURN_T3 = TURN_START + TURN_SPAN * 0.85
TURN_END = TURN_START + TURN_SPAN
TURN_Z = FINISH_LUNGE_Z

WALK_N = 17
WALK_STEP_T = 0.55
WALK_START = TURN_END
WALK_END = WALK_START + WALK_N * WALK_STEP_T
WALK_Z0 = TURN_Z
WALK_Z1 = ts._CLIMB_Z0     # raccord exact avec le premier keyframe de throne_sequence.climb_stairs()
WALK_BOB = 0.07


def _beat5():
    hero = [
        _kf(BREATH_T, root_pos=(0, GROUND_Y, FINISH_LUNGE_Z), Torso=FINISH_STRIKE_TORSO,
            Head=FINISH_STRIKE_HEAD, **FINISH_STRIKE_LEGS,
            **{"Left Arm": FINISH_STRIKE_LEFT_ARM, "Right Arm": FINISH_STRIKE_RIGHT_ARM}),
        _kf(SETTLE_T, root_pos=(0, SETTLE_ROOT_Y, FINISH_LUNGE_Z), Torso=SETTLE_TORSO,
            Head=SETTLE_HEAD, **SETTLE_LEGS,
            **{"Left Arm": SETTLE_LEFT_ARM, "Right Arm": SETTLE_RIGHT_ARM}),
    ]
    # -- flex de victoire tenu ~3.5s : jamais un hold plat non plus (meme
    # retour utilisateur que Beat 0) -- oscillation d'attente entre
    # l'arrivee (FLEX_T) et le debut du demi-tour (FLEX_HOLD_T), bornee
    # a la pose FLEX_* exacte aux deux bouts (voir _idle_stance_span).
    hero += _idle_stance_span(FLEX_T, FLEX_HOLD_T, (0, 0, FINISH_LUNGE_Z), REST,
                               FLEX_TORSO, FLEX_HEAD, FLEX_LEGS,
                               {"Left Arm": FLEX_LEFT_ARM, "Right Arm": FLEX_RIGHT_ARM},
                               period=0.65, phase0=0.0, amp_leg=2.5, amp_torso=1.5)
    hero += [
        # -- demi-tour, meme technique/proportions que climb_stairs() mais
        # en sens INVERSE (Hero part face -Z vers Rival vaincu, doit finir
        # face +Z vers le trone) : 0 -> 0 -> 90 -> 160 -> 180 au lieu de
        # 180 -> 180 -> 90 -> 20 -> 0.
        _kf(TURN_T1, root_pos=(0, GROUND_Y - 0.10, TURN_Z), Torso=(WALK_TORSO_X, 18, 0),
            Head=(-6, 75, 0), **{"Right Leg": (14, 0, 4), "Left Leg": (-3, 0, -2)}, **WALK_ARMS),
        _kf(TURN_T2, root_pos=(0, GROUND_Y - 0.03, TURN_Z), HumanoidRootPart=(0, 90, 0),
            Torso=(WALK_TORSO_X, 8, 0), Head=(-6, 25, 0),
            **{"Right Leg": (6, 0, 0), "Left Leg": (-2, 0, 0)}, **WALK_ARMS),
        _kf(TURN_T3, root_pos=(0, GROUND_Y, TURN_Z), HumanoidRootPart=(0, 160, 0),
            Torso=(WALK_TORSO_X, 3, 0), Head=(-6, 8, 0),
            **{"Right Leg": (0, 0, 0), "Left Leg": (0, 0, 0)}, **WALK_ARMS),
        _kf(TURN_END, root_pos=(0, GROUND_Y, TURN_Z), HumanoidRootPart=(0, 180, 0),
            Torso=(WALK_TORSO_X, 0, 0), Head=WALK_HEAD,
            **{"Right Leg": (0, 0, 0), "Left Leg": (0, 0, 0)}, **WALK_ARMS),
    ]

    # -- marche, WALK_N foulees -- meme grammaire que le pas d'escalier de
    # climb_stairs() (lift a mi-foulee, plant en fin de foulee) mais sur
    # sol plat (pas de STAIR_RISER, juste un leger rebond WALK_BOB).
    for i in range(1, WALK_N + 1):
        lead, trail = ("Right Leg", "Left Leg") if i % 2 == 1 else ("Left Leg", "Right Leg")
        twist = 4 if i % 2 == 1 else -4
        t_mid = WALK_START + (i - 1) * WALK_STEP_T + WALK_STEP_T * 0.5
        t_plant = WALK_START + i * WALK_STEP_T
        z_prev = WALK_Z0 + (i - 1) / WALK_N * (WALK_Z1 - WALK_Z0)
        z_new = WALK_Z0 + i / WALK_N * (WALK_Z1 - WALK_Z0)
        z_mid = (z_prev + z_new) / 2.0

        hero.append(_kf(t_mid, root_pos=(0, GROUND_Y + WALK_BOB, z_mid), HumanoidRootPart=(0, 180, 0),
                         Torso=(WALK_TORSO_X, twist, 0), Head=WALK_HEAD,
                         **{lead: (26, 0, 0), trail: (-8, 0, 0)}, **WALK_ARMS))
        if i == WALK_N:
            # -- derniere foulee : la pose se cale EXACTEMENT sur le
            # premier keyframe de throne_sequence.climb_stairs() (meme
            # temps, meme position, meme pose -- voir hero_track(), qui
            # place le premier keyframe de climb_stairs() a ce meme
            # instant WALK_END, exactement comme full_scene() raccorde
            # climb_stairs() et sit_and_crown() sur un keyframe partage).
            hero.append(_kf(t_plant, root_pos=(0, GROUND_Y, z_new), HumanoidRootPart=(0, 180, 0),
                             Torso=(WALK_TORSO_X, 0, 0), Head=WALK_HEAD,
                             **{"Right Leg": (0, 0, 0), "Left Leg": (0, 0, 0)}, **WALK_ARMS))
        else:
            hero.append(_kf(t_plant, root_pos=(0, GROUND_Y, z_new), HumanoidRootPart=(0, 180, 0),
                             Torso=(WALK_TORSO_X, 0, 0), Head=WALK_HEAD,
                             **{lead: (2, 0, 0), trail: (-4, 0, 0)}, **WALK_ARMS))

    # -- Rival tient sa pose de KO (deja posee par _beat4()) jusqu'a la
    # fin de la scene : un seul keyframe de prolongation suffit.
    rival = [
        _kf(WALK_END, root_pos=(0, COLLAPSE_ROOT_Y, RIVAL_STUMBLE_Z - 2.1), HumanoidRootPart=(0, 150, 0),
            Torso=COLLAPSE_TORSO, Head=COLLAPSE_HEAD, **COLLAPSE_LEGS, **COLLAPSE_ARMS),
    ]
    return hero, rival


BEAT5_END = WALK_END


# =======================================================================
# Assemblage final -- Hero : tous les beats + raccord vers
# throne_sequence.climb_stairs()/sit_and_crown() (decalage en temps
# identique a full_scene(), et le meme decalage en Y de +PLATFORM_H pour
# la partie assise -- voir sa docstring). Rival : tient sa pose de KO
# jusqu'a la toute fin (aucun raccord trone, Rival ne monte pas).
# =======================================================================
def hero_track():
    b0, _ = _beat0()
    b1, _ = _beat1()
    b2, _ = _beat2()
    br, _ = _beat_regroup()
    b3, _ = _beat3()
    b4, _ = _beat4()
    b5, _ = _beat5()

    climb_kf, climb_ph, climb_pt, climb_opts = ts.climb_stairs()
    sit_kf, sit_ph, sit_pt, sit_opts = ts.sit_and_crown()

    shifted_climb_kf = [_shift_kf(k, 0.0, BEAT5_END) for k in climb_kf]
    shifted_sit_kf = []
    for k in sit_kf:
        nk = dict(k)
        nk["time"] = k["time"] + BEAT5_END + ts.CLIMB_T
        x, y, z = k["root_pos"]
        nk["root_pos"] = (x, y + props.PLATFORM_H, z)
        shifted_sit_kf.append(nk)

    keyframes = b0 + b1 + b2 + br + b3 + b4 + b5 + shifted_climb_kf + shifted_sit_kf
    phases = [
        {"name": "garde", "t0": 0.0, "t1": BEAT1_START, "expected_reversals": {}},
        {"name": "jab_rival_encaisse", "t0": BEAT1_START, "t1": BEAT1_END, "expected_reversals": {}},
        {"name": "combo_hero", "t0": BEAT2_START, "t1": BEAT2_END, "expected_reversals": {}},
        {"name": "regroupement", "t0": REGROUP_START, "t1": BEAT3_START, "expected_reversals": {}},
        {"name": "esquive_et_kick", "t0": BEAT3_START, "t1": BEAT3_END, "expected_reversals": {}},
        {"name": "finisher", "t0": BEAT4_START, "t1": BEAT4_END, "expected_reversals": {}},
        {"name": "victoire_et_marche", "t0": BEAT4_END, "t1": BEAT5_END, "expected_reversals": {}},
        {"name": "montee_trone", "t0": BEAT5_END, "t1": BEAT5_END + ts.CLIMB_T, "expected_reversals": {}},
        {"name": "assise_couronnement", "t0": BEAT5_END + ts.CLIMB_T,
         "t1": BEAT5_END + ts.CLIMB_T + sit_kf[-1]["time"], "expected_reversals": {}},
    ]
    preview_times = [0.0, BEAT1_START, BEAT2_START, BEAT2_END, BEAT3_START, HM_STRIKE_T,
                      KICK_STRIKE_T, BEAT4_START, FINISH_STRIKE_T, FLEX_T, TURN_END, WALK_END,
                      BEAT5_END + ts.CLIMB_T, BEAT5_END + ts.CLIMB_T + sit_kf[-1]["time"]]
    engine_opts = {"handle_type": "AUTO_CLAMPED"}
    return keyframes, phases, preview_times, engine_opts


def rival_track():
    _, b0 = _beat0()
    _, b1 = _beat1()
    _, b2 = _beat2()
    _, br = _beat_regroup()
    _, b3 = _beat3()
    _, b4 = _beat4()
    _, b5 = _beat5()

    keyframes = b0 + b1 + b2 + br + b3 + b4 + b5
    phases = [
        {"name": "garde", "t0": 0.0, "t1": BEAT1_START, "expected_reversals": {}},
        {"name": "jab", "t0": BEAT1_START, "t1": BEAT1_END, "expected_reversals": {}},
        {"name": "encaisse_combo", "t0": BEAT2_START, "t1": BEAT2_END, "expected_reversals": {}},
        {"name": "regroupement", "t0": REGROUP_START, "t1": BEAT3_START, "expected_reversals": {}},
        {"name": "haymaker_et_kick_encaisse", "t0": BEAT3_START, "t1": BEAT3_END, "expected_reversals": {}},
        {"name": "titubation_et_ko", "t0": BEAT4_START, "t1": BEAT4_END, "expected_reversals": {}},
        {"name": "ko_tenu", "t0": BEAT4_END, "t1": BEAT5_END, "expected_reversals": {}},
    ]
    preview_times = [0.0, BEAT1_START, BEAT2_START, BEAT2_END, HM_STRIKE_T, PILLAR_HIT_T,
                      BEAT4_START, STUMBLE_T, FINISH_STRIKE_T, BEAT4_END, BEAT5_END]
    engine_opts = {"handle_type": "AUTO_CLAMPED"}
    return keyframes, phases, preview_times, engine_opts


TOTAL_FIGHT_DURATION = BEAT5_END          # duree du combat seul (hors raccord trone), doit etre >= 30s (retour utilisateur)
TOTAL_SCENE_DURATION = BEAT5_END + ts.CLIMB_T + ts.sit_and_crown()[0][-1]["time"]  # combat + montee + assise/couronnement
