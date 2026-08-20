extends Node
## Autoload "HitResponse" — mandat production v1 §4, système "HitResponse
## (côté cible)". Trois réactions déclenchées sur `take_damage()` par la
## cible touchée, jamais par l'attaquant (§4 GDD combat : "recul visible
## sur tout coup qui touche", même principe déjà appliqué au recul —
## c'est la cible qui réagit, pas une primitive de l'attaque) :
##   1. flash_sprite() : flash blanc 2 ticks (shader, jamais un remplacement
##      de texture).
##   2. spawn_damage_number() : chiffre de dégâts poolé, monte et s'efface.
##   3. spawn_death_response() : shardBurst teinté ennemi (ROUGE, §9 doc
##      VFX : "bleu allié / rouge ennemi, non contournable") + décal
##      persistant au sol.
##
## Le recul lui-même (existant) reste porté par Enemy.take_damage(), pas
## ici — ce fichier ne fait QUE la réaction visuelle, jamais la physique.

const FLASH_SHADER := preload("res://src/vfx/shaders/hit_flash.gdshader")
const DamageNumberScript := preload("res://src/gameplay/damage_number.gd")
const GroundDecalScript := preload("res://src/gameplay/ground_decal.gd")

const FLASH_TICKS := 2
const DAMAGE_NUMBER_POOL_SIZE := 16
const DEATH_BURST_HUE_DEG := 0.0            # rouge = ennemi (§9 doc VFX, non contournable)
const DEATH_BURST_SATURATION_PERCENT := 45.0
const DEATH_BURST_VALUE_PERCENT := 42.0
const DEATH_DECAL_COLOR := Color(0.12, 0.04, 0.04, 0.6)  # teinte "sang" desaturee, coherente palette rouge-ennemi
const DEATH_DECAL_RADIUS_PX := 9.0

## instance_id (du CanvasItem flashé) -> { node, ticks_remaining, material }
var _flashing: Dictionary = {}

## Pool de chiffres de dégâts (§4 : "poolé") — créés une fois, jamais par
## hit. `_pool_root` est un Node2D neutre attaché à cet autoload (pas à
## une scène de gameplay précise) pour que les nombres survivent aux
## changements de scène futurs comme n'importe quel autoload.
var _number_pool: Array[Node2D] = []
var _pool_root: Node2D
var _next_pool_index: int = 0


func _ready() -> void:
	_pool_root = Node2D.new()
	_pool_root.name = "DamageNumberPool"
	add_child(_pool_root)
	for i in DAMAGE_NUMBER_POOL_SIZE:
		var n := Node2D.new()
		n.set_script(DamageNumberScript)
		_pool_root.add_child(n)
		_number_pool.append(n)


func _physics_process(_delta: float) -> void:
	if CombatFeedback.is_frozen():
		return
	for instance_id in _flashing.keys().duplicate():
		var entry: Dictionary = _flashing[instance_id]
		# `is_instance_valid()` DOIT recevoir la valeur brute (Variant) —
		# assigner un Object déjà libéré (Enemy mort, `Placeholder` parti
		# avec lui) à une variable TYPÉE (`CanvasItem`) déclenche l'erreur
		# "Trying to assign invalid previously freed instance" AVANT même
		# que is_instance_valid() ait pu s'exécuter. Trouvé en relançant
		# run_gameplay_smoke_test.sh après avoir câblé HitResponse
		# (docs/worklog.md, mandat production v1 J1).
		var node_raw: Variant = entry["node"]
		if not is_instance_valid(node_raw):
			_flashing.erase(instance_id)
			continue
		var node: CanvasItem = node_raw
		entry["ticks_remaining"] -= 1
		if entry["ticks_remaining"] <= 0:
			node.material = entry["material"]
			_flashing.erase(instance_id)
		else:
			var mat: ShaderMaterial = node.material
			mat.set_shader_parameter("flash_amount", float(entry["ticks_remaining"]) / float(FLASH_TICKS))


## `target` : n'importe quel `CanvasItem` (AnimatedSprite2D, Polygon2D —
## le placeholder géométrique d'Enemy inclus, §4 mandat : "shader sur le
## sprite de la cible", un shader s'applique identiquement à une forme
## géométrique ou à un vrai sprite, aucune réécriture attendue quand
## l'art ennemi arrivera). Un flash déjà en cours sur la même cible est
## simplement relancé à pleine intensité (jamais additif ni ignoré —
## cohérent avec CombatFeedback.trigger_hitstop() : le MAX, pas une somme).
func flash_sprite(target: CanvasItem) -> void:
	if not is_instance_valid(target):
		return
	var instance_id: int = target.get_instance_id()
	var original_material: Material = null
	if _flashing.has(instance_id):
		original_material = _flashing[instance_id]["material"]
	else:
		original_material = target.material
	var mat := ShaderMaterial.new()
	mat.shader = FLASH_SHADER
	mat.set_shader_parameter("flash_amount", 1.0)
	target.material = mat
	_flashing[instance_id] = {
		"node": target,
		"ticks_remaining": FLASH_TICKS,
		"material": original_material,
	}


## `parent` : nœud auquel attacher le chiffre en espace MONDE (le parent
## de la cible touchée, typiquement — jamais l'autoload lui-même, qui n'a
## pas de position monde significative pour du gameplay ancré à une scène).
func spawn_damage_number(amount: float, world_pos: Vector2, parent: Node, color: Color = Color.WHITE) -> void:
	var node: Node2D = _number_pool[_next_pool_index]
	_next_pool_index = (_next_pool_index + 1) % _number_pool.size()
	if node.get_parent() != parent:
		node.get_parent().remove_child(node)
		parent.add_child(node)
	node.activate(amount, world_pos, color)


## shardBurst (CONSEQUENCE, degradable — une couche décorative de mort
## peut sauter sous pression de budget, contrairement au CONTACT
## impactFlashFrame déjà protégé ailleurs) + décal persistant. `parent` :
## nœud auquel attacher le décal (survit à la destruction de la cible,
## contrairement au shardBurst qui vit dans le container de VfxDirector).
func spawn_death_response(world_pos: Vector2, away_direction: Vector2, parent: Node) -> void:
	VfxDirector.spawn("shardBurst", {
		"seed": 0,
		"origin": world_pos,
		"direction": away_direction,
		"lifetime_ticks": 16,
		"count": 10,
		"speed_px_per_tick": 3.0,
		"hue_deg": DEATH_BURST_HUE_DEG,
		"saturation_percent": DEATH_BURST_SATURATION_PERCENT,
		"value_percent": DEATH_BURST_VALUE_PERCENT,
		"degradable": true,
	})
	GroundDecalScript.spawn(parent, world_pos, DEATH_DECAL_RADIUS_PX, DEATH_DECAL_COLOR)
