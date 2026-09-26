import cv2, numpy as np, glob, sys, json
def lines(path, show=None):
    im = cv2.imread(path); H, W = im.shape[:2]
    g = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    e = cv2.Canny(g, 60, 160)
    L = cv2.HoughLinesP(e, 1, np.pi/360, 40, minLineLength=45, maxLineGap=6)
    out = []
    if L is None: return out, im
    for x1,y1,x2,y2 in L[:,0]:
        out.append((x1,y1,x2,y2))
    return out, im
def vp_ransac(segs, it=3000, tol_deg=1.0, rng=np.random.default_rng(0)):
    # homogeneous lines
    S = np.array(segs, float)
    if len(S) < 2: return None, []
    p1 = np.c_[S[:,0:2], np.ones(len(S))]; p2 = np.c_[S[:,2:4], np.ones(len(S))]
    Ls = np.cross(p1, p2)
    best = (0, None, None)
    ln = np.hypot(S[:,2]-S[:,0], S[:,3]-S[:,1])
    for _ in range(it):
        i, j = rng.choice(len(S), 2, replace=False)
        v = np.cross(Ls[i], Ls[j])
        if abs(v[2]) < 1e-9: v = v / (np.linalg.norm(v[:2])+1e-12); vp = None
        # angle between segment dir and direction from midpoint to vp
        mid = (S[:,0:2]+S[:,2:4])/2
        d = S[:,2:4]-S[:,0:2]; d /= np.linalg.norm(d,axis=1)[:,None]
        if abs(v[2]) > 1e-9:
            vpt = v[:2]/v[2]; t = vpt - mid
        else:
            t = np.tile(v[:2], (len(S),1))
        t /= (np.linalg.norm(t,axis=1)[:,None]+1e-12)
        ang = np.degrees(np.arccos(np.clip(np.abs((d*t).sum(1)),0,1)))
        inl = ang < tol_deg
        sc = ln[inl].sum()
        if sc > best[0]: best = (sc, v, inl)
    return best[1], best[2]
