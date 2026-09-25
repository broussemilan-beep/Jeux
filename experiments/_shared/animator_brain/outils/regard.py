"""
Outils de REGARD : voir une animation comme la voit quelqu'un qui la regarde à
vitesse réelle, et non comme des images figées agrandies.

Problème à l'origine (retour de Milan sur la v7 : « je vois aucun
changement ») : je vérifiais les poses sur des planches figées, agrandies,
hors du cadrage réel. Ce qui se voit à la lecture n'est pas ça.

- `persistance` : moyenne pondérée des images sur ~80-100 ms (ordre de grandeur
  de la persistance rétinienne / du flou de mouvement perçu). Une pose tenue
  reste nette ; une pose montrée 1-2 images devient un voile. C'est une
  APPROXIMATION de ce que l'œil retient, pas un modèle de la vision.
- `bande_vitesse` : une vignette par ~83 ms (12/s) de ces images persistantes,
  à petite taille (comme un écran de téléphone) : si le coup ne se lit pas
  sur cette bande, il ne se lira pas en jeu.
- `vignette` : réduction à la taille d'un perso vu en jeu (test de la vignette
  des animateurs : une pose forte se lit en tout petit).
Usage : python3 regard.py <dossier_images f%04d.png> <fps> <sortie.png> [debut fin]
"""
import glob
import os
import sys

import numpy as np
from PIL import Image, ImageDraw


def charger(dossier, debut=0, fin=None):
    fs = sorted(glob.glob(os.path.join(dossier, "*.png")))[debut:fin]
    return [np.asarray(Image.open(f).convert("RGB"), dtype=np.float32) for f in fs]


def persistance(images, fps, fenetre_ms=90.0):
    """Image perçue à chaque instant : moyenne à décroissance exponentielle
    sur ~fenetre_ms (la plus récente pèse le plus)."""
    n = max(1, int(round(fenetre_ms / 1000.0 * fps)))
    tau = n / 2.0
    out = []
    for i in range(len(images)):
        acc, wsum = 0.0, 0.0
        for k in range(n):
            j = i - k
            if j < 0:
                break
            w = np.exp(-k / tau)
            acc = acc + w * images[j]
            wsum += w
        out.append(acc / wsum)
    return out


def bande_vitesse(images, fps, sortie, par_s=12, largeur=200, titre=""):
    per = persistance(images, fps)
    pas = max(1, int(round(fps / par_s)))
    choix = list(range(0, len(per), pas))
    h = int(largeur * per[0].shape[0] / per[0].shape[1])
    cols = 12
    rows = (len(choix) + cols - 1) // cols
    S = Image.new("RGB", (cols * largeur, rows * h + 18), (255, 255, 255))
    d = ImageDraw.Draw(S)
    d.text((4, 3), f"{titre}  (ce que l'oeil retient, {par_s} vignettes/s, {largeur}px)", fill=(0, 0, 0))
    for k, i in enumerate(choix):
        im = Image.fromarray(np.clip(per[i], 0, 255).astype(np.uint8)).resize((largeur, h))
        S.paste(im, ((k % cols) * largeur, 18 + (k // cols) * h))
        d.text(((k % cols) * largeur + 3, 18 + (k // cols) * h + 2), f"{i / fps:.2f}", fill=(255, 255, 0))
    S.save(sortie)
    return sortie


def netete(images, fps):
    """Pour chaque instant : écart entre l'image vue et l'image persistante.
    Faible = la pose est tenue assez longtemps pour être VUE ; fort = elle
    passe sans être retenue. Renvoie une liste (0 = parfaitement vue)."""
    per = persistance(images, fps)
    return [float(np.mean(np.abs(a - b))) for a, b in zip(images, per)]


if __name__ == "__main__":
    dossier, fps, sortie = sys.argv[1], float(sys.argv[2]), sys.argv[3]
    a = int(sys.argv[4]) if len(sys.argv) > 4 else 0
    b = int(sys.argv[5]) if len(sys.argv) > 5 else None
    ims = charger(dossier, a, b)
    bande_vitesse(ims, fps, sortie, titre=os.path.basename(dossier.rstrip("/")))
    nt = netete(ims, fps)
    vues = sum(1 for x in nt if x < 4.0) / max(1, len(nt))
    print(f"part du temps où l'image est « vue » (écart < 4) : {vues:.0%}")
