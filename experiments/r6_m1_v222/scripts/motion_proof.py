"""Preuve de mouvement : chaine des pics du M1 pro (M1_1, pack) contre notre
M1 exporte (relu depuis le .rbxmx : c'est le fichier livre qu'on mesure)."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "_shared"))

from animator_brain import audit as A  # noqa: E402
from animator_brain import corpus as C  # noqa: E402
from animator_brain import roblox_export as X  # noqa: E402
from animator_brain.plots import peak_chain_chart, side_by_side  # noqa: E402

OUT = os.path.join(HERE, "..", "output")
ROWS = [("torse", "Torso"), ("tete", "Head"), ("bras droit", "Right Arm"), ("bras gauche", "Left Arm")]


def main(pack):
    pro = [s for s in C.load_rbxm_sequences(pack) if s["name"] == "[2] M1_1"][0]
    _r, clip, sig = A.audit(C.to_samples(C.resolve_world(pro["frames"])), C.brain_rig())
    a = peak_chain_chart(clip, sig, ROWS, 0.0, clip.t[-1], "PRO [2] M1_1 (pack premium) -- 0,65 s",
                         os.path.join(OUT, "_pro.png"), width=1100, row_h=66, fps=60)
    ours = [(t, X.solve(p)) for t, p in X.read_kfseq(os.path.join(OUT, "m1_attaquant.rbxmx"))]
    _r2, clip2, sig2 = A.audit(C.to_samples(ours), C.brain_rig())
    b = peak_chain_chart(clip2, sig2, ROWS, 0.0, clip2.t[-1],
                         "NOTRE M1 (rig V2.22, relu depuis m1_attaquant.rbxmx) -- 0,65 s",
                         os.path.join(OUT, "_ours.png"), width=1100, row_h=66, fps=60)
    side_by_side([a, b], os.path.join(OUT, "m1_chaine_pics_pro_vs_notre.png"))
    os.remove(a)
    os.remove(b)


if __name__ == "__main__":
    main(sys.argv[1])
