"""
Piste 1 en pratique : applique le Cartoon Animation Filter (+ SISO) aux
courbes du cycle 5, balaye les parametres, mesure chaque variante et
exporte la meilleure.

Le filtre s'applique APRES l'echantillonnage des F-curves Blender (il
opere sur le signal dense, pas sur les keyframes authored) et AVANT
l'export -- c'est-a-dire exactement a l'endroit ou le brief le situe :
post-traitement sur des courbes deja correctes.
"""
import argparse
import itertools
import json
import os

import numpy as np

import anim_engine as ae
import cartoon_filter as cf
import export_kfseq as ex
import measure as ms
import preview as pv
from choreography import CYCLES
from r6_rig import PART_ORDER

SAMPLE_HZ = 120      # plus haut que les 60 Hz des cycles : derivees secondes plus propres
EXPORT_HZ = 30
BASE_CYCLE = 5      # surchargeable par --base-cycle


def _rebuild_4tuples(local_samples, n):
    """(t, rot, pos) -> (t, rot, pos, world_pos) via la cinematique directe
    maison (meme convention Roblox que partout ailleurs)."""
    world = ae._world_positions(local_samples, n)
    out = {}
    for part in PART_ORDER:
        out[part] = [
            (local_samples[part][i][0], local_samples[part][i][1],
             local_samples[part][i][2], world[part][i])
            for i in range(n)
        ]
    return out


def _to_local(samples):
    return {part: [(s[0], s[1], s[2]) for s in samples[part]] for part in samples}


def evaluate(objs, keyframes, keyframe_times, base_samples, k_gain, sigma_s, alpha):
    local_filt, _deltas = cf.apply_to_samples(
        base_samples, SAMPLE_HZ, keyframe_times,
        k_gain=k_gain, sigma_s=sigma_s, alpha=alpha,
    )
    n = len(local_filt[PART_ORDER[0]])
    filt_samples = _rebuild_4tuples(local_filt, n)

    response = ms.filter_response(base_samples, filt_samples, SAMPLE_HZ, keyframe_times)
    structural = ms.r6_structural_compliance(objs, keyframes, filt_samples)
    continuity = ms.velocity_continuity(filt_samples, SAMPLE_HZ, keyframe_times)
    score = ms.exaggeration_score(response, structural, continuity)
    return filt_samples, response, structural, continuity, score


def main(out_root, base_cycle=BASE_CYCLE):
    os.makedirs(out_root, exist_ok=True)
    keyframes, phases, preview_times, engine_opts = CYCLES[base_cycle]()
    duration = max(k["time"] for k in keyframes)
    keyframe_times = sorted(k["time"] for k in keyframes)

    objs = ae.build_rig()
    ae.apply_choreography(objs, keyframes, **engine_opts)
    base_samples = ae.sample(objs, duration_s=duration, sample_hz=SAMPLE_HZ)

    # Reference : cycle 5 non filtre, mesure avec les MEMES outils.
    base_response = ms.filter_response(base_samples, base_samples, SAMPLE_HZ, keyframe_times)
    base_struct = ms.r6_structural_compliance(objs, keyframes, base_samples)
    base_cont = ms.velocity_continuity(base_samples, SAMPLE_HZ, keyframe_times)
    base_score = ms.exaggeration_score(base_response, base_struct, base_cont)

    results = [{
        "variant": f"cycle{base_cycle}_raw",
        "k": 0.0, "sigma": None, "alpha": 0.0,
        "score": base_score,
        "response": base_response,
    }]
    print(f"{'variante':<34} {'exag':>6} {'lobes':>6} {'ring':>5} {'cont':>6} {'struct':>7} {'TOTAL':>7}")
    s = base_score
    print(f"{f'cycle{base_cycle}_raw (reference)':<34} {s['exaggeration_in_band']:>6} "
          f"{s['clean_lobes']:>6} {s['ringing_total']:>5} {s['velocity_continuity']:>6} "
          f"{s['structural']:>7} {s['total']:>7}")

    grid_k = [0.0015, 0.003, 0.006]
    grid_sigma = [0.035, 0.06]
    grid_alpha = [0.0, 0.5, 1.0]

    best = None
    for k_gain, sigma_s, alpha in itertools.product(grid_k, grid_sigma, grid_alpha):
        filt_samples, response, structural, continuity, score = evaluate(
            objs, keyframes, keyframe_times, base_samples, k_gain, sigma_s, alpha)
        name = f"k{k_gain}_sig{sigma_s}_a{alpha}"
        results.append({
            "variant": name, "k": k_gain, "sigma": sigma_s, "alpha": alpha,
            "score": score, "response": response,
        })
        print(f"{name:<34} {score['exaggeration_in_band']:>6} "
              f"{score['clean_lobes']:>6} {score['ringing_total']:>5} "
              f"{score['velocity_continuity']:>6} {score['structural']:>7} {score['total']:>7}")
        if best is None or score["total"] > best["score"]["total"]:
            best = {"variant": name, "k": k_gain, "sigma": sigma_s, "alpha": alpha,
                    "score": score, "response": response, "samples": filt_samples,
                    "structural": structural}

    print("\nMeilleure variante :", best["variant"], "->", best["score"]["total"])
    for check, (ok, detail) in best["structural"].items():
        if not ok:
            print(f"  STRUCTURE KO [{check}]: {detail}")

    out_dir = os.path.join(out_root, "best")
    os.makedirs(out_dir, exist_ok=True)
    ex.export_keyframe_sequence(
        best["samples"], SAMPLE_HZ, os.path.join(out_dir, "combo_cartoon.rbxmx"),
        anim_name=f"R6_AerialKickCombo_c{base_cycle}_cartoon", decimate_to_hz=EXPORT_HZ)
    pv.plot_curves(best["samples"], SAMPLE_HZ, os.path.join(out_dir, "curves.png"),
                   f"Cycle {base_cycle} + Cartoon Filter ({best['variant']})")
    pv.plot_poses(best["samples"], preview_times, SAMPLE_HZ,
                  os.path.join(out_dir, "poses.png"),
                  f"Cycle {base_cycle} + Cartoon Filter -- poses cles")

    with open(os.path.join(out_root, "sweep.json"), "w") as f:
        json.dump({"base_cycle": base_cycle, "sample_hz": SAMPLE_HZ,
                   "results": results,
                   "best": {kk: best[kk] for kk in ("variant", "k", "sigma", "alpha", "score", "response")}},
                  f, indent=2, ensure_ascii=False)

    return best


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="../output/cartoon")
    parser.add_argument("--base-cycle", type=int, default=BASE_CYCLE)
    args = parser.parse_args()
    main(args.out, args.base_cycle)
