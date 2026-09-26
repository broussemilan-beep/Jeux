"""
Choregraphie : le personnage DESCEND du ciel (pas une chute libre depuis
le premier instant) -- lent et calme au debut, puis a mi-chemin il
REVELE son cote divin (transition rapide vers la silhouette d'aile
agressive, aura/rayon de lumiere qui s'allument dans le lecteur) et
plonge vite vers le sol. Il ATTERRIT sur ses appuis (pas encore de
coup), MARQUE UNE PAUSE (tenue immobile, tension avant le coup), puis
ABAT RAPIDEMENT son poing au sol -- c'est ce coup, pas l'atterrissage,
qui declenche l'explosion d'aura doree/poussiere/sol brise du lecteur --
avant de se relever dans une pose fiere et puissante.

Deux retours utilisateur successifs ont faconne cette structure :
  1. "il tombe... marque une pause et abat sa colere de son poing" -- la
     toute premiere version faisait atterrissage et coup de poing en un
     seul mouvement continu, corrige en 2 beats distincts (voir LAND_T/
     PAUSE_T/STRIKE_T).
  2. "il ne tombe pas du ciel il en descend donc au debut c'est ralenti
     puis une fois arrive a mi-chemin on montre son cote divin et boum"
     -- la chute etait rapide/accelerante DES LE DEBUT (silhouette
     d'aile agressive a t=0). Corrige en scindant la descente en 2
     temps : lent/calme jusqu'a REVEAL_T (silhouette neutre, aucune
     aura/rayon dans le lecteur), puis reveal + acceleration rapide
     jusqu'au sol.

Meme convention d'ecriture que r6_throne_crown/r6_aerial_kick_combo
(rotations en degres, `_kf` identique, repere/joint conversion
inchanges -- voir `export_kfseq.to_joint_frame`).

Semantique des axes (etablie empiriquement dans r6_throne_crown, PAS
resupposee ici -- reverifiee par calcul dans calibrate.py) :
  - Torso/Head/Right Leg/Left Leg : X positif = penche/tourne VERS
    L'AVANT (bas de la tete, buste courbe, jambe qui monte vers l'avant).
    X negatif = vers l'arriere/le haut (tete fiere, buste droit).
  - Right Arm/Left Arm : X positif = part vers l'AVANT (-Z) puis monte
    par-dessus jusqu'a X=180 (au-dessus de la tete) ; entre 0 et 90, le
    bras pointe en diagonale avant-bas -- utilise pour le poing plante au
    sol a l'impact. Z (bras droit) positif = ecarte VERS L'EXTERIEUR ;
    bras gauche, signe oppose (verifie au calibrage du trone/couronne).
  - Aucun coude/genou (contrainte du rig, voir r6_rig.py) : la fente
    d'atterrissage est donc une posture LARGE et BASSE (les deux jambes
    tendues, angles moderes), pas un genou pose au sol -- limite
    assumee, dite honnetement plutot que maquillee (meme choix que R6
    "assis" dans r6_throne_crown).
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


# Altitude de depart -- assez haute pour une VRAIE sensation de chute
# (~17x la hauteur du personnage), assez basse pour que le lecteur HTML
# puisse suivre toute la descente avec une camera "follow" raisonnable
# (voir README, section camera).
SKY_Y = 34.0
GROUND_Y = 3.0          # hanche debout, cf. r6_throne_crown/README
IMPACT_Y = 1.85          # hanche en fente d'atterrissage -- calibree (voir calibrate.py) :
                          # avec Torso/Head penches a l'impact, une hanche plus haute
                          # (essaye 2.3 en premier) laissait le poing a Y=2.67, tres
                          # loin du sol -- PAS supposee correcte a l'oeil, un balayage
                          # numerique (calibrate.py) a trouve 1.85 comme hauteur ou le
                          # poing peut vraiment approcher le sol (Y=0.66, cf. IMPACT_RIGHT_ARM).

# -- Beat 0a : DESCENTE CALME -- silhouette neutre, presque verticale,
# bras/jambes a peine ecartes : il DESCEND, il ne tombe pas encore. Le
# lecteur n'allume ni aura ni rayon de lumiere avant REVEAL_T (voir
# README) -- "montrer son cote divin" doit rester un evenement, pas un
# etat permanent des le premier instant.
_CALM_ARMS = {"Right Arm": (5, 0, 20), "Left Arm": (5, 0, -20)}
_CALM_LEGS = {"Right Leg": (3, 0, 3), "Left Leg": (3, 0, -3)}
_CALM_TORSO = (8, 0, 0)
_CALM_HEAD = (6, 0, 0)

# -- Beat 0b : REVEAL -- silhouette d'aile agressive, ailes ecartees,
# jambes tendues balayees en arriere, tete/buste plonges vers le sol :
# la posture "divine" que la descente calme cachait jusque-la. Lisible
# de loin (le lecteur zoome/suit rarement d'assez pres pour lire un
# detail fin pendant la chute rapide qui suit).
_FALL_ARMS = {"Right Arm": (-15, 0, 85), "Left Arm": (-15, 0, -85)}
_FALL_LEGS = {"Right Leg": (-8, 0, 6), "Left Leg": (-8, 0, -6)}
_FALL_TORSO = (18, 0, 0)
_FALL_HEAD = (28, 0, 0)

# Jambes d'atterrissage -- calibrees par calcul (voir calibrate.py), pas
# a l'oeil : un premier essai (jambes a 40/18 degres, hanche Y=2.3)
# laissait le poing (une fois le bras ajoute) a Y=2.67 -- plus haut que
# la hanche elle-meme, bien loin du sol. Balayage numerique
# (calibrate.py) : les DEUX pieds touchent le sol pres de Y=0 a
# hanche=1.85 / jambes (22,16)+(8,-10) -- INCHANGEES du touche-au-sol
# jusqu'au coup de poing, seuls le torse/la tete/les bras bougent entre
# ces deux beats (voir docstring de module : retour utilisateur sur la
# structure en 2 temps).
LAND_RIGHT_LEG = (22, 0, 16)
LAND_LEFT_LEG = (8, 0, -10)

# -- Beat 1 : ATTERRISSAGE + PAUSE -- touche le sol, bras REMONTES en
# amorce ("wind-up", comme un marteau leve avant de s'abattre), PAS
# encore de poing au sol. Tenue immobile un instant (meme pose repetee a
# LAND_T et PAUSE_T -- aucune interpolation entre deux keyframes
# identiques, donc un arret net, pas juste un ralentissement) avant le
# coup.
LAND_TORSO = (42, 0, 0)
LAND_HEAD = (32, 0, 0)
LAND_RIGHT_ARM = (125, 0, -25)   # leve/en arriere, amorce du coup -- PAS au sol
LAND_LEFT_ARM = (14, 0, -68)     # bras d'appui/equilibre, immobile pendant tout l'atterrissage

# -- Beat 2 : LE COUP -- le poing s'abat au sol RAPIDEMENT (peu de temps
# entre PAUSE_T et STRIKE_T, voir divine_descent() : un coup est un
# mouvement brusque, pas une transition lente comme le reste de la
# chorégraphie). Angle de bras calibre par balayage numerique
# (calibrate.py) : le poing droit ne peut pas descendre sous Y~0,65 stud
# a cette hauteur de hanche quel que soit l'angle essaye (longueur de
# bras + inclinaison du torse fixes) -- limite REELLE du rig (pas de
# coude), pas une erreur de reglage : valeur la plus basse trouvee par
# balayage retenue plutot que devinee. Torse/tete plonges plus loin
# qu'au simple atterrissage (50/40 vs 42/32) -- le corps entier suit le
# poing dans le coup, pas seulement le bras.
STRIKE_TORSO = (50, 0, 0)
STRIKE_HEAD = (40, 0, 0)
STRIKE_RIGHT_ARM = (-35, 0, -14)
STRIKE_LEFT_ARM = (14, 0, -68)

# Pose finale -- "un dieu s'est pose" : tete haute, buste droit/fier
# (meme convention que la montee d'escalier du trone : X negatif =
# fier), jambes debout, bras legerement ecartes du corps, ouverts.
_STAND_TORSO = (-8, 0, 0)
_STAND_HEAD = (-10, 0, 0)
_STAND_LEGS = {"Right Leg": (0, 0, 3), "Left Leg": (0, 0, -3)}
_STAND_ARMS = {"Right Arm": (2, 0, 12), "Left Arm": (2, 0, -12)}


def divine_descent():
    keyframes = [
        # -- descente calme, tres haut : espacement de temps LARGE, peu
        # de distance parcourue par intervalle -- il DESCEND, un vol
        # controle, pas une chute (retour utilisateur explicite, voir
        # docstring de module). Silhouette neutre (_CALM_*).
        _kf(0.00, root_pos=(0, SKY_Y, 0), Torso=_CALM_TORSO, Head=_CALM_HEAD,
            **_CALM_LEGS, **_CALM_ARMS),
        _kf(0.50, root_pos=(0, SKY_Y - 2.5, 0), Torso=_CALM_TORSO, Head=_CALM_HEAD,
            **_CALM_LEGS, **_CALM_ARMS),
        _kf(1.00, root_pos=(0, SKY_Y - 5.0, 0), Torso=_CALM_TORSO, Head=_CALM_HEAD,
            **_CALM_LEGS, **_CALM_ARMS),
        _kf(REVEAL_T - 0.15, root_pos=(0, SKY_Y - 7.0, 0), Torso=_CALM_TORSO, Head=_CALM_HEAD,
            **_CALM_LEGS, **_CALM_ARMS),

        # -- REVEAL : transition RAPIDE (0,15s) vers la silhouette
        # d'aile agressive -- "on montre son cote divin" doit se lire
        # comme un evenement net, pas une derive progressive. La chute
        # accelere aussi a partir d'ici (voir les increments de Y
        # ci-dessous, bien plus grands qu'avant REVEAL_T).
        _kf(REVEAL_T, root_pos=(0, SKY_Y - 10.0, 0), Torso=_FALL_TORSO, Head=_FALL_HEAD,
            **_FALL_LEGS, **_FALL_ARMS),
        _kf(REVEAL_T + 0.25, root_pos=(0, SKY_Y - 20.0, 0), Torso=_FALL_TORSO, Head=_FALL_HEAD,
            **_FALL_LEGS, **_FALL_ARMS),
        _kf(REVEAL_T + 0.50, root_pos=(0, SKY_Y - 28.0, 0), Torso=_FALL_TORSO, Head=_FALL_HEAD,
            **_FALL_LEGS, **_FALL_ARMS),

        # -- anticipation : tout dernier instant avant le sol, le corps
        # commence deja a se replier vers la posture d'impact (bras qui
        # se ramenent, jambes qui plient l'angle) -- lu comme un
        # freinage/une preparation, pas juste une chute qui s'arrete net.
        _kf(REVEAL_T + 0.62, root_pos=(0, SKY_Y - 30.65, 0), Torso=(30, 0, 0), Head=(30, 0, 0),
            **{"Right Leg": (16, 0, 12), "Left Leg": (6, 0, -7),
               "Right Arm": (-15, 0, 10), "Left Arm": (8, 0, -45)}),

        # -- ATTERRISSAGE : touche le sol, bras deja en amorce (wind-up)
        # -- PAS de poing au sol ici, voir docstring de module.
        _kf(LAND_T, root_pos=(0, IMPACT_Y, 0), Torso=LAND_TORSO, Head=LAND_HEAD,
            **{"Right Leg": LAND_RIGHT_LEG, "Left Leg": LAND_LEFT_LEG,
               "Right Arm": LAND_RIGHT_ARM, "Left Arm": LAND_LEFT_ARM}),

        # -- PAUSE : meme pose EXACTE que LAND_T -- deux keyframes
        # identiques de part et d'autre d'un intervalle de temps donnent
        # une interpolation plate, donc un arret net et tenu, pas un
        # ralentissement. C'est le battement de tension avant le coup.
        _kf(PAUSE_T, root_pos=(0, IMPACT_Y, 0), Torso=LAND_TORSO, Head=LAND_HEAD,
            **{"Right Leg": LAND_RIGHT_LEG, "Left Leg": LAND_LEFT_LEG,
               "Right Arm": LAND_RIGHT_ARM, "Left Arm": LAND_LEFT_ARM}),

        # -- LE COUP : le poing s'abat au sol -- intervalle tres court
        # depuis PAUSE_T (voir STRIKE_T ci-dessous) pour un mouvement
        # brusque, pas une transition lente. C'est CE keyframe qui
        # declenche l'explosion du lecteur (impact_t).
        _kf(STRIKE_T, root_pos=(0, IMPACT_Y, 0), Torso=STRIKE_TORSO, Head=STRIKE_HEAD,
            **{"Right Leg": LAND_RIGHT_LEG, "Left Leg": LAND_LEFT_LEG,
               "Right Arm": STRIKE_RIGHT_ARM, "Left Arm": STRIKE_LEFT_ARM}),

        # -- tenu un instant : le temps que l'onde de choc du lecteur se
        # lise avant que le personnage ne commence a se relever --
        _kf(STRIKE_T + 0.20, root_pos=(0, IMPACT_Y + 0.05, 0), Torso=STRIKE_TORSO, Head=STRIKE_HEAD,
            **{"Right Leg": LAND_RIGHT_LEG, "Left Leg": LAND_LEFT_LEG,
               "Right Arm": STRIKE_RIGHT_ARM, "Left Arm": STRIKE_LEFT_ARM}),

        # -- releve, mi-parcours --
        _kf(STRIKE_T + 0.55, root_pos=(0, 2.35, 0), Torso=(22, 0, 0), Head=(16, 0, 0),
            **{"Right Leg": (14, 0, 10), "Left Leg": (6, 0, -6),
               "Right Arm": (5, 0, 12), "Left Arm": (10, 0, -30)}),

        # -- presque debout, bras qui s'ouvrent --
        _kf(STRIKE_T + 0.90, root_pos=(0, 2.85, 0), Torso=(3, 0, 0), Head=(-2, 0, 0),
            **{"Right Leg": (4, 0, 4), "Left Leg": (2, 0, -3),
               "Right Arm": (2, 0, 9), "Left Arm": (2, 0, -9)}),

        # -- pose finale tenue : "un dieu s'est pose" --
        _kf(STRIKE_T + 1.25, root_pos=(0, GROUND_Y, 0), Torso=_STAND_TORSO, Head=_STAND_HEAD,
            **_STAND_LEGS, **_STAND_ARMS),
    ]

    phases = [
        {"name": "descente", "t0": 0.00, "t1": REVEAL_T, "expected_reversals": {}},
        {"name": "reveal", "t0": REVEAL_T, "t1": REVEAL_T + 0.62, "expected_reversals": {}},
        {"name": "chute", "t0": REVEAL_T + 0.62, "t1": LAND_T, "expected_reversals": {}},
        {"name": "atterrissage", "t0": LAND_T, "t1": PAUSE_T, "expected_reversals": {}},
        {"name": "frappe", "t0": PAUSE_T, "t1": STRIKE_T, "expected_reversals": {}},
        {"name": "impact", "t0": STRIKE_T, "t1": STRIKE_T + 0.20, "expected_reversals": {}},
        {"name": "releve", "t0": STRIKE_T + 0.20, "t1": STRIKE_T + 1.25, "expected_reversals": {}},
    ]
    preview_times = [0.0, 0.50, 1.00, REVEAL_T - 0.15, REVEAL_T, REVEAL_T + 0.25,
                      REVEAL_T + 0.50, REVEAL_T + 0.62, LAND_T, PAUSE_T, STRIKE_T,
                      STRIKE_T + 0.20, STRIKE_T + 0.55, STRIKE_T + 0.90, STRIKE_T + 1.25]
    engine_opts = {"handle_type": "AUTO_CLAMPED"}
    return keyframes, phases, preview_times, engine_opts


# REVEAL_T : fin de la descente calme, debut de la silhouette d'aile +
# acceleration -- exporte separement (voir dump_scene_data.py) pour que
# le lecteur n'allume l'aura/le rayon de lumiere qu'A PARTIR de cet
# instant, jamais avant (retour utilisateur : "montrer son cote divin"
# doit etre un evenement a mi-chemin, pas un etat de la scene entiere).
# LAND_T : touche le sol, pas encore de coup. PAUSE_T : meme pose tenue
# (0,33s de battement -- assez long pour se LIRE comme une pause
# deliberee, pas une hesitation). STRIKE_T : PAUSE_T + 0,10s seulement --
# le coup lui-meme doit etre brusque. IMPACT_T reste le nom exporte lu
# par dump_scene_data.py/le lecteur pour declencher l'explosion : il
# pointe sur le coup (STRIKE_T), jamais sur le simple atterrissage
# (LAND_T) -- distinction explicite, voir aussi dump_scene_data.py qui
# exporte LAND_T et REVEAL_T separement pour la mise en scene de chute
# (rayon de lumiere, camera, trainee) qui doit demarrer a REVEAL_T et
# s'arreter a l'atterrissage, pas attendre le coup.
REVEAL_T = 1.35
LAND_T = REVEAL_T + 0.72
PAUSE_T = LAND_T + 0.33
STRIKE_T = PAUSE_T + 0.10
IMPACT_T = STRIKE_T
