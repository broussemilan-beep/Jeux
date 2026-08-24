"""Quick calibration: apply a candidate rotation to RightArm/LeftArm and
render, to empirically find which local axis/sign drives the arm
forward-and-up (needed before hand-posing coup3, since this Meshy rig's
bone tail data is degenerate and axis convention isn't documented)."""
import bpy, sys, os, math, mathutils

args = {}
argv = sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else []
for a in argv:
    if a.startswith("--") and "=" in a:
        k, v = a[2:].split("=", 1)
        args[k] = v

glb = args["glb"]
out = args["out"]
rx = float(args.get("rx", "0"))
ry = float(args.get("ry", "0"))
rz = float(args.get("rz", "0"))
frx = float(args.get("frx", "0"))
fry = float(args.get("fry", "0"))
frz = float(args.get("frz", "0"))
side = args.get("side", "right")  # right | both

bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=glb)
arm = None
for obj in bpy.context.scene.objects:
    if obj.type == "ARMATURE":
        arm = obj
        break
bpy.context.view_layer.objects.active = arm
arm.select_set(True)
bpy.ops.object.mode_set(mode="POSE")

def set_bone(name, euler_deg):
    pb = arm.pose.bones.get(name)
    if pb is None:
        print("MISSING_BONE", name)
        return
    pb.rotation_mode = "XYZ"
    pb.rotation_euler = tuple(math.radians(d) for d in euler_deg)

if side in ("right", "both"):
    set_bone("RightArm", (rx, ry, rz))
    set_bone("RightForeArm", (frx, fry, frz))
if side in ("left", "both"):
    set_bone("LeftArm", (rx, ry, rz))
    set_bone("LeftForeArm", (frx, fry, frz))

bpy.ops.object.mode_set(mode="OBJECT")
bpy.context.view_layer.update()

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
    center = mathutils.Vector(((mins[0]+maxs[0])/2, (mins[1]+maxs[1])/2, (mins[2]+maxs[2])/2))
    return center, mathutils.Vector(mins), mathutils.Vector(maxs)

scene = bpy.context.scene
cam_data = bpy.data.cameras.new("Cam")
cam_data.type = "ORTHO"
cam_data.ortho_scale = 2.2
cam_obj = bpy.data.objects.new("Cam", cam_data)
scene.collection.objects.link(cam_obj)
yaw, pitch = math.radians(10), math.radians(18)
direction = mathutils.Vector((math.sin(yaw)*math.cos(pitch), -math.cos(yaw)*math.cos(pitch), math.sin(pitch)))
scene.camera = cam_obj
depsgraph = bpy.context.evaluated_depsgraph_get()
depsgraph.update()
center, mins, maxs = compute_bbox(bpy.context.scene.objects, depsgraph)
center.z = mins.z + cam_data.ortho_scale * 0.42
cam_obj.location = center + direction * 10.0
cam_obj.rotation_euler = (center - cam_obj.location).to_track_quat("-Z", "Y").to_euler()

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
scene.cycles.samples = 16
scene.cycles.use_denoising = False
scene.view_layers[0].cycles.use_denoising = False
scene.render.film_transparent = True
scene.render.resolution_x = 260
scene.render.resolution_y = 260
scene.render.image_settings.file_format = "PNG"
scene.render.image_settings.color_mode = "RGBA"
scene.render.filepath = out
bpy.ops.render.render(write_still=True)
print("CAL_RENDERED", out)
