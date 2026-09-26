"""
CARTE DES CHANGEMENTS entre deux exports d'une même scène, écrite en MOTS DE
CORPS, phase par phase. Ceci mesure le CHANGEMENT, pas la QUALITÉ.

Pourquoi elle existe (2026-09-26, chantier « nouveaux yeux », SYNTHESE_YEUX
rang 3) : Milan a dit QUATRE fois « je vois aucun changement » (motif
`aucun_changement`). Le cerveau annonçait des versions « refaites » sans
savoir ce qui avait vraiment bougé, ni où, ni si ça se voyait depuis la caméra
du plan. Et une différence de pixels ne suit pas ce que Milan perçoit (v2 -> v3
« aucun changement » change autant de pixels que v4 -> v5 « un peu mieux »,
SYNTHESE_YEUX §6).

Ce qu'elle mesure :
- les deux versions alignées sur le CONTACT, puis par morceaux entre les
  marqueurs communs (départ, charge, frappe, contact...) : une phase plus
  courte dans B est comparée à la même phase de A, étirée ;
- par phase, avec les grandeurs de `geo_pose.descripteurs` (repère du coup ;
  avant = vers la cible) : buste (tourné, penché), hanches, chaque poing
  (plus haut, plus en avant, plus à droite), écart entre les mains, pieds,
  tête ; une phrase quand l'écart moyen ou le pire écart dépasse un seuil
  d'AFFICHAGE (réglable, écrit dans la sortie ; ce n'est pas un seuil de
  perception) ;
- chaque bras devant / derrière / dans le plan du torse (main dans le repère
  du torse) : « le bras gauche passe de devant à derrière le torse » ;
- le moment où le buste se dévisse et où le poing part (image où la moitié
  du trajet de la phase est faite), en images d'écart ;
- si les staging.json sont donnés : les coupes de caméra de chaque version,
  et le déplacement À L'ÉCRAN du poing et de la tête, en % de la hauteur
  d'image, de deux façons : « vu » (chaque version par SA caméra) et
  « animation seule » (les deux par la caméra de B).

Ce qu'elle NE voit PAS : si c'est mieux (v5 -> v6 est le plus gros changement
mesuré, et c'est la version « c trjs pas bon ») ; ce que Milan regarde
(il juge à vitesse réelle, au cadrage réel, avec le son) ; les effets, le
décor, la secousse de caméra ; la victime ; les seuils ne sont pas ceux de
l'œil humain. Elle ne note pas, ne classe pas, ne bloque rien.

Testée le 2026-09-26 sur « Un seul coup » v1 -> v6 (anciens exports tirés de
git : `--demo-un-seul-coup`), confrontée aux mots de Milan, sans forcer :
- v2 -> v3 (« Je vois aucun changement ») : GROS changements de pose (poing
  droit 2,5 studs plus en avant pendant l'élan ; buste 29° plus tourné vers
  l'arrière en charge ; main gauche passée de devant à derrière le torse),
  mais peu À L'ÉCRAN (« vu », % de la hauteur d'image) : 1-6 % pendant l'élan
  (le poing avance presque dans l'axe de la caméra), 13-15 % en charge,
  4-10 % à la frappe ; pose au contact identique (0,00 stud) ;
- v3 -> v4 : 9-18 % en charge (buste 33° plus penché) ; ses mots sur la v4
  ne disent pas s'il a vu le changement (aucun test possible) ;
- v4 -> v5 (« un peu mieux mais c'est pas bon encore ») : 16-40 % en charge,
  26-58 % à la frappe, une coupe ajoutée (i279) ;
- v5 -> v6 (« c trjs pas bon », puis « le placement du bras sur tout ») :
  15-42 % en charge, deux coupes ajoutées ; main gauche passée de derrière à
  devant le torse pendant la charge ; au contact, buste 26° moins tourné et
  poing gauche 1,7 stud plus à sa gauche.
Lecture : l'écart de POSE en studs ne sépare pas v2 -> v3 de v4 -> v5 (même
ordre de grandeur, voire plus pour v2 -> v3). Le déplacement À L'ÉCRAN, par
la caméra de chaque version, les range dans l'ordre de Milan (v2 -> v3 le
plus faible) ; sur 2-3 passages comparables, c'est un signal, pas une preuve.
Pour « le placement du bras », la carte montre des CANDIDATS (bras gauche
croisé devant pendant la charge ; bras droit, lui, reste devant le torse
dans les deux) ; elle ne dit pas lequel Milan regardait. Et rien ici ne dit
« mieux » : v5 -> v6 est un des plus gros changements, noté « pas bon ».

Usage :
  python3 outils/carte_changements.py --a A.rbxmx --b B.rbxmx [--scene-a sA.json --scene-b sB.json]
        [--staging-a stA.json --staging-b stB.json] [--json sortie.json]
  en série (v1 -> v2 -> v3 ...) :
  python3 outils/carte_changements.py --version v1=att.rbxmx,scene.json,staging.json --version v2=...
  réglages d'affichage : --seuil-stud 0.25 --seuil-deg 8 --seuil-ecran 3
"""
import argparse
import json
import os
import subprocess
import sys
import tempfile

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", ".."))
import geo_pose as G  # noqa: E402
import vues as VU  # noqa: E402

FPS = 60
SEUILS = {"stud": 0.25, "deg": 8.0, "ecran": 3.0, "images": 3}

# grandeurs : (clé, mot de corps, unité, mot si + , mot si -)
GRANDEURS = [
    ("buste_lacet", "buste", "deg", "tourné de plus vers sa gauche (épaule droite plus avancée)",
     "tourné de plus vers sa droite (épaule droite plus reculée)"),
    ("buste_penche", "buste", "deg", "plus penché en avant", "plus redressé"),
    ("buste_cote", "buste", "deg", "plus penché vers sa droite", "plus penché vers sa gauche"),
    ("hanche", "hanches", "stud", "plus hautes", "plus basses"),
    ("RA_haut", "poing droit", "stud", "plus haut", "plus bas"),
    ("RA_avant", "poing droit", "stud", "plus en avant (vers la cible)", "plus en arrière"),
    ("RA_droite", "poing droit", "stud", "plus à sa droite", "plus à sa gauche"),
    ("LA_haut", "poing gauche", "stud", "plus haut", "plus bas"),
    ("LA_avant", "poing gauche", "stud", "plus en avant (vers la cible)", "plus en arrière"),
    ("LA_droite", "poing gauche", "stud", "plus à sa droite", "plus à sa gauche"),
    ("mains", "mains", "stud", "plus écartées", "plus proches"),
    ("RL_avant", "pied droit", "stud", "plus en avant", "plus en arrière"),
    ("LL_avant", "pied gauche", "stud", "plus en avant", "plus en arrière"),
    ("RL_haut", "pied droit", "stud", "plus haut", "plus bas"),
    ("LL_haut", "pied gauche", "stud", "plus haut", "plus bas"),
    ("pieds", "pieds", "stud", "plus écartés", "plus serrés"),
    ("tete_lacet", "tête", "deg", "tournée plus vers sa gauche", "tournée plus vers sa droite"),
    ("tete_el", "tête", "deg", "plus relevée", "plus baissée"),
]
COTE = {"RA": ("Right Arm", "bras droit"), "LA": ("Left Arm", "bras gauche")}


def grandeurs(w):
    d = G.descripteurs(w)
    g = {"buste_lacet": d["buste"]["lacet"], "buste_penche": d["buste"]["penche_avant"],
         "buste_cote": d["buste"]["penche_cote"], "hanche": d["hanche"]}
    for k in ("RA", "LA"):
        a, r, h = d["poing"][k]
        g[f"{k}_avant"], g[f"{k}_droite"], g[f"{k}_haut"] = a, r, h
    g["mains"] = float(np.linalg.norm(np.array(d["poing"]["RA"]) - np.array(d["poing"]["LA"])))
    for k in ("RL", "LL"):
        a, r, h = d["pieds"][k]
        g[f"{k}_avant"], g[f"{k}_haut"] = a, h
    g["pieds"] = float(np.linalg.norm(np.array(d["pieds"]["RL"])[:2] - np.array(d["pieds"]["LL"])[:2]))
    if "tete" in d:
        g["tete_lacet"], g["tete_el"] = d["tete"]["coup"][0], d["tete"]["coup"][1]
    return g


def cote_torse(w, bras):
    """Main devant / derrière / dans le plan du torse (repère du torse ;
    demi-épaisseur du torse 0,5 stud)."""
    Rt, pt = w["Torso"]
    q = np.asarray(Rt).T @ (G.bout(w, COTE[bras][0]) - np.asarray(pt))
    av = -q[2]
    return "devant le torse" if av > 0.5 else ("derrière le torse" if av < -0.5 else "à hauteur du torse (ni devant ni derrière)")


def charger(att, scene=None, staging=None, fps=FPS):
    m = VU.lire_kfseq(att, fps)
    v = {"nom": os.path.basename(att), "mondes": m, "marqueurs": {}, "contact": None, "staging": None}
    if scene:
        s = json.load(open(scene))
        v["marqueurs"] = {n: int(f) for n, f in s.get("markers", [])}
        v["contact"] = s.get("contact_f", v["marqueurs"].get("contact"))
    if staging:
        v["staging"] = json.load(open(staging))
        if not v["marqueurs"]:
            v["marqueurs"] = {n: int(f) for n, f in v["staging"].get("markers", [])}
            v["contact"] = v["staging"].get("contact_f")
    return v


def alignement(va, vb):
    """Couples (image B, image A) : contact + marqueurs communs, monotones."""
    cm = [n for n in vb["marqueurs"] if n in va["marqueurs"]]
    paires = sorted((vb["marqueurs"][n], va["marqueurs"][n], n) for n in cm)
    if not paires and vb["contact"] is not None and va["contact"] is not None:
        paires = [(vb["contact"], va["contact"], "contact")]
    garde = []
    for p in paires:
        if not garde or (p[0] > garde[-1][0] and p[1] > garde[-1][1]):
            garde.append(p)
    return garde or [(0, 0, "début")]


def a_de_b(paires, fb):
    xb = [p[0] for p in paires]
    xa = [p[1] for p in paires]
    if fb <= xb[0]:
        return fb + (xa[0] - xb[0])
    if fb >= xb[-1]:
        return fb + (xa[-1] - xb[-1])
    return float(np.interp(fb, xb, xa))


def phases(vb, de=None, a=None):
    mk = sorted(vb["marqueurs"].items(), key=lambda x: x[1])
    n = len(vb["mondes"]) - 1
    out = []
    for i, (nom, f0) in enumerate(mk):
        f1 = mk[i + 1][1] if i + 1 < len(mk) else n
        if nom == "contact":
            out.append(("au contact", f0, f0))
            if f1 > f0 + 1:
                out.append(("après le contact", f0 + 1, f1))
            continue
        if f1 > f0:
            out.append((nom, f0, f1 - 1))
    if not out:
        out = [("tout", 0, n)]
    return [p for p in out if (de is None or p[2] >= de) and (a is None or p[1] <= a)]


def _fmt(x, unite):
    s = f"{abs(x):.2f}".replace(".", ",") if unite == "stud" else f"{abs(x):.0f}"
    return s + (" stud" if unite == "stud" else "°")


def _projete(p, cam, aspect=16 / 9):
    oeil, cible, fov = cam
    f = np.asarray(cible) - np.asarray(oeil)
    f = f / np.linalg.norm(f)
    r = np.cross(f, [0, 1.0, 0])
    r = r / np.linalg.norm(r)
    u = np.cross(r, f)
    v = np.asarray(p) - np.asarray(oeil)
    z = v @ f
    if z <= 0.3:
        return None
    k = 1.0 / np.tan(np.radians(fov) / 2)
    x = np.array([k * (v @ r) / z / 2, k * (v @ u) / z / 2])   # en hauteurs d'image (1 = toute la hauteur)
    if abs(x[0]) > aspect / 2 or abs(x[1]) > 0.5:
        return None                                              # hors champ
    return x


def _coupes(st, f0, f1):
    return [c[0] for c in st["camera"] if c[4] == "cut" and f0 <= c[0] <= f1]


def comparer(va, vb, seuils=None, de=None, a=None):
    s = dict(SEUILS, **(seuils or {}))
    paires = alignement(va, vb)
    nA, nB = len(va["mondes"]), len(vb["mondes"])
    ga_cache, gb_cache = {}, {}

    def gA(f):
        f = int(min(max(round(f), 0), nA - 1))
        if f not in ga_cache:
            ga_cache[f] = grandeurs(va["mondes"][f])
        return ga_cache[f]

    def gB(f):
        if f not in gb_cache:
            gb_cache[f] = grandeurs(vb["mondes"][f])
        return gb_cache[f]

    rapport = {"a": va["nom"], "b": vb["nom"], "alignement": [[p[2], p[0], p[1]] for p in paires],
               "seuils_affichage": s, "phases": []}
    for nom, f0, f1 in phases(vb, de, a):
        f1 = min(f1, nB - 1)
        if f0 > f1:
            continue
        fbs = list(range(f0, f1 + 1))
        fas = [a_de_b(paires, fb) for fb in fbs]
        ph = {"phase": nom, "b": [f0, f1], "a": [int(round(fas[0])), int(round(fas[-1]))], "phrases": [], "ecarts": {}}
        for cle, corps, unite, plus, moins in GRANDEURS:
            if cle not in gB(f0):
                continue
            d = np.array([gB(fb)[cle] - gA(fa)[cle] for fb, fa in zip(fbs, fas)])
            moy, k = float(d.mean()), int(np.argmax(np.abs(d)))
            seuil = s["stud"] if unite == "stud" else s["deg"]
            ph["ecarts"][cle] = {"moyen": round(moy, 3), "pire": round(float(d[k]), 3), "pire_image_b": fbs[k]}
            if abs(moy) >= seuil or abs(d[k]) >= seuil:
                if len(fbs) == 1:
                    txt = f"{corps} {_fmt(d[k], unite)} {plus if d[k] > 0 else moins}"
                else:
                    txt = f"{corps} {_fmt(moy, unite)} {plus if moy > 0 else moins} en moyenne"
                    if abs(d[k] - moy) >= seuil / 2:
                        txt += f" (au plus {_fmt(d[k], unite)} {plus if d[k] > 0 else moins} à i{fbs[k]})"
                ph["phrases"].append((abs(moy) / seuil, txt))
        # bras devant / derrière le torse
        for bras, (_p, mot) in COTE.items():
            ca = [cote_torse(va["mondes"][int(min(max(round(fa), 0), nA - 1))], bras) for fa in fas]
            cb = [cote_torse(vb["mondes"][fb], bras) for fb in fbs]
            da, db = max(set(ca), key=ca.count), max(set(cb), key=cb.count)
            ph["ecarts"][f"{bras}_torse"] = {"a": da, "b": db}
            if da != db:
                ph["phrases"].append((9.0, f"{mot} : main {da} dans A -> {db} dans B (la plupart des images de la phase)"))
        # quand ça part : moitié du trajet de la phase
        if len(fbs) >= 6:
            for cle, mot in (("buste_lacet", "le buste tourne"), ("RA_avant", "le poing droit avance"),
                             ("LA_avant", "le poing gauche avance")):
                ta, tb = _mi_trajet([gA(fa)[cle] for fa in fas]), _mi_trajet([gB(fb)[cle] for fb in fbs])
                seuil = s["deg"] if cle.startswith("buste") else s["stud"]
                ampa = abs(gA(fas[-1])[cle] - gA(fas[0])[cle])
                ampb = abs(gB(fbs[-1])[cle] - gB(fbs[0])[cle])
                if ta is None or tb is None or min(ampa, ampb) < seuil:
                    continue
                # en images de B : image de B où A est à mi-trajet (via l'alignement)
                fa_mi = fas[0] + ta * (fas[-1] - fas[0]) / max(1, len(fas) - 1)
                fb_mi = f0 + tb
                fb_de_a = f0 + (fa_mi - fas[0]) * (len(fbs) - 1) / max(1e-6, fas[-1] - fas[0])
                dt = fb_mi - fb_de_a
                ph["ecarts"][f"mi_trajet_{cle}"] = {"a_image": round(fa_mi, 1), "b_image": round(fb_mi, 1)}
                if abs(dt) >= s["images"]:
                    ph["phrases"].append((abs(dt) / s["images"],
                                          f"{mot} {abs(dt):.0f} images {'plus tard' if dt > 0 else 'plus tôt'} "
                                          f"(mi-trajet i{fb_mi:.0f} dans B, i{fa_mi:.0f} dans A)"))
        # caméra et écran
        if va["staging"] and vb["staging"]:
            ca_, cb_ = _coupes(va["staging"], int(min(fas)), int(max(fas))), _coupes(vb["staging"], f0, f1)
            ph["coupes"] = {"a": ca_, "b": cb_}
            if len(ca_) != len(cb_) or any(abs(x - y) > 1 for x, y in zip(ca_, cb_)):
                ph["phrases"].append((5.0, f"caméra : coupes {ca_ or 'aucune'} dans A, {cb_ or 'aucune'} dans B"))
            for part, mot in (("Right Arm", "poing droit"), ("Left Arm", "poing gauche"), ("Head", "tête")):
                vu, anim, hors = [], [], []
                for fb, fa in zip(fbs, fas):
                    fa_i = int(min(max(round(fa), 0), nA - 1))
                    wa, wb = va["mondes"][fa_i], vb["mondes"][fb]
                    pa = G.bout(wa, part) if part != "Head" else np.asarray(wa["Head"][1])
                    pb = G.bout(wb, part) if part != "Head" else np.asarray(wb["Head"][1])
                    camb = G.camera_plan(vb["staging"], fb)
                    cama = G.camera_plan(va["staging"], fa_i)
                    xa, xb, xa2 = _projete(pa, cama), _projete(pb, camb), _projete(pa, camb)
                    # « vu » : présent à l'écran dans les deux ; hors champ d'un seul côté = changement noté à part
                    if xa is not None and xb is not None:
                        vu.append(float(np.linalg.norm(xb - xa)))
                    elif (xa is None) != (xb is None):
                        hors.append(fb)
                    if xa2 is not None and xb is not None:
                        anim.append(float(np.linalg.norm(xb - xa2)))
                if vu or anim:
                    mv = 100 * float(np.mean(vu)) if vu else None
                    ma = 100 * float(np.mean(anim)) if anim else None
                    ph["ecarts"][f"ecran_{mot}"] = {"vu_pct": None if mv is None else round(mv, 1),
                                                   "animation_seule_pct": None if ma is None else round(ma, 1),
                                                   "images_dans_le_champ_d_une_seule": len(hors)}
                    if max(mv or 0, ma or 0) >= s["ecran"]:
                        t_vu = "hors champ" if mv is None else f"{mv:.0f} %"
                        t_an = "hors champ" if ma is None else f"{ma:.0f} %"
                        ph["phrases"].append((max(mv or 0, ma or 0) / s["ecran"] / 3,
                                              f"à l'écran, {mot} : écart moyen {t_vu} de la hauteur d'image (vu : chaque "
                                              f"version par sa caméra) / {t_an} (animation seule : caméra de B)"
                                              + (f" ; visible dans une seule version sur {len(hors)} images" if hors else "")))
        ph["phrases"] = [t for _k, t in sorted(ph["phrases"], key=lambda x: -x[0])]
        if not ph["phrases"]:
            pire = max((abs(v["pire"]) for k, v in ph["ecarts"].items() if isinstance(v, dict) and "pire" in v
                        and not k.startswith(("buste", "tete"))), default=0.0)
            ph["phrases"] = [f"rien au-dessus des seuils d'affichage (pire écart de position {pire:.2f} stud)"]
        rapport["phases"].append(ph)
    return rapport


def _mi_trajet(x):
    """Indice (fractionnaire) où x a fait la moitié du chemin de x[0] à x[-1]."""
    x = np.asarray(x, float)
    a, b = x[0], x[-1]
    if abs(b - a) < 1e-9:
        return None
    m = (a + b) / 2
    s = np.sign(b - a)
    for i in range(1, len(x)):
        if s * (x[i] - m) >= 0:
            u = (m - x[i - 1]) / (x[i] - x[i - 1]) if x[i] != x[i - 1] else 0.0
            return i - 1 + float(np.clip(u, 0, 1))
    return None


def imprimer(r, maxi=6):
    print(f"=== {r['a']} (A) -> {r['b']} (B) ; alignement (marqueur, image B, image A) : "
          + ", ".join(f"{n} {b}->{a}" for n, b, a in r["alignement"]))
    for ph in r["phases"]:
        print(f"  [{ph['phase']}] B i{ph['b'][0]}-{ph['b'][1]} / A i{ph['a'][0]}-{ph['a'][1]}")
        for t in ph["phrases"][:maxi]:
            print(f"     - {t}")
        if len(ph["phrases"]) > maxi:
            print(f"     (+{len(ph['phrases']) - maxi} autres dans le JSON)")
    s = r["seuils_affichage"]
    print(f"  seuils d'AFFICHAGE : {s['stud']} stud, {s['deg']}°, {s['ecran']} % d'écran, {s['images']} images "
          "(pas des seuils de perception). Ceci mesure le changement, pas la qualité.")


# ------------------------------------------------------------ démo : les versions d'Un seul coup
VERSIONS_USC = [("v1", "6fcfc4e"), ("v2", "7bb9526"), ("v3", "7e40a57"), ("v4", "8b768e4"),
                ("v5", "f8601ba"), ("v6", "eb816bf")]
MOTS_MILAN = {  # mots EXACTS (corpus/milan_verbatim.jsonl, motifs.json), pour la confrontation
    "v2": "départ ultra rapide validé ; « tjrs pas pour le poing chargé je pense que tu capte pas le truck de poing chargé » (7/10)",
    "v3": "« Je vois aucun changement je ne sais si c un bug ou si on ne sait tjrs pas compris »",
    "v4": "« dans aucune le bras est tendu derrière » ; « le pose des jambe est un peu  trop abusé »",
    "v5": "« c'est un peu mieux mais c'est pas bon encore » (7,5)",
    "v6": "« c trjs pas bon » ; puis « Ce qui était tues pas bon c le placement du bras sur tout »",
}


def extraire_git(dossier, depot=None):
    depot = depot or os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
    chemins = {}
    for v, c in VERSIONS_USC:
        for f in ("usc_attaquant.rbxmx", "scene.json", "staging.json"):
            dst = os.path.join(dossier, f"{v}_{f}")
            if not os.path.exists(dst):
                data = subprocess.run(["git", "-C", depot, "show", f"{c}:experiments/r6_un_seul_coup/output/{f}"],
                                      capture_output=True, check=True).stdout
                open(dst, "wb").write(data)
            chemins.setdefault(v, []).append(dst)
    return chemins


def main():
    ap = argparse.ArgumentParser(description="carte des changements entre deux exports (mesure, pas verdict)")
    ap.add_argument("--a")
    ap.add_argument("--b")
    ap.add_argument("--scene-a")
    ap.add_argument("--scene-b")
    ap.add_argument("--staging-a")
    ap.add_argument("--staging-b")
    ap.add_argument("--version", action="append", default=[], help="nom=attaquant.rbxmx[,scene.json[,staging.json]]")
    ap.add_argument("--demo-un-seul-coup", action="store_true", help="v1 -> v6 d'Un seul coup tirés de git")
    ap.add_argument("--dossier", help="où extraire les anciens exports (défaut : dossier temporaire)")
    ap.add_argument("--de", type=int)
    ap.add_argument("--jusqua", type=int)
    ap.add_argument("--seuil-stud", type=float, default=SEUILS["stud"])
    ap.add_argument("--seuil-deg", type=float, default=SEUILS["deg"])
    ap.add_argument("--seuil-ecran", type=float, default=SEUILS["ecran"])
    ap.add_argument("--max", type=int, default=6, help="phrases affichées par phase")
    ap.add_argument("--json")
    a = ap.parse_args()
    seuils = {"stud": a.seuil_stud, "deg": a.seuil_deg, "ecran": a.seuil_ecran}
    serie = []
    if a.demo_un_seul_coup:
        d = a.dossier or tempfile.mkdtemp(prefix="carte_usc_")
        for v, ch in extraire_git(d).items():
            serie.append((v, charger(*ch)))
    elif a.version:
        for x in a.version:
            nom, reste = x.split("=", 1)
            ch = reste.split(",")
            v = charger(ch[0], ch[1] if len(ch) > 1 else None, ch[2] if len(ch) > 2 else None)
            v["nom"] = nom
            serie.append((nom, v))
    else:
        va = charger(a.a, a.scene_a, a.staging_a)
        vb = charger(a.b, a.scene_b, a.staging_b)
        serie = [("A", va), ("B", vb)]
    tout = []
    for (na, va), (nb, vb) in zip(serie, serie[1:]):
        va["nom"], vb["nom"] = na, nb
        r = comparer(va, vb, seuils, a.de, a.jusqua)
        imprimer(r, a.max)
        if a.demo_un_seul_coup and nb in MOTS_MILAN:
            print(f"  mots de Milan sur {nb} : {MOTS_MILAN[nb]}")
        tout.append(r)
    if a.json:
        json.dump(tout, open(a.json, "w"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
