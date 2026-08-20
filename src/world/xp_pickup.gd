extends Area2D
class_name XpPickup
## Loot/récompense (H3, GDD §11 : "loot/événement" / "récompense") — XP
## directe au contact, pas d'inventaire/objets : GDD §16 ("équipements,
## matériaux, compétences, fragments, consommables") reste explicitement
## "à préciser", H3 ne couvre que le squelette structurel de la Gate,
## pas le système de loot complet.

@export var xp_amount: float = 20.0

var _collected: bool = false


func _ready() -> void:
	body_entered.connect(_on_body_entered)


func _on_body_entered(body: Node) -> void:
	if _collected or not body.is_in_group("player"):
		return
	if body.has_method("is_dead") and body.is_dead():
		return
	_collected = true
	body.stats.add_xp(xp_amount)
	queue_free()
