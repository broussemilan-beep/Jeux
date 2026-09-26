import sys; sys.path.insert(0, '.')
from fit import *
import numpy as np

def projector(cam, W, H):
    eye, tgt, fov = cam
    eye = np.asarray(eye, float); f = np.asarray(tgt, float) - eye; f /= np.linalg.norm(f)
    r = np.cross(f, [0, 1.0, 0]); r /= np.linalg.norm(r); u = np.cross(r, f)
    foc = (H / 2) / np.tan(np.radians(fov) / 2)
    def P(p):
        v = np.asarray(p, float) - eye
        z = v @ f
        return np.array([W / 2 + foc * (v @ r) / z, H / 2 - foc * (v @ u) / z])
    return P

def corners(w, part, sel=None):
    R, c = w[part]
    h = np.array(M.SIZES[part]) / 2 if hasattr(M, 'SIZES') else None
    out = []
    for a in (-1, 1):
        for b in (-1, 1):
            for cc in (-1, 1):
                loc = np.array([a, b, cc]) * h
                if sel is not None and not sel(a, b, cc):
                    continue
                out.append(c + R @ loc)
    return out
import moon as M

def bbox(pts):
    pts = np.array(pts); return np.array([pts[:, 0].min(), pts[:, 0].max(), pts[:, 1].min(), pts[:, 1].max()])

def build(x, spec):
    """x -> (params, camera-args)"""
    names = spec['names']; v = dict(spec['fixed']); v.update(dict(zip(names, x)))
    p = {'hanche': v.get('hanche', 2.4), 'buste': (v.get('lacet', 0.0), v['pav'], v['pco']), 'tete': (0, 15),
         'RA': (v['raz'], v['rel'], v.get('rro', 0.0)), 'LA': (v['laz'], v['lel'], v.get('lro', 0.0)),
         'RL': ('pied', (1.0, 0, -0.6)), 'LL': ('pied', (-1.0, 0, 0.6))}
    return p, v

def residuals(x, spec, obs, W, H, pitch):
    p, v = build(x, spec)
    w = G.pose(p)
    cam = cam3(w, v['caz'], v['cel'], v['cd'], pitch, v['cyo'])
    P = projector(cam, W, H)
    res = []
    for key, target, wt in obs:
        kind, part = key
        if kind == 'Dface':      # hand-end face bbox
            pts = [P(q) for q in corners(w, part, lambda a, b, c: b == -1)]
            val = bbox(pts)
        elif kind == 'Uface':
            pts = [P(q) for q in corners(w, part, lambda a, b, c: b == 1)]
            val = bbox(pts)
        elif kind == 'box':
            val = bbox([P(q) for q in corners(w, part)])
        elif kind == 'torso_left':    # [min x, top y of left side, bottom y of left side]
            pts = np.array([P(q) for q in corners(w, 'Torso')])
            left = pts[np.argsort(pts[:, 0])[:4]]
            val = np.array([pts[:, 0].min(), left[:, 1].min(), left[:, 1].max()])
        elif kind == 'torso_bottom':   # part = x0 ; y of the front-face bottom edge at x0
            a_ = P(w['Torso'][1] + w['Torso'][0] @ np.array([1, -1, -0.5]))
            b_ = P(w['Torso'][1] + w['Torso'][0] @ np.array([-1, -1, -0.5]))
            x0 = part
            tt = (x0 - a_[0]) / (b_[0] - a_[0] + 1e-9)
            val = np.array([a_[1] + tt * (b_[1] - a_[1])])
        elif kind == 'torso_top_left':  # front-face top corner on his right
            val = P(w['Torso'][1] + w['Torso'][0] @ np.array([1, 1, -0.5]))
        elif kind == 'torso_bot_left':
            val = P(w['Torso'][1] + w['Torso'][0] @ np.array([1, -1, -0.5]))
        elif kind == 'head':
            R, c = w['Head']; val = P(c)
        t = np.array(target, float)
        m = ~np.isnan(t)
        res.extend(((val - t)[m] * wt).tolist())
    return np.array(res)

def lm(x0, spec, obs, W, H, pitch, it=200, lam=1e-2):
    x = np.array(x0, float)
    r = residuals(x, spec, obs, W, H, pitch); cost = r @ r
    for k in range(it):
        J = np.zeros((len(r), len(x)))
        for i in range(len(x)):
            dx = np.zeros(len(x)); dx[i] = 1e-3 * max(1.0, abs(x[i]))
            J[:, i] = (residuals(x + dx, spec, obs, W, H, pitch) - r) / dx[i]
        A = J.T @ J; g = J.T @ r
        improved = False
        for _ in range(12):
            step = np.linalg.solve(A + lam * np.diag(np.diag(A) + 1e-6), -g)
            xn = x + step
            rn = residuals(xn, spec, obs, W, H, pitch); cn = rn @ rn
            if cn < cost:
                x, r, cost = xn, rn, cn; lam = max(lam / 3, 1e-7); improved = True; break
            lam *= 4
        if not improved or np.abs(step).max() < 1e-4:
            break
    return x, cost, r
