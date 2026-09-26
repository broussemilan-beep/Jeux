"""
Identite : competence cinematique en 3 temps -- deux concentrations
solaires dans les mains, un combo rapproche court, un coup final
descendant vers la tete. Contrairement aux prototypes precedents
(r6_rock_kick, r6_battle_throne), cette mission a ete explicitement
precedee d'une demande de RECHERCHE ("Ameliore toi fais d'autre
rechercher tes animation sont tjrs bad game") : chaque decision de
timing/poids ci-dessous cite la source qui la justifie, pas seulement
"ca a l'air bien".

Recherche menee (WebSearch, resume complet dans README "Recherche") :
  R1. Game feel / juice (hitstop, screen shake directionnel a decroissance
      exponentielle, spacing des keyframes communique le poids
      independamment de la duree -- espacement LARGE = rapide/leger,
      espacement DENSE/serre = lourd/lent).
  R2. Timing de combo/finisher : un combo a 3 temps escalade
      (coup 1 rapide/peu d'engagement, coup 2 plus lent/plus de rotation
      du corps, coup 3 = engagement maximal, arc le plus dramatique,
      recuperation la plus lente) ; un poing rapide tient en 3-4 frames
      (60fps) quand une arme lourde a des frames plus lentes en haut de
      son arc puis accelere vers l'impact.
  R3. VFX de charge d'energie ("ki charge") : particules qui convergent
      VERS le noyau (inward), pas seulement un halo qui grossit sur
      place -- vocabulaire visuel distinct de tout ce qui a ete fait
      jusqu'ici dans ce depot (rock_kick/divine_orb n'ont que des
      bursts sortants).

Application concrete de chaque principe :
  - Le finisher (R2) : engagement le plus large (bras au-dessus de la
      tete, torse arque au maximum), ET (R1) sa DESCENTE elle-meme est
      etalee sur 11 frames (FIN_COIL_HOLD_T -> FIN_STRIKE_T) avec un
      keyframe intermediaire FIN_MID_T volontairement PROCHE de la pose
      de coil (f=0.18 de la trajectoire totale a plus de la moitie du
      temps ecoule) -- la descente est lente au depart puis accelere,
      jamais un snap 2-frames comme les coups intermediaires. Resultat
      mesure : ~5.5x plus long que le lacher d'un coup de combo (voir
      calibrate.py).
  - Les 2 coups de combo (R2) restent proches du snap 2-frames deja
      valide dans r6_hit_combo (jab/cross) -- coup 1 legerement plus
      "sec" que le coup 2 (moins de rotation de torse), meme escalade.
  - Les noyaux solaires (R3) : voir solar_track.py, particules
      explicitement configurees pour CONVERGER vers chaque main pendant
      la charge, jamais juste un burst statique.
  - Camera (R1, shake directionnel + decroissance exponentielle) :
      implementee au niveau du viewer (dump_scene_data.py/HTML), pas
      ici -- ce fichier ne pose que le squelette.

Lecons du depot deja etablies, reappliquees sans avoir besoin d'un
nouveau retour utilisateur pour chacune :
  - Chaine cinetique exageree bassin/torse (meme principe que
    r6_rock_kick : le rig n'a ni genou ni cheville, tout le "poids"
    vient d'une rotation de torse largement au-dela d'un humain reel).
  - Hold-and-snap pour les coups intermediaires (chambrage tenu, lacher
    quasi instantane) -- SAUF le finisher, ou le principe est
    deliberement invers e (voir R1/R2 ci-dessus) : c'est un choix
    documente, pas un oubli du principe.
  - JAMAIS de hold plat sur une pose d'ATTENTE (garde initiale, retour
    final) -- voir _idle_stance_span(). Reste distinct des vrais holds
    de coil (charge, coil de chaque coup), qui doivent rester geles.
  - Placement des pieds verifie par cinematique directe
    (grounded_root_y/_balanced), jamais un offset Y constant.
  - La sequence principale de l'attaquant NE DEPEND PAS de la presence
    d'une cible (meme discipline "fonctionne sans cible" que
    r6_rock_kick) : ces keyframes jouent integralement que le mannequin
    soit present ou non. dummy_reaction() est une piste SEPAREE,
    synchronisee sur les memes instants d'impact, mais optionnelle.
"""
import math

import numpy as np

from r6_rig import JOINTS, PART_SIZES, joint_for_part

REST = (0.0, 0.0, 0.0)
GROUND_Y = 3.0
SNAP = 1 / 30


def _fr(n):
    return n / 30.0


# ---------------------------------------------------------------------
# Cinematique directe partagee (copiee -- convention du depot : jamais
# d'import croise entre prototypes isoles).
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


def fist_tip_world(root_pos, torso_rot, arm_rot, arm_part):
    joint = joint_for_part(arm_part)
    c0 = np.array(JOINTS[joint]["C0"]["pos"])
    c1 = np.array(JOINTS[joint]["C1"]["pos"])
    r_torso = _euler_xyz_matrix(*torso_rot)
    r_arm_local = _euler_xyz_matrix(*arm_rot)
    arm_local_pos = c0 - r_arm_local @ c1
    r_arm_world = r_torso @ r_arm_local
    half = PART_SIZES[arm_part][1] / 2.0
    offset = r_torso @ arm_local_pos + r_arm_world @ np.array([0.0, -half, 0.0])
    return np.array(root_pos) + offset


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


# -- Attente vivante (voir docstring de module) : jamais un hold plat.
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
# Disposition : l'attaquant avance en 2 pas courts pendant le combo
# (demande utilisateur : "le personnage avance ensuite dans un combo
# court de frappes"), le mannequin-cible reste immobile face a lui
# (meme convention que r6_hit_combo -- DUMMY_Z identique, echelle deja
# calibree pour un combo de coups de poing sur ce rig).
# =======================================================================
CHAR_Z0 = -2.0
DUMMY_Z = -6.6

_READY_TORSO = (4, 0, 0)
_READY_HEAD = (2, 0, 0)
_READY_LEGS = {"Right Leg": (4, 0, 6), "Left Leg": (6, 0, -5)}
_READY_ARMS = {"Right Arm": (18, 0, -8), "Left Arm": (20, 0, 10)}

# =======================================================================
# Phase 0 -- garde initiale, attente vivante (T0_END).
# =======================================================================
T0_END = _fr(18)   # 0.6s


def phase0_idle():
    return _idle_stance_span(0.0, T0_END, (0, 0, CHAR_Z0), REST,
                              _READY_TORSO, _READY_HEAD, _READY_LEGS, _READY_ARMS,
                              period=0.6, phase0=0.0, amp_leg=3.0, amp_torso=2.0)


# =======================================================================
# Phase OUVERTURE -- "ouverture lente et reconnaissable : les deux bras
# s'ecartent, puis se chargent simultanement" (demande utilisateur,
# appliquee litteralement en 2 temps distincts, pas une seule pose) :
#   1. OPEN  : les bras s'ecartent largement sur le cote (mouvement LENT,
#      lisible -- 26 frames/0.87s, le double du T0_END de garde).
#   2. CHARGE: les mains remontent/se replient legerement vers l'avant,
#      presentees "en coupe" -- c'est la pose ou les noyaux solaires
#      naissent (voir solar_track.py). Vrai hold ensuite (CHARGE_HOLD_T,
#      pose identique) : la charge elle-meme est portee par le VFX
#      (particules convergentes, R3), pas par un mouvement de corps --
#      coherent avec la regle du depot "un coil reste un vrai gel".
# =======================================================================
OPEN_T = T0_END + _fr(26)
CHARGE_T = OPEN_T + _fr(14)
CHARGE_HOLD_T = CHARGE_T + _fr(20)

OPEN_TORSO = (-6, 0, 0)
OPEN_HEAD = (-4, 0, 0)
OPEN_LEGS = {"Right Leg": (6, 0, 10), "Left Leg": (8, 0, -9)}
# -- rz calibre par balayage numerique (fist_tip_world) : le signe
# intuitif (Right Arm negatif = "vers l'exterieur") etait FAUX -- la
# rotation C0 du joint d'epaule permute les axes, rz negatif fait en
# realite TRAVERSER le bras vers le centre/l'autre cote (verifie :
# rz=-82 donnait poing droit a X=-0.42, soit a GAUCHE du centre). Le
# signe correct pour un vrai ecartement lateral est INVERSE de
# l'intuition : Right Arm positif, Left Arm negatif (confirme : rz=+82
# donne poing droit a X=+2.56, bien ecarte sur le cote droit).
OPEN_ARMS = {"Right Arm": (8, 0, 82), "Left Arm": (8, 0, -82)}
OPEN_ROOT_Y = grounded_root_y_balanced(OPEN_TORSO, OPEN_LEGS["Left Leg"], OPEN_LEGS["Right Leg"])

CHARGE_TORSO = (-10, 0, 0)
CHARGE_HEAD = (-6, 0, 0)
CHARGE_LEGS = dict(OPEN_LEGS)
CHARGE_ARMS = {"Right Arm": (45, 0, -55), "Left Arm": (45, 0, 55)}
CHARGE_ROOT_Y = grounded_root_y_balanced(CHARGE_TORSO, CHARGE_LEGS["Left Leg"], CHARGE_LEGS["Right Leg"])

# -- position MONDE de chaque main a l'instant ou les noyaux naissent :
# mesuree (pas choisie a l'oeil), utilisee par solar_track.py comme
# point de depart de chaque noyau.
CORE_SPAWN_RIGHT = fist_tip_world((0, CHARGE_ROOT_Y, CHAR_Z0), CHARGE_TORSO, CHARGE_ARMS["Right Arm"], "Right Arm")
CORE_SPAWN_LEFT = fist_tip_world((0, CHARGE_ROOT_Y, CHAR_Z0), CHARGE_TORSO, CHARGE_ARMS["Left Arm"], "Left Arm")


def phase_open_charge():
    return [
        _kf(OPEN_T, root_pos=(0, OPEN_ROOT_Y, CHAR_Z0), Torso=OPEN_TORSO,
            Head=OPEN_HEAD, **OPEN_LEGS, **OPEN_ARMS),
        _kf(CHARGE_T, root_pos=(0, CHARGE_ROOT_Y, CHAR_Z0), Torso=CHARGE_TORSO,
            Head=CHARGE_HEAD, **CHARGE_LEGS, **CHARGE_ARMS),
        _kf(CHARGE_HOLD_T, root_pos=(0, CHARGE_ROOT_Y, CHAR_Z0), Torso=CHARGE_TORSO,
            Head=CHARGE_HEAD, **CHARGE_LEGS, **CHARGE_ARMS),
    ]


# =======================================================================
# Phase COMBO -- 2 coups rapproches, hold-and-snap classique (chambrage
# tenu, lacher en 2 frames -- R2 : le coup 2 a un peu plus de rotation
# de torse que le coup 1, escalade meme sur un combo court). Avance
# franche a chaque coup (hip-drive + pas, "le personnage avance").
# =======================================================================
STRIKE1_WINDUP_T = CHARGE_HOLD_T + _fr(6)
STRIKE1_COIL_T = STRIKE1_WINDUP_T + _fr(5)
STRIKE1_COIL_HOLD_T = STRIKE1_COIL_T + _fr(3)
STRIKE1_T = STRIKE1_COIL_HOLD_T + _fr(2)

STRIKE2_WINDUP_T = STRIKE1_T + _fr(5)
STRIKE2_COIL_T = STRIKE2_WINDUP_T + _fr(5)
STRIKE2_COIL_HOLD_T = STRIKE2_COIL_T + _fr(3)
STRIKE2_T = STRIKE2_COIL_HOLD_T + _fr(2)

FIN_RECOVER_T = STRIKE2_T + _fr(4)

STRIKE1_LUNGE_Z = -4.4
STRIKE2_LUNGE_Z = -5.1

STRIKE1_WINDUP_TORSO = (6, 10, 0)
STRIKE1_WINDUP_HEAD = (4, 6, 0)
STRIKE1_WINDUP_LEGS = {"Right Leg": (8, 0, 9), "Left Leg": (10, 0, -8)}
STRIKE1_WINDUP_ARMS = {"Right Arm": (38, 0, -40), "Left Arm": (50, 0, 50)}
STRIKE1_WINDUP_ROOT_Y = grounded_root_y_balanced(STRIKE1_WINDUP_TORSO, STRIKE1_WINDUP_LEGS["Left Leg"], STRIKE1_WINDUP_LEGS["Right Leg"])

STRIKE1_COIL_TORSO = (10, -24, 2)
STRIKE1_COIL_HEAD = (8, -14, 0)
STRIKE1_COIL_LEGS = {"Right Leg": (12, 0, 14), "Left Leg": (12, 0, -9)}
STRIKE1_COIL_ARMS = {"Right Arm": (75, 0, -20), "Left Arm": (46, 0, 48)}
STRIKE1_COIL_ROOT_Y = grounded_root_y_balanced(STRIKE1_COIL_TORSO, STRIKE1_COIL_LEGS["Left Leg"], STRIKE1_COIL_LEGS["Right Leg"])

# -- lacher : le torse traverse le centre (Y -24 -> +45), le bras droit
# fouette droit devant -- calibre par balayage numerique (ecart mesure
# < 0.03 stud, voir calibrate.py), pas choisi a l'oeil : la version
# initiale (Y=+30, rz=+10) laissait un ecart de ~1 stud en X.
STRIKE1_STRIKE_TORSO = (-10, 45, 0)
STRIKE1_STRIKE_HEAD = (6, 14, 0)
STRIKE1_STRIKE_LEGS = {"Right Leg": (4, 0, -6), "Left Leg": (14, 0, 4)}
STRIKE1_STRIKE_ARMS = {"Right Arm": (90, 0, 0), "Left Arm": (40, 0, 44)}
STRIKE1_STRIKE_ROOT_Y = grounded_root_y(STRIKE1_STRIKE_TORSO, STRIKE1_STRIKE_LEGS["Left Leg"], "Left Leg")

_STRIKE1_ROOT_POS = (0.0, STRIKE1_STRIKE_ROOT_Y, STRIKE1_LUNGE_Z)
STRIKE1_CONTACT_POINT = fist_tip_world(_STRIKE1_ROOT_POS, STRIKE1_STRIKE_TORSO, STRIKE1_STRIKE_ARMS["Right Arm"], "Right Arm")

STRIKE2_WINDUP_TORSO = (4, 22, -2)
STRIKE2_WINDUP_HEAD = (4, 12, 0)
STRIKE2_WINDUP_LEGS = {"Right Leg": (6, 0, 8), "Left Leg": (16, 0, -6)}
STRIKE2_WINDUP_ARMS = {"Right Arm": (60, 0, 6), "Left Arm": (44, 0, 40)}
STRIKE2_WINDUP_ROOT_Y = grounded_root_y_balanced(STRIKE2_WINDUP_TORSO, STRIKE2_WINDUP_LEGS["Left Leg"], STRIKE2_WINDUP_LEGS["Right Leg"])

STRIKE2_COIL_TORSO = (8, -32, -4)
STRIKE2_COIL_HEAD = (6, -20, 0)
STRIKE2_COIL_LEGS = {"Right Leg": (8, 0, 10), "Left Leg": (18, 0, -12)}
STRIKE2_COIL_ARMS = {"Right Arm": (50, 0, 8), "Left Arm": (80, 0, 30)}
STRIKE2_COIL_ROOT_Y = grounded_root_y_balanced(STRIKE2_COIL_TORSO, STRIKE2_COIL_LEGS["Left Leg"], STRIKE2_COIL_LEGS["Right Leg"])

# -- lacher : contrairement au coup 1 (reversal complet du torse), le
# coup 2 est un CROCHET du bras gauche -- le torse CONTINUE de tourner
# dans le meme sens que son chambrage (Y -32 -> -20, jamais un
# renversement de signe ici) pendant que le bras gauche balaie par le
# cote (rz +48 -> +35) -- calibre par balayage numerique (ecart mesure
# < 0.01 stud, voir calibrate.py) plutot que choisi a l'oeil : un
# renversement complet comme le coup 1 aurait envoye le poing loin du
# centre (essaye, ecart > 2.5 stud avant correction).
STRIKE2_STRIKE_TORSO = (-10, -20, 0)
STRIKE2_STRIKE_HEAD = (8, -12, 0)
STRIKE2_STRIKE_LEGS = {"Right Leg": (6, 0, -8), "Left Leg": (18, 0, 6)}
STRIKE2_STRIKE_ARMS = {"Right Arm": (48, 0, 8), "Left Arm": (85, 0, 35)}
STRIKE2_STRIKE_ROOT_Y = grounded_root_y(STRIKE2_STRIKE_TORSO, STRIKE2_STRIKE_LEGS["Left Leg"], "Left Leg")

_STRIKE2_ROOT_POS = (0.0, STRIKE2_STRIKE_ROOT_Y, STRIKE2_LUNGE_Z)
STRIKE2_CONTACT_POINT = fist_tip_world(_STRIKE2_ROOT_POS, STRIKE2_STRIKE_TORSO, STRIKE2_STRIKE_ARMS["Left Arm"], "Left Arm")

FIN_RECOVER_TORSO = (0, 10, 0)
FIN_RECOVER_HEAD = (2, 6, 0)
FIN_RECOVER_LEGS = {"Right Leg": (8, 0, 8), "Left Leg": (10, 0, -6)}
FIN_RECOVER_ARMS = {"Right Arm": (30, 0, 10), "Left Arm": (30, 0, -8)}
FIN_RECOVER_ROOT_Y = grounded_root_y_balanced(FIN_RECOVER_TORSO, FIN_RECOVER_LEGS["Left Leg"], FIN_RECOVER_LEGS["Right Leg"])


def phase_combo():
    return [
        _kf(STRIKE1_WINDUP_T, root_pos=(0, STRIKE1_WINDUP_ROOT_Y, CHAR_Z0), Torso=STRIKE1_WINDUP_TORSO,
            Head=STRIKE1_WINDUP_HEAD, **STRIKE1_WINDUP_LEGS, **STRIKE1_WINDUP_ARMS),
        _kf(STRIKE1_COIL_T, root_pos=(0, STRIKE1_COIL_ROOT_Y, CHAR_Z0), Torso=STRIKE1_COIL_TORSO,
            Head=STRIKE1_COIL_HEAD, **STRIKE1_COIL_LEGS, **STRIKE1_COIL_ARMS),
        _kf(STRIKE1_COIL_HOLD_T, root_pos=(0, STRIKE1_COIL_ROOT_Y, CHAR_Z0), Torso=STRIKE1_COIL_TORSO,
            Head=STRIKE1_COIL_HEAD, **STRIKE1_COIL_LEGS, **STRIKE1_COIL_ARMS),
        _kf(STRIKE1_T, root_pos=(0, STRIKE1_STRIKE_ROOT_Y, STRIKE1_LUNGE_Z), Torso=STRIKE1_STRIKE_TORSO,
            Head=STRIKE1_STRIKE_HEAD, **STRIKE1_STRIKE_LEGS, **STRIKE1_STRIKE_ARMS),
        _kf(STRIKE2_WINDUP_T, root_pos=(0, STRIKE2_WINDUP_ROOT_Y, STRIKE1_LUNGE_Z), Torso=STRIKE2_WINDUP_TORSO,
            Head=STRIKE2_WINDUP_HEAD, **STRIKE2_WINDUP_LEGS, **STRIKE2_WINDUP_ARMS),
        _kf(STRIKE2_COIL_T, root_pos=(0, STRIKE2_COIL_ROOT_Y, STRIKE1_LUNGE_Z), Torso=STRIKE2_COIL_TORSO,
            Head=STRIKE2_COIL_HEAD, **STRIKE2_COIL_LEGS, **STRIKE2_COIL_ARMS),
        _kf(STRIKE2_COIL_HOLD_T, root_pos=(0, STRIKE2_COIL_ROOT_Y, STRIKE1_LUNGE_Z), Torso=STRIKE2_COIL_TORSO,
            Head=STRIKE2_COIL_HEAD, **STRIKE2_COIL_LEGS, **STRIKE2_COIL_ARMS),
        _kf(STRIKE2_T, root_pos=(0, STRIKE2_STRIKE_ROOT_Y, STRIKE2_LUNGE_Z), Torso=STRIKE2_STRIKE_TORSO,
            Head=STRIKE2_STRIKE_HEAD, **STRIKE2_STRIKE_LEGS, **STRIKE2_STRIKE_ARMS),
        _kf(FIN_RECOVER_T, root_pos=(0, FIN_RECOVER_ROOT_Y, STRIKE2_LUNGE_Z), Torso=FIN_RECOVER_TORSO,
            Head=FIN_RECOVER_HEAD, **FIN_RECOVER_LEGS, **FIN_RECOVER_ARMS),
    ]


# =======================================================================
# Phase FINISHER -- "montee du bras / repositionnement du torse puis
# enorme frappe descendante vers la tete" + "la derniere frappe doit
# etre beaucoup plus lente et lourde que les coups intermediaires"
# (demande utilisateur, litterale). Les DEUX bras montent ensemble
# au-dessus de la tete (les deux noyaux solaires se rejoignent, voir
# solar_track.py) -- lecture "hache a deux mains", pas un simple
# crochet. La descente elle-meme est etalee sur 11 frames avec un point
# intermediaire proche du sommet (R1/R2, voir docstring de module),
# jamais un snap 2-frames comme le reste du combo.
# =======================================================================
FIN_COIL_T = FIN_RECOVER_T + _fr(16)      # montee lente et lisible jusqu'au sommet
FIN_COIL_HOLD_T = FIN_COIL_T + _fr(14)    # vrai hold -- tension maximale, la plus longue du set
FIN_MID_T = FIN_COIL_HOLD_T + _fr(6)      # debut de la descente, encore lent (voir FIN_MID_F)
FIN_STRIKE_T = FIN_MID_T + _fr(5)         # impact -- 11 frames depuis le hold, ~5.5x le snap d'un coup de combo
FIN_FOLLOWTHROUGH_T = FIN_STRIKE_T + _fr(8)
FIN_RECOVER2_T = FIN_FOLLOWTHROUGH_T + _fr(28)

FIN_MID_F = 0.18   # fraction de trajectoire parcourue a FIN_MID_T -- deliberement petite (poids/inertie, R1)

FIN_COIL_TORSO = (-42, 8, 0)
FIN_COIL_HEAD = (-24, 0, 0)
FIN_COIL_LEGS = {"Right Leg": (10, 0, 12), "Left Leg": (14, 0, -10)}
FIN_COIL_ARMS = {"Right Arm": (168, 0, -6), "Left Arm": (168, 0, 6)}
FIN_COIL_ROOT_Y = grounded_root_y_balanced(FIN_COIL_TORSO, FIN_COIL_LEGS["Left Leg"], FIN_COIL_LEGS["Right Leg"])

# -- position MONDE ou les deux noyaux fusionnent avant le lacher final
# (mesuree sur chaque main, moyenne -- les deux bras sont quasi
# symetriques au sommet du coil).
_FIN_COIL_ROOT_POS = (0.0, FIN_COIL_ROOT_Y, STRIKE2_LUNGE_Z)
_FIN_COIL_RIGHT = fist_tip_world(_FIN_COIL_ROOT_POS, FIN_COIL_TORSO, FIN_COIL_ARMS["Right Arm"], "Right Arm")
_FIN_COIL_LEFT = fist_tip_world(_FIN_COIL_ROOT_POS, FIN_COIL_TORSO, FIN_COIL_ARMS["Left Arm"], "Left Arm")
CORE_MERGE_POINT = (np.array(_FIN_COIL_RIGHT) + np.array(_FIN_COIL_LEFT)) / 2.0

# -- le finisher ajoute son propre pas en avant (FIN_LUNGE_Z), au-dela
# de STRIKE2_LUNGE_Z : le corps s'engage physiquement dans le coup en
# plus de la rotation/descente des bras (poids qui part vers l'avant --
# lisible comme "le personnage se jette dans sa frappe", pas juste un
# geste de bras immobile). Calibre par balayage numerique conjoint
# (pas/torse/bras) -- ecart mesure ~0.2 stud, voir calibrate.py.
FIN_LUNGE_Z = -6.8

FIN_STRIKE_TORSO = (45, -8, 0)
FIN_STRIKE_HEAD = (26, 0, 0)
FIN_STRIKE_LEGS = {"Right Leg": (14, 0, 10), "Left Leg": (18, 0, -8)}
FIN_STRIKE_ARMS = {"Right Arm": (115, 0, -5), "Left Arm": (115, 0, 5)}
FIN_STRIKE_ROOT_Y = grounded_root_y_balanced(FIN_STRIKE_TORSO, FIN_STRIKE_LEGS["Left Leg"], FIN_STRIKE_LEGS["Right Leg"])

_FIN_STRIKE_ROOT_POS = (0.0, FIN_STRIKE_ROOT_Y, FIN_LUNGE_Z)
_FIN_STRIKE_RIGHT = fist_tip_world(_FIN_STRIKE_ROOT_POS, FIN_STRIKE_TORSO, FIN_STRIKE_ARMS["Right Arm"], "Right Arm")
_FIN_STRIKE_LEFT = fist_tip_world(_FIN_STRIKE_ROOT_POS, FIN_STRIKE_TORSO, FIN_STRIKE_ARMS["Left Arm"], "Left Arm")
FIN_CONTACT_POINT = (np.array(_FIN_STRIKE_RIGHT) + np.array(_FIN_STRIKE_LEFT)) / 2.0

FIN_MID_TORSO = lerp3(FIN_COIL_TORSO, FIN_STRIKE_TORSO, FIN_MID_F)
FIN_MID_HEAD = lerp3(FIN_COIL_HEAD, FIN_STRIKE_HEAD, FIN_MID_F)
FIN_MID_LEGS = lerp_legs(FIN_COIL_LEGS, FIN_STRIKE_LEGS, FIN_MID_F)
FIN_MID_ARMS = lerp_legs(FIN_COIL_ARMS, FIN_STRIKE_ARMS, FIN_MID_F)
FIN_MID_ROOT_Y = grounded_root_y_balanced(FIN_MID_TORSO, FIN_MID_LEGS["Left Leg"], FIN_MID_LEGS["Right Leg"])
FIN_MID_ROOT_Z = STRIKE2_LUNGE_Z + FIN_MID_F * (FIN_LUNGE_Z - STRIKE2_LUNGE_Z)

# -- suite : l'inertie du corps continue sous son propre poids
# au-dela du contact (over-commit, meme principe que le reste du
# depot) avant de se stabiliser.
FIN_FT_TORSO = (68, -12, 0)
FIN_FT_HEAD = (30, 0, 0)
FIN_FT_LEGS = dict(FIN_STRIKE_LEGS)
FIN_FT_ARMS = {"Right Arm": (14, 0, -6), "Left Arm": (14, 0, 6)}
FIN_FT_ROOT_Y = grounded_root_y_balanced(FIN_FT_TORSO, FIN_FT_LEGS["Left Leg"], FIN_FT_LEGS["Right Leg"])

RELAX_TORSO = (20, 0, 0)
RELAX_HEAD = (10, 0, 0)
RELAX_LEGS = {"Right Leg": (10, 0, 10), "Left Leg": (12, 0, -8)}
RELAX_ARMS = {"Right Arm": (20, 0, -10), "Left Arm": (20, 0, 10)}


def phase_finisher():
    kfs = [
        _kf(FIN_COIL_T, root_pos=(0, FIN_COIL_ROOT_Y, STRIKE2_LUNGE_Z), Torso=FIN_COIL_TORSO,
            Head=FIN_COIL_HEAD, **FIN_COIL_LEGS, **FIN_COIL_ARMS),
        _kf(FIN_COIL_HOLD_T, root_pos=(0, FIN_COIL_ROOT_Y, STRIKE2_LUNGE_Z), Torso=FIN_COIL_TORSO,
            Head=FIN_COIL_HEAD, **FIN_COIL_LEGS, **FIN_COIL_ARMS),
        _kf(FIN_MID_T, root_pos=(0, FIN_MID_ROOT_Y, FIN_MID_ROOT_Z), Torso=FIN_MID_TORSO,
            Head=FIN_MID_HEAD, **FIN_MID_LEGS, **FIN_MID_ARMS),
        _kf(FIN_STRIKE_T, root_pos=(0, FIN_STRIKE_ROOT_Y, FIN_LUNGE_Z), Torso=FIN_STRIKE_TORSO,
            Head=FIN_STRIKE_HEAD, **FIN_STRIKE_LEGS, **FIN_STRIKE_ARMS),
        _kf(FIN_FOLLOWTHROUGH_T, root_pos=(0, FIN_FT_ROOT_Y, FIN_LUNGE_Z), Torso=FIN_FT_TORSO,
            Head=FIN_FT_HEAD, **FIN_FT_LEGS, **FIN_FT_ARMS),
    ]
    kfs += _idle_stance_span(FIN_FOLLOWTHROUGH_T + _fr(12), FIN_RECOVER2_T, (0, 0, FIN_LUNGE_Z), REST,
                              RELAX_TORSO, RELAX_HEAD, RELAX_LEGS, RELAX_ARMS,
                              period=0.5, phase0=0.0, amp_leg=2.5, amp_torso=2.0)
    return kfs


def attacker_track():
    keyframes = phase0_idle() + phase_open_charge() + phase_combo() + phase_finisher()
    phases = [
        {"name": "garde", "t0": 0.0, "t1": OPEN_T, "expected_reversals": {}},
        {"name": "ouverture_charge", "t0": OPEN_T, "t1": STRIKE1_WINDUP_T, "expected_reversals": {}},
        {"name": "combo", "t0": STRIKE1_WINDUP_T, "t1": FIN_COIL_T, "expected_reversals": {}},
        {"name": "finisher", "t0": FIN_COIL_T, "t1": FIN_RECOVER2_T, "expected_reversals": {}},
    ]
    preview_times = [0.0, OPEN_T, CHARGE_T, CHARGE_HOLD_T,
                      STRIKE1_WINDUP_T, STRIKE1_COIL_T, STRIKE1_COIL_HOLD_T, STRIKE1_T,
                      STRIKE2_WINDUP_T, STRIKE2_COIL_T, STRIKE2_COIL_HOLD_T, STRIKE2_T, FIN_RECOVER_T,
                      FIN_COIL_T, FIN_COIL_HOLD_T, FIN_MID_T, FIN_STRIKE_T, FIN_FOLLOWTHROUGH_T, FIN_RECOVER2_T]
    engine_opts = {"handle_type": "AUTO_CLAMPED"}
    return keyframes, phases, preview_times, engine_opts


TOTAL_DURATION = FIN_RECOVER2_T

# =======================================================================
# Fenetres de hit / knockback -- DESIGN INTENT documente pour un futur
# cablage gameplay (ce depot n'a pas de moteur de jeu, meme convention
# que r6_rock_kick) : "la derniere frappe doit avoir la plus grosse
# fenetre d'impact et le plus gros knockback" (demande utilisateur,
# verifiee ci-dessous : 11 frames pour le finisher contre 5 pour chaque
# coup de combo, knockback qualitatif croissant applique dans
# dummy_reaction()).
# =======================================================================
HIT_WINDOWS = {
    "combo_1": {"t0": STRIKE1_T - _fr(2), "t1": STRIKE1_T + _fr(3), "knockback": "leger"},
    "combo_2": {"t0": STRIKE2_T - _fr(2), "t1": STRIKE2_T + _fr(3), "knockback": "modere"},
    "finisher": {"t0": FIN_STRIKE_T - _fr(3), "t1": FIN_STRIKE_T + _fr(8), "knockback": "maximal"},
}


# =======================================================================
# Mannequin-cible : encaisse les 2 coups de combo (stagger horizontal,
# escalade comme r6_hit_combo) puis le finisher, qui doit se lire
# DIFFEREMMENT des deux premiers -- un coup descendant sur la tete
# ecrase la cible vers le bas (torse/tete plies vers l'avant, racine Y
# qui chute), PAS un simple recul horizontal -- avant un knockback (Z)
# plus grand que les deux coups de combo reunis, conforme a
# HIT_WINDOWS["finisher"]["knockback"] = "maximal".
# =======================================================================
DUMMY_IDLE_TORSO = (0, 0, 0)
DUMMY_IDLE_HEAD = (0, 0, 0)
DUMMY_IDLE_ARMS = {"Right Arm": (4, 0, 10), "Left Arm": (4, 0, -10)}
DUMMY_IDLE_LEGS = {"Right Leg": (0, 0, 3), "Left Leg": (0, 0, -3)}

S1_HIT_TORSO = (-14, 0, 4)
S1_HIT_HEAD = (-10, -4, 0)
S1_HIT_ARMS = {"Right Arm": (30, 0, 16), "Left Arm": (30, 0, -20)}
S1_HIT_LEGS = {"Right Leg": (-2, 0, 4), "Left Leg": (2, 0, -4)}
S1_OVERSHOOT_TORSO = (-18, 0, 5)
S1_OVERSHOOT_HEAD = (-25, -6, 0)
S1_SETTLE_TORSO = (-8, 0, 2)
S1_SETTLE_HEAD = (-11, -2, 0)

S2_HIT_TORSO = (-26, 0, 8)
S2_HIT_HEAD = (-32, -9, 0)
S2_HIT_ARMS = {"Right Arm": (110, 0, 40), "Left Arm": (110, 0, -55)}
S2_HIT_LEGS = {"Right Leg": (-12, 0, 8), "Left Leg": (6, 0, -10)}
S2_OVERSHOOT_TORSO = (-32, 0, 10)
S2_OVERSHOOT_HEAD = (-38, -11, 0)
S2_SETTLE_TORSO = (-16, 0, 4)
S2_SETTLE_HEAD = (-19, -4, 0)

# -- ecrase vers le bas (pas un recul lateral -- coup descendant sur la
# tete) : torse/tete plies fortement vers l'avant, racine Y qui chute
# (genoux qui cedent), PUIS knockback horizontal (Z) le plus grand du
# set une fois la cible dechue au sol.
FIN_HIT_TORSO = (48, 0, 0)
FIN_HIT_HEAD = (58, 0, 0)
FIN_HIT_ARMS = {"Right Arm": (70, 0, 34), "Left Arm": (70, 0, -34)}
FIN_HIT_LEGS = {"Right Leg": (34, 0, 16), "Left Leg": (38, 0, -14)}
FIN_HIT_ROOT_Y = GROUND_Y - 0.9

FIN_OVERSHOOT_TORSO = (58, 0, 0)
FIN_OVERSHOOT_HEAD = (66, 0, 0)
FIN_OVERSHOOT_ROOT_Y = GROUND_Y - 1.3

FIN_COLLAPSED_TORSO = (74, 0, 0)
FIN_COLLAPSED_HEAD = (62, 0, 0)
FIN_COLLAPSED_ARMS = {"Right Arm": (54, 0, 22), "Left Arm": (54, 0, -22)}
FIN_COLLAPSED_LEGS = {"Right Leg": (46, 0, 10), "Left Leg": (50, 0, -8)}
FIN_COLLAPSED_ROOT_Y = GROUND_Y - 1.7


def dummy_reaction():
    kfs = [
        _kf(0.00, root_pos=(0, GROUND_Y, DUMMY_Z), HumanoidRootPart=(0, 180, 0),
            Torso=DUMMY_IDLE_TORSO, Head=DUMMY_IDLE_HEAD, **DUMMY_IDLE_LEGS, **DUMMY_IDLE_ARMS),
        _kf(STRIKE1_T - 0.03, root_pos=(0, GROUND_Y, DUMMY_Z), HumanoidRootPart=(0, 180, 0),
            Torso=DUMMY_IDLE_TORSO, Head=DUMMY_IDLE_HEAD, **DUMMY_IDLE_LEGS, **DUMMY_IDLE_ARMS),
        # -- coup 1 : flinch leger, whiplash + rebond partiel (le coup 2
        # arrive avant toute recuperation complete).
        _kf(STRIKE1_T, root_pos=(0, GROUND_Y, DUMMY_Z), HumanoidRootPart=(0, 180, 0),
            Torso=S1_HIT_TORSO, Head=S1_HIT_HEAD, **S1_HIT_LEGS, **S1_HIT_ARMS),
        _kf(STRIKE1_T + 0.05, root_pos=(0, GROUND_Y, DUMMY_Z), HumanoidRootPart=(0, 180, 0),
            Torso=S1_OVERSHOOT_TORSO, Head=S1_OVERSHOOT_HEAD, **S1_HIT_LEGS, **S1_HIT_ARMS),
        _kf(STRIKE1_T + 0.14, root_pos=(0, GROUND_Y, DUMMY_Z - 0.15), HumanoidRootPart=(0, 180, 0),
            Torso=S1_SETTLE_TORSO, Head=S1_SETTLE_HEAD, **S1_HIT_LEGS, **S1_HIT_ARMS),
        _kf(STRIKE2_T - 0.03, root_pos=(0, GROUND_Y, DUMMY_Z - 0.15), HumanoidRootPart=(0, 180, 0),
            Torso=S1_SETTLE_TORSO, Head=S1_SETTLE_HEAD, **S1_HIT_LEGS, **S1_HIT_ARMS),
        # -- coup 2 : vacille plus fort (escalade -- meme principe que
        # r6_hit_combo).
        _kf(STRIKE2_T, root_pos=(0, GROUND_Y, DUMMY_Z - 0.15), HumanoidRootPart=(0, 175, 0),
            Torso=S2_HIT_TORSO, Head=S2_HIT_HEAD, **S2_HIT_LEGS, **S2_HIT_ARMS),
        _kf(STRIKE2_T + 0.06, root_pos=(0, GROUND_Y, DUMMY_Z - 0.15), HumanoidRootPart=(0, 175, 0),
            Torso=S2_OVERSHOOT_TORSO, Head=S2_OVERSHOOT_HEAD, **S2_HIT_LEGS, **S2_HIT_ARMS),
        _kf(STRIKE2_T + 0.20, root_pos=(0, GROUND_Y, DUMMY_Z - 0.75), HumanoidRootPart=(0, 172, 0),
            Torso=S2_SETTLE_TORSO, Head=S2_SETTLE_HEAD, **S2_HIT_LEGS, **S2_HIT_ARMS),
        _kf(FIN_STRIKE_T - 0.04, root_pos=(0, GROUND_Y, DUMMY_Z - 0.75), HumanoidRootPart=(0, 172, 0),
            Torso=S2_SETTLE_TORSO, Head=S2_SETTLE_HEAD, **S2_HIT_LEGS, **S2_HIT_ARMS),
        # -- finisher : ECRASEE vers le bas (coup descendant, pas un
        # recul) puis le plus gros knockback horizontal du set une fois
        # a terre.
        _kf(FIN_STRIKE_T, root_pos=(0, FIN_HIT_ROOT_Y, DUMMY_Z - 0.75), HumanoidRootPart=(0, 172, 0),
            Torso=FIN_HIT_TORSO, Head=FIN_HIT_HEAD, **FIN_HIT_LEGS, **FIN_HIT_ARMS),
        _kf(FIN_STRIKE_T + 0.10, root_pos=(0, FIN_OVERSHOOT_ROOT_Y, DUMMY_Z - 1.6), HumanoidRootPart=(0, 168, 0),
            Torso=FIN_OVERSHOOT_TORSO, Head=FIN_OVERSHOOT_HEAD, **FIN_HIT_LEGS, **FIN_HIT_ARMS),
        _kf(FIN_STRIKE_T + 0.45, root_pos=(0, FIN_COLLAPSED_ROOT_Y, DUMMY_Z - 2.9), HumanoidRootPart=(0, 160, 0),
            Torso=FIN_COLLAPSED_TORSO, Head=FIN_COLLAPSED_HEAD, **FIN_COLLAPSED_LEGS, **FIN_COLLAPSED_ARMS),
        _kf(TOTAL_DURATION, root_pos=(0, FIN_COLLAPSED_ROOT_Y, DUMMY_Z - 2.9), HumanoidRootPart=(0, 160, 0),
            Torso=FIN_COLLAPSED_TORSO, Head=FIN_COLLAPSED_HEAD, **FIN_COLLAPSED_LEGS, **FIN_COLLAPSED_ARMS),
    ]
    phases = [
        {"name": "attente", "t0": 0.0, "t1": STRIKE1_T, "expected_reversals": {}},
        {"name": "combo_1_encaisse", "t0": STRIKE1_T, "t1": STRIKE2_T, "expected_reversals": {}},
        {"name": "combo_2_encaisse", "t0": STRIKE2_T, "t1": FIN_STRIKE_T, "expected_reversals": {}},
        {"name": "ecrasee", "t0": FIN_STRIKE_T, "t1": TOTAL_DURATION, "expected_reversals": {}},
    ]
    preview_times = [0.0, STRIKE1_T, STRIKE1_T + 0.05, STRIKE2_T, STRIKE2_T + 0.06,
                      FIN_STRIKE_T, FIN_STRIKE_T + 0.10, FIN_STRIKE_T + 0.45, TOTAL_DURATION]
    engine_opts = {"handle_type": "AUTO_CLAMPED"}
    return kfs, phases, preview_times, engine_opts


# -- secondary motion (spring chase, cf r6_hit_combo) : seulement APRES
# le finisher pour l'attaquant (les coups de combo restent des poses
# CFrame propres a l'instant de contact, sans interference avec la
# calibration), et des le 1er coup pour le mannequin (il "vibre" en
# encaissant tout du long).
ATTACKER_SECONDARY_MOTION = {
    "Torso": {"channels": (0, 1, 2), "stiffness": 260.0, "damping_ratio": 0.42, "t_min": FIN_STRIKE_T},
    "Right Arm": {"channels": (0, 2), "stiffness": 300.0, "damping_ratio": 0.45, "t_min": FIN_STRIKE_T},
    "Left Arm": {"channels": (0, 2), "stiffness": 300.0, "damping_ratio": 0.45, "t_min": FIN_STRIKE_T},
}
DUMMY_SECONDARY_MOTION = {
    "Torso": {"channels": (0, 1, 2), "stiffness": 100.0, "damping_ratio": 0.45, "t_min": STRIKE1_T},
    "Head": {"channels": (0, 1, 2), "stiffness": 150.0, "damping_ratio": 0.5, "t_min": STRIKE1_T},
}
