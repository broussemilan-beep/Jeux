"""
Identite : competence solo "Black Hole" -- pas de combo, pas de cible, un
seul personnage qui s'accroupit (anticipation), se releve en levitation
avec les bras largement ecartes (geste telekinesique), maintient la pose
pendant que des fragments du sol sont arraches et convergent vers un
point central (script separe, voir black_hole_track.py) jusqu'a former un
disque d'accretion + un coeur noir, encaisse un pic de tension (la
gravitation le tire vers l'avant), puis se pose au sol et se detend.

Reference fournie par l'utilisateur (pas une demande texte -- une VRAIE
capture video, 14.16s/60fps/888x1240, "Black Hole Ability", Roblox
Studio, extraite frame par frame via ffmpeg, PAS juste survolee) :
analyse complete au README ("Recherche"), resume ici pour justifier
chaque choix de pose ci-dessous :
  R1. Position de depart : personnage debout normal, bras le long du
      corps (frame ~0.25s).
  R2. Anticipation : accroupissement marque, torse plie vers l'avant,
      camera tres basse/proche pour la dramatisation (frame ~3.25s).
  R3. Relevement explosif + bras ECARTES A L'HORIZONTALE (pas levés au-
      dessus de la tete -- un vrai T-pose lateral, style "telekinesie"),
      le personnage DECOLLE du sol (frame ~5s/6.25s) ; des fragments du
      sol/decor sont arraches et flottent autour de lui.
  R4. Plan large : la camera s'eloigne, les fragments se regroupent en
      amas au-dessus du sol (frame ~7.5s), le personnage hors cadre.
  R5. Formation du trou noir : un anneau lumineux jaune/or (disque
      d'accretion) apparait au centre de l'amas, coeur spherique NOIR au
      milieu, fond de scene qui s'assombrit fortement (vignette quasi
      totale), trainees blanches radiales qui spiralent VERS le disque
      (frames ~8.75s a 11.75s -- le plus long segment de la reference).
  R6. Fondu au noir final (fin de la capture, ~13.5-14s) -- coupe plutot
      qu'une vraie resolution filmee ; la suite (retour au sol, sortie de
      pose) est une decision de conception ASSUMEE de cette session, pas
      lue dans la reference (voir README).

Difference structurelle avec TOUS les prototypes precedents de ce depot
(rock_kick, hit_combo, solar_smite, divine_orb...) : le personnage QUITTE
LE SOL entierement pendant la levitation (R3-R5) -- jusqu'ici
`calibrate.py` ne verifiait QUE des poses au sol. Ce prototype ajoute
donc un 2e mode de verification (personnage explicitement AERIEN, pas de
pied au sol attendu) plutot que d'elargir la tolerance jusqu'a ce que le
check au sol se taise -- voir calibrate.py.

Lecons du depot deja etablies, reappliquees sans nouveau retour :
  - JAMAIS de hold plat sur une pose d'ATTENTE (garde initiale, retour
    final) -- _idle_stance_span(). Le nouvel equivalent aerien
    (_levitate_span()) applique le meme principe en vol : un hover
    parfaitement immobile ne se lit pas comme une vraie levitation.
  - Un vrai hold (coil) reste gele -- l'accroupissement (R2) et le pic de
    tension (avant R6) sont de vrais holds, pas juste des poses de
    passage.
  - Placement des pieds verifie par cinematique directe
    (grounded_root_y_balanced), jamais un offset Y constant, pour toutes
    les phases AU SOL.
  - Solveur de ressort ANALYTIQUE EXACT (anim_engine._spring_chase,
    voir r6_solar_smite) pour le secondary motion -- pas d'integration
    d'Euler.
"""
import math

import numpy as np

from r6_rig import JOINTS, PART_SIZES, joint_for_part

REST = (0.0, 0.0, 0.0)
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


# -- Attente vivante au sol (voir docstring de module) : jamais un hold plat.
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
                       period=0.6, phase0=0.0, amp_leg=3.0, amp_torso=2.0):
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


# -- Hover aerien (nouveau -- aucun prototype precedent n'a de phase ou
# le personnage quitte reellement le sol) : meme principe que l'attente
# vivante au sol (jamais un hold plat), mais le "sol de reference" pour
# grounded_root_y_balanced est REMPLACE par LEVITATE_Y (le personnage
# ne touche plus Y=0) et l'amplitude porte sur les BRAS/TORSE (le vent
# de la gravitation qui les fait osciller), pas sur les jambes (elles
# pendent, ballantes, pas d'appui a simuler).
def _levitate_kf(t, root_pos, humanoid_root_part, base_torso, base_head, base_legs, base_arms, phase,
                  levitate_y, amp_arm=4.0, amp_bob=0.12):
    s, c = math.sin(phase), math.cos(phase)
    arms = {
        "Right Arm": (base_arms["Right Arm"][0], base_arms["Right Arm"][1], base_arms["Right Arm"][2] + amp_arm * s),
        "Left Arm": (base_arms["Left Arm"][0], base_arms["Left Arm"][1], base_arms["Left Arm"][2] - amp_arm * s),
    }
    x, _, z = root_pos
    root_y = levitate_y + amp_bob * c
    return _kf(t, root_pos=(x, root_y, z), HumanoidRootPart=humanoid_root_part,
               Torso=base_torso, Head=base_head, **base_legs, **arms)


def _levitate_span(t0, t1, root_pos, humanoid_root_part, base_torso, base_head, base_legs, base_arms,
                    levitate_y, period=0.9, phase0=0.0, amp_arm=4.0, amp_bob=0.12):
    kfs = []
    half_period = period / 2.0
    n = max(1, round((t1 - t0) / half_period))
    for i in range(n + 1):
        t = t0 + (t1 - t0) * i / n
        phase = phase0 + (t - t0) / period * 2 * math.pi
        a_arm, a_bob = (0.0, 0.0) if i in (0, n) else (amp_arm, amp_bob)
        kfs.append(_levitate_kf(t, root_pos, humanoid_root_part, base_torso, base_head, base_legs, base_arms,
                                 phase, levitate_y, a_arm, a_bob))
    return kfs


# =======================================================================
# Disposition : un seul personnage, centre (pas de mannequin -- meme
# convention "fonctionne seul" que r6_rock_kick pour la sequence
# principale, mais ici il n'y a litteralement personne a frapper : la
# reference elle-meme ne montre qu'un seul personnage).
# =======================================================================
CHAR_X = 0.0
CHAR_Z0 = 0.0

_READY_TORSO = (0, 0, 0)
_READY_HEAD = (0, 0, 0)
_READY_LEGS = {"Right Leg": (0, 0, 4), "Left Leg": (0, 0, -4)}
_READY_ARMS = {"Right Arm": (4, 0, -4), "Left Arm": (4, 0, 4)}

# =======================================================================
# Phase 0 -- debout normal, attente vivante (R1). Allongee suite a un
# retour explicite ("manque de frame d'un debut" -- 0.6s ne laissait pas
# le temps a un plan d'etablissement de se lire avant que tout s'enchaine,
# voir aussi la caméra plus bas : elle glissait deja vers le crouch des
# t=0, jamais un vrai plan fixe).
# =======================================================================
T0_END = _fr(30)  # 1.0s -- vrai plan d'etablissement tenu (etait 0.6s/18 frames)


def phase0_idle():
    return _idle_stance_span(0.0, T0_END, (CHAR_X, 0, CHAR_Z0), REST,
                              _READY_TORSO, _READY_HEAD, _READY_LEGS, _READY_ARMS,
                              period=0.6, phase0=0.0, amp_leg=3.0, amp_torso=2.0)


_READY_ROOT_Y = grounded_root_y_balanced(_READY_TORSO, _READY_LEGS["Left Leg"], _READY_LEGS["Right Leg"])

# =======================================================================
# Phase CROUCH -- accroupissement marque, torse plie vers l'avant (R2).
# Vrai hold au fond (CROUCH_HOLD_T) : l'anticipation doit se lire comme
# un vrai gel, pas un passage.
# =======================================================================
CROUCH_T = T0_END + _fr(15)        # 0.5s -- descente lisible, pas un snap
CROUCH_HOLD_T = CROUCH_T + _fr(9)  # hold bref (0.3s), assez pour se lire

CROUCH_TORSO = (70, 0, 0)
CROUCH_HEAD = (40, 0, 0)
CROUCH_LEGS = {"Right Leg": (32, 0, 15), "Left Leg": (32, 0, -15)}
# -- bras balayes en ARRIERE et legerement releves (comme un sprinter au
# starting-block, PAS tucked contre le corps) : corrige suite a un retour
# explicite ("manque d'exageration", revu contre la reference -- frame
# ~3.25s montre les bras loin derriere le torse, pas replies pres du
# corps comme la version precedente).
CROUCH_ARMS = {"Right Arm": (-38, 0, -22), "Left Arm": (-38, 0, 22)}
CROUCH_ROOT_Y = grounded_root_y_balanced(CROUCH_TORSO, CROUCH_LEGS["Left Leg"], CROUCH_LEGS["Right Leg"])


def phase_crouch():
    return [
        _kf(CROUCH_T, root_pos=(CHAR_X, CROUCH_ROOT_Y, CHAR_Z0), Torso=CROUCH_TORSO, Head=CROUCH_HEAD,
            **CROUCH_LEGS, **CROUCH_ARMS),
        _kf(CROUCH_HOLD_T, root_pos=(CHAR_X, CROUCH_ROOT_Y, CHAR_Z0), Torso=CROUCH_TORSO, Head=CROUCH_HEAD,
            **CROUCH_LEGS, **CROUCH_ARMS),
    ]


# =======================================================================
# Phase RISE -- relevement EXPLOSIF, bras ecartes a l'horizontale style
# telekinesie (R3, pas un lever au-dessus de la tete comme solar_smite --
# geste different, delibere). Le personnage DECOLLE : LEVITATE_Y > 0,
# mesure au-dessus du sol, pas un offset arbitraire -- calcule comme
# l'ecart entre la pose CROUCH (au sol) et une hauteur de vol choisie.
# =======================================================================
RISE_T = CROUCH_HOLD_T + _fr(11)  # 0.37s -- release rapide, contraste avec le hold

# -- clearance des pieds : PAS un offset choisi a la main sur root_pos.y
# (piege trouve en verifiant : une valeur "qui semble haute" comme 3.2
# peut correspondre a une clearance de pieds quasi NULLE selon l'angle
# des jambes -- grounded_root_y_balanced(pose) donne deja la valeur de
# root_pos.y qui pose les pieds PILE sur Y=0 pour CETTE pose ; la vraie
# hauteur de vol est root_pos.y moins CETTE valeur, pas moins Y=0).
# clearance choisie desroissante RISE > CLIMAX > RELEASE > LAND(=0) :
# le personnage "descend" progressivement a mesure que le trou noir le
# tire vers le bas, jusqu'a toucher terre a LAND_T.
RISE_CLEARANCE = 2.4     # nette prise d'altitude, lisible a l'ecran (R3 : decollage franc)
CLIMAX_CLEARANCE = 1.3   # deja tire vers le bas par la gravitation, mais encore clairement en l'air
RELEASE_CLEARANCE = 0.5  # sur le point de toucher terre

RISE_TORSO = (-22, 0, 0)
RISE_HEAD = (-24, 0, 0)
RISE_LEGS = {"Right Leg": (10, 0, 18), "Left Leg": (10, 0, -18)}
# -- bras releves en angle (~30 deg au-dessus de l'horizontale, pas un T
# plat) : corrige contre la reference (frame ~5-6.25s -- les bras
# montent nettement au-dessus de l'horizontale, pas paralleles au sol).
RISE_ARMS = {"Right Arm": (28, 0, -80), "Left Arm": (28, 0, 80)}
LEVITATE_ROOT_Y = grounded_root_y_balanced(RISE_TORSO, RISE_LEGS["Left Leg"], RISE_LEGS["Right Leg"]) + RISE_CLEARANCE


def phase_rise():
    return [_kf(RISE_T, root_pos=(CHAR_X, LEVITATE_ROOT_Y, CHAR_Z0), Torso=RISE_TORSO, Head=RISE_HEAD,
                **RISE_LEGS, **RISE_ARMS)]


# =======================================================================
# Phase HOLD -- levitation soutenue, bras ecartes, hover vivant (R3-R4 :
# c'est pendant cette fenetre que les fragments se regroupent et que le
# disque d'accretion se forme -- voir black_hole_track.py, synchronise
# sur les memes instants). Duree la plus longue de la sequence,
# deliberement (R5 : le segment le plus long de la reference).
# =======================================================================
HOLD_END_T = RISE_T + 3.4  # 3.4s de vol soutenu -- le temps que les debris convergent (voir black_hole_track.py)


def phase_hold():
    # [1:] : phase_rise() pose deja un keyframe identique a RISE_T, on
    # evite le doublon (harmless pour Blender mais inutile).
    return _levitate_span(RISE_T, HOLD_END_T, (CHAR_X, 0, CHAR_Z0), REST,
                           RISE_TORSO, RISE_HEAD, RISE_LEGS, RISE_ARMS,
                           levitate_y=LEVITATE_ROOT_Y, period=1.0, phase0=0.0, amp_arm=8.0, amp_bob=0.35)[1:]


# =======================================================================
# Phase CLIMAX -- pic de tension : le trou noir atteint sa pleine
# intensite, la gravitation tire visiblement le personnage (bras qui se
# resserrent, torse qui penche vers l'avant/le centre, tete baissee --
# oppose au relachement grand-ouvert de RISE/HOLD, pour que le pic se
# LISE comme un pic, pas une simple continuation).
# =======================================================================
CLIMAX_T = HOLD_END_T + _fr(20)  # 0.67s -- transition lente vers la tension, pas un snap (on VEUT que ça se lise comme un effort qui monte)

CLIMAX_TORSO = (26, 0, 0)
CLIMAX_HEAD = (18, 0, 0)
CLIMAX_LEGS = {"Right Leg": (16, 0, 10), "Left Leg": (16, 0, -10)}
CLIMAX_ARMS = {"Right Arm": (32, 0, -48), "Left Arm": (32, 0, 48)}
CLIMAX_ROOT_Y = grounded_root_y_balanced(CLIMAX_TORSO, CLIMAX_LEGS["Left Leg"], CLIMAX_LEGS["Right Leg"]) + CLIMAX_CLEARANCE


def phase_climax():
    return [_kf(CLIMAX_T, root_pos=(CHAR_X, CLIMAX_ROOT_Y, CHAR_Z0), Torso=CLIMAX_TORSO, Head=CLIMAX_HEAD,
                **CLIMAX_LEGS, **CLIMAX_ARMS)]


# =======================================================================
# Phase RELEASE -- le trou noir s'effondre (R6), dernier a-coup
# gravitationnel avant relachement, puis DESCENTE (decision de
# conception assumee -- la reference coupe avant de montrer une fin,
# voir docstring de module) : le personnage revient au sol, absorbe
# l'atterrissage (jambes flechies), puis retour a une attente vivante
# identique a phase0_idle (boucle lisible).
# =======================================================================
RELEASE_T = CLIMAX_T + _fr(6)  # 0.2s -- l'a-coup final est rapide, presque un snap

RELEASE_TORSO = (50, 0, 0)
RELEASE_HEAD = (30, 0, 0)
RELEASE_LEGS = {"Right Leg": (20, 0, 7), "Left Leg": (20, 0, -7)}
RELEASE_ARMS = {"Right Arm": (44, 0, -20), "Left Arm": (44, 0, 20)}
RELEASE_ROOT_Y = grounded_root_y_balanced(RELEASE_TORSO, RELEASE_LEGS["Left Leg"], RELEASE_LEGS["Right Leg"]) + RELEASE_CLEARANCE

LAND_T = RELEASE_T + _fr(14)  # 0.47s de descente jusqu'au contact

LAND_TORSO = (24, 0, 0)
LAND_HEAD = (12, 0, 0)
LAND_LEGS = {"Right Leg": (18, 0, 8), "Left Leg": (18, 0, -8)}  # jambes flechies, absorbent l'impact
LAND_ARMS = {"Right Arm": (18, 0, -16), "Left Arm": (18, 0, 16)}
LAND_ROOT_Y = grounded_root_y_balanced(LAND_TORSO, LAND_LEGS["Left Leg"], LAND_LEGS["Right Leg"])

RECOVER_T = LAND_T + _fr(10)  # 0.33s -- se redresse

# -- pose de cloture DISTINCTE de la garde initiale (etait quasi
# identique -- retour explicite : "manque de frame ... d'une fin", pas
# de plan de cloture qui se lise comme un vrai point final). Legerement
# essouffle (torse encore penche, tete encore basse) ET asymetrique (bras
# droit encore leve/tendu, echo de la main qui portait le trou noir ;
# gauche deja retombe) -- communique "quelque chose vient de se passer",
# pas un simple retour a zero comme si de rien n'etait.
RECOVER_TORSO = (10, 0, 0)
RECOVER_HEAD = (6, 0, 0)
RECOVER_LEGS = {"Right Leg": (4, 0, 6), "Left Leg": (4, 0, -5)}
RECOVER_ARMS = {"Right Arm": (16, 0, -14), "Left Arm": (5, 0, 5)}
RECOVER_ROOT_Y = grounded_root_y_balanced(RECOVER_TORSO, RECOVER_LEGS["Left Leg"], RECOVER_LEGS["Right Leg"])


def phase_release_land():
    return [
        _kf(RELEASE_T, root_pos=(CHAR_X, RELEASE_ROOT_Y, CHAR_Z0), Torso=RELEASE_TORSO, Head=RELEASE_HEAD,
            **RELEASE_LEGS, **RELEASE_ARMS),
        _kf(LAND_T, root_pos=(CHAR_X, LAND_ROOT_Y, CHAR_Z0), Torso=LAND_TORSO, Head=LAND_HEAD,
            **LAND_LEGS, **LAND_ARMS),
        _kf(RECOVER_T, root_pos=(CHAR_X, RECOVER_ROOT_Y, CHAR_Z0), Torso=RECOVER_TORSO, Head=RECOVER_HEAD,
            **RECOVER_LEGS, **RECOVER_ARMS),
    ]


IDLE_OUT_END = RECOVER_T + _fr(30)  # 1s d'attente vivante finale, jamais un hold plat


def phase_idle_out():
    return _idle_stance_span(RECOVER_T, IDLE_OUT_END, (CHAR_X, 0, CHAR_Z0), REST,
                              RECOVER_TORSO, RECOVER_HEAD, RECOVER_LEGS, RECOVER_ARMS,
                              period=0.6, phase0=0.0, amp_leg=2.5, amp_torso=1.5)[1:]  # [1:] : evite un keyframe double a RECOVER_T


def character_track():
    keyframes = (phase0_idle() + phase_crouch() + phase_rise() + phase_hold()
                 + phase_climax() + phase_release_land() + phase_idle_out())
    phases = [
        {"name": "garde", "t0": 0.0, "t1": CROUCH_T, "expected_reversals": {}},
        {"name": "accroupissement", "t0": CROUCH_T, "t1": RISE_T, "expected_reversals": {}},
        {"name": "levitation", "t0": RISE_T, "t1": CLIMAX_T, "expected_reversals": {}},
        {"name": "climax_effondrement", "t0": CLIMAX_T, "t1": LAND_T, "expected_reversals": {}},
        {"name": "atterrissage_attente", "t0": LAND_T, "t1": IDLE_OUT_END, "expected_reversals": {}},
    ]
    preview_times = [0.0, CROUCH_T, CROUCH_HOLD_T, RISE_T, HOLD_END_T, CLIMAX_T, RELEASE_T, LAND_T, RECOVER_T,
                      IDLE_OUT_END]
    engine_opts = {"handle_type": "AUTO_CLAMPED"}
    return keyframes, phases, preview_times, engine_opts


TOTAL_DURATION = IDLE_OUT_END

# =======================================================================
# Fenetres AERIENNES -- design intent pour calibrate.py : entre RISE_T et
# LAND_T le personnage est EXPLICITEMENT cense ne plus toucher le sol
# (pas une anomalie a rattraper par une tolerance plus large -- voir
# calibrate.py, nouveau mode de verification "aerien").
# =======================================================================
AIRBORNE_WINDOW = {"t0": RISE_T, "t1": LAND_T}

# =======================================================================
# Timeline VFX -- ce que le disque d'accretion/coeur noir/debris doivent
# faire, synchronise sur la chorégraphie (voir black_hole_track.py qui
# consomme ces constantes -- rien n'est improvise cote VFX/viewer).
# =======================================================================
VFX_EVENTS = {
    "debris_launch": {"t0": RISE_T, "t1": RISE_T + 0.8},       # les fragments s'arrachent du sol
    "debris_gather": {"t0": RISE_T + 0.8, "t1": HOLD_END_T},   # ils convergent vers le centre
    "disk_form": {"t0": HOLD_END_T - 0.6, "t1": HOLD_END_T + 0.5},  # le disque/coeur apparaissent (chevauche legerement la fin du gather -- pas un pop instantane)
    "climax": {"t0": CLIMAX_T - 0.3, "t1": CLIMAX_T + 0.3},
    "collapse": {"t0": RELEASE_T, "t1": LAND_T},      # fondu au noir / consommation finale -- borne a LAND_T (pas RELEASE_T+constante) : le VFX doit finir PILE a l'atterrissage, jamais deborder dessus (verifie par calibrate.py)
}

# Point central du trou noir (monde) : au-dessus et legerement devant le
# personnage en vol -- mesure depuis LEVITATE_ROOT_Y (pas une valeur
# ecrite a la vue), pour que le disque reste coherent si LEVITATE_HEIGHT
# change un jour.
BLACK_HOLE_CENTER = np.array([CHAR_X, LEVITATE_ROOT_Y + 4.0, CHAR_Z0 + 1.6])

# -- secondary motion (spring chase, solveur analytique exact -- voir
# r6_solar_smite/anim_engine._spring_chase) : demarre a CROUCH_HOLD_T
# (pas RISE_T) -- correction suite a un retour explicite ("le perso dans
# la fluidite ces mouvement etc") : demarrer le ressort PILE a RISE_T
# faisait que le relevement crouch->rise lui-meme (le mouvement le plus
# spectaculaire de toute la sequence) restait une simple interpolation
# Bezier target-a-target, sans depassement/rebond -- un "snap" propre
# mais sans poids. En demarrant le ressort des le hold du crouch (cible
# encore immobile, vitesse nulle), le relevement devient lui-meme
# "chasse" par le ressort : la cible saute brusquement vers la pose de
# vol, le ressort accuse un vrai retard + depassement + stabilisation
# (l'"explosion" du decollage se voit dans le mouvement, pas seulement
# dans le timing des keyframes) -- puis continue sans interruption
# pendant toute la levitation/climax/effondrement (meme convention
# qu'avant : jamais desactive une fois demarre).
# -- damping_ratio abaisse (0.5/0.4 -> 0.32/0.3) suite au meme retour
# ("manque d'exageration") : moins de damping = plus de depassement et
# au moins un rebond visible avant stabilisation, au lieu d'un seul
# aller-retour a peine perceptible.
SECONDARY_MOTION = {
    "Torso": {"channels": (0, 1, 2), "stiffness": 180.0, "damping_ratio": 0.32, "t_min": CROUCH_HOLD_T},
    "Head": {"channels": (0, 1, 2), "stiffness": 220.0, "damping_ratio": 0.32, "t_min": CROUCH_HOLD_T},
    "Right Arm": {"channels": (0, 2), "stiffness": 150.0, "damping_ratio": 0.28, "t_min": CROUCH_HOLD_T},
    "Left Arm": {"channels": (0, 2), "stiffness": 150.0, "damping_ratio": 0.28, "t_min": CROUCH_HOLD_T},
}
