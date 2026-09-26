"""
Critique du cerveau v2 (CERVEAU_V2.md) : JUGER, puis REFLECHIR sur ses
erreurs a partir des notes de Milan.

1. predict(etat) : note predite d'une production + critique ecrite, a partir
   de l'etat de chaque hypothese (hypotheses.json : vraie / fausse / inconnue)
   ponderee par son poids_note.
2. reflect() : relit l'historique (notes_milan.jsonl) et, pour chaque paire de
   versions notees qui se suivent, regarde QUELLES hypotheses ont change d'etat
   et de combien la note a bouge.
   - Une hypothese qui passe a « vraie » sans que la note bouge perd du
     poids_note : elle etait sans doute juste, mais ce n'est pas elle qui
     retient la note (ex. v2 -> v4 : bras, epaules, trajectoire corriges,
     6,7 -> 6,7).
   - Une hypothese qui passe a « vraie » quand la note monte en gagne.
   - Une hypothese TOUJOURS fausse pendant que la note stagne devient un
     SUSPECT : la piste a creuser en priorite.
   Les poids appris sont ecrits dans hypotheses.json (poids_note) ; la
   confiance_principe (vrai en animation) n'est jamais touchee par la note.
3. Les predictions passees sont comparees aux vraies notes : l'erreur est le
   chiffre qui dit si le cerveau juge comme Milan.

Honnetete : avec 3 notes, c'est un raisonnement, pas une statistique. Le
chiffre utile viendra des comparaisons de variantes (Milan choisit entre A, B
et C), qui donnent bien plus d'information par minute de son temps.

Usage : python3 critic.py reflect        -> rapport + poids mis a jour
        python3 critic.py predict <version>
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
HYP = os.path.join(HERE, "hypotheses.json")
NOTES = os.path.join(HERE, "notes_milan.jsonl")
AUTO = os.path.join(HERE, "etats_auto.json")         # etats MESURES (etats.py) : priment sur le jugement manuel
PRODS = os.path.join(HERE, "productions.json")
BASE, SPAN = 5.0, 3.0          # note de depart et amplitude (0 si tout faux .. 10 si tout vrai, avant apprentissage)
LR = 0.35                      # vitesse d'apprentissage des poids


def load():
    """Hypotheses + notes. L'etat de chaque note = jugement manuel, remplace
    par la MESURE quand etats.py en a une (le cerveau juge ce qu'il voit, plus
    mes impressions). Les desaccords sont gardes : ils disent ou mon oeil se
    trompait."""
    hyp = json.load(open(HYP))
    notes = []
    # une version peut avoir plusieurs lignes (la prediction AVANT Milan, puis
    # sa note) : on les fusionne, la plus recente complete l'ancienne
    for l in open(NOTES):
        if not l.strip():
            continue
        n = json.loads(l)
        prev = next((m for m in notes if m["version"] == n["version"] and m.get("production") == n.get("production")), None)
        if prev is None:
            notes.append(n)
        else:
            prev.update({k: v for k, v in n.items() if v is not None})
    auto = json.load(open(AUTO)) if os.path.exists(AUTO) else {}
    for n in notes:
        a = auto.get(n["version"])
        # (2026-09-25) les notes VFX (v10+) n'ont pas d'etat d'hypotheses
        # d'ANIMATION : sans ce garde, reflect() plantait depuis la v10 et le
        # cerveau n'apprenait plus rien
        n["axe_animation"] = "etat" in n
        n.setdefault("etat", {})
        n["etat_manuel"] = dict(n["etat"])
        n["desaccords"] = []
        if a:
            for k, v in a["etat"].items():
                if n["etat"].get(k) is not None and n["etat"][k] != v:
                    n["desaccords"].append((k, n["etat"][k], v))
                n["etat"][k] = v
            n["parties_mesurees"] = a.get("parties", {})
        # jugement visuel partie par partie (etude sur planches) : complete la mesure
        for part, st in (n.get("parties_visuelles") or {}).items():
            n.setdefault("parties_mesurees", {}).setdefault(part, {}).update(st)
    return hyp, notes


def style_warnings(hyp, style_cible):
    """Hypotheses etalonnees sur un style appliquees a une partie d'un autre
    style (ex. regle M1 realiste appliquee a un coup final manga)."""
    out = []
    for h in hyp["hypotheses"]:
        et = h.get("etalon_style", "universel")
        if et == "universel":
            continue
        for part, st in style_cible.items():
            scope = {"coup_leger": ["rafale"], "coup_droit": ["rafale", "final"], "rafale": ["rafale"],
                     "finisher": ["final"], "impact": ["rafale", "final", "aerien"], "tout": ["rafale", "final", "aerien"]}
            touches = [x for p in h["portee"] for x in scope.get(p, [])]
            if part in touches and st != et:
                out.append(f"{h['id']} (etalon {et}) s'applique a la partie « {part} » visee {st}")
    return out


def predict(hyp, etat, style_cible=None):
    """Note predite + critique : moyenne ponderee des hypotheses connues."""
    num = den = 0.0
    forces, defauts, inconnues = [], [], []
    for h in hyp["hypotheses"]:
        s = etat.get(h["id"])
        w = h["poids_note"] * h["confiance_principe"]
        if s is None:
            inconnues.append(h["id"])
            continue
        num += w * (1.0 if s else -1.0)
        den += w
        (forces if s else defauts).append((w, h["id"], h["enonce"]))
    score = num / den if den else 0.0
    cal = hyp.get("_calibration", {"b": BASE, "a": SPAN})
    note = max(0.0, min(10.0, cal["b"] + cal["a"] * score))
    defauts.sort(reverse=True)
    return {"note_predite": round(note, 1), "score_brut": round(score, 3), "defauts_les_plus_lourds": [d[1] for d in defauts[:4]],
            "forces": [f[1] for f in sorted(forces, reverse=True)], "non_evaluees": inconnues,
            "critique": [f"{d[1]} (poids {d[0]:.2f}) : {d[2]}" for d in defauts[:4]],
            "alertes_style": style_warnings(hyp, style_cible) if style_cible else []}


def _valeur(v):
    """Note chiffree d'un champ de Milan : 7.7, [2, 4] -> 3.0, texte -> None."""
    if isinstance(v, (int, float)) and not isinstance(v, bool):
        return float(v)
    if isinstance(v, list) and v and all(isinstance(x, (int, float)) for x in v):
        return sum(v) / len(v)
    return None


def biais_predictions(notes, hyp):
    """Ecart entre MA prediction (ecrite avant l'avis de Milan) et sa note,
    axe par axe. Ecrit hyp['_biais_prediction'] : a SOUSTRAIRE de mes
    prochaines predictions tant que l'ecart ne se resorbe pas."""
    paires = {}
    for n in notes:
        pr = n.get("prediction_avant_milan") or {}
        reel = {}
        if _valeur(n.get("note_milan")) is not None:
            reel["technique"] = _valeur(n["note_milan"])
        for src in (n.get("axes_milan") or {}, n.get("parties") or {}):
            for k, v in src.items():
                if _valeur(v) is not None:
                    reel[k] = _valeur(v)
        if "technique_totale" in reel:
            reel["technique"] = reel.pop("technique_totale")
        pred = {}
        for k in ("note", "jugement", "claude"):
            if _valeur(pr.get(k)) is not None:
                pred["technique"] = _valeur(pr[k])
                break
        for k, v in (pr.get("jugement_axes") or {}).items():
            if _valeur(v) is not None:
                pred[k] = _valeur(v)
        for axe, v in pred.items():
            if axe in reel:
                paires.setdefault(axe, []).append((n["version"], v, reel[axe]))
    out, biais = [], {}
    for axe, ps in sorted(paires.items()):
        m = sum(p - r for _, p, r in ps) / len(ps)
        biais[axe] = {"biais": round(m, 2), "n": len(ps), "paires": [[v, p, r] for v, p, r in ps]}
        out.append(f"- {axe} : biais moyen {m:+.1f} sur {len(ps)} note(s) ("
                   + ", ".join(f"{v} {p:g}->{r:g}" for v, p, r in ps) + ")")
    hyp["_biais_prediction"] = {**biais, "doc": "moi - Milan, par axe ; a soustraire de mes predictions"}
    return out or ["- (aucune paire prediction / note)"]


def reflect(write=True):
    hyp, notes = load()
    byid = {h["id"]: h for h in hyp["hypotheses"]}
    # on rejoue tout l'historique depuis les poids a priori : relancer la
    # reflexion donne le meme resultat (avant, chaque lancement re-appliquait
    # les mises a jour et les poids derivaient avec le nombre de lancements)
    for h in hyp["hypotheses"]:
        h["poids_note"] = h.get("poids_a_priori", 0.5)
    # seules les notes d'ANIMATION apprennent les poids des hypotheses
    # d'animation : une note tiree vers le bas par les VFX (v12 : 4, alors que
    # l'animation du perso vaut 7,7) fausserait tout le modele
    graded = [n for n in notes if n.get("note_milan") is not None and n["axe_animation"]]
    # (la bannière HISTORIQUE est réécrite à chaque génération : sans elle,
    # chaque exécution l'effaçait -- trouvé le 2026-09-26)
    lines = ["# Reflexion du critique", "",
             "> **HISTORIQUE (daté).** Ce document n'est plus un protocole à suivre. Point",
             "> d'entrée actuel de la piste animation : `ETAT.md` ; apprentissages vivants :",
             "> `corpus/CARNET.md` ; conception : `corpus/fiches/`. (Audit mémoire du",
             "> 2026-09-26.)", "", ""]
    lines += ["## Mes predictions contre les notes de Milan, PAR AXE", ""] + biais_predictions(notes, hyp) + [""]
    # 1. predictions (avec les poids d'AVANT l'apprentissage) contre notes reelles
    lines.append("## Predictions contre notes de Milan (poids avant apprentissage)")
    for n in graded:
        p = predict(hyp, n["etat"])
        lines.append(f"- {n['version']} : predit {p['note_predite']}, Milan {n['note_milan']} "
                     f"(ecart {p['note_predite'] - n['note_milan']:+.1f})")
    # 2. paires successives : quoi a change, de combien la note a bouge
    lines += ["", "## Ce qui a change entre deux versions notees"]
    for a, b in zip(graded, graded[1:]):
        dnote = b["note_milan"] - a["note_milan"]
        flips = [k for k in byid if a["etat"].get(k) is False and b["etat"].get(k) is True]
        lost = [k for k in byid if a["etat"].get(k) is True and b["etat"].get(k) is False]
        lines.append(f"- {a['version']} -> {b['version']} : note {a['note_milan']} -> {b['note_milan']} ({dnote:+.1f}) ; "
                     f"corrigees : {', '.join(flips) or 'aucune'} ; perdues : {', '.join(lost) or 'aucune'}")
        if flips:
            # la hausse de note est partagee entre les corrections ; une
            # correction sans hausse fait baisser le poids
            gain = dnote / len(flips)
            for k in flips:
                h = byid[k]
                target = max(0.05, min(1.0, 0.5 + gain))        # +0,7 partage -> ~0,68 ; 0 -> 0,5 puis on baisse
                if abs(dnote) < 0.2:
                    target = 0.2
                h["poids_note"] = round(h["poids_note"] + LR * (target - h["poids_note"]), 3)
    # 3. suspects : toujours faux pendant que la note stagne
    lines += ["", "## Suspects (toujours faux sur toutes les versions notees, note bloquee)"]
    stuck = len(graded) >= 2 and abs(graded[-1]["note_milan"] - graded[-2]["note_milan"]) < 0.2
    suspects = []
    for k, h in byid.items():
        states = [n["etat"].get(k) for n in graded]
        if states and all(s is False for s in states):
            suspects.append(k)
            if stuck:
                h["poids_note"] = round(h["poids_note"] + LR * (0.9 - h["poids_note"]), 3)
    for k in suspects:
        lines.append(f"- **{k}** : {byid[k]['enonce']} (sources : {'; '.join(byid[k]['sources'])})")
    # 3b. la mesure contre mon jugement manuel
    lines += ["", "## Ou la mesure contredit le jugement manuel (etats.py)"]
    for n in notes:
        for k, man, mes in n.get("desaccords", []):
            lines.append(f"- {n['version']} {k} : jugement {man} -> mesure {mes}")
    # 3c. apprendre de ce que Milan AIME : une hypothese mesuree partie par
    # partie qui est vraie dans les parties aimees et fausse dans les parties
    # rejetees DISCRIMINE -> elle gagne du poids ; si elle a le meme etat dans
    # les deux, ce n'est pas elle qui fait la difference -> elle en perd.
    lines += ["", "## Parties aimees contre parties rejetees"]
    per = {}
    for n in notes:
        pm = n.get("parties_mesurees", {})
        for part, verdict in n.get("parties", {}).items():
            for k, v in pm.get(part, {}).items():
                if k in byid and isinstance(v, bool):
                    per.setdefault(k, {"+": [], "-": []})[verdict].append(v)
    for k, d in per.items():
        if not d["+"] or not d["-"]:
            continue
        pos, neg = sum(d["+"]) / len(d["+"]), sum(d["-"]) / len(d["-"])
        h = byid[k]
        if pos - neg >= 0.5:
            h["poids_note"] = round(h["poids_note"] + LR * (0.9 - h["poids_note"]), 3)
            verdict = "DISCRIMINE (vraie ou Milan aime, fausse ou il rejette) -> poids en hausse"
        elif pos == 0 and neg == 0:
            # jamais vraie nulle part : ce n'est pas une preuve d'inutilite,
            # c'est un principe qu'on n'a jamais essaye -> aucun changement
            verdict = "jamais essaye chez nous : pas de preuve, poids inchange (a tester)"
        elif abs(pos - neg) < 0.25:
            h["poids_note"] = round(h["poids_note"] + LR * (0.3 - h["poids_note"]), 3)
            verdict = "ne discrimine pas (vraie dans l'aime ET le rejete) -> poids en baisse"
        else:
            verdict = "signal faible"
        lines.append(f"- {k} : vraie dans {pos:.0%} des parties aimees, {neg:.0%} des rejetees : {verdict}")
    unknown = [k for k, h in byid.items() if all(n["etat"].get(k) is None for n in graded)]
    lines += ["", "## Jamais mesurees (angle mort du cerveau)"] + [f"- {k} : {byid[k]['enonce']}" for k in unknown]
    # 4. calibration de l'echelle : note = b + a * score (moindres carres, a >= 0).
    # Le bareme de Milan integre aussi ce que les hypotheses ne couvrent pas
    # (l'aerien, juge bon) : sans ca, toutes les predictions sont trop basses.
    import numpy as np
    hyp.pop("_calibration", None)
    S = np.array([predict(hyp, n["etat"])["score_brut"] for n in graded])
    Y = np.array([n["note_milan"] for n in graded])
    if len(graded) >= 2 and np.ptp(S) > 1e-6:
        a, b = np.polyfit(S, Y, 1)
        a = max(0.0, float(a))
        b = float(np.mean(Y - a * S))
    else:
        a, b = SPAN, float(np.mean(Y - SPAN * S)) if len(graded) else BASE
    hyp["_calibration"] = {"a": round(a, 3), "b": round(b, 3), "n_notes": len(graded),
                           "doc": "note = b + a * score ; reapprise a chaque reflexion"}
    lines += ["", f"## Echelle calibree sur {len(graded)} notes : note = {b:.2f} + {a:.2f} x score"]
    lines += ["", "## Poids appris (ce qui fait bouger la note de Milan)"]
    for h in sorted(hyp["hypotheses"], key=lambda h: -h["poids_note"]):
        lines.append(f"- {h['id']:20s} poids_note {h['poids_note']:.2f} (confiance principe {h['confiance_principe']:.2f})")
    lines += ["", "## Predictions apres apprentissage"]
    for n in graded:
        p = predict(hyp, n["etat"])
        lines.append(f"- {n['version']} : predit {p['note_predite']}, Milan {n['note_milan']}")
    if write:
        json.dump(hyp, open(HYP, "w"), indent=1, ensure_ascii=False)
    return "\n".join(lines)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "predict":
        hyp, notes = load()
        n = next(n for n in notes if n["version"] == sys.argv[2])
        prods = json.load(open(PRODS))
        style = next((p.get("style_cible") for k, p in prods.items() if not k.startswith("_") and n["version"] in p["versions"]), None)
        print(json.dumps(predict(hyp, n["etat"], style), indent=1, ensure_ascii=False))
    else:
        rep = reflect()
        open(os.path.join(HERE, "REFLEXION.md"), "w").write(rep + "\n")
        print(rep)
