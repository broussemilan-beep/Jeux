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
# coherents avec les temps de keyframes ci-dessus.
PICKUP_T = 1.35
PLACED_T = 2.00
