"""
Package Roblox pret a glisser dans Studio : output/PoingDuDragon.rbxmx

    Folder PoingDuDragon
      Model Attaquant          R6 genere depuis les C0/C1 du vrai rig, regarde -Z
      Model Victime            R6 (couleurs du noob), devant l'attaquant, tourne vers lui
      Folder Animations        PoingDuDragon_Attaquant (markers) + PoingDuDragon_Victime
      ModuleScript DragonFist      (luau/DragonFist.luau)
      ModuleScript DragonFistData  (genere ici depuis staging.json)
      ModuleScript VFXStudio   (studio VFX : moteur d'execution des recettes)
      ModuleScript VFXRecettes (studio VFX : recettes compilees + table des assets)
      Script Demo              RunContext = Client : rejoue la technique en boucle

Genere d'abord luau/DragonFistData.luau (camera, evenements, positions de
fin) depuis output/staging.json -- la meme source que le lecteur HTML.
Puis relit le fichier ECRIT : references uniques, pose de repos coherente,
sens, markers, scripts.

Usage : python3 build_roblox_package.py
"""
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
# briques generiques du package M1 (generation de rig R6, relecture), reutilisees telles quelles
sys.path.insert(0, os.path.join(HERE, "..", "..", "r6_m1_v222", "scripts"))
import build_roblox_package as P  # noqa: E402

VS = os.path.join(HERE, "..", "..", "_shared", "vfx_studio")
sys.path.insert(0, VS)
import compile_roblox as C  # noqa: E402

SCENE = json.load(open(os.path.join(OUT, "scene.json")))
STAGING = json.load(open(os.path.join(OUT, "staging.json")))
DIST = round(SCENE["distance"], 3)

P.COLORS = {
    "Attaquant": {"Head": (233, 184, 143), "Torso": (29, 30, 37), "Left Arm": (233, 184, 143),
                  "Right Arm": (233, 184, 143), "Left Leg": (35, 36, 44), "Right Leg": (35, 36, 44),
                  "HumanoidRootPart": (163, 162, 165)},
    "Victime": {"Head": (245, 205, 48), "Torso": (13, 105, 172), "Left Arm": (245, 205, 48),
                "Right Arm": (245, 205, 48), "Left Leg": (164, 189, 71), "Right Leg": (164, 189, 71),
                "HumanoidRootPart": (163, 162, 165)},
}


def lua(v, ind=1):
    """Valeur Python -> litteral Luau (tables 1-indexees)."""
    pad = "\t" * ind
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        return repr(round(float(v), 4)) if isinstance(v, float) else str(v)
    if isinstance(v, str):
        return json.dumps(v)
    if isinstance(v, (list, tuple)):
        if all(isinstance(x, (int, float)) for x in v):
            return "{ " + ", ".join(lua(x) for x in v) + " }"
        return "{\n" + "".join(f"{pad}\t{lua(x, ind + 1)},\n" for x in v) + pad + "}"
    if isinstance(v, dict):
        return "{ " + ", ".join(f"{k} = {lua(x, ind + 1)}" for k, x in v.items()) + " }"
    raise TypeError(type(v))


def final_positions():
    """Position du HumanoidRootPart a la fin = sous le torse, a hauteur de
    hanche (repere de scene, sol a y = 0)."""
    import staging as ST
    aw, vw = ST.tracks()
    a = aw[-1]["Torso"][1]
    v = vw[-1]["Torso"][1]
    return [round(float(a[0]), 3), 3.0, round(float(a[2]), 3)], [round(float(v[0]), 3), 3.0, round(float(v[2]), 3)]


def write_data_module():
    fa, fv = final_positions()
    cam = [{"f": f, "eye": eye, "look": look, "fov": fov, "cut": mode == "cut"} for f, eye, look, fov, mode in STAGING["camera"]]
    events = sorted(STAGING["events"], key=lambda e: e["frame"])
    # studio VFX : chaque recette est compilée pour Roblox (séquences 0-1 à
    # 20 points, couleurs 0-1, durées des sons) par le compilateur du studio
    events = [dict(e, recette=C.compiler(e["recette"])) if e["kind"] == "studio" else e for e in events]
    whip = next(e["frame"] for e in events if e["kind"] == "whip")
    body = (
        "--!nonstrict\n"
        "-- GENERE par scripts/build_roblox_package.py depuis output/staging.json : ne pas editer a la main.\n"
        "-- Repere de scene : origine au sol sous le HumanoidRootPart de l'attaquant au lancement, avant = -Z.\n"
        "return {\n"
        f"\tFPS = {STAGING['fps']},\n"
        f"\tEND = {STAGING['end_f']},\n"
        f"\tDISTANCE = {DIST},\n"
        f"\tWHIP_FRAME = {whip},\n"
        f"\tCINEMA_DOSE = {STAGING.get('cinema_dose', 1)},\n"
        f"\tTEINTE = {{ 196, {STAGING['markers']['strike'] + 12} }},\n"
        f"\tFINAL = {{ attacker = {lua(fa)}, victim = {lua(fv)} }},\n"
        f"\tCAMERA = {lua(cam, 1)},\n"
        f"\tEVENTS = {lua(events, 1)},\n"
        "}\n"
    )
    path = os.path.join(LUAU, "DragonFistData.luau")
    open(path, "w").write(body)
    return path, fa, fv


def build():
    data_path, fa, fv = write_data_module()
    root = ET.Element("roblox", {"xmlns:xmime": "http://www.w3.org/2005/05/xmlmime",
                                 "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
                                 "xsi:noNamespaceSchemaLocation": "http://www.roblox.com/roblox.xsd",
                                 "version": "4"})
    folder, _fp = P.item(root, "Folder", "PoingDuDragon")
    att_rot, att_pos = np.eye(3), np.array([0.0, 3.0, 0.0])
    ry = np.array([[-1.0, 0, 0], [0, 1.0, 0], [0, 0, -1.0]])
    P.build_rig(folder, "Attaquant", att_rot, att_pos)
    P.build_rig(folder, "Victime", ry, att_pos + np.array([0.0, 0.0, -DIST]))
    anims, _ap = P.item(folder, "Folder", "Animations")
    P.copy_kfs(anims, os.path.join(OUT, "dragon_attaquant.rbxmx"), len(SCENE["markers"]))
    P.copy_kfs(anims, os.path.join(OUT, "dragon_victime.rbxmx"), 0)
    P.script_item(folder, "ModuleScript", "DragonFist", os.path.join(LUAU, "DragonFist.luau"))
    P.script_item(folder, "ModuleScript", "DragonFistData", data_path)
    # studio VFX : moteur d'exécution + assets (textures / sons -> rbxassetid)
    C.main()
    P.script_item(folder, "ModuleScript", "VFXStudio", os.path.join(VS, "luau", "VFXStudio.luau"))
    P.script_item(folder, "ModuleScript", "VFXRecettes", os.path.join(VS, "luau", "VFXRecettes.luau"))
    P.script_item(folder, "Script", "Demo", os.path.join(LUAU, "Demo.client.luau"), run_context=2)
    tree = ET.ElementTree(root)
    ET.indent(tree, space="  ")
    path = os.path.join(OUT, "PoingDuDragon.rbxmx")
    tree.write(path, encoding="utf-8", xml_declaration=True)
    return path


if __name__ == "__main__":
    P.DIST = DIST
    p = build()
    rep = P.verify(p)
    print(json.dumps(rep, indent=1, ensure_ascii=False, default=str))
    ok = rep["referents_uniques"] and rep["pose_repos_coherente_max_ecart"] < 1e-6 and all(rep["sens"].values()) \
        and rep["animations"] == {"PoingDuDragon_Attaquant": len(SCENE["markers"]), "PoingDuDragon_Victime": 0} \
        and rep["demo_run_context_client"] and len(rep["scripts"]) == 5
    print("PACKAGE OK" if ok else "PACKAGE KO", "->", p, os.path.getsize(p) // 1024, "Ko")
    sys.exit(0 if ok else 1)
