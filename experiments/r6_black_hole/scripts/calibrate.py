"""
Verifie par le calcul (pas a l'oeil) : que le placement des pieds reste
plausible AU SOL (jamais un pied qui flotte/s'enfonce sans raison) et
qu'il est bien AERIEN (jamais un pied qui traverse le sol) pendant la
levitation -- 2 modes de check distincts, voir docstring de
choreography.py sur pourquoi ce prototype en a besoin (aucun predecesseur
ne quittait le sol) -- que la structure des deux rigs reste rigide/finie
partout, et que le script VFX (black_hole_track.py) reste numeriquement
sain (pas de NaN, coeur jamais plus grand que le disque, tous les
fragments avales avant l'atterrissage) -- meme discipline que
r6_solar_smite/calibrate.py.
"""
import numpy as np

import anim_engine as ae
import choreography as ch
import pipeline
import black_hole_track as bh
from r6_rig import PART_ORDER, PART_SIZES

TOLERANCE = 0.05  # stud -- meme seuil resserre que r6_solar_smite (voir son README pour la justification/source)


def world_rotations(samples, i):
    rot = {}
    root_r = ae.euler_xyz_matrix(*samples["HumanoidRootPart"][i][1])
    rot["HumanoidRootPart"] = root_r
    torso_r = root_r @ ae.euler_xyz_matrix(*samples["Torso"][i][1])
    rot["Torso"] = torso_r
    for part in PART_ORDER:
        if part in ("HumanoidRootPart", "Torso"):
            continue
        rot[part] = torso_r @ ae.euler_xyz_matrix(*samples[part][i][1])
    return rot


def tip_world(samples, part, i, end="bottom"):
    world_pos = np.array(samples[part][i][3])
    rots = world_rotations(samples, i)
    half = PART_SIZES[part][1] / 2.0
    sign = -1.0 if end == "bottom" else 1.0
    return world_pos + rots[part] @ np.array([0.0, sign * half, 0.0])


def _run():
    return pipeline.build_samples(sample_hz=60)


def idx_at(t, hz=60):
    return round(t * hz)


def main():
    samples, duration = _run()
    n = len(samples["Left Leg"])
    times = [s[0] for s in samples["Left Leg"]]

    print("=== placement des pieds -- CHAQUE echantillon (60 Hz), tolerance", TOLERANCE, "stud ===")
    print("  (appuis : hauteur ET derive horizontale vs cible ; hors appui : jamais sous le sol)")
    blend = 2 / 30
    problems, clipping = [], []
    worst_contact = {}
    # decollage AUTOMATIQUE (pied qui part a pleine extension, voir
    # animator_brain.constraints.foot_lock_pass) : la fin reelle de l'appui
    # est celle mesuree par la passe, pas la borne de securite t1.
    toe_off = pipeline.last_log()["constraints"].get("auto_toe_off", {})
    for leg in ("Right Leg", "Left Leg"):
        wins = []
        for c in ch.CONTACTS:
            if c["leg"] != leg:
                continue
            c = dict(c)
            if c.get("release_after") is not None and leg in toe_off:
                c["t1"] = min(c["t1"], toe_off[leg] - 1 / 60)
            wins.append(c)
        for i in range(n):
            t = times[i]
            tip = tip_world(samples, leg, i, "bottom")
            inside = [c for c in wins if c["t0"] + blend <= t <= c["t1"]]
            if inside:
                tgt = np.array(inside[0]["target"])
                err_y = abs(tip[1] - tgt[1])
                err_h = float(np.hypot(tip[0] - tgt[0], tip[2] - tgt[2]))
                w = worst_contact.setdefault(leg, [0.0, 0.0])
                w[0], w[1] = max(w[0], err_y), max(w[1], err_h)
                if err_y > TOLERANCE or err_h > TOLERANCE:
                    problems.append((leg, round(t, 3), round(err_y, 3), round(err_h, 3)))
            elif tip[1] < -TOLERANCE:
                clipping.append((leg, round(t, 3), round(float(tip[1]), 3)))
    for leg, (wy, wh) in worst_contact.items():
        print(f"  {leg:10s} pendant les appuis : ecart max hauteur={wy:.4f}  derive horizontale max={wh:.4f} stud")
    print(f"\n{'aucune anomalie' if not problems else str(len(problems)) + ' anomalie(s)'} de placement au sol"
          + ("" if not problems else f" -- premieres : {problems[:4]}"))
    print(f"{'aucun clipping' if not clipping else str(len(clipping)) + ' clipping(s)'} hors appui"
          + ("" if not clipping else f" -- premiers : {clipping[:4]}"))
    log = pipeline.last_log()
    print(f"  (passe foot_lock : deplacement max du bassin={log['constraints'].get('max_root_shift')} stud, "
          f"residu max={log['constraints'].get('max_residual')} stud, "
          f"echantillons inexacts={log['constraints'].get('inexact_samples')} ; "
          f"ajustements d'ordre des cles d'overlap : {len(log['overlap_adjustments'])})")

    print("\n=== clearance mesuree aux instants-cles de la levitation (stud au-dessus du sol) ===")
    for name, t in (("RISE (decollage)", ch.RISE_T), ("CLIMAX", ch.CLIMAX_T), ("RELEASE", ch.RELEASE_T)):
        i = idx_at(t)
        ly = tip_world(samples, "Left Leg", i, "bottom")[1]
        ry = tip_world(samples, "Right Leg", i, "bottom")[1]
        print(f"  {name:20s} t={t:.3f}  clearance min={min(ly, ry):.3f} stud")

    print("\n=== structure : rotations finies et plausibles ===")
    bad = []
    for part in PART_ORDER:
        for s in samples[part]:
            rx, ry, rz = s[1]
            if not all(np.isfinite([rx, ry, rz])):
                bad.append(f"{part} : rotation non finie")
                break
            if max(abs(rx), abs(ry), abs(rz)) > 260:
                bad.append(f"{part} : rotation hors plage plausible ({rx:.1f},{ry:.1f},{rz:.1f})")
                break
    print("  OK" if not bad else "  STRUCTURE KO : " + "; ".join(bad))

    print(f"\nDuree totale : {ch.TOTAL_DURATION:.3f}s (echantillonnee : {duration:.3f}s)")

    # =====================================================================
    # VFX (black_hole_track.py) -- verifie numeriquement, pas juste relu :
    # pas de NaN/inf sur toute la timeline, coeur JAMAIS plus grand que le
    # disque (l'occulteur ne doit jamais depasser son propre halo), tous
    # les fragments avales (scale=0, invisible) avant l'atterrissage --
    # sinon un debris resterait fige en l'air une fois le sol de nouveau
    # visible, incoherence immediatement visible a l'ecran.
    # =====================================================================
    print("\n=== VFX (black_hole_track.py) : sante numerique ===")
    ts = np.linspace(0.0, ch.TOTAL_DURATION, 500)
    nonfinite = 0
    core_gt_disk = 0
    max_jump = {}
    prev = {}
    for t in ts:
        r, c = bh.disk_radius(t), bh.core_radius(t)
        if c > r + 1e-9:
            core_gt_disk += 1
        for i in range(bh.N_DEBRIS):
            pos, scale, vis = bh.debris_state(i, t)
            if not np.all(np.isfinite(pos)):
                nonfinite += 1
                continue
            if i in prev and vis and prev[i][1]:
                max_jump[i] = max(max_jump.get(i, 0.0), float(np.linalg.norm(pos - prev[i][0])))
            prev[i] = (pos, vis)
    still_visible_at_land = sum(
        1 for i in range(bh.N_DEBRIS)
        if bh.debris_state(i, ch.LAND_T)[2] and bh.debris_state(i, ch.LAND_T)[1] > 0.01
    )
    print(f"  positions non-finies : {nonfinite}")
    print(f"  coeur > disque (violations) : {core_gt_disk}")
    print(f"  fragments encore visibles a LAND_T ({ch.LAND_T:.3f}s) : {still_visible_at_land} / {bh.N_DEBRIS}")
    print(f"  plus gros saut inter-echantillon (dt~{ts[1]-ts[0]:.4f}s) : {max(max_jump.values()) if max_jump else 0.0:.3f} stud")
    vfx_ok = nonfinite == 0 and core_gt_disk == 0 and still_visible_at_land == 0
    print("  VFX OK" if vfx_ok else "  VFX KO -- voir details ci-dessus")

    # -- coherence timeline : le VFX doit finir (collapse) avant ou pile a
    # l'atterrissage, pas apres (sinon un fragment/le disque resteraient
    # visibles alors que le personnage a deja les pieds au sol).
    collapse_end = ch.VFX_EVENTS["collapse"]["t1"]
    print(f"\n  collapse['t1']={collapse_end:.3f}s  vs  LAND_T={ch.LAND_T:.3f}s  "
          f"({'OK, VFX fini avant atterrissage' if collapse_end <= ch.LAND_T + 1e-6 else 'KO -- VFX deborde sur l atterrissage'})")


if __name__ == "__main__":
    main()
