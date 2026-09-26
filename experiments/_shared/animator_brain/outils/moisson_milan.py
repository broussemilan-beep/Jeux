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

Corrections (2026-09-26) : le fichier est en AJOUT SEUL, on n'y réécrit
jamais une ligne. Quand une ligne marquée « dit » est en fait un texte COLLÉ
(brief de compétence, conseils d'une IA, liste d'outils), la correction va
dans `corpus/milan_verbatim_corrections.jsonl` ({sha1, mode_corrige: "colle",
raison, date}, plus `debut_dit` quand Milan a tapé une phrase avant de coller :
seule cette phrase reste de lui). `charger_verbatim()` ci-dessous applique ces
corrections ; `outils/motifs.py`, `outils/lint_cerveau.py` et `outils/amorce.py`
lisent les mots de Milan par elle : un texte collé ne compte pas comme ses mots.

Usage : python3 moisson_milan.py [transcript.jsonl ...]
  (sans argument : les transcripts du projet dans ~/.claude/projects/)
        python3 moisson_milan.py --signaler-colles
  (liste les lignes « dit » qui ressemblent à un texte collé et n'ont pas
   encore de correction : à relire, rien n'est écrit)
Idempotent : une entrée par (horodatage, empreinte), jamais réécrite.
"""
import glob
import hashlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SORTIE = os.path.join(HERE, "..", "corpus", "milan_verbatim.jsonl")
CORRECTIONS = os.path.join(HERE, "..", "corpus", "milan_verbatim_corrections.jsonl")
LONG_COLLE = 1500


def _jsonl(p):
    out = []
    try:
        for l in open(p, encoding="utf-8"):
            try:
                out.append(json.loads(l))
            except json.JSONDecodeError:
                pass
    except OSError:
        pass
    return out


def charger_corrections(path=CORRECTIONS):
    """{sha1: correction} ; la dernière ligne d'un même sha1 l'emporte."""
    return {c["sha1"]: c for c in _jsonl(path) if c.get("sha1")}


def appliquer_corrections(entrees, corrections=None):
    """Copie des entrées avec les corrections appliquées. Une ligne corrigée en
    « colle » garde son texte d'origine dans `texte_colle` ; `texte` ne garde que
    `debut_dit` (la phrase tapée par Milan avant de coller), ou disparaît."""
    corrections = charger_corrections() if corrections is None else corrections
    out = []
    for e in entrees:
        c = corrections.get(e.get("sha1"))
        if not c or c.get("mode_corrige") != "colle":
            out.append(e)
            continue
        e2 = dict(e)
        t = e.get("texte") or ""
        e2.update({"mode_origine": e.get("mode"), "mode": "colle", "correction": c.get("raison", ""),
                   "texte_colle": t, "longueur": len(t)})
        e2.pop("texte", None)
        d = c.get("debut_dit")
        if d and t.startswith(d):
            e2["texte"] = d
        out.append(e2)
    return out


def charger_verbatim(corrige=True):
    """Les messages de Milan, dans l'ordre du fichier, corrections appliquées."""
    e = _jsonl(SORTIE)
    return appliquer_corrections(e) if corrige else e


RX_COLLE = re.compile(r"•|—|Identité :|Gameplay / hitbox|\n\s*(?:[-*]|\d+[.)])\s")


def signaler_colles():
    """Lignes « dit » qui ressemblent à un texte collé, sans correction."""
    corr = charger_corrections()
    n = 0
    for i, e in enumerate(_jsonl(SORTIE), 1):
        t = e.get("texte") or ""
        if e.get("mode") == "colle" or e.get("sha1") in corr or not RX_COLLE.search(t):
            continue
        n += 1
        print(f"ligne {i} [{e.get('sha1')}] {e.get('date', '')[:16]} : {' '.join(t.split())[:160]}")
    print(f"{n} ligne(s) à relire (aucune n'est corrigée automatiquement ; "
          f"corrections : {os.path.normpath(CORRECTIONS)})")


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
    if "--signaler-colles" in sys.argv:
        signaler_colles()
        sys.exit(0)
    ch = sys.argv[1:] or [p for p in glob.glob(os.path.expanduser("~/.claude/projects/-home-user-Jeux/*.jsonl"))]
    n = moissonner(ch)
    print(f"{len(n)} nouveaux messages versés dans {os.path.normpath(SORTIE)}")
