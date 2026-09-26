import cv2, numpy as np, sys, glob, json
from vp import lines, vp_ransac
def horizon(im):
    g = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY).astype(int)
    H, W = g.shape
    ys = []
    for x in range(10, W-10, 10):
        col = g[:, x]
        # first row from top where it becomes dark (<90) and stays dark 5 px
        for y in range(5, H-5):
            if (col[y:y+5] < 80).all():
                ys.append((x, y)); break
    ys = np.array(ys)
    # robust line fit
    best=None
    for _ in range(300):
        i,j = np.random.choice(len(ys),2,replace=False)
        if ys[i,0]==ys[j,0]: continue
        a=(ys[j,1]-ys[i,1])/(ys[j,0]-ys[i,0]); b=ys[i,1]-a*ys[i,0]
        inl=np.abs(ys[:,1]-(a*ys[:,0]+b))<3
        if best is None or inl.sum()>best[0]: best=(inl.sum(),a,b)
    return best[1], best[2]
def analyse(path, out=None):
    segs, im = lines(path)
    H, W = im.shape[:2]
    a, b = horizon(im)
    segs = [s for s in segs if min(s[1]-(a*s[0]+b), s[3]-(a*s[2]+b)) > 12]
    np.random.seed(0)
    v1, in1 = vp_ransac(segs)
    rest = [s for s, k in zip(segs, in1) if not k]
    v2, in2 = vp_ransac(rest)
    res = []
    for v, inl, ss, col in ((v1, in1, segs, (0,0,255)), (v2, in2, rest, (0,255,0))):
        for s, k in zip(ss, inl):
            if k: cv2.line(im, tuple(map(int, s[:2])), tuple(map(int, s[2:])), col, 2)
        res.append((v[:2]/v[2]) if abs(v[2])>1e-9 else None)
    cv2.line(im, (0,int(b)), (W,int(a*W+b)), (255,0,255), 1)
    if out: cv2.imwrite(out, im)
    c = np.array([W/2, H/2])
    f = None
    if res[0] is not None and res[1] is not None:
        f2 = -np.dot(res[0]-c, res[1]-c)
        f = np.sqrt(f2) if f2 > 0 else None
    return dict(hor=(a,b), vp=[None if r is None else r.round(1).tolist() for r in res], f=f)
if __name__ == "__main__":
    for p in sys.argv[1:]:
        r = analyse(p, out=p.replace('fr640/', 'vpout_'))
        fov = None if r['f'] is None else 2*np.degrees(np.arctan(180/r['f']))
        print(p, r, 'fovV', fov)
