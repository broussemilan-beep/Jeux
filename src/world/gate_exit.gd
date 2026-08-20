extends Area2D
class_name GateExit
## Sortie de Gate (H3, GDD §11/§20 : "sortie" -> "retour" au Hub). L'Outpost
## et la boucle de run complète (Hub → Gate → ... → retour) sont H4, pas
## cette brique — ce marqueur signale juste la fin de la Gate de façon
## observable (un signal, câblable par H4), sans inventer de transition
## vers un hub qui n'existe pas encore.

signal gate_completed

var _triggered: bool = false


func _ready() -> void:
	body_entered.connect(_on_body_entered)


func _on_body_entered(body: Node) -> void:
	if _triggered or not body.is_in_group("player"):
		return
	_triggered = true
	gate_completed.emit()
