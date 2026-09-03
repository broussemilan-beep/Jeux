"""
Construit et exporte le KeyframeSequence du personnage + le Model
statique de la boule divine (Ball, Material=Neon -- brille nativement
dans le moteur Roblox, meme choix que les gemmes de r6_throne_crown).
Verifie (round-trip moteur + sanite structurelle) avant d'ecrire les
fichiers.
"""
import os

import numpy as np

import anim_engine as ae
import export_kfseq as ex
import export_model as em
from choreography import haughty_orb_throw
from orb_track import ORB_MAX_RADIUS
from r6_rig import PART_ORDER

OUT = "../output"

# Couleur du SOLEIL invoque -- jaune-or sature et lumineux, pas le
# blanc-or doux de la premiere version (boule "divine" generique) :
# retour utilisateur explicite ("le soleil"), coherente avec le
# gradient blanc->jaune->orange de l'aura/coeur dans le lecteur (voir
# README) plutot qu'une couleur inventee sans lien avec la mise en scene.
ORB_COLOR = (255, 196, 40)


def structural_sanity(samples):
    problems = []
    for part in PART_ORDER:
        rots = [s[1] for s in samples[part]]
        for rx, ry, rz in rots:
            if not all(np.isfinite([rx, ry, rz])):
                problems.append(f"{part} : rotation non finie")
                break
            if max(abs(rx), abs(ry), abs(rz)) > 260:
                problems.append(f"{part} : rotation hors plage plausible ({rx:.1f},{ry:.1f},{rz:.1f})")
                break
    return problems


def main():
    os.makedirs(OUT, exist_ok=True)
    keyframes, phases, preview_times, engine_opts = haughty_orb_throw()
    duration = max(k["time"] for k in keyframes)

    objs = ae.build_rig()
    ae.apply_choreography(objs, keyframes, **engine_opts)
    samples = ae.sample(objs, duration_s=duration, sample_hz=120)

    problems = structural_sanity(samples)
    if problems:
        print("STRUCTURE KO :")
        for p in problems:
            print(" -", p)
    else:
        print("Structure OK : 6 segments rigides, RootJoint seul a translater, rotations finies et plausibles.")

    char_path, n_kf = ex.export_keyframe_sequence(
        samples, 120, os.path.join(OUT, "character_haughty_orb_throw.rbxmx"),
        anim_name="R6_HaughtyOrbThrow", decimate_to_hz=30)
    print(f"KeyframeSequence exporte : {char_path} ({n_kf} keyframes)")

    orb_spec = [{
        "name": "DivineOrb", "shape": em.SHAPE_BALL,
        "size": (ORB_MAX_RADIUS * 2, ORB_MAX_RADIUS * 2, ORB_MAX_RADIUS * 2),
        "pos": (0.0, 0.0, 0.0), "color_rgb": ORB_COLOR, "material": "Neon",
    }]
    orb_path, n_orb = em.export_model(orb_spec, "DivineOrb", os.path.join(OUT, "divine_orb.rbxmx"),
                                       primary_part="DivineOrb")
    print(f"Boule divine exportee : {orb_path} ({n_orb} part) -- "
          f"position/taille reelles pilotees par orb_track.json (voir README), pas figees dans ce fichier")


if __name__ == "__main__":
    main()
