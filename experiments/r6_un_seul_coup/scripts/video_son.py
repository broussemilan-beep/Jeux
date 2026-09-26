"""
VIDÉO de « Un seul coup » AVEC SON : images du lecteur (filmer.js, 4
processus en parallèle) + mixage des sons de staging.json (les mêmes WAV que
dans Roblox, placés à leur temps) -> MP4.
Usage : python3 video_son.py <sortie.mp4> [fps=30]
"""
import json
import os
import subprocess
import sys
import tempfile

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "output")
VS = os.path.join(HERE, "..", "..", "_shared", "vfx_studio")
sys.path.insert(0, VS)
import sons  # noqa: E402


def mixage(staging, duree):
    mix = np.zeros(int((duree + 4) * sons.SR))
    for so in staging["sons"]:
        x = sons.lire_wav(os.path.join(VS, "sons", so["son"] + ".wav"))
        h = so.get("hauteur", 1.0)
        if h != 1.0:
            x = np.interp(np.arange(0, len(x) - 1, h), np.arange(len(x)), x)
        i = int(so["t"] * sons.SR)
        mix[i:i + len(x)] += so.get("volume", 1.0) * x[: len(mix) - i]
    mix = mix[: int(duree * sons.SR)]
    c = np.max(np.abs(mix))
    return mix / c * 0.98 if c > 0.98 else mix


def main(sortie, fps=30):
    staging = json.load(open(os.path.join(OUT, "staging.json")))
    duree = staging["end_f"] / staging["fps"] + 0.6
    d = tempfile.mkdtemp(prefix="uscvid_", dir=os.environ.get("TMPDIR"))
    env = dict(os.environ, NODE_PATH=subprocess.run(["npm", "root", "-g"], capture_output=True, text=True).stdout.strip())
    parts = 4
    procs = [subprocess.Popen(["node", os.path.join(HERE, "filmer.js"), str(duree * k / parts), str(duree * (k + 1) / parts),
                               d, str(fps)], env=env) for k in range(parts)]
    for p in procs:
        p.wait()
    wav = os.path.join(d, "son.wav")
    sons.ecrire_wav(mixage(staging, duree), wav)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", str(fps), "-i", os.path.join(d, "f%04d.png"), "-i", wav,
                    "-vf", "scale=trunc(iw/2)*2:trunc(ih/2)*2", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20",
                    "-c:a", "aac", "-b:a", "160k", "-shortest", sortie], check=True)
    print(sortie, round(duree, 2), "s")


if __name__ == "__main__":
    main(sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 30)
