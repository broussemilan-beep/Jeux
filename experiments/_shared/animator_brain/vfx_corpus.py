"""
Corpus VFX du cerveau : lire de VRAIS packs d'effets Roblox (.rbxm) et en
tirer des distributions par ROLE d'emetteur (flash, onde, etincelle...).

Meme regle que corpus.py (PLAN.md, section 3) : aucun chiffre d'un pack
n'est copie dans un prototype. Il devient une distribution par role, et
c'est la distribution qu'on consulte. Les packs ne sont pas versionnes
(licences) : seules les mesures derivees le sont.

Usage :
    python3 -m animator_brain.vfx_corpus <pack.rbxm> <sortie.json>
"""
import collections
import json
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, ".."))

import rbxm_reader as R  # noqa: E402

EMITTER_CLASSES = ("ParticleEmitter", "Beam", "Trail", "PointLight", "Highlight")

# Enum ParticleOrientation (API Roblox) : 0 FacingCamera,
# 1 FacingCameraWorldUp, 2 VelocityParallel, 3 VelocityPerpendicular.
ORIENTATION = {0: "FacingCamera", 1: "FacingCameraWorldUp",
               2: "VelocityParallel", 3: "VelocityPerpendicular"}

_EXT = {
    "numseq": ("Size", "Transparency", "Squash", "WidthScale"),
    "colorseq": ("Color",),
    "numrange": ("Lifetime", "Speed", "Rotation", "RotSpeed"),
    "vector3": ("Acceleration",),
}


def load_emitters(path):
    """[{class, name, part, props..., attr: {...}}] pour chaque emetteur.
    `part` = referent de la Part ancetre la plus proche (= un effet)."""
    _v, _nt, _ni, ch = R.read_chunks(path)
    cl = R.parse_inst_chunks(ch)
    parent = R.parse_prnt_chunk(ch)
    cls_of = {r: c["name"] for c in cl.values() for r in c["referents"]}
    P = collections.defaultdict(dict)
    for cname, pname, _dt, vals in R.parse_prop_chunks(ch, cl):
        if isinstance(vals, dict) and "_raw_len" not in vals and "_error" not in vals:
            for r, v in vals.items():
                P[r][pname] = v
    want = {}
    for kind, names in _EXT.items():
        for c in EMITTER_CLASSES:
            for n in names:
                want[(c, n)] = kind
    for c in ("PointLight", "Highlight"):
        want[(c, "Color")] = "color3"
        want[(c, "FillColor")] = "color3"
    for (c, p), d in R.parse_prop_extended(ch, cl, want).items():
        if isinstance(d, dict) and "_error" not in d:
            for r, v in d.items():
                P[r][p] = v
    for (c, p), d in R.parse_enum_and_vector2(ch, cl).items():
        for r, v in d.items():
            P[r][p] = v
    attrs = R.parse_attributes(ch, cl)

    out = []
    for r, c in cls_of.items():
        if c not in EMITTER_CLASSES:
            continue
        a = r
        while a is not None and cls_of.get(a) != "Part":
            a = parent.get(a)
        e = {"class": c, "ref": r, "part": a, "attr": attrs.get(r, {})}
        e.update(P[r])
        out.append(e)
    return out


def _seq_max(s):
    return max(k[1] for k in s) if s else 0.0


def role(e):
    """Role d'un ParticleEmitter, deduit de ses proprietes (pas de son nom :
    les packs nomment tout "ParticleEmitter")."""
    life = (e.get("Lifetime") or (0, 0))[1]
    spd = (e.get("Speed") or (0, 0))[1]
    size = _seq_max(e.get("Size"))
    ori = e.get("Orientation")
    acc = e.get("Acceleration") or (0, 0, 0)
    if e.get("Enabled") and e.get("Rate", 0) > 0 and not e["attr"].get("EmitCount"):
        return "continu"
    if ori == 3 and spd <= 2:
        return "onde"            # plan couche au sol / face a la vitesse
    if ori == 2 and spd >= 15:
        return "etincelle"       # etiree dans le sens de la vitesse
    if acc[1] < -5 and spd > 5:
        return "debris"
    if life <= 0.2 and size >= 3 and spd <= 2:
        return "flash"
    if e.get("Drag", 0) >= 2 or (life >= 0.8 and e.get("LightEmission", 0) <= 0):
        return "fumee"
    if spd >= 15:
        return "eclat"
    return "forme"


def _dist(values):
    v = sorted(values)
    n = len(v)
    if not n:
        return None
    return {"n": n, "p10": v[int(n * 0.1)], "median": v[n // 2],
            "p90": v[min(n - 1, int(n * 0.9))]}


def role_stats(emitters):
    pe = [e for e in emitters if e["class"] == "ParticleEmitter"]
    by = collections.defaultdict(list)
    for e in pe:
        by[role(e)].append(e)
    out = {}
    for r, L in sorted(by.items(), key=lambda kv: -len(kv[1])):
        out[r] = {
            "n": len(L),
            "lifetime_max_s": _dist([(e.get("Lifetime") or (0, 0))[1] for e in L]),
            "speed_max_studs_s": _dist([(e.get("Speed") or (0, 0))[1] for e in L]),
            "size_max_studs": _dist([_seq_max(e.get("Size")) for e in L]),
            "emit_count": _dist([e["attr"].get("EmitCount", 0) for e in L]),
            "light_emission": _dist([e.get("LightEmission", 0) for e in L]),
            "brightness": _dist([e.get("Brightness", 1) for e in L]),
            "drag": _dist([e.get("Drag", 0) for e in L]),
            "size_curve_keys": _dist([len(e.get("Size") or []) for e in L]),
            "flipbook_fraction": sum(1 for e in L if e.get("FlipbookLayout", 0)) / len(L),
            "timescale_ramp_fraction": sum(1 for e in L if e["attr"].get("TimeScale_Duration")) / len(L),
        }
    return out


def effect_stats(emitters):
    """Un effet = une Part du pack. Combien d'emetteurs, quels roles
    combines, quel etalement dans le temps."""
    by = collections.defaultdict(list)
    for e in emitters:
        if e["part"] is not None:
            by[e["part"]].append(e)
    n_pe, n_roles, spans, delayed, combos = [], [], [], [], collections.Counter()
    for L in by.values():
        pe = [e for e in L if e["class"] == "ParticleEmitter"]
        if not pe:
            continue
        roles = sorted({role(e) for e in pe})
        n_pe.append(len(pe))
        n_roles.append(len(roles))
        combos[" + ".join(roles)] += 1
        ends = [e["attr"].get("EmitDelay", 0) + (e.get("Lifetime") or (0, 0))[1] for e in pe]
        spans.append(max(ends))
        delayed.append(sum(1 for e in pe if e["attr"].get("EmitDelay", 0) > 0) / len(pe))
    return {
        "n_effects": len(n_pe),
        "emitters_per_effect": _dist(n_pe),
        "roles_per_effect": _dist(n_roles),
        "effect_duration_s": _dist(spans),
        "delayed_emitter_fraction": _dist(delayed),
        "top_role_combos": combos.most_common(12),
    }


def trigger_convention(emitters):
    """Comment les emetteurs sont declenches : attributs presents, emetteurs
    desactives (joues par :Emit), valeurs frequentes."""
    pe = [e for e in emitters if e["class"] == "ParticleEmitter"]
    keys = collections.Counter(k for e in pe for k in e["attr"])
    vals = {k: collections.Counter(e["attr"][k] for e in pe if k in e["attr"]
                                   and isinstance(e["attr"][k], (int, float))).most_common(6)
            for k, _ in keys.most_common(8)}
    return {
        "n_particle_emitters": len(pe),
        "disabled_fraction": sum(1 for e in pe if not e.get("Enabled")) / max(1, len(pe)),
        "attribute_frequency": keys.most_common(12),
        "attribute_common_values": vals,
        "orientation": {ORIENTATION.get(k, k): v for k, v in
                        collections.Counter(e.get("Orientation") for e in pe).items()},
    }


def build(path, out_path, name):
    em = load_emitters(path)
    classes = collections.Counter(e["class"] for e in em)
    data = {
        "source": name,
        "note": "mesures derivees ; le pack source n'est pas versionne (licence)",
        "classes": dict(classes),
        "trigger_convention": trigger_convention(em),
        "effects": effect_stats(em),
        "roles": role_stats(em),
    }
    with open(out_path, "w") as f:
        json.dump(data, f, indent=1, ensure_ascii=False, default=str)
    return data


if __name__ == "__main__":
    src, dst = sys.argv[1], sys.argv[2]
    d = build(src, dst, os.path.basename(src).split("-", 1)[-1])
    print(json.dumps({k: d[k] for k in ("classes", "effects")}, indent=1, default=str)[:3000])
