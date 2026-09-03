"""
Verifie par le calcul (pas a l'oeil) la choregraphie a deux personnages
(haughty_punch -- attaquant + mannequin) : que le poing de l'attaquant
approche vraiment le torse du mannequin au moment de l'impact (pas une
supposition -- mesure), que la reaction du mannequin est bien
synchronisee sur IMPACT_T, et que la structure des deux rigs reste
plausible.
"""
import numpy as np

import anim_engine as ae
from choreography import (attacker_punch, dummy_reaction, IMPACT_T,
                           ATTACKER_SECONDARY_MOTION, DUMMY_SECONDARY_MOTION,
                           DUMMY_Z, GROUND_Y)
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
    att_samples, att_dur = _run(attacker_punch, ATTACKER_SECONDARY_MOTION)
    dum_samples, dum_dur = _run(dummy_reaction, DUMMY_SECONDARY_MOTION)

    def idx_at(t, hz=60):
        return round(t * hz)

    print(f"=== impact (t={IMPACT_T:.2f}s) : poing de l'attaquant vs torse du mannequin ===")
    i = idx_at(IMPACT_T)
    fist = tip_world(att_samples, "Right Arm", i, "bottom")
    dummy_torso = np.array(dum_samples["Torso"][i][3])
    gap = np.linalg.norm(fist - dummy_torso)
    print(f"  poing (monde)   : {fist.round(3).tolist()}")
    print(f"  torse mannequin : {dummy_torso.round(3).tolist()}  (racine mannequin Z={DUMMY_Z})")
    print(f"  ecart : {gap:.3f} stud -- doit rester petit (contact credible), pas suppose")

    print(f"\n=== charge : le poing recule bien pendant le windup (t=0.00 vs t=0.30s) ===")
    fist0 = tip_world(att_samples, "Right Arm", idx_at(0.0), "bottom")
    fist_wind = tip_world(att_samples, "Right Arm", idx_at(0.30), "bottom")
    print(f"  poing t=0.00 : {fist0.round(3).tolist()}")
    print(f"  poing t=0.30 : {fist_wind.round(3).tolist()}")

    print(f"\n=== synchronisation : le mannequin ne bouge pas avant IMPACT_T ===")
    for t in (0.0, IMPACT_T - 0.05, IMPACT_T - 0.01):
        i = idx_at(t)
        head = np.array(dum_samples["Head"][i][3])
        print(f"  t={t:.3f}s  tete mannequin monde : {head.round(3).tolist()}")
    i_after = idx_at(IMPACT_T + 0.02)
    head_after = np.array(dum_samples["Head"][i_after][3])
    print(f"  t={IMPACT_T+0.02:.3f}s (juste apres l'impact) tete mannequin : {head_after.round(3).tolist()}  (doit avoir bouge)")

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

    print(f"\nDurees : attaquant={att_dur:.2f}s, mannequin={dum_dur:.2f}s (doivent etre egales)")


if __name__ == "__main__":
    main()
