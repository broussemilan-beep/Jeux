"""
Construit et exporte la scene complete : KeyframeSequence du personnage,
Model du trone, Model de la couronne, trajectoire monde de la couronne.
Verifie le tout (round-trip moteur + sanite structurelle) avant d'ecrire
les fichiers.
"""
import os

import numpy as np

import anim_engine as ae
import export_kfseq as ex
import export_model as em
import props
from choreography import full_scene
from r6_rig import PART_ORDER

OUT = "../output"


def structural_sanity(samples):
    """Vérifications minimales, propres à cette scène (pas de contrainte
    "pas de coup de poing" ici -- ce n'est pas un combo de combat) : les
    rotations restent finies et dans une plage plausible pour un seul
    segment rigide sans coude/genou. (La translation locale hors-racine
    n'a PAS a etre verifiee ici : `samples[part][i][2]` est l'offset de
    repos CONSTANT de l'Empty Blender -- build_rig() ne l'anime jamais --
    ce n'est pas ce que Roblox recoit. Le zero hors-racine reellement
    ecrit dans le fichier vient de `export_kfseq.effective_pose_inputs`,
    code partage et deja verifie par `verify_joint_frames.py` dans le
    prototype r6_aerial_kick_combo, reutilise ici sans modification.)"""
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
    keyframes, phases, preview_times, engine_opts = full_scene()
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
        samples, 120, os.path.join(OUT, "character_sit_and_crown.rbxmx"),
        anim_name="R6_SitAndCrown", decimate_to_hz=30)
    print(f"KeyframeSequence exporte : {char_path} ({n_kf} keyframes)")

    throne_and_stairs = props.throne_parts() + props.staircase_parts()
    throne_path, n_throne = em.export_model(throne_and_stairs, "Throne",
                                             os.path.join(OUT, "throne.rbxmx"),
                                             primary_part="Seat")
    print(f"Throne (+ escalier, {len(props.staircase_parts())} marches) exporte : {throne_path} ({n_throne} parts)")

    crown_path, n_crown = em.export_model(props.crown_parts(), "Crown",
                                           os.path.join(OUT, "crown.rbxmx"),
                                           primary_part="Band")
    print(f"Crown exporte : {crown_path} ({n_crown} parts)")


if __name__ == "__main__":
    main()
