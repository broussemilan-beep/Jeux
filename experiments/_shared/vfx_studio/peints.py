"""
TEXTURES PEINTES du studio : ce que le bruit et les formes simples ne savent
pas faire. Ici, le DRAGON du Poing du Dragon (fiches/AURA_DRAGON.md) :
- dragon_tete : tête de profil, museau vers la droite (+U), gueule ouverte,
  crocs, moustaches, cornes, crinière de flammes ; cel à 3 tons + contour
  brun (refs e92ac0d7, 6a961186, 7a2b4ae8) ; le cou sort par le bord gauche,
  au milieu, pour se raccorder au corps ;
- dragon_ecailles : le corps, pour un Beam (U le long du corps, raccord en
  U ; V en travers) : nageoires dorsales brunes en dents de scie (V = 0),
  écailles en écusson dorées, plaques de ventre claires (V = 1) ;
- eclair : éclair (U le long) : cœur blanc, halo qui prend la couleur du
  Beam (vert One For All pour Izuku).

Tout est dessiné en 2x puis réduit (anticrénelage), déterministe.
"""
import math

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

OR = (255, 197, 61)
OR_CLAIR = (255, 236, 160)
OR_OMBRE = (224, 132, 30)
BRUN = (74, 36, 14)
BRUN_CRIN = (140, 62, 22)
CREME = (255, 244, 205)
ROUGE = (200, 30, 20)


def chaikin(pts, it=3, ferme=True):
    """Lissage de Chaikin : un polygone grossier devient une courbe douce."""
    p = [tuple(map(float, x)) for x in pts]
    for _ in range(it):
        q = []
        n = len(p)
        rng = range(n) if ferme else range(n - 1)
        if not ferme:
            q.append(p[0])
        for i in rng:
            a, b = p[i], p[(i + 1) % n]
            q.append((0.75 * a[0] + 0.25 * b[0], 0.75 * a[1] + 0.25 * b[1]))
            q.append((0.25 * a[0] + 0.75 * b[0], 0.25 * a[1] + 0.75 * b[1]))
        if not ferme:
            q.append(p[-1])
        p = q
    return p


def _poly(d, pts, fond, contour=BRUN, trait=10, lisse=True):
    p = chaikin(pts) if lisse else [tuple(map(float, x)) for x in pts]
    d.polygon(p, fill=fond)
    if trait:
        d.line(p + [p[0]], fill=contour, width=trait, joint="curve")


def _courbe(d, pts, couleur, largeur, it=3):
    d.line(chaikin(pts, it, ferme=False), fill=couleur, width=largeur, joint="curve")


def dragon_tete(W=1024, H=512):
    """Tête de profil (museau à droite). Dessinée en 2x. 2e version : 1re
    trop « crocodile » (crinière invisible, cou en bulle, sans colère)."""
    S = 2
    im = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    P = lambda pts: [(x * W * S, y * H * S) for x, y in pts]  # noqa: E731
    # 1. CRINIÈRE de flammes : grandes langues brunes en éventail vers l'arrière
    cx, cy = 0.36, 0.42
    for k, (ang, ln, larg) in enumerate([(125, 0.40, 0.07), (150, 0.46, 0.08), (172, 0.44, 0.08), (195, 0.42, 0.08),
                                         (218, 0.36, 0.07), (240, 0.30, 0.06), (105, 0.30, 0.06)]):
        a = math.radians(ang)
        ux, uy = math.cos(a), -math.sin(a) * 2.0          # repère étiré (image 2:1)
        px, py = -uy / 2.0, ux * 2.0
        nrm = math.hypot(px, py)
        px, py = px / nrm * larg, py / nrm * larg * 2
        tip = (cx + ux * ln, cy + uy * ln)
        crochet = (cx + ux * ln * 0.72 + px * 0.9, cy + uy * ln * 0.72 + py * 0.9)
        pts = [(cx + px, cy + py), (cx + ux * ln * 0.5 + px * 0.9, cy + uy * ln * 0.5 + py * 0.9), crochet, tip,
               (cx + ux * ln * 0.6 - px * 0.5, cy + uy * ln * 0.6 - py * 0.5), (cx - px, cy - py)]
        _poly(d, P(pts), BRUN_CRIN if k % 2 else (176, 84, 30), trait=9)
    # 2. cou (fin, sort par le bord gauche au milieu) : la base du corps
    # (dépasse le bord gauche : coupé net par le cadre, il se raccorde au corps)
    _poly(d, P([(-0.2, 0.38), (0.20, 0.36), (0.36, 0.38), (0.36, 0.64), (0.20, 0.64), (-0.2, 0.62)]), OR, trait=10,
          lisse=False)
    # cornes : deux bois vers l'arrière-haut, bien visibles
    for dx, dy in ((0.0, 0.0), (0.06, 0.04)):
        _poly(d, P([(0.46 + dx, 0.26 + dy), (0.38 + dx, 0.10 + dy), (0.24 + dx, -0.02 + dy), (0.31 + dx, 0.08 + dy),
                    (0.18 + dx, 0.07 + dy), (0.33 + dx, 0.17 + dy), (0.40 + dx, 0.30 + dy)]), OR_OMBRE, trait=8)
    # 3. gueule grande ouverte : fond, langue, mâchoire inférieure épaisse
    _poly(d, P([(0.40, 0.54), (0.64, 0.55), (0.90, 0.64), (0.95, 0.76), (0.86, 0.84), (0.62, 0.80), (0.42, 0.74)]),
          (110, 14, 14), trait=0)
    _poly(d, P([(0.50, 0.68), (0.70, 0.67), (0.84, 0.72), (0.72, 0.75), (0.52, 0.75)]), (230, 70, 60), trait=5)
    _poly(d, P([(0.40, 0.70), (0.64, 0.76), (0.88, 0.80), (0.96, 0.84), (0.90, 0.94), (0.64, 0.93), (0.44, 0.88),
                (0.36, 0.80)]), OR, trait=10)
    _poly(d, P([(0.44, 0.86), (0.64, 0.89), (0.90, 0.90), (0.64, 0.93), (0.44, 0.88)]), OR_OMBRE, trait=0)
    # 4. crâne + museau (bosse du nez au bout)
    crane = [(0.30, 0.36), (0.38, 0.24), (0.50, 0.20), (0.62, 0.25), (0.76, 0.29), (0.88, 0.27), (0.97, 0.31),
             (1.0, 0.42), (0.97, 0.52), (0.84, 0.56), (0.62, 0.57), (0.44, 0.60), (0.32, 0.56)]
    _poly(d, P(crane), OR, trait=10)
    _poly(d, P([(0.40, 0.51), (0.62, 0.51), (0.84, 0.49), (0.97, 0.47), (0.97, 0.52), (0.84, 0.56), (0.62, 0.57),
                (0.44, 0.60)]), OR_OMBRE, trait=0)
    _poly(d, P([(0.44, 0.25), (0.54, 0.22), (0.66, 0.28), (0.78, 0.31), (0.66, 0.32), (0.54, 0.29)]), OR_CLAIR, trait=0)
    # rides du museau (traits cel)
    for x in (0.70, 0.75, 0.80):
        _courbe(d, P([(x, 0.31), (x + 0.02, 0.36), (x + 0.01, 0.40)]), OR_OMBRE, 7, it=2)
    # 5. crocs : deux GROS crocs devant + rangées
    for x, big in ((0.56, 0), (0.62, 0), (0.68, 0), (0.74, 0), (0.80, 0), (0.90, 1)):
        yb = 0.555
        ln, lg = (0.13, 0.026) if big else (0.07, 0.016)
        _poly(d, P([(x - lg, yb), (x + lg, yb), (x + 0.004, yb + ln)]), (255, 252, 240), BRUN, trait=5, lisse=False)
    for x, big in ((0.54, 0), (0.60, 0), (0.66, 0), (0.72, 0), (0.86, 1)):
        yb = 0.77 + 0.07 * (x - 0.5)
        ln, lg = (0.12, 0.024) if big else (0.06, 0.015)
        _poly(d, P([(x - lg, yb), (x + lg, yb), (x - 0.002, yb - ln)]), (255, 252, 240), BRUN, trait=5, lisse=False)
    # 6. ARCADE lourde qui descend vers l'avant (la colère) + œil fendu
    d.ellipse([0.52 * W * S, 0.31 * H * S, 0.61 * W * S, 0.43 * H * S], fill=(255, 250, 220), outline=BRUN, width=7)
    d.ellipse([0.555 * W * S, 0.33 * H * S, 0.59 * W * S, 0.42 * H * S], fill=ROUGE)
    d.line([(0.573 * W * S, 0.335 * H * S), (0.573 * W * S, 0.415 * H * S)], fill=(20, 0, 0), width=7)
    _poly(d, P([(0.44, 0.24), (0.56, 0.22), (0.66, 0.30), (0.64, 0.36), (0.56, 0.32), (0.46, 0.31)]), OR_OMBRE, trait=9,
          lisse=False)
    # narine
    d.ellipse([0.915 * W * S, 0.34 * H * S, 0.955 * W * S, 0.39 * H * S], fill=BRUN)
    # 7. moustaches : deux longues courbes du museau vers l'arrière
    _courbe(d, P([(0.94, 0.42), (0.84, 0.08), (0.60, 0.0), (0.34, 0.04), (0.06, 0.0)]), OR_CLAIR, 12)
    _courbe(d, P([(0.92, 0.46), (0.76, 0.98), (0.50, 1.0), (0.24, 0.94), (0.04, 0.99)]), OR_CLAIR, 12)
    # 8. nageoire de joue (piquants sous l'oreille)
    _poly(d, P([(0.34, 0.60), (0.22, 0.92), (0.35, 0.76), (0.40, 0.98), (0.45, 0.72)]), OR_OMBRE, trait=8, lisse=False)
    return im.resize((W, H), Image.LANCZOS)


def dragon_ecailles(W=512, H=256, periode=4):
    """Corps pour Beam : raccord en U (periode écailles par largeur)."""
    S = 2
    w, h = W * S, H * S
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    haut, bas = 0.30 * h, 0.96 * h
    # nageoires dorsales en dents de scie (brunes), au-dessus du dos
    n_dents = periode * 2
    for k in range(n_dents + 1):
        x0 = k * w / n_dents
        pts = [(x0 - 0.02 * w, haut + 6), (x0 + 0.07 * w, 0.02 * h), (x0 + 0.11 * w, haut + 6)]
        d.polygon(pts, fill=BRUN_CRIN, outline=BRUN)
        d.line(pts, fill=BRUN, width=8)
    # corps
    d.rectangle([0, haut, w, bas], fill=OR)
    # plaques de ventre (crème) dans le bas
    ventre = 0.72 * h
    d.rectangle([0, ventre, w, bas], fill=CREME)
    for k in range(periode * 3 + 1):
        x = k * w / (periode * 3)
        d.line([(x, ventre), (x - 0.02 * w, bas)], fill=OR_OMBRE, width=7)
    # écailles en écusson (rangées décalées), contour ombre
    rangs = 3
    for r in range(rangs):
        y = haut + (r + 0.6) * (ventre - haut) / rangs
        n = periode * 2
        for k in range(n + 1):
            x = (k + 0.5 * (r % 2)) * w / n
            rx, ry = w / n * 0.55, (ventre - haut) / rangs * 0.62
            d.arc([x - rx, y - ry, x + rx, y + ry], 10, 170, fill=OR_OMBRE, width=8)
    # reflet cel le long du dos
    d.rectangle([0, haut + 0.04 * h, w, haut + 0.10 * h], fill=OR_CLAIR)
    # contours dos et ventre
    d.line([(0, haut), (w, haut)], fill=BRUN, width=10)
    d.line([(0, bas), (w, bas)], fill=BRUN, width=10)
    return im.resize((W, H), Image.LANCZOS)


def eclair(W=256, H=64):
    """Segment d'éclair : cœur blanc, halo blanc à teinter (Beam.Color)."""
    y = np.linspace(-1, 1, H)[:, None]
    a = np.clip(1 - np.abs(y) / 0.18, 0, 1) ** 0.6 + 0.55 * np.exp(-(y / 0.45) ** 2)
    a = np.clip(a, 0, 1) * np.ones((1, W))
    rgba = np.zeros((H, W, 4), np.uint8)
    rgba[..., :3] = 255
    rgba[..., 3] = (a * 255).astype(np.uint8)
    return Image.fromarray(rgba)


def dragon_tete_miroir():
    """La même, retournée : face ARRIÈRE de la carte sur Roblox (un Decal ne
    se retourne pas tout seul ; sans elle, vu de dos, le museau pointerait
    vers l'arrière)."""
    return dragon_tete().transpose(Image.FLIP_LEFT_RIGHT)


PEINTS = {
    "dragon_tete": (dragon_tete, "peint", "tête du dragon de profil (carte), museau à droite"),
    "dragon_tete_miroir": (dragon_tete_miroir, "peint", "tête du dragon, miroir (face arrière de la carte Roblox)"),
    "dragon_ecailles": (dragon_ecailles, "peint", "corps du dragon pour Beam, raccord en U"),
    "eclair": (eclair, "à teinter", "segment d'éclair (Beam), cœur blanc"),
}
