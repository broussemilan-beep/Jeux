"""
Textures DESSINÉES pour meshes (idée de Milan, 2026-09-25 : « les VFX qui
complètent les animations, on dirait c'est dessiné, et sûrement parce que
ça passe par des meshes 3D »). Confirmé par ses refs (tornade de feu
0f85f7a1 : croissants en spirale ; jaillissements 8005ceb1 : lames ;
Suiryu : trait peint sur un volume ; pilier : mesh + couleurs peintes).

Le principe : la FORME vient d'un mesh simple (ruban, arc, lame, dans
`meshes.py`), le DESSIN vient d'une texture peinte à bord NET (aplats,
cœur blanc, bord sombre, pas de dégradé mou) posée dessus, sans lumière
(Neon / LightEmission). L'animation vient :
- de la transformation du mesh (grossit vite, tourne) jouée en « 2 »
  (cadence 12 i/s, `cadence` dans la couche mesh) : ça saute comme un
  dessin animé au lieu de glisser comme de la 3D ;
- d'une suite d'images qui s'ÉRODENT (le trait se mange depuis la queue ou
  la base, bord déchiqueté) : `images` dans la couche mesh, qui change la
  texture du mesh image par image (Roblox : TextureId, comme les flipbooks
  de meshes de Pew, DevForum partie 3).

Convention UV (celle de `meshes.py`) : U = le long du trait (0 = queue ou
base, 1 = tête ou pointe), V = en travers. Les textures sont symétriques en
V (le sens de V ne change rien entre moteurs).

Textures « à teinter » : blanc au cœur, gris plus sombres vers le bord ;
la couleur de la couche teinte le tout, le blanc devient la couleur la plus
claire. Les traits d'encre (griffures, veines) sont NOIRS : la teinte ne
les éclaircit pas, ils restent de l'encre.
"""
import math

import numpy as np
from PIL import Image

from formes import bruit, lisse

W, H = 512, 256          # traits : U en largeur, V en hauteur
N_EROSION = 8            # images par érosion


def _rgba(gris, alpha):
    g = (np.clip(gris, 0, 1) * 255).astype(np.uint8)
    a = (np.clip(alpha, 0, 1) * 255).astype(np.uint8)
    return Image.fromarray(np.dstack([g, g, g, a]), "RGBA")


def _uv(w=W, h=H):
    v, u = np.mgrid[0:h, 0:w].astype(np.float32)
    return (u + 0.5) / w, (v + 0.5) / h


def _bruit_rect(w, h, echelle, graine):
    b = bruit(max(w, h), echelle, graine, octaves=3)
    return b[:h, :w]


def _tons(d):
    """d = distance au centre du trait / demi-largeur (0 au cœur, 1 au bord).
    Aplats NETS : cœur blanc, clair, moyen, bord sombre."""
    g = np.where(d < 0.38, 1.0, np.where(d < 0.66, 0.86, np.where(d < 0.88, 0.62, 0.32)))
    return g


def trait(k=0, n=N_EROSION, graine=3):
    """Trait de pinceau le long de U : queue fine et déchiquetée (U=0),
    ventre épais vers U=0,7, tête pointue (U=1). Image k : érosion depuis la
    queue (k=0 entier, k=n-1 presque disparu)."""
    u, v = _uv()
    b = _bruit_rect(W, H, 6, graine)
    prof = np.sin(math.pi * np.clip(u, 0, 1) ** 0.75) ** 0.9            # 0 aux bouts, 1 au ventre
    # bord de PINCEAU : lisse, avec quelques cassures (1er essai : une
    # ondulation régulière faisait une feuille, pas un coup de pinceau)
    dents = 1 + 0.07 * np.sin(u * 2 * math.pi * 2.5 + 4 * b) - 0.10 * np.clip(b - 0.62, 0, 1) * 4
    demi = 0.44 * prof * dents
    d = np.abs(v - 0.5) / np.maximum(demi, 1e-4)
    forme = lisse((np.abs(v - 0.5) - demi) * H, 1.2)
    # érosion : la queue se mange, bord déchiqueté par le bruit
    seuil = (k / max(1, n - 1)) * 0.92
    front = u + 0.18 * (b - 0.5) - seuil
    ero = lisse(-front * W, 1.5)
    return _rgba(_tons(d), forme * ero)


def lame(k=0, n=N_EROSION, graine=11):
    """Lame / langue de flamme le long de U : base large (U=0), pointe fine
    (U=1) avec deux encoches en dents de scie, bout SOMBRE. Image k : la
    base se détache et la lame se consume vers la pointe."""
    u, v = _uv()
    b = _bruit_rect(W, H, 5, graine)
    # langue qui s'AFFINE jusqu'à une pointe et se courbe (1er essai : une
    # forme d'obus, large jusqu'au bout)
    vc = 0.5 + 0.10 * np.sin(math.pi * u * 1.3)
    demi = 0.42 * (1 - u) ** 1.05
    scie = 0.07 * np.maximum(0, np.sin(u * 2 * math.pi * 2.2 + 0.6)) * (u > 0.2) * (1 - u)
    haut = (v - vc) < 0
    demi_c = demi + np.where(haut, scie, 0)          # encoches d'un seul côté
    d = np.abs(v - vc) / np.maximum(demi_c, 1e-4)
    forme = lisse((np.abs(v - vc) - demi_c) * H, 1.2)
    g = _tons(d)
    g = np.where(u > 0.84, np.minimum(g, 0.30), g)                        # le bout est sombre
    seuil = (k / max(1, n - 1)) * 0.9
    front = u + 0.2 * (b - 0.5) - seuil
    ero = lisse(-front * W, 1.5)
    return _rgba(g, forme * ero)


def griffure(n=512, graine=5):
    """Griffures d'ENCRE : 3 arcs noirs effilés, épaisseurs inégales (les
    traits noirs plantés dans l'effet de 8005ceb1)."""
    y, x = np.mgrid[0:n, 0:n].astype(np.float32)
    x, y = (x + 0.5) / n * 2 - 1, (y + 0.5) / n * 2 - 1
    rng = np.random.default_rng(graine)
    a = np.zeros_like(x)
    for i in range(3):
        cx, cy, r = rng.uniform(-0.15, 0.15), 1.4 + 0.2 * i, 1.3
        ang = np.arctan2(y - cy, x - cx)
        t = np.clip((ang + math.pi / 2 + 0.75) / 1.5, 0, 1)              # position le long de l'arc
        ep = (0.03 + 0.018 * (2 - i)) * np.maximum(0.0, np.sin(math.pi * t)) ** 0.7
        d = np.abs(np.hypot(x - cx, y - cy) - r) - ep
        d = np.where((t <= 0.001) | (t >= 0.999), 1.0, d)
        a = np.maximum(a, lisse(d * n, 1.2))
    return _rgba(np.zeros_like(a), a)


def veines(n=512, graine=9):
    """Veines d'encre en étoile (impact sombre 22c8d49c) : branches noires qui
    partent du centre et se ramifient, à poser au sol ou face caméra."""
    y, x = np.mgrid[0:n, 0:n].astype(np.float32)
    x, y = (x + 0.5) / n * 2 - 1, (y + 0.5) / n * 2 - 1
    r, ang = np.hypot(x, y), np.arctan2(y, x)
    rng = np.random.default_rng(graine)
    a = np.zeros_like(x)
    for i in range(11):
        a0 = rng.uniform(-math.pi, math.pi)
        long_ = rng.uniform(0.55, 0.95)
        courbe = rng.uniform(-0.5, 0.5)
        da = np.angle(np.exp(1j * (ang - a0 - courbe * r)))
        ep = 0.06 * np.clip(1 - r / long_, 0, 1) ** 1.3
        d = np.abs(da) * r - ep
        d = np.where(r > long_, 1.0, d)
        a = np.maximum(a, lisse(d * n, 1.0))
        # une branche
        a1 = a0 + rng.choice([-1, 1]) * 0.35
        r0 = long_ * 0.45
        da1 = np.angle(np.exp(1j * (ang - a1)))
        ep1 = 0.03 * np.clip(1 - (r - r0) / (long_ * 0.5), 0, 1)
        d1 = np.abs(da1) * r - ep1
        d1 = np.where((r < r0) | (r > r0 + long_ * 0.5), 1.0, d1)
        a = np.maximum(a, lisse(d1 * n, 1.0))
    a = np.maximum(a, lisse((r - 0.08) * n, 2.0))                            # tache au centre
    return _rgba(np.zeros_like(a), a)


PALETTES = {
    # cœur blanc, clair, moyen, bord sombre (8005ceb1, 0f85f7a1)
    "feu": ((255, 255, 250), (255, 236, 120), (255, 160, 40), (170, 50, 20)),
    "bleu": ((255, 255, 255), (190, 240, 255), (70, 170, 255), (25, 50, 150)),
}


def peindre(im, palette):
    """Aplats gris -> aplats de la palette (le cœur reste BLANC : une teinte
    multiplierait le blanc et le perdrait)."""
    a = np.asarray(im).astype(np.float32) / 255
    g, al = a[..., 0], a[..., 3]
    c = np.zeros(g.shape + (3,), np.float32)
    for seuil, col in zip((0.93, 0.74, 0.45, -1), palette):
        m = (g > seuil) & (c.sum(-1) == 0)
        c[m] = np.array(col, np.float32) / 255
    rgb = (c * 255).astype(np.uint8)
    return Image.fromarray(np.dstack([rgb, (al * 255).astype(np.uint8)]), "RGBA")


def _serie_peinte(fn, nom, pal):
    return {f"{nom}_{pal}_e{k}": (lambda k=k: peindre(fn(k), PALETTES[pal]), "peint",
                                  f"{nom} dessiné ({pal}), érosion {k}/{N_EROSION - 1} (mesh)")
            for k in range(N_EROSION)}


def _serie(fn, nom):
    return {f"{nom}_e{k}": (lambda k=k: fn(k), "à teinter", f"{nom} dessiné, érosion {k}/{N_EROSION - 1} (mesh)")
            for k in range(N_EROSION)}


DESSINS = {
    **_serie(trait, "trait"),
    **_serie(lame, "lame"),
    **_serie_peinte(trait, "trait", "feu"),
    **_serie_peinte(trait, "trait", "bleu"),
    **_serie_peinte(lame, "lame", "feu"),
    **_serie_peinte(lame, "lame", "bleu"),
    "griffure": (griffure, "encre", "griffures d'encre noires (dans l'effet lumineux)"),
    "veines": (veines, "encre", "veines d'encre en étoile (impact sombre, sol)"),
}


def images(nom, pal=None):
    """Noms des images d'érosion d'une série (pour `images` d'une couche mesh)."""
    return [f"{nom}_{pal}_e{k}" if pal else f"{nom}_e{k}" for k in range(N_EROSION)]
