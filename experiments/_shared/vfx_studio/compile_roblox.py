"""
COMPILATION d'une recette vers Roblox : un module de données Luau
(`VFXRecettes.luau`) lu par le moteur d'exécution `luau/VFXStudio.luau`.

Ce que fait la compilation :
- normalise les valeurs typées. Une constante devient une séquence à deux
  points (t = 0 et t = 1), car une NumberSequence Roblox DOIT commencer à 0
  et finir à 1 (doc officielle) ;
- COMPRESSE les courbes à 20 points au plus (limite officielle des
  NumberSequence / ColorSequence), en simplifiant la polyligne par
  Ramer-Douglas-Peucker. Même idée que la compression de VFX Editor (MIT),
  réécrite ici ;
- convertit les couleurs (#hex -> {r, g, b} de 0 à 1) ;
- produit la table des assets (texture / mesh / son -> rbxassetid).
  Ce qui n'est pas encore envoyé sur Roblox est listé comme MANQUANT, pas
  inventé. Le moteur se rabat alors sur une texture intégrée de Roblox.

Usage : python3 compile_roblox.py [sortie.luau]   (défaut : luau/VFXRecettes.luau)
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import recettes  # noqa: E402

MAX_POINTS = 20
# texture intégrée à Roblox (rbxasset://), en repli tant que nos textures ne
# sont pas envoyées sur Roblox. Chemin cité par le guide game-designer
# (VFXRecipes) [README, pas vérifié dans le client : à confirmer dans Studio].
REPLI_TEXTURE = "rbxasset://textures/particles/sparkles_main.dds"


def hex3(h):
    h = h.lstrip("#")
    return [round(int(h[i:i + 2], 16) / 255, 4) for i in (0, 2, 4)]


def rdp(points, eps):
    """Ramer-Douglas-Peucker sur [(t, v)] : garde les extrémités."""
    if len(points) < 3:
        return points
    (t0, v0), (t1, v1) = points[0], points[-1]
    dmax, k = 0.0, 0
    for i in range(1, len(points) - 1):
        t, v = points[i]
        u = (t - t0) / max(1e-9, t1 - t0)
        d = abs(v - (v0 + (v1 - v0) * u))
        if d > dmax:
            dmax, k = d, i
    if dmax > eps:
        return rdp(points[:k + 1], eps)[:-1] + rdp(points[k:], eps)
    return [points[0], points[-1]]


def nseq(s, nom=""):
    """Valeur -> NumberSequence Roblox [[t, v, enveloppe]] : de 0 à 1, au plus
    20 points."""
    if s is None:
        return None
    if isinstance(s, (int, float)):
        return [[0, float(s), 0], [1, float(s), 0]]
    pts = [[float(k[0]), float(k[1]), float(k[2]) if len(k) > 2 else 0.0] for k in s]
    if pts[0][0] > 0:
        pts.insert(0, [0.0, pts[0][1], pts[0][2]])
    if pts[-1][0] < 1:
        pts.append([1.0, pts[-1][1], pts[-1][2]])
    if len(pts) > MAX_POINTS:
        eps = 1e-4
        while True:
            red = rdp([(p[0], p[1]) for p in pts], eps)
            if len(red) <= MAX_POINTS:
                break
            eps *= 1.6
        keep = {round(t, 9) for t, _v in red}
        pts = [p for p in pts if round(p[0], 9) in keep]
    return [[round(p[0], 4), round(p[1], 4), round(p[2], 4)] for p in pts]


def cseq(s):
    if s is None:
        return [[0, [1, 1, 1]], [1, [1, 1, 1]]]
    if isinstance(s, str):
        c = hex3(s)
        return [[0, c], [1, c]]
    pts = [[float(k[0]), hex3(k[1])] for k in s]
    if pts[0][0] > 0:
        pts.insert(0, [0.0, pts[0][1]])
    if pts[-1][0] < 1:
        pts.append([1.0, pts[-1][1]])
    return pts[:MAX_POINTS]


def rng(v):
    if v is None:
        return None
    if isinstance(v, (int, float)):
        return [float(v), float(v)]
    return [float(v[0]), float(v[1])]


def echelle(e):
    if e is None:
        return [[0, [1, 1, 1]], [1, [1, 1, 1]]]
    if isinstance(e, (int, float)):
        return [[0, [e, e, e]], [1, [e, e, e]]]
    out = []
    for k in e:
        v = k[1]
        out.append([k[0], list(v) if isinstance(v, (list, tuple)) else [v, v, v]])
    if out[0][0] > 0:
        out.insert(0, [0, out[0][1]])
    if out[-1][0] < 1:
        out.append([1, out[-1][1]])
    return out


def couche(L):
    c = dict(L)
    t = L["type"]
    if t == "particules":
        for k in ("size", "transparency", "squash"):
            c[k] = nseq(L.get(k, 0 if k != "size" else 1), k)
        c["color"] = cseq(L.get("color"))
        for k in ("lifetime", "speed", "rotation", "rotspeed"):
            c[k] = rng(L.get(k, 0 if k != "lifetime" else 1))
        c["spread"] = list(L.get("spread", [0, 0]))
        c["accel"] = list(L.get("accel", [0, 0, 0]))
        c["light_emission"] = L.get("light_emission", 1)
    elif t == "mesh":
        c["echelle"] = echelle(L.get("echelle"))
        c["transparency"] = nseq(L.get("transparency", 0))
        c["color"] = cseq(L.get("color"))
    elif t in ("trail", "beam"):
        c["largeur"] = nseq(L.get("largeur", 1))
        c["transparency"] = nseq(L.get("transparency", 0))
        c["color"] = cseq(L.get("color"))
    return c


def compiler(rec):
    out = {k: v for k, v in rec.items() if k not in ("couches", "projectile", "bloom", "cameras")}
    out["couches"] = [couche(L) for L in rec["couches"]]
    if rec.get("projectile"):
        p = dict(rec["projectile"])
        v = dict(p.get("visuel", {}))
        v.update({"type": "mesh", "t0": p["t0"], "duree": p["t1"] - p["t0"], "ancre": "projectile"})
        p["visuel"] = couche(v)
        out["projectile"] = p
    b = rec.get("bloom") or {}
    out["bloom"] = {"intensite": nseq(b.get("intensite", 0.6)), "seuil": b.get("seuil", 0.8), "taille": b.get("taille", 2)}
    return out


def lua(v, ind=0):
    pad = "\t" * ind
    if v is None:
        return "nil"
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        f = float(v)
        return str(int(f)) if f.is_integer() else repr(round(f, 5))
    if isinstance(v, str):
        return json.dumps(v, ensure_ascii=False)
    if isinstance(v, (list, tuple)):
        if all(isinstance(x, (int, float)) for x in v):
            return "{" + ", ".join(lua(x) for x in v) + "}"
        return "{\n" + "".join(f"{pad}\t{lua(x, ind + 1)},\n" for x in v) + pad + "}"
    if isinstance(v, dict):
        items = []
        for k, x in v.items():
            key = k if k.isidentifier() else f"[{json.dumps(k)}]"
            items.append(f"{pad}\t{key} = {lua(x, ind + 1)},\n")
        return "{\n" + "".join(items) + pad + "}"
    raise TypeError(type(v))


def assets():
    cat = json.load(open(os.path.join(HERE, "textures", "catalogue.json")))
    ids = cat.get("rbxassetid", {})
    tex = {t["nom"]: ids.get(t["nom"]) for t in cat["textures"]}
    var = {}
    for t in cat["textures"]:
        if t.get("variante_de"):
            var[t["variante_de"]] = var.get(t["variante_de"], 0) + 1
    return {"textures": tex, "variantes": var, "manquants": sorted(k for k, v in tex.items() if not v),
            "repli_texture": REPLI_TEXTURE}


def main(sortie=None):
    sortie = sortie or os.path.join(HERE, "luau", "VFXRecettes.luau")
    os.makedirs(os.path.dirname(sortie), exist_ok=True)
    data = {"recettes": {k: compiler(v) for k, v in recettes.toutes().items()}, "assets": assets()}
    src = ("--!nonstrict\n-- GÉNÉRÉ par vfx_studio/compile_roblox.py : ne pas éditer à la main.\n"
           "-- Recettes VFX compilées (NumberSequence de 0 à 1, <= 20 points ; couleurs 0-1).\n"
           "return " + lua(data) + "\n")
    open(sortie, "w", encoding="utf-8").write(src)
    print(sortie, len(data["recettes"]), "recettes ; textures sans rbxassetid :", len(data["assets"]["manquants"]))
    return data


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)
