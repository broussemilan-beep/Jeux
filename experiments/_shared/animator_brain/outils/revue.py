"""
REVUE d'apprentissage après un retour de Milan : une check-list d'AIDE,
imprimée, qui ne modifie rien et ne bloque rien (brique A10 du plan
`corpus/recherche/PLAN_REORGANISATION_2026-09-26.md`, §2.4 point 6).

Pourquoi cet outil existe. Les retours de Milan arrivaient bien dans
`RETOURS.md` (la chronique), mais ce qu'ils apprenaient ne revenait pas
toujours dans l'endroit qu'on RELIT avant de poser une clé :
- « vers le bas » dit 6 fois ; la leçon écrite (LECONS §10) a été archivée,
  et la fiche du moment ne la portait pas : Un seul coup v1 l'a refait ;
- des corrections empilées sous la phrase fausse (CARNET 2.10), des mots de
  Milan cités de mémoire (13 sur 24 introuvables mot pour mot).
Hermes Agent fait une revue après chaque tour, dans un ordre fixe (la skill
en jeu, puis la parapluie, puis un support, créer en dernier) avec une liste
« ne pas capturer » (`background_review.py:392-500`). On reprend l'ordre et
la liste ; on NE reprend PAS son « sois actif » : « rien à inscrire » est
une sortie valable. Et Milan : « on apprend, pas de règles gravées dans la
roche » : cet outil rappelle et avertit, il ne décide pas à ma place.

Ce qu'il imprime :
1. le dernier retour noté (`notes_milan.jsonl`) et les derniers mots exacts
   (`corpus/milan_verbatim.jsonl`), avec un avertissement si le retour noté
   ne se retrouve pas dans la moisson (lancer `outils/moisson_milan.py`) ;
2. la fiche active (`NOYAU.md` ou `ETAT.md`), son en-tête `quand:` /
   `outils:` / `sorte:` et ses sections ;
3. les sections (fiches, CARNET) dont les mots recoupent le plus ceux de
   Milan : des candidats à relire, pas une décision ;
4. l'ordre de patch, la liste « ne pas inscrire » et le format d'entrée,
   relus dans `corpus/fiches/_MODELE.md` (un seul endroit à changer) ;
5. un AVERTISSEMENT si `RETOURS.md` ou `notes_milan.jsonl` ont changé dans
   git (travail en cours, ou depuis leur dernier commit) sans qu'aucune
   fiche ni le CARNET n'ait changé ; se tait si la dernière entrée de
   RETOURS dit « rien à inscrire ».
Git est seulement LU (status, log, diff --name-only). Code de sortie : 0.

Usage :
  python3 outils/revue.py                 # sur le cerveau du dépôt
  python3 outils/revue.py --sans-git      # sans l'avertissement git
  python3 outils/revue.py --cerveau <dossier du cerveau>   # sur une copie
  python3 outils/revue.py --n 5           # 5 derniers messages de Milan
"""
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import archive_check as ac  # noqa: E402

BRAIN = os.path.normpath(os.path.join(HERE, ".."))

SOURCES = ["RETOURS.md", "notes_milan.jsonl"]
APPRENTISSAGE = ["corpus/fiches/", "corpus/CARNET.md"]

ORDRE = [
    "1. patcher la fiche du moment EN JEU (fiche active, ou celle que ses mots visent) ;",
    "2. puis une fiche de CLASSE, si ce qu'il dit vaut au-delà de cette production ;",
    "3. puis un SUPPORT : une mesure ou un outil qui rendra la chose visible la prochaine fois ;",
    "4. CRÉER une fiche ou une entrée en dernier, seulement si rien n'existe.",
]
NE_PAS_INSCRIRE_DEFAUT = [
    "le journal des versions (il va dans RETOURS.md) ;",
    "un correctif du jour écrit comme une loi (« toujours », « jamais ») ;",
    "des mots de Milan de mémoire (seulement ceux de milan_verbatim.jsonl) ;",
    "un essai non vu par Milan comme un acquis (il reste « piste ») ;",
    "un contrôle vrai/faux de style (seul le technique bloque).",
]


def lire(rel):
    try:
        return open(os.path.join(BRAIN, rel), encoding="utf-8").read()
    except OSError:
        return ""


def jsonl(rel):
    out = []
    for l in lire(rel).splitlines():
        try:
            out.append(json.loads(l))
        except json.JSONDecodeError:
            continue
    return out


def court(t, n=400):
    t = " ".join((t or "").split())
    return t if len(t) <= n else t[:n - 3] + "..."


# --------------------------------------------------------------------------
# 1. Ce que Milan a dit
# --------------------------------------------------------------------------

def dernier_retour():
    notes = jsonl("notes_milan.jsonl")
    if not notes:
        return None, None
    avec_mots = next((n for n in reversed(notes) if n.get("mots_milan") or n.get("note_milan") is not None), None)
    return notes[-1], avec_mots


def derniers_mots(n=3):
    """La moisson est en ajout seul mais pas forcément dans l'ordre (un
    transcript relu plus tard ajoute des messages anciens) : tri par date."""
    vb = sorted((e for e in jsonl("corpus/milan_verbatim.jsonl") if e.get("texte")),
                key=lambda e: e.get("date", ""))
    return vb[-n:], vb


def plus_proche(mots, vb):
    """Message de la moisson le plus ressemblant (aide pour citer juste) :
    part des mots du retour noté retrouvés dans le message (les fautes de
    frappe de Milan font rater une comparaison caractère par caractère)."""
    cible = set(re.findall(r"[a-z0-9]{3,}", ac.norm(mots)))
    best = (0.0, None)
    for e in vb:
        t = set(re.findall(r"[a-z0-9]{3,}", ac.norm(e["texte"])))
        r = len(cible & t) / max(len(cible), 1)
        if r > best[0]:
            best = (r, e)
    return best


def dans_moisson(mots, vb):
    """Le retour noté se retrouve-t-il tel quel dans la moisson ? (40 premiers
    caractères normalisés, ou 3 morceaux de 25 caractères du même message)."""
    if not mots:
        return True
    cible = " ".join(re.findall(r"[a-z0-9]+", ac.norm(mots)))
    tout = [" ".join(re.findall(r"[a-z0-9]+", ac.norm(e["texte"]))) for e in vb]
    pas = max(len(cible) // 3, 25)
    morceaux = [cible[i:i + 25] for i in range(0, max(len(cible) - 25, 1), pas)][:3]
    return any(cible[:40] in t for t in tout) or any(all(m in t for m in morceaux) for t in tout)


# --------------------------------------------------------------------------
# 2. Fiche active
# --------------------------------------------------------------------------

def fiche_active():
    """Cherche « fiche_active: `…` » (ETAT, plan §2.1) puis « Fiche active :
    `…` » (NOYAU), dans ETAT.md puis NOYAU.md."""
    for f in ("ETAT.md", "NOYAU.md"):
        t = lire(f)
        m = re.search(r"fiche[_ ]active\s*:\s*`?([\w/.\-]+\.md)", t, re.I)
        if m:
            p = m.group(1)
            for base in ("", "corpus/", "corpus/fiches/"):
                if os.path.exists(os.path.join(BRAIN, base + p)):
                    return base + p, f
            return p, f
    return None, None


def entete(texte):
    """Champs quand: / outils: / sorte: en tête de fiche (bloc --- ou lignes
    libres dans les 15 premières lignes)."""
    champs = {}
    for l in texte.splitlines()[:15]:
        m = re.match(r"^\s*(quand|outils|sorte)\s*:\s*(.+)$", l, re.I)
        if m:
            champs[m.group(1).lower()] = m.group(2).strip()
    return champs


def sections(texte):
    return [(i + 1, l) for i, l in enumerate(texte.splitlines()) if re.match(r"^##\s", l)]


# --------------------------------------------------------------------------
# 3. Où ses mots pourraient aller (aide)
# --------------------------------------------------------------------------

SORTE_CONNUE = {"UN_SEUL_COUP.md": "production", "POING_DU_DRAGON_V13.md": "production"}   # plan §2.1


def sorte_de(rel):
    t = lire(rel)
    s = entete(t).get("sorte")
    if s and not s.startswith("<"):
        return s
    b = os.path.basename(rel)
    if b == "CARNET.md":
        return "transverse"
    return SORTE_CONNUE.get(b, "classe ?")


def candidats(mots, k=6):
    secs = []
    carnet = os.path.join(BRAIN, "corpus", "CARNET.md")
    if os.path.exists(carnet):
        secs += ac.decouper_md(carnet, items=False, ids_carnet=True)
    fdir = os.path.join(BRAIN, "corpus", "fiches")
    for f in sorted(os.listdir(fdir)) if os.path.isdir(fdir) else []:
        if f.endswith(".md") and not f.startswith("_"):
            secs += ac.decouper_md(os.path.join(fdir, f), items=False)
    for s in secs:
        s["texte"] = ac.sans_origine(s["texte"])
        s["etage"] = "vivant"
    if not secs or not mots.strip():
        return []
    idx = ac.Index(secs)
    _, _, _, res = ac.recouper(dict(fichier="(mots de Milan)", texte=mots), idx)
    out = []
    for r in res[:k]:
        s = idx.secs[r["section"]]
        communs = [t for t in idx.cles(mots, k=25) if t in s["_t"] and len(t) >= 4][:6]
        out.append((r["score"], s, communs))
    return out


# --------------------------------------------------------------------------
# 4. Gabarit
# --------------------------------------------------------------------------

def depuis_modele():
    """Liste « ne pas inscrire » et bloc de format relus dans _MODELE.md."""
    t = lire("corpus/fiches/_MODELE.md")
    npi, fmt = [], None
    m = re.search(r"^## Ne pas inscrire\s*$(.*?)(?=^## )", t, re.S | re.M)
    if m:
        npi = [l[2:].strip() for l in m.group(1).splitlines() if l.startswith("- ")]
    m = re.search(r"^## Format d'une entrée\s*$.*?```\n(.*?)```", t, re.S | re.M)
    if m:
        fmt = m.group(1).rstrip()
    return npi, fmt


# --------------------------------------------------------------------------
# 5. Git (lecture seule)
# --------------------------------------------------------------------------

def _git(racine, *a):
    r = subprocess.run(["git", "-C", racine] + list(a), capture_output=True, text=True, timeout=30)
    if r.returncode != 0:
        raise RuntimeError(r.stderr.strip()[:200] or "git a échoué")
    return r.stdout


def derniere_entree_retours():
    t = lire("RETOURS.md")
    k = [m.start() for m in re.finditer(r"^- \*\*", t, re.M)]
    return t[k[-1]:] if k else t[-2000:]


def verifier_git():
    """Retourne (avertissements, infos). Lecture seule."""
    racine = _git(BRAIN, "rev-parse", "--show-toplevel").strip()
    pref = os.path.relpath(BRAIN, racine).replace(os.sep, "/")
    pref = "" if pref == "." else pref + "/"
    srcs = [pref + s for s in SOURCES]
    appr = [pref + a for a in APPRENTISSAGE]

    def touche(fichiers, motifs):
        return sorted({f for f in fichiers for m in motifs if f == m or (m.endswith("/") and f.startswith(m))})

    st = _git(racine, "status", "--porcelain", "--untracked-files=all", "--", pref or ".")
    en_cours = [l[3:].split(" -> ")[-1].strip('"') for l in st.splitlines() if len(l) > 3]
    av, info = [], []
    src_cours, app_cours = touche(en_cours, srcs), touche(en_cours, appr)
    court_ = lambda fs: ", ".join(f[len(pref):] for f in fs)
    if src_cours:
        if app_cours:
            info.append(f"travail en cours : {court_(src_cours)} ET {court_(app_cours)} ont changé.")
        else:
            av.append(f"{court_(src_cours)} a changé (non commité) sans aucun changement dans "
                      f"corpus/fiches/ ni corpus/CARNET.md.")
        return av, info
    h = _git(racine, "log", "-1", "--format=%H|%h|%ci|%s", "--", *srcs).strip()
    if not h:
        return av, ["aucun commit ne touche RETOURS.md / notes_milan.jsonl."]
    full, abr, quand, sujet = h.split("|", 3)
    try:
        depuis = _git(racine, "diff", "--name-only", full + "^", "HEAD").split()
    except RuntimeError:   # premier commit du dépôt
        depuis = _git(racine, "show", "--name-only", "--format=", full).split()
    app = touche(depuis + en_cours, appr)
    if app:
        info.append(f"dernier retour commité {abr} ({quand[:16]}) ; depuis, apprentissage touché : "
                    + ", ".join(a[len(pref):] for a in app[:6]) + ("…" if len(app) > 6 else ""))
    else:
        av.append(f"le dernier commit qui touche RETOURS / notes ({abr}, {quand[:16]}, « {sujet[:60]} ») "
                  f"n'a été suivi d'AUCUN changement de fiche ni du CARNET (ni dans ce commit, ni après).")
    return av, info


# --------------------------------------------------------------------------
# Programme
# --------------------------------------------------------------------------

def main(argv):
    global BRAIN
    args = list(argv)
    sans_git = "--sans-git" in args
    n = 3
    if "--n" in args:
        n = int(args[args.index("--n") + 1])
    if "--cerveau" in args:
        BRAIN = os.path.abspath(args[args.index("--cerveau") + 1])
        ac.regler_cerveau(BRAIN)
    P = print
    P("=== REVUE d'apprentissage après un retour de Milan (aide : rien n'est modifié, rien n'est bloqué) ===")

    # 1. ses mots
    der, avec = dernier_retour()
    P("\n## 1. Ce qu'il a dit")
    if avec:
        note = avec.get("note_milan")
        P(f"Dernier retour noté (notes_milan.jsonl) : {avec.get('production')} {avec.get('version')} "
          f"({avec.get('date')}) ; note {note if note is not None else '-'} ; "
          f"prédiction {avec.get('prediction', '-')} ; écart {avec.get('ecart_prediction', '-')}")
        if avec.get("mots_milan"):
            P(f"  « {court(avec['mots_milan'], 600)} »")
    if der and der is not avec:
        P(f"Dernière ligne (sans retour encore) : {der.get('production')} {der.get('version')} "
          f"({der.get('date')}), prédiction {der.get('prediction', '-')}")
    mots, vb = derniers_mots(n)
    if mots:
        P(f"Derniers mots exacts (corpus/milan_verbatim.jsonl, {len(vb)} messages) :")
        for e in mots:
            P(f"  - {e.get('date', '')[:16]} [{e.get('mode', '?')}, {e.get('sha1', '')[:8]}] « {court(e['texte'])} »")
    else:
        P("  (milan_verbatim.jsonl vide ou absent : lancer outils/moisson_milan.py)")
    if avec and avec.get("mots_milan") and vb and not dans_moisson(avec["mots_milan"], vb):
        r, e = plus_proche(avec["mots_milan"], vb)
        P("  AVERTISSEMENT : les mots de ce retour noté ne se retrouvent pas tels quels dans la moisson "
          "(version corrigée à la main, ou moisson pas à jour : outils/moisson_milan.py).")
        if e and r >= 0.5:
            P(f"    mots exacts les plus proches ({r:.2f}) : {e.get('date', '')[:16]} [{e.get('sha1', '')[:8]}] "
              f"« {court(e['texte'], 300)} »")
            P("    -> citer CEUX-LÀ (avec le sha1), pas la version de notes_milan.jsonl.")

    # 2. fiche active
    P("\n## 2. Fiche active")
    fa, ou = fiche_active()
    if not fa:
        P("  aucune « fiche active » trouvée dans ETAT.md ni NOYAU.md.")
    else:
        t = lire(fa)
        P(f"  {fa} (déclarée dans {ou}) ; {len(t)} caractères ; sorte : {sorte_de(fa)}")
        e = entete(t)
        if e:
            P("  en-tête : " + " ; ".join(f"{k}: {v}" for k, v in e.items()))
        else:
            P("  en-tête quand: / outils: / sorte: absent (gabarit : corpus/fiches/_MODELE.md)")
        ss = sections(t)
        for ln, s in ss[-4:]:
            P(f"    l.{ln} {s[:90]}")
        if len(ss) > 4:
            P(f"    ({len(ss)} sections ; les 4 dernières ci-dessus)")

    # 3. candidats
    texte_milan = (avec or {}).get("mots_milan") or " ".join(e["texte"] for e in mots)
    P("\n## 3. Où ses mots recoupent le cerveau (candidats à RELIRE, pas une décision)")
    try:
        cs = candidats(texte_milan)
    except Exception as ex:   # l'aide ne doit jamais faire échouer la revue
        cs = []
        P(f"  (recoupement indisponible : {ex})")
    for sc, s, communs in cs:
        mark = " <- fiche active" if fa and s["fichier"].endswith(os.path.basename(fa)) else ""
        P(f"  {sc:.2f}  {s['fichier']}:{s['debut']} §{s['id']} [{sorte_de(s['fichier'])}]{mark}"
          + (f"  mots communs : {', '.join(communs)}" if communs else ""))
    if not cs:
        P("  aucun recoupement : une fiche nouvelle est peut-être à créer (en dernier).")
    P("  Pour chercher un concept : python3 outils/rappel.py \"<concept>\"")

    # 4. check-list
    P("\n## 4. Check-list (une seule revue par retour)")
    for l in ORDRE:
        P("  " + l)
    P("  « Rien à inscrire » est une sortie possible : l'écrire sous le retour dans RETOURS.md, avec la raison.")
    P("  Ne pas s'arrêter à la fiche : ses mots EXACTS en citation, la date, le statut.")
    npi, fmt = depuis_modele()
    P("\n  Ne pas inscrire" + ("" if npi else " (liste par défaut : _MODELE.md introuvable)") + " :")
    for l in npi or NE_PAS_INSCRIRE_DEFAUT:
        P("   - " + l)
    P("\n  Format d'une entrée (corpus/fiches/_MODELE.md, plan §2.3) :")
    for l in (fmt or "**<id> <ce que l'image dit>**\n- Statut : …\n- Source : Milan (<date>) : « … »").splitlines():
        P("    " + l)
    P("\n  Outils après la revue : outils/deplacer.py (absorber une entrée ailleurs, --essai par défaut),")
    P("  outils/lint_cerveau.py <fiche> (chemins, §, citations), outils/archive_check.py.")

    # 5. git
    P("\n## 5. Le retour a-t-il nourri une fiche ? (git, lecture seule)")
    if sans_git:
        P("  (vérification git sautée : --sans-git)")
    else:
        try:
            av, info = verifier_git()
            rien = re.search(r"rien [àa] inscrire", derniere_entree_retours(), re.I)
            for i in info:
                P("  " + i)
            for a in av:
                if rien:
                    P("  (" + a + ") -> la dernière entrée de RETOURS dit « rien à inscrire » : noté.")
                else:
                    P("  AVERTISSEMENT : " + a)
                    P("    -> une revue à faire (ci-dessus), ou écrire « rien à inscrire : <raison> » sous le retour.")
            if not av and not info:
                P("  rien à signaler.")
        except Exception as ex:
            P(f"  (git indisponible : {ex})")
    return 0


if __name__ == "__main__":
    try:
        code = main(sys.argv[1:])
    except Exception as exc:   # jamais bloquant
        print(f"(revue : erreur ignorée : {exc})")
        code = 0
    sys.exit(code)
