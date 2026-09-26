import cv2, numpy as np, sys
t = sys.argv[1]
im = cv2.imread(f'../../refs/pew/t_{t}.png'); im = cv2.resize(im, (960,540))
g = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
# grid lines are bright thin lines on dark ground; keep below horizon
hy = int(sys.argv[2]) if len(sys.argv) > 2 else 140
mask = np.zeros_like(g); mask[hy+5:, :] = 255
th = cv2.adaptiveThreshold(g, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 15, -12)
th = cv2.bitwise_and(th, mask)
L = cv2.HoughLinesP(th, 1, np.pi/360, 60, minLineLength=90, maxLineGap=8)
out = im.copy()
segs = []
for l in (L if L is not None else []):
    x1,y1,x2,y2 = l[0]
    ang = np.degrees(np.arctan2(y2-y1, x2-x1))
    segs.append((x1,y1,x2,y2,ang))
    cv2.line(out,(x1,y1),(x2,y2),(0,0,255),1)
cv2.imwrite(f'lignes_{t}.png', out)
# intersect pairs with the horizon y=hline: x where line reaches horizon row
import collections
for s in segs:
    x1,y1,x2,y2,a = s
    if abs(y2-y1) < 1: continue
    xh = x1 + (hy - y1) * (x2-x1)/(y2-y1)
    print(f"{a:7.1f}  ({x1},{y1})-({x2},{y2})  x@horizon {xh:8.0f}")
