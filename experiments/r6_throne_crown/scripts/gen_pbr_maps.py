"""
Derive de vraies cartes NormalMap et RoughnessMap (le "niveau expert" que
les cartes couleur seules n'atteignaient pas -- voir README, section
"Texturing niveau expert, round 2") a partir des color maps deja
generees et verifiees seamless (gen_textures.py), pour Slate/Marble/
Metal/Fabric (Neon reste auto-eclaire, pas de PBR classique).

Pourquoi PARTIR des color maps existantes plutot que du bruit procedural
natif de Blender (Noise/Voronoi) : verifie par test que ce bruit n'est
PAS periodique par construction (contrairement aux sommes d'ondes a
frequences entieres de gen_textures.py, seamless PAR CONSTRUCTION) --
l'utiliser directement aurait reintroduit un risque de raccord visible a
la tuile, exactement le defaut deja trouve et corrige une fois sur les
color maps. Le NormalMap est donc calcule par bpy a partir du relief
(luminance) de l'image existante (un vrai "height-to-normal", technique
de production standard), qui HERITE de son caractere seamless -- pas
reinvente a partir de zero.

Le RoughnessMap est derive directement en Pillow (plus simple et plus
sur qu'un aller-retour par un bake Blender pour un signal aussi direct
que "contraste de luminance -> rugosite").
"""
import os

import numpy as np
from PIL import Image, ImageOps

IN = "../textures"
OUT = "../textures_pbr"
SIZE = 256

# (bump_strength, roughness_min, roughness_max, metalness) -- pas mesure,
# choix esthetique assume comme tel (cf. Reflectance dans export_model.py) :
# le metal brille (rugosite basse, metalness haute), le tissu ne reflete
# jamais (rugosite haute, pas de metalness).
#
# bump_strength calibre contre `ShaderNodeBump.Distance` fixe explicitement
# a 1.0 dans gen_normal_bpy() -- BUG TROUVE PAR TEST, PAS SUPPOSE : la
# valeur par defaut de Bump.Distance dans Blender est 0.001 (quasi nulle),
# pas 1.0 comme on l'attendrait par analogie avec Strength. Premiere passe
# de ce script : Distance jamais fixee => elle restait a 0.001 => la carte
# normale sortait bake quasi plate (std ~0.001) quel que soit Strength,
# verifie par un test isole (voir le calibrage : Strength=0.5/Distance=1.0
# donne un ecart-type de courbure de 0.177, contre une carte totalement
# plate a Distance=0.001 peu importe Strength). Les valeurs ci-dessous sont
# calibrees pour CETTE distance fixe de 1.0.
MATERIAL_PARAMS = {
    "slate":       {"bump": 1.4,  "rough": (0.55, 0.80), "metal": False},
    "marble":      {"bump": 0.7,  "rough": (0.25, 0.45), "metal": False},
    "metal":       {"bump": 0.9,  "rough": (0.12, 0.32), "metal": True},
    "fabric":      {"bump": 0.6,  "rough": (0.65, 0.88), "metal": False},
    "cobblestone": {"bump": 1.6,  "rough": (0.55, 0.85), "metal": False},
    "wood":        {"bump": 1.1,  "rough": (0.35, 0.60), "metal": False},
}


def gen_roughness(name, params):
    img = Image.open(f"{IN}/{name}_color.png").convert("L")
    arr = np.asarray(img, dtype=np.float64) / 255.0
    lo, hi = params["rough"]
    rough = lo + arr * (hi - lo)
    out = Image.fromarray(np.clip(rough * 255, 0, 255).astype(np.uint8), mode="L")
    out.save(f"{OUT}/{name}_roughness.png")
    print(f"ecrit {OUT}/{name}_roughness.png")


def gen_metalness(name, params):
    if not params["metal"]:
        return
    img = Image.open(f"{IN}/{name}_color.png").convert("L")
    arr = np.asarray(img, dtype=np.float64) / 255.0
    metal = 0.8 + 0.2 * arr   # quasi entierement metallique, legere variation
    out = Image.fromarray(np.clip(metal * 255, 0, 255).astype(np.uint8), mode="L")
    out.save(f"{OUT}/{name}_metalness.png")
    print(f"ecrit {OUT}/{name}_metalness.png")


def gen_normal_bpy(name, params):
    import bpy

    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.mesh.primitive_plane_add(size=2)
    obj = bpy.context.active_object
    # UV par defaut d'un plan Blender = (0,0)-(1,1), deja exactement ce
    # qu'il faut pour un bake 1:1 sans reprojection.

    mat = bpy.data.materials.new(f"{name}_bake_mat")
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    out_node = nt.nodes.new("ShaderNodeOutputMaterial")
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")

    color_path = os.path.abspath(f"{IN}/{name}_color.png")
    tex_node = nt.nodes.new("ShaderNodeTexImage")
    tex_node.image = bpy.data.images.load(color_path)

    bump = nt.nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = params["bump"]
    bump.inputs["Distance"].default_value = 1.0   # voir note MATERIAL_PARAMS -- default Blender = 0.001
    nt.links.new(tex_node.outputs["Color"], bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    nt.links.new(tex_node.outputs["Color"], bsdf.inputs["Base Color"])
    nt.links.new(bsdf.outputs["BSDF"], out_node.inputs["Surface"])

    obj.data.materials.append(mat)

    bake_img = bpy.data.images.new(f"{name}_normal", SIZE, SIZE)
    bake_node = nt.nodes.new("ShaderNodeTexImage")
    bake_node.image = bake_img
    nt.nodes.active = bake_node

    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = 8
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)

    bpy.ops.object.bake(type="NORMAL", normal_space="TANGENT")

    out_path = os.path.abspath(f"{OUT}/{name}_normal.png")
    bake_img.filepath_raw = out_path
    bake_img.file_format = "PNG"
    bake_img.save()
    print(f"ecrit {out_path}")


def main():
    os.makedirs(OUT, exist_ok=True)
    for name, params in MATERIAL_PARAMS.items():
        gen_roughness(name, params)
        gen_metalness(name, params)
        gen_normal_bpy(name, params)


if __name__ == "__main__":
    main()
