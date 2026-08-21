"""Compare reference vs regenerated 3D mesh (posture check) for Crawler
et Brute - confirme que la posture de la reference (quadrupede rampant /
tres accroupi) est bien capturee dans le nouveau maillage Meshy, avant
de traiter le blocage de rigging separement."""

from PIL import Image, ImageDraw, ImageFont

CELL = 420
PAD = 14
LABEL_H = 20

ROWS = [
    ("Crawler", "experiments/monsters_nuit/refs_v2/crawler_threequarter.png", "/tmp/dbg/crawler_v2_check.png"),
    ("Brute", "experiments/monsters_nuit/refs_v2/brute_threequarter.png", "/tmp/dbg/brute_v2_check.png"),
]

width = PAD + 2 * (CELL + PAD)
row_h = LABEL_H + CELL
height = PAD + len(ROWS) * (row_h + PAD)

canvas = Image.new("RGBA", (width, height), (235, 235, 238, 255))
draw = ImageDraw.Draw(canvas)
font = ImageFont.load_default()


def paste_cell(path, x, y, bg=(210, 210, 214, 255)):
    img = Image.open(path).convert("RGBA")
    scale = min(CELL / img.width, CELL / img.height)
    img = img.resize((int(img.width * scale), int(img.height * scale)), Image.LANCZOS)
    cell_bg = Image.new("RGBA", (CELL, CELL), bg)
    ox, oy = (CELL - img.width) // 2, (CELL - img.height) // 2
    cell_bg.alpha_composite(img, (ox, oy))
    canvas.alpha_composite(cell_bg, (x, y))


for i, (label, ref_path, mesh_path) in enumerate(ROWS):
    y0 = PAD + i * (row_h + PAD)
    draw.text((PAD, y0), f"{label} - reference", fill=(20, 20, 24, 255), font=font)
    paste_cell(ref_path, PAD, y0 + LABEL_H, bg=(90, 90, 94, 255))
    x1 = PAD + CELL + PAD
    draw.text((x1, y0), f"{label} - nouveau maillage 3D", fill=(20, 20, 24, 255), font=font)
    paste_cell(mesh_path, x1, y0 + LABEL_H)

canvas.convert("RGB").save("experiments/monsters_nuit/comparison_v2_posture.png")
print("saved experiments/monsters_nuit/comparison_v2_posture.png", canvas.size)
