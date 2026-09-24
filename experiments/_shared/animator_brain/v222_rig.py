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
HOLDERS = ("Left Arm", "Right Arm", "Left Leg", "Right Leg", "Torso", "Head", "Body")
RIG_COLLECTION = "Rig1"         # collection racine du rig dans le .blend

# Conventions MESUREES sur le rig (probe du 2026-09-23, voir RIG_V222.md) :
# avant du personnage = +Y Blender ; 1 unite Blender = 1 stud ; semelles a z=0 ;
# scene a 60 fps.
FORWARD = (0.0, 1.0, 0.0)

_RIGS = []   # rigs de la scene ; le premier est le rig par defaut


def _base(name):
    """'Right Arm.001' -> 'Right Arm' (suffixe ajoute par Blender a l'append)."""
    head, _dot, tail = name.rpartition(".")
    return head if head and tail.isdigit() and len(tail) == 3 else name


class RigHandle:
    """Un personnage V2.22 de la scene : ses objets, retrouves par nom de
    base dans SA collection (un 2e rig ajoute par append porte des noms
    suffixes .001, et ses drivers/contraintes pointent vers SES copies)."""

    def __init__(self, collection):
        self.collection = collection
        objs = list(collection.all_objects)
        self.primary = next(o for o in objs if o.type == "ARMATURE" and o.get("_Rbx_R6_Rig_"))
        self.internal = next(o for o in objs if o.type == "ARMATURE" and _base(o.name) == INTERNAL)
        self.holders = {_base(o.name): o for o in objs if o.type == "EMPTY" and _base(o.name) in HOLDERS}
        self.meshes = {}
        for o in objs:
            b = _base(o.name)
            if o.type == "MESH" and b.endswith("_MBlocky"):
                self.meshes[b[:-len("_MBlocky")]] = o
        missing = [h for h in HOLDERS if h not in self.holders]
        if missing or len(self.meshes) != 6:
            raise RuntimeError(f"rig incomplet dans {collection.name}: reglages manquants {missing}, "
                               f"maillages {sorted(self.meshes)}")

    @property
    def name(self):
        return self.collection.name


def _rig(rig):
    return rig if rig is not None else _RIGS[0]


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _check(path):
    got = sha256(path)
    if got != BLEND_SHA256:
        raise RuntimeError(f"hash du rig inattendu : {got}")


def _detach_rest_action(rig):
    if rig.primary.animation_data:
        rig.primary.animation_data.action = None


def open_rig(path, detach_rest_action=True):
    """Ouvre le rig apres verification du hash, scripts desactives. Le
    fichier embarque une action 'ArmatureAction' (pose de repos cle a la
    frame 0 sur tous les controles) qui ECRASE toute pose manuelle au rendu :
    on la detache par defaut. Retourne le RigHandle (rig par defaut)."""
    import bpy
    _check(path)
    bpy.ops.wm.open_mainfile(filepath=path, load_ui=False, use_scripts=False)
    _RIGS.clear()
    rig = RigHandle(bpy.data.collections[RIG_COLLECTION])
    if detach_rest_action:
        _detach_rest_action(rig)
    _RIGS.append(rig)
    return rig


def append_rig(path, name, detach_rest_action=True):
    """Ajoute un personnage de plus (copie complete de la collection du rig,
    append depuis le MEME fichier verifie). Blender remappe les references
    internes (contraintes, drivers, parents) vers les nouvelles copies :
    verifie par verify_independent()."""
    import os
    import shutil
    import tempfile
    import bpy
    _check(path)
    # Blender refuse d'appendre depuis le fichier deja ouvert : on appende
    # depuis une copie (meme octets, hash reverifie).
    src_path = os.path.join(tempfile.gettempdir(), f"v222_append_{len(_RIGS)}.blend")
    shutil.copyfile(path, src_path)
    _check(src_path)
    with bpy.data.libraries.load(src_path, link=False) as (src, dst):
        dst.collections = [RIG_COLLECTION]
    col = dst.collections[0]
    col.name = name
    bpy.context.scene.collection.children.link(col)
    rig = RigHandle(col)
    if detach_rest_action:
        _detach_rest_action(rig)
    _RIGS.append(rig)
    return rig


def place(rig, location=(0.0, 0.0, 0.0), yaw_deg=0.0):
    """Place un personnage dans la scene (objet __PrimaryArmature : c'est
    lui que suit le HumanoidRootPart, donc c'est la position "en jeu" du
    personnage ; MasterControl reste de l'animation)."""
    import bpy
    from mathutils import Vector
    rig.primary.location = location
    rig.primary.rotation_mode = "XYZ"
    rig.primary.rotation_euler = (0.0, 0.0, math.radians(yaw_deg))
    bpy.context.view_layer.update()
    # Le corps n'est PAS centre sur l'origine de l'armature : la contrainte
    # Child Of du HumanoidRootPart porte un decalage (0, -0.226, -1.763)
    # dans sa matrice inverse. Tourner l'objet fait donc pivoter le corps
    # autour d'un point 0.226 stud derriere lui (mesure : lacet 180 deg ->
    # corps deplace de 0.453 stud). On corrige la position de l'objet pour
    # que le HumanoidRootPart tombe EXACTEMENT a `location` (en x/y).
    arm = rig.internal
    hrp = (arm.matrix_world @ arm.pose.bones["HumanoidRootPart"].matrix).translation
    err = Vector((location[0] - hrp.x, location[1] - hrp.y, 0.0))
    rig.primary.location = Vector(location) + err
    bpy.context.view_layer.update()


def _apply_controls(controls, rig=None):
    from mathutils import Euler
    pb = _rig(rig).primary.pose.bones
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


def set_controls(controls, rig=None):
    """controls = {bone: {"location": (x,y,z), "rotation_euler": (deg,deg,deg)
    ou "rotation_quaternion": (w,x,y,z)}} -- en espace local du controle.
    ATTENTION : si le rig est deja anime, le prochain rafraichissement de la
    scene reevalue l'action et ecrase cette pose -- pour animer, utiliser
    key_controls()."""
    import bpy
    _apply_controls(controls, rig)
    bpy.context.view_layer.update()


def set_setting(part, key, value, rig=None):
    """Reglages du rig (objets de RigSettingsHolder) : ex. set_setting("Right
    Arm", "IK/FK", 1.0), ("Right Arm", "Grab", 1.0), ("Head", "Track Object",
    1.0), ("Left Leg", "Torso Influence", 0.0)."""
    import bpy
    r = _rig(rig)
    holder = r.holders[part]
    holder[key] = value
    # un changement de propriete custom ne marque pas le depsgraph : sans
    # ce tag, les drivers (type AVERAGE + courbe 0->0 / 1->1) ne sont pas
    # reevalues et l'influence des contraintes reste a l'ancienne valeur.
    holder.update_tag()
    r.primary.update_tag()
    bpy.context.view_layer.update()


def part_matrices(rig=None):
    """Matrices monde des 7 parts Roblox (InternalArmature)."""
    import bpy
    bpy.context.view_layer.update()
    arm = _rig(rig).internal
    return {p: arm.matrix_world @ arm.pose.bones[p].matrix for p in PARTS}


def lowest_point(rig=None):
    """z minimal des maillages du corps (semelles) -- pour verifier un appui
    ou une penetration du sol."""
    import bpy
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    zmin = float("inf")
    for o in _rig(rig).meshes.values():
        e = o.evaluated_get(dg)
        for v in e.data.vertices:
            zmin = min(zmin, (e.matrix_world @ v.co).z)
    return zmin


def review_render(out_prefix, views=("front", "side"), res=520, samples=16, center_z=2.3, dist=12.0,
                  ortho=6.5, target=(0.0, 0.0), aspect=1.0):
    """Rendu de revue (Cycles CPU, aucun GPU/ecran) : face et/ou profil,
    orthographique, faces etiquetees F/B/L/R/U du rig visibles. Retourne
    les chemins ecrits."""
    import bpy
    from mathutils import Vector
    S = bpy.context.scene
    S.render.engine = "CYCLES"
    S.cycles.device = "CPU"
    S.cycles.samples = samples
    S.render.resolution_y = res
    S.render.resolution_x = int(res * aspect)
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
    if "ReviewGround" not in bpy.data.objects:
        # sol a z = 0 : sans lui, impossible de juger un appui sur une revue
        me = bpy.data.meshes.new("ReviewGround")
        me.from_pydata([(-30, -30, 0), (30, -30, 0), (30, 30, 0), (-30, 30, 0)], [], [(0, 1, 2, 3)])
        g = bpy.data.objects.new("ReviewGround", me)
        mat = bpy.data.materials.new("ReviewGroundMat")
        mat.use_nodes = True
        mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.42, 0.42, 0.44, 1.0)
        me.materials.append(mat)
        S.collection.objects.link(g)
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
    tx, ty = target
    pos = {"front": (tx, ty + dist, center_z), "side": (tx + dist, ty, center_z), "back": (tx, ty - dist, center_z),
           "three_quarter": (tx + dist * 0.7, ty + dist * 0.7, center_z + 2.0),
           # camera de jeu : derriere l'epaule droite de l'attaquant (face a +Y),
           # assez decalee pour que l'attaquant ne masque pas la cible
           "gameplay": (tx + dist * 0.8, ty - dist * 0.55, center_z + dist * 0.3)}
    out = []
    for v in views:
        cam.location = Vector(pos[v])
        cam.rotation_euler = (Vector((tx, ty, center_z)) - cam.location).to_track_quat("-Z", "Y").to_euler()
        S.render.filepath = f"{out_prefix}_{v}.png"
        bpy.ops.render.render(write_still=True)
        out.append(S.render.filepath)
    return out


def key_controls(frame, controls, interpolation="BEZIER", rig=None, easing=None):
    """Pose les controles et les cle a la frame donnee.

    Piege corrige le 2026-09-24 : poser -> rafraichir la scene -> cler
    enregistrait l'ANCIENNE valeur, car le rafraichissement reevalue l'action
    existante (a la frame courante) et ecrase la pose qu'on vient d'ecrire. Seule
    la 1re cle etait juste, et le clip cuit etait statique. On cle donc
    IMMEDIATEMENT apres avoir ecrit les valeurs, et on ne rafraichit qu'ensuite."""
    import bpy
    _apply_controls(controls, rig)
    arm = _rig(rig).primary
    for name, ch in controls.items():
        b = arm.pose.bones[name]
        if "location" in ch:
            b.keyframe_insert("location", frame=frame)
        if "rotation_euler" in ch or "rotation_quaternion" in ch:
            b.keyframe_insert("rotation_quaternion", frame=frame)
    act = arm.animation_data.action if arm.animation_data else None
    if act is not None:
        for fc in _fcurves(act):
            for kp in fc.keyframe_points:
                if abs(kp.co[0] - frame) < 1e-6:
                    kp.interpolation = interpolation
                    if easing is not None:
                        kp.easing = easing
    bpy.context.view_layer.update()


def key_setting(frame, part, key, value, rig=None):
    """Cle un reglage du rig (ex. IK/FK, Grab) sur l'objet reglage."""
    r = _rig(rig)
    r.holders[part][key] = value
    r.holders[part].keyframe_insert(f'["{key}"]', frame=frame)
    set_setting(part, key, value, rig=rig)


def _fcurves(action):
    try:
        return [fc for layer in action.layers for strip in layer.strips
                for bag in strip.channelbags for fc in bag.fcurves]
    except AttributeError:
        return list(action.fcurves)


def current_parts(rig=None):
    """CFrames monde (repere Roblox) des 7 parts dans l'etat COURANT de la
    scene, sans changer de frame. Methode : delta de chaque os par rapport a
    SA pose de repos, applique a la part Roblox au repos (rotation identite,
    centre standard) -- ne depend d'aucune convention d'axe des os Blender."""
    import numpy as np
    from mathutils import Vector
    from .roblox_export import B2R, REST_CENTER, orthonormalize
    arm = _rig(rig).internal
    world = {}
    for p in PARTS:
        rest = arm.matrix_world @ arm.data.bones[p].matrix_local
        d = (arm.matrix_world @ arm.pose.bones[p].matrix) @ rest.inverted()
        c0 = B2R.T @ np.array(REST_CENTER[p])
        world[p] = (orthonormalize(B2R @ np.array(d.to_3x3()) @ B2R.T), B2R @ np.array(d @ Vector(c0)))
    return world


def limb_tip(world, part):
    """Bout d'un membre (centre de la face du bas), repere Roblox."""
    import numpy as np
    r, p = world[part]
    return p + r @ np.array([0.0, -1.0, 0.0])


def solve_control_for_tip(ctrl, part, target_roblox, rig=None, iters=12, tol=1e-3):
    """Trouve la translation du controle IK `ctrl` qui amene le bout du
    membre `part` au point voulu (repere Roblox), par Gauss-Newton avec
    jacobienne en differences finies -- independant des contraintes du rig.
    Point hors d'atteinte : converge vers le point atteignable le plus
    proche (le membre pointe vers la cible). A appeler AVANT d'animer le rig
    (sinon le rafraichissement reevalue l'action et ecrase la pose).
    Retourne (location, residu en studs)."""
    import bpy
    import numpy as np
    pb = _rig(rig).primary.pose.bones[ctrl]
    target = np.asarray(target_roblox, float)
    loc = np.array(pb.location, float)

    def tip_at(l):
        pb.location = tuple(l)
        bpy.context.view_layer.update()
        return limb_tip(current_parts(rig), part)

    cur = tip_at(loc)
    for _ in range(iters):
        err = target - cur
        if np.linalg.norm(err) < tol:
            break
        J = np.zeros((3, 3))
        for k in range(3):
            dl = np.zeros(3)
            dl[k] = 0.05
            J[:, k] = (tip_at(loc + dl) - cur) / 0.05
        step = np.linalg.solve(J.T @ J + 1e-3 * np.eye(3), J.T @ err)
        n = np.linalg.norm(step)
        if n > 1.5:
            step *= 1.5 / n
        loc = loc + step
        cur = tip_at(loc)
    return tuple(loc), float(np.linalg.norm(target - cur))


def bake_parts(frame_start, frame_end, step=1, hrp="rig", rig=None):
    """Cuit les 7 parts Roblox (InternalArmature) en CFrames MONDE, repere
    ROBLOX, pour chaque frame : [(t, {part: (R 3x3, p 3)})].

    Voir current_parts() pour la methode.
    hrp="rig" (defaut) : HumanoidRootPart = celui du rig, qui suit l'OBJET
    __PrimaryArmature (placement du personnage, voir place()) et pas
    MasterControl : tout mouvement anime passe donc par le RootJoint, comme
    en jeu ou le Humanoid tient le HumanoidRootPart.
    hrp="fixed" : HumanoidRootPart force au repos a l'origine."""
    import bpy
    import numpy as np
    from .roblox_export import REST_CENTER

    S = bpy.context.scene
    fps = S.render.fps / S.render.fps_base
    out = []
    for f in range(frame_start, frame_end + 1, step):
        S.frame_set(f)
        world = current_parts(rig)
        if hrp == "fixed":
            world["HumanoidRootPart"] = (np.eye(3), np.array(REST_CENTER["HumanoidRootPart"]))
        out.append(((f - frame_start) / fps, world))
    return out
