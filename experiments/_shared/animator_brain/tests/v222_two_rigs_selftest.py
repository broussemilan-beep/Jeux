"""
Auto-test : deux personnages V2.22 dans la meme scene (attaquant + victime).

1. Append d'une 2e copie du rig ; verification que TOUTES ses references
   (drivers, contraintes, parents) pointent vers SES objets, jamais vers
   ceux du 1er rig.
2. Independance mesuree : poser/regler la victime ne bouge pas l'attaquant
   (et inversement).
3. Placement : victime a 4 studs devant, face a l'attaquant ; son
   HumanoidRootPart cuit doit etre a (0, 3, -4) en repere Roblox, tourne de
   180 deg.
4. Export des deux KeyframeSequences + aller-retour moteur.
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
from animator_brain import v222_rig as V  # noqa: E402
from animator_brain import roblox_export as X  # noqa: E402


def refs_outside(rig):
    """References de ce rig qui sortent de SA collection."""
    own = set(rig.collection.all_objects)
    bad = []
    for obj in own:
        ad = obj.animation_data
        if ad:
            for d in ad.drivers:
                for v in d.driver.variables:
                    for t in v.targets:
                        if t.id is not None and t.id_type == "OBJECT" and t.id not in own:
                            bad.append((obj.name, d.data_path, t.id.name))
        if obj.parent is not None and obj.parent not in own:
            bad.append((obj.name, "parent", obj.parent.name))
        cons = list(obj.constraints)
        if obj.type == "ARMATURE":
            cons += [c for pb in obj.pose.bones for c in pb.constraints]
        for c in cons:
            t = getattr(c, "target", None)
            if t is not None and t not in own:
                bad.append((obj.name, c.name, t.name))
    return bad


def centers(rig):
    m = V.part_matrices(rig)
    return {p: np.array(m[p].translation) for p in V.PARTS}


def main(blend, outdir):
    a = V.open_rig(blend)
    b = V.append_rig(blend, "Victime")
    print("rigs :", a.name, "/", b.name, "-> objets :", len(a.collection.all_objects), "/", len(b.collection.all_objects))
    bad_a, bad_b = refs_outside(a), refs_outside(b)
    print("references hors de sa collection : attaquant", len(bad_a), "| victime", len(bad_b), bad_b[:5])

    V.place(b, (0.0, 4.0, 0.0), 180.0)
    a0, b0 = centers(a), centers(b)
    # poser la victime : ne doit pas bouger l'attaquant
    V.set_setting("Right Arm", "IK/FK", 1.0, rig=b)
    V.set_controls({"LowerTorso-FK": {"location": (0, -0.5, 0), "rotation_euler": (25, 0, 0)},
                    "RightArm-IK": {"location": (0, 1.0, 0.5)}}, rig=b)
    a1, b1 = centers(a), centers(b)
    da = max(np.linalg.norm(a1[p] - a0[p]) for p in V.PARTS)
    db = max(np.linalg.norm(b1[p] - b0[p]) for p in V.PARTS)
    # et inversement
    V.set_controls({"LowerTorso-FK": {"location": (0, -0.3, 0)}, "RightArm_FK": {"rotation_euler": (-80, 0, 0)}}, rig=a)
    b2 = centers(b)
    db2 = max(np.linalg.norm(b2[p] - b1[p]) for p in V.PARTS)
    ia = a.holders["Right Arm"]["IK/FK"]
    print(f"poser la victime : attaquant bouge de {da:.2e} (victime {db:.2f}) ; poser l'attaquant : victime bouge de {db2:.2e}")
    print(f"reglage IK/FK bras droit : attaquant {ia}, victime {b.holders['Right Arm']['IK/FK']}")

    # placement cuit
    V.set_controls({"LowerTorso-FK": {"location": (0, 0, 0), "rotation_euler": (0, 0, 0)},
                    "RightArm-IK": {"location": (0, 0, 0)}}, rig=b)
    fb = V.bake_parts(0, 0, rig=b)
    r, p = fb[0][1]["HumanoidRootPart"]
    print("HumanoidRootPart victime (repere Roblox) :", np.round(p, 4), "avant du perso (-Z local) ->", np.round(r @ [0, 0, -1], 3))

    # export des deux + aller-retour
    V.key_controls(0, {"LowerTorso-FK": {"location": (0, 0, 0)}}, rig=a)
    V.key_controls(10, {"LowerTorso-FK": {"location": (0, -0.4, 0.3)}}, rig=a)
    V.key_controls(0, {"LowerTorso-FK": {"rotation_euler": (0, 0, 0)}}, rig=b)
    V.key_controls(10, {"LowerTorso-FK": {"rotation_euler": (35, 0, 0)}}, rig=b)
    worst = 0.0
    for rig, nm in ((a, "attaquant"), (b, "victime")):
        fr = V.bake_parts(0, 10, rig=rig)
        path = os.path.join(outdir, f"two_rigs_{nm}.rbxmx")
        X.write_kfseq(fr, path, f"TwoRigs_{nm}")
        e = X.roundtrip_error(path, fr)
        worst = max(worst, max(v[0] for v in e.values()))
    print(f"aller-retour des deux exports : ecart max {worst:.2e} stud")
    ok = not bad_a and not bad_b and da < 1e-6 and db > 0.1 and db2 < 1e-6 and ia == 0.0 \
        and np.allclose(p, [0, 3, -4], atol=1e-4) and np.allclose(r @ [0, 0, -1], [0, 0, 1], atol=1e-4) and worst < 1e-3
    print("DEUX RIGS OK" if ok else "DEUX RIGS KO")
    return ok


if __name__ == "__main__":
    sys.exit(0 if main(sys.argv[1], sys.argv[2]) else 1)
