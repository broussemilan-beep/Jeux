extends Area2D
class_name GateEntrance
## Porte de départ en Gate depuis l'Outpost (H4, GDD §20 : "Hub → choisir
## Gate → entrée"). Un seul choix de Gate existe à ce stade (Première Gate,
## H3) donc pas de sélection réelle ici — juste le déclenchement du
## changement de scène au contact du joueur.
##
## `_should_trigger()` isolée de `_on_body_entered()` : la première est pure
## (testable en boucle de smoke test), la seconde appelle
## `get_tree().change_scene_to_file()`, une opération réelle et destructive
## pour l'arbre de scène en cours — jamais invoquée depuis un test
## automatisé, seulement vérifiée visuellement/manuellement.

@export var target_gate_scene: String = "res://scenes/gameplay/gate_premiere.tscn"

var _triggered: bool = false


func _ready() -> void:
	body_entered.connect(_on_body_entered)


func _should_trigger(body: Node) -> bool:
	if _triggered or not body.is_in_group("player"):
		return false
	if body.has_method("is_dead") and body.is_dead():
		return false
	return true


func _on_body_entered(body: Node) -> void:
	if not _should_trigger(body):
		return
	_triggered = true
	get_tree().change_scene_to_file(target_gate_scene)
