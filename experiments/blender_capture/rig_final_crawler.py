"""Phase 1.1 - armature definitive Crawler : nettoyage mesh (merge-
doubles systematique, cause du blocage Meshy deja resolue) + armature
13 bones + parentage auto, puis 2 captures a l'echelle commune deja
etablie (cam_size=2.6, target_z=1.0878) : idle (bind pose, deja fidele
a la reference) et attaque (pose tenue, quelques os tournes a la main -
pas d'animation, juste une pose comme demande par le mandat)."""

import bpy
import sys
import os
import math
import mathutils

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from normal_pass import render_normal_pass


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
out_glb = args.get("out_glb", "/tmp/crawler_final.glb")
out_idle_raw = args.get("out_idle_raw")
out_attack_raw = args.get("out_attack_raw")
out_idle_normal = args.get("out_idle_normal")
out_attack_normal = args.get("out_attack_normal")
cam_size = float(args.get("cam_size", "2.6"))
target_z = float(args.get("target_z", "1.0878"))

bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=glb_path)

mesh_obj = None
for obj in bpy.context.scene.objects:
    if obj.type == "MESH":
        mesh_obj = obj
        break
assert mesh_obj is not None

bpy.context.view_layer.objects.active = mesh_obj
bpy.ops.object.mode_set(mode="EDIT")
bpy.ops.mesh.select_all(action="SELECT")
bpy.ops.mesh.remove_doubles(threshold=0.0001)
bpy.ops.mesh.normals_make_consistent(inside=False)
bpy.ops.object.mode_set(mode="OBJECT")

arm_data = bpy.data.armatures.new("CrawlerArmature")
arm_obj = bpy.data.objects.new("CrawlerArmature", arm_data)
bpy.context.scene.collection.objects.link(arm_obj)
bpy.context.view_layer.objects.active = arm_obj
bpy.ops.object.mode_set(mode="EDIT")
eb = arm_data.edit_bones


def add_bone(name, head, tail, parent=None):
    b = eb.new(name)
    b.head = mathutils.Vector(head)
    b.tail = mathutils.Vector(tail)
    if parent is not None:
        b.parent = parent
        b.use_connect = False
    return b


pelvis = add_bone("pelvis", (0, 0.55, 0.40), (0, 0.15, 0.55))
chest = add_bone("chest", (0, 0.15, 0.55), (0, -0.45, 0.55), parent=pelvis)
neck = add_bone("neck", (0, -0.45, 0.55), (0, -0.85, 0.40), parent=chest)
head = add_bone("head", (0, -0.85, 0.40), (0, -1.29, 0.26), parent=neck)
tail = add_bone("tail", (0, 0.55, 0.40), (0, 1.29, 0.11), parent=pelvis)
for side, sx in (("L", -1), ("R", 1)):
    hip = add_bone(f"front_{side}_upper", (sx * 0.30, -0.55, 0.50), (sx * 0.45, -0.80, 0.25), parent=chest)
    add_bone(f"front_{side}_lower", (sx * 0.45, -0.80, 0.25), (sx * 0.55, -1.00, 0.0), parent=hip)
for side, sx in (("L", -1), ("R", 1)):
    hip = add_bone(f"back_{side}_upper", (sx * 0.25, 0.55, 0.45), (sx * 0.35, 0.75, 0.20), parent=pelvis)
    add_bone(f"back_{side}_lower", (sx * 0.35, 0.75, 0.20), (sx * 0.35, 0.85, 0.0), parent=hip)

bpy.ops.object.mode_set(mode="OBJECT")

bpy.ops.object.select_all(action="DESELECT")
mesh_obj.select_set(True)
arm_obj.select_set(True)
bpy.context.view_layer.objects.active = arm_obj
bpy.ops.object.parent_set(type="ARMATURE_AUTO")


def setup_render(out_path, res=512, samples=32):
    scene = bpy.context.scene
    for cam in [o for o in scene.objects if o.type == "CAMERA"]:
        bpy.data.objects.remove(cam, do_unlink=True)
    for light in [o for o in scene.objects if o.type == "LIGHT"]:
        bpy.data.objects.remove(light, do_unlink=True)

    cam_data = bpy.data.cameras.new("Cam")
    cam_data.type = "ORTHO"
    cam_data.ortho_scale = cam_size
    cam_obj = bpy.data.objects.new("Cam", cam_data)
    scene.collection.objects.link(cam_obj)
    yaw, pitch = math.radians(35), math.radians(18)
    direction = mathutils.Vector((math.sin(yaw) * math.cos(pitch), -math.cos(yaw) * math.cos(pitch), math.sin(pitch)))
    center = mathutils.Vector((0, 0, target_z))
    cam_obj.location = center + direction * 10.0
    cam_obj.rotation_euler = (center - cam_obj.location).to_track_quat("-Z", "Y").to_euler()
    scene.camera = cam_obj

    light_data = bpy.data.lights.new("L", type="SUN")
    light_data.energy = 3.0
    light_obj = bpy.data.objects.new("L", light_data)
    light_obj.rotation_euler = (math.radians(55), 0.0, math.radians(-30))
    scene.collection.objects.link(light_obj)

    if scene.world is None:
        scene.world = bpy.data.worlds.new("World")
    scene.world.use_nodes = True
    bg = scene.world.node_tree.nodes.get("Background")
    if bg is not None:
        bg.inputs[0].default_value = (0.55, 0.55, 0.57, 1.0)
        bg.inputs[1].default_value = 1.1

    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = samples
    scene.cycles.use_denoising = False
    scene.view_layers[0].cycles.use_denoising = False
    scene.render.film_transparent = True
    scene.render.resolution_x = res
    scene.render.resolution_y = res
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.filepath = out_path
    bpy.ops.render.render(write_still=True)


# --- Idle : bind pose telle quelle, deja fidele a la reference --------
if out_idle_raw:
    setup_render(out_idle_raw)
    print("IDLE_RENDERED", out_idle_raw)
    if out_idle_normal:
        render_normal_pass(bpy.context.scene, out_idle_normal)
        print("IDLE_NORMAL_RENDERED", out_idle_normal)

# --- Attaque : pose tenue (pas d'animation), morsure basse + pattes ----
# avant poussees en avant - lunge de predateur.
bpy.ops.object.select_all(action="DESELECT")
bpy.context.view_layer.objects.active = arm_obj
arm_obj.select_set(True)
bpy.ops.object.mode_set(mode="POSE")

pb_neck = arm_obj.pose.bones["neck"]
pb_neck.rotation_mode = "XYZ"
pb_neck.rotation_euler = (math.radians(-35), 0, 0)

pb_head = arm_obj.pose.bones["head"]
pb_head.rotation_mode = "XYZ"
pb_head.rotation_euler = (math.radians(-25), 0, 0)

for side in ("L", "R"):
    pb_u = arm_obj.pose.bones[f"front_{side}_upper"]
    pb_u.rotation_mode = "XYZ"
    pb_u.rotation_euler = (math.radians(30), 0, 0)
    pb_l = arm_obj.pose.bones[f"front_{side}_lower"]
    pb_l.rotation_mode = "XYZ"
    pb_l.rotation_euler = (math.radians(-15), 0, 0)

pb_pelvis = arm_obj.pose.bones["pelvis"]
pb_pelvis.rotation_mode = "XYZ"
pb_pelvis.rotation_euler = (math.radians(-10), 0, 0)

bpy.ops.object.mode_set(mode="OBJECT")

if out_attack_raw:
    setup_render(out_attack_raw)
    print("ATTACK_RENDERED", out_attack_raw)
    if out_attack_normal:
        render_normal_pass(bpy.context.scene, out_attack_normal)
        print("ATTACK_NORMAL_RENDERED", out_attack_normal)

# --- Retour a la bind pose avant export (le rig livre = repos) ---------
bpy.ops.object.mode_set(mode="POSE")
for b in arm_obj.pose.bones:
    b.rotation_euler = (0, 0, 0)
bpy.ops.object.mode_set(mode="OBJECT")

bpy.ops.object.select_all(action="SELECT")
try:
    bpy.ops.export_scene.gltf(filepath=out_glb, use_selection=True, export_animations=False)
    print("GLB_EXPORTED", out_glb)
except Exception as e:
    print("GLB_EXPORT_FAILED", repr(e))
