"""Ajuste caméra (d, beta, h) + pose sur des repères 2D lus à la main dans la ref.
Minimisation maison (Nelder-Mead numpy, pas de scipy dans ce bac à sable)."""
import sys, json
import numpy as np
sys.path.insert(0, "/tmp/claude-0/-home-user-Jeux/4796ac9e-8e41-51f7-91c4-7b92a6a187d0/scratchpad/poing/wf/recon_pew_c")
sys.path.insert(0, "/home/user/Jeux/experiments/_shared/animator_brain/outils")
import geo_pose as G
import rendu  # noqa
from essai2 import cam_grille

W, H = 960, 540

def project(cam, P):
    eye, target, fov, roll = cam["eye"], cam["target"], cam["fov"], cam["roll"]
    f = target - eye; f = f / np.linalg.norm(f)
    r = np.cross(f, [0, 1.0, 0]); r /= np.linalg.norm(r); u = np.cross(r, f)
    a = np.radians(roll)
    r, u = np.cos(a) * r + np.sin(a) * u, -np.sin(a) * r + np.cos(a) * u
    foc = (H / 2) / np.tan(np.radians(fov) / 2)
    v = np.asarray(P, float) - eye; z = v @ f
    return np.array([W / 2 + foc * (v @ r) / z, H / 2 - foc * (v @ u) / z])

LOCAL = {  # nom -> (partie, point local)
    "RA_tip": ("Right Arm", (0, -1, 0)), "RA_top": ("Right Arm", (0, 1, 0)), "RA_gant": ("Right Arm", (0, -1 / 3, 0)),
    "LA_tip": ("Left Arm", (0, -1, 0)), "LA_top": ("Left Arm", (0, 1, 0)), "LA_gant": ("Left Arm", (0, -1 / 3, 0)),
    "T_bas_D_av": ("Torso", (1, -1, -0.5)), "T_bas_G_av": ("Torso", (-1, -1, -0.5)),
    "T_haut_D_av": ("Torso", (1, 1, -0.5)), "T_haut_G_av": ("Torso", (-1, 1, -0.5)),
    "T_bas_D_ar": ("Torso", (1, -1, 0.5)), "T_bas_G_ar": ("Torso", (-1, -1, 0.5)),
    "T_haut_D_ar": ("Torso", (1, 1, 0.5)), "T_haut_G_ar": ("Torso", (-1, 1, 0.5)),
    "T_av": ("Torso", (0, 0, -0.5)), "T_c": ("Torso", (0, 0, 0)), "T_cou": ("Torso", (0, 1, 0)),
    "T_D": ("Torso", (1, 0, 0)), "T_G": ("Torso", (-1, 0, 0)),
    "Tete": ("Head", (0, 0, 0)),
    "RL_tip": ("Right Leg", (0, -1, 0)), "LL_tip": ("Left Leg", (0, -1, 0)),
    "RL_c": ("Right Leg", (0, 0, 0)), "LL_c": ("Left Leg", (0, 0, 0)),
}

def point(w, name):
    if name.startswith("@"):   # "@Torso:x,y,z" point local libre
        part, xyz = name[1:].split(":")
        R, p = w[part]
        return p + R @ np.array([float(v) for v in xyz.split(",")])
    part, loc = LOCAL[name]
    R, p = w[part]
    return p + R @ np.array(loc, float)

def build(x, spec):
    """x -> (params pose, params cam) selon spec = liste de (clé, chemin)"""
    pose = json.loads(json.dumps(spec["pose0"]))
    cam = dict(spec["cam0"])
    for v, (kind, key, idx) in zip(x, spec["vars"]):
        if kind == "cam":
            cam[key] = v
        else:
            val = list(pose.get(key, [0, 0, 0]))
            val[idx] = v
            pose[key] = val
    for k in ("buste", "RA", "LA", "RL", "LL", "tete"):
        if k in pose and isinstance(pose[k], list):
            pose[k] = tuple(pose[k])
    return pose, cam

def cost(x, spec, detail=False):
    pose, cam = build(x, spec)
    w = G.pose(pose)
    c = cam_grille(w["Torso"][1], **cam)
    err = 0; det = {}
    for name, (uv, wt) in spec["marks"].items():
        pr = project(c, point(w, name))
        e = np.linalg.norm(pr - np.array(uv))
        det[name] = (pr.round(0).tolist(), round(float(e), 1))
        err += wt * min(e, 150) ** 2
    for name, (tgt, wt) in spec.get("vers_cam", {}).items():
        part = {"RA": "Right Arm", "LA": "Left Arm"}[name]
        R_, p_ = w[part]
        dv = R_ @ np.array([0, -1.0, 0]); top = p_ + R_ @ np.array([0, 1.0, 0])
        tc = c["eye"] - top; tc /= np.linalg.norm(tc)
        ang = np.degrees(np.arccos(np.clip(dv @ tc, -1, 1)))
        det["angle_cam_" + name] = round(float(ang), 1)
        err += wt * max(0.0, ang - tgt) ** 2 * 10
    for (a_, b_, ang, wt) in spec.get("dirs", []):
        pa, pb = project(c, point(w, a_)), project(c, point(w, b_))
        v = pb - pa
        got = np.degrees(np.arctan2(v[0], -v[1]))   # 0 = vers le haut de l'image, + = penche à droite
        e = (got - ang + 180) % 360 - 180
        det["dir_" + a_ + ">" + b_] = (round(float(got), 1), round(float(e), 1))
        err += wt * (e * 3) ** 2
    for name, (bb, wt) in spec.get("bbox", {}).items():
        part = {"RA": "Right Arm", "LA": "Left Arm"}[name]
        R_, p_ = w[part]
        cs = [p_ + R_ @ np.array([a, -1.0, b]) for a in (-0.5, 0.5) for b in (-0.5, 0.5)]
        pr = np.array([project(c, q) for q in cs])
        got = np.array([pr[:, 0].min(), pr[:, 1].min(), pr[:, 0].max(), pr[:, 1].max()])
        e = np.abs(got - np.array(bb)).mean()
        det["bbox_" + name] = (got.round(0).tolist(), round(float(e), 1))
        err += wt * min(e, 150) ** 2 * 4
    if spec.get("masque") is not None:
        ref, care = spec["masque"]
        im = np.asarray(rendu.render([w], c, (ref.shape[1], ref.shape[0]), flat=True))[:, :, 0] > 200
        a = im & care; b = ref & care
        iou = (a & b).sum() / max(1, (a | b).sum())
        det["IoU"] = round(float(iou), 3)
        err += spec.get("w_iou", 3000) * (1 - iou)
    # prior léger
    for (kind, key, idx), v, (mu, sd) in zip(spec["vars"], x, spec["prior"]):
        err += ((v - mu) / sd) ** 2 * 25
    return (err, det) if detail else err

def nelder_mead(f, x0, step, iters=1500, tol=1e-6):
    n = len(x0)
    pts = [np.array(x0, float)] + [np.array(x0, float) + np.eye(n)[i] * step[i] for i in range(n)]
    vals = [f(p) for p in pts]
    for it in range(iters):
        order = np.argsort(vals); pts = [pts[i] for i in order]; vals = [vals[i] for i in order]
        if abs(vals[-1] - vals[0]) < tol * (abs(vals[0]) + 1e-9) and it > 200:
            break
        c = np.mean(pts[:-1], axis=0)
        xr = c + (c - pts[-1]); fr = f(xr)
        if fr < vals[0]:
            xe = c + 2 * (c - pts[-1]); fe = f(xe)
            pts[-1], vals[-1] = (xe, fe) if fe < fr else (xr, fr)
        elif fr < vals[-2]:
            pts[-1], vals[-1] = xr, fr
        else:
            xc = c + 0.5 * (pts[-1] - c); fc = f(xc)
            if fc < vals[-1]:
                pts[-1], vals[-1] = xc, fc
            else:
                pts = [pts[0] + 0.5 * (p - pts[0]) for p in pts]; vals = [f(p) for p in pts]
    i = int(np.argmin(vals))
    return pts[i], vals[i]

def run(spec, restarts=4, seed=0):
    rng = np.random.default_rng(seed)
    x0 = np.array([v for v in spec["x0"]], float)
    step = np.array(spec["step"], float)
    best = nelder_mead(lambda x: cost(x, spec), x0, step)
    for k in range(restarts):
        xs = best[0] + rng.normal(0, 1, len(x0)) * step * 0.7
        cand = nelder_mead(lambda x: cost(x, spec), xs, step)
        if cand[1] < best[1]:
            best = cand
    return best


def prep_masque(t, excl_ref, care_excl, scale=0.5):
    import cv2
    from masque import masque_blanc
    m = masque_blanc(t, excl_ref)
    care = np.ones_like(m)
    for poly in care_excl:
        cv2.fillPoly(care, [np.array(poly, np.int32)], 0)
    W2, H2 = int(960 * scale), int(540 * scale)
    m = cv2.resize(m, (W2, H2), interpolation=cv2.INTER_NEAREST) > 0
    care = cv2.resize(care, (W2, H2), interpolation=cv2.INTER_NEAREST) > 0
    return m, care
