"""MANDAT MIGRATION CENDRE - pilote. Rend le combo de base 3 coups en
haute densite depuis le GLB rigge+anime (Meshy Punch_Combo, action_id
198) + une retouche manuelle (coup 3, os poses a la main) - meme
technique que pose_walk_brute.py/pose_walk_crawler.py (rotation de
bones nommes, capture Cycles CPU headless par frame).

Coup1 (croix, mocap Punch_Combo) et coup2 (uppercut, mocap Punch_Combo)
viennent du mouvement de bibliotheque Meshy tel quel (aucune retouche
de pose, seulement un echantillonnage non-uniforme du temps : dense a
l'anticipation, 2 frames au contact, etale a la recuperation - regle
de la Bible d'animation). Coup3 (crochet gauche, finisher) n'existe pas
dans Punch_Combo (qui ne contient que 2 frappes distinctes, verifie par
scout render avant tout rendu final - voir docs/worklog.md) : pose a la
main sur le meme squelette (bones LeftArm/LeftForeArm/Spine), amorcee
depuis la pose de garde reelle du mocap (frame 49, quasi-bind-pose) pour
que la coupure mocap->pose-a-la-main soit invisible.

CORRECTIF post-verification (2026-08-23, voir docs/worklog.md) : le
choix initial des frames de contact coup2 (mocap plat, aucun pic) et
coup3 (frac=1.0 dupliquee, 0.00% de diff) a ete revu - voir les
commentaires sur COUP2 et COUP3_CONTACT_KEYS ci-dessous pour le detail
et la justification mesuree.

CORRECTIF MANDAT CORRECTION PILOTE (2026-08-23, voir docs/worklog.md) :
deux defauts visuels releves par Milan sur la capture ci-dessus,
corriges A LA SOURCE (pas de retouche frame par frame) :
- Defaut 1 (bavure aux articulations, coup1 contact) : cause isolee par
  diagnostic (experiments/blender_capture/cendre_pilot/diag_defect1.py
  + inspect_shard_weights.py, non commites) - PAS un exces d'influences
  par sommet (deja plafonne a 4, standard glTF) ni les sommets
  dupliques (48.6% de doublons mesures mais un rebind apres fusion
  reproduit IDENTIQUEMENT le defaut, doublons elimines comme cause).
  Cause reelle : en VRAIE pose de repos (bras le long du corps, pas la
  pose de garde de la frame 1 de l'action), la main droite touche/frole
  l'ourlet dechiquete de la tunique a hauteur de hanche -> le
  heat-weighting automatique (Meshy comme Blender, verifie par un
  rebind ARMATURE_AUTO qui reproduit le meme defaut) colle ~950 sommets
  de l'ourlet a l'os RightHand (poids ~0.96-0.98) au lieu de
  Hips/RightUpLeg. Quand le bras part en avant dans le coup, ces
  sommets sont traines avec le poing -> l'echarde. Fix (fonction
  `fix_shoulder_hem_skinning` ci-dessous, appliquee une fois au rig,
  benefice automatique a toutes les animations futures) : recalcul des
  poids automatiques (`ARMATURE_AUTO`) pendant que LES DEUX bras sont
  ECARTES du corps (le contact disparait, le heat-weighting retombe sur
  le bon os), puis remise a plat de la pose (0,0,0) - la pose utilisee
  pour le calcul n'affecte que la QUALITE du heat-weighting, pas les
  matrices de repos de l'armature ni l'action Punch_Combo qui continue
  de s'appliquer normalement par-dessus.
- Defaut 2 (silhouette molle, coup3) : rim light ajoutee dans
  `setup_scene()` (lumiere de contour froide/neutre, discrete, en
  contre-jour) pour detacher les membres du torse sombre. Saturation
  re-mesuree apres coup (voir docs/worklog.md) pour confirmer qu'elle
  ne derive pas au-dessus du PixelLab existant.

MANDAT DERNIERE TENTATIVE, round 3 materiau (2026-08-23, voir docs/
worklog.md) : le test au vrai canvas cuit 64px (commit b1e762e) a
donne un verdict NEGATIF - le rendu devient un bloc grisatre moucheté
("poivre et sel") une fois quantifie/compresse, moins lisible que le
PixelLab a la meme taille. Diagnostic MESURE (pas suppose) avant toute
retouche : le materiau importe du GLB (`Material_1`) a `Metallic=1.0`,
`Roughness=0.41` - une comparaison rendue metallic=1 vs metallic=0 ne
change quasiment rien au bruit (diff pixel moyenne ~1.3/255 sur 512px,
voir mat_round3/compare_iter0_iter1.png, working dir non commite) : la
specularite BSDF n'est PAS la cause dominante. La vraie cause, retrouvee
en exportant `texture_0` (2048px, partagee par Base Color ET Emission
Color, Emission Strength=1.0) : c'est une texture d'albedo a tres haute
frequence (mosaique de patches gris/noir/creme de quelques dizaines de
pixels sur 2048px, cf. mat_round3/texture_0.png) qui, emise quasi TELLE
QUELLE (Emission Strength=1.0, non affectee par l'eclairage), s'aliase
en bruit une fois le rendu downscale a 64px - exactement le "poivre et
sel" deja note au round 2. Fix retenu (fonction
`flatten_material_albedo` ci-dessous, testee frame par frame avant
generalisation - voir docs/worklog.md) : (1) reduction de la
contribution specular/metallique comme demande par le mandat (Metallic
0.0, Roughness 0.9, Specular IOR Level 0.15) - insuffisant seul mais
conserve car conforme a l'intention du mandat et sans effet negatif ;
(2) posterisation du canal VALUE (HSV, Teinte/Saturation intactes -
evite le shift de couleur d'un posterize RGB par canal) de la texture
d'albedo/emission en 5 paliers, inseree par noeuds Blender
(SeparateColor/Math SNAP/CombineColor) directement sur le graphe de
materiau importe - AUCUNE texture regeneree ni modifiee sur le disque,
un rendu/shader plus proche d'un toon shading comme suggere par le
mandat en cas d'insuffisance de la seule reduction specular. Rim light
(round 1) intacte, non touchee par ce changement.

Usage:
    blender --background --factory-startup --python render_combo_cendre.py -- \
        --glb=<combo.glb> --out_dir=<dir> [--res=512] [--samples=32] \
        [--sections=coup1,transition_1_2,coup2,transition_2_3,coup3] \
        [--fix_weights=1] [--rim_light=1] [--mat_flatten=1] \
        [--mat_metallic=0.0] [--mat_roughness=0.9] [--mat_specular=0.15] \
        [--mat_posterize_steps=5]
"""
import bpy
import sys
import os
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
out_dir = args["out_dir"]
res = int(args.get("res", "512"))
samples = int(args.get("samples", "32"))
cam_size = float(args.get("cam_size", "2.2"))
yaw_deg = float(args.get("yaw_deg", "10"))
# --sections permet de ne regenerer qu'un sous-ensemble des blocs
# (correctif post-verification coup2/coup3, voir docs/worklog.md
# 2026-08-23) sans re-rendre tout le combo (coup1 inchange, cout/temps
# inutile). Defaut = tout, comme avant.
sections = set(args.get("sections", "coup1,transition_1_2,coup2,transition_2_3,coup3").split(","))
fix_weights = args.get("fix_weights", "1") != "0"
rim_light_enabled = args.get("rim_light", "1") != "0"
# MANDAT DERNIERE TENTATIVE round 3 (voir docs/worklog.md) : aplatissement
# du materiau (specular + posterisation de l'albedo/emission). Defaut ON
# avec les valeurs retenues par comparaison mesuree ; mat_flatten=0
# reproduit le comportement des rounds 1/2 (materiau Meshy tel quel).
mat_flatten_enabled = args.get("mat_flatten", "1") != "0"
mat_metallic = float(args.get("mat_metallic", "0.0"))
mat_roughness = float(args.get("mat_roughness", "0.9"))
mat_specular = float(args.get("mat_specular", "0.15"))
mat_posterize_steps = int(args.get("mat_posterize_steps", "5"))

os.makedirs(out_dir, exist_ok=True)

# ---------------------------------------------------------------- import
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=glb_path)

armature = None
mesh_obj = None
for obj in bpy.context.scene.objects:
    if obj.type == "ARMATURE":
        armature = obj
    if obj.type == "MESH" and obj.name.lower() != "icosphere":
        if mesh_obj is None or len(obj.data.vertices) > len(mesh_obj.data.vertices):
            mesh_obj = obj
assert armature is not None
assert mesh_obj is not None


def fix_shoulder_hem_skinning(armature, mesh_obj):
    """CORRECTIF MANDAT CORRECTION PILOTE, defaut 1 (voir docs/worklog.md
    2026-08-23) : recalcule les poids automatiques du mesh pendant que
    RightArm/LeftArm sont ecartes du corps, pour eviter que le
    heat-weighting colle l'ourlet de la tunique (qui touche la main au
    repos, bras le long du corps) a l'os de la main. Applique UNE FOIS
    au rig import - benefice automatique a toutes les poses/animations
    rendues ensuite dans ce process (coup1/2/3 et au-dela)."""
    orig_parent_inverse = mesh_obj.matrix_parent_inverse.copy()

    bpy.context.view_layer.objects.active = armature
    bpy.ops.object.select_all(action="DESELECT")
    armature.select_set(True)
    bpy.ops.object.mode_set(mode="POSE")
    for pb_name, euler_deg in (("RightArm", (90.0, 0.0, 0.0)), ("LeftArm", (-90.0, 0.0, 0.0))):
        pb = armature.pose.bones[pb_name]
        pb.rotation_mode = "XYZ"
        pb.rotation_euler = tuple(math.radians(d) for d in euler_deg)
    bpy.ops.object.mode_set(mode="OBJECT")
    bpy.context.view_layer.update()

    bpy.context.view_layer.objects.active = mesh_obj
    bpy.ops.object.select_all(action="DESELECT")
    mesh_obj.select_set(True)
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.mesh.remove_doubles(threshold=0.0001)  # ~48.6% de sommets dupliques mesures (piege Meshy connu) - fusionnes ici, meme s'ils n'etaient pas la cause de la bavure
    bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.object.mode_set(mode="OBJECT")

    bpy.ops.object.select_all(action="DESELECT")
    mesh_obj.select_set(True)
    armature.select_set(True)
    bpy.context.view_layer.objects.active = armature
    bpy.ops.object.parent_set(type="ARMATURE_AUTO")

    mesh_obj.matrix_parent_inverse = orig_parent_inverse

    bpy.context.view_layer.objects.active = armature
    bpy.ops.object.select_all(action="DESELECT")
    armature.select_set(True)
    bpy.ops.object.mode_set(mode="POSE")
    for pb_name in ("RightArm", "LeftArm"):
        pb = armature.pose.bones[pb_name]
        pb.rotation_mode = "XYZ"
        pb.rotation_euler = (0.0, 0.0, 0.0)
    bpy.ops.object.mode_set(mode="OBJECT")
    bpy.context.view_layer.update()
    print("FIX_SHOULDER_HEM_SKINNING_APPLIED")


def fix_hip_hem_proximity(armature, mesh_obj):
    """CORRECTIF MANDAT CORRECTION PILOTE ROUND 2, defaut 2 (ecoharde
    triangulaire residuelle a la hanche, voir docs/worklog.md) : le fix
    round 1 (fix_shoulder_hem_skinning, abduction 90 deg + rebind) a
    corrige la bavure epaule/bras mais PAS ce second point de tunique -
    diagnostic mesure (inspect_hip_shard.py/inspect_static_proximity.py,
    working dir non commite) : ~605-2002 sommets restent domines
    (poids >0.9) par RightHand/LeftHand meme apres abduction a 90/135/
    175 deg (la distance brute a la main AUGMENTE avec l'abduction, de
    ~0.27 a plus de 1.3 unite, sans que le poids recalcule change - donc
    PAS un probleme de distance 3D corrigible par une pose ecartee,
    contrairement au defaut epaule/bras). Cause confirmee differente :
    l'integralite du groupe de vertex "RightHand a poids dominant" (measure :
    n=2002, z entre 0.566 et 0.874) est **entierement** sous la tete de
    l'os RightHand (z=1.142, marge -0.27 a -0.58) - largement au-dela
    d'une longueur de main/doigts plausible (~0.10-0.15 sur un
    personnage d'~1.7 unite) - preuve que ce ne sont PAS des sommets de
    main/gant legitimes mais un pan de tunique entier mal rattache par
    le heat-weighting (probablement par diffusion/visibilite bloquee
    par la geometrie, pas par distance 3D simple - une tentative de
    vote topologique BFS en excluant les sommets suspects a confirme
    poids inchange, preuve que le pan mal-pese est plus etendu que le
    seul sous-ensemble a deplacement anormal).

    Correctif retenu (le plus etroit qui separe reellement le tissu de
    la main sans toucher la vraie geometrie de main/gant, verifie par
    rendu comparatif avant/apres sur coup1/2/3) : parmi les sommets a
    poids RightHand/LeftHand dominant (>0.5), ceux dont le Z de repos
    est de plus de 0.18 unite SOUS la tete de l'os concerne (marge
    choisie entre l'etendue mesuree du defaut ~0.27-0.58 et une longueur
    de main plausible ~0.10-0.15) sont reassignes a l'os du bas du corps
    (Hips/RightUpLeg/LeftUpLeg/RightLeg/LeftLeg) le plus proche par
    distance de tete, poids plein, autres groupes retires. Applique
    APRES fix_shoulder_hem_skinning (qui reste necessaire pour le
    defaut epaule/bras, non touche par ce correctif)."""
    scene_local = bpy.context.scene
    scene_local.frame_set(1)
    bpy.context.view_layer.update()

    vg_index_to_name = {vg.index: vg.name for vg in mesh_obj.vertex_groups}

    def weight_of(v, bone_name):
        for g in v.groups:
            if vg_index_to_name.get(g.group, "?") == bone_name:
                return g.weight
        return 0.0

    hand_head_z = {}
    for hand in ("RightHand", "LeftHand"):
        pb = armature.pose.bones[hand]
        hand_head_z[hand] = (armature.matrix_world @ pb.head).z

    bone_head = {}
    for name in ("Hips", "RightUpLeg", "LeftUpLeg", "RightLeg", "LeftLeg"):
        pb = armature.pose.bones[name]
        bone_head[name] = armature.matrix_world @ pb.head

    MARGIN = 0.18
    reassign_plan = {}
    for v in mesh_obj.data.vertices:
        for hand in ("RightHand", "LeftHand"):
            w = weight_of(v, hand)
            if w <= 0.5:
                continue
            p = mesh_obj.matrix_world @ v.co
            if hand_head_z[hand] - p.z > MARGIN:
                hip_dists = {b: (p - bone_head[b]).length for b in bone_head}
                best = min(hip_dists, key=hip_dists.get)
                reassign_plan[v.index] = best
            break

    vg_by_name = {vg.name: vg for vg in mesh_obj.vertex_groups}
    for vidx, new_bone in reassign_plan.items():
        v = mesh_obj.data.vertices[vidx]
        old_groups = [vg_index_to_name.get(g.group, "?") for g in v.groups]
        for gname in old_groups:
            if gname in vg_by_name:
                vg_by_name[gname].remove([vidx])
        if new_bone not in vg_by_name:
            vg_by_name[new_bone] = mesh_obj.vertex_groups.new(name=new_bone)
            vg_by_name = {vg.name: vg for vg in mesh_obj.vertex_groups}
        vg_by_name[new_bone].add([vidx], 1.0, "REPLACE")

    print(f"FIX_HIP_HEM_PROXIMITY_APPLIED reassigned={len(reassign_plan)} margin={MARGIN}")


def _posterize_texture_output(node_tree, tex_node_name, steps):
    """MANDAT DERNIERE TENTATIVE round 3 (voir docs/worklog.md). Insere
    Separate/Combine Color (mode HSV) + Math(SNAP) sur le SEUL canal
    Value juste apres le noeud TEX_IMAGE nomme, pour aplatir le bruit
    haute-frequence de l'albedo/emission (mesure comme la cause reelle
    du "poivre et sel" a 64px, pas la specularite BSDF - comparaison
    metallic=1 vs metallic=0 quasi identique, voir docstring en tete de
    fichier) en un petit nombre de plages de LUMINOSITE plates. Teinte/
    Saturation d'origine intactes (evite le shift de couleur d'un
    posterize RGB par canal, teste et rejete - voir mat_round3/
    iter2_posterize5.png, working dir non commite). AUCUNE texture
    modifiee sur le disque - uniquement le graphe de noeuds en memoire
    pour ce rendu. Rebranche tous les liens existants depuis la sortie
    Color du noeud texture vers la sortie posterisee."""
    if tex_node_name not in node_tree.nodes:
        return
    tex_node = node_tree.nodes[tex_node_name]
    color_output = tex_node.outputs["Color"]
    links_to_rewire = [l for l in node_tree.links if l.from_socket == color_output]
    if not links_to_rewire:
        return
    sep = node_tree.nodes.new("ShaderNodeSeparateColor")
    sep.mode = "HSV"
    node_tree.links.new(color_output, sep.inputs["Color"])
    comb = node_tree.nodes.new("ShaderNodeCombineColor")
    comb.mode = "HSV"
    node_tree.links.new(sep.outputs["Red"], comb.inputs["Red"])      # Teinte, passthrough
    node_tree.links.new(sep.outputs["Green"], comb.inputs["Green"])  # Saturation, passthrough
    incr = 1.0 / steps
    m = node_tree.nodes.new("ShaderNodeMath")
    m.operation = "SNAP"
    m.inputs[1].default_value = incr
    node_tree.links.new(sep.outputs["Blue"], m.inputs[0])  # Value
    node_tree.links.new(m.outputs[0], comb.inputs["Blue"])
    for l in links_to_rewire:
        to_socket = l.to_socket
        node_tree.links.remove(l)
        node_tree.links.new(comb.outputs["Color"], to_socket)
    print(f"POSTERIZE_APPLIED node={tex_node_name} steps={steps}")


def flatten_material_specular(metallic, roughness, specular, posterize_steps):
    """MANDAT DERNIERE TENTATIVE round 3 (voir docs/worklog.md) : reduit
    la contribution specular/metallique du materiau Cendre importe du
    GLB (`Material_1`, seul materiau texture du personnage - `Material`
    et `Dots Stroke` ne portent aucune texture visible, non touches) ET
    aplatit son albedo/emission par bandes de luminosite (posterisation
    HSV Value, voir `_posterize_texture_output`). Les deux leviers
    demandes par le mandat (roughness/specular ET bascule vers un rendu
    plus "toon") - la reduction specular seule etait mesuree insuffisante
    (voir docstring en tete de fichier), la posterisation est ce qui
    apporte le gain reel."""
    for mat in bpy.data.materials:
        if mat.name != "Material_1" or not mat.use_nodes:
            continue
        for node in mat.node_tree.nodes:
            if node.type == "BSDF_PRINCIPLED":
                node.inputs["Metallic"].default_value = metallic
                node.inputs["Roughness"].default_value = roughness
                node.inputs["Specular IOR Level"].default_value = specular
        if posterize_steps > 0:
            for tex_name in ("Image Texture", "Image Texture.001"):
                _posterize_texture_output(mat.node_tree, tex_name, posterize_steps)
        print(f"MATERIAL_FLATTENED metallic={metallic} roughness={roughness} specular={specular} posterize_steps={posterize_steps}")


if fix_weights:
    fix_shoulder_hem_skinning(armature, mesh_obj)
    fix_hip_hem_proximity(armature, mesh_obj)

if mat_flatten_enabled:
    flatten_material_specular(mat_metallic, mat_roughness, mat_specular, mat_posterize_steps)

action = bpy.data.actions[0]
if armature.animation_data is None:
    armature.animation_data_create()
armature.animation_data.action = action

# ---------------------------------------------------------------- camera/light (memes reglages que capture_pose.py/rig_final_*.py)
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
cam_data.ortho_scale = cam_size
cam_obj = bpy.data.objects.new("Cam", cam_data)
scene.collection.objects.link(cam_obj)
yaw, pitch = math.radians(yaw_deg), math.radians(18)
direction = mathutils.Vector((math.sin(yaw) * math.cos(pitch), -math.cos(yaw) * math.cos(pitch), math.sin(pitch)))
scene.camera = cam_obj

light_data = bpy.data.lights.new("L", type="SUN")
light_data.energy = 3.0
light_obj = bpy.data.objects.new("L", light_data)
light_obj.rotation_euler = (math.radians(55), 0.0, math.radians(-30))
scene.collection.objects.link(light_obj)

# CORRECTIF MANDAT CORRECTION PILOTE, defaut 2 (silhouette molle, voir
# docs/worklog.md 2026-08-23) : rim light en contre-jour pour detacher
# les membres du torse sombre. Rayons alignes sur `direction` (le
# vecteur camera->centre calcule plus haut) via le meme to_track_quat
# que la camera, pour que la lumiere vienne bien de DERRIERE le
# personnage relativement a la camera, quel que soit yaw_deg - generique,
# pas une valeur en dur specifique a cette prise de vue. Teinte
# neutre/froide (leger bleu) et energie sous la key light (3.0) pour
# rester discrete, ne pas creer de halo colore qui casserait l'identite
# desaturee de Cendre (re-mesure de saturation faite separement, voir
# docs/worklog.md).
if rim_light_enabled:
    rim_data = bpy.data.lights.new("RimL", type="SUN")
    rim_data.energy = 1.6
    rim_data.color = (0.80, 0.88, 1.0)
    rim_obj = bpy.data.objects.new("RimL", rim_data)
    rim_obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    scene.collection.objects.link(rim_obj)

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

# Cadrage a echelle commune (meme logique que rig_final_brute.py) : Z
# du sol calcule une fois sur la bind pose, tenu fixe pour toutes les
# frames pour eviter tout jitter de camera entre poses.
scene.frame_set(1)
bpy.context.view_layer.update()
depsgraph = bpy.context.evaluated_depsgraph_get()
depsgraph.update()
_, mins0, maxs0 = compute_bbox(bpy.context.scene.objects, depsgraph)
target_z = mins0.z + cam_size * 0.42


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
    print("FRAME_RENDERED", tag, out_path)
    return out_path


manifest = []

# ---------------------------------------------------------------- coup1 (croix, mocap pur)
if "coup1" in sections:
    COUP1 = {
        "anticipation": [2, 4, 6, 8, 10, 11, 12, 13],
        "contact": [16, 18],
        "recovery": [20, 22, 24],
    }
    for phase, frames in COUP1.items():
        for i, f in enumerate(frames):
            scene.frame_set(f)
            tag = f"coup1_{phase}_{i:02d}_mocapframe{f}"
            render_current_pose(tag)
            manifest.append({"coup": 1, "phase": phase, "source": "mocap_punch_combo", "mocap_frame": f, "tag": tag})

# ---------------------------------------------------------------- transition 1->2 (mocap pur, zone de fondu)
if "transition_1_2" in sections:
    TRANSITION_1_2 = [25, 27, 29]
    for i, f in enumerate(TRANSITION_1_2):
        scene.frame_set(f)
        tag = f"transition_1to2_{i:02d}_mocapframe{f}"
        render_current_pose(tag)
        manifest.append({"coup": "transition_1to2", "phase": "transition", "source": "mocap_punch_combo", "mocap_frame": f, "tag": tag})

# ---------------------------------------------------------------- coup2 (uppercut, mocap pur - anticipation propre + les 3 frames de transition ci-dessus lui appartiennent aussi narrativement)
# CORRECTIF post-verification (voir docs/worklog.md, 2026-08-23) :
# l'ancien choix contact=[34, 35] tombait dans un plateau quasi-statique
# du clip (le bras/lame reste leve pres du visage de la frame 32 a la
# frame 38, diff pixel a plat 5-10%, aucun pic net au contact). Scout
# fin frame-par-frame (scout_coup2/, diff pixel + inspection visuelle
# zoomee) sur TOUT le segment mocap 24-42 : la frame 31 est le point de
# reach maximal reel (bbox top-of-silhouette la plus haute de tout le
# clip, bras+lame au plus loin du corps) ; la frame 33 est la 2e frame
# la plus distincte pres du pic (main qui se replie deja legerement
# vers le visage). anticipation raccourcie a [26, 28] pour que le grand
# mouvement de swing (frames 29-31, la portion la plus rapide du clip,
# ~11%/frame) tombe ENTRE la derniere frame d'anticipation et la
# premiere frame de contact au lieu d'etre absorbe dedans - c'est ce
# qui cree le pic a l'entree en contact (meme principe que coup1, qui
# saute lui aussi 2 frames mocap entre anticipation et contact).
COUP2 = {
    "anticipation": [26, 28],
    "contact": [31, 33],
    "recovery": [35, 37, 39, 41],
}
if "coup2" in sections:
    for phase, frames in COUP2.items():
        for i, f in enumerate(frames):
            scene.frame_set(f)
            tag = f"coup2_{phase}_{i:02d}_mocapframe{f}"
            render_current_pose(tag)
            manifest.append({"coup": 2, "phase": phase, "source": "mocap_punch_combo", "mocap_frame": f, "tag": tag})

# ---------------------------------------------------------------- transition 2->3 (mocap pur, queue de garde qui sert de pont vers la pose a la main)
if "transition_2_3" in sections:
    TRANSITION_2_3 = [43, 46, 49]
    for i, f in enumerate(TRANSITION_2_3):
        scene.frame_set(f)
        tag = f"transition_2to3_{i:02d}_mocapframe{f}"
        render_current_pose(tag)
        manifest.append({"coup": "transition_2to3", "phase": "transition", "source": "mocap_punch_combo", "mocap_frame": f, "tag": tag})

# ---------------------------------------------------------------- coup3 (crochet gauche, pose a la main - retouche Blender)
# Punch_Combo (verifie par scout render avant ce rendu final, voir
# docs/worklog.md) ne contient que 2 frappes distinctes (croix + uppercut) ;
# le 3e coup du combo de base n'existe pas dans le mouvement de
# bibliotheque. Pose a la main a partir de la derniere frame mocap (49,
# quasi-bind-pose de garde) pour que la coupure soit invisible : action
# detachee a ce point precis, la pose courante devient la nouvelle base,
# puis LeftArm/LeftForeArm/Spine sont pilotes directement (meme technique
# que pose_walk_brute.py/pose_walk_crawler.py). Calibration des axes
# effectuee au prealable par rendus-test isoles (rx=-90 sur LeftArm =
# bras leve devant soi, confirme visuellement avant tout rendu final).
if "coup3" in sections:
    scene.frame_set(49)
    bpy.context.view_layer.update()
    armature.animation_data.action = None  # la pose courante (frame 49) devient la base figee

    bpy.context.view_layer.objects.active = armature
    armature.select_set(True)
    bpy.ops.object.mode_set(mode="POSE")

    def set_bone_euler(name, euler_deg):
        pb = armature.pose.bones[name]
        pb.rotation_mode = "XYZ"
        pb.rotation_euler = tuple(math.radians(d) for d in euler_deg)

    # RightArm/RightForeArm ne sont touches QUE pendant le contact
    # (contre-mouvement du bras de garde, voir COUP3_CONTACT_KEYS
    # ci-dessous) - leur pose de frame 49 (mocap, garde reelle) est
    # capturee ici pour etre explicitement restauree en recuperation,
    # au lieu de laisser un residu du contre-mouvement de contact.
    right_arm_base = tuple(armature.pose.bones["RightArm"].rotation_euler)
    right_forearm_base = tuple(armature.pose.bones["RightForeArm"].rotation_euler)

    def restore_right_arm_base():
        armature.pose.bones["RightArm"].rotation_mode = "XYZ"
        armature.pose.bones["RightArm"].rotation_euler = right_arm_base
        armature.pose.bones["RightForeArm"].rotation_mode = "XYZ"
        armature.pose.bones["RightForeArm"].rotation_euler = right_forearm_base

    # Amplitude "posee" (calibree empiriquement) : bras leve devant/vers
    # le haut, avant-bras replie, leger contre-buste dans le coup. Sert
    # de reference (fraction 1.0) pour l'anticipation/recuperation.
    PEAK_RX, PEAK_FRX, PEAK_SPINE_RZ = -90.0, -60.0, -12.0

    COUP3_ANTICIPATION_FRACS = [0.05, 0.15, 0.28, 0.42, 0.58, 0.72, 0.85]
    COUP3_RECOVERY_FRACS = [0.75, 0.5, 0.28, 0.08]

    # CORRECTIF post-verification (voir docs/worklog.md, 2026-08-23) :
    # l'ancien contact=[1.0, 1.0] posait deux fois la MEME fraction (donc
    # la meme pose, 0.00% de diff pixel mesure) au lieu d'une vraie 2e
    # cle. Remplace par deux cles d'impact distinctes et intentionnelles.
    # Un premier essai en pur overshoot (108-135% de l'amplitude posee
    # sur LeftArm/LeftForeArm/Spine seuls) a ete mesure INSUFFISANT
    # (~6% de diff, encore dans le bruit d'anticipation - voir
    # tune_coup3_contact.py, diagnostic conserve dans le repertoire de
    # travail non commite) : au-dela d'un certain angle, le bras gauche
    # seul ne degage plus assez de nouveaux pixels (silhouette bornee
    # pres de la tete/epaule). Ajout d'un VRAI contre-mouvement du bras
    # DROIT (bras de garde qui se retire/s'abaisse pendant que le bras
    # gauche porte le coup - mecanique de hanche/epaule d'un vrai
    # crochet) : ca fait bouger une 2e zone independante de l'image et
    # ramene le pic mesure a l'ordre de grandeur de coup1 (~13-14%
    # d'entree/sortie de contact, cf. rapport de verification ci-dessous):
    #   - impact_peak    : LeftArm/LeftForeArm en overshoot (135/140% de
    #     l'amplitude posee), Spine tres marque (180%), RightArm/
    #     RightForeArm tires vers l'arriere/le bas (contre-mouvement de
    #     garde, +20/+15 deg) - le corps entier "rentre" dans le coup.
    #   - impact_release : le buste commence a se de-rotater (130%,
    #     redescend depuis 180%), le bras gauche relache legerement
    #     (105%) et le bras droit revient partiellement vers sa pose de
    #     base (+8/+6 deg) - relachement immediat de l'impact, silhouette
    #     encore nettement differente de la 1ere frame de recuperation
    #     (frac 0.75, RightArm non touche = pose de base frame 49).
    # Meme axe (rx) que la calibration d'origine pour LeftArm/LeftForeArm/
    # Spine ; RightArm/RightForeArm rx deja calibres et verifies pour
    # l'autre bras par le mandat d'origine (cal_right.png/cal_right2.png,
    # calibrate_pose.py --side=right) - meme convention de signe reutilisee,
    # aucune nouvelle calibration d'axe necessaire.
    COUP3_CONTACT_KEYS = [
        ("impact_peak", 1.35, 1.4, 1.8, 20.0, 15.0),
        ("impact_release", 1.05, 1.05, 1.3, 8.0, 6.0),
    ]

    for i, frac in enumerate(COUP3_ANTICIPATION_FRACS):
        set_bone_euler("LeftArm", (PEAK_RX * frac, 0, 0))
        set_bone_euler("LeftForeArm", (PEAK_FRX * frac, 0, 0))
        set_bone_euler("Spine", (0, 0, PEAK_SPINE_RZ * frac))
        bpy.ops.object.mode_set(mode="OBJECT")
        tag = f"coup3_anticipation_{i:02d}_frac{frac:.2f}"
        render_current_pose(tag)
        manifest.append({"coup": 3, "phase": "anticipation", "source": "hand_posed_blender_script", "pose_fraction": frac, "tag": tag})
        bpy.context.view_layer.objects.active = armature
        armature.select_set(True)
        bpy.ops.object.mode_set(mode="POSE")

    for i, (key_tag, arm_frac, forearm_frac, spine_frac, right_arm_rx, right_forearm_rx) in enumerate(COUP3_CONTACT_KEYS):
        set_bone_euler("LeftArm", (PEAK_RX * arm_frac, 0, 0))
        set_bone_euler("LeftForeArm", (PEAK_FRX * forearm_frac, 0, 0))
        set_bone_euler("Spine", (0, 0, PEAK_SPINE_RZ * spine_frac))
        set_bone_euler("RightArm", (right_arm_rx, 0, 0))
        set_bone_euler("RightForeArm", (right_forearm_rx, 0, 0))
        bpy.ops.object.mode_set(mode="OBJECT")
        tag = f"coup3_contact_{i:02d}_{key_tag}"
        render_current_pose(tag)
        manifest.append({
            "coup": 3, "phase": "contact", "source": "hand_posed_blender_script",
            "pose_key": key_tag, "arm_frac": arm_frac, "forearm_frac": forearm_frac,
            "spine_frac": spine_frac, "right_arm_rx": right_arm_rx,
            "right_forearm_rx": right_forearm_rx, "tag": tag,
        })
        bpy.context.view_layer.objects.active = armature
        armature.select_set(True)
        bpy.ops.object.mode_set(mode="POSE")

    for i, frac in enumerate(COUP3_RECOVERY_FRACS):
        set_bone_euler("LeftArm", (PEAK_RX * frac, 0, 0))
        set_bone_euler("LeftForeArm", (PEAK_FRX * frac, 0, 0))
        set_bone_euler("Spine", (0, 0, PEAK_SPINE_RZ * frac))
        restore_right_arm_base()  # efface le contre-mouvement de contact, retour a la garde mocap frame49
        bpy.ops.object.mode_set(mode="OBJECT")
        tag = f"coup3_recovery_{i:02d}_frac{frac:.2f}"
        render_current_pose(tag)
        manifest.append({"coup": 3, "phase": "recovery", "source": "hand_posed_blender_script", "pose_fraction": frac, "tag": tag})
        bpy.context.view_layer.objects.active = armature
        armature.select_set(True)
        bpy.ops.object.mode_set(mode="POSE")

    bpy.ops.object.mode_set(mode="OBJECT")

import json
with open(os.path.join(out_dir, "manifest.json"), "w") as fh:
    json.dump(manifest, fh, indent=2)

print("RENDER_COMBO_DONE", len(manifest), "frames")
