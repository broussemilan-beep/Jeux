import sys, os, json
sys.path.insert(0, "/home/user/Jeux/experiments/_shared/animator_brain/outils")
import geo_pose as G
import numpy as np
D = "/tmp/claude-0/-home-user-Jeux/4796ac9e-8e41-51f7-91c4-7b92a6a187d0/scratchpad/poing/wf/recon_anime/"
S = "/tmp/claude-0/-home-user-Jeux/4796ac9e-8e41-51f7-91c4-7b92a6a187d0/scratchpad/poing/refs/stills/"

def run(ref, name, params, cam, avant=(0, 0, -1), cible=None):
    w = G.pose(params)
    if cible is None:
        cible = (params.get("x", 0), params.get("hanche", 3.0) - 0.3, params.get("z", 0))
    c = G.camera_orbite(cible, *cam, avant=avant) if len(cam) == 4 else G.camera_orbite(cible, cam[0], cam[1], cam[2], cam[3], avant=avant)
    out = D + "rounds/" + name + ".png"
    G.cote_a_cote(ref, [w], c, sortie=out, titre=name)
    d = G.descripteurs(w, avant=avant)
    print(name, "|", G.resume(d))
    print("   pieds", d["pieds"], "tete", d.get("tete"))
    return w, d, out

M = G.M
def roll_naturel(az, el):
    """roulis tel que aim(d, roll) = pivot sans torsion depuis le repos (bras le long du corps).
    Sans ça, geo_pose.pose() avec roulis 0 met le bloc du bras jusqu'à 1 stud DANS le torse."""
    d = G.az_el_vers_dir(az, el)
    A = M.aim(d, 0.0)
    Rs = M._align(np.array([0, -1.0, 0]), d)
    Q = A.T @ Rs   # rotation autour de Y
    return float(np.degrees(np.arctan2(Q[0, 2], Q[0, 0])))

def nat(p):
    q = dict(p)
    for k in ("RA", "LA"):
        v = q.get(k)
        if v is not None and len(v) == 2:
            q[k] = (v[0], v[1], roll_naturel(v[0], v[1]))
    return q

def runn(ref, name, params, cam, avant=(0, 0, -1), cible=None):
    return run(ref, name, nat(params), cam, avant, cible)

from PIL import Image as _I
def pile(paths, out):
    ims = [_I.open(p) for p in paths]
    W = max(i.width for i in ims); H = sum(i.height for i in ims) + 4 * len(ims)
    o = _I.new("RGB", (W, H)); y = 0
    for i in ims:
        o.paste(i, (0, y)); y += i.height + 4
    o.save(out); return out
