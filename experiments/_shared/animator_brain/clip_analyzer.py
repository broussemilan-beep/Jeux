"""
Analyseur de clips (etape 1 du cerveau v2, voir CERVEAU_V2.md) : n'importe
quelle video ou GIF -> une FICHE chiffree (JSON) + une planche contact (PNG).
Sert a nos productions comme aux references (Roblox, anime, manga anime,
jeux de combat...), pour qu'elles soient comparables.

Mesure, en 1-3 s par clip, ce qu'on a appris a regarder a la main :
- cadence de dessin : duree mediane d'une image distincte (en 1, 2, 3...) ;
- tenues : poses gelees >= 150 ms, leur nombre et leur part du temps ;
- energie du mouvement : courbe, contraste pic / mediane, part rapide ;
- cartes d'impact : images blanches, noires, silhouettes (fiche IMPACT HAVEN),
  leurs durees et le rythme entre elles ;
- profil autour des impacts : le mouvement freine-t-il AVANT le choc ?
- coupes de plan et secousses de camera ;
- palette dominante.

Ce qu'il NE mesure PAS : les poses (ligne d'action, d'ou part un coup...).
Les estimateurs de squelette ne marchent ni sur les dessins ni sur les blocs
R6 : la lecture des poses reste un jugement, fait sur la planche contact.

Recadrage automatique sur la zone qui bouge (les captures d'ecran de
telephone ont une interface fixe autour du jeu).

Dependances : ffmpeg, numpy, Pillow ; OpenCV (opencv-python-headless<4.10,
numpy<2 pour rester compatible avec bpy) pour les secousses de camera.

Usage : python3 clip_analyzer.py <clip> [<clip> ...] --out <dossier fiches>
        [--sheets <dossier planches>] [--label <nom>]
"""
import argparse
import hashlib
import json
import os
import subprocess

import numpy as np
from PIL import Image, ImageDraw

FPS = 60                 # tout est ramene a 60 i/s : une image tenue = des doublons
GRAY_W = 160             # largeur de travail (niveaux de gris)
CHANGE = 1.2             # difference moyenne (0-255) au-dessus de laquelle l'image a change
HOLD_MS = 150            # une tenue = une pose gelee au moins aussi longtemps


def _probe(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                          "stream=width,height:format=duration", "-of", "json", path],
                         capture_output=True, text=True).stdout
    d = json.loads(out)
    s = d["streams"][0]
    return int(s["width"]), int(s["height"]), float(d["format"].get("duration", 0) or 0)


def _decode(path, w, h, width):
    hh = int(round(h * width / w / 2)) * 2
    cmd = ["ffmpeg", "-v", "error", "-i", path, "-vf", f"fps={FPS},scale={width}:{hh}", "-f", "rawvideo",
           "-pix_fmt", "rgb24", "-"]
    raw = subprocess.run(cmd, capture_output=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, hh, width, 3)


def _autocrop(rgb):
    """Boite de la zone qui bouge (ecart-type temporel), marge 4 %."""
    g = rgb.mean(axis=3)
    std = g.std(axis=0)
    mask = std > max(6.0, np.percentile(std, 60))
    ys, xs = np.where(mask)
    if len(xs) < 50:
        return 0, 0, rgb.shape[2], rgb.shape[1]
    x0, x1 = np.percentile(xs, [1, 99]).astype(int)
    y0, y1 = np.percentile(ys, [1, 99]).astype(int)
    mx, my = int(0.04 * rgb.shape[2]), int(0.04 * rgb.shape[1])
    return max(0, x0 - mx), max(0, y0 - my), min(rgb.shape[2], x1 + mx), min(rgb.shape[1], y1 + my)


def _runs(flags):
    """[(debut, longueur)] des suites de True."""
    out, i, n = [], 0, len(flags)
    while i < n:
        if flags[i]:
            j = i
            while j + 1 < n and flags[j + 1]:
                j += 1
            out.append((i, j - i + 1))
            i = j + 1
        else:
            i += 1
    return out


def analyze(path, sheet_dir=None, label=None):
    w, h, dur = _probe(path)
    rgb = _decode(path, w, h, GRAY_W)
    x0, y0, x1, y1 = _autocrop(rgb)
    rgb = rgb[:, y0:y1, x0:x1]
    g = rgb.mean(axis=3).astype(np.float32)
    n = len(g)
    ms = 1000.0 / FPS
    # --- cartes plein ecran
    white = (g > 235).mean(axis=(1, 2))
    dark = (g < 40).mean(axis=(1, 2))
    kind = np.array([("blanc" if wh > 0.85 else "silhouette" if (dk > 0.5 and wh > 0.05) else "noir" if dk > 0.9
                      else "") for wh, dk in zip(white, dark)])
    card = kind != ""
    # --- changements d'image, tenues, cadence
    diff = np.r_[0.0, np.abs(np.diff(g, axis=0)).mean(axis=(1, 2))]
    changed = diff > CHANGE
    changed[0] = True
    img_runs = []                         # duree de chaque image distincte (ms)
    last = 0
    for i in range(1, n):
        if changed[i]:
            img_runs.append((i - last) * ms)
            last = i
    img_runs.append((n - last) * ms)
    img_runs = np.array(img_runs)
    holds = [(s, L) for s, L in _runs(~changed) if (L + 1) * ms >= HOLD_MS and not card[s:s + L].any()]
    hold_ms = sum((L + 1) * ms for _s, L in holds)
    # cadence : duree mediane d'une image distincte HORS tenues
    moving = img_runs[img_runs < HOLD_MS]
    cad_ms = float(np.median(moving)) if len(moving) else float("nan")
    cadence = ("en 1" if cad_ms < 25 else "en 2" if cad_ms < 45 else "en 3" if cad_ms < 70 else
               "en 4+") + f" a {FPS} i/s de lecture"
    # --- energie (hors cartes)
    e = diff.copy()
    e[card] = 0.0
    e[np.r_[False, card[:-1]]] = 0.0      # l'image qui suit une carte : saut artificiel
    live = e[e > CHANGE]
    k = max(1, int(round(100 / ms)))      # lissage 100 ms
    es = np.convolve(e, np.ones(k) / k, mode="same")
    energy = {
        "mediane": round(float(np.median(live)), 2) if len(live) else 0.0,
        "pic_p95": round(float(np.percentile(live, 95)), 2) if len(live) else 0.0,
        "contraste_p95_sur_mediane": round(float(np.percentile(live, 95) / max(1e-6, np.median(live))), 2)
        if len(live) else 0.0,
        "part_rapide": round(float(np.mean(es > 0.5 * es.max())), 3) if es.max() > 0 else 0.0,
    }
    # --- cartes d'impact
    cards = []
    for s, L in _runs(card):
        cards.append({"t_s": round(s / FPS, 3), "type": kind[s], "duree_ms": round(L * ms)})
    impacts = []                          # un impact = une salve de cartes (ecart < 120 ms)
    for c in cards:
        if impacts and c["t_s"] - (impacts[-1]["t_s"] + impacts[-1]["duree_ms"] / 1000) < 0.12:
            impacts[-1]["cartes"].append(c["type"])
            impacts[-1]["duree_ms"] = round((c["t_s"] - impacts[-1]["t_s"]) * 1000 + c["duree_ms"])
        else:
            impacts.append({"t_s": c["t_s"], "duree_ms": c["duree_ms"], "cartes": [c["type"]]})
    gaps = np.diff([i["t_s"] for i in impacts]) if len(impacts) > 1 else np.array([])
    # profil de mouvement autour des impacts (median), -0,2 s .. +0,25 s
    prof = []
    for imp in impacts:
        i0 = int(round(imp["t_s"] * FPS))
        i1 = i0 + int(round(imp["duree_ms"] / ms))
        before = e[max(0, i0 - 12):i0]
        after = e[i1:i1 + 15]
        if len(before) == 12 and len(after) == 15:
            prof.append(np.r_[before, after])
    profil = None
    if prof:
        P = np.median(np.array(prof), axis=0)
        approche, juste_avant, apres = P[:6].mean(), P[6:12].mean(), P[12:18].mean()
        profil = {"approche": round(float(approche), 2), "0,1 s avant": round(float(juste_avant), 2),
                  "0,1 s apres": round(float(apres), 2),
                  "tenue_avant_choc": bool(juste_avant < 0.5 * approche),
                  "explosion_apres": bool(apres > 1.5 * max(juste_avant, 1e-6))}
    # --- coupes de plan (histogrammes) et secousses (correlation de phase)
    cuts = []
    prev = None
    for i in range(n):
        if card[i]:
            continue
        hist = np.histogram(g[i], bins=24, range=(0, 255))[0].astype(float)
        hist /= hist.sum() + 1e-9
        if prev is not None:
            j, hp = prev
            inter = np.minimum(hist, hp).sum()
            if inter < 0.45 and diff[i] > 12:
                cuts.append(round(i / FPS, 3))
        prev = (i, hist)
    shake = None
    try:
        import cv2
        shifts = []
        for i in range(1, n):
            if card[i] or card[i - 1] or not changed[i]:
                continue
            (dx, dy), _r = cv2.phaseCorrelate(g[i - 1].astype(np.float64), g[i].astype(np.float64))
            shifts.append(np.hypot(dx, dy) / g.shape[2])
        if shifts:
            s = np.array(shifts)
            shake = {"decalage_median_pct": round(float(np.median(s) * 100), 2),
                     "decalage_p95_pct": round(float(np.percentile(s, 95) * 100), 2)}
    except ImportError:
        pass
    # --- palette (mosaique de 12 images)
    idx = np.linspace(0, n - 1, min(12, n)).astype(int)
    mosaic = Image.fromarray(np.concatenate([rgb[i] for i in idx], axis=1))
    q = mosaic.quantize(colors=6, method=Image.Quantize.MEDIANCUT)
    pal = q.getpalette()[:18]
    counts = sorted(q.getcolors(), reverse=True)
    palette = [{"hex": "#%02x%02x%02x" % tuple(pal[3 * c:3 * c + 3]), "part": round(cnt / (mosaic.width * mosaic.height), 3)}
               for cnt, c in counts]
    # --- interet (HEURISTIQUE, a calibrer sur les notes de Milan) : contraste de
    # temps, part de tenues, rythme d'impacts. Chaque terme est dit.
    hold_frac = hold_ms / (n * ms)
    contrast = energy["contraste_p95_sur_mediane"]
    terms = {
        "contraste_de_temps": min(1.0, max(0.0, (contrast - 1.5) / 3.5)),
        "tenues_presentes": 1.0 - min(1.0, abs(hold_frac - 0.3) / 0.3),
        "impacts_rythmes": min(1.0, len(impacts) / max(1.0, n / FPS) / 1.5),
    }
    interest = round(100 * (0.45 * terms["contraste_de_temps"] + 0.35 * terms["tenues_presentes"]
                            + 0.20 * terms["impacts_rythmes"]))
    fiche = {
        "clip": label or os.path.basename(path),
        "sha1_16": hashlib.sha1(open(path, "rb").read()).hexdigest()[:16],
        "duree_s": round(n / FPS, 2), "resolution": [w, h], "zone_analysee": [int(x0), int(y0), int(x1), int(y1)],
        "cadence": {"image_distincte_mediane_ms": round(cad_ms, 1), "lecture": cadence},
        "tenues": {"nombre": len(holds), "part_du_temps": round(hold_frac, 3),
                   "plus_longue_ms": round(max([(L + 1) * ms for _s, L in holds], default=0))},
        "energie": energy,
        "impacts": {"nombre": len(impacts), "par_seconde": round(len(impacts) / max(1e-6, n / FPS), 2),
                    "ecart_median_s": round(float(np.median(gaps)), 3) if len(gaps) else None,
                    "cartes": cards[:60], "profil_autour": profil},
        "coupes": {"nombre": len(cuts), "t_s": cuts[:40]},
        "camera": shake,
        "palette": palette,
        "interet_heuristique": {"score_100": interest, "termes": {k: round(v, 2) for k, v in terms.items()},
                                "avertissement": "heuristique non calibree : a comparer aux notes de Milan"},
    }
    if sheet_dir:
        os.makedirs(sheet_dir, exist_ok=True)
        fiche["planche"] = _sheet(rgb, card, kind, impacts, os.path.join(
            sheet_dir, os.path.splitext(os.path.basename(label or path))[0] + ".png"))
    return fiche


def _sheet(rgb, card, kind, impacts, out, cols=8):
    """Planche : 16 images regulieres + 8 autour des impacts (juste avant /
    juste apres les cartes), horodatees."""
    n = len(rgb)
    picks = list(np.linspace(0, n - 1, 16).astype(int))
    for imp in impacts[:4]:
        i0 = int(round(imp["t_s"] * FPS))
        picks += [max(0, i0 - 3), min(n - 1, i0 + int(round(imp["duree_ms"] * FPS / 1000)) + 3)]
    picks = sorted(set(picks))[:32]
    th_w = 220
    th_h = int(rgb.shape[1] * th_w / rgb.shape[2])
    rows = (len(picks) + cols - 1) // cols
    s = Image.new("RGB", (th_w * cols, th_h * rows), "black")
    for k, i in enumerate(picks):
        t = Image.fromarray(rgb[i]).resize((th_w, th_h))
        d = ImageDraw.Draw(t)
        d.rectangle((0, 0, 58, 11), fill="black")
        d.text((2, 0), f"{i / FPS:5.2f}s{' *' if card[i] else ''}", fill=(255, 255, 0))
        s.paste(t, ((k % cols) * th_w, (k // cols) * th_h))
    s.save(out)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("clips", nargs="+")
    ap.add_argument("--out", required=True)
    ap.add_argument("--sheets")
    ap.add_argument("--label", action="append")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    for i, c in enumerate(a.clips):
        label = a.label[i] if a.label and i < len(a.label) else None
        f = analyze(c, a.sheets, label)
        name = os.path.splitext(os.path.basename(label or c))[0]
        json.dump(f, open(os.path.join(a.out, name + ".json"), "w"), indent=1, ensure_ascii=False)
        imp = f["impacts"]
        print(f"{name:34s} {f['duree_s']:5.1f}s  cadence {f['cadence']['image_distincte_mediane_ms']:5.1f} ms  "
              f"tenues {f['tenues']['nombre']:2d} ({f['tenues']['part_du_temps']:.0%})  contraste "
              f"{f['energie']['contraste_p95_sur_mediane']:4.1f}  impacts {imp['nombre']:2d}  coupes "
              f"{f['coupes']['nombre']:2d}  interet {f['interet_heuristique']['score_100']}")


if __name__ == "__main__":
    main()
