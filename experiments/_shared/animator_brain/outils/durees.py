"""
DURÉES à l'écran : une vidéo (la nôtre ou une réf) vue sur un axe de TEMPS
RÉEL, pas en images choisies.

Né du retour de Milan sur la v12 (« le dragon apparaît 0,5 seconde ») : mes
planches montraient 8 beaux instants choisis, elles ne montraient pas que
le dragon de l'invocation ne vivait que 0,57 s quand le GIF de Goku tient
l'invocation 2 s. Une planche d'images fixes cache la durée (CARNET 4b.12).

Ce que l'outil fait (et rien de plus) :
- extrait les images à cadence FIXE (défaut 30 i/s, temps réel, GIF compris) ;
- par image : part des pixels d'EFFET (très clairs, ou clairs et saturés :
  additif, feu, énergie), saut d'image (flash, carte, coupe), mouvement ;
- ÉPISODES D'EFFET : suites d'images où la part d'effet dépasse un seuil,
  avec leur durée (s), leur pic et le temps jusqu'au pic ;
- TENUES : suites d'images quasi immobiles >= 100 ms ;
- bande temporelle (PNG) : une vignette tous les `pas` s (défaut 0,1 s),
  10 par ligne = 1 s par ligne ; les courbes en bas avec les secondes. Ce
  qui dure 0,5 s occupe 5 vignettes, ce qui dure 2 s en occupe 20 : la
  durée se VOIT.

C'est une aide pour regarder : aucun seuil de qualité. Comparer notre
vidéo à la réf sur le même axe de temps (même `pas`), c'est tout.

Usage : python3 durees.py <video|gif> <sortie.png> [pas=0.1] [debut_s] [fin_s]
Imprime un résumé JSON (épisodes d'effet, tenues, durée totale).
"""
import json
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from planche_ref import extraire  # noqa: E402

FPS = 30


def signaux(ims):
    """Par image : effet (part de pixels d'effet), saut (écart à l'image
    précédente), en [0, 1]."""
    out, prev = [], None
    for im in ims:
        a = np.asarray(im.resize((160, max(1, int(160 * im.size[1] / im.size[0])))), dtype=np.float32) / 255.0
        mx, mn = a.max(axis=2), a.min(axis=2)
        # effet : quasi blanc, OU clair et saturé (feu, énergie, additif)
        eff = (mx > 0.93) | ((mx > 0.6) & ((mx - mn) / (mx + 1e-6) > 0.55))
        lum = a.mean(axis=2)
        saut = 0.0 if prev is None else float(np.mean(np.abs(lum - prev)))
        prev = lum
        out.append({"effet": float(np.mean(eff)), "saut": saut})
    return out


def episodes(v, fps, seuil, min_img=2):
    """Suites d'images où v > seuil : [(debut_s, duree_s, pic, t_pic_s)]."""
    ep, i = [], 0
    while i < len(v):
        if v[i] > seuil:
            j = i
            while j < len(v) and v[j] > seuil:
                j += 1
            if j - i >= min_img:
                k = i + int(np.argmax(v[i:j]))
                ep.append({"debut_s": round(i / fps, 2), "duree_s": round((j - i) / fps, 2),
                           "pic": round(float(v[k]), 3), "montee_s": round((k - i) / fps, 2)})
            i = j
        else:
            i += 1
    return ep


def tenues(saut, fps, seuil=0.012, min_s=0.1):
    t, i = [], 1
    while i < len(saut):
        if saut[i] < seuil:
            j = i
            while j < len(saut) and saut[j] < seuil:
                j += 1
            if (j - i) / fps >= min_s:
                t.append({"debut_s": round(i / fps, 2), "duree_s": round((j - i) / fps, 2)})
            i = j
        else:
            i += 1
    return t


def bande(ims, sig, fps, pas, t0, largeur=150):
    idx = [int(round(k * pas * fps)) for k in range(int(len(ims) / (pas * fps)) + 1)]
    idx = [i for i in idx if i < len(ims)]
    w = largeur
    h = int(w * ims[0].size[1] / ims[0].size[0])
    par_ligne = max(1, int(round(1.0 / pas)))
    lignes = (len(idx) + par_ligne - 1) // par_ligne
    H_courbe = 90
    im = Image.new("RGB", (w * par_ligne, (h + 14) * lignes + H_courbe + 16), (18, 18, 20))
    d = ImageDraw.Draw(im)
    for n, i in enumerate(idx):
        x, y = (n % par_ligne) * w, (n // par_ligne) * (h + 14)
        im.paste(ims[i].resize((w, h)), (x, y + 14))
        d.text((x + 3, y + 1), f"{t0 + i / fps:.1f}s", fill=(230, 230, 230))
    # courbes : effet (orange) et saut (bleu), axe en secondes
    y0 = (h + 14) * lignes + 8
    W = w * par_ligne
    e = np.array([s["effet"] for s in sig])
    j = np.array([s["saut"] for s in sig])
    n = len(sig)
    for arr, col, k in ((e, (255, 160, 40), 1.0 / max(1e-6, e.max())), (j, (90, 160, 255), 1.0 / max(1e-6, j.max()))):
        pts = [(int(q / max(1, n - 1) * (W - 1)), int(y0 + H_courbe - arr[q] * k * (H_courbe - 4))) for q in range(n)]
        d.line(pts, fill=col, width=2)
    for s in range(int(n / fps) + 1):
        x = int(s * fps / max(1, n - 1) * (W - 1))
        d.line([(x, y0), (x, y0 + H_courbe)], fill=(70, 70, 70))
        d.text((x + 2, y0), f"{t0 + s:.0f}s", fill=(200, 200, 200))
    d.text((4, y0 + H_courbe - 12), "orange = part d'effet ; bleu = saut d'image", fill=(200, 200, 200))
    return im


def main(src, sortie, pas=0.1, debut=None, fin=None):
    ims = extraire(src, fps=FPS, largeur=320)
    i0 = int((debut or 0) * FPS)
    i1 = int(fin * FPS) if fin else len(ims)
    ims = ims[i0:i1]
    sig = signaux(ims)
    e = np.array([s["effet"] for s in sig])
    # seuil relatif : la moitié du pic, et au moins 3 % de l'image
    seuil = max(0.03, 0.5 * float(e.max()))
    res = {"source": os.path.basename(src), "duree_s": round(len(ims) / FPS, 2), "fps_analyse": FPS,
           "seuil_effet": round(seuil, 3), "effet_max": round(float(e.max()), 3),
           "episodes_effet": episodes(e, FPS, seuil),
           "episodes_effet_faible": episodes(e, FPS, max(0.015, 0.2 * float(e.max()))),
           "tenues": tenues([s["saut"] for s in sig], FPS)}
    bande(ims, sig, FPS, pas, (debut or 0)).save(sortie)
    print(json.dumps(res, indent=1, ensure_ascii=False))
    return res


if __name__ == "__main__":
    a = sys.argv[1:]
    main(a[0], a[1], float(a[2]) if len(a) > 2 else 0.1, float(a[3]) if len(a) > 3 else None,
         float(a[4]) if len(a) > 4 else None)
