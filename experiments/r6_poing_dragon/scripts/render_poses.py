"""
Revue visuelle des poses cles (methode animate-roblox-characters : chaque pose
regardee de profil et de trois-quarts, sol visible, faces etiquetees).
Usage : python3 render_poses.py /chemin/Blender_R6.blend
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "..", "_shared"))
import dragon_clip as M  # noqa: E402
from animator_brain import v222_rig as V  # noqa: E402

RES = 260
KEYS = [(0, "garde basse / activation"), (7, "H1 arme, torse sur pied arriere"), (14, "H1 jab G poitrine"), (15, "H1 reaction"),
        (33, "H2 arme"), (40, "H2 direct D plexus"), (42, "H2 se plie"), (57, "H3 arme"), (64, "H3 crochet G cotes"),
        (66, "H3 plie de cote"), (90, "H4 au corps"), (93, "H4 la victime decolle"), (144, "fente tenue"),
        (150, "UPPERCUT"), (200, "apex"), (250, "temps suspendu"), (278, "CONTACT en l'air"), (288, "ecrasement au sol"),
        (334, "revelation"), (526, "fin")]


def main(blend, out_name="dragon_poses_cles.png", keys=KEYS, views=("side", "three_quarter")):
    import bpy
    from PIL import Image, ImageDraw
    a, b, aw, vw = M.main(blend)
    tmp = os.path.join(M.OUT, "_frames")
    os.makedirs(tmp, exist_ok=True)
    S = bpy.context.scene
    tiles = []
    for f, label in keys:
        S.frame_set(f)
        pts = np.array([p for w in (aw[f], vw[f]) for k, (r, p) in w.items() if k != "HumanoidRootPart"])
        lo, hi = pts.min(0) - 1.2, pts.max(0) + 1.2
        c = (lo + hi) / 2
        ext = max(hi - lo)
        paths = V.review_render(os.path.join(tmp, f"k{f:03d}"), views=views, res=RES, samples=6,
                                target=(float(c[0]), float(-c[2])), center_z=float(c[1]), ortho=float(max(6.5, ext * 1.1)),
                                aspect=1.25, dist=30.0)
        tiles.append((f, label, [Image.open(p).convert("RGB") for p in paths]))
    w, h = tiles[0][2][0].size
    cols = 3 if len(tiles) > 8 else 2
    rows = (len(tiles) + cols - 1) // cols
    nv = len(views)
    sheet = Image.new("RGB", (cols * (nv * w + 10) + 10, rows * (h + 24) + 36), (255, 255, 255))
    dr = ImageDraw.Draw(sheet)
    dr.text((10, 10), "Poing du Dragon -- poses cles, 2 rigs V2.22, 60 fps -- " + " | ".join(views), fill=(0, 0, 0))
    for i, (f, label, ims) in enumerate(tiles):
        x = 10 + (i % cols) * (nv * w + 10)
        y = 36 + (i // cols) * (h + 24)
        for k, im in enumerate(ims):
            sheet.paste(im, (x + k * w, y + 16))
        dr.text((x, y + 2), f"f{f} ({f / 60:.2f} s) {label}", fill=(0, 0, 0))
    path = os.path.join(M.OUT, out_name)
    sheet.save(path)
    print(path)


if __name__ == "__main__":
    main(sys.argv[1])
