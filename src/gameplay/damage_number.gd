extends Node2D
## Chiffre de dégâts flottant (mandat production v1 §4, HitResponse :
## "chiffre de dégâts poolé (police pixel, monte et s'efface ~20 ticks)").
##
## Police : le thème par défaut de Godot (`ThemeDB.fallback_font`), PAS
## une police pixel dédiée — aucun asset de police n'a été fourni pour ce
## HUD (même discipline que le reste du projet : ne jamais fabriquer un
## asset non fourni). Limite connue, signalée ici plutôt que cachée ; à
## remplacer dès qu'une police pixel arrive (§17 UI, hors scope J1).
##
## "poolé" : instances créées une fois par HitResponse (voir sa pool),
## jamais recréées par hit — activate() réinitialise l'état d'une
## instance existante. Ticks purs (pas un Tween temps réel) : ce nœud
## consulte lui-même CombatFeedback.is_frozen(), comme tout nœud de
## combat du projet, pour ne jamais dériver pendant un hit-stop.

const LIFETIME_TICKS := 20
const RISE_PX := 18.0
const FONT_SIZE := 14

var _ticks_elapsed: int = -1  # -1 = inactif, invisible, hors cycle
var _amount: float = 0.0
var _color: Color = Color.WHITE
var _origin: Vector2 = Vector2.ZERO


func _ready() -> void:
	visible = false


func activate(amount: float, world_pos: Vector2, color: Color) -> void:
	_amount = amount
	_color = color
	_origin = world_pos
	_ticks_elapsed = 0
	global_position = world_pos
	visible = true
	queue_redraw()


func is_active() -> bool:
	return _ticks_elapsed >= 0


func _physics_process(_delta: float) -> void:
	if _ticks_elapsed < 0:
		return
	if CombatFeedback.is_frozen():
		return
	_ticks_elapsed += 1
	if _ticks_elapsed >= LIFETIME_TICKS:
		_ticks_elapsed = -1
		visible = false
		return
	var t: float = float(_ticks_elapsed) / float(LIFETIME_TICKS)
	global_position = _origin + Vector2(0.0, -RISE_PX * t)
	queue_redraw()


func _draw() -> void:
	if _ticks_elapsed < 0:
		return
	var t: float = float(_ticks_elapsed) / float(LIFETIME_TICKS)
	var alpha: float = 1.0 - clampf((t - 0.6) / 0.4, 0.0, 1.0)  # fade sur les 40% finaux, meme forme que shard_burst.gd
	var font: Font = ThemeDB.fallback_font
	var text: String = str(int(round(_amount)))
	var col := Color(_color.r, _color.g, _color.b, alpha)
	var size := font.get_string_size(text, HORIZONTAL_ALIGNMENT_CENTER, -1, FONT_SIZE)
	draw_string(font, Vector2(-size.x / 2.0, 0.0), text, HORIZONTAL_ALIGNMENT_CENTER, -1, FONT_SIZE, col)
