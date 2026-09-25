"""
VIDÉO du Poing du Dragon AVEC SON : images du lecteur (filmer_lecteur.js,
4 processus en parallèle) + mixage des sons des recettes studio, placés à
leur temps RÉEL (hitstops compris, même calcul que realTimeOf() du
lecteur) -> MP4.

Usage : python3 video_son.py <sortie.mp4> [camera=cinema] [fps=30]
"""
import json
import os
import subprocess
import sys
import tempfile

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "output")
sys.path.insert(0, os.path.join(HERE, "..", "..", "_shared", "vfx_studio"))
import sons  # noqa: E402


def mixage(staging, duree):
    E = staging["events"]
    fps = staging["fps"]
    stops = sorted((e["frame"], e["hitstop"]) for e in E if e["kind"] == "impact" and e.get("hitstop", 0) > 0)
    rt = lambda f: f / fps + sum(h for fs, h in stops if fs < f)  # noqa: E731
    mix = np.zeros(int((duree + 3) * sons.SR))
    for e in E:
        if e["kind"] != "studio":
            continue
        for so in e["recette"].get("sons", []):
            x = sons.lire_wav(os.path.join(HERE, "..", "..", "_shared", "vfx_studio", "sons", so["son"] + ".wav"))
            h = so.get("hauteur", 1.0)
            if h != 1.0:
                x = np.interp(np.arange(0, len(x) - 1, h), np.arange(len(x)), x)
            i = int((rt(e["frame"]) + so["t0"]) * sons.SR)
            mix[i:i + len(x)] += so.get("volume", 1.0) * x[: len(mix) - i]
    mix = mix[: int(duree * sons.SR)]
    c = np.max(np.abs(mix))
    return mix / c * 0.98 if c > 0.98 else mix


def main(sortie, cam="cinema", fps=30):
    staging = json.load(open(os.path.join(OUT, "staging.json")))
    E = staging["events"]
    stops = sorted((e["frame"], e["hitstop"]) for e in E if e["kind"] == "impact" and e.get("hitstop", 0) > 0)
    duree = staging["end_f"] / staging["fps"] + sum(h for _f, h in stops) + 0.8
    d = tempfile.mkdtemp(prefix="dragonvid_")
    env = dict(os.environ, NODE_PATH=subprocess.run(["npm", "root", "-g"], capture_output=True, text=True).stdout.strip())
    parts = 4
    procs = [subprocess.Popen(["node", os.path.join(HERE, "filmer_lecteur.js"), str(duree * k / parts),
                               str(min(duree, duree * (k + 1) / parts)), d, cam, str(fps)], env=env)
             for k in range(parts)]
    for p in procs:
        p.wait()
    wav = os.path.join(d, "son.wav")
    sons.ecrire_wav(mixage(staging, duree), wav)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", str(fps), "-i", os.path.join(d, "f%04d.png"), "-i", wav,
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", "-c:a", "aac", "-b:a", "160k", "-shortest", sortie],
                   check=True)
    print(sortie, round(duree, 2), "s")


if __name__ == "__main__":
    a = sys.argv[1:]
    main(a[0], a[1] if len(a) > 1 else "cinema", int(a[2]) if len(a) > 2 else 30)
