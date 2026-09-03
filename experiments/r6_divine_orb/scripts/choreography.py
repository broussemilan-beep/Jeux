"""
Choregraphie : le personnage leve LES DEUX MAINS des le tout debut de
l'animation pour invoquer une boule d'energie colossale -- LE SOLEIL --
a la maniere d'un genkidama (energie rassemblee a deux mains au-dessus
de la tete), la laisse grossir en la tenant (leger balancement,
"l'energie qui respire", pas un gel total), PUIS l'abat rapidement vers
l'avant a deux mains -- lancer brusque, pas une transition lente -- pour
la jeter sur le monde en contrebas, avant de reprendre sa posture
hautaine, satisfait, a regarder l'impact au loin.

Retour utilisateur explicite (correction de la premiere version de cette
scene, elle-meme nee du rejet de la chute divine "Nul, on tente un
autre") : "Non le personnage leve la main droit au debut de l'animation
et abas le soleil comme un genkidama sur le monde." Trois changements
par rapport a la premiere version :
  1. Le lever de main(s) commence AU DEBUT de l'animation (RAISE_T tres
     court), plus apres 0,70 s d'attente hautaine immobile.
  2. Geste a DEUX mains (genkidama), pas une seule -- Left Arm calibree
     par balayage numerique en miroir de Right Arm, jamais supposee
     (voir calibrate.py) -- et la boule devient "le soleil" (couleur,
     voir run_scene.py/viewer), pas une boule violette generique.
  3. BUG DE MESURE TROUVE ET CORRIGE en re-calibrant pour ce changement :
     la premiere version croyait a une "limite reelle du rig" (main ne
     depassant jamais ~1 stud sous la tete, quel que soit l'angle) --
     faux. `calibrate.py`/`orb_track.py` lisaient le bout "top" du bras
     (`tip_world(..., "bottom")` vs `"top")`), qui est le point PRES DE
     L'EPAULE (quasi immobile quel que soit l'angle du bras), pas la
     main. Verifie numeriquement (voir le sweep isole dans le worklog de
     session) : avec le bon bout ("bottom"), X=180 (bras droit au-dessus
     de la tete, exactement la valeur documentee ci-dessous) met la main
     LEGEREMENT AU-DESSUS du sommet de la tete, pas 1 stud en dessous.
     Les angles ci-dessous (RAISE/ANTICIP/THROW/FOLLOW) sont donc
     redefinis en consequence -- X=0 ne veut plus dire "main levee" (X=0
     = bras qui pend, c'etait le vrai sens depuis le debut, la premiere
     version se trompait de bout de bras).

Meme convention d'ecriture/semantique des axes que les prototypes
precedents (rotations en degres, `_kf` identique, verifiee -- pas
resupposee -- par calcul dans calibrate.py) :
  - Torso/Head/Right Leg/Left Leg : X positif = penche/tourne VERS
    L'AVANT. X negatif = vers l'arriere/le haut -- c'est CE signe qui
    porte "hautain" ici (buste et tete inclines en arriere, menton haut).
  - Right Arm/Left Arm : X positif = part vers l'AVANT (-Z) puis monte
    par-dessus jusqu'a X=180 (au-dessus de la tete). Z (bras droit)
    positif = ecarte VERS L'EXTERIEUR ; bras gauche, signe oppose (donc
    un geste symetrique a deux mains a le MEME X et un Z de signe
    OPPOSE sur les deux bras).
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


GROUND_Y = 3.0  # hanche debout, cf. les prototypes precedents

_HAUGHTY_TORSO = (-10, 0, 0)
_HAUGHTY_HEAD = (-10, 0, 0)
_HAUGHTY_LEGS = {"Right Leg": (0, 0, 4), "Left Leg": (0, 0, -2)}
_IDLE_ARMS = {"Right Arm": (2, 0, 10), "Left Arm": (2, 0, -15)}

# Geste a deux mains -- Right Arm calibree (voir README/calibrate.py :
# balayage fin 160..190 x -40..0 avec le bout "bottom" -- le vrai bout
# main -- torse -15, tete -12 : X=180 Z=-20 met la main ~0,15 stud
# AU-DESSUS du sommet de la tete). Left Arm en miroir EXACT (meme X, Z de
# signe oppose) puis VERIFIEE (pas supposee) par calibrate.py -- symetrie
# du rig confirmee numeriquement (ecart D/G nul a ce keyframe).
RAISE_RIGHT_ARM = (180, 0, -20)
RAISE_LEFT_ARM = (180, 0, 20)

ANTICIP_TORSO = (-22, 0, 0)
ANTICIP_HEAD = (-15, 0, 0)
# Anticipation : les mains se resserrent legerement (Z reduit en
# magnitude) juste avant le lancer -- "l'energie qui se comprime" avant
# de s'abattre -- plutot qu'un vrai changement d'angle X (deja au max
# utile a 180).
ANTICIP_RIGHT_ARM = (185, 0, -10)
ANTICIP_LEFT_ARM = (185, 0, 10)

THROW_TORSO = (20, 0, 0)
THROW_HEAD = (15, 0, 0)
# Lancer : les deux bras balaient vers le bas-avant depuis le dessus de
# la tete (180) jusqu'a un peu au-dela de l'horizontale (40) -- un vrai
# "abattre", pas un geste qui reste haut comme dans la premiere version
# (consequence du bug de mesure corrige ci-dessus : sans lui, X=100
# semblait deja "vers le bas" alors qu'il ne l'etait pas tant que ca).
THROW_RIGHT_ARM = (40, 0, -8)
THROW_LEFT_ARM = (40, 0, 8)
THROW_LEGS = {"Right Leg": (10, 0, 6), "Left Leg": (0, 0, -2)}

FOLLOW_TORSO = (26, 0, 0)
FOLLOW_HEAD = (18, 0, 0)
# Suite du geste : les bras continuent leur descente (10, presque le long
# du corps) -- le soleil est deja parti, les mains achevent le mouvement.
FOLLOW_RIGHT_ARM = (10, 0, -5)
FOLLOW_LEFT_ARM = (10, 0, 5)


def haughty_orb_throw():
    keyframes = [
        # t=0 : le lever des DEUX mains commence des la premiere frame --
        # pas de pose hautaine immobile avant (retour utilisateur : "au
        # debut de l'animation"). Le buste/tete hautains restent presents
        # des le depart : le personnage ne se met pas en garde, il invoque.
        _kf(0.00, root_pos=(0, GROUND_Y, 0), Torso=(-8, 0, 0), Head=(-8, 0, 0),
            **_HAUGHTY_LEGS, **_IDLE_ARMS),
        _kf(RAISE_T, root_pos=(0, GROUND_Y, 0), Torso=(-15, 0, 0), Head=(-12, 0, 0),
            **_HAUGHTY_LEGS, **{"Right Arm": RAISE_RIGHT_ARM, "Left Arm": RAISE_LEFT_ARM}),
        _kf(0.95, root_pos=(0, GROUND_Y, 0), Torso=(-15, 3, 0), Head=(-12, 0, 0),
            **_HAUGHTY_LEGS, **{"Right Arm": RAISE_RIGHT_ARM, "Left Arm": RAISE_LEFT_ARM}),
        _kf(1.60, root_pos=(0, GROUND_Y, 0), Torso=(-15, -3, 0), Head=(-12, 0, 0),
            **_HAUGHTY_LEGS, **{"Right Arm": RAISE_RIGHT_ARM, "Left Arm": RAISE_LEFT_ARM}),
        _kf(ANTICIP_T, root_pos=(0, GROUND_Y, 0), Torso=ANTICIP_TORSO, Head=ANTICIP_HEAD,
            **_HAUGHTY_LEGS, **{"Right Arm": ANTICIP_RIGHT_ARM, "Left Arm": ANTICIP_LEFT_ARM}),
        _kf(THROW_T, root_pos=(0, GROUND_Y, 0), Torso=THROW_TORSO, Head=THROW_HEAD,
            **THROW_LEGS, **{"Right Arm": THROW_RIGHT_ARM, "Left Arm": THROW_LEFT_ARM}),
        _kf(THROW_T + 0.15, root_pos=(0, GROUND_Y, 0), Torso=FOLLOW_TORSO, Head=FOLLOW_HEAD,
            **THROW_LEGS, **{"Right Arm": FOLLOW_RIGHT_ARM, "Left Arm": FOLLOW_LEFT_ARM}),
        _kf(THROW_T + 0.55, root_pos=(0, GROUND_Y, 0), Torso=(-5, 0, 0), Head=(-5, 0, 0),
            **_HAUGHTY_LEGS, **{"Right Arm": (10, 0, 5), "Left Arm": (10, 0, -5)}),
        _kf(THROW_T + 1.15, root_pos=(0, GROUND_Y, 0), Torso=_HAUGHTY_TORSO, Head=_HAUGHTY_HEAD,
            **_HAUGHTY_LEGS, **_IDLE_ARMS),
    ]

    phases = [
        {"name": "invocation", "t0": 0.00, "t1": 0.35, "expected_reversals": {}},
        {"name": "charge", "t0": 0.35, "t1": ANTICIP_T, "expected_reversals": {}},
        {"name": "lancer", "t0": ANTICIP_T, "t1": THROW_T + 0.15, "expected_reversals": {}},
        {"name": "vol", "t0": THROW_T + 0.15, "t1": IMPACT_T, "expected_reversals": {}},
        {"name": "aftermath", "t0": IMPACT_T, "t1": THROW_T + 1.15, "expected_reversals": {}},
    ]
    preview_times = [0.0, RAISE_T, 0.95, 1.60, ANTICIP_T, THROW_T, THROW_T + 0.15,
                      THROW_T + 0.55, THROW_T + 1.15]
    engine_opts = {"handle_type": "AUTO_CLAMPED"}
    return keyframes, phases, preview_times, engine_opts


# Lever immediat -- 0,30 s, contre 0,70 s d'attente hautaine puis lever
# dans la premiere version : c'est ce raccourci qui traduit "des le debut
# de l'animation" sans pour autant faire un pop instantane (une vraie
# interpolation reste visible et lisible sur 0,30 s).
RAISE_T = 0.30
ANTICIP_T = 1.75
THROW_T = ANTICIP_T + 0.15
RELEASE_T = THROW_T
IMPACT_T = THROW_T + 0.85
