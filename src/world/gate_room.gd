extends Node2D
class_name GateRoom
## Une salle de la Première Gate (H3, GDD §11 : "Entrée → combats →
## loot/événement → embranchement → Elite → repos → boss → récompense →
## sortie"). `requires_clear` verrouille la `Door` enfant tant que tous
## les ennemis DE CETTE SALLE (pas globalement — un ennemi d'une autre
## salle ne doit jamais bloquer/débloquer la mauvaise porte) ne sont pas
## morts. Ennemis attendus comme enfants directs d'un nœud "Enemies".

@export var requires_clear: bool = false

var _tracked_enemies: Array = []
var _door_open: bool = false


func _ready() -> void:
	if has_node("Enemies"):
		for child in get_node("Enemies").get_children():
			_tracked_enemies.append(child)
	if not requires_clear or _tracked_enemies.is_empty():
		_open_door()


func _physics_process(_delta: float) -> void:
	if not _door_open and requires_clear and _all_enemies_dead():
		_open_door()


func is_cleared() -> bool:
	return _door_open


func _all_enemies_dead() -> bool:
	for e in _tracked_enemies:
		if is_instance_valid(e) and not e.is_dead():
			return false
	return true


## La porte n'a besoin d'aucune animation d'ouverture pour cette tranche
## logique-avant-l'art (même précédent que G/H2) : la retirer suffit,
## collision ET visuel disparaissent ensemble puisqu'ils vivent sur le
## même nœud.
func _open_door() -> void:
	_door_open = true
	if has_node("Door"):
		get_node("Door").queue_free()
