"""
ARCHIVE_CHECK : chaque entrée d'un fichier HISTORIQUE a-t-elle une
destination VIVANTE ? (brique A2 du plan de réorganisation,
`corpus/recherche/PLAN_REORGANISATION_2026-09-26.md` §2.4 point 8, §4.1).

Pourquoi cet outil existe. Au commit 1395eb3 (26/09, 07:20), `LECONS.md` est
passé en HISTORIQUE avec la phrase « ce qu'ils contiennent de vivant est passé
dans CARNET.md et les fiches ». Ce n'était pas vrai pour ses §10-11 (« frappe
vers le bas », « un coup droit voyage à plat ») : 47 minutes plus tard, « Un
seul coup » v1 refaisait « vers le bas ». Personne n'avait VÉRIFIÉ que chaque
entrée archivée avait bien un endroit vivant où être relue. Hermes Agent
refuse une suppression sans `absorbed_into` vers une cible qui existe ; on va
plus loin : on regarde si les NOMBRES et les TERMES CLÉS de l'entrée sont
vraiment arrivés quelque part.

Ce que fait l'outil (il ne modifie RIEN) :
1. découpe chaque fichier HISTORIQUE (liste d'ETAT.md §3) en entrées : un
   titre (#, ##, ###) = une entrée ; si une section contient au moins deux
   items numérotés en début de ligne (« 1. », « 2. »), chaque item devient
   une entrée à part ;
2. découpe les destinations en sections : CARNET (titres + entrées
   « **2.9 … »), fiches (titres), outils et code (docstring de module, puis
   une section par `def` / `class` de premier niveau) ; les sous-points
   « Origine » écrits par `deplacer.py` (texte recopié en citation) ne
   comptent pas : une copie n'est pas une digestion ;
3. pour chaque entrée, calcule par recoupement la part de ses termes rares
   (pondérés par leur rareté dans les destinations), de ses nombres et de
   ses expressions entre « » qui se retrouvent dans chaque section ;
4. imprime « entrée -> destination probable (score) | AUCUNE destination »,
   avec ce qui MANQUE (nombres, termes), et écrit un JSON si demandé.

Trois étages de destinations, dits dans le rapport :
- « vivant » : CARNET, fiches, outils/, code du cerveau encore branché ;
- « en veille » : rules.py, etats.py, critic.py, audit.py (plan §1 point 3 et
  brique A1 : muets sur le rig V2.22, gelés à la v9) : le savoir y est ÉCRIT,
  mais plus rien ne le relit pendant une production ;
- « production » : `experiments/r6_*/scripts/*.py` : le savoir est attaché à
  une production passée, la suivante ne le relit pas.
Seul l'étage « vivant » compte pour le verdict « destination vivante
complète » ; les deux autres sont affichés à côté.

Ce n'est PAS un juge : c'est une aide à la relecture. Un score est un
recoupement de mots et de nombres, pas une compréhension. Une entrée
« partielle » peut être parfaitement digérée en d'autres mots ; une entrée
« complète » peut avoir été recopiée sans avoir été comprise. Il ne bloque
rien, n'écrit rien dans le cerveau, et « abandonnée : <raison> » écrit dans
une entrée est une sortie valable (l'entrée n'est alors plus cherchée).

Usage :
  python3 outils/archive_check.py                     # tous les HISTORIQUE
  python3 outils/archive_check.py --fichier LECONS.md --entree 10
  python3 outils/archive_check.py --json sortie.json --md rapport.md
  python3 outils/archive_check.py --seuls-manques     # masque les complètes
  python3 outils/archive_check.py --cerveau <copie>   # sur une copie du cerveau
"""
import glob
import json
import math
import os
import re
import sys
import unicodedata
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
BRAIN = os.path.normpath(os.path.join(HERE, ".."))
ROOT = os.path.normpath(os.path.join(BRAIN, "..", "..", ".."))   # racine du dépôt

def regler_cerveau(dossier):
    """Pointe l'outil sur une COPIE du cerveau (tests, essais à blanc)."""
    global BRAIN, ROOT
    BRAIN = os.path.abspath(dossier)
    ROOT = os.path.normpath(os.path.join(BRAIN, "..", "..", ".."))


# Liste d'ETAT.md §3 (« Historique (daté, ne plus suivre comme protocole) »).
# Relue dans ETAT.md à chaque lancement si possible (voir historiques()).
HISTORIQUES_DEFAUT = ["LECONS.md", "CERVEAU_V2.md", "PLAN.md", "REFLEXION.md", "ANGLES_MORTS.md",
                      "SCENE_POING_DU_DRAGON.md", "corpus/ETUDE_*.md", "corpus/TUTOS_ANIMATION.md",
                      "corpus/REFERENCES_VIDEO.md"]

# Code du cerveau écrit mais plus relu (plan §1 point 3, brique A1).
EN_VEILLE = {"rules.py", "etats.py", "critic.py", "audit.py"}

# Mots-outils (après retrait des accents) : on les ignore dans le recoupement.
MOTS_VIDES = set("""
les des une un le la du de et en au aux par pour sur sous dans avec sans pas plus moins que qui quoi
est sont ete etre avoir fait faire font son ses sa leur leurs ce cet cette ces cela ca il ils elle
elles on nous vous je tu me te se lui y ou mais donc car ni si tout tous toute toutes tres trop
bien peu ne non oui meme aussi comme alors puis quand entre vers apres avant chez deja encore
jamais toujours ici la-bas autre autres chaque dont avait etait sera seront etaient ont ai as a
lire voir plus pas qu quelle quel quels quelles d l s c n j m t self none true false return def
import from class elif else for while print len int float str dict list range with the and not
this that are was were has have its into but you your any all can use used one two out get set
ils elles leurs cet car mes mon ton tes notre nos votre vos soit etc via fois cas deux trois
""".split())

MARQUE_ABSORBE = re.compile(r"(→|->)\s*absorb[ée]", re.I)
MARQUE_ABANDON = re.compile(r"abandonn[ée]e?\s*:", re.I)


# --------------------------------------------------------------------------
# Normalisation, termes, nombres, expressions
# --------------------------------------------------------------------------

def norm(s):
    s = unicodedata.normalize("NFD", s.lower())
    return "".join(c for c in s if unicodedata.category(c) != "Mn")


def racine(w):
    """Racine grossière : pluriel retiré, 6 premières lettres (« frappe »,
    « frapper », « frappes » se rejoignent ; « epaule/epaules » aussi)."""
    w = w.rstrip("sx") if len(w) > 4 else w
    return w[:6]


def termes(texte):
    """Liste des racines des mots de >= 3 lettres hors mots-outils (le rappel
    ignorait « bas », « bras », « dos » : on les garde ici)."""
    out = []
    for w in re.findall(r"[a-z]+", norm(texte)):
        if len(w) >= 3 and w not in MOTS_VIDES:
            out.append(racine(w))
    return out


_NOMBRE = re.compile(r"(?<![\w§:/.,#])(?<!\d[-−])(?<!\d –)([-−+]?)(\d+(?:[.,]\d+)?)(?![\w:/]|[.,]\d|-\d)")
_PLAGE = re.compile(r"^\s*(?:à|a|-|–|et)\s*[-−+]?\d+(?:[.,]\d+)?")   # « 15 à −30° », « 18-28° »
_UNITE = re.compile(r"^\s*(?:°|%|f\b|s\b|ms\b|px\b|i/s|stud|deg|fps|frame|image|clé|cle|degr)", re.I)


def nombres(texte):
    """Nombres « porteurs » : décimaux (0,32 stud, 1,45), entiers >= 10
    suivis d'une unité (40°, 180 f, 12 %), ou entiers >= 100 (empreintes
    sakuga, durées en f) ; ni années, ni heures, ni renvois (§10,
    RETOURS:83, v13), ni les numéros des titres. Normalisés sans signe ni
    zéro inutile (« −0,20 » -> « 0.2 ») : le signe s'écrit de trop de façons
    pour être comparé de manière fiable."""
    out = set()
    for ligne in texte.splitlines():
        if _TITRE.match(ligne):
            continue
        for m in _NOMBRE.finditer(ligne):
            n = m.group(2)
            try:
                v = float(n.replace(",", "."))
            except ValueError:
                continue
            if "." in n or "," in n:
                if v != 0:
                    out.add("%g" % v)
            elif 1900 <= v <= 2100:
                continue
            elif v >= 100 or (v >= 10 and _UNITE.match(_PLAGE.sub("", ligne[m.end():], count=1))):
                out.add(str(int(v)))
    return out


def expressions(texte):
    """Expressions entre « » (souvent les mots de Milan) de 2 à 10 mots."""
    out = set()
    for m in re.findall(r"«\s*([^»]{3,120}?)\s*»", texte):
        e = " ".join(re.findall(r"[a-z0-9']+", norm(m)))
        if 2 <= len(e.split()) <= 10:
            out.add(e)
    return out


# --------------------------------------------------------------------------
# Découpage des fichiers
# --------------------------------------------------------------------------

_TITRE = re.compile(r"^(#{1,6})\s+(.*\S)\s*$")
_ITEM = re.compile(r"^(\d+)[.)]\s+\S")
_CARNET_ID = re.compile(r"^\*\*(\d+b?\.\d+[a-z]?)\s")


def _id_titre(titre):
    """« 10. On règle… » -> « 10 » ; « 4 bis. Vu… » -> « 4 bis » ;
    « 7b. Les poids… » -> « 7b » ; sinon le titre court."""
    m = re.match(r"^(\d+[a-z]?(?:\s+(?:bis|ter|quater))?)[.)]?\s", titre)
    if m:
        return m.group(1)
    m = re.match(r"^([A-Z])\.\s", titre)
    if m:
        return m.group(1)
    t = re.sub(r"[*`]", "", titre)
    return t[:48] + ("…" if len(t) > 48 else "")


def lignes_hors_code(lignes):
    """Indices des lignes hors blocs ``` (un titre dans un bloc de code n'en
    est pas un)."""
    dedans = False
    out = []
    for i, l in enumerate(lignes):
        if l.lstrip().startswith("```"):
            dedans = not dedans
            continue
        if not dedans:
            out.append(i)
    return set(out)


def decouper_md(chemin, items=True, ids_carnet=False):
    """Découpe un .md en entrées. Chaque entrée : fichier, id, titre, debut,
    fin (lignes 1-indexées, fin incluse), texte. L'en-tête avant le premier
    titre de niveau >= 2 est l'entrée « en-tête »."""
    lignes = open(chemin, encoding="utf-8").read().splitlines()
    hors = lignes_hors_code(lignes)
    coupes = []   # (indice de ligne, id, titre, niveau)
    for i, l in enumerate(lignes):
        if i not in hors:
            continue
        m = _TITRE.match(l)
        if m:
            niv = len(m.group(1))
            if niv == 1:
                coupes.append((i, "en-tête", m.group(2), 1))
            else:
                coupes.append((i, _id_titre(m.group(2)), m.group(2), niv))
            continue
        if ids_carnet:
            m = _CARNET_ID.match(l)
            if m:
                titre = re.sub(r"\*\*", "", l)[:90]
                coupes.append((i, m.group(1), titre, 7))
    if not coupes or coupes[0][0] != 0:
        coupes.insert(0, (0, "en-tête", os.path.basename(chemin), 1))
    rel = os.path.relpath(chemin, BRAIN)
    entrees = []
    for k, (i, eid, titre, niv) in enumerate(coupes):
        j = coupes[k + 1][0] if k + 1 < len(coupes) else len(lignes)
        bloc = lignes[i:j]
        # items numérotés de premier niveau dans la section ?
        its = [n for n, l in enumerate(bloc) if (i + n) in hors and _ITEM.match(l)] if items else []
        if len(its) >= 2:
            prelude = bloc[:its[0]]
            if len("\n".join(prelude[1:]).strip()) >= 200:
                entrees.append(dict(fichier=rel, id=eid, titre=titre, debut=i + 1, fin=i + its[0],
                                    texte="\n".join(prelude)))
            for a, n in enumerate(its):
                m_ = its[a + 1] if a + 1 < len(its) else len(bloc)
                num = _ITEM.match(bloc[n]).group(1)
                txt = "\n".join(bloc[n:m_])
                t1 = re.sub(r"[*`]", "", bloc[n])[:70]
                entrees.append(dict(fichier=rel, id=f"{eid} item {num}", titre=t1, debut=i + n + 1,
                                    fin=i + m_, texte=txt, parent=eid))
        else:
            entrees.append(dict(fichier=rel, id=eid, titre=titre, debut=i + 1, fin=j, texte="\n".join(bloc)))
    return entrees


def decouper_py(chemin):
    """Une section pour la docstring/en-tête du module, puis une par `def` /
    `class` de premier niveau (commentaires et code compris)."""
    try:
        lignes = open(chemin, encoding="utf-8").read().splitlines()
    except (UnicodeDecodeError, OSError):
        return []
    coupes = [(0, "module")]
    for i, l in enumerate(lignes):
        m = re.match(r"^(?:def|class)\s+(\w+)", l)
        if m:
            coupes.append((i, m.group(1)))
    rel = os.path.relpath(chemin, BRAIN)
    out = []
    for k, (i, nom) in enumerate(coupes):
        j = coupes[k + 1][0] if k + 1 < len(coupes) else len(lignes)
        if j > i:
            out.append(dict(fichier=rel, id=nom, titre=nom, debut=i + 1, fin=j, texte="\n".join(lignes[i:j])))
    return out


# --------------------------------------------------------------------------
# Sources historiques et destinations
# --------------------------------------------------------------------------

def historiques():
    """Lit la liste d'ETAT.md §3 (ligne « Historique ») ; repli sur la liste
    connue si le format a changé."""
    etat = os.path.join(BRAIN, "ETAT.md")
    motifs = []
    try:
        txt = open(etat, encoding="utf-8").read()
        m = re.search(r"^\*\*Historique[^*]*\*\*(.*?)(?:\n\n|Ce qu'ils contiennent)", txt, re.S | re.M)
        if m:
            motifs = re.findall(r"`([^`]+\.md)`", m.group(1))
    except OSError:
        pass
    motifs = motifs or HISTORIQUES_DEFAUT
    out = []
    for mo in motifs:
        for p in sorted(glob.glob(os.path.join(BRAIN, mo))):
            if p not in out:
                out.append(p)
    return out


_ORIGINE = re.compile(r"^- Origine \(absorb[ée] de ")


def sans_origine(texte):
    """Retire les sous-points « Origine » écrits par `deplacer.py` (texte
    d'origine recopié mot pour mot, en citation « > »). Une copie n'est pas
    une digestion : si on la comptait, toute entrée déplacée rendrait sa
    cible « complète » pour elle ET pour ses voisines."""
    out, dedans = [], False
    for l in texte.splitlines():
        if _ORIGINE.match(l):
            dedans = True
            continue
        if dedans and (l.startswith("  >") or l == ""):
            if l == "":
                dedans = False
                out.append(l)
            continue
        dedans = False
        out.append(l)
    return "\n".join(out)


def destinations():
    """Sections des destinations, chacune avec son étage."""
    secs = []
    carnet = os.path.join(BRAIN, "corpus", "CARNET.md")
    if os.path.exists(carnet):
        for s in decouper_md(carnet, items=False, ids_carnet=True):
            s["etage"] = "vivant"
            s["texte"] = sans_origine(s["texte"])
            secs.append(s)
    for p in sorted(glob.glob(os.path.join(BRAIN, "corpus", "fiches", "*.md"))):
        if os.path.basename(p).startswith("_"):   # gabarit, pas du savoir
            continue
        for s in decouper_md(p, items=False):
            s["etage"] = "vivant"
            s["texte"] = sans_origine(s["texte"])
            secs.append(s)
    for p in sorted(glob.glob(os.path.join(BRAIN, "outils", "*.py")) + glob.glob(os.path.join(BRAIN, "*.py"))):
        b = os.path.basename(p)
        if b in ("archive_check.py", "deplacer.py", "revue.py", "__init__.py"):
            continue
        for s in decouper_py(p):
            s["etage"] = "en veille" if b in EN_VEILLE else "vivant"
            secs.append(s)
    for p in sorted(glob.glob(os.path.join(ROOT, "experiments", "r6_*", "scripts", "*.py"))):
        for s in decouper_py(p):
            s["etage"] = "production"
            secs.append(s)
    return secs


# --------------------------------------------------------------------------
# Recoupement
# --------------------------------------------------------------------------

class Index:
    """Index des sections de destination. La rareté d'un terme se mesure à
    part dans la prose (.md) et dans le code (.py) : « rule » est rare dans
    la prose et banal dans le code, « fente » l'inverse ; on garde le plus
    banal des deux pour ne pas prendre un mot courant pour une clé."""

    def __init__(self, secs):
        self.secs = secs
        self.df = {}
        self.df_md = {}
        self.df_py = {}
        self.dfn = {}
        self.par_terme = {}
        self.par_nombre = {}
        for k, s in enumerate(secs):
            s["_t"] = set(termes(s["texte"]))
            s["_n"] = nombres(s["texte"])
            s["_x"] = " ".join(re.findall(r"[a-z0-9']+", norm(s["texte"])))
            s["_py"] = s["fichier"].endswith(".py")
            dd = self.df_py if s["_py"] else self.df_md
            for t in s["_t"]:
                self.df[t] = self.df.get(t, 0) + 1
                dd[t] = dd.get(t, 0) + 1
                self.par_terme.setdefault(t, []).append(k)
            for n in s["_n"]:
                self.dfn[n] = self.dfn.get(n, 0) + 1
                self.par_nombre.setdefault(n, []).append(k)
        self.N = len(secs)
        self.N_py = sum(1 for s in secs if s["_py"]) or 1
        self.N_md = (self.N - self.N_py) or 1
        self.gabarit = set()

    def idf(self, t):
        return math.log((self.N + 1) / (self.df.get(t, 0) + 1)) + 1.0

    def idf_n(self, n):
        """Rareté d'un nombre : « 10 » ou « 0.5 » sont partout, « 0.32 » non."""
        return math.log((self.N + 1) / (self.dfn.get(n, 0) + 1)) + 0.1

    def banal(self, t):
        return max(self.df_md.get(t, 0) / self.N_md, self.df_py.get(t, 0) / self.N_py) > 0.10

    def apprendre_gabarit(self, entrees):
        """Les mots du gabarit d'un fichier historique (« - **Retour** : »,
        « **Cause** : », « **Règle** : » dans LECONS) reviennent dans presque
        toutes ses entrées : ce ne sont pas des clés. On prend les mots des
        étiquettes en gras suivies de « : » présentes dans >= 3 entrées, et
        les mots présents dans >= 75 % des entrées (au-delà, c'est le sujet
        du fichier entier, pas celui d'une entrée)."""
        n = len(entrees)
        if n < 4:
            return
        cpt, etiq = {}, {}
        for e in entrees:
            for t in set(termes(e["texte"])):
                cpt[t] = cpt.get(t, 0) + 1
            vus = set()
            for m in re.findall(r"^\s*(?:[-*]\s*)?\*\*([^*\n]{2,40})\*\*\s*:", e["texte"], re.M):
                vus |= set(termes(m))
            for t in vus:
                etiq[t] = etiq.get(t, 0) + 1
        self.gabarit |= {t for t, c in etiq.items() if c >= 3}
        self.gabarit |= {t for t, c in cpt.items() if c / n >= 0.75}

    def cles(self, texte, k=15):
        """Termes clés d'une entrée : les plus rares dans les destinations,
        pondérés par leur fréquence dans l'entrée. Un mot absent de toutes les
        destinations compte s'il revient au moins 2 fois dans l'entrée (un
        mot dit une seule fois et introuvable est souvent du bruit)."""
        tf = {}
        for t in termes(texte):
            tf[t] = tf.get(t, 0) + 1
        cand = []
        for t, f in tf.items():
            d = self.df.get(t, 0)
            if (d == 0 and f < 2) or t in self.gabarit or self.banal(t):
                continue
            cand.append((f * self.idf(t), t))
        cand.sort(reverse=True)
        return [t for _, t in cand[:k]]


def recouper(entree, index, k_top=3):
    txt = entree["texte"]
    cles = index.cles(txt)
    nbs = nombres(txt)
    exps = expressions(txt)
    poids = {t: index.idf(t) for t in cles}
    tot_p = sum(poids.values()) or 1.0
    pn = {n: index.idf_n(n) for n in nbs}
    tot_n = sum(pn.values()) or 1.0
    le = max(len(txt), 400)
    confiance = min(1.0, (len(cles) + len(nbs)) / 8.0)
    cand = set()
    for t in cles:
        cand.update(index.par_terme.get(t, []))
    for n in nbs:
        cand.update(index.par_nombre.get(n, []))
    res = []
    for c in cand:
        s = index.secs[c]
        if s["fichier"] == entree["fichier"]:
            continue
        ct = sum(poids[t] for t in cles if t in s["_t"]) / tot_p if cles else None
        cn = sum(pn[n] for n in nbs & s["_n"]) / tot_n if nbs else None
        cx = sum(1 for e in exps if e in s["_x"]) / len(exps) if exps else None
        parts = [(0.5, ct), (0.35, cn), (0.15, cx)]
        w = sum(a for a, v in parts if v is not None)
        score = sum(a * v for a, v in parts if v is not None) / w if w else 0.0
        # une très longue section contient beaucoup de mots par hasard :
        # léger malus au-delà de 3 fois la longueur de l'entrée
        score *= min(1.0, (3.0 * le / max(len(s["texte"]), 1)) ** 0.3)
        # peu d'indices (3 mots, 1 nombre) = recoupement fragile : on tempère
        score *= 0.5 + 0.5 * confiance
        res.append(dict(section=c, score=round(score, 3), termes=round(ct, 2) if ct is not None else None,
                        nombres=round(cn, 2) if cn is not None else None,
                        expressions=round(cx, 2) if cx is not None else None))
    res.sort(key=lambda r: -r["score"])
    return cles, nbs, exps, res


def _lien(s):
    return f"{s['fichier']}:{s['debut']} {s['id']}"


def verdict(entree, index):
    """Retourne le dict de résultat d'une entrée."""
    txt = entree["texte"]
    tl = txt.splitlines()
    corps = "\n".join(tl[1:] if tl and _TITRE.match(tl[0]) else tl).strip()
    base = dict(fichier=entree["fichier"], id=entree["id"], titre=entree["titre"], ligne=entree["debut"])
    if MARQUE_ABSORBE.search(txt):
        cible = re.search(r"absorb[ée]+\s+dans\s+`?([\w/.\-]+\.(?:md|py))`?(?:\s+§([\w.]+[\w]))?", txt)
        existe, sect_ok = None, None
        if cible:
            p = cible.group(1)
            vus = [os.path.join(b, p) for b in (BRAIN, os.path.join(BRAIN, "corpus"), ROOT)
                   if os.path.exists(os.path.join(b, p))]
            existe = bool(vus)
            if vus and cible.group(2) and p.endswith(".md"):
                ids = {e["id"] for e in decouper_md(vus[0], items=False, ids_carnet=True)}
                sect_ok = cible.group(2) in ids
        base.update(statut="absorbé", cible=cible.group(1) if cible else None, cible_existe=existe,
                    section=cible.group(2) if cible else None, section_existe=sect_ok)
        return base
    if MARQUE_ABANDON.search(txt):
        base.update(statut="abandonnée", raison=MARQUE_ABANDON.split(txt, 1)[1].strip().splitlines()[0][:160])
        return base
    if len(corps) < 60 or "**HISTORIQUE" in txt[:400]:
        base.update(statut="vide" if len(corps) < 60 else "bandeau")
        return base
    cles, nbs, exps, res = recouper(entree, index)
    viv = [r for r in res if index.secs[r["section"]]["etage"] == "vivant"]
    autres = [r for r in res if index.secs[r["section"]]["etage"] != "vivant"]
    meil = viv[0] if viv else None
    # couverture cumulée des 3 meilleures sections vivantes (une leçon peut
    # avoir été répartie en plusieurs endroits)
    top = [index.secs[r["section"]] for r in viv[:3]]
    tt = set().union(*[s["_t"] for s in top]) if top else set()
    nn = set().union(*[s["_n"] for s in top]) if top else set()
    manque_t = [t for t in cles if t not in tt]
    manque_n = sorted(nbs - nn, key=lambda x: float(x))
    cum_t = 1 - len(manque_t) / len(cles) if cles else None
    cum_n = 1 - len(manque_n) / len(nbs) if nbs else None
    sc = meil["score"] if meil else 0.0
    nb_ok = meil is None or meil["nombres"] is None or meil["nombres"] >= 0.5
    if meil and sc >= 0.55 and nb_ok:
        st = "complète"
    elif meil and (sc >= 0.3 or ((cum_t or 0) >= 0.6 and (cum_n is None or cum_n >= 0.5))):
        st = "partielle"
    else:
        st = "AUCUNE"

    def fmt(r):
        s = index.secs[r["section"]]
        return dict(ou=_lien(s), etage=s["etage"], score=r["score"], termes=r["termes"],
                    nombres=r["nombres"], expressions=r["expressions"])
    base.update(statut=st, score=sc,
                meilleure_vivante=fmt(meil) if meil else None,
                autres_vivantes=[fmt(r) for r in viv[1:3]],
                hors_vivant=[fmt(r) for r in autres[:2] if r["score"] > sc],
                cles=cles, nombres=sorted(nbs, key=float), expressions=sorted(exps),
                cumul_3_vivantes=dict(termes=round(cum_t, 2) if cum_t is not None else None,
                                      nombres=round(cum_n, 2) if cum_n is not None else None),
                manque_termes=manque_t, manque_nombres=manque_n)
    return base


def analyser(chemins=None, entree=None):
    index = Index(destinations())
    out = []
    for p in chemins or historiques():
        es = decouper_md(p)
        index.apprendre_gabarit(es)
        for e in es:
            if entree and not (e["id"] == entree or e["id"].startswith(entree + " ")
                               or entree.lower() in e["titre"].lower()):
                continue
            out.append(verdict(e, index))
    return out, index


# --------------------------------------------------------------------------
# Sorties
# --------------------------------------------------------------------------

def ligne_texte(r):
    tete = f"{r['fichier']} §{r['id']} (l.{r['ligne']}) « {r['titre'][:60]} »"
    st = r["statut"]
    if st in ("vide", "bandeau"):
        return f"{tete} -> ({'moins de 60 caractères' if st == 'vide' else st}, non cherché)"
    if st == "absorbé":
        ok = {True: "cible présente", False: "CIBLE INTROUVABLE", None: "cible non lue"}[r["cible_existe"]]
        if r.get("section"):
            ok += {True: ", section présente", False: ", SECTION INTROUVABLE", None: ""}[r.get("section_existe")]
            return f"{tete} -> déjà absorbé dans {r['cible']} §{r['section']} ({ok})"
        return f"{tete} -> déjà absorbé dans {r['cible']} ({ok})"
    if st == "abandonnée":
        return f"{tete} -> abandonnée : {r['raison']}"
    m = r["meilleure_vivante"]
    s = []
    if st == "AUCUNE":
        s.append(f"{tete} -> AUCUNE destination vivante" + (f" (meilleure : {m['ou']} {m['score']})" if m else ""))
    else:
        s.append(f"{tete} -> {m['ou']} ({m['score']}, {st})")
    for h in r.get("hors_vivant", []):
        s.append(f"      plus proche hors vivant : {h['ou']} ({h['score']}, {h['etage']})")
    if r["manque_nombres"]:
        s.append(f"      nombres absents des 3 meilleures vivantes : {', '.join(r['manque_nombres'][:12])}")
    if r["manque_termes"] and st != "complète":
        s.append(f"      termes clés absents : {', '.join(r['manque_termes'][:10])}")
    return "\n".join(s)


def resume(res):
    par = {}
    for r in res:
        d = par.setdefault(r["fichier"], {})
        d[r["statut"]] = d.get(r["statut"], 0) + 1
    return par


def ecrire_md(res, chemin, focus=("LECONS.md", ("10", "11"))):
    ordre = ["complète", "partielle", "AUCUNE", "absorbé", "abandonnée", "vide", "bandeau"]
    L = [f"# archive_check du {date.today().isoformat()} : destinations vivantes des entrées HISTORIQUE",
         "",
         "Rapport produit par `python3 outils/archive_check.py` (brique A2 du",
         "plan `PLAN_REORGANISATION_2026-09-26.md`). **Rien n'a été modifié.** C'est",
         "une aide à la relecture, pas un verdict : un score recoupe des mots et des",
         "nombres, il ne dit pas si une leçon a été comprise.",
         "",
         "Lecture : « complète » = une section vivante reprend l'essentiel des termes",
         "rares et au moins la moitié des nombres (score >= 0,55) ; « partielle » =",
         "une partie seulement (score >= 0,3, ou 3 sections vivantes réunies >= 60 %",
         "des termes) ; « AUCUNE » = rien de vivant ne la reprend. « Hors vivant » =",
         "code en veille (rules / etats / critic / audit) ou code d'une production",
         "passée : écrit, mais plus relu.",
         ""]
    fic, ids = focus
    cas = [r for r in res if r["fichier"] == fic and (r["id"] in ids)]
    if cas:
        L += ["## Premier cas test : LECONS §10-11 (« vers le bas », « à plat »)", ""]
        for r in cas:
            L += ["```", ligne_texte(r), "```", ""]
        L += ["Attendu (cause de la rechute d'« Un seul coup » v1) : pas de destination",
              "vivante complète. Les nombres listés « absents » sont ce qui serait perdu",
              "si l'on ne gardait que les destinations vivantes.", ""]
    tot = {}
    for r in res:
        tot[r["statut"]] = tot.get(r["statut"], 0) + 1
    L += ["## Totaux", "",
          f"{len(res)} entrées : " + ", ".join(f"{o} {tot.get(o, 0)}" for o in ordre) + ".", "",
          "ETAT.md §3 dit des fichiers HISTORIQUE : « Ce qu'ils contiennent de vivant",
          "est passé dans CARNET.md et les fiches. » Ce recoupement ne le confirme que",
          "pour une minorité d'entrées. Ce n'est pas une liste de choses à recopier :",
          "beaucoup d'entrées « AUCUNE » sont datées ou abandonnées à juste titre (on",
          "l'écrit alors « abandonnée : raison » dans l'entrée). C'est la liste de ce",
          "qu'il faut RELIRE avant d'écrire une pierre tombale (`outils/deplacer.py`).",
          "",
          "Limites : recoupement lexical (racines de 6 lettres, nombres sans signe) ;",
          "une leçon reformulée en d'autres mots sort « partielle » ou « AUCUNE » ;",
          "un nombre banal (10, 0,5) peut se retrouver par hasard ; les tableaux sont",
          "lus comme du texte ; le code est découpé par fonction de premier niveau.",
          ""]
    L += ["## Résumé par fichier", "", "| fichier | " + " | ".join(ordre) + " |",
          "|---|" + "---|" * len(ordre)]
    for f, d in resume(res).items():
        L.append(f"| `{f}` | " + " | ".join(str(d.get(o, 0)) for o in ordre) + " |")
    L.append("")
    for f in dict.fromkeys(r["fichier"] for r in res):
        L += [f"## `{f}`", "", "```"]
        for r in res:
            if r["fichier"] == f:
                L.append(ligne_texte(r))
        L += ["```", ""]
    open(chemin, "w", encoding="utf-8").write("\n".join(L))


def main(argv):
    args = list(argv)

    def opt(nom):
        if nom in args:
            k = args.index(nom)
            v = args[k + 1]
            del args[k:k + 2]
            return v
        return None
    fic = opt("--fichier")
    ent = opt("--entree")
    js = opt("--json")
    md = opt("--md")
    seuls = "--seuls-manques" in args
    cer = opt("--cerveau")
    if cer:
        regler_cerveau(cer)
    chemins = None
    if fic:
        p = fic if os.path.isabs(fic) else os.path.join(BRAIN, fic)
        if not os.path.exists(p):
            p = os.path.join(os.getcwd(), fic)
        chemins = [p]
    res, index = analyser(chemins, ent)
    print(f"ARCHIVE_CHECK -- {len(res)} entrées, {index.N} sections de destination "
          f"(vivant / en veille / production). Rien n'est modifié.\n")
    for r in res:
        if seuls and r["statut"] in ("complète", "vide", "bandeau", "absorbé", "abandonnée"):
            continue
        print(ligne_texte(r))
    print("\nRésumé :")
    for f, d in resume(res).items():
        print(f"  {f} : " + ", ".join(f"{k} {v}" for k, v in d.items()))
    if js:
        json.dump(dict(date=date.today().isoformat(), entrees=res), open(js, "w", encoding="utf-8"),
                  ensure_ascii=False, indent=1)
        print(f"\nJSON : {js}")
    if md:
        ecrire_md(res, md)
        print(f"Rapport : {md}")


if __name__ == "__main__":
    main(sys.argv[1:])
