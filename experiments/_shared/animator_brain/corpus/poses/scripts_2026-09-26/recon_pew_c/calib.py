"""Calibre la caméra d'une image de ref Pew à partir de la grille du sol :
2 points de fuite (familles orthogonales) -> focale, tangage, roulis, lacet
de la caméra par rapport aux axes de la grille (modulo 90 deg)."""
import cv2, numpy as np, sys, itertools
W, H = 960, 540
cx, cy = W / 2, H / 2

def segments(png, ymin_fn, excl=()):
    im = cv2.imread(png); im = cv2.resize(im, (W, H))
    g = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    th = cv2.adaptiveThreshold(g, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 15, -12)
    ys, xs = np.mgrid[0:H, 0:W]
    th[ys < ymin_fn(xs)] = 0
    for (a, b, c, d) in excl:
        th[b:d, a:c] = 0
    L = cv2.HoughLinesP(th, 1, np.pi / 720, 50, minLineLength=70, maxLineGap=6)
    return im, [tuple(map(float, l[0])) for l in (L if L is not None else [])]

def vp_ransac(segs, it=4000, tol=2.5, rng=np.random.default_rng(0)):
    lines = [np.cross([x1, y1, 1], [x2, y2, 1]) for x1, y1, x2, y2 in segs]
    lines = [l / np.linalg.norm(l[:2]) for l in lines]
    best = (0, None, None)
    for _ in range(it):
        i, j = rng.choice(len(lines), 2, replace=False)
        v = np.cross(lines[i], lines[j])
        if abs(v[2]) < 1e-9: continue
        v = v / v[2]
        inl = []
        for k, (s, l) in enumerate(zip(segs, lines)):
            # angular consistency: distance from segment endpoints' line to v measured as angle
            x1, y1, x2, y2 = s; m = np.array([(x1 + x2) / 2, (y1 + y2) / 2])
            d1 = np.array([x2 - x1, y2 - y1]); d2 = v[:2] - m
            ang = np.degrees(np.arccos(abs(d1 @ d2) / (np.linalg.norm(d1) * np.linalg.norm(d2) + 1e-9)))
            if ang < tol: inl.append(k)
        if len(inl) > best[0]: best = (len(inl), v, inl)
    # refine with least squares on inliers
    A = np.array([lines[k] for k in best[2]])
    _, _, vt = np.linalg.svd(A)
    v = vt[-1]; v = v / v[2] if abs(v[2]) > 1e-12 else v
    return v, best[2]

def calib(png, ymin_fn=lambda x: 0 * x + 150, out=None, excl=(), tol=1.2):
    im, segs = segments(png, ymin_fn, excl)
    v1, in1 = vp_ransac(segs, tol=tol)
    rest = [s for k, s in enumerate(segs) if k not in in1]
    v2, in2 = vp_ransac(rest, tol=tol)
    p1 = v1[:2] - [cx, cy]; p2 = v2[:2] - [cx, cy]
    f2 = -(p1 @ p2)
    res = {"v1": v1[:2].round(1).tolist(), "v2": v2[:2].round(1).tolist(), "n1": len(in1), "n2": len(in2)}
    if f2 > 0:
        f = np.sqrt(f2)
        d1 = np.array([p1[0], p1[1], f]); d1 /= np.linalg.norm(d1)
        d2 = np.array([p2[0], p2[1], f]); d2 /= np.linalg.norm(d2)
        # image coords: x right, y DOWN, z forward. world up = cross of the two ground dirs (sign: pointing to -y image)
        up = np.cross(d1, d2); up /= np.linalg.norm(up)
        if up[1] > 0: up = -up
        pitch = np.degrees(np.arcsin(up[2]))           # >0 : caméra regarde vers le bas
        roll = np.degrees(np.arctan2(up[0], -up[1]))   # >0 : haut du monde penche vers la droite de l'image
        # lacet de la caméra par rapport à l'axe de grille d1 : angle entre cap caméra (z projeté au sol) et d1
        zc = np.array([0, 0, 1.0]); zh = zc - (zc @ up) * up; zh /= np.linalg.norm(zh)
        rt = np.cross(up, zh)  # vecteur "droite" au sol (image x) — signe vérifié par d1.x
        a1 = np.degrees(np.arctan2(d1 @ rt, d1 @ zh))
        res.update(fov=round(float(np.degrees(2 * np.arctan(cy / f))), 1), f=round(float(f), 1),
                   pitch=round(float(pitch), 1), roll=round(float(roll), 1), axe1_vs_cap=round(float(a1), 1))
    if out:
        for k, s in enumerate(segs):
            c = (0, 0, 255) if k in in1 else ((0, 255, 0) if s in [rest[j] for j in in2] else (120, 120, 120))
            cv2.line(im, tuple(map(int, s[:2])), tuple(map(int, s[2:])), c, 2)
        cv2.imwrite(out, im)
    return res

if __name__ == "__main__":
    t = sys.argv[1]
    a, b = float(sys.argv[2]), float(sys.argv[3])
    ex = eval(sys.argv[4]) if len(sys.argv) > 4 else ()
    print(t, calib(f"../../refs/pew/t_{t}.png" if len(t) == 5 else t, lambda x: a + b * x, out=f"calib_{t.split('/')[-1]}.png", excl=ex))
