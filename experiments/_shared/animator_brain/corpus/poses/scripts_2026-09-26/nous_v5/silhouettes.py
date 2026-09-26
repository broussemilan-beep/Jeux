import sys, numpy as np
from PIL import Image
sys.path.insert(0, "/home/user/Jeux/experiments/_shared/animator_brain/outils")
import geo_pose as G, moon as M
W = G.mondes_rbxmx("/home/user/Jeux/experiments/r6_un_seul_coup/output/usc_attaquant.rbxmx")
off = np.array([W[271]["Torso"][1][0], 0.0, W[271]["Torso"][1][2]])
KEYS = [173, 200, 214, 250, 271, 275, 279, 281, 283, 290]
CAMS = [(0, 10), (45, 15), (90, 5), (200, 20)]
noir = {p: (15, 15, 15) for p in M.SIZES}
sheet = Image.new("RGB", (10 * 160, 4 * 140), (255, 255, 255))
for r, (az, el) in enumerate(CAMS):
    for c, fr in enumerate(KEYS):
        w = {k: (R, p - off) for k, (R, p) in W[fr].items()}
        e, t, fov = G.camera_orbite(w["Torso"][1], az, el, 9, 50)
        im = M.render([w], e, t, fov, (160, 140), title=f"{fr} az{az}", sky=(255, 255, 255), ground=False,
                      couleurs=noir, ombre=False, contour=None)
        sheet.paste(im, (c * 160, r * 140))
sheet.save("silhouettes_noires.png")
