"""
Reconstruit le trone/escalier/couronne comme de VRAIS maillages bpy
(pas les Empty utilises pour l'animation, pas les <Item class="Part">
de export_model.py) -- UV-deplies, materiaux PBR (ColorMap+NormalMap+
RoughnessMap[+MetalnessMap], voir gen_pbr_maps.py), exportes en FBX.

Pourquoi : SurfaceAppearance (le vrai systeme PBR de Roblox) ne
fonctionne QUE sur MeshPart, verifie par recherche (voir README,
"Texturing niveau expert"). Le trone/la couronne livres jusqu'ici sont
des Part primitives (Texture/StudsPerTileU seulement, pas de vraie
carte normale/rugosite). Ce script produit l'alternative MeshPart :
importer le FBX dans Roblox Studio cree un Model avec un MeshPart par
piece nommee, sur lequel un SurfaceAppearance (ColorMap/NormalMap/
RoughnessMap/MetalnessMap) peut etre attache -- etape qui demande le
compte Roblox de l'utilisateur (upload des images), documentee dans le
README plutot que faite ici.
"""
import math
import os

import numpy as np

import props

OUT = "../output"
PBR = os.path.abspath("../textures_pbr")
COLOR_DIR = os.path.abspath("../textures")

_ROT_Y_NEG90 = np.array([[0.0, 0.0, -1.0], [0.0, 1.0, 0.0], [1.0, 0.0, 0.0]])

# Materiau Roblox (props.py, champ "material") -> nom de fichier PBR
# (gen_pbr_maps.py) + taille de tuile en studs (memes valeurs que
# MATERIALS.studsPerTile dans le lecteur HTML, pour un aspect coherent
# entre le lecteur et le maillage reel).
MATERIAL_TO_PBR = {
    "Slate": ("slate", 2.6), "Marble": ("marble", 3.0),
    "Metal": ("metal", 1.3), "Fabric": ("fabric", 0.7),
    "Cobblestone": ("cobblestone", 2.6),
}


def _blender_material(name, pbr_name, is_metal):
    import bpy
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    out_node = nt.nodes.new("ShaderNodeOutputMaterial")
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")

    color_img = bpy.data.images.load(os.path.join(COLOR_DIR, f"{pbr_name}_color.png"))
    color_node = nt.nodes.new("ShaderNodeTexImage")
    color_node.image = color_img
    nt.links.new(color_node.outputs["Color"], bsdf.inputs["Base Color"])

    normal_img = bpy.data.images.load(os.path.join(PBR, f"{pbr_name}_normal.png"))
    normal_img.colorspace_settings.name = "Non-Color"
    normal_tex = nt.nodes.new("ShaderNodeTexImage")
    normal_tex.image = normal_img
    normal_map = nt.nodes.new("ShaderNodeNormalMap")
    nt.links.new(normal_tex.outputs["Color"], normal_map.inputs["Color"])
    nt.links.new(normal_map.outputs["Normal"], bsdf.inputs["Normal"])

    rough_img = bpy.data.images.load(os.path.join(PBR, f"{pbr_name}_roughness.png"))
    rough_img.colorspace_settings.name = "Non-Color"
    rough_node = nt.nodes.new("ShaderNodeTexImage")
    rough_node.image = rough_img
    nt.links.new(rough_node.outputs["Color"], bsdf.inputs["Roughness"])

    if is_metal:
        metal_img = bpy.data.images.load(os.path.join(PBR, f"{pbr_name}_metalness.png"))
        metal_img.colorspace_settings.name = "Non-Color"
        metal_node = nt.nodes.new("ShaderNodeTexImage")
        metal_node.image = metal_img
        nt.links.new(metal_node.outputs["Color"], bsdf.inputs["Metallic"])

    nt.links.new(bsdf.outputs["BSDF"], out_node.inputs["Surface"])
    return mat


def _build_object(spec, materials):
    import bpy
    name = spec["name"]
    size = spec["size"]
    pos = spec["pos"]
    rot = np.array(spec.get("rot", [[1, 0, 0], [0, 1, 0], [0, 0, 1]]))
    shape = spec.get("shape", "1")

    if shape == "2":  # Cylinder : Roblox = longueur le long de l'axe LOCAL X
        bpy.ops.mesh.primitive_cylinder_add(radius=size[1] / 2.0, depth=size[0], vertices=24)
        obj = bpy.context.active_object
        obj.data.transform(_mat4(_ROT_Y_NEG90, (0, 0, 0)))  # Blender Z -> local X
    elif shape == "0":  # Ball
        bpy.ops.mesh.primitive_uv_sphere_add(radius=size[0] / 2.0, segments=20, ring_count=12)
        obj = bpy.context.active_object
    else:  # Block
        bpy.ops.mesh.primitive_cube_add(size=1.0)
        obj = bpy.context.active_object
        obj.data.transform(_mat4(np.eye(3), (0, 0, 0), scale=size))

    obj.name = name
    obj.matrix_world = _mat4(rot, pos)

    tile = MATERIAL_TO_PBR.get(spec.get("material", ""), (None, 2.0))[1]
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.cube_project(cube_size=tile)
    bpy.ops.object.mode_set(mode="OBJECT")
    obj.select_set(False)

    mat_key = spec.get("material", "")
    if mat_key in materials:
        obj.data.materials.append(materials[mat_key])
    return obj


def _mat4(rot3, pos, scale=(1.0, 1.0, 1.0)):
    import mathutils
    m = mathutils.Matrix.Identity(4)
    for i in range(3):
        for j in range(3):
            m[i][j] = rot3[i][j] * scale[j]
        m[i][3] = pos[i]
    return m


def _export_selection(objs, out_name):
    import bpy
    bpy.ops.object.select_all(action="DESELECT")
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]

    out_path = os.path.abspath(os.path.join(OUT, out_name))
    bpy.ops.export_scene.fbx(filepath=out_path, use_selection=True,
                              global_scale=1.0, apply_unit_scale=True,
                              axis_forward="-Z", axis_up="Y")
    print(f"exporte {out_path} ({len(objs)} objets)")
    return out_path


def main():
    import bpy
    os.makedirs(OUT, exist_ok=True)

    # Reset UNE SEULE fois, avant de creer quoi que ce soit : un second
    # appel a read_factory_settings entre les deux exports (throne puis
    # couronne) DETRUIT les datablocks Material deja crees (bug trouve
    # par test -- "ReferenceError: StructRNA of type Material has been
    # removed" a la 2e construction) puisqu'il reinitialise TOUTES les
    # donnees bpy, pas seulement les objets de la scene. Trone et
    # couronne sont donc construits dans LA MEME session bpy, exportes
    # chacun via une simple selection differente plutot que deux resets.
    bpy.ops.wm.read_factory_settings(use_empty=True)

    # Un seul jeu de materiaux Blender, partage par toutes les pieces
    # d'une meme categorie -- coherent avec "un jeu de cartes PBR par
    # Material", pas un bake par piece individuelle.
    materials = {}
    for roblox_mat, (pbr_name, _tile) in MATERIAL_TO_PBR.items():
        materials[roblox_mat] = _blender_material(f"mat_{roblox_mat}", pbr_name, roblox_mat == "Metal")
    # Neon : pas de PBR classique (auto-eclaire), juste une couleur/emission plate.
    neon_mat = bpy.data.materials.new("mat_Neon")
    neon_mat.use_nodes = True
    nt = neon_mat.node_tree
    nt.nodes.clear()
    out_node = nt.nodes.new("ShaderNodeOutputMaterial")
    emit = nt.nodes.new("ShaderNodeEmission")
    emit.inputs["Color"].default_value = (0.85, 0.25, 0.22, 1.0)
    emit.inputs["Strength"].default_value = 2.0
    nt.links.new(emit.outputs["Emission"], out_node.inputs["Surface"])
    materials["Neon"] = neon_mat

    throne_specs = props.throne_parts() + props.staircase_parts()
    crown_specs = props.crown_parts()

    throne_objs = [_build_object(spec, materials) for spec in throne_specs]
    crown_objs = [_build_object(spec, materials) for spec in crown_specs]

    _export_selection(throne_objs, "throne_mesh.fbx")
    _export_selection(crown_objs, "crown_mesh.fbx")


if __name__ == "__main__":
    main()
