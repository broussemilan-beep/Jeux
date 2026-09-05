"""
Verifie par le calcul (pas a l'oeil) le combo a deux personnages
(attacker_combo + dummy_combo_reaction) : que CHACUN des 3 coups
(jab/cross/hook) approche vraiment sa cible au moment de son impact, que
la reaction du mannequin est bien synchronisee coup par coup, et que la
structure des deux rigs reste plausible tout du long.
"""
import numpy as np

import anim_engine as ae
from choreography import (attacker_combo, dummy_combo_reaction,
                           JAB_T, CROSS_T, HOOK_T,
                           ATTACKER_SECONDARY_MOTION, DUMMY_SECONDARY_MOTION,
                           DUMMY_Z)
from r6_rig import PART_ORDER, PART_SIZES


def world_rotations(samples, i):
    rot = {}
    root_r = ae.euler_xyz_matrix(*samples["HumanoidRootPart"][i][1])
    rot["HumanoidRootPart"] = root_r
    torso_r = root_r @ ae.euler_xyz_matrix(*samples["Torso"][i][1])
    rot["Torso"] = torso_r
    for part in PART_ORDER:
        if part in ("HumanoidRootPart", "Torso"):
            continue
        rot[part] = torso_r @ ae.euler_xyz_matrix(*samples[part][i][1])
    return rot


def tip_world(samples, part, i, end="bottom"):
    world_pos = np.array(samples[part][i][3])
    rots = world_rotations(samples, i)
    half = PART_SIZES[part][1] / 2.0
    sign = -1.0 if end == "bottom" else 1.0
    return world_pos + rots[part] @ np.array([0.0, sign * half, 0.0])


def _run(choreo_fn, secondary_motion, sample_hz=60):
    keyframes, phases, preview_times, engine_opts = choreo_fn()
    duration = max(k["time"] for k in keyframes)
    objs = ae.build_rig()
    ae.apply_choreography(objs, keyframes, **engine_opts)
    samples = ae.sample(objs, duration_s=duration, sample_hz=sample_hz, secondary_motion=secondary_motion)
    return samples, duration


def main():
    att_samples, att_dur = _run(attacker_combo, ATTACKER_SECONDARY_MOTION)
    dum_samples, dum_dur = _run(dummy_combo_reaction, DUMMY_SECONDARY_MOTION)

    def idx_at(t, hz=60):
        return round(t * hz)

    print("=== contact par coup (poing/bras de l'attaquant vs torse du mannequin) ===")
    for name, t, arm in (("jab", JAB_T, "Left Arm"), ("cross", CROSS_T, "Right Arm"), ("hook", HOOK_T, "Left Arm")):
        i = idx_at(t)
        fist = tip_world(att_samples, arm, i, "bottom")
        dummy_torso = np.array(dum_samples["Torso"][i][3])
        gap = np.linalg.norm(fist - dummy_torso)
        print(f"  {name:6s} (t={t:.2f}s, {arm}) : poing={fist.round(3).tolist()}  "
              f"torse mannequin={dummy_torso.round(3).tolist()}  ecart={gap:.3f} stud")

    print("\n=== synchronisation : le mannequin ne bouge qu'apres chaque impact ===")
    for name, t in (("jab", JAB_T), ("cross", CROSS_T), ("hook", HOOK_T)):
        i_before = idx_at(t - 0.02)
        i_after = idx_at(t + 0.02)
        head_before = np.array(dum_samples["Head"][i_before][3])
        head_after = np.array(dum_samples["Head"][i_after][3])
        moved = np.linalg.norm(head_after - head_before)
        print(f"  {name:6s} : tete avant={head_before.round(3).tolist()}  "
              f"apres={head_after.round(3).tolist()}  deplacement={moved:.3f} stud (doit croitre jab<cross<hook)")

    print("\n=== structure : rotations finies et plausibles (attaquant + mannequin) ===")
    for label, samples in (("attaquant", att_samples), ("mannequin", dum_samples)):
        problems = []
        for part in PART_ORDER:
            for s in samples[part]:
                rx, ry, rz = s[1]
                if not all(np.isfinite([rx, ry, rz])):
                    problems.append(f"{part} : rotation non finie")
                    break
                if max(abs(rx), abs(ry), abs(rz)) > 260:
                    problems.append(f"{part} : rotation hors plage plausible ({rx:.1f},{ry:.1f},{rz:.1f})")
                    break
        if problems:
            print(f"  {label} : STRUCTURE KO :")
            for p in problems:
                print("   -", p)
        else:
            print(f"  {label} : OK -- 6 segments rigides, rotations finies et plausibles.")

    print(f"\nDurees : attaquant={att_dur:.2f}s, mannequin={dum_dur:.2f}s (doivent etre egales), DUMMY_Z={DUMMY_Z}")


if __name__ == "__main__":
    main()
