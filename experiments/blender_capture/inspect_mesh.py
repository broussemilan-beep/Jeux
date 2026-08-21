"""Inspecte le maillage evalue : trouve les sommets aux extremes de
chaque axe (utile pour placer une armature a la main sans deviner a
l'oeil sur un rendu projete)."""

import bpy
import sys
import math


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

bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=glb_path)

depsgraph = bpy.context.evaluated_depsgraph_get()
depsgraph.update()

all_verts = []
for obj in bpy.context.scene.objects:
    if obj.type != "MESH":
        continue
    eval_obj = obj.evaluated_get(depsgraph)
    mesh = eval_obj.to_mesh()
    for v in mesh.vertices:
        world = eval_obj.matrix_world @ v.co
        all_verts.append((world.x, world.y, world.z))
    eval_obj.to_mesh_clear()

print("TOTAL_VERTS", len(all_verts))

for axis_i, axis_name in enumerate("xyz"):
    vmin = min(all_verts, key=lambda p: p[axis_i])
    vmax = max(all_verts, key=lambda p: p[axis_i])
    print(f"AXIS_{axis_name}_MIN", vmin)
    print(f"AXIS_{axis_name}_MAX", vmax)

# Slice profile along Y (front-back) : pour chaque tranche de 10%,
# largeur (X) et hauteur (Z) moyennes des sommets dans la tranche.
ys = [p[1] for p in all_verts]
y0, y1 = min(ys), max(ys)
print("Y_RANGE", y0, y1)
n_slices = 12
for i in range(n_slices):
    lo = y0 + (y1 - y0) * i / n_slices
    hi = y0 + (y1 - y0) * (i + 1) / n_slices
    bucket = [p for p in all_verts if lo <= p[1] < hi]
    if not bucket:
        print(f"SLICE {i} y=[{lo:.2f},{hi:.2f}] EMPTY")
        continue
    xs = [p[0] for p in bucket]
    zs = [p[2] for p in bucket]
    print(f"SLICE {i} y=[{lo:.2f},{hi:.2f}] n={len(bucket)} "
          f"x=[{min(xs):.2f},{max(xs):.2f}] z=[{min(zs):.2f},{max(zs):.2f}] "
          f"z_mean={sum(zs)/len(zs):.2f}")
