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
    # (v13b : l'ordre compte, une mèche passe d'une pastille à la VOISINE ;
    # entre deux pastilles éloignées, le mélange traversait toutes les autres
    # -> rayures rouge/blanc dans la crinière)
    "flamme": ((255, 120, 24), (196, 52, 12)),
    "creme": ((255, 244, 200), (238, 192, 116)),
    "brun": ((160, 58, 14), (96, 30, 6)),
    "blanc": ((255, 255, 250), (226, 220, 206)),
    "rouge": ((196, 30, 22), (118, 10, 10)),
    # (v13 : œil CYAN à pupille ronde -> « ça casse tout, c'est moche »,
    # Milan ; v13b 1er essai blanc cerclé de noir = globuleux) -> or
    # incandescent, fente fine, sous l'arcade
    "oeil": ((255, 226, 80), (255, 132, 16)),
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


CHARNIERE = np.array([-0.8, -0.12, 0])  # charnière de la mâchoire (repère du modèle, avant l'échelle de tête)
MACHOIRE_REPOS = 20.0                    # angle d'ouverture de la mâchoire MODÉLISÉE (degrés) ; os à l'identité


def construire():
    M = Piece()
    TETE = -1   # liaison : os de tête (rigide)

    # ------------------------------------------------------------ CORPS
    n_anneaux = 90
    xs = np.linspace(-0.2, L, n_anneaux)

    def rayon(x):
        u = max(0.0, x / L)
        return 0.74 + 0.22 * math.sin(math.pi * min(1, u * 1.6)) * (1 - u) - 0.66 * u ** 1.5 if u < 1 else 0.06

    R = [max(0.07, rayon(x)) for x in xs]

    def uv_corps(i, a, p):
        return (xs[i] / L, 0.56 * ((a / (2 * math.pi)) % 1.0))
    # (section plus RONDE qu'en v13 : ex 2,6 -> un tube un peu carré, « cubique »)
    P, UV, F = loft([(x, 0, 0) for x in xs], R, [r * 0.95 for r in R], n=20, ex=2.2, uvf=uv_corps)
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
                P, UV, F = tube(bezier(g0, g0 + (g1 - g0) * 0.5, g1, g2, 5), np.linspace(0.07, 0.015, 5), 4,
                                uv=uv_pastille("blanc", 0.6))
                M.ajoute(P, UV, F, x0)

    # touffe de flammes au bout de la queue
    for k in range(7):
        a = -0.9 + 1.8 * k / 6
        base = np.array([L - 0.15, 0, 0])
        dirn = np.array([math.cos(a * 0.6), math.sin(a), 0.35 * math.sin(3 * a)])
        pts = bezier(base, base + dirn * 0.5, base + dirn * 1.0 + np.array([0.5, 0.15, 0]), base + dirn * 1.5 + np.array([0.9, 0.35, 0]), 8)
        P, UV, F = tube(pts, np.linspace(0.14, 0.01, 8), 5, uv_h=lambda s, j: uv_pastille("flamme", 1 - s))
        M.ajoute(P, UV, F, L)

    # ------------------------------------------------------------ TÊTE
    # v13b (Milan : « les yeux cassent le truc, c'est moche ; trop cubique,
    # pas assez travaillé ») : 2e tête (v12-v13) = un museau en PLANCHE
    # (sections presque carrées, ex 3-3,4, 4,5 studs de long), œil rond cyan
    # à pupille = jouet, crinière de lames plates en hérisson. Ici, d'après
    # le dragon d'or du film (d514ee70) : crâne haut et large, museau PLUS
    # COURT qui s'affine, bosse du nez, lèvre supérieure renflée, sections
    # ARRONDIES (ex 2,1-2,4), arcades lourdes en V (colère), œil ÉTROIT et
    # incandescent enfoncé sous l'arcade, pommettes, crinière de FLAMMES en
    # mèches à deux tons ; la tête a sa propre bande de texture (plaques du
    # nez, écailles du crâne, ligne des lèvres à l'encre).
    X0, X1 = 0.4, -3.28                      # du cou au bout du nez

    def profil_tete(x):
        """x de X0 (cou) à X1 (nez) -> (haut, bas, demi-largeur, exposant)."""
        # (1er essai : museau plat et large = un bec de canard) -> plus HAUT que
        # large, bosse du nez, lèvre renflée, plus court
        k = [(0.4, 0.78, -0.78, 0.74, 2.1), (-0.2, 0.98, -0.72, 0.8, 2.1), (-0.85, 0.94, -0.52, 0.72, 2.2),
             (-1.35, 0.72, -0.38, 0.54, 2.3), (-1.95, 0.6, -0.3, 0.42, 2.3), (-2.5, 0.68, -0.28, 0.4, 2.3),
             (-2.9, 0.6, -0.3, 0.37, 2.2), (-3.15, 0.38, -0.25, 0.28, 2.1), (-3.28, 0.06, -0.06, 0.08, 2.0)]
        for a_, b_ in zip(k, k[1:]):
            if b_[0] <= x <= a_[0]:
                u = (a_[0] - x) / (a_[0] - b_[0])
                u = u * u * (3 - 2 * u)            # raccord doux entre les clés (pas de cassure)
                return tuple(a_[m] + (b_[m] - a_[m]) * u for m in range(1, 5))
        return k[-1][1:]

    def uv_tete(x, a):
        """bande de la tête dans l'atlas : U le long (cou -> nez), V = angle."""
        return ((X0 - x) / (X0 - X1), 1 - (0.56 + 0.22 * ((a / (2 * math.pi)) % 1.0)))
    xs_t = np.linspace(X0, X1, 50)
    n_t = 32
    P, UV = [], []
    for x in xs_t:
        ht, hb_, w, ex = profil_tete(x)
        yc = (ht + hb_) / 2
        hh = (ht - hb_) / 2
        for jj in range(n_t):
            a_ = 2 * math.pi * jj / n_t
            c, s_ = math.cos(a_), math.sin(a_)
            y = math.copysign(abs(s_) ** (2 / ex), s_)
            z = math.copysign(abs(c) ** (2 / ex), c)
            # arête du nez : le dessus du museau se pince (pas un dos plat)
            if y > 0 and x < -1.3:
                z *= 1 - 0.22 * y ** 2
            P.append(np.array([x, yc + y * hh, z * w]))
            UV.append(uv_tete(x, a_))
    F = grille_faces(len(xs_t), n_t)
    cidx = len(P); P.append(np.array([X1 - 0.02, 0.0, 0])); UV.append(UV[-1])
    for jj in range(n_t):
        a_, b_ = (len(xs_t) - 1) * n_t + jj, (len(xs_t) - 1) * n_t + (jj + 1) % n_t
        F.append((a_, cidx, b_))
    M.ajoute(P, UV, F, TETE)

    def surface_haut(x, z=0.0):
        ht, hb_, w, ex = profil_tete(x)
        return (ht if abs(z) < 1e-6 else (ht + hb_) / 2 + (ht - hb_) / 2 * max(0.0, 1 - abs(z / w) ** ex) ** (1 / ex))
    # naseaux : bosses au bout du museau + narines sombres
    for cote in (1, -1):
        # (1er essai : bosses hautes sur le dessus = deux OREILLES d'ourson vues
        # de face) -> naseaux bas et plats, sur les côtés du bout du museau,
        # qui filent vers l'arrière
        b0 = np.array([-2.95, surface_haut(-2.95) - 0.12, cote * 0.24])
        P, UV, F = tube(bezier(b0, b0 + np.array([0.1, 0.05, cote * 0.05]), b0 + np.array([0.3, 0.07, cote * 0.08]),
                               b0 + np.array([0.55, 0.02, cote * 0.1]), 8), np.linspace(0.07, 0.015, 8), 8, aplati=0.6,
                        uv=uv_pastille("or_fonce", 0.85))
        M.ajoute(P, UV, F, TETE)
        P, UV, F = ellipsoide((-3.08, 0.36, cote * 0.17), (0.06, 0.04, 0.05), 10, 6, pastille="noir")
        M.ajoute(P, UV, F, TETE)
    charn = CHARNIERE
    ouv = math.radians(MACHOIRE_REPOS)
    Rm = rotz(ouv)     # rotation de la mâchoire inférieure (vers le bas, autour de Z)
    MACH = -2          # liaison : os « Machoire » (v13 : la gueule s'ouvre et MORD)
    XJ1 = -2.85        # bout du menton (plus court que le museau)
    # langue
    P, UV, F = loft([charn + Rm @ (np.array([x, -0.02, 0]) - charn) for x in np.linspace(-1.0, -2.6, 8)],
                    np.linspace(0.26, 0.12, 8), [0.06] * 8, n=12, uvf=lambda i, a, p: uv_pastille("rouge", 0.95))
    M.ajoute(P, UV, F, MACH)
    # mâchoire inférieure : arrondie, menton qui remonte, gencive rouge étroite
    xs_j = np.linspace(charn[0], XJ1, 20)
    cj, lwj, lhj = [], [], []
    for x in xs_j:
        u = (charn[0] - x) / (charn[0] - XJ1)
        cj.append(charn + Rm @ (np.array([x, -0.2 + 0.14 * u * u, 0]) - charn))
        # (1er essai : 0,24 de haut partout = un BÂTON) -> profonde à la
        # charnière, fine au menton
        lwj.append(0.54 - 0.32 * u ** 1.2)
        lhj.append(0.36 - 0.22 * u ** 0.8)
    axes = [(Rm @ np.array([0, 1.0, 0]), np.array([0, 0, 1.0]))] * len(cj)
    P, UV, F = loft(cj, lwj, lhj, n=24, axes=axes, ex=2.3, ventre=1.0,
                    uvf=lambda i, a, p: uv_pastille("rouge" if math.sin(a) > 0.8 else ("creme" if math.sin(a) < -0.3 else "or"),
                                                    0.5 + 0.5 * math.sin(a)))
    M.ajoute(P, UV, F, MACH)
    # crocs du haut (vers le bas), gros crocs devant ; du bas (vers le haut)
    for cote in (1, -1):
        for k, x in enumerate(np.linspace(-1.35, -3.0, 9)):
            gros = k in (6, 7)
            ln = 0.46 if gros else 0.2
            ht, hb_, w, ex = profil_tete(x)
            base = np.array([x, hb_ + 0.04, cote * w * 0.82])
            P, UV, F = tube([base, base + np.array([-0.02, -ln * 0.6, cote * -0.01]), base + np.array([-0.06, -ln, cote * -0.03])],
                            [0.08 if gros else 0.05, 0.045, 0.008], 6, uv=uv_pastille("blanc", 0.7))
            M.ajoute(P, UV, F, TETE)
        for k, x in enumerate(np.linspace(-1.2, -2.65, 8)):
            gros = k in (5, 6)
            ln = 0.36 if gros else 0.16
            u = (charn[0] - x) / (charn[0] - XJ1)
            w = 0.54 - 0.32 * u ** 1.2
            base = charn + Rm @ (np.array([x, -0.2 + 0.14 * u * u + (0.36 - 0.22 * u ** 0.8) * 0.9, cote * w * 0.78]) - charn)
            up = Rm @ np.array([0, 1.0, 0])
            P, UV, F = tube([base, base + up * ln * 0.6, base + up * ln + np.array([0.02, 0, 0])],
                            [0.07 if gros else 0.045, 0.035, 0.008], 6, uv=uv_pastille("blanc", 0.7))
            M.ajoute(P, UV, F, MACH)
    # ARCADES lourdes en V (colère) qui débordent au-dessus des yeux, finies
    # par une épine vers l'arrière ; ORBITE sombre ; ŒIL étroit, incandescent
    for cote in (1, -1):
        arc = bezier(np.array([-1.45, 0.66, cote * 0.34]), np.array([-1.05, 0.9, cote * 0.52]),
                     np.array([-0.55, 1.02, cote * 0.62]), np.array([0.05, 1.12, cote * 0.66]), 12)
        # (1er essai : un tube de rayon constant = un TUYAU posé sur la tête)
        # -> fuseau qui naît de la peau et s'y fond (rayon 0 aux deux bouts)
        fus = 0.03 + 0.19 * np.sin(np.pi * np.linspace(0.08, 0.92, 12)) ** 0.8
        P, UV, F = tube(arc - np.array([0, 0.06, 0]), fus, 10, aplati=0.5, plat_ref=np.array([0, 0, 1.0]),
                        uv_h=lambda s_, j: uv_pastille("or_fonce", 0.9 - 0.4 * s_))
        M.ajoute(P, UV, F, TETE)
        pe = arc[-1]
        P, UV, F = tube(bezier(pe, pe + np.array([0.3, 0.1, cote * 0.05]), pe + np.array([0.6, 0.25, cote * 0.12]),
                               pe + np.array([0.95, 0.42, cote * 0.18]), 8), np.linspace(0.12, 0.01, 8), 8,
                        uv_h=lambda s_, j: uv_pastille("or_fonce", 0.8 - 0.5 * s_))
        M.ajoute(P, UV, F, TETE)
        orbite = rotz(math.radians(-18))
        P, UV, F = ellipsoide((-0.99, 0.66, cote * 0.645), (0.29, 0.095, 0.06), 16, 8, pastille="brun", rot=orbite)
        M.ajoute(P, UV, F, TETE)
        P, UV, F = ellipsoide((-1.0, 0.665, cote * 0.672), (0.25, 0.07, 0.05), 16, 8, pastille="oeil", rot=orbite)
        M.ajoute(P, UV, F, TETE)
        P, UV, F = ellipsoide((-1.0, 0.665, cote * 0.708), (0.018, 0.06, 0.02), 6, 6, pastille="noir", rot=orbite)
        M.ajoute(P, UV, F, TETE)
        # pommette : arête sous l'œil qui file vers la joue
        pom = bezier(np.array([-1.5, 0.36, cote * 0.52]), np.array([-1.0, 0.36, cote * 0.68]),
                     np.array([-0.5, 0.3, cote * 0.74]), np.array([0.05, 0.18, cote * 0.74]), 10)
        P, UV, F = tube(pom, 0.02 + 0.09 * np.sin(np.pi * np.linspace(0.1, 0.9, 10)), 8, aplati=0.6, plat_ref=np.array([0, 0, 1.0]),
                        uv_h=lambda s_, j: uv_pastille("or_fonce", 0.7))
        M.ajoute(P, UV, F, TETE)
    # cornes en bois de cerf (tube + deux branches)
    for cote in (1, -1):
        b0 = np.array([-0.3, 0.8, cote * 0.4])
        pts = bezier(b0, b0 + np.array([0.3, 0.6, cote * 0.1]), b0 + np.array([1.2, 1.15, cote * 0.35]),
                     b0 + np.array([2.3, 1.3, cote * 0.55]), 14)
        P, UV, F = tube(pts, np.linspace(0.15, 0.02, 14), 10, uv_h=lambda s, j: uv_pastille("or_fonce", 0.85 - 0.5 * s))
        M.ajoute(P, UV, F, TETE)
        for kb, (i_b, dirb) in enumerate(((5, (0.25, 0.75, 0.05)), (9, (0.45, 0.55, 0.12)))):
            br0 = pts[i_b]
            d_ = np.array(dirb) * (0.9 - 0.2 * kb)
            P, UV, F = tube(bezier(br0, br0 + d_ * 0.35, br0 + d_ * 0.7 + np.array([0.05, 0.05, cote * 0.05]),
                                   br0 + d_ + np.array([0.12, 0.08, cote * 0.1]), 7),
                            np.linspace(0.075, 0.012, 7), 8, uv_h=lambda s, j: uv_pastille("or_fonce", 0.8 - 0.5 * s))
            M.ajoute(P, UV, F, TETE)
    # moustaches : de la lèvre vers l'arrière, ondulées
    for cote in (1, -1):
        # (1er essai : elles partaient à hauteur des yeux et BARRAIENT le visage
        # d'un trait blanc) -> de la lèvre, vers le bas et l'extérieur d'abord
        m0 = np.array([-2.8, 0.08, cote * 0.4])
        pts = bezier(m0, m0 + np.array([0.3, -0.25, cote * 1.4]), m0 + np.array([2.4, -0.4, cote * 2.8]),
                     m0 + np.array([5.2, -1.2, cote * 3.4]), 40)
        pts = pts + np.array([0, 1.0, 0]) * (0.18 * np.sin(np.linspace(0, 5 * math.pi, 40)) * np.linspace(0, 1, 40))[:, None]
        P, UV, F = tube(pts, np.linspace(0.04, 0.006, 40), 5, uv=uv_pastille("creme", 0.8))
        M.ajoute(P, UV, F, TETE)
    # crinière de FLAMMES : mèches aplaties en S, trois couches, DEUX TONS
    # le long de la mèche (racine or, pointe flamme) ; plus fines et plus
    # nombreuses que les lames brunes v12 (un hérisson de carton)
    rng = np.random.default_rng(4)
    for couche, (nb, ln0, rac, pointe) in enumerate(((13, 2.5, "or_fonce", "flamme"), (10, 1.9, "or", "flamme"),
                                                     (7, 1.3, "or", "or_fonce"))):
        for k in range(nb):
            a_ = math.radians(-50 + 145 * k / (nb - 1))
            for cote in (1, -1):
                base = np.array([-0.1 + 0.25 * rng.random() + 0.3 * couche, 0.2 + 0.72 * math.sin(a_),
                                 cote * (0.4 + 0.34 * abs(math.cos(a_)))])
                rad = np.array([0, math.sin(a_), cote * abs(math.cos(a_))])
                d = np.array([1.0, 0, 0]) * 1.0 + rad * 0.5
                d /= np.linalg.norm(d)
                ln = ln0 * (0.75 + 0.5 * rng.random())
                ond = rad * 0.3
                boucle = np.array([0, 0.25, 0]) * (1 if k % 2 else -0.4)
                pts = bezier(base, base + d * ln * 0.35 + ond, base + d * ln * 0.7 - ond, base + d * ln + ond * 1.2 + boucle, 9)
                P, UV, F = tube(pts, np.linspace(0.2, 0.008, 9) * (1 - 0.2 * couche), 4, aplati=0.3, plat_ref=rad,
                                uv_h=lambda s_, j, r=rac, pt=pointe: uv_pastille(r if s_ < 0.45 else pt, 0.95 - 0.6 * s_))
                M.ajoute(P, UV, F, TETE)
    # barbe (flammes sous le menton) et piquants de joue
    for k in range(5):
        base = charn + Rm @ (np.array([-2.4 + 0.22 * k, -0.4, 0.1 * (k - 2)]) - charn)
        pts = bezier(base, base + np.array([0.1, -0.3, 0]), base + np.array([0.4, -0.6, 0]), base + np.array([0.8, -0.85, 0.05 * k]), 8)
        P, UV, F = tube(pts, np.linspace(0.1, 0.01, 8), 6, aplati=0.4, plat_ref=np.array([0, 0, 1.0]),
                        uv_h=lambda s, j: uv_pastille("or_fonce" if s < 0.5 else "flamme", 0.9 - 0.6 * s))
        M.ajoute(P, UV, F, MACH)
    for cote in (1, -1):
        for k in range(3):
            base = np.array([-0.55 + 0.28 * k, -0.25, cote * 0.66])
            pts = [base, base + np.array([0.35, -0.2 - 0.1 * k, cote * 0.25]), base + np.array([0.8, -0.32 - 0.15 * k, cote * 0.45])]
            P, UV, F = tube(pts, [0.11, 0.06, 0.01], 8, uv=uv_pastille("or_fonce", 0.5))
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
    hb = int(0.56 * H)     # hauteur de la bande du corps (y = angle autour de la colonne)
    ht0, ht1 = hb, int(0.78 * H)   # v13b : bande de la TÊTE (U = du cou au nez, V = angle)
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
    # ---- bande de la TÊTE : aplats, palais rouge, lèvres, plaques du nez,
    # écailles du crâne, rides de joue, tout au trait d'encre
    def ya(a):
        return ht0 + a * (ht1 - ht0)
    for yy in range(ht0, ht1):
        a = (yy - ht0) / (ht1 - ht0)
        c = zone(a) if not (0.19 < a < 0.31) else CLAIR
        d.line([(0, yy), (W, yy)], fill=c or (255, 236, 176))
    xu = lambda u: u * W  # noqa: E731
    # dessous : gorge crème (u < 0,3), palais rouge sombre au-delà, lèvres
    d.rectangle([xu(0.3), ya(0.62), W, ya(0.88)], fill=(150, 20, 16))
    for yl in (0.62, 0.88):
        d.rectangle([xu(0.3), ya(yl) - 4 * S, W, ya(yl) + 4 * S], fill=ENCRE)
    # plaques du nez sur l'arête (u 0,34-0,92), cernées
    d.rectangle([xu(0.34), ya(0.205), xu(0.92), ya(0.295)], fill=(246, 168, 44))
    for i in range(12):
        x = xu(0.34 + 0.58 * i / 11)
        d.line([(x, ya(0.205)), (x + 6 * S, ya(0.295))], fill=ENCRE, width=4 * S)
    for yl in (0.205, 0.295):
        d.line([(xu(0.34), ya(yl)), (xu(0.92), ya(yl))], fill=ENCRE, width=4 * S)
    # écailles du crâne (u < 0,3), petites, en festons
    for i in range(10):
        for j in range(8):
            a = (j + 0.5) / 8
            if zone(a) is None:
                continue
            x = xu(0.02 + 0.028 * i + 0.014 * (j % 2))
            y = ya(a)
            rx, ry = xu(0.016), (ht1 - ht0) * 0.07
            d.arc([x - rx, y - ry, x + rx, y + ry], -90, 90, fill=ENCRE, width=3 * S)
    # rides de joue et de museau (traits courts, deux côtés)
    for a0 in (0.07, 0.43):
        for i in range(3):
            u0 = 0.36 + 0.07 * i
            d.arc([xu(u0), ya(a0) - 30 * S, xu(u0 + 0.12), ya(a0) + 30 * S], 200, 320, fill=ENCRE, width=3 * S)
    # pastilles à DEUX TONS (clair au-dessus de h = 0,45, ombre dessous)
    n = len(NOMS)
    ys = int((0.80 + 0.18 * 0.55) * H)
    for k, nom in enumerate(NOMS):
        haut, bas = PASTILLES[nom]
        x0, x1 = int(k * W / n), int((k + 1) * W / n)
        d.rectangle([x0, ht1, x1, ys], fill=haut)
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
