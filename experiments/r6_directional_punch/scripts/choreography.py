"""
Choregraphie a DEUX personnages (deux rigs R6 independants, meme
chronologie -- pas un "combo" sur un seul acteur comme
r6_aerial_kick_combo) : un attaquant qui charge un direct puissant
("Directional Punch", meme idee que les jeux de combat Roblox -- voir
README/reference) sur un mannequin qui encaisse et recule sous le choc.

Demande utilisateur (reference : capture GIF d'un jeu Roblox montrant un
personnage qui charge et assene un coup direct sur un mannequin
d'entrainement, avec un changement de cadrage juste avant l'impact et un
flash impact-frame façon manga au contact) : "cree une animation avec
texturing decores etc ou le perso fais ca avec changement de cam etc
fais du niveau expert."

Meme convention d'ecriture/semantique des axes que les prototypes
precedents (rotations en degres, `_kf` identique, verifiee -- pas
resupposee -- par calcul dans calibrate.py) :
  - Torso/Head/Right Leg/Left Leg : X positif = penche/tourne VERS
    L'AVANT. X negatif = vers l'arriere/le haut.
  - Right Arm/Left Arm : X positif = part vers l'AVANT (-Z) puis monte
    par-dessus jusqu'a X=180 (au-dessus de la tete). X=90 = horizontale,
    droit devant -- VERIFIE (pas suppose) : bras droit a X=90, torse
    neutre, racine Y=0 => poing en Z=-1.5 (donc "devant" = -Z, meme
    convention que r6_divine_orb/r6_throne_crown).
  - Torso Y (torsion) : VERIFIE par calcul isole (pas suppose) -- Y
    POSITIF fait pivoter l'EPAULE DROITE VERS L'AVANT (-Z). C'est donc CE
    signe qui porte la rotation hanches/buste d'un direct du droit :
    Y negatif = buste arme en arriere (charge), Y positif = buste qui
    "tire" le poing en avant (relachement de la charge dans le coup).
  - HumanoidRootPart Y=180 : personnage retourne, "devant" devient +Z --
    utilise pour que le mannequin fasse face a l'attaquant (positionne
    plus loin en -Z).
  - Aucun coude/genou (contrainte du rig, voir r6_rig.py).
"""

REST = (0.0, 0.0, 0.0)


def _kf(time, root_pos=(0.0, 3.0, 0.0), HumanoidRootPart=REST, Torso=REST,
        Head=REST, **legs_arms):
    d = {
        "time": time,
        "root_pos": root_pos,
        "HumanoidRootPart": HumanoidRootPart,
        "Torso": Torso,
        "Head": Head,
    }
    d.update(legs_arms)
    return d


GROUND_Y = 3.0

# Retour utilisateur explicite ("c bcp trop rapide on ne lit pas assez
# les mouvement y'a pas de logique le perso est censé charge son poing")
# apres une premiere version ou toute la charge tenait en 0.15s : le
# COUP lui-meme reste brusque (principe d'animation "lent a l'approche,
# rapide dans l'action" -- pas remis en cause), mais la charge qui le
# precede doit se LIRE, avec une vraie duree et un signal visuel de
# "poing qui charge" (voir CHARGE_GLOW dans le lecteur), pas juste une
# pose tenue 0.15s.
GARDE_T = 0.35        # garde tenue, avant de commencer a charger
WINDUP_T = 0.75        # transition vers la pose de charge (bras arme)
CHARGE_A_T = 1.20      # charge, 1er battement de "respiration"
CHARGE_B_T = 1.65      # charge, 2e battement
COIL_T = 2.00          # dernier resserrement avant le lacher -- le poing
                       # est "au maximum", tendu, juste avant de partir
IMPACT_T = COIL_T + 0.20   # lacher brusque (0.20s -- toujours rapide)
DURATION = IMPACT_T + 0.85

# -- Positions de depart : l'attaquant est pres de la camera (Z peu
# negatif), le mannequin loin devant lui (Z tres negatif) -- l'attaquant
# regarde donc bien vers le mannequin (front = -Z, racine Y=0).
ATTACKER_Z0 = -1.0
DUMMY_Z = -7.0

_READY_TORSO = (-5, 0, 0)
_READY_HEAD = (-5, 0, 0)
_READY_LEGS = {"Right Leg": (0, 0, 5), "Left Leg": (4, 0, -4)}
_READY_ARMS = {"Right Arm": (22, 0, 16), "Left Arm": (22, 0, -16)}

# -- Amplitudes de charge/lacher reprises apres analyse d'un pack
# d'animation de combat premium fourni par l'utilisateur ("ça manque
# d'exagération") : mesure reelle (rotation vs repos, matrices Pose.CFrame
# decodees numeriquement -- voir experiments/_shared/rbxm_reader.py et
# le rapport correspondant) sur une sequence "M1_1" comparable -- bras
# ~178 deg, buste ~99 deg, tete ~88 deg, contre ~65/38/15 deg ici avant
# ce passage. La CHARGE (anticipation, en l'air, aucune contrainte de
# contact) est le levier le plus sur a exagerer fortement ; le LACHER
# (STRIKE_*, plus bas) reste lui volontairement INCHANGE -- calibre au
# stud pres par balayage numerique (0,62 stud d'ecart, voir
# calibrate.py), un gain d'exageration qui casserait ce contact ne
# vaudrait pas le coup.
WINDUP_TORSO = (-14, -38, 2)
WINDUP_HEAD = (-11, -15, 0)
WINDUP_RIGHT_ARM = (-8, 0, -22)
WINDUP_LEGS = {"Right Leg": (-9, 0, 6), "Left Leg": (18, 0, -5)}

# -- Battements de "respiration" pendant la charge -- la pose ne reste
# PAS parfaitement figee entre WINDUP_T et COIL_T (un gel total lirait
# comme une pause plutot qu'un effort soutenu) : leger va-et-vient du
# buste/bras, resserrement progressif jusqu'au coil final juste avant le
# lacher. Meme principe que le balancement "l'energie qui respire" de
# r6_divine_orb, applique ici au poing plutot qu'a une boule.
CHARGE_A_TORSO = (-16, -42, 3)
CHARGE_A_RIGHT_ARM = (-10, 0, -30)
CHARGE_B_TORSO = (-13, -34, 1)
CHARGE_B_RIGHT_ARM = (-6, 0, -18)
COIL_TORSO = (-20, -56, 4)
COIL_HEAD = (-17, -22, 0)
COIL_RIGHT_ARM = (-22, 0, -52)

# Calibre par balayage numerique (pas a l'oeil, voir calibrate.py) :
# X=100 semblait "plus de puissance" mais releve le poing bien au-dessus
# du torse vise (X=90..180 monte vers l'aisselle/au-dessus de la tete,
# meme convention que r6_divine_orb) -- X=65, buste penche 16 (au lieu de
# 22) et une avancee (LUNGE_Z) plus profonde rapprochent le poing du
# torse du mannequin a 0,49 stud (ecart mesure, pas suppose).
STRIKE_TORSO = (16, 34, 0)
STRIKE_HEAD = (10, 12, 0)
STRIKE_RIGHT_ARM = (65, 0, -4)
STRIKE_LEGS = {"Right Leg": (-14, 0, 5), "Left Leg": (26, 0, -4)}
LUNGE_Z = -5.40   # racine avancee (pas dans le coup) au moment de l'impact -- calibre par calcul (voir calibrate.py) pour amener le poing pres du torse du mannequin

# -- Follow-through : le coup ne s'arrete pas net a IMPACT_T -- le poids
# du corps continue legerement au-dela du point de contact calibre avant
# de repartir en arriere (principe d'animation "overshoot"/"follow
# through"). Garde IMPACT_T (le seul instant mesure par calibrate.py)
# strictement inchange ; cette pose n'existe que 0,06s APRES, donc ne
# touche pas le contact calibre lui-meme.
OVERSHOOT_TORSO = (20, 40, 0)
OVERSHOOT_HEAD = (13, 16, 0)
OVERSHOOT_RIGHT_ARM = (72, 0, 2)

RECOVER_TORSO = (-14, 4, 0)
RECOVER_HEAD = (-9, 2, 0)
RECOVER_RIGHT_ARM = (22, 0, 14)

FINAL_TORSO = (-12, 0, 0)
FINAL_HEAD = (-8, 0, 0)


def attacker_punch():
    keyframes = [
        _kf(0.00, root_pos=(0, GROUND_Y, ATTACKER_Z0), Torso=_READY_TORSO, Head=_READY_HEAD,
            **_READY_LEGS, **_READY_ARMS),
        # -- garde tenue (deux keyframes identiques -> vrai plat, pas un
        # gel numerique accidentel, meme technique que r6_divine_orb).
        _kf(GARDE_T, root_pos=(0, GROUND_Y, ATTACKER_Z0), Torso=_READY_TORSO, Head=_READY_HEAD,
            **_READY_LEGS, **_READY_ARMS),
        _kf(WINDUP_T, root_pos=(0, GROUND_Y, ATTACKER_Z0), Torso=WINDUP_TORSO, Head=WINDUP_HEAD,
            **WINDUP_LEGS, **{"Right Arm": WINDUP_RIGHT_ARM, "Left Arm": _READY_ARMS["Left Arm"]}),
        _kf(CHARGE_A_T, root_pos=(0, GROUND_Y, ATTACKER_Z0), Torso=CHARGE_A_TORSO, Head=WINDUP_HEAD,
            **WINDUP_LEGS, **{"Right Arm": CHARGE_A_RIGHT_ARM, "Left Arm": _READY_ARMS["Left Arm"]}),
        _kf(CHARGE_B_T, root_pos=(0, GROUND_Y, ATTACKER_Z0), Torso=CHARGE_B_TORSO, Head=WINDUP_HEAD,
            **WINDUP_LEGS, **{"Right Arm": CHARGE_B_RIGHT_ARM, "Left Arm": _READY_ARMS["Left Arm"]}),
        _kf(COIL_T, root_pos=(0, GROUND_Y, ATTACKER_Z0), Torso=COIL_TORSO, Head=COIL_HEAD,
            **WINDUP_LEGS, **{"Right Arm": COIL_RIGHT_ARM, "Left Arm": _READY_ARMS["Left Arm"]}),
        _kf(IMPACT_T, root_pos=(0, GROUND_Y, LUNGE_Z), Torso=STRIKE_TORSO, Head=STRIKE_HEAD,
            **STRIKE_LEGS, **{"Right Arm": STRIKE_RIGHT_ARM, "Left Arm": (10, 0, -20)}),
        # -- follow-through : le poing/buste continuent legerement au-dela
        # du point de contact calibre (voir OVERSHOOT_* plus haut) avant
        # de repartir en arriere -- IMPACT_T lui-meme reste inchange.
        _kf(IMPACT_T + 0.06, root_pos=(0, GROUND_Y, LUNGE_Z - 0.15), Torso=OVERSHOOT_TORSO, Head=OVERSHOOT_HEAD,
            **STRIKE_LEGS, **{"Right Arm": OVERSHOOT_RIGHT_ARM, "Left Arm": (10, 0, -20)}),
        _kf(IMPACT_T + 0.40, root_pos=(0, GROUND_Y, LUNGE_Z), Torso=RECOVER_TORSO, Head=RECOVER_HEAD,
            **STRIKE_LEGS, **{"Right Arm": RECOVER_RIGHT_ARM, "Left Arm": _READY_ARMS["Left Arm"]}),
        _kf(IMPACT_T + 0.85, root_pos=(0, GROUND_Y, LUNGE_Z + 0.4), Torso=FINAL_TORSO, Head=FINAL_HEAD,
            **_READY_LEGS, **_READY_ARMS),
    ]
    phases = [
        {"name": "garde", "t0": 0.00, "t1": WINDUP_T, "expected_reversals": {}},
        {"name": "charge", "t0": WINDUP_T, "t1": COIL_T, "expected_reversals": {}},
        {"name": "lacher", "t0": COIL_T, "t1": IMPACT_T, "expected_reversals": {}},
        {"name": "impact", "t0": IMPACT_T, "t1": IMPACT_T + 0.12, "expected_reversals": {}},
        {"name": "suite", "t0": IMPACT_T + 0.12, "t1": IMPACT_T + 0.40, "expected_reversals": {}},
        {"name": "posture_finale", "t0": IMPACT_T + 0.40, "t1": DURATION, "expected_reversals": {}},
    ]
    preview_times = [0.0, GARDE_T, WINDUP_T, CHARGE_A_T, CHARGE_B_T, COIL_T, IMPACT_T,
                      IMPACT_T + 0.40, IMPACT_T + 0.85]
    engine_opts = {"handle_type": "AUTO_CLAMPED"}
    return keyframes, phases, preview_times, engine_opts


# -- Mannequin : encaisse et recule. Racine Y=180 (face a l'attaquant,
# "devant" = +Z pour lui). Reaction synchronisee EXACTEMENT sur
# IMPACT_T -- pas avant (ce serait "prevoir le coup"), pas apres (ca
# lirait comme desynchronise).
DUMMY_IDLE_TORSO = (0, 0, 0)
DUMMY_IDLE_HEAD = (0, 0, 0)
DUMMY_IDLE_ARMS = {"Right Arm": (4, 0, 10), "Left Arm": (4, 0, -10)}
DUMMY_IDLE_LEGS = {"Right Leg": (0, 0, 3), "Left Leg": (0, 0, -3)}

HIT_TORSO = (-32, 0, 8)
HIT_HEAD = (-38, -10, 0)
HIT_ARMS = {"Right Arm": (150, 0, 55), "Left Arm": (150, 0, -70)}
HIT_LEGS = {"Right Leg": (-18, 0, 10), "Left Leg": (10, 0, -14)}

DAZED_TORSO = (18, 0, -4)
DAZED_HEAD = (10, 6, 0)
DAZED_ARMS = {"Right Arm": (30, 0, 20), "Left Arm": (30, 0, -25)}
DAZED_LEGS = {"Right Leg": (6, 0, 8), "Left Leg": (2, 0, -10)}


def dummy_reaction():
    keyframes = [
        _kf(0.00, root_pos=(0, GROUND_Y, DUMMY_Z), HumanoidRootPart=(0, 180, 0),
            Torso=DUMMY_IDLE_TORSO, Head=DUMMY_IDLE_HEAD, **DUMMY_IDLE_LEGS, **DUMMY_IDLE_ARMS),
        _kf(IMPACT_T - 0.03, root_pos=(0, GROUND_Y, DUMMY_Z), HumanoidRootPart=(0, 180, 0),
            Torso=DUMMY_IDLE_TORSO, Head=DUMMY_IDLE_HEAD, **DUMMY_IDLE_LEGS, **DUMMY_IDLE_ARMS),
        # -- l'instant du choc : whiplash brutal, quasi instantane (0.03s)
        # -- une reaction lente lirait comme "il a vu venir le coup".
        _kf(IMPACT_T, root_pos=(0, GROUND_Y, DUMMY_Z), HumanoidRootPart=(0, 180, 0),
            Torso=HIT_TORSO, Head=HIT_HEAD, **HIT_LEGS, **HIT_ARMS),
        # -- recul (knockback) : la racine part plus loin de l'attaquant
        # (Z encore plus negatif -- l'attaquant est du cote +Z pour lui).
        _kf(IMPACT_T + 0.35, root_pos=(0, GROUND_Y, DUMMY_Z - 1.6), HumanoidRootPart=(0, 178, 0),
            Torso=HIT_TORSO, Head=HIT_HEAD, **HIT_LEGS, **HIT_ARMS),
        _kf(IMPACT_T + 0.75, root_pos=(0, GROUND_Y, DUMMY_Z - 1.9), HumanoidRootPart=(0, 180, 0),
            Torso=DAZED_TORSO, Head=DAZED_HEAD, **DAZED_LEGS, **DAZED_ARMS),
        # -- tenue de la pose hebetee jusqu'a la fin de la scene, alignee
        # EXACTEMENT sur la duree totale de l'attaquant (voir DURATION) :
        # les deux rigs doivent couvrir la meme fenetre de temps pour
        # rester synchronises dans le lecteur.
        _kf(DURATION, root_pos=(0, GROUND_Y, DUMMY_Z - 1.9), HumanoidRootPart=(0, 180, 0),
            Torso=DAZED_TORSO, Head=DAZED_HEAD, **DAZED_LEGS, **DAZED_ARMS),
    ]
    phases = [
        {"name": "attente", "t0": 0.00, "t1": IMPACT_T, "expected_reversals": {}},
        {"name": "choc", "t0": IMPACT_T, "t1": IMPACT_T + 0.35, "expected_reversals": {}},
        {"name": "recul", "t0": IMPACT_T + 0.35, "t1": DURATION, "expected_reversals": {}},
    ]
    preview_times = [0.0, IMPACT_T - 0.03, IMPACT_T, IMPACT_T + 0.35, IMPACT_T + 0.75, DURATION]
    engine_opts = {"handle_type": "AUTO_CLAMPED"}
    return keyframes, phases, preview_times, engine_opts


# -- "Secondary motion" (recree localement, voir r6_throne_crown pour
# l'origine de la technique -- Cascadeur non disponible dans ce sandbox)
# : le buste de l'attaquant chasse sa cible avec un leger depassement
# juste apres l'impact -- le coup "vibre" avant de se stabiliser, plutot
# que de s'arreter net. t_min = IMPACT_T : aucun effet pendant la charge
# elle-meme (deja un mouvement rapide et delibere, pas besoin d'y
# ajouter du flou).
# damping_ratio abaisse (0.55->0.40, 0.6->0.45) apres le passage
# "exageration" : le follow-through explicite (OVERSHOOT_*) donne deja un
# grand mouvement delibere, le spring-chase qui suit doit maintenant se
# lire comme un vrai rebond/vibration APRES ce mouvement plutot qu'un
# simple amortissement plat -- plus underdamped, une ou deux oscillations
# visibles avant stabilisation.
ATTACKER_SECONDARY_MOTION = {
    "Torso": {"channels": (0, 1, 2), "stiffness": 260.0,
              "damping_ratio": 0.40, "t_min": IMPACT_T},
    "Right Arm": {"channels": (0, 2), "stiffness": 320.0,
                  "damping_ratio": 0.45, "t_min": IMPACT_T},
}
DUMMY_SECONDARY_MOTION = {
    "Torso": {"channels": (0, 1, 2), "stiffness": 90.0,
              "damping_ratio": 0.45, "t_min": IMPACT_T},
    "Head": {"channels": (0, 1, 2), "stiffness": 140.0,
             "damping_ratio": 0.5, "t_min": IMPACT_T},
}
