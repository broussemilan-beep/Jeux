"""
VIDÉO d'une recette AVEC SON : images du labo (capture_lab.js, mode vidéo)
+ mixage des sons de la recette (sons.mixer) -> MP4.

Usage : python3 video_recette.py <recette> <camera> <sortie.mp4> [fps=30] [ralenti=1]
ralenti = 4 : la même recette jouée 4 fois plus lentement (images ET son,
comme le ×0,25 du labo) ; utile pour juger l'enchaînement.
"""
import os
import subprocess
import sys
import tempfile

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import recettes  # noqa: E402
import sons  # noqa: E402


def main(nom, cam, sortie, fps=30, ralenti=1):
    rec = recettes.toutes()[nom]
    d = tempfile.mkdtemp(prefix="vfxvid_")
    env = dict(os.environ, NODE_PATH=subprocess.run(["npm", "root", "-g"], capture_output=True, text=True).stdout.strip())
    subprocess.run(["node", os.path.join(HERE, "capture_lab.js"), nom, cam, f"video:{fps * ralenti}:{rec['duree']}", d],
                   check=True, env=env, capture_output=True)
    mix = sons.mixer(rec)[: int(rec["duree"] * sons.SR)]
    if ralenti != 1:
        mix = np.interp(np.arange(0, len(mix) - 1, 1 / ralenti), np.arange(len(mix)), mix)
    crete = np.max(np.abs(mix)) if len(mix) else 0
    if crete > 0.98:
        mix = mix / crete * 0.98
    wav = os.path.join(d, "son.wav")
    sons.ecrire_wav(mix, wav)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", str(fps), "-i", os.path.join(d, "f%04d.png"), "-i", wav,
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", "-c:a", "aac", "-b:a", "160k", "-shortest", sortie],
                   check=True)
    print(sortie)


if __name__ == "__main__":
    a = sys.argv[1:]
    main(a[0], a[1], a[2], int(a[3]) if len(a) > 3 else 30, int(a[4]) if len(a) > 4 else 1)
