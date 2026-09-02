"""
Assemble le JSON du lecteur HTML : le personnage (resolu par le moteur,
jamais la FK brute -- meme discipline que les prototypes precedents) ET
la trajectoire de la boule divine (orb_track.py, deja son propre
fichier -- relue ici plutot que recalculee, pour ne jamais pouvoir
diverger du .json livre).
"""
import json
import os

import resolve_rbxmx as rr
from choreography import RAISE_T, RELEASE_T, IMPACT_T
from r6_rig import PART_ORDER, PART_SIZES

OUT_HZ = 30


def main():
    char_path = "../output/character_haughty_orb_throw.rbxmx"
    char_frames = rr.resolve_to_frames(char_path, out_hz=OUT_HZ)
    duration = char_frames[-1]["t"]

    with open("../output/orb_track.json") as f:
        orb_data = json.load(f)

    out = {
        "fps": OUT_HZ,
        "duration": duration,
        "part_sizes": {p: list(PART_SIZES[p]) for p in PART_ORDER},
        "part_order": PART_ORDER,
        "char_frames": char_frames,
        "orb_track": orb_data["track"],
        "raise_t": RAISE_T,
        "release_t": RELEASE_T,
        "impact_t": IMPACT_T,
        "world_target_pos": orb_data["world_target_pos"],
    }
    path = os.environ.get("SCENE_OUT", "/tmp/divine_orb_scene_data.json")
    with open(path, "w") as f:
        json.dump(out, f, separators=(",", ":"))
    print(f"ecrit {path}, {os.path.getsize(path)} octets, {len(char_frames)} frames, duree {duration:.2f}s")


if __name__ == "__main__":
    main()
