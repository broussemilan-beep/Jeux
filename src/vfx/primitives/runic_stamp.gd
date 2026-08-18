extends Node2D
## Primitive "runicStamp" — docs/ARCHITECTURE_VFX_v3.md §7.1 :
## "glyphe/empreinte de sol". Couche ACTION CORE typique (§9.3) : le motif
## d'identité visuelle d'un pouvoir, statique une fois apparu (contraste
## avec fractureLine qui progresse activement).

const MIN_VALUE_HSV := 0.20
const MAX_VALUE_HSV := 0.92

var seed_val: int = 0
var lifetime_ticks: int = 9
var scale_px: float = 20.0
var origin: Vector2 = Vector2.ZERO
var _color: Color = Color.from_hsv(0.0, 0.0, 0.55, 1.0)
var _spike_count: int = 5

var _ticks_elapsed: int = 0
var _rng := RandomNumberGenerator.new()
var _spike_lengths: Array[float] = []


func configure(params: Dictionary) -> void:
	seed_val = params.get("seed", 0)
	lifetime_ticks = max(1, int(params.get("lifetime_ticks", 9)))
	scale_px = params.get("scale_px", 20.0)
	origin = params.get("origin", Vector2.ZERO)
	position = origin
	z_index = 20  # ACTION CORE : au-dessus d'ANTICIPATION (groundRing=10).

	var value_pct: float = clampf(params.get("value_percent", 55.0), 0.0, 100.0) / 100.0
	var hue_deg: float = params.get("hue_deg", 0.0)
	var sat_pct: float = clampf(params.get("saturation_percent", 0.0), 0.0, 100.0) / 100.0
	var v: float = clampf(value_pct, MIN_VALUE_HSV, MAX_VALUE_HSV)
	_color = Color.from_hsv(hue_deg / 360.0, sat_pct, v, 1.0)

	_rng.seed = seed_val
	_spike_count = 5 + (_rng.randi() % 3)  # 5-7 branches, jamais un pentagramme identique partout
	_spike_lengths.clear()
	for i in _spike_count:
		_spike_lengths.append(0.6 + _rng.randf() * 0.4)  # longueur irrégulière par branche


func tick(ticks_elapsed: int) -> void:
	_ticks_elapsed = ticks_elapsed
	queue_redraw()


func _draw() -> void:
	var t: float = float(_ticks_elapsed) / float(lifetime_ticks)
	# Apparaît vite (empreinte "frappée" au sol), reste net, fade en fin
	# de vie — jamais un dessin qui se construit trait par trait (ça,
	# c'est fractureLine).
	var appear: float = min(1.0, t / 0.25)
	var fade: float = 1.0 - clampf((t - 0.75) / 0.25, 0.0, 1.0)
	var alpha: float = appear * fade
	var col := Color(_color.r, _color.g, _color.b, alpha)

	# Glyphe anguleux : cercle central + branches asymétriques, jamais un
	# symbole occulte lisse/circulaire parfait (matière "ink", §7.2 :
	# "masses irrégulières").
	draw_arc(Vector2.ZERO, scale_px * 0.25, 0.0, TAU, 16, col, 2.0)
	for i in _spike_count:
		var a: float = (float(i) / _spike_count) * TAU
		var len_px: float = scale_px * _spike_lengths[i]
		var dir := Vector2(cos(a), sin(a))
		draw_line(dir * scale_px * 0.2, dir * len_px, col, 1.5)
