"""
Planche d'ÉTUDE d'une référence vidéo / GIF, pour regarder son ANIMATION
(corps, timing, tenues, contraste lent/rapide) et pas seulement ses effets.

Ce que l'outil fait (et rien de plus) :
- extrait les images à cadence fixe (30 i/s par défaut) ;
- énergie du mouvement e[i] = écart moyen entre deux images successives
  (niveaux de gris réduits) ; un changement de plan = pic énorme, marqué
  « coupe » ;
- TENUES = suites d'images quasi immobiles (e < seuil) d'au moins 3 images
  (100 ms) : c'est là qu'une pose est donnée à voir ;
- planche : la 1re image de chaque tenue (avec sa durée) + les pics de
  mouvement, dans l'ordre du temps, + la courbe d'énergie en bas.
Les choix de ce qu'il FAUT y voir restent à l'œil : l'outil ne juge rien.

Usage : python3 planche_ref.py <video|gif> <sortie.png> [fps (0 = natif, max 30)] [largeur_vignette]
Imprime un résumé JSON (tenues, part du temps tenu, contraste).
"""
import json
import os
import subprocess
import sys
import tempfile

import numpy as np
from PIL import Image, ImageDraw


def extraire(src, fps=30, largeur=480):
    d = tempfile.mkdtemp(prefix="planche_")
    subprocess.run(["ffmpeg", "-v", "error", "-i", src, "-vf", f"fps={fps},scale={largeur}:-2", os.path.join(d, "f%04d.png")],
                   check=True)
    fs = sorted(os.listdir(d))
    return [Image.open(os.path.join(d, f)).convert("RGB") for f in fs]


def energie(ims):
    g = [np.asarray(im.convert("L").resize((160, max(1, int(160 * im.size[1] / im.size[0])))), dtype=np.float32) for im in ims]
    return [0.0] + [float(np.mean(np.abs(b - a))) for a, b in zip(g, g[1:])]


def analyser(e, fps):
    e = np.array(e)
    mv = e[e > 0.5]
    med = float(np.median(mv)) if len(mv) else 1.0
    coupe = max(25.0, 6 * med)
    seuil = max(0.6, 0.18 * med)
    tenues, i = [], 1
    while i < len(e):
        if e[i] < seuil:
            j = i
            while j < len(e) and e[j] < seuil:
                j += 1
            if j - i >= 3:
                tenues.append((i, j - i))
            i = j
        else:
            i += 1
    coupes = [int(k) for k in np.where(e > coupe)[0]]
    mob = e[(e >= seuil) & (e <= coupe)]
    return {
        "duree_s": round(len(e) / fps, 2),
        "tenues": [{"t": round(a / fps, 2), "duree_s": round(n / fps, 2)} for a, n in tenues],
        "part_tenue": round(sum(n for _, n in tenues) / max(1, len(e)), 2),
        "tenue_mediane_s": round(float(np.median([n for _, n in tenues])) / fps, 2) if tenues else 0,
        "contraste_p90_p50": round(float(np.percentile(mob, 90) / max(np.percentile(mob, 50), 1e-3)), 2) if len(mob) else None,
        "coupes_s": [round(k / fps, 2) for k in coupes],
        "_seuil": round(seuil, 2), "_coupe": round(coupe, 1),
    }, tenues, coupes


def planche(ims, e, fps, tenues, coupes, sortie, titre="", vign=240, max_v=24):
    e = np.array(e)
    choix = {a: f"tenue {n / fps:.2f}s" for a, n in tenues}
    # pics de mouvement (hors coupes) : maxima locaux les plus forts
    pics = [k for k in range(2, len(e) - 2) if e[k] == e[k - 2:k + 3].max() and k not in coupes and e[k] > 0]
    pics = sorted(pics, key=lambda k: -e[k])[:max(4, max_v - len(choix))]
    for k in pics:
        choix.setdefault(k, "pic")
    for k in coupes:
        choix.setdefault(k, "coupe")
    # priorité : tenues les plus longues, puis pics les plus forts, puis coupes
    rang = sorted(choix, key=lambda k: (0, -dict(tenues).get(k, 0)) if "tenue" in choix[k] else ((1, -e[k]) if choix[k] == "pic" else (2, 0)))
    ks = sorted(rang[:max_v])
    w0, h0 = ims[0].size
    vh = int(vign * h0 / w0)
    cols = 6
    rows = (len(ks) + cols - 1) // cols
    H = 20 + rows * (vh + 14) + 130
    S = Image.new("RGB", (cols * vign, H), (255, 255, 255))
    d = ImageDraw.Draw(S)
    d.text((4, 4), titre, fill=(0, 0, 0))
    for n, k in enumerate(ks):
        x, y = (n % cols) * vign, 20 + (n // cols) * (vh + 14)
        S.paste(ims[k].resize((vign, vh)), (x, y))
        col = (0, 110, 200) if "tenue" in choix[k] else ((200, 40, 40) if choix[k] == "pic" else (120, 120, 120))
        d.text((x + 2, y + vh + 1), f"{k / fps:.2f}s {choix[k]}", fill=col)
    # courbe
    y0, W = H - 120, cols * vign
    m = max(1e-3, float(np.percentile(e, 99)))
    for a, n in tenues:
        d.rectangle([int(a * W / len(e)), y0, int((a + n) * W / len(e)), y0 + 110], fill=(215, 232, 250))
    for k in range(len(e)):
        x = int(k * W / len(e)); h = int(108 * min(1.0, e[k] / m))
        d.line([x, y0 + 110, x, y0 + 110 - h], fill=(150, 150, 150) if k in coupes else (40, 40, 40))
    for s in range(int(len(e) / fps) + 1):
        x = int(s * fps * W / len(e)); d.line([x, y0 + 106, x, y0 + 110], fill=(200, 0, 0)); d.text((x + 2, y0 - 12), f"{s}s", fill=(200, 0, 0))
    d.text((4, y0 + 1), "energie du mouvement (bleu = tenues)", fill=(0, 0, 0))
    S.save(sortie)


def cadence_native(src):
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=avg_frame_rate",
                        "-of", "csv=p=0", src], capture_output=True, text=True).stdout.strip()
    try:
        a, b = r.split("/")
        return float(a) / float(b)
    except (ValueError, ZeroDivisionError):
        return 30.0


def main(src, sortie, fps=None, vign=240):
    # cadence native si <= 30 i/s (GIF à 16,7 : sinon une image sur deux serait
    # dupliquée et les tenues de 1 image deviendraient des « tenues »)
    fps = fps or min(30.0, cadence_native(src))
    ims = extraire(src, fps)
    e = energie(ims)
    res, tenues, coupes = analyser(e, fps)
    planche(ims, e, fps, tenues, coupes, sortie, titre=os.path.basename(src), vign=vign)
    return res


if __name__ == "__main__":
    fps = float(sys.argv[3]) if len(sys.argv) > 3 and float(sys.argv[3]) > 0 else None
    vign = int(sys.argv[4]) if len(sys.argv) > 4 else 240
    print(json.dumps(main(sys.argv[1], sys.argv[2], fps, vign), ensure_ascii=False))
