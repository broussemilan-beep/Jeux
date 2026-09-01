"""
Geometrie standard du rig R6 (Roblox Engine), convention Roblox : +Y haut,
-Z avant, repere direct (right-handed), unites en studs.

Ces valeurs (tailles de parts, offsets C0/C1 des Motor6D) sont la geometrie
PUBLIQUE et standard de tout personnage R6 -- identique pour chaque avatar
R6 du moteur, documentee dans d'innombrables scripts/tutoriels publics
Roblox. Ce ne sont PAS des donnees issues du rig communautaire "R6 IK+FK
Blender Rig" du DevForum (inaccessible depuis ce sandbox, voir README).
Le rig IK+FK bloque n'aurait de toute facon fait qu'ajouter une couche
d'os de controle par-dessus exactement cette meme geometrie -- il ne
change pas le squelette Motor6D sous-jacent.

Contrainte non negociable (mandat utilisateur) : 6 segments rigides
(Torso, Head, Right Arm, Left Arm, Right Leg, Left Leg), aucun coude ni
genou. Verifie structurellement par scripts/measure.py.
"""

# Taille (X, Y, Z) de chaque part, en studs.
PART_SIZES = {
    "HumanoidRootPart": (2.0, 2.0, 1.0),
    "Torso": (2.0, 2.0, 1.0),
    "Head": (2.0, 1.0, 1.0),
    "Right Arm": (1.0, 2.0, 1.0),
    "Left Arm": (1.0, 2.0, 1.0),
    "Right Leg": (1.0, 2.0, 1.0),
    "Left Leg": (1.0, 2.0, 1.0),
}

# joint_name -> (part0, part1, C0_position, C1_position)
# Rotation de C0/C1 = identite (standard R6). Position en studs, locale a
# chaque part au repos.
JOINTS = {
    "RootJoint":      ("HumanoidRootPart", "Torso",      (0.0, 0.0, 0.0), (0.0, 0.0, 0.0)),
    "Neck":           ("Torso", "Head",       (0.0, 1.0, 0.0), (0.0, -0.5, 0.0)),
    "Right Shoulder": ("Torso", "Right Arm",  (1.0, 0.5, 0.0), (-0.5, 0.5, 0.0)),
    "Left Shoulder":  ("Torso", "Left Arm",   (-1.0, 0.5, 0.0), (0.5, 0.5, 0.0)),
    "Right Hip":      ("Torso", "Right Leg",  (1.0, -1.0, 0.0), (0.5, 1.0, 0.0)),
    "Left Hip":       ("Torso", "Left Leg",   (-1.0, -1.0, 0.0), (-0.5, 1.0, 0.0)),
}

# Hierarchie (part -> part parent), derivee de JOINTS, root = HumanoidRootPart.
PARENT = {part1: part0 for (part0, part1, _, _) in JOINTS.values()}

# Ordre d'evaluation topologique (parent avant enfant), pour construction
# et export.
PART_ORDER = [
    "HumanoidRootPart", "Torso", "Head",
    "Right Arm", "Left Arm", "Right Leg", "Left Leg",
]

# Segments animables par un "coup de pied" au sens strict de la contrainte
# utilisateur (le reste -- Torso/Root/Head/bras -- sert au contrepoids/elan,
# jamais a un coup de poing).
LEG_PARTS = ("Right Leg", "Left Leg")
ARM_PARTS = ("Right Arm", "Left Arm")


def local_offset(joint_name):
    """Position locale de part1 par rapport a part0 au repos = C0 - C1."""
    _, _, c0, c1 = JOINTS[joint_name]
    return tuple(c0[i] - c1[i] for i in range(3))


def joint_for_part(part_name):
    """Retourne le nom du joint qui attache part_name a son parent, ou None
    pour HumanoidRootPart (racine, pas de joint parent)."""
    for jname, (p0, p1, _, _) in JOINTS.items():
        if p1 == part_name:
            return jname
    return None
