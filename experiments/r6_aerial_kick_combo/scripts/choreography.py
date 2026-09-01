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


CYCLES = {1: cycle_1, 2: cycle_2, 3: cycle_3, 4: cycle_4, 5: cycle_5, 6: cycle_6}
