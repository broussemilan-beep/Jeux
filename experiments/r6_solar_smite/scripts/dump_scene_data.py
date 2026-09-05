"""
Assemble le JSON du lecteur HTML : les deux personnages (attaquant via
attacker_track(), mannequin via dummy_reaction()) resolus DIRECTEMENT via
anim_engine.build_rig()/apply_choreography()/sample() -- MEME convention
que r6_rock_kick/scripts/export_model.py (pas de .rbxmx exporte pour ce
prototype, cf. calibrate.py qui echantillonne deja de cette facon), PAS
la relecture d'un .rbxmx (resolve_rbxmx) utilisee par r6_hit_combo.

Ajoute au format commun (t, part -> {p, r}) : le contenu deja genere de
solar_track.json (couleurs/rayons/instants VFX, particules aspirees) sous
la cle "solar", FIN_MID_F (necessaire au lecteur pour reproduire
merged_core_position() en JS avec la MEME courbure que le corps -- pas
present tel quel dans solar_track.json), HIT_WINDOWS et tous les instants
de phase de choreography.py necessaires a la mise en scene VFX/camera du
lecteur (jamais devines cote JS).
"""
import json
import os

import anim_engine as ae
import choreography as ch
from calibrate import world_rotations
from r6_rig import PART_ORDER, PART_SIZES

OUT_HZ = 30
SOLAR_TRACK_JSON = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "output", "solar_track.json")


def build_frames(choreo_fn, secondary_motion, out_hz=OUT_HZ):
    keyframes, phases, preview_times, engine_opts = choreo_fn()
    duration = max(k["time"] for k in keyframes)
    objs = ae.build_rig()
    ae.apply_choreography(objs, keyframes, **engine_opts)
    samples = ae.sample(objs, duration_s=duration, sample_hz=out_hz, secondary_motion=secondary_motion)

    n = len(samples["HumanoidRootPart"])
    frames = []
    for i in range(n):
        t = samples["HumanoidRootPart"][i][0]
        rots = world_rotations(samples, i)
        f = {"t": round(t, 4)}
        for part in PART_ORDER:
            if part == "HumanoidRootPart":
                continue
            pos = samples[part][i][3]
            rot = rots[part]
            f[part] = {
                "p": [round(float(v), 4) for v in pos],
                "r": [round(float(v), 5) for row in rot for v in row],
            }
        frames.append(f)
    return frames, duration


def main():
    att_frames, att_dur = build_frames(ch.attacker_track, ch.ATTACKER_SECONDARY_MOTION)
    dum_frames, dum_dur = build_frames(ch.dummy_reaction, ch.DUMMY_SECONDARY_MOTION)

    with open(SOLAR_TRACK_JSON) as f:
        solar = json.load(f)
    solar["fin_mid_f"] = ch.FIN_MID_F

    out = {
        "fps": OUT_HZ,
        "duration": ch.TOTAL_DURATION,
        "part_sizes": {p: list(PART_SIZES[p]) for p in PART_ORDER},
        "part_order": PART_ORDER,
        "attacker_frames": att_frames,
        "dummy_frames": dum_frames,
        "solar": solar,
        "hit_windows": ch.HIT_WINDOWS,
        "char_z0": ch.CHAR_Z0,
        "dummy_z": ch.DUMMY_Z,
        "key_times": {
            "open_t": ch.OPEN_T,
            "charge_t": ch.CHARGE_T,
            "charge_hold_t": ch.CHARGE_HOLD_T,
            "strike1_windup_t": ch.STRIKE1_WINDUP_T,
            "strike1_coil_t": ch.STRIKE1_COIL_T,
            "strike1_coil_hold_t": ch.STRIKE1_COIL_HOLD_T,
            "strike1_t": ch.STRIKE1_T,
            "strike2_windup_t": ch.STRIKE2_WINDUP_T,
            "strike2_coil_t": ch.STRIKE2_COIL_T,
            "strike2_coil_hold_t": ch.STRIKE2_COIL_HOLD_T,
            "strike2_t": ch.STRIKE2_T,
            "fin_recover_t": ch.FIN_RECOVER_T,
            "fin_coil_t": ch.FIN_COIL_T,
            "fin_coil_hold_t": ch.FIN_COIL_HOLD_T,
            "fin_mid_t": ch.FIN_MID_T,
            "fin_strike_t": ch.FIN_STRIKE_T,
            "fin_followthrough_t": ch.FIN_FOLLOWTHROUGH_T,
            "fin_recover2_t": ch.FIN_RECOVER2_T,
        },
    }
    path = os.environ.get("SCENE_OUT", "/tmp/solar_smite_scene_data.json")
    with open(path, "w") as f:
        json.dump(out, f, separators=(",", ":"))
    print(f"ecrit {path}, {os.path.getsize(path)} octets, "
          f"{len(att_frames)} frames attaquant, {len(dum_frames)} frames mannequin, "
          f"duree {ch.TOTAL_DURATION:.3f}s")


if __name__ == "__main__":
    main()
