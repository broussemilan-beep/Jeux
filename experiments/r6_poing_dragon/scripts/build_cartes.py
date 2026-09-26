"""
v6 : les 3 cartes du COUP CHARGE (f150), tirees de NOTRE pose (silhouette
rendue dans Blender au contact), jamais copiees. Grammaire etudiee
(corpus/ETUDE_VISUELLE.md A-C ; « First time fighting a dummy », Black
Flash, Serious Punch TSB) :
1. silhouette BLANCHE sur NOIR, lignes radiales blanches depuis le poing ;
2. croquis a l'encre hachure (noir sur blanc) ;
3. GROS PLAN DU POING (x3,2) : poing et avant-bras blancs sur noir, eclat
   dentele aux phalanges (planche OPM de Milan : le poing vers le lecteur).
Le grand X est RESERVE aux planches de l'aerien (f298, le vrai final) : la
v6 l'avait d'abord repris ici, vu sur la video (le X revenait deux fois,
l'escalade et la signature du final s'effacaient) -> remplace.
Plus sobres que les planches de l'aerien : c'est le 2e plus gros impact,
pas le 1er (escalade). Graines fixes.

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
    a0 = alpha
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
    # 3. gros plan du poing : zoom x3,2, poing place aux 2/3 droits du cadre
    import math
    z3, tx, ty = 3.2, W * 0.64, H * 0.5
    big3 = a0.resize((int(W * z3), int(H * z3)))
    ox, oy = int(fist_px[0] * z3 - tx), int(fist_px[1] * z3 - ty)
    fist3 = big3.crop((ox, oy, ox + W, oy + H))
    c3 = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(c3)
    BM.speed_lines(d, (tx, ty), 120, 90, 1200, 6, 255, random.Random(13), 0.014)
    # eclat dentele aux phalanges (le poing « perce » le cadre)
    rng = random.Random(14)
    pts = []
    for i in range(22):
        ang = i / 22 * 2 * math.pi
        r = (230 if i % 2 == 0 else 70) * (0.75 + 0.5 * rng.random())
        pts.append((tx + 40 + math.cos(ang) * r, ty + math.sin(ang) * r))
    d.polygon(pts, fill=255)
    c3.paste(0, (0, 0), fist3.filter(ImageFilter.MaxFilter(15)))
    c3.paste(255, (0, 0), fist3)
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
