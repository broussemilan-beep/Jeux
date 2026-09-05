"""
Export d'un KeyframeSequence Roblox natif (.rbxmx, XML) a partir des
echantillons produits par anim_engine.sample().

Format XML standard Roblox (schema public du moteur, utilise par toute
animation R6/R15 -- independant du plugin Cautioned/DevForum bloque) :
un <Item class="KeyframeSequence"> contenant des <Item class="Keyframe">
(un par temps d'echantillon), chacun contenant une hierarchie de
<Item class="Pose"> imbriquee (HumanoidRootPart > Torso > {Head, Right Arm,
Left Arm, Right Leg, Left Leg}) qui reproduit la hierarchie des Motor6D.

Choix : on exporte TOUS les echantillons (echantillonnage dense, 30 Hz)
avec EasingStyle=Linear entre eux plutot que d'essayer de faire
correspondre les poignees Bezier de Blender aux styles d'easing a jeton
limites de Roblox (Linear/Cubic/Sine/...). A frequence d'echantillonnage
suffisante, un rééchantillonnage lineaire d'une courbe deja lisse est
visuellement indiscernable de la courbe source -- c'est la meme technique
que "Bake to keyframes" dans l'editeur d'animation Roblox et dans la
plupart des pipelines d'export d'animation par courbes.
"""
import xml.etree.ElementTree as ET

import numpy as np

from r6_rig import PART_ORDER, PARENT, joint_for_part, joint_rotations
from anim_engine import euler_xyz_matrix

_ref_counter = [0]


def _next_ref():
    _ref_counter[0] += 1
    return f"RBXKFC_{_ref_counter[0]:06d}"


def _cframe_element(parent, name, pos, matrix):
    el = ET.SubElement(parent, "CoordinateFrame", {"name": name})
    for tag, val in zip(("X", "Y", "Z"), pos):
        ET.SubElement(el, tag).text = repr(float(val))
    for i in range(3):
        for j in range(3):
            ET.SubElement(el, f"R{i}{j}").text = repr(float(matrix[i][j]))
    return el


def _properties(item, entries):
    props = ET.SubElement(item, "Properties")
    for kind, name, value in entries:
        el = ET.SubElement(props, kind, {"name": name})
        if kind != "CoordinateFrame":
            el.text = str(value)
    return props


def to_joint_frame(part, rot_parent_frame, translation_parent_frame):
    """Convertit une rotation exprimee dans le repere du PARENT (la
    convention d'ecriture de toute la choregraphie : "X positif = la jambe
    part vers l'avant") vers le repere du JOINT, seul repere que Roblox
    utilise pour Pose.CFrame.

    Le moteur resout Part1 = Part0 * C0 * Transform * C1^-1. En notant
    (J0, c0) et (J1, c1) les C0/C1, la rotation vue dans le repere du
    parent vaut donc J0 . T_R . J1^T. Pour qu'elle soit egale a la
    rotation R que j'ai ecrite, il faut poser :

        T_R = J0^T . R . J1

    Tant que J0 et J1 sont l'identite, T_R = R et la question ne se pose
    pas -- c'est ce que le code supposait. Or AUCUN des 6 Motor6D du rig
    reel n'a de C0/C1 identite (verifie par `import_rig.py` sur
    rig/RigR6.rbxmx) : hanches et epaules portent +/-90 deg autour de Y,
    Neck et RootJoint une permutation Y/Z. Sans cette conversion, un
    KeyframeSequence ecrit "en repere parent" joue les BONS ANGLES AUTOUR
    DES MAUVAIS AXES sur un vrai rig : la rotation d'axe a devient une
    rotation d'axe J0.a. Concretement, mes coups de pied vers l'avant
    (axe X) sortaient lateralement, et le spin du torse (axe Y) sortait
    en roulis.

    La pose de repos, elle, restait juste (R = identite => T_R = identite
    quels que soient J0/J1), ce qui explique que le rig au repos ait
    toujours eu l'air correct.

    Translation : les membres gardent T_t = 0 -- c'est deja exactement le
    pivot autour du point d'attache (le terme -R.c1 s'en charge). Seul le
    HumanoidRootPart porte une translation voulue d (le saut) ; comme son
    c1 est nul, il faut poser T_t = J0^T . d."""
    jname = joint_for_part(part)
    if jname is None:
        return rot_parent_frame, translation_parent_frame
    j0, j1 = joint_rotations(jname)
    j0 = np.array(j0)
    j1 = np.array(j1)
    t_rot = j0.T @ np.array(rot_parent_frame) @ j1
    t_pos = j0.T @ np.array(translation_parent_frame)
    return t_rot, tuple(t_pos.tolist())


def effective_pose_inputs(samples, sample_index):
    """Rotation (repere parent) et translation a encoder pour CHAQUE part,
    avant conversion vers le repere du joint.

    Le mouvement d'ensemble du corps (rotation du "bassin" + arc du saut)
    est REPLIE SUR LA POSE DU TORSE, et la pose HumanoidRootPart devient
    l'identite.

    Pourquoi : l'Animator de Roblox applique une Pose au Motor6D dont le
    Part1 porte le meme nom. Or dans un rig R6, HumanoidRootPart n'est
    Part1 d'AUCUN Motor6D (il n'est que le Part0 du RootJoint, verifie sur
    rig/r6_rig.json). Une Pose nommee "HumanoidRootPart" ne pilote donc
    rien et est ignoree a la lecture : tout l'arc du saut, qui etait ecrit
    la, disparaissait -- le personnage enchainait les coups sans jamais
    decoller. Le joint qui porte reellement le mouvement du corps entier
    est le RootJoint (HumanoidRootPart -> Torso), c'est-a-dire la pose du
    TORSE. C'est ainsi que sont faites les animations de saut de Roblox.

    Ce repli est sur quelle que soit l'interpretation : meme si une pose
    racine etait honoree, on y ecrit l'identite, donc aucun double-emploi."""
    root_rot = euler_xyz_matrix(*samples["HumanoidRootPart"][sample_index][1])
    root_trans = samples["HumanoidRootPart"][sample_index][2]

    out = {}
    for part in PART_ORDER:
        rot = euler_xyz_matrix(*samples[part][sample_index][1])
        if part == "HumanoidRootPart":
            out[part] = (np.eye(3), (0.0, 0.0, 0.0))
        elif part == "Torso":
            out[part] = (root_rot @ rot, tuple(root_trans))
        else:
            out[part] = (rot, (0.0, 0.0, 0.0))
    return out


def build_pose_tree(keyframe_item, part, samples, sample_index, parent_xml=None,
                    effective=None):
    if effective is None:
        effective = effective_pose_inputs(samples, sample_index)
    rot_parent_frame, trans_parent_frame = effective[part]
    item = ET.SubElement(parent_xml if parent_xml is not None else keyframe_item,
                          "Item", {"class": "Pose", "referent": _next_ref()})
    props = ET.SubElement(item, "Properties")
    ET.SubElement(props, "string", {"name": "Name"}).text = part
    ET.SubElement(props, "token", {"name": "EasingDirection"}).text = "0"
    ET.SubElement(props, "token", {"name": "EasingStyle"}).text = "1"  # Linear
    ET.SubElement(props, "float", {"name": "Weight"}).text = "1"
    matrix, world_pos = to_joint_frame(part, rot_parent_frame, trans_parent_frame)
    _cframe_element(props, "CFrame", world_pos, matrix)

    child_parts = [p for p, parent in PARENT.items() if parent == part]
    for cp in child_parts:
        build_pose_tree(keyframe_item, cp, samples, sample_index, parent_xml=item,
                        effective=effective)
    return item


def export_keyframe_sequence(samples, sample_hz, out_path, anim_name="R6_AerialKickCombo",
                              loop=False, decimate_to_hz=30):
    """samples: dict part -> [(t, quat_wxyz, pos_xyz), ...] a sample_hz.
    Reechantillonne (decime) a decimate_to_hz pour la sortie (limite la
    taille du fichier tout en restant assez dense pour une interpolation
    lineaire visuellement fluide)."""
    n_samples = len(next(iter(samples.values())))
    stride = max(1, round(sample_hz / decimate_to_hz))
    indices = list(range(0, n_samples, stride))
    if indices[-1] != n_samples - 1:
        indices.append(n_samples - 1)

    root = ET.Element("roblox", {
        "xmlns:xmime": "http://www.w3.org/2005/05/xmlmime",
        "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
        "xsi:noNamespaceSchemaLocation": "http://www.roblox.com/roblox.xsd",
        "version": "4",
    })
    kfseq = ET.SubElement(root, "Item", {"class": "KeyframeSequence", "referent": _next_ref()})
    props = ET.SubElement(kfseq, "Properties")
    ET.SubElement(props, "string", {"name": "Name"}).text = anim_name
    ET.SubElement(props, "bool", {"name": "Loop"}).text = "true" if loop else "false"
    ET.SubElement(props, "token", {"name": "Priority"}).text = "3"  # Action

    for out_i, idx in enumerate(indices):
        t = samples["HumanoidRootPart"][idx][0]
        kf_item = ET.SubElement(kfseq, "Item", {"class": "Keyframe", "referent": _next_ref()})
        kprops = ET.SubElement(kf_item, "Properties")
        ET.SubElement(kprops, "string", {"name": "Name"}).text = f"Keyframe{out_i}"
        ET.SubElement(kprops, "float", {"name": "Time"}).text = repr(float(t))
        build_pose_tree(kf_item, "HumanoidRootPart", samples, idx)

    tree = ET.ElementTree(root)
    ET.indent(tree, space="  ")
    tree.write(out_path, encoding="utf-8", xml_declaration=True)
    return out_path, len(indices)
