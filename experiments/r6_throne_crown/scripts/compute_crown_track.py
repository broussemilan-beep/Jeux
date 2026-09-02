"""
Calcule la trajectoire MONDE de la couronne (position + rotation, par
echantillon) pendant toute la scene, et l'exporte en JSON.

Pourquoi ce n'est PAS un second KeyframeSequence : un KeyframeSequence
anime les Motor6D d'UN SEUL rig (celui du personnage) -- il ne peut pas
faire porter un objet par la main puis le faire "sauter" sur la tete, ce
qui demande de changer l'objet PARENT (main -> tete) en cours de clip.
Dans un vrai projet Roblox, ca se fait par un script cote client/serveur
qui re-weld la couronne au bon moment (typiquement synchronise sur un
Marker de l'AnimationTrack). Ce fichier fournit exactement les donnees
dont un tel script a besoin : la trajectoire MONDE cible, calculee par
la meme cinematique directe que tout le reste du pipeline (pas une
approximation).

Trois phases (voir choreography.PICKUP_T / PLACED_T) :
  1. t < PICKUP_T   : statique, posee sur le coussin (props.CrownCushion).
  2. PICKUP_T..PLACED_T : suit le bout de la main droite, orientation
     gardee verticale (identite) -- la couronne est tenue a plat, pas
     vrillee avec la rotation complete du bras (~170 deg sur cette
     fenetre, la vriller pareillement aurait l'air faux).
  3. t >= PLACED_T  : suit le sommet de la tete, ROTATION DE LA TETE
     COMPRISE -- une fois posee, elle est "portee" et tourne avec la tete.
"""
import json

import numpy as np

import anim_engine as ae
from calibrate import tip_world, world_rotations
from choreography import sit_and_crown, PICKUP_T, PLACED_T

CUSHION_POS = (2.5, 3.08, 0.0)  # sommet de props.CrownCushion
SAMPLE_HZ = 30


def main():
    keyframes, phases, preview_times, engine_opts = sit_and_crown()
    duration = max(k["time"] for k in keyframes)
    objs = ae.build_rig()
    ae.apply_choreography(objs, keyframes, **engine_opts)
    samples = ae.sample(objs, duration_s=duration, sample_hz=SAMPLE_HZ)

    n = len(samples["Torso"])
    track = []
    for i in range(n):
        t = samples["Torso"][i][0]
        if t < PICKUP_T:
            pos = np.array(CUSHION_POS)
            rot = np.eye(3)
            phase = "coussin"
        elif t < PLACED_T:
            pos = tip_world(samples, "Right Arm", i, "bottom")
            rot = np.eye(3)
            phase = "porte_main"
        else:
            pos = tip_world(samples, "Head", i, "top")
            rot = world_rotations(samples, i)["Head"]
            phase = "sur_tete"
        track.append({
            "t": round(t, 4), "phase": phase,
            "pos": [round(float(v), 4) for v in pos],
            "rot": [[round(float(v), 5) for v in row] for row in rot],
        })

    out = {
        "sample_hz": SAMPLE_HZ,
        "duration": duration,
        "pickup_t": PICKUP_T,
        "placed_t": PLACED_T,
        "note": ("Trajectoire monde de la couronne. A appliquer via un "
                 "script (Weld/CFrame direct), PAS via l'Animator -- voir "
                 "docstring de ce fichier."),
        "track": track,
    }
    path = "../output/crown_track.json"
    with open(path, "w") as f:
        json.dump(out, f, indent=1)
    print(f"ecrit {path}, {len(track)} echantillons")

    # Verification des deux points de recollement (pas de saut brutal).
    i_pickup = round(PICKUP_T * SAMPLE_HZ)
    i_placed = round(PLACED_T * SAMPLE_HZ)
    gap1 = np.linalg.norm(np.array(track[i_pickup]["pos"]) - np.array(CUSHION_POS))
    gap2_hand = tip_world(samples, "Right Arm", i_placed, "bottom")
    gap2_head = tip_world(samples, "Head", i_placed, "top")
    print(f"saut au pickup (coussin -> main) : {gap1:.3f} stud")
    print(f"saut au placement (main -> tete) : {np.linalg.norm(gap2_hand-gap2_head):.3f} stud")


if __name__ == "__main__":
    main()
