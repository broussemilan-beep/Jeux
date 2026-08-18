extends Control
class_name VirtualJoystick
## Joystick tactile minimal — outil de test rapide (feel du combo/dash/
## Gueule Vide sur iPhone), pas le HUD final du jeu. Pilote les actions
## ui_left/right/up/down existantes via Input.action_press/release
## (strength), donc Player._handle_movement() n'a besoin d'aucun
## changement : il lit déjà Input.get_action_strength() sur ces 4 actions.
## Fonctionne aussi à la souris (drag) pour tester depuis un navigateur
## desktop avant l'export.

const RADIUS_PX := 50.0
const DEADZONE := 0.15

@onready var _base: Control = $Base
@onready var _knob: Control = $Base/Knob

var _active: bool = false
var _touch_index: int = -1


func _input(event: InputEvent) -> void:
	if event is InputEventScreenTouch:
		if event.pressed:
			if not _active and _base.get_global_rect().has_point(event.position):
				_active = true
				_touch_index = event.index
				_update(event.position)
		elif event.index == _touch_index:
			_release()
	elif event is InputEventScreenDrag:
		if _active and event.index == _touch_index:
			_update(event.position)
	elif event is InputEventMouseButton and event.button_index == MOUSE_BUTTON_LEFT:
		if event.pressed:
			if not _active and _base.get_global_rect().has_point(event.position):
				_active = true
				_update(event.position)
		elif _active:
			_release()
	elif event is InputEventMouseMotion and _active:
		_update(event.position)


func _update(screen_pos: Vector2) -> void:
	var center := _base.get_global_rect().position + _base.size / 2.0
	var offset: Vector2 = (screen_pos - center).limit_length(RADIUS_PX)
	_knob.position = _base.size / 2.0 + offset - _knob.size / 2.0
	_apply_axis(offset / RADIUS_PX)


func _release() -> void:
	_active = false
	_touch_index = -1
	_knob.position = _base.size / 2.0 - _knob.size / 2.0
	_apply_axis(Vector2.ZERO)


func _apply_axis(axis: Vector2) -> void:
	_set_dir("ui_left", maxf(0.0, -axis.x))
	_set_dir("ui_right", maxf(0.0, axis.x))
	_set_dir("ui_up", maxf(0.0, -axis.y))
	_set_dir("ui_down", maxf(0.0, axis.y))


func _set_dir(action: String, strength: float) -> void:
	if strength > DEADZONE:
		Input.action_press(action, strength)
	else:
		Input.action_release(action)
