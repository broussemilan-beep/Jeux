"""
Package Roblox pret a glisser dans Studio : output/M1_Technique.rbxmx

    Folder M1_Technique
      Model Attaquant        R6 genere depuis les C0/C1 du vrai rig, regarde -Z
      Model Victime          R6, place devant l'attaquant et tourne vers lui
      Folder Animations      KeyframeSequence M1_Attaquant (marqueurs trail_on /
                             hit / trail_off) + M1_Victime_Reaction
      ModuleScript M1Technique   (luau/M1Technique.luau)
      Script Demo            RunContext = Client : rejoue le coup en boucle en Play

Puis verifie le fichier ECRIT (relu) : references uniques et resolues,
pose de repos coherente avec les Motor6D (Part1 = Part0*C0*C1^-1),
visage sur la face avant (-Z), victime devant/face a l'attaquant, marqueurs.

Usage : python3 build_roblox_package.py
"""
import json
import os
import sys
import xml.etree.ElementTree as ET

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
OUT = os.path.join(ROOT, "output")
RIG = json.load(open(os.path.join(HERE, "..", "..", "_shared", "animator_brain", "data", "r6_rig.json")))
SCENE = json.load(open(os.path.join(OUT, "scene.json")))
DIST = round(SCENE["distance"], 3)

COLORS = {
    "Attaquant": {"Head": (234, 184, 146), "Torso": (33, 84, 185), "Left Arm": (234, 184, 146),
                  "Right Arm": (234, 184, 146), "Left Leg": (39, 70, 45), "Right Leg": (39, 70, 45),
                  "HumanoidRootPart": (163, 162, 165)},
    "Victime": {"Head": (163, 162, 165), "Torso": (120, 120, 124), "Left Arm": (163, 162, 165),
                "Right Arm": (163, 162, 165), "Left Leg": (91, 93, 105), "Right Leg": (91, 93, 105),
                "HumanoidRootPart": (163, 162, 165)},
}

_ref = [0]


def nref():
    _ref[0] += 1
    return f"RBXM1{_ref[0]:06d}"


def cframe_el(parent, name, rot, pos, tag="CoordinateFrame"):
    el = ET.SubElement(parent, tag, {"name": name})
    for t, v in zip(("X", "Y", "Z"), pos):
        ET.SubElement(el, t).text = repr(float(v))
    for i in range(3):
        for j in range(3):
            ET.SubElement(el, f"R{i}{j}").text = repr(float(rot[i][j]))
    return el


def vec3(parent, name, v):
    el = ET.SubElement(parent, "Vector3", {"name": name})
    for t, x in zip(("X", "Y", "Z"), v):
        ET.SubElement(el, t).text = repr(float(x))


def prop(parent, kind, name, value):
    ET.SubElement(parent, kind, {"name": name}).text = str(value)


def item(parent, cls, name):
    it = ET.SubElement(parent, "Item", {"class": cls, "referent": nref()})
    props = ET.SubElement(it, "Properties")
    prop(props, "string", "Name", name)
    return it, props


def rest_world(root_rot, root_pos):
    """CFrames monde au repos par l'equation du moteur (Transform = identite)."""
    world = {"HumanoidRootPart": (np.asarray(root_rot, float), np.asarray(root_pos, float))}
    for part in RIG["part_order"]:
        if part == "HumanoidRootPart":
            continue
        j = next(j for j in RIG["joints"].values() if j["part1"] == part)
        r0, p0 = world[j["part0"]]
        j0, c0 = np.array(j["C0"]["rot"]), np.array(j["C0"]["pos"])
        j1, c1 = np.array(j["C1"]["rot"]), np.array(j["C1"]["pos"])
        rot = j0 @ j1.T
        world[part] = (r0 @ rot, p0 + r0 @ (c0 - rot @ c1))
    return world


def build_rig(parent, name, root_rot, root_pos):
    model, mprops = item(parent, "Model", name)
    world = rest_world(root_rot, root_pos)
    parts = {}
    for part in RIG["part_order"]:
        it, p = item(model, "Part", part)
        r, pos = world[part]
        cframe_el(p, "CFrame", r, pos)
        vec3(p, "size", RIG["part_sizes"][part])
        c = COLORS[name][part]
        prop(p, "Color3uint8", "Color3uint8", (255 << 24) | (c[0] << 16) | (c[1] << 8) | c[2])
        prop(p, "bool", "Anchored", "true" if part == "HumanoidRootPart" else "false")
        prop(p, "bool", "CanCollide", "false")
        prop(p, "float", "Transparency", "1" if part == "HumanoidRootPart" else "0")
        prop(p, "token", "TopSurface", 0)
        prop(p, "token", "BottomSurface", 0)
        prop(p, "token", "shape", 1)
        prop(p, "token", "Material", 256)
        parts[part] = it
    head = parts["Head"]
    _m, mp = item(head, "SpecialMesh", "Mesh")
    prop(mp, "token", "MeshType", 0)  # Head
    vec3(mp, "Scale", (1.25, 1.25, 1.25))
    _d, dp = item(head, "Decal", "face")
    tex = ET.SubElement(dp, "Content", {"name": "Texture"})
    ET.SubElement(tex, "url").text = "rbxasset://textures/face.png"
    prop(dp, "token", "Face", 5)  # Front = -Z : le visage regarde vers l'avant
    for jname, j in RIG["joints"].items():
        host = parts["HumanoidRootPart"] if jname == "RootJoint" else parts["Torso"]
        _it, jp = item(host, "Motor6D", jname)
        ET.SubElement(jp, "Ref", {"name": "Part0"}).text = parts[j["part0"]].get("referent")
        ET.SubElement(jp, "Ref", {"name": "Part1"}).text = parts[j["part1"]].get("referent")
        cframe_el(jp, "C0", j["C0"]["rot"], j["C0"]["pos"])
        cframe_el(jp, "C1", j["C1"]["rot"], j["C1"]["pos"])
        prop(jp, "float", "MaxVelocity", 0.1)
    hum, hp = item(model, "Humanoid", "Humanoid")
    prop(hp, "token", "RigType", 0)  # R6
    prop(hp, "token", "DisplayDistanceType", 2)  # None
    item(hum, "Animator", "Animator")
    ET.SubElement(mprops, "Ref", {"name": "PrimaryPart"}).text = parts["HumanoidRootPart"].get("referent")
    return model


def copy_kfs(parent, path, markers_expected):
    src = ET.parse(path).getroot().find("Item")
    assert src.get("class") == "KeyframeSequence"

    def reref(el):
        if el.tag == "Item":
            el.set("referent", nref())
        for ch in el:
            reref(ch)
    reref(src)
    parent.append(src)
    n = len(src.findall(".//Item[@class='KeyframeMarker']"))
    assert n == markers_expected, (path, n)
    return src


def script_item(parent, cls, name, source_path, run_context=None):
    _it, p = item(parent, cls, name)
    src = open(source_path).read()
    ET.SubElement(p, "ProtectedString", {"name": "Source"}).text = src
    if run_context is not None:
        prop(p, "token", "RunContext", run_context)


def build():
    root = ET.Element("roblox", {"xmlns:xmime": "http://www.w3.org/2005/05/xmlmime",
                                 "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
                                 "xsi:noNamespaceSchemaLocation": "http://www.roblox.com/roblox.xsd",
                                 "version": "4"})
    folder, _fp = item(root, "Folder", "M1_Technique")
    att_rot, att_pos = np.eye(3), np.array([0.0, 3.0, 0.0])
    ry = np.array([[-1.0, 0, 0], [0, 1.0, 0], [0, 0, -1.0]])        # CFrame.Angles(0, pi, 0)
    vic_rot, vic_pos = ry, att_pos + att_rot @ np.array([0.0, 0.0, -DIST])
    build_rig(folder, "Attaquant", att_rot, att_pos)
    build_rig(folder, "Victime", vic_rot, vic_pos)
    anims, _ap = item(folder, "Folder", "Animations")
    copy_kfs(anims, os.path.join(OUT, "m1_attaquant.rbxmx"), 3)
    copy_kfs(anims, os.path.join(OUT, "m1_victime_reaction.rbxmx"), 0)
    script_item(folder, "ModuleScript", "M1Technique", os.path.join(ROOT, "luau", "M1Technique.luau"))
    script_item(folder, "Script", "Demo", os.path.join(ROOT, "luau", "Demo.client.luau"), run_context=2)
    tree = ET.ElementTree(root)
    ET.indent(tree, space="  ")
    path = os.path.join(OUT, "M1_Technique.rbxmx")
    tree.write(path, encoding="utf-8", xml_declaration=True)
    return path


def read_cf(el):
    v = {c.tag: float(c.text) for c in el}
    return np.array([[v[f"R{i}{j}"] for j in range(3)] for i in range(3)]), np.array([v["X"], v["Y"], v["Z"]])


def verify(path):
    """Relit le fichier ECRIT et controle structure, pose de repos et sens."""
    root = ET.parse(path).getroot()
    items = root.findall(".//Item")
    refs = [i.get("referent") for i in items]
    report = {"instances": len(items), "referents_uniques": len(refs) == len(set(refs))}
    by_ref = {i.get("referent"): i for i in items}
    name = lambda it: it.find("Properties/string[@name='Name']").text  # noqa: E731
    folder = root.find("Item")
    rigs = {name(m): m for m in folder.findall("Item[@class='Model']")}
    worst_rest = 0.0
    sens = {}
    for rig_name, model in rigs.items():
        parts = {name(p): p for p in model.findall("Item[@class='Part']")}
        cfs = {n: read_cf(p.find("Properties/CoordinateFrame[@name='CFrame']")) for n, p in parts.items()}
        for m in model.findall(".//Item[@class='Motor6D']"):
            p0 = by_ref[m.find("Properties/Ref[@name='Part0']").text]
            p1 = by_ref[m.find("Properties/Ref[@name='Part1']").text]
            j0, c0 = read_cf(m.find("Properties/CoordinateFrame[@name='C0']"))
            j1, c1 = read_cf(m.find("Properties/CoordinateFrame[@name='C1']"))
            r0, q0 = cfs[name(p0)]
            r1, q1 = cfs[name(p1)]
            pr = r0 @ j0 @ j1.T
            pp = q0 + r0 @ (c0 - j0 @ j1.T @ c1)
            worst_rest = max(worst_rest, float(np.abs(pr - r1).max()), float(np.abs(pp - q1).max()))
        prim = model.find("Properties/Ref[@name='PrimaryPart']").text
        assert name(by_ref[prim]) == "HumanoidRootPart"
        face = parts["Head"].find("Item[@class='Decal']/Properties/token[@name='Face']").text
        look = cfs["Head"][0] @ np.array([0.0, 0.0, -1.0])     # face Front = -Z local
        sens[rig_name] = {"visage_face_avant": face == "5", "regard": np.round(look, 3).tolist(),
                          "hrp": np.round(cfs["HumanoidRootPart"][1], 3).tolist()}
    report["pose_repos_coherente_max_ecart"] = worst_rest
    a, v = sens["Attaquant"], sens["Victime"]
    report["sens"] = {
        "attaquant_regarde_moins_z": a["regard"] == [0.0, 0.0, -1.0] or np.allclose(a["regard"], [0, 0, -1]),
        "victime_devant": bool(np.allclose(v["hrp"], [0, 3, -DIST], atol=1e-3)),
        "victime_face_a_l_attaquant": bool(np.allclose(v["regard"], [0, 0, 1], atol=1e-3)),
        "visages_sur_face_avant": a["visage_face_avant"] and v["visage_face_avant"],
    }
    kfs = folder.findall("Item[@class='Folder']/Item[@class='KeyframeSequence']")
    report["animations"] = {name(k): len(k.findall(".//Item[@class='KeyframeMarker']")) for k in kfs}
    report["scripts"] = [(i.get("class"), name(i)) for i in folder.findall("Item")
                         if i.get("class") in ("Script", "ModuleScript")]
    rc = folder.find("Item[@class='Script']/Properties/token[@name='RunContext']")
    report["demo_run_context_client"] = rc is not None and rc.text == "2"
    return report


if __name__ == "__main__":
    p = build()
    rep = verify(p)
    print(json.dumps(rep, indent=1, ensure_ascii=False, default=str))
    ok = rep["referents_uniques"] and rep["pose_repos_coherente_max_ecart"] < 1e-6 and all(rep["sens"].values()) \
        and rep["animations"] == {"M1_Attaquant": 3, "M1_Victime_Reaction": 0} and rep["demo_run_context_client"]
    print("PACKAGE OK" if ok else "PACKAGE KO", "->", p)
    sys.exit(0 if ok else 1)
