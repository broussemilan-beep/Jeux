"""
Bibliothèque de MESHES VFX du studio : les formes 3D des effets. On y trouve
dômes, anneaux, sphères, tourbillons, croissants 3D et vagues au sol, avec
des UV pensés pour le défilement de texture (UV scrolling) :
- U court le long de la forme (azimut, longueur de l'arc) : faire défiler U
  fait tourner l'énergie autour de la forme ;
- V court en travers (hauteur, rayon) : faire défiler V la fait monter ou
  s'écarter.

Ces formes sont purement géométriques : numpy suffit, c'est déterministe et
sans dépendance. Blender reste l'outil des formes sculptées (le dragon de
l'aura, par exemple).

Sorties :
- meshes/<nom>.obj : import Roblox (MeshPart) ;
- meshes/meshes.json : positions, normales, UV et indices, pour l'aperçu
  three.js.
Unité : 1 stud ; formes centrées, Y vers le haut.

Usage : python3 meshes.py [dossier_sortie]
"""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))


def grille_tri(nu, nv):
    """Indices de triangles d'une grille (nu+1) x (nv+1)."""
    idx = []
    for i in range(nu):
        for j in range(nv):
            a = i * (nv + 1) + j
            b = (i + 1) * (nv + 1) + j
            idx += [a, b, a + 1, b, b + 1, a + 1]
    return idx


def surface(f, nu, nv):
    """f(u, v) -> point 3D, u et v dans [0, 1]. Normales calculées par
    différences finies. UV = (u, v)."""
    P, UV = [], []
    for i in range(nu + 1):
        for j in range(nv + 1):
            u, v = i / nu, j / nv
            P.append(f(u, v))
            UV.append((u, v))
    P = np.array(P, float)
    N = np.zeros_like(P)
    g = P.reshape(nu + 1, nv + 1, 3)
    du = np.gradient(g, axis=0)
    dv = np.gradient(g, axis=1)
    n = np.cross(du, dv)
    ln = np.linalg.norm(n, axis=2, keepdims=True)
    N = (n / np.where(ln < 1e-9, 1, ln)).reshape(-1, 3)
    return {"positions": P, "normales": N, "uv": np.array(UV), "indices": grille_tri(nu, nv)}


def dome(nu=48, nv=16):
    """Dôme (demi-sphère ouverte en bas) : onde de choc en coupole (Stagnant
    Rage), bouclier."""
    return surface(lambda u, v: (math.cos(2 * math.pi * u) * math.cos(v * math.pi / 2),
                                 math.sin(v * math.pi / 2),
                                 math.sin(2 * math.pi * u) * math.cos(v * math.pi / 2)), nu, nv)


def sphere(nu=48, nv=24):
    """Sphère : orbe, soleil (texture qui défile), cœur d'impact."""
    return surface(lambda u, v: (math.cos(2 * math.pi * u) * math.sin(v * math.pi),
                                 -math.cos(v * math.pi),
                                 math.sin(2 * math.pi * u) * math.sin(v * math.pi)), nu, nv)


def anneau_plat(nu=64, nv=2, interieur=0.9):
    """Anneau plat au sol (onde de choc qui s'élargit) : U = azimut, V = rayon."""
    return surface(lambda u, v: ((interieur + (1 - interieur) * v) * math.cos(2 * math.pi * u), 0.0,
                                 (interieur + (1 - interieur) * v) * math.sin(2 * math.pi * u)), nu, nv)


def tourbillon(nu=48, nv=12, tours=0.6):
    """Tourbillon : cône ouvert dont la paroi est tordue (air autour du poing,
    tourbillon de fumée du Serious Punch). Pointe en bas (y = 0), large en
    haut (y = 1). Avec une texture qui défile en U, l'air tourne."""
    def f(u, v):
        r = 0.12 + 0.88 * v
        a = 2 * math.pi * (u + tours * v)
        return (r * math.cos(a), v, r * math.sin(a))
    return surface(f, nu, nv)


def croissant_3d(nu=40, nv=4, ouverture=220.0):
    """Croissant 3D : bande plate en arc, effilée aux bouts (coupe, arc de vent
    qui tourne autour d'un impact). Dans le plan XZ, rayon 1, largeur maximale
    0,28 au milieu de l'arc."""
    def f(u, v):
        a = math.radians(-ouverture / 2 + ouverture * u)
        w = 0.28 * math.sin(math.pi * u) ** 0.8
        r = 1.0 + (v - 0.5) * w
        return (r * math.sin(a), 0.0, r * math.cos(a))
    return surface(f, nu, nv)


def vague_sol(nu=96, nv=3, dents=18):
    """Vague de vent au sol : couronne verticale à dents (Moon, Stagnant).
    Rayon 1, hauteur 1 au plus haut des dents ; U = azimut, V = hauteur."""
    def f(u, v):
        a = 2 * math.pi * u
        haut = 0.45 + 0.55 * abs(math.sin(dents * math.pi * u)) ** 3
        return (math.cos(a), v * haut, math.sin(a))
    return surface(f, nu, nv)


def tore(nu=64, nv=10, r_tube=0.04):
    """Anneau 3D fin (tore) : anneau net vu sous tous les angles."""
    def f(u, v):
        a, b = 2 * math.pi * u, 2 * math.pi * v
        R = 1 + r_tube * math.cos(b)
        return (R * math.cos(a), r_tube * math.sin(b), R * math.sin(a))
    return surface(f, nu, nv)


MESHES = {
    "dome": (dome, "onde de choc en coupole, bouclier"),
    "sphere": (sphere, "orbe, soleil, cœur d'impact"),
    "anneau_plat": (anneau_plat, "onde au sol qui s'élargit"),
    "tourbillon": (tourbillon, "air ou fumée qui tourne autour du poing"),
    "croissant_3d": (croissant_3d, "coupe, arc de vent autour de l'impact"),
    "vague_sol": (vague_sol, "vague de vent à dents au sol"),
    "tore": (tore, "anneau net en 3D"),
}


def ecrire_obj(m, chemin):
    with open(chemin, "w") as fh:
        fh.write("# studio VFX Rank Zero / Poing du Dragon, mesh genere (meshes.py)\n")
        for p in m["positions"]:
            fh.write(f"v {p[0]:.5f} {p[1]:.5f} {p[2]:.5f}\n")
        for t in m["uv"]:
            fh.write(f"vt {t[0]:.5f} {t[1]:.5f}\n")
        for n in m["normales"]:
            fh.write(f"vn {n[0]:.5f} {n[1]:.5f} {n[2]:.5f}\n")
        idx = m["indices"]
        for k in range(0, len(idx), 3):
            a, b, c = idx[k] + 1, idx[k + 1] + 1, idx[k + 2] + 1
            fh.write(f"f {a}/{a}/{a} {b}/{b}/{b} {c}/{c}/{c}\n")


def main(sortie=None):
    sortie = sortie or os.path.join(HERE, "meshes")
    os.makedirs(sortie, exist_ok=True)
    tout = {}
    for nom, (fn, role) in MESHES.items():
        m = fn()
        ecrire_obj(m, os.path.join(sortie, f"{nom}.obj"))
        tout[nom] = {"role": role, "triangles": len(m["indices"]) // 3,
                     "positions": np.round(m["positions"], 4).ravel().tolist(),
                     "normales": np.round(m["normales"], 3).ravel().tolist(),
                     "uv": np.round(m["uv"], 4).ravel().tolist(), "indices": m["indices"]}
    json.dump(tout, open(os.path.join(sortie, "meshes.json"), "w"))
    print({k: v["triangles"] for k, v in tout.items()}, "triangles ->", sortie)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)
