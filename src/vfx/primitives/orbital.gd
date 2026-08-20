extends Node2D
## Primitive "orbital" — docs/ARCHITECTURE_VFX_v3.md §7.1 : "instances
## autour d'une ellipse seedée". Contrairement à spiral (aspiration, le
## rayon décroît vers le centre), orbital maintient une trajectoire
## elliptique STABLE sur toute sa durée de vie — la lecture "quelque
## chose orbite autour du personnage" (une garde, un buff actif, une
## invocation qui accompagne plutôt qu'attaque). Couche ACTION CORE (§4).

const MIN_VALUE_HSV := 0.20
const MAX_VALUE_HSV := 0.92
const ELLIPSE_RATIO := 0.55  # rayon vertical vs. horizontal — une ellipse "à plat" (perspective de jeu top-down/3-4), jamais un cercle

var seed_val: int = 0
var lifetime_ticks: int = 20
var scale_px: float = 26.0
var origin: Vector2 = Vector2.ZERO
var instance_count: int = 3
var _color: Color = Color.from_hsv(0.0, 0.0, 0.55, 1.0)

var _ticks_elapsed: int = 0
var _rng := RandomNumberGenerator.new()
var _phase_offsets: Array[float] = []
var _sizes: Array[float] = []
var _speed_mult: Array[float] = []


func configure(params: Dictionary) -> void:
	seed_val = params.get("seed", 0)
	lifetime_ticks = maxi(1, int(params.get("lifetime_ticks", 20)))
	scale_px = params.get("scale_px", 26.0)
	origin = params.get("origin", Vector2.ZERO)
	position = origin
	instance_count = clampi(int(params.get("count", 3)), 1, 8)
	z_index = 35  # ACTION CORE : au-dessus de beamSegment (30) — un accompagnement continu, pas un tir instantané.

	var value_pct: float = clampf(params.get("value_percent", 55.0), 0.0, 100.0) / 100.0
	var hue_deg: float = params.get("hue_deg", 0.0)
	var sat_pct: float = clampf(params.get("saturation_percent", 0.0), 0.0, 100.0) / 100.0
	var v: float = clampf(value_pct, MIN_VALUE_HSV, MAX_VALUE_HSV)
	_color = Color.from_hsv(hue_deg / 360.0, sat_pct, v, 1.0)

	_rng.seed = seed_val
	_phase_offsets.clear()
	_sizes.clear()
	_speed_mult.clear()
	for i in instance_count:
		_phase_offsets.append((TAU / float(instance_count)) * i)
		_sizes.append(3.0 + _rng.randf() * 2.0)
		# Léger désaccord de vitesse par instance — elles ne restent pas
		# parfaitement alignées tout du long, une lecture plus vivante.
		_speed_mult.append(0.9 + _rng.randf() * 0.2)


func tick(ticks_elapsed: int) -> void:
	_ticks_elapsed = ticks_elapsed
	queue_redraw()


func _draw() -> void:
	var t: float = clampf(float(_ticks_elapsed) / float(lifetime_ticks), 0.0, 1.0)
	# Entrée et sortie en fondu (10% chacune), plein régime au milieu —
	# une orbite qui s'installe et se retire, jamais un pop/disparition
	# brutale.
	var alpha_in: float = clampf(t / 0.1, 0.0, 1.0)
	var alpha_out: float = 1.0 - clampf((t - 0.9) / 0.1, 0.0, 1.0)
	var alpha: float = minf(alpha_in, alpha_out)
	if alpha <= 0.0:
		return
	var col := Color(_color.r, _color.g, _color.b, alpha)
	for i in instance_count:
		var angle: float = _phase_offsets[i] + TAU * _speed_mult[i] * t * 2.0
		var p := Vector2(cos(angle) * scale_px, sin(angle) * scale_px * ELLIPSE_RATIO)
		draw_circle(p, _sizes[i], col)
