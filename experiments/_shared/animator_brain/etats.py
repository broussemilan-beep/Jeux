"""
Etats des hypotheses CALCULES (cerveau v2, CERVEAU_V2.md) : relie la
perception au jugement. Avant, l'etat de chaque hypothese etait rempli a la
main dans notes_milan.jsonl ; le critique jugeait donc mes jugements. Ici,
chaque etat vient d'une mesure, avec sa preuve et son etalon :

- regles_<version>.json (regles v1 mesurees sur le corpus) ;
- fiche video corpus/clips/nous_<production>_<version>.json (clip_analyzer),
  comparee aux fiches des references de Milan ;
- perception 3D (perception.py) sur l'animation exportee de la version,
  comparee au pack pro (corpus/perception_pro.json).

Ce qui n'est pas mesurable reste « jugement » (etat manuel de la note),
et le rapport dit quand la mesure CONTREDIT le jugement manuel.

Sortie : etats_auto.json  {version: {etat, preuve, parties}}.
Usage : python3 etats.py [pack_pro.rbxm] [tsb.rbxm]
"""
import glob
import json
import os
import subprocess
import sys
import tempfile

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from animator_brain import perception as P  # noqa: E402

REPO = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=HERE, capture_output=True, text=True).stdout.strip()
PRO = os.path.join(HERE, "corpus", "perception_pro.json")
CLIPS = os.path.join(HERE, "corpus", "clips")
OUT = os.path.join(HERE, "etats_auto.json")


# ------------------------------------------------------------------ etalons

def pro_reference(pack=None):
    """Mesures de perception du pack pro, mises en cache (donnees derivees
    seulement, le pack n'est jamais versionne)."""
    if pack and os.path.exists(pack):
        from animator_brain import corpus as C
        ref = {"source": os.path.basename(pack), "clips": {}}
        m1 = []
        for s in C.load_rbxm_sequences(pack):
            w = [x[1] for x in C.resolve_world(s["frames"])]
            e = {"arcs": P.arcs(w)}
            if "M1" in s["name"] or "Uppercut" in s["name"]:
                h = max(("Right Arm", "Left Arm"),
                        key=lambda h: max((P.tip(x, h) - x["Torso"][1]) @ np.array([0, 0, -1.0]) for x in w))
                c = P.strike_frame(w, h)
                if c >= 6:
                    e.update({"contact_f": c, "main": h, "approche": P.approche(w, c, h), "charge": P.charge(w, c, h)})
                    if "M1" in s["name"]:
                        m1.append((w, c, h))
            if "M1" in s["name"] and "contact_f" in e:
                e["pose_impact"] = P.pose_impact(w, e["contact_f"], e["main"])
            ref["clips"][s["name"]] = e
        shapes = []
        for w, c, h in m1:
            sh = P.fist_shape(w, c, h)
            shapes.append(sh * np.array([-1.0, 1, 1]) if h == "Left Arm" else sh)
        n = min(len(s) for s in shapes)
        d = [float(np.sqrt(((a[:n] - b[:n]) ** 2).sum(1).mean())) for i, a in enumerate(shapes) for b in shapes[i + 1:]]
        ref["variete_m1"] = round(float(np.median(d)), 3)
        json.dump(ref, open(PRO, "w"), indent=1, ensure_ascii=False)
    return json.load(open(PRO))


TSB = os.path.join(HERE, "corpus", "perception_tsb.json")


def tsb_reference(path=None):
    """Mesures derivees des animations TSB officielles (fichier fourni par
    Milan le 2026-09-24, jamais versionne) : profil de frappe des M1,
    bascule du torse des competences, densite de cles."""
    if path and os.path.exists(path):
        from animator_brain import corpus as C
        ref = {"source": "TSB (animations officielles, fichier de Milan)", "clips": {}}
        for s in C.load_rbxm_sequences(path):
            t = np.array([x[0] for x in s["frames"]]) * 60
            w = [x[1] for x in C.resample_linear(s["frames"])]
            up = [x["Torso"][0] @ np.array([0, 1.0, 0]) for x in w]
            tilt = [float(np.degrees(np.arccos(np.clip(u[1], -1, 1)))) for u in up]
            e = {"cles": len(t), "duree_s": round(float(t[-1] / 60), 2),
                 "cles_par_s": round(float(len(t) / max(t[-1] / 60, 1e-6)), 1),
                 "ecart_median_f": round(float(np.median(np.diff(t))), 1) if len(t) > 1 else None,
                 "bascule_torse_p90": round(float(np.percentile(tilt, 90)), 1),
                 "croix_frac": round(float(np.mean([P.silhouette(x)["croix"] for x in w])), 3)}
            if s["name"] in ("M1", "M2", "M3", "M4"):
                h = max(("Right Arm", "Left Arm"), key=lambda h: max((P.tip(x, h) - x["Torso"][1]) @ np.array([0, 0, -1.0]) for x in w))
                c = P.strike_frame(w, h)
                e.update({"contact_f": c, "main": h, "profil_frappe": P.profil_frappe(w, c, h), "pose_impact": P.pose_impact(w, c, h)})
            ref["clips"][s["name"]] = e
        json.dump(ref, open(TSB, "w"), indent=1, ensure_ascii=False)
    return json.load(open(TSB)) if os.path.exists(TSB) else None


def etalons(pro):
    m1 = {k: v for k, v in pro["clips"].items() if "M1" in k}
    devs = [v["arcs"]["deviation_mediane"] for v in m1.values() if v["arcs"]["deviation_mediane"]]
    rates = [v["arcs"]["traits_par_s_de_mouvement"] for v in m1.values() if v["arcs"]["traits_par_s_de_mouvement"]]
    refs = [json.load(open(f)) for f in glob.glob(os.path.join(CLIPS, "*.json")) if not os.path.basename(f).startswith("nous_")]
    contr = [r["energie"]["contraste_p95_sur_mediane"] for r in refs]
    E = {
        "arcs_deviation_min": round(min(devs), 3),
        "arcs_deviation_mediane": round(float(np.median(devs)), 3),
        # mediane des M1 + 30 % : M1_3 (9,6) commence deja en extension, ce n'est
        # pas un coup complet ; les reactions aux coups (Hit 1-3) sont a 9-13.
        "traits_par_s_max": round(float(np.median(rates)) * 1.3, 2),
        "variete_min": pro.get("variete_m1"),
        "contraste_refs_mediane": round(float(np.median(contr)), 2),
        "tenue_charge_min_f": 12, "depart_charge_max_f": 6,     # principe (Serious Punch : garde tenue 32 f) -- provisoire
        "doc": "arcs/traits/variete : pack pro M1 ; contraste : fiches des refs de Milan ; charge : principe, provisoire ; anatomie R6 (pose_impact) : M1 pro + marge",
    }
    pi = [v["pose_impact"] for v in m1.values() if "pose_impact" in v]
    if pi:
        # marge : 10 deg / 0,2 stud / 0,2 autour de la plage pro (4 M1)
        E["bras_epaules_max_deg"] = round(max(x["bras_epaules_deg"] for x in pi) + 10, 1)
        E["torse_detourne_min_deg"] = round(min(x["torse_detourne_deg"] for x in pi) - 10, 1)
        E["bras_libre_max"] = round(max(x["bras_libre"] for x in pi) + 0.2, 2)
        E["translation_bras_min"] = round(min(x["translation_bras"] for x in pi) - 0.2, 2)
    tsb = tsb_reference()
    if tsb:
        m = [v for k, v in tsb["clips"].items() if k.startswith("M") and v.get("profil_frappe")]
        E["plateau_min"] = round(min(v["profil_frappe"]["plateau"] for v in m) - 0.07, 2)
        # competences faites a la main (hors M1-M4, hors ultime cinematique sobre, hors victime et cuits image par image)
        sk = [v["bascule_torse_p90"] for k, v in tsb["clips"].items()
              if not k.startswith("M") and "Victim" not in k and "Ultimate" not in k]
        E["bascule_competence_min"] = round(float(np.percentile(sk, 25)), 1)
        cx = [v["croix_frac"] for k, v in tsb["clips"].items() if "Victim" not in k and "croix_frac" in v]
        if cx:
            E["croix_max"] = round(max(cx) + 0.05, 3)
        E["doc_tsb"] = "croix : part max d'images en croix chez l'attaquant TSB + 5 points ; plateau : M1-M4 TSB - 0,07 ; bascule : 1er quartile des competences TSB (p90 de la bascule du torse)"
    return E


# ------------------------------------------------------------------ une version

def _git_file(commit, path, dst):
    data = subprocess.run(["git", "show", f"{commit}:{path}"], cwd=REPO, capture_output=True).stdout
    if not data:
        return None
    open(dst, "wb").write(data)
    return dst


def _regles(prod_dir, version):
    f = os.path.join(REPO, prod_dir, f"regles_{version}.json")
    return json.load(open(f))["regles"] if os.path.exists(f) else None


def etat_version(prod, cfg, version, commit, hyp, E):
    tmp = tempfile.mkdtemp()
    kf = _git_file(commit, f"{cfg['dossier']}/{cfg['attaquant']}", os.path.join(tmp, "a.rbxmx"))
    sc = json.load(open(_git_file(commit, f"{cfg['dossier']}/scene.json", os.path.join(tmp, "s.json"))))
    world = P.load_production(kf, end_f=sc["end_f"])
    m = P.measure_production(world, sc)
    var = P.variete(world, sc["hits"])
    regles = _regles(cfg["dossier"], version)
    fiche_p = os.path.join(CLIPS, f"{cfg.get('fiche', 'nous_' + prod)}_{version}.json")
    fiche = json.load(open(fiche_p)) if os.path.exists(fiche_p) else None

    etat, preuve = {}, {}
    for h in hyp["hypotheses"]:
        k, mes = h["id"], h.get("mesure") or ""
        if mes.startswith("regles:") and regles is not None:
            rs = [r for r in regles if r["regle"].startswith(mes[7:])]
            if rs:
                etat[k] = all(r["ok"] for r in rs)
                preuve[k] = f"regles_{version}.json : " + " ; ".join(f"{r['regle']} {'ok' if r['ok'] else 'NON'}" for r in rs)
    seg = m["arcs_par_partie"]
    # arcs : les traits de la rafale et du final devient autant que ceux des M1 pro
    dv = [seg[s]["deviation_mediane"] for s in ("rafale", "final") if seg[s]["deviation_mediane"] is not None]
    etat["arcs"] = min(dv) >= E["arcs_deviation_min"]
    preuve["arcs"] = f"deviation mediane rafale {seg['rafale']['deviation_mediane']} / final {seg['final']['deviation_mediane']} ; M1 pro >= {E['arcs_deviation_min']} (mediane {E['arcs_deviation_mediane']})"
    # fluidite : mesure « traits par seconde » RETIREE du jugement le
    # 2026-09-24 (v5) -- confondue avec le tempo de la rafale (hypotheses.json)
    ch = m["charge_final"]
    etat["coup_charge"] = ch["tenue_f"] >= E["tenue_charge_min_f"] and ch["depart_f"] <= E["depart_charge_max_f"]
    preuve["coup_charge"] = f"coup final : tenue {ch['tenue_f']} f, depart {ch['depart_f']} f, buste {ch['enroulement_buste_deg']} deg ; principe : tenue >= {E['tenue_charge_min_f']} f puis depart <= {E['depart_charge_max_f']} f"
    if E["variete_min"] is not None:
        etat["variete_coups"] = var >= E["variete_min"]
        preuve["variete_coups"] = f"distance mediane entre formes de coups {var} studs ; M1 pro entre eux {E['variete_min']}"
    if fiche:
        pa = fiche["impacts"].get("profil_autour") or {}
        if "tenue_avant_choc" in pa:
            etat["tenue_avant_choc"] = bool(pa["tenue_avant_choc"])
            etat["explosion_apres"] = bool(pa.get("explosion_apres"))
            preuve["explosion_apres"] = f"fiche video : profil {pa}"
            preuve["tenue_avant_choc"] = f"fiche video : {fiche['impacts']['nombre']} carte(s) d'impact, profil {pa}"
        c = fiche["energie"]["contraste_p95_sur_mediane"]
        etat["contraste_de_temps"] = c >= E["contraste_refs_mediane"]
        preuve["contraste_de_temps"] = f"contraste d'energie {c} ; refs de Milan mediane {E['contraste_refs_mediane']}"
    # anatomie R6 au contact des coups droits (rafale + coup final au sol)
    if "bras_epaules_max_deg" in E:
        part = {"R": "Right Arm", "L": "Left Arm"}
        coups = [(c, part[s_]) for c, s_, _k in sc["hits"]]
        if sc.get("final_f"):
            coups.append((sc["final_f"], part[sc.get("final_side", "R")]))
        pi = [P.pose_impact(world, c, h) for c, h in coups]
        med = {k: float(np.median([x[k] for x in pi])) for k in pi[0]}
        etat["ligne_epaules"] = med["bras_epaules_deg"] <= E["bras_epaules_max_deg"] and med["torse_detourne_deg"] >= E["torse_detourne_min_deg"]
        preuve["ligne_epaules"] = f"mediane bras/epaules {med['bras_epaules_deg']:.0f} deg (pro <= {E['bras_epaules_max_deg']}), torse detourne {med['torse_detourne_deg']:.0f} deg (pro >= {E['torse_detourne_min_deg']})"
        etat["bras_libre_ramene"] = med["bras_libre"] <= E["bras_libre_max"]
        preuve["bras_libre_ramene"] = f"mediane bras libre / bras qui frappe {med['bras_libre']:.2f} (pro <= {E['bras_libre_max']})"
        etat["bras_avant_bras"] = med["translation_bras"] >= E["translation_bras_min"]
        preuve["bras_avant_bras"] = f"mediane translation d'epaule au contact {med['translation_bras']:.2f} stud (pro >= {E['translation_bras_min']})"
    # TSB : vitesse constante du poing entre deux cles (cles eparses en Linear)
    if "plateau_min" in E:
        part = {"R": "Right Arm", "L": "Left Arm"}
        coups = [(c, part[s_]) for c, s_, _k in sc["hits"]]
        if sc.get("final_f"):
            coups.append((sc["final_f"], part[sc.get("final_side", "R")]))
        pf = [P.profil_frappe(world, c, h) for c, h in coups]
        pl = [x["plateau"] for x in pf if x]
    if "plateau_min" in E and pl:
        etat["frappe_lineaire"] = float(np.median(pl)) >= E["plateau_min"]
        preuve["frappe_lineaire"] = f"plateau de vitesse du poing (min/max phase rapide) mediane {np.median(pl):.2f} {pl} ; TSB M1-M4 >= {E['plateau_min']}"
    if "bascule_competence_min" in E:
        ff = sc.get("final_f")
        if ff:
            tilt = [float(np.degrees(np.arccos(np.clip((world[i]["Torso"][0] @ np.array([0, 1.0, 0]))[1], -1, 1))))
                    for i in range(max(0, ff - 42), min(len(world), ff + 20))]
            b90 = float(np.percentile(tilt, 90))
            etat["bascule_competence"] = b90 >= E["bascule_competence_min"]
            preuve["bascule_competence"] = f"coup final (f{ff - 42}-{ff + 20}) : bascule du torse p90 {b90:.0f} deg ; competences TSB >= {E['bascule_competence_min']}"
    # tutos video (2026-09-24) : croix de face pendant la charge du coup final, torsion charge -> contact
    ff = sc.get("final_f")
    if ff:
        cr = [P.silhouette(world[i])["croix"] for i in range(max(0, ff - 32), min(len(world), ff - 3))]
        frac = float(np.mean(cr)) if cr else 0.0
        etat["silhouette_non_croix"] = frac <= E.get("croix_max", 0.05)
        preuve["silhouette_non_croix"] = f"charge du coup final (f{ff - 32}-{ff - 4}) : {frac * 100:.0f} % des images en croix ; TSB attaquant <= {E.get('croix_max', 0.05) * 100:.0f} %"
        tr = P.torsion(world, ff - 32, ff - 3, ff)
        etat["torsion_charge_contact"] = tr >= 90
        preuve["torsion_charge_contact"] = f"lacet du torse charge -> contact f{ff} : {tr:.0f} deg ; tutos R6 >= 90"
    # parties : les memes mesures, partie par partie (pour apprendre de ce que Milan AIME)
    parties = {s: {"arcs": v["deviation_mediane"] is not None and v["deviation_mediane"] >= E["arcs_deviation_min"],
                   "mesures": v} for s, v in seg.items()}
    return {"etat": etat, "preuve": preuve, "parties": parties, "mesures_coups": m["coups"],
            "charge_final": ch, "variete": var}


def main(pack=None, tsb=None):
    hyp = json.load(open(os.path.join(HERE, "hypotheses.json")))
    tsb_reference(tsb)
    pro = pro_reference(pack)
    E = etalons(pro)
    prods = json.load(open(os.path.join(HERE, "productions.json")))
    out = {"_etalons": E}
    for prod, cfg in prods.items():
        if prod.startswith("_"):
            continue
        for v, commit in cfg["versions"].items():
            out[v] = etat_version(prod, cfg, v, commit, hyp, E)
    json.dump(out, open(OUT, "w"), indent=1, ensure_ascii=False)
    # desaccords mesure / jugement manuel
    notes = {n["version"]: n for n in (json.loads(l) for l in open(os.path.join(HERE, "notes_milan.jsonl")) if l.strip())}
    print("etalons :", json.dumps(E, ensure_ascii=False))
    for v, r in out.items():
        if v.startswith("_"):
            continue
        man = notes.get(v, {}).get("etat", {})
        diff = [f"{k} (jugement {man[k]} -> mesure {r['etat'][k]})" for k in r["etat"] if man.get(k) is not None and man[k] != r["etat"][k]]
        print(f"{v}: " + " ".join(f"{k}={'V' if s else 'F'}" for k, s in r["etat"].items()))
        if diff:
            print("   la mesure contredit le jugement : " + ", ".join(diff))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None, sys.argv[2] if len(sys.argv) > 2 else None)
