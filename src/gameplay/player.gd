extends CharacterBody2D
class_name Player
## Personnage jouable minimal — mouvement 8 directions + stats + les 5
## animations de base (Phase 1.3 : idle/déplacement/dash/hurt/mort,
## `AnimatedSprite2D` + `SpriteFrames` cuits par
## scripts/cook_character_frames.py, direction sud uniquement pour
## l'instant — voir docs/worklog.md). Pas de combo (Phase 1.4).
##
## Entrée : actions UI par défaut de Godot (ui_left/right/up/down, liées
## aux flèches par défaut) plutôt qu'un input map dédié — aucune exigence
## de contrôles réels dans le mandat Phase 1 (touche tactile, remap, etc.
## sont hors scope ici), et ce choix évite d'éditer project.godot pour un
## mapping qui sera de toute façon revu quand l'UI/contrôles arriveront.

@export var stats: Stats = Stats.new()

## Direction de face courante (8 valeurs), utile aux futures frames
## directionnelles PixelLab (Phase 1.3+, 7 directions restantes) — mis à
## jour uniquement quand il y a un mouvement réel, jamais remis à zéro à
## l'arrêt (le perso garde sa dernière orientation).
var facing: Vector2 = Vector2.DOWN

## Verrouille l'animation de mouvement (idle/déplacement) pendant qu'une
## action ponctuelle (hurt/dash/mort) joue — sinon _physics_process
## écraserait la pose dès la frame suivante. Levé par
## _on_sprite_animation_finished(), jamais par un timer (durée réelle de
## l'animation, pas une estimation à côté).
var _action_lock: bool = false

@onready var _sprite: AnimatedSprite2D = $AnimatedSprite2D


func _ready() -> void:
	_sprite.animation_finished.connect(_on_sprite_animation_finished)


func _physics_process(_delta: float) -> void:
	var input_dir := Vector2(
		Input.get_action_strength("ui_right") - Input.get_action_strength("ui_left"),
		Input.get_action_strength("ui_down") - Input.get_action_strength("ui_up")
	)
	if input_dir.length_squared() > 1.0:
		input_dir = input_dir.normalized()

	velocity = input_dir * stats.move_speed_px
	if input_dir.length_squared() > 0.0001:
		facing = input_dir.normalized()

	move_and_slide()

	if not _action_lock and not stats.is_dead():
		_sprite.play("deplacement" if input_dir.length_squared() > 0.0001 else "idle")


func is_dead() -> bool:
	return stats.is_dead()


## Réaction à un coup subi — pas encore appelée par du vrai gameplay dans
## cette tranche verticale (aucun ennemi n'attaque le joueur, hors scope
## Phase 1), mais l'animation existe et le hook est prêt pour quand le
## combat réel arrivera.
func play_hurt() -> void:
	if stats.is_dead():
		return
	_action_lock = true
	_sprite.play("hurt")


func play_dash() -> void:
	if stats.is_dead() or _action_lock:
		return
	_action_lock = true
	_sprite.play("dash")


func _on_sprite_animation_finished() -> void:
	if _sprite.animation == "mort":
		return  # reste sur la dernière frame, jamais reverrouillé sur idle
	_action_lock = false


func die() -> void:
	stats.hp = 0.0
	_action_lock = true
	_sprite.play("mort")
