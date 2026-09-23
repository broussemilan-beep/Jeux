"""
Audit de mouvement de CE prototype via le cerveau partage
(experiments/_shared/animator_brain/audit.py) : echantillonne la
choregraphie exactement comme calibrate.py (60 Hz, ressorts compris),
ecrit un rapport JSON + texte et le graphe "chaine de pics".

Usage : python3 audit_motion.py <tag>   (ex. avant / apres)
Sorties : ../output/motion_audit_<tag>.json|.txt|_peaks.png
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "_shared"))

import calibrate  # noqa: E402
import choreography as ch  # noqa: E402
import r6_rig  # noqa: E402
from animator_brain import audit as A  # noqa: E402
from animator_brain import plots as P  # noqa: E402
from animator_brain.rig_math import Rig  # noqa: E402

OUT = os.path.join(HERE, "..", "output")


def loop_windows():
    w = getattr(ch, "AUDIT_LOOP_WINDOWS", None)
    if w:
        return w
    return {
        "idle": (0.0, ch.T0_END),
        "hover": (ch.RISE_T + 0.2, ch.HOLD_END_T),
        "idle_out": (ch.RECOVER_T, ch.IDLE_OUT_END),
    }


def main():
    tag = sys.argv[1] if len(sys.argv) > 1 else "courant"
    samples, _ = calibrate._run()  # meme pipeline que le rendu et l export
    rig = Rig.from_module(r6_rig)
    report, clip, sig = A.audit(samples, rig, loop_windows=loop_windows(),
                                free_leg_windows=getattr(ch, "AUDIT_FREE_LEG_WINDOWS", None),
                                intended_snaps=getattr(ch, "AUDIT_INTENDED_SNAPS", None))
    os.makedirs(OUT, exist_ok=True)
    base = os.path.join(OUT, f"motion_audit_{tag}")
    A.save_json(report, base + ".json")
    txt = A.format_report(report)
    with open(base + ".txt", "w") as f:
        f.write(txt + "\n")
    print(txt)
    rows = [("racine (lin.)", "root"), ("Torso", "Torso"), ("Head", "Head"),
            ("Right Arm", "Right Arm"), ("Left Arm", "Left Arm"),
            ("Right Leg", "Right Leg"), ("Left Leg", "Left Leg")]
    t0 = getattr(ch, "AUDIT_CHART_WINDOW", (ch.T0_END - 0.2, ch.RISE_T + 1.0))
    P.peak_chain_chart(clip, sig, rows, t0[0], t0[1],
                       f"r6_black_hole [{tag}] -- vitesse normalisee par articulation, pics marques "
                       f"(accroupissement -> decollage)", base + "_peaks.png")
    P.onion_skin(clip, ch.T0_END, getattr(ch, "V_T", ch.RISE_T + 0.33), 0.2,
                 f"[{tag}] profil, avant du perso -> droite, 1 silhouette / 6 frames",
                 base + "_onion.png", width=620, height=700, scale=70)
    print("ecrit", base + ".json", base + ".txt", base + "_peaks.png", base + "_onion.png")


if __name__ == "__main__":
    main()
