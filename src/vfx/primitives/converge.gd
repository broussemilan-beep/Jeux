extends Node2D
## Primitive "converge" — docs/ARCHITECTURE_VFX_v3.md §7.1 : "fragments
## qui reviennent vers une cible". L'inverse de shardBurst (qui PART de
## l'origine) : des fragments naissent sur un cercle autour de l'origine
## et VIENNENT s'y rassembler — la lecture "je rassemble une matière avant
## d'agir", utile à l'archétype de cast "canalisation" (mandat §5) même
## si aucun pouvoir concret ne l'utilise encore. Couche ANTICIPATION (§4).

const MIN_VALUE_HSV := 0.20
const MAX_VALUE_HSV := 0.92
const START_RADIUS_RATIO := 1.0  # rayon de départ des fragments, en unités de scale_px

var seed_val: int = 0
var lifetime_ticks: int = 12
var scale_px: float = 32.0
var origin: Vector2 = Vector2.ZERO
var fragment_count: int = 6
var _color: Color = Color.from_hsv(0.0, 0.0, 0.55, 1.0)

var _ticks_elapsed: int = 0
var _rng := RandomNumberGenerator.new()
var _start_positions: Array[Vector2] = []
var _sizes: Array[float] = []


func configure(params: Dictionary) -> void:
	seed_val = params.get("seed", 0)
	lifetime_ticks = maxi(1, int(params.get("lifetime_ticks", 12)))
	scale_px = params.get("scale_px", 32.0)
	origin = params.get("origin", Vector2.ZERO)
	position = origin
	# Même plafond que shardBurst (§8.2 : quelques fragments distincts,
	# jamais un système de particules GPU).
	fragment_count = clampi(int(params.get("count", 6)), 1, 16)
	z_index = 13  # ANTICIPATION : au-dessus de groundRing (10) — la matière se rassemble avant l'action.

	var value_pct: float = clampf(params.get("value_percent", 55.0), 0.0, 100.0) / 100.0
	var hue_deg: float = params.get("hue_deg", 0.0)
	var sat_pct: float = clampf(params.get("saturation_percent", 0.0), 0.0, 100.0) / 100.0
	var v: float = clampf(value_pct, MIN_VALUE_HSV, MAX_VALUE_HSV)
	_color = Color.from_hsv(hue_deg / 360.0, sat_pct, v, 1.0)

	_rng.seed = seed_val
	_start_positions.clear()
	_sizes.clear()
	for i in fragment_count:
		# Répartis tout autour de l'origine (360°) — "convergent", pas un
		# cône dirigé comme shardBurst/converge n'a pas de `direction`.
		var a: float = (TAU / float(fragment_count)) * i + _rng.randf() * 0.4
		var r: float = scale_px * START_RADIUS_RATIO * (0.8 + _rng.randf() * 0.4)
		_start_positions.append(Vector2(cos(a), sin(a)) * r)
		_sizes.append(2.0 + _rng.randf() * 2.5)


func tick(ticks_elapsed: int) -> void:
	_ticks_elapsed = ticks_elapsed
	queue_redraw()


func _draw() -> void:
	var t: float = clampf(float(_ticks_elapsed) / float(lifetime_ticks), 0.0, 1.0)
	# Accélère en approchant du centre (ease-in) — une convergence qui
	# "aspire" à la fin, pas une translation linéaire plate.
	var progress: float = t * t
	# S'efface juste avant d'atteindre le centre, jamais en plein vol —
	# la disparition se lit comme "absorbé", pas "éteint en chemin".
	var alpha: float = 1.0 - clampf((t - 0.85) / 0.15, 0.0, 1.0)
	if alpha <= 0.0:
		return
	var col := Color(_color.r, _color.g, _color.b, alpha)
	for i in fragment_count:
		var p: Vector2 = _start_positions[i].lerp(Vector2.ZERO, progress)
		var size_px: float = _sizes[i] * (1.0 - progress * 0.3)
		# Fragment anguleux (triangle) comme shardBurst — cohérence
		# visuelle "matière qui se fragmente", pas une particule ronde.
		var dir_to_center: Vector2 = (Vector2.ZERO - p).normalized() if p.length_squared() > 0.0001 else Vector2.RIGHT
		var perp: Vector2 = Vector2(-dir_to_center.y, dir_to_center.x) * size_px * 0.4
		var tip: Vector2 = p + dir_to_center * size_px
		var base_a: Vector2 = p - dir_to_center * size_px * 0.3 + perp
		var base_b: Vector2 = p - dir_to_center * size_px * 0.3 - perp
		draw_polygon(PackedVector2Array([tip, base_a, base_b]), PackedColorArray([col, col, col]))
