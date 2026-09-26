import numpy as np, sys
from PIL import Image
def horizon(png):
    a = np.asarray(Image.open(png).convert('RGB').resize((960,540))).astype(float)
    lum = a.mean(2); blue = a[:,:,2]-a[:,:,0]
    res = []
    for x in range(20, 960, 60):
        col = lum[:, x]
        # sky bright (>150) above, ground dark (<90) below: first y where 5 consecutive px dark after bright
        y0 = None
        for y in range(5, 535):
            if col[y-3:y].mean() > 140 and col[y:y+4].mean() < 90:
                y0 = y; break
        res.append((x, y0))
    return res
for f in sys.argv[1:]:
    h = horizon(f); pts = [(x,y) for x,y in h if y is not None]
    if len(pts) > 2:
        xs, ys = np.array(pts).T; k, b = np.polyfit(xs, ys, 1)
        print(f.split('/')[-1], 'pente %.3f (%.1f deg), y@480 = %.1f' % (k, np.degrees(np.arctan(k)), k*480+b), pts)
