#!/usr/bin/env python3
"""Cuit les frames brutes PixelLab (assets/source/pixellab/<perso>/...) en
frames de jeu (assets/processed/sprites/<perso>/<anim>/<i>.png), toutes
sur UN SEUL canvas partagé avec le pivot bas-centre (docs/ARCHITECTURE_VFX_v3.md
§6.3) au MEME pixel dans chaque frame.

Pourquoi : PixelLab v3 en mode custom ne garde pas une taille de canvas
fixe d'une animation a l'autre (32x64 pour idle/marche/hurt, 88x88 pour
mort/dash - le canvas s'agrandit pour la portee du mouvement). Un
AnimatedSprite2D Godot n'a qu'UN SEUL `offset` pour TOUTES ses frames/
animations : sans normalisation, changer d'animation ferait sauter les
pieds du personnage. Solution : recadrer chaque frame sur son centre de
masse alpha bas (les pieds), puis coller sur un canvas commun avec ce
point toujours au meme pixel — un seul `offset` suffit ensuite cote Godot.

Usage :
    python3 scripts/cook_character_frames.py --character cendre \
        --anim idle:assets/source/pixellab/cendre/animations/idle \
        --anim deplacement:assets/source/pixellab/cendre/animations/deplacement \
        --anim hurt:assets/source/pixellab/cendre/animations/hurt \
        --anim mort:assets/source/pixellab/cendre/animations/mort \
        --anim dash:assets/source/pixellab/cendre/animations/dash \
        --out-canvas 96x96 --foot-margin-px 4
"""
from __future__ import annotations

import argparse
import json
import os
import sys

from PIL import Image


def alpha_bbox(img: Image.Image) -> tuple[int, int, int, int] | None:
    alpha = img.split()[-1] if img.mode == "RGBA" else None
    if alpha is None:
        return (0, 0, img.width, img.height)
    return alpha.getbbox()


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--character", required=True)
    p.add_argument("--anim", action="append", required=True, help="name:source_dir")
    p.add_argument("--out-canvas", required=True, help="WxH, e.g. 96x96")
    p.add_argument("--foot-margin-px", type=int, default=4,
                    help="Distance entre les pieds et le bas du canvas (marge pour ombre/anim future).")
    p.add_argument("--repo-root", default=os.getcwd())
    args = p.parse_args()

    out_w, out_h = (int(x) for x in args.out_canvas.lower().split("x"))
    anchor_x = out_w // 2
    anchor_y = out_h - args.foot_margin_px

    anims: dict[str, str] = {}
    for entry in args.anim:
        name, src = entry.split(":", 1)
        anims[name] = src

    manifest: dict[str, dict] = {}
    for name, src_dir in anims.items():
        files = sorted(
            (f for f in os.listdir(src_dir) if f.endswith(".png")),
            key=lambda f: int(os.path.splitext(f)[0]),
        )
        out_dir = os.path.join(args.repo_root, "assets", "processed", "sprites", args.character, name)
        os.makedirs(out_dir, exist_ok=True)

        frame_paths = []
        for f in files:
            src_path = os.path.join(src_dir, f)
            img = Image.open(src_path).convert("RGBA")
            bbox = alpha_bbox(img)
            if bbox is None:
                # Frame entierement transparente (ne devrait pas arriver) - centrer tel quel.
                foot_x, foot_y = img.width // 2, img.height
            else:
                left, top, right, bottom = bbox
                foot_x = (left + right) // 2
                foot_y = bottom

            canvas = Image.new("RGBA", (out_w, out_h), (0, 0, 0, 0))
            paste_x = anchor_x - foot_x
            paste_y = anchor_y - foot_y
            canvas.paste(img, (paste_x, paste_y), img)

            out_path = os.path.join(out_dir, f)
            canvas.save(out_path)
            frame_paths.append(os.path.relpath(out_path, args.repo_root))

        manifest[name] = {
            "frames": frame_paths,
            "canvas": [out_w, out_h],
            "anchor_px": [anchor_x, anchor_y],
        }
        print(f"{name}: {len(frame_paths)} frames -> {out_dir}")

    manifest_path = os.path.join(
        args.repo_root, "assets", "manifests", f"{args.character}_frames_cooked.json"
    )
    os.makedirs(os.path.dirname(manifest_path), exist_ok=True)
    with open(manifest_path, "w") as fh:
        json.dump({
            "character": args.character,
            "out_canvas": [out_w, out_h],
            "anchor_px": [anchor_x, anchor_y],
            "animations": manifest,
        }, fh, indent=2)
    print(f"manifest -> {manifest_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
