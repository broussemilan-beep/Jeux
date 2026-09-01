"""
Exporte les positions monde (par segment, + bouts de membres) de plusieurs
variantes dans un seul JSON, pour le lecteur HTML de comparaison A/B/C.
"""
import json
import math
import os

import numpy as np

import anim_engine as ae
import cartoon_filter as cf
from choreography import CYCLES
from r6_rig import PART_ORDER, PARENT, PART_SIZES

SAMPLE_HZ = 120
OUT_HZ = 30


def _frames_from_local(local_samples, n):
    """Recalcule matrices monde + positions, et renvoie les frames decimees."""
    world_pos = {p: [None] * n for p in PART_ORDER}
    world_rot = {p: [None] * n for p in PART_ORDER}
    for i in range(n):
        for part in PART_ORDER:
            _, rot, pos = local_samples[part][i]
            m_local = ae.euler_xyz_matrix(*rot)
            parent = PARENT.get(part)
            if parent is None:
                world_pos[part][i] = np.array(pos, dtype=float)
                world_rot[part][i] = m_local
            else:
                world_pos[part][i] = world_pos[parent][i] + world_rot[parent][i] @ np.array(pos, dtype=float)
                world_rot[part][i] = world_rot[parent][i] @ m_local

    stride = max(1, round(SAMPLE_HZ / OUT_HZ))
    frames = []
    for i in range(0, n, stride):
        f = {"t": round(local_samples["Torso"][i][0], 4)}
        for part in PART_ORDER:
            f[part] = [round(v, 4) for v in world_pos[part][i].tolist()]
            sy = PART_SIZES[part][1]
            if part in ("Right Arm", "Left Arm", "Right Leg", "Left Leg"):
                tip = world_pos[part][i] + world_rot[part][i] @ np.array([0, -sy / 2, 0])
                f[part + "_tip"] = [round(v, 4) for v in tip.tolist()]
            if part == "Head":
                top = world_pos[part][i] + world_rot[part][i] @ np.array([0, sy / 2, 0])
                f["Head_top"] = [round(v, 4) for v in top.tolist()]
        frames.append(f)
    return frames


def build_variant(cycle_n, k_gain=0.0, sigma_s=0.06, alpha=0.0):
    keyframes, phases, _pt, engine_opts = CYCLES[cycle_n]()
    duration = max(k["time"] for k in keyframes)
    kts = sorted(k["time"] for k in keyframes)
    objs = ae.build_rig()
    ae.apply_choreography(objs, keyframes, **engine_opts)
    samples = ae.sample(objs, duration_s=duration, sample_hz=SAMPLE_HZ)

    if k_gain == 0.0 and alpha == 0.0:
        local = {p: [(s[0], s[1], s[2]) for s in samples[p]] for p in samples}
    else:
        local, _ = cf.apply_to_samples(samples, SAMPLE_HZ, kts,
                                       k_gain=k_gain, sigma_s=sigma_s, alpha=alpha)
    n = len(local[PART_ORDER[0]])
    return {
        "duration": duration,
        "phases": [{"name": p["name"], "t0": p["t0"], "t1": p["t1"]} for p in phases],
        "frames": _frames_from_local(local, n),
    }


if __name__ == "__main__":
    out = {
        "fps": OUT_HZ,
        "variants": {
            "cycle5": build_variant(5),
            "cycle2": build_variant(2),
            "cartoon": build_variant(2, k_gain=0.0015, sigma_s=0.06, alpha=1.0),
        },
    }
    path = os.environ.get("PREVIEW_OUT", "/tmp/combo_ab_data.json")
    with open(path, "w") as f:
        json.dump(out, f, separators=(",", ":"))
    print("ecrit", path, os.path.getsize(path), "octets")
    for name, v in out["variants"].items():
        print(f"  {name}: {len(v['frames'])} frames, {v['duration']}s")
