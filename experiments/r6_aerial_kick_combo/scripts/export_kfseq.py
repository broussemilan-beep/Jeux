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
from r6_rig import PART_ORDER, PARENT
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


def build_pose_tree(keyframe_item, part, samples, sample_index, parent_xml=None):
    t, rot, pos, _wpos = samples[part][sample_index]
    item = ET.SubElement(parent_xml if parent_xml is not None else keyframe_item,
                          "Item", {"class": "Pose", "referent": _next_ref()})
    props = ET.SubElement(item, "Properties")
    ET.SubElement(props, "string", {"name": "Name"}).text = part
    ET.SubElement(props, "token", {"name": "EasingDirection"}).text = "0"
    ET.SubElement(props, "token", {"name": "EasingStyle"}).text = "1"  # Linear
    ET.SubElement(props, "float", {"name": "Weight"}).text = "1"
    matrix = euler_xyz_matrix(*rot)
    world_pos = pos if part == "HumanoidRootPart" else (0.0, 0.0, 0.0)
    _cframe_element(props, "CFrame", world_pos, matrix)

    child_parts = [p for p, parent in PARENT.items() if parent == part]
    for cp in child_parts:
        build_pose_tree(keyframe_item, cp, samples, sample_index, parent_xml=item)
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
