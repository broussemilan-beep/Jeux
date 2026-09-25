"""
ALLURE d'un serpent / dragon (couches « serpent » d'une scène), mesurée sur
les données JOUÉES (staging.json : images de la forme en temps de recette).

Né du retour de Milan sur le Poing du Dragon v13d (7,85/10) : « le dragon va
dans tous les sens hyper rapidement ». Mesuré avec cet outil : la tête filait
à 25-60 studs/s et virait à 200-900 °/s presque tout le temps, sans moment
lent. Les refs (Last Breath, Goku) : lent et tenu, avec UN OU DEUX coups
rapides. L'outil ne dit pas ce qui est beau ; il montre le RYTHME :

- vitesse de la tête (studs/s) et en LONGUEURS DE CORPS par seconde ;
- vitesse de virage (°/s) ;
- par tranches de 0,2 s, avec une étiquette : TENU (< 0,3 corps/s),
  LENT (< 1,2), RAPIDE (< 2,5), FOUET (au-delà), et « VIRE » si > 250 °/s ;
- un résumé : part du temps rapide ou fouet, part du temps qui vire.

Usage : python3 allure.py <staging.json> [nom_couche ...]
"""
import json
import sys

import numpy as np

SEUILS = ((0.3, "TENU"), (1.2, "LENT"), (2.5, "RAPIDE"), (1e9, "FOUET"))
VIRE = 250.0


def longueur(pts):
    p = np.asarray(pts, float)
    return float(np.linalg.norm(np.diff(p, axis=0), axis=1).sum())


def allure(L, fps=60, frame0=0, pas=0.2, imprimer=True):
    ims = L["images"]
    T = np.array([t for t, _ in ims], float)
    H = np.array([p[0] for _, p in ims], float)
    corps = np.median([longueur(p) for _, p in ims])
    dt = np.diff(T)
    v = np.linalg.norm(np.diff(H, axis=0), axis=1) / np.maximum(dt, 1e-6)
    dirs = np.diff(H, axis=0)
    dirs /= (np.linalg.norm(dirs, axis=1, keepdims=True) + 1e-9)
    ang = np.zeros_like(v)
    ang[1:] = np.degrees(np.arccos(np.clip((dirs[1:] * dirs[:-1]).sum(1), -1, 1))) / np.maximum(dt[1:], 1e-6)
    tt = T[1:]
    lignes = []
    for a in np.arange(T[0], T[-1], pas):
        m = (tt >= a) & (tt < a + pas)
        if not m.any():
            continue
        vc = float(v[m].mean()) / corps
        tag = next(n for s, n in SEUILS if vc < s)
        vir = float(np.median(ang[m]))
        lignes.append({"t": round(float(a), 2), "frame": int(round(frame0 + a * fps)), "studs_s": round(float(v[m].mean()), 1),
                       "corps_s": round(vc, 2), "virage": round(vir), "etat": tag + (" VIRE" if vir > VIRE else "")})
    n = max(1, len(lignes))
    res = {"nom": L.get("nom"), "corps_studs": round(float(corps), 1),
           "part_rapide": round(sum(l["etat"].startswith(("RAPIDE", "FOUET")) for l in lignes) / n, 2),
           "part_vire": round(sum("VIRE" in l["etat"] for l in lignes) / n, 2),
           "part_lent_ou_tenu": round(sum(l["etat"].startswith(("LENT", "TENU")) for l in lignes) / n, 2), "tranches": lignes}
    if imprimer:
        print(f"\n{res['nom']} (corps {res['corps_studs']} studs) : rapide/fouet {res['part_rapide']:.0%}, "
              f"vire {res['part_vire']:.0%}, lent/tenu {res['part_lent_ou_tenu']:.0%}")
        for l in lignes:
            print(f"  f{l['frame']:4d}  {l['studs_s']:5.1f} st/s = {l['corps_s']:4.2f} corps/s  virage {l['virage']:4d} °/s  {l['etat']}")
    return res


def main(chemin, noms=()):
    d = json.load(open(chemin))
    fps = d.get("fps", 60)
    out = []
    for e in d.get("events", []):
        r = e.get("recette")
        if not isinstance(r, dict):
            continue
        for L in r.get("couches", []):
            if L.get("type") == "serpent" and (not noms or L.get("nom") in noms):
                out.append(allure(L, fps, e["frame"] + L.get("t0", 0) * fps))
    return out


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
    else:
        main(sys.argv[1], sys.argv[2:])
