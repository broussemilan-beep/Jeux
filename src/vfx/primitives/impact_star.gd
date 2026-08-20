extends Node2D
## Primitive "impactStar" — docs/ARCHITECTURE_VFX_v3.md §7.1 : "étoile/éclat
## central asymétrique". §9.3 étape 2 : "silhouette secondaire" affichée
## juste APRÈS impactFlashFrame — distincte de lui (§4 : "Distincte
## d'impactStar") — le flash est un disque plein neutre, cette primitive
## est la forme dentelée qui reste une fois le flash retombé. Couche
## CONTACT (§4).
##
## Asymétrique par construction (§7.1) : les branches n'ont ni longueur ni
## angle uniformes — un éclat qui a l'air d'avoir été frappé, pas un motif
## d'étoile générique répété partout.

const MIN_VALUE_HSV := 0.20
const MAX_VALUE_HSV := 0.92
const SPIKE_COUNT_MIN := 5
const SPIKE_COUNT_MAX := 7
const INNER_RATIO := 0.35  # rayon du creux entre deux branches, vs. rayon de branche

var seed_val: int = 0
var lifetime_ticks: int = 4
var scale_px: float = 22.0
var origin: Vector2 = Vector2.ZERO
var _color: Color = Color.from_hsv(0.0, 0.0, 0.75, 1.0)

var _ticks_elapsed: int = 0
var _rng := RandomNumberGenerator.new()
var _spike_lengths: Array[float] = []
var _spike_angles: Array[float] = []


func configure(params: Dictionary) -> void:
	seed_val = params.get("seed", 0)
	lifetime_ticks = maxi(1, int(params.get("lifetime_ticks", 4)))
	scale_px = params.get("scale_px", 22.0)
	origin = params.get("origin", Vector2.ZERO)
	position = origin
	z_index = 96  # CONTACT : au-dessus d'arcSlash (95), sous impactFlashFrame (100) — la silhouette qui suit le flash.

	var value_pct: float = clampf(params.get("value_percent", 75.0), 0.0, 100.0) / 100.0
	var hue_deg: float = params.get("hue_deg", 0.0)
	var sat_pct: float = clampf(params.get("saturation_percent", 0.0), 0.0, 100.0) / 100.0
	var v: float = clampf(value_pct, MIN_VALUE_HSV, MAX_VALUE_HSV)
	_color = Color.from_hsv(hue_deg / 360.0, sat_pct, v, 1.0)

	_rng.seed = seed_val
	var spike_count: int = _rng.randi_range(SPIKE_COUNT_MIN, SPIKE_COUNT_MAX)
	_spike_lengths.clear()
	_spike_angles.clear()
	var base_angle_step: float = TAU / float(spike_count)
	for i in spike_count:
		# Angle ET longueur bruités indépendamment — deux branches voisines
		# ne se ressemblent jamais tout à fait (§7.1 "asymétrique").
		_spike_angles.append(base_angle_step * i + (_rng.randf() - 0.5) * base_angle_step * 0.5)
		_spike_lengths.append(scale_px * (0.55 + _rng.randf() * 0.45))


func tick(ticks_elapsed: int) -> void:
	_ticks_elapsed = ticks_elapsed
	queue_redraw()


func _draw() -> void:
	var t: float = float(_ticks_elapsed) / float(lifetime_ticks)
	var alpha: float = 1.0 - clampf(t, 0.0, 1.0)
	if alpha <= 0.0:
		return
	var col := Color(_color.r, _color.g, _color.b, alpha)
	var count: int = _spike_angles.size()
	if count == 0:
		return

	var points := PackedVector2Array()
	for i in count:
		var a_prev: float = _spike_angles[(i - 1 + count) % count]
		var a_cur: float = _spike_angles[i]
		var a_next: float = _spike_angles[(i + 1) % count]
		var inner_a: float = (a_prev + a_cur) * 0.5
		var tip: Vector2 = Vector2(cos(a_cur), sin(a_cur)) * _spike_lengths[i]
		var valley: Vector2 = Vector2(cos(inner_a), sin(inner_a)) * (_spike_lengths[i] * INNER_RATIO)
		points.append(valley)
		points.append(tip)
	var colors := PackedColorArray()
	colors.resize(points.size())
	colors.fill(col)
	draw_polygon(points, colors)
