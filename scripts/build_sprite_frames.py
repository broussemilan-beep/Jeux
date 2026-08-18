#!/usr/bin/env python3
"""Génère une ressource SpriteFrames (.tres) Godot 4 à partir du manifeste
produit par scripts/cook_character_frames.py.

Toutes les vitesses (fps) DOIVENT diviser 60 exactement — le mandat exige
que toute durée s'exprime en ticks entiers (docs/ARCHITECTURE_VFX_v3.md
§0 : "Toutes les durées d'animation/VFX s'expriment en ticks"). Une fps
qui ne divise pas 60 (ex. 8 -> 7.5 ticks/frame) est refusée ici plutôt
que silencieusement arrondie ailleurs.

Usage :
    python3 scripts/build_sprite_frames.py \
        --cooked-manifest assets/manifests/cendre_frames_cooked.json \
        --anim idle:fps=6:loop=true \
        --anim deplacement:fps=10:loop=true \
        --anim hurt:fps=12:loop=false \
        --anim mort:fps=6:loop=false \
        --anim dash:fps=15:loop=false \
        --out assets/processed/sprites/cendre/cendre_frames.tres
"""
from __future__ import annotations

import argparse
import json
import os
import sys

VALID_FPS = {f for f in range(1, 61) if 60 % f == 0}


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--cooked-manifest", required=True)
    p.add_argument("--anim", action="append", required=True,
                    help="name:fps=N:loop=true|false")
    p.add_argument("--out", required=True)
    p.add_argument("--repo-root", default=os.getcwd())
    args = p.parse_args()

    with open(args.cooked_manifest) as f:
        cooked = json.load(f)

    anim_config = {}
    for entry in args.anim:
        parts = entry.split(":")
        name = parts[0]
        cfg = {"fps": 10.0, "loop": True}
        for part in parts[1:]:
            k, v = part.split("=", 1)
            if k == "fps":
                cfg["fps"] = float(v)
            elif k == "loop":
                cfg["loop"] = v.lower() == "true"
        anim_config[name] = cfg

    for name, cfg in anim_config.items():
        fps = cfg["fps"]
        if not fps.is_integer() or int(fps) not in VALID_FPS:
            print(f"ERREUR: fps={fps} pour '{name}' ne divise pas 60 exactement "
                  f"(valeurs valides: {sorted(VALID_FPS)}) — durée non exprimable en ticks entiers.",
                  file=sys.stderr)
            return 1

    ext_lines = []
    res_id = 1
    tex_id_map = {}
    for anim_name, data in cooked["animations"].items():
        if anim_name not in anim_config:
            continue
        for fp in data["frames"]:
            res_path = "res://" + fp
            res_id += 1
            tex_id_map[fp] = res_id
            ext_lines.append(f'[ext_resource type="Texture2D" path="{res_path}" id="{res_id}"]')

    load_steps = len(tex_id_map) + 1

    anim_blocks = []
    for anim_name, data in cooked["animations"].items():
        if anim_name not in anim_config:
            continue
        cfg = anim_config[anim_name]
        frame_entries = [
            '{\n"duration": 1.0,\n"texture": ExtResource("%d")\n}' % tex_id_map[fp]
            for fp in data["frames"]
        ]
        frames_str = ", ".join(frame_entries)
        block = (
            '{\n'
            f'"frames": [{frames_str}],\n'
            f'"loop": {"true" if cfg["loop"] else "false"},\n'
            f'"name": &"{anim_name}",\n'
            f'"speed": {cfg["fps"]}\n'
            '}'
        )
        anim_blocks.append(block)

    animations_str = ", ".join(anim_blocks)

    out_lines = [
        f'[gd_resource type="SpriteFrames" load_steps={load_steps} format=3]',
        "",
        *ext_lines,
        "",
        "[resource]",
        f"animations = [{animations_str}]",
        "",
    ]

    out_path = os.path.join(args.repo_root, args.out)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as f:
        f.write("\n".join(out_lines))
    print(f"wrote {out_path} (load_steps={load_steps})")

    for name, cfg in anim_config.items():
        ticks_per_frame = 60 // int(cfg["fps"])
        print(f"  {name}: {cfg['fps']}fps -> {ticks_per_frame} ticks/frame, loop={cfg['loop']}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
