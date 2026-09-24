"""
Taxonomie v1 des techniques (PLAN.md, section 3, couche B).

Chaque connaissance chiffree du cerveau est rattachee a UNE categorie : on
ne transpose jamais un chiffre d'une categorie a une autre (ce qui fait un
bon poing ne vaut pas pour un deplacement). Une categorie sans assez
d'exemples est signalee comme telle -- le cerveau retombe alors sur les
principes universels au lieu d'extrapoler.
"""

CATEGORIES = {
    "frappe_legere": "coup de base enchainable (M1) : court, lisible, recuperation rapide",
    "frappe_lourde": "finisher / capacite de frappe (uppercut, downslam) : anticipation marquee, gros deplacement",
    "deplacement": "dash, esquive, saut ponctuel : le corps entier part, les membres suivent",
    "locomotion": "cycle marche/course : boucle, appuis alternes",
    "attente": "idle, garde : boucle vivante, faible energie",
    "reaction": "victime : touche, recul, projection",
    "garde_touchee": "blocage qui encaisse",
    "charge": "incantation, charge d'energie (pas encore d'exemple dans le corpus)",
    "aerien": "action en l'air (pas encore d'exemple dans le corpus)",
    "cinematique": "scene longue mise en scene (nos prototypes) : ne se compare PAS aux clips de jeu",
}

MIN_EXAMPLES = 3   # en dessous : distribution signalee "fragile"

# rattachement des sources connues (nom exact de la KeyframeSequence)
SOURCE_CATEGORIES = {
    "battleground_animation_pack_v1.0.1": {
        "[1] Idle": "attente", "[1] Walk": "locomotion", "[1] Run": "locomotion",
        "[2] M1_1": "frappe_legere", "[2] M1_2": "frappe_legere", "[2] M1_3": "frappe_legere",
        "[2] M1_4": "frappe_legere",
        "[3] Backdash": "deplacement", "[3] Forward Dash": "deplacement", "[3] Sidedash_L": "deplacement",
        "[3] Sidedash_R": "deplacement",
        "[3] Downslam V1": "frappe_lourde", "[3] Downslam V2": "frappe_lourde", "[3] Uppercut": "frappe_lourde",
        "[4] Hit 1": "reaction", "[4] Hit 2": "reaction", "[4] Hit 3": "reaction",
        "[5] Block Hit": "garde_touchee", "[5] Block Idle": "attente",
    },
}
