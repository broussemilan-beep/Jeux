"""
Graphe "chaine de pics" (PIL seul -- pas de matplotlib dans le Python qui
porte bpy) : une ligne par articulation, vitesse normalisee dans le temps,
un trait vertical a chaque pic. Des pics alignes verticalement sur toutes
les lignes = mouvement mecanique (tout le corps culmine a la meme frame) ;
des pics en escalier = chevauchement (le parent culmine, puis la tete, puis
les bras...). C'est la preuve visuelle committee de l'overlap -- une
capture fixe ne peut PAS la montrer.
"""
import numpy as np
from PIL import Image, ImageDraw

from .audit import find_peaks, smooth

ROW_COLORS = [(230, 90, 60), (240, 170, 50), (90, 180, 90), (70, 140, 230), (150, 100, 220),
              (200, 90, 160), (60, 170, 180)]


def peak_chain_chart(clip, sig, rows, t0, t1, title, out_path, width=1400, row_h=86, fps=30):
    m = (clip.t >= t0) & (clip.t <= t1)
    t = clip.t[m]
    left, right, top = 150, 30, 56
    H = top + row_h * len(rows) + 40
    img = Image.new("RGB", (width, H), (252, 250, 245))
    d = ImageDraw.Draw(img)
    d.text((12, 12), title, fill=(20, 20, 30))
    plot_w = width - left - right

    def x_of(tt):
        return left + (tt - t0) / (t1 - t0) * plot_w

    # grille : une ligne toutes les 5 frames a 30 fps, etiquette toutes les 15
    f0, f1 = int(np.ceil(t0 * fps)), int(np.floor(t1 * fps))
    for f in range(f0, f1 + 1):
        if f % 5:
            continue
        x = x_of(f / fps)
        d.line([(x, top - 6), (x, H - 30)], fill=(225, 222, 214) if f % 15 else (200, 196, 186))
        if f % 15 == 0:
            d.text((x - 10, H - 26), f"{f}f", fill=(110, 110, 110))

    for r, (label, key) in enumerate(rows):
        y0 = top + r * row_h
        base = y0 + row_h - 12
        col = ROW_COLORS[r % len(ROW_COLORS)]
        d.text((12, y0 + row_h // 2 - 6), label, fill=col)
        s = smooth(sig[key], 3)
        smax = s.max() if s.max() > 1e-9 else 1.0
        sw = s[m] / smax
        pts = [(x_of(tt), base - v * (row_h - 22)) for tt, v in zip(t, sw)]
        if len(pts) > 1:
            d.line(pts, fill=col, width=2)
        for i in find_peaks(s, 0.15 * smax):
            if t0 <= clip.t[i] <= t1:
                x = x_of(clip.t[i])
                d.line([(x, y0 + 4), (x, base)], fill=col, width=1)
                d.ellipse([x - 3, base - s[i] / smax * (row_h - 22) - 3, x + 3,
                           base - s[i] / smax * (row_h - 22) + 3], fill=col)
        d.line([(left, base), (width - right, base)], fill=(200, 200, 200))
    img.save(out_path)
    return out_path


def side_by_side(paths, out_path, gap=12, bg=(255, 255, 255)):
    ims = [Image.open(p) for p in paths]
    W = max(i.width for i in ims)
    H = sum(i.height for i in ims) + gap * (len(ims) - 1)
    out = Image.new("RGB", (W, H), bg)
    y = 0
    for i in ims:
        out.paste(i, (0, y))
        y += i.height + gap
    out.save(out_path)
    return out_path


def onion_skin(clip, t0, t1, step, title, out_path, trails=(("Right Arm", "bottom"), ("Left Arm", "bottom"),
                                                          ("Head", "top")),
               width=900, height=620, scale=None, margin=40):
    """Vue de PROFIL (axe horizontal = avant du personnage, -Z ; vertical
    = Y), une silhouette par pas de temps (de plus en plus opaque), et les
    TRAJECTOIRES continues des mains et du haut de la tete. Ce que montre
    ce graphe et qu'aucune capture fixe ne montre : les ARCS (une main qui
    decrit une courbe, pas une droite) et le RETARD des extremites (la
    trainee de la main en retard sur le corps)."""
    ts = np.arange(t0, t1 + 1e-9, step)
    idxs = [clip.idx(t) for t in ts]
    parts = [p for p in clip.parts if p != clip.rig.root]
    corners = np.array([[sx, sy, sz] for sx in (-.5, .5) for sy in (-.5, .5) for sz in (-.5, .5)])

    def proj(p):
        return np.array([-p[2], p[1]])
    pts_all = []
    polys = []
    for k, i in enumerate(idxs):
        frame_polys = []
        for p in parts:
            size = np.array(clip.rig.part_sizes[p])
            w = clip.world_pos[p][i] + (clip.world_rot[p][i] @ (corners * size).T).T
            q = np.array([proj(v) for v in w])
            pts_all.append(q)
            frame_polys.append(q)
        polys.append(frame_polys)
    trail_pts = {}
    dense = range(clip.idx(t0), clip.idx(t1) + 1)
    for part, end in trails:
        tip = clip.tip(part, end)
        trail_pts[part] = np.array([proj(tip[i]) for i in dense])
        pts_all.append(trail_pts[part])
    allp = np.vstack(pts_all)
    lo, hi = allp.min(axis=0), allp.max(axis=0)
    s = scale or min((width - 2 * margin) / max(1e-6, hi[0] - lo[0]),
                     (height - 2 * margin - 30) / max(1e-6, hi[1] - lo[1]))

    def to_px(q):
        return (margin + (q[0] - lo[0]) * s, height - margin - (q[1] - lo[1]) * s)
    img = Image.new("RGBA", (width, height), (252, 250, 245, 255))
    d = ImageDraw.Draw(img, "RGBA")
    d.text((12, 10), title, fill=(20, 20, 30, 255))
    gy = to_px(np.array([lo[0], 0.0]))[1]
    if margin <= gy <= height - margin + 5:
        d.line([(margin, gy), (width - margin, gy)], fill=(180, 170, 150, 255), width=1)
    n = len(polys)
    for k, frame_polys in enumerate(polys):
        a = int(40 + 180 * (k + 1) / n)
        col = (60, 50, 110, a)
        for q in frame_polys:
            hull = _hull2d(q)
            d.polygon([to_px(v) for v in hull], outline=col)
    tcol = {"Right Arm": (40, 120, 230, 255), "Left Arm": (150, 90, 220, 255), "Head": (220, 90, 60, 255)}
    for part, pts in trail_pts.items():
        d.line([to_px(v) for v in pts], fill=tcol.get(part, (0, 0, 0, 255)), width=2)
    y = height - 22
    x = 12
    for part, c in tcol.items():
        if part in trail_pts:
            d.rectangle((x, y + 4, x + 14, y + 10), fill=c)
            lbl = {"Right Arm": "main droite", "Left Arm": "main gauche", "Head": "haut de la tete"}[part]
            d.text((x + 18, y), lbl, fill=(40, 40, 40, 255))
            x += 150
    img.convert("RGB").save(out_path)
    return out_path


def _hull2d(pts):
    pts = sorted(set(map(tuple, np.round(pts, 5))))
    if len(pts) <= 2:
        return [np.array(p) for p in pts]

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lower, upper = [], []
    for p in pts:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)
    for p in reversed(pts):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)
    return [np.array(p) for p in lower[:-1] + upper[:-1]]


def side_by_side_h(paths, out_path, gap=12, bg=(255, 255, 255)):
    ims = [Image.open(p) for p in paths]
    H = max(i.height for i in ims)
    W = sum(i.width for i in ims) + gap * (len(ims) - 1)
    out = Image.new("RGB", (W, H), bg)
    x = 0
    for i in ims:
        out.paste(i, (x, 0))
        x += i.width + gap
    out.save(out_path)
    return out_path
