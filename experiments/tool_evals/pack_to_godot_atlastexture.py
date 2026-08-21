"""T.1.3 - PyTexturePacker : callable atlas_format personnalise qui
emet directement des ressources Godot AtlasTexture (.tres), une par
frame, au lieu du plist Cocos2d/JSON generique par defaut - preuve que
le hook `atlas_format` (fonction) suffit a brancher l'outil sur Godot
sans dependance a un format intermediaire a parser cote moteur."""

import os
from PyTexturePacker import Packer

ATLAS_RES_PATH = "res://experiments/tool_evals/texturepacker_test/cendre_idle_south_atlas.png"


def godot_atlastexture_format(data_dict, file_path):
    """data_dict['frames'][path] = {frame: {x,y,w,h}, ...} (schema JSON,
    cf. AtlasInterface.dump_plist branche 'else'). Ecrit un .tres par
    frame a cote du fichier plist (file_path sert de base de nommage)."""
    out_dir = os.path.dirname(file_path)
    written = []
    for name, info in data_dict["frames"].items():
        frame = info["frame"]
        tres_name = os.path.splitext(name)[0].replace("/", "_") + "_atlastex.tres"
        tres_path = os.path.join(out_dir, tres_name)
        content = (
            '[gd_resource type="AtlasTexture" load_steps=2 format=3]\n\n'
            f'[ext_resource type="Texture2D" path="{ATLAS_RES_PATH}" id="1"]\n\n'
            "[resource]\n"
            'atlas = ExtResource("1")\n'
            f'region = Rect2({frame["x"]}, {frame["y"]}, {frame["w"]}, {frame["h"]})\n'
        )
        with open(tres_path, "w") as f:
            f.write(content)
        written.append(tres_path)
    # Retourne un resume texte (le hook attend une string a ecrire dans
    # file_path + ext deduite - ici on renvoie juste un journal, les
    # vraies ressources sont deja ecrites individuellement ci-dessus).
    return "# AtlasTexture .tres generes:\n" + "\n".join(written)


packer = Packer.create(
    max_width=256, max_height=256, bg_color=0x00000000,
    enable_rotated=False, atlas_format=godot_atlastexture_format,
)
packer.pack(
    "assets/processed/sprites/cendre/idle_south",
    "cendre_idle_south_atlas",
    output_path="experiments/tool_evals/texturepacker_test",
)
print("DONE")
