"""
Assemble le lecteur HTML final : substitue DATA (dump_scene_data.py) dans
le template divine_descent_viewer.html. Pas de textures a embarquer ici
(pas de decor/props, juste le personnage) -- plus simple que
r6_throne_crown/build_viewer.py.
"""
import json
import os
import subprocess
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.join(SCRIPT_DIR, "divine_descent_viewer.html")
SCENE_JSON = "/tmp/divine_descent_scene_data.json"


def main():
    out_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        SCRIPT_DIR, "..", "output", "divine_descent_viewer_final.html")

    env = dict(os.environ, SCENE_OUT=SCENE_JSON)
    subprocess.run([sys.executable, "dump_scene_data.py"], cwd=SCRIPT_DIR, env=env, check=True)
    with open(SCENE_JSON) as f:
        scene_data = f.read()

    with open(TEMPLATE) as f:
        html = f.read()
    html = html.replace("__SCENE_DATA__", scene_data)

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as f:
        f.write(html)
    print(f"ecrit {out_path}, {os.path.getsize(out_path)} octets")


if __name__ == "__main__":
    main()
