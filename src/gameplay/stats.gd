extends Resource
class_name Stats
## Bloc de stats minimal partagé par Player et Enemy. Volontairement plat —
## rien ici que la tranche verticale Phase 1 n'exige déjà (INT, requis par
## le scaling de dégâts du Totem du Vide ; pas de force/dex/résistances
## tant qu'aucune recette/pouvoir ne les consomme réellement, §5.1
## "aucun appel PixelLab pour une variation que le runtime peut dériver
## d'une forme existante" — même discipline appliquée ici au code : pas de
## stat non exercée).

@export var max_hp: float = 100.0
@export var hp: float = max_hp
@export var int_stat: float = 10.0
@export var move_speed_px: float = 100.0

signal died


func apply_damage(amount: float) -> void:
	if amount <= 0.0 or is_dead():
		return
	hp = max(0.0, hp - amount)
	if is_dead():
		died.emit()


func is_dead() -> bool:
	return hp <= 0.0
