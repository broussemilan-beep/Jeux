"""
Rejoue un KeyframeSequence exporte EN PASSANT PAR L'EQUATION DU MOTEUR,
avec les C0/C1 du vrai rig -- au lieu de la cinematique directe maison.

C'est la verification qui manquait a tout ce travail. Jusqu'ici les
apercus (stick-figures, courbes) etaient calcules a partir des rotations
que j'avais ECRITES, avec mes propres conventions. Ils montraient donc
fidelement mon intention, jamais ce que Roblox en ferait -- raison pour
laquelle ni le mauvais repere de joint ni la pose racine ignoree n'ont
ete vus pendant cinq cycles de "verification visuelle".

Ici on part du fichier .rbxmx REEL, on lit chaque Pose, et on resout :

    Part1.CFrame = Part0.CFrame * C0 * Transform * C1^-1

en descendant la hierarchie des Motor6D du rig importe. Une Pose dont le
nom ne correspond au Part1 d'aucun Motor6D est IGNOREE, exactement comme
le fait l'Animator -- c'est ce qui rend le probleme de la pose
HumanoidRootPart visible plutot que theorique.
"""
import json
import os
import xml.etree.ElementTree as ET

import numpy as np

from r6_rig import JOINTS, PARENT, PART_ORDER, PART_SIZES, joint_for_part

HERE = os.path.dirname(os.path.abspath(__file__))


def parse_keyframe_sequence(path):
    """Retourne [(time, {part_name: (rot 3x3, pos 3)}), ...] trie par temps."""
    root = ET.parse(path).getroot()
    kfseq = root.find("Item")
    frames = []
    for kf in kfseq.findall("Item"):
        if kf.get("class") != "Keyframe":
            continue
        t = float(kf.find("Properties/float[@name='Time']").text)
        poses = {}

        def walk(item):
            for pose in item.findall("Item"):
                if pose.get("class") != "Pose":
                    continue
                name = pose.find("Properties/string[@name='Name']").text
                cf = pose.find("Properties/CoordinateFrame[@name='CFrame']")
                v = {c.tag: float(c.text) for c in cf}
                rot = np.array([[v[f"R{i}{j}"] for j in range(3)] for i in range(3)])
                pos = np.array([v["X"], v["Y"], v["Z"]])
                poses[name] = (rot, pos)
                walk(pose)

        walk(kf)
        frames.append((t, poses))
    frames.sort(key=lambda f: f[0])
    return frames


def solve_frame(poses, warn=None):
    """Applique l'equation du moteur en descendant la hierarchie du rig.
    Retourne {part: (rot_monde 3x3, pos_monde 3)}, HumanoidRootPart pris a
    l'identite (c'est le jeu, pas l'animation, qui le place)."""
    world = {"HumanoidRootPart": (np.eye(3), np.zeros(3))}
    for part in PART_ORDER:
        if part == "HumanoidRootPart":
            continue
        jname = joint_for_part(part)
        if jname is None:
            continue
        j = JOINTS[jname]
        parent = j["part0"]
        p_rot, p_pos = world[parent]

        j0 = np.array(j["C0"]["rot"]); c0 = np.array(j["C0"]["pos"])
        j1 = np.array(j["C1"]["rot"]); c1 = np.array(j["C1"]["pos"])

        if part in poses:
            t_rot, t_pos = poses[part]
        else:
            t_rot, t_pos = np.eye(3), np.zeros(3)

        # C0 * T * C1^-1, puis compose sur le parent.
        rot = j0 @ t_rot @ j1.T
        pos = c0 + j0 @ t_pos - rot @ c1
        world[part] = (p_rot @ rot, p_pos + p_rot @ pos)

    if warn is not None:
        drivable = {j["part1"] for j in JOINTS.values()}
        for name in poses:
            if name not in drivable and name != "HumanoidRootPart":
                warn.add(name)
    return world


def ignored_poses(path):
    """Noms de Pose qui ne pilotent aucun Motor6D (donc ignorees par
    l'Animator), et amplitude de ce qu'elles portaient."""
    frames = parse_keyframe_sequence(path)
    drivable = {j["part1"] for j in JOINTS.values()}
    report = {}
    for _t, poses in frames:
        for name, (rot, pos) in poses.items():
            if name in drivable:
                continue
            r = report.setdefault(name, {"max_translation": 0.0, "max_angle_deg": 0.0})
            r["max_translation"] = max(r["max_translation"], float(np.linalg.norm(pos)))
            ang = np.degrees(np.arccos(max(-1.0, min(1.0, (np.trace(rot) - 1) / 2))))
            r["max_angle_deg"] = max(r["max_angle_deg"], float(ang))
    return report


def resolve_to_frames(path, out_hz=30):
    """Frames pretes a dessiner : centre + matrice monde par part."""
    frames = parse_keyframe_sequence(path)
    out = []
    for t, poses in frames:
        world = solve_frame(poses)
        f = {"t": round(t, 4)}
        for part in PART_ORDER:
            rot, pos = world[part]
            f[part] = {
                "p": [round(float(v), 4) for v in pos],
                "r": [round(float(v), 5) for row in rot for v in row],
            }
        out.append(f)
    return out


if __name__ == "__main__":
    import sys
    path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        HERE, "..", "output", "cartoon_c2", "best", "combo_cartoon.rbxmx")
    ign = ignored_poses(path)
    print("Poses ne pilotant aucun Motor6D (ignorees par l'Animator) :")
    if not ign:
        print("  aucune")
    for name, r in ign.items():
        print(f"  {name}: translation max {r['max_translation']:.3f} studs, "
              f"rotation max {r['max_angle_deg']:.1f} deg")
    frames = resolve_to_frames(path)
    ys = [f["Torso"]["p"][1] for f in frames]
    print(f"\nfr Torso Y resolu par le moteur : min {min(ys):.3f}  max {max(ys):.3f}  "
          f"amplitude {max(ys)-min(ys):.3f} studs")
