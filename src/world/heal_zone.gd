extends Area2D
class_name HealZone
## Salle "repos" (H3, GDD §11) — interprétation délibérée du mot lui-même
## plutôt qu'un couloir vide entre Elite et boss : soin complet au
## contact, une seule fois, rien de plus (pas de nouvelle ressource ni
## de mécanique de camp inventée au-delà de ce que "repos" implique déjà
## — à reconsidérer si Milan le juge hors-scope ou insuffisant).

var _used: bool = false


func _ready() -> void:
	body_entered.connect(_on_body_entered)


func _on_body_entered(body: Node) -> void:
	if _used or not body.is_in_group("player"):
		return
	if body.has_method("is_dead") and body.is_dead():
		return
	_used = true
	body.stats.hp = body.stats.max_hp
