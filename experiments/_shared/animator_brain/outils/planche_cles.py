"""
PLANCHE DE CLÉS : voir une animation comme son animateur l'a posée.

Né du chantier 4 (2026-09-26, Milan : « comment les animations sont faites,
où il place les rig etc., c'est vraiment apprendre au sens large »). Les
études d'avant mesuraient les animations pros en STATISTIQUES (clés/s,
interpolation) ; personne n'avait REGARDÉ chaque clé posée : où est le
torse, où sont les bras, ce qui bouge d'une clé à la suivante, ce qui
attend.

Pour une KeyframeSequence (.rbxm binaire des pros, ou notre .rbxmx) :
- une planche PNG : chaque CLÉ (instant où l'animateur a posé au moins une
  part) rendue sous 2 angles fixes (3/4 face, profil), avec son temps, son
  écart en images à 60 i/s depuis la clé d'avant, et les parts posées à
  cette clé (les autres attendent ou interpolent) ;
- une bande « rythme » : les clés sur l'axe du temps, part par part (qui est
  posé quand : décalages, chevauchement, tenues) ;
- une vue « arcs » : trajets des poings, des pieds et du torse sur toute
  l'anim, de profil et de dessus (espacement = densité des points à 60 i/s) ;
- un tableau texte (stdout, ou --json) : par clé, parts posées et
  descripteurs geo_pose (buste, bras, poings, pieds, hanche).

Aide pour regarder : aucun seuil, aucun verdict.

Usage :
  python3 outils/planche_cles.py --rbxm <fichier.rbxm> --liste
  python3 outils/planche_cles.py --rbxm <fichier.rbxm> --nom M1 --sortie m1.png [--json m1.json]
  python3 outils/planche_cles.py --rbxmx <export.rbxmx> --sortie nous.png
  options : --avant x,z (direction du coup ; défaut 0,-1 = -Z) ;
            --max 24 (nombre max de clés dessinées ; les autres sont listées)
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", ".."))
import geo_pose as G  # noqa: E402

PARTS = ["Torso", "Head", "Right Arm", "Left Arm", "Right Leg", "Left Leg"]
COURT = {"Torso": "T", "Head": "H", "Right Arm": "BD", "Left Arm": "BG", "Right Leg": "JD", "Left Leg": "JG"}
FPS = 60


def cles_rbxm(path, nom):
    from animator_brain import corpus as C
    for s in C.load_rbxm_sequences(path):
        if s["name"] == nom:
            return s
    raise KeyError(nom)


def cles_rbxmx(path):
    """Notre export : chaque Keyframe et ses Poses (lecture XML minimale)."""
    import xml.etree.ElementTree as ET
    from animator_brain import roblox_export as X  # noqa: F401
    root = ET.parse(path).getroot()
    frames = []
    for kf in root.iter("Item"):
        if kf.get("class") != "Keyframe":
            continue
        t = None
        for p in kf.find("Properties"):
            if p.get("name") == "Time":
                t = float(p.text)
        poses = {}
        for it in kf.iter("Item"):
            if it.get("class") != "Pose":
                continue
            pr = it.find("Properties")
            nm, cf, wgt = None, None, 1.0
            for p in pr:
                if p.get("name") == "Name":
                    nm = p.text
                elif p.get("name") == "Weight":
                    wgt = float(p.text)
                elif p.tag == "CoordinateFrame" and p.get("name") == "CFrame":
                    v = {c.tag: float(c.text) for c in p}
                    R = np.array([[v["R00"], v["R01"], v["R02"]], [v["R10"], v["R11"], v["R12"]],
                                  [v["R20"], v["R21"], v["R22"]]])
                    cf = (R, np.array([v["X"], v["Y"], v["Z"]]))
            if nm in PARTS and cf is not None and wgt != 0.0:
                poses[nm] = cf
        frames.append((t, poses))
    frames.sort(key=lambda f: f[0])
    return {"name": os.path.basename(path), "frames": frames}


def _monde_a(mondes, t):
    i = min(int(round(t * FPS)), len(mondes) - 1)
    return mondes[i][1]


def analyser(seq, avant=(0.0, 0.0, -1.0)):
    from animator_brain import corpus as C
    mondes = C.resample_linear(seq["frames"], FPS)
    cles = []
    t_prec = None
    for t, poses in seq["frames"]:
        parts = [p for p in PARTS if p in poses]
        if not parts:
            continue
        w = _monde_a(mondes, t)
        d = G.descripteurs(w, avant)
        cles.append({"t": round(t, 4), "image60": int(round(t * FPS)),
                     "ecart_images": None if t_prec is None else int(round((t - t_prec) * FPS)),
                     "parts_posees": [COURT[p] for p in parts], "pose": d})
        t_prec = t
    return mondes, cles


def _cam(mondes, az, el, avant, dist_min=7.0):
    pts = np.array([w["Torso"][1] for _t, w in mondes])
    c = (pts.min(0) + pts.max(0)) / 2
    c[1] = 2.4
    ext = float(np.max(pts.max(0) - pts.min(0)))
    return G.camera_orbite(c, az, el, max(dist_min, 9.0 + 1.3 * ext), 40.0, avant)


def planche(seq, sortie, avant=(0.0, 0.0, -1.0), maxi=24):
    mondes, cles = analyser(seq, avant)
    montre = cles if len(cles) <= maxi else [cles[int(round(i * (len(cles) - 1) / (maxi - 1)))] for i in range(maxi)]
    cams = [("3/4 face", _cam(mondes, 35, 12, avant)), ("profil", _cam(mondes, 90, 5, avant))]
    tw, th = 200, 200
    col = 8
    lignes = (len(montre) + col - 1) // col
    W = col * tw
    H_cles = lignes * (2 * th + 30)
    H_ryt, H_arc = 150, 330
    im = Image.new("RGB", (W, 40 + H_cles + H_ryt + H_arc), (24, 24, 30))
    d = ImageDraw.Draw(im)
    try:
        from PIL import ImageFont
        fnt = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 11)
        _txt = d.text
        d.text = lambda xy, t, **kw: _txt(xy, t, font=fnt, **kw)
    except OSError:
        pass
    duree = seq["frames"][-1][0] if seq["frames"] else 0
    d.text((8, 8), f"{seq['name']} : {len(cles)} clés en {duree:.2f} s ({len(mondes)} images à 60 i/s)"
           + ("" if len(montre) == len(cles) else f" ; {len(montre)} clés dessinées sur {len(cles)}"),
           fill=(255, 230, 120))
    jamais = [COURT[p] for p in PARTS if not any(p in po for _t, po in seq["frames"])]
    if jamais:
        d.text((700, 8), f"jamais posées ici : {' '.join(jamais)} (laissées à l'anim du dessous ; rendues au repos, "
               "attachées au torse comme dans Roblox)", fill=(255, 150, 150))
    d.text((8, 22), "chaque case : image60 (+écart depuis la clé précédente) / parts posées à cette clé ; "
           "haut = 3/4 face, bas = profil (caméras fixes) ; bras DROIT vert, bras GAUCHE bleu, torse rouge ; flèche rose au sol = « avant » (--avant)", fill=(170, 170, 180))
    y0 = 40
    for k, c in enumerate(montre):
        x, y = (k % col) * tw, y0 + (k // col) * (2 * th + 30)
        w = _monde_a(mondes, c["t"])
        for j, (_n, cam) in enumerate(cams):
            import moon as MO
            tp = w["Torso"][1]
            fa = np.array(avant, float) / np.linalg.norm(avant)

            def fleche(dr, proj, tp=tp, fa=fa):
                a, _ = proj((tp[0], 0.02, tp[2]))
                b, _ = proj((tp[0] + 1.6 * fa[0], 0.02, tp[2] + 1.6 * fa[2]))
                dr.line([a, b], fill=(255, 60, 200), width=3)
                dr.ellipse([b[0] - 4, b[1] - 4, b[0] + 4, b[1] + 4], fill=(255, 60, 200))
            r = MO.render([w], cam[0], cam[1], cam[2], (tw - 4, th - 4), sky=(200, 205, 215), extra=fleche)
            im.paste(r, (x + 2, y + 2 + j * th))
        e = "" if c["ecart_images"] is None else f" (+{c['ecart_images']})"
        d.text((x + 4, y + 2 * th + 2), f"i{c['image60']}{e}", fill=(255, 255, 255))
        d.text((x + 4, y + 2 * th + 15), " ".join(c["parts_posees"]), fill=(150, 220, 150))
    # rythme : qui est posé quand
    yr = y0 + H_cles + 10
    d.text((8, yr), "RYTHME : une barre = une clé de cette part (60 i/s)", fill=(255, 230, 120))
    x0, x1 = 60, W - 20
    n = max(1, len(mondes) - 1)
    for i, p in enumerate(PARTS):
        yy = yr + 22 + i * 19
        d.text((8, yy), COURT[p], fill=(200, 200, 200))
        d.line([(x0, yy + 7), (x1, yy + 7)], fill=(60, 60, 70))
        for t, poses in seq["frames"]:
            if p in poses:
                xx = x0 + (x1 - x0) * (t * FPS) / n
                d.line([(xx, yy), (xx, yy + 14)], fill=(120, 200, 255), width=2)
    for s in range(0, int(duree) + 1):
        xx = x0 + (x1 - x0) * (s * FPS) / n
        d.text((xx, yr + 22 + 6 * 19), f"{s}s", fill=(150, 150, 150))
    # arcs : trajets (profil et dessus)
    ya = yr + H_ryt + 10
    f, r = G.repere(avant)
    traces = {"poing D": ("Right Arm", (80, 200, 110)), "poing G": ("Left Arm", (70, 140, 255)),
              "pied D": ("Right Leg", (255, 170, 60)), "pied G": ("Left Leg", (120, 220, 120)),
              "torse": ("Torso", (240, 240, 240))}
    pts = {k: np.array([(G.bout(w, p) if p != "Torso" else w["Torso"][1]) for _t, w in mondes])
           for k, (p, _c) in traces.items()}
    allp = np.concatenate(list(pts.values()))
    for j, (titre, ax1, ax2) in enumerate((("ARCS de profil (avant ->, haut ^)", f, np.array([0, 1.0, 0])),
                                           ("ARCS de dessus (avant ->, droite v)", f, r))):
        bx = j * (W // 2)
        d.text((bx + 8, ya), titre + " ; un point = une image : serrés = lent, espacés = rapide", fill=(255, 230, 120))
        a1, a2 = allp @ ax1, allp @ ax2
        sc = min((W // 2 - 40) / max(1e-3, a1.max() - a1.min()), (H_arc - 50) / max(1e-3, a2.max() - a2.min()))
        for k, (_p, colr) in traces.items():
            q = pts[k]
            for v in q:
                px = bx + 20 + (v @ ax1 - a1.min()) * sc
                py = ya + 30 + (a2.max() - v @ ax2) * sc if j == 0 else ya + 30 + (v @ ax2 - a2.min()) * sc
                d.ellipse([px - 1.5, py - 1.5, px + 1.5, py + 1.5], fill=colr)
        for i2, (k, (_p, colr)) in enumerate(traces.items()):
            d.text((bx + 20 + i2 * 90, ya + H_arc - 18), k, fill=colr)
    if sortie:
        im.save(sortie)
    return im, cles


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rbxm")
    ap.add_argument("--rbxmx")
    ap.add_argument("--nom")
    ap.add_argument("--liste", action="store_true")
    ap.add_argument("--sortie")
    ap.add_argument("--json")
    ap.add_argument("--avant", default="0,-1")
    ap.add_argument("--max", type=int, default=24)
    a = ap.parse_args()
    ax, az = (float(v) for v in a.avant.split(","))
    avant = (ax, 0.0, az)
    if a.rbxm and a.liste:
        from animator_brain import corpus as C
        for s in C.load_rbxm_sequences(a.rbxm):
            print(f"{s['name']:28s} {len(s['frames']):4d} clés  {s['frames'][-1][0] if s['frames'] else 0:6.2f} s  "
                  f"loop={s['loop']} priorité={s['priority']}")
        return
    seq = cles_rbxm(a.rbxm, a.nom) if a.rbxm else cles_rbxmx(a.rbxmx)
    _im, cles = planche(seq, a.sortie, avant, a.max)
    if a.json:
        json.dump({"nom": seq["name"], "cles": cles}, open(a.json, "w"), ensure_ascii=False, indent=1)
    for c in cles:
        p = c["pose"]
        print(f"i{c['image60']:4d} (+{c['ecart_images'] if c['ecart_images'] is not None else '-':>3}) "
              f"{' '.join(c['parts_posees']):18s} {G.resume(p)}")


if __name__ == "__main__":
    main()
