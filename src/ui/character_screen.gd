extends CanvasLayer
class_name CharacterScreen
## H5 (GDD §17 : "Écran personnage : NAME / RANK / LEVEL / FOR / AGI / INT
## / VIT / CLASS / SKILLS / EQUIPMENT. Rank Zero doit afficher CLASS =
## NONE et ne jamais recevoir une Classe inventée."). Panneau basculé par
## l'action "character_screen" (Tab clavier / bouton tactile "PERSO").
## Poll en _process() comme Hud (voir hud.gd) — un lecteur d'état, pas un
## propriétaire.
##
## NOM/RANG : "Rank Zero" est à la fois le titre du jeu et l'identité du
## protagoniste dans le GDD lui-même (§1/§3 : personnage sans nom propre,
## connu uniquement par son Rang) — pas un nom inventé ici. CLASSE =
## AUCUNE est une exigence explicite du GDD, jamais une Classe inventée.
## COMPÉTENCES : les deux emplacements actifs déjà câblés (power1 =
## Gueule Vide, power2 = Bras-Faux, voir player.gd) — aucun système de
## swap de loadout, hors scope de cette brique. ÉQUIPEMENT : les 4
## catégories du GDD §16 (arme/tenue/accessoires/reliques), toutes
## vides — aucun système de loot n'existe encore ("Boutique/craft/
## déblocages : à préciser", GDD §16), afficher un objet inventé serait
## pire que rien afficher.

@onready var _player: Player = get_tree().get_first_node_in_group("player")
@onready var _panel: Control = $Panel
@onready var _stats_label: Label = $Panel/StatsLabel
@onready var _skills_label: Label = $Panel/SkillsLabel
@onready var _equipment_label: Label = $Panel/EquipmentLabel

var _open: bool = false


func _process(_delta: float) -> void:
	if Input.is_action_just_pressed("character_screen"):
		_open = not _open
		_panel.visible = _open

	if not _open or _player == null or not is_instance_valid(_player):
		return

	var stats: Stats = _player.stats
	_stats_label.text = (
		"NOM : Rank Zero\nRANG : Zéro\nNIVEAU : %d\n\nFOR : %d\nAGI : %d\nINT : %d\nVIT : %d\n\nCLASSE : AUCUNE"
		% [stats.level, int(stats.for_stat), int(stats.agi_stat), int(stats.int_stat), int(stats.vit_stat)]
	)
	_skills_label.text = "COMPÉTENCES\nE — Gueule Vide\nR — Bras-Faux"
	_equipment_label.text = "ÉQUIPEMENT\nArme : —\nTenue : —\nAccessoire : —\nRelique : —"


func is_open() -> bool:
	return _open
