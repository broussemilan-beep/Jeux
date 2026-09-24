"""
Auto-test de la chaine rig V2.22 -> KeyframeSequence Roblox.

1. Anime le vrai rig par ses CONTROLES (bassin, poitrine, main droite en
   IK, bras gauche FK, jambe gauche IK), 60 fps, courbes Bezier.
2. Cuit les 7 parts (bake_parts) et ecrit un .rbxmx.
3. Aller-retour : relit le fichier et rejoue l'equation du moteur.
4. Verification INDEPENDANTE : les sommets reels des maillages du rig
   (MBlocky, deformes par Blender) sont compares aux sommets predits par
   les CFrames du fichier. Ce test ne passe pas par les os : il attrape une
   erreur de repere, de delta ou de C0/C1.

Usage : python3 tests/v222_export_selftest.py /chemin/Blender_R6.blend out.rbxmx
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
from animator_brain import v222_rig as V  # noqa: E402
from animator_brain import roblox_export as X  # noqa: E402


def mesh_vertices_roblox():
    import bpy
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    out = {}
    for p in ("Torso", "Head", "Left Arm", "Right Arm", "Left Leg", "Right Leg"):
        e = bpy.data.objects[p + "_MBlocky"].evaluated_get(dg)
        out[p] = np.array([X.B2R @ np.array(e.matrix_world @ v.co) for v in e.data.vertices])
    return out


def main(blend, out):
    import bpy
    V.open_rig(blend)
    S = bpy.context.scene
    S.frame_set(0)
    rest_v = mesh_vertices_roblox()
    V.key_setting(0, "Right Arm", "IK/FK", 1.0)
    V.key_controls(0, {"LowerTorso-FK": {"location": (0, 0, 0), "rotation_euler": (0, 0, 0)},
                       "UpperTorso-IKTarget": {"location": (0, 0, 0)},
                       "RightArm-IK": {"location": (0, 0, 0)},
                       "LeftArm_FK": {"rotation_euler": (0, 0, 0)},
                       "LeftLeg-IK": {"location": (0, 0, 0)}})
    V.key_controls(12, {"LowerTorso-FK": {"location": (0, -0.5, 0.2), "rotation_euler": (10, -25, 5)},
                        "UpperTorso-IKTarget": {"location": (0, 0.3, 0)},
                        "RightArm-IK": {"location": (0, -0.4, 0.3)},
                        "LeftArm_FK": {"rotation_euler": (-60, 0, 20)},
                        "LeftLeg-IK": {"location": (0, 0.4, 0.6)}})
    V.key_controls(20, {"LowerTorso-FK": {"location": (0, -0.3, -0.3), "rotation_euler": (-15, 30, -5)},
                        "UpperTorso-IKTarget": {"location": (0, 0.6, 0)},
                        "RightArm-IK": {"location": (0, 1.6, 0.9)},
                        "LeftArm_FK": {"rotation_euler": (30, 0, -10)},
                        "LeftLeg-IK": {"location": (0, 0.0, 0.0)}})
    V.key_controls(36, {"LowerTorso-FK": {"location": (0, 0, 0), "rotation_euler": (0, 0, 0)},
                        "UpperTorso-IKTarget": {"location": (0, 0, 0)},
                        "RightArm-IK": {"location": (0, 0, 0)},
                        "LeftArm_FK": {"rotation_euler": (0, 0, 0)},
                        "LeftLeg-IK": {"location": (0, 0, 0)}})
    frames = V.bake_parts(0, 36)
    # garde-fou : l'animation cuite doit BOUGER et passer par les valeurs
    # clees (un clip statique passerait tous les autres tests trivialement)
    def yaw_pitch(r):
        f = r @ np.array([0.0, 0.0, -1.0])
        return np.degrees(np.arctan2(-f[0], -f[2])), np.degrees(np.arcsin(np.clip(f[1], -1, 1)))
    y12, p12 = yaw_pitch(frames[12][1]["Torso"][0])
    y20, p20 = yaw_pitch(frames[20][1]["Torso"][0])
    motion = max(np.linalg.norm(frames[i][1][p][1] - frames[0][1][p][1]) for i in range(37) for p in X.PART_ORDER)
    print(f"torse cuit : f12 lacet {y12:.1f} (cle -25) ; f20 lacet {y20:.1f} (cle 30) ; deplacement max {motion:.2f} stud")
    # tolerance 5 deg : tangage et roulis cles en meme temps decalent un peu
    # le lacet MESURE du vecteur avant (composition des angles)
    moving = abs(y12 - (-25)) < 5 and abs(y20 - 30) < 5 and motion > 0.5
    X.write_kfseq(frames, out, "V222_Selftest", markers=[(20 / 60, "hit", "right_hand")])
    rt = X.roundtrip_error(out, frames)
    print("aller-retour (pos studs, angle deg) :", {k: (round(a, 6), round(b, 5)) for k, (a, b) in rt.items()})

    # verification independante par les sommets
    back = X.read_kfseq(out)
    worst = 0.0
    for f, (t, poses) in zip(range(0, 37), back):
        S.frame_set(f)
        cur = mesh_vertices_roblox()
        solved = X.solve(poses, root=frames[f][1]["HumanoidRootPart"])
        for p, v0 in rest_v.items():
            c = np.array(X.REST_CENTER[p])
            r, pos = solved[p]
            pred = (r @ (v0 - c).T).T + pos
            worst = max(worst, float(np.abs(pred - cur[p]).max()))
    print(f"sommets reels vs fichier : ecart max {worst:.6f} stud sur 37 frames x 6 parts")
    ok = max(a for a, _b in rt.values()) < 1e-3 and worst < 0.01 and moving
    print("CHAINE V2.22 -> ROBLOX OK" if ok else "CHAINE KO")
    return ok


if __name__ == "__main__":
    sys.exit(0 if main(sys.argv[1], sys.argv[2]) else 1)
