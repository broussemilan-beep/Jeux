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

Usage : python3 build_planches.py [rendu_gueule.png] [rendu_silhouette.png]
          ->  ../output/planches/*.png
(rendus du labo : recettes dragon_gueule_demo caméra « face » et
dragon_silhouette_demo caméra « profil », `capture_lab.js ... video:1:1`,
image f0001 ; sans rendu : la gueule n'est pas produite / le soleil est
sans silhouette)

v13c (retour de Milan : tourbillon et rouge « trop peinture, pas dessiné »,
soleil « bonne idée, à faire beaucoup mieux ») : les trois sont TRACÉS
(lames effilées cernées, hachures, lignes de vitesse), la silhouette du
soleil est notre modèle. fiches/PLEIN_ECRAN.md.
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


SS = 2                      # tracé à 2x puis réduit : bords nets mais lissés
CARRE = 1440                # côté des planches qui tournent


def toile(col):
    return Image.new("RGB", (W * SS, H * SS), col)


def reduire(im):
    return im.resize((W, H), Image.LANCZOS)


# ------------------------------------------------------------------ DESSIN
# (retour de Milan sur la v13 : « le tourbillon et le rouge : trop peinture,
# pas dessiné ». Ils venaient d'un champ de bruit coupé en paliers -> des
# taches aux bords mous. Ici chaque forme est TRACÉE : une ligne médiane,
# une largeur qui s'effile en pointe, un trait d'encre plus épais du côté
# de l'ombre, des traits de détail à l'intérieur. fiches/PLEIN_ECRAN.md)

def _normales(pts):
    pts = np.asarray(pts, float)
    n = len(pts)
    out = []
    for i in range(n):
        t = pts[min(n - 1, i + 1)] - pts[max(0, i - 1)]
        t /= (np.linalg.norm(t) + 1e-9)
        out.append(np.array([-t[1], t[0]]))
    return pts, out


def contour_lame(pts, larg, ga=0.0, dr=0.0, pointes=()):
    """Polygone d'une lame : ligne médiane `pts`, demi-largeur larg[i],
    + ga à gauche et + dr à droite (le trait d'encre, asymétrique).
    `pointes` : (indice, longueur) des langues secondaires sur le bord
    droit, qui partent vers l'avant (dents de scie du feu)."""
    pts, nn = _normales(pts)
    n = len(pts)
    g = [tuple(p + n_ * (w + ga * (w > 0.5))) for p, n_, w in zip(pts, nn, larg)]
    d = []
    pk = dict(pointes)
    for i, (p, n_, w) in enumerate(zip(pts, nn, larg)):
        d.append(tuple(p - n_ * (w + dr * (w > 0.5))))
        if i in pk and 0 < i < n - 1:
            t = pts[i + 1] - pts[i - 1]
            t /= (np.linalg.norm(t) + 1e-9)
            ln = pk[i]
            d.append(tuple(p - n_ * (w + ln * 0.55 + dr) + t * (ln + dr)))
    return g + d[::-1]


def lame(d, pts, larg, fond, encre_, e_ombre, e_jour, details=0, rng=None, col_detail=None, pointes=()):
    """Lame dessinée : trait d'encre (plus épais côté ombre = gauche), aplat,
    puis `details` traits fins parallèles côté ombre (le dessin du feu)."""
    d.polygon(contour_lame(pts, larg, e_ombre, e_jour, pointes), fill=encre_)
    d.polygon(contour_lame(pts, larg, 0, 0, pointes), fill=fond)
    if details:
        pts_, nn = _normales(pts)
        n = len(pts_)
        for j in range(details):
            off = 0.25 + 0.5 * j / max(1, details - 1)
            a0 = int(n * (0.12 + 0.12 * rng.random()))
            a1 = int(n * (0.55 + 0.3 * rng.random()))
            ligne = [tuple(pts_[i] + nn[i] * larg[i] * off) for i in range(a0, a1)]
            if len(ligne) > 1:
                # trait effilé : segments de plus en plus fins
                for i in range(len(ligne) - 1):
                    w = max(1, int(round(larg[a0 + i] * 0.09 * (1 - i / len(ligne)) + 1)))
                    d.line([ligne[i], ligne[i + 1]], fill=col_detail or encre_, width=w)


def trait_effile(d, a, b, w0, w1, col):
    """Trait de vitesse : trapèze de largeur w0 en a à w1 en b."""
    a, b = np.asarray(a, float), np.asarray(b, float)
    t = b - a
    t /= (np.linalg.norm(t) + 1e-9)
    n = np.array([-t[1], t[0]])
    d.polygon([tuple(a + n * w0), tuple(b + n * w1), tuple(b - n * w1), tuple(a - n * w0)], fill=col)


def etoile(d, cx, cy, r, pointes, creux, col, rot=0.0, rng=None, jit=0.0):
    pts = []
    for i in range(pointes * 2):
        a = rot + math.pi * i / pointes
        rr = r * (1 if i % 2 == 0 else creux)
        if rng is not None and i % 2 == 0:
            rr *= 1 + jit * (rng.random() - 0.5)
        pts.append((cx + math.cos(a) * rr, cy + math.sin(a) * rr))
    d.polygon(pts, fill=col)


def profil_lame(n, pointe=1.0, base=0.35):
    """Largeur le long de la lame (0..1) : naît fine, gonfle, finit en POINTE."""
    t = np.linspace(0, 1, n)
    return np.sin(np.pi * np.clip(t, 0, 1) ** 0.65) ** 0.9 * (1 - 0.25 * t) * (base + (1 - base) * np.minimum(1, t * 3))


def spirale(k):
    """Tourbillon de feu DESSINÉ (Goku d514ee70, 1,0-2,1 s) : lames en
    spirale empilées du bord sombre au cœur blanc, cernées, avec les traits
    du feu ; virgules éjectées ; lignes de vitesse. k = dessin (le trait
    « bout » d'un dessin à l'autre, les formes restent)."""
    # CARRÉE : le lecteur et DragonFist.luau posent une planche qui tourne
    # dans un carré de côté = diagonale de l'écran ; on n'en voit que le
    # disque de rayon côté/2 (1er essai en 16:9 : recadrée x2, et étirée
    # en jeu)
    C = CARRE * SS
    im = Image.new("RGB", (C, C), (58, 6, 3))
    d = ImageDraw.Draw(im)
    cx, cy = C / 2, C / 2
    R = C / 2
    rng = np.random.default_rng(100 + k)
    sens = 1.0
    # lignes de vitesse du fond : arcs de spirale effilés
    for i in range(70):
        a0 = rng.uniform(0, 2 * math.pi)
        r0 = rng.uniform(0.35, 1.05) * R
        pts = [(cx + math.cos(a0 + sens * 0.5 * u) * r0 * (1 - 0.25 * u), cy + math.sin(a0 + sens * 0.5 * u) * r0 * (1 - 0.25 * u))
               for u in np.linspace(0, 1, 10)]
        w0 = rng.uniform(1.5, 6) * SS
        for j in range(len(pts) - 1):
            trait_effile(d, pts[j], pts[j + 1], w0 * (1 - j / 9), w0 * (1 - (j + 1) / 9) + 0.3,
                         (120, 20, 8) if i % 3 else (28, 2, 1))
    # (1er essai : 4 couches de grandes lames lisses, blanc à 30 % de
    # l'image = un logo vectoriel, pas du feu) -> lames plus fines et plus
    # nombreuses, langues secondaires en dents de scie, cœur blanc petit
    couches = [  # (aplat, encre, nb, r_in, r_out, largeur, courbure, détails)
        ((178, 34, 12), (30, 3, 2), 11, 0.28, 1.30, 0.13, 2.3, 3),
        ((226, 78, 16), (70, 10, 3), 11, 0.2, 1.08, 0.105, 2.45, 2),
        (ORANGE, (120, 26, 6), 10, 0.13, 0.80, 0.085, 2.6, 2),
        (OR, (176, 78, 10), 9, 0.07, 0.52, 0.065, 2.75, 1),
        (BLANC, (238, 158, 40), 7, 0.03, 0.28, 0.045, 2.9, 0),
    ]
    for c, (fond, enc, nb, ri, ro, lw, courb, det) in enumerate(couches):
        for i in range(nb):
            th0 = 2 * math.pi * (i + 0.5 * c) / nb + 0.04 * (rng.random() - 0.5)
            cv = courb * (1 + 0.05 * (rng.random() - 0.5))
            n = 40
            pts = []
            for u in np.linspace(0, 1, n):
                r = (ri + (ro - ri) * u ** 0.9) * R
                th = th0 + sens * cv * u
                pts.append((cx + math.cos(th) * r, cy + math.sin(th) * r))
            larg = profil_lame(n) * lw * R * (1 + 0.07 * (rng.random() - 0.5))
            pk = [(int(n * f), lw * R * rng.uniform(0.5, 0.9)) for f in (0.35 + 0.05 * rng.random(), 0.6 + 0.05 * rng.random())]
            lame(d, pts, larg, fond, enc, e_ombre=(4.5 + 1.5 * rng.random()) * SS, e_jour=1.2 * SS,
                 details=det, rng=rng, col_detail=enc, pointes=pk)
    # cœur : étoile blanche cernée d'or
    etoile(d, cx, cy, 0.085 * R, 11, 0.6, (238, 158, 40), rot=0.3 + 0.05 * k, rng=rng, jit=0.25)
    etoile(d, cx, cy, 0.072 * R, 11, 0.6, BLANC, rot=0.3 + 0.05 * k, rng=rng, jit=0.2)
    # petites langues de feu éjectées (tangentes, effilées aux deux bouts)
    # (1er essai en virgules à tête ronde : des comètes)
    for i in range(18):
        a0 = rng.uniform(0, 2 * math.pi)
        r0 = rng.uniform(0.3, 0.9) * R
        ln = rng.uniform(0.05, 0.1) * R
        pts = [(cx + math.cos(a0 + sens * u * ln / r0) * (r0 + 0.35 * ln * u), cy + math.sin(a0 + sens * u * ln / r0) * (r0 + 0.35 * ln * u))
               for u in np.linspace(0, 1, 14)]
        larg = profil_lame(14, base=0.8) * ln * 0.16
        lame(d, pts, larg, OR if i % 3 else BLANC, (120, 26, 6), 2.5 * SS, 1.0 * SS)
    # éclats (croix blanches)
    for i in range(22):
        a0, r0 = rng.uniform(0, 2 * math.pi), rng.uniform(0.2, 0.9) * R
        x, y, s = cx + math.cos(a0) * r0, cy + math.sin(a0) * r0, rng.uniform(6, 16) * SS
        etoile(d, x, y, s, 4, 0.18, (255, 250, 220), rot=rng.uniform(0, 1))
    return im.resize((CARRE, CARRE), Image.LANCZOS)


def rouge(k):
    """Horizon rouge DESSINÉ (Last Breath v1, 18,3 s) : le dragon a plongé à
    l'horizon ; lignes de vitesse qui CONVERGENT sur l'impact, halos en
    couronnes pointues, dôme de langues de feu cernées, sol noir fissuré,
    éclats de roche projetés."""
    im = toile((188, 30, 12))
    d = ImageDraw.Draw(im)
    rng = np.random.default_rng(200 + k)
    Wc, Hc = W * SS, H * SS
    px, py = Wc * 0.5, Hc * 0.66
    # bande sombre du haut, bord en dents de scie
    haut = [(0, 0), (Wc, 0)]
    for i in range(41):
        x = Wc * (1 - i / 40)
        haut.append((x, Hc * (0.16 + 0.05 * (i % 2)) + rng.uniform(-6, 6) * SS))
    d.polygon(haut, fill=(92, 10, 5))
    # halos en couronnes pointues
    for rr, fond, enc in ((0.62, (226, 78, 16), (120, 20, 6)), (0.44, ORANGE, (150, 40, 6)),
                          (0.3, OR, (190, 90, 12)), (0.17, BLANC, (240, 160, 40))):
        etoile(d, px, py, rr * Hc + 5 * SS, 38, 0.86, enc, rot=0.05 * k, rng=rng, jit=0.12)
        etoile(d, px, py, rr * Hc, 38, 0.86, fond, rot=0.05 * k, rng=rng, jit=0.12)
    # lignes de vitesse noires qui convergent (manga), zone claire autour
    for i in range(150):
        a = rng.uniform(math.pi * 1.02, math.pi * 1.98) if i % 5 else rng.uniform(0, 2 * math.pi)
        r1 = rng.uniform(0.62, 0.95) * Hc
        r0 = 1.3 * Wc
        w0 = rng.uniform(1.5, 9) * SS
        trait_effile(d, (px + math.cos(a) * r0, py + math.sin(a) * r0), (px + math.cos(a) * r1, py + math.sin(a) * r1),
                     w0, 0.3, (26, 3, 1))
    # dôme de langues de feu (du fond vers l'avant : sombre -> blanc)
    for c, (fond, enc, lmin, lmax, lw) in enumerate(((ROUGE, (40, 4, 2), 0.38, 0.62, 0.075),
                                                     (ORANGE, (120, 26, 6), 0.28, 0.48, 0.06),
                                                     (OR, (176, 78, 10), 0.18, 0.34, 0.048),
                                                     (BLANC, (238, 158, 40), 0.1, 0.2, 0.035))):
        nb = 15 - 2 * c
        for i in range(nb):
            a = math.radians(-172 + 164 * (i + 0.5 * (c % 2)) / nb) + 0.05 * (rng.random() - 0.5)
            ln = rng.uniform(lmin, lmax) * Hc
            courbe = rng.uniform(-0.35, 0.35)
            n = 30
            pts = [(px + math.cos(a + courbe * u * u) * ln * u, py + math.sin(a + courbe * u * u) * ln * u) for u in np.linspace(0, 1, n)]
            larg = profil_lame(n, base=0.6) * lw * Hc
            lame(d, pts, larg, fond, enc, 4 * SS, 1.2 * SS, details=1 if c < 2 else 0, rng=rng, col_detail=enc)
    # sol noir, horizon en roches
    sol = [(0, Hc)]
    for i in range(61):
        x = Wc * i / 60
        bosse = 0 if abs(x - px) > 0.12 * Wc else -0.02 * Hc
        sol.append((x, py + bosse + rng.uniform(-9, 3) * SS * (1 + 2 * (i % 7 == 0))))
    sol.append((Wc, Hc))
    d.polygon(sol, fill=(16, 4, 2))
    # fissures de lave en perspective depuis l'impact
    for i in range(18):
        x = px
        y = py + 4 * SS
        cible = rng.uniform(-0.6, 1.6) * Wc
        pts = [(x, y)]
        for j in range(1, 9):
            u = j / 8
            pts.append((px + (cible - px) * u + rng.uniform(-14, 14) * SS * u, py + (Hc * 1.05 - py) * u ** 1.3))
        for j in range(len(pts) - 1):
            w = (1 - j / 8) * rng.uniform(2, 6) * SS + 1
            trait_effile(d, pts[j], pts[j + 1], w, w * 0.8, (230, 90, 20) if i % 3 else OR)
    # éclats de roche projetés, avec traînée
    for i in range(12):
        a = rng.uniform(math.pi * 1.1, math.pi * 1.9)
        r = rng.uniform(0.5, 0.8) * Hc
        x, y = px + math.cos(a) * r, py + math.sin(a) * r
        s = rng.uniform(6, 20) * SS
        trait_effile(d, (x - math.cos(a) * s * 3, y - math.sin(a) * s * 3), (x, y), 0.4, s * 0.35, (60, 8, 4))
        pts = [(x + math.cos(t) * s * rng.uniform(0.6, 1), y + math.sin(t) * s * rng.uniform(0.6, 1)) for t in np.linspace(0, 2 * math.pi, 6)[:-1]]
        d.polygon(pts, fill=(14, 3, 1))
    return reduire(im)


def masque_silhouette(rendu):
    """Rendu du labo (recette dragon_silhouette_demo, ciel uni) -> masque du
    dragon (NOTRE modèle : crinière, cornes, moustaches, gueule)."""
    a = np.asarray(Image.open(rendu).convert("RGB"), np.float32)
    h, w, _ = a.shape
    fond = np.median(np.concatenate([a[:8].reshape(-1, 3), a[-8:].reshape(-1, 3)]), axis=0)
    m = np.linalg.norm(a - fond, axis=-1) > 38
    m[:3], m[-3:], m[:, :3], m[:, -3:] = False, False, False, False     # coins arrondis du cadre
    ys, xs = np.nonzero(m)
    x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
    return Image.fromarray((m[y0:y1 + 1, x0:x1 + 1] * 255).astype(np.uint8))


def soleil(rendu_sil=None):
    """Soleil DESSINÉ avec la silhouette de NOTRE dragon qui plonge (Last
    Breath v1, 20,3 s ; l'idée que Milan aime, à mieux faire) : couronne de
    rayons en triangles, trame de points vers les bords, disque cerné,
    silhouette avec liseré de contre-jour, lignes de vitesse."""
    Wc, Hc = W * SS, H * SS
    im = toile((232, 104, 20))
    d = ImageDraw.Draw(im)
    rng = np.random.default_rng(300)
    cx, cy, R = Wc * 0.53, Hc * 0.47, Hc * 0.34
    # rayons : triangles alternés
    for i in range(48):
        a = 2 * math.pi * i / 48
        w = 0.05 if i % 2 else 0.028
        col = (250, 150, 36) if i % 2 else (176, 44, 10)
        d.polygon([(cx + math.cos(a - w) * R * 0.9, cy + math.sin(a - w) * R * 0.9), (cx + math.cos(a) * Wc * 1.2, cy + math.sin(a) * Wc * 1.2),
                   (cx + math.cos(a + w * 0.4) * Wc * 1.2, cy + math.sin(a + w * 0.4) * Wc * 1.2), (cx + math.cos(a + w) * R * 0.9, cy + math.sin(a + w) * R * 0.9)], fill=col)
    # trame de points (plus grosse vers les bords : le manga)
    pas = 18 * SS
    for y in range(0, Hc, pas):
        for x in range(0, Wc, pas):
            xx = x + (pas / 2 if (y // pas) % 2 else 0)
            r = math.hypot(xx - cx, y - cy) / (Wc * 0.62)
            rr = max(0, (r - 0.55)) * 11 * SS
            if rr > 0.6:
                d.ellipse([xx - rr, y - rr, xx + rr, y + rr], fill=(120, 24, 6))
    # lignes de vitesse noires sur les bords
    for i in range(90):
        a = rng.uniform(0, 2 * math.pi)
        r1 = rng.uniform(0.62, 0.8) * Wc
        trait_effile(d, (cx + math.cos(a) * Wc * 1.3, cy + math.sin(a) * Wc * 1.3), (cx + math.cos(a) * r1, cy + math.sin(a) * r1),
                     rng.uniform(1.5, 7) * SS, 0.3, (30, 4, 1))
    # disque : anneau d'encre, or, crème, cœur blanc ; deux arcs de lumière
    for rr, col in ((1.1, (60, 10, 2)), (1.06, OR), (0.93, (255, 236, 150)), (0.78, BLANC)):
        d.ellipse([cx - R * rr, cy - R * rr, cx + R * rr, cy + R * rr], fill=col)
    for rr in (0.86, 0.99):
        d.arc([cx - R * rr, cy - R * rr, cx + R * rr, cy + R * rr], 200, 250, fill=(255, 250, 230), width=5 * SS)
    # silhouette de NOTRE dragon, qui déborde du soleil (plus long que le cadre)
    if rendu_sil and os.path.exists(rendu_sil):
        m = masque_silhouette(rendu_sil)
        # (1er essai à 0,98 H : la tête, sous le sol, ne se lisait pas ;
        # c'est la gueule ouverte qui dit « notre dragon ») -> plus petit,
        # la tête AU-DESSUS du sol, qui plonge
        haut = int(Hc * 0.8)
        larg = int(m.size[0] * haut / m.size[1])
        m = m.resize((larg, haut), Image.BICUBIC).filter(ImageFilter.GaussianBlur(1.2 * SS))
        m = m.point(lambda v: 255 if v > 120 else 0)
        ox, oy = int(cx - larg * 0.5), int(cy - haut * 0.56)
        full = Image.new("L", (Wc, Hc), 0)
        full.paste(m, (ox, oy))
        M = np.asarray(full) > 0
        # liseré de contre-jour : bord du dragon tourné vers le soleil
        yy, xx = np.nonzero(M)
        dx, dy = cx - xx, cy - yy
        nrm = np.hypot(dx, dy) + 1e-6
        k_ = 7 * SS
        sx = np.clip((xx + dx / nrm * k_).astype(int), 0, Wc - 1)
        sy = np.clip((yy + dy / nrm * k_).astype(int), 0, Hc - 1)
        bord = ~M[sy, sx]
        arr = np.asarray(im).copy()
        arr[M] = (16, 6, 3)
        prox = np.clip(1.6 - nrm / (R * 1.4), 0, 1)
        rim = np.zeros(M.shape, bool)
        rim[yy[bord & (prox > 0.2)], xx[bord & (prox > 0.2)]] = True
        arr[rim] = (255, 196, 70)
        im = Image.fromarray(arr)
        d = ImageDraw.Draw(im)
    # sol noir, horizon en roches
    sol = [(0, Hc)]
    for i in range(41):
        sol.append((Wc * i / 40, Hc * 0.9 + rng.uniform(-10, 4) * SS * (1 + 2 * (i % 5 == 0))))
    sol.append((Wc, Hc))
    d.polygon(sol, fill=(12, 3, 1))
    return reduire(im)


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


def main(rendu=None, rendu_sil=None):
    os.makedirs(OUT, exist_ok=True)
    for k in range(3):
        spirale(k).save(os.path.join(OUT, f"spirale_{k}.png"))
    for k in range(2):
        rouge(k).save(os.path.join(OUT, f"rouge_{k}.png"))
    soleil(rendu_sil).save(os.path.join(OUT, "soleil.png"))
    if rendu and os.path.exists(rendu):
        g = encre(rendu)
        g.save(os.path.join(OUT, "gueule_encre.png"))
        inverse(g).save(os.path.join(OUT, "gueule_inverse.png"))
    print(sorted(os.listdir(OUT)))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None, sys.argv[2] if len(sys.argv) > 2 else None)
