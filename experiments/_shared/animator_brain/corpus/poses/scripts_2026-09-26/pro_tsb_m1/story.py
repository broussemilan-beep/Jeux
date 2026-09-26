import sys, numpy as np
import charge as K, geo_pose as G
from PIL import Image, ImageDraw
nom = sys.argv[1]; frames = [int(x) for x in sys.argv[2].split(',')] if ',' in sys.argv[2] else list(range(int(sys.argv[2]), int(sys.argv[3])+1, int(sys.argv[4])))
out = sys.argv[-1]
mw = K.mondes(nom)
cams = [(0, 10), (90, 10), (45, 35), (180,10)]
tw, th = 220, 200
sheet = Image.new('RGB', (tw*len(cams), th*len(frames)), (0,0,0))
for r, i in enumerate(frames):
    w = mw[i][1]
    c = w['Torso'][1].copy(); c[1] = max(c[1]-0.3, 1.5)
    for k, (az, el) in enumerate(cams):
        cam = G.camera_orbite(c, az, el, 11, 50)
        im = G.rendre(w, cam, (tw, th), f'{nom} f{i} az{az}')
        sheet.paste(im, (k*tw, r*th))
sheet.save(out)
print(out, sheet.size)
