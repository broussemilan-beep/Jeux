extends Node2D
## Racine de la Première Gate (H4, GDD §20 : "... → retour"). Câble la
## sortie de la Gate (H3, `GateExit.gate_completed`) vers le retour à
## l'Outpost — la seule pièce manquante en H3, qui laissait volontairement
## `GateExit` non connectée (voir gate_exit.gd) faute d'Outpost à l'époque.

@onready var _exit: Area2D = $Exit


func _ready() -> void:
	_exit.gate_completed.connect(_on_gate_completed)


func _on_gate_completed() -> void:
	get_tree().change_scene_to_file("res://scenes/gameplay/outpost.tscn")
