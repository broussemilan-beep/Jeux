"""
Geometrie du rig R6, CHARGEE DEPUIS UN VRAI FICHIER DE RIG
(`rig/r6_rig.json`, genere par `import_rig.py` depuis `rig/RigR6.rbxmx`,
dépôt Adonis, licence MIT -- voir `rig/PROVENANCE.md`).

Avant, ces valeurs etaient ecrites a la main de memoire. La comparaison
avec le rig reel (voir `import_rig.compare`) donne :

  - tailles des 7 parts .................... identiques
  - translations C0/C1 des 6 Motor6D ....... identiques
  - ROTATIONS C0/C1 des 6 Motor6D .......... TOUTES FAUSSES

Le code affirmait "Rotation de C0/C1 = identite (standard R6)". C'est
faux : aucun des 6 joints n'a une rotation C0/C1 identite. Les hanches et
epaules portent un +/-90 deg autour de Y, le Neck et le RootJoint une
permutation Y/Z. Consequence detaillee dans `export_kfseq.py` : une pose
exprimee dans le repere du parent doit etre CONVERTIE dans le repere du
joint avant d'etre ecrite dans le KeyframeSequence, sinon les axes du
mouvement sont permutes a la lecture sur un vrai rig.

Contrainte non negociable (mandat utilisateur), inchangee et toujours
verifiee structurellement par `measure.py` : 6 segments rigides (Torso,
Head, Right/Left Arm, Right/Left Leg), aucun coude ni genou, Motor6D a 3
DOF rotationnels, pas de translation interne.
"""
import json
import os

_HERE = os.path.dirname(os.path.abspath(__file__))
_RIG_JSON = os.path.join(_HERE, "..", "rig", "r6_rig.json")

with open(_RIG_JSON) as _f:
    _RIG = json.load(_f)

RIG_SOURCE = _RIG["source"]

# name -> (X, Y, Z) en studs
PART_SIZES = {name: tuple(size) for name, size in _RIG["part_sizes"].items()}

# joint_name -> {"part0", "part1", "C0": {"pos", "rot"}, "C1": {...}}
JOINTS = _RIG["joints"]

# part enfant -> part parent
PARENT = dict(_RIG["parent"])

# ordre topologique (parent avant enfant), racine en tete
PART_ORDER = list(_RIG["part_order"])

LEG_PARTS = ("Right Leg", "Left Leg")
ARM_PARTS = ("Right Arm", "Left Arm")

_JOINT_BY_PART1 = {j["part1"]: name for name, j in JOINTS.items()}


def joint_for_part(part_name):
    """Nom du joint qui rattache part_name a son parent (None pour la racine)."""
    return _JOINT_BY_PART1.get(part_name)


def local_offset(joint_name):
    """Position locale de part1 par rapport a part0 AU REPOS.

    Vaut C0.pos - C1.pos : dans ce rig, C0.rot == C1.rot pour les 6 joints,
    donc au repos (Transform = identite) les rotations s'annulent dans
    Part1 = Part0 * C0 * Transform * C1^-1 et il ne reste que cet ecart de
    translation. C'est aussi pourquoi la pose de repos etait correcte
    malgre l'hypothese fausse sur les rotations."""
    j = JOINTS[joint_name]
    c0, c1 = j["C0"]["pos"], j["C1"]["pos"]
    return tuple(c0[i] - c1[i] for i in range(3))


def joint_rotations(joint_name):
    """(C0.rot, C1.rot) en matrices 3x3 (listes de listes)."""
    j = JOINTS[joint_name]
    return j["C0"]["rot"], j["C1"]["rot"]
