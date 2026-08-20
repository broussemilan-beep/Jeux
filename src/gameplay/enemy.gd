extends CharacterBody2D
class_name Enemy
## Ennemi minimal pour la tranche verticale Phase 1 — stationnaire, sans IA
## (hors scope de ce document, §1/§16.6). Son seul rôle ici est d'être une
## cible valide pour Targeting.nearest_enemy_in_radius() et de porter la
## réaction `recoil` (doc VFX §4, §9.3 point 4 : "recul visible de la
## cible... pas une primitive du pouvoir qui la touche, une réaction de
## l'ennemi").

@export var stats: Stats = Stats.new()

var _recoil_ticks_remaining: int = 0
var _recoil_velocity: Vector2 = Vector2.ZERO

signal hit(amount: float)

## Nœud visuel de la cible — `Placeholder` (Polygon2D géométrique) pour
## l'instant, mandat production v1 §4 : "shader sur le sprite de la
## cible" s'applique identiquement à cette forme géométrique, aucune
## réécriture attendue le jour où un vrai sprite ennemi (G, GDD §10)
## remplace ce placeholder.
@onready var _visual: CanvasItem = $Placeholder


func _ready() -> void:
	add_to_group("enemies")


func _physics_process(_delta: float) -> void:
	if CombatFeedback.is_frozen():
		return
	if _recoil_ticks_remaining > 0:
		_recoil_ticks_remaining -= 1
		velocity = _recoil_velocity
		_recoil_velocity = _recoil_velocity.move_toward(Vector2.ZERO, _recoil_velocity.length() / max(1, _recoil_ticks_remaining + 1))
		move_and_slide()


func is_dead() -> bool:
	return stats.is_dead()


## `source_position` sert à orienter le recul (toujours opposé à l'attaque,
## jamais isotrope — §4 : "jamais un bruit isotrope"). `damage` peut être 0
## pour un recul sans dégâts (pas de cas connu aujourd'hui, mais la
## signature reste correcte pour ça).
func take_damage(amount: float, source_position: Vector2, recoil_strength_px: float = 24.0, recoil_ticks: int = 6) -> void:
	if is_dead():
		return
	stats.apply_damage(amount)
	hit.emit(amount)
	var away: Vector2 = (global_position - source_position)
	if away.length_squared() < 0.0001:
		away = Vector2.RIGHT
	away = away.normalized()
	_recoil_velocity = away * (recoil_strength_px * Engine.physics_ticks_per_second / max(1, recoil_ticks))
	_recoil_ticks_remaining = recoil_ticks

	# HitResponse (mandat production v1 §4) : flash + chiffre de dégâts sur
	# TOUT coup qui touche, avant le early-return de mort ci-dessous — la
	# cible qui meurt doit quand même flasher/afficher son dernier chiffre,
	# jamais les sauter silencieusement.
	HitResponse.flash_sprite(_visual)
	HitResponse.spawn_damage_number(amount, global_position, get_parent())

	if is_dead():
		HitResponse.spawn_death_response(global_position, away, get_parent())
		queue_free()
