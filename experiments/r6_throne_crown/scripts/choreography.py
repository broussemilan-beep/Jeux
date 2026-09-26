"""
Choregraphie du personnage : s'assoit sur le trone, se couronne, tient la
pose finale. Meme convention d'ecriture que r6_aerial_kick_combo
(rotations en degres, reperes/`_kf` identiques -- voir docstring de
`export_kfseq.to_joint_frame` pour la conversion vers le repere du joint,
inchangee, reutilisee telle quelle).

Les angles de jambe/torse/bras ci-dessous sont VERIFIES par calcul de
position monde (voir `scripts/calibrate.py` et le README, section
"Calibration") contre la geometrie du trone dans `props.py` -- pas
poses a l'oeil. HumanoidRootPart reste a Y=3 pendant toute l'assise :
c'est le meme mecanisme que l'assise R6 par defaut de Roblox (le bassin
ne descend pas, seules les jambes tournent a la hanche -- pas de genou
dans ce rig, donc les jambes restent droites, ce qui EST le look attendu
plutot qu'une simplification a cacher, voir README).

Semantique des axes de rotation du BRAS (Right Arm/Left Arm), etablie par
diagnostic empirique (voir README "Calibration") -- PAS supposee par
analogie avec les jambes des cycles precedents, verifiee fausse a la
premiere passe :
  - X positif : le bras part vers l'AVANT (-Z) puis monte par dessus,
    jusqu'a X=180 = au-dessus de la tete.
  - Z (bras droit) positif : leve le bras VERS L'EXTERIEUR (+X) et vers
    le haut (position accoudoir : Z=~55). Negatif : ramene le bras VERS
    L'INTERIEUR (croise le corps). Bras gauche : signe oppose (symetrie
    miroir verifiee au calibrage).
Consequence mesuree : la portee verticale max du poignet a l'epaule est
~Y=5.0 (bras droit, sans coude, longueur fixe) -- la couronne ne peut pas
etre "levee tres haut au-dessus de la tete", seulement juste au-dessus,
qui est deja la ou elle doit atterrir.
"""

import props

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


def sit_and_crown():
    keyframes = [
        # -- approche : debout devant le trone, garde neutre. Z NEGATIF
        # (le trone/siege occupe Z de -0.9 a +2.7, "devant" = plus loin
        # en Z negatif) -- premiere version avait le signe invers, le
        # personnage debout se retrouvait cache DERRIERE/DANS le siege et
        # le dossier des le depart (trouve par capture d'ecran reelle du
        # lecteur, pas suppose -- voir README "Calibration") --
        _kf(0.00, root_pos=(0, 3.0, -1.6),
            **{"Right Arm": (5, 0, -8), "Left Arm": (5, 0, 8),
               "Right Leg": (0, 0, 0), "Left Leg": (0, 0, 0)}),

        # -- debut de l'assise : le bassin recule vers le siege, les
        # cuisses commencent a monter --
        _kf(0.35, root_pos=(0, 2.95, -1.0), Torso=(-8, 0, 0), Head=(2, 0, 0),
            **{"Right Arm": (-10, 0, -10), "Left Arm": (-10, 0, 10),
               "Right Leg": (45, 0, 6), "Left Leg": (45, 0, -6)}),

        # -- assis, installe : jambes horizontales (pas de genou -- la
        # jambe entiere pointe vers l'avant, cf. note de module), dos
        # contre le dossier, mains posees sur les accoudoirs (Z=+-55,
        # calibre pour tomber exactement sur le dessus de l'accoudoir --
        # voir calibrate.py) --
        _kf(0.70, root_pos=(0, 3.0, 0.0), Torso=(-14, 0, 0), Head=(3, 0, 0),
            **{"Right Arm": (0, 0, 55), "Left Arm": (0, 0, -55),
               "Right Leg": (88, 0, 8), "Left Leg": (88, 0, -8)}),
        _kf(1.00, root_pos=(0, 3.0, 0.0), Torso=(-14, 0, 0), Head=(3, 0, 0),
            **{"Right Arm": (0, 0, 55), "Left Arm": (0, 0, -55),
               "Right Leg": (88, 0, 8), "Left Leg": (88, 0, -8)}),

        # -- couronnement : saisit la couronne posee sur un coussin a
        # l'endroit exact ou repose la main droite (voir props.py
        # CrownCushion, meme coordonnees) --
        _kf(1.35, root_pos=(0, 3.0, 0.0), Torso=(-12, 0, 0), Head=(2, 0, 0),
            **{"Right Arm": (5, 0, 58), "Left Arm": (0, 0, -55),
               "Right Leg": (88, 0, 8), "Left Leg": (88, 0, -8)}),

        # -- souleve la couronne des deux mains (X=180 : portee verticale
        # maximale du bras sans coude, voir note de module) --
        _kf(1.70, root_pos=(0, 3.0, 0.0), Torso=(-10, 0, 0), Head=(-4, 0, 0),
            **{"Right Arm": (180, 0, -35), "Left Arm": (180, 0, 35),
               "Right Leg": (88, 0, 8), "Left Leg": (88, 0, -8)}),

        # -- abaisse la couronne exactement sur le sommet de la tete
        # (position calibree, voir calibrate.py : main a 0.14 stud du
        # sommet de la tete a ce reglage) --
        _kf(2.00, root_pos=(0, 3.0, 0.0), Torso=(-13, 0, 0), Head=(-2, 0, 0),
            **{"Right Arm": (180, 0, -45), "Left Arm": (180, 0, 45),
               "Right Leg": (88, 0, 8), "Left Leg": (88, 0, -8)}),

        # -- relache, mains reviennent sur les accoudoirs, tete fiere --
        _kf(2.30, root_pos=(0, 3.0, 0.0), Torso=(-16, 2, 0), Head=(-6, 0, 0),
            **{"Right Arm": (0, 0, 55), "Left Arm": (0, 0, -55),
               "Right Leg": (88, 0, 8), "Left Leg": (88, 0, -8)}),

        # -- pose finale tenue --
        _kf(2.80, root_pos=(0, 3.0, 0.0), Torso=(-16, 3, 0), Head=(-8, 0, 0),
            **{"Right Arm": (0, 0, 55), "Left Arm": (0, 0, -55),
               "Right Leg": (88, 0, 8), "Left Leg": (88, 0, -8)}),
    ]

    phases = [
        {"name": "approche", "t0": 0.00, "t1": 0.35, "expected_reversals": {}},
        {"name": "assise", "t0": 0.35, "t1": 1.00, "expected_reversals": {}},
        {"name": "couronnement", "t0": 1.00, "t1": 2.30, "expected_reversals": {}},
        {"name": "pose_finale", "t0": 2.30, "t1": 2.80, "expected_reversals": {}},
    ]
    preview_times = [0.0, 0.35, 0.70, 1.35, 1.70, 2.00, 2.30, 2.80]
    engine_opts = {"handle_type": "AUTO_CLAMPED"}
    return keyframes, phases, preview_times, engine_opts


# Instants-cles utilises par compute_crown_track.py pour savoir quand la
# couronne quitte son piedestal / atteint la tete -- doivent rester
# coherents avec les temps de keyframes ci-dessus. RELATIFS a
# sit_and_crown() seule -- voir FULL_PICKUP_T/FULL_PLACED_T pour la
# version decalee par la montee de l'escalier, utilisee partout ailleurs.
PICKUP_T = 1.35
PLACED_T = 2.00

# -- Montee de l'escalier -- "sombre mais fiere" : pas lent et delibere
# (STEP_T large), bras presque immobiles (pas de balancement naturel --
# c'est la retenue qui lit comme sombre/impérial, pas une pose precise),
# tete haute constante (menton leve, fier) du debut a la fin. Chaque
# marche = une seule jambe qui se leve puis se pose, alternee, avec une
# legere contre-rotation du torse (contrapposto) au moment du levers.
#
# Orientation -- bug trouve sur retour utilisateur direct ("ça voudrait
# dire que il les monte en arriere") : root_pos avance en Z croissant
# (vers le trone) mais HumanoidRootPart restait a l'identite partout,
# donc le personnage gardait le cap -Z (avant du rig) du debut a la fin
# -- il montait donc bien les marches en marchant a reculons, exactement
# le defaut signale. Corrige en deux temps :
#   1. Pendant la montee elle-meme (marches), HumanoidRootPart Y=180 :
#      le personnage fait face au trone (+Z), donc avance en marchant
#      VRAIMENT vers l'avant (la jambe qui se leve en "avant" dans son
#      propre repere -- convention X positif inchangee, elle est locale
#      au torse, voir docstring de module -- pousse alors bien le
#      personnage vers +Z, plus vers -Z).
#   2. Une fois en haut, un demi-tour (TURN_T) ramene HumanoidRootPart
#      de 180 a 0 SUR PLACE (racine immobile) avant l'assise -- assise
#      qui suppose une orientation a 0 (dos au dossier, face a -Z,
#      convention deja verifiee dans sit_and_crown). Sans ce demi-tour
#      le personnage se serait assis dos au vide, face au dossier.
#
# Ecrit directement dans le repere MONDE final (pas de decalage a
# appliquer ensuite) : commence au pied de l'escalier (sol reel, Y=3
# hanche = pieds a 0) et finit exactement au premier keyframe de
# sit_and_crown() DEJA DECALE par PLATFORM_H (voir full_scene) --
# c'est ce raccord qui garantit qu'il n'y a pas de saut visible entre
# la montee et l'assise.
STEP_T = 0.75
STAIRS_T = props.STAIR_N * STEP_T
TURN_T = 0.85
CLIMB_T = STAIRS_T + TURN_T

_CLIMB_Z0 = -7.2   # au pied de l'escalier, avec une marge avant la 1ere marche
_CLIMB_Z1 = -1.6   # doit correspondre au premier keyframe de sit_and_crown()
_PROUD_HEAD = (-6, 0, 0)
_PROUD_TORSO_X = -6
_FACE_STAIRS = (0, 180, 0)   # HumanoidRootPart : face au trone (+Z), pendant la montee
_FACE_ROOM = (0, 0, 0)       # HumanoidRootPart : face a la salle (-Z), convention assise


def climb_stairs():
    keyframes = [
        _kf(0.00, root_pos=(0, 3.0, _CLIMB_Z0), HumanoidRootPart=_FACE_STAIRS,
            Torso=(_PROUD_TORSO_X, 0, 0), Head=_PROUD_HEAD,
            **{"Right Arm": (2, 0, -5), "Left Arm": (2, 0, 5),
               "Right Leg": (0, 0, 0), "Left Leg": (0, 0, 0)}),
    ]
    for i in range(1, props.STAIR_N + 1):
        lead, trail = ("Right Leg", "Left Leg") if i % 2 == 1 else ("Left Leg", "Right Leg")
        twist = -4 if i % 2 == 1 else 4
        t_lift = (i - 1) * STEP_T + STEP_T * 0.45
        t_plant = i * STEP_T
        y_prev = 3.0 + (i - 1) * props.STAIR_RISER
        y_new = 3.0 + i * props.STAIR_RISER
        z_prev = _CLIMB_Z0 + (i - 1) / props.STAIR_N * (_CLIMB_Z1 - _CLIMB_Z0)
        z_new = _CLIMB_Z0 + i / props.STAIR_N * (_CLIMB_Z1 - _CLIMB_Z0)

        keyframes.append(_kf(
            t_lift, root_pos=(0, y_prev + props.STAIR_RISER * 0.3, (z_prev + z_new) / 2.0),
            HumanoidRootPart=_FACE_STAIRS, Torso=(_PROUD_TORSO_X, twist, 0), Head=_PROUD_HEAD,
            **{lead: (30, 0, 0), trail: (-8, 0, 0),
               "Right Arm": (2, 0, -5), "Left Arm": (2, 0, 5)}))
        keyframes.append(_kf(
            t_plant, root_pos=(0, y_new, z_new),
            HumanoidRootPart=_FACE_STAIRS, Torso=(_PROUD_TORSO_X, 0, 0), Head=_PROUD_HEAD,
            **{lead: (2, 0, 0), trail: (-4, 0, 0),
               "Right Arm": (2, 0, -5), "Left Arm": (2, 0, 5)}))

    # -- demi-tour sur place, en haut des marches -- PAS une rotation
    # rigide d'un seul bloc (1re version, retour utilisateur : "on dirait
    # il tourne comme une toupie"). Un vrai demi-tour humain (le "about
    # face" militaire est le modele le plus proche du personnage "sombre
    # mais fiere") decompose le mouvement au lieu de tourner tout le
    # corps a vitesse constante autour d'un axe fixe :
    #   1. la TETE part en premier ("spotting", meme principe que le
    #      head_lead mesure dans le combo de coups de pied -- on regarde
    #      ou on va avant que le corps suive), le poids se transfere sur
    #      la jambe d'appui (leger creux vertical) et la jambe libre se
    #      souleve legerement, amorcant un pas de pivot ;
    #   2. le CORPS (HumanoidRootPart) tourne pendant que la jambe libre
    #      est encore en l'air -- pas apres qu'elle soit reposee, sinon
    #      le tourne-sur-deux-pieds-plantes est exactement ce qui lit
    #      comme une toupie ;
    #   3. la jambe se repose au sol, deja tournee avec le corps ("step
    #      turn"), le torse epaules-en-avant se rattrape en dernier.
    # Chaque partie a donc SA PROPRE cadence plutot que de bouger toutes
    # ensemble a la meme vitesse -- c'est cette desynchronisation qui
    # lit comme un geste humain plutot qu'une rotation mecanique unique.
    top_y = 3.0 + props.STAIR_N * props.STAIR_RISER
    HALF_TURN = (0, 90, 0)

    # t0 : appui pris franchement sur la jambe gauche, jambe droite se
    # souleve pour amorcer le pivot, la tete a deja commence a tourner
    # (repere LOCAL au torse -- son cap effectif dans le monde est donc
    # torse+tete, en avance sur le corps qui n'a pas encore tourne).
    keyframes.append(_kf(
        STAIRS_T + TURN_T * 0.28, root_pos=(0, top_y - 0.10, _CLIMB_Z1),
        HumanoidRootPart=_FACE_STAIRS, Torso=(_PROUD_TORSO_X, -18, 0), Head=(-6, -75, 0),
        **{"Right Arm": (2, 0, -5), "Left Arm": (2, 0, 5),
           "Right Leg": (14, 0, 4), "Left Leg": (-3, 0, -2)}))

    # t1 : le corps tourne PENDANT que la jambe droite est encore en
    # l'air (c'est ce qui distingue un pas-pivot d'une toupie) --
    # le poids remonte, la jambe commence a se replanter dans le nouveau
    # cap.
    keyframes.append(_kf(
        STAIRS_T + TURN_T * 0.62, root_pos=(0, top_y - 0.03, _CLIMB_Z1),
        HumanoidRootPart=HALF_TURN, Torso=(_PROUD_TORSO_X, -8, 0), Head=(-6, -25, 0),
        **{"Right Arm": (2, 0, -5), "Left Arm": (2, 0, 5),
           "Right Leg": (6, 0, 0), "Left Leg": (-2, 0, 0)}))

    # t2 : jambe replantee, le torse/la tete finissent de se rattraper
    # en dernier -- le corps a fini de tourner legerement avant eux, pas
    # tout en meme temps.
    keyframes.append(_kf(
        STAIRS_T + TURN_T * 0.85, root_pos=(0, top_y, _CLIMB_Z1),
        HumanoidRootPart=(0, 20, 0), Torso=(_PROUD_TORSO_X, -3, 0), Head=(-6, -8, 0),
        **{"Right Arm": (2, 0, -5), "Left Arm": (2, 0, 5),
           "Right Leg": (0, 0, 0), "Left Leg": (0, 0, 0)}))

    # t3 : pose finale du demi-tour, tout est rattrape et immobile --
    # doit coincider EXACTEMENT avec le premier keyframe de
    # sit_and_crown() decale (voir docstring de full_scene()).
    keyframes.append(_kf(
        STAIRS_T + TURN_T, root_pos=(0, top_y, _CLIMB_Z1),
        HumanoidRootPart=_FACE_ROOM, Torso=(_PROUD_TORSO_X, 0, 0), Head=_PROUD_HEAD,
        **{"Right Arm": (2, 0, -5), "Left Arm": (2, 0, 5),
           "Right Leg": (0, 0, 0), "Left Leg": (0, 0, 0)}))

    phases = [
        {"name": "montee", "t0": 0.00, "t1": STAIRS_T, "expected_reversals": {}},
        {"name": "demi_tour", "t0": STAIRS_T, "t1": CLIMB_T, "expected_reversals": {}},
    ]
    preview_times = [0.0, STEP_T * 0.45, STEP_T, STAIRS_T,
                      STAIRS_T + TURN_T * 0.28, STAIRS_T + TURN_T * 0.62, STAIRS_T + TURN_T]
    engine_opts = {"handle_type": "AUTO_CLAMPED"}
    return keyframes, phases, preview_times, engine_opts


def full_scene():
    """Scene complete : montee de l'escalier (repere monde final, non
    decalee) puis assise + couronnement (sit_and_crown(), authoree au
    niveau de SA PROPRE estrade -- Y=3 de hanche -- et decalee ici de
    +PLATFORM_H en Y et de +CLIMB_T en temps). Le raccord entre les deux
    est exact : le dernier keyframe de climb_stairs() et le premier de
    sit_and_crown() (decale) tombent tous deux sur (0, 3.0+PLATFORM_H,
    _CLIMB_Z1) -- verifie dans calibrate.py, pas seulement suppose."""
    climb_kf, climb_ph, climb_pt, climb_opts = climb_stairs()
    sit_kf, sit_ph, sit_pt, sit_opts = sit_and_crown()

    shifted_sit_kf = []
    for kf in sit_kf:
        nk = dict(kf)
        nk["time"] = kf["time"] + CLIMB_T
        rp = kf["root_pos"]
        nk["root_pos"] = (rp[0], rp[1] + props.PLATFORM_H, rp[2])
        shifted_sit_kf.append(nk)

    shifted_sit_ph = [{**p, "t0": p["t0"] + CLIMB_T, "t1": p["t1"] + CLIMB_T} for p in sit_ph]
    shifted_sit_pt = [t + CLIMB_T for t in sit_pt]

    keyframes = climb_kf + shifted_sit_kf
    phases = climb_ph + shifted_sit_ph
    preview_times = climb_pt + shifted_sit_pt
    return keyframes, phases, preview_times, sit_opts


FULL_PICKUP_T = PICKUP_T + CLIMB_T
FULL_PLACED_T = PLACED_T + CLIMB_T

# "Secondary motion" -- retard/depassement/stabilisation du buste pendant
# l'assise et le couronnement, recree localement (voir anim_engine.
# _spring_chase()) faute d'acces a un outil comme Cascadeur dans ce
# sandbox (pas de GPU, pas de cle d'API -- voir le worklog de session).
# PORTEE VOLONTAIREMENT LIMITEE :
#   - Seul le Torso est concerne. Les bras portent la couronne et
#     s'appuient sur les accoudoirs a des positions CALIBREES au stud
#     pres (voir calibrate.py) -- leur ajouter du retard desynchroniserait
#     la couronne suivie (compute_crown_track.py lit tip_world("Right
#     Arm") sur les MEMES echantillons, donc resterait cinematiquement
#     coherent, mais la couronne "flotterait" visiblement en retard de
#     la main au moment prevu pour l'attraper/la poser).
#   - t_min=CLIMB_T : aucun effet pendant la montee de l'escalier et le
#     demi-tour, deja choregraphies a la main image par image (tete qui
#     part en premier, jambe en l'air pendant la rotation du corps, buste
#     qui rattrape en dernier -- voir climb_stairs()) -- un lissage
#     automatique par-dessus risquerait de diluer ce travail plutot que
#     de l'ameliorer.
SECONDARY_MOTION = {
    "Torso": {"channels": (0, 1, 2), "stiffness": 220.0,
              "damping_ratio": 0.78, "t_min": CLIMB_T},
}
