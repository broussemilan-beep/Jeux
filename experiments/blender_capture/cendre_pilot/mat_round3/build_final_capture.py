#!/usr/bin/env python3
"""Livrable - MANDAT MIGRATION CENDRE, dernière tentative ciblée (round 3,
materiau aplati). MEME format que captures/verification/2026-08-23-cendre-
migration-3d-dernier-test-cuit-64px-reel.png (le test precedent) : 3 blocs
coup1/2/3, chaque bloc = 2 frames 3D cuites 64px reel + 1 frame PixelLab
de reference, echelle x8 nearest-neighbor."""
import os
from PIL import Image, ImageDraw, ImageFont

ROOT = "/home/user/jeux"
SCRATCH = "/tmp/claude-0/-home-user-Alpha-Project-Live/e304835e-195c-5813-864a-d285531ad037/scratchpad/cendre_cook_final_v4"
NEW_64 = f"{SCRATCH}/assets/processed/sprites/cendre_pilot_test_v4"
PIXELLAB_DIR = f"{ROOT}/assets/processed/sprites/cendre"
OUT_PATH = f"{ROOT}/captures/verification/2026-08-23-cendre-migration-3d-round3-materiau-aplati-cuit-64px-reel.png"

FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

BG = (32, 32, 34)
PANEL_BG = (44, 44, 48)
TEXT = (235, 235, 232)
SUBTEXT = (190, 190, 185)
LABEL_3D = (180, 210, 230)
LABEL_PL = (220, 200, 150)

CONTACT_FRAMES = {
    1: ("coup1_contact", ["0", "1"]),
    2: ("coup2_contact", ["0", "1"]),
    3: ("coup3_contact", ["0", "1"]),
}

CELL = 64 * 8
PAD = 8
MARGIN = 24


def load_tile(path, cell, bg=(70, 70, 74, 255)):
    im = Image.open(path).convert("RGBA")
    t = Image.new("RGBA", (cell, cell), bg)
    scaled = im.resize((cell, cell), Image.NEAREST) if im.size != (cell, cell) else im
    t.alpha_composite(scaled)
    return t


def coup_block(coup):
    anim_name, idxs = CONTACT_FRAMES[coup]
    font_h2 = ImageFont.truetype(FONT_BOLD, 22)
    font_label = ImageFont.truetype(FONT_BOLD, 16)
    label_h = 24

    new_ims = [load_tile(f"{NEW_64}/{anim_name}/{i}.png", CELL) for i in idxs]
    pl_im = load_tile(f"{PIXELLAB_DIR}/coup{coup}/2.png", CELL)

    group_w = len(new_ims) * CELL + (len(new_ims) - 1) * PAD
    row_w = group_w + 60 + CELL + 2 * PAD
    row_h = 34 + label_h + CELL + PAD
    row = Image.new("RGBA", (row_w, row_h), PANEL_BG + (255,))
    d = ImageDraw.Draw(row)
    d.text((PAD, 4), f"COUP {coup} — contact, canvas cuit 64px REEL (echelle x8, nearest)", font=font_h2, fill=TEXT)

    y_label = 34
    y_img = y_label + label_h
    x = PAD
    d.text((x, y_label), "3D round3 (materiau aplati) -> cook_character_frames.py reel", font=font_label, fill=LABEL_3D)
    for im in new_ims:
        row.paste(im, (x, y_img), im)
        x += CELL + PAD

    x = group_w + 60
    d.text((x, y_label), "PixelLab 2D -> cuit 64px (deja en jeu, coup{}/2.png)".format(coup), font=font_label, fill=LABEL_PL)
    row.paste(pl_im, (x, y_img), pl_im)

    return row


def main():
    font_title = ImageFont.truetype(FONT_BOLD, 24)
    font_small = ImageFont.truetype(FONT_REG, 14)

    blocks = [coup_block(c) for c in (1, 2, 3)]
    title_h = 110
    total_w = max(b.width for b in blocks) + 2 * MARGIN
    total_h = title_h + sum(b.height for b in blocks) + MARGIN * (len(blocks) + 1) + 130

    canvas = Image.new("RGB", (total_w, total_h), BG)
    d = ImageDraw.Draw(canvas)
    d.text((MARGIN, 14), "MANDAT MIGRATION CENDRE — derniere tentative ciblee, round 3",
           font=font_title, fill=TEXT)
    d.text((MARGIN, 44), "materiau aplati (specular reduite + posterisation albedo/emission), canvas cuit 64px REEL",
           font=font_title, fill=TEXT)
    d.text((MARGIN, 78), "3 coups, frames de contact, meme pipeline reel (cook_character_frames.py) vs reference PixelLab deja cuite 64px, echelle egale.",
           font=font_small, fill=SUBTEXT)

    y = title_h
    for blk in blocks:
        canvas.paste(blk.convert("RGB"), (MARGIN, y))
        y += blk.height + MARGIN

    verdict_lines = [
        "VERDICT (voir docs/worklog.md pour le detail mesure) :",
        "Diagnostic mesure avant retouche : la reduction specular/metallique seule (mandat, etape 1) change tres peu le bruit",
        "(diff pixel moyenne ~1.3/255 sur 512px, metallic=1 vs 0) - la cause reelle est la texture d'albedo/emission elle-meme",
        "(mosaique haute-frequence, emise quasi telle quelle, Emission Strength=1.0), pas la specularite BSDF.",
        "Fix retenu : specular reduite (Metallic 0, Roughness 0.9, Specular 0.15) + posterisation HSV Value 5 paliers de",
        "l'albedo/emission (Teinte/Saturation intactes) - un rendu plus \"toon\", pas une texture regeneree.",
    ]
    yv = y + 4
    for line in verdict_lines:
        d.text((MARGIN, yv), line, font=font_small, fill=SUBTEXT)
        yv += 18

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    canvas.save(OUT_PATH)
    print("SAVED", OUT_PATH, canvas.size)


if __name__ == "__main__":
    main()
