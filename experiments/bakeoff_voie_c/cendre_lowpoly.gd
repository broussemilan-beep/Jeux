extends Node3D
## Bake-off Animation, Voie C — proxy 3D low-poly de Cendre, construit par
## primitives (pas de modélisation main/outil externe : aucun outil de
## génération 3D n'est accessible depuis cet environnement — ni MCP dédié
## (Meshy/Tripo/etc., recherchés et absents), ni Blender en CLI (vérifié,
## absent). Fallback explicitement sanctionné par le mandat : "le design
## du perso... est volontairement favorable à un modèle low-poly simple
## si besoin de le construire à la main/par script."
##
## Volumes et teintes calqués sur le turnaround v3 (assets/source/pixellab/
## cendre/reference_v3_turnaround_raw.png, sans cape) : crâne lisse pâle,
## tunique grise, pantalon/gants sombres — masses simples, pas de détail
## fin (harnais/sangles/lanières ignorés : hors de portée d'un proxy
## primitive, et de toute façon invisibles à 64×64 après quantification).

const HEAD_RADIUS := 0.11
const TORSO_RADIUS := 0.20
const TORSO_HEIGHT := 0.30
const LEG_RADIUS := 0.085
const LEG_HEIGHT := 0.62
const ARM_RADIUS := 0.065
const ARM_HEIGHT := 0.46
const NECK_GAP := 0.02

## Hauteur totale du personnage (pieds a sommet du crane), en unites Godot
## — sert au calcul de cadrage de la camera orthogonale (voir capture_idle.gd).
var total_height: float = 0.0


func _ready() -> void:
	var leg_top: float = LEG_HEIGHT
	var torso_bottom: float = leg_top
	var torso_top: float = torso_bottom + TORSO_HEIGHT
	var head_center_y: float = torso_top + NECK_GAP + HEAD_RADIUS
	total_height = head_center_y + HEAD_RADIUS

	_add_capsule("LegLeft", LEG_RADIUS, LEG_HEIGHT, Vector3(-0.11, leg_top * 0.5, 0.0), _dark_pants_material())
	_add_capsule("LegRight", LEG_RADIUS, LEG_HEIGHT, Vector3(0.11, leg_top * 0.5, 0.0), _dark_pants_material())
	_add_capsule("Torso", TORSO_RADIUS, TORSO_HEIGHT, Vector3(0.0, torso_bottom + TORSO_HEIGHT * 0.5, 0.0), _grey_tunic_material())
	_add_capsule("ArmLeft", ARM_RADIUS, ARM_HEIGHT, Vector3(-(TORSO_RADIUS + ARM_RADIUS + 0.01), torso_top - ARM_HEIGHT * 0.55, 0.0), _grey_tunic_material())
	_add_capsule("ArmRight", ARM_RADIUS, ARM_HEIGHT, Vector3(TORSO_RADIUS + ARM_RADIUS + 0.01, torso_top - ARM_HEIGHT * 0.55, 0.0), _grey_tunic_material())
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


## Valeurs HSV visées dans la fourchette "character" (data/palettes/
## value_bands.json, V dans [15,90]%) — matériaux volontairement mats
## (roughness haut, metallic 0) : GDD §2 "palette désaturée... NO GLOW,
## NO MAGIC LIGHT EFFECTS" s'applique aussi au proxy, pas seulement au
## pixel art final.
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
	mat.albedo_color = Color(0.22, 0.22, 0.24)
	mat.roughness = 0.95
	mat.metallic = 0.0
	return mat
