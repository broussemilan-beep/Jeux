"""
Revue visuelle du clip M1 : planche des poses cles (profil + camera de jeu)
et GIF de l'animation complete (camera de jeu), rendus Cycles CPU sans ecran.

Usage : python3 render_review.py /chemin/Blender_R6.blend
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "..", "_shared"))

import m1_clip as M  # noqa: E402
from animator_brain import v222_rig as V  # noqa: E402

KEY_FRAMES = (0, 3, 10, 14, 17, 19, 21, 33, 39)
LABELS = {0: "repos", 3: "armement (claque)", 10: "extreme armement", 14: "la main mene", 17: "IMPACT",
          19: "suite", 21: "fin d'arc", 33: "retour du bras", 39: "tenue"}


def main(blend):
    import bpy
    from PIL import Image, ImageDraw
    a, b, wa, wb, d = M.main(blend)
    tmp = os.path.join(M.OUT, "_frames")
    os.makedirs(tmp, exist_ok=True)
    S = bpy.context.scene
    target = (0.0, d / 2)
    tiles = []
    for f in KEY_FRAMES:
        S.frame_set(f)
        paths = V.review_render(os.path.join(tmp, f"k{f:02d}"), views=("side", "gameplay"), res=300, samples=8,
                                target=target, center_z=2.6, ortho=7.5, aspect=1.2)
        tiles.append((f, [Image.open(p).convert("RGB") for p in paths]))
    w, h = tiles[0][1][0].size
    cols = 3
    rows = (len(tiles) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * (2 * w + 10) + 10, rows * (h + 28) + 40), (255, 255, 255))
    dr = ImageDraw.Draw(sheet)
    dr.text((10, 10), f"M1 + reaction, 2 rigs V2.22, 60 fps -- profil | camera de jeu -- victime a {d:.2f} studs, "
                      f"impact f{M.IMPACT_F}", fill=(0, 0, 0))
    for i, (f, (side, game)) in enumerate(tiles):
        x = 10 + (i % cols) * (2 * w + 10)
        y = 40 + (i // cols) * (h + 28)
        sheet.paste(side, (x, y + 18))
        sheet.paste(game, (x + w, y + 18))
        dr.text((x, y + 2), f"f{f} ({f / 60:.2f} s) -- {LABELS[f]}", fill=(0, 0, 0))
    sheet_path = os.path.join(M.OUT, "m1_poses_cles.png")
    sheet.save(sheet_path)
    # GIF : toutes les 2 frames (30 i/s), camera de jeu
    gif_frames = []
    for f in range(0, M.ATT_END_F + 1, 2):
        S.frame_set(f)
        p = V.review_render(os.path.join(tmp, f"g{f:02d}"), views=("gameplay",), res=360, samples=8,
                            target=target, center_z=2.6, ortho=7.5, aspect=1.2)[0]
        gif_frames.append(Image.open(p).convert("RGB"))
    pal = gif_frames[len(gif_frames) // 2].quantize(colors=255, method=Image.Quantize.MEDIANCUT)
    q = [g.quantize(palette=pal, dither=Image.Dither.FLOYDSTEINBERG) for g in gif_frames]
    gif_path = os.path.join(M.OUT, "m1_camera_de_jeu.gif")
    q[0].save(gif_path, save_all=True, append_images=q[1:] + [q[-1]] * 8, duration=33, loop=0, disposal=2,
              optimize=False)
    print("planche :", sheet_path, "| gif :", gif_path, len(q), "images")


if __name__ == "__main__":
    main(sys.argv[1])
