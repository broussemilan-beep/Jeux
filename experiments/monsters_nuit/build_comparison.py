"""Compose l'image comparaison avant/apres (echelle incoherente vs echelle
commune) demandee par Milan pour la revue des 3 monstres. Chaque case est
mise a l'echelle du meme facteur (nearest, pas de lissage) pour rester
fidele aux pixels quantifies ; empilees dans une grille 4 colonnes x 2
lignes (Cendre reference / Crawler / Brute / Ranged, avant / apres)."""

from PIL import Image, ImageDraw, ImageFont

SCALE = 6
CELL = 64 * SCALE
PAD = 14
LABEL_H = 20
OUT_DIR = "experiments/monsters_nuit"
V2 = f"{OUT_DIR}/blender_out_v2"
OLD = f"{OUT_DIR}/out"

COLUMNS = [
    ("Cendre (ref)", None, f"{V2}/cendre_idle_64.png"),
    ("Crawler", f"{OLD}/crawler_idle_64.png", f"{V2}/crawler_idle_64.png"),
    ("Brute", f"{OLD}/brute_idle_64.png", f"{V2}/brute_idle_64.png"),
    ("Ranged", f"{OLD}/ranged_idle_64.png", f"{V2}/ranged_idle_64.png"),
]

n_cols = len(COLUMNS)
width = PAD + n_cols * (CELL + PAD)
row_h = LABEL_H + CELL
height = PAD + LABEL_H + row_h + PAD + row_h + PAD

canvas = Image.new("RGBA", (width, height), (235, 235, 238, 255))
draw = ImageDraw.Draw(canvas)
font = ImageFont.load_default()


def paste_cell(path, x, y):
    cell_bg = Image.new("RGBA", (CELL, CELL), (210, 210, 214, 255))
    if path is not None:
        img = Image.open(path).convert("RGBA")
        img = img.resize((CELL, CELL), Image.NEAREST)
        cell_bg.alpha_composite(img)
    else:
        draw.text((x + CELL // 2 - 20, y + CELL // 2), "N/A", fill=(120, 120, 120, 255), font=font)
    canvas.alpha_composite(cell_bg, (x, y))


title_y = PAD
row1_label_y = title_y + LABEL_H
row1_cell_y = row1_label_y + LABEL_H
row2_label_y = row1_cell_y + CELL + PAD
row2_cell_y = row2_label_y + LABEL_H

for i, (label, before_path, after_path) in enumerate(COLUMNS):
    x = PAD + i * (CELL + PAD)
    draw.text((x, title_y), label, fill=(20, 20, 24, 255), font=font)
    draw.text((x, row1_label_y), "avant", fill=(140, 40, 40, 255), font=font)
    paste_cell(before_path, x, row1_cell_y)
    draw.text((x, row2_label_y), "apres", fill=(30, 110, 40, 255), font=font)
    paste_cell(after_path, x, row2_cell_y)

canvas.convert("RGB").save(f"{OUT_DIR}/comparison_scale_fix.png")
print("saved", f"{OUT_DIR}/comparison_scale_fix.png", canvas.size)
