"""
Assemble le lecteur HTML final : substitue DATA (dump_scene_data.py) et
TEXTURES_B64 (toutes les images de ../textures/ ET ../textures_pbr/,
indexees par nom de fichier sans extension -- "slate_color",
"slate_normal", "slate_roughness", "metal_metalness", etc.) dans le
template throne_crown_viewer.html.

Existe pour que le lecteur soit reconstructible depuis le depot seul :
avant ce script, l'assemblage (embarquer les textures en base64, injecter
le JSON de scene) se faisait par des commandes ad hoc non versionnees --
le template lui-meme ne vivait que dans le scratchpad de session, jamais
commit. Les deux sont maintenant dans scripts/, le lecteur final (gros,
binaire par les PNG embarques) reste un artefact construit dans
../output/, jamais committe -- comme .rbxmx/.fbx exportes, mais celui-la
n'a pas besoin de l'etre : il se reconstruit a l'identique par la seule
commande ci-dessous.
"""
import base64
import glob
import json
import os
import subprocess
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.join(SCRIPT_DIR, "throne_crown_viewer.html")
SCENE_JSON = "/tmp/throne_scene_data.json"


def main():
    out_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        SCRIPT_DIR, "..", "output", "throne_crown_viewer_final.html")

    env = dict(os.environ, SCENE_OUT=SCENE_JSON)
    subprocess.run([sys.executable, "dump_scene_data.py"], cwd=SCRIPT_DIR, env=env, check=True)
    with open(SCENE_JSON) as f:
        scene_data = f.read()

    textures = {}
    for folder in ["../textures", "../textures_pbr"]:
        for path in sorted(glob.glob(os.path.join(SCRIPT_DIR, folder, "*.png"))):
            name = os.path.splitext(os.path.basename(path))[0]
            with open(path, "rb") as fh:
                textures[name] = base64.b64encode(fh.read()).decode("ascii")

    with open(TEMPLATE) as f:
        html = f.read()
    html = html.replace("__SCENE_DATA__", scene_data)
    html = html.replace("__TEXTURES_B64__", json.dumps(textures))

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as f:
        f.write(html)
    print(f"ecrit {out_path}, {os.path.getsize(out_path)} octets, {len(textures)} textures embarquees")


if __name__ == "__main__":
    main()
