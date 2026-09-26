"""
Assemble le lecteur HTML final : substitue DATA (dump_scene_data.py),
TEXTURES_B64 (les deux textures de ../textures/, indexees par nom de
fichier sans extension -- "stone_ground", "ruin_wall") et THREE_JS
(bibliotheque Three.js vendorisee, voir vendor/three.min.js --
cdnjs.cloudflare.com est bloque dans ce bac a sable, donc pas de
<script src> externe possible, la lib est embarquee telle quelle) dans le
template rock_kick_viewer.html. Meme pattern que
r6_hit_combo/scripts/build_viewer.py.
"""
import base64
import glob
import json
import os
import subprocess
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.join(SCRIPT_DIR, "rock_kick_viewer.html")
THREE_JS = os.path.join(SCRIPT_DIR, "vendor", "three.min.js")
SCENE_JSON = "/tmp/rock_kick_scene_data.json"


def main():
    out_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        SCRIPT_DIR, "..", "output", "rock_kick_viewer_final.html")

    env = dict(os.environ, SCENE_OUT=SCENE_JSON)
    subprocess.run([sys.executable, "dump_scene_data.py"], cwd=SCRIPT_DIR, env=env, check=True)
    with open(SCENE_JSON) as f:
        scene_data = f.read()

    textures = {}
    for path in sorted(glob.glob(os.path.join(SCRIPT_DIR, "../textures", "*.png"))):
        name = os.path.splitext(os.path.basename(path))[0]
        with open(path, "rb") as fh:
            textures[name] = base64.b64encode(fh.read()).decode("ascii")

    with open(THREE_JS) as f:
        three_js = f.read()

    with open(TEMPLATE) as f:
        html = f.read()
    html = html.replace("__THREE_JS__", three_js)
    html = html.replace("__SCENE_DATA__", scene_data)
    html = html.replace("__TEXTURES_B64__", json.dumps(textures))

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as f:
        f.write(html)
    print(f"ecrit {out_path}, {os.path.getsize(out_path)} octets, "
          f"{len(textures)} textures embarquees, three.min.js {os.path.getsize(THREE_JS)} octets")


if __name__ == "__main__":
    main()
