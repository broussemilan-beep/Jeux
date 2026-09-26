"""
DEPLACER : absorber une entrée d'un fichier du cerveau dans un autre, sans
rien perdre (brique A10 du plan `corpus/recherche/PLAN_REORGANISATION_2026-09-26.md`,
§2.4 point 8 et §4.1).

Pourquoi cet outil existe. Au commit 1395eb3, `LECONS.md` est passé en
HISTORIQUE avec la phrase « ce qu'ils contiennent de vivant est passé dans
CARNET.md et les fiches ». Pour ses §10-11 (« vers le bas », « à plat »),
c'était faux, et « Un seul coup » v1 a refait l'erreur 47 minutes plus tard.
Un déplacement fait à la main, en prose, ne laisse ni trace vérifiable ni
chemin de retour. Hermes Agent refuse une suppression sans `absorbed_into`
vers une cible qui existe ; on fait un peu plus : on vérifie que les NOMBRES
et les TERMES CLÉS de l'entrée sont bien arrivés dans la cible.

Ce que fait l'outil :
1. repère l'entrée dans la source (même découpage qu'`archive_check.py` :
   un titre = une entrée ; « **2.9 … » dans le CARNET ; « en-tête item 2 »
   pour un item numéroté ; ou des lignes explicites avec --lignes) ;
2. repère la section cible (§ id : « 2.9 » dans le CARNET, « 3 » dans une
   fiche) ;
3. recopie le texte d'origine MOT POUR MOT à la fin de la section cible, en
   sous-point « Origine » (citation « > », titres compris, rien reformulé) ;
4. remplace le corps de l'entrée source par une pierre tombale
   « → absorbé dans <fichier> §<n> (<date>) » ; le titre (et donc l'id cité
   par le code et les autres fichiers) reste en place, rien n'est renuméroté ;
5. vérifie, AVANT d'écrire : le texte recopié se relit à l'identique dans la
   cible, chaque nombre, terme et expression « » de l'entrée est présent
   dans la section cible, aucune autre section (source ou cible) n'a bougé,
   et `archive_check` lit bien la pierre tombale avec une cible qui existe.
   Si une vérification échoue : rien n'est écrit (annulé). Après écriture, les
   fichiers sont relus et revérifiés ; en cas d'écart, les originaux sont
   remis.

Ce qu'il ne fait PAS : il ne juge pas si la leçon a été COMPRISE. Il
affiche seulement, à titre d'aide, ce que la section cible ne dit pas encore
en dehors de la citation (« à digérer ») : recopier n'est pas digérer. Il
ne touche jamais aux fichiers en ajout seul (RETOURS.md, notes_milan.jsonl,
milan_verbatim.jsonl) : un `git revert` d'un entretien pourrait sinon
effacer un retour de Milan (plan §6). Il ne lance aucune commande git : il
imprime le message d'un commit dédié, à faire à part de la production.

Par défaut : ESSAI (--essai), rien n'est écrit, le diff est imprimé.

Usage :
  python3 outils/deplacer.py --source LECONS.md --entree 10 \\
      --cible corpus/CARNET.md --section 2.9                 # essai, diff
  python3 outils/deplacer.py ... --appliquer                 # écrit
  python3 outils/deplacer.py --source LECONS.md --lignes 162-182 ...
  python3 outils/deplacer.py ... --cerveau /chemin/copie     # sur une copie
  python3 outils/deplacer.py --liste corpus/CARNET.md        # ids repérables
Options : --date AAAA-MM-JJ (défaut : aujourd'hui).
"""
import difflib
import os
import re
import sys
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import archive_check as ac  # noqa: E402

AJOUT_SEUL = {"RETOURS.md", "notes_milan.jsonl", "milan_verbatim.jsonl"}
ETIQUETTE_ORIGINE = "- Origine"


def brain():
    return ac.BRAIN


def chemin(rel):
    p = rel if os.path.isabs(rel) else os.path.join(brain(), rel)
    return os.path.normpath(p)


def relatif(p):
    return os.path.relpath(p, brain())


# --------------------------------------------------------------------------
# Repérage des entrées et des sections
# --------------------------------------------------------------------------

def _decoupe_texte(texte, rel, items):
    """Découpe un texte en mémoire avec le découpeur d'archive_check (il lit
    un fichier : on passe par un fichier temporaire dans le même dossier
    virtuel, pour garder les chemins relatifs)."""
    import tempfile
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8") as f:
        f.write(texte)
        tmp = f.name
    try:
        es = ac.decouper_md(tmp, items=items, ids_carnet=True)
    finally:
        os.unlink(tmp)
    for e in es:
        e["fichier"] = rel
    return es


def entrees(texte, rel):
    """Toutes les entrées repérables : sections entières d'abord, puis items
    numérotés (« en-tête item 2 »)."""
    entieres = _decoupe_texte(texte, rel, items=False)
    ids = {e["id"] for e in entieres}
    out = list(entieres)
    for e in _decoupe_texte(texte, rel, items=True):
        if "item" in e["id"] and e["id"] not in ids:
            out.append(e)
    return out


def trouver(texte, rel, eid=None, lignes=None):
    lg = texte.splitlines()
    if lignes:
        a, b = lignes
        if not (1 <= a <= b <= len(lg)):
            raise SystemExit(f"--lignes {a}-{b} hors du fichier ({len(lg)} lignes).")
        return dict(fichier=rel, id=f"l.{a}-{b}", titre=lg[a - 1][:70], debut=a, fin=b,
                    texte="\n".join(lg[a - 1:b]))
    es = entrees(texte, rel)
    cand = [e for e in es if e["id"] == eid]
    if not cand:
        cand = [e for e in es if eid.lower() in e["titre"].lower()]
    if len(cand) != 1:
        dispo = ", ".join(e["id"] for e in es[:60])
        quoi = "aucune" if not cand else f"{len(cand)} ({', '.join(c['id'] for c in cand)})"
        raise SystemExit(f"Entrée « {eid} » dans {rel} : {quoi} trouvée(s). Ids repérables : {dispo}")
    return cand[0]


def fin_utile(lg, debut, fin):
    """Dernière ligne non vide d'un bloc [debut, fin] (1-indexé)."""
    k = fin
    while k > debut and not lg[k - 1].strip():
        k -= 1
    return k


# --------------------------------------------------------------------------
# Construction du déplacement (en mémoire)
# --------------------------------------------------------------------------

def bloc_origine(entree, src_rel, jour):
    """Sous-point « Origine » : l'en-tête dit d'où et quand, puis le texte
    d'origine en citation, ligne pour ligne (lignes vides comprises)."""
    lg = entree["texte"].splitlines()
    while lg and not lg[-1].strip():
        lg = lg[:-1]
    tete = (f"{ETIQUETTE_ORIGINE} (absorbé de `{src_rel}` §{entree['id']}, l.{entree['debut']}, "
            f"le {jour} ; texte d'origine mot pour mot) :")
    return [tete] + [("  > " + l) if l else "  >" for l in lg]


def relire_origine(lignes_bloc):
    """Inverse de bloc_origine : retrouve le texte d'origine."""
    out = []
    for l in lignes_bloc[1:]:
        if l == "  >":
            out.append("")
        elif l.startswith("  > "):
            out.append(l[4:])
        else:
            break
    return "\n".join(out)


def pierre_tombale(entree, cible_rel, section, jour):
    """Garde la ligne de titre (l'id reste cité ailleurs) ; remplace le corps."""
    lg = entree["texte"].splitlines()
    marque = (f"→ absorbé dans {cible_rel} §{section} ({jour}). Texte d'origine recopié mot "
              f"pour mot là-bas (sous-point « Origine ») ; il reste aussi dans l'historique git.")
    premiere = lg[0] if lg else ""
    if ac._TITRE.match(premiere):
        return [premiere, "", marque]
    m = ac._ITEM.match(premiere)
    if m:
        court = re.sub(r"^\d+[.)]\s+", "", premiere)[:60]
        return [f"{m.group(1)}. {marque} (« {court}… »)"]
    return [marque]


def construire(src_txt, src_rel, entree, cib_txt, cib_rel, sect, jour):
    """Retourne (nouvelle source, nouvelle cible, lignes insérées)."""
    s_lg = src_txt.splitlines()
    c_lg = cib_txt.splitlines()
    # source : on remplace [debut, fin_utile] et on garde les lignes vides
    # qui séparent l'entrée de la suivante
    fu = fin_utile(s_lg, entree["debut"], entree["fin"])
    s_new = s_lg[:entree["debut"] - 1] + pierre_tombale(entree, cib_rel, sect["id"], jour) + s_lg[fu:]
    # cible : insertion après la dernière ligne non vide de la section
    fc = fin_utile(c_lg, sect["debut"], sect["fin"])
    bloc = bloc_origine(entree, src_rel, jour)
    c_new = c_lg[:fc] + bloc + c_lg[fc:]
    fin_nl = "\n"
    return ("\n".join(s_new) + (fin_nl if src_txt.endswith("\n") else ""),
            "\n".join(c_new) + (fin_nl if cib_txt.endswith("\n") else ""),
            bloc)


# --------------------------------------------------------------------------
# Vérifications
# --------------------------------------------------------------------------

def signature(e):
    return (ac.nombres(e["texte"]), set(ac.termes(e["texte"])), ac.expressions(e["texte"]))


def verifier(entree, src_rel, src_old, src_new, cib_rel, cib_old, cib_new, sect_id, meme_fichier):
    """Liste des problèmes (vide = tout est arrivé)."""
    pb = []
    nbs, tms, exps = signature(entree)
    # 1. la section cible contient le bloc, relu à l'identique
    ces = {e["id"]: e for e in _decoupe_texte(cib_new, cib_rel, items=False)}
    sc = ces.get(sect_id)
    if not sc:
        return [f"la section §{sect_id} n'existe plus dans la cible après insertion"]
    lg = sc["texte"].splitlines()
    tete = f"{ETIQUETTE_ORIGINE} (absorbé de `{src_rel}` §{entree['id']}, l.{entree['debut']},"
    k = next((i for i, l in enumerate(lg) if l.startswith(tete)), None)
    if k is None:
        pb.append("le sous-point « Origine » n'est pas dans la section cible")
    else:
        relu = relire_origine(lg[k:])
        attendu = "\n".join(entree["texte"].splitlines()).rstrip()
        if relu.rstrip() != attendu:
            pb.append("le texte relu dans la cible diffère de l'original")
    # 2. nombres, termes, expressions arrivés dans la section cible
    n2, t2, x2 = ac.nombres(sc["texte"].replace("  > ", "")), set(ac.termes(sc["texte"])), \
        " ".join(re.findall(r"[a-z0-9']+", ac.norm(sc["texte"])))
    manque_n = sorted(nbs - n2)
    manque_t = sorted(tms - t2)
    manque_x = sorted(e for e in exps if e not in x2)
    if manque_n:
        pb.append("nombres absents de la cible : " + ", ".join(manque_n))
    if manque_t:
        pb.append("termes absents de la cible : " + ", ".join(manque_t[:15]))
    if manque_x:
        pb.append("expressions « » absentes de la cible : " + " | ".join(manque_x))
    # 3. aucune autre section n'a bougé (hors entrée déplacée et section cible)
    if not meme_fichier:
        avant = [(e["id"], e["texte"]) for e in _decoupe_texte(cib_old, cib_rel, items=False) if e["id"] != sect_id]
        apres = [(e["id"], e["texte"]) for e in _decoupe_texte(cib_new, cib_rel, items=False) if e["id"] != sect_id]
        if avant != apres:
            pb.append("d'autres sections de la cible ont changé (insertion mal placée ?)")
        so = [e for e in _decoupe_texte(src_old, src_rel, items=False)]
        sn = [e for e in _decoupe_texte(src_new, src_rel, items=False)]
        if [e["id"] for e in so] != [e["id"] for e in sn]:
            pb.append("les ids de la source ont changé (renumérotation ou titre perdu)")
        else:
            for a, b in zip(so, sn):
                if a["id"] != entree.get("parent", entree["id"]) and not (a["debut"] <= entree["debut"] <= a["fin"]):
                    if a["texte"].rstrip() != b["texte"].rstrip():
                        pb.append(f"la section source §{a['id']} a changé alors qu'elle n'était pas visée")
    # 4. la pierre tombale est lisible par archive_check, cible existante
    if not ac.MARQUE_ABSORBE.search(src_new):
        pb.append("pierre tombale introuvable dans la source")
    return pb


def a_digerer(entree, cib_new, cib_rel, sect_id):
    """Aide, pas verdict : ce que la section cible ne dit pas encore HORS de
    la citation d'origine (nombres et termes rares de l'entrée)."""
    sc = {e["id"]: e for e in _decoupe_texte(cib_new, cib_rel, items=False)}[sect_id]
    lg = sc["texte"].splitlines()
    propre = "\n".join(l for l in lg if not (l.startswith("  >") or l.startswith(ETIQUETTE_ORIGINE)))
    nbs, tms, _ = signature(entree)
    n2, t2 = ac.nombres(propre), set(ac.termes(propre))
    return sorted(nbs - n2, key=float), sorted(t for t in tms - t2 if len(t) >= 5)[:20]


# --------------------------------------------------------------------------
# Programme
# --------------------------------------------------------------------------

def _diff(a, b, nom):
    return "".join(difflib.unified_diff(a.splitlines(True), b.splitlines(True),
                                        fromfile=f"a/{nom}", tofile=f"b/{nom}", n=2))


def deplacer(source, cible, section, eid=None, lignes=None, jour=None, appliquer=False, sortie=print):
    jour = jour or date.today().isoformat()
    sp, cp = chemin(source), chemin(cible)
    for p in (sp, cp):
        if os.path.basename(p) in AJOUT_SEUL:
            raise SystemExit(f"{relatif(p)} est en AJOUT SEUL (chronique, mots de Milan) : on ne le "
                             f"réécrit pas. Citer la ligne depuis la fiche à la place.")
        if not os.path.exists(p):
            raise SystemExit(f"Fichier introuvable : {p}")
    src_rel, cib_rel = relatif(sp), relatif(cp)
    meme = sp == cp
    if meme:
        raise SystemExit("Source et cible sont le même fichier : non pris en charge (le déplacement "
                         "interne décalerait les lignes ; corriger sur place à la main).")
    src_old = open(sp, encoding="utf-8").read()
    cib_old = open(cp, encoding="utf-8").read()
    entree = trouver(src_old, src_rel, eid, lignes)
    if ac.MARQUE_ABSORBE.search(entree["texte"]):
        raise SystemExit(f"{src_rel} §{entree['id']} porte déjà une pierre tombale : rien à déplacer.")
    sects = {e["id"]: e for e in _decoupe_texte(cib_old, cib_rel, items=False)}
    if section not in sects:
        raise SystemExit(f"Section §{section} introuvable dans {cib_rel}. Ids : " + ", ".join(list(sects)[:60]))
    sortie(f"DEPLACER ({'APPLIQUER' if appliquer else 'ESSAI, rien n est écrit'}) : "
           f"{src_rel} §{entree['id']} (l.{entree['debut']}-{entree['fin']}) -> {cib_rel} §{section}")
    # verdict archive_check de l'entrée (aide à la relecture)
    try:
        idx = ac.Index(ac.destinations())
        r = ac.verdict(entree, idx)
        if r.get("meilleure_vivante"):
            sortie(f"  archive_check : {r['statut']} (meilleure vivante : {r['meilleure_vivante']['ou']}, "
                   f"{r['meilleure_vivante']['score']})")
        else:
            sortie(f"  archive_check : {r['statut']}")
    except Exception as ex:  # l'aide ne doit jamais empêcher le déplacement
        sortie(f"  archive_check indisponible ({ex})")

    src_new, cib_new, bloc = construire(src_old, src_rel, entree, cib_old, cib_rel, sects[section], jour)
    pb = verifier(entree, src_rel, src_old, src_new, cib_rel, cib_old, cib_new, section, meme)
    sortie("")
    sortie(_diff(src_old, src_new, src_rel) + _diff(cib_old, cib_new, cib_rel))
    nbs, tms, exps = signature(entree)
    sortie(f"Vérification : {len(nbs)} nombres, {len(tms)} termes, {len(exps)} expressions « » de l'entrée.")
    if pb:
        sortie("ANNULÉ, rien n'est écrit :")
        for p in pb:
            sortie("  - " + p)
        return False
    sortie("  tous arrivés dans la section cible ; aucune autre section touchée ; pierre tombale lisible.")
    mn, mt = a_digerer(entree, cib_new, cib_rel, section)
    if mn or mt:
        sortie("À digérer (aide, pas verdict) : hors citation, la section cible ne dit pas encore")
        if mn:
            sortie("  nombres : " + ", ".join(mn))
        if mt:
            sortie("  termes : " + ", ".join(mt))
        sortie("  -> réécrire la phrase de la section au présent, avec sa mesure (format §2.3 du plan),")
        sortie("     ou écrire pourquoi ce n'est plus vrai (« CONTREDIT … »). Recopier n'est pas digérer.")
    if not appliquer:
        sortie("\nEssai seulement. Relancer avec --appliquer pour écrire.")
        return True
    open(sp, "w", encoding="utf-8").write(src_new)
    open(cp, "w", encoding="utf-8").write(cib_new)
    # relecture sur disque
    s2 = open(sp, encoding="utf-8").read()
    c2 = open(cp, encoding="utf-8").read()
    pb2 = verifier(entree, src_rel, src_old, s2, cib_rel, cib_old, c2, section, meme)
    if s2 != src_new or c2 != cib_new or pb2:
        open(sp, "w", encoding="utf-8").write(src_old)
        open(cp, "w", encoding="utf-8").write(cib_old)
        sortie("ANNULÉ après écriture (relecture différente) : originaux remis. " + "; ".join(pb2))
        return False
    sortie(f"\nÉcrit : {src_rel}, {cib_rel}.")
    sortie("Commit DÉDIÉ conseillé (séparé de la production), par exemple :")
    sortie(f"  cerveau: absorbe {src_rel} §{entree['id']} dans {cib_rel} §{section} (deplacer.py, {jour})")
    return True


def main(argv):
    args = list(argv)

    def opt(nom):
        if nom in args:
            k = args.index(nom)
            if k + 1 >= len(args):
                raise SystemExit(f"{nom} attend une valeur")
            v = args[k + 1]
            del args[k:k + 2]
            return v
        return None
    cer = opt("--cerveau")
    if cer:
        ac.regler_cerveau(cer)
    liste = opt("--liste")
    if liste:
        p = chemin(liste)
        for e in entrees(open(p, encoding="utf-8").read(), relatif(p)):
            print(f"§{e['id']:<18} l.{e['debut']:<5} {e['titre'][:80]}")
        return 0
    src, cib, sect = opt("--source"), opt("--cible"), opt("--section")
    eid, lig, jour = opt("--entree"), opt("--lignes"), opt("--date")
    appliquer = "--appliquer" in args
    if not (src and cib and sect and (eid or lig)):
        print(__doc__)
        return 2
    lignes = None
    if lig:
        a, b = lig.split("-")
        lignes = (int(a), int(b))
    ok = deplacer(src, cib, sect, eid, lignes, jour, appliquer)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
