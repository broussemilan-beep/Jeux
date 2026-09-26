"""
Calcule la trajectoire MONDE du soleil invoque (position + rayon, par
echantillon) pendant toute la scene, et l'exporte en JSON -- meme
principe que compute_crown_track.py dans r6_throne_crown : ce n'est PAS
un second KeyframeSequence (un KeyframeSequence anime les Motor6D d'UN
SEUL rig), et la trajectoire de vol n'est PAS derivee de la vitesse du
bras au lancer (verifie par calibrate.py que cette vitesse ne dit rien
d'utile sur la duree/portee du vol -- voir sa docstring).

Trois phases :
  1. t < RAISE_T        : n'existe pas encore (rayon 0).
  2. RAISE_T..RELEASE_T : "en charge", suit LA MAIN DROITE levee (geste a
     UNE main -- retour utilisateur explicite, voir choreography.py) avec
     un decalage vertical FIXE (HAND_OFFSET_Y) au-dessus d'elle, pour que
     le soleil flotte visiblement AU-DESSUS de la main plutot que de lui
     etre colle dessus (la main est deja au-dessus de la tete a ce
     keyframe -- voir calibrate.py et choreography.RAISE_RIGHT_ARM ; PAS
     une compensation de limite du rig, contrairement a la toute
     premiere version de ce fichier, qui mesurait le mauvais bout du
     bras -- voir le commentaire de HAND_OFFSET_Y). Rayon : croit de 0 a
     ORB_MAX_RADIUS (interpolation lissee, pas lineaire -- une invocation
     qui accelere en grossissant se lit mieux qu'une croissance a vitesse
     constante).
  3. RELEASE_T..IMPACT_T : vol libre SCRIPTE vers WORLD_TARGET_POS (un
     point choisi, pas mesure sur le personnage) -- interpolation avec
     une legere composante d'arc (pas une ligne droite parfaite, un jet
     de puissance a une trajectoire qui s'incurve legerement vers le
     bas). Rayon constant (ORB_MAX_RADIUS) pendant le vol.
  4. t >= IMPACT_T : la boule a disparu (impact) -- plus de position
     utile, le lecteur bascule sur les effets d'impact a ce moment.
"""
import json

import numpy as np

import anim_engine as ae
from calibrate import tip_world
from choreography import haughty_orb_throw, RAISE_T, RELEASE_T, IMPACT_T

SAMPLE_HZ = 30

# Decalage vertical au-dessus de la main droite levee -- purement une
# marge visuelle (le soleil flotte au-dessus de la main plutot que de la
# toucher), PAS une compensation de limite du rig. La toute premiere
# version de ce fichier utilisait 1,4 stud pour compenser un ecart
# mesure de ~1,0-1,05 stud "sous la tete" -- un artefact du bug de
# mesure corrige dans calibrate.py (mauvais bout du bras, voir sa
# docstring) : la main est en realite deja LEGEREMENT AU-DESSUS de la
# tete a ce keyframe. 1,0 stud choisi pour une marge nette au-dessus de
# la main sans coller le soleil sur la tete (verifie par capture
# d'ecran).
HAND_OFFSET_Y = 1.0

ORB_MAX_RADIUS = 1.1

# Point cible du lancer -- CHOISI, pas mesure : loin en contrebas et
# devant le personnage, pour lire "le monde" comme un point distant en
# dessous de lui (voir README pour la mise en scene du lecteur -- le
# personnage se tient au bord d'un a-pic, le monde est visible tres bas
# et loin devant).
WORLD_TARGET_POS = np.array([2.0, -26.0, -34.0])


def _ease_in(f):
    """Acceleration douce (quadratique) -- une invocation qui grossit
    de plus en plus vite se lit mieux qu'une croissance lineaire."""
    return f * f


def main():
    keyframes, phases, preview_times, engine_opts = haughty_orb_throw()
    duration = max(k["time"] for k in keyframes)
    objs = ae.build_rig()
    ae.apply_choreography(objs, keyframes, **engine_opts)
    samples = ae.sample(objs, duration_s=duration, sample_hz=SAMPLE_HZ)

    n = len(samples["Torso"])
    release_pos = None
    track = []
    for i in range(n):
        t = samples["Torso"][i][0]
        if t < RAISE_T:
            pos, radius, phase = None, 0.0, "absente"
        elif t < RELEASE_T:
            hand_r = tip_world(samples, "Right Arm", i, "bottom")
            pos = hand_r + np.array([0.0, HAND_OFFSET_Y, 0.0])
            frac = (t - RAISE_T) / (RELEASE_T - RAISE_T)
            radius = ORB_MAX_RADIUS * _ease_in(min(1.0, frac))
            phase = "charge"
            release_pos = pos
        elif t < IMPACT_T:
            frac = (t - RELEASE_T) / (IMPACT_T - RELEASE_T)
            # Arc leger : interpolation lineaire + une bosse vers le haut
            # au milieu du vol (sin(pi*frac)), pas une ligne droite --
            # lit comme un vrai jet lance, pas un teleport.
            base = release_pos + (WORLD_TARGET_POS - release_pos) * frac
            arc = np.array([0.0, 4.0 * np.sin(np.pi * frac), 0.0])
            pos = base + arc
            radius = ORB_MAX_RADIUS
            phase = "vol"
        else:
            pos, radius, phase = None, 0.0, "impact"

        track.append({
            "t": round(t, 4), "phase": phase,
            "pos": [round(float(v), 4) for v in pos] if pos is not None else None,
            "radius": round(float(radius), 4),
        })

    out = {
        "sample_hz": SAMPLE_HZ,
        "duration": duration,
        "raise_t": RAISE_T,
        "release_t": RELEASE_T,
        "impact_t": IMPACT_T,
        "world_target_pos": [float(v) for v in WORLD_TARGET_POS],
        "hand_offset_y": HAND_OFFSET_Y,
        "note": ("Trajectoire monde de la boule divine. A appliquer via un "
                 "script (CFrame direct + Size sur un Ball Neon), PAS via "
                 "l'Animator -- voir docstring de ce fichier."),
        "track": track,
    }
    path = "../output/orb_track.json"
    with open(path, "w") as f:
        json.dump(out, f, indent=1)
    print(f"ecrit {path}, {len(track)} echantillons")

    # Verification : pas de saut brutal au relachement (le dernier point
    # "charge" et le premier point "vol" doivent coincider).
    i_release = round(RELEASE_T * SAMPLE_HZ)
    p_before = np.array(track[i_release - 1]["pos"])
    p_after = np.array(track[i_release]["pos"])
    print(f"saut au relachement (charge -> vol) : {np.linalg.norm(p_after - p_before):.4f} stud")
    print(f"position au relachement : {p_after.round(2).tolist()}")
    print(f"position cible (le monde) : {WORLD_TARGET_POS.tolist()}")


if __name__ == "__main__":
    main()
