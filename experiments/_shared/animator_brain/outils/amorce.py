"""
AMORCE : ce que la session doit avoir en tête dès le démarrage et après
chaque compaction, imprimé sur la sortie standard (un hook SessionStart de
Claude Code l'ajoute au contexte : `.claude/settings.json` à la racine du
dépôt, installé avec l'accord de Milan le 2026-09-26).

Pourquoi : 24 compactions depuis le 2026-08-31 et rien n'était relu après ;
la consigne « lire ETAT d'abord » dépendait de ma mémoire. Hermes Agent
relit sa mémoire sur disque à chaque frontière de contexte
(agent/system_prompt.py:802, invalidate_system_prompt) ; on fait pareil avec
un fichier versionné.

Imprime, court : le NOYAU ; les 3 derniers messages de Milan (mots exacts,
≤ 700 caractères) ; les motifs répétés s'ils existent (corpus/motifs.json) ;
les propositions en attente (PROPOSITIONS.md). Ne modifie rien. Ne doit
jamais échouer bruyamment : une erreur imprime une ligne et sort en 0.

Usage : python3 amorce.py [source]   (source = startup | resume | compact)
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
B = os.path.normpath(os.path.join(HERE, ".."))


def _lire(p):
    try:
        return open(p, encoding="utf-8").read()
    except OSError:
        return ""


def derniers_mots(n=3, plafond=700):
    lignes = _lire(os.path.join(B, "corpus", "milan_verbatim.jsonl")).splitlines()
    out, total = [], 0
    for l in reversed(lignes):
        try:
            e = json.loads(l)
        except json.JSONDecodeError:
            continue
        t = e.get("texte")
        if not t:
            continue
        t = " ".join(t.split())
        t = t if len(t) <= 300 else t[:297] + "..."
        if total + len(t) > plafond and out:
            break
        out.append(f"- {e.get('date', '')[:16]} : « {t} »")
        total += len(t)
        if len(out) >= n:
            break
    return list(reversed(out))


def motifs():
    try:
        m = json.load(open(os.path.join(B, "corpus", "motifs.json"), encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    items = m.get("motifs", m) if isinstance(m, dict) else m
    out = []
    for x in items if isinstance(items, list) else []:
        if isinstance(x, dict) and x.get("statut", "actif") == "actif":
            out.append(f"- {x.get('phrase', x.get('id', '?'))} ({x.get('nombre_de_fois', '?')} fois)")
    return out[:8]


def main(source=""):
    print(f"=== AMORCE du cerveau d'animation ({source or 'lancement manuel'}) ===")
    print(_lire(os.path.join(B, "NOYAU.md")).strip())
    mots = derniers_mots()
    if mots:
        print("\n## Derniers mots de Milan (moisson ; lancer outils/moisson_milan.py pour la mettre à jour)")
        print("\n".join(mots))
    mt = motifs()
    if mt:
        print("\n## Motifs actifs (mes résumés, pas ses mots ; ses mots exacts : outils/motifs.py)")
        print("\n".join(mt))
    prop = _lire(os.path.join(B, "PROPOSITIONS.md")).strip()
    if prop:
        print("\n## En attente de l'accord de Milan (PROPOSITIONS.md)")
        print(prop[:800])
    print("\nSuite : ETAT.md (où on en est), puis rappel.py et la fiche du moment.")


if __name__ == "__main__":
    try:
        main(sys.argv[1] if len(sys.argv) > 1 else "")
    except Exception as exc:  # jamais bloquant
        print(f"(amorce : erreur ignorée : {exc})")
    sys.exit(0)
