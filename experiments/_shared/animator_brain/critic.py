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
BASE, SPAN = 5.0, 3.0          # note de depart et amplitude (0 si tout faux .. 10 si tout vrai, avant apprentissage)
LR = 0.35                      # vitesse d'apprentissage des poids


def load():
    hyp = json.load(open(HYP))
    notes = [json.loads(l) for l in open(NOTES) if l.strip()]
    return hyp, notes


def predict(hyp, etat):
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
            "critique": [f"{d[1]} (poids {d[0]:.2f}) : {d[2]}" for d in defauts[:4]]}


def reflect(write=True):
    hyp, notes = load()
    byid = {h["id"]: h for h in hyp["hypotheses"]}
    graded = [n for n in notes if n.get("note_milan") is not None]
    lines = ["# Reflexion du critique", ""]
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
        print(json.dumps(predict(hyp, n["etat"]), indent=1, ensure_ascii=False))
    else:
        rep = reflect()
        open(os.path.join(HERE, "REFLEXION.md"), "w").write(rep + "\n")
        print(rep)
