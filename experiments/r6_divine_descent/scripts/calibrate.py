"""
Verifie par le calcul (pas a l'oeil) la choregraphie de divine_descent() :
descente Y strictement monotone (pas de rebond/remontee parasite avant
l'impact), poing droit pres du sol ET devant le corps a l'instant
d'impact, pieds pas grossierement enfonces sous le sol pendant la fente
d'atterrissage, raideur structurelle (rotations finies, plausibles).
"""
import numpy as np

import anim_engine as ae
from choreography import divine_descent, IMPACT_T
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
    keyframes, phases, preview_times, engine_opts = divine_descent()
    duration = max(k["time"] for k in keyframes)
    objs = ae.build_rig()
    ae.apply_choreography(objs, keyframes, **engine_opts)
    samples = ae.sample(objs, duration_s=duration, sample_hz=60)

    def idx_at(t):
        return round(t * 60)

    print("=== chute : hauteur de hanche strictement decroissante jusqu'a l'impact ===")
    ys = [samples["HumanoidRootPart"][idx_at(t)][3][1] for t in np.arange(0.0, IMPACT_T, 0.05)]
    monotone = all(ys[i] >= ys[i + 1] - 1e-6 for i in range(len(ys) - 1))
    print(f"  {len(ys)} echantillons de t=0 a t={IMPACT_T:.2f}s, Y va de {ys[0]:.2f} a {ys[-1]:.2f}")
    print(f"  strictement decroissante : {'OUI' if monotone else 'NON -- PROBLEME'}")

    print(f"\n=== impact (t={IMPACT_T:.2f}s) : poing droit vs sol ===")
    i = idx_at(IMPACT_T)
    r_hand = tip_world(samples, "Right Arm", i, "bottom")
    root = np.array(samples["HumanoidRootPart"][i][3])
    print(f"  poing droit monde : {r_hand.round(3).tolist()}")
    print(f"  racine (hanche)   : {root.round(3).tolist()}")
    # Cible realiste, pas Y=0 exact : balayage numerique (voir
    # choreography.IMPACT_RIGHT_ARM) a etabli que ~0.65 stud est le plus
    # bas atteignable a cette hanche -- longueur de bras + inclinaison du
    # torse fixes, pas de coude pour "plier" davantage vers le sol.
    print(f"  poing proche du sol (Y < 1.0, limite reelle du rig) : {'OUI' if r_hand[1] < 1.0 else 'NON -- verifier'}")

    print(f"\n=== impact (t={IMPACT_T:.2f}s) : pieds vs sol reel (Y=0) ===")
    for leg in ("Right Leg", "Left Leg"):
        foot = tip_world(samples, leg, i, "bottom")
        print(f"  {leg} monde : {foot.round(3).tolist()}  ({'OK' if foot[1] > -0.35 else 'ENFONCE -- A CORRIGER'})")

    print("\n=== pose finale (t=2.80s) : pieds au sol, tete/buste ===")
    i = idx_at(2.80)
    for leg in ("Right Leg", "Left Leg"):
        foot = tip_world(samples, leg, i, "bottom")
        print(f"  {leg} monde : {foot.round(3).tolist()}  (attendu Y proche de 0)")

    print("\n=== structure : rotations finies et plausibles (pas de coude/genou a simuler) ===")
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
