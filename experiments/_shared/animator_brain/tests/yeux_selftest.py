"""
Cas connus des NOUVEAUX YEUX (chantier du 2026-09-26, SYNTHESE_YEUX rangs 1 à
7) : chaque outil est rejoué sur un cas dont on connaît la réponse AVANT de
lui faire confiance (« toute conversion passe par un cas où la réponse est
connue », SYNTHESE_YEUX piège 5).

- geo_pose.profondeur_ambigue : bras pointé sur l'objectif = ambigu ; le même
  bras vu de profil = pas ambigu ; bras croisé devant la poitrine vu de face =
  lisible, devant ; bras derrière le dos vu de face = lisible, derrière ;
  miroir sans recouvrement = ambigu ;
- moon.render(faces=True) : de face on voit F (rouge) au centre du torse, de
  dos B (bleu), de dessus U (cyan) ; la couleur par membre reste inchangée
  sans l'option ;
- impact : bras horizontal à hauteur de poitrine -> pente 0°, poing à
  y = +0,5 ; bras incliné de 20° vers le bas -> pente -20° ; pied qui glisse
  de 1 stud pendant un appui -> dérive 1,0 (définition B) ;
- carte_changements : deux fois le même export -> « rien » partout ; le poing
  droit monté de 0,4 stud au contact -> la phrase le dit, avec le chiffre ;
  la main gauche passée derrière le torse -> la phrase le dit ;
- cote_a_cote : deux vidéos synthétiques dont l'image blanche tombe à 1,0 s
  et à 1,5 s -> dans la sortie, les deux moitiés sont blanches à la MÊME
  image ; durée et son vérifiés par ffprobe ; le mode exports rend un mp4 ;
- questions_aveugle : même graine -> même ordre ; 5 à 8 questions, chaque
  extrait retrouvé mot pour mot ; prédiction inscrite ; refus d'une
  prédiction après un retour ; comparaison sans pourcentage ;
- planche_cles --faces : tourne et inscrit la profondeur par caméra.

Usage : python3 tests/yeux_selftest.py (sortie 1 si un cas échoue).
"""
import io
import json
import os
import subprocess
import sys
import tempfile
from contextlib import redirect_stdout

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
B = os.path.normpath(os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(B, "outils"))
sys.path.insert(0, os.path.normpath(os.path.join(B, "..")))
import geo_pose as G  # noqa: E402
import moon as M  # noqa: E402

ECHECS = []
DEPOT = os.path.normpath(os.path.join(B, "..", "..", ".."))
EXPORT = os.path.join(DEPOT, "experiments", "r6_un_seul_coup", "output")


def cas(nom, ok, detail=""):
    print(("OK    " if ok else "ÉCHEC ") + nom + (f" ({detail})" if detail else ""))
    if not ok:
        ECHECS.append(nom)


def t_profondeur():
    w = G.pose({"RA": (0, 0)})                            # bras droit tendu droit devant
    face = G.camera_orbite((0, 3, 0), 0, 0, 12)            # caméra devant le perso
    profil = G.camera_orbite((0, 3, 0), 90, 0, 12)         # à sa droite
    p = G.profondeur_ambigue(w, face)
    cas("profondeur : bras pointé sur l'objectif = ambigu", p["BD"]["lecture"] == "ambigu" and p["BD"]["axe_visee"] > 0.95,
        G.resume_profondeur(p))
    p = G.profondeur_ambigue(w, profil)
    cas("profondeur : le même bras de profil n'est pas ambigu", p["BD"]["lecture"] != "ambigu" and p["BD"]["axe_visee"] < 0.1,
        G.resume_profondeur(p))
    w = G.pose({"RA": (-60, 0)})                          # bras droit croisé devant la poitrine
    p = G.profondeur_ambigue(w, face)
    cas("profondeur : bras croisé devant la poitrine, de face = lisible, devant",
        p["BD"]["lecture"] == "lisible" and p["BD"]["ordre_3d"] == "devant", G.resume_profondeur(p))
    w = G.pose({"RA": (-120, 0)})                         # bras droit passé derrière le dos
    p = G.profondeur_ambigue(w, face)
    cas("profondeur : bras derrière le dos, de face = lisible, derrière",
        p["BD"]["lecture"] == "lisible" and p["BD"]["ordre_3d"] == "derrière", G.resume_profondeur(p))
    w = G.pose({"RA": (0, 0)})
    haut_ = G.camera_orbite((0, 3, 0), 90, 80, 12)        # bras tendu devant, vu de dessus-côté
    p = G.profondeur_ambigue(w, G.camera_orbite((0, 3, 0), 0, 0, 12))
    cas("profondeur : les seuils sont rendus avec le résultat", "_seuils" in p and "axe_visee" in p["_seuils"])
    w = G.pose({"RA": (90, 0)})                           # bras tendu sur le côté, vu de face
    p = G.profondeur_ambigue(w, face)
    cas("profondeur : bras sur le côté vu de face = à côté", p["BD"]["lecture"] == "à côté", G.resume_profondeur(p))
    del haut_


def _pixel(im, x, y):
    return np.array(im.getpixel((x, y)), float)


def t_faces():
    w = G.pose({})
    res = {}
    for nom, (az, el), attendu in (("F", (0, 0), (228, 49, 32)), ("B", (180, 0), (40, 80, 230)),
                                  ("U", (0, 89), (26, 197, 255))):
        cam = G.camera_orbite((0, 3.0, 0), az, el, 8, 40)
        im = M.render([w], cam[0], cam[1], cam[2], (200, 200), faces=True, ground=False, sky=(0, 0, 0))
        # un anneau autour du centre du torse (le centre porte la lettre)
        xs = [(100 + dx, 100 + dy) for dx, dy in ((-14, -14), (14, -14), (-14, 14), (14, 14))]
        if nom == "U":                                   # de dessus : le dessus de la TÊTE, hors de sa lettre
            px = np.mean([_pixel(im, 100 + dx, 100 + dy) for dx, dy in ((-22, -22), (22, -22), (-22, 22), (22, 22))], 0)
        else:
            px = np.mean([_pixel(im, *p) for p in xs], 0)
        d = np.abs(px - np.array(attendu)) / np.maximum(np.array(attendu), 30)
        res[nom] = px
        cas(f"faces : {nom} au centre vu de {'face' if nom == 'F' else 'dos' if nom == 'B' else 'dessus'}",
            np.argmax(px) == np.argmax(attendu) and float(np.max(d)) < 0.35, f"pixel {px.round()} attendu {attendu}")
    cam = G.camera_orbite((0, 3.0, 0), 0, 0, 8, 40)
    im = M.render([w], cam[0], cam[1], cam[2], (200, 200), ground=False, sky=(0, 0, 0))
    px = np.mean([_pixel(im, 100 + dx, 100 + dy) for dx, dy in ((-14, -14), (14, -14), (-14, 14), (14, 14))], 0)
    cas("faces : sans l'option, le torse garde sa couleur (rouge COL)", px[0] > px[1] and px[0] > px[2], f"{px.round()}")


def t_impact():
    import impact as I
    w0 = G.pose({"RA": (0, 0)})
    # victime : son torse face à l'attaquant, poing juste à sa poitrine (y +0,5)
    poing = G.bout(w0, "Right Arm")
    Rv = np.diag([-1.0, 1.0, -1.0])
    pv = poing + np.array([0.0, -0.5, -0.5])              # poing à y +0,5 du centre, sur la face avant
    V = [{"Torso": (Rv, pv)}]
    r = I.mesurer_contact([w0], V, 0, n_trajet=0)
    cas("impact : bras horizontal -> pente 0°", abs(r["pente_bras_deg"]) < 0.5, f"{r['pente_bras_deg']}")
    cas("impact : poing à y +0,5 -> écart à la poitrine 0", abs(r["ecart_a_la_poitrine"]) < 0.01,
        f"{r['poing_repere_victime']} écart {r['ecart_a_la_poitrine']}")
    w1 = G.pose({"RA": (0, -20)})
    r = I.mesurer_contact([w1], V, 0, n_trajet=0)
    cas("impact : bras incliné de 20° vers le bas -> pente -20°", abs(r["pente_bras_deg"] + 20) < 0.5, f"{r['pente_bras_deg']}")
    # trajet : le poing descend de 0,5 en 4 images en avançant de 0,5
    wa = G.pose({"RA": (0, 0), "hanche": 3.5, "z": 0.5})
    r = I.mesurer_contact([wa, wa, wa, wa, w0], V + V + V + V + V, 4, n_trajet=4)
    cas("impact : trajet qui descend en avançant -> pente du trajet -45°", abs(r["pente_trajet_deg"] + 45) < 1,
        f"{r['pente_trajet_deg']}")
    # pieds : un pied planté qui glisse de 1 stud
    mondes = []
    for f in range(60):
        dx = 0.0 if f < 20 else min(1.0, (f - 20) / 20)
        mondes.append(G.pose({"x": dx}))
    g = I.glissement_coin(mondes)
    cas("impact : pied planté qui glisse de 1 stud -> dérive 1,0 (définition B)",
        abs(g["Right Leg"]["pire_derive_studs"] - 1.0) < 0.02, f"{g['Right Leg']['pire_derive_studs']}")
    a = I.glissement_audit(mondes)
    cas("impact : la définition A (audit.contact_report) tourne et rend ses appuis", "Right Leg" in a and "runs" in a["Right Leg"],
        f"A : {a['Right Leg']['contacts']} appui(s), pire {a['Right Leg']['worst_skate_studs']}")


def t_carte():
    import carte_changements as C
    n = 40
    marq = {"charge": 0, "frappe": 20, "contact": 30}

    def version(mod=None, centre=15):
        m = []
        for f in range(n):
            lac = -40 + 40 / (1 + np.exp(-(f - centre) / 1.5))   # le buste se dévisse autour de l'image `centre`
            p = {"buste": (lac, 0, 0), "RA": (0, -30 + f), "LA": (-20, -60)}
            if mod:
                p = mod(f, p)
            m.append(G.pose(p))
        return {"nom": "x", "mondes": m, "marqueurs": dict(marq), "contact": 30, "staging": None}
    a = version()
    r = C.comparer(a, version())
    tout_rien = all(ph["phrases"][0].startswith("rien") for ph in r["phases"])
    cas("carte : deux fois la même version -> rien partout", tout_rien, "; ".join(ph["phrases"][0] for ph in r["phases"]))

    def monte(f, p):                                    # au contact, le bras droit remonte
        if f == 30:
            p = dict(p, RA=(0, 0 + 12))
        return p
    r = C.comparer(a, version(monte))
    ph = next(p for p in r["phases"] if p["phase"] == "au contact")
    dz = ph["ecarts"]["RA_haut"]["pire"]
    cas("carte : poing droit plus haut au contact -> la phrase le dit, avec le chiffre",
        any("poing droit" in t and "plus haut" in t for t in ph["phrases"]) and dz > 0.25,
        f"{ph['phrases'][:2]} ; écart {dz}")

    def derriere(f, p):                                 # la main gauche passe derrière le torse
        return dict(p, LA=(-150, -40))
    r = C.comparer(a, version(derriere))
    ph = next(p for p in r["phases"] if p["phase"] == "charge")
    cas("carte : bras gauche qui passe derrière le torse -> la phrase le dit",
        any("bras gauche" in t and "derrière le torse dans B" in t for t in ph["phrases"]), f"{ph['phrases'][:1]}")

    r = C.comparer(a, version(centre=9))                # mêmes poses, le buste se dévisse 6 images plus tôt
    ph = next(p for p in r["phases"] if p["phase"] == "charge")
    cas("carte : buste qui tourne plus tôt -> « plus tôt » en images", any("buste tourne" in t and "plus tôt" in t
                                                                           for t in ph["phrases"]), f"{ph['phrases'][:3]}")


def _video_flash(chemin, t_blanc, duree=3.0, fps=30, frequence=440):
    d = tempfile.mkdtemp(prefix="flash_")
    for k in range(int(duree * fps)):
        c = 255 if k == int(round(t_blanc * fps)) else 20
        Image.new("RGB", (160, 90), (c, c, c)).save(os.path.join(d, f"f{k:04d}.png"))
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", str(fps), "-i", os.path.join(d, "f%04d.png"),
                    "-f", "lavfi", "-i", f"sine=frequency={frequence}:duration={duree}", "-shortest",
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "10", "-c:a", "aac", chemin], check=True)


def _moyennes_moities(mp4):
    out = subprocess.run(["ffmpeg", "-v", "error", "-i", mp4, "-f", "rawvideo", "-pix_fmt", "gray", "-"],
                         capture_output=True, check=True).stdout
    import cote_a_cote as CA
    s = CA.sonde(mp4)
    W, H = s["largeur"], s["hauteur"]
    fr = np.frombuffer(out, np.uint8).reshape(-1, H, W)
    g = fr[:, 40:H - 40, : W // 2].reshape(len(fr), -1).mean(1)
    d = fr[:, 40:H - 40, W // 2:].reshape(len(fr), -1).mean(1)
    return g, d, s


def t_cote_a_cote(tmp):
    import cote_a_cote as CA
    a, b = os.path.join(tmp, "a.mp4"), os.path.join(tmp, "b.mp4")
    _video_flash(a, 1.0, frequence=440)
    _video_flash(b, 1.5, frequence=660)
    out = os.path.join(tmp, "ab.mp4")
    r = CA.videos([(a, 1.0), (b, 1.5)], out, avant=0.8, apres=1.0, hauteur=90)
    g, d, s = _moyennes_moities(out)
    ig, id_ = int(np.argmax(g)), int(np.argmax(d))
    cas("côte à côte : les deux images blanches tombent à la même image de sortie", ig == id_ == r["image_contact_sortie"],
        f"gauche i{ig}, droite i{id_}, contact attendu i{r['image_contact_sortie']}")
    cas("côte à côte : durée = avant + après, cadence d'origine, son présent (ffprobe)",
        abs(s["duree"] - 1.8) < 0.07 and abs(s["fps"] - 30) < 0.01 and s["son"], f"{s}")
    try:
        CA.videos([(a, 0.2), (b, 1.5)], os.path.join(tmp, "x.mp4"), avant=0.8, apres=1.0)
        cas("côte à côte : une fenêtre qui sort de la vidéo est refusée", False)
    except ValueError:
        cas("côte à côte : une fenêtre qui sort de la vidéo est refusée", True)
    att = os.path.join(EXPORT, "usc_attaquant.rbxmx")
    if os.path.exists(att):
        spec = (f"v=" + att + "," + os.path.join(EXPORT, "usc_victime.rbxmx") + "," + os.path.join(EXPORT, "staging.json")
                + "," + os.path.join(EXPORT, "scene.json"))
        o2 = os.path.join(tmp, "exp.mp4")
        r = CA.exports([spec, spec], o2, avant=0.1, apres=0.1, fps=30, taille=(160, 90))
        cas("côte à côte (exports) : mp4 rendu, 2 versions x 2 caméras, profondeur au contact inscrite",
            r["sortie"]["largeur"] == 320 and r["sortie"]["hauteur"] == 180 and "v" in r["profondeur_au_contact"],
            f"{r['images']} images, {r['sortie']['largeur']}x{r['sortie']['hauteur']}")
    else:
        cas("côte à côte (exports) : export d'Un seul coup absent, cas sauté", True, "sauté")


def t_aveugle(tmp):
    import questions_aveugle as Q
    a, b = os.path.join(tmp, "va.txt"), os.path.join(tmp, "vb.txt")
    open(a, "w").write("version a")
    open(b, "w").write("version b")
    r1 = Q.preparer(a, b, os.path.join(tmp, "p1"), "va", "vb", graine=7)
    r2 = Q.preparer(a, b, os.path.join(tmp, "p2"), "va", "vb", graine=7)
    c1 = json.load(open(os.path.join(tmp, "p1", ".cle.json")))
    c2 = json.load(open(os.path.join(tmp, "p2", ".cle.json")))
    cas("aveugle : même graine -> même ordre", c1["A"] == c2["A"] and c1["graine"] == 7, f"A = {c1['A']}")
    ordres = set()
    for g in range(12):
        Q.preparer(a, b, os.path.join(tmp, f"g{g}"), "va", "vb", graine=g)
        ordres.add(json.load(open(os.path.join(tmp, f"g{g}", ".cle.json")))["A"])
    cas("aveugle : l'ordre change selon la graine", ordres == {"va", "vb"}, f"{ordres}")
    contenu_A = open(os.path.join(tmp, "p1", "A.txt")).read()
    cas("aveugle : le fichier A est bien la version annoncée par la clé", contenu_A == f"version {c1['A'][1]}")
    qs = json.load(open(os.path.join(tmp, "p1", "questions.json")))["questions"]
    ok, ret = Q.questions_verifiees()
    cas("aveugle : 5 à 8 questions, extraits retrouvés mot pour mot", 5 <= len(qs) <= 8 and not ret, f"{len(qs)} ; retirées {ret}")
    faux = [dict(Q.QUESTIONS[0], id="qx", extrait="phrase que Milan n'a jamais écrite")]
    ok2, ret2 = Q.questions_verifiees(faux)
    cas("aveugle : un extrait introuvable retire la question (pas de reformulation)", not ok2 and len(ret2) == 1)
    journal = os.path.join(tmp, "predictions.jsonl")
    rep = json.load(open(os.path.join(tmp, "p1", "reponses.json")))
    rep["reponses"]["q1"] = {"A": "non", "B": "non", "vu": "poing à plat dans les deux"}
    rep["preference"], rep["confiance"] = "B", 0.6
    json.dump(rep, open(os.path.join(tmp, "p1", "reponses.json"), "w"))
    Q.predire(os.path.join(tmp, "p1"), journal=journal, qui="test")
    lignes = [json.loads(l) for l in open(journal)]
    cas("aveugle : prédiction inscrite avec graine et ordre", lignes[-1]["type"] == "prediction" and lignes[-1]["graine"] == 7)
    buf = io.StringIO()
    with redirect_stdout(buf):
        Q.imprimer_comparaison(Q.comparer(os.path.join(tmp, "p1"), milan_texte="le bras part vers le bas", journal=journal))
    s = buf.getvalue()
    cas("aveugle : comparaison sans pourcentage ni score, mots retrouvés", "%" not in s and "bas" in s, s.splitlines()[0])
    try:
        Q.predire(os.path.join(tmp, "p1"), journal=journal)
        cas("aveugle : prédiction refusée après un retour", False)
    except SystemExit:
        cas("aveugle : prédiction refusée après un retour", True)


def t_planche(tmp):
    att = os.path.join(EXPORT, "usc_attaquant.rbxmx")
    if not os.path.exists(att):
        cas("planche --faces : export absent, cas sauté", True, "sauté")
        return
    out, js = os.path.join(tmp, "pl.png"), os.path.join(tmp, "pl.json")
    p = subprocess.run([sys.executable, os.path.join(B, "outils", "planche_cles.py"), "--rbxmx", att, "--sortie", out,
                        "--json", js, "--max", "4", "--faces"], capture_output=True, text=True)
    d = json.load(open(js)) if os.path.exists(js) else {}
    avec = [c for c in d.get("cles", []) if "profondeur" in c]
    cas("planche --faces : rendue, profondeur par caméra inscrite pour les clés dessinées",
        p.returncode == 0 and os.path.exists(out) and len(avec) == 4 and set(avec[0]["profondeur"]) == {"3/4 face", "profil"},
        p.stderr[-200:] if p.returncode else f"{len(avec)} clés")


def main():
    tmp = tempfile.mkdtemp(prefix="yeux_")
    for t in (t_profondeur, t_faces, t_impact, t_carte, lambda: t_cote_a_cote(tmp), lambda: t_aveugle(tmp),
              lambda: t_planche(tmp)):
        try:
            t()
        except Exception as e:                            # un outil qui plante est un échec, pas un arrêt
            import traceback
            traceback.print_exc()
            cas(f"{getattr(t, '__name__', 'cas')} a planté", False, repr(e))
    print(f"\n{'TOUT OK' if not ECHECS else str(len(ECHECS)) + ' ÉCHEC(S) : ' + ', '.join(ECHECS)}")
    sys.exit(1 if ECHECS else 0)


if __name__ == "__main__":
    main()
