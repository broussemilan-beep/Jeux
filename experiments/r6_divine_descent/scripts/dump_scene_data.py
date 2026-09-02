"""
Assemble le JSON du lecteur HTML : uniquement le personnage (resolu par
le moteur, jamais la FK brute -- meme discipline que
r6_aerial_kick_combo/dump_preview_data.py et
r6_throne_crown/dump_scene_data.py), plus les instants de phase et trois
instants-cles exportes separement pour le lecteur : reveal_t (debut de
l'aura/rayon de lumiere), land_t (fin des effets de chute), impact_t (le
coup, declenche l'explosion).
"""
import json
import os

import resolve_rbxmx as rr
from choreography import divine_descent, IMPACT_T, LAND_T, REVEAL_T, SKY_Y
from r6_rig import PART_ORDER, PART_SIZES

OUT_HZ = 30


def main():
    char_path = "../output/character_divine_descent.rbxmx"
    char_frames = rr.resolve_to_frames(char_path, out_hz=OUT_HZ)
    duration = char_frames[-1]["t"]

    _kf, phases, _pt, _opts = divine_descent()

    out = {
        "fps": OUT_HZ,
        "duration": duration,
        "part_sizes": {p: list(PART_SIZES[p]) for p in PART_ORDER},
        "part_order": PART_ORDER,
        "char_frames": char_frames,
        "impact_t": IMPACT_T,
        "land_t": LAND_T,
        "reveal_t": REVEAL_T,
        "sky_y": SKY_Y,
        "phases": [{"name": p["name"], "t0": p["t0"], "t1": min(p["t1"], duration)} for p in phases],
    }
    path = os.environ.get("SCENE_OUT", "/tmp/divine_descent_scene_data.json")
    with open(path, "w") as f:
        json.dump(out, f, separators=(",", ":"))
    print(f"ecrit {path}, {os.path.getsize(path)} octets, {len(char_frames)} frames, duree {duration:.2f}s")


if __name__ == "__main__":
    main()
