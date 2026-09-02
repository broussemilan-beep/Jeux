"""
Assemble le JSON du lecteur HTML : personnage (resolu par le moteur,
comme dump_preview_data.py dans r6_aerial_kick_combo -- jamais la FK
brute), trone + escalier (statique), couronne (trajectoire calculee,
composee avec sa geometrie locale a chaque frame).
"""
import json
import os

import numpy as np

import props
import resolve_rbxmx as rr
from choreography import full_scene, FULL_PICKUP_T, FULL_PLACED_T
from r6_rig import PART_ORDER, PART_SIZES
from calibrate import tip_world, world_rotations
import anim_engine as ae

CUSHION_POS = props.cushion_top_pos()
OUT_HZ = 30


def crown_frames_at(char_frames):
    """Pour chaque frame DEJA DECIMEE du personnage (meme grille de temps
    -- lecture synchronisee), transforme chaque sous-part locale de la
    couronne (props.crown_parts(), repere local = centre de la bande) par
    la transformation monde de la couronne a cet instant (statique sur le
    coussin / suit la main / suit la tete, voir compute_crown_track.py -
    meme logique, recalculee ici sur la grille decimee plutot que relue
    depuis le fichier)."""
    keyframes, phases, _pt, engine_opts = full_scene()
    duration = max(k["time"] for k in keyframes)
    objs = ae.build_rig()
    ae.apply_choreography(objs, keyframes, **engine_opts)
    samples = ae.sample(objs, duration_s=duration, sample_hz=120)

    local_parts = props.crown_parts()
    out = []
    for cf in char_frames:
        t = cf["t"]
        i = min(int(round(t * 120)), len(samples["Torso"]) - 1)
        if t < FULL_PICKUP_T:
            c_pos, c_rot = np.array(CUSHION_POS), np.eye(3)
        elif t < FULL_PLACED_T:
            c_pos, c_rot = tip_world(samples, "Right Arm", i, "bottom"), np.eye(3)
        else:
            c_pos = tip_world(samples, "Head", i, "top")
            c_rot = world_rotations(samples, i)["Head"]

        frame = {"t": t}
        for spec in local_parts:
            lp = np.array(spec["pos"])
            lr = np.array(spec.get("rot", [[1, 0, 0], [0, 1, 0], [0, 0, 1]]))
            wp = c_pos + c_rot @ lp
            wr = c_rot @ lr
            frame[spec["name"]] = {
                "p": [round(float(v), 4) for v in wp],
                "r": [round(float(v), 5) for row in wr for v in row],
                "size": list(spec["size"]),
                "color": spec["color_rgb"],
                "shape": spec.get("shape", "1"),
                "material": spec.get("material", "Plastic"),
            }
        out.append(frame)
    return out


def main():
    char_path = "../output/character_sit_and_crown.rbxmx"
    char_frames = rr.resolve_to_frames(char_path, out_hz=OUT_HZ)
    duration = char_frames[-1]["t"]

    static_parts = props.throne_parts() + props.staircase_parts()
    throne = []
    for spec in static_parts:
        throne.append({
            "name": spec["name"], "size": list(spec["size"]),
            "pos": list(spec["pos"]), "rot": spec.get("rot", [[1, 0, 0], [0, 1, 0], [0, 0, 1]]),
            "color": spec["color_rgb"], "shape": spec.get("shape", "1"),
            "material": spec.get("material", "Plastic"),
        })

    crown_f = crown_frames_at(char_frames)
    crown_part_names = [s["name"] for s in props.crown_parts()]

    _kf, phases, _pt, _opts = full_scene()

    out = {
        "fps": OUT_HZ,
        "duration": duration,
        "part_sizes": {p: list(PART_SIZES[p]) for p in PART_ORDER},
        "part_order": PART_ORDER,
        "char_frames": char_frames,
        "throne": throne,
        "crown_part_names": crown_part_names,
        "crown_frames": crown_f,
        "crowned_t": FULL_PLACED_T,
        "phases": [{"name": p["name"], "t0": p["t0"], "t1": min(p["t1"], duration)} for p in phases],
    }
    path = os.environ.get("SCENE_OUT", "/tmp/throne_scene_data.json")
    with open(path, "w") as f:
        json.dump(out, f, separators=(",", ":"))
    print(f"ecrit {path}, {os.path.getsize(path)} octets, {len(char_frames)} frames, duree {duration:.2f}s")


if __name__ == "__main__":
    main()
