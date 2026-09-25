"""
Vues de JUGEMENT : des façons de mieux voir une pose ou un coup, tirées des
méthodes des animateurs (corpus/recherche/jugement_2026-09-25.md, vérifié
dans le texte d'*Illusion of Life* et d'*Animator's Survival Kit*).
Ce sont des aides pour regarder, pas des critères à cocher : aucun seuil
ici ne décide qu'une pose est « bonne ».

- `silhouette` : le perso en aplat noir sur blanc. Disney (Mickey noir sur
  noir) : « A hand in front of the chest would simply disappear » ; Walt :
  « Work in silhouette so that everything can be seen clearly ». Un bloc R6
  devant le torse s'y perd pareil.
- `hors_silhouette` : part de chaque membre qui dépasse du torse + tête,
  vue depuis une caméra donnée (0 = le membre se fond dans le tronc).
- `pelure` : pelure d'oignon (plusieurs images en fantômes) : l'espacement
  et les arcs deviennent visibles sur une seule image.
- `espacement` : déplacement par image d'un point (poing...) à l'écran :
  montre le contraste lent / rapide (Williams : « the slow against the
  fast »), ou son absence.
- `miroir` : l'image retournée casse l'habitude de regard (« a fresh pair
  of eyes »).
- `lire_kfseq` : échantillonne une KeyframeSequence exportée comme le
  moteur la joue (Linear : lerp + slerp) -> un monde par image.
"""
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", ".."))
import moon as M  # noqa: E402
from animator_brain import roblox_export as X  # noqa: E402

NOIR = {p: (0, 0, 0) for p in M.SIZES}


def lire_kfseq(path, fps=60, root=(np.eye(3), np.array([0.0, 3.0, 0.0]))):
    """[(frame, world)] par image, interpolation Linear (celle de nos exports)."""
    fr = X.read_kfseq(path)
    ts = [t for t, _ in fr]
    n = int(round(ts[-1] * fps)) + 1
    out = []
    for f in range(n):
        t = f / fps
        i = max(0, max(k for k, tt in enumerate(ts) if tt <= t + 1e-9))
        j = min(i + 1, len(fr) - 1)
        u = 0.0 if j == i else (t - ts[i]) / (ts[j] - ts[i])
        tr = {}
        for part in ("Torso",) + M.LIMBS:
            ra, pa = fr[i][1].get(part, (np.eye(3), np.zeros(3)))
            rb, pb = fr[j][1].get(part, (np.eye(3), np.zeros(3)))
            tr[part] = (X._slerp_rot(ra, rb, u), (1 - u) * pa + u * pb)
        out.append(X.solve(tr, root=root))
    return out


def _solo(w, parts):
    return {k: v for k, v in w.items() if k in parts}


def silhouette(worlds, eye, target, fov, size=(480, 270), titre=""):
    return M.render(worlds, eye, target, fov, size, title=titre, sky=(255, 255, 255), ground=False,
                    couleurs=NOIR, ombre=False, contour=None)


def _masque(w, parts, eye, target, fov, size):
    im = M.render([_solo(w, parts)], eye, target, fov, size, sky=(255, 255, 255), ground=False,
                  couleurs=NOIR, ombre=False, contour=None)
    return np.asarray(im.convert("L")) < 128


def hors_silhouette(w, eye, target, fov, size=(480, 270)):
    """{membre: part de son aire à l'écran HORS du tronc (torse + tête)} ;
    un membre invisible (derrière, hors champ) vaut None."""
    tronc = _masque(w, ("Torso", "Head"), eye, target, fov, size)
    out = {}
    for m in ("Right Arm", "Left Arm", "Right Leg", "Left Leg"):
        mk = _masque(w, (m,), eye, target, fov, size)
        a = mk.sum()
        out[m] = None if a < 20 else round(float((mk & ~tronc).sum() / a), 2)
    return out


def pelure(worlds, eye, target, fov, size=(480, 270), titre="", couleur=(214, 54, 46)):
    """Fantômes de plus en plus opaques ; la dernière image est pleine."""
    fond = Image.new("RGB", size, (255, 255, 255))
    n = len(worlds)
    for k, w in enumerate(worlds):
        im = M.render([w], eye, target, fov, size, sky=(255, 255, 255), ground=False,
                      couleurs={p: couleur for p in M.SIZES}, ombre=False, contour=None)
        mk = Image.fromarray(((np.asarray(im.convert("L")) < 250) * 255).astype(np.uint8))
        a = 0.18 + 0.82 * (k / max(1, n - 1)) ** 2
        teinte = Image.new("RGB", size, tuple(int(255 - (255 - c) * a) for c in couleur))
        fond.paste(teinte, (0, 0), mk)
        ImageDraw.Draw(fond)
    if titre:
        ImageDraw.Draw(fond).text((4, 2), titre, fill=(0, 0, 0))
    return fond


def projeter(p, eye, target, fov, size):
    W, H = size
    eye = np.asarray(eye, float); f = np.asarray(target, float) - eye; f /= np.linalg.norm(f)
    r = np.cross(f, [0, 1.0, 0]); r /= np.linalg.norm(r); u = np.cross(r, f)
    foc = (H / 2) / np.tan(np.radians(fov) / 2)
    v = np.asarray(p) - eye; z = max(v @ f, 1e-3)
    return np.array([W / 2 + foc * (v @ r) / z, H / 2 - foc * (v @ u) / z])


def espacement(worlds, part, cams, size=(480, 270)):
    """Pixels parcourus à l'écran par le bout de `part` entre deux images.
    cams : une caméra (eye, target, fov) par image, ou une seule pour toutes."""
    if not isinstance(cams, list):
        cams = [cams] * len(worlds)
    pts = [projeter(M.tip(w, part), *c, size) for w, c in zip(worlds, cams)]
    return [0.0] + [float(np.linalg.norm(b - a)) for a, b in zip(pts, pts[1:])]


def courbe(vals, largeur=480, hauteur=120, titre="", marques=()):
    im = Image.new("RGB", (largeur, hauteur), (255, 255, 255))
    d = ImageDraw.Draw(im)
    m = max(vals) or 1.0
    n = len(vals)
    for k, v in enumerate(vals):
        x = int(k * largeur / n); h = int((hauteur - 16) * v / m)
        d.rectangle([x, hauteur - h, x + max(1, largeur // n - 1), hauteur], fill=(40, 40, 40))
    for k, lab in marques:
        x = int(k * largeur / n); d.line([x, 12, x, hauteur], fill=(220, 60, 40)); d.text((x + 2, 12), lab, fill=(220, 60, 40))
    d.text((4, 1), f"{titre} (max {m:.0f} px/image)", fill=(0, 0, 0))
    return im


def miroir(im):
    return ImageOps.mirror(im)
