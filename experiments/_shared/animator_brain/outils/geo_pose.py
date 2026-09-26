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
4. `profondeur_ambigue(monde, camera)` (2026-09-26) : pour chaque bras et
   jambe, l'ordre devant/derrière le torse se lit-il depuis CETTE caméra, ou
   est-il ambigu ? (+ `camera_plan`, `camera_jeu`, `racine_victime` : les deux
   caméras des nouveaux yeux et le placement de la victime.)

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


# ------------------------------------------------------------ 4. profondeur lisible ?
# Ajouté le 2026-09-26 (chantier « nouveaux yeux », SYNTHESE_YEUX rang 4).
# Faiblesse 2 du cerveau : sur une ref, j'ai lu un bras « devant » le torse
# alors qu'il était derrière. Sur un R6, un bloc est rigide et de longueur
# connue : à l'écran, seul le SIGNE de sa profondeur se perd. Cette fonction ne
# devine rien ; elle dit, pour une caméra donnée, si l'ordre devant/derrière
# le torse SE LIT (un bloc en recouvre un autre, à une vraie distance) ou non.
#
# Ce qu'elle mesure, par membre :
#   axe_visee   |cos| entre l'axe du membre (épaule/hanche -> bout) et le rayon
#               de visée : 0 = vu de travers (longueur entière visible),
#               1 = pointé droit sur l'objectif (ou droit vers le fond) ;
#   vers_camera le bout va-t-il vers la caméra (+) ou vers le fond (-) ;
#   ordre_3d    la moitié BOUT du membre (main, pied) est-elle « devant » ou
#               « derrière » le torse : là où ils se recouvrent à l'écran, par
#               lancer de rayons (qui le rayon touche d'abord) ; sinon en
#               comparant leurs profondeurs le long du rayon (« au niveau du »
#               si elles se chevauchent) ; vérité 3D que NOUS connaissons pour
#               nos anims, pas ce que montre l'image ;
#   ecart       distance entre les surfaces (studs) : le long des rayons là
#               où ils se recouvrent, sinon en profondeur (0 si « au niveau du »)
#   recouvrement part de l'aire à l'écran de cette moitié bout qui recouvre
#               le torse (polygones projetés exacts, pas de pixels ; la moitié
#               épaule/hanche est exclue : son attache recouvre toujours) ;
#   lecture     « lisible » : elle recouvre le torse et en est séparée en
#               profondeur : l'image montre qui passe devant (sur nos blocs
#               à couleur plate, le recouvrement se voit) ;
#               « ambigu » : dans l'axe de visée (le signe de sa profondeur
#               se perd), OU recouvre le torse au contact (moins de
#               `contact` entre les surfaces, ou ils se traversent), OU devant/derrière
#               sans recouvrir le torse : l'image miroir (même membre de
#               l'autre côté du torse) donnerait le même dessin ;
#               « à côté » : ni recouvrement ni écart de profondeur.
# Ce qu'elle NE voit PAS : les coupes et le mouvement (une image à la fois ;
# l'image d'avant peut lever l'ambiguïté), la lumière et les ombres de la vraie
# scène, les effets qui cachent un membre, la tête ; et un seuil n'est pas un
# œil humain : les seuils sont des réglages d'affichage, rendus dans la sortie.
# Aucun verdict de style : elle ne choisit pas de caméra (le poing jeté dans
# l'objectif peut être voulu, SYNTHESE_YEUX rang 4).
MEMBRES_PROF = {"BD": "Right Arm", "BG": "Left Arm", "JD": "Right Leg", "JG": "Left Leg"}
SEUILS_PROF = {"axe_visee": 0.85, "tolerance": 0.1, "recouvrement": 0.05, "contact": 0.05}


def _coins(w, part, moitie_bout=False):
    """8 coins monde du bloc ; moitie_bout : seulement la moitié côté BOUT
    (main / pied), pour ne pas compter l'attache épaule/hanche, qui recouvre
    toujours le torse."""
    R, c = w[part]
    h = np.array(M.SIZES[part]) / 2
    ys = (-1, 0) if moitie_bout else (-1, 1)
    cs = np.array([[a, b, cc] for a in (-1, 1) for b in ys for cc in (-1, 1)]) * h
    return (np.asarray(R) @ cs.T).T + np.asarray(c)


def _enveloppe(pts):
    """Enveloppe convexe 2D (chaîne monotone), sens trigonométrique."""
    pts = sorted(set((round(float(x), 6), round(float(y), 6)) for x, y in pts))
    if len(pts) < 3:
        return pts

    def cr(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    bas, haut_ = [], []
    for p in pts:
        while len(bas) >= 2 and cr(bas[-2], bas[-1], p) <= 0:
            bas.pop()
        bas.append(p)
    for p in reversed(pts):
        while len(haut_) >= 2 and cr(haut_[-2], haut_[-1], p) <= 0:
            haut_.pop()
        haut_.append(p)
    return bas[:-1] + haut_[:-1]


def _aire(poly):
    if len(poly) < 3:
        return 0.0
    return 0.5 * abs(sum(poly[i][0] * poly[i - 1][1] - poly[i - 1][0] * poly[i][1] for i in range(len(poly))))


def _intersection(sujet, clip):
    """Sutherland-Hodgman : polygone convexe `sujet` découpé par le convexe `clip`
    (les deux en sens trigonométrique)."""
    out = list(sujet)
    for i in range(len(clip)):
        a, b = clip[i - 1], clip[i]
        entree, out = out, []
        if not entree:
            break

        def dedans(p):
            return (b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0]) >= 0

        def coupe(p, q):
            x1, y1, x2, y2 = p[0], p[1], q[0], q[1]
            x3, y3, x4, y4 = a[0], a[1], b[0], b[1]
            den = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
            if abs(den) < 1e-12:
                return q
            t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / den
            return (x1 + t * (x2 - x1), y1 + t * (y2 - y1))
        s = entree[-1]
        for e in entree:
            if dedans(e):
                if not dedans(s):
                    out.append(coupe(s, e))
                out.append(e)
            elif dedans(s):
                out.append(coupe(s, e))
            s = e
    return out


def _projeter(pts, oeil, f, r, u):
    v = np.asarray(pts) - oeil
    z = np.maximum(v @ f, 1e-3)
    return [(float(a), float(b)) for a, b in zip((v @ r) / z, (v @ u) / z)]


def _boite(w, part, moitie_bout=False):
    R, c = w[part]
    R, c = np.asarray(R, float), np.asarray(c, float)
    h = np.array(M.SIZES[part], float) / 2
    if moitie_bout:
        c = c + R @ np.array([0.0, -h[1] / 2, 0.0])
        h = h * np.array([1.0, 0.5, 1.0])
    return R, c, h


def _entree(oeil, dirn, boite):
    """Distance (le long de dirn) où le rayon entre dans la boîte, ou None."""
    R, c, h = boite
    o, dd = R.T @ (oeil - c), R.T @ dirn
    t0, t1 = -np.inf, np.inf
    for i in range(3):
        if abs(dd[i]) < 1e-12:
            if abs(o[i]) > h[i]:
                return None
            continue
        a, b = (-h[i] - o[i]) / dd[i], (h[i] - o[i]) / dd[i]
        t0, t1 = max(t0, min(a, b)), min(t1, max(a, b))
    return float(t0) if t1 >= max(t0, 0.0) else None


def profondeur_ambigue(monde, camera, seuils=None):
    """monde {part: (R, p)} ; camera (oeil, cible[, fov]) -> {BD/BG/JD/JG: {...}}
    (voir l'en-tête de cette section). Les seuils utilisés sont rendus sous la
    clé « _seuils »."""
    s = dict(SEUILS_PROF, **(seuils or {}))
    oeil = np.asarray(camera[0], float)
    cible = np.asarray(camera[1], float)
    f = cible - oeil
    f /= np.linalg.norm(f)
    r = np.cross(f, Y)
    r = r / np.linalg.norm(r) if np.linalg.norm(r) > 1e-6 else np.array([1.0, 0, 0])
    u = np.cross(r, f)
    tc = np.asarray(monde["Torso"][1], float)
    poly_t = _enveloppe(_projeter(_coins(monde, "Torso"), oeil, f, r, u))
    out = {"_seuils": s}
    for k, part in MEMBRES_PROF.items():
        if part not in monde:
            continue
        a, b = haut(monde, part), bout(monde, part)
        d = (b - a) / np.linalg.norm(b - a)
        c = np.asarray(monde[part][1], float)
        ray = (c - oeil) / np.linalg.norm(c - oeil)
        axe = float(abs(d @ ray))
        poly_m = _enveloppe(_projeter(_coins(monde, part, moitie_bout=True), oeil, f, r, u))
        am = _aire(poly_m)
        inter = _intersection(poly_m, poly_t) if am > 1e-12 else []
        rec = _aire(inter) / am if am > 1e-12 else 0.0
        raisons = []
        if axe >= s["axe_visee"]:
            raisons.append(f"presque dans l'axe de visée ({axe:.2f})")
        if rec >= s["recouvrement"]:
            # là où les deux se recouvrent à l'écran : qui le rayon touche-t-il d'abord ?
            cx = sum(p[0] for p in inter) / len(inter)
            cy = sum(p[1] for p in inter) / len(inter)
            ecarts = []
            for px, py in [(cx, cy)] + [(cx + 0.8 * (p[0] - cx), cy + 0.8 * (p[1] - cy)) for p in inter]:
                dirn = f + px * r + py * u
                dirn = dirn / np.linalg.norm(dirn)
                tt = _entree(oeil, dirn, _boite(monde, "Torso"))
                tm = _entree(oeil, dirn, _boite(monde, part, moitie_bout=True))
                if tt is not None and tm is not None:
                    ecarts.append(tt - tm)
            g = float(np.median(ecarts)) if ecarts else 0.0
            ecart = abs(g)
            ordre = "devant" if g > 0 else "derrière"
            if not ecarts or ecart < s["contact"] or (min(ecarts) < 0 < max(ecarts)):
                raisons.append(f"recouvre le torse ({rec:.0%} de sa moitié bout) au contact "
                               f"({ecart * 100:.0f} cm entre les surfaces)")
        else:
            pt_ = (_coins(monde, "Torso") - oeil) @ ray
            pm = (_coins(monde, part, moitie_bout=True) - oeil) @ ray
            tn, tf, mn, mf = pt_.min(), pt_.max(), pm.min(), pm.max()
            tol = s["tolerance"]
            if mf <= tn + tol:
                ordre, ecart = "devant", max(0.0, tn - mf)
            elif mn >= tf - tol:
                ordre, ecart = "derrière", max(0.0, mn - tf)
            else:
                ordre, ecart = "au niveau du", 0.0
            if ordre != "au niveau du":
                raisons.append(f"{ordre} le torse ({ecart:.2f} stud) sans le recouvrir : le miroir donnerait le même dessin")
        if raisons:
            lecture = "ambigu"
        elif rec >= s["recouvrement"]:
            lecture = "lisible"
        else:
            lecture = "à côté"
        dz = ecart if ordre == "derrière" else -ecart
        out[k] = {"axe_visee": round(axe, 2), "vers_camera": bool(d @ ray < 0), "dz": round(dz, 2),
                  "recouvrement": round(float(rec), 2), "ordre_3d": ordre, "lecture": lecture, "raisons": raisons}
    return out


def _ordre_txt(v):
    return "au niveau du torse" if v["ordre_3d"] == "au niveau du" else f"{v['ordre_3d']} le torse"


def resume_profondeur(p, court=False):
    """Une ligne : « BD lisible (devant le torse vu d'ici) ; BG AMBIGU (...) ».
    « devant » = entre la caméra et le torse, « derrière » = plus loin que le
    torse, depuis CETTE caméra (pas l'avant du personnage)."""
    morceaux = []
    for k in MEMBRES_PROF:
        if k not in p:
            continue
        v = p[k]
        if court:
            morceaux.append(f"{k}{'?' if v['lecture'] == 'ambigu' else ('=' if v['lecture'] == 'lisible' else '.')}")
        elif v["lecture"] == "ambigu":
            morceaux.append(f"{k} AMBIGU ({_ordre_txt(v)} vu d'ici ; {', '.join(v['raisons'])})")
        else:
            morceaux.append(f"{k} {v['lecture']} ({_ordre_txt(v)} vu d'ici)")
    return (" ".join(morceaux)) if court else " ; ".join(morceaux)


# ------------------------------------------------------------ caméras de scène
def camera_plan(staging, f, secousse=False):
    """Caméra d'un plan écrit (staging.json d'une production : clés
    [image, oeil, cible, fov, "cut"|"smooth"]) à l'image f, interpolée comme le
    lecteur (lerp si la clé SUIVANTE est « smooth »). La secousse n'est pas
    rendue (secousse=False) : elle ne change pas la pose lue."""
    cs = staging["camera"]
    i = max([k for k, c in enumerate(cs) if c[0] <= f] or [0])
    a = cs[i]
    if i + 1 < len(cs) and cs[i + 1][4] == "smooth":
        b = cs[i + 1]
        t = min(1.0, max(0.0, (f - a[0]) / (b[0] - a[0])))
        return (np.array(a[1]) + t * (np.array(b[1]) - np.array(a[1])),
                np.array(a[2]) + t * (np.array(b[2]) - np.array(a[2])), a[3] + t * (b[3] - a[3]))
    return (np.array(a[1], float), np.array(a[2], float), float(a[3]))


# Caméra de JEU par défaut (hypothèse à mesurer dans Studio le moment venu,
# SYNTHESE_YEUX rang 1) : caméra Roblox classique, FOV vertical 70°, cible =
# HumanoidRootPart + 1,5 stud, 12,5 studs derrière, 15° au-dessus, décalée de
# 1,75 stud vers l'épaule droite (comme le verrouillage d'épaule).
CAMERA_JEU = {"fov": 70.0, "distance": 12.5, "elevation": 15.0, "epaule": 1.75, "hauteur_cible": 1.5}


def camera_jeu(hrp=(0.0, 3.0, 0.0), avant=(0.0, 0.0, -1.0), **reglages):
    """Caméra fixe du joueur, derrière l'épaule. -> (oeil, cible, fov)."""
    c = dict(CAMERA_JEU, **reglages)
    fa, ra = repere(avant)
    cible = np.asarray(hrp, float) + Y * c["hauteur_cible"] + ra * c["epaule"]
    e = np.radians(c["elevation"])
    oeil = cible + c["distance"] * (-np.cos(e) * fa + np.sin(e) * Y)
    return (oeil, cible, c["fov"])


# Placement de la VICTIME de nos scènes à deux rigs : face à l'attaquant, à
# `distance` studs devant lui (experiments/r6_un_seul_coup/scripts/staging.py).
def racine_victime(distance=16.0):
    return (np.diag([-1.0, 1.0, -1.0]), np.array([0.0, 3.0, -float(distance)]))


# ------------------------------------------------------------ sources
def mondes_rbxmx(path, fps=60):
    """Notre export (KeyframeSequence .rbxmx) -> un monde par image."""
    return VU.lire_kfseq(path, fps)


def mondes_rbxm(path, nom, fps=60):
    """Une KeyframeSequence d'un .rbxm binaire (TSB, packs) -> [(t, monde)]."""
    from animator_brain import corpus as C
    for s in C.load_rbxm_sequences(path):
        if s["name"] == nom:
            return C.resample_linear(s["frames"], fps, easing=s.get("easing"))
    raise KeyError(nom)


if __name__ == "__main__":
    w = pose({})
    print("repos :", resume(descripteurs(w)))
    w = pose({"buste": (40, 20, 0), "RA": (90, 0), "LA": (-90, 0), "hanche": 2.5,
              "RL": ("pied", (0.8, 0.0, 0.6)), "LL": ("pied", (-0.8, 0.0, -0.8))})
    print("essai :", resume(descripteurs(w)))
    print(descripteurs(w)["pieds"])
