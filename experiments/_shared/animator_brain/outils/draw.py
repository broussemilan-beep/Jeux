"""Dessin fil de fer de poses R6 (3 vues) pour etude visuelle."""
import sys, numpy as np
sys.path.insert(0, '/home/user/Jeux/experiments/_shared')
from PIL import Image, ImageDraw
from animator_brain import roblox_export as X
S = X.RIG["part_sizes"]
EDGES = [(0,1),(0,2),(0,4),(1,3),(1,5),(2,3),(2,6),(3,7),(4,5),(4,6),(5,7),(6,7)]
FACES = [(0,1,3,2),(4,5,7,6),(0,1,5,4),(2,3,7,6),(0,2,6,4),(1,3,7,5)]
COL = {'Torso':(60,60,60),'Head':(170,170,170),'Left Arm':(42,125,225),'Right Arm':(225,85,42),'Left Leg':(130,130,130),'Right Leg':(100,100,100)}
def view_mat(name):
    # base camera : colonnes = droite ecran, haut ecran, vers la camera ; perso regarde -Z
    if name == 'profil':   eye = np.array([1.0, 0.0, 0.0])      # vu de sa droite
    elif name == 'jeu':    eye = np.array([0.35, 0.35, 1.0])    # derriere, un peu a droite et haut
    elif name == 'face34': eye = np.array([0.8, 0.15, -1.0])    # devant 3/4
    elif name == 'dessus': eye = np.array([0.0, 1.0, 0.001])
    f = eye / np.linalg.norm(eye); up = np.array([0,1.0,0]) if name != 'dessus' else np.array([0,0,-1.0])
    r = np.cross(up, f); r /= np.linalg.norm(r); u = np.cross(f, r)
    return np.stack([r, u, f])
def draw(w, view, size=260, sc=30, title='', center=None, fill=True):
    im = Image.new('RGB', (size, size + 18), 'white'); d = ImageDraw.Draw(im)
    M = view_mat(view); c0 = w['Torso'][1] if center is None else center
    polys = []
    for part in ['Left Leg','Right Leg','Torso','Head','Left Arm','Right Arm']:
        r, p = w[part]; sz = np.array(S[part]) / 2
        cs = np.array([[a,b,c] for a in (-1,1) for b in (-1,1) for c in (-1,1)]) * sz
        cs = (r @ cs.T).T + p - c0
        v = (M @ cs.T).T
        P2 = np.c_[v[:,0] * sc + size/2, -v[:,1] * sc + size/2 + 18]
        for f in FACES:
            polys.append((float(np.mean(v[list(f),2])), [tuple(P2[i]) for i in f], COL[part]))
    for depth, pts, col in sorted(polys, key=lambda x: x[0]):
        if fill: d.polygon(pts, fill=tuple(min(255, int(c*0.35+255*0.65)) for c in col), outline=col)
        else: d.line(pts + [pts[0]], fill=col, width=2)
    d.text((4, 2), title, fill='black')
    return im
def sheet(rows, out):
    W = max(sum(im.width for im in r) for r in rows); H = sum(max(im.height for im in r) for r in rows)
    S_ = Image.new('RGB', (W, H), 'white'); y = 0
    for r in rows:
        x = 0
        for im in r: S_.paste(im, (x, y)); x += im.width
        y += max(im.height for im in r)
    S_.save(out)
