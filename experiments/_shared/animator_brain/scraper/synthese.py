"""
Synthese des fiches scrapees -> corpus/refs/SYNTHESE.md : ce que les
references de reference (anime sakuga, Danbooru) disent, mesure par mesure,
face aux refs de Milan (corpus/clips) et a nos versions. C'est ce que le
cerveau lit pour confirmer ou affaiblir une hypothese (hypotheses.json) --
jamais une regle recopiee.

Usage : python3 synthese.py
"""
import glob
import json
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
BRAIN = os.path.dirname(HERE)
REFS = os.path.join(BRAIN, "corpus", "refs")


def load(pattern):
    return [json.load(open(f)) for f in sorted(glob.glob(pattern))]


def stats(fiches):
    def col(fn):
        v = [fn(f) for f in fiches]
        return [x for x in v if x is not None]
    imp = [f for f in fiches if f["impacts"]["nombre"] > 0 and f["impacts"].get("profil_autour")]
    out = {
        "n": len(fiches),
        "image distincte (ms, mediane)": col(lambda f: f["cadence"]["image_distincte_mediane_ms"]),
        "impacts par seconde": col(lambda f: f["impacts"]["par_seconde"]),
        "contraste d'energie": col(lambda f: f["energie"]["contraste_p95_sur_mediane"]),
        "part de tenues": col(lambda f: f["tenues"]["part_du_temps"]),
        "part des pics qui montent": col(lambda f: (f.get("mouvement") or {}).get("part_des_pics_qui_montent")),
        "tenue avant le choc (clips avec impacts)": f"{sum(f['impacts']['profil_autour']['tenue_avant_choc'] for f in imp)}/{len(imp)}",
        "explosion apres le choc (clips avec impacts)": f"{sum(f['impacts']['profil_autour']['explosion_apres'] for f in imp)}/{len(imp)}",
    }
    return out


def fmt(v):
    if isinstance(v, list):
        if not v:
            return "-"
        return f"{np.median(v):.2f} [{np.percentile(v, 25):.2f}-{np.percentile(v, 75):.2f}]"
    return str(v)


def main():
    groups = {}
    for src in sorted(os.listdir(REFS)) if os.path.isdir(REFS) else []:
        if os.path.isdir(os.path.join(REFS, src)) and src != "images":
            groups[src] = load(os.path.join(REFS, src, "*.json"))
    clips = load(os.path.join(BRAIN, "corpus", "clips", "*.json"))
    groups["refs de Milan"] = [c for c in clips if not c["clip"].startswith("nous_")]
    groups["nos versions"] = [c for c in clips if c["clip"].startswith("nous_")]
    S = {k: stats(v) for k, v in groups.items() if v}
    keys = list(next(iter(S.values())).keys())
    lines = ["# Synthese des references scrapees", "",
             "Genere par `scraper/synthese.py`. Mediane [quartiles]. Les fiches sont des mesures video",
             "(clip_analyzer) ; les limites de chaque mesure sont dans CERVEAU_V2.md et ANGLES_MORTS.md §7",
             "(les arrets en 2D ne sont pas valides ; la direction des pics l'est).", "",
             "| mesure | " + " | ".join(S) + " |", "|---|" + "---|" * len(S)]
    for k in keys:
        lines.append(f"| {k} | " + " | ".join(fmt(S[g][k]) for g in S) + " |")
    # oeuvres et artistes les plus presents (sakugabooru : etiquettes)
    tags = {}
    for f in groups.get("sakugabooru", []) + groups.get("danbooru", []):
        for t in f["source"].get("tags", "").split():
            tags[t] = tags.get(t, 0) + 1
    common = {"fighting", "animated", "effects", "smears", "background_animation", "debris", "smoke", "impact_frames",
              "sound", "video", "webm", "mp4", "has_audio"}
    top = [f"{t} ({n})" for t, n in sorted(tags.items(), key=lambda x: -x[1]) if t not in common][:30]
    lines += ["", "## Etiquettes les plus frequentes (oeuvres, artistes, techniques)", "", ", ".join(top) or "-"]
    # meilleurs clips par score de la source
    best = sorted(groups.get("sakugabooru", []) + groups.get("danbooru", []), key=lambda f: -(f["source"].get("score") or 0))[:15]
    lines += ["", "## Clips les mieux notes par les fans (a regarder en priorite)", "",
              "| score | source | lien | image distincte ms | impacts/s | pics qui montent |", "|---|---|---|---|---|---|"]
    for f in best:
        s = f["source"]
        lines.append(f"| {s.get('score')} | {s['nom']} | {s.get('url')} | {f['cadence']['image_distincte_mediane_ms']} | "
                     f"{f['impacts']['par_seconde']} | {(f.get('mouvement') or {}).get('part_des_pics_qui_montent')} |")
    open(os.path.join(REFS, "SYNTHESE.md"), "w").write("\n".join(lines) + "\n")
    print("\n".join(lines[:20]))


if __name__ == "__main__":
    main()
