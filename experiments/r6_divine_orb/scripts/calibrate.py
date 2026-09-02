"""
Verifie par le calcul (pas a l'oeil) la choregraphie de
haughty_orb_throw() : la position de la main levee (pour caler le
decalage vertical de la boule dans le lecteur, voir choreography.py),
que la vitesse instantanee du bras au keyframe de lancer est bien quasi
nulle (donc que la trajectoire de vol de la boule DOIT etre scriptee
independamment, pas derivee de cette vitesse -- trouve par ce calcul
meme, pas suppose), et que la structure reste plausible (rotations
finies, pas de coude/genou a simuler).
"""
import numpy as np

import anim_engine as ae
from choreography import haughty_orb_throw, RELEASE_T
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


def main():
    keyframes, phases, preview_times, engine_opts = haughty_orb_throw()
    duration = max(k["time"] for k in keyframes)
    objs = ae.build_rig()
    ae.apply_choreography(objs, keyframes, **engine_opts)
    samples = ae.sample(objs, duration_s=duration, sample_hz=60)

    def idx_at(t):
        return round(t * 60)

    print("=== main levee (t=0.70s, 1.35s, 2.00s) : position + ecart a la tete ===")
    for t in (0.70, 1.35, 2.00):
        i = idx_at(t)
        hand = tip_world(samples, "Right Arm", i, "top")
        head = tip_world(samples, "Head", i, "top")
        gap = head[1] - hand[1]
        print(f"  t={t:.2f}s  main haute={hand.round(3).tolist()}  sommet tete={head.round(3).tolist()}"
              f"  (ecart Y tete-main : {gap:.3f}, limite reelle du rig -- voir choreography.RAISE_RIGHT_ARM)")

    print(f"\n=== lancer (RELEASE_T={RELEASE_T:.2f}s) : vitesse instantanee du bras ===")
    i0 = idx_at(RELEASE_T - 1.0 / 60)
    i1 = idx_at(RELEASE_T + 1.0 / 60)
    hand0 = tip_world(samples, "Right Arm", i0, "top")
    hand1 = tip_world(samples, "Right Arm", i1, "top")
    vel = (hand1 - hand0) * 30.0
    print(f"  position main au relachement : {hand0.round(3).tolist()}")
    print(f"  vitesse instantanee (studs/s) : {vel.round(2).tolist()} (norme : {np.linalg.norm(vel):.2f})")
    print("  -> mesuree pour verification, mais PAS utilisee pour deriver la trajectoire de vol :"
          " la boule doit atteindre un point precis (\"le monde\", position scriptee) a un instant"
          " dramatique precis (IMPACT_T) -- un vol scripte independamment (meme principe que la"
          " couronne de r6_throne_crown) est plus fiable qu'une extrapolation depuis cette vitesse.")

    print("\n=== structure : rotations finies et plausibles ===")
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
        print("  STRUCTURE KO :")
        for p in problems:
            print("   -", p)
    else:
        print("  OK : 6 segments rigides, rotations finies et plausibles.")


if __name__ == "__main__":
    main()
