extends Node2D
## Primitive "fractureLine" — docs/ARCHITECTURE_VFX_v3.md §7.1 :
## "fissure segmentée qui progresse". Couche CONTACT/CONSEQUENCE typique
## (§9.3) : contrairement à runicStamp (statique une fois apparu), cette
## primitive RÉVÈLE progressivement ses segments tick après tick — elle
## "progresse", elle n'apparaît pas d'un coup.

const MIN_VALUE_HSV := 0.20
const MAX_VALUE_HSV := 0.92

var seed_val: int = 0
var lifetime_ticks: int = 6
var length_px: float = 32.0
var direction: Vector2 = Vector2.RIGHT
var origin: Vector2 = Vector2.ZERO
var _color: Color = Color.from_hsv(0.0, 0.0, 0.24, 1.0)

var _ticks_elapsed: int = 0
var _rng := RandomNumberGenerator.new()
var _points: Array[Vector2] = []

const SEGMENT_COUNT := 7


func configure(params: Dictionary) -> void:
	seed_val = params.get("seed", 0)
	lifetime_ticks = max(1, int(params.get("lifetime_ticks", 6)))
	length_px = params.get("scale_px", 32.0)
	direction = params.get("direction", Vector2.RIGHT)
	if direction.length_squared() < 0.0001:
		direction = Vector2.RIGHT
	direction = direction.normalized()
	origin = params.get("origin", Vector2.ZERO)
	position = origin
	z_index = 90  # CONTACT : juste sous impactFlashFrame (100), au-dessus de CORE (20).

	var value_pct: float = clampf(params.get("value_percent", 24.0), 0.0, 100.0) / 100.0
	var hue_deg: float = params.get("hue_deg", 0.0)
	var sat_pct: float = clampf(params.get("saturation_percent", 0.0), 0.0, 100.0) / 100.0
	var v: float = clampf(value_pct, MIN_VALUE_HSV, MAX_VALUE_HSV)
	_color = Color.from_hsv(hue_deg / 360.0, sat_pct, v, 1.0)

	# Chemin en zigzag seedé (reproductible, §13.4), perpendiculaire à
	# `direction` pour le jitter — jamais une ligne droite (ce serait
	# beamSegment, pas fractureLine).
	_rng.seed = seed_val
	var perp := Vector2(-direction.y, direction.x)
	_points.clear()
	_points.append(Vector2.ZERO)
	for i in range(1, SEGMENT_COUNT + 1):
		var along: float = length_px * (float(i) / SEGMENT_COUNT)
		var jitter: float = (_rng.randf() - 0.5) * length_px * 0.18
		_points.append(direction * along + perp * jitter)


func tick(ticks_elapsed: int) -> void:
	_ticks_elapsed = ticks_elapsed
	queue_redraw()


func _draw() -> void:
	var t: float = float(_ticks_elapsed) / float(lifetime_ticks)
	# Progression : le nombre de segments visibles croît avec le temps.
	var visible_segments: int = int(ceil(t * SEGMENT_COUNT))
	visible_segments = clampi(visible_segments, 0, SEGMENT_COUNT)
	if visible_segments <= 0:
		return
	var alpha: float = 1.0 - clampf((t - 0.8) / 0.2, 0.0, 1.0)  # fade sur les 20% finaux
	var col := Color(_color.r, _color.g, _color.b, alpha)
	for i in visible_segments:
		draw_line(_points[i], _points[i + 1], col, 2.0)
