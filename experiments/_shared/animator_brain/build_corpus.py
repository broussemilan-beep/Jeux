"""
Construit le corpus du cerveau a partir des sources disponibles et compare
nos propres exports aux distributions par categorie.

Sorties (versionnees, MESURES DERIVEES uniquement -- jamais les poses) :
    corpus/<source>.json      une fiche par animation
    corpus/categories.json    distributions par categorie (mediane, min, max, n)
    corpus/nos_protos.json    fiches de nos exports .rbxmx
    corpus/<source>_m1_chaine_pics.png, preuve visuelle

Usage : python3 build_corpus.py <battleground_animation_pack_v1.0.1.rbxm>
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))

from animator_brain import audit as A  # noqa: E402
from animator_brain import corpus as C  # noqa: E402
from animator_brain import roblox_export as X  # noqa: E402
from animator_brain import taxonomy as T  # noqa: E402
from animator_brain.plots import peak_chain_chart, side_by_side  # noqa: E402

OUT = os.path.join(HERE, "corpus")
EXPERIMENTS = os.path.join(HERE, "..", "..")
OUR_EXPORTS = {
    "r6_hit_combo/attaquant": ("r6_hit_combo/output/character_attacker_combo.rbxmx", "cinematique"),
    "r6_hit_combo/mannequin": ("r6_hit_combo/output/character_dummy_combo_reaction.rbxmx", "cinematique"),
    "r6_directional_punch/attaquant": ("r6_directional_punch/output/character_attacker_punch.rbxmx", "cinematique"),
    "r6_directional_punch/mannequin": ("r6_directional_punch/output/character_dummy_reaction.rbxmx", "cinematique"),
    "r6_black_hole": ("r6_black_hole/output/black_hole_r6.rbxmx", "cinematique"),
}


def flatten(d, prefix=""):
    out = {}
    for k, v in d.items():
        key = f"{prefix}{k}"
        if isinstance(v, dict):
            out.update(flatten(v, key + "."))
        elif isinstance(v, (int, float)) and not isinstance(v, bool):
            out[key] = float(v)
    return out


def category_stats(fiches):
    by = {}
    for f in fiches:
        by.setdefault(f["categorie"], []).append(f)
    stats = {}
    for cat, fs in sorted(by.items()):
        vals = {}
        for f in fs:
            for k, v in flatten({"timing": f["timing"], "audit": f["audit"]}).items():
                vals.setdefault(k, []).append(v)
        stats[cat] = {
            "n": len(fs),
            "fragile": len(fs) < T.MIN_EXAMPLES,
            "exemples": [f["nom"] for f in fs],
            "mesures": {k: {"mediane": round(float(np.median(v)), 3), "min": round(float(min(v)), 3),
                            "max": round(float(max(v)), 3), "n": len(v)} for k, v in sorted(vals.items())},
        }
    return stats


def main(pack_path):
    os.makedirs(OUT, exist_ok=True)
    source = "battleground_animation_pack_v1.0.1"
    cats = T.SOURCE_CATEGORIES[source]
    fiches = []
    clips = {}
    for s in C.load_rbxm_sequences(pack_path):
        cat = cats[s["name"]]
        w = C.resolve_world(s["frames"])
        ign = C.ignored_by_weight(s)
        m = C.measure(w, s["loop"], ign, strike=cat.startswith("frappe"))
        fiches.append({"source": source, "nom": s["name"], "categorie": cat, "boucle": s["loop"],
                       "poids_nul_fraction": s["poids_nul_fraction"], **m})
        clips[s["name"]] = w
        print(f"  {s['name']:<16} {cat:<14} audit {m['audit_ok']['ok']}/{m['audit_ok']['total']}")
    json.dump(fiches, open(os.path.join(OUT, f"{source}.json"), "w"), indent=1, ensure_ascii=False)
    stats = category_stats(fiches)
    json.dump(stats, open(os.path.join(OUT, "categories.json"), "w"), indent=1, ensure_ascii=False)

    ours = []
    for name, (rel, cat) in OUR_EXPORTS.items():
        path = os.path.join(EXPERIMENTS, rel)
        if not os.path.exists(path):
            print("  absent :", rel)
            continue
        w = [(t, X.solve(p)) for t, p in X.read_kfseq(path)]
        m = C.measure(w, False, (), strike=False)
        ours.append({"source": "nos_protos", "nom": name, "categorie": cat, **m})
        print(f"  {name:<32} audit {m['audit_ok']['ok']}/{m['audit_ok']['total']}  duree {m['timing']['duree_s']} s")
    json.dump(ours, open(os.path.join(OUT, "nos_protos.json"), "w"), indent=1, ensure_ascii=False)

    # preuve visuelle : chaine de pics d'un M1 pro vs notre coup
    rows = [("torse", "Torso"), ("tete", "Head"), ("bras droit", "Right Arm"), ("bras gauche", "Left Arm")]
    rep, clip, sig = A.audit(C.to_samples(clips["[2] M1_1"]), C.brain_rig())
    a = peak_chain_chart(clip, sig, rows, 0.0, clip.t[-1],
                         "PRO [2] M1_1 (pack) -- vitesse par partie, pics marques : armement f0-10, coup f10-21 "
                         "(le BRAS culmine d'abord, puis torse, puis tete), puis tenue", os.path.join(OUT, "_a.png"),
                         width=1200, row_h=70, fps=60)
    ours_w = [(t, X.solve(p)) for t, p in X.read_kfseq(os.path.join(EXPERIMENTS, OUR_EXPORTS["r6_directional_punch/attaquant"][0]))]
    rep2, clip2, sig2 = A.audit(C.to_samples(ours_w), C.brain_rig())
    b = peak_chain_chart(clip2, sig2, rows, 0.0, clip2.t[-1],
                         f"NOTRE r6_directional_punch/attaquant -- meme mesure, {clip2.t[-1]:.2f} s au total",
                         os.path.join(OUT, "_b.png"), width=1200, row_h=70, fps=30)
    side_by_side([a, b], os.path.join(OUT, f"{source}_m1_vs_notre_coup.png"))
    os.remove(a)
    os.remove(b)
    return stats, ours


if __name__ == "__main__":
    main(sys.argv[1])
