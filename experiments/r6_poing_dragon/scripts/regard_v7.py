"""
Regarder la v7 avec les vues de jugement des animateurs (outils/vues.py) :
silhouette, part de chaque membre hors du tronc, pelure d'oignon et
espacement du poing, dans la CAMÉRA DE JEU du lecteur (la seule que le
joueur verra à chaque fois) et de profil.

But : chercher des problèmes de lecture qu'aucune de nos vérifications ne
voyait (planches figées, poses isolées, vues choisies pour le croquis).
Usage : python3 regard_v7.py sortie.png
"""
import json
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "_shared", "animator_brain", "outils"))
import moon as M  # noqa: E402
import vues as V  # noqa: E402

OUT = os.path.join(HERE, "..", "output")
S = (480, 270)
# couleurs du lecteur (tenue de l'attaquant) : torse noir, peau, jambes sombres
TENUE = {"Torso": (28, 28, 30), "Head": (234, 184, 146), "Right Arm": (234, 184, 146),
         "Left Arm": (234, 184, 146), "Right Leg": (58, 58, 62), "Left Leg": (58, 58, 62)}


def cam_jeu(w):
    """Copie de placeCamera(camMode === "jeu") du lecteur."""
    a = w["Torso"][1]
    sx = 0.3 * a[0] + 1.75
    return (np.array([sx, max(4.5, a[1] + 1.8), a[2] + 10]), np.array([sx, a[1] + 0.2, a[2] - 4]), 70.0)


def cam_profil(w):
    a = w["Torso"][1]
    return (a + np.array([9.0, 0.6, -0.5]), a + np.array([0, -0.3, -0.5]), 40.0)


def cam_jeu_serre(w):
    """Même axe que la caméra de jeu, recadrée sur le perso (pour lire la pose
    elle-même ; la vignette réelle est à côté)."""
    e, t, _f = cam_jeu(w)
    return (e, t, 24.0)


def main(out):
    W = V.lire_kfseq(os.path.join(OUT, "dragon_attaquant.rbxmx"))
    st = json.load(open(os.path.join(OUT, "staging.json")))
    mk = st["markers"]
    moments = [("h1", mk["hit1"]), ("h4", mk["hit4"]), ("charge", 136), ("f146", 146), ("f149", 149),
               ("contact", mk["coup_charge"]), ("f153", 153), ("apres", 158)]
    rows, mesures = [], {}
    for nom, f in moments:
        w = W[f]
        cj, cs = cam_jeu(w), cam_jeu_serre(w)
        a = M.render([w], *cj, S, title=f"{nom} f{f} jeu (taille reelle)", couleurs=TENUE)
        b = M.render([w], *cs, S, title="jeu serre, tenue reelle", couleurs=TENUE, sky=(120, 130, 150))
        c = V.silhouette([w], *cs, S, titre="jeu serre : silhouette")
        d = V.silhouette([w], *cam_profil(w), S, titre="profil : silhouette")
        hs = V.hors_silhouette(w, *cs, S)
        mesures[nom] = {"frame": f, "hors_tronc_camera_jeu": hs}
        row = Image.new("RGB", (S[0] * 4, S[1] + 16), (255, 255, 255))
        for k, im in enumerate((a, b, c, d)):
            row.paste(im, (k * S[0], 0))
        txt = "  ".join(f"{m.split()[0][0]}{m.split()[1][0]}:{'-' if v is None else f'{v:.0%}'}" for m, v in hs.items())
        ImageDraw.Draw(row).text((4, S[1] + 2), f"part hors du tronc, camera de jeu (bras D/G, jambes D/G) : {txt}", fill=(0, 0, 0))
        rows.append(row)

    # pelure + espacement du poing sur la frappe (charge -> pose d'après)
    seq = list(range(140, 162, 2))
    pj = V.pelure([W[f] for f in seq], *cam_jeu_serre(W[150]), S, titre="pelure f140-160, camera de jeu (serree)")
    pp = V.pelure([W[f] for f in seq], *cam_profil(W[150]), S, titre="pelure f140-160, profil")
    fr = list(range(110, 175))
    poing = max(("Right Arm", "Left Arm"), key=lambda p: max(V.espacement([W[f] for f in fr], p, cam_profil(W[150]), S)))
    ej = V.espacement([W[f] for f in fr], poing, [cam_jeu(W[f]) for f in fr], S)
    ep = V.espacement([W[f] for f in fr], poing, cam_profil(W[150]), S)
    marques = [(136 - 110, "charge"), (150 - 110, "contact"), (158 - 110, "apres")]
    cj_ = V.courbe(ej, 480, 135, f"espacement {poing}, camera de jeu (taille reelle), f110-174", marques)
    cp_ = V.courbe(ep, 480, 135, f"espacement {poing}, profil, f110-174", marques)
    bas = Image.new("RGB", (S[0] * 4, S[1]), (255, 255, 255))
    bas.paste(pj, (0, 0)); bas.paste(pp, (S[0], 0)); bas.paste(cj_, (2 * S[0], 0)); bas.paste(cp_, (2 * S[0], 135))
    bas.paste(V.miroir(pp).resize((S[0], S[1])), (3 * S[0], 0))
    ImageDraw.Draw(bas).text((3 * S[0] + 4, 2), "profil en MIROIR (yeux neufs)", fill=(0, 0, 0))
    rows.append(bas)
    mesures["espacement_poing"] = {"poing": poing, "jeu_px": [round(x, 1) for x in ej], "profil_px": [round(x, 1) for x in ep]}

    H = sum(r.size[1] for r in rows)
    P = Image.new("RGB", (S[0] * 4, H), (255, 255, 255))
    y = 0
    for r in rows:
        P.paste(r, (0, y)); y += r.size[1]
    P.save(out)
    json.dump(mesures, open(os.path.splitext(out)[0] + ".json", "w"), indent=1, ensure_ascii=False)
    for k, v in mesures.items():
        if k != "espacement_poing":
            print(k, v)
    print("poing", poing, "jeu max", max(ej), "profil max", max(ep))


if __name__ == "__main__":
    main(sys.argv[1])
