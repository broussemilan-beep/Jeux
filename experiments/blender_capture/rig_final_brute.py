"""Phase 1.1 - armature definitive Brute : meme methode que Crawler,
capture idle (bind pose) + attaque (bras droit leve pour un smash
aerien, pose tenue) a l'echelle commune (cam_size=2.6, target_z=0.892)."""

import bpy
import sys
import os
import math
import mathutils

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from normal_pass import render_normal_pass


def compute_bbox(objects, depsgraph):
    mins = [math.inf, math.inf, math.inf]
    maxs = [-math.inf, -math.inf, -math.inf]
    for obj in objects:
        if obj.type != "MESH":
            continue
        eval_obj = obj.evaluated_get(depsgraph)
        mesh = eval_obj.to_mesh()
        for vert in mesh.vertices:
            world = eval_obj.matrix_world @ vert.co
            for i in range(3):
                mins[i] = min(mins[i], world[i])
                maxs[i] = max(maxs[i], world[i])
        eval_obj.to_mesh_clear()
    center = mathutils.Vector(((mins[0] + maxs[0]) / 2, (mins[1] + maxs[1]) / 2, (mins[2] + maxs[2]) / 2))
    return center, mathutils.Vector(mins), mathutils.Vector(maxs)


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
out_glb = args.get("out_glb", "/tmp/brute_final.glb")
out_idle_raw = args.get("out_idle_raw")
out_attack_raw = args.get("out_attack_raw")
out_idle_normal = args.get("out_idle_normal")
out_attack_normal = args.get("out_attack_normal")
cam_size = float(args.get("cam_size", "2.6"))
target_z = float(args.get("target_z", "0.892"))

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

arm_data = bpy.data.armatures.new("BruteArmature")
arm_obj = bpy.data.objects.new("BruteArmature", arm_data)
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


pelvis = add_bone("pelvis", (0, 0.7, 0.85), (0, 0.3, 1.3))
chest = add_bone("chest", (0, 0.3, 1.3), (0, -0.1, 1.85), parent=pelvis)
neck = add_bone("neck", (0, -0.1, 1.85), (0, -0.6, 1.75), parent=chest)
head = add_bone("head", (0, -0.6, 1.75), (0, -1.1, 1.3), parent=neck)
for side, sx in (("L", -1), ("R", 1)):
    shoulder = add_bone(f"arm_{side}_upper", (sx * 0.6, -0.3, 1.7), (sx * 1.0, -0.5, 1.0), parent=chest)
    add_bone(f"arm_{side}_lower", (sx * 1.0, -0.5, 1.0), (sx * 1.35, -0.6, 0.45), parent=shoulder)
for side, sx in (("L", -1), ("R", 1)):
    hip = add_bone(f"leg_{side}_upper", (sx * 0.4, 0.5, 0.9), (sx * 0.5, 0.7, 0.5), parent=pelvis)
    add_bone(f"leg_{side}_lower", (sx * 0.5, 0.7, 0.5), (sx * 0.45, 0.85, 0.0), parent=hip)

bpy.ops.object.mode_set(mode="OBJECT")

bpy.ops.object.select_all(action="DESELECT")
mesh_obj.select_set(True)
arm_obj.select_set(True)
bpy.context.view_layer.objects.active = arm_obj
bpy.ops.object.parent_set(type="ARMATURE_AUTO")


def setup_render(out_path, fixed_target_z, res=512, samples=32):
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
    depsgraph = bpy.context.evaluated_depsgraph_get()
    depsgraph.update()
    center, mins, maxs = compute_bbox(bpy.context.scene.objects, depsgraph)
    print("BBOX_CENTER_XY", center.x, center.y, "mins", tuple(mins), "maxs", tuple(maxs), "fixed_target_z", fixed_target_z)
    center.z = fixed_target_z
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


bottom_margin_frac = 0.08
depsgraph_bind = bpy.context.evaluated_depsgraph_get()
depsgraph_bind.update()
_, mins_bind, maxs_bind = compute_bbox(bpy.context.scene.objects, depsgraph_bind)
computed_target_z = mins_bind.z + cam_size * (0.5 - bottom_margin_frac)
print("BIND_MINS_Z", mins_bind.z, "BIND_MAXS_Z", maxs_bind.z, "computed_target_z", computed_target_z,
      "cli_target_z", target_z)
target_z = computed_target_z

if out_idle_raw:
    setup_render(out_idle_raw, target_z)
    print("IDLE_RENDERED", out_idle_raw)
    if out_idle_normal:
        render_normal_pass(bpy.context.scene, out_idle_normal)
        print("IDLE_NORMAL_RENDERED", out_idle_normal)

# --- Attaque : bras droit leve (smash aerien), bras gauche stabilise ---
bpy.ops.object.select_all(action="DESELECT")
bpy.context.view_layer.objects.active = arm_obj
arm_obj.select_set(True)
bpy.ops.object.mode_set(mode="POSE")

pb_ru = arm_obj.pose.bones["arm_R_upper"]
pb_ru.rotation_mode = "XYZ"
pb_ru.rotation_euler = (math.radians(-100), math.radians(15), math.radians(-15))

pb_rl = arm_obj.pose.bones["arm_R_lower"]
pb_rl.rotation_mode = "XYZ"
pb_rl.rotation_euler = (math.radians(50), 0, 0)

pb_lu = arm_obj.pose.bones["arm_L_upper"]
pb_lu.rotation_mode = "XYZ"
pb_lu.rotation_euler = (math.radians(10), 0, math.radians(10))

pb_chest = arm_obj.pose.bones["chest"]
pb_chest.rotation_mode = "XYZ"
pb_chest.rotation_euler = (math.radians(-15), 0, math.radians(8))

bpy.ops.object.mode_set(mode="OBJECT")

if out_attack_raw:
    setup_render(out_attack_raw, target_z)
    print("ATTACK_RENDERED", out_attack_raw)
    if out_attack_normal:
        render_normal_pass(bpy.context.scene, out_attack_normal)
        print("ATTACK_NORMAL_RENDERED", out_attack_normal)

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
