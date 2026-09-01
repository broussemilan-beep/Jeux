"""
Produit le JSON du lecteur HTML.

Chaque variante est EXPORTEE en .rbxmx puis RESOLUE par l'equation du
moteur Roblox (`resolve_rbxmx`), avec les C0/C1 du vrai rig. Le lecteur
affiche donc ce que Roblox calculerait a partir du fichier livre, et non
ce que j'ai ecrit -- c'est precisement cette distinction qui avait laisse
passer le mauvais repere de joint, la pose racine ignoree et le pivot des
membres.
"""
import json
import os
import tempfile

import anim_engine as ae
import cartoon_filter as cf
import export_kfseq as ex
import resolve_rbxmx as rr
from choreography import CYCLES
from r6_rig import PART_ORDER, PART_SIZES

SAMPLE_HZ = 120
EXPORT_HZ = 30


def build_variant(cycle_n, k_gain=0.0, sigma_s=0.06, alpha=0.0):
    keyframes, phases, _pt, engine_opts = CYCLES[cycle_n]()
    duration = max(k["time"] for k in keyframes)
    kts = sorted(k["time"] for k in keyframes)

    objs = ae.build_rig()
    ae.apply_choreography(objs, keyframes, **engine_opts)
    samples = ae.sample(objs, duration_s=duration, sample_hz=SAMPLE_HZ)

    if k_gain or alpha:
        local, _ = cf.apply_to_samples(samples, SAMPLE_HZ, kts,
                                       k_gain=k_gain, sigma_s=sigma_s, alpha=alpha)
        n = len(local[PART_ORDER[0]])
        world = ae._world_positions(local, n)
        samples = {p: [(local[p][i][0], local[p][i][1], local[p][i][2], world[p][i])
                       for i in range(n)] for p in PART_ORDER}

    with tempfile.NamedTemporaryFile(suffix=".rbxmx", delete=False) as tmp:
        path = tmp.name
    ex.export_keyframe_sequence(samples, SAMPLE_HZ, path, decimate_to_hz=EXPORT_HZ)
    frames = rr.resolve_to_frames(path)
    os.unlink(path)

    return {
        "duration": duration,
        "phases": [{"name": p["name"], "t0": p["t0"], "t1": p["t1"]} for p in phases],
        "frames": frames,
    }


if __name__ == "__main__":
    out = {
        "fps": EXPORT_HZ,
        "part_sizes": {p: list(PART_SIZES[p]) for p in PART_ORDER},
        "part_order": PART_ORDER,
        "variants": {
            # jambes seules (bras en simple contrepoids)
            "legs": build_variant(2),
            # haut du corps actif : garde, spotting, fermeture des bras
            "fullbody": build_variant(6),
            # idem + exageration cartoon, au gain le plus fort qui respecte
            # encore la contrainte "aucun coup de poing"
            "cartoon": build_variant(6, k_gain=0.0015, sigma_s=0.035, alpha=1.0),
            # recreation de la reference video (lunge -> montee tenue ->
            # ramasse -> spin -> pivot d'atterrissage), + filtre cartoon
            "reference": build_variant(7, k_gain=0.0015, sigma_s=0.06, alpha=1.0),
        },
    }
    path = os.environ.get("PREVIEW_OUT", "/tmp/combo_ab_data.json")
    with open(path, "w") as f:
        json.dump(out, f, separators=(",", ":"))
    print("ecrit", path, os.path.getsize(path), "octets")
    for name, v in out["variants"].items():
        ys = [f["Torso"]["p"][1] for f in v["frames"]]
        print(f"  {name}: {len(v['frames'])} frames, Torso Y de {min(ys):.2f} a {max(ys):.2f}")
