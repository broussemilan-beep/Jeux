import bpy, sys
argv = sys.argv[sys.argv.index("--")+1:]
glb = argv[0]
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=glb)
arm = None
for obj in bpy.context.scene.objects:
    if obj.type == "ARMATURE":
        arm = obj
        break
print("ARMATURE", arm.name if arm else None)
if arm:
    for b in arm.data.bones:
        parent = b.parent.name if b.parent else None
        print("BONE", b.name, "parent=", parent, "head=", tuple(round(x,3) for x in b.head_local), "tail=", tuple(round(x,3) for x in b.tail_local))
