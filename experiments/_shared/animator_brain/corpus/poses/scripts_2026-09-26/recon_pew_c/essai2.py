"""Caméra calée sur la grille (repère monde = axes de la grille, -Z = axe G).
python3 essai2.py <t|png> <sortie> '<pose dict>' '<cam dict>' ['<avant>']
cam = {L: cap de la caméra en deg à GAUCHE de -Z (calib), pitch: deg vers le bas,
       roll: deg, fov, d: distance horizontale oeil->torse, beta: le torse est
       vu beta deg à GAUCHE du cap, h: hauteur de l'oeil}"""
import sys, ast
import numpy as np
sys.path.insert(0, "/tmp/claude-0/-home-user-Jeux/4796ac9e-8e41-51f7-91c4-7b92a6a187d0/scratchpad/poing/wf/recon_pew_c")
import rendu as R
import geo_pose as G

def cap(L):
    a = np.radians(L)
    return np.array([-np.sin(a), 0.0, -np.cos(a)])

def cam_grille(tc, L, pitch, roll, fov, d, beta, h):
    hd = cap(L)
    to_torse = cap(L + beta)
    eye = np.array([tc[0], 0, tc[2]]) - d * to_torse
    eye[1] = h
    pr = np.radians(pitch)
    fwd = np.cos(pr) * hd - np.sin(pr) * np.array([0, 1.0, 0])
    return dict(eye=eye, target=eye + fwd, fov=fov, roll=roll)

if __name__ == "__main__":
    t, out, ps, cs = sys.argv[1:5]
    avant = ast.literal_eval(sys.argv[5]) if len(sys.argv) > 5 else (0, 0, -1)
    p = ast.literal_eval(ps); c = ast.literal_eval(cs)
    w = G.pose(p)
    cam = cam_grille(w["Torso"][1], **c)
    src = t if t.startswith('/') else f"/tmp/claude-0/-home-user-Jeux/4796ac9e-8e41-51f7-91c4-7b92a6a187d0/scratchpad/poing/refs/pew/t_{t}.png"
    R.compare(src, w, cam, out, titre=out.split('/')[-1])
    big = R.render([w], cam, (960, 540))
    d = G.descripteurs(w, avant)
    print(G.resume(d))
    print("pieds", d["pieds"], "| oeil", np.round(cam["eye"], 2))
