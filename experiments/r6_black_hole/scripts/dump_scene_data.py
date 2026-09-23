"""
Assemble le JSON du lecteur HTML : un seul personnage (character_track())
resolu DIRECTEMENT via anim_engine.build_rig()/apply_choreography()/
sample() (meme convention que r6_solar_smite/dump_scene_data.py), plus la
config VFX statique de black_hole_track.export_config() (le lecteur
recalcule les trajectoires debris/disque/coeur/vignette LUI-MEME a partir
de ces parametres -- il ne rejoue pas une liste figee, voir docstring de
black_hole_track.export_config()).
"""
import json
import os

import anim_engine as ae
import black_hole_track as bh
import choreography as ch
from calibrate import world_rotations
from r6_rig import PART_ORDER, PART_SIZES

OUT_HZ = 30


def build_frames(choreo_fn, secondary_motion, out_hz=OUT_HZ):
    keyframes, phases, preview_times, engine_opts = choreo_fn()
    duration = max(k["time"] for k in keyframes)
    objs = ae.build_rig()
    ae.apply_choreography(objs, keyframes, **engine_opts)
    samples = ae.sample(objs, duration_s=duration, sample_hz=out_hz, secondary_motion=secondary_motion)

    n = len(samples["HumanoidRootPart"])
    frames = []
    for i in range(n):
        t = samples["HumanoidRootPart"][i][0]
        rots = world_rotations(samples, i)
        f = {"t": round(t, 4)}
        for part in PART_ORDER:
            if part == "HumanoidRootPart":
                continue
            pos = samples[part][i][3]
            rot = rots[part]
            f[part] = {
                "p": [round(float(v), 4) for v in pos],
                "r": [round(float(v), 5) for row in rot for v in row],
            }
        frames.append(f)
    return frames, duration


def main():
    char_frames, char_dur = build_frames(ch.character_track, ch.SECONDARY_MOTION)

    out = {
        "fps": OUT_HZ,
        "duration": ch.TOTAL_DURATION,
        "part_sizes": {p: list(PART_SIZES[p]) for p in PART_ORDER},
        "part_order": PART_ORDER,
        "character_frames": char_frames,
        "black_hole": bh.export_config(),
        "airborne_window": ch.AIRBORNE_WINDOW,
        "key_times": {
            "t0_end": ch.T0_END,
            "crouch_t": ch.CROUCH_T,
            "crouch_hold_t": ch.CROUCH_HOLD_T,
            "rise_t": ch.RISE_T,
            "hold_end_t": ch.HOLD_END_T,
            "climax_t": ch.CLIMAX_T,
            "release_t": ch.RELEASE_T,
            "land_t": ch.LAND_T,
            "recover_t": ch.RECOVER_T,
            "idle_out_end": ch.IDLE_OUT_END,
        },
    }
    path = os.environ.get("SCENE_OUT", "/tmp/black_hole_scene_data.json")
    with open(path, "w") as f:
        json.dump(out, f, separators=(",", ":"))
    print(f"ecrit {path}, {os.path.getsize(path)} octets, "
          f"{len(char_frames)} frames personnage, duree {ch.TOTAL_DURATION:.3f}s")


if __name__ == "__main__":
    main()
