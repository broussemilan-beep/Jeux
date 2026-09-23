"""
Pilotage headless du rig "R6 IK + FK Blender Rig V2.22" (Aeresei) par bpy.

Le rig n'est PAS versionne ici (pas de licence de redistribution) : on le
reference par son SHA-256, publie aussi par dillydog580/animate-roblox-
characters. Verifie a chaque ouverture ; ouvert scripts desactives (les 5
scripts embarques ne font que de l'UI : selecteur de rig, panneau de
reglages, accessoires, texture, sync d'armes -- audites, voir RIG_V222.md).
Les drivers du rig sont de type AVERAGE avec une courbe de correspondance
0->0 / 1->1 (80 sur 82 ; les 2 autres sont des expressions simples),
evalues sans Python : IK/FK, Grab, Torso Influence, Track Object fonctionnent donc
sans les scripts.

Usage (python3 avec le paquet bpy) :
    from animator_brain import v222_rig as V
    V.open_rig("/chemin/Blender_R6.blend")
    V.set_controls({"LowerTorso-FK": {"location": (0, -0.6, 0)}})
    V.review_render("/tmp/pose")      # -> pose_front.png, pose_side.png
"""
import hashlib
import math

BLEND_SHA256 = "ff75c44b572d32328b62095141c6ce6255c4e9b772ee63d46d92280de1edcdc8"
RBXM_SHA256 = "a85e1ce13b6cb15c2094be8afcf6bd66ab2017e10f42be6ecb95faa20dd93444"

PRIMARY = "__PrimaryArmature"   # controles de l'animateur
INTERNAL = "InternalArmature"   # vraies parts Roblox (Motor6D), menees par les controles
PARTS = ("HumanoidRootPart", "Torso", "Head", "Left Arm", "Right Arm", "Left Leg", "Right Leg")

# Conventions MESUREES sur le rig (probe du 2026-09-23, voir RIG_V222.md) :
# avant du personnage = +Y Blender ; 1 unite Blender = 1 stud ; semelles a z=0 ;
# scene a 60 fps.
FORWARD = (0.0, 1.0, 0.0)


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def open_rig(path, detach_rest_action=True):
    """Ouvre le rig apres verification du hash, scripts desactives. Le
    fichier embarque une action 'ArmatureAction' (pose de repos cle a la
    frame 0 sur tous les controles) qui ECRASE toute pose manuelle au rendu :
    on la detache par defaut."""
    import bpy
    got = sha256(path)
    if got != BLEND_SHA256:
        raise RuntimeError(f"hash du rig inattendu : {got}")
    bpy.ops.wm.open_mainfile(filepath=path, load_ui=False, use_scripts=False)
    arm = bpy.data.objects[PRIMARY]
    if detach_rest_action and arm.animation_data:
        arm.animation_data.action = None
    return arm


def set_controls(controls):
    """controls = {bone: {"location": (x,y,z), "rotation_euler": (deg,deg,deg)
    ou "rotation_quaternion": (w,x,y,z)}} -- en espace local du controle."""
    import bpy
    from mathutils import Euler
    pb = bpy.data.objects[PRIMARY].pose.bones
    for name, ch in controls.items():
        b = pb[name]
        if "location" in ch:
            b.location = ch["location"]
        if "rotation_euler" in ch:
            b.rotation_mode = "QUATERNION"
            b.rotation_quaternion = Euler([math.radians(a) for a in ch["rotation_euler"]], "XYZ").to_quaternion()
        if "rotation_quaternion" in ch:
            b.rotation_mode = "QUATERNION"
            b.rotation_quaternion = ch["rotation_quaternion"]
    bpy.context.view_layer.update()


def set_setting(part, key, value):
    """Reglages du rig (objets de RigSettingsHolder) : ex. set_setting("Right
    Arm", "IK/FK", 1.0), ("Right Arm", "Grab", 1.0), ("Head", "Track Object",
    1.0), ("Left Leg", "Torso Influence", 0.0)."""
    import bpy
    holder = bpy.data.objects[part]
    holder[key] = value
    # un changement de propriete custom ne marque pas le depsgraph : sans
    # ce tag, les drivers (type AVERAGE + courbe 0->0 / 1->1) ne sont pas
    # reevalues et l'influence des contraintes reste a l'ancienne valeur.
    holder.update_tag()
    bpy.data.objects[PRIMARY].update_tag()
    bpy.context.view_layer.update()


def part_matrices():
    """Matrices monde des 7 parts Roblox (InternalArmature)."""
    import bpy
    bpy.context.view_layer.update()
    arm = bpy.data.objects[INTERNAL]
    return {p: arm.matrix_world @ arm.pose.bones[p].matrix for p in PARTS}


def visible_body_meshes():
    import bpy
    return [o for o in bpy.data.objects if o.type == "MESH" and not o.hide_render
            and not o.name.startswith("_Shape") and not o.hide_get()]


def lowest_point():
    """z minimal des maillages visibles du corps (semelles) -- pour verifier
    un appui ou une penetration du sol."""
    import bpy
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    zmin = float("inf")
    for o in visible_body_meshes():
        e = o.evaluated_get(dg)
        for v in e.data.vertices:
            zmin = min(zmin, (e.matrix_world @ v.co).z)
    return zmin


def review_render(out_prefix, views=("front", "side"), res=520, samples=16, center_z=2.3, dist=12.0,
                  ortho=6.5):
    """Rendu de revue (Cycles CPU, aucun GPU/ecran) : face et/ou profil,
    orthographique, faces etiquetees F/B/L/R/U du rig visibles. Retourne
    les chemins ecrits."""
    import bpy
    from mathutils import Vector
    S = bpy.context.scene
    S.render.engine = "CYCLES"
    S.cycles.device = "CPU"
    S.cycles.samples = samples
    S.render.resolution_x = S.render.resolution_y = res
    S.render.film_transparent = False
    if S.world is None:
        S.world = bpy.data.worlds.new("ReviewWorld")
    S.world.use_nodes = True
    bg = S.world.node_tree.nodes["Background"]
    bg.inputs[0].default_value = (0.25, 0.25, 0.27, 1.0)
    bg.inputs[1].default_value = 1.0
    for o in bpy.data.objects:
        if o.type in ("ARMATURE", "EMPTY"):
            o.hide_render = True
    if "ReviewSun" not in bpy.data.objects:
        sun = bpy.data.objects.new("ReviewSun", bpy.data.lights.new("ReviewSun", "SUN"))
        sun.data.energy = 3.0
        sun.rotation_euler = (math.radians(50), 0, math.radians(30))
        S.collection.objects.link(sun)
    cam = bpy.data.objects.get("ReviewCam")
    if cam is None:
        cam = bpy.data.objects.new("ReviewCam", bpy.data.cameras.new("ReviewCam"))
        S.collection.objects.link(cam)
    cam.data.type = "ORTHO"
    cam.data.ortho_scale = ortho
    S.camera = cam
    pos = {"front": (0, dist, center_z), "side": (dist, 0, center_z), "back": (0, -dist, center_z),
           "three_quarter": (dist * 0.7, dist * 0.7, center_z + 2.0)}
    out = []
    for v in views:
        cam.location = Vector(pos[v])
        cam.rotation_euler = (Vector((0, 0, center_z)) - cam.location).to_track_quat("-Z", "Y").to_euler()
        S.render.filepath = f"{out_prefix}_{v}.png"
        bpy.ops.render.render(write_still=True)
        out.append(S.render.filepath)
    return out
