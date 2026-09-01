"""
Choregraphie du combo aerien "pieds uniquement" -- une entree par cycle
(CYCLES[n]), chacune un ajustement documente de la precedente. Convention
de rotation : CFrame.Angles(x,y,z) style Roblox (Rx*Ry*Rz, degres).
  - Hanche (Right/Left Hip), sur la jambe (repos = pend vers -Y) :
      X>0 balance la jambe vers l'AVANT (-Z) ; X<0 vers l'arriere (+Z).
      Z>0 leve la jambe vers +X (droite du perso) ; Z<0 vers -X (gauche).
      Y = vrille/rotation conique de la jambe autour de son propre axe une
          fois levee -- utilisee pour la qualite "en croissant"/circulaire.
  - Torse/Root (HumanoidRootPart) : X>0 = penche en arriere (bascule vers
    +Z) ; X<0 = penche en avant. Y = lacet (spin vertical). Z = roulis
    (inclinaison laterale).
  - Bras : mouvement de contrepoids uniquement (jamais de projection avant
    a plat façon coup de poing -- verifie automatiquement par
    measure.no_punch_like_arm_pose).

Le Root (HumanoidRootPart) porte le "moteur" de rotation du corps (spin,
lean) -- c'est le seul proxy disponible pour une notion de "bassin" sur un
rig R6 ou Torso est un unique segment rigide sans bassin separe (voir
README, section rig). Torso ajoute par-dessus une rotation locale
supplementaire (le haut du corps qui accompagne/amplifie legerement le
mouvement du bassin, jamais qui le contredit).

Phases nommees, utilisees a la fois pour le reglage fin et pour
measure.twist_reversals (les inversions de sens ATTENDUES, ex. le
"snap" des ciseaux, sont declarees explicitement -- tout le reste est
du tortillement non voulu).
"""

REST = (0.0, 0.0, 0.0)


def _kf(time, root_pos=(0.0, 0.0, 0.0), HumanoidRootPart=REST, Torso=REST,
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


def _smoothstep(x):
    return 3 * x * x - 2 * x * x * x


def _ease_kf(k0, k1, t_mid, ease=True):
    """Keyframe intermediaire entre k0 et k1. Avec ease=True, la
    FRACTION DE VALEUR appliquee suit un smoothstep de la fraction de
    temps (au lieu d'un lerp lineaire pur) : rapproche la valeur de
    l'extremite la plus proche en temps, ce qui, une fois ce point
    lui-meme relie par des segments DROITS (VECTOR), approxime une
    entree/sortie adoucie autour d'une keyframe-sommet -- sans reintroduire
    l'overshoot par tangente auto que VECTOR evite par construction
    (voir cycle 5 / README)."""
    frac_t = (t_mid - k0["time"]) / (k1["time"] - k0["time"])
    frac_v = _smoothstep(frac_t) if ease else frac_t

    def lerp_tuple(a, b):
        return tuple(a[i] + (b[i] - a[i]) * frac_v for i in range(3))

    kf = {"time": t_mid}
    for key in ("root_pos", "HumanoidRootPart", "Torso", "Head",
                "Right Arm", "Left Arm", "Right Leg", "Left Leg"):
        a = k0.get(key, (0.0, 0.0, 0.0))
        b = k1.get(key, (0.0, 0.0, 0.0))
        kf[key] = lerp_tuple(a, b)
    return kf


def cycle_1():
    keyframes = [
        _kf(0.00),

        # Anticipation : leger flechissement (dip du root) + lean avant,
        # les jambes reculent legerement (chargent l'impulsion).
        _kf(0.18, root_pos=(0, -0.35, 0), Torso=(-10, 0, 0),
            **{"Right Leg": (-8, 0, 0), "Left Leg": (-8, 0, 0)}),

        # Impulsion : extension explosive vers le haut, jambes qui
        # repoussent vers le bas/arriere (reaction), torse qui se redresse.
        _kf(0.36, root_pos=(0, 0.9, 0), Torso=(6, 0, 0),
            **{"Right Leg": (-25, 0, 0), "Left Leg": (5, 0, 0),
               "Right Arm": (-20, 0, -10), "Left Arm": (-20, 0, 10)}),

        # KICK 1 -- Croissant exterieur (jambe droite), porte par la
        # rotation du bassin/torse (Root+Torso tournent vers -Y/lateral
        # pour lancer l'arc) plutot que par un simple lever de jambe isole.
        _kf(0.62, root_pos=(0.3, 1.35, 0.1), HumanoidRootPart=(0, -18, 6),
            Torso=(10, -22, 10), Head=(5, -15, 0),
            **{"Right Leg": (55, 35, 95), "Left Leg": (-15, 0, -10),
               "Right Arm": (-15, 10, -70), "Left Arm": (-30, -10, 40)}),

        # Retour/liaison : la jambe droite revient, le corps commence deja
        # a s'engager dans le lacet du kick 2 (chainage, pas d'arret net).
        _kf(0.88, root_pos=(0.1, 1.25, -0.1), HumanoidRootPart=(0, 55, -4),
            Torso=(2, 40, -6),
            **{"Right Leg": (0, 20, 15), "Left Leg": (-20, 10, -20),
               "Right Arm": (-10, 0, -20), "Left Arm": (-25, 0, 30)}),

        # KICK 2 -- Retourne / spin hook kick (jambe gauche). Le
        # Root+Torso terminent une rotation d'environ 190 deg au total
        # depuis le repos ; la jambe part au moment ou la vitesse
        # angulaire du spin est maximale (timing classique du coup
        # retourne), fouettee par ce meme spin, jamais une jambe qui se
        # leve seule sans le corps.
        _kf(1.16, root_pos=(-0.2, 1.55, -0.15), HumanoidRootPart=(0, 150, -10),
            Torso=(-8, 170, -14), Head=(0, 25, 0),
            **{"Right Leg": (-10, 0, -25), "Left Leg": (30, -40, -100),
               "Right Arm": (-20, -20, -35), "Left Arm": (-15, 25, 55)}),

        # Recuperation post-spin : le corps termine sa rotation vers
        # l'avant (-Z), les jambes se rassemblent, transition vers les
        # ciseaux.
        _kf(1.42, root_pos=(0, 1.4, 0), HumanoidRootPart=(0, 195, 0),
            Torso=(15, 195, 0),
            **{"Right Leg": (10, 0, 0), "Left Leg": (-5, 0, 0)}),

        # KICK 3 -- Ciseaux (tesoura, capoeira). Torse/root basculent
        # fortement en arriere (horizontal), les deux jambes s'ecartent en
        # sens opposes (droite avant-haut, gauche arriere-bas) : X oppose
        # sur Right Hip / Left Hip, entrainees par le meme lean de torse.
        _kf(1.66, root_pos=(0, 1.2, 0.25), HumanoidRootPart=(35, 200, 0),
            Torso=(65, 200, 0),
            **{"Right Leg": (55, 0, 0), "Left Leg": (-50, 0, 0),
               "Right Arm": (10, 0, -25), "Left Arm": (10, 0, 25)}),

        # Snap des ciseaux : les jambes inversent (le "coup de ciseaux"
        # proprement dit) -- SEULE inversion de sens deliberee de tout le
        # combo, declaree dans PHASES comme attendue.
        _kf(1.86, root_pos=(0, 1.0, 0.1), HumanoidRootPart=(20, 200, 0),
            Torso=(45, 200, 0),
            **{"Right Leg": (-45, 0, 0), "Left Leg": (50, 0, 0)}),

        # Retour au corps rassemble, rotation du corps revient face -Z.
        _kf(2.05, root_pos=(0, 0.5, 0), HumanoidRootPart=(0, 20, 0),
            Torso=(5, 20, 0),
            **{"Right Leg": (0, 0, 0), "Left Leg": (0, 0, 0)}),

        # Atterrissage : impact absorbe (dip root + leger lean avant),
        # corps de nouveau face -Z.
        _kf(2.20, root_pos=(0, -0.15, 0), Torso=(-12, 0, 0),
            **{"Right Leg": (-5, 0, 0), "Left Leg": (-5, 0, 0)}),

        # Retour au repos neutre.
        _kf(2.36),
    ]

    phases = [
        {"name": "anticipation", "t0": 0.00, "t1": 0.36, "expected_reversals": {}},
        {"name": "kick1_croissant", "t0": 0.36, "t1": 0.88, "expected_reversals": {}},
        {"name": "kick2_retourne", "t0": 0.88, "t1": 1.42, "expected_reversals": {}},
        {"name": "kick3_ciseaux", "t0": 1.42, "t1": 2.05,
         "expected_reversals": {"Right Leg": 1, "Left Leg": 1}},
        {"name": "atterrissage", "t0": 2.05, "t1": 2.36, "expected_reversals": {}},
    ]
    preview_times = [0.0, 0.36, 0.62, 1.16, 1.66, 1.86, 2.36]
    engine_opts = {"handle_type": "AUTO_CLAMPED"}
    return keyframes, phases, preview_times, engine_opts


def cycle_2():
    """Cycle 2 -- une seule variable changee par rapport au cycle 1
    (methode : isoler l'effet avant de combiner plusieurs changements) :
    type de tangente Bezier AUTO_CLAMPED -> VECTOR sur tous les canaux.

    Hypothese testee : les 3 micro-tortillements du cycle 1 (Right Leg
    @0.36, Left Arm+Right Leg @0.88-1.16, Right/Left Leg @1.42-1.66)
    viennent d'un keyframe "pivot" dont la tangente AUTO_CLAMPED est
    tiree par un voisin distant qui repart dans une direction opposee
    (overshoot local). VECTOR = tangente rectiligne vers chaque voisin
    immediat, aucun overshoot possible par construction, au prix d'un
    leger "cassant" aux keyframes (moins d'ease-in/out) que AUTO_CLAMPED.
    """
    keyframes, phases, preview_times, _ = cycle_1()
    engine_opts = {"handle_type": "VECTOR"}
    return keyframes, phases, preview_times, engine_opts


def cycle_3():
    """Cycle 3 -- hypothese differente du cycle 2. Le cycle 2 (VECTOR
    partout) gagnait sur le jerk intra-segment (perfection triviale :
    segment rectiligne = jerk nul par construction) mais degradait la
    continuite de vitesse aux keyframes (17.2 vs 52.2 au cycle 1) --
    mouvement plus "mecanique". Ici on garde AUTO_CLAMPED (sa continuite
    de vitesse native) mais on INSERE des keyframes intermediaires a
    mi-arc sur les 3 segments a plus fort jerk releves au cycle 1
    (Left Leg=131, Right Leg=119, Torso=102, sur smoothness_per_joint) :
    kick1 (0.36->0.62), kick2 (0.88->1.16), kick3 approche (1.42->1.66).
    Un arc plus court = moins de courbure requise par segment = jerk plus
    bas, SANS toucher a la continuite (reste AUTO_CLAMPED partout)."""
    keyframes, phases, preview_times, _ = cycle_1()
    by_time = {round(k["time"], 5): k for k in keyframes}

    def lerp_kf(t0, t1, t_mid, extra=None):
        k0, k1 = by_time[round(t0, 5)], by_time[round(t1, 5)]
        frac = (t_mid - t0) / (t1 - t0)

        def lerp_tuple(a, b):
            return tuple(a[i] + (b[i] - a[i]) * frac for i in range(3))

        kf = {"time": t_mid}
        for key in ("root_pos", "HumanoidRootPart", "Torso", "Head",
                    "Right Arm", "Left Arm", "Right Leg", "Left Leg"):
            a = k0.get(key, (0.0, 0.0, 0.0))
            b = k1.get(key, (0.0, 0.0, 0.0))
            kf[key] = lerp_tuple(a, b)
        if extra:
            kf.update(extra)
        return kf

    # Mi-arc kick1 (0.36 -> 0.62), avec un peu plus de lift/torse deja
    # engage que le pur lerp lineaire (le mouvement doit deja "partir",
    # pas juste etre la moyenne arithmetique des deux poses).
    mid1 = lerp_kf(0.36, 0.62, 0.49, extra={
        "Right Leg": (25, 15, 45), "Torso": (8, -10, 5), "root_pos": (0.15, 1.15, 0.05),
    })
    # Mi-arc kick2 (0.88 -> 1.16) -- le spin est deja bien engage a mi-chemin.
    mid2 = lerp_kf(0.88, 1.16, 1.02, extra={
        "HumanoidRootPart": (0, 100, -7), "Torso": (-3, 105, -10),
        "Left Leg": (10, -20, -55),
    })
    # Mi-arc approche kick3 (1.42 -> 1.66).
    mid3 = lerp_kf(1.42, 1.66, 1.54, extra={
        "HumanoidRootPart": (18, 197, 0), "Torso": (40, 197, 0),
        "Right Leg": (30, 0, 0), "Left Leg": (-25, 0, 0),
    })

    new_keyframes = sorted(keyframes + [mid1, mid2, mid3], key=lambda k: k["time"])
    engine_opts = {"handle_type": "AUTO_CLAMPED"}
    return new_keyframes, phases, preview_times, engine_opts


def cycle_4():
    """Cycle 4 -- synthese des cycles 2 et 3. Cycle 2 (VECTOR partout)
    gagnait largement au total (87.6) grace au jerk intra-segment nul,
    mais degradait la continuite de vitesse (17.2). Cycle 3 (AUTO_CLAMPED
    + keyframes intermediaires) n'a quasi rien change (65.4, dans le
    bruit du cycle 1) -- ajouter des keyframes intermediaires choisies a
    la main n'a pas aide, voire legerement aggrave Left/Right Leg.

    Hypothese cycle 4 : VECTOR seulement sur les articulations qui
    PORTENT le geste (Right/Left Leg -- ce sont elles qui frappent, un
    tempo net/franc y est stylistiquement defendable pour un impact de
    coup de pied) et sur Torso/HumanoidRootPart (le "moteur" bassin/elan,
    doit rester synchronise avec les jambes) ; AUTO_CLAMPED conserve sur
    Head/Right Arm/Left Arm (mouvement d'accompagnement secondaire, ou la
    continuite de vitesse compte plus que le franc)."""
    keyframes, phases, preview_times, _ = cycle_1()
    engine_opts = {
        "handle_type": "AUTO_CLAMPED",
        "handle_type_per_part": {
            "Right Leg": "VECTOR", "Left Leg": "VECTOR",
            "Torso": "VECTOR", "HumanoidRootPart": "VECTOR",
        },
    }
    return keyframes, phases, preview_times, engine_opts


def cycle_5():
    """Cycle 5 (dernier du budget borne a 5) -- s'appuie sur cycle 2
    (VECTOR partout, meilleur score jusqu'ici : 87.6) et cible directement
    sa faiblesse mesuree : velocity_continuity_at_keyframes releve les
    plus gros sauts pile aux 3 sommets d'appui (t=0.62 kick1, t=1.16
    kick2, t=1.66/1.86 kick3 -- jusqu'a 1.4 de saut normalise sur Head/
    Right Leg/Left Leg). Insertion d'UNE keyframe juste avant et juste
    apres chacun de ces 4 points, par interpolation smoothstep (pas
    lineaire) -- voir _ease_kf : approxime une entree/sortie adoucie
    avec des segments toujours droits (VECTOR reste utilise partout,
    donc le jerk intra-segment nul du cycle 2 est preserve par
    construction), en reduisant la taille du saut de direction concentre
    exactement sur ces 4 keyframes.

    Cycles 3 et 4 avaient deja tente d'ajouter des keyframes ou de
    melanger les types de tangente -- tous deux ont fait PIRE que cycle 2
    (65.4 et 62.9). Ceci teste une derniere variable non essayee : garder
    VECTOR partout (l'ingredient qui a fonctionne) et seulement densifier
    intelligemment le voisinage des sommets (l'ingredient qui n'avait pas
    encore ete essaye EN COMBINAISON avec VECTOR)."""
    keyframes, phases, preview_times, _ = cycle_1()
    by_time = {round(k["time"], 5): k for k in keyframes}
    apex_times = [0.62, 1.16, 1.66, 1.86]
    offset = 0.10

    extra = []
    sorted_times = sorted(by_time.keys())
    for apex in apex_times:
        idx = sorted_times.index(apex)
        prev_t, next_t = sorted_times[idx - 1], sorted_times[idx + 1]
        k_prev, k_apex, k_next = by_time[prev_t], by_time[apex], by_time[next_t]
        t_before = max(prev_t + 0.02, apex - offset)
        t_after = min(next_t - 0.02, apex + offset)
        extra.append(_ease_kf(k_prev, k_apex, t_before, ease=True))
        extra.append(_ease_kf(k_apex, k_next, t_after, ease=True))

    new_keyframes = sorted(keyframes + extra, key=lambda k: k["time"])
    engine_opts = {"handle_type": "VECTOR"}
    return new_keyframes, phases, preview_times, engine_opts


def cycle_6():
    """Cycle 6 -- HAUT DU CORPS ACTIF : le combo est rejoue avec la
    mecanique reelle du taekwondo, ou le haut du corps ne suit pas le
    mouvement mais le PRODUIT. Jambes et timing inchanges par rapport au
    cycle 2 ; tout ce qui change est tete, bras et l'accompagnement du
    torse.

    Trois mecaniques reelles encodees, chacune mesuree par
    measure.taekwondo_signature() :

    1. SPOTTING (la signature la plus reconnaissable). Sur un coup
       retourne, on tourne la TETE en premier, on fixe la cible par-dessus
       l'epaule, puis le corps suit, la jambe arrive en dernier. Ici la
       tete part a -55 deg des 0.88 s alors que le torse n'a tourne que de
       40 deg, puis se "devisse" (revient vers 0 relatif) a mesure que le
       torse la rattrape a 1.16.

    2. FERMETURE DES BRAS pendant la vrille. Un patineur accelere sa
       rotation en ramenant les bras : conservation du moment cinetique.
       Les deux bras se replient sur la poitrine au pic de vitesse
       (Z = -75 / +75, mains a l'axe), puis s'ouvrent en grand pour
       freiner a la sortie du coup.

    3. COUPLAGE CONTRALATERAL. Le bras OPPOSE a la jambe qui frappe part
       en avant, celui du meme cote tire en arriere -- c'est le schema
       croise naturel de tout geste athletique. Kick 1 = jambe droite,
       donc bras gauche devant, bras droit qui tire.

    Garde : mains devant la poitrine au depart, entre les coups et a
    l'arrivee, jamais bras ballants. Cela reste conforme a la contrainte
    "aucun coup de poing" : aucune DETENTE de bras (allonge + vitesse
    d'extension) -- voir measure.no_punch_thrust, qui distingue une garde
    d'un direct par la vitesse et non par la pose."""
    keyframes = [
        _kf(0.00,
            **{"Right Arm": (55, 0, -28), "Left Arm": (55, 0, 28)}),

        # Anticipation : garde qui se resserre, tete qui cherche deja la cible.
        _kf(0.18, root_pos=(0, -0.35, 0), Torso=(-10, 0, 0), Head=(4, -12, 0),
            **{"Right Leg": (-8, 0, 0), "Left Leg": (-8, 0, 0),
               "Right Arm": (62, 0, -34), "Left Arm": (62, 0, 34)}),

        # Impulsion : les bras fouettent vers le haut (ils tirent le corps
        # en l'air, mecanique reelle d'un saut), tete verrouillee sur la cible.
        _kf(0.36, root_pos=(0, 0.9, 0), Torso=(6, 0, 0), Head=(2, -22, 0),
            **{"Right Leg": (-25, 0, 0), "Left Leg": (5, 0, 0),
               "Right Arm": (-55, 0, -20), "Left Arm": (-40, 0, 30)}),

        # KICK 1 -- croissant jambe DROITE. Couplage contralateral : le bras
        # GAUCHE part devant/en travers, le bras DROIT tire en arriere.
        _kf(0.62, root_pos=(0.3, 1.35, 0.1), HumanoidRootPart=(0, -18, 6),
            Torso=(10, -22, 10), Head=(6, -16, -4),
            **{"Right Leg": (55, 35, 95), "Left Leg": (-15, 0, -10),
               "Right Arm": (-42, 0, 38), "Left Arm": (68, 0, 46)}),

        # Liaison : les bras commencent a se refermer, et surtout la TETE
        # part en avance sur la vrille (-55 alors que le torse n'est qu'a 40).
        _kf(0.88, root_pos=(0.1, 1.25, -0.1), HumanoidRootPart=(0, 55, -4),
            Torso=(2, 40, -6), Head=(0, 55, 0),
            **{"Right Leg": (0, 20, 15), "Left Leg": (-20, 10, -20),
               "Right Arm": (25, 0, -58), "Left Arm": (30, 0, 52)}),

        # KICK 2 -- retourne. Bras replies au maximum (pic de vitesse de
        # vrille), tete presque devissee : le corps l'a rattrapee.
        _kf(1.16, root_pos=(-0.2, 1.55, -0.15), HumanoidRootPart=(0, 150, -10),
            Torso=(-8, 170, -14), Head=(0, 12, 0),
            **{"Right Leg": (-10, 0, -25), "Left Leg": (30, -40, -100),
               "Right Arm": (40, 0, -78), "Left Arm": (38, 0, 74)}),

        # Sortie de vrille : les bras s'OUVRENT en grand pour freiner la
        # rotation (l'inverse exact de la fermeture).
        _kf(1.42, root_pos=(0, 1.4, 0), HumanoidRootPart=(0, 195, 0),
            Torso=(15, 195, 0), Head=(-8, -18, 0),
            **{"Right Leg": (10, 0, 0), "Left Leg": (-5, 0, 0),
               "Right Arm": (5, 0, 68), "Left Arm": (0, 0, -62)}),

        # KICK 3 -- ciseaux. Corps a l'horizontale : un bras cherche le sol
        # (appui visuel facon capoeira), l'autre contrebalance haut.
        _kf(1.66, root_pos=(0, 1.2, 0.25), HumanoidRootPart=(35, 200, 0),
            Torso=(65, 200, 0), Head=(-34, 0, 0),
            **{"Right Leg": (55, 0, 0), "Left Leg": (-50, 0, 0),
               "Right Arm": (-25, 0, 72), "Left Arm": (40, 0, -30)}),

        # Snap des ciseaux : les bras inversent avec les jambes.
        _kf(1.86, root_pos=(0, 1.0, 0.1), HumanoidRootPart=(20, 200, 0),
            Torso=(45, 200, 0), Head=(-24, 0, 0),
            **{"Right Leg": (-45, 0, 0), "Left Leg": (50, 0, 0),
               "Right Arm": (35, 0, 40), "Left Arm": (-20, 0, -55)}),

        # Rassemblement, retour face -Z, la garde se reforme.
        _kf(2.05, root_pos=(0, 0.5, 0), HumanoidRootPart=(0, 20, 0),
            Torso=(5, 20, 0), Head=(0, -10, 0),
            **{"Right Leg": (0, 0, 0), "Left Leg": (0, 0, 0),
               "Right Arm": (48, 0, -30), "Left Arm": (48, 0, 30)}),

        # Atterrissage absorbe, garde tenue.
        _kf(2.20, root_pos=(0, -0.15, 0), Torso=(-12, 0, 0), Head=(5, 0, 0),
            **{"Right Leg": (-5, 0, 0), "Left Leg": (-5, 0, 0),
               "Right Arm": (58, 0, -32), "Left Arm": (58, 0, 32)}),

        # Repos : garde d'ouverture, identique a t=0 (boucle propre).
        _kf(2.36,
            **{"Right Arm": (55, 0, -28), "Left Arm": (55, 0, 28)}),
    ]

    phases = [
        {"name": "anticipation", "t0": 0.00, "t1": 0.36, "expected_reversals": {}},
        {"name": "kick1_croissant", "t0": 0.36, "t1": 0.88, "expected_reversals": {}},
        {"name": "kick2_retourne", "t0": 0.88, "t1": 1.42, "expected_reversals": {}},
        {"name": "kick3_ciseaux", "t0": 1.42, "t1": 2.05,
         "expected_reversals": {"Right Leg": 1, "Left Leg": 1}},
        {"name": "atterrissage", "t0": 2.05, "t1": 2.36, "expected_reversals": {}},
    ]
    preview_times = [0.0, 0.36, 0.62, 0.88, 1.16, 1.66, 2.36]
    engine_opts = {"handle_type": "VECTOR"}
    return keyframes, phases, preview_times, engine_opts


def cycle_7():
    """Cycle 7 -- recreation d'une reference video fournie par l'utilisateur
    (capture d'ecran Roblox Studio/Moon Animator, "Linear Easing Test" par
    EclipseThemDev, rig R6, meme contrainte 6-segments-rigides que ce
    projet). Video decodee via ffmpeg (imageio-ffmpeg, pas de systeme
    ffmpeg/libva utilisable ici -- voir note dans le rapport), 22
    extractions a haute resolution entre t=0.00 et t=1.70s pour lire la
    pose corps par corps.

    RECREATION, pas reproduction pixel-exacte : je n'ai pas les courbes
    sources (fichier Moon Animator propietaire, non fourni), seulement
    l'image. Ce qui est repris est la STRUCTURE et le TIMING du mouvement
    lus sur les captures ; les valeurs d'angle sont les miennes. Les VFX de
    la reference (trainee lumineuse le long de la jambe, anneau de
    choc au sol, eclats a l'impact) ne sont PAS recreees -- ce pipeline
    exporte un KeyframeSequence (animation de corps uniquement), pas des
    ParticleEmitter/Beam ; ce serait un travail separe, cote Studio.

    Structure lue sur les captures (t en secondes, video source) :
      0.00-0.20  fente profonde (lunge) : torse penche en avant, jambe
                 arriere tendue en arriere, bras qui trainent -- charge
                 avant l'impulsion, flash d'impact au pied vers 0.20.
      0.20-0.90  jambe qui monte de la hanche jusqu'a la quasi-verticale,
                 A L'AVANT du corps (verifie sur t=0.30 : trainee devant
                 le torse, pas derriere), torse qui bascule en arriere en
                 contrepoids -- TENUE en l'air de 0.60 a 0.90 (hang-time
                 marque, pas un pic instantane).
      0.90-1.30  la jambe redescend, corps se ramasse en crouch bas et
                 compact -- chargement du spin.
      1.30-1.50  liberation rapide en spin (eclats/traits de vitesse sur
                 les captures), tres bref (~0.2s reel).
      1.50-1.70  retour a une posture debout neutre.

    Reproduit ici avec le moteur du projet (hanche+bassin-root, jamais de
    pli de jambe inexistant, jamais de coup de poing -- verifie comme
    toujours par measure.no_punch_thrust) : jambe DROITE pour la montee
    tenue, jambe GAUCHE pour le spin (asymetrie deliberee, cf. la garde
    asymetrique jamais faite au cycle 6)."""
    keyframes = [
        _kf(0.00,
            **{"Right Arm": (50, 0, -25), "Left Arm": (50, 0, 25)}),

        # Fente profonde : torse tres penche en avant, jambe arriere
        # tendue, bras qui trainent en arriere (contrepoids du sprinteur).
        _kf(0.10, root_pos=(0, -0.55, 0.05), Torso=(-38, 0, 0), Head=(18, 0, 0),
            **{"Right Leg": (-52, 0, 8), "Left Leg": (22, 0, -6),
               "Right Arm": (-68, 0, -18), "Left Arm": (-62, 0, 22)}),

        # Impulsion : le corps commence a se redresser et a monter.
        _kf(0.22, root_pos=(0, 0.35, 0.02), Torso=(-8, 8, -10),
            **{"Right Leg": (-70, 20, 18), "Left Leg": (8, 0, -10),
               "Right Arm": (-28, 0, -42), "Left Arm": (18, 0, 32)}),

        # La jambe droite balaie vers le haut, A L'AVANT du corps.
        _kf(0.42, root_pos=(0.05, 0.95, -0.05), Torso=(18, 12, -18), Head=(-12, 12, 0),
            **{"Right Leg": (100, 28, 22), "Left Leg": (-8, 0, -10),
               "Right Arm": (-18, 0, -55), "Left Arm": (30, 0, 42)}),

        # TENUE en l'air -- hang-time marque (0.60 a 0.90 dans la reference).
        _kf(0.62, root_pos=(0.05, 1.45, -0.08), Torso=(24, 16, -12), Head=(-18, 16, 0),
            **{"Right Leg": (158, 26, 16), "Left Leg": (-6, 0, -8),
               "Right Arm": (-14, 0, -58), "Left Arm": (36, 0, 46)}),

        # Deuxieme point de tenue, quasi identique -- une derive minime pour
        # eviter un segment degenere, pas une vraie deuxieme pose.
        _kf(0.86, root_pos=(0.03, 1.42, -0.06), Torso=(23, 17, -11), Head=(-16, 17, 0),
            **{"Right Leg": (161, 27, 16), "Left Leg": (-7, 0, -8),
               "Right Arm": (-16, 0, -57), "Left Arm": (35, 0, 45)}),

        # La jambe redescend, le corps entame le ramasse.
        _kf(1.02, root_pos=(0, 0.65, 0), Torso=(2, 8, -3),
            **{"Right Leg": (55, 12, 8), "Left Leg": (-14, 0, -5),
               "Right Arm": (10, 0, -20), "Left Arm": (14, 0, 18)}),

        # Crouch bas, compact -- chargement du spin (bras ramenes au corps,
        # meme mecanique de fermeture que le cycle 6).
        _kf(1.22, root_pos=(0, -0.28, 0), Torso=(-16, 3, 0), Head=(6, -10, 0),
            **{"Right Leg": (-14, 0, 4), "Left Leg": (-20, 0, -6),
               "Right Arm": (48, 0, -38), "Left Arm": (48, 0, 38)}),

        # SPIN -- liberation rapide (jambe gauche), corps qui tourne vite.
        _kf(1.36, root_pos=(0, 0.28, 0.05), HumanoidRootPart=(0, -130, 10),
            Torso=(8, -110, 14), Head=(0, -95, 0),
            **{"Left Leg": (28, 22, -68), "Right Leg": (-10, 0, 8),
               "Right Arm": (-28, 0, 58), "Left Arm": (-18, 0, -48)}),

        # Pic du spin -- extension maximale de la jambe gauche.
        _kf(1.48, root_pos=(0, 0.32, 0.05), HumanoidRootPart=(0, -250, 5),
            Torso=(3, -240, 8), Head=(0, -35, 0),
            **{"Left Leg": (65, 15, -135), "Right Leg": (-5, 0, 5),
               "Right Arm": (-12, 0, 74), "Left Arm": (-8, 0, -60)}),

        # La jambe se rassemble, le corps a fini l'essentiel du tour.
        _kf(1.58, root_pos=(0, 0.10, 0), HumanoidRootPart=(0, -258, 0),
            Torso=(-4, -252, 0),
            **{"Left Leg": (18, 4, -35), "Right Leg": (-6, 0, 3)}),

        # Pivot correctif d'atterrissage -- retour face -Z (comme au
        # cycle 6 apres le kick2 : un vrai athlete re-cale son appui apres
        # un spin, ce n'est jamais instantane).
        _kf(1.75, root_pos=(0, -0.12, 0), HumanoidRootPart=(0, -30, 0),
            Torso=(-6, -30, 0), Head=(4, 0, 0),
            **{"Right Leg": (-6, 0, 4), "Left Leg": (-6, 0, -4),
               "Right Arm": (55, 0, -30), "Left Arm": (55, 0, 30)}),

        # Repos, garde tenue, boucle propre.
        _kf(1.92,
            **{"Right Arm": (50, 0, -25), "Left Arm": (50, 0, 25)}),
    ]

    phases = [
        {"name": "anticipation", "t0": 0.00, "t1": 0.22, "expected_reversals": {}},
        {"name": "montee_tenue", "t0": 0.22, "t1": 1.02, "expected_reversals": {}},
        {"name": "ramasse", "t0": 1.02, "t1": 1.36, "expected_reversals": {}},
        {"name": "spin", "t0": 1.36, "t1": 1.75, "expected_reversals": {}},
        {"name": "atterrissage", "t0": 1.75, "t1": 1.92, "expected_reversals": {}},
    ]
    preview_times = [0.0, 0.10, 0.42, 0.62, 1.22, 1.48, 1.92]
    engine_opts = {"handle_type": "VECTOR"}
    return keyframes, phases, preview_times, engine_opts


def cycle_8():
    """Cycle 8 -- deuxieme passe sur la reference video du cycle 7, apres
    une mesure BEAUCOUP plus rigoureuse : extraction native (108 frames,
    ~58.4 fps reelles, imageio-ffmpeg) au lieu des 22 captures ponctuelles
    du cycle 7, mesure de coordonnees pixel (pas d'estimation a l'oeil) sur
    des crops agrandis avec grille de reference, calage temporel a la
    frame video pres.

    CORRECTION STRUCTURELLE trouvee par cette mesure plus fine (invisible
    a la densite du cycle 7) : la jambe ne fait PAS une seule montee
    continue tenue en l'air. Elle fait DEUX montees distinctes :
      - kick 1, t=0.086-0.308 : montee rapide, PAS tenue
      - creux, t=0.308-0.462 : redescend, corps se redresse brievement
      - kick 2, t=0.462-0.908 : remonte plus haut, CETTE fois tenue
        (hang-time 0.616-0.908, ~0.3s -- confirme, present aussi au
        cycle 7 mais attribue par erreur a une seule montee ininterrompue)

    Plafond de la methode, atteint et documente plutot que contourne en
    silence (voir echange avec l'utilisateur) : sur les frames avec flash
    d'impact (ex. t=0.086), les aretes de plusieurs membres se chevauchent
    au point qu'on ne peut PAS determiner avec certitude quelle arete
    appartient a quel segment -- ce n'est pas resolu par plus de zoom. Et
    une camera fixe unique ne distingue pas un membre qui pointe VERS la
    camera d'un membre qui pointe a l'oppose (silhouette 2D identique) --
    ambiguite de profondeur monoculaire, pas un manque de rigueur.
    Consequence assumee : le calage temporel des 16 temps forts ci-dessous
    est mesure a la frame pres (objectif, non ambigu) ; les angles de la
    jambe active reprennent l'ordre de grandeur du cycle 7 (deja informe
    par la meme lecture visuelle) plutot qu'une nouvelle inversion
    camera-par-membre qui n'aurait pas convergé mieux que ca sur les
    frames a VFX ; torse/bras/tete suivent la meme mecanique que cycle 7
    (contrepoids, fermeture pendant le spin), retimes sur la nouvelle
    structure a deux montees.

    16 temps forts mesures (t en secondes, video source, 108 frames a
    ~58.4 fps) :
      0.000-0.086  fente immobile (aucun mouvement mesure sur 6 frames)
      0.086        flash d'impact, lancement
      0.188        kick 1 -- pic (PAS tenu, redescend aussitot)
      0.308-0.445  creux -- la jambe redescend, corps se redresse
      0.462        relance vers kick 2
      0.616-0.908  kick 2 -- tenu (hang-time confirme sur 17 frames a
                   58.4 fps, ~0.3s reel)
      0.925-1.010  la jambe redescend
      1.010-1.216  ramasse bas, compact
      1.318        lancement du spin
      1.370        pic du spin (rafale de pixels sur les captures)
      1.421        fin de la rotation rapide
      1.438-1.524  jambe qui se replie, anneau au sol
      1.541-1.729  posture d'atterrissage tenue (17 frames stables)
      1.747+       transition vers la position debout (segment grand-angle)
    """
    keyframes = [
        _kf(0.00,
            **{"Right Arm": (50, 0, -25), "Left Arm": (50, 0, 25)}),

        # Fente, immobile 0.000-0.086 (aucun changement mesure sur les
        # 6 premieres frames video).
        _kf(0.086, root_pos=(0, -0.55, 0.05), Torso=(-38, 0, 0), Head=(18, 0, 0),
            **{"Right Leg": (-52, 0, 8), "Left Leg": (22, 0, -6),
               "Right Arm": (-68, 0, -18), "Left Arm": (-62, 0, 22)}),

        # KICK 1 -- montee rapide, non tenue.
        _kf(0.188, root_pos=(0.02, 0.55, -0.02), Torso=(6, 6, -8),
            **{"Right Leg": (108, 15, 12), "Left Leg": (0, 0, -8),
               "Right Arm": (-22, 0, -35), "Left Arm": (22, 0, 28)}),

        # CREUX -- redescend, corps se redresse (trouve par la mesure
        # fine, absent du cycle 7).
        _kf(0.40, root_pos=(0, 0.55, 0), Torso=(2, 4, -2),
            **{"Right Leg": (18, 5, 2), "Left Leg": (-6, 0, -4),
               "Right Arm": (5, 0, -10), "Left Arm": (10, 0, 10)}),

        # Relance vers kick 2.
        _kf(0.50, root_pos=(0.03, 0.85, -0.05), Torso=(15, 10, -14), Head=(-10, 12, 0),
            **{"Right Leg": (70, 20, 18), "Left Leg": (-6, 0, -8),
               "Right Arm": (-16, 0, -48), "Left Arm": (28, 0, 38)}),

        # KICK 2 -- montee au pic, tenue.
        _kf(0.62, root_pos=(0.05, 1.45, -0.08), Torso=(24, 16, -12), Head=(-18, 16, 0),
            **{"Right Leg": (158, 26, 16), "Left Leg": (-6, 0, -8),
               "Right Arm": (-14, 0, -58), "Left Arm": (36, 0, 46)}),

        # Toujours tenu -- derive minime pour eviter un segment degenere.
        _kf(0.86, root_pos=(0.03, 1.42, -0.06), Torso=(23, 17, -11), Head=(-16, 17, 0),
            **{"Right Leg": (161, 27, 16), "Left Leg": (-7, 0, -8),
               "Right Arm": (-16, 0, -57), "Left Arm": (35, 0, 45)}),

        # La jambe redescend.
        _kf(1.01, root_pos=(0, 0.65, 0), Torso=(2, 8, -3),
            **{"Right Leg": (55, 12, 8), "Left Leg": (-14, 0, -5),
               "Right Arm": (10, 0, -20), "Left Arm": (14, 0, 18)}),

        # Ramasse bas, compact -- chargement du spin.
        _kf(1.22, root_pos=(0, -0.28, 0), Torso=(-16, 3, 0), Head=(6, -10, 0),
            **{"Right Leg": (-14, 0, 4), "Left Leg": (-20, 0, -6),
               "Right Arm": (48, 0, -38), "Left Arm": (48, 0, 38)}),

        # SPIN -- lancement.
        _kf(1.318, root_pos=(0, 0.28, 0.05), HumanoidRootPart=(0, -130, 10),
            Torso=(8, -110, 14), Head=(0, -95, 0),
            **{"Left Leg": (28, 22, -68), "Right Leg": (-10, 0, 8),
               "Right Arm": (-28, 0, 58), "Left Arm": (-18, 0, -48)}),

        # Pic du spin -- extension maximale de la jambe gauche.
        _kf(1.37, root_pos=(0, 0.32, 0.05), HumanoidRootPart=(0, -250, 5),
            Torso=(3, -240, 8), Head=(0, -35, 0),
            **{"Left Leg": (65, 15, -135), "Right Leg": (-5, 0, 5),
               "Right Arm": (-12, 0, 74), "Left Arm": (-8, 0, -60)}),

        # Fin de la rotation rapide -- la jambe se rassemble, les bras
        # commencent a se refermer (pas encore la garde -- voir point
        # intermediaire suivant).
        _kf(1.421, root_pos=(0, 0.10, 0), HumanoidRootPart=(0, -258, 0),
            Torso=(-4, -252, 0),
            **{"Left Leg": (18, 4, -35), "Right Leg": (-6, 0, 3),
               "Right Arm": (10, 0, 30), "Left Arm": (5, 0, -22)}),

        # Point intermediaire -- ralentit le retour des bras vers la garde
        # (trouve en corrigeant un vrai bug : le retour direct 1.421->1.55
        # faisait passer brièvement l'allonge+detente au-dessus du
        # seuil "aucun coup de poing" pendant 1 echantillon sur 120/s,
        # cf. no_punch_thrust -- un vrai artefact de vitesse, pas une
        # fausse alerte).
        _kf(1.49, root_pos=(0, -0.02, 0), HumanoidRootPart=(0, -35, 0),
            Torso=(-5, -35, 0),
            **{"Right Leg": (-3, 0, 3), "Left Leg": (-3, 0, -3),
               "Right Arm": (32, 0, 0), "Left Arm": (28, 0, 0)}),

        # Pivot correctif d'atterrissage -- retour face -Z. Amplitude bras
        # volontairement retenue ici (45 et non 55) : le segment precedent
        # (1.49) est court (0.06s) et une cible trop haute y faisait
        # repasser brièvement au-dessus du seuil no_punch_thrust --
        # la garde complete est atteinte juste apres, au point suivant.
        _kf(1.55, root_pos=(0, -0.12, 0), HumanoidRootPart=(0, -30, 0),
            Torso=(-6, -30, 0), Head=(4, 0, 0),
            **{"Right Leg": (-6, 0, 4), "Left Leg": (-6, 0, -4),
               "Right Arm": (45, 0, -15), "Left Arm": (45, 0, 15)}),

        # Posture d'atterrissage TENUE (17 frames stables mesurees,
        # 1.541-1.729) -- derive minime pour eviter un segment degenere.
        _kf(1.73, root_pos=(0, -0.10, 0), HumanoidRootPart=(0, -28, 0),
            Torso=(-5, -28, 0), Head=(3, 0, 0),
            **{"Right Leg": (-5, 0, 3), "Left Leg": (-5, 0, -3),
               "Right Arm": (53, 0, -29), "Left Arm": (53, 0, 29)}),

        # Transition vers la position debout.
        _kf(1.85, root_pos=(0, -0.02, 0), HumanoidRootPart=(0, -6, 0),
            Torso=(-1, -6, 0),
            **{"Right Leg": (-2, 0, 1), "Left Leg": (-2, 0, -1),
               "Right Arm": (52, 0, -26), "Left Arm": (52, 0, 26)}),

        # Repos, garde tenue, boucle propre.
        _kf(1.95,
            **{"Right Arm": (50, 0, -25), "Left Arm": (50, 0, 25)}),
    ]

    phases = [
        {"name": "anticipation", "t0": 0.00, "t1": 0.086, "expected_reversals": {}},
        {"name": "kick1", "t0": 0.086, "t1": 0.40, "expected_reversals": {}},
        {"name": "kick2_tenu", "t0": 0.40, "t1": 1.01, "expected_reversals": {}},
        {"name": "ramasse", "t0": 1.01, "t1": 1.318, "expected_reversals": {}},
        {"name": "spin", "t0": 1.318, "t1": 1.55, "expected_reversals": {}},
        {"name": "atterrissage", "t0": 1.55, "t1": 1.95, "expected_reversals": {}},
    ]
    preview_times = [0.0, 0.086, 0.188, 0.40, 0.62, 1.22, 1.37, 1.73, 1.95]
    engine_opts = {"handle_type": "VECTOR"}
    return keyframes, phases, preview_times, engine_opts


CYCLES = {1: cycle_1, 2: cycle_2, 3: cycle_3, 4: cycle_4, 5: cycle_5, 6: cycle_6, 7: cycle_7, 8: cycle_8}
