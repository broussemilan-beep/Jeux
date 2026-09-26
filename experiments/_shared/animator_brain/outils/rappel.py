"""
RAPPEL : ce que le cerveau sait déjà sur un concept, AVANT de travailler.

Retour de Milan (2026-09-25) : « poing chargé puissant » devait faire écho au
Serious Punch de Saitama (le GIF et l'anime TSB). La mémoire existait dans
les fichiers, mais rien ne la rappelait.

Réparé le 2026-09-26 (plan de réorganisation, brique A4 ; repli inspiré de
Hermes Agent, `hermes_state_search.py:1129`). L'ancienne version sortait
12,5 k caractères de prose sans un nombre ni un statut, ignorait les mots de
moins de 5 lettres (« bas », « bras », « dos »), rangeait « vers le bas »
dans l'aérien et resservait en premier des lectures démenties par Milan.
Ce qu'il fait maintenant :
- mots de 3 lettres et plus (hors mots-outils), cherchés par leur RACINE
  (« frappe » trouve « frappait ») ; familles de synonymes (CONCEPTS) :
  « vers le bas » -> contact, hauteur du poing ; « poing chargé » -> charge,
  armé, coup chargé ;
- repli en trois temps, section par section : ET (tous les mots) -> racines
  et trigrammes (« juste » ~ « buste » : Milan dicte, les mots arrivent
  déformés) -> OU (au moins un mot). Chaque ligne dit comment elle a été
  trouvée : [ET], [~], [OU] ;
- en tête, un INDEX court : id de l'entrée, statut (mesuré, lu, essayé,
  retour de Milan, CONTREDIT, HISTORIQUE), nombres, fichier:ligne ;
- puis la fiche du moment (la meilleure, en entier jusqu'à 3 000
  caractères ; la fiche active du NOYAU compte un peu plus) ;
- puis les motifs (`corpus/motifs.json`), les mots EXACTS de Milan datés
  (`corpus/milan_verbatim.jsonl` ; un message cité par une entrée trouvée
  remonte), les mesures (`corpus/poses/sources/*.json` avec les verdicts des
  vérificateurs, `corpus/clips/*.json`, `perception_*.json`,
  `hypotheses.json`, `notes_milan.jsonl`), le catalogue des refs, les outils
  de TOUT le dépôt, et le reste en fichier:ligne ;
- les fichiers marqués HISTORIQUE sont rétrogradés, jamais exclus ;
- les lignes marquées CONTREDIT (ou barrées, ou réfutées par un
  vérificateur) sortent EN DERNIER, avec leur marque ;
- 0 résultat -> « aucun résultat ≠ aucun savoir », et ce qui a été fouillé.
Ce n'est pas un moteur sémantique : il faut lire ce qu'il sort. Rien ici
n'est un verdict : chaque ligne dit d'où elle vient. Quand un concept
manque, on l'ajoute dans CONCEPTS. Cas connus rejoués :
`python3 tests/rappel_selftest.py`.

Usage : python3 outils/rappel.py "poing chargé" [--max 20] [--court]
        [--exclure fichier1,fichier2] [--autour fichier:ligne]
"""
import json
import math
import os
import re
import subprocess
import sys
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
BRAIN = os.path.normpath(os.path.join(HERE, ".."))
ROOT = os.path.normpath(os.path.join(BRAIN, "..", "..", ".."))   # racine du dépôt
CORPUS = os.path.join(BRAIN, "corpus")
FICHES = os.path.join(CORPUS, "fiches")
CATALOGUE = os.path.join(CORPUS, "CATALOGUE_REFS.md")

# Familles de synonymes. Une famille s'applique quand une de ses expressions
# est dans la requête ; ses termes élargissent alors les mots couverts.
CONCEPTS = {
    "coup charge": ["coup charge", "coup chargé", "poing charge", "poing chargé", "poing charge puissant",
                    "serious punch", "serious", "saitama", "obari", "one punch", "opm", "deku",
                    "poing vers la camera", "poing vers le lecteur", "poing geant", "charge", "charger",
                    "armé", "arme", "armer", "armé tenu", "arme tenu", "tenue de la charge", "stoic bomb",
                    "coup final", "ultime"],
    "contact": ["vers le bas", "frappe vers le bas", "part du bas", "pars du bas", "d'en bas", "du bas",
                "de en bas", "hauteur du poing", "poing au contact", "au contact", "hauteur du coup",
                "hauteur de poitrine", "bascule du buste", "penche_avant", "poing_y_contact", "coup à plat",
                "coup a plat", "arrivee du coup", "arrivée du coup"],
    "buste": ["buste", "bust", "torse", "lacet", "buste qui tourne", "tourne son buste", "tournant son bust",
              "rotation du buste", "torsion", "epaule", "épaule"],
    "corps bras": ["que les bras", "anime que les bras", "animé que les bras", "corps_bras", "le corps porte",
                   "corps d'abord", "torse fige", "torse figé"],
    "changement": ["aucun changement", "pas de changement", "pas trop de dif", "pas de gros changement",
                   "ecart n-1", "écart", "avant/après", "avant apres"],
    "jambes": ["jambes", "jambe", "appuis", "appui", "pieds", "fente", "genoux", "hanche"],
    "rafale": ["rafale", "m1", "gatling", "jab", "direct", "crochet", "combo", "cross punch", "punch practice"],
    "impact": ["impact", "carte", "cartes", "hitstop", "gel", "blanc", "noir", "silhouette inversee", "flash",
               "skip the point of contact", "babbitt", "ken harris"],
    "camera": ["camera", "caméra", "cadrage", "gros plan", "plan large", "secousse", "shake", "contre-plongee",
               "camera de jeu", "cinema", "cinématique", "trauma"],
    "timing": ["timing", "tenue", "tenu", "contraste", "slow against the fast", "lent", "rapide", "ease",
               "amorti", "linear", "cles eparses", "clés éparses", "espacement", "interpolation"],
    "pose": ["pose", "silhouette", "torsion", "lacet", "bascule", "bras libre", "armé", "fente", "ligne",
             "exager", "exagér", "pousser", "geo_pose"],
    "aerien": ["aerien", "aérien", "en l'air", "plongee", "plongée", "suspendu", "saut"],
    "vfx": ["vfx", "effet", "effets", "particule", "particleemitter", "beam", "trail", "trainee", "traînée",
            "aura", "etincelle", "étincelle", "onde", "fumee", "fumée", "debris", "débris", "smear", "halo",
            "cratere", "cratère", "flipbook", "shader", "texture"],
    "son": ["son", "sons", "sfx", "audio", "bruitage", "sound", "grondement", "souffle", "vide avant",
            "silence", "ecoute", "écoute", "spectrogramme"],
    "duree": ["duree", "durée", "temps reel", "temps réel", "à l'écran", "a l'ecran", "couverture", "tenue",
              "signature", "planche d'images fixes", "effet_max", "durees.py"],
    "jugement_vfx": ["qualité vfx", "qualite vfx", "biais", "prediction", "prédiction", "compter les couches",
                     "surestime", "note vfx", "auto-évaluation", "auto-evaluation", "juge", "porte", "plein ecran",
                     "plein écran", "consequence", "conséquence", "juge.py"],
    "dragon": ["dragon", "aura dragon", "goku", "ssj3", "shenron", "izuku", "deku", "one for all", "full cowl",
               "eclair vert", "éclair vert", "tourbillon de feu", "suiryu", "dragon's descent", "tete de dragon",
               "tête de dragon", "violet", "last breath", "morsure", "mange", "gueule", "machoire", "mâchoire",
               "invocation", "dragon d'or"],
    "victime": ["victime", "reaction", "réaction", "recul", "encaisse"],
    "studio": ["roblox studio", "plugin", "mcp", "stock vfx", "stocks de vfx", "tuto de a a z", "frein",
               "capture_screenshot", "moon animator", "vfx forge", "creator store"],
    "allure": ["allure", "allure.py", "vitesse du dragon", "dans tous les sens", "trop rapide", "virage",
               "majestueux", "rythme", "enchainement", "enchaînement", "serpent", "corps par seconde"],
}

MOTS_OUTILS = set("""les des une que qui quoi dont dans sur pour avec par son ses sa leur leurs aux au du de la le
un et ou est sont pas plus moins vers the and comme mais tout tous toute cette ces cet nous vous elle ils elles lui
etre avoir fait faire tres bien encore aussi donc car quand sous chez tjrs toujours peu trop ca cela ceci celui
celle qu il on se ne en y a""".split())

W_SYN = 0.6      # un mot trouvé par un synonyme de sa famille compte moins que le mot lui-même
W_FLOU = 0.5     # un mot trouvé par trigrammes (forme déformée)
NUM_RE = re.compile(r"[-−+]?\d+(?:[,.]\d+)?\s?(?:°|studs?\b|i/s|%|ms\b|s\b|f\b|images?\b|px\b|/10\b)")
SHA_RE = re.compile(r"\b[0-9a-f]{16}\b")
MARQUE_RE = re.compile(r"\[\s*(?:lecture\s+)?contredit|~~")   # une MARQUE posée, pas un texte qui en parle


# ------------------------------------------------------------ texte
def norm(s):
    s = unicodedata.normalize("NFD", str(s).lower().replace("’", "'").replace("−", "-"))
    return "".join(c for c in s if unicodedata.category(c) != "Mn")


def mots(s):
    return [w for w in re.findall(r"[a-z0-9_]+", norm(s)) if len(w) >= 3]


def racine(w):
    for suf in ("ements", "ement", "ations", "ation", "aient", "ait", "ant", "ees", "ee", "es", "er", "ez",
                "e", "s"):
        if w.endswith(suf) and len(w) - len(suf) >= 4:
            return w[:-len(suf)]
    return w


def motif_mot(w):
    if len(w) <= 4:
        return r"(?<![a-z0-9])" + re.escape(w) + r"s?(?![a-z0-9])"
    return r"(?<![a-z0-9])" + re.escape(racine(w))


def trigrammes(w):
    return {w[i:i + 3] for i in range(len(w) - 2)}


# ------------------------------------------------------------ requête
class Groupe:
    """Un mot de la requête : sa racine (poids 1), les termes de sa famille
    (poids W_SYN), une ressemblance par trigrammes (poids W_FLOU)."""

    def __init__(self, mot):
        self.mot = mot
        self.re_mot = re.compile(motif_mot(mot))
        self.syn = []
        self.re_syn = None
        self.tri = trigrammes(mot) if len(mot) >= 4 else None
        self._flou = {}

    def ajouter_famille(self, termes):
        for t in termes:
            t = norm(t)
            if t and t not in self.syn and t != self.mot:
                self.syn.append(t)
        if self.syn:
            self.re_syn = re.compile("|".join(r"(?<![a-z0-9])" + re.escape(t) for t in
                                              sorted(self.syn, key=len, reverse=True)))

    def exact(self, nt):
        if self.re_mot.search(nt):
            return 1.0
        if self.re_syn is not None and self.re_syn.search(nt):
            return W_SYN
        return 0.0

    def flou(self, jetons):
        if self.tri is None:
            return 0.0
        for j in jetons:
            r = self._flou.get(j)
            if r is None:
                r = False
                if abs(len(j) - len(self.mot)) <= 3 and len(j) >= 4:
                    tj = trigrammes(j)
                    r = len(tj & self.tri) / len(tj | self.tri) >= 0.5
                self._flou[j] = r
            if r:
                return W_FLOU
        return 0.0


class Requete:
    def __init__(self, req):
        self.brute = req
        self.phrase = " ".join(re.findall(r"[a-z0-9_']+", norm(req)))
        tous = mots(req)
        contenu = [w for w in tous if w not in MOTS_OUTILS] or tous
        vus, self.groupes = set(), []
        for w in contenu:
            if w not in vus:
                vus.add(w)
                self.groupes.append(Groupe(w))
        self.familles = []
        for nom, termes in CONCEPTS.items():
            fam = [norm(t) for t in termes]
            couverts = set()
            for t in fam:
                for m in re.finditer(r"(?<![a-z0-9])" + re.escape(t) + r"(?![a-z0-9])", self.phrase):
                    couverts |= set(mots(m.group(0)))
            if couverts:
                self.familles.append(nom)
                for g in self.groupes:
                    if g.mot in couverts:
                        g.ajouter_famille(fam)

    def noter(self, nt, jetons=None):
        """-> (niveau, score) ou None. niveau : ET | ~ | OU."""
        if not self.groupes:
            return None
        vals, flous = [], 0
        for g in self.groupes:
            v = g.exact(nt)
            if not v:
                if jetons is None:
                    jetons = set(re.findall(r"[a-z0-9_]+", nt))
                v = g.flou(jetons)
                flous += bool(v)
            vals.append(v)
        k = sum(1 for v in vals if v)
        if not k:
            return None
        s = sum(vals) / len(vals)
        if len(self.phrase) > 3 and self.phrase in nt:
            s += 1.0
        s *= 1.0 + 0.25 * min(1.0, 100.0 / max(1, len(nt)))   # un passage court et dense est plus précis
        if k == len(vals):
            return ("~" if flous else "ET"), s
        return "OU", s * 0.35 * k / len(vals)


# ------------------------------------------------------------ sources
def lire(p):
    try:
        return open(p, encoding="utf-8").read()
    except (OSError, UnicodeDecodeError):
        return ""


def rel(p):
    return os.path.relpath(p, ROOT)


def rel_b(p):
    return os.path.relpath(p, BRAIN)


def fichiers_md(exclus):
    out = []
    for dp, dn, fs in os.walk(BRAIN):
        dn[:] = sorted(d for d in dn if d not in ("__pycache__", "data", "scraper"))
        for f in sorted(fs):
            if f.endswith(".md"):
                out.append(os.path.join(dp, f))
    exp = os.path.join(ROOT, "experiments")
    for prod in sorted(os.listdir(exp)):
        d = os.path.join(exp, prod)
        if prod.startswith("_") or not os.path.isdir(d):
            continue
        for f in sorted(os.listdir(d)):
            if f == "README.md" or (f.startswith("FICHE") and f.endswith(".md")):
                out.append(os.path.join(d, f))
    return [p for p in out if not any(e and e in p for e in exclus)]


def historique(lignes):
    return any("**HISTORIQUE" in l for l in lignes[:15])


def poids_fichier(p, hist):
    b = rel_b(p)
    w = 1.0
    if b == "corpus/CARNET.md":
        w = 1.3
    elif b.startswith("corpus/fiches/"):
        w = 1.2
    elif b in ("NOYAU.md", "ETAT.md", "RETOURS.md"):
        w = 1.1
    elif b.startswith("corpus/recherche/"):
        w = 0.5   # plans, audits, rapports : ils citent tout, ils ne sont pas la source
    elif not p.startswith(BRAIN):
        w = 0.8
    return w * (0.35 if hist else 1.0)


class Unite:
    __slots__ = ("src", "ligne", "texte", "nt", "entree", "marque", "genre", "extra", "niveau", "score", "brut")

    def __init__(self, src, ligne, texte, entree=None, genre="md", marque=None, extra=None):
        self.src, self.ligne, self.texte = src, ligne, texte
        self.nt = norm(texte)
        self.entree, self.genre, self.marque, self.extra = entree, genre, marque, extra or {}
        self.niveau, self.score, self.brut = None, 0.0, 0.0


class Entree:
    def __init__(self, src, ligne, eid, titre, genre="md", statut_fixe=None):
        self.src, self.ligne, self.id, self.titre = src, ligne, eid, titre
        self.genre, self.statut_fixe = genre, statut_fixe
        self.unites, self.score, self.hist, self.contenu = [], 0.0, False, 0.0


def decouper_md(p):
    """Unités = paragraphes, puces (avec leurs lignes de suite), lignes de
    tableau. Entrées = titres ; dans le CARNET, les « **N.N » ; dans
    RETOURS, les puces datées « - **2026-… »."""
    lignes = lire(p).splitlines()
    base = os.path.basename(p)
    hist = historique(lignes)
    court = base[:-3]
    entrees, unites = [], []
    ent = Entree(p, 1, court, court)
    ent.hist = hist
    entrees.append(ent)
    cur = None

    def fermer():
        nonlocal cur
        if cur:
            num, txt = cur
            u = Unite(p, num, "\n".join(txt), ent)
            if MARQUE_RE.search(u.nt):
                u.marque = marque_de(u.texte)
            unites.append(u)
            ent.unites.append(u)
        cur = None

    for i, raw in enumerate(lignes, 1):
        s = raw.strip()
        h = re.match(r"^(#{1,4})\s+(.*)", raw)
        c = base == "CARNET.md" and re.match(r"^\*\*(\d+b?\.\d+[a-z]?)\s+(.*)", raw)
        r_ = base == "RETOURS.md" and re.match(r"^- \*\*(\d{4}-\d\d-\d\d[^*]*)\*\*", raw)
        if h or c or r_:
            fermer()
            if h:
                titre = h.group(2).strip()
                sec = re.match(r"^(\d+[a-z]?(?:\s?(?:bis|ter|quater))?)\.", titre)
                eid = f"{court} §{sec.group(1)}" if sec else f"{court}:{i}"
            elif c:
                titre = c.group(2)
                eid = f"{court} {c.group(1)}"
            else:
                titre = r_.group(1)
                eid = f"{court}:{i}"
            ent = Entree(p, i, eid, titre.strip("* "))
            ent.hist = hist
            entrees.append(ent)
            cur = (i, [raw])
            continue
        if not s:
            fermer()
        elif re.match(r"^\s*([-*+]|\d+[.)])\s", raw) or s.startswith("|") or s.startswith(">"):
            fermer()
            cur = (i, [raw])
        elif cur:
            cur[1].append(raw)
        else:
            cur = (i, [raw])
    fermer()
    for e in entrees:
        if e.genre == "md" and e.unites and (base == "CARNET.md"):
            t = e.unites[0].texte
            m = re.match(r"^\*\*\S+\s+(.*?)\*\*", t.replace("\n", " "))
            if m:
                e.titre = m.group(1)
    return entrees, unites, hist


def marque_de(texte):
    m = re.search(r"\[[^\]]*(?:CONTREDIT|contredit)[^\]]*\]", texte)
    if m:
        return m.group(0)[:110]
    m = re.search(r"~~([^~]+)~~", texte)
    if m:
        return f"~~{m.group(1)[:60]}~~ (barré)"
    return "CONTREDIT"


def aplatir(x, chemin=""):
    """JSON -> [(chemin, texte)] : feuilles texte, listes de nombres en une ligne."""
    out = []
    if isinstance(x, dict):
        for k, v in x.items():
            out += aplatir(v, f"{chemin}.{k}" if chemin else str(k))
    elif isinstance(x, list):
        if x and all(not isinstance(v, (dict, list)) for v in x) and sum(len(str(v)) for v in x) < 160:
            out.append((chemin, json.dumps(x, ensure_ascii=False)))
        else:
            for i, v in enumerate(x):
                out += aplatir(v, f"{chemin}[{i}]")
    elif isinstance(x, str):
        if x.lstrip().startswith(("{", "[")):
            try:
                return aplatir(json.loads(x), chemin)
            except json.JSONDecodeError:
                pass
        for j, par in enumerate(p for p in re.split(r"\n\s*\n", x) if p.strip()):
            out.append((chemin + (f"~{j}" if j else ""), par.strip()))
    elif x is not None:
        out.append((chemin, str(x)))
    return out


def texte_chemin(chemin, texte):
    """Le nom de la clé compte dans la recherche (« penche_avant_contact_deg »)."""
    dernier = re.sub(r"\[\d+\]|~\d+", "", chemin).split(".")[-1] if chemin else ""
    if re.fullmatch(r"[-\d., \[\]e+]+", texte.strip()) or len(texte) < 40:
        return f"{dernier} = {texte}"
    return texte


def sources_json(exclus):
    """Entrées + unités des JSON : poses mesurées (avec vérifications),
    clips, perception, hypothèses."""
    entrees, unites = [], []
    lot = []
    d = os.path.join(CORPUS, "poses", "sources")
    if os.path.isdir(d):
        lot += [(os.path.join(d, f), "pose") for f in sorted(os.listdir(d)) if f.endswith(".json")]
    d = os.path.join(CORPUS, "clips")
    if os.path.isdir(d):
        lot += [(os.path.join(d, f), "clip") for f in sorted(os.listdir(d)) if f.endswith(".json")]
    lot += [(os.path.join(CORPUS, f), "perception") for f in sorted(os.listdir(CORPUS))
            if f.startswith("perception_") and f.endswith(".json")]
    lot.append((os.path.join(BRAIN, "hypotheses.json"), "hypothese"))
    for p, genre in lot:
        if any(e and e in p for e in exclus):
            continue
        try:
            data = json.load(open(p, encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        nom = os.path.basename(p)[:-5]
        if genre == "pose":
            st = ("mesuré (exact R6)" if nom.startswith("pro_") else
                  "mesuré (reconstruit, vérifié par contradicteur)" if nom.startswith("recon_") else
                  "mesuré (notre export)" if nom.startswith("nous_") else "mesuré")
            verdicts = [v.get("verdict") for v in data.get("verifications", []) if isinstance(v, dict)]
            if verdicts:
                st += " ; vérifs : " + ", ".join(str(v) for v in verdicts)
            e = Entree(p, 0, f"poses/{nom}", data.get("label", nom), "json", st)
            for ch, t in aplatir(data.get("resultat"), "resultat"):
                u = Unite(p, 0, texte_chemin(ch, t), e, "json", extra={"chemin": ch})
                e.unites.append(u)
            for i, v in enumerate(data.get("verifications", [])):
                if not isinstance(v, dict):
                    continue
                for j, a in enumerate(v.get("affirmations", []) or []):
                    if not isinstance(a, dict):
                        continue
                    stat = str(a.get("statut", "?"))
                    t = f"{a.get('affirmation', '')} — vérif « {stat} » : {a.get('preuve', '')}"
                    u = Unite(p, 0, t, e, "json", extra={"chemin": f"verifications[{i}].affirmations[{j}]",
                                                          "verif": stat})
                    if stat.startswith("refut"):
                        u.marque = "RÉFUTÉ par le vérificateur"
                    e.unites.append(u)
                for ch, t in aplatir(v.get("corrections"), f"verifications[{i}].corrections"):
                    e.unites.append(Unite(p, 0, t, e, "json", extra={"chemin": ch, "verif": "correction"}))
        else:
            st = {"clip": "mesuré (clip_analyzer / durees)", "perception": "mesuré (perception.py)",
                  "hypothese": "hypothèses (pistes, pas des règles)"}[genre]
            e = Entree(p, 0, f"{genre}s/{nom}" if genre == "clip" else nom, nom, "json", st)
            for ch, t in aplatir(data):
                e.unites.append(Unite(p, 0, texte_chemin(ch, t), e, "json", extra={"chemin": ch}))
        entrees.append(e)
        unites += e.unites
    # notes de Milan (une ligne = une version notée)
    p = os.path.join(BRAIN, "notes_milan.jsonl")
    e = Entree(p, 0, "notes_milan", "notes de Milan par version", "json", "retour de Milan (notes)")
    for i, l in enumerate(lire(p).splitlines(), 1):
        try:
            n = json.loads(l)
        except json.JSONDecodeError:
            continue
        tete = f"{n.get('production')} {n.get('version')} ({n.get('date')}) note {n.get('note_milan')}"
        for ch, t in aplatir({k: v for k, v in n.items() if k not in ("etat", "parties_visuelles")}):
            if ch in ("production", "version", "date", "note_milan"):
                continue
            e.unites.append(Unite(p, i, f"{tete} — {ch} : {t}", e, "json", extra={"chemin": ch}))
    entrees.append(e)
    unites += e.unites
    return entrees, unites


def verbatim():
    out = []
    p = os.path.join(CORPUS, "milan_verbatim.jsonl")
    for i, l in enumerate(lire(p).splitlines(), 1):
        try:
            m = json.loads(l)
        except json.JSONDecodeError:
            continue
        t = m.get("texte") or m.get("debut") or ""
        out.append(Unite(p, i, t, None, "milan", extra=m))
    return out


def motifs_json():
    try:
        d = json.load(open(os.path.join(CORPUS, "motifs.json"), encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    items = d.get("motifs", []) if isinstance(d, dict) else d
    return [m for m in items if isinstance(m, dict)]


def outils_depot():
    try:
        fs = subprocess.run(["git", "-C", ROOT, "ls-files", "*.py"], capture_output=True, text=True,
                            timeout=10).stdout.split()
    except (OSError, subprocess.SubprocessError):
        fs = []
    fs = set(fs) | {rel(os.path.join(HERE, f)) for f in os.listdir(HERE) if f.endswith(".py")}
    return sorted(fs)


def doc_py(p):
    t = lire(os.path.join(ROOT, p))[:1800]
    m = re.search(r'^\s*(?:#[^\n]*\n)*\s*(?:"""|\'\'\')(.*?)(?:"""|\'\'\')', t, re.S)
    if m:
        return m.group(1).strip()
    # sans docstring : seulement les commentaires de tête (le code n'est pas une description)
    return " ".join(l.lstrip("# ").strip() for l in t.splitlines()[:8] if l.startswith("#")
                    and not l.startswith("#!")).strip()


def fiche_active():
    for f in ("NOYAU.md", "ETAT.md"):
        m = re.search(r"[Ff]iche[ _]active\s*:\s*`?([^`\s]+\.md)", lire(os.path.join(BRAIN, f)))
        if m:
            return os.path.basename(m.group(1))
    return None


# ------------------------------------------------------------ entrées
def statut_entree(e):
    if e.statut_fixe:
        return e.statut_fixe
    t = "\n".join(u.texte for u in e.unites)
    nt = norm(t)
    out = []
    m = re.search(r"statut\s*:\s*([^\n;.]{3,70})", t, re.I)
    if m:
        out.append(m.group(1).strip().strip("*"))
    else:
        for cle, lib in (("texte verifie", "lu (texte vérifié)"), ("lu par agent", "lu (agent)"),
                         ("lu par gemini", "lu (agent)"), ("*extrait*", "extrait"),
                         ("mesure chez nous", "mesuré"), ("*mesure", "mesuré"), ("*essaye", "essayé"),
                         ("vu dans les refs", "vu dans les refs"), ("retour de milan", "retour de Milan"),
                         ("(milan,", "retour de Milan"), ("milan (", "retour de Milan")):
            if cle in nt and lib not in out:
                out.append(lib)
    marques = [u for u in e.unites if u.marque]
    if marques:
        out.append(f"CONTREDIT x{len(marques)} (l. {', '.join(str(u.ligne) for u in marques[:4])})")
    if e.hist:
        out.append("HISTORIQUE")
    return " + ".join(out[:4]) or "sans statut"


def nombres(unites, n=4):
    vus = []
    for u in unites:
        for x in NUM_RE.findall(u.texte):
            x = x.strip()
            if x not in vus:
                vus.append(x)
            if len(vus) >= n:
                return vus
    return vus


def noter_entree(e, Q, poids):
    vivantes = [u for u in e.unites if u.niveau and not u.marque]
    touchees = [u for u in e.unites if u.niveau]
    if not touchees:
        return 0.0
    sc = sorted((u.score if u.niveau != "OU" else u.score * 0.5 for u in vivantes), reverse=True)
    base = (sc[0] + 0.25 * sum(sc[1:6])) if sc else 0.1
    e.contenu = base * poids
    bonus = 0.0
    r = Q.noter(norm(e.titre))
    if r:
        bonus = {"ET": 1.5, "~": 1.0, "OU": 0.4}[r[0]] + (1.0 if Q.phrase in norm(e.titre) else 0.0)
    return (base + bonus) * poids


def ou(u):
    if u.genre == "json":
        ch = u.extra.get("chemin", "")
        if u.src.endswith(".jsonl"):
            return f"{rel_b(u.src)}:{u.ligne}"
        return f"{rel_b(u.src)}#{ch}"
    if u.src.startswith(BRAIN):
        return f"{rel_b(u.src)}:{u.ligne}"
    return f"{rel(u.src)}:{u.ligne}"


def meilleure_ligne(u, Q):
    lignes = [l for l in u.texte.split("\n") if l.strip()]
    if len(lignes) <= 1:
        return u.ligne, u.texte.strip()
    best, bi = -1, 0
    for i, l in enumerate(lignes):
        nl = norm(l)
        s = sum(1 for g in Q.groupes if g.exact(nl))
        if s > best:
            best, bi = s, i
    return u.ligne + bi if u.genre == "md" else u.ligne, lignes[bi].strip()


def extrait_autour(t, Q, lim):
    """Les mots EXACTS de Milan : le message entier s'il est court, sinon une
    fenêtre copiée telle quelle autour du premier mot trouvé (jamais
    réécrite), bornée par « […] »."""
    if len(t) <= lim:
        return f"« {t} »"
    nt = norm(t)   # même longueur que t (accents retirés un par un, ’ -> ')
    pos = None
    if len(nt) == len(t):
        for g in Q.groupes:
            m = g.re_mot.search(nt) or (g.re_syn.search(nt) if g.re_syn is not None else None)
            if m and (pos is None or m.start() < pos):
                pos = m.start()
    a = 0 if pos is None else max(0, pos - lim // 3)
    if a:
        a = t.rfind(" ", 0, a) + 1   # coupe entre deux mots, jamais dans un mot
    b = min(len(t), a + lim)
    if b < len(t) and " " in t[a:b]:
        b = t.rfind(" ", a, b)
    return (f"« {'[…] ' if a else ''}{t[a:b]}{' […]' if b < len(t) else ''} » ({len(t)} car.)")


def court(t, n):
    t = " ".join(t.split())
    return t if len(t) <= n else t[:n - 1] + "…"


# ------------------------------------------------------------ fiche du moment
def choisir_fiche(entrees_md, Q, active):
    par_fiche = {}
    for e in entrees_md:
        if not e.src.startswith(FICHES + os.sep) or os.path.basename(e.src).startswith("_"):
            continue
        par_fiche.setdefault(e.src, []).append(e)
    notes = []
    for p, es in par_fiche.items():
        sc = sorted((e.score for e in es), reverse=True)
        s = sc[0] + 0.3 * sum(sc[1:3]) if sc else 0.0
        if active and os.path.basename(p) == active:
            s *= 1.5
        if s > 0:
            notes.append((s, p, es))
    notes.sort(key=lambda x: -x[0])
    return notes


def recence(e):
    """(date la plus récente, version la plus haute) lues dans le titre d'une
    section : dans une fiche de production, la lecture la plus récente a pu
    démentir les précédentes."""
    dates = re.findall(r"20\d\d-\d\d-\d\d", e.titre)
    vs = [int(v) for v in re.findall(r"\bv(\d+)", e.titre)]
    return (max(vs) if vs else -1, max(dates) if dates else "")


def repond(e):
    """La section répond-elle vraiment (pas un mot au passage) ? Au moins deux
    passages où les mots de la requête sont là en propre, ou un où la
    phrase entière est là."""
    forts = [u for u in e.unites if u.niveau in ("ET", "~") and not u.marque]
    return sum(1 for u in forts if u.brut >= 0.8) >= 2 or any(u.brut >= 1.5 for u in forts)


def texte_fiche(p, es, budget=3000):
    lignes = lire(p).splitlines()
    tout = "\n".join(lignes)
    if len(tout) <= budget:
        return tout, []
    tete_fin = next((e.ligne for e in es if e.ligne > 1), len(lignes) + 1) - 1
    tete = "\n".join(lignes[:tete_fin])
    if len(tete) > 420:
        tete = tete[:420].rsplit("\n", 1)[0] + "\n[…]"
    cles = sorted({recence(e) for e in es if e.score > 0 and e.ligne > 1})
    rang = {k: i for i, k in enumerate(cles)}

    def note(e):
        f = 1.0 + (0.5 * rang[recence(e)] / (len(cles) - 1) if len(cles) > 1 else 0.0)
        return e.score * f

    reste, pris, blocs = budget - len(tete), [], {}
    bornes = sorted(e.ligne for e in es)
    cand = sorted((e for e in es if e.score > 0 and e.ligne > 1), key=lambda e: -note(e))
    # la section la plus RÉCENTE parmi celles qui répondent bien passe d'abord
    # (la mieux notée peut porter une lecture démentie depuis)
    if cand and len(cles) > 1:
        bons = [e for e in cand if recence(e) != (-1, "") and repond(e)]
        if bons:
            recent = max(bons, key=recence)
            cand.remove(recent)
            cand.insert(0, recent)
            texte_fiche.recente = recent
    for e in cand:
        fin = next((b for b in bornes if b > e.ligne), len(lignes) + 1) - 1
        bloc = "\n".join(lignes[e.ligne - 1:fin]).rstrip()
        dispo = reste - 2
        if dispo < 400:
            break
        if len(bloc) > dispo:
            coupe = bloc[:dispo - 60].rsplit("\n", 1)[0]
            bloc = coupe + f"\n[… suite : {rel_b(p)}:{e.ligne + coupe.count(chr(10)) + 1}]"
        blocs[e] = bloc
        pris.append(e)
        reste -= len(bloc) + 2
    ordre = [tete] + [blocs[e] for e in sorted(pris, key=lambda e: e.ligne)]
    autres = [e for e in es if e.score > 0 and e not in pris and e.ligne > 1]
    texte_fiche.montrees = pris
    return "\n\n".join(ordre), sorted(autres, key=lambda e: -note(e))


# ------------------------------------------------------------ principal
def autour(spec, n=15):
    f, _, l = spec.rpartition(":")
    for base in (BRAIN, ROOT, os.getcwd()):
        p = os.path.join(base, f)
        if os.path.isfile(p):
            lignes = lire(p).splitlines()
            k = int(l)
            for i in range(max(1, k - n), min(len(lignes), k + n) + 1):
                print(f"{'>' if i == k else ' '}{i:5d}  {lignes[i - 1]}")
            return
    print(f"(introuvable : {spec})")


def rappel(req, maxi=20, court_=False, exclus=()):
    Q = Requete(req)
    out = []
    P = out.append
    # 1. collecte
    entrees_md, unites_md, fichiers = [], [], fichiers_md(exclus)
    poids = {}
    for p in fichiers:
        es, us, hist = decouper_md(p)
        poids[p] = poids_fichier(p, hist)
        entrees_md += es
        unites_md += us
    entrees_js, unites_js = sources_json(exclus)
    milan = verbatim()
    motifs = motifs_json()
    outils = outils_depot()
    # 2. notation
    for u in unites_md + unites_js + milan:
        r = Q.noter(u.nt)
        if r:
            u.niveau, u.brut = r
            u.score = u.brut * poids.get(u.src, 1.0)
    for e in entrees_md:
        e.score = noter_entree(e, Q, poids.get(e.src, 1.0))
    for e in entrees_js:
        e.score = noter_entree(e, Q, 1.1 if e.id.startswith("poses/") else 0.8)
    # messages de Milan cités (sha1) par une entrée trouvée : la source primaire remonte
    cites = {}
    for u in unites_md:
        if u.niveau in ("ET", "~") and not u.marque and u.src.startswith(BRAIN) \
                and not rel_b(u.src).startswith("corpus/recherche/"):
            for s in SHA_RE.findall(u.texte):
                cites.setdefault(s, ou(u))
    for m in motifs:   # une citation de motif remonte seulement si SES mots répondent à la requête
        for c in m.get("citations", []):
            r = Q.noter(norm(c.get("extrait", "")))
            if c.get("sha1") and r and r[0] != "OU":
                cites.setdefault(c["sha1"], f"motifs.json {m.get('id')}")
    for k, u in enumerate(milan):   # le plus récent compte un peu plus (« le dernier message l'emporte »)
        if u.niveau:
            u.score += 0.3 * k / max(1, len(milan))
        s = u.extra.get("sha1")
        if s in cites:
            if not u.niveau:
                u.niveau, u.score = "cité", 0.0
            u.score += 1.5
            u.extra = dict(u.extra, cite_par=cites[s])
    # 3. INDEX
    cand = [e for e in entrees_md + entrees_js if e.score > 0 and os.path.basename(e.src) != "CATALOGUE_REFS.md"]
    cand.sort(key=lambda e: -e.score)
    active = fiche_active()
    fiches = choisir_fiche(entrees_md, Q, active)
    mots_q = ", ".join(g.mot for g in Q.groupes)
    P(f"RAPPEL « {req} » -- mots : {mots_q}" + (f" ; familles : {', '.join(Q.familles)}" if Q.familles else ""))
    P("(information datée avec sa source, pas des règles ; [ET] tous les mots, [~] racines/trigrammes, "
      "[OU] une partie ; CONTREDIT en dernier)")
    idx, nj = [], 0
    for e in cand:   # au plus 3 sources JSON dans l'INDEX : les entrées écrites passent aussi
        if e.genre == "json":
            nj += 1
            if nj > 3:
                continue
        idx.append(e)
        if len(idx) >= 10:
            break
    if court_:
        return rappel_court(req, Q, idx, fiches, motifs, milan, unites_md + unites_js), Q
    if idx:
        P("\n== INDEX (id | statut | nombres | où) ==")
        for k, e in enumerate(idx, 1):
            tu = sorted((u for u in e.unites if u.niveau and not u.marque), key=lambda u: -u.score)
            nb = nombres(tu[:6] or e.unites[:3])
            lieu = ou(tu[0]) if tu else (f"{rel_b(e.src)}:{e.ligne}" if e.genre == "md" else rel_b(e.src))
            P(f"{k:2d}. {e.id} « {court(e.titre, 60)} » | {statut_entree(e)} | "
              f"{' ; '.join(nb) if nb else '-'} | {lieu}")
    # 4. fiche du moment
    if fiches:
        s, p, es = fiches[0]
        texte_fiche.montrees, texte_fiche.recente = [], None
        txt, autres = texte_fiche(p, es)
        act = " ; fiche active (NOYAU)" if active and os.path.basename(p) == active else ""
        mt = [e.id.split()[-1] + (" (la plus récente qui répond)" if e is texte_fiche.recente else "")
              for e in texte_fiche.montrees]
        sec = f" ; montré : {', '.join(mt)}" if mt else ""
        P(f"\n== Fiche du moment : {rel_b(p)} ({len(txt)} caractères{act}{sec}) ==")
        P(txt)
        if autres:
            P("-- autres sections de cette fiche : " + " ; ".join(f"{e.id} ({rel_b(p)}:{e.ligne})" for e in autres[:6]))
        if len(fiches) > 1:
            P("-- autres fiches : " + " ; ".join(f"{rel_b(q)} ({round(sc, 1)})" for sc, q, _ in fiches[1:5]))
    # 5. motifs
    ms = []
    for m in motifs:
        t = norm(" ".join([m.get("phrase", ""), m.get("id", "")] + [c.get("extrait", "") for c in m.get("citations", [])]))
        r = Q.noter(t)
        if r and r[0] != "OU":
            ms.append((r[1], m))
    ms.sort(key=lambda x: -x[0])
    if ms:
        P("\n== Motifs (corpus/motifs.json : Milan te l'a dit N fois, ses mots exacts) ==")
        try:
            sys.path.insert(0, HERE)
            import motifs as MO  # noqa: E402
            chrono = MO.chronologie()
            for k, (_, m) in enumerate(ms[:2]):
                bl = MO.bloc(m, chrono, max_cit=3)
                if k:   # la mesure liée seulement pour le premier motif ; le reste : outils/motifs.py
                    bl = [l for l in bl if not l.startswith("  mesure liée") and not l.startswith("    ")]
                    bl.append(f"  (mesure liée : python3 outils/motifs.py {m.get('id')})")
                P("\n".join(bl))
        except Exception as exc:  # l'affichage des motifs ne doit pas casser le rappel
            for _, m in ms[:3]:
                P(f"{m.get('phrase')} (mon résumé) : Milan l'a dit {m.get('nombre_de_fois')} fois ({m.get('statut')}) ({exc})")
    # 6. mots de Milan
    mil = sorted((u for u in milan if u.niveau), key=lambda u: (u.niveau == "OU", -u.score, u.extra.get("date", "")))
    forts = [u for u in mil if u.niveau != "OU"]
    montres = (forts if len(forts) >= 3 else mil)[:5]
    montres.sort(key=lambda u: u.extra.get("date", ""))
    if montres:
        P(f"\n== Mots de Milan (corpus/milan_verbatim.jsonl, mots exacts datés ; {len(forts)} trouvés en ET/~"
          f"{', ' + str(len(mil) - len(forts)) + ' en OU' if len(mil) > len(forts) else ''}) ==")
        for u in montres:
            m = u.extra
            t = m.get("texte")
            lim = 250 if not m.get("cite_par") and u.niveau == "OU" else 450
            if t is None:
                corps = f"[collé, {m.get('longueur', '?')} car.] {court(m.get('debut', ''), 200)}"
            else:
                corps = extrait_autour(t, Q, lim)
            cp = f" ; cité par {m['cite_par']}" if m.get("cite_par") else ""
            P(f"- {m.get('date', '')[:16].replace('T', ' ')} [{m.get('sha1')}] ({m.get('mode')} ; "
              f"[{u.niveau}]{cp}) {corps}")
    # 7. mesures (JSON)
    mj = sorted((u for u in unites_js if u.niveau and not u.marque), key=lambda u: (u.niveau == "OU", -u.score))
    fj = [u for u in mj if u.niveau != "OU"]
    mj = (fj if len(fj) >= 3 else mj)
    par_f, garde = {}, []
    for u in mj:   # au plus 2 par fichier : plusieurs sources plutôt qu'une seule très bavarde
        par_f[u.src] = par_f.get(u.src, 0) + 1
        if par_f[u.src] <= 2:
            garde.append(u)
    mj = garde[:8]
    if mj:
        P("\n== Mesures et lectures (poses/ avec vérifications, clips/, perception, notes, hypothèses) ==")
        for u in mj:
            v = f" [vérif : {u.extra['verif']}]" if u.extra.get("verif") else ""
            P(f"- [{u.niveau}] {ou(u)}{v} : {court(u.texte, 170)}")
    # 8. catalogue
    cat = [u for u in unites_md if u.src == CATALOGUE and u.niveau and not u.marque and u.texte.startswith("|")
           and "---" not in u.texte]
    cat.sort(key=lambda u: (u.niveau == "OU", -u.score))
    fc = [u for u in cat if u.niveau != "OU"]
    cat = (fc if fc else cat)[:8]
    if cat:
        P("\n== Refs du catalogue (corpus/CATALOGUE_REFS.md) ==")
        for u in cat:
            P(f"  [{u.niveau}] :{u.ligne} {court(u.texte, 170)}")
    # 9. outils
    to = []
    for f in outils:
        if f.endswith("outils/rappel.py"):
            continue
        r = Q.noter(norm(f.replace("_", " ") + " " + doc_py(f)))
        if r and r[0] != "OU":
            to.append((r[1] + (0.5 if "animator_brain" in f else 0.0), f))
    to.sort(key=lambda x: -x[0])
    if to:
        P("\n== Outils (tout le dépôt) ==")
        for _, f in to[:8]:
            d = court(doc_py(f).split("\n\n")[0], 100)
            P(f"  {f} : {d}")
    # 10. passages
    deja = {id(u) for u in cat}
    pas = [u for u in unites_md if u.niveau and not u.marque and id(u) not in deja
           and not (u.src.startswith(FICHES) and fiches and u.src == fiches[0][1])]
    fp = [u for u in pas if u.niveau != "OU"]
    pas = fp if len(fp) >= 5 else pas
    par = {}
    for u in pas:
        par.setdefault(u.src, []).append(u)
    ordre = sorted(par.items(), key=lambda kv: -max(u.score for u in kv[1]))
    if ordre:
        P("\n== Passages (fichier:ligne) ==")
        total = 0
        for p, us in ordre:
            us.sort(key=lambda u: -u.score)
            h = " [HISTORIQUE, rétrogradé]" if any(e.hist for e in {u.entree for u in us if u.entree}) else ""
            P(f"-- {rel_b(p) if p.startswith(BRAIN) else rel(p)} ({len(us)}){h}")
            for u in us[:3]:
                ln, t = meilleure_ligne(u, Q)
                P(f"   {ln}: [{u.niveau}] {court(t, 120)}")
                total += 1
            if total >= maxi:
                reste = ordre[ordre.index((p, us)) + 1:]
                if reste:
                    # rétrogradés ou coupés par la limite, jamais cachés : au moins leur nom et leurs lignes
                    P(f"   ... (limite {maxi} atteinte ; --max pour plus) ; aussi dans : " + " ; ".join(
                        f"{rel_b(q) if q.startswith(BRAIN) else rel(q)} ({len(v)}"
                        f"{', HISTORIQUE' if any(u.entree and u.entree.hist for u in v) else ''} : "
                        f"l.{', '.join(str(u.ligne) for u in sorted(v, key=lambda u: -u.score)[:3])})"
                        for q, v in reste))
                break
    # 11. CONTREDIT en dernier
    cn = [u for u in unites_md + unites_js if u.niveau and u.marque]
    if cn:
        # d'abord les lectures démenties par Milan (marques dans le cerveau), puis les réfutations des vérificateurs
        cn.sort(key=lambda u: (u.genre != "md", -u.score))
        P("\n== CONTREDIT / réfuté (gardé pour la trace, affiché en dernier) ==")
        for u in cn[:10]:
            ln, t = meilleure_ligne(u, Q)
            lieu = ou(u) if u.genre == "json" else (f"{rel_b(u.src)}:{ln}" if u.src.startswith(BRAIN) else f"{rel(u.src)}:{ln}")
            eid = f" ({u.entree.id})" if u.entree and u.genre == "md" else ""
            reste = u.texte.replace(u.marque, " ") if u.marque in u.texte else t
            P(f"- {lieu}{eid} {court(u.marque, 90)} : {court(reste.lstrip(' -|'), 150)}")
    # 12. couverture
    trouve = any(u.niveau for u in unites_md + unites_js + milan) or ms or to
    fouille = (f"{len(fichiers)} fichiers .md (cerveau + README/FICHE des productions), {len(milan)} messages "
               f"de Milan, {len(entrees_js) - 1} JSON (poses, clips, perception, hypothèses) + notes_milan, "
               f"{len(motifs)} motifs, {len(outils)} outils .py")
    if not trouve:
        P("\nAUCUN RÉSULTAT. Aucun résultat ≠ aucun savoir : le cerveau peut le dire avec d'autres mots.")
        P(f"Fouillé : {fouille}.")
        P(f"Mots cherchés (racines) : {', '.join(racine(g.mot) for g in Q.groupes) or '(aucun mot de 3 lettres)'}"
          " ; essayer un synonyme, un seul mot, ou python3 outils/motifs.py --candidats.")
    else:
        P(f"\nFouillé : {fouille}.")
    return "\n".join(out), Q


def rappel_court(req, Q, idx, fiches, motifs, milan, unites):
    """Sortie courte (~1 500 caractères) : pour un rappel poussé à chaque
    message (hook), seulement quand la version complète a fait ses preuves."""
    out = [f"RAPPEL court « {req} » ({', '.join(g.mot for g in Q.groupes)}"
           f"{' ; ' + ', '.join(Q.familles) if Q.familles else ''}) : information, pas règle."]
    for k, e in enumerate(idx[:3], 1):
        tu = sorted((u for u in e.unites if u.niveau and not u.marque), key=lambda u: -u.score)
        nb = nombres(tu[:6])
        out.append(f"{k}. {e.id} [{court(statut_entree(e), 60)}] {' ; '.join(nb[:3])} "
                   f"{ou(tu[0]) if tu else rel_b(e.src)}")
    if fiches:
        out.append(f"Fiche du moment : {rel_b(fiches[0][1])}")
    for m in motifs:
        t = norm(" ".join([m.get("phrase", ""), m.get("id", "")] + [c.get("extrait", "") for c in m.get("citations", [])]))
        r = Q.noter(t)
        if r and r[0] != "OU":
            der = sorted(m.get("citations", []), key=lambda c: c.get("date", ""))[-1:]
            d = f" ; dernier {der[0]['date'][:10]} « {court(der[0]['extrait'], 90)} »" if der else ""
            out.append(f"Motif (mon résumé) : {m.get('phrase')} : Milan l'a dit {m.get('nombre_de_fois')} fois "
                       f"({m.get('statut')}){d}")
            break
    mil = sorted((u for u in milan if u.niveau and u.niveau != "OU"), key=lambda u: -u.score)[:2]
    for u in sorted(mil, key=lambda u: u.extra.get("date", "")):
        t = u.extra.get("texte")
        out.append(f"Milan {u.extra.get('date', '')[:16].replace('T', ' ')} [{u.extra.get('sha1', '')[:8]}] "
                   + (extrait_autour(t, Q, 200) if t else f"[collé] « {court(u.extra.get('debut', ''), 150)} »"))
    nc = sum(1 for u in unites if u.niveau and u.marque)
    if nc:
        out.append(f"{nc} ligne(s) CONTREDIT / réfutées : voir le rappel complet.")
    if len(out) == 1:
        out.append("Aucun résultat ≠ aucun savoir : essayer d'autres mots (rappel complet).")
    out.append(f"Complet : python3 outils/rappel.py \"{req}\"")
    return "\n".join(out)


def main(argv):
    args = list(argv)
    m, court_, exclus = 20, False, []
    if "--max" in args:
        k = args.index("--max")
        m = int(args[k + 1])
        del args[k:k + 2]
    if "--exclure" in args:
        k = args.index("--exclure")
        exclus = [x for x in args[k + 1].split(",") if x]
        del args[k:k + 2]
    if "--autour" in args:
        k = args.index("--autour")
        autour(args[k + 1])
        return
    if "--court" in args:
        court_ = True
        args.remove("--court")
    texte, _ = rappel(" ".join(args) or "coup charge", m, court_, exclus)
    print(texte)


if __name__ == "__main__":
    main(sys.argv[1:])
