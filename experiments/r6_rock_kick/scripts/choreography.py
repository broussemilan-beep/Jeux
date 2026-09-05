"""
Identite : le personnage TAPE LE SOL avec la jambe droite (un
enfoncement/stomp, pas un coup de pied lateral) -- l'impact fait
JAILLIR une enorme roche du sol a cet endroit precis. Le personnage
enchaine ensuite avec un coup de pied circulaire tres large qui propulse
cette roche fraichement sortie comme projectile, puis une frappe SUR la
roche en plein vol pour la rediriger plus fort vers sa trajectoire
finale (impact environnemental si aucune cible n'est touchee -- voir
rock_track.py).

Correction explicite apres un premier essai ou la roche etait deja
presente au sol AVANT l'action (retour utilisateur : "c pas tout a fait
ca en gros le perso tape le sol avec sa jambe droit et fait ressortir
une roche du sol") : l'apparition de la roche n'est plus un decor
prealable, c'est la CONSEQUENCE MESUREE du point d'impact du stomp
(voir STOMP_POINT plus bas) -- jamais un point choisi a l'oeil puis la
roche posee approximativement devant le personnage.

Lecons explicitement reappliquees suite aux retours utilisateur sur
`r6_battle_throne` (jamais redecouvertes, portees ici des le depart) :
  - JAMAIS de hold plat (2 keyframes identiques) sur une pose d'ATTENTE
    (presence de la roche, recuperation) -- voir _idle_stance_span().
    Reste distinct du hold-and-snap d'un COIL de frappe, qui lui DOIT
    rester un vrai gel (tension qui monte avant le lacher).
  - Chaine cinetique explicite et EXAGEREE au bassin/torse (demande
    utilisateur : "Le corps doit exagerer la rotation du bassin et du
    torse pour compenser les limites R6") : le rig n'a ni genou ni
    cheville, donc TOUT le "punch" d'un coup de pied circulaire doit
    venir d'une rotation de torse largement plus grande qu'un humain
    reel n'en aurait besoin, sequencee (hanche/jambe d'appui tourne en
    premier, torse suit, jambe qui frappe se detend en dernier et le
    plus vite -- un vrai fouet, pas un bloc rigide qui tourne d'un
    seul morceau).
  - Placement des pieds VERIFIE par cinematique directe
    (grounded_root_y/_balanced), jamais un offset Y constant.
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
# Cinematique directe partagee (copiee de r6_hit_combo/r6_battle_throne
# -- module independant, convention du depot : jamais d'import croise
# entre prototypes isoles).
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


def foot_tip_world(root_pos, torso_rot, leg_rot, leg_part):
    """Position MONDE du bas du pied (bottom tip) -- utilisee pour poser
    la roche exactement la ou le pied la percute, plutot que de deviner
    une position puis chercher un renversement qui l'atteigne (voir
    docstring de module -- ici la roche n'a pas de contrainte propre,
    on peut se permettre de la placer au point mesure directement)."""
    joint = joint_for_part(leg_part)
    c0 = np.array(JOINTS[joint]["C0"]["pos"])
    c1 = np.array(JOINTS[joint]["C1"]["pos"])
    r_torso = _euler_xyz_matrix(*torso_rot)
    r_leg_local = _euler_xyz_matrix(*leg_rot)
    leg_local_pos = c0 - r_leg_local @ c1
    r_leg_world = r_torso @ r_leg_local
    half = PART_SIZES[leg_part][1] / 2.0
    offset = r_torso @ leg_local_pos + r_leg_world @ np.array([0.0, -half, 0.0])
    return np.array(root_pos) + offset


def sphere_center_for_surface_contact(contact_point, char_root_xz, radius):
    """Etant donne un point de contact mesure (bout du pied/poing) et la
    position XZ de la racine du personnage, calcule le CENTRE d'une
    sphere de rayon `radius`, posee au sol (centre a Y=radius), telle
    que ce point de contact tombe EXACTEMENT sur sa surface -- jamais
    sur son centre (une frappe qui atterrit au centre d'une sphere de
    plusieurs studs de rayon voudrait dire un poing enfonce en plein
    milieu de la roche, pas un impact credible en surface). Le centre
    est place plus loin du personnage que le point de contact, le long
    du rayon horizontal personnage->contact : le coup frappe la face
    avant de la roche, qui s'etend au-dela vers l'exterieur."""
    cx0, cz0 = char_root_xz
    fx, fy, fz = contact_point
    dx, dz = fx - cx0, fz - cz0
    horiz_dist = math.hypot(dx, dz)
    ux, uz = dx / horiz_dist, dz / horiz_dist
    dy = fy - radius
    remaining_sq = radius * radius - dy * dy
    if remaining_sq < 0:
        raise ValueError(f"point de contact (Y={fy:.3f}) plus haut que le sommet de la sphere "
                          f"(rayon={radius:.3f}) -- augmenter le rayon ou baisser le point de contact")
    horiz_needed = math.sqrt(remaining_sq)
    return np.array([fx + ux * horiz_needed, radius, fz + uz * horiz_needed])


def sphere_center_for_surface_contact_3d(contact_point, from_point, radius):
    """Variante 3D de sphere_center_for_surface_contact(), pour une
    roche DEJA EN VOL (pas posee au sol -- la contrainte "centre a
    Y=radius" ne s'applique plus) : place le centre a distance `radius`
    du point de contact, le long du rayon from_point->contact_point
    prolonge -- le poing atteint la face de la roche la plus proche du
    personnage, la roche s'etend au-dela le long de cette meme droite."""
    contact = np.array(contact_point, dtype=float)
    origin = np.array(from_point, dtype=float)
    direction = contact - origin
    direction = direction / np.linalg.norm(direction)
    return contact + direction * radius


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
# Disposition : le personnage reste immobile en Z (aucun deplacement de
# root necessaire pour ce skill -- coup de pied puis frappe de suivi,
# meme convention "combo sans trajet" que r6_hit_combo). La roche est
# devant et legerement sur le cote -- position EXACTE mesuree par
# cinematique directe sur le pied qui frappe (voir KICK_CONTACT_POINT
# plus bas), pas choisie a l'oeil puis retro-ajustee.
# =======================================================================
CHAR_Z = -2.0
ROCK_RADIUS = 2.0   # "enorme roche" -- diametre ~4 studs, plus haute que les hanches du personnage (GROUND_Y=3.0)

_READY_TORSO = (4, 0, 0)
_READY_HEAD = (2, 0, 0)
_READY_LEGS = {"Right Leg": (4, 0, 6), "Left Leg": (6, 0, -5)}
_READY_ARMS = {"Right Arm": (18, 0, -8), "Left Arm": (20, 0, 10)}
_READY_ROOT_Y = grounded_root_y_balanced(_READY_TORSO, _READY_LEGS["Left Leg"], _READY_LEGS["Right Leg"])

# =======================================================================
# Phase 1 -- garde initiale, AUCUNE roche encore (T0_END secondes).
# Attente vivante, PAS un hold plat (voir lecon de module).
# =======================================================================
T0_END = _fr(18)   # 0.6s -- juste assez pour etablir le plan, la roche n'existe pas encore a ce stade


def phase1_idle():
    return _idle_stance_span(0.0, T0_END, (0, 0, CHAR_Z), REST,
                              _READY_TORSO, _READY_HEAD, _READY_LEGS, _READY_ARMS,
                              period=0.6, phase0=0.0, amp_leg=3.0, amp_torso=2.0)


# =======================================================================
# Phase STOMP -- la jambe droite s'enfonce dans le sol. Meme discipline
# hold-and-snap que le reste du combo (chambrage tenu, lacher en
# quelques frames), mais un STOMP est un mouvement VERTICAL (la jambe
# retombe depuis un chambrage haut jusqu'a s'ecraser au sol), pas un
# balayage lateral comme le coup de pied circulaire qui suit -- le
# torse charge en ARRIERE au chambrage (contrepoids pendant que la
# jambe se leve) puis fouette vers l'AVANT/BAS au lacher (transferer le
# poids du corps dans l'impact, meme exageration bassin/torse que
# partout ailleurs dans ce fichier).
# =======================================================================
STOMP_WINDUP_T = T0_END + _fr(12)    # 0.4s : la jambe droite se souleve
STOMP_HOLD_T = STOMP_WINDUP_T + _fr(6)   # vrai hold (0.2s) -- la jambe reste chargee en l'air avant de s'ecraser
STOMP_STRIKE_T = STOMP_HOLD_T + _fr(3)   # lacher rapide (0.1s) -- la jambe s'ecrase au sol
STOMP_RECOVER_T = STOMP_STRIKE_T + _fr(6)  # le corps absorbe le choc de l'impact avant d'enchainer

STOMP_WINDUP_TORSO = (-18, 8, 0)
STOMP_WINDUP_HEAD = (-10, 0, 0)
STOMP_WINDUP_LEGS = {"Right Leg": (80, 0, -4), "Left Leg": (2, 0, 4)}
STOMP_WINDUP_ARMS = {"Right Arm": (10, 0, -10), "Left Arm": (55, 0, 22)}
STOMP_WINDUP_ROOT_Y = grounded_root_y(STOMP_WINDUP_TORSO, STOMP_WINDUP_LEGS["Left Leg"], "Left Leg")

# -- lacher : le torse renverse de Y=+8 (charge arriere) a Y=+4 (fouette
# avant/bas, X : -18 -> +32) ; la jambe droite s'ecrase du chambrage
# (X=80) jusqu'a quasiment sous la hanche (X=-8) -- MEME axe Z conserve
# (-4 -> -8, un stomp descend, il ne change pas de cote comme le coup de
# pied circulaire qui suit) : c'est un ecrasement vertical, pas un fouet
# lateral.
STOMP_STRIKE_TORSO = (32, 4, 0)
STOMP_STRIKE_HEAD = (20, 0, 0)
STOMP_STRIKE_LEGS = {"Right Leg": (-8, 0, -8), "Left Leg": (4, 0, 6)}
STOMP_STRIKE_ARMS = {"Right Arm": (55, 0, -18), "Left Arm": (12, 0, 16)}
STOMP_STRIKE_ROOT_Y = grounded_root_y(STOMP_STRIKE_TORSO, STOMP_STRIKE_LEGS["Left Leg"], "Left Leg")

# -- point d'impact MESURE (pas choisi a l'oeil) : c'est LA ou la roche
# va jaillir du sol -- voir ROCK_X0/ROCK_Z0 plus bas, qui reprennent
# directement X/Z de ce point (seul Y differe, la roche repose au sol
# a Y=ROCK_RADIUS, le pied lui-meme s'enfonce legerement sous Y=0 au
# moment de l'impact -- normal pour un stomp qui fissure le sol, pas
# une anomalie de placement).
_STOMP_STRIKE_ROOT_POS = (0.0, STOMP_STRIKE_ROOT_Y, CHAR_Z)
STOMP_POINT = foot_tip_world(_STOMP_STRIKE_ROOT_POS, STOMP_STRIKE_TORSO, STOMP_STRIKE_LEGS["Right Leg"], "Right Leg")

STOMP_RECOVER_TORSO = (10, 6, 0)
STOMP_RECOVER_HEAD = (6, 0, 0)
STOMP_RECOVER_LEGS = {"Right Leg": (2, 0, 2), "Left Leg": (6, 0, -4)}
STOMP_RECOVER_ARMS = {"Right Arm": (28, 0, -14), "Left Arm": (22, 0, 16)}
STOMP_RECOVER_ROOT_Y = grounded_root_y_balanced(STOMP_RECOVER_TORSO, STOMP_RECOVER_LEGS["Left Leg"], STOMP_RECOVER_LEGS["Right Leg"])


def phase_stomp():
    return [
        _kf(STOMP_WINDUP_T, root_pos=(0, STOMP_WINDUP_ROOT_Y, CHAR_Z), Torso=STOMP_WINDUP_TORSO,
            Head=STOMP_WINDUP_HEAD, **STOMP_WINDUP_LEGS, **STOMP_WINDUP_ARMS),
        _kf(STOMP_HOLD_T, root_pos=(0, STOMP_WINDUP_ROOT_Y, CHAR_Z), Torso=STOMP_WINDUP_TORSO,
            Head=STOMP_WINDUP_HEAD, **STOMP_WINDUP_LEGS, **STOMP_WINDUP_ARMS),
        _kf(STOMP_STRIKE_T, root_pos=(0, STOMP_STRIKE_ROOT_Y, CHAR_Z), Torso=STOMP_STRIKE_TORSO,
            Head=STOMP_STRIKE_HEAD, **STOMP_STRIKE_LEGS, **STOMP_STRIKE_ARMS),
        _kf(STOMP_RECOVER_T, root_pos=(0, STOMP_RECOVER_ROOT_Y, CHAR_Z), Torso=STOMP_RECOVER_TORSO,
            Head=STOMP_RECOVER_HEAD, **STOMP_RECOVER_LEGS, **STOMP_RECOVER_ARMS),
    ]


# =======================================================================
# Phase 2 -- prise d'appui + coup de pied circulaire tres large (frappe
# la roche qui vient de jaillir du sol -- voir STOMP_POINT ci-dessus).
# Chaine cinetique EXPLICITE : la jambe d'appui (Left) pivote en premier
# (WINDUP), le torse suit et charge tres au-dela de ce qu'un torse humain
# ferait (retour utilisateur : exagerer pour compenser l'absence de
# genou/cheville), puis tout se relache en un SNAP (2 frames, meme
# principe hold-and-snap que le reste du depot) -- la jambe qui frappe
# est ce qui bouge le plus vite et le plus tard dans la chaine, comme un
# fouet.
# =======================================================================
WINDUP_T = STOMP_RECOVER_T + _fr(6)     # enchaine directement depuis la recuperation du stomp
COIL_T = WINDUP_T + _fr(18)     # 0.6s : chambrage complet
COIL_HOLD_T = COIL_T + _fr(6)   # vrai hold (0.2s) -- la tension doit se voir avant le lacher
STRIKE_T = COIL_HOLD_T + _fr(2)  # snap quasi instantane (cf. hold-and-snap)

WINDUP_TORSO = (10, -35, -8)
WINDUP_HEAD = (6, -20, 0)
WINDUP_LEGS = {"Right Leg": (20, 0, -18), "Left Leg": (2, 0, 6)}
WINDUP_ARMS = {"Right Arm": (24, 0, -20), "Left Arm": (40, 0, 30)}
WINDUP_ROOT_Y = grounded_root_y_balanced(WINDUP_TORSO, WINDUP_LEGS["Left Leg"], WINDUP_LEGS["Right Leg"])

# -- chambrage : torse tourne tres loin (Y=-62, largement au-dela d'un
# vrai buste humain -- compensation explicite demandee) pendant que la
# jambe d'appui (Left, Y local = pivot sur l'avant du pied) commence deja
# a tourner dans le MEME sens que le futur relachement (elle initie la
# chaine, le torse et la jambe qui frappe suivent).
COIL_TORSO = (16, -62, -14)
COIL_HEAD = (10, -34, 0)
COIL_LEGS = {"Right Leg": (58, 0, -34), "Left Leg": (4, -16, 8)}
COIL_ARMS = {"Right Arm": (30, 0, -26), "Left Arm": (55, 0, 40)}
COIL_ROOT_Y = grounded_root_y(COIL_TORSO, COIL_LEGS["Left Leg"], "Left Leg")

# -- lacher : renversement complet du torse (Y : -62 -> +78, ~140 deg de
# fouet -- l'exageration demandee) ; la jambe d'appui acheve son pivot
# (Y local -16 -> +30) ; la jambe qui frappe INVERSE le signe de son axe
# Z (chambre a -34, frappe a +58 -- meme principe de renversement d'axe
# que tout le reste du depot, jamais juste une amplitude qui grandit).
STRIKE_TORSO = (-8, 78, 16)
STRIKE_HEAD = (12, 40, 0)
STRIKE_LEGS = {"Right Leg": (96, 0, 58), "Left Leg": (6, 30, -10)}
STRIKE_ARMS = {"Right Arm": (34, 0, -30), "Left Arm": (70, 0, 60)}
STRIKE_ROOT_Y = grounded_root_y(STRIKE_TORSO, STRIKE_LEGS["Left Leg"], "Left Leg")

# -- point de contact du coup de pied MESURE (verification, pas
# placement -- voir plus bas) : contrairement au premier essai, la
# roche n'est plus placee a partir de ce point. Elle jaillit du sol a
# STOMP_POINT (voir Phase STOMP ci-dessus) ; ce contact-ci sert
# seulement a VERIFIER que le pied qui frappe atteint bien sa surface,
# via calibrate.py.
_STRIKE_ROOT_POS = (0.0, STRIKE_ROOT_Y, CHAR_Z)
KICK_CONTACT_POINT = foot_tip_world(_STRIKE_ROOT_POS, STRIKE_TORSO, STRIKE_LEGS["Right Leg"], "Right Leg")

# -- la roche jaillit EXACTEMENT au point d'impact du stomp (X/Z de
# STOMP_POINT) ; seul Y differe (la roche repose au sol une fois sortie,
# Y=ROCK_RADIUS, quel que soit le Y exact -- legerement negatif -- du
# pied qui a fissure le sol a cet endroit).
ROCK_X0 = float(STOMP_POINT[0])
ROCK_Z0 = float(STOMP_POINT[2])
ROCK_REST_Y = ROCK_RADIUS

# -- suite : le torse continue de tourner sous son propre elan
# (over-rotation -- l'inertie ne s'arrete pas net a l'instant du contact)
# avant que tout ne se stabilise.
FOLLOWTHROUGH_T = STRIKE_T + _fr(6)
FOLLOWTHROUGH_TORSO = (-14, 92, 20)
FOLLOWTHROUGH_HEAD = (14, 48, 0)
FOLLOWTHROUGH_LEGS = {"Right Leg": (88, 0, 66), "Left Leg": (8, 34, -12)}
FOLLOWTHROUGH_ARMS = {"Right Arm": (30, 0, -26), "Left Arm": (76, 0, 66)}
FOLLOWTHROUGH_ROOT_Y = grounded_root_y(FOLLOWTHROUGH_TORSO, FOLLOWTHROUGH_LEGS["Left Leg"], "Left Leg")

RECOVER_T = FOLLOWTHROUGH_T + _fr(10)
RECOVER_TORSO = (0, 20, 0)
RECOVER_HEAD = (4, 10, 0)
RECOVER_LEGS = {"Right Leg": (10, 10, 10), "Left Leg": (8, 10, -8)}
RECOVER_ARMS = {"Right Arm": (22, 0, -14), "Left Arm": (26, 0, 16)}
RECOVER_ROOT_Y = grounded_root_y_balanced(RECOVER_TORSO, RECOVER_LEGS["Left Leg"], RECOVER_LEGS["Right Leg"])


def phase2_kick():
    return [
        _kf(WINDUP_T, root_pos=(0, WINDUP_ROOT_Y, CHAR_Z), Torso=WINDUP_TORSO,
            Head=WINDUP_HEAD, **WINDUP_LEGS, **WINDUP_ARMS),
        _kf(COIL_T, root_pos=(0, COIL_ROOT_Y, CHAR_Z), Torso=COIL_TORSO,
            Head=COIL_HEAD, **COIL_LEGS, **COIL_ARMS),
        _kf(COIL_HOLD_T, root_pos=(0, COIL_ROOT_Y, CHAR_Z), Torso=COIL_TORSO,
            Head=COIL_HEAD, **COIL_LEGS, **COIL_ARMS),
        _kf(STRIKE_T, root_pos=(0, STRIKE_ROOT_Y, CHAR_Z), Torso=STRIKE_TORSO,
            Head=STRIKE_HEAD, **STRIKE_LEGS, **STRIKE_ARMS),
        _kf(FOLLOWTHROUGH_T, root_pos=(0, FOLLOWTHROUGH_ROOT_Y, CHAR_Z), Torso=FOLLOWTHROUGH_TORSO,
            Head=FOLLOWTHROUGH_HEAD, **FOLLOWTHROUGH_LEGS, **FOLLOWTHROUGH_ARMS),
        _kf(RECOVER_T, root_pos=(0, RECOVER_ROOT_Y, CHAR_Z), Torso=RECOVER_TORSO,
            Head=RECOVER_HEAD, **RECOVER_LEGS, **RECOVER_ARMS),
    ]


# =======================================================================
# Phase 4 -- frappe de suivi SUR la roche (deja en vol, voir
# rock_track.py) pour la rediriger plus fort vers sa trajectoire finale.
# Vocabulaire de coup de poing (cross), pas de pied -- varie le geste,
# et la roche est deja haute/loin, un second coup de pied depuis un
# appui statique n'atteindrait plus rien. Meme chaine cinetique
# (hanche -> torse -> bras), meme hold-and-snap (coil bref tenu, lacher
# en 2 frames).
# =======================================================================
FOLLOWUP_WINDUP_T = RECOVER_T + _fr(5)
FOLLOWUP_COIL_T = FOLLOWUP_WINDUP_T + _fr(6)
FOLLOWUP_COIL_HOLD_T = FOLLOWUP_COIL_T + _fr(4)
FOLLOWUP_STRIKE_T = FOLLOWUP_COIL_HOLD_T + _fr(2)

FOLLOWUP_WINDUP_TORSO = (6, -10, -4)
FOLLOWUP_WINDUP_HEAD = (4, -6, 0)
FOLLOWUP_WINDUP_LEGS = {"Right Leg": (8, 6, 8), "Left Leg": (10, 6, -6)}
FOLLOWUP_WINDUP_RIGHT_ARM = (30, 0, -50)
FOLLOWUP_WINDUP_LEFT_ARM = (20, 0, 16)
FOLLOWUP_WINDUP_ROOT_Y = grounded_root_y_balanced(FOLLOWUP_WINDUP_TORSO, FOLLOWUP_WINDUP_LEGS["Left Leg"], FOLLOWUP_WINDUP_LEGS["Right Leg"])

FOLLOWUP_COIL_TORSO = (10, -34, -8)
FOLLOWUP_COIL_HEAD = (6, -20, 0)
FOLLOWUP_COIL_LEGS = {"Right Leg": (10, 10, 12), "Left Leg": (14, 8, -10)}
FOLLOWUP_COIL_RIGHT_ARM = (70, 0, -74)
FOLLOWUP_COIL_LEFT_ARM = (16, 0, 10)
FOLLOWUP_COIL_ROOT_Y = grounded_root_y_balanced(FOLLOWUP_COIL_TORSO, FOLLOWUP_COIL_LEGS["Left Leg"], FOLLOWUP_COIL_LEGS["Right Leg"])

# -- lacher : le torse repart en sens inverse (Y -34 -> +50), le bras
# droit fouette de -74 a +30 en Z (meme principe de renversement).
FOLLOWUP_STRIKE_TORSO = (-6, 50, 10)
FOLLOWUP_STRIKE_HEAD = (10, 26, 0)
FOLLOWUP_STRIKE_LEGS = {"Right Leg": (14, 6, -10), "Left Leg": (18, 6, 10)}
FOLLOWUP_STRIKE_RIGHT_ARM = (100, 0, 30)
FOLLOWUP_STRIKE_LEFT_ARM = (18, 0, 12)
FOLLOWUP_STRIKE_ROOT_Y = grounded_root_y_balanced(FOLLOWUP_STRIKE_TORSO, FOLLOWUP_STRIKE_LEGS["Left Leg"], FOLLOWUP_STRIKE_LEGS["Right Leg"])

# -- point de contact du suivi, mesure comme le premier (voir plus
# haut) : c'est le poing qui doit atteindre CE point, mais la roche
# elle-meme (son centre, utilise par rock_track.py pour placer la
# trajectoire) est reculee de sorte que ce point tombe sur SA SURFACE --
# meme raisonnement que ROCK_X0/ROCK_Z0 plus haut, jamais le centre
# colle sur le point de contact.
_FOLLOWUP_ROOT_POS = (0.0, FOLLOWUP_STRIKE_ROOT_Y, CHAR_Z)
FOLLOWUP_CONTACT_POINT = fist_tip_world(_FOLLOWUP_ROOT_POS, FOLLOWUP_STRIKE_TORSO, FOLLOWUP_STRIKE_RIGHT_ARM, "Right Arm")
# -- la roche est deja EN VOL a cet instant (pas posee au sol) : variante
# 3D de la fonction ci-dessus (voir sphere_center_for_surface_contact_3d),
# le rayon personnage->poing prolonge de ROCK_RADIUS place son centre.
FOLLOWUP_ROCK_CENTER = sphere_center_for_surface_contact_3d(FOLLOWUP_CONTACT_POINT, _FOLLOWUP_ROOT_POS, ROCK_RADIUS)

FOLLOWUP_RECOVER_T = FOLLOWUP_STRIKE_T + _fr(10)


def phase4_followup():
    kfs = [
        _kf(FOLLOWUP_WINDUP_T, root_pos=(0, FOLLOWUP_WINDUP_ROOT_Y, CHAR_Z), Torso=FOLLOWUP_WINDUP_TORSO,
            Head=FOLLOWUP_WINDUP_HEAD, **FOLLOWUP_WINDUP_LEGS,
            **{"Right Arm": FOLLOWUP_WINDUP_RIGHT_ARM, "Left Arm": FOLLOWUP_WINDUP_LEFT_ARM}),
        _kf(FOLLOWUP_COIL_T, root_pos=(0, FOLLOWUP_COIL_ROOT_Y, CHAR_Z), Torso=FOLLOWUP_COIL_TORSO,
            Head=FOLLOWUP_COIL_HEAD, **FOLLOWUP_COIL_LEGS,
            **{"Right Arm": FOLLOWUP_COIL_RIGHT_ARM, "Left Arm": FOLLOWUP_COIL_LEFT_ARM}),
        _kf(FOLLOWUP_COIL_HOLD_T, root_pos=(0, FOLLOWUP_COIL_ROOT_Y, CHAR_Z), Torso=FOLLOWUP_COIL_TORSO,
            Head=FOLLOWUP_COIL_HEAD, **FOLLOWUP_COIL_LEGS,
            **{"Right Arm": FOLLOWUP_COIL_RIGHT_ARM, "Left Arm": FOLLOWUP_COIL_LEFT_ARM}),
        _kf(FOLLOWUP_STRIKE_T, root_pos=(0, FOLLOWUP_STRIKE_ROOT_Y, CHAR_Z), Torso=FOLLOWUP_STRIKE_TORSO,
            Head=FOLLOWUP_STRIKE_HEAD, **FOLLOWUP_STRIKE_LEGS,
            **{"Right Arm": FOLLOWUP_STRIKE_RIGHT_ARM, "Left Arm": FOLLOWUP_STRIKE_LEFT_ARM}),
    ]
    kfs += _idle_stance_span(FOLLOWUP_STRIKE_T + _fr(3), FOLLOWUP_RECOVER_T, (0, 0, CHAR_Z), REST,
                              _READY_TORSO, _READY_HEAD, _READY_LEGS, _READY_ARMS,
                              period=0.5, phase0=0.0, amp_leg=2.5, amp_torso=2.0)
    return kfs


def striker_track():
    keyframes = phase1_idle() + phase_stomp() + phase2_kick() + phase4_followup()
    phases = [
        {"name": "garde", "t0": 0.0, "t1": STOMP_WINDUP_T, "expected_reversals": {}},
        {"name": "stomp", "t0": STOMP_WINDUP_T, "t1": WINDUP_T, "expected_reversals": {}},
        {"name": "coup_de_pied", "t0": WINDUP_T, "t1": RECOVER_T, "expected_reversals": {}},
        {"name": "frappe_de_suivi", "t0": RECOVER_T, "t1": FOLLOWUP_RECOVER_T, "expected_reversals": {}},
    ]
    preview_times = [0.0, STOMP_WINDUP_T, STOMP_HOLD_T, STOMP_STRIKE_T, STOMP_RECOVER_T,
                      WINDUP_T, COIL_T, COIL_HOLD_T, STRIKE_T, FOLLOWTHROUGH_T, RECOVER_T,
                      FOLLOWUP_WINDUP_T, FOLLOWUP_COIL_T, FOLLOWUP_STRIKE_T, FOLLOWUP_RECOVER_T]
    engine_opts = {"handle_type": "AUTO_CLAMPED"}
    return keyframes, phases, preview_times, engine_opts


TOTAL_DURATION = FOLLOWUP_RECOVER_T
