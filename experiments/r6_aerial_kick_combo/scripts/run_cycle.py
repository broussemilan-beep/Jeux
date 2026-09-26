import argparse
import json
import os

import anim_engine as ae
import export_kfseq as ex
import measure as ms
import preview as pv
from choreography import CYCLES

SAMPLE_HZ = 60
EXPORT_HZ = 30


def _fine_phases(keyframes, named_phases):
    """Une fenetre de mesure par segment consecutif de keyframes (au lieu
    des 5 phases narratives grossieres). Justification (trouvee au cycle
    1, voir README) : chaque segment n'est borne que par DEUX keyframes
    que j'ai choisies pour representer UN seul geste continu -- un
    changement de signe A L'INTERIEUR d'un tel segment n'est donc jamais
    voulu, c'est un artefact de tangente Bezier influencee par les
    keyframes voisines. Les 5 phases narratives (kick1, kick2, ...)
    servent seulement a l'affichage/au rapport ; elles regroupent souvent
    plusieurs de ces segments avec un changement de sens deliberement
    voulu entre eux (ex. l'anticipation puis l'extension), ce qui rend
    "expected_reversals" difficile a regler juste a cette granularite
    grossiere -- inutile a cette granularite fine."""
    times = sorted(k["time"] for k in keyframes)
    fine = []
    for i in range(len(times) - 1):
        fine.append({"name": f"seg_{i}_{times[i]:.2f}-{times[i+1]:.2f}",
                     "t0": times[i], "t1": times[i + 1], "expected_reversals": {}})
    return fine


def run(cycle_n, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    keyframes, phases, preview_times, engine_opts = CYCLES[cycle_n]()
    duration = max(k["time"] for k in keyframes)
    fine_phases = _fine_phases(keyframes, phases)

    objs = ae.build_rig()
    ae.apply_choreography(objs, keyframes, **engine_opts)
    samples = ae.sample(objs, duration_s=duration, sample_hz=SAMPLE_HZ)

    anim_path = os.path.join(out_dir, "combo.rbxmx")
    _, n_kf = ex.export_keyframe_sequence(
        samples, SAMPLE_HZ, anim_path,
        anim_name=f"R6_AerialKickCombo_cycle{cycle_n}",
        decimate_to_hz=EXPORT_HZ,
    )

    keyframe_times = sorted(k["time"] for k in keyframes)
    smoothness = ms.curve_smoothness(samples, SAMPLE_HZ, fine_phases)
    twist = ms.twist_reversals(samples, SAMPLE_HZ, fine_phases)
    continuity = ms.velocity_continuity(samples, SAMPLE_HZ, keyframe_times)
    structural = ms.r6_structural_compliance(objs, keyframes, samples)
    composite = ms.composite_score(smoothness, twist, structural, continuity)

    poses_path = os.path.join(out_dir, "poses.png")
    curves_path = os.path.join(out_dir, "curves.png")
    pv.plot_poses(samples, preview_times, SAMPLE_HZ, poses_path,
                  f"Cycle {cycle_n} -- poses cles")
    pv.plot_curves(samples, SAMPLE_HZ, curves_path,
                   f"Cycle {cycle_n} -- angle (deg) vs temps par articulation")

    metrics = {
        "cycle": cycle_n,
        "duration_s": duration,
        "n_keyframes_exported": n_kf,
        "smoothness_per_joint": smoothness,
        "velocity_continuity_at_keyframes": continuity,
        "twist_reversals": twist,
        "structural_checks": {k: {"ok": v[0], "detail": v[1]} for k, v in structural.items()},
        "composite_score": composite,
    }
    metrics_path = os.path.join(out_dir, "metrics.json")
    with open(metrics_path, "w") as f:
        json.dump(metrics, f, indent=2, ensure_ascii=False)

    print(json.dumps(composite, indent=2))
    for phase_name, parts in twist.items():
        extras = {p: r["extra"] for p, r in parts.items() if r["extra"] > 0}
        if extras:
            print(f"  tortillement non voulu en phase '{phase_name}': {extras}")
    for check, (ok, detail) in structural.items():
        if not ok:
            print(f"  STRUCTURE KO [{check}]: {detail}")

    return metrics


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--cycle", type=int, required=True)
    parser.add_argument("--out", type=str, default=None)
    args = parser.parse_args()
    out_dir = args.out or f"../output/cycle{args.cycle}"
    run(args.cycle, out_dir)
