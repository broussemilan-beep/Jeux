"""
MOTIFS : ce que Milan t'a dit plusieurs fois, avec SES mots exacts.

Pourquoi (plan de réorganisation du 2026-09-26, brique A6 ; audit §4) :
« il frappe vers le bas » est revenu 7 fois, de r6_directional_punch
(2026-09-03) à Un seul coup v1 (2026-09-26). Personne ne comptait. Les
leçons qui le portaient ont été rangées en historique, puis oubliées.

Principe de Milan (2026-09-26 09:50) : « tu apprends et tu te nourris tu crée
pas de règles grave dans la roche ». Donc cet outil AFFICHE, il ne juge pas :
- le nombre de fois, les dates, la production et la version, et l'extrait
  EXACT de chaque message (copié de `corpus/milan_verbatim.jsonl`, repéré
  par son sha1, jamais paraphrasé) ;
- la mesure liée : la valeur de la production active À CÔTÉ des mêmes
  grandeurs mesurées sur les refs (`corpus/poses/sources/`), avec leur
  repère et leur statut. Aucun « ok », aucun seuil : c'est l'œil de Milan
  qui juge ;
- ce qui manque pour mesurer (dit franchement).

Statut d'un motif (calculé, jamais décrété) : « actif » si Milan l'a dit
sur l'une des 3 dernières versions notées dans `notes_milan.jsonl` ; sinon
« pas revenu depuis <production version> » (la première version notée
après sa dernière occurrence). Un motif calme peut revenir : les retours
après un silence (« vers le bas » : 8 versions sans le dire, puis Un seul
coup v1) sont affichés à côté.

Mots de Milan lus avec les corrections de `corpus/milan_verbatim_corrections.jsonl`
(2026-09-26 : un brief ou un conseil d'IA COLLÉ, marqué « dit » à la moisson,
ne compte pas comme ses mots ; `outils/moisson_milan.py`, charger_verbatim).

Données : `corpus/motifs.json` ({"motifs": [...]}, clés lues aussi par
`outils/amorce.py` : phrase, nombre_de_fois, statut).

Usage :
  python3 outils/motifs.py                 # tous les motifs, actifs d'abord
  python3 outils/motifs.py "vers le bas"   # ceux qui parlent de ça
  python3 outils/motifs.py --court         # une ligne par motif
  python3 outils/motifs.py --verifier      # chaque extrait est-il mot pour
                                           # mot dans milan_verbatim ? comptes
                                           # et statuts à jour ? (sortie 1 si
                                           # une donnée est incohérente)
  python3 outils/motifs.py --recompter     # réécrit nombre_de_fois,
                                           # productions et statut
  python3 outils/motifs.py --candidats     # messages de Milan qui ressemblent
                                           # à un motif et n'y sont pas encore
                                           # (à relire, rien n'est ajouté seul)
"""
import json
import os
import re
import sys
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
B = os.path.normpath(os.path.join(HERE, ".."))
ROOT = os.path.normpath(os.path.join(B, "..", "..", ".."))
MOTIFS_JSON = os.path.join(B, "corpus", "motifs.json")
VERBATIM = os.path.join(B, "corpus", "milan_verbatim.jsonl")
NOTES = os.path.join(B, "notes_milan.jsonl")


def norm(s):
    s = unicodedata.normalize("NFD", str(s).lower().replace("’", "'"))
    return "".join(c for c in s if unicodedata.category(c) != "Mn")


def lire_jsonl(p):
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


def charger():
    try:
        d = json.load(open(MOTIFS_JSON, encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"motifs": []}
    if isinstance(d, list):
        d = {"motifs": d}
    return d


def verbatim():
    """Les messages de Milan, corrections de `corpus/milan_verbatim_corrections.jsonl`
    appliquées (un texte collé ne compte pas comme ses mots : seul `debut_dit`
    reste dans `texte`). Repli sur le fichier brut si le chargeur manque."""
    try:
        if HERE not in sys.path:
            sys.path.insert(0, HERE)
        import moisson_milan
        return moisson_milan.charger_verbatim()
    except Exception:                    # jamais bloquant : le brut vaut mieux que rien
        return lire_jsonl(VERBATIM)


def verbatim_par_sha():
    return {e.get("sha1"): e for e in verbatim()}


# ------------------------------------------------------------ statut
def chronologie():
    """[(production, version courte, date)] dans l'ordre de notes_milan.
    Seulement les versions que Milan a VUES (une note ou ses mots) : une
    version livrée qui n'a reçu qu'une prédiction ne peut pas « calmer » un
    motif, il ne l'a pas encore regardée."""
    out = []
    for e in lire_jsonl(NOTES):
        if e.get("note_milan") is None and not e.get("mots_milan"):
            continue
        p, v = e.get("production", ""), str(e.get("version", "")).split("_")[0]
        if not out or out[-1][:2] != (p, v):
            out.append((p, v, e.get("date", "")))
    return out


def _cle_prod(p):
    return p.replace("r6_", "")


FENETRE_ACTIF = 3   # dernières versions notées où un motif compte comme « actif »


def position(c, chrono):
    """Indice de la version notée d'une citation ; à défaut (production sans
    note), indice fractionnaire placé à sa date."""
    idx = [i for i, (p, v, _d) in enumerate(chrono)
           if _cle_prod(p) == _cle_prod(c.get("production", "")) and v == c.get("version")]
    if idx:
        return float(idx[-1])
    jour = c.get("date", "")[:10]
    return next((k for k, (_p, _v, d) in enumerate(chrono) if d > jour), len(chrono)) - 0.5


def statut_calcule(m, chrono=None):
    chrono = chrono if chrono is not None else chronologie()
    cits = sorted(m.get("citations", []), key=lambda c: c.get("date", ""))
    if not cits or not chrono:
        return "actif"
    pos = position(cits[-1], chrono)
    if pos >= len(chrono) - FENETRE_ACTIF:
        return "actif"
    i = int(pos) + 1
    return f"pas revenu depuis {chrono[i][0]} {chrono[i][1]}"


def retours_apres_silence(m, chrono=None, mini=3):
    """Paires d'occurrences séparées d'au moins `mini` versions notées."""
    chrono = chrono if chrono is not None else chronologie()
    cits = sorted(m.get("citations", []), key=lambda c: c.get("date", ""))
    out = []
    for a, b in zip(cits, cits[1:]):
        pa, pb = position(a, chrono), position(b, chrono)
        entre = [f"{p} {v}" for k, (p, v, _d) in enumerate(chrono) if pa < k < pb]
        if len(entre) >= mini:
            out.append((a, b, entre))
    return out


def silence(m, chrono=None):
    """Versions notées APRÈS la dernière occurrence (information, pas verdict)."""
    chrono = chrono if chrono is not None else chronologie()
    cits = sorted(m.get("citations", []), key=lambda c: c.get("date", ""))
    if not cits:
        return []
    der = cits[-1]
    idx = [i for i, (p, v, _d) in enumerate(chrono)
           if _cle_prod(p) == _cle_prod(der.get("production", "")) and v == der.get("version")]
    if not idx:
        return []
    return [f"{p} {v}" for p, v, _d in chrono[idx[-1] + 1:]]


# ------------------------------------------------------------ mesures
def valeur(fichier, cle):
    """Valeur à un chemin JSON (liste de clés / indices) ; None si absente."""
    try:
        x = json.load(open(os.path.join(ROOT, fichier), encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    for k in cle:
        try:
            x = x[k]
        except (KeyError, IndexError, TypeError):
            return None
    return x


def _court(v):
    return json.dumps(v, ensure_ascii=False) if not isinstance(v, str) else v


def lignes_mesure(m, indent="  "):
    me = m.get("mesure") or {}
    out = []
    if me.get("quoi"):
        out.append(f"{indent}mesure liée : {me['quoi']}")
    if me.get("outil"):
        out.append(f"{indent}  outil : {me['outil']}")
    for g in me.get("grandeurs", []):
        v = valeur(g["fichier"], g["cle"])
        prod = g["fichier"].split("/")[1] if g["fichier"].startswith("experiments/") else g["fichier"]
        txt = f"{indent}  - {g['nom']} : {prod} = {_court(v) if v is not None else '(absent du fichier)'}"
        refs = []
        for r in g.get("refs", []):
            rv = valeur(r["source"], r["cle"])
            refs.append(f"{os.path.basename(r['source'])} {_court(rv) if rv is not None else '(absent)'} [{r.get('statut', '?')}]")
        if refs:
            txt += " | refs : " + " ; ".join(refs)
        out.append(txt)
    for h in me.get("historique", []):
        out.append(f"{indent}  - {h['version']} : {h['valeurs']} ({h['source']})")
    if me.get("manque"):
        out.append(f"{indent}  manque : {me['manque']}")
    return out


# ------------------------------------------------------------ affichage
def ligne_court(m):
    return f"{m.get('phrase')} (résumé à moi ; ses mots exacts dessous) : Milan l'a dit {m.get('nombre_de_fois', len(m.get('citations', [])))} fois ({m.get('statut', '?')}) [{m.get('id')}]"


def bloc(m, chrono=None, max_cit=None):
    n = m.get("nombre_de_fois", len(m.get("citations", [])))
    out = [f"{m.get('phrase')} (résumé à moi ; ses mots exacts dessous) : Milan l'a dit {n} fois ({m.get('statut', '?')}) [{m.get('id')}]"]
    cits = sorted(m.get("citations", []), key=lambda c: c.get("date", ""))
    montrees = cits if max_cit is None else cits[-max_cit:]
    if len(montrees) < len(cits):
        out.append(f"  ({len(cits) - len(montrees)} plus anciennes : outils/motifs.py {m.get('id')})")
    for c in montrees:
        pv = (c.get("production", "") + " " + c.get("version", "")).strip()
        extra = f" ({c['sens']})" if c.get("sens") else ""
        extra += f" ; {c['note']}" if c.get("note") else ""
        out.append(f"  {c.get('date', '')[:16].replace('T', ' ')} {pv} : « {c.get('extrait')} »{extra} [{c.get('sha1', '')[:8]}]")
    sil = silence(m, chrono)
    if sil:
        out.append(f"  pas redit depuis sur : {', '.join(sil)}")
    for a, b, entre in retours_apres_silence(m, chrono):
        pa = (a.get("production", "") + " " + a.get("version", "")).strip()
        pb = (b.get("production", "") + " " + b.get("version", "")).strip()
        out.append(f"  déjà revenu après un silence : {pa} -> {pb} ({len(entre)} versions notées sans le dire)")
    out.extend(lignes_mesure(m))
    return out


def correspond(m, req):
    r = norm(req)
    mots = [w for w in re.split(r"[^a-z0-9]+", r) if len(w) >= 3]
    tout = norm(" ".join([m.get("id", ""), m.get("phrase", "")] + [c.get("extrait", "") for c in m.get("citations", [])]))
    return r in tout or (mots and all(w in tout for w in mots))


def ordonner(ms):
    return sorted(ms, key=lambda m: (m.get("statut") != "actif", -m.get("nombre_de_fois", 0)))


# ------------------------------------------------------------ vérifier
def verifier(d):
    V = verbatim_par_sha()
    chrono = chronologie()
    pb = 0
    for m in d.get("motifs", []):
        for c in m.get("citations", []):
            e = V.get(c.get("sha1"))
            if not e:
                print(f"[{m['id']}] sha1 {c.get('sha1')} absent de milan_verbatim"); pb += 1
                continue
            if c.get("extrait") not in (e.get("texte") or ""):
                if e.get("correction") and c.get("extrait") in (e.get("texte_colle") or ""):
                    print(f"[{m['id']}] extrait pris dans un texte COLLÉ ({c['sha1']}, corrigé : "
                          f"{e['correction'][:80]}) : ce ne sont pas les mots de Milan"); pb += 1
                else:
                    print(f"[{m['id']}] extrait PAS mot pour mot dans {c['sha1']} : « {c.get('extrait')} »"); pb += 1
            if c.get("date") != e.get("date"):
                print(f"[{m['id']}] date {c.get('date')} != {e.get('date')} ({c['sha1']})"); pb += 1
            ch = c.get("chronique")
            if ch:
                f, _, n = ch.partition(":")
                try:
                    nb = sum(1 for _ in open(os.path.join(B, f), encoding="utf-8"))
                    if not n.isdigit() or int(n) > nb:
                        print(f"[{m['id']}] renvoi {ch} hors du fichier ({nb} lignes)"); pb += 1
                except OSError:
                    print(f"[{m['id']}] renvoi {ch} : fichier introuvable"); pb += 1
        if m.get("nombre_de_fois") != len(m.get("citations", [])):
            print(f"[{m['id']}] nombre_de_fois {m.get('nombre_de_fois')} != {len(m.get('citations', []))} citations"); pb += 1
        st = statut_calcule(m, chrono)
        if m.get("statut") != st:
            print(f"[{m['id']}] statut enregistré « {m.get('statut')} », recalculé « {st} » (--recompter)"); pb += 1
        for g in (m.get("mesure") or {}).get("grandeurs", []):
            if valeur(g["fichier"], g["cle"]) is None:
                print(f"[{m['id']}] (info) mesure absente : {g['fichier']} {g['cle']}")
    n = sum(len(m.get("citations", [])) for m in d.get("motifs", []))
    print(f"{len(d.get('motifs', []))} motifs, {n} citations vérifiées contre milan_verbatim : "
          f"{'aucune incohérence' if not pb else str(pb) + ' incohérence(s)'}")
    return pb


def recompter(d):
    chrono = chronologie()
    for m in d.get("motifs", []):
        m["citations"] = sorted(m.get("citations", []), key=lambda c: c.get("date", ""))
        m["nombre_de_fois"] = len(m["citations"])
        prods = []
        for c in m["citations"]:
            p = (c.get("production", "") + " " + c.get("version", "")).strip()
            if p not in prods:
                prods.append(p)
        m["productions"] = prods
        m["statut"] = statut_calcule(m, chrono)
    json.dump(d, open(MOTIFS_JSON, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"motifs.json recompté : " + ", ".join(f"{m['id']} {m['nombre_de_fois']} ({m['statut']})" for m in d["motifs"]))


def candidats(d):
    cites = {(m["id"], c["sha1"]) for m in d.get("motifs", []) for c in m.get("citations", [])}
    for m in d.get("motifs", []):
        rx = [re.compile(r) for r in m.get("reperes", [])]
        if not rx:
            continue
        found = []
        for e in verbatim():
            t = e.get("texte")
            if not t or e.get("mode") == "colle" or (m["id"], e.get("sha1")) in cites:
                continue
            if any(r.search(norm(t)) for r in rx):
                found.append(e)
        if found:
            print(f"[{m['id']}] {len(found)} message(s) à relire (ressemblent, pas encore cités) :")
            for e in found:
                print(f"  {e['date'][:16]} [{e['sha1'][:8]}] {' '.join(t for t in e['texte'].split())[:200]}")


def main(argv):
    d = charger()
    if "--verifier" in argv:
        return 1 if verifier(d) else 0
    if "--recompter" in argv:
        recompter(d)
        return 0
    if "--candidats" in argv:
        candidats(d)
        return 0
    court = "--court" in argv
    req = " ".join(a for a in argv if not a.startswith("--"))
    ms = [m for m in d.get("motifs", []) if not req or correspond(m, req)]
    if not ms:
        print(f"Aucun motif pour « {req} » dans corpus/motifs.json (aucun résultat ≠ aucun savoir : "
              f"essayer outils/rappel.py \"{req}\", ou --candidats).")
        return 0
    chrono = chronologie()
    print("MOTIFS (mots exacts de Milan ; information, pas verdict)")
    for m in ordonner(ms):
        if court:
            print("- " + ligne_court(m))
        else:
            print()
            print("\n".join(bloc(m, chrono)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
