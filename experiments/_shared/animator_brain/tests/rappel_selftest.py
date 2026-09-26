"""
Cas connus du RAPPEL (plan de réorganisation du 2026-09-26, brique A4 :
« testé sur des cas connus AVANT tout branchement automatique »).

Chaque cas vient d'un oubli réel :
- « frappe vers le bas » : Milan l'a dit 7 fois ; l'ancien rappel rangeait
  « vers le bas » dans l'aérien et sortait LECONS en 11e. La lecture vivante
  est CARNET 2.9 : elle doit sortir en tête de l'INDEX.
- « poing chargé » : l'ancien rappel resservait en 2e et 9e lignes des
  lectures démenties (CATALOGUE:24, :31). Il faut la fiche UN_SEUL_COUP
  (fiche active), CARNET 2.10, et ses marques CONTREDIT, EN DERNIER.
- « buste qui tourne » : Milan l'a dicté « juste tourne » (2026-09-26 09:04).
  Ses mots exacts doivent remonter (trigrammes + message cité par CARNET 2.10).
Plus : mots de 3 lettres, familles, HISTORIQUE rétrogradé mais pas exclu,
poses mesurées lues, 0 résultat honnête, motifs vérifiés contre les mots
exacts.

Ce n'est pas un test de goût : il vérifie que la mémoire RETROUVE ce qu'elle
contient. Usage : python3 tests/rappel_selftest.py (sortie 1 si un cas échoue).
"""
import io
import json
import os
import re
import sys
from contextlib import redirect_stdout

HERE = os.path.dirname(os.path.abspath(__file__))
B = os.path.normpath(os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(B, "outils"))
import rappel as R  # noqa: E402
import motifs as MO  # noqa: E402

ECHECS = []
_CACHE = {}


def sortie(req, **kw):
    cle = (req, tuple(sorted(kw.items())))
    if cle not in _CACHE:
        _CACHE[cle] = R.rappel(req, **kw)[0]
    return _CACHE[cle]


def section(txt, titre):
    """Texte d'une section « == titre… == » jusqu'à la suivante."""
    m = re.search(r"^== " + re.escape(titre) + r".*?==\n(.*?)(?=^== |^Fouillé|\Z)", txt, re.S | re.M)
    return m.group(1) if m else ""


def cas(nom, ok, detail=""):
    print(f"[{'ok' if ok else 'ÉCHEC'}] {nom}" + (f" -- {detail}" if detail and not ok else ""))
    if not ok:
        ECHECS.append(nom)


def verbatim(sha):
    for l in open(os.path.join(B, "corpus", "milan_verbatim.jsonl"), encoding="utf-8"):
        e = json.loads(l)
        if e.get("sha1") == sha:
            return e
    return {}


def main():
    # --- mots et familles
    q = R.Requete("frappe vers le bas")
    cas("« bas » (3 lettres) est cherché", "bas" in [g.mot for g in q.groupes], [g.mot for g in q.groupes])
    cas("« vers le bas » -> famille contact, plus l'aérien",
        "contact" in q.familles and "aerien" not in q.familles, q.familles)
    q2 = R.Requete("poing chargé")
    syn = set(sum((g.syn for g in q2.groupes), []))
    cas("« poing chargé » -> charge, armé, coup chargé", {"charge", "arme", "coup charge"} <= syn, sorted(syn)[:12])
    cas("racine : « frappe » trouve « frappait »", bool(q.groupes[0].exact(R.norm("le perso frappait vers le bas"))))

    # --- 1. frappe vers le bas
    t = sortie("frappe vers le bas")
    idx = section(t, "INDEX")
    premiere = next((l for l in idx.splitlines() if re.match(r"\s*1\.", l)), "")
    cas("« frappe vers le bas » : CARNET 2.9 en tête de l'INDEX", "CARNET 2.9" in premiere, premiere[:120])
    cas("« frappe vers le bas » : l'INDEX donne des nombres (40°, 2,5 studs)",
        "40°" in premiere and "2,5 studs" in premiere, premiere[:160])
    cas("« frappe vers le bas » : le motif compte les fois (mots exacts)",
        "Milan l'a dit 7 fois" in t and "tu donnz dzs coup vers le bas" in t)
    cas("« frappe vers le bas » : la mesure liée est affichée à côté des refs, sans verdict",
        "penché vers l'avant au contact" in t and "pro_tsb_m1_m4.json" in t)
    hist = "LECONS.md" in t and "HISTORIQUE" in t
    cas("HISTORIQUE rétrogradé mais pas exclu (LECONS.md apparaît, marqué)", hist)
    pos_l, pos_c = t.find("LECONS.md"), t.find("CARNET 2.9")
    cas("HISTORIQUE après la lecture vivante", 0 <= pos_c < pos_l, (pos_c, pos_l))

    # --- 2. poing chargé
    t = sortie("poing chargé")
    cas("« poing chargé » : fiche du moment = UN_SEUL_COUP",
        re.search(r"^== Fiche du moment : corpus/fiches/UN_SEUL_COUP\.md", t, re.M) is not None)
    idx = section(t, "INDEX")
    l210 = next((l for l in idx.splitlines() if "CARNET 2.10" in l), "")
    cas("« poing chargé » : CARNET 2.10 dans l'INDEX, avec sa marque CONTREDIT", "CONTREDIT" in l210, l210[:160])
    cn = section(t, "CONTREDIT")
    cas("« poing chargé » : l'arc tendu sort avec sa marque [CONTREDIT v3",
        "CARNET.md:343" in cn and "[CONTREDIT v3" in cn, cn[:200])
    cas("« poing chargé » : la 2e lecture démentie aussi ([CONTREDIT en partie v4)", "[CONTREDIT en partie v4" in cn)
    cas("« poing chargé » : CATALOGUE:24 et :31 (démentis) dans CONTREDIT seulement",
        "CATALOGUE_REFS.md:24" in cn and "CATALOGUE_REFS.md:31" in cn
        and ":24 " not in section(t, "Refs du catalogue") and ":31 " not in section(t, "Refs du catalogue"))
    ordre = [t.find("== INDEX"), t.find("== Fiche du moment"), t.find("== CONTREDIT"), t.find("\nFouillé")]
    cas("« poing chargé » : INDEX, puis fiche, ..., CONTREDIT en dernier", ordre == sorted(ordre) and -1 not in ordre,
        ordre)
    fiche = section(t, "Fiche du moment")
    n = re.search(r"^== Fiche du moment : \S+ \((\d+) caractères", t, re.M)
    corps = fiche.split("\n-- autres ")[0]
    cas("« poing chargé » : la fiche fait 3 000 caractères au plus",
        n is not None and int(n.group(1)) <= 3000 and len(corps.strip()) <= 3000, (n and n.group(1), len(corps)))
    derniere = re.findall(r"^## (\d+)\. ", open(os.path.join(B, "corpus", "fiches", "UN_SEUL_COUP.md"), encoding="utf-8").read(), re.M)[-1]
    cas(f"« poing chargé » : la section la plus récente (§{derniere}) est montrée", f"\n## {derniere}. " in fiche)

    # --- 3. buste qui tourne
    t = sortie("buste qui tourne")
    e = verbatim("bbef1dc35f95e2c0")
    mil = section(t, "Mots de Milan")
    cas("« buste qui tourne » : le message EXACT de Milan du 2026-09-26 09:04",
        bool(e) and e["texte"] in mil and "2026-09-26 09:04" in mil, mil[:300])

    # --- 4. poses mesurées (JSON)
    t = sortie("penche avant contact")
    cas("les poses mesurées sont lues (pro_tsb_m1_m4 fourchettes)",
        "pro_tsb_m1_m4.json#resultat.fourchettes.penche_avant_contact_deg" in t)
    t = sortie("poing tendu derrière")
    cas("les verdicts des vérificateurs sont lus (RÉFUTÉ, en dernier)", "RÉFUTÉ par le vérificateur" in section(t, "CONTREDIT"))

    # --- 5. outils de tout le dépôt
    t = sortie("verify export un seul coup")
    cas("outils de tout le dépôt (r6_un_seul_coup/scripts/verify_export.py)",
        "experiments/r6_un_seul_coup/scripts/verify_export.py" in section(t, "Outils"))

    # --- 6. rien trouvé
    t = sortie("zzqxw plorf")
    cas("0 résultat : « aucun résultat ≠ aucun savoir » et ce qui a été fouillé",
        "Aucun résultat ≠ aucun savoir" in t and "Fouillé :" in t and "messages de Milan" in t)

    # --- 7. sortie courte et taille
    tc = sortie("frappe vers le bas", court_=True)
    cas("--court tient en ~1 500 caractères et garde CARNET 2.9 en tête",
        len(tc) <= 1600 and "1. CARNET 2.9" in tc, len(tc))
    tl = max(len(sortie(x)) for x in ("frappe vers le bas", "poing chargé", "buste qui tourne"))
    cas("sortie complète bornée (< 24 000 caractères)", tl < 24000, tl)

    # --- 8. motifs : mots exacts vérifiés
    buf = io.StringIO()
    with redirect_stdout(buf):
        pb = MO.verifier(MO.charger())
    cas("motifs.json : chaque extrait est mot pour mot dans milan_verbatim, comptes et statuts à jour", pb == 0,
        buf.getvalue()[-300:])

    print(f"\n{len(ECHECS)} échec(s)" + (" : " + " ; ".join(ECHECS) if ECHECS else ""))
    return 1 if ECHECS else 0


if __name__ == "__main__":
    sys.exit(main())
