"""
RAPPORT DE REGARD : les outils de vigilance qu'on avait écrits, relancés
ENSEMBLE sur une version, pour savoir quoi regarder avant de la montrer.
NON BLOQUANT : aucun seuil ici ne dit qu'une version est bonne ou mauvaise.

Pourquoi (audit du 2026-09-26 §3.B-C et priorité 1 point 7 ; plan de
réorganisation §4.1, brique A9) : `corps_bras`, `audit.audit`, `perception`,
`geo_pose` existaient, mais personne ne les relançait depuis la migration
vers le rig V2.22 (le Dragon v9). Relancés à la main sur « Un seul coup » v5 :
torse figé 55/85 images pendant la charge, poing qui ralentit avant le
contact. Personne ne l'avait vu. Ce rapport les rebranche en une commande :
- `corps_bras.phase` entre marqueurs (qui porte le mouvement : buste ou bras) ;
- `audit.audit` via `corpus.to_samples` (overlap, arrêts simultanés, holds
  morts, discontinuités) ; le contrôle de pieds est refait avec un
  `contact_eps` réglé pour V2.22 (l'audit l'a montré : avec 0,02 stud, des
  pieds posés à 0,03 donnent un faux « rien à signaler ») ;
- `perception` : charge, torsion, arcs, silhouette / croix, pose d'impact,
  profil de frappe ;
- `geo_pose.descripteurs` à chaque marqueur (nombres d'animateur) ;
- espacement et vitesse du poing (courbe) ;
Sorties : un JSON, une planche PNG (silhouettes aux marqueurs, de profil et
de trois-quarts face, + courbe de vitesse du poing), et deux listes en
langage simple : « à REGARDER » (où poser l'œil) et « à DIRE à Milan »
(ce qu'on a mesuré, dit sans verdict ; c'est son œil qui juge). Principe de
Milan : « on apprend, pas de règles gravées dans la roche ». Les repères
chiffrés cités viennent des docstrings des outils (M1 pro, TSB, tutos) :
ils se lisent À CÔTÉ, pas comme des portes.

Usage :
  python3 outils/rapport_regard.py <attaquant.rbxmx> [frame=nom,frame=nom,...]
         [--bras R|L] [--png sortie.png] [--json sortie.json] [--preuve <production>]
  - sans marqueurs : ceux du fichier (KeyframeMarker) ; le marqueur nommé
    « contact » (sinon le dernier) est le contact ;
  - sorties par défaut : captures/verification/<date>-regard-<nom>.png/.json
    (la planche est une preuve : elle se committe avec le changement) ;
  - --preuve : ajoute une ligne `mesure_pose` (statut « valeurs ») au
    registre corpus/preuves.jsonl (outils/preuves.py).
Code de sortie : toujours 0.
"""
import datetime
import json
import os
import re
import sys
import xml.etree.ElementTree as ET

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
BRAIN = os.path.normpath(os.path.join(HERE, ".."))
ROOT = os.path.normpath(os.path.join(BRAIN, "..", "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(BRAIN, ".."))
import corps_bras as CB  # noqa: E402
import geo_pose as G  # noqa: E402
import vues as VU  # noqa: E402
from animator_brain import audit as A  # noqa: E402
from animator_brain import corpus as C  # noqa: E402
from animator_brain import perception as P  # noqa: E402

FPS = 60


# ------------------------------------------------------------ entrées
def lire_marqueurs(path):
    """[(frame, nom)] des KeyframeMarker du fichier (temps de leur Keyframe)."""
    out = []
    seq = ET.parse(path).getroot().find("Item")
    for kf in seq.findall("Item"):
        if kf.get("class") != "Keyframe":
            continue
        t = float(kf.find("Properties/float[@name='Time']").text)
        for m in kf.findall("Item"):
            if m.get("class") == "KeyframeMarker":
                out.append((int(round(t * FPS)), m.find("Properties/string[@name='Name']").text))
    return sorted(out)


def parser_marqueurs(args):
    """« 173=garde,214=arme » (un ou plusieurs arguments) -> [(173, 'garde'), ...]."""
    out = []
    for a in args:
        for x in a.split(","):
            if x.strip():
                f, nom = x.split("=", 1)
                out.append((int(f), nom.strip()))
    return sorted(out)


def _r(x, n=2):
    return None if x is None else round(float(x), n)


def _json(o):
    if isinstance(o, dict):
        return {str(k): _json(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_json(v) for v in o]
    if isinstance(o, np.ndarray):
        return _json(o.tolist())
    if isinstance(o, (np.floating,)):
        return float(o)
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, np.bool_):
        return bool(o)
    return o


# ------------------------------------------------------------ mesures
def mesurer(W, marqueurs, bras="Right Arm"):
    n = len(W)
    frames = [f for f, _ in marqueurs]
    noms = {f: nom for f, nom in marqueurs}
    c = next((f for f, nom in marqueurs if nom.lower() == "contact"), frames[-1])
    lo = frames[0]
    apres = min(n - 1, c + 30)
    rep = {"frames_du_clip": n, "bras": bras, "contact_f": c, "marqueurs": [[f, nom] for f, nom in marqueurs]}

    # 1. corps ou bras, entre marqueurs (et 30 images après le contact)
    bornes = frames + ([apres] if apres > frames[-1] else [])
    phases = []
    for a, b in zip(bornes, bornes[1:]):
        r = CB.phase(W, a, b)
        # même condition que l'alerte de corps_bras.main (« REGARDER »)
        r["torse_fige_et_bras_qui_bougent"] = bool(r["torse_fige"] > 0.4 * r["images"]
                                                    and r["bras_D"] + r["bras_G"] > 3 * r["torse"] + 20)
        phases.append({"de": noms.get(a, a), "a": noms.get(b, f"contact+{b - c}"), "f0": a, "f1": b,
                       **{k: (_r(v, 1) if isinstance(v, float) else v) for k, v in r.items()}})
    rep["corps_bras"] = phases

    # 2. audit du mouvement (fenêtre : 1er marqueur -> contact + 30)
    fen = [(f / FPS, W[f]) for f in range(lo, apres + 1)]
    au, clip, _sig = A.audit(C.to_samples(fen), C.brain_rig())
    pieds = {p: float(clip.tip(p)[:, 1].min()) for p in ("Right Leg", "Left Leg")}
    eps = max(0.02, min(pieds.values()) + 0.06)
    rep["audit"] = {
        "fenetre_f": [lo, apres],
        "overlap": au["overlap"],
        "arrets_simultanes": au["stop_clusters"],
        "holds_morts_fraction": au["frozen_fraction"],
        "discontinuites": {p: len(v.get("pops", [])) for p, v in au["pops"].items()},
        "planarite": au["planarity"],
        "pieds": {"hauteur_min_studs": {p: _r(v, 3) for p, v in pieds.items()},
                  "contact_eps_v222": _r(eps, 3),
                  "contacts": A.contact_report(clip, contact_eps=eps),
                  "equilibre": A.balance_report(clip, contact_eps=eps)},
        "note": "valeurs brutes de audit.py ; son verdict (TARGETS non calibrés) n'est pas repris",
    }

    # 3. perception
    arme = next((f for f, nom in marqueurs if nom.lower().startswith("arm")), frames[1] if len(frames) > 2 else lo)
    avant_c = [f for f in frames if f < c]
    detente = avant_c[-1] if avant_c else lo
    rep["perception"] = {
        "charge": P.charge(W, c, bras, n=c - lo),
        "torsion_buste_deg": P.torsion(W, arme, max(arme + 1, detente), c),
        "torsion_fenetre_charge_f": [arme, detente],
        "arcs_attaque": P.arcs(W, lo, c + 1),
        "arcs_poing": P.arcs(W, lo, c + 1, parts=(bras,)),
        "pose_impact": P.pose_impact(W, c, bras),
        "profil_frappe": P.profil_frappe(W, c, bras, n=max(12, c - detente)),
        "silhouette": {nom: P.silhouette(W[f]) for f, nom in marqueurs},
    }

    # 4. geo_pose aux marqueurs
    rep["geo_pose"] = {nom: {"f": f, "descripteurs": G.descripteurs(W[f]), "resume": G.resume(G.descripteurs(W[f]))}
                       for f, nom in marqueurs}

    # 5. espacement et vitesse du poing
    # fenêtre : du 1er marqueur (pas avant : un déplacement éclair du perso
    # avant la garde écraserait l'échelle) à contact + 45 ; la pointe est
    # cherchée entre le dernier marqueur avant le contact et le contact
    a0, b0 = lo, min(n - 1, c + 45)
    pts = np.array([P.tip(W[f], bras) for f in range(a0, b0 + 1)])
    v = np.r_[0.0, np.linalg.norm(np.diff(pts, axis=0), axis=1)]
    pic = (detente - a0) + int(np.argmax(v[detente - a0: c - a0 + 1]))
    rep["poing"] = {
        "fenetre_f": [a0, b0],
        "vitesse_studs_par_s": [_r(x * FPS, 2) for x in v],
        "espacement_studs_par_image_detente_contact": [_r(x, 3) for x in v[detente - a0: c - a0 + 1]],
        "pointe_avant_contact": {"f": a0 + pic, "studs_par_s": _r(v[pic] * FPS, 1)},
        "arrivee_au_contact_part_de_la_pointe": _r(v[c - a0] / v[pic], 2) if v[pic] > 0 else None,
        "approche_12f": P.approche(W, c, bras),
    }
    return rep


# ------------------------------------------------------------ à regarder / à dire
def lectures(rep):
    """(à_regarder, à_dire) : phrases simples, sans verdict."""
    reg, dire = [], []
    cote = "droit" if rep["bras"] == "Right Arm" else "gauche"
    for ph in rep["corps_bras"]:
        if ph["torse_fige_et_bras_qui_bougent"]:
            reg.append(f"{ph['de']} -> {ph['a']} (f{ph['f0']}-{ph['f1']}) : le buste est quasi immobile "
                       f"{ph['torse_fige']}/{ph['images']} images pendant que les bras tournent de "
                       f"{ph['bras_D'] + ph['bras_G']:.0f}° (buste {ph['torse']:.0f}°). Regarder si c'est une "
                       "tenue voulue ou « que les bras ».")
        elif ph["images"] >= 12 and ph["torse_fige"] >= 0.8 * ph["images"]:
            reg.append(f"{ph['de']} -> {ph['a']} (f{ph['f0']}-{ph['f1']}) : le buste est quasi immobile "
                       f"{ph['torse_fige']}/{ph['images']} images, les bras aussi (bras {ph['bras_D'] + ph['bras_G']:.0f}°, "
                       f"buste {ph['torse']:.0f}°). Tenue : regarder à vitesse réelle si elle vit ou si elle est figée.")
    charge = [ph for ph in rep["corps_bras"] if ph["f1"] <= rep["contact_f"]]
    if charge:
        fg = sum(p["torse_fige"] for p in charge); im = sum(p["images"] for p in charge)
        dire.append(f"Du 1er marqueur au contact, le buste est quasi immobile {fg} images sur {im} "
                    f"(il tourne de {sum(p['torse'] for p in charge):.0f}° au total ; le bras {cote} de "
                    f"{sum(p['bras_D' if cote == 'droit' else 'bras_G'] for p in charge):.0f}° par rapport au buste).")
    po = rep["poing"]
    arr = po["arrivee_au_contact_part_de_la_pointe"]
    if arr is not None:
        dire.append(f"Le poing va le plus vite à l'image {po['pointe_avant_contact']['f']} "
                    f"({po['pointe_avant_contact']['studs_par_s']} studs/s) et arrive au contact "
                    f"(image {rep['contact_f']}) à {int(round(100 * arr))} % de cette vitesse.")
        if arr < 0.8:
            reg.append(f"Le poing RALENTIT avant le contact ({int(round(100 * arr))} % de sa pointe à l'image "
                       "du contact) : regarder la courbe de vitesse sur la planche, à vitesse réelle.")
    ap = po["approche_12f"]
    if ap:
        dire.append(f"Sur les 3 dernières images avant le contact, le poing va en moyenne à "
                    f"{int(round(100 * ap['frein_3f_sur_pic']))} % de sa pointe ; {int(round(100 * ap['part_dernier_tiers']))} % "
                    "du trajet des 12 dernières images se fait dans leur dernier tiers (espacement).")
    pf = rep["perception"]["profil_frappe"]
    if pf:
        dire.append(f"Profil de la frappe : phase rapide de {pf['phase_rapide_f']} images, plateau {pf['plateau']} "
                    f"(1 = vitesse tenue), arrivée {pf['arrivee']} de la pointe. Repère lu dans le fichier TSB "
                    "(perception.profil_frappe) : poing à pleine vitesse en 1 image, tenue 2-3 images.")
    t = rep["perception"]["torsion_buste_deg"]
    dire.append(f"Entre la charge (images {rep['perception']['torsion_fenetre_charge_f'][0]}-"
                f"{rep['perception']['torsion_fenetre_charge_f'][1]}) et le contact, le buste pivote de {t:.0f}° "
                "(repère des tutos R6 cité par perception.torsion : ~90 à 180° sur un coup qui compte).")
    ch = rep["perception"]["charge"]
    if ch:
        dire.append(f"Charge : tenue immobile la plus longue {ch['tenue_f']} images, enroulement max du buste "
                    f"{ch['enroulement_buste_deg']:.0f}°, départ du poing en {ch['depart_f']} images.")
    croix = [nom for nom, s in rep["perception"]["silhouette"].items() if s["croix"]]
    if croix:
        reg.append("Silhouette en CROIX (buste droit, deux bras écartés à l'horizontale) à : " + ", ".join(croix)
                   + ". Regarder la silhouette noire de ce marqueur.")
    gp = rep["geo_pose"]
    cn = next((nom for f, nom in rep["marqueurs"] if f == rep["contact_f"]), None)
    if cn:
        d = gp[cn]["descripteurs"]
        k = "RA" if cote == "droit" else "LA"
        av, dr, ht = d["poing"][k]
        dire.append(f"Au contact : poing à {av:+.2f} stud devant le centre du torse, {ht:+.2f} en hauteur "
                    f"({'au-dessus' if ht >= 0 else 'au-dessous'} du centre du torse), buste penché de "
                    f"{d['buste']['penche_avant']:+.0f}° vers l'avant, lacet {d['buste']['lacet']:+.0f}°, "
                    f"hanche à {d['hanche']:.2f} (debout : 3,0).")
    pi = rep["perception"]["pose_impact"]
    dire.append(f"Pose d'impact : bras / ligne des épaules {pi['bras_epaules_deg']:.0f}°, torse détourné "
                f"{pi['torse_detourne_deg']:.0f}°, bras libre {pi['bras_libre']:+.2f}. Repères M1 pro cités par "
                "perception.pose_impact : 18-28°, 67-75°, -0,1 à 0,3.")
    ov = rep["audit"]["overlap"]
    avance = [k.split(" <-")[0] for k, v in ov.items() if v.get("n") and v.get("median_frames") is not None
              and v["median_frames"] <= 0 and "Arm" in k]
    if avance:
        reg.append("Chevauchement : " + ", ".join(avance) + " culmine(nt) en même temps que le buste ou AVANT lui "
                   "(retard médian ≤ 0 image). Regarder si le mouvement part bien du corps.")
    hm = rep["audit"]["holds_morts_fraction"]
    if hm:
        dire.append(f"Holds morts (tout le corps immobile) : {int(round(100 * hm))} % des images de la fenêtre.")
    asim = rep["audit"]["arrets_simultanes"]
    if asim.get("stops"):
        dire.append(f"Arrêts simultanés : {asim['clustered']} arrêts sur {asim['stops']} tombent à la même image "
                    "que ceux d'au moins 3 autres membres.")
    ps = rep["audit"]["pieds"]
    dire.append("Pieds : hauteur mini " + ", ".join(f"{p} {h}" for p, h in ps["hauteur_min_studs"].items())
                + f" stud (contact compté sous {ps['contact_eps_v222']}).")
    return reg, dire


# ------------------------------------------------------------ planche
ENCRE, ENCRE2, GRILLE, FOND, TRAIT = (30, 30, 34), (95, 95, 105), (225, 225, 230), (255, 255, 255), (37, 99, 170)


def cams(w):
    """Profil (côté droit du perso, qui regarde -Z) et trois-quarts face, centrées sur le torse."""
    p = w["Torso"][1]
    cible = np.array([p[0], 2.4, p[2]])
    return {"profil": (cible + np.array([14.0, 0.6, 0.0]), cible, 32.0),
            "3/4 face": (cible + np.array([9.0, 1.8, -11.0]), cible, 32.0)}


def courbe_vitesse(rep, larg, haut):
    im = Image.new("RGB", (larg, haut), FOND)
    d = ImageDraw.Draw(im)
    v = [x or 0.0 for x in rep["poing"]["vitesse_studs_par_s"]]
    a0 = rep["poing"]["fenetre_f"][0]
    g, dr, h0, b = 56, 16, 30, 28
    vmax = max(v) or 1.0
    e = 10 ** np.floor(np.log10(vmax / 4))
    pas = next(m * e for m in (1, 2, 2.5, 5, 10) if m * e * 4 >= vmax)     # 4 intervalles ronds
    top = 4 * pas
    X = lambda i: g + (larg - g - dr) * i / max(1, len(v) - 1)  # noqa: E731
    Y = lambda x: haut - b - (haut - b - h0) * x / top  # noqa: E731
    for k in range(0, 5):
        y = Y(top * k / 4)
        d.line([g, y, larg - dr, y], fill=GRILLE)
        d.text((4, y - 6), f"{top * k / 4:g}", fill=ENCRE2)
    dernier, rang = -1e9, 0
    for f, nom in rep["marqueurs"]:
        if a0 <= f < a0 + len(v):
            x = X(f - a0)
            rang = rang + 1 if x - dernier < 110 else 0          # étiquettes proches : décalées
            dernier = x
            d.line([x, h0, x, haut - b], fill=(170, 170, 180))
            d.text((x + 3, h0 + 13 * rang), f"{nom} {f}", fill=ENCRE)
    d.line([(X(i), Y(x)) for i, x in enumerate(v)], fill=TRAIT, width=2)
    c = rep["contact_f"] - a0
    pk = rep["poing"]["pointe_avant_contact"]["f"] - a0
    for i, lab in ((pk, f"pointe {v[pk]:.0f}"), (c, f"contact {v[c]:.0f}")):
        d.ellipse([X(i) - 4, Y(v[i]) - 4, X(i) + 4, Y(v[i]) + 4], outline=FOND, fill=TRAIT, width=2)
        tx = X(i) - 8 - 6 * len(lab) if lab.startswith("pointe") else X(i) + 6
        d.text((tx, Y(v[i]) - 6), lab, fill=ENCRE)
    d.text((g, 8), f"Vitesse du poing ({'droit' if rep['bras'] == 'Right Arm' else 'gauche'}), studs/s, "
                   f"images {a0}-{a0 + len(v) - 1} (60 i/s)", fill=ENCRE)
    d.text((g, haut - b + 8), "image ->", fill=ENCRE2)
    return im


def planche(W, rep, sortie, titre):
    tw, th = 240, 250
    marq = rep["marqueurs"]
    larg = max(tw * len(marq), 960)
    lignes = ["profil", "3/4 face"]
    haut_courbe = 240
    H = 30 + len(lignes) * (th + 34) + haut_courbe + 10
    out = Image.new("RGB", (larg, H), FOND)
    d = ImageDraw.Draw(out)
    d.text((8, 8), titre + " -- rapport de regard (mesures, pas de verdict)", fill=ENCRE)
    y = 30
    for vue in lignes:
        for i, (f, nom) in enumerate(marq):
            cam = cams(W[f])[vue]
            im = VU.silhouette([W[f]], *cam, size=(tw, th))
            out.paste(im, (i * tw, y))
            s = rep["perception"]["silhouette"][nom]
            gp = rep["geo_pose"][nom]["descripteurs"]
            k = "RA" if rep["bras"] == "Right Arm" else "LA"
            d.text((i * tw + 6, y + 4), f"{nom}  f{f}  ({vue})", fill=ENCRE)
            d.text((i * tw + 6, y + th + 3), f"bascule {s['bascule_deg']:.0f}°  lacet {gp['buste']['lacet']:+.0f}°"
                   + ("  CROIX" if s["croix"] else ""), fill=ENCRE2)
            d.text((i * tw + 6, y + th + 17), f"poing av {gp['poing'][k][0]:+.1f} haut {gp['poing'][k][2]:+.1f}",
                   fill=ENCRE2)
            if i:
                d.line([i * tw, y, i * tw, y + th], fill=GRILLE)
        y += th + 34
    out.paste(courbe_vitesse(rep, larg, haut_courbe), (0, y))
    out.save(sortie)
    return sortie


# ------------------------------------------------------------ principal
def rapport(path, marqueurs=None, bras="Right Arm", png=None, js=None):
    W = VU.lire_kfseq(path)
    marqueurs = marqueurs or lire_marqueurs(path)
    marqueurs = [(f, nom) for f, nom in marqueurs if 0 <= f < len(W)]
    if len(marqueurs) < 2:
        raise SystemExit("il faut au moins 2 marqueurs (frame=nom,...) dans le clip")
    rep = mesurer(W, marqueurs, bras)
    reg, dire = lectures(rep)
    rep = _json({"fichier": os.path.relpath(os.path.abspath(path), ROOT),
                 "date": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
                 "consultatif": True, **rep, "a_regarder": reg, "a_dire_a_milan": dire})
    nom = re.sub(r"\.rbxmx?$", "", os.path.basename(path))
    base = os.path.join(ROOT, "captures", "verification", f"{datetime.date.today().isoformat()}-regard-{nom}")
    png = png or base + ".png"
    js = js or base + ".json"
    os.makedirs(os.path.dirname(os.path.abspath(png)), exist_ok=True)
    rep["planche"] = os.path.abspath(png)
    planche(W, rep, png, nom)
    json.dump(rep, open(js, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    return rep, png, js


def texte(rep, png, js):
    L = [f"RAPPORT DE REGARD (non bloquant) -- {rep['fichier']}",
         "marqueurs : " + ", ".join(f"{nom}={f}" for f, nom in rep["marqueurs"]) + f" ; contact f{rep['contact_f']}", ""]
    L.append("CORPS OU BRAS (corps_bras, degrés cumulés ; bras/jambes/tête par rapport au torse)")
    for p in rep["corps_bras"]:
        L.append(f"  {p['de'][:10]:>10s} -> {p['a'][:12]:12s} {p['images']:3d} i | torse {p['torse']:5.0f}° "
                 f"(figé {p['torse_fige']}/{p['images']}) | bras D {p['bras_D']:5.0f}° G {p['bras_G']:5.0f}° | "
                 f"jambes {p['jambes']:5.0f}° | tête {p['tete']:4.0f}°")
    L.append("")
    L.append("GEO_POSE AUX MARQUEURS")
    for nom, g in rep["geo_pose"].items():
        L.append(f"  {nom:10s} f{g['f']:<4d} {g['resume']}")
    L += ["", "À REGARDER (où poser l'œil ; aucune de ces lignes n'est une faute)"]
    L += [f"  - {x}" for x in rep["a_regarder"]]
    if not rep["a_regarder"]:
        L.append("  (rien de signalé par les mesures : regarder quand même, à vitesse réelle)")
    L += ["", "À DIRE À MILAN (ce qu'on a mesuré, sans verdict)"]
    L += [f"  - {x}" for x in rep["a_dire_a_milan"]]
    L += ["", f"planche : {png}", f"json    : {js}"]
    return "\n".join(L)


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a or a[0] in ("-h", "--help"):
        print(__doc__)
        sys.exit(0)
    opts = {}
    for k in ("--bras", "--png", "--json", "--preuve"):
        if k in a:
            i = a.index(k)
            opts[k] = a[i + 1]
            a = a[:i] + a[i + 2:]
    bras = {"R": "Right Arm", "L": "Left Arm"}.get(opts.get("--bras", "R").upper(), "Right Arm")
    rep, png, js = rapport(a[0], parser_marqueurs(a[1:]) or None, bras, opts.get("--png"), opts.get("--json"))
    print(texte(rep, png, js))
    if "--preuve" in opts:
        import preuves as PR
        e = PR.enregistrer_preuve(opts["--preuve"], "mesure_pose", "scene", "valeurs", [a[0]],
                                  {"a_regarder": rep["a_regarder"], "a_dire_a_milan": rep["a_dire_a_milan"]},
                                  "python3 " + " ".join(sys.argv))
        print(f"preuve ajoutée : {e['production']} mesure_pose, commit {(e['commit'] or '?')[:8]}")
    sys.exit(0)
