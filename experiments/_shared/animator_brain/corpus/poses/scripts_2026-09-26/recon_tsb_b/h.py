import sys, json
sys.path.insert(0, "/home/user/Jeux/experiments/_shared/animator_brain/outils")
import geo_pose as G
import numpy as np
REF = "/tmp/claude-0/-home-user-Jeux/4796ac9e-8e41-51f7-91c4-7b92a6a187d0/scratchpad/poing/refs/tsb/t_%s.png"
OUT = "/tmp/claude-0/-home-user-Jeux/4796ac9e-8e41-51f7-91c4-7b92a6a187d0/scratchpad/poing/wf/recon_tsb_b/"

def essai(t, nom, p, cam, avant=(0, 0, -1), cible=None):
    """cam = (az, el, dist, fov) ; cible = point regardé (défaut centre torse)."""
    w = G.pose(p)
    c = cible if cible is not None else w["Torso"][1]
    cm = G.camera_orbite(c, cam[0], cam[1], cam[2], cam[3], avant=avant)
    G.cote_a_cote(REF % t, [w], cm, sortie=OUT + nom + ".png", titre=nom)
    d = G.descripteurs(w, avant)
    print(nom, "|", G.resume(d))
    print("   pieds", d["pieds"], "tete", d.get("tete"))
    return w, d

import moon as MM
def bbox(w, part, cam, W=520, H=360):
    """bbox 2D (x0,y0,x1,y1) d'une pièce, caméra (oeil, cible, fov), panneau 520x360."""
    eye, tgt, fov = cam
    eye = np.asarray(eye, float); tgt = np.asarray(tgt, float)
    f = tgt - eye; f /= np.linalg.norm(f)
    r = np.cross(f, [0, 1.0, 0]); r /= np.linalg.norm(r); u = np.cross(r, f)
    foc = (H / 2) / np.tan(np.radians(fov) / 2)
    R, c = w[part]
    h = np.array(MM.SIZES[part]) / 2
    cs = np.array([[a, b, cc] for a in (-1, 1) for b in (-1, 1) for cc in (-1, 1)]) * h
    vs = (R @ cs.T).T + c
    pts = []
    for v in vs:
        d = v - eye; z = d @ f
        pts.append((W / 2 + foc * (d @ r) / max(z, 1e-3), H / 2 - foc * (d @ u) / max(z, 1e-3)))
    pts = np.array(pts)
    return tuple(np.round([pts[:, 0].min(), pts[:, 1].min(), pts[:, 0].max(), pts[:, 1].max()]).astype(int))

def cam_de(w, cam, cible=None, avant=(0, 0, -1)):
    c = cible if cible is not None else w["Torso"][1]
    return G.camera_orbite(c, cam[0], cam[1], cam[2], cam[3], avant=avant)

from PIL import Image as _I
def planche(noms, sortie):
    ims = [_I.open(OUT + n + ".png") for n in noms]
    W, H = ims[0].size
    out = _I.new("RGB", (W, H * len(ims)))
    for i, im in enumerate(ims):
        out.paste(im, (0, i * H))
    out.save(OUT + sortie)

# ---- pose2 : comme G.pose, mais membres orientés par la rotation MINIMALE depuis
# le repos (comme une vraie épaule/hanche R6 qu'on tourne), pas par aim() dont le
# roulis par défaut met le bras DANS le torse (x=0.5 au repos). Roulis optionnel
# = rotation autour de l'axe du membre APRÈS la rotation minimale.
def _rot_axe(d, ang):
    d = d / np.linalg.norm(d); a = np.radians(ang)
    K = np.array([[0, -d[2], d[1]], [d[2], 0, -d[0]], [-d[1], d[0], 0]])
    return np.eye(3) + np.sin(a) * K + (1 - np.cos(a)) * (K @ K)

def pose2(p):
    lac, pen, cote = p.get("buste", (0.0, 0.0, 0.0))
    Rt = MM.E(lac, -pen, -cote)
    q = MM.neutral(p.get("hanche", 3.0))
    q["root"] = (np.array([p.get("x", 0.0), p.get("hanche", 3.0), p.get("z", 0.0)]), Rt)
    for k, part in {**G.BRAS, **G.JAMBES}.items():
        v = p.get(k)
        if v is None or (isinstance(v, tuple) and v and v[0] == "pied"):
            continue
        d = G.az_el_vers_dir(v[0], v[1])
        R = MM._align(np.array([0, -1.0, 0]), d)
        if len(v) > 2:
            R = _rot_axe(d, v[2]) @ R
        q[part] = (R, np.zeros(3))
    th = p.get("tete")
    if th is not None:
        q["Head"] = (MM.E(th[0], -th[1], 0.0), np.zeros(3))
    for k, part in G.JAMBES.items():
        v = p.get(k)
        if isinstance(v, tuple) and v and v[0] == "pied":
            MM.plant(q, part, np.asarray(v[1], float))
    return MM.world(q)

def essai2(t, nom, p, cam, avant=(0, 0, -1), cible=None):
    w = pose2(p)
    c = cible if cible is not None else w["Torso"][1]
    cm = G.camera_orbite(c, cam[0], cam[1], cam[2], cam[3], avant=avant)
    G.cote_a_cote(REF % t, [w], cm, sortie=OUT + nom + ".png", titre=nom)
    d = G.descripteurs(w, avant)
    print(nom, "|", G.resume(d))
    print("   pieds", d["pieds"], "tete", d.get("tete"))
    return w, d

def essai3(t, nom, p, oeil, cible, fov, avant=(0, 0, -1), extra=None):
    """Caméra explicite (oeil, cible monde)."""
    w = pose2(p)
    cm = (np.asarray(oeil, float), np.asarray(cible, float), fov)
    mondes = [w] + (extra or [])
    G.cote_a_cote(REF % t, mondes, cm, sortie=OUT + nom + ".png", titre=nom)
    d = G.descripteurs(w, avant)
    print(nom, "|", G.resume(d))
    print("   pieds", d["pieds"], "tete", d.get("tete"))
    return w, d
