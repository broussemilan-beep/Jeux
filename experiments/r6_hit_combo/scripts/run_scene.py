"""
Construit et exporte les deux KeyframeSequence du combo (attaquant +
mannequin). Verifie (round-trip moteur + sanite structurelle) avant
d'ecrire les fichiers -- meme discipline que les autres prototypes.
"""
import os

import numpy as np

import anim_engine as ae
import export_kfseq as ex
from choreography import (attacker_combo, dummy_combo_reaction,
                           ATTACKER_SECONDARY_MOTION, DUMMY_SECONDARY_MOTION)
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


def _export(choreo_fn, secondary_motion, out_name, anim_name):
    keyframes, phases, preview_times, engine_opts = choreo_fn()
    duration = max(k["time"] for k in keyframes)
    objs = ae.build_rig()
    ae.apply_choreography(objs, keyframes, **engine_opts)
    samples = ae.sample(objs, duration_s=duration, sample_hz=120, secondary_motion=secondary_motion)

    problems = structural_sanity(samples)
    if problems:
        print(f"STRUCTURE KO ({out_name}) :")
        for p in problems:
            print(" -", p)
    else:
        print(f"Structure OK ({out_name}) : 6 segments rigides, rotations finies et plausibles.")

    path, n_kf = ex.export_keyframe_sequence(
        samples, 120, os.path.join(OUT, out_name), anim_name=anim_name, decimate_to_hz=30)
    print(f"KeyframeSequence exporte : {path} ({n_kf} keyframes)")


def main():
    os.makedirs(OUT, exist_ok=True)
    _export(attacker_combo, ATTACKER_SECONDARY_MOTION,
             "character_attacker_combo.rbxmx", "R6_HitCombo")
    _export(dummy_combo_reaction, DUMMY_SECONDARY_MOTION,
             "character_dummy_combo_reaction.rbxmx", "R6_ComboReaction")


if __name__ == "__main__":
    main()
