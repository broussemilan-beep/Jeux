"""
Choregraphie : le personnage leve LA MAIN DROITE des le tout debut de
l'animation pour invoquer une boule d'energie colossale -- LE SOLEIL --
a la maniere d'un genkidama (energie rassemblee a UNE main, tenue
au-dessus de la tete), la laisse grossir en la tenant (leger balancement,
"l'energie qui respire", pas un gel total), PUIS l'abat rapidement vers
l'avant -- lancer brusque, pas une transition lente -- pour la jeter sur
le monde en contrebas, avant de reprendre sa posture hautaine, satisfait,
a regarder l'impact au loin.

Historique des retours utilisateur sur cette meme scene (apres rejet de
la chute divine, "Nul, on tente un autre") :
  1. "le perso leve la main pour invoquer une enorme boule divine et
     d'un ton hautain [la jette] la-bas sur le monde." -> premiere
     version : une seule main (Right Arm), boule violette generique.
  2. "Non le personnage leve la main droit au debut de l'animation et
     abas le soleil comme un genkidama sur le monde." -> mal interprete
     a tort comme "deux mains" (con fusion avec le mot "genkidama",
     habituellement mime a deux mains dans Dragon Ball) ; en fait "main
     droit" voulait bien dire LA MAIN DROITE, une seule -- deuxieme
     version (deux bras, genkidama classique) etait donc fausse.
  3. "non mais ca doit etre a 1 main je vais t'envoyer une ref" ->
     correction explicite, plus une reference video envoyee (clip
     Roblox "The Creator VFX" par Systech) montrant precisement UNE
     main levee (poing pres de l'epaule/au-dessus de la tete, l'autre
     bras reste a hauteur du corps) pendant que le soleil se forme
     au-dessus, PUIS un flash/impact au loin. Cette troisieme version
     revient donc a un geste a une main, tout en gardant la calibration
     corrigee de la deuxieme iteration (voir plus bas) -- le bug de
     mesure trouve alors reste corrige, seul le nombre de mains change.

Meme convention d'ecriture/semantique des axes que les prototypes
precedents (rotations en degres, `_kf` identique, verifiee -- pas
resupposee -- par calcul dans calibrate.py) :
  - Torso/Head/Right Leg/Left Leg : X positif = penche/tourne VERS
    L'AVANT. X negatif = vers l'arriere/le haut -- c'est CE signe qui
    porte "hautain" ici (buste et tete inclines en arriere, menton haut).
  - Right Arm/Left Arm : X positif = part vers l'AVANT (-Z) puis monte
    par-dessus jusqu'a X=180 (au-dessus de la tete). Z (bras droit)
    positif = ecarte VERS L'EXTERIEUR ; bras gauche, signe oppose.
  - Aucun coude/genou (contrainte du rig, voir r6_rig.py) -- le bras
    reste droit meme au-dessus de la tete, pas plie pres de l'epaule
    comme dans la reference video (le rig ne le permet pas), voir
    README pour la reconciliation.
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

# Left Arm reste a cette pose d'appui/equilibre PENDANT TOUTE la charge
# et le lancer -- une seule main invoque, l'autre ne bouge pas (retour
# utilisateur explicite + reference video : bras libre le long du corps,
# pas leve).
_SIDE_LEFT_ARM = (5, 0, -20)

# Right Arm calibree (voir README/calibrate.py : balayage fin 170..185 x
# 0..-20 avec le bout "bottom" -- le vrai bout main -- torse -15, tete
# -12, Left Arm au repos : X=180 Z=-15 met la main ~0,15 stud AU-DESSUS
# du sommet de la tete, quasi inchange par la presence/absence du bras
# gauche leve). Un seul bras, donc pas de miroir a verifier ici.
RAISE_RIGHT_ARM = (180, 0, -15)

ANTICIP_TORSO = (-22, 0, 0)
ANTICIP_HEAD = (-15, 0, 0)
# Anticipation : la main se resserre legerement vers le corps (Z reduit
# en magnitude) juste avant le lancer -- "l'energie qui se comprime" --
# plutot qu'un vrai changement d'angle X (deja au max utile a 180).
ANTICIP_RIGHT_ARM = (185, 0, -6)

THROW_TORSO = (20, 0, 0)
THROW_HEAD = (15, 0, 0)
# Lancer : le bras balaie depuis au-dessus de la tete (180) jusqu'a un
# peu au-dela de l'horizontale (40) -- un vrai "abattre", pas un geste
# qui reste haut.
THROW_RIGHT_ARM = (40, 0, -8)
THROW_LEGS = {"Right Leg": (10, 0, 6), "Left Leg": (0, 0, -2)}

FOLLOW_TORSO = (26, 0, 0)
FOLLOW_HEAD = (18, 0, 0)
# Suite du geste : le bras continue sa descente (10, presque le long du
# corps) -- le soleil est deja parti, la main acheve le mouvement.
FOLLOW_RIGHT_ARM = (10, 0, -5)


def haughty_orb_throw():
    keyframes = [
        # t=0 : le lever de la main droite commence des la premiere
        # frame -- pas de pose hautaine immobile avant (retour
        # utilisateur : "au debut de l'animation"). Le buste/tete
        # hautains restent presents des le depart : le personnage
        # n'entre pas en garde, il invoque.
        _kf(0.00, root_pos=(0, GROUND_Y, 0), Torso=(-8, 0, 0), Head=(-8, 0, 0),
            **_HAUGHTY_LEGS, **{"Right Arm": _IDLE_ARMS["Right Arm"], "Left Arm": _SIDE_LEFT_ARM}),
        _kf(RAISE_T, root_pos=(0, GROUND_Y, 0), Torso=(-15, 0, 0), Head=(-12, 0, 0),
            **_HAUGHTY_LEGS, **{"Right Arm": RAISE_RIGHT_ARM, "Left Arm": _SIDE_LEFT_ARM}),
        _kf(0.95, root_pos=(0, GROUND_Y, 0), Torso=(-15, 3, 0), Head=(-12, 0, 0),
            **_HAUGHTY_LEGS, **{"Right Arm": RAISE_RIGHT_ARM, "Left Arm": _SIDE_LEFT_ARM}),
        _kf(1.60, root_pos=(0, GROUND_Y, 0), Torso=(-15, -3, 0), Head=(-12, 0, 0),
            **_HAUGHTY_LEGS, **{"Right Arm": RAISE_RIGHT_ARM, "Left Arm": _SIDE_LEFT_ARM}),
        _kf(ANTICIP_T, root_pos=(0, GROUND_Y, 0), Torso=ANTICIP_TORSO, Head=ANTICIP_HEAD,
            **_HAUGHTY_LEGS, **{"Right Arm": ANTICIP_RIGHT_ARM, "Left Arm": _SIDE_LEFT_ARM}),
        _kf(THROW_T, root_pos=(0, GROUND_Y, 0), Torso=THROW_TORSO, Head=THROW_HEAD,
            **THROW_LEGS, **{"Right Arm": THROW_RIGHT_ARM, "Left Arm": _SIDE_LEFT_ARM}),
        _kf(THROW_T + 0.15, root_pos=(0, GROUND_Y, 0), Torso=FOLLOW_TORSO, Head=FOLLOW_HEAD,
            **THROW_LEGS, **{"Right Arm": FOLLOW_RIGHT_ARM, "Left Arm": _SIDE_LEFT_ARM}),
        _kf(THROW_T + 0.55, root_pos=(0, GROUND_Y, 0), Torso=(-5, 0, 0), Head=(-5, 0, 0),
            **_HAUGHTY_LEGS, **{"Right Arm": (10, 0, 5), "Left Arm": _IDLE_ARMS["Left Arm"]}),
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
# dans la toute premiere version : c'est ce raccourci qui traduit "des le
# debut de l'animation" sans pour autant faire un pop instantane (une
# vraie interpolation reste visible et lisible sur 0,30 s).
RAISE_T = 0.30
ANTICIP_T = 1.75
THROW_T = ANTICIP_T + 0.15
RELEASE_T = THROW_T
IMPACT_T = THROW_T + 0.85
