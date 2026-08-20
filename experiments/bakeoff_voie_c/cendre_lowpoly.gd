extends Node3D
## Bake-off Animation, Voie C — proxy 3D low-poly de Cendre, construit par
## primitives (pas de modélisation main/outil externe : aucun outil de
## génération 3D n'est accessible depuis cet environnement — ni MCP dédié
## (Meshy/Tripo/etc., recherchés et absents), ni Blender en CLI (vérifié,
## absent). Fallback explicitement sanctionné par le mandat : "le design
## du perso... est volontairement favorable à un modèle low-poly simple
## si besoin de le construire à la main/par script."
##
## v2 — 1er rendu (sphère+capsules nues) jugé "pas pareil" par Milan : pas
## assez d'éléments identifiants pour lire comme Cendre, même en silhouette
## grossière. Ajout des pièces qui PORTENT l'identité visuelle du perso
## (turnaround v3, assets/source/pixellab/cendre/reference_v3_turnaround_raw.png) :
## col sombre, jupe de tunique en cloche (l'ourlet dépenaillé), ceinture +
## pochette, bras + gants, bottes distinctes du pantalon. Toujours des
## primitives (cylindres/capsules/sphère), pas de modélisation fine (pas
## de vrai tissu déchiqueté, pas de harnais en sangles croisées — tenté en
## boîtes plates tournées en X, retiré : à la caméra 3/4 utilisée ici la
## copie "derrière" débordait de la silhouette côté visible, lisant comme
## des ailes plutôt qu'un harnais — à reprendre plus tard en décalque de
## texture si Milan le juge nécessaire) — mais les MASSES et le DÉCOUPAGE
## en zones de couleur reproduisent maintenant la vraie silhouette au lieu
## d'un mannequin nu.

const HEAD_RADIUS := 0.10
const TORSO_RADIUS := 0.20
const TORSO_HEIGHT := 0.48
const SKIRT_HEIGHT := 0.20
const SKIRT_FLARE := 1.35
const LEG_RADIUS := 0.085
const LEG_HEIGHT := 0.62
const BOOT_HEIGHT := 0.14
const BOOT_RADIUS := 0.10
const ARM_RADIUS := 0.032
const ARM_LENGTH := 0.34
const GLOVE_RADIUS := 0.038
const NECK_GAP := 0.0
const NECK_RADIUS := 0.09
const NECK_HEIGHT := 0.01
const BELT_RADIUS := 0.235
const BELT_HEIGHT := 0.045

## Hauteur totale du personnage (pieds a sommet du crane), en unites Godot
## — sert au calcul de cadrage de la camera orthogonale (voir capture_idle.gd).
var total_height: float = 0.0


func _ready() -> void:
	var boot_top: float = BOOT_HEIGHT
	var leg_top: float = boot_top + LEG_HEIGHT
	var torso_bottom: float = leg_top
	var torso_top: float = torso_bottom + TORSO_HEIGHT
	var neck_center_y: float = torso_top + NECK_GAP + NECK_HEIGHT * 0.5
	var head_center_y: float = torso_top + NECK_GAP + NECK_HEIGHT + HEAD_RADIUS
	total_height = head_center_y + HEAD_RADIUS

	# Bottes — distinctes du pantalon (teinte plus claire, façon lanières
	# enroulées du turnaround), sous le pantalon sombre.
	_add_cylinder("BootLeft", BOOT_RADIUS, BOOT_RADIUS * 0.85, BOOT_HEIGHT, Vector3(-0.11, boot_top * 0.5, 0.0), _boot_material())
	_add_cylinder("BootRight", BOOT_RADIUS, BOOT_RADIUS * 0.85, BOOT_HEIGHT, Vector3(0.11, boot_top * 0.5, 0.0), _boot_material())

	# Jambes / pantalon sombre.
	_add_capsule("LegLeft", LEG_RADIUS, LEG_HEIGHT, Vector3(-0.11, boot_top + LEG_HEIGHT * 0.5, 0.0), _dark_pants_material())
	_add_capsule("LegRight", LEG_RADIUS, LEG_HEIGHT, Vector3(0.11, boot_top + LEG_HEIGHT * 0.5, 0.0), _dark_pants_material())

	# Torse (chemise/tunique haute).
	_add_capsule("Torso", TORSO_RADIUS, TORSO_HEIGHT, Vector3(0.0, torso_bottom + TORSO_HEIGHT * 0.5, 0.0), _grey_tunic_material())

	# Jupe de tunique — cône évasé qui retombe sur le haut des jambes,
	# lit comme l'ourlet dépenaillé du turnaround sans vraie géométrie
	# déchiquetée (hors de portée d'un proxy primitive).
	_add_cone("TunicSkirt", TORSO_RADIUS * 0.95, TORSO_RADIUS * SKIRT_FLARE, SKIRT_HEIGHT, Vector3(0.0, torso_bottom - SKIRT_HEIGHT * 0.35, 0.0), _grey_tunic_material())

	# Col sombre (sous-vêtement/écharpe basse visible au cou, turnaround).
	_add_cylinder("Collar", NECK_RADIUS, NECK_RADIUS, NECK_HEIGHT, Vector3(0.0, neck_center_y, 0.0), _dark_pants_material())

	# Ceinture + pochette.
	_add_cylinder("Belt", BELT_RADIUS, BELT_RADIUS, BELT_HEIGHT, Vector3(0.0, torso_bottom + 0.01, 0.0), _leather_material())
	_add_box("Pouch", Vector3(0.07, 0.075, 0.05), Vector3(0.14, torso_bottom - 0.05, TORSO_RADIUS * 0.55), _leather_material())

	# Bras : un seul segment par bras (épaule -> poignet) + un gant sphère
	# au bout, minces et rentrés près du torse. Deux bugs trouvés en
	# itérant : (1) 3 segments empilés (manche/avant-bras/gant) avec des
	# hauteurs qui se compensaient mal finissaient groupés tout en haut,
	# près du cou, lisant comme des "pointes" parasites plutôt que des
	# bras tombants — simplifié à 1 segment ; (2) à 64px final, une
	# capsule assez épaisse n'a pas assez de résolution pour montrer son
	# arrondi et lit comme un pavé plat détaché du corps (vérifié en
	# comparant le rendu haute résolution AVANT pixelisation, où la
	# géométrie était correcte, à la version pixelisée) — corrigé en
	# amincissant le rayon et en rentrant les bras plus près du torse.
	var shoulder_y: float = torso_top - TORSO_RADIUS * 0.45
	var arm_center_y: float = shoulder_y - ARM_LENGTH * 0.5
	var glove_y: float = shoulder_y - ARM_LENGTH - GLOVE_RADIUS * 0.5
	for side in [-1.0, 1.0]:
		var shoulder_x: float = side * (TORSO_RADIUS + ARM_RADIUS * 0.4)
		_add_capsule("Arm%s" % side, ARM_RADIUS, ARM_LENGTH, Vector3(shoulder_x, arm_center_y, 0.0), _grey_tunic_material())
		_add_sphere("Glove%s" % side, GLOVE_RADIUS, Vector3(shoulder_x, glove_y, 0.0), _dark_pants_material())

	_add_sphere("Head", HEAD_RADIUS, Vector3(0.0, head_center_y, 0.0), _pale_skull_material())


func _add_capsule(node_name: String, radius: float, height: float, pos: Vector3, mat: StandardMaterial3D) -> void:
	var mesh := CapsuleMesh.new()
	mesh.radius = radius
	mesh.height = height
	var inst := MeshInstance3D.new()
	inst.name = node_name
	inst.mesh = mesh
	inst.material_override = mat
	inst.position = pos
	add_child(inst)


func _add_sphere(node_name: String, radius: float, pos: Vector3, mat: StandardMaterial3D) -> void:
	var mesh := SphereMesh.new()
	mesh.radius = radius
	mesh.height = radius * 2.0
	var inst := MeshInstance3D.new()
	inst.name = node_name
	inst.mesh = mesh
	inst.material_override = mat
	inst.position = pos
	add_child(inst)


func _add_cylinder(node_name: String, top_radius: float, bottom_radius: float, height: float, pos: Vector3, mat: StandardMaterial3D) -> void:
	var mesh := CylinderMesh.new()
	mesh.top_radius = top_radius
	mesh.bottom_radius = bottom_radius
	mesh.height = height
	var inst := MeshInstance3D.new()
	inst.name = node_name
	inst.mesh = mesh
	inst.material_override = mat
	inst.position = pos
	add_child(inst)


## Jupe de tunique évasée — cône dont le sommet touche le bas du torse
## (rayon proche du torse) et la base s'évase davantage (ourlet flottant).
func _add_cone(node_name: String, top_radius: float, bottom_radius: float, height: float, pos: Vector3, mat: StandardMaterial3D) -> void:
	var mesh := CylinderMesh.new()
	mesh.top_radius = top_radius
	mesh.bottom_radius = bottom_radius
	mesh.height = height
	var inst := MeshInstance3D.new()
	inst.name = node_name
	inst.mesh = mesh
	inst.material_override = mat
	inst.position = pos
	add_child(inst)


func _add_box(node_name: String, size: Vector3, pos: Vector3, mat: StandardMaterial3D) -> void:
	var mesh := BoxMesh.new()
	mesh.size = size
	var inst := MeshInstance3D.new()
	inst.name = node_name
	inst.mesh = mesh
	inst.material_override = mat
	inst.position = pos
	add_child(inst)


## Valeurs HSV visées dans la fourchette "character" (data/palettes/
## value_bands.json, V dans [15,90]%) — matériaux volontairement mats
## (roughness haut, metallic 0) : GDD §2 "palette désaturée... NO GLOW,
## NO MAGIC LIGHT EFFECTS" s'applique aussi au proxy, pas seulement au
## pixel art final. Le shader désature quasi tout (target_saturation) —
## les teintes ci-dessous restent volontairement proches, seule la
## luminosité (V) les distingue une fois passées dans le pipeline.
func _pale_skull_material() -> StandardMaterial3D:
	var mat := StandardMaterial3D.new()
	mat.albedo_color = Color(0.86, 0.85, 0.82)
	mat.roughness = 0.9
	mat.metallic = 0.0
	return mat


func _grey_tunic_material() -> StandardMaterial3D:
	var mat := StandardMaterial3D.new()
	mat.albedo_color = Color(0.52, 0.51, 0.50)
	mat.roughness = 0.95
	mat.metallic = 0.0
	return mat


func _dark_pants_material() -> StandardMaterial3D:
	var mat := StandardMaterial3D.new()
	mat.albedo_color = Color(0.20, 0.20, 0.22)
	mat.roughness = 0.95
	mat.metallic = 0.0
	return mat


## Cuir du harnais/ceinture/pochette — plus sombre que la tunique, plus
## clair que le pantalon, pour rester lisible comme une 3e zone distincte
## une fois quantifié (turnaround : sangles brunes bien visibles sur fond
## gris tunique).
func _leather_material() -> StandardMaterial3D:
	var mat := StandardMaterial3D.new()
	mat.albedo_color = Color(0.30, 0.26, 0.22)
	mat.roughness = 0.9
	mat.metallic = 0.0
	return mat


## Bottes — teinte intermédiaire (lanières enroulées, ni aussi sombre que
## le pantalon ni aussi clair que la tunique).
func _boot_material() -> StandardMaterial3D:
	var mat := StandardMaterial3D.new()
	mat.albedo_color = Color(0.42, 0.40, 0.37)
	mat.roughness = 0.95
	mat.metallic = 0.0
	return mat
