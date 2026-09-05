"""
Assemble le JSON du lecteur HTML : les deux personnages (resolus par le
moteur depuis les .rbxmx exportes, jamais la FK brute), synchronises sur
la meme grille de temps, plus les instants-cles de chaque coup pour la
mise en scene VFX/camera du lecteur.
"""
import json
import os

import resolve_rbxmx as rr
from choreography import (DURATION, JAB_T, CROSS_T, HOOK_T,
                           JAB_WINDUP_T, CROSS_WINDUP_T, HOOK_WINDUP_T)
from r6_rig import PART_ORDER, PART_SIZES

OUT_HZ = 30


def main():
    att_frames = rr.resolve_to_frames("../output/character_attacker_combo.rbxmx", out_hz=OUT_HZ)
    dum_frames = rr.resolve_to_frames("../output/character_dummy_combo_reaction.rbxmx", out_hz=OUT_HZ)

    out = {
        "fps": OUT_HZ,
        "duration": DURATION,
        "hits": [
            {"name": "jab", "windup_t": JAB_WINDUP_T, "impact_t": JAB_T},
            {"name": "cross", "windup_t": CROSS_WINDUP_T, "impact_t": CROSS_T},
            {"name": "hook", "windup_t": HOOK_WINDUP_T, "impact_t": HOOK_T},
        ],
        "part_sizes": {p: list(PART_SIZES[p]) for p in PART_ORDER},
        "part_order": PART_ORDER,
        "attacker_frames": att_frames,
        "dummy_frames": dum_frames,
    }
    path = os.environ.get("SCENE_OUT", "/tmp/hit_combo_scene_data.json")
    with open(path, "w") as f:
        json.dump(out, f, separators=(",", ":"))
    print(f"ecrit {path}, {os.path.getsize(path)} octets, "
          f"{len(att_frames)} frames attaquant, {len(dum_frames)} frames mannequin")


if __name__ == "__main__":
    main()
