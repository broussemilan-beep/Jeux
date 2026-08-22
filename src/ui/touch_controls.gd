extends CanvasLayer
## Amendement GDD Pouvoir/déblocage (confirmé par Milan) : les 5 boutons
## ButtonPower1-5 ne sont plus des identités figées ("GV"/"BF"/"PB"/"PT")
## gravées dans la scène — ils reflètent maintenant, à chaque frame, le
## Pouvoir actif de la run + le niveau courant du joueur, via
## Player.get_power_slot_info(). Poll en _process(), même patron que
## hud.gd/character_screen.gd (un lecteur d'état, pas un propriétaire).
##
## Exigence explicite de Milan : un emplacement non débloqué doit être
## ABSENT, pas grisé — `visible = false`, pas une simple superposition
## sombre comme les overlays de cooldown du HUD.

@onready var _player: Player = get_tree().get_first_node_in_group("player")

@onready var _power_buttons: Array[TouchScreenButton] = [
	$ButtonPower1, $ButtonPower2, $ButtonPower3, $ButtonPower4, $ButtonPower5,
]


func _process(_delta: float) -> void:
	if _player == null or not is_instance_valid(_player):
		return
	for i in _power_buttons.size():
		var slot_index: int = i + 1
		var info: Dictionary = _player.get_power_slot_info(slot_index)
		var button: TouchScreenButton = _power_buttons[i]
		button.visible = not info.is_empty()
		if not info.is_empty():
			var label: Label = button.get_node("Label")
			label.text = info.get("touch_label", "")
