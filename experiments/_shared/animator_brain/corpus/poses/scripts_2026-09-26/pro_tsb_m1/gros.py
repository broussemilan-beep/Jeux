import json, sys
import numpy as np
import charge as K, geo_pose as G
from PIL import Image, ImageDraw
R = {r['id']: r for r in json.load(open('frappes_tsb.json'))}
CAMS = [(0, 5, 'face (cote cible)'), (90, 5, 'sa droite'), (45, 30, 'az45 el30'), (180, 10, 'dos')]
fid = sys.argv[1]
r = R[fid]; mw = K.mondes(r['anim']); av = tuple(r['avant_vecteur'])
poses = [('ARME', r['images']['arme_max_poing_le_plus_recule']), ('DEPART', r['images']['depart_detente']), ('CONTACT', r['images']['contact'])]
tw = th = 330
im = Image.new('RGB', (tw * len(CAMS), th * len(poses)), (0, 0, 0))
c = mw[r['images']['contact']][1]['Torso'][1].copy(); c[1] = 2.2
for i, (nm, f) in enumerate(poses):
    for k, (az, el, cn) in enumerate(CAMS):
        cam = G.camera_orbite(c, az, el, 9.0, 50, avant=av)
        im.paste(G.rendre(mw[f][1], cam, (tw, th), f"{fid} {nm} f{f} {cn}"), (k * tw, i * th))
im.save(f'gros_{fid}.png'); print(im.size)
