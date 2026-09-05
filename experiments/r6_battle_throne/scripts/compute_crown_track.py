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

Trois phases (voir choreography.FULL_PICKUP_T / FULL_PLACED_T -- decalees
de la duree de la montee de l'escalier par rapport a sit_and_crown() seule) :
  1. t < FULL_PICKUP_T   : statique, posee sur le coussin (props.cushion_top_pos()).
  2. FULL_PICKUP_T..FULL_PLACED_T : suit le bout de la main droite, orientation
     gardee verticale (identite) -- la couronne est tenue a plat, pas
     vrillee avec la rotation complete du bras (~170 deg sur cette
     fenetre, la vriller pareillement aurait l'air faux).
  3. t >= FULL_PLACED_T  : suit le sommet de la tete, ROTATION DE LA TETE
     COMPRISE -- une fois posee, elle est "portee" et tourne avec la tete.
     Un leger REBOND D'ATTERRISSAGE (voir LANDING_*) s'ajoute sur les
     ~0,4s qui suivent FULL_PLACED_T -- une sinusoide amortie en fermeture
     close (pas une simulation iterative comme _spring_chase()) puisqu'il
     n'y a pas de courbe cible a poursuivre ici, juste une impulsion a
     l'atterrissage -- puis s'annule : la position en regime stationnaire
     (bien apres l'atterrissage) reste EXACTEMENT celle calibree (couronne
     posee au sommet de la tete), le rebond ne fait que dramatiser
     l'instant du contact. Meme idee que le "secondary motion" recree
     dans anim_engine.py, mais en forme fermee ici (objet libre, pas de
     courbe de reference a suivre).
"""
import json
import math

import numpy as np

import anim_engine as ae
import props
from calibrate import tip_world, world_rotations
from choreography import full_scene, FULL_PICKUP_T, FULL_PLACED_T, SECONDARY_MOTION

CUSHION_POS = props.cushion_top_pos()
SAMPLE_HZ = 30
PICKUP_T, PLACED_T = FULL_PICKUP_T, FULL_PLACED_T

# Rebond d'atterrissage -- voir docstring de module. Amplitude modeste
# (0,05 stud, un tressaillement, pas un vrai rebond physique de couronne
# qui quitterait la tete) et decroissance rapide (deux oscillations
# visibles avant de s'eteindre) pour rester credible : une couronne posee
# soigneusement, pas lachee de haut.
LANDING_DUR = 0.40
LANDING_AMPLITUDE = 0.05
LANDING_FREQ_HZ = 5.0
LANDING_TAU = 0.11


def main():
    keyframes, phases, preview_times, engine_opts = full_scene()
    duration = max(k["time"] for k in keyframes)
    objs = ae.build_rig()
    ae.apply_choreography(objs, keyframes, **engine_opts)
    samples = ae.sample(objs, duration_s=duration, sample_hz=SAMPLE_HZ, secondary_motion=SECONDARY_MOTION)

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
            age = t - PLACED_T
            if age < LANDING_DUR:
                bounce = (LANDING_AMPLITUDE * math.exp(-age / LANDING_TAU)
                          * math.cos(2 * math.pi * LANDING_FREQ_HZ * age))
                pos = pos + np.array([0.0, bounce, 0.0])
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
