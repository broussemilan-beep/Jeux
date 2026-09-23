"""
Export Roblox de la choregraphie construite avec le cerveau d'animateur :
KeyframeSequence natif (.rbxmx) + verification ALLER-RETOUR par
l'equation du moteur (resolve_rbxmx : Part1 = Part0 * C0 * T * C1^-1 avec
les C0/C1 du vrai rig) -- jamais "ca doit marcher parce que l'apercu est
bon".

Point d'attention (verifie ici, pas suppose) : dans l'apercu, le bassin
(HumanoidRootPart) porte sa hauteur ABSOLUE (~3 studs : pieds au sol).
En jeu, le Humanoid tient deja le HumanoidRootPart a la hauteur de
hanche ; la translation du RootJoint doit donc etre l'ECART au repos,
sinon le personnage flotterait 3 studs trop haut. REST_ROOT est mesure
par FK (pose de repos, semelles a y=0), pas ecrit de memoire.

Usage : python3 export_roblox.py
Sortie : ../output/black_hole_r6.rbxmx
"""
import copy
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "_shared"))

import pipeline  # noqa: E402
import resolve_rbxmx  # noqa: E402
import r6_rig  # noqa: E402
from export_kfseq import export_keyframe_sequence  # noqa: E402
from animator_brain.rig_math import Rig, fk_pose, part_tip  # noqa: E402

OUT = os.path.join(HERE, "..", "output", "black_hole_r6.rbxmx")


def rest_root_height(rig):
    """Hauteur du bassin au repos, semelles exactement a y = 0 (FK)."""
    wp, wr = fk_pose(rig, {}, (0.0, 0.0, 0.0))
    foot_y = min(part_tip(rig, wp, wr, l)[1] for l in ("Right Leg", "Left Leg"))
    return -foot_y


def main():
    rig = Rig.from_module(r6_rig)
    rest_y = rest_root_height(rig)
    samples, _ = pipeline.build_samples(sample_hz=60)

    # ecart au repos pour la translation du RootJoint
    exp = copy.deepcopy(samples)
    exp["HumanoidRootPart"] = [(t, r, (p[0], p[1] - rest_y, p[2]), w) for (t, r, p, w) in exp["HumanoidRootPart"]]
    path, n = export_keyframe_sequence(exp, 60, OUT, anim_name="R6_BlackHole", decimate_to_hz=30)
    print(f"ecrit {path} : {n} keyframes (30 Hz), hauteur de repos du bassin = {rest_y:.4f} studs (FK)")

    ign = resolve_rbxmx.ignored_poses(path)
    print("poses ignorees par l'Animator :", "aucune" if not ign else ign)

    # aller-retour : le moteur (C0/C1 reels) doit reproduire l'apercu, a
    # REST_ROOT pres (le HumanoidRootPart du jeu est a la hauteur de hanche)
    frames = resolve_rbxmx.resolve_to_frames(path)
    times = [s[0] for s in samples["HumanoidRootPart"]]
    worst = {}
    for f in frames:
        i = int(np.argmin(np.abs(np.array(times) - f["t"])))
        for part in r6_rig.PART_ORDER:
            if part == "HumanoidRootPart":
                continue
            p_game = np.array(f[part]["p"]) + np.array([0.0, rest_y, 0.0])
            p_prev = np.array(samples[part][i][3])
            worst[part] = max(worst.get(part, 0.0), float(np.linalg.norm(p_game - p_prev)))
    print("ecart max moteur Roblox vs apercu (studs) :", {k: round(v, 4) for k, v in worst.items()})
    ok = max(worst.values()) < 0.01
    print("ALLER-RETOUR OK" if ok else "ALLER-RETOUR KO")
    return ok


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
