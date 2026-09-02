"""
Choregraphie : le personnage, debout dans une posture hautaine (buste et
tete penches en arriere -- fier, dedaigneux), leve la main pour invoquer
une enorme boule d'energie divine, la laisse grossir en la tenant (leger
balancement, "l'energie qui respire", pas un gel total comme la pause
d'attente d'un coup au sol), PUIS l'abat rapidement vers l'avant --
lancer brusque, pas une transition lente -- pour la jeter sur le monde
en contrebas, avant de reprendre sa posture hautaine, satisfait, a
regarder l'impact au loin.

Retour utilisateur explicite (apres rejet de la scene de chute divine,
"Nul, on tente un autre") : "le perso leve la main pour invoquer une
enorme boule divine et d'un ton hautain [la jette] la-bas sur le monde."
Nouvelle scene ISOLEE (nouveau dossier, meme infra de rig reutilisee
telle quelle -- voir README) -- pas une variation de r6_divine_descent.

Meme convention d'ecriture/semantique des axes que les prototypes
precedents (rotations en degres, `_kf` identique, verifiee -- pas
resupposee -- par calcul dans calibrate.py) :
  - Torso/Head/Right Leg/Left Leg : X positif = penche/tourne VERS
    L'AVANT. X negatif = vers l'arriere/le haut -- c'est CE signe qui
    porte "hautain" ici (buste et tete inclines en arriere, menton haut).
  - Right Arm/Left Arm : X positif = part vers l'AVANT (-Z) puis monte
    par-dessus jusqu'a X=180 (au-dessus de la tete). Z (bras droit)
    positif = ecarte VERS L'EXTERIEUR ; bras gauche, signe oppose.
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

# -- Posture hautaine de base -- buste/tete en arriere (X negatif),
# hanche stable, jambes en appui asymetrique decontracte (pas une garde
# de combat : un dieu qui toise le monde n'a pas besoin de se preparer
# a l'impact).
_HAUGHTY_TORSO = (-10, 0, 0)
_HAUGHTY_HEAD = (-10, 0, 0)
_HAUGHTY_LEGS = {"Right Leg": (0, 0, 4), "Left Leg": (0, 0, -2)}
_IDLE_ARMS = {"Right Arm": (2, 0, 10), "Left Arm": (2, 0, -15)}

# -- Bras leve pour invoquer -- X=0 est en fait le point de portee
# MAXIMALE de ce bras (verifie par balayage numerique, voir
# calibrate.py, pas suppose) : la main haute plafonne a ~1,1 stud SOUS
# le sommet de la tete quel que soit l'angle essaye (X de -90 a 180,
# inclinaison du torse de -15 a 0) -- longueur de bras fixe, limite
# REELLE du rig, meme categorie que les limites deja documentees dans
# r6_divine_descent (portee du poing, hauteur de hanche). La boule
# n'est donc PAS ancree exactement a la pointe du bras : le lecteur
# l'affiche avec un decalage vertical fixe au-dessus de cette main
# (voir README, "La boule ne sort pas exactement de la main") pour
# qu'elle se lise bien au-dessus de la tete malgre cette limite.
RAISE_RIGHT_ARM = (0, 0, -15)

# -- Anticipation avant le lancer : le bras se replie legerement en
# arriere/vers le haut -- principe d'anticipation classique (le
# mouvement inverse avant l'action donne plus de poids au lancer).
# Aucune contrainte de portee ici (pas de sol/tete a atteindre), reglee
# a l'oeil puis verifiee par capture d'ecran (voir README).
ANTICIP_TORSO = (-22, 0, 0)
ANTICIP_HEAD = (-15, 0, 0)
ANTICIP_RIGHT_ARM = (-15, 0, -25)

# -- Lancer : le bras s'abat vers l'avant-bas, le buste suit (transfert
# de poids reel, pas juste le bras qui bouge seul). La trajectoire de
# VOL de la boule apres relachement n'est PAS derivee de la vitesse du
# bras a ce keyframe (mesuree par calibrate.py : ~5,3 studs/s vers le
# bas, une valeur bien reelle mais qui ne dit rien sur ou se trouve
# "le monde" ni combien de temps le vol doit durer pour rester
# dramatique) : elle est scriptee independamment dans le lecteur, comme
# la trajectoire de la couronne dans r6_throne_crown -- un point de
# depart (la main a RELEASE_T) et un point d'arrivee choisis, pas une
# extrapolation physique.
THROW_TORSO = (20, 0, 0)
THROW_HEAD = (15, 0, 0)
THROW_RIGHT_ARM = (100, 0, -10)
THROW_LEGS = {"Right Leg": (10, 0, 6), "Left Leg": (0, 0, -2)}

FOLLOW_TORSO = (26, 0, 0)
FOLLOW_HEAD = (18, 0, 0)
FOLLOW_RIGHT_ARM = (130, 0, -15)


def haughty_orb_throw():
    keyframes = [
        _kf(0.00, root_pos=(0, GROUND_Y, 0), Torso=_HAUGHTY_TORSO, Head=_HAUGHTY_HEAD,
            **_HAUGHTY_LEGS, **_IDLE_ARMS),

        # -- leve la main : invocation --
        _kf(RAISE_T, root_pos=(0, GROUND_Y, 0), Torso=(-15, 0, 0), Head=(-12, 0, 0),
            **_HAUGHTY_LEGS, **{"Right Arm": RAISE_RIGHT_ARM, "Left Arm": _IDLE_ARMS["Left Arm"]}),

        # -- charge/tenue : la boule grossit dans le lecteur (voir
        # dump_scene_data.py -- taille lue depuis les instants de
        # phase), leger balancement du buste (Torso Y +-3) pour que
        # "l'energie qui respire" se lise dans le corps, pas seulement
        # dans le halo -- different de la pause figee du prototype
        # precedent (celle-la etait une tension avant un coup, celle-ci
        # est une accumulation de puissance, pas un arret).
        _kf(1.35, root_pos=(0, GROUND_Y, 0), Torso=(-15, 3, 0), Head=(-12, 0, 0),
            **_HAUGHTY_LEGS, **{"Right Arm": RAISE_RIGHT_ARM, "Left Arm": _IDLE_ARMS["Left Arm"]}),
        _kf(2.00, root_pos=(0, GROUND_Y, 0), Torso=(-15, -3, 0), Head=(-12, 0, 0),
            **_HAUGHTY_LEGS, **{"Right Arm": RAISE_RIGHT_ARM, "Left Arm": _IDLE_ARMS["Left Arm"]}),

        # -- anticipation : encore plus en arriere juste avant le lancer --
        _kf(ANTICIP_T, root_pos=(0, GROUND_Y, 0), Torso=ANTICIP_TORSO, Head=ANTICIP_HEAD,
            **_HAUGHTY_LEGS, **{"Right Arm": ANTICIP_RIGHT_ARM, "Left Arm": _IDLE_ARMS["Left Arm"]}),

        # -- LANCER : rapide (voir THROW_T - ANTICIP_T), la boule quitte
        # la main a cet instant precis (RELEASE_T, exporte separement --
        # voir dump_scene_data.py).
        _kf(THROW_T, root_pos=(0, GROUND_Y, 0), Torso=THROW_TORSO, Head=THROW_HEAD,
            **THROW_LEGS, **{"Right Arm": THROW_RIGHT_ARM, "Left Arm": _IDLE_ARMS["Left Arm"]}),

        # -- prolongement du geste (follow-through) --
        _kf(THROW_T + 0.15, root_pos=(0, GROUND_Y, 0), Torso=FOLLOW_TORSO, Head=FOLLOW_HEAD,
            **THROW_LEGS, **{"Right Arm": FOLLOW_RIGHT_ARM, "Left Arm": _IDLE_ARMS["Left Arm"]}),

        # -- recupere, revient vers la posture hautaine --
        _kf(THROW_T + 0.55, root_pos=(0, GROUND_Y, 0), Torso=(-5, 0, 0), Head=(-5, 0, 0),
            **_HAUGHTY_LEGS, **{"Right Arm": (10, 0, 5), "Left Arm": _IDLE_ARMS["Left Arm"]}),

        # -- pose finale hautaine, satisfait, regarde l'impact au loin --
        _kf(THROW_T + 1.15, root_pos=(0, GROUND_Y, 0), Torso=_HAUGHTY_TORSO, Head=_HAUGHTY_HEAD,
            **_HAUGHTY_LEGS, **_IDLE_ARMS),
    ]

    phases = [
        {"name": "invocation", "t0": 0.00, "t1": 0.70, "expected_reversals": {}},
        {"name": "charge", "t0": 0.70, "t1": ANTICIP_T, "expected_reversals": {}},
        {"name": "lancer", "t0": ANTICIP_T, "t1": THROW_T + 0.15, "expected_reversals": {}},
        {"name": "vol", "t0": THROW_T + 0.15, "t1": IMPACT_T, "expected_reversals": {}},
        {"name": "aftermath", "t0": IMPACT_T, "t1": THROW_T + 1.15, "expected_reversals": {}},
    ]
    preview_times = [0.0, 0.70, 1.35, 2.00, ANTICIP_T, THROW_T, THROW_T + 0.15,
                      THROW_T + 0.55, THROW_T + 1.15]
    engine_opts = {"handle_type": "AUTO_CLAMPED"}
    return keyframes, phases, preview_times, engine_opts


# ANTICIP_T -> THROW_T : 0,15s seulement -- le lancer doit etre brusque,
# pas une transition lente comme le reste de la choregraphie (meme
# principe que le coup de poing de r6_divine_descent). RELEASE_T = THROW_T :
# la boule quitte la main exactement au keyframe du lancer, pas avant/
# apres -- exporte separement pour que le lecteur sache exactement quand
# basculer du suivi "en main" au vol libre scripte. IMPACT_T : instant
# scripte (pas mesure sur le personnage, qui ne bouge plus a ce moment)
# ou la boule atteint le monde en contrebas -- voir orb_track.py.
RAISE_T = 0.70
ANTICIP_T = 2.15
THROW_T = ANTICIP_T + 0.15
RELEASE_T = THROW_T
IMPACT_T = THROW_T + 0.85
