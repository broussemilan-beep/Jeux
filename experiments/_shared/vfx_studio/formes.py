"""
Bibliothèque de FORMES CEL du studio VFX : textures et flipbooks générés
ici, de façon déterministe (graine), prêts pour Roblox.

Pourquoi (corpus/RELECTURE_REFS_VFX_2026-09-25.md, CARNET §4b) : dans les
refs, les effets sont graphiques, jamais réalistes. On y voit :
- des croissants effilés, des éclats acérés, des étoiles à 4 branches ;
- des anneaux en trait fin, de la fumée en boules à deux tons ;
- du feu en aplats cerné de rouge sombre, des flammes d'aura à pointes ;
- des arcs de vent.
Nos anciennes textures procédurales étaient des taches floues.

Conventions :
- les textures « à teinter » sont BLANCHES avec de l'alpha. La couleur vient
  de l'émetteur (ParticleEmitter.Color multiplie la texture) ;
- les textures « peintes » (feu cel) portent leurs couleurs, et on leur met
  Color = blanc ;
- les flipbooks sont des planches de 1024², en grille 2x2 ou 4x4. Chaque
  image laisse une MARGE transparente dans sa case : la doc officielle
  l'exige, pour le mip-mapping (fiches/VFX.md §3) ;
- les textures qui défilent (UV scrolling) se raccordent horizontalement.

Usage : python3 formes.py [dossier_sortie]  (défaut : ./textures)
"""
import json
import math
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
N = 512  # taille d'une texture simple


# ---------------------------------------------------------------- outils

def grille(n):
    y, x = np.mgrid[0:n, 0:n].astype(np.float32)
    return (x + 0.5) / n * 2 - 1, (y + 0.5) / n * 2 - 1  # [-1, 1], y vers le bas


def lisse(d, largeur):
    """Bord net mais anti-crénelé : distance signée -> alpha."""
    return np.clip(0.5 - d / max(largeur, 1e-6), 0.0, 1.0)


def bruit(n, echelle, graine, octaves=4):
    """Bruit de valeur fractal, périodique (raccord sur les deux axes)."""
    rng = np.random.default_rng(graine)
    out = np.zeros((n, n), np.float32)
    amp, tot = 1.0, 0.0
    for o in range(octaves):
        k = int(echelle * 2 ** o)
        g = rng.random((k, k)).astype(np.float32)
        t = np.linspace(0, k, n, endpoint=False)
        i0 = np.floor(t).astype(int) % k
        i1 = (i0 + 1) % k
        f = t - np.floor(t)
        f = f * f * (3 - 2 * f)
        a = g[i0][:, i0] * (1 - f)[None, :] + g[i0][:, i1] * f[None, :]
        b = g[i1][:, i0] * (1 - f)[None, :] + g[i1][:, i1] * f[None, :]
        out += amp * (a * (1 - f)[:, None] + b * f[:, None])
        tot += amp
        amp *= 0.5
    return out / tot


def rgba_blanc(alpha):
    a = (np.clip(alpha, 0, 1) * 255).astype(np.uint8)
    w = np.full_like(a, 255)
    return Image.fromarray(np.dstack([w, w, w, a]), "RGBA")


def planche(images, grille_n, taille=1024, marge=8):
    """Flipbook Roblox : grille_n x grille_n cases, marge transparente dans
    chaque case (mip-mapping)."""
    case = taille // grille_n
    S = Image.new("RGBA", (taille, taille), (0, 0, 0, 0))
    for k, im in enumerate(images[: grille_n * grille_n]):
        im = im.resize((case - 2 * marge, case - 2 * marge), Image.LANCZOS)
        S.paste(im, ((k % grille_n) * case + marge, (k // grille_n) * case + marge))
    return S


# ---------------------------------------------------------------- formes

def croissant(n=N, epaisseur=0.30, decalage=0.30):
    """Croissant de lune effilé aux deux bouts, entièrement dans le cadre :
    trace d'un coup, coupe, vent. Disque extérieur moins un disque décalé vers
    le bas ; épais au sommet, pointu aux extrémités.
    (1er essai : les cercles débordaient du cadre, on voyait une arche coupée.)"""
    x, y = grille(n)
    ext = np.hypot(x, y) - 0.9
    inte = (0.9 - epaisseur * 0.5) - np.hypot(x, y - decalage)
    d = np.maximum(ext, inte)
    return rgba_blanc(lisse(d, 2.5 / n))


def eclat(n=N):
    """Éclat acéré (losange très allongé) : étincelle orientée par la vitesse
    (VelocityParallel)."""
    x, y = grille(n)
    d = np.abs(x) / 0.13 + np.abs(y) / 0.95 - 1
    a = lisse(d, 0.02) * (0.75 + 0.25 * (1 - np.abs(y)))
    return rgba_blanc(a)


def etoile4(n=N, finesse=0.07):
    """Étoile à 4 branches longues et fines, avec un petit cœur (Black Hole,
    carte d'impact 41d7796b)."""
    x, y = grille(n)
    bras = np.minimum(np.abs(x) / finesse + np.abs(y), np.abs(y) / finesse + np.abs(x)) - 1
    coeur = np.hypot(x, y) / 0.16 - 1
    a = np.maximum(lisse(bras, 0.03), lisse(coeur, 0.1))
    return rgba_blanc(a)


def anneau(n=N, rayon=0.86, trait=0.035):
    """Anneau en trait fin et net (onde de choc des M1, 449 / aafdc91d)."""
    x, y = grille(n)
    d = np.abs(np.hypot(x, y) - rayon) - trait
    return rgba_blanc(lisse(d, 2.0 / n))


def flash(n=N, rayons=14, graine=3):
    """Éclat de flash : cœur plein et rayons irréguliers (1-2 images au contact)."""
    rng = np.random.default_rng(graine)
    x, y = grille(n)
    r, t = np.hypot(x, y), np.arctan2(y, x)
    long = np.zeros_like(r)
    for k in range(rayons):
        a0 = rng.uniform(-math.pi, math.pi)
        L = rng.uniform(0.5, 1.0)
        w = rng.uniform(0.04, 0.09)
        da = np.angle(np.exp(1j * (t - a0)))
        long = np.maximum(long, L * np.clip(1 - np.abs(da) / w, 0, 1))
    d = r - np.maximum(0.28, long * 0.95)
    return rgba_blanc(lisse(d, 0.02))


def ligne_vitesse(n=N):
    """Ligne de vitesse effilée (traits radiaux, fonds remplacés)."""
    x, y = grille(n)
    d = np.abs(y) / (0.06 * np.clip(1 - np.abs(x), 0, 1) + 1e-3) - 1
    return rgba_blanc(lisse(d, 0.08) * (np.abs(x) < 1))


def bruit_energie(n=N, graine=7):
    """Texture qui DÉFILE (UV scrolling) sur un mesh ou un Beam : filaments
    d'énergie étirés le long de U, raccord parfait sur les deux axes.
    (1er essai : bruit isotrope = des taches, pas des filaments.)"""
    rng = np.random.default_rng(graine)
    y = np.arange(n)[:, None] / n
    x = np.arange(n)[None, :] / n
    v = np.zeros((n, n), np.float32)
    for _ in range(26):
        f = rng.integers(1, 4)                       # ondulation périodique en U
        ph, amp = rng.uniform(0, 2 * math.pi), rng.uniform(0.01, 0.05)
        y0, w = rng.uniform(0, 1), rng.uniform(0.004, 0.018)
        dy = (y - y0 - amp * np.sin(2 * math.pi * f * x + ph) + 0.5) % 1.0 - 0.5
        long = 0.5 + 0.5 * np.sin(2 * math.pi * rng.integers(1, 3) * x + rng.uniform(0, 6.3))
        v = np.maximum(v, np.clip(1 - np.abs(dy) / w, 0, 1) * (long > 0.35))
    v = np.where(v > 0.5, 1.0, v * 0.6)
    return rgba_blanc(v)


def arc_vent(n=N, graine=11):
    """Arc de vent (air) : croissant large rempli de stries parallèles à l'arc
    (Stagnant Rage, Moon, coup chapeau). Sur un mesh ou un Beam, il défile
    le long de l'arc."""
    x, y = grille(n)
    base = np.asarray(croissant(n, epaisseur=0.42, decalage=0.36))[..., 3] / 255.0
    rng = np.random.default_rng(graine)
    stries = np.zeros_like(x)
    r = np.hypot(x, y)
    for _ in range(9):
        r0, w = rng.uniform(0.55, 0.9), rng.uniform(0.006, 0.02)
        stries = np.maximum(stries, np.clip(1 - np.abs(r - r0) / w, 0, 1))
    return rgba_blanc(base * (0.35 + 0.65 * stries))


def ruban(n=N):
    """Ruban pour Trail / Beam / anneaux : U le long, V en travers. Cœur
    brillant au milieu de V, bords doux, et une strie fine. Sans stries
    pointillées : la 1re traînée, en bruit_energie, se lisait comme des
    pointillés."""
    y = (np.arange(n)[:, None] + 0.5) / n * 2 - 1
    v = np.clip(1 - np.abs(y) / 0.9, 0, 1) ** 1.6
    coeur = np.clip(1 - np.abs(y) / 0.18, 0, 1)
    a = np.clip(0.55 * v + coeur, 0, 1) * np.ones((1, n))
    return rgba_blanc(a)


def halo(n=N):
    """Halo doux (lueur autour d'un orbe ou d'un point chaud). Seul endroit où
    un dégradé doux est voulu : il accompagne une forme nette, il ne la
    remplace pas (CARNET §4b.1)."""
    x, y = grille(n)
    r = np.hypot(x, y)
    return rgba_blanc(np.clip(1 - r, 0, 1) ** 2.2)


# ------------------------------------------------------------- flipbooks

def fumee_cel(k, n_img, n=256, graine=21):
    """Bouffée de fumée cel à deux tons (blanc éclairé / gris d'ombre) : elle
    gonfle, puis se ronge par le bruit (dissolution) au lieu de s'effacer."""
    t = k / (n_img - 1)
    rng = np.random.default_rng(graine)
    x, y = grille(n)
    d = np.full_like(x, 9.0)
    for _ in range(6):
        cx, cy = rng.uniform(-0.35, 0.35), rng.uniform(-0.25, 0.3)
        rr = rng.uniform(0.28, 0.42) * (0.55 + 0.55 * math.sqrt(t))
        d = np.minimum(d, np.hypot(x - cx * (0.6 + t), y - cy * (0.6 + t)) - rr)
    ronge = bruit(n, 4, graine + 1) - 0.25
    seuil = -0.9 + 1.25 * t ** 1.4
    a = lisse(d, 0.02) * lisse(seuil - ronge, 0.04)
    # ombre cel : la forme décalée vers le bas-droite ; son intersection avec
    # la forme est la partie à l'ombre, et le bord haut-gauche reste éclairé.
    # (1er essai : érosion = bord blanc partout, lumière incohérente.)
    rng2 = np.random.default_rng(graine)
    d2 = np.full_like(x, 9.0)
    for _ in range(6):
        cx, cy = rng2.uniform(-0.35, 0.35), rng2.uniform(-0.25, 0.3)
        rr = rng2.uniform(0.28, 0.42) * (0.55 + 0.55 * math.sqrt(t))
        d2 = np.minimum(d2, np.hypot(x - cx * (0.6 + t) - 0.10, y - cy * (0.6 + t) - 0.12) - rr)
    ombre = lisse(d2, 0.02)
    ton = 1.0 - 0.3 * ombre                   # 2 tons : 1.0 (clair) / 0.7 (ombre)
    v = (np.clip(ton, 0, 1) * 255).astype(np.uint8)
    return Image.fromarray(np.dstack([v, v, v, (a * 255).astype(np.uint8)]), "RGBA")


def feu_cel(k, n_img, n=256, graine=31):
    """Feu cel PEINT (Stagnant Rage) : cœur jaune pâle, corps orange, contour
    rouge sombre. Il monte, se déchire, puis s'éteint."""
    t = k / (n_img - 1)
    x, y = grille(n)
    b = bruit(n, 3, graine + k * 0 + 1, octaves=4)
    b2 = np.roll(b, int(-t * n * 0.6), axis=0)            # le bruit monte
    forme = np.hypot(x * (1.1 + 0.4 * t), (y + 0.1 - 0.25 * t) * 0.85) - (0.62 - 0.2 * t) - (b2 - 0.5) * (0.9 + 0.6 * t)
    forme = forme + np.clip(y + 0.15, 0, 1) * 0.3 * t      # le bas s'éteint d'abord
    ext = lisse(forme, 0.02)
    corps = lisse(forme + 0.09, 0.02)
    coeur = lisse(forme + 0.30 - 0.15 * t, 0.02)
    rgb = np.zeros((n, n, 3), np.float32)
    rgb[:] = (0.45, 0.06, 0.04)                           # contour rouge sombre
    rgb = rgb * (1 - corps[..., None]) + np.array((1.0, 0.45, 0.08)) * corps[..., None]
    rgb = rgb * (1 - coeur[..., None]) + np.array((1.0, 0.92, 0.55)) * coeur[..., None]
    a = ext * (1 - np.clip((t - 0.75) / 0.25, 0, 1))
    return Image.fromarray(np.dstack([(rgb * 255).astype(np.uint8), (a * 255).astype(np.uint8)]), "RGBA")


def flamme_aura(k, n_img, n=256, graine=41):
    """Flamme d'aura : des LANGUES effilées qui montent et ondulent (Gemini,
    boxeur), à teinter. Boucle : la dernière image rejoint la première.
    (1er essai : un rectangle à pointes, sans langues.)"""
    t = k / n_img
    x, y = grille(n)
    rng = np.random.default_rng(graine)
    a = np.zeros_like(x)
    coeur = np.zeros_like(x)
    for i in range(7):
        cx = rng.uniform(-0.55, 0.55)
        h = rng.uniform(0.9, 1.6)
        ph = rng.uniform(0, 2 * math.pi)
        # langue : largeur qui décroît vers le haut, pointe qui ondule
        u = np.clip((0.9 - y) / h, 0, 1)                  # 0 en bas, 1 à la pointe
        sway = 0.12 * u ** 1.5 * np.sin(2 * math.pi * t * rng.integers(1, 3) + ph + 3 * u)
        larg = 0.28 * (1 - u) ** 0.8 * (1 - 0.5 * (y > 0.6))
        d = np.abs(x - cx - sway) - larg
        d = np.where((y < 0.9 - h) | (y > 0.95), 1.0, d)
        a = np.maximum(a, lisse(d, 0.02))
        coeur = np.maximum(coeur, lisse(d + 0.09, 0.02))
    a *= np.clip((0.95 - y) / 0.25, 0, 1)                # la base se fond
    v = 0.8 + 0.2 * coeur
    g = (v * 255).astype(np.uint8)
    return Image.fromarray(np.dstack([g, g, g, (a * 255).astype(np.uint8)]), "RGBA")


def roches_cel(k, n_img, n=256, graine=53):
    """DÉBRIS de sol peints (Stagnant Rage : des blocs qui volent partout ;
    auto-évaluation VFX, piste 1). Éclat de roche anguleux, 3 tons cel :
    facette éclairée, corps, facette d'ombre, contour brun sombre. 4 formes
    (planche 2x2) : chaque particule en tire une au hasard."""
    rng = np.random.default_rng(graine + 17 * k)
    m = rng.integers(5, 8)
    ang = np.sort(rng.uniform(0, 2 * math.pi, m))
    rad = rng.uniform(0.55, 0.92, m)
    px, py = rad * np.cos(ang), rad * np.sin(ang) * rng.uniform(0.65, 0.95)
    x, y = grille(n)
    # distance signée au polygone convexe (max des demi-plans)
    d = np.full_like(x, -1e9)
    for i in range(m):
        ax_, ay_ = px[i], py[i]
        bx_, by_ = px[(i + 1) % m], py[(i + 1) % m]
        nx_, ny_ = by_ - ay_, -(bx_ - ax_)
        ln = math.hypot(nx_, ny_) + 1e-9
        d = np.maximum(d, ((x - ax_) * nx_ + (y - ay_) * ny_) / ln)
    ext = lisse(d, 0.02)
    corps = lisse(d + 0.07, 0.02)
    # facette éclairée en haut à gauche, ombre en bas à droite (coupe en biais)
    cx, cy = rng.uniform(-0.15, 0.15), rng.uniform(-0.15, 0.15)
    haut = ((x - cx) * 0.6 + (y - cy) * 1.0) < -0.12
    bas = ((x - cx) * -0.4 + (y - cy) * 1.0) > 0.22
    rgb = np.zeros((n, n, 3), np.float32)
    rgb[:] = (0.16, 0.11, 0.08)                               # contour
    base = np.array((0.52, 0.45, 0.38))
    col = np.where(haut[..., None], np.array((0.78, 0.72, 0.62)), np.where(bas[..., None], np.array((0.30, 0.25, 0.21)), base))
    rgb = rgb * (1 - corps[..., None]) + col * corps[..., None]
    return Image.fromarray(np.dstack([(rgb * 255).astype(np.uint8), (ext * 255).astype(np.uint8)]), "RGBA")


FORMES = {
    "croissant": (croissant, "à teinter", "trace d'un coup, coupe, vent (VelocityPerpendicular ou mesh)"),
    "eclat": (eclat, "à teinter", "étincelle acérée orientée (VelocityParallel)"),
    "etoile4": (etoile4, "à teinter", "étoile à 4 branches (flash cel, scintillement)"),
    "anneau": (anneau, "à teinter", "onde de choc en trait fin"),
    "flash": (flash, "à teinter", "éclat de contact 1-2 images"),
    "ligne_vitesse": (ligne_vitesse, "à teinter", "ligne de vitesse effilée"),
    "bruit_energie": (bruit_energie, "à teinter", "texture qui défile (Beam / mesh), raccord"),
    "arc_vent": (arc_vent, "à teinter", "arc de vent strié (air)"),
    "ruban": (ruban, "à teinter", "Trail / Beam / anneau : cœur brillant, bords doux"),
    "halo": (halo, "à teinter", "lueur douce autour d'un point chaud (accompagne une forme nette)"),
}
FLIPBOOKS = {
    "fumee_cel": (fumee_cel, 16, 4, "à teinter", "bouffée de fumée cel 2 tons, OneShot"),
    "feu_cel": (feu_cel, 16, 4, "peint", "feu cel à contour, OneShot"),
    "flamme_aura": (flamme_aura, 16, 4, "à teinter", "flamme d'aura à pointes, Loop"),
    "roches_cel": (roches_cel, 4, 2, "peint", "débris de sol, 4 formes (départ aléatoire, 1 i/s)"),
}


# DÉFILEMENT sur Roblox : un mesh n'a pas de décalage de texture natif. On
# fait tourner N copies de la texture, décalées de k/N en U (le moteur Luau
# échange SpecialMesh.TextureId). L'aperçu quantifie son défilement de la
# même façon : ce qu'on voit dans le labo, c'est ce que Roblox fera.
VARIANTES_DEFILEMENT = {"bruit_energie": 8}


def variantes(img, n):
    """n copies décalées de k/n de la largeur (U), sans couture si l'image
    boucle en U."""
    import numpy as _np
    a = _np.asarray(img)
    w = a.shape[1]
    return [Image.fromarray(_np.roll(a, -round(k * w / n), axis=1)) for k in range(n)]


def main(sortie=None):
    sortie = sortie or os.path.join(HERE, "textures")
    os.makedirs(sortie, exist_ok=True)
    catalogue = []
    import peints  # textures peintes (dragon, éclair) : peints.py
    import dessins  # textures dessinées pour meshes (traits, lames, encre) : dessins.py
    for nom, (fn, mode, role) in list(FORMES.items()) + list(peints.PEINTS.items()) + list(dessins.DESSINS.items()):
        im = fn()
        im.save(os.path.join(sortie, f"{nom}.png"))
        catalogue.append({"nom": nom, "fichier": f"{nom}.png", "grille": "Static", "resolution": max(im.size), "mode": mode,
                          "role": role})
    for nom, n in VARIANTES_DEFILEMENT.items():
        for k, im in enumerate(variantes(Image.open(os.path.join(sortie, f"{nom}.png")), n)):
            im.save(os.path.join(sortie, f"{nom}_d{k}.png"))
            catalogue.append({"nom": f"{nom}_d{k}", "fichier": f"{nom}_d{k}.png", "grille": "Static", "resolution": N,
                              "mode": "defilement", "variante_de": nom, "decalage_u": k / n,
                              "role": f"défilement Roblox : {nom} décalée de {k}/{n} en U"})
    for nom, (fn, n_img, g, mode, role) in FLIPBOOKS.items():
        planche([fn(k, n_img) for k in range(n_img)], g).save(os.path.join(sortie, f"{nom}_{g}x{g}.png"))
        catalogue.append({"nom": nom, "fichier": f"{nom}_{g}x{g}.png", "grille": f"Grid{g}x{g}", "images": n_img,
                          "resolution": 1024, "marge_px": 8, "mode": mode, "role": role})
    # format de catalogue façon OpenVFX : {asset, grille, résolution} ; l'asset
    # Roblox (rbxassetid) sera rempli après envoi des textures sur Roblox
    json.dump({"textures": catalogue, "rbxassetid": {}}, open(os.path.join(sortie, "catalogue.json"), "w"),
              indent=1, ensure_ascii=False)
    print(len(catalogue), "textures ->", sortie)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)
