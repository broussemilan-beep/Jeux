"""
Choregraphie : le personnage leve LA MAIN DROITE des le tout debut de
l'animation pour invoquer une boule d'energie colossale -- LE SOLEIL --
a la maniere d'un genkidama (energie rassemblee a UNE main, tenue
au-dessus de la tete), la laisse grossir en la tenant (leger balancement,
"l'energie qui respire", pas un gel total), PUIS l'abat rapidement vers
l'avant -- lancer brusque, pas une transition lente -- pour la jeter sur
le monde en contrebas, PLONGE tout le corps dans la fin du geste (le
buste et le bras continuent vers le sol, pas juste la main qui retombe
mollement), tient cette posture jusqu'a l'impact, puis se redresse
lentement vers sa posture hautaine, satisfait.

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
  4. "fais plus d'effort la fin de mouvement doit allez vers le sol" ->
     la version precedente relevait le bras (10,0,5) et redressait le
     buste des THROW_T+0.55, AVANT MEME l'impact (IMPACT_T tombait apres
     ce redressement) -- le personnage se relevait avant que le soleil
     ait fini sa chute, donc "la fin de mouvement" ne descendait pas.
     Corrige : ajout d'une phase DEEP (le buste plonge vers l'avant-bas,
     X=42, le bras continue sa descente jusqu'a X quasi nul -- son
     minimum geometrique, voir plus bas -- les jambes en fente), TENUE
     jusqu'a IMPACT_T (deux keyframes identiques -> hold plat, meme
     technique que les prototypes precedents), PUIS redressement lent
     (0,5s) vers la posture hautaine. La duree totale de la scene
     s'allonge en consequence (3,05s -> 3,90s) pour laisser le temps a
     cet arc complet (anticipation -> action -> tenue -> retour).

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
    README pour la reconciliation. CONSEQUENCE IMPORTANTE pour la fin de
    geste : X=0 (bras qui pend) est le point le plus BAS que le bras
    puisse atteindre tout seul -- tourner davantage dans un sens ou
    l'autre RELEVE la main (verifie numeriquement, voir le sweep dans le
    worklog de session). "Aller vers le sol" au-dela de X=0 ne peut donc
    PAS venir d'une rotation d'epaule supplementaire : c'est le PENCHE
    DU BUSTE vers l'avant (Torso X positif fort) qui incline tout le
    bras (attache au buste) vers le sol en espace monde, meme si le
    bras reste a X quasi nul dans le repere du buste.
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

# DEEP : le buste plonge vers l'avant-bas (X=42, bien au-dela du simple
# THROW_TORSO=20) et le bras acheve sa descente jusqu'a X quasi nul --
# son minimum geometrique (voir docstring de module) -- si bien qu'en
# repere MONDE le bras entier pointe vers le sol, porte par le buste
# penche, pas par une rotation d'epaule qui n'existe pas. Jambes en
# fente (Right Leg tres flechie vers l'avant, Left Leg tendue en
# arriere) pour vendre le poids du corps qui plonge avec le geste.
DEEP_TORSO = (42, 0, 0)
DEEP_HEAD = (30, 0, 0)
DEEP_RIGHT_ARM = (4, 0, -4)
DEEP_LEGS = {"Right Leg": (22, 0, 6), "Left Leg": (-12, 0, -2)}

RISE_TORSO = (5, 0, 0)
RISE_HEAD = (2, 0, 0)
RISE_RIGHT_ARM = (5, 0, 3)


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
        # DEEP : le plongeon continue APRES le lancer, pas un simple
        # relachement mou -- buste/tete/jambes vont plus loin que
        # THROW_*, le bras acheve sa descente (voir DEEP_RIGHT_ARM).
        _kf(DEEP_T, root_pos=(0, GROUND_Y, 0), Torso=DEEP_TORSO, Head=DEEP_HEAD,
            **DEEP_LEGS, **{"Right Arm": DEEP_RIGHT_ARM, "Left Arm": _SIDE_LEFT_ARM}),
        # Keyframe identique -> hold plat (meme technique que les holds
        # de r6_divine_descent) : le personnage reste plonge vers le sol
        # jusqu'a l'impact du soleil sur le monde, il ne se redresse pas
        # avant -- c'est CE hold qui fait que "la fin de mouvement" reste
        # bien vers le sol au moment ou ca compte.
        _kf(IMPACT_T, root_pos=(0, GROUND_Y, 0), Torso=DEEP_TORSO, Head=DEEP_HEAD,
            **DEEP_LEGS, **{"Right Arm": DEEP_RIGHT_ARM, "Left Arm": _SIDE_LEFT_ARM}),
        _kf(RISE_T, root_pos=(0, GROUND_Y, 0), Torso=RISE_TORSO, Head=RISE_HEAD,
            **_HAUGHTY_LEGS, **{"Right Arm": RISE_RIGHT_ARM, "Left Arm": _IDLE_ARMS["Left Arm"]}),
        _kf(FINAL_T, root_pos=(0, GROUND_Y, 0), Torso=_HAUGHTY_TORSO, Head=_HAUGHTY_HEAD,
            **_HAUGHTY_LEGS, **_IDLE_ARMS),
    ]

    phases = [
        {"name": "invocation", "t0": 0.00, "t1": 0.35, "expected_reversals": {}},
        {"name": "charge", "t0": 0.35, "t1": ANTICIP_T, "expected_reversals": {}},
        {"name": "lancer", "t0": ANTICIP_T, "t1": THROW_T, "expected_reversals": {}},
        {"name": "vol", "t0": THROW_T, "t1": IMPACT_T, "expected_reversals": {}},
        {"name": "aftermath", "t0": IMPACT_T, "t1": FINAL_T, "expected_reversals": {}},
    ]
    preview_times = [0.0, RAISE_T, 0.95, 1.60, ANTICIP_T, THROW_T, DEEP_T,
                      IMPACT_T, RISE_T, FINAL_T]
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
DEEP_T = THROW_T + 0.15
IMPACT_T = THROW_T + 0.85
# Redressement lent (0,50s) apres l'impact -- pas un retour brusque,
# retour utilisateur : la version precedente se relevait AVANT l'impact,
# ce qui cassait justement l'effet "fin de mouvement vers le sol" ; le
# redressement doit donc a la fois commencer APRES IMPACT_T et prendre
# son temps plutot que revenir d'un coup.
RISE_T = IMPACT_T + 0.50
FINAL_T = RISE_T + 0.35
