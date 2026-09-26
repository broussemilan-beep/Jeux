"""
Mini « Moon Animator » R6 en Python : poser et animer comme les animateurs Roblox
des tutos (corpus/tutos/etude_complete_*.md), pas comme notre pipeline IK.

- Chaque membre tourne autour de SON pivot (épaule, hanche, cou), en axes du
  torse ; les membres suivent le torse (FK) : « move it with the torso ».
- Les membres peuvent être TRANSLATÉS (bras « disloqué », jambe montée/descendue).
- Interpolation entre clés = celle de Roblox en Linear (CFrame:Lerp par Motor6D),
  via roblox_export.solve : ce qu'on voit ici est ce que le moteur jouera.
- `plant` recale une jambe pour garder un pied à sa place (onion skin du tuto).
- `wiggle` : petits cercles qui ralentissent (amorti d'énergie, tuto uppercut).
- `render` : rendu perspective ombré (caméra libre, FOV), pour juger à l'œil
  et comparer aux vidéos au même angle.
- `render(..., faces=True)` (2026-09-26) : chaque FACE de chaque bloc colorée
  selon sa direction LOCALE, avec sa lettre : F rouge (avant), B bleu
  (arrière), R vert (droite), L jaune (gauche), U cyan (haut), D orange (bas).
  C'est le rig de contrôle que les animateurs TSB et le tuto Moon utilisent
  (corpus/etude_c4/C1_tsb_videos.md §4, B1_moon_smooth_r6.md) : la couleur vue
  dit comment le bloc est tourné (face D visible = on voit le bout du bras,
  donc il pointe vers la caméra ; un « bras vert » est un bras dont on voit la
  face droite, pas forcément le bras droit). Ce rendu ne voit pas la lumière
  ni les matériaux de la vraie scène ; il ne juge rien.

Repère : le perso regarde -Z, +X = sa droite, +Y = haut, sol à y = 0.
"""
import os
import subprocess
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
from animator_brain import roblox_export as X  # noqa: E402

LIMBS = ("Head", "Right Arm", "Left Arm", "Right Leg", "Left Leg")
SIZES = {"Torso": (2, 2, 1), "Head": (1.25, 1.25, 1.25), "Right Arm": (1, 2, 1), "Left Arm": (1, 2, 1),
         "Right Leg": (1, 2, 1), "Left Leg": (1, 2, 1)}


def Rx(a):
    a = np.radians(a); c, s = np.cos(a), np.sin(a)
    return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])


def Ry(a):
    a = np.radians(a); c, s = np.cos(a), np.sin(a)
    return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])


def Rz(a):
    a = np.radians(a); c, s = np.cos(a), np.sin(a)
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])


def E(yaw=0.0, pitch=0.0, roll=0.0):
    """Lacet (+ = tourne vers sa gauche), tangage (+ = penche en ARRIÈRE,
    - = en avant), roulis (+ = penche sur SA gauche)."""
    return Ry(yaw) @ Rx(pitch) @ Rz(roll)


def aim(d, roll=0.0):
    """Rotation qui envoie l'axe du membre (-Y local, pivot -> bout) sur d."""
    d = np.asarray(d, float); d = d / np.linalg.norm(d); y = -d
    ref = np.array([0, 0, -1.0]) if abs(y[2]) < 0.9 else np.array([1.0, 0, 0])
    x = np.cross(y, ref); x /= np.linalg.norm(x); z = np.cross(x, y)
    return np.stack([x, y, z], axis=1) @ Ry(roll)


class Pose(dict):
    """{'root': (pos monde du centre du torse, rotation monde du torse),
        membre: (rotation dans les axes du torse, translation dans les axes du torse)}"""

    def copy(self):
        return Pose({k: (np.array(v[0], float), np.array(v[1], float)) for k, v in self.items()})


def neutral(y=3.0):
    p = Pose({"root": (np.array([0.0, y, 0.0]), np.eye(3))})
    for m in LIMBS:
        p[m] = (np.eye(3), np.zeros(3))
    return p


def transforms(pose):
    """Pose -> transformations Motor6D (ce qu'écrit une KeyframeSequence)."""
    t = {}
    pos, rt = pose["root"]
    for part in ("Torso",) + LIMBS:
        _n, j = X.JOINT_BY_PART1[part]
        j0 = np.array(j["C0"]["rot"], float)
        j1 = np.array(j["C1"]["rot"], float)
        if part == "Torso":
            rel, tr = rt, np.zeros(3)
        else:
            rel, tr = pose[part]
        t[part] = (j0.T @ rel @ j1, j0.T @ np.asarray(tr, float))
    return t


def world(pose):
    pos, _rt = pose["root"]
    return X.solve(transforms(pose), root=(np.eye(3), np.asarray(pos, float)))


def tip(w, part):
    r, p = w[part]
    return p + r @ np.array([0.0, -1.0, 0.0])


def _align(u, v):
    """Rotation qui envoie le vecteur unitaire u sur v."""
    u = u / np.linalg.norm(u); v = v / np.linalg.norm(v)
    c = float(u @ v); ax = np.cross(u, v); s = np.linalg.norm(ax)
    if s < 1e-9:
        return np.eye(3) if c > 0 else Rx(180)
    k = ax / s; K = np.array([[0, -k[2], k[1]], [k[2], 0, -k[0]], [-k[1], k[0], 0]])
    ang = np.arctan2(s, c)
    return np.eye(3) + np.sin(ang) * K + (1 - np.cos(ang)) * (K @ K)


def plant(pose, leg, foot):
    """Oriente la jambe (pivot R6 : coin haut-extérieur, C0 = (+-1, -1, 0)) pour
    que le bas-milieu du pied tombe sur `foot`, et la translate le long de l'axe
    si la distance n'est pas la bonne (« ONLY use position to move the leg up
    and down » : tuto uppercut). Garde le pied à plat autant que possible."""
    w = world(pose)
    rt, tp = w["Torso"]
    side = 1.0 if leg == "Right Leg" else -1.0
    pivot = tp + rt @ np.array([side * 1.0, -1.0, 0.0])
    u_loc = np.array([-side * 0.5, -2.0, 0.0])          # pivot -> bout du pied, repère jambe au repos
    d = np.asarray(foot, float) - pivot
    L0, L = np.linalg.norm(u_loc), np.linalg.norm(d)
    Rw = _align(u_loc, d)                               # rotation monde de la jambe
    pose[leg] = (rt.T @ Rw, rt.T @ (d / L) * (L - L0))
    return pose


def interp(a, b, u):
    """Clé à clé comme Roblox en Linear : lerp position, slerp rotation."""
    out = Pose()
    for k in a:
        ra, pa = a[k] if k != "root" else (a[k][1], a[k][0])
        rb, pb = b[k] if k != "root" else (b[k][1], b[k][0])
        r = X._slerp_rot(np.asarray(ra), np.asarray(rb), u)
        p = (1 - u) * np.asarray(pa) + u * np.asarray(pb)
        out[k] = (p, r) if k == "root" else (r, p)
    return out


def sample(keys, n_frames):
    """keys : [(frame, Pose)] triées -> une Pose par frame (tenue avant/après)."""
    keys = sorted(keys, key=lambda k: k[0])
    out = []
    for f in range(n_frames):
        if f <= keys[0][0]:
            out.append(keys[0][1]); continue
        if f >= keys[-1][0]:
            out.append(keys[-1][1]); continue
        i = max(i for i, (kf, _p) in enumerate(keys) if kf <= f)
        f0, p0 = keys[i]; f1, p1 = keys[i + 1]
        out.append(interp(p0, p1, (f - f0) / (f1 - f0)))
    return out


def wiggle(pose, part, t, amp_deg=3.0, period=12.0, decay=20.0):
    """Petits cercles qui ralentissent : rotation additionnelle d'un membre (ou
    du torse si part == 'root') au temps t (frames) après le début de la tenue."""
    a = amp_deg * np.exp(-t / decay)
    ph = 2 * np.pi * t / (period * (1 + t / (2 * decay)))
    dr = Rx(a * np.sin(ph)) @ Rz(a * np.cos(ph))
    p = pose.copy()
    if part == "root":
        p["root"] = (p["root"][0], p["root"][1] @ dr)
    else:
        p[part] = (p[part][0] @ dr, p[part][1])
    return p


# ------------------------------------------------------------------ rendu
COL = {"Torso": (214, 54, 46), "Head": (230, 230, 230), "Right Arm": (80, 200, 110), "Left Arm": (40, 120, 220),
       "Right Leg": (240, 200, 40), "Left Leg": (240, 200, 40)}
FACES = [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)]
# rig de contrôle à faces lettrées (couleurs relevées sur les vidéos TSB, C1
# §4 : F (228,49,32), R (12,181,125), U (26,197,255), L (213,174,17) ; D y
# est un orange-ambre très proche de L : pris ici plus orange pour les
# distinguer sans lire la lettre ; B bleu)
FACES_DIR = {(0, 0, -1): ("F", (228, 49, 32)), (0, 0, 1): ("B", (40, 80, 230)), (1, 0, 0): ("R", (12, 181, 125)),
             (-1, 0, 0): ("L", (213, 174, 17)), (0, 1, 0): ("U", (26, 197, 255)), (0, -1, 0): ("D", (245, 120, 20))}
_POLICES = {}


def _police(taille):
    if taille not in _POLICES:
        try:
            from PIL import ImageFont
            _POLICES[taille] = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", taille)
        except OSError:
            _POLICES[taille] = None
    return _POLICES[taille]


def render(worlds, eye, target, fov=50.0, size=(640, 360), title="", extra=None, sky=(170, 190, 210), backdrop=None, ground=True,
           couleurs=None, ombre=True, contour=(20, 20, 20), faces=False):
    """worlds : liste de dicts {part: (R, p)} (plusieurs persos). Caméra perspective.
    couleurs : {part: rgb} à la place de COL (ex. tout noir = silhouette) ; ombre=False
    et contour=None donnent un aplat pur (test de silhouette des animateurs).
    faces=True : rig de contrôle, chaque face colorée et lettrée selon sa
    direction locale (FACES_DIR). ground : True (dalles autour de l'origine)
    ou (xmin, xmax, zmin, zmax) pour étendre le sol (ex. deux persos à 16 studs)."""
    from PIL import Image, ImageDraw
    W, H = size
    eye = np.asarray(eye, float); target = np.asarray(target, float)
    f = target - eye; f /= np.linalg.norm(f)
    r = np.cross(f, [0, 1.0, 0]); r /= np.linalg.norm(r); u = np.cross(r, f)
    foc = (H / 2) / np.tan(np.radians(fov) / 2)

    def proj(p):
        v = np.asarray(p) - eye
        z = v @ f
        return (W / 2 + foc * (v @ r) / max(z, 1e-3), H / 2 - foc * (v @ u) / max(z, 1e-3)), z

    im = Image.new("RGB", size, sky)
    d = ImageDraw.Draw(im)
    if backdrop:
        backdrop(d, proj, W, H)     # fond remplacé (aplat + lignes radiales), dessiné sous tout
    # sol (dalles)
    polys = []
    gx0, gx1, gz0, gz1 = ground if isinstance(ground, (tuple, list)) else (-12, 12, -12, 12)
    gx0, gz0 = int(gx0) // 2 * 2, int(gz0) // 2 * 2
    for gx in (range(gx0, int(gx1) + 1, 2) if ground else ()):
        for gz in range(gz0, int(gz1) + 1, 2):
            c = [(gx, 0, gz), (gx + 2, 0, gz), (gx + 2, 0, gz + 2), (gx, 0, gz + 2)]
            pts = [proj(p) for p in c]
            if min(z for _p, z in pts) <= 0.1:
                continue
            shade = 120 if (gx + gz) // 2 % 2 == 0 else 110
            polys.append((1e9, [p for p, _z in pts], (shade, shade + 5, shade + 18), None, None))
    light = np.array([0.4, 0.9, 0.3]); light /= np.linalg.norm(light)
    for w in worlds:
        for part, (R, c) in w.items():
            if part not in SIZES:
                continue
            h = np.array(SIZES[part]) / 2
            cs = np.array([[a, b, cc] for a in (-1, 1) for b in (-1, 1) for cc in (-1, 1)]) * h
            vs = (R @ cs.T).T + c
            for fc in FACES:
                q = vs[list(fc)]
                nloc = tuple(int(x) for x in np.sign(np.round(cs[list(fc)].mean(0) / h, 6)))
                n = np.cross(q[1] - q[0], q[2] - q[0]); n /= np.linalg.norm(n) + 1e-9
                if n @ (q.mean(0) - eye) >= 0:
                    continue          # face arrière
                pts = [proj(p) for p in q]
                if min(z for _p, z in pts) <= 0.05:
                    continue
                lettre = None
                if faces:
                    lettre, base = FACES_DIR[nloc]
                    k = (0.78 + 0.22 * max(0.0, n @ light)) if ombre else 1.0
                else:
                    base = (couleurs or COL)[part]
                    k = (0.45 + 0.55 * max(0.0, n @ light)) if ombre else 1.0
                col = tuple(int(min(255, x * k)) for x in base)
                polys.append((float(np.mean([z for _p, z in pts])), [p for p, _z in pts], col, contour, lettre))
    for poly in sorted(polys, key=lambda x: -x[0]):
        _z, pts, col, ol = poly[:4]
        d.polygon(pts, fill=col, outline=ol)
        lettre = poly[4] if len(poly) > 4 else None
        if lettre:
            xs, ys = [p[0] for p in pts], [p[1] for p in pts]
            aire = 0.5 * abs(sum(xs[i] * ys[i - 1] - xs[i - 1] * ys[i] for i in range(len(xs))))
            taille = int(min(40, 0.55 * aire ** 0.5))
            if taille >= 7:
                cx, cy = sum(xs) / len(xs), sum(ys) / len(ys)
                fnt = _police(taille)
                d.text((cx, cy), lettre, fill=(255, 255, 255), font=fnt, anchor="mm", stroke_width=1,
                       stroke_fill=(0, 0, 0)) if fnt else d.text((cx - 3, cy - 5), lettre, fill=(255, 255, 255))
    if extra:
        extra(d, proj)
    if title:
        d.rectangle([0, 0, 8 * len(title) + 8, 16], fill=(0, 0, 0)); d.text((4, 2), title, fill=(255, 230, 120))
    return im


def video(frames_png_dir, out_mp4, fps=60):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", str(fps), "-i", os.path.join(frames_png_dir, "f%04d.png"),
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", out_mp4], check=True)
