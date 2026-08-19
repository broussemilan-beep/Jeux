extends Node2D
## Primitive "arcSlash" — docs/ARCHITECTURE_VFX_v3.md §7.1 : "croissant
## anguleux directionnel". Couche CONTACT (§9.3) : un appui visuel bref
## sur un coup qui touche — la TRACE du geste, jamais le swing d'arme
## lui-même (ça, c'est l'animation du personnage). Pensée pour un usage
## très court (2 ticks typiquement, mandat combo Phase 1.4+ : "arc
## visuel bref sur 2 ticks" au coup 2).

const MIN_VALUE_HSV := 0.20
const MAX_VALUE_HSV := 0.92

## Ouverture angulaire de base du croissant (~100°) et ratio rayon
## intérieur/extérieur — un croissant "épais", pas un simple trait d'arc.
const BASE_SWEEP := PI * 0.55
const INNER_RATIO := 0.45
const SEGMENTS := 10

var seed_val: int = 0
var lifetime_ticks: int = 2
var scale_px: float = 28.0
var origin: Vector2 = Vector2.ZERO
var direction: Vector2 = Vector2.RIGHT
var _color: Color = Color.from_hsv(0.0, 0.0, 0.8, 1.0)
var _sweep_rad: float = BASE_SWEEP

var _ticks_elapsed: int = 0
var _rng := RandomNumberGenerator.new()


func configure(params: Dictionary) -> void:
	seed_val = params.get("seed", 0)
	lifetime_ticks = max(1, int(params.get("lifetime_ticks", 2)))
	scale_px = params.get("scale_px", 28.0)
	origin = params.get("origin", Vector2.ZERO)
	position = origin
	direction = params.get("direction", Vector2.RIGHT)
	if direction.length_squared() < 0.0001:
		direction = Vector2.RIGHT
	direction = direction.normalized()
	z_index = 95  # CONTACT : juste sous impactFlashFrame (100), au-dessus de fractureLine (90).

	var value_pct: float = clampf(params.get("value_percent", 80.0), 0.0, 100.0) / 100.0
	var hue_deg: float = params.get("hue_deg", 0.0)
	var sat_pct: float = clampf(params.get("saturation_percent", 0.0), 0.0, 100.0) / 100.0
	var v: float = clampf(value_pct, MIN_VALUE_HSV, MAX_VALUE_HSV)
	_color = Color.from_hsv(hue_deg / 360.0, sat_pct, v, 1.0)

	# Seedé (§13.4) pour une légère variation d'ouverture d'un coup à
	# l'autre, jamais identique au pixel près — mais jamais assez pour
	# changer la lecture "croissant directionnel".
	_rng.seed = seed_val
	_sweep_rad = BASE_SWEEP * (0.85 + _rng.randf() * 0.3)


func tick(ticks_elapsed: int) -> void:
	_ticks_elapsed = ticks_elapsed
	queue_redraw()


func _draw() -> void:
	var t: float = float(_ticks_elapsed) / float(lifetime_ticks)
	# Net dès le premier tick, s'efface vite — un appui bref, pas une
	# traînée qui persiste (ça, c'est ribbonTrail).
	var alpha: float = 1.0 - clampf(t, 0.0, 1.0)
	if alpha <= 0.0:
		return
	var col := Color(_color.r, _color.g, _color.b, alpha)

	var facing_angle: float = direction.angle()
	var outer: float = scale_px
	var inner: float = scale_px * INNER_RATIO
	var points := PackedVector2Array()
	for i in range(SEGMENTS + 1):
		var a: float = facing_angle - _sweep_rad * 0.5 + _sweep_rad * (float(i) / SEGMENTS)
		points.append(Vector2(cos(a), sin(a)) * outer)
	for i in range(SEGMENTS + 1):
		var a: float = facing_angle + _sweep_rad * 0.5 - _sweep_rad * (float(i) / SEGMENTS)
		points.append(Vector2(cos(a), sin(a)) * inner)
	var colors := PackedColorArray()
	colors.resize(points.size())
	colors.fill(col)
	draw_polygon(points, colors)
