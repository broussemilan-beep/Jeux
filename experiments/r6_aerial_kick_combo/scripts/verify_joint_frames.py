"""
Auto-test de la conversion repere parent -> repere joint (export_kfseq).

Trois verifications :
1. Aller-retour : pour chaque joint, une rotation R ecrite en repere parent,
   convertie puis rejouee par la formule du moteur Roblox
   (Part1 = Part0 * C0 * T * C1^-1), doit redonner exactement R.
2. Pose de repos : avec T = identite, le squelette resolu doit redonner la
   silhouette R6 attendue (tete a +1.5 du torse, jambes a -2, etc.).
3. Demonstration du bug : ce que l'ancien export (T = R, sans conversion)
   produisait reellement sur un vrai rig.
"""
import math

import numpy as np

from r6_rig import JOINTS, PART_ORDER, PARENT, joint_for_part, joint_rotations, local_offset
from anim_engine import euler_xyz_matrix
from export_kfseq import to_joint_frame


def engine_solve(part, t_rot, t_pos):
    """Reproduit Part1 = Part0 * C0 * T * C1^-1, exprime dans le repere du
    parent (on prend Part0 = identite). Retourne (rotation, translation)."""
    jname = joint_for_part(part)
    j = JOINTS[jname]
    j0 = np.array(j["C0"]["rot"]); c0 = np.array(j["C0"]["pos"])
    j1 = np.array(j["C1"]["rot"]); c1 = np.array(j["C1"]["pos"])
    rot = j0 @ np.array(t_rot) @ j1.T
    pos = c0 + j0 @ np.array(t_pos) - rot @ c1
    return rot, pos


def axis_of(rot):
    """Axe et angle (deg) d'une matrice de rotation, pour affichage."""
    angle = math.degrees(math.acos(max(-1.0, min(1.0, (np.trace(rot) - 1) / 2))))
    if angle < 1e-6:
        return np.array([0.0, 0.0, 0.0]), 0.0
    ax = np.array([rot[2, 1] - rot[1, 2], rot[0, 2] - rot[2, 0], rot[1, 0] - rot[0, 1]])
    n = np.linalg.norm(ax)
    return (ax / n if n > 1e-9 else ax), angle


def test_roundtrip():
    print("=== 1. aller-retour repere parent -> joint -> moteur ===")
    rng = np.random.default_rng(7)
    worst = 0.0
    for part in PART_ORDER:
        if joint_for_part(part) is None:
            continue
        for _ in range(200):
            r = euler_xyz_matrix(*rng.uniform(-180, 180, 3))
            d = rng.uniform(-2, 2, 3) if part == "HumanoidRootPart" else np.zeros(3)
            t_rot, t_pos = to_joint_frame(part, r, tuple(d))
            back_rot, back_pos = engine_solve(part, t_rot, t_pos)
            worst = max(worst, float(np.abs(back_rot - r).max()))
            # translation attendue : pivot naturel autour du point d'attache,
            # plus d pour la racine.
            j = JOINTS[joint_for_part(part)]
            c0 = np.array(j["C0"]["pos"]); c1 = np.array(j["C1"]["pos"])
            expected_pos = c0 - r @ c1 + d
            worst = max(worst, float(np.abs(back_pos - expected_pos).max()))
        print(f"  {part:<18} ok")
    print(f"  ecart max sur 200 tirages x {len(PART_ORDER)-1} joints : {worst:.2e}")
    assert worst < 1e-9, "la conversion ne boucle pas"


def test_rest_pose():
    print()
    print("=== 2. pose de repos (T = identite) ===")
    expected = {
        "Torso": (0.0, 0.0, 0.0), "Head": (0.0, 1.5, 0.0),
        "Right Arm": (1.5, 0.0, 0.0), "Left Arm": (-1.5, 0.0, 0.0),
        "Right Leg": (0.5, -2.0, 0.0), "Left Leg": (-0.5, -2.0, 0.0),
    }
    ident = np.eye(3)
    for part, exp in expected.items():
        _, pos = engine_solve(part, ident, np.zeros(3))
        ok = np.allclose(pos, exp, atol=1e-9)
        print(f"  {part:<18} {tuple(round(v,3) for v in pos)}  attendu {exp}  {'ok' if ok else 'KO'}")
        assert ok
        assert np.allclose(pos, local_offset(joint_for_part(part)), atol=1e-9)


def test_bug_demo():
    print()
    print("=== 3. ce que faisait l'ancien export (T = R, sans conversion) ===")
    cases = [
        ("Right Leg", (60, 0, 0), "coup de pied vers l'AVANT (axe X)"),
        ("Left Leg", (60, 0, 0), "coup de pied vers l'AVANT (axe X)"),
        ("Torso", (0, 90, 0), "spin du torse (lacet, axe Y)"),
    ]
    for part, euler, label in cases:
        r = euler_xyz_matrix(*euler)
        want_axis, want_angle = axis_of(r)
        # ancien comportement : Pose.CFrame = R tel quel
        got_rot, _ = engine_solve(part, r, np.zeros(3))
        got_axis, got_angle = axis_of(got_rot)
        print(f"  {part} {euler} — {label}")
        print(f"     voulu : {want_angle:5.1f} deg autour de ({want_axis[0]:+.2f},{want_axis[1]:+.2f},{want_axis[2]:+.2f})")
        print(f"     obtenu: {got_angle:5.1f} deg autour de ({got_axis[0]:+.2f},{got_axis[1]:+.2f},{got_axis[2]:+.2f})")
        dev = math.degrees(math.acos(max(-1.0, min(1.0, float(np.dot(want_axis, got_axis))))))
        print(f"     -> meme angle, axe devie de {dev:.0f} deg")


if __name__ == "__main__":
    test_roundtrip()
    test_rest_pose()
    test_bug_demo()
    print()
    print("tous les tests passent")
