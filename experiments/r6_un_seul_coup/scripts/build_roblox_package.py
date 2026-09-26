"""
Package Roblox prêt à glisser dans Studio : output/UnSeulCoup.rbxmx

    Folder UnSeulCoup
      Model Attaquant            R6 généré depuis les C0/C1 du vrai rig, regarde -Z
      Model Victime              R6 (noob), devant l'attaquant, tourné vers lui
      Folder Animations          UnSeulCoup_Attaquant (markers) + UnSeulCoup_Victime
      ModuleScript UnSeulCoup    (luau/UnSeulCoup.luau)
      ModuleScript UnSeulCoupData (généré ici depuis staging.json)
      Script Demo                RunContext = Client : rejoue la technique en boucle

Génère d'abord luau/UnSeulCoupData.luau (caméra, événements, décor de la
destruction, sons, positions de fin) depuis output/staging.json -- la même
source que le lecteur HTML. Puis relit le fichier ÉCRIT (références uniques,
pose de repos, sens, markers, scripts).

Usage : python3 build_roblox_package.py
"""
import importlib.util
import json
import os
import sys
import xml.etree.ElementTree as ET

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
OUT = os.path.join(ROOT, "output")
LUAU = os.path.join(ROOT, "luau")
sys.path.insert(0, HERE)


def _charger(nom, chemin):
    spec = importlib.util.spec_from_file_location(nom, chemin)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


# briques génériques du package M1 (génération de rig R6, relecture) et
# l'écriture de littéraux Luau du Poing du Dragon, réutilisées telles quelles
P = _charger("m1_package", os.path.join(HERE, "..", "..", "r6_m1_v222", "scripts", "build_roblox_package.py"))
lua = _charger("dragon_package", os.path.join(HERE, "..", "..", "r6_poing_dragon", "scripts", "build_roblox_package.py")).lua

SCENE = json.load(open(os.path.join(OUT, "scene.json")))
STAGING = json.load(open(os.path.join(OUT, "staging.json")))
DIST = round(SCENE["distance"], 3)
FPS = STAGING["fps"]

P.COLORS = {
    "Attaquant": {"Head": (243, 207, 168), "Torso": (242, 195, 24), "Left Arm": (242, 195, 24),
                  "Right Arm": (242, 195, 24), "Left Leg": (242, 195, 24), "Right Leg": (242, 195, 24),
                  "HumanoidRootPart": (163, 162, 165)},
    "Victime": {"Head": (245, 205, 48), "Torso": (13, 105, 172), "Left Arm": (245, 205, 48),
                "Right Arm": (245, 205, 48), "Left Leg": (164, 189, 71), "Right Leg": (164, 189, 71),
                "HumanoidRootPart": (163, 162, 165)},
}


def final_positions():
    # (chargé par son chemin : le module du Poing du Dragon, chargé plus haut,
    # a mis son propre dossier en tête de sys.path, avec un staging.py homonyme)
    ST = _charger("usc_staging", os.path.join(HERE, "staging.py"))
    aw, vw = ST.tracks()
    a, v = aw[-1]["Torso"][1], vw[-1]["Torso"][1]
    return [round(float(a[0]), 3), 3.0, round(float(a[2]), 3)], [round(float(v[0]), 3), 3.0, round(float(v[2]), 3)]


def evenements():
    E = []
    ev = {e["kind"]: e for e in STAGING["events"]}
    d, si, ch = ev["depart_sol"], ev["sillage"], ev["charge_sol"]
    E.append({"frame": d["frame"], "kind": "depart_sol", "pos": d["pos"], "rayon": d["rayon"]})
    E.append({"frame": si["frame"], "kind": "sillage", "de": si["de"], "a": si["a"]})
    E.append({"frame": ch["frame"], "kind": "charge_sol", "pos": ch["pos"], "fin": ch["fin"]})
    E.append({"frame": ev["tourbillon"]["frame"], "kind": "tourbillon", "fin": ev["tourbillon"]["fin"]})
    E.append({"frame": ev["souffle_sol"]["frame"], "kind": "souffle_sol", "pos": ev["souffle_sol"]["pos"]})
    E.append({"frame": STAGING["contact_f"], "kind": "destruction"})
    for s in STAGING["sons"]:
        E.append({"frame": int(round(s["t"] * FPS)), "kind": "son", "son": s["son"], "volume": s["volume"],
                  "hauteur": s["hauteur"]})
    return sorted(E, key=lambda e: e["frame"]), ev


def write_data_module():
    fa, fv = final_positions()
    E, ev = evenements()
    cam = [{"f": f, "eye": eye, "look": look, "fov": fov, "cut": mode == "cut"} for f, eye, look, fov, mode in STAGING["camera"]]
    D = STAGING["decor"]
    decor = {"vitesse": D["vitesse"], "sillon": D["sillon"], "fente": D["fente"], "choc_montagne": D["choc_montagne"],
             "roches": D["roches"], "fumees": D["fumees"], "nuages": D["nuages"]}
    b = ev["blanc"]
    body = (
        "--!nonstrict\n"
        "-- GÉNÉRÉ par scripts/build_roblox_package.py depuis output/staging.json : ne pas éditer à la main.\n"
        "-- Repère de scène : origine au sol sous le HumanoidRootPart de l'attaquant au lancement, avant = -Z.\n"
        "return {\n"
        f"\tFPS = {FPS},\n"
        f"\tEND = {STAGING['end_f']},\n"
        f"\tDISTANCE = {DIST},\n"
        f"\tCONTACT_F = {STAGING['contact_f']},\n"
        f"\tCONTACT_T = {round(STAGING['contact_f'] / FPS, 4)},\n"
        f"\tINVERSE = {{ {ev['inverse']['frame']}, {ev['inverse']['fin']} }},\n"
        f"\tBLANC = {{ {b['frame']}, {b['plein']}, {b['fin']} }},\n"
        f"\tFONDU_NOIR = {{ {ev['fondu_noir']['frame']}, {ev['fondu_noir']['fin']} }},\n"
        f"\tSECOUSSES = {lua([[e['frame'], e['fin'], e['amp']] for e in STAGING['events'] if e['kind'] == 'secousse'], 1)},\n"
        f"\tVICTIME = {{ cachee = {ev['cacher_victime']['debut']}, pov = {lua(ev['cacher_victime']['pov'])} }},\n"
        f"\tFINAL = {{ attacker = {lua(fa)}, victim = {lua(fv)} }},\n"
        f"\tCAMERA = {lua(cam, 1)},\n"
        f"\tEVENTS = {lua(E, 1)},\n"
        f"\tDECOR = {lua(decor, 1)},\n"
        "}\n"
    )
    path = os.path.join(LUAU, "UnSeulCoupData.luau")
    open(path, "w").write(body)
    return path


def build():
    data_path = write_data_module()
    root = ET.Element("roblox", {"xmlns:xmime": "http://www.w3.org/2005/05/xmlmime",
                                 "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
                                 "xsi:noNamespaceSchemaLocation": "http://www.roblox.com/roblox.xsd",
                                 "version": "4"})
    folder, _fp = P.item(root, "Folder", "UnSeulCoup")
    att_rot, att_pos = np.eye(3), np.array([0.0, 3.0, 0.0])
    ry = np.array([[-1.0, 0, 0], [0, 1.0, 0], [0, 0, -1.0]])
    P.build_rig(folder, "Attaquant", att_rot, att_pos)
    P.build_rig(folder, "Victime", ry, att_pos + np.array([0.0, 0.0, -DIST]))
    anims, _ap = P.item(folder, "Folder", "Animations")
    P.copy_kfs(anims, os.path.join(OUT, "usc_attaquant.rbxmx"), len(SCENE["markers"]))
    P.copy_kfs(anims, os.path.join(OUT, "usc_victime.rbxmx"), 0)
    P.script_item(folder, "ModuleScript", "UnSeulCoup", os.path.join(LUAU, "UnSeulCoup.luau"))
    P.script_item(folder, "ModuleScript", "UnSeulCoupData", data_path)
    P.script_item(folder, "Script", "Demo", os.path.join(LUAU, "Demo.client.luau"), run_context=2)
    tree = ET.ElementTree(root)
    ET.indent(tree, space="  ")
    path = os.path.join(OUT, "UnSeulCoup.rbxmx")
    tree.write(path, encoding="utf-8", xml_declaration=True)
    return path


if __name__ == "__main__":
    P.DIST = DIST
    p = build()
    rep = P.verify(p)
    print(json.dumps({k: v for k, v in rep.items()}, ensure_ascii=False, default=str))
    ok = rep["referents_uniques"] and rep["pose_repos_coherente_max_ecart"] < 1e-6 and all(rep["sens"].values()) \
        and rep["animations"] == {"UnSeulCoup_Attaquant": len(SCENE["markers"]), "UnSeulCoup_Victime": 0} \
        and rep["demo_run_context_client"] and len(rep["scripts"]) == 3
    print("PACKAGE OK" if ok else "PACKAGE KO", "->", p, os.path.getsize(p) // 1024, "Ko")
    sys.exit(0 if ok else 1)
