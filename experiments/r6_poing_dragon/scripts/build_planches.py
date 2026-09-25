"""
PLANCHES plein écran de la v13 (fiche POING_DU_DRAGON_V13.md §5), peintes
à bord NET (aplats, cœur blanc, pas de dégradé mou), déterministes :

- gueule_encre / gueule_inverse : la carte manga de la morsure (Last Breath
  v1, 17,0 s : la gueule du dragon dessinée à l'ENCRE), tirée de NOTRE
  modèle (rendu du labo, recette dragon_gueule_demo) : trait = contours du
  rendu, aplats noirs dans l'ombre, trame de points dans les demi-teintes,
  lignes de vitesse et éclaboussures autour ; puis la même inversée et
  fissurée ;
- spirale_0..2 : le tourbillon de feu plein écran (GIF Goku d514ee70,
  1,0-2,1 s) : cœur blanc, bandes or, orange, rouge sombre, en spirale ;
  trois « dessins » différents joués en 2 (12 i/s), tournés par le lecteur ;
- rouge_0..1 : rouge radial et horizon à rayons (Last Breath v1, 18,3 s) ;
- soleil : soleil orange avec la silhouette noire du dragon qui plonge
  (Last Breath v1, 20,3 s).

Usage : python3 build_planches.py [rendu_gueule.png]  ->  ../output/planches/*.png
(sans rendu : la gueule n'est pas produite, le reste oui)
"""
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "output", "planches")
W, H = 1280, 720
BLANC, OR, ORANGE, ROUGE, SOMBRE = (255, 252, 240), (255, 214, 72), (255, 132, 26), (196, 42, 14), (92, 12, 6)


def bruit(n, echelle, graine):
    rng = np.random.default_rng(graine)
    g = rng.random((echelle + 3, echelle + 3))
    im = Image.fromarray((g * 255).astype(np.uint8)).resize((n, n), Image.BICUBIC)
    return np.asarray(im, np.float32) / 255


def tons(v, pal):
    """v in [0,1] -> aplats (seuils durs)."""
    out = np.zeros(v.shape + (3,), np.uint8)
    for seuil, col in pal:
        out[v >= seuil] = col
    return out


def spirale(k):
    """Tourbillon de feu : bandes en spirale logarithmique, cœur blanc."""
    n = 1500
    y, x = np.mgrid[0:n, 0:n].astype(np.float32)
    x, y = (x - n / 2) / (n / 2), (y - n / 2) / (n / 2)
    r = np.hypot(x, y) + 1e-4
    a = np.arctan2(y, x)
    b = bruit(n, 7, 11 + k)
    b2 = bruit(n, 23, 31 + k)
    phase = a * 3 + 2.6 * np.log(r) + 0.9 * k + 1.6 * (b - 0.5) + 0.5 * (b2 - 0.5)
    bande = 0.5 + 0.5 * np.sin(phase)
    chaleur = np.clip(1.15 - r * 0.85, 0, 1)                     # plus chaud au centre
    v = 0.62 * bande + 0.55 * chaleur - 0.1
    img = tons(v, [(-9, SOMBRE), (0.28, ROUGE), (0.45, ORANGE), (0.62, OR), (0.83, BLANC)])
    img[r < 0.16 + 0.03 * np.sin(a * 5 + k)] = BLANC
    im = Image.fromarray(img)
    # traits d'encre qui s'enroulent (le dessin, pas un bruit)
    d = ImageDraw.Draw(im)
    rng = np.random.default_rng(50 + k)
    for i in range(22):
        a0 = rng.uniform(0, 2 * math.pi)
        r0 = rng.uniform(0.25, 0.8)
        pts = []
        for t in np.linspace(0, 1, 18):
            rr = r0 * (1 + 0.55 * t)
            aa = a0 - 1.2 * t - 2.6 * math.log(rr) / 3
            pts.append((n / 2 + rr * n / 2 * math.cos(aa), n / 2 + rr * n / 2 * math.sin(aa)))
        d.line(pts, fill=SOMBRE, width=int(rng.uniform(4, 11)))
    return im


def rouge(k):
    """Horizon rouge à rayons : ciel rouge-orange en bandes, sol noir."""
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    hy = H * (0.62 + 0.01 * k)
    cx = W * (0.5 + 0.03 * k)
    a = np.arctan2(y - hy, x - cx)
    b = bruit(max(W, H), 9, 70 + k)[:H, :W]
    rayons = 0.5 + 0.5 * np.sin(a * 26 + 3 * (b - 0.5) + 1.3 * k)
    dist = np.clip((hy - y) / hy, 0, 1)
    v = 0.75 - 0.6 * dist + 0.3 * rayons * (1 - dist * 0.5)
    img = tons(v, [(-9, SOMBRE), (0.3, ROUGE), (0.55, ORANGE), (0.8, OR), (0.97, BLANC)])
    sol = y > hy + 6 * np.sin(x / W * 17 + k) + 10 * (b - 0.5)
    img[sol] = (18, 4, 2)
    im = Image.fromarray(img)
    d = ImageDraw.Draw(im)
    rng = np.random.default_rng(90 + k)
    for i in range(40):                                        # traînées sombres au sol, vers le point de fuite
        xx = rng.uniform(-0.2, 1.2) * W
        d.line([(xx, H), (cx + (xx - cx) * 0.12, hy + 4)], fill=(70, 10, 4), width=int(rng.uniform(2, 7)))
    return im


def silhouette_dragon(d, pts, epaisseur, couleur=(8, 4, 2)):
    """Corps en ruban effilé + épines + tête gueule ouverte (encre)."""
    pts = np.asarray(pts, float)
    n = len(pts)
    gauche, droite = [], []
    for i in range(n):
        t = pts[min(n - 1, i + 1)] - pts[max(0, i - 1)]
        t /= (np.linalg.norm(t) + 1e-9)
        nn = np.array([-t[1], t[0]])
        w = epaisseur * (1 - 0.85 * (i / (n - 1)) ** 1.3)
        gauche.append(tuple(pts[i] + nn * w))
        droite.append(tuple(pts[i] - nn * w))
        if i % 3 == 1 and i < n - 3:                           # épines dorsales
            d.polygon([tuple(pts[i] + nn * w * 0.9), tuple(pts[i] + nn * w * 2.1 - t * w * 0.8),
                       tuple(pts[i] + nn * w * 0.9 - t * w * 1.2)], fill=couleur)
    d.polygon(gauche + droite[::-1], fill=couleur)
    # tête : museau + mâchoire ouverte + cornes, dans le sens du 1er segment
    t = pts[0] - pts[1]
    t /= np.linalg.norm(t)
    nn = np.array([-t[1], t[0]])
    h = pts[0]
    e = epaisseur
    haut = [h + nn * e * 0.9, h + t * e * 3.6 + nn * e * 0.5, h + t * e * 3.9 + nn * e * 0.1, h + t * e * 1.2 - nn * e * 0.1]
    bas = [h - nn * e * 0.6, h + t * e * 3.0 - nn * e * 1.9, h + t * e * 2.7 - nn * e * 2.2, h + t * e * 0.6 - nn * e * 0.5]
    d.polygon([tuple(p) for p in haut], fill=couleur)
    d.polygon([tuple(p) for p in bas], fill=couleur)
    for s_ in (1, -1):
        d.line([tuple(h + nn * e * 0.8), tuple(h - t * e * 2.2 + nn * e * (1.8 + 0.4 * s_))], fill=couleur, width=int(e * 0.35))


def soleil():
    im = Image.new("RGB", (W, H), ORANGE)
    d = ImageDraw.Draw(im)
    cx, cy, R = W * 0.52, H * 0.46, H * 0.36
    # lignes radiales noires (Last Breath : soleil rayé de noir)
    for i in range(64):
        a = 2 * math.pi * i / 64 + 0.02 * (i % 3)
        w = 0.012 if i % 2 else 0.02
        d.polygon([(cx + math.cos(a - w) * R * 1.15, cy + math.sin(a - w) * R * 1.15),
                   (cx + math.cos(a) * W, cy + math.sin(a) * W),
                   (cx + math.cos(a + w) * R * 1.15, cy + math.sin(a + w) * R * 1.15)], fill=(160, 40, 8))
    d.ellipse([cx - R * 1.08, cy - R * 1.08, cx + R * 1.08, cy + R * 1.08], fill=OR)
    d.ellipse([cx - R, cy - R, cx + R, cy + R], fill=(255, 236, 150))
    d.ellipse([cx - R * 0.8, cy - R * 0.8, cx + R * 0.8, cy + R * 0.8], fill=BLANC)
    # la silhouette du dragon qui plonge à travers le soleil (tête en bas à gauche)
    pts = []
    for t in np.linspace(0, 1, 40):
        x = cx - R * 0.95 + t * R * 2.6
        y = cy + R * 0.95 - t * R * 1.9 + math.sin(t * 7.5) * R * 0.22
        pts.append((x, y))
    silhouette_dragon(d, pts, epaisseur=R * 0.11)
    # sol noir
    d.rectangle([0, H * 0.86, W, H], fill=(10, 3, 1))
    return im


def encre(rendu):
    """Rendu couleur du modèle -> carte manga à l'encre (aplats noirs,
    trame de points, contours), cadrée sur la gueule."""
    src = Image.open(rendu).convert("RGB")
    a = np.asarray(src, np.float32) / 255
    lum = 0.3 * a[..., 0] + 0.59 * a[..., 1] + 0.11 * a[..., 2]
    sat = a.max(-1) - a.min(-1)
    # fond du labo : ciel bleu, sol gris-bleu (1er essai : le sol devenait une
    # trame qui mangeait la moitié de la carte)
    ciel = ((a[..., 2] > a[..., 0] + 0.04) & (lum > 0.3) & (lum < 0.78)) | ((sat < 0.12) & (lum > 0.28) & (lum < 0.66))
    rouge_ = (a[..., 0] > 0.45) & (a[..., 1] < 0.3)                   # intérieur de la gueule
    gris = Image.fromarray((lum * 255).astype(np.uint8))
    bords = np.asarray(gris.filter(ImageFilter.FIND_EDGES), np.float32) / 255
    h, w = lum.shape
    y, x = np.mgrid[0:h, 0:w]
    trame = ((x % 6 < 3) ^ (y % 6 < 3)) & ((x + y) % 3 == 0)
    out = np.full((h, w), 255, np.uint8)
    corps = ~ciel
    out[corps & (lum < 0.62) & trame] = 0                             # demi-teinte : trame
    out[corps & ((lum < 0.36) | rouge_)] = 0                          # ombres et gueule : aplat noir
    out[corps & (bords > 0.16)] = 0                                   # trait
    im = Image.fromarray(out).filter(ImageFilter.MinFilter(3))
    # cadrage 16:9 sur la tête (boîte des pixels du modèle), la gueule
    # légèrement à gauche du centre, marge de papier
    ys, xs = np.nonzero(corps)
    bx0, bx1, by0, by1 = np.percentile(xs, 1), np.percentile(xs, 99), np.percentile(ys, 1), np.percentile(ys, 99)
    bw, bh = (bx1 - bx0) * 1.15, (by1 - by0) * 1.15
    if bw / bh < 16 / 9:
        bw = bh * 16 / 9
    else:
        bh = bw * 9 / 16
    cxb, cyb = (bx0 + bx1) / 2 + bw * 0.06, (by0 + by1) / 2
    fond = Image.new("L", (int(bw) + 2, int(bh) + 2), 255)
    im = im.crop((4, 4, im.size[0] - 4, im.size[1] - 4))          # bord noir du filtre
    fond.paste(im, (int(bw / 2 - cxb) + 4, int(bh / 2 - cyb) + 4))
    im = fond.resize((W, H), Image.LANCZOS)
    im = im.point(lambda v: 255 if v > 128 else 0).convert("RGB")
    d = ImageDraw.Draw(im)
    rng = np.random.default_rng(7)
    cx, cy = W * 0.42, H * 0.45
    for i in range(90):                                              # lignes de vitesse vers la gueule
        aa = rng.uniform(0, 2 * math.pi)
        r0, r1 = rng.uniform(0.3, 0.42) * W, W * 1.1
        ww = rng.uniform(0.002, 0.008)
        d.polygon([(cx + math.cos(aa) * r0, cy + math.sin(aa) * r0), (cx + math.cos(aa - ww) * r1, cy + math.sin(aa - ww) * r1),
                   (cx + math.cos(aa + ww) * r1, cy + math.sin(aa + ww) * r1)], fill=(0, 0, 0))
    for i in range(26):                                              # éclaboussures d'encre
        px, py = rng.uniform(0, W), rng.uniform(0, H)
        if abs(px - cx) < W * 0.3 and abs(py - cy) < H * 0.3:
            continue
        rr = rng.uniform(4, 22)
        d.ellipse([px - rr, py - rr, px + rr, py + rr], fill=(0, 0, 0))
    # teinte papier chaud (pas un blanc numérique)
    arr = np.asarray(im).copy()
    arr[(arr == 255).all(-1)] = (250, 240, 214)
    arr[(arr == 0).all(-1)] = (22, 10, 6)
    return Image.fromarray(arr)


def inverse(im):
    arr = 255 - np.asarray(im)
    im2 = Image.fromarray(arr.astype(np.uint8))
    d = ImageDraw.Draw(im2)
    rng = np.random.default_rng(3)
    for i in range(9):                                               # fissures
        x, y = W * 0.42, H * 0.45
        pts = [(x, y)]
        a = rng.uniform(0, 2 * math.pi)
        for k in range(10):
            a += rng.uniform(-0.6, 0.6)
            x += math.cos(a) * rng.uniform(40, 110)
            y += math.sin(a) * rng.uniform(40, 110)
            pts.append((x, y))
        d.line(pts, fill=(255, 250, 235), width=int(rng.uniform(3, 8)))
    return im2


def main(rendu=None):
    os.makedirs(OUT, exist_ok=True)
    for k in range(3):
        spirale(k).save(os.path.join(OUT, f"spirale_{k}.png"))
    for k in range(2):
        rouge(k).save(os.path.join(OUT, f"rouge_{k}.png"))
    soleil().save(os.path.join(OUT, "soleil.png"))
    if rendu and os.path.exists(rendu):
        g = encre(rendu)
        g.save(os.path.join(OUT, "gueule_encre.png"))
        inverse(g).save(os.path.join(OUT, "gueule_inverse.png"))
    print(sorted(os.listdir(OUT)))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)
