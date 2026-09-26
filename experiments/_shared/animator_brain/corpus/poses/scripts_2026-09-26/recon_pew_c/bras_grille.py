"""Recherche exhaustive de la direction d'un bras (az, el dans les axes du torse),
torse + caméra fixés. Coût = bout du bras + boîte de la face du bout (+ IoU des
parties blanches dans une zone). Sort une carte de coût (ambiguïtés visibles)."""
import sys, json
sys.path.insert(0, ".")
import numpy as np
import cv2
import fit as F
import geo_pose as G
import rendu as R
from essai2 import cam_grille

def carte(base_json, bras, tip, bb, zone=None, masque=None, pas=5, w_iou=0.0, extra_marks=None):
    d = json.load(open(base_json))
    pose0 = {k: (tuple(v) if isinstance(v, list) else v) for k, v in d["pose"].items()}
    azs = np.arange(-180, 181, pas); els = np.arange(-90, 91, pas)
    C = np.full((len(els), len(azs)), np.nan)
    part = {"RA": "Right Arm", "LA": "Left Arm"}[bras]
    for i, el in enumerate(els):
        for j, az in enumerate(azs):
            p = dict(pose0); p[bras] = (float(az), float(el))
            w = G.pose(p)
            c = cam_grille(w["Torso"][1], **d["cam"])
            e = 0.0
            pr = F.project(c, F.point(w, bras + "_tip"))
            e += np.sum((pr - tip) ** 2)
            R_, p_ = w[part]
            cs = [p_ + R_ @ np.array([a, -1.0, b]) for a in (-0.5, 0.5) for b in (-0.5, 0.5)]
            # face du bout visible ?
            n = R_ @ np.array([0, -1.0, 0]); vis = n @ (p_ + R_ @ np.array([0, -1.0, 0]) - c["eye"]) < 0
            q = np.array([F.project(c, x) for x in cs])
            got = np.array([q[:, 0].min(), q[:, 1].min(), q[:, 0].max(), q[:, 1].max()])
            e += 4 * np.sum((got - bb) ** 2) / 4
            if not vis:
                e += 3000   # la face noire du bout doit être visible
            for nm, (uv, wt) in (extra_marks or {}).items():
                e += wt * np.sum((F.project(c, F.point(w, nm)) - np.array(uv)) ** 2)
            if w_iou and masque is not None:
                im = np.asarray(R.render([w], c, (480, 270), flat=True))[:, :, 0] > 200
                a = im & zone; b = masque & zone
                e += w_iou * (1 - (a & b).sum() / max(1, (a | b).sum()))
            C[i, j] = e
    return azs, els, C

def dessin(azs, els, C, sortie, titre):
    L = np.log10(C); L = (L - np.nanmin(L)) / (np.nanmax(L) - np.nanmin(L) + 1e-9)
    img = (255 * (1 - L)).astype(np.uint8)[::-1]
    img = cv2.applyColorMap(cv2.resize(img, (len(azs) * 8, len(els) * 8), interpolation=cv2.INTER_NEAREST), cv2.COLORMAP_VIRIDIS)
    i, j = np.unravel_index(np.nanargmin(C), C.shape)
    cx, cy = j * 8 + 4, (len(els) - 1 - i) * 8 + 4
    cv2.drawMarker(img, (cx, cy), (0, 0, 255), cv2.MARKER_STAR, 20, 2)
    out = cv2.copyMakeBorder(img, 30, 30, 50, 10, cv2.BORDER_CONSTANT, value=(255, 255, 255))
    for az in range(-180, 181, 45):
        x = 50 + int((az - azs[0]) / (azs[1] - azs[0]) * 8) + 4
        cv2.putText(out, str(az), (x - 12, out.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1)
    for el in range(-90, 91, 30):
        y = 30 + (len(els) - 1 - int((el - els[0]) / (els[1] - els[0]))) * 8 + 4
        cv2.putText(out, str(el), (5, y + 4), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1)
    cv2.putText(out, titre + "  (x: az torse, 0=devant +90=sa droite ; y: el ; clair = bon)", (50, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1)
    cv2.imwrite(sortie, out)
    return azs[j], els[i]
