"""
LINT DU CERVEAU : ce que la mémoire affirme, est-ce que ça existe vraiment ?
CONSULTATIF : il avertit, il ne bloque jamais rien (ni commit, ni export).

Pourquoi (audit + plan de réorganisation du 2026-09-26, brique A7, plan
§2.4 point 10) : la mémoire se trompait sans que rien ne le voie.
- 49 entrées du CARNET sur 72 n'avaient aucun statut (mesuré, lu, essayé…) :
  une lecture de 2 vignettes pesait autant qu'une mesure.
- 13 citations de Milan sur 24 ne se retrouvaient pas mot pour mot dans ses
  vrais messages : on citait nos reformulations comme ses mots.
- La « fiche UN_SEUL_COUP §11 » était citée comme source (verify_export,
  RETOURS, ETAT) alors qu'elle n'existait pas.
- CARNET 2.9 décrivait un « garde-fou mis dans l'export » retiré depuis
  (6f0539e) : la mémoire promettait un contrôle que le code n'a plus.
Chez Hermes Agent, le compte rendu vient des actions réelles, pas de la
prose (`background_review.py:663`). Ici, pareil : on confronte la prose aux
fichiers. Mais on NE BLOQUE PAS : Hermes a connu une « tempête de refus »
(~346 refus en 2 jours) ; et Milan : « on apprend, pas de règles gravées
dans la roche ». Un signalement est une question à regarder, pas une faute.

Ce qu'il signale (type -> ce que ça veut dire) :
- entree_sans_statut : une entrée du CARNET (ou une section de fiche) sans
  aucun des statuts (mesuré / lu / vu dans les refs / essayé / retour de
  Milan / déduit / non établi / CONTREDIT) ;
- citation_milan_introuvable : un « … » attribué à Milan qu'on ne retrouve
  pas dans corpus/milan_verbatim.jsonl (tolérance : casse, ponctuation,
  apostrophes ; « … » et [insertions] coupent la citation en morceaux) ;
  la meilleure correspondance approchée est donnée pour aider. Les mots de
  Milan sont lus avec les corrections de corpus/milan_verbatim_corrections.jsonl
  (un texte COLLÉ, brief ou conseil d'IA, ne compte pas comme ses mots : une
  citation retrouvée seulement là est signalée). Une citation suivie de
  « (paraphrase, pas ses mots) » n'est pas cherchée (comptée à part) ;
- chemin_introuvable / ligne_hors_fichier : un chemin cité (`x/y.py`,
  RETOURS.md:828) qui n'existe pas dans le dépôt, ou une ligne au-delà de
  la fin du fichier ;
- renvoi_introuvable : un « §n » (ou « CARNET 2.9 ») dont la section
  n'existe pas dans le fichier visé ; renvoi_ambigu : un « §n » nu absent
  du fichier courant mais présent ailleurs (à préciser) ;
- absolu_sans_source : une phrase en « jamais / toujours / doit / il faut »
  sans source dans la phrase (citation, chemin, §, date, mesure, Milan…) ;
- garde_fou_introuvable : une phrase qui annonce un garde-fou ou un contrôle
  d'export dont on ne retrouve ni l'identifiant, ni les mots, ni le seuil
  dans le code de la production (verify_export…) ; garde_fou_non_verifiable :
  annonce sans rien de vérifiable (à relire).

Heuristiques assumées : des faux positifs existent (un « toujours » qui veut
dire « encore », un § d'un autre document). Le rapport sert à RELIRE.

Usage :
  python3 lint_cerveau.py [fichier.md ...] [--json sortie.json] [--md sortie.md]
      (sans fichier : CARNET.md, fiches/*.md, CATALOGUE_REFS.md, ETAT.md, NOYAU.md)
Code de sortie : toujours 0.
"""
import datetime
import difflib
import glob
import json
import os
import re
import sys
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
BRAIN = os.path.normpath(os.path.join(HERE, ".."))
ROOT = os.path.normpath(os.path.join(BRAIN, "..", "..", ".."))
VERBATIM = os.path.join(BRAIN, "corpus", "milan_verbatim.jsonl")

TYPES = ("entree_sans_statut", "citation_milan_introuvable", "chemin_introuvable", "ligne_hors_fichier",
         "renvoi_introuvable", "renvoi_ambigu", "absolu_sans_source", "garde_fou_introuvable",
         "garde_fou_non_verifiable")


def defaut_fichiers():
    c = os.path.join(BRAIN, "corpus")
    return ([os.path.join(c, "CARNET.md")] + sorted(f for f in glob.glob(os.path.join(c, "fiches", "*.md")) if not os.path.basename(f).startswith("_"))
            + [os.path.join(c, "CATALOGUE_REFS.md"), os.path.join(BRAIN, "ETAT.md")]
            + [p for p in [os.path.join(BRAIN, "NOYAU.md")] if os.path.exists(p)])


# ------------------------------------------------------------ texte
def sans_accents(s):
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")


def norm_mots(s, accents=True):
    """Casse, ponctuation et apostrophes neutralisées -> mots séparés par un espace."""
    s = unicodedata.normalize("NFKC", s).lower().replace("’", "'").replace("œ", "oe")
    if not accents:
        s = sans_accents(s)
    s = re.sub(r"[^\w]+", " ", s)
    return " " + " ".join(s.split()) + " "


def rel(p):
    return os.path.relpath(p, ROOT)


class Doc:
    """Un fichier markdown : lignes, lignes hors blocs de code, paragraphes."""

    def __init__(self, path):
        self.path = path
        self.lignes = open(path, encoding="utf-8").read().splitlines()
        self.code = set()
        dedans = False
        for i, l in enumerate(self.lignes):
            if l.strip().startswith("```"):
                dedans = not dedans
                self.code.add(i)
            elif dedans:
                self.code.add(i)

    def paragraphes(self):
        """[(texte joint, [(offset, n° de ligne 1-based)], est_tableau)] hors code.
        Une ligne de tableau ou un item de liste ouvre son propre paragraphe."""
        out, cur, carte = [], [], []

        def fin():
            if cur:
                out.append((" ".join(cur), list(carte), cur[0].lstrip().startswith("|")))
            cur.clear(); carte.clear()
        for i, l in enumerate(self.lignes):
            s = l.strip()
            if i in self.code or not s:
                fin(); continue
            if s.startswith("|") or s.startswith("#") or re.match(r"^([-*]|\d+\.)\s", s):
                fin()
            carte.append((sum(len(x) + 1 for x in cur), i + 1))
            cur.append(s)
            if s.startswith("|") or s.startswith("#"):
                fin()
        fin()
        return out


def ligne_de(carte, off):
    n = carte[0][1]
    for o, ln in carte:
        if o <= off:
            n = ln
    return n


def phrases(texte):
    """[(offset, phrase)] ; coupe après . ! ? suivis d'une majuscule / « / -."""
    out, d = [], 0
    for m in re.finditer(r"(?<=[.!?])\s+(?=[A-ZÉÈÀÂÎÔÛÇ«*(\-\[])", texte):
        out.append((d, texte[d:m.start()]))
        d = m.end()
    out.append((d, texte[d:]))
    return out


# ------------------------------------------------------------ index du dépôt
_INDEX = None


def index_depot():
    """{basename: [chemins relatifs]} de tout le dépôt (hors .git, caches)."""
    global _INDEX
    if _INDEX is None:
        _INDEX = {}
        for dp, dn, fs in os.walk(ROOT):
            dn[:] = [d for d in dn if d not in (".git", "__pycache__", "node_modules", "captures_local")]
            for f in fs + dn:
                _INDEX.setdefault(f, []).append(os.path.relpath(os.path.join(dp, f), ROOT))
    return _INDEX


# ------------------------------------------------------------ 1. statuts
STATUTS = {
    "mesuré": r"mesur",
    "lu": r"texte v[ée]rifi|lu par|lu \(|\blu\b|lecture|extrait|lu dans",
    "vu dans les refs": r"\bvu\b|\bvus\b|vue? dans|v[ée]rifi[ée] (à|a) l'[ée]cran",
    "essayé": r"essay|appris en construisant",
    "retour de Milan": r"retour de milan|milan",
    "déduit": r"d[ée]duit",
    "non établi": r"non [ée]tabli",
    "CONTREDIT": r"contredit",
}


def marqueurs_statut(bloc):
    """Texte où un statut peut se dire : italiques *…*, lignes « Statut : »,
    crochets [CONTREDIT …]."""
    t = " ".join(bloc)
    m = re.findall(r"(?<!\*)\*(?!\*)([^*]{2,160})\*(?!\*)", t)
    m += [l for l in bloc if re.match(r"^\s*[-*]?\s*\**statut", l, re.I)]
    m += re.findall(r"\[[^\]]*contredit[^\]]*\]", t, re.I)
    m += re.findall(r"\(([^()]{2,160})\)", " ".join(bloc[:2]))      # « (mesuré, pas écouté…) » du titre
    return " | ".join(m)


def entrees(doc):
    """[(id, n° ligne, lignes)] : entrées **n.n** du CARNET, sections ## des fiches."""
    carnet = os.path.basename(doc.path) == "CARNET.md"
    fiche = os.sep + "fiches" + os.sep in doc.path
    if not (carnet or fiche):
        return []
    out, cur = [], None
    for i, l in enumerate(doc.lignes):
        if i in doc.code:
            if cur:
                cur[2].append(l)
            continue
        m = re.match(r"^\*\*(\d+[a-z]?(?:\.\d+[a-z]?)*)\b", l) if carnet else re.match(r"^##\s+(.+)", l)
        if m or (carnet and l.startswith("#")):
            if cur:
                out.append(cur)
            cur = [m.group(1).strip()[:60], i + 1, [l]] if m else None
        elif cur:
            cur[2].append(l)
    if cur:
        out.append(cur)
    return out


def verifier_statuts(doc, sig):
    for eid, ln, bloc in entrees(doc):
        if len([l for l in bloc if l.strip()]) < 2:
            continue
        mk = marqueurs_statut(bloc)
        trouves = [k for k, rx in STATUTS.items() if re.search(rx, mk, re.I)]
        if not trouves:
            sig.append({"type": "entree_sans_statut", "fichier": rel(doc.path), "ligne": ln, "entree": eid,
                        "detail": ("marqueur hors des statuts : « " + mk[:80] + " »") if mk else "aucun marqueur",
                        "extrait": bloc[0].strip()[:160]})


# ------------------------------------------------------------ 2. citations de Milan
_MOTS_FR = set("le la les de des du un une et est pas que qui je tu il on ça ca ce en à a au aux pour dans sur "
               "avec mais ou se sa son ses me te ne plus très tres c j l d n qu".split())
_TITRES = {" un seul coup ", " poing du dragon ", " serious punch ", " serious punch 2 "}
_MOTS_EN = set("the a an of to and is it in that you your this for with on as be are not but have they what "
               "when would if so can do all one my he his was".split())


def _entrees_verbatim():
    """Entrées de milan_verbatim avec les corrections appliquées (outils/moisson_milan.py)."""
    try:
        if HERE not in sys.path:
            sys.path.insert(0, HERE)
        import moisson_milan
        return moisson_milan.charger_verbatim()
    except Exception:                    # consultatif : repli sur le brut
        out = []
        if os.path.exists(VERBATIM):
            for l in open(VERBATIM, encoding="utf-8"):
                try:
                    out.append(json.loads(l))
                except json.JSONDecodeError:
                    continue
        return out


def charger_verbatim(colles=False):
    """Les mots de Milan (colles=False) ; ou (colles=True) les textes COLLÉS que la
    correction a retirés de ses mots, pour dire d'où vient une citation."""
    msgs = []
    for e in _entrees_verbatim():
        t = (e.get("texte_colle") or "") if colles else (e.get("texte") or e.get("debut") or "")
        if not t:
            continue
        msgs.append({"date": e.get("date"), "sha1": e.get("sha1"), "mode": e.get("mode"), "brut": t,
                     "n": norm_mots(t), "na": norm_mots(t, accents=False)})
    return msgs


def morceaux(q):
    """Une citation -> morceaux cherchables (« … », […] et [insertions] coupent)."""
    q = re.sub(r"\[[^\]]*\]", " … ", q)
    parts = re.split(r"…|\.\.\.", q)
    return [p for p in (norm_mots(x) for x in parts) if len(p.split()) >= 2]


def chercher_citation(q, msgs):
    ms = morceaux(q)
    if not ms:
        return None
    for champ, niveau in (("n", "exacte"), ("na", "aux accents près")):
        mm = ms if champ == "n" else [norm_mots(sans_accents(x)) for x in ms]
        for m in msgs:
            if all(x in m[champ] for x in mm):
                return {"niveau": niveau, "date": m["date"], "sha1": m["sha1"]}
        if all(any(x in m[champ] for m in msgs) for x in mm):
            return {"niveau": niveau + ", en morceaux (plusieurs messages)"}
    return {"niveau": "introuvable"}


def meilleure_approche(q, msgs):
    mots = [w for w in norm_mots(q, accents=False).split() if len(w) >= 3]
    if not mots:
        return None
    best = (0.0, None)
    for m in msgs:
        tm = m["na"].split()
        if not tm:
            continue
        sm = difflib.SequenceMatcher(None, mots, tm, autojunk=False)
        a = sum(b.size for b in sm.get_matching_blocks()) / len(mots)
        if a > best[0]:
            best = (a, m)
    if best[1] is None:
        return None
    m = best[1]
    # proximité en CARACTÈRES sur la meilleure fenêtre du message (fautes de frappe corrigées ?)
    qa = norm_mots(q, accents=False).strip()
    ma = m["na"].strip()
    prox, extrait = 0.0, m["brut"][:220]
    pas = max(1, len(qa) // 6)
    for d in range(0, max(1, len(ma) - len(qa) // 2), pas):
        r = difflib.SequenceMatcher(None, qa, ma[d:d + int(len(qa) * 1.15) + 2], autojunk=False).ratio()
        if r > prox:
            prox = r
    return {"part_des_mots_retrouves_dans_l_ordre": round(best[0], 2), "proximite_caracteres": round(prox, 2),
            "date": m["date"], "sha1": m["sha1"], "mode": m["mode"], "message": extrait}


RX_PARAPHRASE = re.compile(r"^\s*[,;]?\s*\((?:[^()]{0,40}\b)?paraphrase", re.I)


def sans_noms_de_fichier(t):
    """« milan » dans `moisson_milan.py` ou notes_milan.jsonl n'attribue rien à Milan."""
    t = re.sub(r"`[^`]*`", " ", t)
    return re.sub(r"[\w./-]*_milan[\w./-]*|[\w./-]*milan_[\w./-]*", " ", t, flags=re.I)


def verifier_citations(doc, msgs, sig, stats, colles=()):
    entete_tableau, precedent = "", ""
    for texte, carte, tableau in doc.paragraphes():
        if tableau and re.match(r"^\|\s*[-: ]+\|", texte):
            entete_tableau = precedent.lower()      # l'en-tête est la ligne AVANT |---| (pas n'importe quelle ligne)
            continue
        precedent = texte if tableau else ""
        if not tableau:
            entete_tableau = ""
        for m in re.finditer(r"«\s*(.+?)\s*»", texte):
            q = m.group(1)
            if len(norm_mots(q).split()) < 3:
                continue
            mots = norm_mots(q).split()
            if sum(w in _MOTS_EN for w in mots) >= 0.3 * len(mots) or not any(w in _MOTS_FR for w in mots) \
                    or norm_mots(q) in _TITRES:
                continue                         # anglais (Williams, Disney…), titre, nom de ref
            if RX_PARAPHRASE.match(texte[m.end():m.end() + 60]):
                stats["citations_marquees_paraphrase"] += 1
                continue                         # marquée « (paraphrase, pas ses mots) » : pas une citation
            avant = sans_noms_de_fichier(texte[max(0, m.start() - 250):m.start()])
            k = avant.lower().rfind("milan")
            # attribuée si « Milan » précède SANS fin de phrase entre les deux (« Milan : « a » ; « b » » oui ;
            # « (Milan, v1). L'image dit « … » » non : c'est notre phrase)
            attribuee = (k >= 0 and not re.search(r"[.!?]\s+[A-ZÉÈÀ(]", avant[k:])) or \
                (tableau and ("milan" in entete_tableau or "ses mots" in entete_tableau))
            if not attribuee:
                continue
            stats["citations_milan_vues"] += 1
            r = chercher_citation(q, msgs)
            if r is None:
                continue
            if r["niveau"] == "introuvable":
                ap = meilleure_approche(q, msgs)
                s_ = {"type": "citation_milan_introuvable", "fichier": rel(doc.path),
                      "ligne": ligne_de(carte, m.start()), "citation": q[:240], "approche": ap,
                      "proche": bool(ap and ap["proximite_caracteres"] >= 0.85)}
                rc = chercher_citation(q, colles) if colles else None
                if rc and rc["niveau"] != "introuvable":
                    s_["dans_texte_colle"] = rc.get("sha1") or True
                sig.append(s_)
            else:
                stats["citations_milan_retrouvees"] += 1


# ------------------------------------------------------------ 3. chemins
EXT = r"(?:py|md|json|jsonl|png|jpe?g|gif|webp|mp4|rbxmx|rbxm|html|js|txt|log|sh|luau|lua|blend|glsl|csv|wav|ogg|mp3)"
RX_CHEMIN = re.compile(r"(?<![\w/.-])((?:[\w.-]+/)*[\w.-]+\." + EXT + r")(?::(\d+)(?:[-–](\d+))?)?(?![\w/])")
RX_DOSSIER = re.compile(r"^(?:[\w.-]+/)+$")


def bases(doc):
    d = os.path.dirname(doc.path)
    return [d, BRAIN, os.path.join(BRAIN, "corpus"), os.path.join(BRAIN, "outils"),
            os.path.join(BRAIN, "corpus", "fiches"), ROOT, os.path.join(ROOT, "experiments"),
            os.path.join(ROOT, "experiments", "_shared"), os.path.join(ROOT, "docs"),
            os.path.join(ROOT, "captures", "verification")]


def resoudre(tok, doc):
    """Chemin absolu existant, ou None."""
    tok = tok.strip()
    if tok.startswith("/"):
        return tok if os.path.exists(tok) else None
    for b in bases(doc):
        p = os.path.normpath(os.path.join(b, tok))
        if os.path.exists(p):
            return p
    idx = index_depot()
    nom = os.path.basename(tok.rstrip("/"))
    for c in idx.get(nom, []):
        if c.endswith(tok.rstrip("/").lstrip("./")):
            return os.path.join(ROOT, c)
    return None


RX_HORS_DEPOT = re.compile(r"hors d[ée]p[ôo]t|non versionn|jamais versionn|scratchpad|\(session\)", re.I)


def _ignorer(tok):
    """Ce qui n'est pas censé être dans le dépôt : refs envoyées par Milan (préfixe d'upload, jamais
    versionnées : droits), sources .rbxm sous licence, noms de bibliothèque, gabarits."""
    base = os.path.basename(tok)
    return (any(c in tok for c in "<>*{}$~…") or tok.startswith(("http", "/tmp")) or "scratchpad" in tok
            or tok.startswith(("poing/", "…")) or tok.count(".") > 4
            or re.match(r"^[0-9a-f]{8}-", base) or base.startswith("IMG_") or tok.endswith(".rbxm")
            or base in ("three.js", "d3.js", "node.js"))


def verifier_chemins(doc, sig, stats):
    vus = set()
    for i, l in enumerate(doc.lignes):
        cands = []
        for m in RX_CHEMIN.finditer(l):
            cands.append((m.group(1), m.group(2), m.group(3), m.start(1)))
        for m in re.finditer(r"`([^`]+)`", l):
            for w in m.group(1).split():
                w = w.strip("\"'(),;")
                if RX_DOSSIER.match(w) and len(w) > 3:
                    cands.append((w, None, None, m.start()))
        for tok, l0, l1, pos in cands:
            if _ignorer(tok) or l[max(0, pos - 12):pos].rstrip().endswith("://") or RX_HORS_DEPOT.search(l) \
                    or (pos > 0 and l[pos - 1] == "<"):
                continue
            # un nom seul sans dossier ni extension de code est souvent un mot (ex. « v1.md » improbable)
            cle = (tok, l0, i)
            if cle in vus:
                continue
            vus.add(cle)
            stats["chemins_vus"] += 1
            p = resoudre(tok, doc)
            if p is None:
                sig.append({"type": "chemin_introuvable", "fichier": rel(doc.path), "ligne": i + 1, "chemin": tok,
                            "extrait": l.strip()[:160]})
                continue
            if l0 and os.path.isfile(p):
                try:
                    n = sum(1 for _ in open(p, encoding="utf-8", errors="ignore"))
                except OSError:
                    continue
                fin = int(l1 or l0)
                if fin > n:
                    sig.append({"type": "ligne_hors_fichier", "fichier": rel(doc.path), "ligne": i + 1,
                                "chemin": f"{tok}:{l0}" + (f"-{l1}" if l1 else ""), "lignes_du_fichier": n,
                                "extrait": l.strip()[:160]})


# ------------------------------------------------------------ 4. renvois §
RX_NUM = r"(\d+[a-z]?(?:\.\d+[a-z]?)*)"
_SECTIONS = {}


def sections(path):
    """Ids de section d'un fichier : titres « ## 2.1 », « ## 4b. », entrées **2.9."""
    if path not in _SECTIONS:
        ids = set()
        try:
            d = Doc(path)
        except (OSError, UnicodeDecodeError):
            _SECTIONS[path] = ids
            return ids
        for i, l in enumerate(d.lignes):
            if i in d.code:
                continue
            m = re.match(r"^#{1,6}\s+(?:§\s*)?(?:le[cç]on\s+)?" + RX_NUM + r"(?:\s*(bis|ter|quater))?\b", l, re.I)
            if m:
                ids.add(m.group(1).lower())
                if m.group(2):
                    ids.add((m.group(1) + " " + m.group(2)).lower())
            m = re.match(r"^\*\*(?:§\s*)?" + RX_NUM + r"\b", l)
            if m:
                ids.add(m.group(1).lower())
        _SECTIONS[path] = ids
    return _SECTIONS[path]


def section_existe(path, num):
    num = num.lower()
    for s in sections(path):
        if s == num or s.startswith(num + ".") or (s.startswith(num) and s[len(num):len(num) + 1].isalpha()):
            return True
    return False


def docs_nommes():
    """{nom (minuscule): chemin} : fichiers .md du cerveau et de docs/, + alias."""
    out = {}
    for p in glob.glob(os.path.join(BRAIN, "*.md")) + glob.glob(os.path.join(BRAIN, "corpus", "*.md")) \
            + glob.glob(os.path.join(BRAIN, "corpus", "fiches", "*.md")) + glob.glob(os.path.join(ROOT, "docs", "*.md")):
        out[os.path.basename(p)[:-3].lower()] = p
    alias = {"carnet": "carnet", "lecon": "lecons", "leçon": "lecons", "leçons": "lecons", "lecons": "lecons",
             "etat": "etat", "état": "etat", "retours": "retours"}
    for a, b in alias.items():
        if b in out:
            out[a] = out[b]
    m = os.path.join(ROOT, "docs", "PRODUCTION_MANDATE_v1.md")
    if os.path.exists(m):
        out["mandat"] = m
    return out


def verifier_renvois(doc, sig, stats):
    noms = docs_nommes()
    fiches = glob.glob(os.path.join(BRAIN, "corpus", "fiches", "*.md"))
    autres = fiches + [noms[k] for k in ("carnet", "etat") if k in noms]
    rx_nomme = re.compile(r"(?<![\w/])(`?[\w./-]+?`?|[A-Za-zÉéèç_]+)(\.md)?`?\s*(§\s*|\s(?=\d))" + RX_NUM)
    for i, l in enumerate(doc.lignes):
        if i in doc.code:
            continue
        pris = set()
        for m in rx_nomme.finditer(l):
            nom = m.group(1).strip("`")
            num = m.group(4)
            cible = None
            if "/" in nom or nom.endswith(".md"):
                cible = resoudre(nom if nom.endswith(".md") else nom + ".md", doc)
            elif nom.lower() in noms and (m.group(3).strip() == "§" or nom.isupper()):
                cible = noms[nom.lower()]
            if cible is None:
                continue
            pris.add(m.start(4))
            stats["renvois_vus"] += 1
            if not section_existe(cible, num):
                sig.append({"type": "renvoi_introuvable", "fichier": rel(doc.path), "ligne": i + 1,
                            "renvoi": f"{os.path.basename(cible)} §{num}", "extrait": l.strip()[:160]})
        for m in re.finditer(r"§\s*" + RX_NUM, l):
            if m.start(1) in pris or any(abs(m.start(1) - p) < 3 for p in pris):
                continue
            num = m.group(1)
            stats["renvois_vus"] += 1
            if section_existe(doc.path, num):
                continue
            ailleurs = [os.path.basename(p) for p in autres if p != doc.path and section_existe(p, num)]
            fiche_dite = re.search(r"fiche\s*$", l[:m.start()].rstrip()[-12:] + " ", re.I) or "fiche" in l[max(0, m.start() - 12):m.start()].lower()
            if ailleurs:
                sig.append({"type": "renvoi_ambigu", "fichier": rel(doc.path), "ligne": i + 1, "renvoi": f"§{num}",
                            "detail": f"absent de ce fichier ; existe dans {', '.join(ailleurs[:4])}",
                            "extrait": l.strip()[:160]})
            else:
                sig.append({"type": "renvoi_introuvable", "fichier": rel(doc.path), "ligne": i + 1,
                            "renvoi": f"§{num}" + (" (fiche)" if fiche_dite else ""),
                            "detail": "absent de ce fichier, des fiches, du CARNET et d'ETAT",
                            "extrait": l.strip()[:160]})


# ------------------------------------------------------------ 5. absolus
RX_ABSOLU = re.compile(r"\b(jamais|toujours|doit|doivent|devra|devront|il faut)\b", re.I)
RX_SOURCE = re.compile(r"«|`|§|retours|carnet|le[cç]on|milan|mesur|verbatim|\b[0-9a-f]{7,16}\b|https?://|"
                       r"texte v[ée]rifi|lu par|vu dans|\bref\b|réf|source|\d{4}-\d{2}-\d{2}|\bv\d+\b|"
                       r"\.py|\.md|\.json|tsb|williams|disney|walt|essay", re.I)


def verifier_absolus(doc, sig, stats):
    for texte, carte, _tab in doc.paragraphes():
        if texte.startswith("#"):
            continue
        for off, ph in phrases(texte):
            hors = re.sub(r"«.*?»|`[^`]*`|“.*?”|\"[^\"]*\"", " ", ph)
            hors = re.sub(r"toujours pas|pas toujours|n'est pas toujours|pas forcément", " ", hors, flags=re.I)
            m = RX_ABSOLU.search(hors)
            if not m:
                continue
            stats["absolus_vus"] += 1
            if RX_SOURCE.search(ph):
                continue
            sig.append({"type": "absolu_sans_source", "fichier": rel(doc.path), "ligne": ligne_de(carte, off),
                        "mot": m.group(1), "extrait": ph.strip()[:200]})


# ------------------------------------------------------------ 6. garde-fous annoncés
RX_GARDE = re.compile(r"garde[- ]fou|contr[ôo]les?\s+(?:d'export|dans l'export|de l'export|bloquants?)|"
                      r"bloque(?:nt)? l'export|dans (?:le |l')?verify_export|contr[ôo]le d'export", re.I)
RX_RETIRE = re.compile(r"retir|supprim|n'existe plus|n'a plus|plus de r[èe]gles|abandonn|ancien|absent du code", re.I)
_STOP = set("pour dans avec sans plus moins sous vers comme depuis entre tout tous toute toutes elle elles "
            "leur leurs cette celle ceux dont mais donc être avoir fait faire".split())


def _prod_de(texte, doc):
    t = texte.lower() + " " + os.path.basename(doc.path).lower()
    if "un seul coup" in t or "un_seul_coup" in t or "usc" in t:
        return "r6_un_seul_coup"
    if "dragon" in t:
        return "r6_poing_dragon"
    return None


def code_actif(path):
    """Le code sans commentaires ni docstrings : un contrôle cité dans un commentaire
    (« retiré le … ») n'est pas un contrôle."""
    t = open(path, encoding="utf-8", errors="ignore").read()
    t = re.sub(r'"""[\s\S]*?"""|\'\'\'[\s\S]*?\'\'\'', " ", t)
    return "\n".join(re.sub(r"(^|\s)#.*$", "", l) for l in t.splitlines())


def code_controle(prod, ph, doc):
    """Fichiers de code où chercher le contrôle annoncé (un nom de fichier cité est
    cherché d'abord dans la production du paragraphe)."""
    fs = []
    for m in RX_CHEMIN.finditer(ph):
        if m.group(1).endswith(".py"):
            p = None
            if prod and "/" not in m.group(1):
                c = glob.glob(os.path.join(ROOT, "experiments", prod, "**", m.group(1)), recursive=True)
                p = c[0] if c else None
            p = p or resoudre(m.group(1), doc)
            if p:
                fs.append(p)
    if not fs:
        motif = os.path.join(ROOT, "experiments", prod or "*", "scripts", "verify_export*.py")
        fs = glob.glob(motif) + ([os.path.join(BRAIN, "rules.py")] if prod is None else [])
    return fs


def verifier_garde_fous(doc, sig, stats):
    for texte, carte, _tab in doc.paragraphes():
        for off, ph in phrases(texte):
            if not RX_GARDE.search(ph) or RX_RETIRE.search(ph):
                continue
            stats["garde_fous_vus"] += 1
            prod = _prod_de(texte, doc)
            fichiers = code_controle(prod, ph, doc)
            code = "\n".join(code_actif(f) for f in fichiers)
            codeA = sans_accents(code.lower())
            idents = set(re.findall(r"[a-z_][a-z0-9_]{5,}", codeA))
            lignesA = codeA.splitlines()
            items = []
            for m in re.finditer(r"`([A-Za-z_][\w.]{3,})`", ph):
                x = m.group(1)
                if "." in x and x.rsplit(".", 1)[-1] in ("py", "md", "json"):
                    continue
                items.append(("identifiant", x, x.lower().split(".")[-1] in codeA))
            for m in re.finditer(r"«\s*(.+?)\s*»", ph):
                mots = [w for w in norm_mots(m.group(1), accents=False).split() if len(w) >= 4 and w not in _STOP]
                if len(mots) < 2:
                    continue
                seuil = max(2, int(0.7 * len(mots) + 0.5))
                ok = any(sum(w[:5] in idt for w in mots) >= seuil for idt in idents) \
                    or any(sum(w[:5] in la for w in mots) >= seuil for la in lignesA)
                items.append(("mots", m.group(1), ok))
            for m in re.finditer(r"([<>≤≥])\s*(\d+(?:[.,]\d+)?)", ph):
                v = m.group(2).replace(",", ".")
                ok = bool(re.search(r"[<>]=?\s*" + re.escape(v) + r"(?!\d)", code))
                items.append(("seuil", m.group(1) + " " + v, ok))
            base = {"fichier": rel(doc.path), "ligne": ligne_de(carte, off), "extrait": ph.strip()[:220],
                    "code_cherche": [rel(f) for f in fichiers]}
            if not items:
                sig.append({"type": "garde_fou_non_verifiable", **base,
                            "detail": "annonce sans identifiant, mots cités ni seuil : à relire à la main"})
            elif not any(ok for _k, _x, ok in items):
                sig.append({"type": "garde_fou_introuvable", **base,
                            "absents": [f"{k} : {x}" for k, x, _ok in items]})
            elif not all(ok for _k, _x, ok in items):
                sig.append({"type": "garde_fou_introuvable", **base, "detail": "en partie",
                            "absents": [f"{k} : {x}" for k, x, ok in items if not ok]})


# ------------------------------------------------------------ rapport
def lint(fichiers):
    msgs = charger_verbatim()
    colles = charger_verbatim(colles=True)
    sig = []
    stats = {k: 0 for k in ("citations_milan_vues", "citations_milan_retrouvees", "citations_marquees_paraphrase",
                            "chemins_vus", "renvois_vus", "absolus_vus", "garde_fous_vus")}
    stats["entrees_vues"] = 0
    for f in fichiers:
        doc = Doc(f)
        stats["entrees_vues"] += sum(1 for e in entrees(doc) if len([x for x in e[2] if x.strip()]) >= 2)
        verifier_statuts(doc, sig)
        verifier_citations(doc, msgs, sig, stats, colles)
        verifier_chemins(doc, sig, stats)
        verifier_renvois(doc, sig, stats)
        verifier_absolus(doc, sig, stats)
        verifier_garde_fous(doc, sig, stats)
    compte = {t: sum(1 for s in sig if s["type"] == t) for t in TYPES}
    return {"citations_tres_proches": sum(1 for s in sig if s.get("proche")), "date": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
            "consultatif": True, "fichiers": [rel(f) for f in fichiers],
            "messages_de_milan_lus": len(msgs), "vus": stats, "compte": compte, "signalements": sig}


def _ligne(s):
    loc = f"{s['fichier']}:{s['ligne']}"
    t = s["type"]
    if t == "entree_sans_statut":
        return f"{loc} [{s['entree']}] {s['detail']} -- {s['extrait']}"
    if t == "citation_milan_introuvable":
        a = s.get("approche") or {}
        ap = (f"\n      au plus près ({int(100 * a['part_des_mots_retrouves_dans_l_ordre'])} % des mots dans l'ordre, "
              f"{int(100 * a['proximite_caracteres'])} % des caractères{' : TRÈS PROCHE, orthographe corrigée ?' if s.get('proche') else ''} ; "
              f"{(a.get('date') or '')[:16]}, {a.get('sha1')}) : {a.get('message', '')[:160]!r}") if a else ""
        col = (f"\n      trouvée seulement dans un texte COLLÉ ({s['dans_texte_colle']}) : pas ses mots"
               if s.get("dans_texte_colle") else "")
        return f"{loc} « {s['citation']} »{col}{ap}"
    if t in ("chemin_introuvable",):
        return f"{loc} {s['chemin']} -- {s['extrait']}"
    if t == "ligne_hors_fichier":
        return f"{loc} {s['chemin']} (le fichier a {s['lignes_du_fichier']} lignes)"
    if t in ("renvoi_introuvable", "renvoi_ambigu"):
        return f"{loc} {s['renvoi']} {('(' + s['detail'] + ')') if s.get('detail') else ''} -- {s['extrait']}"
    if t == "absolu_sans_source":
        return f"{loc} « {s['mot']} » : {s['extrait']}"
    if t.startswith("garde_fou"):
        d = "; ".join(s.get("absents", [])) or s.get("detail", "")
        return f"{loc} {d}\n      phrase : {s['extrait']}\n      code cherché : {', '.join(s['code_cherche']) or 'aucun'}"
    return f"{loc} {s}"


SENS = {
    "entree_sans_statut": "entrées sans statut (mesuré / lu / vu / essayé / retour de Milan / déduit / non établi / CONTREDIT)",
    "citation_milan_introuvable": "citations attribuées à Milan introuvables mot pour mot dans milan_verbatim.jsonl",
    "chemin_introuvable": "chemins cités qui n'existent pas dans le dépôt",
    "ligne_hors_fichier": "renvois fichier:ligne au-delà de la fin du fichier",
    "renvoi_introuvable": "renvois § dont la section n'existe pas",
    "renvoi_ambigu": "§ nus absents du fichier courant, présents ailleurs (préciser le fichier)",
    "absolu_sans_source": "phrases en « jamais / toujours / doit / il faut » sans source dans la phrase",
    "garde_fou_introuvable": "garde-fous / contrôles annoncés absents du code cité",
    "garde_fou_non_verifiable": "garde-fous annoncés sans rien de vérifiable",
}


def texte_rapport(r):
    out = [f"LINT DU CERVEAU (consultatif, rien n'est bloqué) -- {r['date']}",
           f"fichiers : {len(r['fichiers'])} ; messages de Milan lus : {r['messages_de_milan_lus']}",
           "vus : " + ", ".join(f"{k} {v}" for k, v in r["vus"].items()), "", "COMPTE PAR TYPE"]
    for t in TYPES:
        out.append(f"  {r['compte'][t]:4d}  {t} : {SENS[t]}")
    out.append(f"        (dont {r['citations_tres_proches']} citations très proches : orthographe de Milan corrigée ?)")
    for t in TYPES:
        ss = [s for s in r["signalements"] if s["type"] == t]
        if ss:
            out += ["", f"== {t} ({len(ss)}) =="] + ["  " + _ligne(s) for s in ss]
    return "\n".join(out)


def markdown_rapport(r):
    L = [f"# Lint du cerveau : rapport du {r['date'][:10]}", "",
         "> **Consultatif.** Produit par `outils/lint_cerveau.py` (brique A7 du plan de réorganisation,",
         "> §2.4 point 10). Rien n'est bloqué : chaque ligne est une question à relire, pas une faute.",
         "> Heuristiques : il y a des faux positifs (un « toujours » qui veut dire « encore », un § d'un",
         "> autre document). Relancer : `python3 outils/lint_cerveau.py --md <sortie.md>`.", "",
         f"Fichiers lus : {', '.join('`' + f + '`' for f in r['fichiers'])}.", "",
         f"Messages de Milan lus (`corpus/milan_verbatim.jsonl`) : {r['messages_de_milan_lus']}. "
         f"Citations attribuées à Milan vues : {r['vus']['citations_milan_vues']}, retrouvées mot pour mot "
         f"(casse et ponctuation près) : {r['vus']['citations_milan_retrouvees']}. Entrées vues : "
         f"{r['vus']['entrees_vues']}. Chemins vus : {r['vus']['chemins_vus']}. Renvois vus : "
         f"{r['vus']['renvois_vus']}. Phrases en absolu vues : {r['vus']['absolus_vus']}. "
         f"Annonces de garde-fou vues : {r['vus']['garde_fous_vus']}.", "",
         "## Compte par type", "", "| type | nb | ce que ça veut dire |", "|---|---:|---|"]
    for t in TYPES:
        L.append(f"| `{t}` | {r['compte'][t]} | {SENS[t]} |")
    L += ["", f"Parmi les citations introuvables, {r['citations_tres_proches']} sont très proches d'un vrai message "
              "(≥ 85 % des caractères) : probablement ses mots avec l'orthographe corrigée. Les autres sont des "
              "reformulations, des messages d'avant la moisson (projets précédents), ou des mots jamais écrits."]
    for t in TYPES:
        ss = [s for s in r["signalements"] if s["type"] == t]
        if not ss:
            continue
        L += ["", f"## {t} ({len(ss)})", ""]
        for s in ss:
            L.append("- " + _ligne(s).replace("\n      ", "\n  - ").replace("|", "\\|"))
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    a = sys.argv[1:]
    sj = sm = None
    if "--json" in a:
        k = a.index("--json"); sj = a[k + 1]; a = a[:k] + a[k + 2:]
    if "--md" in a:
        k = a.index("--md"); sm = a[k + 1]; a = a[:k] + a[k + 2:]
    fs = [os.path.abspath(x) for x in a] or defaut_fichiers()
    r = lint(fs)
    print(texte_rapport(r))
    if sj:
        json.dump(r, open(sj, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    if sm:
        open(sm, "w", encoding="utf-8").write(markdown_rapport(r))
    sys.exit(0)
