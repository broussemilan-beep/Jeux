import json, sys
import numpy as np
import charge as K, geo_pose as G
from PIL import Image, ImageDraw
R = {r['id']: r for r in json.load(open('frappes_tsb.json'))}
CAMS = [(0, 5, 'face'), (90, 5, 'sa droite'), (45, 30, '45/30')]
def planche(ids, sortie, tw=210, th=230, poses=('arme_max_poing_le_plus_recule', 'depart_detente', 'contact')):
    noms = {'arme_max_poing_le_plus_recule': 'ARME', 'depart_detente': 'DEPART', 'contact': 'CONTACT'}
    W = tw * len(CAMS) * len(poses) + 8 * (len(poses) - 1)
    im = Image.new('RGB', (W, th * len(ids)), (0, 0, 0))
    for row, fid in enumerate(ids):
        r = R[fid]; mw = K.mondes(r['anim']); av = tuple(r['avant_vecteur'])
        fc = r['images']['contact']
        c = mw[fc][1]['Torso'][1].copy(); c[1] = 2.0
        for j, p in enumerate(poses):
            f = r['images'][p]
            for k, (az, el, nm) in enumerate(CAMS):
                cam = G.camera_orbite(c, az, el, 10.5, 50, avant=av)
                t = G.rendre(mw[f][1], cam, (tw, th), f"{fid} {noms[p]} f{f} {nm}")
                x = (j * len(CAMS) + k) * tw + j * 8
                im.paste(t, (x, row * th))
    im.save(sortie); print(sortie, im.size)
planche(['M1', 'M2', 'M3'], 'planche_M1_M3.png')
planche(['M4', 'WC1', 'WC2', 'WC3'], 'planche_M4_WC.png')
