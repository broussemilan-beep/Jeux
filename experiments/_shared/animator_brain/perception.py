"""
Perception 3D du cerveau v2 (CERVEAU_V2.md) : mesurer, sur les CFrames monde
d'une animation (la notre ou un pack pro), les principes que les regles v1 ne
voyaient pas, pour que l'etat des hypotheses ne soit plus rempli a la main.

- arcs : un membre qui voyage en ARC devie de la corde entre deux arrets.
  Le controle IK de nos exports est interpole en ligne droite entre les cles,
  avec un ralenti a chaque cle : chaque trait est un segment droit, suivi
  d'un arret. Deux mesures, comparees au pack pro :
    * deviation : fleche max / corde de chaque trait (0 = ligne droite) ;
    * arrets : traits par seconde de mouvement (mouvement saccade = beaucoup
      de petits traits separes par des arrets).
- espacement : part du trajet d'approche parcourue dans le dernier tiers du
  temps (coup qui « claque » = beaucoup a la fin ; coup mou = regulier).
- charge (coup final) : tenue immobile avant le depart, enroulement du buste
  (lacet du torse par rapport au contact), duree du depart.
- frein avant le choc : la main ralentit-elle dans les 3 f avant le contact
  (principe IMPACT HAVEN / coup chapeau), ou arrive-t-elle a pleine vitesse ?

Toutes les mesures sont a 60 i/s, en studs et degres.
"""
import numpy as np

FPS = 60
EXTREMITES = ("Right Arm", "Left Arm", "Right Leg", "Left Leg")
V_MIN = 0.03          # stud/f : en dessous, le membre est « arrete »


def tip(w, part):
    r, p = w[part]
    return p + r @ np.array([0.0, -1.0, 0.0])


def track(world, part, lo=0, hi=None):
    hi = len(world) if hi is None else hi
    return np.array([tip(world[i], part) for i in range(max(0, lo), min(len(world), hi))])


def yaw_deg(world, i):
    f = world[i]["Torso"][0] @ np.array([0.0, 0.0, -1.0])
    return float(np.degrees(np.arctan2(-f[0], -f[2])))


def strokes(x, v_min=V_MIN, min_chord=0.25):
    """Decoupe une trajectoire en traits entre arrets (minima de vitesse
    sous v_min, ou minima locaux marques). -> [(i0, i1, deviation)]."""
    v = np.linalg.norm(np.diff(x, axis=0), axis=1)
    if len(v) < 3:
        return []
    stop = v < v_min
    # un minimum local net (< 45 % des pics voisins) coupe aussi le trait
    for i in range(1, len(v) - 1):
        if v[i] <= v[i - 1] and v[i] <= v[i + 1]:
            lo, hi = v[max(0, i - 8): i].max(initial=0), v[i + 1: i + 9].max(initial=0)
            if v[i] < 0.45 * min(lo, hi):
                stop[i] = True
    out, i = [], 0
    while i < len(v):
        if stop[i]:
            i += 1
            continue
        j = i
        while j < len(v) and not stop[j]:
            j += 1
        a, b = x[i], x[j]
        chord = np.linalg.norm(b - a)
        if chord >= min_chord:
            seg = x[i: j + 1]
            u = (b - a) / chord
            rel = seg - a
            perp = rel - np.outer(rel @ u, u)
            out.append((i, j, float(np.linalg.norm(perp, axis=1).max() / chord)))
        i = j
    return out


def arcs(world, lo=0, hi=None, parts=EXTREMITES):
    """{'deviation_mediane', 'traits_par_s', 'n_traits'} sur la fenetre."""
    devs, n, moving = [], 0, 0
    for p in parts:
        x = track(world, p, lo, hi)
        s = strokes(x)
        devs += [d for _i, _j, d in s]
        n += len(s)
        moving += sum(j - i for i, j, _d in s)
    return {"deviation_mediane": round(float(np.median(devs)), 3) if devs else None,
            "deviation_p75": round(float(np.percentile(devs, 75)), 3) if devs else None,
            "traits_par_s_de_mouvement": round(n / max(1e-6, moving / FPS), 2) if n else None,
            "n_traits": n}


def strike_frame(world, part, fwd=np.array([0.0, 0.0, -1.0])):
    """Contact d'un clip pro : frame ou la main est le plus loin devant le torse."""
    reach = [(tip(w, part) - w["Torso"][1]) @ fwd for w in world]
    return int(np.argmax(reach))


def approche(world, c, part, n=12):
    """Espacement et frein sur les n frames avant le contact c."""
    x = track(world, part, c - n, c + 1)
    v = np.linalg.norm(np.diff(x, axis=0), axis=1)
    if len(v) < 6 or v.sum() < 1e-6:
        return None
    third = max(1, len(v) // 3)
    return {"part_dernier_tiers": round(float(v[-third:].sum() / v.sum()), 2),
            "frein_3f_sur_pic": round(float(v[-3:].mean() / v.max()), 2),
            "vitesse_pic_studs_par_f": round(float(v.max()), 3)}


def charge(world, c, part, n=60):
    """Mesures de charge avant le contact c (coup final)."""
    lo = max(0, c - n)
    x = track(world, part, lo, c + 1)
    v = np.linalg.norm(np.diff(x, axis=0), axis=1)
    torso = np.array([world[i]["Torso"][1] for i in range(lo, c + 1)])
    vt = np.linalg.norm(np.diff(torso, axis=0), axis=1)
    if len(v) < 2:
        return None
    peak = v.max()
    # depart : derniere frame ou la main etait sous 25 % du pic
    slow = np.where(v < 0.25 * peak)[0]
    start = int(slow[-1]) if len(slow) else 0
    depart = len(v) - start
    # tenue : plus longue suite ou le torse ET la main sont quasi immobiles
    still = (vt < 0.015) & (v < V_MIN)
    best = run = 0
    for s in still[:start + 1]:
        run = run + 1 if s else 0
        best = max(best, run)
    yc = yaw_deg(world, c)
    coil = max(abs(((yaw_deg(world, i) - yc + 180) % 360) - 180) for i in range(lo, c + 1))
    return {"tenue_f": int(best), "enroulement_buste_deg": round(float(coil), 1), "depart_f": int(depart)}


# ------------------------------------------------------------------ productions

def load_production(kfseq_path, root=(np.eye(3), np.array([0.0, 3.0, 0.0])), end_f=None):
    """KeyframeSequence exportee -> CFrames monde a 60 i/s (interpolation
    lineaire/slerp entre cles, comme notre lecteur)."""
    from . import roblox_export as X
    keys = X.read_kfseq(kfseq_path)
    ts = [k[0] for k in keys]
    n = int(round(ts[-1] * FPS)) if end_f is None else end_f
    out = []
    for f in range(n + 1):
        t = f / FPS
        i = max(0, min(len(ts) - 2, int(np.searchsorted(ts, t, side="right")) - 1))
        u = min(1.0, max(0.0, (t - ts[i]) / (ts[i + 1] - ts[i])))
        pose = {p: (X._slerp_rot(keys[i][1][p][0], keys[i + 1][1][p][0], u),
                    keys[i][1][p][1] + (keys[i + 1][1][p][1] - keys[i][1][p][1]) * u) for p in keys[i][1]}
        out.append(X.solve(pose, root=root))
    return out


def final_strike(scene):
    """Le « coup final » : depuis la prise de recul du 2026-09-24
    (ANGLES_MORTS.md 1), c'est le coup de f150 (uppercut en v1-v4, coup charge
    en v5), pas le 4e coup de la rafale."""
    if "upper_f" in scene:
        return scene["upper_f"], scene.get("final_side", "R")
    c, s, _k = scene["hits"][-1]
    return c, s


def segments(scene):
    """Fenetres (frames) des parties d'une production, depuis scene.json."""
    hits = scene["hits"]
    fin, _s = final_strike(scene)
    return {"rafale": (max(0, hits[0][0] - 14), hits[-1][0] + 12),
            "final": (fin - 45, fin + 12),
            "aerien": (scene["upper_f"], scene["impact_f"] + 10)}


def measure_production(world, scene):
    part = {"R": "Right Arm", "L": "Left Arm"}
    hits = [{"f": c, "type": k, **(approche(world, c, part[s]) or {})} for c, s, k in scene["hits"]]
    c, s = final_strike(scene)
    seg = {name: arcs(world, lo, hi) for name, (lo, hi) in segments(scene).items()}
    return {"coups": hits, "charge_final": charge(world, c, part[s]), "arcs_par_partie": seg,
            "arcs_global": arcs(world)}


def fist_shape(world, c, part, n=12, after=6):
    """Forme du trajet du poing autour du contact, dans le repere du torse
    au contact, recentree sur le point de contact (compare des FORMES de
    coups, pas des positions)."""
    r, p = world[c]["Torso"]
    pts = np.array([r.T @ (tip(world[i], part) - p) for i in range(max(0, c - n), min(len(world), c + after + 1))])
    return pts - pts[min(n, len(pts) - 1)]


def variete(world, hits):
    """Distance mediane (studs, RMS) entre les formes des coups d'une rafale ;
    les coups d'un bras gauche sont miroites pour comparer la forme, pas le cote."""
    part = {"R": "Right Arm", "L": "Left Arm"}
    shapes = []
    for c, s, _k in hits:
        sh = fist_shape(world, c, part[s])
        if s == "L":
            sh = sh * np.array([-1.0, 1.0, 1.0])
        shapes.append(sh)
    n = min(len(s) for s in shapes)
    d = [float(np.sqrt(((a[:n] - b[:n]) ** 2).sum(1).mean())) for i, a in enumerate(shapes) for b in shapes[i + 1:]]
    return round(float(np.median(d)), 3) if d else None


def pose_impact(world, c, part):
    """Anatomie R6 au contact d'un coup droit (etude des tutos, 2026-09-24,
    corpus/TUTOS_ANIMATION.md) :
    - bras_epaules_deg : angle entre le bras qui frappe (epaule -> poing) et la
      ligne des epaules cote bras ; 0 = le bras PROLONGE les epaules (torse de
      profil, une seule droite). M1 pro : 18-28 ; nous v6 : 46-72.
    - torse_detourne_deg : lacet du torse par rapport a la direction du coup.
      M1 pro : 67-75 ; nous : 32-48.
    - bras_libre : produit scalaire des directions des deux bras ; ~1 = le bras
      libre est tendu vers l'avant lui aussi, ~0 ramene contre le corps. M1
      pro : -0,1 a 0,3 ; nous : 0,9.
    - translation_bras : translation du Motor6D d'epaule (bras « decolle »,
      le bras R6 joue l'avant-bras). M1 pro AU CONTACT : 0,58-0,92 ; nous :
      0,96 -> pas un ecart (les 1,25-1,6 pro sont la mediane du clip, garde
      comprise : c'est la GARDE pro qui tient les bras translates devant)."""
    from animator_brain import roblox_export as X
    other = "Left Arm" if part == "Right Arm" else "Right Arm"
    w = world[c]
    rT = w["Torso"][0]
    arm = w[part][0] @ np.array([0.0, -1.0, 0.0])
    free = w[other][0] @ np.array([0.0, -1.0, 0.0])
    sh = rT @ np.array([1.0 if part == "Right Arm" else -1.0, 0.0, 0.0])
    d = tip(w, part) - w["Torso"][1]
    d[1] = 0.0
    fwd = rT @ np.array([0.0, 0.0, -1.0])
    fwd[1] = 0.0
    cosang = float(np.clip(fwd @ d / (np.linalg.norm(fwd) * np.linalg.norm(d) + 1e-9), -1, 1))
    return {"bras_epaules_deg": round(float(np.degrees(np.arccos(np.clip(arm @ sh, -1, 1)))), 1),
            "torse_detourne_deg": round(float(np.degrees(np.arccos(cosang))), 1),
            "bras_libre": round(float(arm @ free), 2),
            "translation_bras": round(float(np.linalg.norm(X.joint_transform(part, w)[1])), 2)}


def profil_frappe(world, c, part, n=12):
    """Forme du profil de vitesse du poing jusqu'au contact (fichier TSB
    officiel, 2026-09-24). TSB M1-M4 : lente derive (~15-20 studs/s) puis le
    poing PASSE a pleine vitesse en 1 image et y reste en palier 2-3 images
    (cles eparses en Linear). Nous v1-v6 : rampe en triangle sur 2-3 images,
    pointe unique (courbes Bezier cuites image par image).
    Le contact est pris a la 1re image ou le poing atteint 97 % de son
    extension vers l'avant (sinon on tombe 1 image trop tard, sur une derive).
    - plateau : vitesse mini / maxi pendant la phase rapide (>= 50 % de la
      pointe) ; 1 = vitesse constante, rectangle.
    - arrivee : vitesse de la derniere image avant le contact / pointe."""
    lo = max(0, c - n)
    fwd = np.array([0.0, 0.0, -1.0])
    ext = np.array([(tip(world[i], part) - world[i]["Torso"][1]) @ (world[i]["Torso"][0] @ fwd) for i in range(lo, c + 1)])
    c2 = lo + int(np.argmax(ext >= ext.min() + 0.97 * (ext.max() - ext.min())))
    pts = np.array([tip(world[i], part) for i in range(lo, c2 + 1)])
    v = np.linalg.norm(np.diff(pts, axis=0), axis=1) * 60.0
    if len(v) < 2 or v.max() <= 0:
        return None
    pk = float(v.max())
    j = len(v) - 1
    while j > 0 and v[j - 1] >= 0.5 * pk:
        j -= 1
    fast = v[j:]
    fast = fast[fast >= 0.5 * pk] if (fast >= 0.5 * pk).any() else fast
    return {"plateau": round(float(fast.min() / fast.max()), 2), "arrivee": round(float(v[-1] / pk), 2),
            "phase_rapide_f": int(len(v) - j), "pointe": round(pk, 1), "contact_f": c2}
