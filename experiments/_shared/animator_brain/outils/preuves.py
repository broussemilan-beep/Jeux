"""
REGISTRE DE PREUVES : une ligne écrite par l'OUTIL qui a tourné, jamais par
le modèle qui raconte.

Pourquoi (audit + plan de réorganisation du 2026-09-26, brique A8, plan
§2.4 point 5) : « vérifié », « mesuré », « confirmé » s'écrivaient en prose
dans le worklog et les fiches, sans trace de ce qui avait VRAIMENT tourné,
sur QUELS fichiers, à QUEL commit. Une preuve d'hier sur un export modifié
depuis était encore citée comme valable. Chez Hermes Agent, le registre de
vérification est écrit par le code (`verification_evidence.py`) ; ici pareil.

Ce qu'on adapte (principe de Milan : « on apprend, pas de règles gravées ») :
- le statut se lit PAR TYPE de preuve, pas « la dernière preuve gagne » : un
  `juge_temps` récent ne cache pas un `technique` périmé ;
- SEUL le type `technique` (sens Roblox, interpolation, aller-retour
  moteur…) peut être « passe » ou « echoue ». Tous les autres types
  (mesures de pose, juge temporel, durées, capture, vu par Milan) portent le
  statut « valeurs » : ce sont des nombres à lire, pas des portes ;
- le fichier ne fait que GRANDIR (on ajoute, on ne réécrit jamais) :
  `croissance` vérifie que la version committée est un préfixe du fichier.

Une ligne de `corpus/preuves.jsonl` :
  date (UTC), production, kind, portee (image / plan / scene / partielle),
  statut, commit HEAD, entrees_hors_commit (fichiers modifiés non committés
  au moment de la preuve), entrees {chemin: sha256}, commande,
  sortie_resumee (≤ 2000 caractères : 1/3 de tête + la fin, car une sortie
  dit souvent l'essentiel à la fin).

Statut d'une production, par kind (`statut <production>`) :
  non_verifie : aucune ligne de ce type ;
  perime      : au moins un fichier d'entrée a changé (sha différent, ou
                disparu) depuis la dernière ligne de ce type ;
  passe / echoue : dernière ligne `technique` à jour ;
  valeurs     : dernière ligne à jour d'un autre type (des mesures existent
                pour CES fichiers ; les lire, pas les compter).

Usage :
  from preuves import enregistrer_preuve        # depuis un outil
  from preuves import executer_et_enregistrer   # brancher un vieux script (capture sa sortie)
  python3 preuves.py statut <production> [--json] [--tout]
  python3 preuves.py lancer --production P --kind K --portee S --entrees a,b -- <commande…>
      (lance la commande, enregistre SA sortie ; technique : code 0 = passe)
  python3 preuves.py croissance                 # le registre n'a fait que grandir ?
Variable d'environnement PREUVES_JSONL : autre registre (tests).
Consultatif : le code de sortie est 0, sauf `lancer` qui rend celui de la
commande lancée.
"""
import datetime
import hashlib
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BRAIN = os.path.normpath(os.path.join(HERE, ".."))
ROOT = os.path.normpath(os.path.join(BRAIN, "..", "..", ".."))
REGISTRE = os.path.join(BRAIN, "corpus", "preuves.jsonl")

KINDS = ("technique", "mesure_technique", "mesure_pose", "juge_temps", "durees", "capture", "vu_par_milan")
# mesure_technique (ajouté le 2026-09-26) : contact, sol, structure MESURÉS
# sans seuil (les anciens calibrate.py / foot_check.py des prototypes
# pré-V2.22 impriment des écarts sans dire passe/échoue) : des valeurs à lire.
PORTEES = ("image", "plan", "scene", "partielle")
MAX_RESUME = 2000


def registre_courant(registre=None):
    return registre or os.environ.get("PREUVES_JSONL") or REGISTRE


# ------------------------------------------------------------ empreintes
def _sha_fichier(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for bloc in iter(lambda: f.read(1 << 20), b""):
            h.update(bloc)
    return h.hexdigest()


def empreinte(chemin):
    """sha256 d'un fichier ; d'un dossier : sha256 des (chemin relatif, sha)
    de tous ses fichiers triés ; None si le chemin n'existe pas."""
    if os.path.isfile(chemin):
        return _sha_fichier(chemin)
    if os.path.isdir(chemin):
        h = hashlib.sha256()
        for dp, dn, fs in sorted(os.walk(chemin)):
            dn[:] = sorted(d for d in dn if d not in ("__pycache__", ".git"))
            for f in sorted(fs):
                p = os.path.join(dp, f)
                h.update(os.path.relpath(p, chemin).encode() + b"\0" + _sha_fichier(p).encode() + b"\n")
        return "dossier:" + h.hexdigest()
    return None


def _cle(chemin):
    """Chemin relatif à la racine du dépôt quand il y est (lisible, stable)."""
    a = os.path.abspath(chemin)
    return os.path.relpath(a, ROOT) if a.startswith(ROOT + os.sep) else a


def _abs(cle):
    return cle if os.path.isabs(cle) else os.path.join(ROOT, cle)


def _git(*args, brut=False):
    """Sortie de git ; brut=True : sans strip() (le format --porcelain commence
    par un espace significatif : « M chemin » ; le strip() coupait la 1re
    lettre du 1er chemin, bug vu et corrigé le 2026-09-26)."""
    try:
        out = subprocess.run(["git", "-C", ROOT] + list(args), capture_output=True, text=True,
                             timeout=30).stdout
    except (OSError, subprocess.SubprocessError):
        return ""
    return out if brut else out.strip()


def resumer(texte, n=MAX_RESUME):
    """≤ n caractères : le tiers de tête + la fin (le verdict d'une sortie
    est souvent en bas), avec le nombre de caractères coupés au milieu."""
    texte = texte or ""
    if len(texte) <= n:
        return texte
    coupe = len(texte)
    for _ in range(3):                   # la marque dépend du nombre coupé : on itère
        marque = f"\n[… {coupe} caractères coupés …]\n"
        tete = (n - len(marque)) // 3
        fin = n - len(marque) - tete
        coupe = len(texte) - tete - fin
    return texte[:tete] + marque + texte[-fin:]


# ------------------------------------------------------------ écrire
def enregistrer_preuve(production, kind, portee, statut, entrees, sortie_resumee, commande, registre=None):
    """Ajoute UNE ligne au registre et la renvoie (dict).

    production : nom du dossier de la production (ex. « r6_un_seul_coup ») ;
    kind : technique | mesure_technique | mesure_pose | juge_temps | durees | capture | vu_par_milan ;
    portee : image | plan | scene | partielle ;
    statut : « passe » / « echoue » pour technique ; pour tout autre kind,
      None ou « valeurs » (un autre statut lève ValueError : une mesure n'est
      pas une porte) ;
    entrees : chemins (fichiers ou dossiers) dont la preuve dépend (export,
      scène, script) : leur sha256 sert à dire « périmé » plus tard ;
    sortie_resumee : la sortie de l'outil (texte ou objet JSON-able), coupée
      à 2000 caractères (1/3 tête + fin) ;
    commande : la commande ou l'appel qui a produit la preuve."""
    if kind not in KINDS:
        raise ValueError(f"kind inconnu : {kind!r} (attendu : {', '.join(KINDS)})")
    if portee not in PORTEES:
        raise ValueError(f"portee inconnue : {portee!r} (attendu : {', '.join(PORTEES)})")
    if kind == "technique":
        if statut not in ("passe", "echoue"):
            raise ValueError("kind technique : statut « passe » ou « echoue »")
    else:
        if statut not in (None, "valeurs"):
            raise ValueError(f"kind {kind} : pas de passe/échoue (des valeurs à lire), statut « valeurs »")
        statut = "valeurs"
    if isinstance(entrees, str):
        entrees = [entrees]
    emp = {_cle(p): empreinte(os.path.abspath(p)) for p in entrees}
    hors = []
    if emp:
        st = _git("status", "--porcelain", "--", *[_abs(k) for k in emp], brut=True)
        hors = sorted({ln[3:].strip() for ln in st.splitlines() if ln.strip()})
    if not isinstance(sortie_resumee, str):
        sortie_resumee = json.dumps(sortie_resumee, ensure_ascii=False, default=str)
    ligne = {"date": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
             "production": production, "kind": kind, "portee": portee, "statut": statut,
             "commit": _git("rev-parse", "HEAD") or None, "entrees_hors_commit": hors,
             "entrees": emp, "commande": commande if isinstance(commande, str) else " ".join(map(str, commande)),
             "sortie_resumee": resumer(sortie_resumee)}
    reg = registre_courant(registre)
    os.makedirs(os.path.dirname(os.path.abspath(reg)), exist_ok=True)
    with open(reg, "a", encoding="utf-8") as f:           # AJOUT seulement
        f.write(json.dumps(ligne, ensure_ascii=False) + "\n")
    return ligne



class _Tee:
    """Recopie ce qu'on écrit sur la sortie d'origine ET le garde."""

    def __init__(self, dest):
        self.dest, self.morceaux = dest, []

    def write(self, x):
        self.morceaux.append(x)
        return self.dest.write(x)

    def flush(self):
        self.dest.flush()

    def texte(self):
        return "".join(self.morceaux)


def executer_et_enregistrer(production, kind, portee, entrees, fonction, commande, statut=None, registre=None):
    """Branchement minimal d'un script de vérification existant : lance
    fonction() en laissant sa sortie s'afficher, la capture, puis ajoute UNE
    ligne au registre avec cette sortie (le script ne change pas de
    comportement). Renvoie (résultat de fonction, ligne).

    statut : pour kind « technique », « passe » / « echoue » ou une fonction
    (résultat, sortie) -> « passe » / « echoue » ; ignoré pour les autres
    kinds (« valeurs »). Si fonction lève une exception (SystemExit
    compris) : en « technique », une ligne « echoue » est écrite avec la fin de
    la sortie et l'erreur, puis l'exception remonte ; pour les autres kinds,
    rien n'est écrit (une mesure qui plante n'est pas une valeur)."""
    import traceback
    tee = _Tee(sys.stdout)
    ancien, sys.stdout = sys.stdout, tee
    try:
        try:
            res = fonction()
        except SystemExit as ex:
            if ex.code not in (None, 0):
                raise
            res = None                  # sys.exit(0) : fin normale, pas un échec (relecture 2026-09-26)
    except BaseException as ex:
        sys.stdout = ancien
        if kind == "technique":
            err = "".join(traceback.format_exception_only(type(ex), ex)).strip()
            enregistrer_preuve(production, kind, portee, "echoue", entrees,
                               tee.texte() + f"\n[erreur] {err}", commande, registre)
        raise
    finally:
        sys.stdout = ancien
    if kind == "technique":
        st = statut(res, tee.texte()) if callable(statut) else statut
    else:
        st = "valeurs"
    ligne = enregistrer_preuve(production, kind, portee, st, entrees, tee.texte(), commande, registre)
    print(f"[preuves] ligne ajoutée : {production} {kind} {ligne['statut']} commit {(ligne['commit'] or '?')[:8]}")
    return res, ligne

# ------------------------------------------------------------ lire
def lire(registre=None):
    reg = registre_courant(registre)
    out = []
    if not os.path.exists(reg):
        return out
    for i, l in enumerate(open(reg, encoding="utf-8"), 1):
        if l.strip():
            try:
                e = json.loads(l)
                e["_ligne"] = i
                out.append(e)
            except json.JSONDecodeError:
                out.append({"_ligne": i, "_illisible": l[:120]})
    return out


def changes(e):
    """Entrées dont le sha actuel diffère de celui de la preuve."""
    return [k for k, h in (e.get("entrees") or {}).items() if empreinte(_abs(k)) != h]


def statut(production, registre=None):
    """{kind: {etat, derniere, changes, n}} pour chaque kind connu."""
    lignes = [e for e in lire(registre) if e.get("production") == production]
    out = {}
    for k in KINDS:
        ls = [e for e in lignes if e.get("kind") == k]
        if not ls:
            out[k] = {"etat": "non_verifie", "n": 0}
            continue
        d = ls[-1]
        ch = changes(d)
        etat = "perime" if ch else d.get("statut", "valeurs")
        out[k] = {"etat": etat, "n": len(ls), "changes": ch,
                  "derniere": {c: d.get(c) for c in ("date", "commit", "portee", "commande", "entrees_hors_commit",
                                                      "_ligne")},
                  "extrait": (d.get("sortie_resumee") or "")[-160:]}
    return out


def texte_statut(production, st, registre=None, tout=False):
    reg = registre_courant(registre)
    L = [f"PREUVES de {production} (registre {_cle(reg)}) -- consultatif, par type",
         "  (seul « technique » dit passe/échoue ; les autres types sont des valeurs à lire)"]
    for k in KINDS:
        s = st[k]
        if s["etat"] == "non_verifie":
            L.append(f"  {k:13s} non_verifie")
            continue
        d = s["derniere"]
        L.append(f"  {k:13s} {s['etat']:11s} {(d['date'] or '')[:16]}  commit {(d['commit'] or '?')[:8]}  "
                 f"portée {d['portee']}  ({s['n']} ligne{'s' if s['n'] > 1 else ''}, dernière l.{d['_ligne']})")
        if s["changes"]:
            L.append("      fichiers changés depuis : " + ", ".join(s["changes"]))
        if d.get("entrees_hors_commit"):
            L.append("      entrées non committées au moment de la preuve : " + ", ".join(d["entrees_hors_commit"]))
        L.append(f"      commande : {d['commande'][:150]}")
    if tout:
        L.append("")
        L.append("HISTORIQUE")
        for e in lire(registre):
            if e.get("production") == production:
                L.append(f"  l.{e['_ligne']:<4d} {e['date'][:16]} {e['kind']:13s} {e['statut']:7s} "
                         f"{(e.get('commit') or '?')[:8]}  {e['commande'][:90]}")
    return "\n".join(L)


# ------------------------------------------------------------ croissance
def croissance(registre=None):
    """Le registre n'a fait que grandir depuis HEAD ? (la version committée
    doit être un préfixe exact du fichier actuel)."""
    reg = registre_courant(registre)
    rel = os.path.relpath(os.path.abspath(reg), ROOT)
    try:
        avant = subprocess.run(["git", "-C", ROOT, "show", f"HEAD:{rel}"], capture_output=True, timeout=30)
    except (OSError, subprocess.SubprocessError) as ex:
        return {"ok": None, "detail": f"git indisponible : {ex}"}
    if avant.returncode != 0:
        return {"ok": None, "detail": f"{rel} pas encore dans HEAD : rien à comparer"}
    maintenant = open(reg, "rb").read() if os.path.exists(reg) else b""
    ok = maintenant.startswith(avant.stdout)
    return {"ok": ok, "octets_head": len(avant.stdout), "octets_maintenant": len(maintenant),
            "detail": "le registre n'a fait que grandir" if ok else
            "ATTENTION : des lignes committées ont été modifiées ou supprimées (le registre doit seulement grandir)"}


# ------------------------------------------------------------ CLI
def _lancer(a):
    """lancer --production P --kind K --portee S [--entrees a,b] [--statut valeurs] -- commande…"""
    if "--" not in a:
        raise SystemExit("usage : preuves.py lancer --production P --kind K --portee S --entrees a,b -- <commande…>")
    k = a.index("--")
    opts, cmd = a[:k], a[k + 1:]
    o = {}
    for i in range(0, len(opts) - 1, 2):
        o[opts[i].lstrip("-")] = opts[i + 1]
    r = subprocess.run(cmd, capture_output=True, text=True)
    sortie = (r.stdout or "") + (("\n[stderr]\n" + r.stderr) if r.stderr.strip() else "")
    sys.stdout.write(r.stdout)
    sys.stderr.write(r.stderr)
    kind = o["kind"]
    st = ("passe" if r.returncode == 0 else "echoue") if kind == "technique" else "valeurs"
    ent = [x for x in o.get("entrees", "").split(",") if x]
    e = enregistrer_preuve(o["production"], kind, o["portee"], st, ent, sortie + f"\n[code de sortie {r.returncode}]",
                           cmd)
    print(f"[preuves] ligne ajoutée : {e['production']} {e['kind']} {e['statut']} commit {(e['commit'] or '?')[:8]}",
          file=sys.stderr)
    return r.returncode


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a or a[0] in ("-h", "--help"):
        print(__doc__)
        sys.exit(0)
    if a[0] == "statut" and len(a) >= 2:
        s = statut(a[1])
        if "--json" in a:
            print(json.dumps(s, ensure_ascii=False, indent=1))
        else:
            print(texte_statut(a[1], s, tout="--tout" in a))
        sys.exit(0)
    if a[0] == "croissance":
        print(json.dumps(croissance(), ensure_ascii=False))
        sys.exit(0)
    if a[0] == "lancer":
        sys.exit(_lancer(a[1:]))
    print(__doc__)
    sys.exit(0)
