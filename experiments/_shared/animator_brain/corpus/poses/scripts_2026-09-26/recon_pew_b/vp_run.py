import cv2, numpy as np, sys
from vp import lines, vp_ransac
def analyse(path, out=None, horizon_max=None):
    segs, im = lines(path)
    H, W = im.shape[:2]
    # keep segments in lower part (floor) -- below approx horizon
    segs = [s for s in segs if min(s[1], s[3]) > (horizon_max or 0)]
    v1, in1 = vp_ransac(segs)
    rest = [s for s, k in zip(segs, in1) if not k]
    v2, in2 = vp_ransac(rest)
    res = []
    for v, inl, ss, col in ((v1, in1, segs, (0,0,255)), (v2, in2, rest, (0,255,0))):
        if v is None: res.append(None); continue
        for s, k in zip(ss, inl):
            if k: cv2.line(im, tuple(map(int, s[:2])), tuple(map(int, s[2:])), col, 2)
        res.append((v[:2]/v[2]).tolist() if abs(v[2])>1e-9 else ("inf", (v[:2]/np.linalg.norm(v[:2])).tolist()))
    if out: cv2.imwrite(out, im)
    return res
if __name__ == "__main__":
    for p in sys.argv[1:]:
        print(p, analyse(p, out=p.replace('fr640/', 'vpout_')))
