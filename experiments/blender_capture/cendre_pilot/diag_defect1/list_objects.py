import bpy, sys
glb = sys.argv[sys.argv.index("--")+1]
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=glb)
for obj in bpy.context.scene.objects:
    print("OBJ", obj.name, obj.type)
    if obj.type == "MESH":
        print("MESH_INFO", obj.name, "verts=", len(obj.data.vertices), "vgroups=", [vg.name for vg in obj.vertex_groups])
