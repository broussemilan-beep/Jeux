extends Node2D
## Primitive "beamSegment" — docs/ARCHITECTURE_VFX_v3.md §7.1 : "rayon
## discret en segments". DISCRET par construction : une suite de blocs
## séparés par des espaces le long de `direction`, jamais un rayon
## continu plein — la forme principale attendue pour l'archétype de cast
## "projection avant" (mandat §5, encore sans exemple concret) : un tir
## qui part du joueur en ligne droite. Couche ACTION CORE (§4).

const MIN_VALUE_HSV := 0.20
const MAX_VALUE_HSV := 0.92
const SEGMENT_COUNT := 5
const GAP_RATIO := 0.35  # fraction de la longueur d'un segment laissée vide entre deux segments

var seed_val: int = 0
var lifetime_ticks: int = 8
var scale_px: float = 60.0  # longueur totale du rayon
var origin: Vector2 = Vector2.ZERO
var direction: Vector2 = Vector2.RIGHT
var _color: Color = Color.from_hsv(0.0, 0.0, 0.6, 1.0)
var _width_px: float = 6.0

var _ticks_elapsed: int = 0
var _rng := RandomNumberGenerator.new()
var _segment_jitter: Array[float] = []


func configure(params: Dictionary) -> void:
	seed_val = params.get("seed", 0)
	lifetime_ticks = maxi(1, int(params.get("lifetime_ticks", 8)))
	scale_px = params.get("scale_px", 60.0)
	_width_px = params.get("width_px", 6.0)
	origin = params.get("origin", Vector2.ZERO)
	position = origin
	direction = params.get("direction", Vector2.RIGHT)
	if direction.length_squared() < 0.0001:
		direction = Vector2.RIGHT
	direction = direction.normalized()
	z_index = 30  # ACTION CORE : au-dessus de spiral (25) — la forme d'un tir en ligne, pas un vortex.

	var value_pct: float = clampf(params.get("value_percent", 60.0), 0.0, 100.0) / 100.0
	var hue_deg: float = params.get("hue_deg", 0.0)
	var sat_pct: float = clampf(params.get("saturation_percent", 0.0), 0.0, 100.0) / 100.0
	var v: float = clampf(value_pct, MIN_VALUE_HSV, MAX_VALUE_HSV)
	_color = Color.from_hsv(hue_deg / 360.0, sat_pct, v, 1.0)

	# Léger bruit de largeur par segment (§13.4, seedé) — un rayon
	# "instable" plutôt que des blocs parfaitement identiques.
	_rng.seed = seed_val
	_segment_jitter.clear()
	for i in SEGMENT_COUNT:
		_segment_jitter.append(0.85 + _rng.randf() * 0.3)


func tick(ticks_elapsed: int) -> void:
	_ticks_elapsed = ticks_elapsed
	queue_redraw()


func _draw() -> void:
	var t: float = clampf(float(_ticks_elapsed) / float(lifetime_ticks), 0.0, 1.0)
	# Le rayon s'étend depuis l'origine sur les premiers 40% de sa durée
	# de vie (le tir "part"), reste plein, puis s'efface sur les 30%
	# finaux (le tir se dissipe) — jamais présent à pleine longueur dès le
	# tick 0.
	var extend_t: float = clampf(t / 0.4, 0.0, 1.0)
	var alpha: float = 1.0 - clampf((t - 0.7) / 0.3, 0.0, 1.0)
	if alpha <= 0.0 or extend_t <= 0.0:
		return
	var col := Color(_color.r, _color.g, _color.b, alpha)
	var perp := Vector2(-direction.y, direction.x)
	var unit_len: float = (scale_px / float(SEGMENT_COUNT)) * (1.0 - GAP_RATIO)
	var gap_len: float = (scale_px / float(SEGMENT_COUNT)) * GAP_RATIO
	var current_length: float = scale_px * extend_t

	var dist: float = 0.0
	for i in SEGMENT_COUNT:
		var seg_start: float = dist
		var seg_end: float = dist + unit_len
		dist = seg_end + gap_len
		if seg_start >= current_length:
			break
		var visible_end: float = minf(seg_end, current_length)
		var half_w: float = _width_px * 0.5 * _segment_jitter[i]
		var p0: Vector2 = direction * seg_start - perp * half_w
		var p1: Vector2 = direction * visible_end - perp * half_w
		var p2: Vector2 = direction * visible_end + perp * half_w
		var p3: Vector2 = direction * seg_start + perp * half_w
		var colors := PackedColorArray([col, col, col, col])
		draw_polygon(PackedVector2Array([p0, p1, p2, p3]), colors)
