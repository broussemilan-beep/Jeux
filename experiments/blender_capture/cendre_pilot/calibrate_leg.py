import bpy, sys, os, math, mathutils
args = {}
argv = sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else []
for a in argv:
    if a.startswith("--") and "=" in a:
        k, v = a[2:].split("=", 1)
        args[k] = v
glb = args["glb"]; out = args["out"]
bone = args.get("bone", "RightUpLeg")
rx = float(args.get("rx","0")); ry=float(args.get("ry","0")); rz=float(args.get("rz","0"))
kbone = args.get("kbone", "RightLeg")
krx = float(args.get("krx","0"))

bpy.ops.object.select_all(action="SELECT"); bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=glb)
arm = next(o for o in bpy.context.scene.objects if o.type=="ARMATURE")
bpy.context.view_layer.objects.active = arm; arm.select_set(True)
bpy.ops.object.mode_set(mode="POSE")
pb = arm.pose.bones[bone]; pb.rotation_mode="XYZ"; pb.rotation_euler=(math.radians(rx),math.radians(ry),math.radians(rz))
pb2 = arm.pose.bones[kbone]; pb2.rotation_mode="XYZ"; pb2.rotation_euler=(math.radians(krx),0,0)
bpy.ops.object.mode_set(mode="OBJECT")
bpy.context.view_layer.update()

def compute_bbox(objects, depsgraph):
    mins=[math.inf]*3; maxs=[-math.inf]*3
    for o in objects:
        if o.type!="MESH" or o.name.lower()=="icosphere": continue
        eo=o.evaluated_get(depsgraph); me=eo.to_mesh()
        for v in me.vertices:
            w=eo.matrix_world @ v.co
            for i in range(3):
                mins[i]=min(mins[i],w[i]); maxs[i]=max(maxs[i],w[i])
        eo.to_mesh_clear()
    c=mathutils.Vector(((mins[0]+maxs[0])/2,(mins[1]+maxs[1])/2,(mins[2]+maxs[2])/2))
    return c, mathutils.Vector(mins), mathutils.Vector(maxs)

scene=bpy.context.scene
cd=bpy.data.cameras.new("Cam"); cd.type="ORTHO"; cd.ortho_scale=2.2
co=bpy.data.objects.new("Cam",cd); scene.collection.objects.link(co)
yaw,pitch=math.radians(10),math.radians(18)
direction=mathutils.Vector((math.sin(yaw)*math.cos(pitch),-math.cos(yaw)*math.cos(pitch),math.sin(pitch)))
scene.camera=co
dg=bpy.context.evaluated_depsgraph_get(); dg.update()
center,mins,maxs=compute_bbox(bpy.context.scene.objects, dg)
center.z = mins.z + cd.ortho_scale*0.42
co.location = center + direction*10.0
co.rotation_euler = (center-co.location).to_track_quat("-Z","Y").to_euler()
ld=bpy.data.lights.new("L",type="SUN"); ld.energy=3.0
lo=bpy.data.objects.new("L",ld); lo.rotation_euler=(math.radians(55),0,math.radians(-30))
scene.collection.objects.link(lo)
if scene.world is None: scene.world=bpy.data.worlds.new("World")
scene.world.use_nodes=True
bg=scene.world.node_tree.nodes.get("Background")
if bg: bg.inputs[0].default_value=(0.55,0.55,0.57,1.0); bg.inputs[1].default_value=1.1
scene.render.engine="CYCLES"; scene.cycles.device="CPU"; scene.cycles.samples=16
scene.cycles.use_denoising=False; scene.view_layers[0].cycles.use_denoising=False
scene.render.film_transparent=True; scene.render.resolution_x=260; scene.render.resolution_y=260
scene.render.image_settings.file_format="PNG"; scene.render.image_settings.color_mode="RGBA"
scene.render.filepath=out
bpy.ops.render.render(write_still=True)
print("CAL_RENDERED", out)
