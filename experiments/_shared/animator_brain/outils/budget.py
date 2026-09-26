"""
BUDGET du noyau : NOYAU.md reste court pour être relu en entier à chaque
démarrage et après chaque compaction (idée reprise de Hermes Agent, dont la
mémoire toujours injectée est plafonnée à 2 200 caractères,
tools/memory_tool_store.py:99).

Adapté : Hermes REFUSE l'écriture au-delà ; ici on AVERTIT seulement (rien
ne bloque, rappel de Milan : pas de règles gravées). Pour ajouter une ligne
au noyau, on fusionne ou on retire, on n'empile pas.

Usage : python3 budget.py   (code de sortie 0 dans tous les cas)
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
NOYAU = os.path.join(HERE, "..", "NOYAU.md")
PLAFOND = 3500


def etat():
    n = len(open(NOYAU, encoding="utf-8").read())
    return n, round(100 * n / PLAFOND)


if __name__ == "__main__":
    n, pct = etat()
    msg = f"NOYAU.md : {n} / {PLAFOND} caractères ({pct} %)"
    if n > PLAFOND:
        msg += " -- AU-DELÀ du plafond : fusionner ou retirer une ligne avant d'en ajouter (avertissement seulement)"
    print(msg)
