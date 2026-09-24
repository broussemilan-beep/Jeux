"""
v6 : les 3 cartes du COUP CHARGE (f150), tirees de NOTRE pose (silhouette
rendue dans Blender au contact), jamais copiees. Grammaire etudiee
(corpus/ETUDE_VISUELLE.md A-C ; « First time fighting a dummy », Black
Flash, Serious Punch TSB) :
1. silhouette BLANCHE sur NOIR, lignes radiales blanches depuis le poing ;
2. croquis a l'encre hachure (noir sur blanc) ;
3. grand X blanc sur hachures noires.
Plus sobres que les planches de l'aerien (f288) : c'est le 2e plus gros
impact, pas le 1er (escalade). Graines fixes.

Usage : python3 build_cartes.py /chemin/Blender_R6.blend -> ../output/carte_1..3.png
"""
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build_manga as BM  # noqa: E402
import dragon_clip as M  # noqa: E402


def cards(sil_path, fist_px):
    from PIL import Image, ImageChops, ImageDraw, ImageFilter
    W, H = BM.W, BM.H
    alpha = Image.open(sil_path).convert("RGBA").split()[3].point(lambda v: 255 if v > 40 else 0)
    # la silhouette doit REMPLIR la carte (lecture en 4 f) : zoom x1,45 autour du poing
    z = 1.45
    big = alpha.resize((int(W * z), int(H * z)))
    ox, oy = int(fist_px[0] * z - fist_px[0]), int(fist_px[1] * z - fist_px[1])
    alpha = big.crop((ox, oy, ox + W, oy + H))
    out = []
    # 1. silhouette blanche sur noir + lignes radiales blanches
    c1 = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(c1)
    BM.speed_lines(d, fist_px, 150, 200, 1100, 5, 255, random.Random(11), 0.012)
    c1.paste(0, (0, 0), alpha.filter(ImageFilter.MaxFilter(9)))
    c1.paste(255, (0, 0), alpha)
    out.append(c1)
    # 2. croquis encre : contour tremble + hachures, fond blanc
    c2 = Image.new("L", (W, H), 255)
    d = ImageDraw.Draw(c2)
    BM.speed_lines(d, fist_px, 90, 300, 1100, 4, 0, random.Random(12), 0.01)
    c2.paste(BM.hatch((W, H), 6, 120, 2, 0, 255), (0, 0), alpha)
    edge = alpha.filter(ImageFilter.FIND_EDGES).filter(ImageFilter.MaxFilter(7))
    c2.paste(0, (0, 0), edge)
    c2.paste(0, (0, 0), ImageChops.offset(edge, -3, 2))
    out.append(c2)
    # 3. grand X blanc sur hachures (meme dessin que la planche 3, graine differente)
    c3 = BM.hatch((W, H), 7, 60, 3, 0, 30)
    d = ImageDraw.Draw(c3)
    import math
    cx, cy = W / 2, H / 2
    for sgn in (1, -1):
        a = math.atan2(H * 0.9, sgn * W * 0.55)
        ux, uy = math.cos(a), math.sin(a)
        nx, ny = -uy, ux
        L, w = 540, 40
        d.polygon([(cx - ux * L, cy - uy * L), (cx + nx * w, cy + ny * w), (cx + ux * L, cy + uy * L),
                   (cx - nx * w, cy - ny * w)], fill=255)
    out.append(c3)
    paths = []
    for i, c in enumerate(out):
        p = os.path.join(M.OUT, f"carte_{i + 1}.png")
        c.convert("RGB").save(p, optimize=True)
        paths.append(p)
    return paths


if __name__ == "__main__":
    sil, fist = BM.render_silhouette(sys.argv[1], 150, (1.0, -0.12, 0.08), tag="carte_sil")
    print(cards(sil, fist), "poing a l'ecran :", [round(v) for v in fist])
