"""
Verifie par le calcul (pas a l'oeil) que la choregraphie de
choreography.full_scene() (montee de l'escalier + assise + couronnement)
s'encastre dans la geometrie de props.py : hauteur des marches pendant la
montee, hauteur des hanches au niveau du siege, mains sur les accoudoirs
au repos, pointe des pieds au-dessus du sol pendant l'assise (jambe
raide, pas de genou), main droite au repos proche du piedestal de la
couronne, raccord sans saut entre montee et assise.
"""
import math

import anim_engine as ae
import numpy as np
import props
from choreography import full_scene, CLIMB_T, FULL_PICKUP_T, FULL_PLACED_T, STEP_T
from r6_rig import PART_ORDER, PARENT, JOINTS, joint_for_part, PART_SIZES


def world_rotations(samples, i):
    """Matrice de rotation MONDE par part a l'echantillon i (le rig n'a
    que 2 niveaux de profondeur : racine -> Torso -> membres)."""
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
    """Position MONDE de l'extremite d'un membre (bout de la main/du
    pied), a partir du centre + demi-longueur locale le long de -Y (ou
    +Y pour "top")."""
    world_pos = np.array(samples[part][i][3])
    rots = world_rotations(samples, i)
    half = PART_SIZES[part][1] / 2.0
    sign = -1.0 if end == "bottom" else 1.0
    return world_pos + rots[part] @ np.array([0.0, sign * half, 0.0])


def main():
    keyframes, phases, preview_times, engine_opts = full_scene()
    duration = max(k["time"] for k in keyframes)
    objs = ae.build_rig()
    ae.apply_choreography(objs, keyframes, **engine_opts)
    samples = ae.sample(objs, duration_s=duration, sample_hz=60)

    def idx_at(t):
        return round(t * 60)

    print("=== montee de l'escalier : pied avant/apres chaque marche ===")
    for k in range(1, props.STAIR_N + 1):
        i = idx_at(k * STEP_T)
        lead = "Right Leg" if k % 2 == 1 else "Left Leg"
        foot = tip_world(samples, lead, i, "bottom")
        expected_y = k * props.STAIR_RISER
        print(f"  marche {k} (t={k*STEP_T:.2f}s) : pied {lead} monde {foot.round(3).tolist()}  "
              f"(hanche/racine attendue Y={3.0+expected_y:.2f})")

    print(f"\n=== raccord montee -> assise (t={CLIMB_T:.2f}s) ===")
    i_end_climb = idx_at(CLIMB_T - 1.0 / 60)
    i_start_sit = idx_at(CLIMB_T)
    root_end = np.array(samples["HumanoidRootPart"][i_end_climb][3])
    root_start = np.array(samples["HumanoidRootPart"][i_start_sit][3])
    print(f"  racine juste avant la fin de montee : {root_end.round(3).tolist()}")
    print(f"  racine au debut de l'assise (decalee): {root_start.round(3).tolist()}")
    print(f"  ecart : {np.linalg.norm(root_end - root_start):.4f} stud (doit etre ~0)")

    t_assise = CLIMB_T + 0.70
    print(f"\n=== assise (t={t_assise:.2f}s = 0.70s + montee) ===")
    i = idx_at(t_assise)
    hip_y = samples["Torso"][i][3][1] - 1.0
    seat_top = 2.0 + props.PLATFORM_H
    print(f"  Torso world Y (=hanche haut) : {samples['Torso'][i][3][1]:.3f}  "
          f"(bas du torse / hanche : {hip_y:.3f}, cible sommet siege = {seat_top:.2f})")
    r_hand = tip_world(samples, "Right Arm", i, "bottom")
    l_hand = tip_world(samples, "Left Arm", i, "bottom")
    print(f"  Main droite monde : {r_hand.round(3).tolist()}  (accoudoir droit ~ X=2.6 Y~{3.0+props.PLATFORM_H:.1f} Z~0.0-0.9)")
    print(f"  Main gauche monde : {l_hand.round(3).tolist()}")
    r_foot = tip_world(samples, "Right Leg", i, "bottom")
    print(f"  Pied droit monde : {r_foot.round(3).tolist()}  (doit rester au-dessus de l'estrade Y={props.PLATFORM_H:.1f})")

    print(f"\n=== couronnement : main au pickup (t={FULL_PICKUP_T:.2f}s) ===")
    i = idx_at(FULL_PICKUP_T)
    r_hand = tip_world(samples, "Right Arm", i, "bottom")
    cushion = props.cushion_top_pos()
    print(f"  Main droite monde : {r_hand.round(3).tolist()}")
    print(f"  Dessus du coussin : {list(cushion)}  (ecart : {np.linalg.norm(r_hand-np.array(cushion)):.4f} stud)")

    print(f"\n=== couronnement : pose sur la tete (t={FULL_PLACED_T:.2f}s) ===")
    i = idx_at(FULL_PLACED_T)
    r_hand = tip_world(samples, "Right Arm", i, "bottom")
    head_top = tip_world(samples, "Head", i, "top")
    print(f"  Main droite monde : {r_hand.round(3).tolist()}")
    print(f"  Sommet de la tete monde : {head_top.round(3).tolist()}  (ecart : {np.linalg.norm(r_hand-head_top):.4f} stud)")

    print("\n=== debout, t=0.00 (sanity check pieds au sol reel) ===")
    i = idx_at(0.0)
    r_foot = tip_world(samples, "Right Leg", i, "bottom")
    print(f"  Pied droit monde : {r_foot.round(3).tolist()}  (attendu Y proche de 0)")


if __name__ == "__main__":
    main()
