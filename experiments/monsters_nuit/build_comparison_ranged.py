"""Comparaison dediee Ranged idle+attack : demontre le fix de lisibilite
(dither desactive + plancher de Value releve) demande par Milan, la pose
attack etant la pire (silhouette noire/violette tres sombre)."""

from PIL import Image, ImageDraw, ImageFont

SCALE = 6
CELL = 64 * SCALE
PAD = 14
LABEL_H = 20
OUT_DIR = "experiments/monsters_nuit"
V2 = f"{OUT_DIR}/blender_out_v2"
OLD = f"{OUT_DIR}/out"

COLUMNS = [
    ("Ranged idle", f"{OLD}/ranged_idle_64.png", f"{V2}/ranged_idle_64.png"),
    ("Ranged attack", f"{OLD}/ranged_attack_64.png", f"{V2}/ranged_attack_64.png"),
]

n_cols = len(COLUMNS)
width = PAD + n_cols * (CELL + PAD)
row_h = LABEL_H + CELL
height = PAD + LABEL_H + row_h + PAD + row_h + PAD

canvas = Image.new("RGBA", (width, height), (235, 235, 238, 255))
draw = ImageDraw.Draw(canvas)
font = ImageFont.load_default()


def paste_cell(path, x, y):
    img = Image.open(path).convert("RGBA").resize((CELL, CELL), Image.NEAREST)
    cell_bg = Image.new("RGBA", (CELL, CELL), (210, 210, 214, 255))
    cell_bg.alpha_composite(img)
    canvas.alpha_composite(cell_bg, (x, y))


title_y = PAD
row1_label_y = title_y + LABEL_H
row1_cell_y = row1_label_y + LABEL_H
row2_label_y = row1_cell_y + CELL + PAD
row2_cell_y = row2_label_y + LABEL_H

for i, (label, before_path, after_path) in enumerate(COLUMNS):
    x = PAD + i * (CELL + PAD)
    draw.text((x, title_y), label, fill=(20, 20, 24, 255), font=font)
    draw.text((x, row1_label_y), "avant (dither 0.35, plancher V 0.165)", fill=(140, 40, 40, 255), font=font)
    paste_cell(before_path, x, row1_cell_y)
    draw.text((x, row2_label_y), "apres (sans dither, plancher V 0.35)", fill=(30, 110, 40, 255), font=font)
    paste_cell(after_path, x, row2_cell_y)

canvas.convert("RGB").save(f"{OUT_DIR}/comparison_ranged_legibility.png")
print("saved", f"{OUT_DIR}/comparison_ranged_legibility.png", canvas.size)
