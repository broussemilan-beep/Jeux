"""
ÉCOUTE : ce que fait le SON d'une référence, mesuré (il n'y a pas d'oreille
dans ce bac à sable, seulement des mesures).

Pour chaque vidéo :
- on décode la piste audio (ffmpeg, mono, 44,1 kHz) ;
- on repère les ATTAQUES (flux spectral, pics séparés d'au moins 0,12 s) ;
- pour les K attaques les plus fortes, on mesure :
  - le temps de montée (10 % -> 90 % du pic d'enveloppe) ;
  - la durée jusqu'à -20 dB sous le pic (la « queue ») ;
  - la part d'énergie par bande au pic et sur les 300 ms qui suivent :
    sub (<100 Hz), grave (100-400), médium (400-2k), aigu (2-6k), air (>6k) ;
  - le centroïde spectral à l'attaque puis 100 ms après : s'il chute, le son
    « tombe » (craquement aigu, puis corps grave) ;
  - le SILENCE d'avant : le niveau des 100 ms qui précèdent, relatif au pic ;
- on cherche le pic VISUEL le plus proche (score de planche_vfx.py : pixels
  clairs, saturés, saut d'image) et on donne l'écart son -> image, en ms.
- le fond (médiane du niveau) : s'il est haut, il y a probablement une
  musique par-dessus, et les attaques mesurées peuvent en venir.

C'est une aide à l'étude, pas un verdict : ça dit QUOI regarder et écouter.

Usage : python3 ecoute.py <video> [K=6] [--json sortie.json]
"""
import json
import os
import subprocess
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

SR = 44100
N, HOP = 2048, 256
BANDES = [("sub", 20, 100), ("grave", 100, 400), ("medium", 400, 2000), ("aigu", 2000, 6000), ("air", 6000, 16000)]


def audio(src):
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", src, "-vn", "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                       capture_output=True, check=True)
    return np.frombuffer(r.stdout, dtype=np.float32).astype(np.float64)


def stft(x):
    w = np.hanning(N)
    n = 1 + max(0, (len(x) - N) // HOP)
    fr = np.stack([x[i * HOP:i * HOP + N] * w for i in range(n)])
    return np.abs(np.fft.rfft(fr, axis=1)) ** 2, np.fft.rfftfreq(N, 1 / SR)


def db(v):
    return 10 * np.log10(np.maximum(v, 1e-12))


def attaques(S, f, k):
    L = np.log1p(S * 1e3)
    flux = np.maximum(0, np.diff(L, axis=0)).sum(axis=1)
    flux = np.concatenate([[0], flux])
    med = np.median(flux)
    mad = np.median(np.abs(flux - med)) + 1e-9
    seuil = med + 6 * mad
    ecart = int(0.12 * SR / HOP)
    pics = [i for i in range(1, len(flux) - 1) if flux[i] > seuil and flux[i] >= flux[i - 1] and flux[i] >= flux[i + 1]]
    pics.sort(key=lambda i: -flux[i])
    pris = []
    for i in pics:
        if all(abs(i - p) >= ecart for p in pris):
            pris.append(i)
        if len(pris) >= k:
            break
    return sorted(pris), flux


def mesurer(S, f, i):
    tot = S.sum(axis=1)
    env = db(tot)
    j = int(0.4 * SR / HOP)
    fen = env[i:i + j]
    ip = i + int(np.argmax(fen[: int(0.08 * SR / HOP) + 1]))
    pic = env[ip]
    # montée : 10 % -> 90 % en amplitude = -20 dB -> -0,9 dB
    a0 = ip
    while a0 > max(0, i - int(0.05 * SR / HOP)) and env[a0] > pic - 20:
        a0 -= 1
    montee = (ip - a0) * HOP / SR
    q = ip
    fin = min(len(env) - 1, ip + int(3.0 * SR / HOP))
    while q < fin and env[q] > pic - 20:
        q += 1
    queue = (q - ip) * HOP / SR
    avant = env[max(0, i - int(0.1 * SR / HOP)):max(1, i - 1)]
    silence = float(np.median(avant) - pic) if len(avant) else 0.0

    def parts(sl):
        e = S[sl].sum(axis=0)
        t = e.sum() + 1e-12
        return {nom: round(float(e[(f >= lo) & (f < hi)].sum() / t), 3) for nom, lo, hi in BANDES}

    def centroide(k):
        e = S[k]
        return float((e * f).sum() / (e.sum() + 1e-12))

    return {
        "t": round(i * HOP / SR, 3),
        "niveau_pic_db": round(float(pic), 1),
        "montee_ms": round(montee * 1000),
        "queue_ms_a_-20dB": round(queue * 1000),
        "silence_avant_db": round(silence, 1),
        "bandes_au_pic": parts(slice(ip, ip + 2)),
        "bandes_300ms": parts(slice(ip, ip + int(0.3 * SR / HOP))),
        "centroide_hz_attaque": round(centroide(ip)),
        "centroide_hz_+100ms": round(centroide(min(len(S) - 1, ip + int(0.1 * SR / HOP)))),
    }


def pics_visuels(src):
    from planche_ref import cadence_native, extraire
    from planche_vfx import moments, scores
    fps = min(30.0, cadence_native(src))
    ims = extraire(src, fps=fps, largeur=160)
    sc, _ = scores(ims)
    return [m / fps for m in moments(sc, fps, k=12, ecart_s=0.25)], fps


def main(src, k=6, sortie=None):
    x = audio(src)
    S, f = stft(x)
    ids, _flux = attaques(S, f, k)
    fond = float(np.median(db(S.sum(axis=1))))
    res = {"fichier": os.path.basename(src)[:8], "duree_s": round(len(x) / SR, 2), "fond_db": round(fond, 1),
           "attaques": [mesurer(S, f, i) for i in ids]}
    try:
        vis, fps = pics_visuels(src)
        for a in res["attaques"]:
            d = min(vis, key=lambda v: abs(v - a["t"])) if vis else None
            a["pic_visuel_proche_s"] = None if d is None else round(d, 3)
            a["ecart_son_image_ms"] = None if d is None else round((a["t"] - d) * 1000)
        res["fps_video"] = fps
    except Exception as e:  # la vidéo peut manquer de piste image exploitable
        res["visuel"] = f"non mesuré : {e}"
    print(json.dumps(res, ensure_ascii=False, indent=1))
    if sortie:
        json.dump(res, open(sortie, "w"), ensure_ascii=False, indent=1)
    return res


if __name__ == "__main__":
    a = [x for x in sys.argv[1:] if not x.startswith("--")]
    out = sys.argv[sys.argv.index("--json") + 1] if "--json" in sys.argv else None
    if out in a:
        a.remove(out)
    main(a[0], int(a[1]) if len(a) > 1 else 6, out)
