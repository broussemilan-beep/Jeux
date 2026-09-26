"""Ajustement silhouette : rendu par étiquettes (boîtes R6 + casquette + cape) vs masques de la ref."""
import sys, json, math, random
import numpy as np
from PIL import Image, ImageDraw
sys.path.insert(0, "/home/user/Jeux/experiments/_shared/animator_brain/outils")
import geo_pose as G

REFD = "/tmp/claude-0/-home-user-Jeux/4796ac9e-8e41-51f7-91c4-7b92a6a187d0/scratchpad/poing/refs/"
OUT = "/tmp/claude-0/-home-user-Jeux/4796ac9e-8e41-51f7-91c4-7b92a6a187d0/scratchpad/poing/wf/recon_sp2/r/"
W0, H0 = 320, 180  # fit resolution
SIZES = {"Torso": (2, 2, 1), "Head": (1.25, 1.25, 1.25), "Right Arm": (1, 2, 1), "Left Arm": (1, 2, 1),
         "Right Leg": (1, 2, 1), "Left Leg": (1, 2, 1), "Cap": (1.3, 0.55, 1.3), "Cape": (2.0, 3.6, 0.12)}
# label: 1 dark (black parts), 2 white (head, cape)
LAB = {"Torso": 1, "Right Arm": 1, "Left Arm": 1, "Right Leg": 1, "Left Leg": 1, "Cap": 1, "Head": 2, "Cape": 2}
COLV = {"Torso": (214, 54, 46), "Head": (235, 235, 235), "Right Arm": (80, 200, 110), "Left Arm": (40, 120, 220),
        "Right Leg": (240, 200, 40), "Left Leg": (200, 160, 30), "Cap": (30, 30, 30), "Cape": (250, 250, 250)}
CUBE = np.array([[a, b, c] for a in (-1, 1) for b in (-1, 1) for c in (-1, 1)], float)
FACES = [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)]
FN = [(-1, 0, 0), (1, 0, 0), (0, -1, 0), (0, 1, 0), (0, 0, -1), (0, 0, 1)]


def Rx(a):
    a = math.radians(a); c, s = math.cos(a), math.sin(a)
    return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])


def monde_complet(q):
    """q: dict params geo_pose + 'cape' (angle d'écart au dos, deg), 'capeL'."""
    p = {k: v for k, v in q.items() if k in ("hanche", "buste", "tete", "RA", "LA", "RL", "LL", "x", "z")}
    w = dict(G.pose(p))
    Rh, ph = w["Head"]
    w["Cap"] = (Rh, ph + Rh @ np.array([0, 0.45, 0.0]))
    Rt, pt = w["Torso"]
    L = q.get("capeL", 3.6)
    phi = q.get("cape", 15.0)
    Rc = Rt @ Rx(phi)  # rotation autour de X local : bas de la cape s'écarte vers +Z (dos)
    hinge = pt + Rt @ np.array([0, 1.0, 0.56])
    w["Cape"] = (Rc, hinge + Rc @ np.array([0, -L / 2, 0.0]))
    return w


def camera(cam, cible):
    """cam = (az, el, dist, fov, dx, dy, roll)."""
    az, el, dist, fov = cam[:4]
    eye, tgt, fov = G.camera_orbite(cible, az, el, dist, fov)
    return np.asarray(eye, float), np.asarray(tgt, float), fov


def rendu(w, cam, cible, taille=(W0, H0), mode="lab", sizes=None):
    W, H = taille
    eye, tgt, fov = camera(cam, cible)
    dx, dy = (cam[4], cam[5]) if len(cam) > 5 else (0, 0)
    roll = cam[6] if len(cam) > 6 else 0.0
    f = tgt - eye; f /= np.linalg.norm(f)
    r = np.cross(f, [0, 1.0, 0]); r /= np.linalg.norm(r); u = np.cross(r, f)
    if roll:
        a = math.radians(roll); r, u = r * math.cos(a) + u * math.sin(a), -r * math.sin(a) + u * math.cos(a)
    foc = (H / 2) / math.tan(math.radians(fov) / 2)
    sx = W / 640.0
    polys = []
    for part, (R, c) in w.items():
        if part not in SIZES:
            continue
        h = np.array((sizes or SIZES)[part]) / 2
        vs = (R @ (CUBE * h).T).T + c
        for fc, n in zip(FACES, FN):
            nw = R @ np.array(n, float)
            cen = vs[list(fc)].mean(0)
            if (cen - eye) @ nw >= 0:
                continue
            pts = []
            ok = True
            for i in fc:
                v = vs[i] - eye; z = v @ f
                if z < 0.05:
                    ok = False; break
                pts.append((W / 2 + foc * (v @ r) / z + dx * sx, H / 2 - foc * (v @ u) / z + dy * sx))
            if not ok:
                continue
            polys.append((np.linalg.norm(cen - eye), pts, part, nw))
    polys.sort(key=lambda t: -t[0])
    if mode == "lab":
        im = Image.new("L", (W, H), 0)
        d = ImageDraw.Draw(im)
        for _z, pts, part, _n in polys:
            d.polygon(pts, fill=LAB[part])
        return np.asarray(im)
    im = Image.new("RGB", (W, H), (200, 205, 215))
    d = ImageDraw.Draw(im)
    light = np.array([0.4, 0.9, 0.3]); light /= np.linalg.norm(light)
    for _z, pts, part, nw in polys:
        k = 0.55 + 0.45 * max(0, nw @ light)
        col = tuple(int(x * k) for x in COLV[part])
        d.polygon(pts, fill=col, outline=(10, 10, 10))
    return im


def masque_ref(path, taille=(W0, H0), sombre=60, blanc=205):
    im = Image.open(path).convert("RGB").resize(taille, Image.BILINEAR)
    a = np.asarray(im).astype(int)
    lum = a.mean(2)
    sat = a.max(2) - a.min(2)
    lab = np.zeros(lum.shape, np.uint8)
    lab[(lum < sombre)] = 1
    lab[(a[..., 0] > 150) & (a[..., 1] < 90) & (a[..., 2] < 90)] = 1  # rouge (casquette, logos) -> sombre
    lab[(lum > blanc) & (sat < 30)] = 2
    return lab


def score(lab_r, lab_ref, zone=None):
    s = 0.0
    for k, wgt in ((1, 1.0), (2, 0.6)):
        a = lab_r == k; b = lab_ref == k
        if zone is not None:
            a = a & zone; b = b & zone
        inter = (a & b).sum(); uni = (a | b).sum()
        s += wgt * (inter / uni if uni else 1.0)
    return s / 1.6

NOMS = ["az", "el", "dist", "dx", "dy", "roll", "hanche", "pen", "cote", "RAaz", "RAel", "LAaz", "LAel",
        "RLaz", "RLel", "LLaz", "LLel", "tl", "tt", "cape", "lac"]
PAS = {"az": 8, "el": 5, "dist": 0.6, "dx": 8, "dy": 8, "roll": 3, "hanche": 0.2, "pen": 8, "cote": 6,
       "RAaz": 15, "RAel": 12, "LAaz": 15, "LAel": 12, "RLaz": 15, "RLel": 10, "LLaz": 15, "LLel": 10,
       "tl": 15, "tt": 10, "cape": 8, "lac": 0}


def vers_q(x):
    return {"hanche": x["hanche"], "buste": (x.get("lac", 0.0), x["pen"], x["cote"]), "tete": (x["tl"], x["tt"]),
            "RA": (x["RAaz"], x["RAel"]), "LA": (x["LAaz"], x["LAel"]),
            "RL": (x["RLaz"], x["RLel"]), "LL": (x["LLaz"], x["LLel"]), "cape": x["cape"]}


def vers_cam(x):
    return (x["az"], x["el"], x["dist"], 70.0, x["dx"], x["dy"], x["roll"])


def cible_de(w):
    return tuple(w["Torso"][1])


def evalue(x, lab_ref, zone, pieds=True):
    q = vers_q(x)
    w = monde_complet(q)
    lab = rendu(w, vers_cam(x), (x.get("cx", 0), x.get("cy", 2.0), x.get("cz", 0)))
    s = score(lab, lab_ref, zone)
    if pieds:
        ys = [G.bout(w, k)[1] for k in ("Right Leg", "Left Leg")]
        pen = 0.0
        pen += 0.15 * abs(min(ys))            # le pied le plus bas touche le sol
        pen += 0.15 * max(0, max(ys) - 0.8)   # l'autre pas trop en l'air
        s -= pen
    return s


def optimise(x0, lab_ref, zone, libres, tours=6, echelle=1.0, graine=0, verbose=False, pieds=True):
    rnd = random.Random(graine)
    x = dict(x0)
    best = evalue(x, lab_ref, zone, pieds)
    k = echelle
    for t in range(tours):
        ameliore = False
        ordre = list(libres); rnd.shuffle(ordre)
        for n in ordre:
            for sgn in (1, -1):
                for mult in (1.0, 0.5):
                    y = dict(x); y[n] = x[n] + sgn * mult * k * PAS[n]
                    if n == "dist" and y[n] < 1.5:
                        continue
                    s = evalue(y, lab_ref, zone, pieds)
                    if s > best + 1e-4:
                        x, best, ameliore = y, s, True
                        break
        if verbose:
            print(t, round(best, 4), round(k, 3))
        if not ameliore:
            k *= 0.5
            if k < 0.12:
                break
    return x, best


def montre(x, t, nom, box=None, src="sp2"):
    q = vers_q(x)
    w = monde_complet(q)
    cam = vers_cam(x)
    cib = (x.get("cx", 0), x.get("cy", 2.0), x.get("cz", 0))
    im = rendu(w, cam, cib, (640, 360), mode="rgb")
    ref = Image.open(REFD + f"{src}/t_{t}.png").convert("RGB").resize((640, 360))
    sup = Image.blend(ref, im, 0.5)
    if box:
        ref, im, sup = ref.crop(box), im.crop(box), sup.crop(box)
    out = Image.new("RGB", (3 * ref.width + 8, ref.height))
    for i, a in enumerate((ref, im, sup)):
        out.paste(a, (i * (ref.width + 4), 0))
    ImageDraw.Draw(out).text((4, 4), f"{src} {t} {nom}", fill=(255, 255, 0))
    out.save(OUT + f"{t}_{nom}.png")
    return OUT + f"{t}_{nom}.png"


def zone_box(box, taille=(W0, H0)):
    z = np.zeros((taille[1], taille[0]), bool)
    s = taille[0] / 640.0
    z[int(box[1] * s):int(box[3] * s), int(box[0] * s):int(box[2] * s)] = True
    return z

# ---- v2 : tête ignorée (luminance = sol), points-clés
LAB["Head"] = 3


def masque_ref2(path, taille=(W0, H0), sombre=22, blanc=180):
    im = Image.open(path).convert("RGB").resize(taille, Image.BILINEAR)
    a = np.asarray(im).astype(int)
    lum = a.mean(2); sat = a.max(2) - a.min(2)
    lab = np.zeros(lum.shape, np.uint8)
    lab[lum < sombre] = 1
    lab[(a[..., 0] > 120) & (a[..., 0] - a[..., 1] > 60)] = 1   # rouge
    lab[(lum > blanc) & (sat < 25)] = 2
    return lab


def projette(pts, cam, cible, taille=(640, 360)):
    W, H = taille
    eye, tgt, fov = camera(cam, cible)
    dx, dy = cam[4], cam[5]; roll = cam[6] if len(cam) > 6 else 0.0
    f = tgt - eye; f /= np.linalg.norm(f)
    r = np.cross(f, [0, 1.0, 0]); r /= np.linalg.norm(r); u = np.cross(r, f)
    if roll:
        a = math.radians(roll); r, u = r * math.cos(a) + u * math.sin(a), -r * math.sin(a) + u * math.cos(a)
    foc = (H / 2) / math.tan(math.radians(fov) / 2)
    out = []
    for p in pts:
        v = np.asarray(p) - eye; z = max(v @ f, 0.05)
        out.append((W / 2 + foc * (v @ r) / z + dx, H / 2 - foc * (v @ u) / z + dy))
    return out


def points_modele(w, q):
    Rh, ph = w["Head"]
    return {"tete": ph, "mainG": G.bout(w, "Left Arm"), "mainD": G.bout(w, "Right Arm"),
            "piedG": G.bout(w, "Left Leg"), "piedD": G.bout(w, "Right Leg"),
            "epG": w["Torso"][1] + w["Torso"][0] @ np.array([-1.0, 1.0, 0.5]),
            "epD": w["Torso"][1] + w["Torso"][0] @ np.array([1.0, 1.0, 0.5])}


def evalue2(x, lab_ref, zone, kp=None, kpw=0.004, pieds=True):
    q = vers_q(x)
    w = monde_complet(q)
    cam = vers_cam(x); cib = (x.get("cx", 0), x.get("cy", 2.0), x.get("cz", 0))
    lab = rendu(w, cam, cib)
    ign = lab == 3
    zz = zone & ~ign
    s = 0.0
    for k, wgt in ((1, 1.0), (2, 0.5)):
        a = (lab == k) & zz; b = (lab_ref == k) & zz
        uni = (a | b).sum()
        s += wgt * ((a & b).sum() / uni if uni else 1.0)
    s /= 1.5
    if kp:
        pm = points_modele(w, q)
        noms = list(kp)
        pr = projette([pm[n] for n in noms], cam, cib)
        e = 0.0
        for n, (u, v) in zip(noms, pr):
            e += min(math.hypot(u - kp[n][0], v - kp[n][1]), 150)
        s -= kpw * e / len(noms)
    if pieds:
        ys = [G.bout(w, k)[1] for k in ("Right Leg", "Left Leg")]
        s -= 0.15 * abs(min(ys)) + 0.15 * max(0, max(ys) - 0.8)
    # bornes douces tête
    s -= 0.002 * max(0, abs(x["tt"]) - 35) + 0.002 * max(0, abs(x["tl"]) - 80)
    return s


def optimise2(x0, lab_ref, zone, libres, kp=None, tours=12, echelle=1.0, graine=0, verbose=False):
    rnd = random.Random(graine)
    x = dict(x0)
    best = evalue2(x, lab_ref, zone, kp)
    k = echelle
    for t in range(tours):
        ameliore = False
        ordre = list(libres); rnd.shuffle(ordre)
        for n in ordre:
            for sgn in (1, -1):
                for mult in (1.0, 0.4):
                    y = dict(x); y[n] = x[n] + sgn * mult * k * PAS[n]
                    if n == "dist" and y[n] < 1.5:
                        continue
                    s = evalue2(y, lab_ref, zone, kp)
                    if s > best + 1e-4:
                        x, best, ameliore = y, s, True
                        break
        if not ameliore:
            k *= 0.5
            if k < 0.12:
                break
    return x, best


def debug(x, t, nom, zone_b, src="sp2"):
    lab = masque_ref2(REFD + f"{src}/t_{t}.png")
    w = monde_complet(vers_q(x)); L = rendu(w, vers_cam(x), (x.get("cx", 0), x.get("cy", 2.0), x.get("cz", 0)))
    a = np.zeros((H0, W0, 3), np.uint8); b = np.zeros((H0, W0, 3), np.uint8)
    for arr, m in ((a, lab), (b, L)):
        arr[m == 1] = (255, 60, 60); arr[m == 2] = (60, 60, 255); arr[m == 3] = (90, 90, 90)
    z = zone_box(zone_b)
    a[~z] //= 3; b[~z] //= 3
    im = Image.new("RGB", (2 * W0, H0)); im.paste(Image.fromarray(a), (0, 0)); im.paste(Image.fromarray(b), (W0, 0))
    im.resize((4 * W0, 2 * H0)).save(OUT + f"{t}_{nom}_masques.png")

def masque_tsb(path, taille):
    im = Image.open(path).convert("RGB").resize(taille, Image.BILINEAR)
    a = np.asarray(im).astype(int)
    R_, G_, B_ = a[..., 0], a[..., 1], a[..., 2]
    lum = a.mean(2)
    lab = np.zeros(lum.shape, np.uint8)
    lab[lum < 28] = 1
    lab[(R_ > 140) & (G_ > 120) & (B_ < 90)] = 2          # jaune (tête, cape)
    lab[(B_ > 110) & (R_ > 70) & (G_ < 80) & (B_ > G_ + 60)] = 4   # violet (torse)
    return lab

# ---- v3 : fov libre, bornes
NOMS3 = NOMS + ["fov"]
PAS["fov"] = 6
BORNES = {"cape": (0, 40), "fov": (35, 95), "hanche": (0.8, 3.2), "el": (-40, 80), "dist": (1.5, 20),
          "tt": (-40, 45), "tl": (-85, 85), "RAel": (-90, 90), "LAel": (-90, 90), "RLel": (-90, 30), "LLel": (-90, 30)}


def borne(x):
    for k, (a, b) in BORNES.items():
        if k in x:
            x[k] = min(max(x[k], a), b)
    return x


def vers_cam3(x):
    return (x["az"], x["el"], x["dist"], x.get("fov", 70.0), x["dx"], x["dy"], x.get("roll", 0.0))


def evalue3(x, lab_ref, zone, kp=None, kpw=0.004, contraintes=None):
    q = vers_q(x)
    w = monde_complet(q)
    cam = vers_cam3(x); cib = (0.0, x["hanche"], 0.0)
    lab = rendu(w, cam, cib)
    zz = zone & ~(lab == 3)
    s = 0.0
    for k, wgt in ((1, 1.0), (2, 0.5)):
        a = (lab == k) & zz; b = (lab_ref == k) & zz
        uni = (a | b).sum()
        s += wgt * ((a & b).sum() / uni if uni else 1.0)
    s /= 1.5
    if kp:
        pm = points_modele(w, q)
        noms = list(kp)
        pr = projette([pm[n] for n in noms], cam, cib)
        e = sum(min(math.hypot(u - kp[n][0], v - kp[n][1]), 150) for n, (u, v) in zip(noms, pr))
        s -= kpw * e / len(noms)
    ys = [G.bout(w, k)[1] for k in ("Right Leg", "Left Leg")]
    s -= 0.15 * abs(min(ys)) + 0.15 * max(0, max(ys) - 0.8)
    if contraintes:
        s -= contraintes(x, w)
    return s


def optimise3(x0, lab_ref, zone, libres, kp=None, tours=14, graine=0, contraintes=None, echelle=1.0):
    rnd = random.Random(graine)
    x = borne(dict(x0))
    best = evalue3(x, lab_ref, zone, kp, contraintes=contraintes)
    k = echelle
    for t in range(tours):
        ameliore = False
        ordre = list(libres); rnd.shuffle(ordre)
        for n in ordre:
            for sgn in (1, -1):
                for mult in (1.0, 0.4):
                    y = dict(x); y[n] = x[n] + sgn * mult * k * PAS[n]; y = borne(y)
                    s = evalue3(y, lab_ref, zone, kp, contraintes=contraintes)
                    if s > best + 1e-4:
                        x, best, ameliore = y, s, True
                        break
        if not ameliore:
            k *= 0.5
            if k < 0.12:
                break
    return x, best


def cible_equiv(x):
    """cible pour G.camera_orbite qui reproduit le décalage dx, dy (translation caméra)."""
    fov = x.get("fov", 70.0)
    foc = 180.0 / math.tan(math.radians(fov) / 2)
    tc = np.array([0.0, x["hanche"], 0.0])
    eye, tgt, _ = G.camera_orbite(tuple(tc), x["az"], x["el"], x["dist"], fov)
    eye = np.asarray(eye); f = tc - eye; f /= np.linalg.norm(f)
    r = np.cross(f, [0, 1.0, 0]); r /= np.linalg.norm(r); u = np.cross(r, f)
    d = x["dist"]
    return tuple(tc - (x["dx"] * d / foc) * r + (x["dy"] * d / foc) * u)


def montre3(x, t, nom, box=None, src="sp2"):
    w = monde_complet(vers_q(x)); cam = vers_cam3(x)
    im = rendu(w, cam, (0.0, x["hanche"], 0.0), (640, 360), mode="rgb")
    ref = Image.open(REFD + f"{src}/t_{t}.png").convert("RGB").resize((640, 360))
    sup = Image.blend(ref, im, 0.5)
    if box:
        ref, im, sup = ref.crop(box), im.crop(box), sup.crop(box)
    out = Image.new("RGB", (3 * ref.width + 8, ref.height))
    for i, a in enumerate((ref, im, sup)):
        out.paste(a, (i * (ref.width + 4), 0))
    ImageDraw.Draw(out).text((4, 4), f"{src} {t} {nom}", fill=(255, 255, 0))
    out.save(OUT + f"{t}_{nom}.png")
    return OUT + f"{t}_{nom}.png"


def geo_cote(x, t, nom, src="sp2"):
    """Vérif avec l'outil officiel : G.pose (sans cape) + G.camera_orbite + G.cote_a_cote."""
    q = vers_q(x); q = {k: v for k, v in q.items() if k != "cape"}
    w = G.pose(q)
    c = G.camera_orbite(cible_equiv(x), x["az"], x["el"], x["dist"], x.get("fov", 70.0))
    p = OUT + f"{t}_{nom}_geo.png"
    G.cote_a_cote(REFD + f"{src}/t_{t}.png", [w], c, sortie=p, titre=nom)
    return p

LAB["Cap"] = 3
SIZES["Cap"] = (1.5, 0.75, 1.7)
