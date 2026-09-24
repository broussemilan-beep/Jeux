"""
Regles du cerveau : ce qu'il a APPRIS des retours de Milan et du corpus,
sous deux formes utilisables par une production :

1. des CIBLES DE CONCEPTION (design_targets) : les valeurs du corpus pro a
   lire AVANT de poser, pour que les poses partent des donnees au lieu d'etre
   tapees de tete puis jugees apres coup (erreur du Poing du Dragon v1,
   voir LECONS.md) ;
2. des VERIFICATIONS (check_*) : chaque lecon de LECONS.md a son controle
   chiffre, avec sa provenance. Une production appelle run_all() et publie le
   rapport.

Aucune constante sans source : chaque seuil vient soit du corpus
(corpus/categories.json, relu a chaque appel), soit d'une reference mesuree
(corpus/REFERENCES_VIDEO.md), soit d'un retour de Milan (RETOURS.md).
"""
import json
import os

_HERE = os.path.dirname(os.path.abspath(__file__))


def _stats():
    return json.load(open(os.path.join(_HERE, "corpus", "categories.json")))


def corpus_value(category, measure, which="mediane"):
    m = _stats()[category]["mesures"]["timing." + measure]
    return m[which]


def design_targets(category):
    """Valeurs du corpus pro a viser en posant (mediane, et plage)."""
    keys = {
        "affaissement_torse_max": "affaissement_torse_studs.max",
        "affaissement_torse_median": "affaissement_torse_studs.median",
        "amplitude_torse_deg": "membres.Torso.amplitude_vs_repos_deg",
        "action_f60": "phases.action_f60",
        "vitesse_bras_max_deg_s": "membres.Right Arm.vitesse_max_deg_s",
        "translation_bras_max": "translation_articulation_max_studs.Right Arm",
        "duree_s": "duree_s",
    }
    m = _stats()[category]["mesures"]
    out = {"categorie": category, "n_exemples": _stats()[category].get("n")}
    for k, v in keys.items():
        ref = m.get("timing." + v)
        if ref:
            out[k] = {"mediane": ref["mediane"], "min": ref["min"], "max": ref["max"]}
    return out


# --------------------------------------------------------------------- verifications
# Chaque fonction renvoie {"regle", "ok", "valeur", "seuil", "source"}.

def check_affaissement(torso_y_frames, category="frappe_legere", slack=0.1):
    """LECON 1 (retour de Milan, 2026-09-24, « il est accroupi ») : pendant des
    coups legers, le torse reste pres de la hauteur debout. Le seuil est le
    MAX pro de la categorie (+10 %) ; torso_y_frames = hauteurs du centre du
    torse, frames au sol seulement."""
    import numpy as np
    sag = np.maximum(0.0, 3.0 - np.asarray(torso_y_frames))
    lim = corpus_value(category, "affaissement_torse_studs.max", "max") * (1 + slack)
    med = float(np.median(sag))
    lim_med = corpus_value(category, "affaissement_torse_studs.median", "max") * (1 + slack) + 0.02
    return {"regle": "posture droite pendant les coups legers", "ok": bool(sag.max() <= lim and med <= lim_med),
            "valeur": {"max": round(float(sag.max()), 3), "median": round(med, 3)},
            "seuil": {"max": round(lim, 3), "median": round(lim_med, 3)},
            "source": f"corpus {category} (affaissement_torse_studs) ; retour Milan 2026-09-24"}


def check_escalade(values, name, min_rise=1.15):
    """LECON 2 (retour de Milan : « l'enchainement », « manque de puissance ») :
    une rafale MONTE. La valeur (hitstop, recul de la victime, secousse...)
    du dernier tiers doit depasser celle du premier tiers d'au moins 15 %, et
    aucun coup ne doit etre nettement plus faible que le precedent. Principe
    tire des refs (Black Flash, Serious Punch), pas du corpus : le pack n'a
    pas de rafale."""
    n = len(values)
    k = max(1, n // 3)
    first, last = sum(values[:k]) / k, sum(values[-k:]) / k
    drops = [i for i in range(1, n) if values[i] < values[i - 1] * 0.9]
    ok = last >= first * min_rise and not drops
    return {"regle": f"escalade : {name}", "ok": bool(ok), "valeur": [round(v, 3) for v in values],
            "seuil": f"dernier tiers >= {min_rise} x premier tiers, aucune baisse > 10 %",
            "source": "refs Black Flash / Serious Punch ; retour Milan 2026-09-24"}


def check_impact_visible(impact_f, first_overlay_f, min_frames=6):
    """LECON 3 (auto-critique validee par Milan, 2026-09-24) : le plus gros
    impact doit etre VU avant tout effet plein ecran. Serious Punch : le poing
    dans la fumee reste 24 f (a 30 i/s) a l'ecran avant les planches."""
    shown = first_overlay_f - impact_f
    return {"regle": "impact final visible avant les effets plein ecran", "ok": bool(shown >= min_frames),
            "valeur": shown, "seuil": f">= {min_frames} f a 60 i/s",
            "source": "REFERENCES_VIDEO.md (Serious Punch) ; LECONS.md 3"}


def check_plan_lisible(camera_keys, f0, f1, min_frames=20):
    """LECON 3b : la plongee vers l'impact tient dans un plan sans coupe
    assez long pour etre lu (>= 20 f a 60 i/s)."""
    cuts = [f for f, *_r, mode in camera_keys if mode == "cut" and f0 < f < f1]
    last_cut = max([f for f, *_r, mode in camera_keys if mode == "cut" and f <= f0] + [0])
    start = max([last_cut] + cuts)
    return {"regle": "plongee lisible (plan sans coupe)", "ok": bool(f1 - start >= min_frames),
            "valeur": f1 - start, "seuil": f">= {min_frames} f", "source": "LECONS.md 3"}


def check_variete_camera(camera_keys, hit_frames, every=2):
    """LECON 2b : dans une rafale, la camera change d'angle au moins toutes
    les `every` frappes (Black Flash : punch-in et coupe a chaque coup)."""
    cuts = sorted(f for f, *_r, mode in camera_keys if mode == "cut")
    shots = []
    for h in hit_frames:
        shots.append(max([c for c in cuts if c <= h] + [0]))
    runs, cur = [], 1
    for a, b in zip(shots, shots[1:]):
        cur = cur + 1 if a == b else 1
        runs.append(cur)
    worst = max(runs + [1])
    return {"regle": f"rafale : changement d'angle au moins toutes les {every} frappes", "ok": bool(worst <= every),
            "valeur": worst, "seuil": f"<= {every} frappes par plan", "source": "refs Black Flash ; LECONS.md 2"}


def check_epaules(shoulder_y, category="frappe_legere", slack=0.05):
    """LECON 6 (retour de Milan sur la v2, 2026-09-24, « les bras sont trop
    hauts ») : les pros BAISSENT l'epaule pour frapper (mediane -0,59 a
    -0,92 stud sur les M1), ils ne la montent jamais (max +0,04). Un
    haussement d'epaule se lit comme des bras trop hauts et un corps crispe.
    shoulder_y = decalages verticaux des Motor6D d'epaule (axe haut du torse),
    toutes frames et les deux bras."""
    import numpy as np
    y = np.asarray(shoulder_y, float)
    lim = corpus_value(category, "decalage_epaule_vertical_studs.haut_max", "max") + slack
    lim_med = corpus_value(category, "decalage_epaule_vertical_studs.median", "max") + slack
    med = float(np.median(y))
    return {"regle": "epaules jamais haussees", "ok": bool(y.max() <= lim and med <= lim_med),
            "valeur": {"max": round(float(y.max()), 3), "median": round(med, 3)},
            "seuil": {"max": round(lim, 3), "median": round(lim_med, 3)},
            "source": f"corpus {category} (decalage_epaule_vertical_studs) ; retour Milan 2026-09-24 (v2)"}


def check_bras_au_contact(elevations_deg, fist_heights=None, category="frappe_legere", slack=5.0):
    """LECON 6b : au contact d'un coup de poing leger, le bras est a
    l'horizontale ou en dessous (pro : -20 a 0 deg, poing a hauteur de
    poitrine 2,5-3,6). Viser la tete bras leve = coup « tape a l'oeil » sans
    poids. elevations_deg = angle epaule->poing au-dessus de l'horizontale,
    un par coup."""
    lim = corpus_value(category, "mecanique_frappe.bras_elevation_deg", "max") + slack
    ok = max(elevations_deg) <= lim
    val = {"elevation_deg": [round(e, 1) for e in elevations_deg]}
    seuil = {"elevation_deg": round(lim, 1)}
    if fist_heights is not None:
        # hauteur absolue du poing (sol = 0) : un bras horizontal sur une
        # epaule haussee reste trop haut -- l'angle seul ne le voit pas
        lim_h = corpus_value(category, "mecanique_frappe.poing_hauteur_studs", "max") + 0.1
        ok = ok and max(fist_heights) <= lim_h
        val["poing_hauteur"] = [round(h, 2) for h in fist_heights]
        seuil["poing_hauteur"] = round(lim_h, 2)
    return {"regle": "bras a l'horizontale ou en dessous au contact", "ok": bool(ok),
            "valeur": val, "seuil": seuil,
            "source": f"corpus {category} (mecanique_frappe) ; refs Black Flash"}


def check_transfert_poids(transfers, category="frappe_lourde", n_power=1):
    """LECON 7 (retour de Milan sur la v2 : « pas en transfert de poids ») :
    un coup qui doit peser fait passer le TORSE au-dessus du pied avant entre
    l'armement et le contact (pro frappe_lourde : 0,33 a 0,92 stud, mediane
    0,84). Avancer le pied AVEC le torse ne compte pas. Les M1 legers du pack
    n'animent pas les jambes et laissent le jeu pousser le perso par script ;
    le seul qui anime le torse (M1_1) transfere 0,74. Dans une cinematique,
    l'animation porte TOUT le corps : la reference est donc le min de la
    frappe lourde, exige sur les `n_power` derniers coups (tous, par defaut
    dans une rafale)."""
    lim = corpus_value(category, "mecanique_frappe.transfert_poids_studs", "min")
    power = transfers[-n_power:]
    return {"regle": "transfert de poids sur les coups de puissance", "ok": bool(min(power) >= lim),
            "valeur": [round(t, 2) for t in transfers], "seuil": f">= {round(lim, 2)} stud sur les {n_power} derniers",
            "source": f"corpus {category} (mecanique_frappe.transfert_poids_studs) ; retour Milan 2026-09-24 (v2)"}


def report(checks):
    ok = sum(1 for c in checks if c["ok"])
    return {"ok": ok, "total": len(checks), "regles": checks}
