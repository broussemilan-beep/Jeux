"""
CRITIQUE VFX, 1re partie : les LIMITES OFFICIELLES de Roblox et les repères
de coût, vérifiés sur les recettes compilées. Ça ne dit rien de la beauté :
c'est l'œil qui juge. Ça dit si l'effet est valide, et ce qu'il coûte.

Sources (fiches/VFX.md §3 ; recherche/vfx_2026-09-25/03 tableau P1-P19) :
- Rate <= 400/s (100 sur mobile) ;
- Lifetime <= 20 s ;
- séquences de 0 à 1 et au plus 20 points ;
- FlipbookFramerate <= 30 ;
- flipbook 1024² avec une grille qui tombe juste ;
- Beam.Segments >= n-1 points ;
- Trail.Lifetime entre 0,01 et 20 s.
Repères non officiels, affichés comme tels : 50-100 particules simultanées
par effet (roblox-dev-notes, non sourcé) ; un appel de rendu par émetteur,
par Beam et par Part semi-transparente (MrChickenRocket).

Usage : python3 critique.py            -> rapport + code de sortie 1 si erreur
"""
import json
import os
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import compile_roblox as C  # noqa: E402
import recettes  # noqa: E402


def verifier_seq(s, nom, err, bornes=None):
    if s is None:
        return
    if s[0][0] != 0 or s[-1][0] != 1:
        err.append(f"{nom} : la séquence doit aller de t=0 à t=1")
    if len(s) > 20:
        err.append(f"{nom} : {len(s)} points > 20")
    if bornes:
        for k in s:
            if not (bornes[0] - 1e-6 <= k[1] <= bornes[1] + 1e-6):
                err.append(f"{nom} : valeur {k[1]} hors [{bornes[0]}, {bornes[1]}]")
                break


def critiquer(nom, rec):
    comp = C.compiler(rec)
    cat = {t["nom"]: t for t in json.load(open(os.path.join(HERE, "textures", "catalogue.json")))["textures"]}
    err, avert, info = [], [], []
    appels, semi, tex, courbe = 0, 0, set(), []
    for L in comp["couches"] + ([comp["projectile"]["visuel"]] if comp.get("projectile") else []):
        n = f"{nom}/{L.get('nom', L['type'])}"
        if L.get("texture"):
            tex.add(L["texture"])
            if L["texture"] not in cat:
                err.append(f"{n} : texture inconnue {L['texture']}")
        if L["type"] == "particules":
            appels += 1
            rate = L.get("rate", 0) or 0
            if rate > 400:
                err.append(f"{n} : Rate {rate} > 400/s")
            elif rate > 100:
                avert.append(f"{n} : Rate {rate} > 100/s (plafond mobile)")
            if L["lifetime"][1] > 20:
                err.append(f"{n} : Lifetime {L['lifetime'][1]} > 20 s")
            verifier_seq(L["size"], n + ".Size", err)
            verifier_seq(L["transparency"], n + ".Transparency", err, (0, 1))
            verifier_seq(L["squash"], n + ".Squash", err)
            courbe.append(L)
            fb = L.get("flipbook")
            if fb:
                t = cat.get(L["texture"], {})
                im = Image.open(os.path.join(HERE, "textures", t["fichier"]))
                if im.size != (1024, 1024):
                    err.append(f"{n} : flipbook {im.size} au lieu de 1024x1024")
                if im.size[0] % fb["grille"]:
                    err.append(f"{n} : 1024 n'est pas multiple de la grille {fb['grille']}")
                if fb.get("fps", 0) > 30:
                    err.append(f"{n} : FlipbookFramerate {fb['fps']} > 30")
                if not t.get("marge_px"):
                    avert.append(f"{n} : flipbook sans marge entre les images (mip-mapping)")
        elif L["type"] == "mesh":
            appels += 1
            verifier_seq(L["transparency"], n + ".Transparency", err, (0, 1))
            if any(0 < k[1] < 1 for k in L["transparency"]):
                semi += 1
            du, dv = (L.get("defilement") or [0, 0])
            nv = sum(1 for t in cat.values() if t.get("variante_de") == L.get("texture"))
            if du and not nv:
                err.append(f"{n} : défilement sur {L.get('texture')} sans variantes décalées (formes.VARIANTES_DEFILEMENT)")
            if dv:
                avert.append(f"{n} : défilement en V ({dv}/s) non reproduit sur Roblox (variantes en U seulement)")
        elif L["type"] == "trail":
            appels += 1
            lt = L.get("lifetime", 2)
            if not (0.01 <= lt <= 20):
                err.append(f"{n} : Trail.Lifetime {lt} hors [0,01 ; 20]")
            verifier_seq(L["transparency"], n + ".Transparency", err, (0, 1))
        elif L["type"] == "serpent":
            n_pts = len(L["images"][0][1])
            if any(len(im[1]) != n_pts for im in L["images"]):
                err.append(f"{n} : échantillons de tailles différentes")
            if L["images"][0][0] > 1e-6 or any(b[0] < a[0] for a, b in zip(L["images"], L["images"][1:])):
                err.append(f"{n} : temps des échantillons pas croissants depuis 0")
            appels += 1 + (1 if L.get("tete") else 0)
            if L.get("tete"):
                for k in ("texture", "texture_miroir"):
                    if L["tete"].get(k) and L["tete"][k] not in cat:
                        err.append(f"{n} : texture de tête inconnue {L['tete'][k]}")
            info.append(f"{n} : {n_pts - 1} Beams + carte de tête, {len(L['images'])} échantillons")
        elif L["type"] == "eclairs":
            appels += 1
            info.append(f"{n} : {L.get('nombre', 4) * L.get('brisures', 5)} Beams recyclés (jamais recréés)")
        elif L["type"] == "beam":
            appels += 1
            npts = max(len(L["transparency"]), len(L["color"]))
            if L.get("segments", 10) < npts - 1:
                err.append(f"{n} : Beam.Segments {L.get('segments', 10)} < {npts - 1}")
    # particules vivantes INSTANT PAR INSTANT (pas la somme de toutes les
    # couches : la 1re version additionnait des couches jamais simultanées)
    def vivantes(t):
        n = 0.0
        for L in courbe:
            lo, hi = L["lifetime"]
            if L.get("emit") is not None:
                n += L["emit"] if L["t0"] <= t <= L["t0"] + hi else 0
            else:
                d = L.get("duree_emission", 0)
                a, b = max(L["t0"], t - hi), min(L["t0"] + d, t)
                n += max(0.0, b - a) * L["rate"]
        return n
    simult = max(vivantes(i / 120) for i in range(int(rec["duree"] * 120) + 1))
    if simult > 100:
        avert.append(f"{nom} : ~{int(simult)} particules simultanées au pic (repère non officiel : 50-100 par effet)")
    # son : existence dans la banque, puis le vide avant l'impact (sons.py)
    import sons as SONS
    for so in rec.get("sons", []):
        if so["son"] not in SONS.BANQUE:
            err.append(f"{nom} : son inconnu {so['son']}")
    if not err:
        e2, i2 = SONS.critique_son(rec)
        err += e2
        info += i2
    info.append(f"{nom} : {len(comp['couches'])} couches, ~{int(simult)} particules au pic, "
                f"~{appels + semi} appels de rendu estimés ({semi} meshes semi-transparents), {len(tex)} textures")
    return err, avert, info


def main():
    E, A, I = [], [], []
    for k, r in recettes.toutes().items():
        e, a, i = critiquer(k, r)
        E += e; A += a; I += i
    for x in I:
        print("INFO  ", x)
    for x in A:
        print("AVERT ", x)
    for x in E:
        print("ERREUR", x)
    print("CRITIQUE OK" if not E else f"CRITIQUE : {len(E)} erreur(s)")
    return 0 if not E else 1


if __name__ == "__main__":
    sys.exit(main())
