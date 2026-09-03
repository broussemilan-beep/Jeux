"""
Assemble le JSON du lecteur HTML : les deux personnages (resolus par le
moteur depuis les .rbxmx exportes, jamais la FK brute -- meme discipline
que les autres prototypes), synchronises sur la meme grille de temps.
"""
import json
import os

import resolve_rbxmx as rr
from choreography import IMPACT_T, DURATION, WINDUP_T, COIL_T
from r6_rig import PART_ORDER, PART_SIZES

OUT_HZ = 30


def main():
    att_frames = rr.resolve_to_frames("../output/character_attacker_punch.rbxmx", out_hz=OUT_HZ)
    dum_frames = rr.resolve_to_frames("../output/character_dummy_reaction.rbxmx", out_hz=OUT_HZ)

    out = {
        "fps": OUT_HZ,
        "duration": DURATION,
        "impact_t": IMPACT_T,
        "windup_t": WINDUP_T,
        "coil_t": COIL_T,
        "part_sizes": {p: list(PART_SIZES[p]) for p in PART_ORDER},
        "part_order": PART_ORDER,
        "attacker_frames": att_frames,
        "dummy_frames": dum_frames,
    }
    path = os.environ.get("SCENE_OUT", "/tmp/directional_punch_scene_data.json")
    with open(path, "w") as f:
        json.dump(out, f, separators=(",", ":"))
    print(f"ecrit {path}, {os.path.getsize(path)} octets, "
          f"{len(att_frames)} frames attaquant, {len(dum_frames)} frames mannequin")


if __name__ == "__main__":
    main()
