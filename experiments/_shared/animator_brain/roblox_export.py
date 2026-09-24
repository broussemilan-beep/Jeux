"""
Export Roblox (KeyframeSequence .rbxmx) a partir des CFrames MONDE des 7
parts R6, et verification par l'equation du moteur.

Entree : frames = [(t, {part: (R 3x3, p 3)}), ...] en repere ROBLOX (Y en
haut, avant = -Z, droite = +X), HumanoidRootPart compris. Peu importe d'ou
viennent ces CFrames (rig V2.22 cuit par v222_rig.bake_parts, ou tout autre
solveur) : l'export ne suppose rien sur les conventions de pose.

Pour chaque Motor6D (Part0 -> Part1, C0, C1), le moteur resout
    Part1 = Part0 * C0 * T * C1^-1
donc la Pose a ecrire vaut
    T = C0^-1 * Part0^-1 * Part1 * C1.

HumanoidRootPart : en jeu, c'est le Humanoid qui le place (hauteur de
hanche) ; une Pose "HumanoidRootPart" ne pilote aucun Motor6D. Le
mouvement d'ensemble passe donc par le RootJoint (pose du Torso), relatif
au HumanoidRootPart fourni dans chaque frame.

Donnees du rig : data/r6_rig.json (RigR6.rbxmx d'Adonis, MIT). Verifie
identique, a 0 pres, aux C0/C1 du "Studio R6 Rig.rbxm" livre avec le rig
V2.22 (voir RIG_V222.md).
"""
import json
import os
import xml.etree.ElementTree as ET

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
RIG = json.load(open(os.path.join(_HERE, "data", "r6_rig.json")))
PART_ORDER = RIG["part_order"]
PARENT = RIG["parent"]
JOINT_BY_PART1 = {j["part1"]: (name, j) for name, j in RIG["joints"].items()}

# Blender (Z haut, avant +Y, droite +X) -> Roblox (Y haut, avant -Z, droite +X)
# x' = x, y' = z, z' = -y  (rotation propre, det = +1)
B2R = np.array([[1.0, 0.0, 0.0], [0.0, 0.0, 1.0], [0.0, -1.0, 0.0]])

# centres des parts au repos, repere Roblox (rig standard, pieds a y=0)
REST_CENTER = {"HumanoidRootPart": (0.0, 3.0, 0.0), "Torso": (0.0, 3.0, 0.0), "Head": (0.0, 4.5, 0.0),
               "Right Arm": (1.5, 3.0, 0.0), "Left Arm": (-1.5, 3.0, 0.0),
               "Right Leg": (0.5, 1.0, 0.0), "Left Leg": (-0.5, 1.0, 0.0)}


def orthonormalize(r):
    """Projection sur SO(3) (SVD) : les matrices de Blender sont en
    float32, un CFrame doit etre orthonormal."""
    u, _s, vt = np.linalg.svd(np.asarray(r, float))
    m = u @ vt
    if np.linalg.det(m) < 0:
        u[:, -1] *= -1
        m = u @ vt
    return m


def blender_to_roblox(rot, pos):
    return B2R @ np.asarray(rot) @ B2R.T, B2R @ np.asarray(pos)


def _cf(j, key):
    return np.array(j[key]["rot"], float), np.array(j[key]["pos"], float)


def joint_transform(part, world):
    """T du Motor6D dont `part` est le Part1."""
    _name, j = JOINT_BY_PART1[part]
    r0, p0 = world[j["part0"]]
    r1, p1 = world[part]
    j0, c0 = _cf(j, "C0")
    j1, c1 = _cf(j, "C1")
    # A = Part0^-1 * Part1
    ra = r0.T @ r1
    pa = r0.T @ (p1 - p0)
    # T = C0^-1 * A * C1
    rt = j0.T @ ra @ j1
    pt = j0.T @ (ra @ c1 + pa - c0)
    return rt, pt


def solve(transforms, root=(np.eye(3), np.array([0.0, 3.0, 0.0]))):
    """Equation du moteur : CFrames monde a partir des Poses (T)."""
    world = {"HumanoidRootPart": (np.asarray(root[0]), np.asarray(root[1]))}
    for part in PART_ORDER:
        if part == "HumanoidRootPart":
            continue
        _n, j = JOINT_BY_PART1[part]
        r0, p0 = world[j["part0"]]
        j0, c0 = _cf(j, "C0")
        j1, c1 = _cf(j, "C1")
        rt, pt = transforms.get(part, (np.eye(3), np.zeros(3)))
        rot = j0 @ rt @ j1.T
        pos = c0 + j0 @ pt - rot @ c1
        world[part] = (r0 @ rot, p0 + r0 @ pos)
    return world


def _cframe(parent, name, pos, m):
    el = ET.SubElement(parent, "CoordinateFrame", {"name": name})
    for tag, v in zip(("X", "Y", "Z"), pos):
        ET.SubElement(el, tag).text = repr(float(v))
    for i in range(3):
        for k in range(3):
            ET.SubElement(el, f"R{i}{k}").text = repr(float(m[i][k]))


def write_kfseq(frames, out_path, name, loop=False, priority=3, markers=(), zero_weight=()):
    """frames : [(t, world)] ; markers : [(t, "nom", "valeur")] -> KeyframeMarker
    sous le Keyframe le plus proche (utilises en jeu par GetMarkerReachedSignal).
    zero_weight : parts ecrites avec Weight = 0 (une autre animation les mene
    en jeu -- ex. jambes d'un M1, comme dans le pack pro, corpus/README.md)."""
    ref = [0]

    def nref():
        ref[0] += 1
        return f"RBXAB{ref[0]:06d}"

    root = ET.Element("roblox", {"xmlns:xmime": "http://www.w3.org/2005/05/xmlmime",
                                 "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
                                 "xsi:noNamespaceSchemaLocation": "http://www.roblox.com/roblox.xsd",
                                 "version": "4"})
    seq = ET.SubElement(root, "Item", {"class": "KeyframeSequence", "referent": nref()})
    sp = ET.SubElement(seq, "Properties")
    ET.SubElement(sp, "string", {"name": "Name"}).text = name
    ET.SubElement(sp, "bool", {"name": "Loop"}).text = "true" if loop else "false"
    ET.SubElement(sp, "token", {"name": "Priority"}).text = str(priority)
    times = [t for t, _w in frames]
    kf_items = []
    for i, (t, world) in enumerate(frames):
        kf = ET.SubElement(seq, "Item", {"class": "Keyframe", "referent": nref()})
        kp = ET.SubElement(kf, "Properties")
        ET.SubElement(kp, "string", {"name": "Name"}).text = f"Keyframe{i}"
        ET.SubElement(kp, "float", {"name": "Time"}).text = repr(float(t))
        kf_items.append(kf)

        def pose(parent_xml, part):
            it = ET.SubElement(parent_xml, "Item", {"class": "Pose", "referent": nref()})
            pp = ET.SubElement(it, "Properties")
            ET.SubElement(pp, "string", {"name": "Name"}).text = part
            ET.SubElement(pp, "token", {"name": "EasingDirection"}).text = "0"
            ET.SubElement(pp, "token", {"name": "EasingStyle"}).text = "1"  # Linear
            ET.SubElement(pp, "float", {"name": "Weight"}).text = "0" if part in zero_weight else "1"
            if part == "HumanoidRootPart":
                rt, pt = np.eye(3), np.zeros(3)
            else:
                rt, pt = joint_transform(part, world)
            _cframe(pp, "CFrame", pt, rt)
            for child in [p for p, par in PARENT.items() if par == part]:
                pose(it, child)
        pose(kf, "HumanoidRootPart")
    for t, mname, value in markers:
        k = int(np.argmin(np.abs(np.array(times) - t)))
        it = ET.SubElement(kf_items[k], "Item", {"class": "KeyframeMarker", "referent": nref()})
        mp = ET.SubElement(it, "Properties")
        ET.SubElement(mp, "string", {"name": "Name"}).text = mname
        ET.SubElement(mp, "string", {"name": "Value"}).text = str(value)
    tree = ET.ElementTree(root)
    ET.indent(tree, space="  ")
    tree.write(out_path, encoding="utf-8", xml_declaration=True)
    return out_path


def read_kfseq(path):
    """[(t, {part: (R, p)})] -- Poses brutes (T) lues dans le fichier."""
    seq = ET.parse(path).getroot().find("Item")
    out = []
    for kf in seq.findall("Item"):
        if kf.get("class") != "Keyframe":
            continue
        t = float(kf.find("Properties/float[@name='Time']").text)
        poses = {}

        def walk(item):
            for p in item.findall("Item"):
                if p.get("class") != "Pose":
                    continue
                nm = p.find("Properties/string[@name='Name']").text
                v = {c.tag: float(c.text) for c in p.find("Properties/CoordinateFrame[@name='CFrame']")}
                poses[nm] = (np.array([[v[f"R{i}{k}"] for k in range(3)] for i in range(3)]),
                             np.array([v["X"], v["Y"], v["Z"]]))
                walk(p)
        walk(kf)
        out.append((t, poses))
    out.sort(key=lambda f: f[0])
    return out


def roundtrip_error(path, frames):
    """Relit le fichier, rejoue l'equation du moteur (avec le
    HumanoidRootPart de chaque frame) et renvoie l'ecart max (position en
    studs, angle en degres) par part."""
    back = read_kfseq(path)
    worst = {}
    for (t, world), (t2, poses) in zip(frames, back):
        assert abs(t - t2) < 1e-6
        solved = solve(poses, root=world["HumanoidRootPart"])
        for part in PART_ORDER:
            r, p = world[part]
            r2, p2 = solved[part]
            dp = float(np.linalg.norm(p - p2))
            # angle stable pres de 0 (arccos(trace) perd ~0.05 deg en float32)
            da = float(np.degrees(2 * np.arcsin(min(1.0, np.linalg.norm(r - r2) / (2 * np.sqrt(2))))))
            w = worst.setdefault(part, [0.0, 0.0])
            w[0], w[1] = max(w[0], dp), max(w[1], da)
    return worst
