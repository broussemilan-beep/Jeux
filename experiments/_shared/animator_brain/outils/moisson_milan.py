"""
MOISSON des mots exacts de Milan -> corpus/milan_verbatim.jsonl (versionné,
ajout seul).

Pourquoi (audit + étude Hermes du 2026-09-26) : la conversation est
compactée (24 fois depuis le 2026-08-31) et le transcript reste dans le
conteneur, hors de git. 13 des 24 citations de Milan relevées dans le
cerveau ne se retrouvaient pas mot pour mot dans ses vrais messages. Hermes
recopie les mots de l'utilisateur par du CODE, jamais par le modèle ; on fait
pareil : ce script lit le transcript et verse les messages tels quels.

Ce qui est versé (accord de Milan, 2026-09-26 : ses retours, pas un vrac) :
- ses messages tapés (« dit »), y compris ceux envoyés pendant un travail ;
- les longs documents collés (« colle ») : seulement l'empreinte, la
  longueur et les 200 premiers caractères.
Jamais : résumés de compaction, rappels système, résultats d'outils.

Usage : python3 moisson_milan.py [transcript.jsonl ...]
  (sans argument : les transcripts du projet dans ~/.claude/projects/)
Idempotent : une entrée par (horodatage, empreinte), jamais réécrite.
"""
import glob
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SORTIE = os.path.join(HERE, "..", "corpus", "milan_verbatim.jsonl")
LONG_COLLE = 1500


def _textes(c):
    if isinstance(c, str):
        return [("dit", c)]
    out = []
    for x in c if isinstance(c, list) else []:
        if not isinstance(x, dict):
            continue
        if x.get("type") == "text":
            out.append(("dit", x.get("text", "")))
    return out


def moissonner(chemins):
    vus = set()
    if os.path.exists(SORTIE):
        for l in open(SORTIE, encoding="utf-8"):
            e = json.loads(l)
            vus.add((e["date"], e["sha1"]))
    nouveaux = []
    for p in chemins:
        for l in open(p, encoding="utf-8"):
            try:
                j = json.loads(l)
            except json.JSONDecodeError:
                continue
            a = j.get("attachment") or {}
            if j.get("type") == "attachment" and a.get("type") == "queued_command" \
                    and (a.get("origin") or {}).get("kind") == "human":
                # message tapé PENDANT un travail (file d'attente du harnais)
                items = [("dit_pendant_travail", a.get("prompt", ""))]
            elif j.get("type") != "user" or j.get("isCompactSummary") or j.get("isMeta"):
                continue
            else:
                items = _textes(j.get("message", {}).get("content"))
            for mode, t in items:
                t = (t or "").strip()
                if not t or t.startswith("[Request interrupted"):
                    continue
                if t.startswith("<") and any(k in t[:300] for k in ("system-reminder", "task-notification", "command-", "local-command")):
                    continue
                h = hashlib.sha1(t.encode()).hexdigest()[:16]
                cle = (j.get("timestamp"), h)
                if cle in vus:
                    continue
                vus.add(cle)
                e = {"date": j.get("timestamp"), "sha1": h, "session": j.get("sessionId"), "uuid": j.get("uuid")}
                if len(t) > LONG_COLLE and mode == "dit":
                    e.update({"mode": "colle", "longueur": len(t), "debut": t[:200]})
                else:
                    e.update({"mode": mode, "texte": t})
                nouveaux.append(e)
    nouveaux.sort(key=lambda e: e["date"] or "")
    with open(SORTIE, "a", encoding="utf-8") as f:
        for e in nouveaux:
            f.write(json.dumps(e, ensure_ascii=False) + "\n")
    return nouveaux


if __name__ == "__main__":
    ch = sys.argv[1:] or [p for p in glob.glob(os.path.expanduser("~/.claude/projects/-home-user-Jeux/*.jsonl"))]
    n = moissonner(ch)
    print(f"{len(n)} nouveaux messages versés dans {os.path.normpath(SORTIE)}")
