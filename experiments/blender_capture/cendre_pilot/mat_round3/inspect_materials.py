import bpy
import sys

argv = sys.argv
argv = argv[argv.index("--") + 1:] if "--" in argv else []
glb_path = argv[0]

bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=glb_path)

for mat in bpy.data.materials:
    print("=== MATERIAL", mat.name, "use_nodes=", mat.use_nodes)
    if not mat.use_nodes:
        continue
    for node in mat.node_tree.nodes:
        print("  NODE", node.type, node.name)
        if node.type == "TEX_IMAGE":
            print("    interpolation=", node.interpolation, "extension=", node.extension, "projection=", node.projection)
        if node.type == "BSDF_PRINCIPLED":
            for inp in node.inputs:
                try:
                    val = inp.default_value
                except Exception:
                    val = "?"
                links = len(inp.links)
                print(f"    INPUT {inp.name!r} default={val} n_links={links}")
                if links:
                    print("      <-", inp.links[0].from_node.name, inp.links[0].from_node.type)

for img in bpy.data.images:
    print("IMAGE", img.name, img.size[:], img.filepath)
