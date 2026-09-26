"""
IMPACT : où le poing arrive SUR la victime, avec quelle pente, et ce que font
les pieds plantés. Des chiffres affichés, jamais un verdict.

Pourquoi il existe (2026-09-26, chantier « nouveaux yeux », SYNTHESE_YEUX
rangs 5 et 7) : le motif `vers_le_bas` (7 citations dans corpus/motifs.json
au 2026-09-26 ; ses mots exacts, par ex. « le perso frappait vers le bas »,
« les coup parte tjrs du bas »), et le cerveau n'avait pas UN chiffre pour
le vérifier sur la victime elle-même : on mesurait le bras de l'attaquant
seul, dans son repère. Et la mesure du glissement des pieds existait déjà
(`audit.contact_report`) sans être appelée sur « Un seul coup ».

Ce qu'il mesure, à l'image du contact (et aux images voisines) :
- le poing (bout du bras qui frappe = centre de la face du bas du bloc) dans
  le repère du TORSE DE LA VICTIME : x vers SA droite, y vers le haut
  (0 = centre du torse, +1 = ses épaules, -1 = sa ceinture), avant = + devant
  sa poitrine ; « écart à la poitrine » = y - 0,5 (la POITRINE est définie ici
  comme le milieu de la moitié haute du torse, y = +0,5 ; une définition, pas
  une norme) ;
- la pente du BRAS (épaule -> poing, monde ; + = monte, - = descend) ;
- la pente du TRAJET du poing sur les n dernières images avant le contact
  (d'où il arrive : un poing à plat qui arrive d'en haut « frappe vers le bas »
  autrement qu'un bras incliné) ;
- la vitesse du poing à l'arrivée, le buste de l'attaquant (lacet, penché) ;
- le glissement des pieds plantés, avec DEUX définitions écrites à côté du
  chiffre (la même anim donne 12 studs ou 1,37 selon la définition,
  SYNTHESE_YEUX §1.7) :
    A. `audit.contact_report` (code existant) : pied = centre de la face du
       bas du bloc jambe ; planté = hauteur < 0,02 stud ET |vitesse
       verticale| < 0,5 stud/s ; glissement = plus grand écart horizontal
       depuis le début de l'appui ;
    B. coin le plus bas du bloc jambe ; planté = hauteur < 0,1 stud ET
       |vitesse verticale| < 0,5 stud/s ; dérive max et chemin parcouru.

Ce qu'il NE voit PAS : la caméra (le même contact peut se LIRE « vers le
bas » depuis une contre-plongée, ou pas) ; le mouvement avant le contact
au-delà de n images ; les effets ; si un glissement est voulu (une glissade)
ou un patin : il faut le regarder à vitesse réelle
(`outils/cote_a_cote.py`) ; si le chiffre compte pour Milan : il ne dit
jamais « bon » ou « mauvais ».

Usage :
  python3 outils/impact.py --attaquant A.rbxmx --victime V.rbxmx [--scene scene.json]
        [--contact 283] [--distance 16] [--bras RA|LA] [--json sortie.json]
  plusieurs versions d'une même scène (une ligne chacune) :
  python3 outils/impact.py --version v5=A5.rbxmx,V5.rbxmx,scene5.json --version v6=...
"""
import argparse
import itertools
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", ".."))
import geo_pose as G  # noqa: E402
import vues as VU  # noqa: E402

FPS = 60
POITRINE_Y = 0.5
BRAS = {"RA": "Right Arm", "LA": "Left Arm"}


def charger(attaquant, victime, distance=16.0, fps=FPS):
    """-> (mondes attaquant, mondes victime), un monde par image, la victime
    placée comme dans nos scènes (geo_pose.racine_victime)."""
    ha = (np.eye(3), np.array([0.0, 3.0, 0.0]))
    A = VU.lire_kfseq(attaquant, fps, root=ha)
    V = VU.lire_kfseq(victime, fps, root=G.racine_victime(distance)) if victime else None
    return A, V


def _pente(v):
    v = np.asarray(v, float)
    n = np.linalg.norm(v)
    return float(np.degrees(np.arcsin(np.clip(v[1] / n, -1, 1)))) if n > 1e-9 else 0.0


def mesurer_contact(A, V, f, bras=None, n_trajet=4, fps=FPS):
    """A, V : listes de mondes ; f : image du contact. -> dict de mesures."""
    f = min(f, len(A) - 1, len(V) - 1)
    wa, wv = A[f], V[f]
    Rv, pv = wv["Torso"]
    Rv, pv = np.asarray(Rv), np.asarray(pv)
    if bras is None:
        bras = min(BRAS, key=lambda k: np.linalg.norm(G.bout(wa, BRAS[k]) - pv))
    part = BRAS[bras]
    poing = G.bout(wa, part)
    q = Rv.T @ (poing - pv)                       # repère du torse de la victime
    epaule = G.haut(wa, part)
    f0 = max(0, f - n_trajet)
    trajet = poing - G.bout(A[f0], part)
    d = G.descripteurs(wa)
    dans = bool(abs(q[0]) < 1 and abs(q[1]) < 1 and abs(q[2]) < 0.5)
    return {
        "image": f, "bras": bras,
        "poing_repere_victime": {"droite_victime": round(float(q[0]), 2), "haut": round(float(q[1]), 2),
                                 "devant_poitrine": round(float(-q[2]), 2)},
        "ecart_a_la_poitrine": round(float(q[1] - POITRINE_Y), 2),
        "poing_dans_le_torse": dans,
        "pente_bras_deg": round(_pente(poing - epaule), 1),
        "pente_trajet_deg": round(_pente(trajet), 1) if np.linalg.norm(trajet) > 1e-6 else None,
        "trajet_sur_images": f - f0,
        "vitesse_poing_studs_s": round(float(np.linalg.norm(trajet) / max(1, f - f0) * fps), 1),
        "hauteur_poing_monde": round(float(poing[1]), 2),
        "hauteur_poitrine_victime_monde": round(float((pv + Rv @ np.array([0, POITRINE_Y, 0]))[1]), 2),
        "buste_attaquant": d["buste"],
        "hanche_attaquant": d["hanche"],
    }


class _Clip:
    """Adaptateur minimal pour audit.contact_report (parts, t, dt, tip)."""

    def __init__(self, mondes, fps=FPS):
        self.parts = ["Right Leg", "Left Leg"]
        self.t = np.arange(len(mondes)) / fps
        self.dt = 1.0 / fps
        self._m = mondes

    def tip(self, part):
        return np.array([G.bout(w, part) for w in self._m])


def glissement_audit(mondes, fps=FPS):
    """Définition A (audit.contact_report, code existant du dépôt)."""
    from animator_brain import audit
    return audit.contact_report(_Clip(mondes, fps))


def glissement_coin(mondes, eps=0.1, vy_eps=0.5, fps=FPS):
    """Définition B : coin le plus bas du bloc jambe."""
    C = np.array(list(itertools.product((-.5, .5), (-1, 1), (-.5, .5))))
    out = {}
    for leg in ("Right Leg", "Left Leg"):
        low = []
        for w in mondes:
            R, p = w[leg]
            pts = (np.asarray(R) @ C.T).T + np.asarray(p)
            low.append(pts[np.argmin(pts[:, 1])])
        low = np.array(low)
        y = low[:, 1]
        vy = np.gradient(y) * fps
        plant = (y < eps) & (np.abs(vy) < vy_eps)
        runs, i = [], 0
        while i < len(mondes):
            if plant[i]:
                j = i
                while j + 1 < len(mondes) and plant[j + 1]:
                    j += 1
                if j > i:
                    h = low[i:j + 1][:, [0, 2]]
                    dd = np.linalg.norm(h - h[0], axis=1)
                    runs.append({"f0": i, "f1": j, "t0": round(i / fps, 2), "t1": round(j / fps, 2),
                                 "derive_max_studs": round(float(dd.max()), 3),
                                 "chemin_studs": round(float(np.linalg.norm(np.diff(h, axis=0), axis=1).sum()), 3)})
                i = j + 1
            else:
                i += 1
        out[leg] = {"hauteur_min": round(float(y.min()), 3), "appuis": runs,
                    "pire_derive_studs": max((r["derive_max_studs"] for r in runs), default=0.0)}
    return out


DEFINITIONS = {
    "A": "audit.contact_report : centre de la face du bas ; planté = y < 0,02 ET |vy| < 0,5 stud/s ; glissement = écart horizontal max depuis le début de l'appui",
    "B": "coin le plus bas du bloc ; planté = y < 0,1 ET |vy| < 0,5 stud/s ; dérive = écart horizontal max depuis le début de l'appui",
}


def rapport(A, V, contact, bras=None, voisins=(-2, 0, 2)):
    return {"contact": [mesurer_contact(A, V, contact + k, bras) for k in voisins],
            "pieds": {"definitions": DEFINITIONS, "A": glissement_audit(A), "B": glissement_coin(A)}}


def ligne(nom, r):
    c = next((x for x in r["contact"] if x["image"] == r.get("_contact")), r["contact"][len(r["contact"]) // 2])
    p = c["poing_repere_victime"]
    pa, pb = r["pieds"]["A"], r["pieds"]["B"]
    na = sum(v["contacts"] for v in pa.values())
    nb = sum(len(v["appuis"]) for v in pb.values())
    ga = max(v["worst_skate_studs"] for v in pa.values())
    gb = max(v["pire_derive_studs"] for v in pb.values())
    return (f"{nom:>4} i{c['image']} {c['bras']} | poing haut {p['haut']:+.2f} (poitrine {c['ecart_a_la_poitrine']:+.2f}) "
            f"droite {p['droite_victime']:+.2f} devant {p['devant_poitrine']:+.2f}{' DANS le torse' if c['poing_dans_le_torse'] else ''} | "
            f"pente bras {c['pente_bras_deg']:+.0f}° trajet {c['pente_trajet_deg'] if c['pente_trajet_deg'] is None else format(c['pente_trajet_deg'], '+.0f')}° "
            f"({c['trajet_sur_images']} i, {c['vitesse_poing_studs_s']} studs/s) | buste lacet {c['buste_attaquant']['lacet']:+.0f} "
            f"penché {c['buste_attaquant']['penche_avant']:+.0f} | pieds : A {na} appui(s), pire {ga:.2f} stud / "
            f"B {nb} appui(s), pire {gb:.2f} stud")


def _scene(path):
    s = json.load(open(path))
    return s.get("contact_f"), s.get("distance", 16.0)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    ap.add_argument("--attaquant")
    ap.add_argument("--victime")
    ap.add_argument("--scene", help="scene.json de la production (contact_f, distance)")
    ap.add_argument("--contact", type=int)
    ap.add_argument("--distance", type=float)
    ap.add_argument("--bras", choices=list(BRAS))
    ap.add_argument("--version", action="append", default=[], help="nom=attaquant.rbxmx,victime.rbxmx[,scene.json]")
    ap.add_argument("--json")
    a = ap.parse_args()
    jobs = []
    if a.attaquant:
        jobs.append(("", a.attaquant, a.victime, a.scene))
    for v in a.version:
        nom, reste = v.split("=", 1)
        ch = reste.split(",")
        jobs.append((nom, ch[0], ch[1], ch[2] if len(ch) > 2 else None))
    tout = {}
    for nom, att, vic, sc in jobs:
        cf, dist = _scene(sc) if sc else (None, None)
        cf = a.contact if a.contact is not None else cf
        dist = a.distance if a.distance is not None else (dist or 16.0)
        if cf is None:
            sys.exit("contact inconnu : --contact <image> ou --scene scene.json")
        A, V = charger(att, vic, dist)
        r = rapport(A, V, cf, a.bras)
        r["_contact"] = cf
        tout[nom or os.path.basename(att)] = r
        print(ligne(nom or "", r))
        for c in r["contact"]:
            if c["image"] != cf:
                print(f"       i{c['image']} poing haut {c['poing_repere_victime']['haut']:+.2f} devant "
                      f"{c['poing_repere_victime']['devant_poitrine']:+.2f} pente bras {c['pente_bras_deg']:+.0f}°")
        for d in ("A", "B"):
            for leg, v in r["pieds"][d].items():
                runs = v["runs"] if d == "A" else v["appuis"]
                cle = "skate_max_studs" if d == "A" else "derive_max_studs"
                long_ = [x for x in runs if x[cle] >= 0.1]
                if long_:
                    print(f"       pieds {d} {leg}: " + " ; ".join(f"{x['t0']}-{x['t1']} s : {x[cle]}" for x in long_[:6]))
    print("définitions des pieds : A = " + DEFINITIONS["A"] + " ; B = " + DEFINITIONS["B"])
    print("poitrine = y +0,5 dans le torse de la victime (centre 0, épaules +1) ; pentes : + = monte, - = descend. "
          "Mesures sans verdict ; ne voit ni la caméra ni si un glissement est voulu.")
    if a.json:
        json.dump(tout, open(a.json, "w"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
