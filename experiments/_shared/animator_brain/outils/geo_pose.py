"""
GÉOMÉTRIE D'UNE POSE R6 : la mesurer, la reconstruire depuis une image, la
comparer depuis la MÊME caméra.

Né du retour de Milan sur « Un seul coup » v5 (7,5) : « analyse visuellement,
géométriquement ; c'est une brique qui te manque ». Cinq versions du poing
chargé ont été faites en traduisant des MOTS (« arrière », « buste qui
tourne », « sur le côté ») en clés, sans jamais savoir où étaient VRAIMENT les
membres dans les refs. Cet outil donne trois choses :

1. `descripteurs(w)` : une pose -> des nombres lisibles d'animateur, dans le
   repère DU COUP (avant = direction de la frappe) : lacet / penché du buste,
   direction de chaque bras dans les axes du TORSE (az 0 = devant le torse,
   +90 = son côté droit, 180 = derrière ; el +90 = vers le haut), poing et
   épaules dans le repère du coup, pieds, hauteur de hanche.
   Les mêmes nombres pour nos exports, les animations officielles TSB et le
   pack battleground : on compare ce qui est comparable.
2. `pose(params)` : une pose R6 décrite par CES MÊMES paramètres (inverse de
   1) -> reconstruire une image de ref par essais : on pose, on rend depuis
   une caméra qui imite la sienne, on superpose, on corrige.
3. `cote_a_cote(ref, mondes, cam)` : ref | notre rendu | superposition, à la
   taille de la ref : on ne juge plus une pose de mémoire.

Repère : le perso regarde -Z, +X = sa droite, +Y = haut (celui de moon.py).
Aide pour voir et mesurer : aucun seuil ici ne dit qu'une pose est bonne.
"""
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", ".."))
import moon as M  # noqa: E402
import vues as VU  # noqa: E402
from animator_brain import roblox_export as X  # noqa: E402

Y = np.array([0.0, 1.0, 0.0])
BRAS = {"RA": "Right Arm", "LA": "Left Arm"}
JAMBES = {"RL": "Right Leg", "LL": "Left Leg"}


# ------------------------------------------------------------ repère du coup
def repere(avant=(0.0, 0.0, -1.0)):
    """(avant, droite) horizontaux unitaires ; avant = direction de la frappe."""
    f = np.array(avant, float); f[1] = 0.0; f /= np.linalg.norm(f)
    r = np.cross(f, Y); r /= np.linalg.norm(r)
    return f, r


def _deg(x):
    return float(np.degrees(x))


def _dir_az_el(v, f, r, u=Y):
    """Direction v -> (az, el) : az 0 = f, +90 = r ; el +90 = u."""
    v = np.asarray(v, float) / np.linalg.norm(v)
    return round(_deg(np.arctan2(v @ r, v @ f)), 1), round(_deg(np.arcsin(np.clip(v @ u, -1, 1))), 1)


def az_el_vers_dir(az, el):
    """(az, el) dans les axes du torse -> vecteur local (avant du torse = -Z)."""
    a, e = np.radians(az), np.radians(el)
    return np.array([np.cos(e) * np.sin(a), np.sin(e), -np.cos(e) * np.cos(a)])


def bout(w, part):
    r, p = w[part]
    return p + r @ np.array([0.0, -1.0, 0.0])


def haut(w, part):
    r, p = w[part]
    return p + r @ np.array([0.0, 1.0, 0.0])


# ------------------------------------------------------------ 1. mesurer
def descripteurs(w, avant=(0.0, 0.0, -1.0)):
    """Pose monde {part: (R, p)} -> nombres dans le repère du coup.

    buste.lacet : + = le torse a tourné vers SA gauche (épaule droite qui
      AVANCE, comme au contact d'un direct du droit) ; - = tourné vers sa
      droite (épaule droite qui RECULE, comme à l'armé) ;
    buste.penche_avant : + = penché vers l'avant de SON torse ;
    buste.penche_cote : + = penché vers sa droite ;
    bras.X.torse = (az, el) dans les axes du torse ; bras.X.coup = (az, el)
      dans le repère du coup (az 0 = vers la cible) ;
    poing.X = bout du bras (avant, droite, haut) depuis le centre du torse,
      repère du coup ; epaules.recul_droite = de combien l'épaule droite est
      DERRIÈRE la gauche le long du coup (+ = reculée) ;
    pieds.X = (avant, droite, y) depuis le centre du torse ; hanche = hauteur
      du centre du torse (debout : 3,0)."""
    f, r = repere(avant)
    Rt, pt = w["Torso"]
    ft, rt_, ut = Rt @ np.array([0, 0, -1.0]), Rt @ np.array([1.0, 0, 0]), Rt @ Y
    fh = ft - (ft @ Y) * Y
    fh = fh / np.linalg.norm(fh) if np.linalg.norm(fh) > 1e-6 else f
    rh = np.cross(fh, Y)
    d = {"hanche": round(float(pt[1]), 3),
         "buste": {"lacet": round(_deg(np.arctan2(-(fh @ r), fh @ f)), 1),
                   "penche_avant": round(_deg(np.arctan2(ut @ fh, ut @ Y)), 1),
                   "penche_cote": round(_deg(np.arctan2(ut @ rh, ut @ Y)), 1)},
         "bras": {}, "poing": {}, "pieds": {}}

    def loc(p):
        v = np.asarray(p) - pt
        return [round(float(v @ f), 2), round(float(v @ r), 2), round(float(v @ Y), 2)]

    for k, part in BRAS.items():
        if part not in w:
            continue
        dirw = w[part][0] @ np.array([0.0, -1.0, 0.0])
        d["bras"][k] = {"torse": _dir_az_el(Rt.T @ dirw, np.array([0, 0, -1.0]), np.array([1.0, 0, 0])),
                        "coup": _dir_az_el(dirw, f, r)}
        d["poing"][k] = loc(bout(w, part))
    if "Right Arm" in w and "Left Arm" in w:
        d["epaules"] = {"recul_droite": round(float((haut(w, "Left Arm") - haut(w, "Right Arm")) @ f), 2)}
    for k, part in JAMBES.items():
        if part in w:
            d["pieds"][k] = loc(bout(w, part))
    if "Head" in w:
        hv = w["Head"][0] @ np.array([0, 0, -1.0])
        d["tete"] = {"torse": _dir_az_el(Rt.T @ hv, np.array([0, 0, -1.0]), np.array([1.0, 0, 0])),
                     "coup": _dir_az_el(hv, f, r)}
    return d


def resume(d):
    """Une ligne lisible."""
    b = d["buste"]
    s = f"hanche {d['hanche']:.2f} | buste lacet {b['lacet']:+.0f} penché {b['penche_avant']:+.0f} côté {b['penche_cote']:+.0f}"
    for k in ("RA", "LA"):
        if k in d["bras"]:
            s += f" | {k} torse az {d['bras'][k]['torse'][0]:+.0f} el {d['bras'][k]['torse'][1]:+.0f}"
            s += f" (coup az {d['bras'][k]['coup'][0]:+.0f} el {d['bras'][k]['coup'][1]:+.0f}) poing {d['poing'][k]}"
    if "epaules" in d:
        s += f" | épaule D reculée {d['epaules']['recul_droite']:+.2f}"
    return s


# ------------------------------------------------------------ 2. reconstruire
def _oriente(d, roulis=0.0):
    """Rotation (axes du torse) qui amène l'axe du membre (-Y, pivot -> bout)
    sur d par la rotation MINIMALE depuis le repos, puis tourne de `roulis`
    autour de d. Corrigé le 2026-09-26 : la 1re version passait par moon.aim,
    dont le roulis arbitraire faisait tourner le bloc autour de son axe ; comme
    le pivot R6 est au coin de l'épaule (pas sur l'axe), le bras se décalait
    jusqu'à 1 stud (repos (0,-90) : centre à x = 0,5 au lieu de 1,5). Trouvé
    par un vérificateur adverse de la reconstruction TSB."""
    d = np.asarray(d, float) / np.linalg.norm(d)
    r = M._align(np.array([0.0, -1.0, 0.0]), d)
    if roulis:
        a = np.radians(roulis)
        K = np.array([[0, -d[2], d[1]], [d[2], 0, -d[0]], [-d[1], d[0], 0]])
        r = (np.eye(3) + np.sin(a) * K + (1 - np.cos(a)) * (K @ K)) @ r
    return r


def pose(p):
    """Paramètres -> monde R6 (pour reconstruire une image de ref).

    p = {"hanche": 3.0,                       # hauteur du centre du torse
         "buste": (lacet, penche_avant, penche_cote),   # mêmes conventions que descripteurs
         "tete": (lacet, tangage) relatifs au torse (tangage + = baisse la tête),
         "RA"/"LA": (az, el[, roulis]) direction du bras dans les axes du torse,
         "RL"/"LL": (az, el[, roulis]) direction de la jambe dans les axes du torse
                    OU ("pied", (x, y, z)) point monde où poser le pied,
         "x", "z": position horizontale du torse (défaut 0, 0)}"""
    lac, pen, cote = p.get("buste", (0.0, 0.0, 0.0))
    Rt = M.E(lac, -pen, -cote)
    q = M.neutral(p.get("hanche", 3.0))
    q["root"] = (np.array([p.get("x", 0.0), p.get("hanche", 3.0), p.get("z", 0.0)]), Rt)
    for k, part in {**BRAS, **JAMBES}.items():
        v = p.get(k)
        if v is None or (isinstance(v, tuple) and v and v[0] == "pied"):
            continue
        roul = v[2] if len(v) > 2 else 0.0
        q[part] = (_oriente(az_el_vers_dir(v[0], v[1]), roul), np.zeros(3))
    th = p.get("tete")
    if th is not None:
        q["Head"] = (M.E(th[0], -th[1], 0.0), np.zeros(3))
    for k, part in JAMBES.items():
        v = p.get(k)
        if isinstance(v, tuple) and v and v[0] == "pied":
            M.plant(q, part, np.asarray(v[1], float))
    return M.world(q)


# ------------------------------------------------------------ 3. comparer
def camera_orbite(cible, az, el, dist, fov=50.0, avant=(0.0, 0.0, -1.0)):
    """Caméra autour de la cible, dans le repère du coup : az 0 = DEVANT le
    perso (côté cible, elle le regarde de face), +90 = à sa droite, 180 = dans
    son dos ; el + = au-dessus. -> (oeil, cible, fov)."""
    f, r = repere(avant)
    a, e = np.radians(az), np.radians(el)
    dirc = np.cos(e) * (np.cos(a) * f + np.sin(a) * r) + np.sin(e) * Y
    c = np.asarray(cible, float)
    return (c + dist * dirc, c, fov)


def rendre(mondes, cam, taille=(640, 360), titre="", fond=(200, 205, 215), sol=True):
    if isinstance(mondes, dict):
        mondes = [mondes]
    return M.render(mondes, cam[0], cam[1], cam[2], taille, title=titre, sky=fond, ground=sol)


def cote_a_cote(ref_png, mondes, cam, sortie=None, titre="", alpha=0.5):
    """[ref | rendu | superposition] à la taille de la ref (hauteur 360)."""
    ref = Image.open(ref_png).convert("RGB")
    h = 360
    wd = int(ref.width * h / ref.height)
    ref = ref.resize((wd, h))
    im = rendre(mondes, cam, (wd, h), titre)
    sup = Image.blend(ref, im, alpha)
    out = Image.new("RGB", (3 * wd + 8, h), (0, 0, 0))
    for i, x in enumerate((ref, im, sup)):
        out.paste(x, (i * (wd + 4), 0))
    ImageDraw.Draw(out).text((4, h - 14), os.path.basename(ref_png), fill=(255, 255, 0))
    if sortie:
        out.save(sortie)
    return out


# ------------------------------------------------------------ sources
def mondes_rbxmx(path, fps=60):
    """Notre export (KeyframeSequence .rbxmx) -> un monde par image."""
    return VU.lire_kfseq(path, fps)


def mondes_rbxm(path, nom, fps=60):
    """Une KeyframeSequence d'un .rbxm binaire (TSB, packs) -> [(t, monde)]."""
    from animator_brain import corpus as C
    for s in C.load_rbxm_sequences(path):
        if s["name"] == nom:
            return C.resample_linear(s["frames"], fps)
    raise KeyError(nom)


if __name__ == "__main__":
    w = pose({})
    print("repos :", resume(descripteurs(w)))
    w = pose({"buste": (40, 20, 0), "RA": (90, 0), "LA": (-90, 0), "hanche": 2.5,
              "RL": ("pied", (0.8, 0.0, 0.6)), "LL": ("pied", (-0.8, 0.0, -0.8))})
    print("essai :", resume(descripteurs(w)))
    print(descripteurs(w)["pieds"])
