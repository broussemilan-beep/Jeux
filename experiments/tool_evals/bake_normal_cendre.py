"""T.1.2 — Test isole de bake de normal map (vue camera fixe, pour
sprite 2D) sur Cendre idle. Rend en parallele : (1) beauty (couleur,
meme convention que capture_pose.py), (2) passe Normal (Cycles, espace
camera - directement exploitable comme normal map 2D puisque le sprite
est une image fixe sous un seul angle, pas un mapping tangent-espace
UV classique 3D). Verifie ensuite manuellement (script Godot separe)
que la convention Y+ (haut) correspond a ce qu'attend Light2D.
"""

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
out_beauty = args.get("out_beauty", "/tmp/cendre_beauty.png")
out_normal = args.get("out_normal", "/tmp/cendre_normal.png")
res = int(args.get("res", "512"))

bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=glb_path)

scene = bpy.context.scene

# Sphere de reference (a cote du personnage) pour calibrer sans ambiguite
# la convention Y du normal pass Blender brut, AVANT tout remap pour
# Godot : son sommet (pole nord, normal =(0,0,1) LOCAL mais tourne vers
# le haut de l'image une fois projete par la camera) sert de repere
# connu, comme le hemisphere_normal.png synthetique deja verifie cote
# Godot (G haut = haut de l'image = lumiere du dessus).
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.35, location=(0.9, 0, 1.2), segments=32, ring_count=16)
ref_sphere = bpy.context.object
ref_sphere.name = "RefSphere"

cam_data = bpy.data.cameras.new("Cam")
cam_data.type = "ORTHO"
cam_data.ortho_scale = 2.2
cam_obj = bpy.data.objects.new("Cam", cam_data)
scene.collection.objects.link(cam_obj)
yaw, pitch = math.radians(20), math.radians(12)
direction = mathutils.Vector((math.sin(yaw) * math.cos(pitch), -math.cos(yaw) * math.cos(pitch), math.sin(pitch)))
center = mathutils.Vector((0, 0, 0.9))
cam_obj.location = center + direction * 10.0
cam_obj.rotation_euler = (center - cam_obj.location).to_track_quat("-Z", "Y").to_euler()
scene.camera = cam_obj

light_data = bpy.data.lights.new("KeyLight", type="SUN")
light_data.energy = 3.0
light_obj = bpy.data.objects.new("KeyLight", light_data)
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
scene.cycles.samples = 32
scene.cycles.use_denoising = False
scene.view_layers[0].cycles.use_denoising = False
scene.render.film_transparent = True
scene.render.resolution_x = res
scene.render.resolution_y = res
scene.render.image_settings.file_format = "PNG"
scene.render.image_settings.color_mode = "RGBA"

# --- Passe beauty (couleur) ---------------------------------------------
scene.render.filepath = out_beauty
bpy.ops.render.render(write_still=True)
print("BEAUTY_SAVED", out_beauty)

# --- Passe Normal (espace camera, via compositor) -----------------------
# Remap [-1,1] -> [0,1] directement dans le compositor (mult 0.5 + add 0.5)
# pour sortir un PNG 8-bit standard, sans dependance a un lecteur EXR.
view_layer = scene.view_layers[0]
view_layer.use_pass_normal = True
scene.use_nodes = True
tree = scene.node_tree
for n in list(tree.nodes):
    tree.nodes.remove(n)
rl = tree.nodes.new("CompositorNodeRLayers")
mul = tree.nodes.new("CompositorNodeMixRGB")
mul.blend_type = "MULTIPLY"
mul.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
add = tree.nodes.new("CompositorNodeMixRGB")
add.blend_type = "ADD"
add.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
alpha = tree.nodes.new("CompositorNodeSetAlpha")
comp = tree.nodes.new("CompositorNodeComposite")
tree.links.new(rl.outputs["Normal"], mul.inputs[1])
tree.links.new(mul.outputs["Image"], add.inputs[1])
tree.links.new(add.outputs["Image"], alpha.inputs["Image"])
tree.links.new(rl.outputs["Alpha"], alpha.inputs["Alpha"])
tree.links.new(alpha.outputs["Image"], comp.inputs["Image"])

scene.render.filepath = out_normal
scene.render.image_settings.file_format = "PNG"
scene.render.image_settings.color_mode = "RGBA"
scene.render.image_settings.color_management = "OVERRIDE"
scene.view_settings.view_transform = "Standard"
scene.frame_set(1)
bpy.ops.render.render(write_still=True)
print("NORMAL_PASS_SAVED", out_normal)
