extends CanvasLayer
class_name Hud
## HUD minimal (H1, GDD §17 : "PV, ressource si nécessaire, niveau, XP,
## compétences équipées, cooldowns, dash/esquive"). Pas de ressource
## secondaire pour l'instant — aucun pouvoir n'en consomme, "ressource si
## nécessaire" reste donc TBD. Poll en `_process()` plutôt qu'un signal
## par valeur : un HUD lit un état, il ne le possède pas, même discipline
## que VfxDirector/CombatFeedback (des singletons consultés, jamais des
## propriétaires qui poussent un événement à chaque UI intéressée).
## Dash n'a pas de cooldown chiffré par le mandat/GDD (contrairement à
## esquive/Gueule Vide/Bras-Faux) : son icône reste toujours "prête",
## sans overlay — inventer un cooldown non demandé serait hors mandat.

const ICON_SIZE := 26.0

@onready var _player: Player = get_tree().get_first_node_in_group("player")
@onready var _hp_fill: ColorRect = $HpBar/Fill
@onready var _hp_label: Label = $HpBar/Label
@onready var _level_label: Label = $LevelLabel
@onready var _xp_fill: ColorRect = $XpBar/Fill
@onready var _cd_dodge: ColorRect = $Cooldowns/Dodge/Overlay
## Mandat critique probabiliste : plein écran, jamais une simple
## variante plus lumineuse d'un effet existant — voir CombatFeedback.
## trigger_screen_flash()/get_screen_flash_color(), déclenché uniquement
## par Player._try_hit() sur un coup qui vient de rouler critique.
@onready var _screen_flash: ColorRect = $ScreenFlash

## Amendement GDD Pouvoir/déblocage (confirmé par Milan) : 5 emplacements
## génériques (plus 4 fixes) — chaque conteneur entier (pas seulement son
## overlay) est masqué quand Player.get_power_slot_info() est vide, pour
## qu'un emplacement non débloqué soit ABSENT, pas juste "grisé" (même
## exigence que touch_controls.gd).
@onready var _power_slots: Array[ColorRect] = [
	$Cooldowns/Power1, $Cooldowns/Power2, $Cooldowns/Power3, $Cooldowns/Power4, $Cooldowns/Power5,
]

const HP_BAR_WIDTH := 120.0
const XP_BAR_WIDTH := 120.0


func _process(_delta: float) -> void:
	if _player == null or not is_instance_valid(_player):
		return
	var stats: Stats = _player.stats

	var hp_ratio: float = clampf(stats.hp / max(1.0, stats.max_hp), 0.0, 1.0)
	_hp_fill.size.x = HP_BAR_WIDTH * hp_ratio
	_hp_label.text = "%d/%d" % [int(stats.hp), int(stats.max_hp)]
	_level_label.text = "Niv. %d" % stats.level

	var xp_ratio: float = clampf(stats.xp / max(1.0, stats.xp_to_next_level()), 0.0, 1.0)
	_xp_fill.size.x = XP_BAR_WIDTH * xp_ratio

	_set_cooldown_overlay(_cd_dodge, _player.get_dodge_cooldown_ratio())
	_screen_flash.color = CombatFeedback.get_screen_flash_color()

	for i in _power_slots.size():
		var slot_index: int = i + 1
		var info: Dictionary = _player.get_power_slot_info(slot_index)
		var container: ColorRect = _power_slots[i]
		container.visible = not info.is_empty()
		if info.is_empty():
			continue
		var label: Label = container.get_node("Label")
		label.text = info.get("touch_label", "")
		var overlay: ColorRect = container.get_node("Overlay")
		_set_cooldown_overlay(overlay, _player.get_power_slot_cooldown_ratio(slot_index))


## `ratio` 1.0 = vient d'être utilisé (icône entièrement voilée) -> 0.0 =
## prêt (aucun voile). Le voile rétrécit et descend vers le bas au fil
## du cooldown — balayage vertical classique, pas une simple visibilité
## on/off qui ne communiquerait pas "combien de temps encore".
func _set_cooldown_overlay(overlay: ColorRect, ratio: float) -> void:
	var covered_height: float = ICON_SIZE * clampf(ratio, 0.0, 1.0)
	overlay.position.y = ICON_SIZE - covered_height
	overlay.size.y = covered_height
