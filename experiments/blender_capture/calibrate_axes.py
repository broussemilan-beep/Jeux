"""Depose des marqueurs colores a des coordonnees candidates pour
determiner empiriquement l'orientation reelle du maillage importe
(quel signe de Y est la tete, quel signe de X est gauche/droite) avant
de placer une armature a la main - plus fiable que d'interpreter un
rendu en calculant a la main la projection camera."""

import bpy
import sys
import math
import mathutils


def parse_args():
    argv = sys.argv
    argv = argv[argv.index("--") + 1:] if "--" in argv else []
    result = {}
    for arg in argv:
        if arg.startswith("--") and "=" in arg:
            k, v = arg[2:].split("=", 1)
            result[k] = v
    return result


args = parse_args()
glb_path = args["glb"]
out_path = args.get("out", "/tmp/calibrate.png")

bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=glb_path)

markers = [
    ("head_guess_negY", (0, -1.2, 0.3), (1, 0, 0, 1)),
    ("tail_guess_posY", (0, 1.2, 0.3), (0, 0, 1, 1)),
    ("right_guess_posX", (0.5, 0, 0.7), (0, 1, 0, 1)),
    ("left_guess_negX", (-0.5, 0, 0.7), (1, 0, 1, 1)),
]
for name, loc, color in markers:
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.08, location=loc)
    obj = bpy.context.object
    obj.name = name
    mat = bpy.data.materials.new(name + "_mat")
    mat.diffuse_color = color
    mat.use_nodes = True
    mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = color
    mat.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"].default_value = 2.0
    mat.node_tree.nodes["Principled BSDF"].inputs["Emission Color"].default_value = color
    obj.data.materials.append(mat)

scene = bpy.context.scene
cam_data = bpy.data.cameras.new("CalibCam")
cam_data.type = "ORTHO"
cam_data.ortho_scale = 3.5
cam_obj = bpy.data.objects.new("CalibCam", cam_data)
scene.collection.objects.link(cam_obj)

yaw = math.radians(35)
pitch = math.radians(20)
direction = mathutils.Vector((math.sin(yaw) * math.cos(pitch), -math.cos(yaw) * math.cos(pitch), math.sin(pitch)))
center = mathutils.Vector((0, 0, 0.45))
cam_obj.location = center + direction * 10.0
cam_obj.rotation_euler = (center - cam_obj.location).to_track_quat("-Z", "Y").to_euler()
scene.camera = cam_obj

light_data = bpy.data.lights.new("L", type="SUN")
light_data.energy = 3.0
light_obj = bpy.data.objects.new("L", light_data)
light_obj.rotation_euler = (math.radians(55), 0.0, math.radians(-30))
scene.collection.objects.link(light_obj)

scene.render.engine = "CYCLES"
scene.cycles.device = "CPU"
scene.cycles.samples = 16
scene.cycles.use_denoising = False
scene.view_layers[0].cycles.use_denoising = False
scene.render.film_transparent = True
scene.render.resolution_x = 512
scene.render.resolution_y = 512
scene.render.image_settings.file_format = "PNG"
scene.render.filepath = out_path
bpy.ops.render.render(write_still=True)
print("CALIBRATE_SAVED", out_path)
