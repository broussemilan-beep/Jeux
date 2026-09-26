"""
Assemble le lecteur HTML final : substitue DATA (dump_scene_data.py,
personnage + trajectoire de la boule) dans le template
divine_orb_viewer.html.
"""
import json
import os
import subprocess
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.join(SCRIPT_DIR, "divine_orb_viewer.html")
SCENE_JSON = "/tmp/divine_orb_scene_data.json"


def main():
    out_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        SCRIPT_DIR, "..", "output", "divine_orb_viewer_final.html")

    env = dict(os.environ, SCENE_OUT=SCENE_JSON)
    subprocess.run([sys.executable, "orb_track.py"], cwd=SCRIPT_DIR, env=env, check=True)
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
