"""
Lecteur jouable (page HTML autonome) de « Un seul coup », à partir des
FICHIERS EXPORTÉS (KeyframeSequences relues par l'équation du moteur) et de
staging.json (caméra, décor, destruction, sons) : la même source que le
module Roblox. three.js r134 embarqué (CARNET 4b.28 : jamais de CDN).

Usage : python3 build_player.py   ->   ../output/un_seul_coup.html
"""
import base64
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.environ.get("USC_OUT") or os.path.join(HERE, "..", "output")
DRAGON = os.path.join(HERE, "..", "..", "r6_poing_dragon", "scripts")
sys.path.insert(0, os.path.join(HERE, "..", "..", "_shared"))
sys.path.insert(0, DRAGON)
sys.path.insert(0, HERE)

import staging as ST  # noqa: E402
from animator_brain import roblox_export as X  # noqa: E402
import importlib.util  # noqa: E402


def _dragon(nom):
    """Module du Poing du Dragon chargé par son CHEMIN (mêmes noms de fichiers ici)."""
    spec = importlib.util.spec_from_file_location("dragon_" + nom, os.path.join(DRAGON, nom + ".py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


_BP = _dragon("build_player")
pack, PARTS = _BP.pack, _BP.PARTS

VS = os.path.join(HERE, "..", "..", "_shared", "vfx_studio")


def main():
    staging, aw, vw = ST.main()
    ver = json.load(open(os.path.join(OUT, "verification.json")))
    noms = sorted({s["son"] for s in staging["sons"]})
    data = {
        "fps": staging["fps"], "end": staging["end_f"], "parts": PARTS, "sizes": X.RIG["part_sizes"],
        "att": pack(aw), "vic": pack(vw), "camera": staging["camera"], "events": staging["events"],
        "decor": staging["decor"], "sons": staging["sons"], "beats": staging["beats"],
        "contact_t": staging["contact_f"] / staging["fps"],
        "wav": {n: "data:audio/wav;base64," + base64.b64encode(open(os.path.join(VS, "sons", n + ".wav"), "rb").read()).decode()
                for n in noms},
        "verif": {"cles": ver["cles"], "aller_retour": ver["aller_retour_max"], "sens": all(ver["sens_roblox"].values())},
    }
    html = open(os.path.join(HERE, "player_template.html")).read()
    three = os.path.join(HERE, "..", "..", "r6_black_hole", "scripts", "vendor", "three.min.js")
    html = html.replace("/*__THREE_JS__*/", open(three).read())
    html = html.replace("/*__DATA__*/null", json.dumps(data, separators=(",", ":")))
    path = os.path.join(OUT, "un_seul_coup.html")
    open(path, "w").write(html)
    print(path, len(html) // 1024, "Ko")
    return path


if __name__ == "__main__":
    main()
