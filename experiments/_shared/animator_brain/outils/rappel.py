"""
RAPPEL : ce que le cerveau sait déjà sur un concept, AVANT de travailler.

Retour de Milan (2026-09-25) : « poing chargé puissant » devait faire écho au
Serious Punch de Saitama (le GIF et l'anime TSB). La mémoire existait dans
les fichiers, mais rien ne la rappelait. Cet outil :
- élargit le mot demandé avec des familles de synonymes (CONCEPTS) ;
- cherche dans TOUT le cerveau versionné (carnet, catalogue des refs, notes
  brutes, études, retours, leçons, fiches, tutos, recherches, README des
  productions) ;
- affiche d'abord les refs du CATALOGUE, puis les passages, fichier par
  fichier, avec leur numéro de ligne.
Ce n'est pas un moteur sémantique : il faut lire ce qu'il sort. Quand un
concept manque, on l'ajoute ici.

Usage : python3 rappel.py "poing chargé" [--max 60]
"""
import os
import re
import sys
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
BRAIN = os.path.normpath(os.path.join(HERE, ".."))
ROOT = os.path.normpath(os.path.join(BRAIN, "..", "..", ".."))   # racine du dépôt

CONCEPTS = {
    "coup charge": ["coup charge", "coup chargé", "poing charge", "serious punch", "serious", "saitama", "obari",
                    "one punch", "opm", "deku", "poing vers la camera", "poing vers le lecteur", "poing geant",
                    "charge", "armé tenu", "arme tenu", "stoic bomb", "coup final", "ultime"],
    "rafale": ["rafale", "m1", "gatling", "jab", "direct", "crochet", "combo", "cross punch", "punch practice"],
    "impact": ["impact", "carte", "cartes", "hitstop", "gel", "blanc", "noir", "silhouette inversee", "flash",
               "contact", "skip the point of contact", "babbitt", "ken harris"],
    "camera": ["camera", "caméra", "cadrage", "gros plan", "plan large", "secousse", "shake", "contre-plongee",
               "camera de jeu", "cinema", "cinématique", "trauma"],
    "timing": ["timing", "tenue", "tenu", "contraste", "slow against the fast", "lent", "rapide", "ease",
               "amorti", "linear", "cles eparses", "clés éparses", "espacement", "interpolation"],
    "pose": ["pose", "silhouette", "torsion", "lacet", "bascule", "bras libre", "armé", "fente", "ligne",
             "exager", "exagér", "pousser"],
    "aerien": ["aerien", "aérien", "en l'air", "plongee", "plongée", "suspendu", "saut", "vers le bas"],
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
    "allure": ["allure", "allure.py", "vitesse du dragon", "dans tous les sens", "trop rapide", "virage",
               "majestueux", "rythme", "enchainement", "enchaînement", "serpent", "corps par seconde"],
}


def norm(s):
    s = unicodedata.normalize("NFD", s.lower())
    return "".join(c for c in s if unicodedata.category(c) != "Mn")


def termes(req):
    r = norm(req)
    out = {r}
    for nom, syn in CONCEPTS.items():
        fam = [norm(x) for x in syn] + [norm(nom)]
        if any(t in r or r in t for t in fam):
            out |= set(fam)
    return sorted(out, key=len, reverse=True)


def fichiers():
    """Le cerveau (.md + notes de Milan) et, pour chaque production, son
    README et ses fiches."""
    for dp, _dn, fs in os.walk(BRAIN):
        if "__pycache__" in dp or "/data" in dp:
            continue
        for f in fs:
            if f.endswith(".md") or f == "notes_milan.jsonl":
                yield os.path.join(dp, f)
    exp = os.path.join(ROOT, "experiments")
    for prod in sorted(os.listdir(exp)):
        d = os.path.join(exp, prod)
        if prod.startswith("_") or not os.path.isdir(d):
            continue
        for f in sorted(os.listdir(d)):
            if f == "README.md" or (f.startswith("FICHE") and f.endswith(".md")):
                yield os.path.join(d, f)


def main(req, maxi=60):
    ts = termes(req)
    motif = re.compile("|".join(re.escape(t) for t in ts))
    print(f"RAPPEL « {req} » -- termes : {', '.join(ts[:14])}{' ...' if len(ts) > 14 else ''}\n")
    cat = os.path.join(BRAIN, "corpus", "CATALOGUE_REFS.md")
    print("== Refs du catalogue ==")
    for ligne in open(cat, encoding="utf-8"):
        if ligne.startswith("|") and motif.search(norm(ligne)) and "---" not in ligne:
            print("  " + ligne.strip()[:230])
    print("\n== Passages (fichier : ligne) ==")
    total = 0
    scores = []
    for p in fichiers():
        if p == cat:
            continue
        try:
            lignes = open(p, encoding="utf-8").read().splitlines()
        except (UnicodeDecodeError, OSError):
            continue
        hits = [(i + 1, l) for i, l in enumerate(lignes) if motif.search(norm(l))]
        if hits:
            scores.append((len(hits), p, hits))
    for n, p, hits in sorted(scores, reverse=True):
        rel = os.path.relpath(p, ROOT)
        print(f"-- {rel} ({n})")
        for i, l in hits[:4]:
            print(f"   {i}: {l.strip()[:170]}")
            total += 1
        if total >= maxi:
            print("   ... (limite atteinte ; --max pour plus)")
            break


if __name__ == "__main__":
    args = sys.argv[1:]
    m = 60
    if "--max" in args:
        k = args.index("--max")
        m = int(args[k + 1])
        args = args[:k] + args[k + 2:]
    main(" ".join(args) or "coup charge", m)
