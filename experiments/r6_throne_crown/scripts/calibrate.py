"""
Verifie par le calcul (pas a l'oeil) que la choregraphie de
choreography.sit_and_crown() s'encastre dans la geometrie de
props.throne_parts()/crown_parts() : hauteur des hanches au niveau du
siege, mains sur les accoudoirs au repos, pointe des pieds au-dessus du
sol pendant l'assise (jambe raide, pas de genou), main droite au repos
proche du piedestal de la couronne.
"""
import math

import anim_engine as ae
import numpy as np
from choreography import sit_and_crown
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
    keyframes, phases, preview_times, engine_opts = sit_and_crown()
    duration = max(k["time"] for k in keyframes)
    objs = ae.build_rig()
    ae.apply_choreography(objs, keyframes, **engine_opts)
    samples = ae.sample(objs, duration_s=duration, sample_hz=60)

    def idx_at(t):
        return round(t * 60)

    print("=== assise (t=0.70) ===")
    i = idx_at(0.70)
    hip_y = samples["Torso"][i][3][1] - 1.0  # bas du torse = point d'attache hanche
    print(f"  Torso world Y (=hanche haut) : {samples['Torso'][i][3][1]:.3f}  "
          f"(bas du torse / hanche : {hip_y:.3f}, cible sommet siege = 2.0)")
    r_hand = tip_world(samples, "Right Arm", i, "bottom")
    l_hand = tip_world(samples, "Left Arm", i, "bottom")
    print(f"  Main droite monde : {r_hand.round(3).tolist()}  (accoudoir droit ~ X=2.6 Y~3.0 Z~0.0-0.9)")
    print(f"  Main gauche monde : {l_hand.round(3).tolist()}  (accoudoir gauche ~ X=-2.6 Y~3.0 Z~0.0-0.9)")
    r_foot = tip_world(samples, "Right Leg", i, "bottom")
    print(f"  Pied droit monde : {r_foot.round(3).tolist()}  (doit rester au-dessus du sol Y=0, "
          f"pas d'attente de contact -- jambe raide sans genou)")

    print("\n=== couronnement : main au moment du pickup (t=1.35) ===")
    i = idx_at(1.35)
    r_hand = tip_world(samples, "Right Arm", i, "bottom")
    print(f"  Main droite monde : {r_hand.round(3).tolist()}  <- position du piedestal de la couronne a caler dessus")

    print("\n=== couronnement : mains au sommet du geste (t=1.70) ===")
    i = idx_at(1.70)
    r_hand = tip_world(samples, "Right Arm", i, "bottom")
    l_hand = tip_world(samples, "Left Arm", i, "bottom")
    head_top = tip_world(samples, "Head", i, "top")
    print(f"  Main droite monde : {r_hand.round(3).tolist()}")
    print(f"  Main gauche monde : {l_hand.round(3).tolist()}")
    print(f"  Sommet de la tete monde : {head_top.round(3).tolist()}  (mains doivent etre au-dessus)")

    print("\n=== pose de la couronne (t=2.00) ===")
    i = idx_at(2.00)
    r_hand = tip_world(samples, "Right Arm", i, "bottom")
    head_top = tip_world(samples, "Head", i, "top")
    print(f"  Main droite monde : {r_hand.round(3).tolist()}")
    print(f"  Sommet de la tete monde : {head_top.round(3).tolist()}  (doivent etre proches)")

    print("\n=== debout, t=0.00 (sanity check pieds au sol) ===")
    i = idx_at(0.0)
    r_foot = tip_world(samples, "Right Leg", i, "bottom")
    print(f"  Pied droit monde : {r_foot.round(3).tolist()}  (attendu Y proche de 0)")


if __name__ == "__main__":
    main()
