"""
ÉVALUATION À L'AVEUGLE : deux versions A / B dans un ordre tiré au sort, des
questions oui/non tirées des mots EXACTS de Milan, des prédictions écrites
AVANT son retour, puis comparées à ce qu'il dit.

Pourquoi il existe (2026-09-26, chantier « nouveaux yeux », SYNTHESE_YEUX
rang 2) : mes prédictions sont trop hautes de +0,3 en moyenne (critic.py,
notes_milan.jsonl). Quand je juge en SACHANT quelle version est la nouvelle,
le biais revient. Aucun dépôt étudié ne corrige ça par un juge automatique ;
ce qui aide : des questions fermées et observables, un répondant qui ne sait
pas quelle version est la nouvelle (un sous-agent), et des prédictions
enregistrées avant, qu'on peut démentir après.

Ce qu'il fait :
- `preparer` : copie les deux fichiers sous des noms neutres (A, B ; vidéos
  sans métadonnées), dans un ordre tiré au sort avec une GRAINE notée ;
  écrit `questions.json` (5 à 8 questions, chacune avec l'extrait EXACT de
  Milan qui l'a fait naître, sa date et son sha1, vérifié mot pour mot dans
  `corpus/milan_verbatim.jsonl` au moment de préparer ; une question dont
  l'extrait ne se retrouve pas est retirée, pas reformulée), un fichier de
  réponses à remplir, et `.cle.json` (l'ordre réel : à ne pas ouvrir par le
  répondant) ;
- `predire` : enregistre les réponses (et la préférence A/B, la note prédite
  si on en a une) dans `corpus/predictions_aveugle.jsonl`, AVANT tout retour
  de Milan sur ce paquet (refusé si un retour est déjà inscrit) ;
- `comparer` : après le retour, remet chaque réponse en face des mots de
  Milan (texte ou sha1 d'un message de milan_verbatim) : les mots des
  questions retrouvés dans son message, et c'est tout. Pas de pourcentage,
  pas de score : dire si une prédiction est démentie reste une lecture
  humaine, inscrite à part (`--lecture q1=juste,q2=dementi,q3=muet`).

Ce qu'il NE voit PAS : si les questions sont les bonnes (elles viennent de
retours passés ; Milan peut juger sur autre chose) ; si Milan a répondu à la
question (il répond rarement point par point : « muet » est une issue
normale) ; le répondant peut deviner l'ordre si la nouvelle version se
reconnaît (même aveugle, ce n'est pas une garantie) ; les mots-clés
retrouvés ne disent pas le sens (une négation échappe).

Usage :
  python3 outils/questions_aveugle.py preparer --a v5.mp4 --b v6.mp4 --nom-a v5 --nom-b v6 --paquet <dossier> [--graine 1234]
  (le répondant aveugle lit <dossier>/questions.json, regarde A et B, remplit <dossier>/reponses.json)
  python3 outils/questions_aveugle.py predire --paquet <dossier> [--reponses <fichier>] [--qui "sous-agent aveugle"]
  python3 outils/questions_aveugle.py comparer --paquet <id ou dossier> (--milan-texte "..." | --milan-sha1 <sha1>) [--lecture q1=juste,...]
  option commune : --journal <fichier.jsonl> (défaut corpus/predictions_aveugle.jsonl)
"""
import argparse
import datetime
import hashlib
import json
import os
import random
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import motifs as MO  # noqa: E402

B = os.path.normpath(os.path.join(HERE, ".."))
JOURNAL = os.path.join(B, "corpus", "predictions_aveugle.jsonl")

# Questions : observables, oui/non, chacune née d'un message exact de Milan.
# portee « chaque » = une réponse pour A et une pour B ; « paire » = une seule.
QUESTIONS = [
    {"id": "q1", "motif": "vers_le_bas", "sha1": "2c8d5a6a64c1853c",
     "extrait": "le perso frappait vers le bas",
     "question": "Au contact, le coup part-il vers le bas (le poing arrive d'en haut sur la victime) ?",
     "portee": "chaque", "comment": "regard à vitesse réelle au cadrage réel ; mesure à côté : outils/impact.py (pente du bras et du trajet)",
     "cadrage": "ciné (caméra du plan) et jeu", "mots": ["bas", "vers le bas", "descend"]},
    {"id": "q2", "motif": "poing_charge", "sha1": "bbef1dc35f95e2c0",
     "extrait": "dans aucune le bras est tendu derrière",
     "question": "Pendant la charge, le bras qui va frapper est-il tendu derrière le corps ?",
     "portee": "chaque", "comment": "regard à vitesse réelle ; mesure : geo_pose (bras.RA.torse az proche de 180)",
     "cadrage": "ciné", "mots": ["tendu", "derriere", "arriere"]},
    {"id": "q3", "motif": "que_les_bras", "sha1": "bbef1dc35f95e2c0",
     "extrait": "arrière qui est engager par le juste tourne",
     "question": "Le recul de la charge vient-il du buste qui tourne (et pas du bras seul) ?",
     "portee": "chaque", "comment": "regard à vitesse réelle ; mesure : geo_pose buste.lacet pendant la charge",
     "cadrage": "ciné", "mots": ["buste", "bust", "tourne", "corps"]},
    {"id": "q4", "motif": "jambes", "sha1": "bbef1dc35f95e2c0",
     "extrait": "le pose des jambe est un peu  trop abusé",
     "question": "La pose des jambes est-elle trop abusée (trop écartées, trop pliées) ?",
     "portee": "chaque", "comment": "regard ; mesure : geo_pose pieds et hanche",
     "cadrage": "ciné", "mots": ["jambe", "abuse", "pied"]},
    {"id": "q5", "motif": "mecanique", "sha1": "2cba2eeeacb56e1e",
     "extrait": "pq tout à l’aire mécanique dans tes rendues",
     "question": "Le mouvement a-t-il l'air mécanique (tout part et s'arrête ensemble, sans souplesse) ?",
     "portee": "chaque", "comment": "regard à vitesse réelle seulement",
     "cadrage": "ciné et jeu", "mots": ["mecanique", "smooth", "fluide", "robot"]},
    {"id": "q6", "motif": "poing_charge", "sha1": "fe52222a372389e9",
     "extrait": "il donne pas le give d’un coup chargé",
     "question": "Le coup se lit-il comme un coup CHARGÉ (une tenue qui accumule, puis une détente) ?",
     "portee": "chaque", "comment": "regard à vitesse réelle avec le son",
     "cadrage": "ciné", "mots": ["charge", "give", "puissan"]},
    {"id": "q7", "motif": "aucun_changement", "sha1": "d02679fb1213aa4e",
     "extrait": "Je vois aucun changement",
     "question": "À vitesse réelle, voit-on une différence entre A et B sans chercher ?",
     "portee": "paire", "comment": "regard à vitesse réelle, A et B côte à côte (outils/cote_a_cote.py)",
     "cadrage": "ciné", "mots": ["changement", "dif", "pareil", "meme"]},
    {"id": "q8", "motif": None, "sha1": "5122b639e93ab2d9",
     "extrait": "c le placement du bras sur tout",
     "question": "Le placement du bras qui frappe diffère-t-il visiblement entre A et B (pendant la charge et au départ du coup) ?",
     "portee": "paire", "comment": "regard ; mesure : outils/carte_changements.py (bras devant / derrière le torse)",
     "cadrage": "ciné", "mots": ["placement", "bras"]},
]

CONSIGNE = ("Tu réponds À L'AVEUGLE : tu ne sais pas laquelle de A ou B est la version la plus récente, ne cherche "
            "pas à le deviner et n'ouvre pas .cle.json. Regarde A et B à vitesse réelle, avec le son, au cadrage "
            "donné. Pour chaque question : « oui », « non » ou « ? » (on ne voit pas), et une phrase en mots de "
            "corps sur ce que tu as vu. Puis : préférence A ou B (ou « aucune ») et ta confiance (0 à 1). Pas de note.")


def _sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def questions_verifiees(questions=None):
    """Garde les questions dont l'extrait est MOT POUR MOT dans le message
    (sha1) de milan_verbatim (normalisation de motifs.py : casse, accents,
    apostrophes) ; -> (gardées, retirées)."""
    vb = MO.verbatim_par_sha()
    ok, retirees = [], []
    for q in (questions or QUESTIONS):
        e = vb.get(q["sha1"])
        texte = (e or {}).get("texte") or ""
        if e and MO.norm(q["extrait"]) in MO.norm(texte):
            q = dict(q, date=e.get("date"))
            ok.append(q)
        else:
            retirees.append({"id": q["id"], "raison": "extrait introuvable mot pour mot dans milan_verbatim"})
    return ok, retirees


def _copier(src, dst):
    if src.lower().endswith((".mp4", ".mov", ".mkv", ".webm")):
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-map", "0", "-map_metadata", "-1", "-c", "copy",
                        dst], check=True)
    else:
        shutil.copyfile(src, dst)


def preparer(a, b, paquet, nom_a="a", nom_b="b", graine=None, moment=""):
    graine = int.from_bytes(os.urandom(4), "big") if graine is None else int(graine)
    inverse = random.Random(graine).random() < 0.5
    os.makedirs(paquet, exist_ok=True)
    ext_a, ext_b = os.path.splitext(a)[1], os.path.splitext(b)[1]
    ordre = [(b, nom_b, ext_b), (a, nom_a, ext_a)] if inverse else [(a, nom_a, ext_a), (b, nom_b, ext_b)]
    for lettre, (src, _n, ext) in zip("AB", ordre):
        _copier(src, os.path.join(paquet, lettre + ext))
    qs, retirees = questions_verifiees()
    date = datetime.date.today().isoformat()
    pid = f"{date}-{nom_a}-{nom_b}-{graine}"
    json.dump({"paquet": pid, "moment": moment, "consigne": CONSIGNE,
               "fichiers": {"A": "A" + ordre[0][2], "B": "B" + ordre[1][2]},
               "questions": [{k: q[k] for k in ("id", "question", "portee", "comment", "cadrage", "extrait", "date", "sha1")}
                             for q in qs], "questions_retirees": retirees},
              open(os.path.join(paquet, "questions.json"), "w"), ensure_ascii=False, indent=1)
    gabarit = {"paquet": pid, "reponses": {q["id"]: ({"A": "", "B": "", "vu": ""} if q["portee"] == "chaque"
                                                     else {"reponse": "", "vu": ""}) for q in qs},
               "preference": "", "confiance": None, "note_predite": None}
    json.dump(gabarit, open(os.path.join(paquet, "reponses.json"), "w"), ensure_ascii=False, indent=1)
    cle = {"paquet": pid, "graine": graine, "A": ordre[0][1], "B": ordre[1][1],
           "sources": {ordre[0][1]: {"fichier": ordre[0][0], "sha256": _sha256(ordre[0][0])},
                       ordre[1][1]: {"fichier": ordre[1][0], "sha256": _sha256(ordre[1][0])}}}
    json.dump(cle, open(os.path.join(paquet, ".cle.json"), "w"), ensure_ascii=False, indent=1)
    return {"paquet": pid, "dossier": paquet, "graine": graine, "questions": len(qs), "retirees": retirees}


def _journal(chemin):
    return MO.lire_jsonl(chemin)


def predire(paquet, reponses=None, qui="", journal=JOURNAL):
    cle = json.load(open(os.path.join(paquet, ".cle.json")))
    qs = json.load(open(os.path.join(paquet, "questions.json")))
    rep = json.load(open(reponses or os.path.join(paquet, "reponses.json")))
    pid = cle["paquet"]
    lignes = _journal(journal)
    if any(l.get("paquet") == pid and l.get("type") == "retour" for l in lignes):
        raise SystemExit(f"refusé : un retour de Milan est déjà inscrit pour {pid} ; une prédiction se fait AVANT.")
    vides = [k for k, v in rep["reponses"].items() if not any(str(x).strip() for kk, x in v.items() if kk != "vu")]
    ligne = {"type": "prediction", "date": datetime.datetime.now().isoformat(timespec="seconds"), "paquet": pid,
             "graine": cle["graine"], "ordre": {"A": cle["A"], "B": cle["B"]}, "sources": cle["sources"],
             "qui": qui, "questions": [{"id": q["id"], "question": q["question"], "sha1": q["sha1"],
                                         "extrait": q["extrait"]} for q in qs["questions"]],
             "reponses": rep["reponses"], "preference": rep.get("preference"), "confiance": rep.get("confiance"),
             "note_predite": rep.get("note_predite"), "questions_sans_reponse": vides}
    os.makedirs(os.path.dirname(os.path.abspath(journal)), exist_ok=True)
    with open(journal, "a", encoding="utf-8") as f:
        f.write(json.dumps(ligne, ensure_ascii=False) + "\n")
    return {"paquet": pid, "inscrit_dans": journal, "sans_reponse": vides}


def comparer(paquet, milan_texte=None, milan_sha1=None, lecture=None, journal=JOURNAL, inscrire=True):
    pid = paquet
    if os.path.isdir(paquet):
        pid = json.load(open(os.path.join(paquet, ".cle.json")))["paquet"]
    lignes = [l for l in _journal(journal) if l.get("paquet") == pid]
    preds = [l for l in lignes if l.get("type") == "prediction"]
    if not preds:
        raise SystemExit(f"aucune prédiction inscrite pour {pid} : rien à comparer (une prédiction se fait avant).")
    p = preds[-1]
    if milan_sha1:
        e = MO.verbatim_par_sha().get(milan_sha1)
        if not e:
            raise SystemExit(f"sha1 {milan_sha1} absent de milan_verbatim")
        milan_texte = e.get("texte") or ""
    txt = MO.norm(milan_texte or "")
    par_id = {q["id"]: q for q in QUESTIONS}
    sortie = []
    for q in p["questions"]:
        r = p["reponses"].get(q["id"], {})
        if "reponse" in r:
            pr = f"paire : {r.get('reponse') or '(vide)'}"
        else:
            pr = f"{p['ordre']['A']} : {r.get('A') or '(vide)'} ; {p['ordre']['B']} : {r.get('B') or '(vide)'}"
        mots = [m for m in par_id.get(q["id"], {}).get("mots", []) if MO.norm(m) in txt]
        sortie.append({"id": q["id"], "question": q["question"], "prediction": pr, "vu": r.get("vu", ""),
                       "mots_de_la_question_dans_son_message": mots})
    pref = p.get("preference")
    pref_v = p["ordre"].get(pref, pref) if pref in ("A", "B") else pref
    res = {"paquet": pid, "ordre_revele": p["ordre"], "graine": p["graine"], "questions": sortie,
           "preference_predite": pref_v, "confiance": p.get("confiance"), "note_predite": p.get("note_predite"),
           "mots_de_milan": milan_texte, "lecture_humaine": lecture or {}}
    if inscrire:
        with open(journal, "a", encoding="utf-8") as f:
            f.write(json.dumps({"type": "retour", "date": datetime.datetime.now().isoformat(timespec="seconds"),
                                "paquet": pid, "milan_sha1": milan_sha1, "mots_de_milan": milan_texte,
                                "lecture_humaine": lecture or {}}, ensure_ascii=False) + "\n")
    return res


def imprimer_comparaison(r):
    print(f"=== {r['paquet']} ; ordre révélé : A = {r['ordre_revele']['A']}, B = {r['ordre_revele']['B']} "
          f"(graine {r['graine']})")
    print(f"mots de Milan : « {r['mots_de_milan']} »")
    for q in r["questions"]:
        print(f"- {q['id']} {q['question']}\n    prédit : {q['prediction']}" + (f" ; vu : {q['vu']}" if q["vu"] else ""))
        m = q["mots_de_la_question_dans_son_message"]
        print("    dans son message : " + (", ".join(m) if m else "rien de cette question (muet ?)")
              + (f" ; lecture humaine : {r['lecture_humaine'][q['id']]}" if q["id"] in r["lecture_humaine"] else ""))
    print(f"préférence prédite : {r['preference_predite']} (confiance {r['confiance']}) ; note prédite : {r['note_predite']}")
    print("Pas de score : une prédiction est « démentie » ou « juste » seulement par une lecture humaine (--lecture).")


def main():
    ap = argparse.ArgumentParser(description="évaluation à l'aveugle (questions oui/non tirées des mots de Milan)")
    sp = ap.add_subparsers(dest="cmd", required=True)
    p1 = sp.add_parser("preparer")
    p1.add_argument("--a", required=True)
    p1.add_argument("--b", required=True)
    p1.add_argument("--nom-a", default="a")
    p1.add_argument("--nom-b", default="b")
    p1.add_argument("--paquet", required=True)
    p1.add_argument("--graine", type=int)
    p1.add_argument("--moment", default="")
    p2 = sp.add_parser("predire")
    p2.add_argument("--paquet", required=True)
    p2.add_argument("--reponses")
    p2.add_argument("--qui", default="")
    p3 = sp.add_parser("comparer")
    p3.add_argument("--paquet", required=True)
    p3.add_argument("--milan-texte")
    p3.add_argument("--milan-sha1")
    p3.add_argument("--lecture", default="", help="q1=juste,q2=dementi,q3=muet (lecture humaine)")
    p4 = sp.add_parser("questions", help="affiche les questions et vérifie leurs extraits")
    for p in (p1, p2, p3, p4):
        p.add_argument("--journal", default=JOURNAL)
    a = ap.parse_args()
    if a.cmd == "preparer":
        print(json.dumps(preparer(a.a, a.b, a.paquet, a.nom_a, a.nom_b, a.graine, a.moment), ensure_ascii=False, indent=1))
    elif a.cmd == "predire":
        print(json.dumps(predire(a.paquet, a.reponses, a.qui, a.journal), ensure_ascii=False, indent=1))
    elif a.cmd == "comparer":
        lect = dict(x.split("=", 1) for x in a.lecture.split(",") if "=" in x)
        imprimer_comparaison(comparer(a.paquet, a.milan_texte, a.milan_sha1, lect, a.journal))
    else:
        ok, ret = questions_verifiees()
        for q in ok:
            print(f"{q['id']} [{q['portee']}] {q['question']}\n    « {q['extrait']} » ({q['date'][:10]}, {q['sha1']})")
        for r in ret:
            print(f"RETIRÉE {r['id']} : {r['raison']}")


if __name__ == "__main__":
    main()
