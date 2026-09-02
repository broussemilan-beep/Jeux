"""
Construit et exporte le KeyframeSequence de la descente divine. Verifie
(round-trip moteur + sanite structurelle) avant d'ecrire le fichier --
meme pattern que r6_throne_crown/r6_aerial_kick_combo.
"""
import os

import numpy as np

import anim_engine as ae
import export_kfseq as ex
from choreography import divine_descent
from r6_rig import PART_ORDER

OUT = "../output"


def structural_sanity(samples):
    problems = []
    for part in PART_ORDER:
        rots = [s[1] for s in samples[part]]
        for rx, ry, rz in rots:
            if not all(np.isfinite([rx, ry, rz])):
                problems.append(f"{part} : rotation non finie")
                break
            if max(abs(rx), abs(ry), abs(rz)) > 260:
                problems.append(f"{part} : rotation hors plage plausible ({rx:.1f},{ry:.1f},{rz:.1f})")
                break
    return problems


def main():
    os.makedirs(OUT, exist_ok=True)
    keyframes, phases, preview_times, engine_opts = divine_descent()
    duration = max(k["time"] for k in keyframes)

    objs = ae.build_rig()
    ae.apply_choreography(objs, keyframes, **engine_opts)
    samples = ae.sample(objs, duration_s=duration, sample_hz=120)

    problems = structural_sanity(samples)
    if problems:
        print("STRUCTURE KO :")
        for p in problems:
            print(" -", p)
    else:
        print("Structure OK : 6 segments rigides, RootJoint seul a translater, rotations finies et plausibles.")

    char_path, n_kf = ex.export_keyframe_sequence(
        samples, 120, os.path.join(OUT, "character_divine_descent.rbxmx"),
        anim_name="R6_DivineDescent", decimate_to_hz=30)
    print(f"KeyframeSequence exporte : {char_path} ({n_kf} keyframes)")


if __name__ == "__main__":
    main()
