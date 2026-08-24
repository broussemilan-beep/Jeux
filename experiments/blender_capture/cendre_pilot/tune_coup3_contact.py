"""Rapid iteration harness (diagnostic only, not part of the final
pilot deliverable): renders the coup3 anticipation-tail (frac 0.72,
0.85), several CANDIDATE contact-key parameter sets, and the
recovery-head (frac 0.75) from the SAME frame-49 base pose as
render_combo_cendre.py, so several overshoot multipliers can be
compared by pixel diff in one Blender run instead of a full
combo re-render per candidate."""
import bpy
import sys
import os
import math
import mathutils

args = {}
argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
for a in argv:
    if a.startswith("--") and "=" in a:
        k, v = a[2:].split("=", 1)
        args[k] = v

glb_path = args["glb"]
out_dir = args["out_dir"]
res = int(args.get("res", "320"))
samples = int(args.get("samples", "16"))
os.makedirs(out_dir, exist_ok=True)

bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=glb_path)

armature = None
for obj in bpy.context.scene.objects:
    if obj.type == "ARMATURE":
        armature = obj
        break
assert armature is not None
action = bpy.data.actions[0]
if armature.animation_data is None:
    armature.animation_data_create()
armature.animation_data.action = action

IGNORE_MESH_NAMES = {"icosphere"}


def compute_bbox(objects, depsgraph):
    mins = [math.inf, math.inf, math.inf]
    maxs = [-math.inf, -math.inf, -math.inf]
    for obj in objects:
        if obj.type != "MESH" or obj.name.lower() in IGNORE_MESH_NAMES:
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


scene = bpy.context.scene
cam_data = bpy.data.cameras.new("Cam")
cam_data.type = "ORTHO"
cam_data.ortho_scale = 2.2
cam_obj = bpy.data.objects.new("Cam", cam_data)
scene.collection.objects.link(cam_obj)
yaw, pitch = math.radians(10), math.radians(18)
direction = mathutils.Vector((math.sin(yaw) * math.cos(pitch), -math.cos(yaw) * math.cos(pitch), math.sin(pitch)))
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

scene.frame_set(1)
bpy.context.view_layer.update()
depsgraph = bpy.context.evaluated_depsgraph_get()
depsgraph.update()
_, mins0, maxs0 = compute_bbox(bpy.context.scene.objects, depsgraph)
target_z = mins0.z + cam_data.ortho_scale * 0.42


def render_current_pose(tag):
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    dg.update()
    center, mins, maxs = compute_bbox(bpy.context.scene.objects, dg)
    center.z = target_z
    cam_obj.location = center + direction * 10.0
    cam_obj.rotation_euler = (center - cam_obj.location).to_track_quat("-Z", "Y").to_euler()
    out_path = os.path.join(out_dir, f"{tag}.png")
    scene.render.filepath = out_path
    bpy.ops.render.render(write_still=True)
    print("TUNE_RENDERED", tag, out_path)


scene.frame_set(49)
bpy.context.view_layer.update()
armature.animation_data.action = None

bpy.context.view_layer.objects.active = armature
armature.select_set(True)
bpy.ops.object.mode_set(mode="POSE")


def set_bone_euler(name, euler_deg):
    pb = armature.pose.bones[name]
    pb.rotation_mode = "XYZ"
    pb.rotation_euler = tuple(math.radians(d) for d in euler_deg)


PEAK_RX, PEAK_FRX, PEAK_SPINE_RZ = -90.0, -60.0, -12.0


def pose_and_render(tag, arm_frac, forearm_frac, spine_frac, right_arm_rx=None, right_forearm_rx=None):
    set_bone_euler("LeftArm", (PEAK_RX * arm_frac, 0, 0))
    set_bone_euler("LeftForeArm", (PEAK_FRX * forearm_frac, 0, 0))
    set_bone_euler("Spine", (0, 0, PEAK_SPINE_RZ * spine_frac))
    if right_arm_rx is not None:
        set_bone_euler("RightArm", (right_arm_rx, 0, 0))
    if right_forearm_rx is not None:
        set_bone_euler("RightForeArm", (right_forearm_rx, 0, 0))
    bpy.ops.object.mode_set(mode="OBJECT")
    render_current_pose(tag)
    bpy.context.view_layer.objects.active = armature
    armature.select_set(True)
    bpy.ops.object.mode_set(mode="POSE")


# Contexte (queue d'anticipation + tete de recuperation, inchangees)
pose_and_render("ctx_antic_072", 0.72, 0.72, 0.72)
pose_and_render("ctx_antic_085", 0.85, 0.85, 0.85)
pose_and_render("ctx_recovery_075", 0.75, 0.75, 0.75)

# Candidats contact (a comparer par diff pixel vs ctx_antic_085 et
# vs ctx_recovery_075)
CANDIDATES = {
    "cand_a_mild": (1.12, 1.15, 1.35, None, None),
    "cand_b_strong": (1.35, 1.4, 1.8, None, None),
    "cand_c_verystrong": (1.6, 1.7, 2.2, None, None),
    "cand_d_release_for_b": (1.05, 1.05, 1.3, None, None),
    "cand_e_rightarm_peak": (1.35, 1.4, 1.8, -35.0, -25.0),
    "cand_f_rightarm_release": (1.05, 1.05, 1.3, -15.0, -10.0),
    "cand_g_rightarm_pulled_back": (1.35, 1.4, 1.8, 20.0, 15.0),
    "cand_h_release_for_g": (1.05, 1.05, 1.3, 8.0, 6.0),
}
for tag, (a, f, s, ra, rf) in CANDIDATES.items():
    pose_and_render(tag, a, f, s, ra, rf)

bpy.ops.object.mode_set(mode="OBJECT")
print("TUNE_DONE")
