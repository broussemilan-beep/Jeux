"""
DRAGON 3D du Poing du Dragon (fiches/AURA_DRAGON.md, retour de Milan v11 :
« le dragon est moche, pas du tout du modèle premium »). Un vrai modèle en
VOLUME, riggé pour suivre une courbe :

- corps : tube loft (section en superellipse, ventre aplati) de 14 studs,
  rayon qui s'affine vers la queue, nageoires dorsales, 4 pattes griffues,
  touffe de flammes au bout de la queue ;
- tête (museau vers -X) : crâne, museau et mâchoire inférieure OUVERTE en
  lofts, bosse du nez, arcades, yeux, crocs (gros crocs devant), cornes en
  bois de cerf, longues moustaches, crinière de flammes, barbe, piquants de
  joue ;
- une texture atlas (2048²) : bande du corps (écailles en écusson, dos plus
  foncé, plaques de ventre crème) + pastilles de couleur en dégradé (le
  dégradé fait l'ombrage peint) pour les pièces de la tête ;
- skinning : os « Tete » (rigide pour toute la tête) + 24 os de colonne le
  long de +X, au plus 2 influences par sommet ; os racine sans influence
  (spécifications Roblox : <= 20 000 triangles, <= 4 influences).

Sorties (dossier modeles/) :
- dragon.json : géométrie + skinning pour l'aperçu three.js (SkinnedMesh) ;
- dragon_atlas.png : la texture ;
- dragon.fbx : pour Roblox (export_blender.py, via Blender).

Repère : Y en haut, colonne le long de +X (tête à x <= 0, queue à x = L).
Unité : le stud.
"""
import json
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
L = 14.0          # longueur du corps
NB = 24           # os de colonne
ATLAS = 2048

# pastilles (v de 0.78 à 1 ; 8 colonnes) : nom -> (ton clair, ton d'ombre).
# v13 (Milan : « VFX de qualité dessin, pas cartoon » ; refs Goku d514ee70,
# Dragon Ball Rage) : DEUX TONS francs, plus de dégradé (le dégradé faisait
# une statue éclairée) ; yeux CYAN (accent complémentaire de l'or).
PASTILLES = {
    "or": ((255, 212, 64), (232, 138, 28)),
    "or_fonce": ((236, 150, 36), (168, 76, 14)),
    "creme": ((255, 244, 200), (238, 192, 116)),
    "brun": ((160, 58, 14), (96, 30, 6)),
    "blanc": ((255, 255, 250), (226, 220, 206)),
    "rouge": ((196, 30, 22), (118, 10, 10)),
    "oeil": ((170, 255, 255), (40, 214, 255)),
    "noir": ((30, 12, 4), (18, 6, 2)),
}
NOMS = list(PASTILLES)


def uv_pastille(nom, h):
    """UV dans la pastille `nom`, h in [0,1] = hauteur relative (1 = haut, clair)."""
    k = NOMS.index(nom)
    u = (k + 0.5) / len(NOMS)
    v = 0.80 + 0.18 * (1 - np.clip(h, 0, 1))
    return u, 1 - v   # convention UV (v vers le haut de l'image = 1)


class Piece:
    def __init__(self):
        self.P, self.UV, self.F, self.B = [], [], [], []   # sommets, uv, faces, os (x de liaison ou -1 = tête)

    def ajoute(self, P, UV, F, liaison):
        # faces tournées vers l'EXTÉRIEUR de la pièce (les lofts construits du
        # cou vers le nez avaient l'enroulement inverse du corps : dans
        # three.js, face avant seulement, on voyait la coque noire du contour)
        Pa, Fa = np.asarray(P, float), np.asarray(F, int)
        tri = Pa[Fa]
        n = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
        centre = Pa.mean(axis=0)
        if np.sum(np.einsum("ij,ij->i", tri.mean(axis=1) - centre, n)) < 0:
            F = [(a, c, b) for a, b, c in F]
        o = len(self.P)
        self.P += [tuple(p) for p in P]
        self.UV += [tuple(u) for u in UV]
        self.F += [(a + o, b + o, c + o) for a, b, c in F]
        self.B += list(liaison) if hasattr(liaison, "__len__") else [liaison] * len(P)


def grille_faces(nu, nv, ferme_v=True):
    F = []
    for i in range(nu - 1):
        for j in range(nv if ferme_v else nv - 1):
            a, b = i * nv + j, i * nv + (j + 1) % nv
            c, d = (i + 1) * nv + j, (i + 1) * nv + (j + 1) % nv
            F += [(a, c, b), (b, c, d)]
    return F


def section(n, ex=2.6, ventre=0.75):
    """Section en superellipse, ventre aplati. Angle 0 = côté +Z, pi/2 = dos (+Y)."""
    out = []
    for j in range(n):
        a = 2 * math.pi * j / n
        c, s = math.cos(a), math.sin(a)
        y = math.copysign(abs(s) ** (2 / ex), s)
        z = math.copysign(abs(c) ** (2 / ex), c)
        if y < 0:
            y *= ventre
        out.append((y, z, a))
    return out


def loft(centres, largeurs, hauteurs, n=20, axes=None, ex=2.6, ventre=0.75, uvf=None, liaison=None, bouchon=True):
    """Anneaux le long de `centres` ; axes[i] = (Y, Z) du repère local (défaut : monde)."""
    sec = section(n, ex, ventre)
    P, UV = [], []
    for i, c in enumerate(centres):
        Y, Z = (np.array([0, 1.0, 0]), np.array([0, 0, 1.0])) if axes is None else axes[i]
        for (y, z, a) in sec:
            p = np.array(c) + Y * y * hauteurs[i] + Z * z * largeurs[i]
            P.append(p)
            UV.append(uvf(i, a, p) if uvf else (0, 0))
    F = grille_faces(len(centres), n)
    if bouchon:   # bouchons plats aux deux bouts
        for bout, ordre in ((0, 1), (len(centres) - 1, -1)):
            cidx = len(P)
            P.append(np.array(centres[bout]))
            UV.append(UV[bout * n])
            for j in range(n):
                a, b = bout * n + j, bout * n + (j + 1) % n
                F.append((cidx, a, b) if ordre < 0 else (cidx, b, a))
    return P, UV, F


def tube(pts, rayons, n=8, uv=(0, 0), uv_h=None, aplati=1.0, plat_ref=None):
    """Tube le long d'une polyligne (cornes, moustaches, griffes, flammes) ;
    aplati < 1 : section en ellipse (langue de flamme), écrasée le long de
    plat_ref (la normale du plan de la flamme)."""
    pts = np.asarray(pts, float)
    P, UV = [], []
    up = np.array([0, 1.0, 0])
    for i, p in enumerate(pts):
        t = pts[min(i + 1, len(pts) - 1)] - pts[max(i - 1, 0)]
        t /= np.linalg.norm(t) + 1e-12
        ref = (np.asarray(plat_ref, float) if plat_ref is not None else up)
        if abs(t @ ref) > 0.95:
            ref = np.array([1.0, 0, 0])
        e1 = np.cross(t, ref); e1 /= np.linalg.norm(e1)
        e2 = np.cross(t, e1)
        for j in range(n):
            a = 2 * math.pi * j / n
            P.append(p + rayons[i] * (math.cos(a) * e1 + aplati * math.sin(a) * e2))
            UV.append(uv if uv_h is None else uv_h(i / (len(pts) - 1), j / n))
    F = grille_faces(len(pts), n)
    # pointe fermée
    cidx = len(P)
    P.append(pts[-1] + (pts[-1] - pts[-2]) * 0.3)
    UV.append(UV[-1])
    for j in range(n):
        a, b = (len(pts) - 1) * n + j, (len(pts) - 1) * n + (j + 1) % n
        F.append((a, cidx, b))
    return P, UV, F


def bezier(p0, p1, p2, p3, n):
    t = np.linspace(0, 1, n)[:, None]
    p0, p1, p2, p3 = map(np.asarray, (p0, p1, p2, p3))
    return (1 - t) ** 3 * p0 + 3 * (1 - t) ** 2 * t * p1 + 3 * (1 - t) * t ** 2 * p2 + t ** 3 * p3


def ellipsoide(c, r, nu=16, nv=12, pastille="or", rot=None):
    P, UV, F = [], [], []
    for i in range(nv + 1):
        th = math.pi * i / nv
        for j in range(nu):
            ph = 2 * math.pi * j / nu
            d = np.array([math.sin(th) * math.cos(ph), math.cos(th), math.sin(th) * math.sin(ph)]) * np.array(r)
            if rot is not None:
                d = rot @ d
            P.append(np.array(c) + d)
            UV.append(uv_pastille(pastille, 0.5 + 0.5 * math.cos(th)))
    F = grille_faces(nv + 1, nu)
    return P, UV, F


def rotz(a):
    c, s = math.cos(a), math.sin(a)
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1.0]])


CHARNIERE = np.array([-0.9, 0.12, 0])   # charnière de la mâchoire (repère du modèle, avant l'échelle de tête)
MACHOIRE_REPOS = 20.0                    # angle d'ouverture de la mâchoire MODÉLISÉE (degrés) ; os à l'identité


def construire():
    M = Piece()
    TETE = -1   # liaison : os de tête (rigide)

    # ------------------------------------------------------------ CORPS
    n_anneaux = 120
    xs = np.linspace(-0.2, L, n_anneaux)

    def rayon(x):
        u = max(0.0, x / L)
        return 0.74 + 0.22 * math.sin(math.pi * min(1, u * 1.6)) * (1 - u) - 0.66 * u ** 1.5 if u < 1 else 0.06

    R = [max(0.07, rayon(x)) for x in xs]

    def uv_corps(i, a, p):
        return (xs[i] / L, 0.78 * ((a / (2 * math.pi)) % 1.0))
    P, UV, F = loft([(x, 0, 0) for x in xs], R, [r * 0.95 for r in R], n=20, uvf=uv_corps)
    UV = [(u, 1 - v) for u, v in UV]
    M.ajoute(P, UV, F, [p[0] for p in P])

    # nageoires dorsales (lames brunes, penchées vers l'arrière)
    for x0 in np.arange(0.6, L - 0.8, 0.42):
        r = max(0.08, rayon(x0))
        h = 0.55 * (r / 0.7) ** 0.8
        base_a, base_b = np.array([x0 - 0.18, r * 0.9, 0]), np.array([x0 + 0.22, r * 0.9, 0])
        pointe = np.array([x0 + 0.34, r * 0.9 + h, 0])
        ep = np.array([0, 0, 0.045])
        P = [base_a + ep, base_b + ep, pointe + ep * 0.3, base_a - ep, base_b - ep, pointe - ep * 0.3]
        UV = [uv_pastille("brun", 0.2), uv_pastille("brun", 0.2), uv_pastille("brun", 0.9)] * 2
        F = [(0, 1, 2), (3, 5, 4), (0, 2, 3), (3, 2, 5), (1, 4, 2), (4, 5, 2), (0, 3, 1), (1, 3, 4)]
        M.ajoute(P, UV, F, x0)

    # pattes griffues (Shenron : 4 petites pattes)
    for x0 in (2.6, 8.4):
        r = rayon(x0)
        for cote in (1, -1):
            haut = np.array([x0, -0.25 * r, cote * 0.75 * r])
            coude = haut + np.array([0.35, -0.55, cote * 0.35])
            pied = coude + np.array([-0.25, -0.35, cote * 0.1])
            pts = bezier(haut, haut + np.array([0.2, -0.3, cote * 0.3]), coude, pied, 8)
            P, UV, F = tube(pts, np.linspace(0.2, 0.12, 8), 8, uv_h=lambda s, j: uv_pastille("or", 0.7 - 0.4 * s))
            M.ajoute(P, UV, F, x0)
            for k in (-1, 0, 1):   # 3 griffes
                g0 = pied
                g1 = pied + np.array([-0.28, -0.05, k * 0.14 + cote * 0.05])
                g2 = g1 + np.array([-0.12, -0.14, k * 0.04])
                P, UV, F = tube(bezier(g0, g0 + (g1 - g0) * 0.5, g1, g2, 5), np.linspace(0.07, 0.015, 5), 6,
                                uv=uv_pastille("blanc", 0.6))
                M.ajoute(P, UV, F, x0)

    # touffe de flammes au bout de la queue
    for k in range(7):
        a = -0.9 + 1.8 * k / 6
        base = np.array([L - 0.15, 0, 0])
        dirn = np.array([math.cos(a * 0.6), math.sin(a), 0.35 * math.sin(3 * a)])
        pts = bezier(base, base + dirn * 0.5, base + dirn * 1.0 + np.array([0.5, 0.15, 0]), base + dirn * 1.5 + np.array([0.9, 0.35, 0]), 8)
        P, UV, F = tube(pts, np.linspace(0.14, 0.01, 8), 6, uv_h=lambda s, j: uv_pastille("brun", 1 - s))
        M.ajoute(P, UV, F, L)

    # ------------------------------------------------------------ TÊTE
    # TÊTE d'un seul tenant (2e version : crâne + museau collés = « canard ») :
    # un loft du cou au bout du nez dont la section passe de ronde (crâne) à
    # anguleuse (museau), arête du nez, naseaux relevés ; le palais est rouge
    def profil_tete(x):
        """x de 0.3 (cou) à -4.1 (nez) -> (yc, largeur, haut, bas, exposant)."""
        k = [(0.3, 0.20, 0.78, 0.80, 0.55, 2.2), (-0.6, 0.22, 0.82, 0.78, 0.45, 2.3), (-1.3, 0.24, 0.72, 0.62, 0.22, 2.6),
             (-1.9, 0.27, 0.60, 0.46, 0.13, 3.0), (-2.8, 0.27, 0.50, 0.36, 0.12, 3.4), (-3.5, 0.30, 0.46, 0.38, 0.12, 3.4),
             (-3.8, 0.33, 0.50, 0.44, 0.13, 3.0), (-4.05, 0.30, 0.30, 0.24, 0.10, 2.6), (-4.15, 0.28, 0.06, 0.06, 0.05, 2.2)]
        for a, b in zip(k, k[1:]):
            if b[0] <= x <= a[0]:
                u = (a[0] - x) / (a[0] - b[0])
                return tuple(a[m] + (b[m] - a[m]) * u for m in range(1, 6))
        return k[-1][1:]
    xs_t = np.linspace(0.3, -4.15, 34)
    n_t = 26
    P, UV = [], []
    for x in xs_t:
        yc, w, ht, hb, ex = profil_tete(x)
        for jj in range(n_t):
            a = 2 * math.pi * jj / n_t
            c, s_ = math.cos(a), math.sin(a)
            y = math.copysign(abs(s_) ** (2 / ex), s_)
            z = math.copysign(abs(c) ** (2 / ex), c)
            y = y * (ht if y > 0 else hb)
            # arête du nez : le dessus du museau se pince légèrement
            if y > 0 and x < -1.6:
                z *= 1 - 0.18 * (y / ht) ** 3
            P.append(np.array([x, yc + y, z * w]))
            palais = s_ < -0.55 and x < -1.1
            UV.append(uv_pastille("rouge" if palais else "or", 0.5 + 0.5 * s_))
    F = grille_faces(len(xs_t), n_t)
    cidx = len(P); P.append(np.array([xs_t[-1] - 0.02, 0.28, 0])); UV.append(UV[-1])
    for jj in range(n_t):
        a_, b_ = (len(xs_t) - 1) * n_t + jj, (len(xs_t) - 1) * n_t + (jj + 1) % n_t
        F.append((a_, cidx, b_))
    M.ajoute(P, UV, F, TETE)
    # naseaux relevés + narines
    for cote in (1, -1):
        b0 = np.array([-3.75, 0.62, cote * 0.24])
        P, UV, F = tube(bezier(b0, b0 + np.array([-0.05, 0.12, cote * 0.05]), b0 + np.array([0.05, 0.22, cote * 0.1]),
                               b0 + np.array([0.2, 0.2, cote * 0.14]), 6), np.linspace(0.1, 0.03, 6), 8,
                        uv=uv_pastille("or", 0.8))
        M.ajoute(P, UV, F, TETE)
        P, UV, F = ellipsoide((-3.93, 0.5, cote * 0.2), (0.07, 0.06, 0.07), 8, 6, pastille="noir")
        M.ajoute(P, UV, F, TETE)
    charn = CHARNIERE
    ouv = math.radians(MACHOIRE_REPOS)
    Rm = rotz(ouv)     # rotation de la mâchoire inférieure (vers le bas, autour de Z)
    MACH = -2          # liaison : os « Machoire » (v13 : la gueule s'ouvre et MORD)
    # langue
    P, UV, F = loft([charn + Rm @ (np.array([x, 0.02, 0]) - charn) for x in np.linspace(-1.4, -3.0, 8)],
                    np.linspace(0.28, 0.14, 8), [0.07] * 8, n=10, uvf=lambda i, a, p: uv_pastille("rouge", 0.95))
    M.ajoute(P, UV, F, MACH)
    # mâchoire inférieure (ouverte) : dessus rouge (gencive), menton doré
    # (v13, vu gueule ouverte de face : une mâchoire aussi longue que le
    # museau, dessus tout rouge = une PLANCHE rouge) -> plus courte que le
    # museau, gencive rouge étroite au milieu, lèvres or, dessous crème
    xs_j = np.linspace(-0.9, -2.95, 16)
    cj, lwj, lhj = [], [], []
    for x in xs_j:
        u = (-(x + 0.9)) / 2.05
        # le menton REMONTE vers le bout (une mâchoire droite = une planche)
        cj.append(charn + Rm @ (np.array([x, -0.08 + 0.16 * u * u, 0]) - charn))
        lwj.append(0.5 - 0.24 * u)
        lhj.append(0.3 - 0.12 * u)
    axes = [(Rm @ np.array([0, 1.0, 0]), np.array([0, 0, 1.0]))] * len(cj)
    P, UV, F = loft(cj, lwj, lhj, n=20, axes=axes, ex=3.0, ventre=1.0,
                    uvf=lambda i, a, p: uv_pastille("rouge" if math.sin(a) > 0.82 else ("creme" if math.sin(a) < -0.35 else "or"),
                                                    0.5 + 0.5 * math.sin(a)))
    M.ajoute(P, UV, F, MACH)
    # crocs : rangée du haut (vers le bas), gros crocs devant ; du bas (vers le haut)
    for cote in (1, -1):
        for k, x in enumerate(np.linspace(-1.6, -3.6, 8)):
            gros = k >= 6
            ln = 0.44 if gros else 0.2
            yc, w, ht, hb, ex = profil_tete(x)
            base = np.array([x, yc - hb * 0.8, cote * (w * 0.8)])
            P, UV, F = tube([base, base + np.array([-0.02, -ln * 0.6, 0]), base + np.array([-0.05, -ln, cote * -0.02])],
                            [0.075 if gros else 0.05, 0.04, 0.008], 6, uv=uv_pastille("blanc", 0.7))
            M.ajoute(P, UV, F, TETE)
        for k, x in enumerate(np.linspace(-1.5, -2.8, 7)):
            gros = k >= 5
            ln = 0.34 if gros else 0.16
            uu = (-(x + 0.9)) / 2.05
            w = 0.5 - 0.24 * uu
            base = charn + Rm @ (np.array([x, 0.14 + 0.16 * uu * uu, cote * w * 0.78]) - charn)
            up = Rm @ np.array([0, 1.0, 0])
            P, UV, F = tube([base, base + up * ln * 0.6, base + up * ln + np.array([0.02, 0, 0])],
                            [0.065 if gros else 0.045, 0.035, 0.008], 6, uv=uv_pastille("blanc", 0.7))
            M.ajoute(P, UV, F, MACH)
    # yeux + arcades (en colère : l'arcade descend vers l'avant)
    for cote in (1, -1):
        P, UV, F = ellipsoide((-1.55, 0.68, cote * 0.55), (0.24, 0.15, 0.1), 12, 8, pastille="oeil",
                              rot=rotz(math.radians(-12)))
        M.ajoute(P, UV, F, TETE)
        P, UV, F = ellipsoide((-1.62, 0.68, cote * 0.63), (0.04, 0.12, 0.04), 8, 6, pastille="noir")
        M.ajoute(P, UV, F, TETE)
        P, UV, F = ellipsoide((-1.62, 0.64, cote * 0.645), (0.025, 0.025, 0.02), 6, 4, pastille="blanc")
        M.ajoute(P, UV, F, TETE)
        P, UV, F = ellipsoide((-1.45, 0.92, cote * 0.52), (0.62, 0.13, 0.22), 12, 8, pastille="or_fonce",
                              rot=rotz(math.radians(-22)))
        M.ajoute(P, UV, F, TETE)
    # cornes en bois de cerf (tube + une branche)
    for cote in (1, -1):
        b0 = np.array([-0.9, 0.85, cote * 0.38])
        pts = bezier(b0, b0 + np.array([0.3, 0.6, cote * 0.1]), b0 + np.array([1.2, 1.2, cote * 0.35]), b0 + np.array([2.2, 1.35, cote * 0.55]), 12)
        P, UV, F = tube(pts, np.linspace(0.15, 0.02, 12), 8, uv_h=lambda s, j: uv_pastille("or_fonce", 0.8 - 0.5 * s))
        M.ajoute(P, UV, F, TETE)
        br0 = pts[5]
        P, UV, F = tube(bezier(br0, br0 + np.array([0.1, 0.35, 0]), br0 + np.array([0.3, 0.6, cote * 0.1]), br0 + np.array([0.55, 0.8, cote * 0.12]), 7),
                        np.linspace(0.08, 0.015, 7), 6, uv_h=lambda s, j: uv_pastille("or_fonce", 0.8 - 0.5 * s))
        M.ajoute(P, UV, F, TETE)
    # moustaches : longues, du nez vers l'arrière, ondulées
    for cote in (1, -1):
        m0 = np.array([-3.7, 0.5, cote * 0.4])
        pts = bezier(m0, m0 + np.array([0.3, -0.5, cote * 1.0]), m0 + np.array([2.8, 0.9, cote * 2.2]),
                     m0 + np.array([5.5, -0.3, cote * 3.0]), 40)
        pts = pts + np.array([0, 1.0, 0]) * (0.18 * np.sin(np.linspace(0, 5 * math.pi, 40)) * np.linspace(0, 1, 40))[:, None]
        P, UV, F = tube(pts, np.linspace(0.035, 0.006, 40), 5, uv=uv_pastille("creme", 0.8))
        M.ajoute(P, UV, F, TETE)
    # crinière de FLAMMES (2e version : cônes raides = hérisson vu de face) :
    # langues aplaties, en S, qui COULENT vers l'arrière, deux couches
    rng = np.random.default_rng(4)
    for couche, (nb, ln0, col) in enumerate(((11, 2.4, "brun"), (7, 1.6, "or_fonce"))):
        for k in range(nb):
            a = math.radians(-55 + 150 * k / (nb - 1))       # autour de l'axe X, du bas vers le haut
            for cote in (1, -1):
                base = np.array([-0.4 + 0.25 * rng.random() + 0.3 * couche, 0.25 + 0.6 * math.sin(a),
                                 cote * (0.35 + 0.3 * abs(math.cos(a)))])
                rad = np.array([0, math.sin(a), cote * abs(math.cos(a))])
                d = np.array([1.0, 0, 0]) * 1.0 + rad * 0.55
                d /= np.linalg.norm(d)
                ln = ln0 * (0.8 + 0.4 * rng.random())
                ond = rad * 0.35
                pts = bezier(base, base + d * ln * 0.35 + ond, base + d * ln * 0.7 - ond, base + d * ln + ond * 1.4, 10)
                P, UV, F = tube(pts, np.linspace(0.26, 0.01, 10) * (1 - 0.25 * couche), 6, aplati=0.35,
                                plat_ref=rad, uv_h=lambda s_, j, col=col: uv_pastille(col, 0.95 - 0.8 * s_))
                M.ajoute(P, UV, F, TETE)
    # barbe (touffe sous le menton) et piquants de joue
    for k in range(4):
        base = charn + Rm @ (np.array([-2.6 + 0.25 * k, -0.35, 0.1 * (k - 1.5)]) - charn)
        pts = bezier(base, base + np.array([0.1, -0.3, 0]), base + np.array([0.4, -0.6, 0]), base + np.array([0.8, -0.8, 0.05 * k]), 7)
        P, UV, F = tube(pts, np.linspace(0.1, 0.01, 7), 6, uv_h=lambda s, j: uv_pastille("brun", 0.9 - 0.8 * s))
        M.ajoute(P, UV, F, MACH)
    for cote in (1, -1):
        for k in range(3):
            base = np.array([-0.9 + 0.25 * k, -0.2, cote * 0.62])
            pts = [base, base + np.array([0.35, -0.2 - 0.1 * k, cote * 0.25]), base + np.array([0.75, -0.3 - 0.15 * k, cote * 0.45])]
            P, UV, F = tube(pts, [0.11, 0.06, 0.01], 6, uv=uv_pastille("or_fonce", 0.5))
            M.ajoute(P, UV, F, TETE)
    return M


def normales(P, F):
    P = np.asarray(P)
    N = np.zeros_like(P)
    tri = P[np.asarray(F)]
    n = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
    for k in range(3):
        np.add.at(N, np.asarray(F)[:, k], n)
    return N / (np.linalg.norm(N, axis=1, keepdims=True) + 1e-12)


def os_colonne():
    return [L * i / (NB - 1) for i in range(NB)]


def poids(M):
    """os 0 = Tete (rigide), os 1..NB = colonne à x_i, os NB+1 = Machoire
    (rigide) ; 2 influences max."""
    xs = os_colonne()
    idx, w = [], []
    for b in M.B:
        if b == -1:
            idx.append([0, 0, 0, 0]); w.append([1, 0, 0, 0]); continue
        if b == -2:
            idx.append([NB + 1, 0, 0, 0]); w.append([1, 0, 0, 0]); continue
        x = min(max(b, 0.0), L)
        f = x / L * (NB - 1)
        i0 = int(min(NB - 2, math.floor(f)))
        u = f - i0
        if x < 0.35:            # le cou suit la tête
            k = x / 0.35
            idx.append([0, 1, 0, 0]); w.append([1 - k, k, 0, 0]); continue
        idx.append([1 + i0, 2 + i0, 0, 0]); w.append([1 - u, u, 0, 0])
    return idx, w


def atlas(chemin):
    """Texture DESSINÉE (v13) : bande du corps + pastilles à deux tons.

    v2 : écailles peintes en VOLUME (dégradés) -> une statue d'or (Milan :
    VFX 2-4/10). v13, d'après le dragon d'or du film (d514ee70) et Dragon
    Ball Rage : aplats francs (flanc clair, bas de flanc à l'ombre, arête
    dorsale brun-orange), ÉCAILLES en TRAIT d'encre brun (arcs en U ouverts
    vers la tête, pas de relief), plaques de ventre crème cernées de brun,
    quelques reflets clairs en trait. Dessinée à 2x puis réduite (trait net,
    bords lissés)."""
    S = 2
    W = H = ATLAS * S
    im = Image.new("RGB", (W, H), (255, 206, 64))
    d = ImageDraw.Draw(im)
    hb = int(0.78 * H)     # hauteur de la bande du corps (y = angle autour de la colonne)
    ENCRE = (86, 34, 8)
    CLAIR, OMBRE, ARETE = (255, 208, 66), (232, 138, 28), (192, 86, 18)
    ventre = (0.655, 0.845)

    def zone(a):
        a = a % 1.0
        if 0.19 < a < 0.31:
            return ARETE
        if ventre[0] <= a <= ventre[1]:
            return None
        if 0.5 < a < ventre[0] or a > ventre[1] + 0.0:
            return OMBRE
        return CLAIR
    for yy in range(hb):
        c = zone(yy / hb)
        if c:
            d.line([(0, yy), (W, yy)], fill=c)
    # écailles en TRAIT : rangées décalées, arc en U (bord libre vers la queue)
    # (1er essai 34 x 12, arcs de 160° : des « ) » isolées, pas des écailles)
    # -> moins d'écailles, plus grandes, arcs de 180° qui se touchent : un
    # feston continu d'une rangée à l'autre
    n_long, n_tour = 26, 8
    pas_x, pas_y = W / n_long, hb / n_tour
    for i in range(-1, n_long + 2):
        for j in range(n_tour):
            a = ((j + 0.5) / n_tour) % 1.0
            if zone(a) in (None, ARETE):
                continue
            x = (i + 0.5 * (j % 2)) * pas_x
            y = (j + 0.5) * pas_y
            rx, ry = pas_x * 0.55, pas_y * 0.56
            d.arc([x - rx, y - ry, x + rx, y + ry], -90, 90, fill=ENCRE, width=5 * S)
            if zone(a) == CLAIR and (i + j) % 3 == 0:     # reflet en trait, pas partout
                d.arc([x - rx * 0.62, y - ry * 0.55, x + rx * 0.62, y + ry * 0.55], -60, -15,
                      fill=(255, 246, 180), width=3 * S)
    # ventre et arête PAR-DESSUS les écailles (elles débordaient sur l'arête)
    # ventre : plaques crème, moitié basse de chaque plaque à l'ombre, traits bruns
    y0, y1 = int(ventre[0] * hb), int(ventre[1] * hb)
    d.rectangle([0, y0, W, y1], fill=(255, 240, 190))
    ym = int((ventre[0] + 0.62 * (ventre[1] - ventre[0])) * hb)
    d.rectangle([0, ym, W, y1], fill=(240, 196, 120))
    n_pl = 44
    for i in range(n_pl + 1):
        x = i * W / n_pl
        d.line([(x, y0), (x + 10 * S, y1)], fill=ENCRE, width=5 * S)
    d.rectangle([0, y0 - 5 * S, W, y0 + 3 * S], fill=ENCRE)
    d.rectangle([0, y1 - 3 * S, W, y1 + 5 * S], fill=ENCRE)
    # arête dorsale : bande sombre + trait central
    yd = int(0.25 * hb)
    d.rectangle([0, int(0.19 * hb), W, int(0.31 * hb)], fill=ARETE)
    d.rectangle([0, yd - 6 * S, W, yd + 6 * S], fill=(120, 44, 10))
    for yb in (int(0.19 * hb), int(0.31 * hb)):
        d.rectangle([0, yb - 3 * S, W, yb + 3 * S], fill=ENCRE)
    # pastilles à DEUX TONS (clair au-dessus de h = 0,45, ombre dessous)
    n = len(NOMS)
    ys = int((0.80 + 0.18 * 0.55) * H)
    for k, nom in enumerate(NOMS):
        haut, bas = PASTILLES[nom]
        x0, x1 = int(k * W / n), int((k + 1) * W / n)
        d.rectangle([x0, hb, x1, ys], fill=haut)
        d.rectangle([x0, ys, x1, H], fill=bas)
    im = im.resize((ATLAS, ATLAS), Image.LANCZOS)
    im.save(chemin)


TETE_ECHELLE = 1.35   # Shenron : la tête domine le cou (1er rendu : tête trop petite pour le corps)


def main(dossier=HERE):
    M = construire()
    P = np.asarray(M.P, float)
    tete = np.array([b in (-1, -2) for b in M.B])
    pivot = np.array([0.3, 0.1, 0.0])
    P[tete] = pivot + (P[tete] - pivot) * TETE_ECHELLE
    charn = pivot + (CHARNIERE - pivot) * TETE_ECHELLE
    F = np.asarray(M.F, int)
    N = normales(P, F)
    idx, w = poids(M)
    atlas(os.path.join(dossier, "dragon_atlas.png"))
    data = {"longueur": L, "os_x": os_colonne(), "positions": np.round(P, 4).ravel().tolist(),
            "normales": np.round(N, 3).ravel().tolist(), "uv": np.round(np.asarray(M.UV), 4).ravel().tolist(),
            "indices": F.ravel().tolist(), "os_indices": np.asarray(idx).ravel().tolist(),
            "os_poids": np.round(np.asarray(w), 4).ravel().tolist(), "triangles": int(len(F)),
            # os NB+1 : mâchoire, charnière (repère du modèle), angle modélisé
            "machoire": {"charniere": np.round(charn, 4).tolist(), "repos": MACHOIRE_REPOS}}
    json.dump(data, open(os.path.join(dossier, "dragon.json"), "w"))
    print("dragon :", len(P), "sommets,", len(F), "triangles (limite Roblox 20 000)")
    return M, data


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else HERE)
