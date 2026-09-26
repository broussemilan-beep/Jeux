"""Rendu de comparaison pour la reconstruction Pew (dossier recon_pew_c).
Copie locale de moon.render avec : roulis caméra, bout de main (face -Y des
bras) en noir, face avant du torse avec 3 bandes noires (bretelles + cravate
de la ref), ligne d'horizon, point du poing. N'écrit rien dans le dépôt."""
import sys
sys.path.insert(0, "/home/user/Jeux/experiments/_shared/animator_brain/outils")
import numpy as np
from PIL import Image, ImageDraw
import geo_pose as G
import moon as M

SIZES = M.SIZES
GANT = 0.0   # fraction du bras peinte en noir (0 = seulement la face du bout, lecture retenue)
COL = dict(M.COL)
FACES = M.FACES  # 0:-x 1:+x 2:-y 3:+y 4:-z 5:+z


def camera(cible, az, el, dist, fov=70.0, roll=0.0, avant=(0, 0, -1), decal=(0, 0, 0), pitch=None, yaw_off=0.0):
    """Oeil en orbite autour de cible (repère du coup : az 0 = devant le perso).
    pitch=None : regarde cible+decal. Sinon : regard horizontal vers la cible
    tourné de yaw_off (+ = vers la droite de l'image) puis baissé de pitch deg."""
    eye, c, fov = G.camera_orbite(cible, az, el, dist, fov, avant)
    eye = np.asarray(eye); c = np.asarray(c) + np.asarray(decal, float)
    if pitch is None:
        return dict(eye=eye, target=c, fov=fov, roll=roll)
    h = c - eye; h[1] = 0; h /= np.linalg.norm(h)
    a = np.radians(-yaw_off)
    h = np.array([np.cos(a) * h[0] + np.sin(a) * h[2], 0, -np.sin(a) * h[0] + np.cos(a) * h[2]])
    pr = np.radians(pitch)
    fwd = np.cos(pr) * h - np.sin(pr) * np.array([0, 1.0, 0])
    return dict(eye=eye, target=eye + fwd, fov=fov, roll=roll)


def render(worlds, cam, size=(960, 540), titre="", flat=False):
    W, H = size
    eye, target, fov, roll = cam["eye"], cam["target"], cam["fov"], cam.get("roll", 0.0)
    f = target - eye; f = f / np.linalg.norm(f)
    r = np.cross(f, [0, 1.0, 0]); r /= np.linalg.norm(r); u = np.cross(r, f)
    a = np.radians(roll)  # roulis + = image tournée dans le sens horaire (horizon monte à droite)
    r, u = np.cos(a) * r + np.sin(a) * u, -np.sin(a) * r + np.cos(a) * u
    foc = (H / 2) / np.tan(np.radians(fov) / 2)

    def proj(p):
        v = np.asarray(p, float) - eye
        z = v @ f
        return (W / 2 + foc * (v @ r) / max(z, 1e-3), H / 2 - foc * (v @ u) / max(z, 1e-3)), z

    def projdir(dv):
        z = dv @ f
        if z <= 1e-3:
            return None
        return (W / 2 + foc * (dv @ r) / z, H / 2 - foc * (dv @ u) / z)

    im = Image.new("RGB", size, (0, 0, 0) if flat else (200, 205, 215))
    d = ImageDraw.Draw(im)
    # sol : dalles 4x4 studs, sombres, jusqu'à loin
    polys = []
    for gx in (range(-40, 41, 4) if not flat else ()):
        for gz in range(-40, 41, 4):
            c = [(gx, 0, gz), (gx + 4, 0, gz), (gx + 4, 0, gz + 4), (gx, 0, gz + 4)]
            pts = [proj(p) for p in c]
            if min(z for _p, z in pts) <= 0.1:
                continue
            sh = 70 if ((gx + gz) // 4) % 2 == 0 else 60
            polys.append((1e9, [[p for p, _z in pts]], [(sh, sh + 5, sh + 20)], (90, 100, 130)))
    light = np.array([0.4, 0.9, 0.3]); light /= np.linalg.norm(light)
    boxes = []
    for w in worlds:
        for part, (R, c) in w.items():
            if part not in SIZES:
                continue
            h = np.array(SIZES[part]) / 2
            if part in ("Right Arm", "Left Arm") and GANT > 0:
                # manche (haut 2/3) + gant noir (bas 1/3) comme le perso de Pew
                boxes.append((part, R, c + R @ np.array([0, GANT, 0]), np.array([0.5, 1 - GANT, 0.5]), False))
                boxes.append((part, R, c + R @ np.array([0, GANT - 1, 0]), np.array([0.5, GANT, 0.5]), True))
            else:
                boxes.append((part, R, c, h, False))
    for part, R, c, h, gant in boxes:
            cs = np.array([[a_, b, cc] for a_ in (-1, 1) for b in (-1, 1) for cc in (-1, 1)]) * h
            vs = (R @ cs.T).T + c
            for i, fc in enumerate(FACES):
                q = vs[list(fc)]
                n = np.cross(q[1] - q[0], q[2] - q[0]); n /= np.linalg.norm(n) + 1e-9
                if n @ (q.mean(0) - eye) >= 0:
                    continue
                pts = [proj(p) for p in q]
                if min(z for _p, z in pts) <= 0.05:
                    continue
                k = 0.45 + 0.55 * max(0.0, n @ light)
                base = COL[part]
                if gant:
                    base = tuple(int(x * 0.35) for x in base)
                if part in ("Right Arm", "Left Arm") and i == 2:
                    base = (15, 15, 15)          # bout de la main (face -Y) noir
                if part == "Torso" and i == 5 - 0 and False:
                    pass
                col = tuple(int(min(255, x * k)) for x in base)
                if flat:
                    col = (255, 255, 255) if (part == "Torso" or (part in ("Right Arm", "Left Arm") and not gant and i != 2)) else ((60, 60, 60) if part == "Head" else (0, 0, 0))
                subs = [[p for p, _z in pts]]; cols = [col]
                if part == "Torso" and i == 4:   # face avant (-z) : 3 bandes
                    base = (240, 150, 140); cols = [(255, 255, 255) if flat else tuple(int(min(255, x * k)) for x in base)]
                    for sx in (-0.55, 0.0, 0.55):
                        sq = np.array([[sx - 0.08, 1, -0.5], [sx + 0.08, 1, -0.5], [sx + 0.08, -1, -0.5], [sx - 0.08, -1, -0.5]])
                        sv = (R @ sq.T).T + c
                        subs.append([proj(p)[0] for p in sv]); cols.append((10, 10, 10))
                polys.append((float(np.mean([z for _p, z in pts])), subs, cols, (20, 20, 20)))
    for _z, subs, cols, ol in sorted(polys, key=lambda x: -x[0]):
        for j, (pts, col) in enumerate(zip(subs, cols)):
            d.polygon(pts, fill=col, outline=(None if flat else (ol if j == 0 else None)))
    if flat:
        return im
    # horizon
    hs = [projdir(np.array([np.cos(t), 0, np.sin(t)])) for t in np.linspace(0, 2 * np.pi, 721)]
    seg = [p for p in hs if p is not None and -2 * W < p[0] < 3 * W]
    seg.sort()
    if len(seg) > 1:
        d.line(seg, fill=(255, 0, 255), width=2)
    # poings
    for part, colr in (("Right Arm", (0, 255, 0)), ("Left Arm", (0, 160, 255))):
        for w in worlds:
            if part in w:
                p, z = proj(M.tip(w, part))
                if z > 0.05:
                    d.ellipse([p[0] - 5, p[1] - 5, p[0] + 5, p[1] + 5], outline=colr, width=2)
    if titre:
        d.rectangle([0, 0, 7 * len(titre) + 8, 16], fill=(0, 0, 0)); d.text((4, 2), titre, fill=(255, 230, 120))
    return im


def compare(ref_png, worlds, cam, sortie, titre="", alpha=0.5):
    ref = Image.open(ref_png).convert("RGB").resize((960, 540))
    im = render(worlds if isinstance(worlds, list) else [worlds], cam, (960, 540), titre)
    import cv2
    g = cv2.cvtColor(np.asarray(ref)[:, :, ::-1].copy(), cv2.COLOR_BGR2GRAY)
    e = cv2.Canny(cv2.GaussianBlur(g, (5, 5), 0), 30, 80)
    sup = np.asarray(Image.blend(ref, im, alpha)).copy()
    sup[e > 0] = (255, 40, 40)
    wm = (g > 175).astype(np.uint8)
    ctr = cv2.morphologyEx(wm, cv2.MORPH_GRADIENT, np.ones((3, 3), np.uint8)) > 0
    sup[ctr] = (255, 255, 0)
    sup = Image.fromarray(sup)
    sup.save(sortie.replace(".png", "_sup.png"))
    out = Image.new("RGB", (960 * 3 + 8, 540), (0, 0, 0))
    for i, x in enumerate((ref, im, sup)):
        out.paste(x, (i * 964, 0))
    out = out.resize((out.width * 5 // 6, 450))
    out.save(sortie)
    return out
