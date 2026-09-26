"""
Importe la geometrie du rig depuis un VRAI fichier de rig R6 (.rbxmx),
au lieu de constantes ecrites a la main.

Source : rig/RigR6.rbxmx (dépôt Adonis, MIT -- voir rig/PROVENANCE.md).

Extrait, pour chaque Part : son nom et sa taille ; pour chaque Motor6D :
Part0, Part1, C0 et C1 (translation ET matrice de rotation). On ne lit
JAMAIS les CFrame monde des parts comme reference de repos : ce modele est
sauvegarde retourne (Ry(180) sur toutes les parts), alors que les C0/C1
sont locaux aux parts donc invariants par rotation globale du modele.

Lance directement, ce script ecrit rig/r6_rig.json et affiche la
comparaison avec les valeurs qui etaient codees en dur.
"""
import json
import os
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
RIG_XML = os.path.join(HERE, "..", "rig", "RigR6.rbxmx")
RIG_JSON = os.path.join(HERE, "..", "rig", "r6_rig.json")

PART_CLASSES = ("Part", "MeshPart")


def _index_referents(root):
    by_ref = {}

    def walk(el):
        for item in el.findall("Item"):
            ref = item.get("referent")
            if ref:
                by_ref[ref] = item
            walk(item)

    walk(root)
    return by_ref


def _name(item):
    node = item.find("Properties/string[@name='Name']")
    return node.text if node is not None else None


def _vector3(props, name):
    el = props.find(f"Vector3[@name='{name}']")
    if el is None:
        return None
    vals = {c.tag: float(c.text) for c in el}
    return [vals["X"], vals["Y"], vals["Z"]]


def _cframe(props, name):
    el = props.find(f"CoordinateFrame[@name='{name}']")
    if el is None:
        return None
    v = {c.tag: float(c.text) for c in el}
    return {
        "pos": [v["X"], v["Y"], v["Z"]],
        "rot": [[v[f"R{i}{j}"] for j in range(3)] for i in range(3)],
    }


def parse_rig(xml_path=RIG_XML):
    root = ET.parse(xml_path).getroot()
    by_ref = _index_referents(root)

    parts = {}
    joints = {}
    for item in by_ref.values():
        cls = item.get("class")
        props = item.find("Properties")
        if props is None:
            continue
        if cls in PART_CLASSES:
            size = _vector3(props, "size") or _vector3(props, "Size")
            if size:
                parts[_name(item)] = size
        elif cls == "Motor6D":
            p0 = props.find("Ref[@name='Part0']")
            p1 = props.find("Ref[@name='Part1']")
            if p0 is None or p1 is None:
                continue
            n0 = _name(by_ref[p0.text]) if p0.text in by_ref else None
            n1 = _name(by_ref[p1.text]) if p1.text in by_ref else None
            if not n0 or not n1:
                continue
            joints[_name(item)] = {
                "part0": n0,
                "part1": n1,
                "C0": _cframe(props, "C0"),
                "C1": _cframe(props, "C1"),
            }
    return parts, joints


def build_json(xml_path=RIG_XML, out_path=RIG_JSON):
    parts, joints = parse_rig(xml_path)
    parent = {j["part1"]: j["part0"] for j in joints.values()}

    # Ordre topologique (parent avant enfant) depuis la racine.
    roots = [p for p in parts if p not in parent]
    order = []
    pending = list(roots)
    while pending:
        cur = pending.pop(0)
        order.append(cur)
        pending += sorted(p for p, par in parent.items() if par == cur)

    data = {
        "source": "https://github.com/Epix-Incorporated/Adonis "
                  "MainModule/Server/Dependencies/Assets/RigR6.rbxmx (MIT)",
        "part_sizes": parts,
        "joints": joints,
        "parent": parent,
        "part_order": order,
    }
    with open(out_path, "w") as f:
        json.dump(data, f, indent=2, sort_keys=True)
    return data


# Valeurs qui etaient CODEES EN DUR avant cet import, gardees ici uniquement
# pour la comparaison (elles ne servent plus a rien d'autre).
HARDCODED_SIZES = {
    "HumanoidRootPart": [2.0, 2.0, 1.0], "Torso": [2.0, 2.0, 1.0],
    "Head": [2.0, 1.0, 1.0], "Right Arm": [1.0, 2.0, 1.0],
    "Left Arm": [1.0, 2.0, 1.0], "Right Leg": [1.0, 2.0, 1.0],
    "Left Leg": [1.0, 2.0, 1.0],
}
HARDCODED_C0C1 = {
    "RootJoint": ([0.0, 0.0, 0.0], [0.0, 0.0, 0.0]),
    "Neck": ([0.0, 1.0, 0.0], [0.0, -0.5, 0.0]),
    "Right Shoulder": ([1.0, 0.5, 0.0], [-0.5, 0.5, 0.0]),
    "Left Shoulder": ([-1.0, 0.5, 0.0], [0.5, 0.5, 0.0]),
    "Right Hip": ([1.0, -1.0, 0.0], [0.5, 1.0, 0.0]),
    "Left Hip": ([-1.0, -1.0, 0.0], [-0.5, 1.0, 0.0]),
}
IDENTITY = [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]


def compare(data):
    print("=== tailles de parts ===")
    for part, size in sorted(data["part_sizes"].items()):
        old = HARDCODED_SIZES.get(part)
        verdict = "identique" if old == size else f"DIFFERENT (code en dur: {old})"
        print(f"  {part:<18} {size}  -> {verdict}")

    print()
    print("=== C0 / C1 : translations ===")
    for jname, j in sorted(data["joints"].items()):
        old = HARDCODED_C0C1.get(jname)
        c0, c1 = j["C0"]["pos"], j["C1"]["pos"]
        if old and [round(x, 6) for x in c0] == old[0] and [round(x, 6) for x in c1] == old[1]:
            print(f"  {jname:<16} identique")
        else:
            print(f"  {jname:<16} DIFFERENT reel C0={c0} C1={c1} / code en dur {old}")

    print()
    print("=== C0 / C1 : ROTATIONS (le point qui etait faux) ===")
    for jname, j in sorted(data["joints"].items()):
        r0 = [[round(v, 3) for v in row] for row in j["C0"]["rot"]]
        r1 = [[round(v, 3) for v in row] for row in j["C1"]["rot"]]
        same01 = r0 == r1
        print(f"  {jname:<16} identite ? C0={'oui' if r0 == IDENTITY else 'NON'} "
              f"C1={'oui' if r1 == IDENTITY else 'NON'}   C0==C1 ? {'oui' if same01 else 'NON'}")
        if r0 != IDENTITY:
            print(f"                   C0.rot = {r0}")


if __name__ == "__main__":
    data = build_json()
    print(f"ecrit {os.path.normpath(RIG_JSON)}")
    print(f"parts: {len(data['part_sizes'])}, joints: {len(data['joints'])}")
    print(f"ordre: {data['part_order']}")
    print()
    compare(data)
