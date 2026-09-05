"""
Combo de 3 coups (jab gauche -> cross droit -> hook gauche) sur un
mannequin, deux rigs R6 independants (meme principe que
r6_directional_punch : un attaquant + un mannequin, chronologie commune).

Demande utilisateur explicite : "Fais une nvl animation de combo de hit
avec VFX texturing inspire toi des refs que je t'ai envoye sois encore
plus fluide je veux pas du saccade du chelou et enfin fais Camera de
loin qui montre la scene en entierete."

Consequence directe sur la chronologie : contrairement a
r6_directional_punch (une longue charge de ~1,25s avant UN coup), un
combo n'a PAS de temps mort entre les coups -- chaque retour de bras
DEVIENT l'amorce du coup suivant (le buste qui se re-tord dans l'autre
sens pendant que la main revient sert de windup au coup suivant), pour
eviter tout arret qui lirait comme "saccade". Chaque coup individuel
reutilise la lecon apprise sur r6_directional_punch (retour utilisateur
+ recherche) : la fenetre HIP_DRIVE_T -> IMPACT_T (chaine cinetique ->
lacher) est un vrai SNAP D'UNE SEULE FRAME (1/30s, le OUT_HZ de
dump_scene_data.py) -- jamais 3-5 frames intermediaires (= effet "pale
de moulin" sur un bras rigide sans coude, cause identifiee la derniere
fois).

Meme convention d'axes que r6_directional_punch (verifiee, pas
resupposee) :
  - Torso/Head/jambes : X positif = penche/tourne vers l'AVANT.
  - Right/Left Arm : X positif = part vers l'avant (-Z) puis monte
    par-dessus jusqu'a X=180 (au-dessus de la tete). X=90 = horizontale,
    droit devant. X negatif = derriere le corps.
  - Torso Y (torsion) : Y POSITIF fait pivoter l'EPAULE DROITE VERS
    L'AVANT (donc l'epaule GAUCHE vers l'arriere) -- Y negatif fait
    l'inverse (epaule gauche en avant). Un jab gauche "lache" donc sur Y
    NEGATIF (epaule gauche projetee en avant), un cross droit sur Y
    POSITIF -- exactement l'inverse l'un de l'autre, ce qui fait que le
    buste OSCILLE d'un cote a l'autre a chaque coup, jamais un aller
    simple : c'est cette oscillation, pas des pauses, qui enchaine les
    coups sans a-coup.
  - Left Arm : X va dans le MEME sens que Right Arm (avant = -Z pour les
    deux bras, symetrie du rig) ; Z va dans le sens OPPOSE (deja etabli
    sur r6_throne_crown/r6_directional_punch -- "vers l'exterieur" du
    corps a un signe different pour chaque bras).
  - HumanoidRootPart Y=180 : personnage retourne, "devant" devient +Z --
    utilise pour le mannequin (place plus loin en -Z, doit faire face a
    l'attaquant).
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
ATTACKER_Z0 = -1.2
DUMMY_Z = -6.6
SNAP = 1 / 30  # une frame de sortie a 30 fps -- voir docstring de module

# -- Jeu de jambes : la racine (HumanoidRootPart, donc les hanches) NE
# BOUGEAIT JAMAIS en Y avant cette correction -- root_pos utilisait
# GROUND_Y partout, constant du debut a la fin, alors qu'un vrai coup de
# poing part des jambes (charge en flechissant, detente vers le haut/
# avant au lacher). Retour utilisateur : "le jeu du coup et des jambes
# c'est trop statique". Chaque coup CHARGE (creuse sous GROUND_Y pendant
# windup/coil, amplitude croissante jab<cross<hook, meme principe
# d'escalade que le VFX du lecteur) puis SE DETEND en remontant tout pres
# de GROUND_Y au moment du hip-drive -- et EXACTEMENT GROUND_Y a l'instant
# de l'impact (JAB_T/CROSS_T/HOOK_T) pour ne PAS decalibrer le contact
# deja mesure (calibrate.py) : seule la Y des frames INTERMEDIAIRES change.
JAB_DIP = 0.05
CROSS_DIP = 0.11
HOOK_DIP = 0.17

# -- Chronologie -- pas de temps mort entre les coups (retour utilisateur
# "encore plus fluide, pas de saccade") : chaque RETRACT sert de WINDUP
# au coup suivant, le buste passe directement d'une torsion a l'autre.
GARDE_T = 0.18
JAB_WINDUP_T = 0.34
JAB_HIPDRIVE_T = 0.46 - SNAP
JAB_T = 0.46
CROSS_WINDUP_T = 0.62      # = retour du jab qui devient l'armement du cross
CROSS_COIL_T = 0.80
CROSS_HIPDRIVE_T = 0.98 - SNAP
CROSS_T = 0.98
HOOK_WINDUP_T = 1.14       # = retour du cross qui devient l'armement du hook
HOOK_COIL_T = 1.34
HOOK_HIPDRIVE_T = 1.58 - SNAP
HOOK_T = 1.58
DURATION = HOOK_T + 1.05


def lerp3(a, b, f):
    return tuple(a[i] + f * (b[i] - a[i]) for i in range(3))


def lerp_legs(a, b, f):
    return {k: lerp3(a[k], b[k], f) for k in a}


# ---------------------------------------------------------------------
# Garde -- stance de combat alerte (pas la charge lente du direct du
# droit) : buste legerement penche en avant, poings deja hauts pres du
# visage, jambes deja flechies -- un combo part d'une garde prete, pas
# d'une pose neutre relachee.
_READY_TORSO = (5, 0, 0)
_READY_HEAD = (3, 0, 0)
_READY_LEGS = {"Right Leg": (5, 0, 7), "Left Leg": (7, 0, -6)}
_READY_ARMS = {"Right Arm": (62, 0, -10), "Left Arm": (66, 0, 12)}

# -- JAB (gauche) -- rapide, amplitude modeste (un jab ne charge pas
# loin), sert surtout a amorcer l'oscillation du buste pour le cross qui
# suit.
JAB_WINDUP_TORSO = (4, 9, 0)
JAB_WINDUP_HEAD = (3, 5, 0)
JAB_WINDUP_LEGS = {"Right Leg": (7, 0, 8), "Left Leg": (9, 0, -7)}
JAB_WINDUP_LEFT_ARM = (52, 0, 16)
JAB_WINDUP_RIGHT_ARM = (64, 0, -11)

JAB_STRIKE_TORSO = (-3, -15, 0)
JAB_STRIKE_HEAD = (5, -7, 0)
JAB_STRIKE_LEGS = {"Right Leg": (2, 0, 6), "Left Leg": (10, 0, -8)}
JAB_STRIKE_LEFT_ARM = (90, 0, 34)     # Z calibre par balayage numerique (0,493 stud, voir calibrate.py)
JAB_STRIKE_RIGHT_ARM = (58, 0, -12)
# Avancee calibree par mesure directe (calibrate.py), pas devinee : la
# premiere passe laissait 3,1 studs d'ecart (le mannequin est loin,
# Z=-6.6, contre une avancee de -0.55 seulement) -- corrige pour amener
# le poing pres du torse au moment de l'impact.
JAB_LUNGE_Z = -4.743

# Chaine cinetique du jab -- fraction reduite par rapport au cross/hook
# (un jab n'a pas besoin d'un runway de chaine cinetique aussi marque,
# c'est un coup rapide du bras plus que des hanches) : buste/jambes/
# racine a 85%, bras gauche (le jab) a seulement 25% -- le payload du
# snap final.
_JF_BODY, _JF_ARM = 0.85, 0.25
JAB_HIPDRIVE_TORSO = lerp3(JAB_WINDUP_TORSO, JAB_STRIKE_TORSO, _JF_BODY)
JAB_HIPDRIVE_HEAD = lerp3(JAB_WINDUP_HEAD, JAB_STRIKE_HEAD, _JF_BODY)
JAB_HIPDRIVE_LEGS = lerp_legs(JAB_WINDUP_LEGS, JAB_STRIKE_LEGS, _JF_BODY)
JAB_HIPDRIVE_LEFT_ARM = lerp3(JAB_WINDUP_LEFT_ARM, JAB_STRIKE_LEFT_ARM, _JF_ARM)
JAB_HIPDRIVE_RIGHT_ARM = lerp3(JAB_WINDUP_RIGHT_ARM, JAB_STRIKE_RIGHT_ARM, _JF_BODY)
JAB_HIPDRIVE_ROOT_Z = ATTACKER_Z0 + _JF_BODY * (JAB_LUNGE_Z - ATTACKER_Z0)

# -- CROSS (droit) -- meme mecanique de puissance que r6_directional_punch
# (chaine cinetique complete, buste dominant), retimee ici pour s'enchainer
# directement depuis le retour du jab. Les valeurs STRIKE_* sont les
# memes que celles calibrees dans r6_directional_punch (ecart de contact
# 0,366 stud verifie la-bas) -- reutilisees telles quelles, pas redevinees.
CROSS_WINDUP_TORSO = (6, 6, 1)      # le buste repart de la torsion du jab (Y negatif) vers l'autre sens
CROSS_WINDUP_HEAD = (5, 4, 0)
CROSS_WINDUP_LEGS = {"Right Leg": (9, 0, 9), "Left Leg": (10, 0, -7)}
CROSS_WINDUP_RIGHT_ARM = (-25, 0, -9)
CROSS_WINDUP_LEFT_ARM = (58, 0, 20)

CROSS_COIL_TORSO = (11, -28, 3)
CROSS_COIL_HEAD = (9, -18, 0)
# Jeu de jambes -- retour utilisateur ("les jambes c'est trop statique") :
# la jambe AVANT (Left, qui va planter/encaisser le transfert de poids)
# charge plus large (Z plus negatif) et la jambe ARRIERE (Right, qui va
# pousser/pivoter) charge plus fort en flexion (X plus grand) -- avant,
# les deux jambes bougeaient a peine entre le coil et le strike (6-8
# degres), ce qui ne lisait aucun vrai transfert de poids.
CROSS_COIL_LEGS = {"Right Leg": (19, 0, 16), "Left Leg": (20, 0, -14)}
CROSS_COIL_RIGHT_ARM = (-85, 0, -17)
CROSS_COIL_LEFT_ARM = (46, 0, 40)

CROSS_STRIKE_TORSO = (-8, 34, 0)
CROSS_STRIKE_HEAD = (10, 12, 0)
# Jambe arriere (Right) qui pousse/pivote : grand swing X (19 -> -18,
# 37 degres, contre 31 avant). Jambe avant (Left) qui plante sous le
# poids transfere : compression nette (20 -> 34) + leger pivot vers
# l'exterieur (Z -14 -> 2) au lieu de rester quasi immobile.
CROSS_STRIKE_LEGS = {"Right Leg": (-18, 0, 10), "Left Leg": (34, 0, 2)}
CROSS_STRIKE_RIGHT_ARM = (90, 0, -4)
CROSS_STRIKE_LEFT_ARM = (10, 0, -18)
# Idem jab : calibre par mesure. Premiere valeur (-7.109) etait FAUSSE --
# calculee a partir d'une mesure contaminee par le secondary motion actif
# depuis JAB_T (voir plus bas), qui perturbait deja legerement la pose du
# cross a son propre instant d'impact. Recalcule PROPREMENT
# (secondary_motion=None pendant la mesure) une fois le t_min corrige.
CROSS_LUNGE_Z = -4.6513

_CF_BODY, _CF_ARM = 0.92, 0.20
CROSS_HIPDRIVE_TORSO = lerp3(CROSS_COIL_TORSO, CROSS_STRIKE_TORSO, _CF_BODY)
CROSS_HIPDRIVE_HEAD = lerp3(CROSS_COIL_HEAD, CROSS_STRIKE_HEAD, _CF_BODY)
CROSS_HIPDRIVE_LEGS = lerp_legs(CROSS_COIL_LEGS, CROSS_STRIKE_LEGS, _CF_BODY)
CROSS_HIPDRIVE_RIGHT_ARM = lerp3(CROSS_COIL_RIGHT_ARM, CROSS_STRIKE_RIGHT_ARM, _CF_ARM)
CROSS_HIPDRIVE_LEFT_ARM = lerp3(CROSS_COIL_LEFT_ARM, CROSS_STRIKE_LEFT_ARM, 0.85)
CROSS_HIPDRIVE_ROOT_Z = ATTACKER_Z0 + _CF_BODY * (CROSS_LUNGE_Z - ATTACKER_Z0)

# -- HOOK (gauche) -- le finisher : pas un coup droit mais un balayage
# lateral (Z, pas seulement X) porte par une GRANDE rotation du buste --
# lecture visuelle differente du cross (qui "pousse" tout droit, le hook
# "balaie" autour). Amplitude la plus grande du combo, VFX les plus
# lourds (voir le lecteur).
HOOK_WINDUP_TORSO = (8, -22, -2)     # repart de la torsion du cross (Y positif) vers l'autre sens
HOOK_WINDUP_HEAD = (6, -12, 0)
HOOK_WINDUP_LEGS = {"Right Leg": (12, 0, 10), "Left Leg": (14, 0, -9)}
# Convention (docstring de module) : Z bras GAUCHE negatif = vers
# l'EXTERIEUR du corps, positif = vers l'INTERIEUR (croise). Un hook se
# charge large vers l'exterieur (Z tres negatif) puis BALAYE vers
# l'interieur en frappant (Z devient positif a l'impact) -- c'est cet
# arc lateral, pas une simple extension en X, qui distingue le hook du
# jab/cross (tous deux des coups droits).
HOOK_WINDUP_LEFT_ARM = (70, 0, -50)
HOOK_WINDUP_RIGHT_ARM = (30, 0, -14)

HOOK_COIL_TORSO = (14, -40, -4)
HOOK_COIL_HEAD = (9, -24, 0)
HOOK_COIL_LEGS = {"Right Leg": (20, 0, 18), "Left Leg": (24, 0, -18)}
HOOK_COIL_LEFT_ARM = (78, 0, -78)
HOOK_COIL_RIGHT_ARM = (26, 0, -16)

HOOK_STRIKE_TORSO = (-10, 46, 2)
HOOK_STRIKE_HEAD = (12, 22, 0)
# Le hook pivote sur la jambe AVANT (Left, meme cote que le bras qui
# frappe) : le pied tourne vers l'interieur pendant que la hanche
# balaie -- Left Leg Z fait donc un grand swing (-18 -> 14, 32 degres,
# echo au bras dont le Z va de -78 a 91) au lieu de rester quasi fixe
# (-12 -> -6, 6 degres, avant correction). La jambe arriere (Right)
# suit la rotation de hanche.
HOOK_STRIKE_LEGS = {"Right Leg": (-20, 0, 16), "Left Leg": (34, 0, 14)}
HOOK_STRIKE_LEFT_ARM = (88, 0, 91)     # balaye de l'exterieur (Z negatif, charge) vers l'interieur (Z positif, croise sur la cible) -- Z calibre par balayage numerique (0,380 stud, voir calibrate.py), pas devine
HOOK_STRIKE_RIGHT_ARM = (18, 0, -20)
# Idem jab/cross : calibre par mesure PROPRE (secondary_motion=None).
HOOK_LUNGE_Z = CROSS_LUNGE_Z - 2.102

_HF_BODY, _HF_ARM = 0.90, 0.18
HOOK_HIPDRIVE_TORSO = lerp3(HOOK_COIL_TORSO, HOOK_STRIKE_TORSO, _HF_BODY)
HOOK_HIPDRIVE_HEAD = lerp3(HOOK_COIL_HEAD, HOOK_STRIKE_HEAD, _HF_BODY)
HOOK_HIPDRIVE_LEGS = lerp_legs(HOOK_COIL_LEGS, HOOK_STRIKE_LEGS, _HF_BODY)
HOOK_HIPDRIVE_LEFT_ARM = lerp3(HOOK_COIL_LEFT_ARM, HOOK_STRIKE_LEFT_ARM, _HF_ARM)
HOOK_HIPDRIVE_RIGHT_ARM = lerp3(HOOK_COIL_RIGHT_ARM, HOOK_STRIKE_RIGHT_ARM, _HF_BODY)
HOOK_HIPDRIVE_ROOT_Z = CROSS_LUNGE_Z + _HF_BODY * (HOOK_LUNGE_Z - CROSS_LUNGE_Z)

# -- Follow-through + pose finale (fiere, le combo est termine) --
OVERSHOOT_TORSO = (2, 58, 4)
OVERSHOOT_HEAD = (16, 26, 0)
OVERSHOOT_LEFT_ARM = (96, 0, -44)

RECOVER_TORSO = (-10, 10, 0)
RECOVER_HEAD = (-6, 4, 0)
RECOVER_LEFT_ARM = (30, 0, 12)
RECOVER_RIGHT_ARM = (34, 0, -14)

FINAL_TORSO = (-8, 0, 0)
FINAL_HEAD = (-6, 0, 0)


def attacker_combo():
    keyframes = [
        _kf(0.00, root_pos=(0, GROUND_Y, ATTACKER_Z0), Torso=_READY_TORSO, Head=_READY_HEAD,
            **_READY_LEGS, **_READY_ARMS),
        _kf(GARDE_T, root_pos=(0, GROUND_Y, ATTACKER_Z0), Torso=_READY_TORSO, Head=_READY_HEAD,
            **_READY_LEGS, **_READY_ARMS),

        # -- JAB -- (creuse un peu pendant le windup, remonte presque
        # entierement au hip-drive, pile GROUND_Y a l'impact)
        _kf(JAB_WINDUP_T, root_pos=(0, GROUND_Y - JAB_DIP * 0.4, ATTACKER_Z0), Torso=JAB_WINDUP_TORSO, Head=JAB_WINDUP_HEAD,
            **JAB_WINDUP_LEGS, **{"Left Arm": JAB_WINDUP_LEFT_ARM, "Right Arm": JAB_WINDUP_RIGHT_ARM}),
        _kf(JAB_HIPDRIVE_T, root_pos=(0, GROUND_Y - JAB_DIP * (1 - _JF_BODY), JAB_HIPDRIVE_ROOT_Z), Torso=JAB_HIPDRIVE_TORSO, Head=JAB_HIPDRIVE_HEAD,
            **JAB_HIPDRIVE_LEGS, **{"Left Arm": JAB_HIPDRIVE_LEFT_ARM, "Right Arm": JAB_HIPDRIVE_RIGHT_ARM}),
        _kf(JAB_T, root_pos=(0, GROUND_Y, JAB_LUNGE_Z), Torso=JAB_STRIKE_TORSO, Head=JAB_STRIKE_HEAD,
            **JAB_STRIKE_LEGS, **{"Left Arm": JAB_STRIKE_LEFT_ARM, "Right Arm": JAB_STRIKE_RIGHT_ARM}),

        # -- CROSS (le retour du jab EST l'armement du cross -- une seule
        # keyframe de transition, pas de pause) -- charge plus profond que
        # le jab (coup plus puissant), meme principe : creuse au windup/
        # coil, remonte au hip-drive, GROUND_Y pile a l'impact --
        _kf(CROSS_WINDUP_T, root_pos=(0, GROUND_Y - CROSS_DIP * 0.3, JAB_LUNGE_Z), Torso=CROSS_WINDUP_TORSO, Head=CROSS_WINDUP_HEAD,
            **CROSS_WINDUP_LEGS, **{"Right Arm": CROSS_WINDUP_RIGHT_ARM, "Left Arm": CROSS_WINDUP_LEFT_ARM}),
        _kf(CROSS_COIL_T, root_pos=(0, GROUND_Y - CROSS_DIP, JAB_LUNGE_Z), Torso=CROSS_COIL_TORSO, Head=CROSS_COIL_HEAD,
            **CROSS_COIL_LEGS, **{"Right Arm": CROSS_COIL_RIGHT_ARM, "Left Arm": CROSS_COIL_LEFT_ARM}),
        _kf(CROSS_HIPDRIVE_T, root_pos=(0, GROUND_Y - CROSS_DIP * (1 - _CF_BODY), CROSS_HIPDRIVE_ROOT_Z), Torso=CROSS_HIPDRIVE_TORSO, Head=CROSS_HIPDRIVE_HEAD,
            **CROSS_HIPDRIVE_LEGS, **{"Right Arm": CROSS_HIPDRIVE_RIGHT_ARM, "Left Arm": CROSS_HIPDRIVE_LEFT_ARM}),
        _kf(CROSS_T, root_pos=(0, GROUND_Y, CROSS_LUNGE_Z), Torso=CROSS_STRIKE_TORSO, Head=CROSS_STRIKE_HEAD,
            **CROSS_STRIKE_LEGS, **{"Right Arm": CROSS_STRIKE_RIGHT_ARM, "Left Arm": CROSS_STRIKE_LEFT_ARM}),

        # -- HOOK (finisher -- le retour du cross EST l'armement du hook)
        # -- la charge la plus profonde du combo (HOOK_DIP), le finisher
        # doit se lire comme le coup qui pousse le plus depuis le sol --
        _kf(HOOK_WINDUP_T, root_pos=(0, GROUND_Y - HOOK_DIP * 0.35, CROSS_LUNGE_Z), Torso=HOOK_WINDUP_TORSO, Head=HOOK_WINDUP_HEAD,
            **HOOK_WINDUP_LEGS, **{"Left Arm": HOOK_WINDUP_LEFT_ARM, "Right Arm": HOOK_WINDUP_RIGHT_ARM}),
        _kf(HOOK_COIL_T, root_pos=(0, GROUND_Y - HOOK_DIP, CROSS_LUNGE_Z), Torso=HOOK_COIL_TORSO, Head=HOOK_COIL_HEAD,
            **HOOK_COIL_LEGS, **{"Left Arm": HOOK_COIL_LEFT_ARM, "Right Arm": HOOK_COIL_RIGHT_ARM}),
        _kf(HOOK_HIPDRIVE_T, root_pos=(0, GROUND_Y - HOOK_DIP * (1 - _HF_BODY), HOOK_HIPDRIVE_ROOT_Z), Torso=HOOK_HIPDRIVE_TORSO, Head=HOOK_HIPDRIVE_HEAD,
            **HOOK_HIPDRIVE_LEGS, **{"Left Arm": HOOK_HIPDRIVE_LEFT_ARM, "Right Arm": HOOK_HIPDRIVE_RIGHT_ARM}),
        _kf(HOOK_T, root_pos=(0, GROUND_Y, HOOK_LUNGE_Z), Torso=HOOK_STRIKE_TORSO, Head=HOOK_STRIKE_HEAD,
            **HOOK_STRIKE_LEGS, **{"Left Arm": HOOK_STRIKE_LEFT_ARM, "Right Arm": HOOK_STRIKE_RIGHT_ARM}),

        # -- follow-through + pose finale -- leger rebond vers le HAUT
        # juste apres l'impact (le corps continue de monter/avancer sur
        # sa lancee, plutot que de retomber platement a GROUND_Y), puis
        # redescend en se stabilisant --
        _kf(HOOK_T + 0.08, root_pos=(0, GROUND_Y + 0.05, HOOK_LUNGE_Z - 0.2), Torso=OVERSHOOT_TORSO, Head=OVERSHOOT_HEAD,
            **HOOK_STRIKE_LEGS, **{"Left Arm": OVERSHOOT_LEFT_ARM, "Right Arm": HOOK_STRIKE_RIGHT_ARM}),
        _kf(HOOK_T + 0.45, root_pos=(0, GROUND_Y, HOOK_LUNGE_Z), Torso=RECOVER_TORSO, Head=RECOVER_HEAD,
            **HOOK_STRIKE_LEGS, **{"Left Arm": RECOVER_LEFT_ARM, "Right Arm": RECOVER_RIGHT_ARM}),
        _kf(DURATION, root_pos=(0, GROUND_Y, HOOK_LUNGE_Z + 0.35), Torso=FINAL_TORSO, Head=FINAL_HEAD,
            **_READY_LEGS, **{"Left Arm": (10, 0, 12), "Right Arm": (10, 0, -12)}),
    ]
    phases = [
        {"name": "garde", "t0": 0.00, "t1": JAB_WINDUP_T, "expected_reversals": {}},
        {"name": "jab", "t0": JAB_WINDUP_T, "t1": JAB_T, "expected_reversals": {}},
        {"name": "cross", "t0": JAB_T, "t1": CROSS_T, "expected_reversals": {}},
        {"name": "hook", "t0": CROSS_T, "t1": HOOK_T, "expected_reversals": {}},
        {"name": "suite", "t0": HOOK_T, "t1": HOOK_T + 0.45, "expected_reversals": {}},
        {"name": "posture_finale", "t0": HOOK_T + 0.45, "t1": DURATION, "expected_reversals": {}},
    ]
    preview_times = [0.0, GARDE_T, JAB_WINDUP_T, JAB_T, CROSS_WINDUP_T, CROSS_COIL_T, CROSS_T,
                      HOOK_WINDUP_T, HOOK_COIL_T, HOOK_T, HOOK_T + 0.45, DURATION]
    engine_opts = {"handle_type": "AUTO_CLAMPED"}
    return keyframes, phases, preview_times, engine_opts


# -----------------------------------------------------------------------
# Mannequin : encaisse les 3 coups avec une intensite croissante (leger
# flinch au jab, vacillement au cross, projection au hook -- le combo
# doit se lire comme une escalade, pas 3 fois le meme recul). Racine
# Y=180 (face a l'attaquant, "devant" = +Z pour lui), meme convention que
# r6_directional_punch.
DUMMY_IDLE_TORSO = (0, 0, 0)
DUMMY_IDLE_HEAD = (0, 0, 0)
DUMMY_IDLE_ARMS = {"Right Arm": (4, 0, 10), "Left Arm": (4, 0, -10)}
DUMMY_IDLE_LEGS = {"Right Leg": (0, 0, 3), "Left Leg": (0, 0, -3)}

JAB_HIT_TORSO = (-10, 0, 3)
JAB_HIT_HEAD = (-16, -4, 0)
JAB_HIT_ARMS = {"Right Arm": (40, 0, 20), "Left Arm": (40, 0, -25)}
JAB_HIT_LEGS = {"Right Leg": (-4, 0, 4), "Left Leg": (2, 0, -4)}
# -- whiplash : la rotation continue un instant au-dela de la pose de
# contact (l'inertie du coup n'est pas absorbee instantanement), avant un
# rebond elastique partiel qui NE revient PAS a l'idle (le prochain coup
# arrive avant toute recuperation complete -- combo sans temps mort).
JAB_OVERSHOOT_TORSO = (-15, 0, 4)
JAB_OVERSHOOT_HEAD = (-23, -6, 0)
JAB_SETTLE_TORSO = (-6, 0, 2)
JAB_SETTLE_HEAD = (-9, -2, 0)

CROSS_HIT_TORSO = (-30, 0, 7)
CROSS_HIT_HEAD = (-36, -9, 0)
CROSS_HIT_ARMS = {"Right Arm": (130, 0, 50), "Left Arm": (130, 0, -62)}
CROSS_HIT_LEGS = {"Right Leg": (-16, 0, 9), "Left Leg": (9, 0, -12)}
CROSS_OVERSHOOT_TORSO = (-38, 0, 9)
CROSS_OVERSHOOT_HEAD = (-44, -12, 0)
CROSS_SETTLE_TORSO = (-19, 0, 4)
CROSS_SETTLE_HEAD = (-23, -5, 0)

HOOK_HIT_TORSO = (-18, 40, -10)
HOOK_HIT_HEAD = (-24, 46, -6)
HOOK_HIT_ARMS = {"Right Arm": (150, 0, 70), "Left Arm": (150, 0, -85)}
HOOK_HIT_LEGS = {"Right Leg": (-20, 0, 20), "Left Leg": (-8, 0, -22)}
# -- le finisher : whiplash + court hop (racine Y) pendant la projection,
# le corps continue de tourner sous l'impact avant de retomber au sol.
HOOK_OVERSHOOT_TORSO = (-22, 48, -12)
HOOK_OVERSHOOT_HEAD = (-30, 55, -8)
HOOK_HOP_Y = GROUND_Y + 0.42

DAZED_TORSO = (26, 0, -6)
DAZED_HEAD = (14, 8, 0)
DAZED_ARMS = {"Right Arm": (24, 0, 14), "Left Arm": (24, 0, -18)}
DAZED_LEGS = {"Right Leg": (4, 0, 6), "Left Leg": (0, 0, -8)}


def dummy_combo_reaction():
    keyframes = [
        _kf(0.00, root_pos=(0, GROUND_Y, DUMMY_Z), HumanoidRootPart=(0, 180, 0),
            Torso=DUMMY_IDLE_TORSO, Head=DUMMY_IDLE_HEAD, **DUMMY_IDLE_LEGS, **DUMMY_IDLE_ARMS),
        _kf(JAB_T - 0.03, root_pos=(0, GROUND_Y, DUMMY_Z), HumanoidRootPart=(0, 180, 0),
            Torso=DUMMY_IDLE_TORSO, Head=DUMMY_IDLE_HEAD, **DUMMY_IDLE_LEGS, **DUMMY_IDLE_ARMS),
        # -- flinch au jab : snap sur le contact, puis whiplash + rebond
        # partiel (jamais un retour a l'idle -- le cross arrive avant) --
        _kf(JAB_T, root_pos=(0, GROUND_Y, DUMMY_Z), HumanoidRootPart=(0, 180, 0),
            Torso=JAB_HIT_TORSO, Head=JAB_HIT_HEAD, **JAB_HIT_LEGS, **JAB_HIT_ARMS),
        _kf(JAB_T + 0.05, root_pos=(0, GROUND_Y, DUMMY_Z), HumanoidRootPart=(0, 180, 0),
            Torso=JAB_OVERSHOOT_TORSO, Head=JAB_OVERSHOOT_HEAD, **JAB_HIT_LEGS, **JAB_HIT_ARMS),
        _kf(JAB_T + 0.16, root_pos=(0, GROUND_Y, DUMMY_Z - 0.15), HumanoidRootPart=(0, 180, 0),
            Torso=JAB_SETTLE_TORSO, Head=JAB_SETTLE_HEAD, **JAB_HIT_LEGS, **JAB_HIT_ARMS),
        _kf(CROSS_T - 0.03, root_pos=(0, GROUND_Y, DUMMY_Z - 0.15), HumanoidRootPart=(0, 180, 0),
            Torso=JAB_SETTLE_TORSO, Head=JAB_SETTLE_HEAD, **JAB_HIT_LEGS, **JAB_HIT_ARMS),
        # -- vacille fort au cross : meme principe (snap -> whiplash ->
        # rebond partiel), amplitude plus grande --
        _kf(CROSS_T, root_pos=(0, GROUND_Y, DUMMY_Z - 0.15), HumanoidRootPart=(0, 180, 0),
            Torso=CROSS_HIT_TORSO, Head=CROSS_HIT_HEAD, **CROSS_HIT_LEGS, **CROSS_HIT_ARMS),
        _kf(CROSS_T + 0.06, root_pos=(0, GROUND_Y, DUMMY_Z - 0.15), HumanoidRootPart=(0, 180, 0),
            Torso=CROSS_OVERSHOOT_TORSO, Head=CROSS_OVERSHOOT_HEAD, **CROSS_HIT_LEGS, **CROSS_HIT_ARMS),
        _kf(CROSS_T + 0.20, root_pos=(0, GROUND_Y, DUMMY_Z - 0.85), HumanoidRootPart=(0, 180, 0),
            Torso=CROSS_SETTLE_TORSO, Head=CROSS_SETTLE_HEAD, **CROSS_HIT_LEGS, **CROSS_HIT_ARMS),
        _kf(HOOK_T - 0.03, root_pos=(0, GROUND_Y, DUMMY_Z - 0.85), HumanoidRootPart=(0, 165, 0),
            Torso=CROSS_SETTLE_TORSO, Head=CROSS_SETTLE_HEAD, **CROSS_HIT_LEGS, **CROSS_HIT_ARMS),
        # -- projete par le hook : le plus grand deplacement, tete/torse
        # tournent fort (coup lateral), whiplash + court hop pendant la
        # projection avant l'atterrissage --
        _kf(HOOK_T, root_pos=(0, GROUND_Y, DUMMY_Z - 0.85), HumanoidRootPart=(0, 150, 0),
            Torso=HOOK_HIT_TORSO, Head=HOOK_HIT_HEAD, **HOOK_HIT_LEGS, **HOOK_HIT_ARMS),
        _kf(HOOK_T + 0.08, root_pos=(0, HOOK_HOP_Y, DUMMY_Z - 1.35), HumanoidRootPart=(0, 145, 0),
            Torso=HOOK_OVERSHOOT_TORSO, Head=HOOK_OVERSHOOT_HEAD, **HOOK_HIT_LEGS, **HOOK_HIT_ARMS),
        _kf(HOOK_T + 0.35, root_pos=(0, GROUND_Y, DUMMY_Z - 2.6), HumanoidRootPart=(0, 130, 0),
            Torso=HOOK_HIT_TORSO, Head=HOOK_HIT_HEAD, **HOOK_HIT_LEGS, **HOOK_HIT_ARMS),
        _kf(HOOK_T + 0.75, root_pos=(0, GROUND_Y, DUMMY_Z - 3.0), HumanoidRootPart=(0, 140, 0),
            Torso=DAZED_TORSO, Head=DAZED_HEAD, **DAZED_LEGS, **DAZED_ARMS),
        _kf(DURATION, root_pos=(0, GROUND_Y, DUMMY_Z - 3.0), HumanoidRootPart=(0, 140, 0),
            Torso=DAZED_TORSO, Head=DAZED_HEAD, **DAZED_LEGS, **DAZED_ARMS),
    ]
    phases = [
        {"name": "attente", "t0": 0.00, "t1": JAB_T, "expected_reversals": {}},
        {"name": "jab_encaisse", "t0": JAB_T, "t1": CROSS_T, "expected_reversals": {}},
        {"name": "cross_encaisse", "t0": CROSS_T, "t1": HOOK_T, "expected_reversals": {}},
        {"name": "projete", "t0": HOOK_T, "t1": DURATION, "expected_reversals": {}},
    ]
    preview_times = [0.0, JAB_T, JAB_T + 0.05, CROSS_T, CROSS_T + 0.06, HOOK_T, HOOK_T + 0.08,
                      HOOK_T + 0.35, HOOK_T + 0.75, DURATION]
    engine_opts = {"handle_type": "AUTO_CLAMPED"}
    return keyframes, phases, preview_times, engine_opts


# -- Secondary motion -- UN SEUL t_min par part supporte par
# anim_engine._spring_chase (pas un par coup) : le mettre a JAB_T (le
# 1er coup) perturberait alors la pose CALIBREE du cross et du hook a
# leurs propres instants d'impact (trouve par calibrate.py -- l'ecart de
# contact du cross/hook explosait a 1,6/2,5 studs avec t_min=JAB_T,
# contre le residu attendu de ~0,5-1 stud une fois retombe a t_min=HOOK_T
# seul). Donc, comme r6_directional_punch, la vibration ne s'applique
# qu'APRES le DERNIER coup du combo (le hook, le seul qui a un vrai
# follow-through tenu) -- les coups intermediaires (jab, cross) restent
# des poses CFrame propres a leur instant d'impact, sans interference.
ATTACKER_SECONDARY_MOTION = {
    "Torso": {"channels": (0, 1, 2), "stiffness": 300.0,
              "damping_ratio": 0.42, "t_min": HOOK_T},
    "Left Arm": {"channels": (0, 2), "stiffness": 340.0,
                 "damping_ratio": 0.45, "t_min": HOOK_T},
}
DUMMY_SECONDARY_MOTION = {
    "Torso": {"channels": (0, 1, 2), "stiffness": 100.0,
              "damping_ratio": 0.45, "t_min": JAB_T},
    "Head": {"channels": (0, 1, 2), "stiffness": 150.0,
             "damping_ratio": 0.5, "t_min": JAB_T},
}
