"""
Verifie le placement des pieds au sol (Y=0) pour l'attaquant, a chaque
instant-cle de la choreographie -- meme cinematique directe que
calibrate.py, mais appliquee au bas du corps plutot qu'au poing. Ecrit
suite au retour utilisateur "le placement [des jambes] n'est pas bon" :
un pied qui flotte ou s'enfonce ne se voit pas dans calibrate.py (qui ne
mesure que le poing contre le torse du mannequin), il fallait un script
dedie. Voir grounded_root_y()/grounded_root_y_balanced() dans
choreography.py pour la correction elle-meme.
"""
import numpy as np

import anim_engine as ae
from choreography import attacker_combo
from r6_rig import PART_SIZES


def _world_rotations(samples, i):
    rot = {}
    root_r = ae.euler_xyz_matrix(*samples["HumanoidRootPart"][i][1])
    rot["HumanoidRootPart"] = root_r
    torso_r = root_r @ ae.euler_xyz_matrix(*samples["Torso"][i][1])
    rot["Torso"] = torso_r
    for part in samples:
        if part in ("HumanoidRootPart", "Torso"):
            continue
        rot[part] = torso_r @ ae.euler_xyz_matrix(*samples[part][i][1])
    return rot


def _foot_y(samples, part, i):
    world_pos = np.array(samples[part][i][3])
    rots = _world_rotations(samples, i)
    half = PART_SIZES[part][1] / 2.0
    tip = world_pos + rots[part] @ np.array([0.0, -half, 0.0])
    return tip[1]


def main():
    keyframes, phases, preview_times, engine_opts = attacker_combo()
    duration = max(k["time"] for k in keyframes)
    objs = ae.build_rig()
    ae.apply_choreography(objs, keyframes, **engine_opts)
    samples = ae.sample(objs, duration_s=duration, sample_hz=120, secondary_motion=None)

    print("=== hauteur des pieds (sol = Y0.0) a chaque instant-cle de la choreographie ===")
    hz = 120
    for t in sorted(set(k["time"] for k in keyframes)):
        i = min(round(t * hz), len(samples["Left Leg"]) - 1)
        ly = _foot_y(samples, "Left Leg", i)
        ry = _foot_y(samples, "Right Leg", i)
        root_y = samples["HumanoidRootPart"][i][2][1]
        print(f"  t={t:6.3f}  rootY={root_y:6.3f}  LeftFootY={ly:7.3f}  RightFootY={ry:7.3f}")


if __name__ == "__main__":
    main()
