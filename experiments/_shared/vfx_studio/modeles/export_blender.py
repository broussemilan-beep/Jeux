"""
Export Blender du DRAGON (modeles/dragon.json + dragon_atlas.png) :
- dragon.fbx pour Roblox : maillage + armature (Racine sans influence, Tete,
  Os01..Os24 enfants de Racine, à plat), poids de dragon.json, réglages de la
  doc officielle (art/modeling/export-requirements.md : Apply Scalings = FBX
  Unit Scale, pas de « leaf bones ») ;
- rendus de contrôle Cycles (--rendu dossier) : 3 vues du modèle au repos.

Usage : python3 export_blender.py [--rendu dossier]
"""
import json
import math
import os
import sys

import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))


def scene_vide():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def construire():
    d = json.load(open(os.path.join(HERE, "dragon.json")))
    P = [tuple(d["positions"][i:i + 3]) for i in range(0, len(d["positions"]), 3)]
    # Blender : Z en haut ; notre repère : Y en haut -> (x, y, z) -> (x, -z, y)
    Pb = [(x, -z, y) for (x, y, z) in P]
    F = [tuple(d["indices"][i:i + 3]) for i in range(0, len(d["indices"]), 3)]
    me = bpy.data.meshes.new("Dragon")
    me.from_pydata(Pb, [], F)
    me.update()
    uvl = me.uv_layers.new(name="UV")
    uv = d["uv"]
    for poly in me.polygons:
        for li in poly.loop_indices:
            vi = me.loops[li].vertex_index
            uvl.data[li].uv = (uv[2 * vi], uv[2 * vi + 1])
    for p in me.polygons:
        p.use_smooth = True
    ob = bpy.data.objects.new("Dragon", me)
    bpy.context.scene.collection.objects.link(ob)
    # matériau : atlas
    mat = bpy.data.materials.new("Dragon")
    mat.use_nodes = True
    nt = mat.node_tree
    bsdf = nt.nodes.get("Principled BSDF")
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = bpy.data.images.load(os.path.join(HERE, "dragon_atlas.png"))
    nt.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    bsdf.inputs["Metallic"].default_value = 0.55
    bsdf.inputs["Roughness"].default_value = 0.32
    me.materials.append(mat)
    # armature
    arm = bpy.data.armatures.new("Squelette")
    ao = bpy.data.objects.new("Squelette", arm)
    bpy.context.scene.collection.objects.link(ao)
    bpy.context.view_layer.objects.active = ao
    bpy.ops.object.mode_set(mode="EDIT")
    racine = arm.edit_bones.new("Racine")
    racine.head, racine.tail = (0, 0, 0), (0, 0, 0.3)
    noms = ["Tete"] + [f"Os{i + 1:02d}" for i in range(len(d["os_x"]))]
    xs = [-1.2] + d["os_x"]
    for nom, x in zip(noms, xs):
        b = arm.edit_bones.new(nom)
        b.head, b.tail = (x, 0, 0), (x + 0.3, 0, 0)
        b.parent = racine
    bpy.ops.object.mode_set(mode="OBJECT")
    # poids
    groupes = [ob.vertex_groups.new(name=n) for n in noms]
    oi, ow = d["os_indices"], d["os_poids"]
    for v in range(len(P)):
        for k in range(4):
            wv = ow[4 * v + k]
            if wv > 0:
                groupes[oi[4 * v + k]].add([v], wv, "ADD")
    ob.parent = ao
    mod = ob.modifiers.new("Squelette", "ARMATURE")
    mod.object = ao
    return ob, ao, d


def exporter_fbx(chemin):
    bpy.ops.export_scene.fbx(filepath=chemin, apply_scale_options="FBX_SCALE_UNITS", add_leaf_bones=False,
                             bake_anim=False, object_types={"MESH", "ARMATURE"}, path_mode="COPY", embed_textures=False)


def rendus(dossier):
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.samples = 48
    sc.cycles.device = "CPU"
    sc.render.resolution_x, sc.render.resolution_y = 960, 540
    sc.render.film_transparent = False
    w = bpy.data.worlds.new("Monde")
    w.use_nodes = True
    w.node_tree.nodes["Background"].inputs[0].default_value = (0.35, 0.42, 0.55, 1)
    w.node_tree.nodes["Background"].inputs[1].default_value = 0.8
    sc.world = w
    sun = bpy.data.objects.new("Soleil", bpy.data.lights.new("Soleil", "SUN"))
    sun.data.energy = 3.5
    sun.rotation_euler = (math.radians(50), 0, math.radians(30))
    sc.collection.objects.link(sun)
    cam = bpy.data.objects.new("Cam", bpy.data.cameras.new("Cam"))
    sc.collection.objects.link(cam)
    sc.camera = cam
    vues = {"tete_34": ((-7.5, -6.0, 2.8), (-2.0, 0, 0.4), 38), "profil": ((4, -19, 2), (4.5, 0, 0), 50),
            "face": ((-9.5, -0.5, 1.2), (-2.0, 0, 0.5), 40)}
    for nom, (oeil, cible, lens_fov) in vues.items():
        cam.location = oeil
        dirn = Vector(cible) - Vector(oeil)
        cam.rotation_euler = dirn.to_track_quat("-Z", "Y").to_euler()
        cam.data.angle = math.radians(lens_fov)
        sc.render.filepath = os.path.join(dossier, f"dragon_{nom}.png")
        bpy.ops.render.render(write_still=True)


if __name__ == "__main__":
    scene_vide()
    construire()
    exporter_fbx(os.path.join(HERE, "dragon.fbx"))
    print("FBX ->", os.path.join(HERE, "dragon.fbx"))
    if "--rendu" in sys.argv:
        rendus(sys.argv[sys.argv.index("--rendu") + 1])
