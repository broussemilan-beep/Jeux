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
## AUCUNE est une exigence explicite du GDD, JAMAIS touchée par
## l'amendement Pouvoir/déblocage (règle GDD distincte, confirmée
## toujours valide par Milan — docs/worklog.md) : le "Pouvoir" tiré au
## hasard par run (RunState.active_power) est un concept SÉPARÉ, affiché
## dans son propre champ juste en dessous (_pouvoir_label), jamais fondu
## dans la ligne CLASSE. COMPÉTENCES : reflète maintenant dynamiquement
## les emplacements réellement débloqués+implémentés du Pouvoir actif
## (Player.get_power_slot_info(), même source que touch_controls.gd/
## hud.gd) — l'ancien texte statique "E — Gueule Vide\nR — Bras-Faux"
## était déjà obsolète avant cet amendement (oubliait Poing Belluaire/
## Poing Tellurique) et n'a plus de sens du tout maintenant que power1-4
## ne sont plus des identités figées. ÉQUIPEMENT : les 4 catégories du
## GDD §16 (arme/tenue/accessoires/reliques), toutes vides — aucun
## système de loot n'existe encore ("Boutique/craft/déblocages : à
## préciser", GDD §16), afficher un objet inventé serait pire que rien
## afficher.

## Touches physiques réelles de power1..power5 (project.godot) — dans
## cet ordre, pour l'affichage seulement, jamais utilisées pour lire
## l'input.
const POWER_SLOT_KEYS := ["E", "R", "T", "G", "H"]

@onready var _player: Player = get_tree().get_first_node_in_group("player")
@onready var _panel: Control = $Panel
@onready var _stats_label: Label = $Panel/StatsLabel
@onready var _pouvoir_label: Label = $Panel/PouvoirLabel
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

	var active_power: String = ""
	if has_node("/root/RunState"):
		active_power = get_node("/root/RunState").active_power
	_pouvoir_label.text = "POUVOIR : %s" % active_power.capitalize()

	var skill_lines := PackedStringArray()
	for slot_index in range(1, POWER_SLOT_KEYS.size() + 1):
		var info: Dictionary = _player.get_power_slot_info(slot_index)
		if info.is_empty():
			continue
		skill_lines.append("%s — %s" % [POWER_SLOT_KEYS[slot_index - 1], info.get("name", "")])
	_skills_label.text = (
		"COMPÉTENCES\n" + "\n".join(skill_lines) if not skill_lines.is_empty() else "COMPÉTENCES\n(aucune débloquée)"
	)

	_equipment_label.text = "ÉQUIPEMENT\nArme : —\nTenue : —\nAccessoire : —\nRelique : —"


func is_open() -> bool:
	return _open
