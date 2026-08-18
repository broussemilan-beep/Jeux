extends CharacterBody2D
class_name Player
## Personnage jouable minimal — mouvement 8 directions + stats. Pas
## d'animation ici (Phase 1.3, idle/déplacement/dash/hurt/mort viendront
## remplacer le Sprite2D statique par un AnimationPlayer/AnimatedSprite2D
## sur ce même nœud) et pas de combo (Phase 1.4).
##
## Entrée : actions UI par défaut de Godot (ui_left/right/up/down, liées
## aux flèches par défaut) plutôt qu'un input map dédié — aucune exigence
## de contrôles réels dans le mandat Phase 1 (touche tactile, remap, etc.
## sont hors scope ici), et ce choix évite d'éditer project.godot pour un
## mapping qui sera de toute façon revu quand l'UI/contrôles arriveront.

@export var stats: Stats = Stats.new()

## Direction de face courante (8 valeurs), utile aux futures frames
## directionnelles PixelLab (Phase 1.3) — mis à jour uniquement quand il y
## a un mouvement réel, jamais remis à zéro à l'arrêt (le perso garde sa
## dernière orientation, comme la convention 8-directions PixelLab).
var facing: Vector2 = Vector2.DOWN


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


func is_dead() -> bool:
	return stats.is_dead()
