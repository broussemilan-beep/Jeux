extends Node2D
## Primitive "groundRing" — docs/ARCHITECTURE_VFX_v3.md §7.1 :
## "anneau au sol cassé ou incomplet". Couche ANTICIPATION la plus
## fréquente (§9.3) : télégraphie une zone avant qu'un effet plus fort
## n'y arrive — jamais un cercle plein/fermé, ce serait un halo, pas un
## anneau.
##
## Contrat primitive (§7.1) : seed, palette (résolue en amont par
## VfxRecipeRegistry — cette primitive ne connaît que la couleur finale,
## jamais un palette_id brut), durée, direction, échelle, origine,
## overdraw_cost.

const MIN_VALUE_HSV := 0.20
const MAX_VALUE_HSV := 0.92

var seed_val: int = 0
var lifetime_ticks: int = 9
var radius_px: float = 24.0
var origin: Vector2 = Vector2.ZERO
var _color: Color = Color.from_hsv(0.0, 0.0, 0.5, 1.0)
var _gap_count: int = 3

var _ticks_elapsed: int = 0
var _rng := RandomNumberGenerator.new()
var _gap_angles: Array[float] = []


func configure(params: Dictionary) -> void:
	seed_val = params.get("seed", 0)
	lifetime_ticks = max(1, int(params.get("lifetime_ticks", 9)))
	radius_px = params.get("scale_px", 24.0)
	origin = params.get("origin", Vector2.ZERO)
	position = origin
	z_index = 10  # ANTICIPATION : sous CONTACT (impactFlashFrame=100), au-dessus du décor.

	var value_pct: float = clampf(params.get("value_percent", 50.0), 0.0, 100.0) / 100.0
	var hue_deg: float = params.get("hue_deg", 0.0)
	var sat_pct: float = clampf(params.get("saturation_percent", 0.0), 0.0, 100.0) / 100.0
	var v: float = clampf(value_pct, MIN_VALUE_HSV, MAX_VALUE_HSV)
	_color = Color.from_hsv(hue_deg / 360.0, sat_pct, v, 1.0)

	# "cassé ou incomplet" — seedé pour rester reproductible (§13.4) sans
	# jamais retomber sur un anneau plein (au moins 2 coupures).
	_rng.seed = seed_val
	_gap_count = 2 + (_rng.randi() % 2)
	_gap_angles.clear()
	for i in _gap_count:
		_gap_angles.append(_rng.randf() * TAU)


func tick(ticks_elapsed: int) -> void:
	_ticks_elapsed = ticks_elapsed
	queue_redraw()


func _draw() -> void:
	var t: float = float(_ticks_elapsed) / float(lifetime_ticks)
	# Grandit puis se fige — un anneau qui grandit sans fin lirait comme
	# une expansion infinie, pas une zone d'invocation fixe.
	var grow: float = min(1.0, t / 0.4)
	var r: float = radius_px * (0.5 + 0.5 * grow)
	var alpha: float = 1.0 - clampf((t - 0.7) / 0.3, 0.0, 1.0)  # fade sur les 30% finaux
	var col := Color(_color.r, _color.g, _color.b, alpha)

	const SEGMENTS := 48
	const GAP_WIDTH := 0.18  # radians, largeur de chaque coupure
	for i in SEGMENTS:
		var a0: float = (float(i) / SEGMENTS) * TAU
		var a1: float = (float(i + 1) / SEGMENTS) * TAU
		var in_gap := false
		for gap_a in _gap_angles:
			var d: float = abs(wrapf(a0 - gap_a, -PI, PI))
			if d < GAP_WIDTH:
				in_gap = true
				break
		if in_gap:
			continue
		draw_line(Vector2(cos(a0), sin(a0)) * r, Vector2(cos(a1), sin(a1)) * r, col, 2.0)
