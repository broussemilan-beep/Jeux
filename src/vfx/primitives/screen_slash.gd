extends Node2D
## Primitive "screenSlash" — docs/ARCHITECTURE_VFX_v3.md §7.1 : "coupe
## écran locale/flash directionnel limité". LOCALE malgré le nom : ceci
## reste un Node2D borné dans l'espace comme toute autre primitive de
## cette liste, JAMAIS une passe de post-render plein écran (§10 : une
## seule passe globale/frame pour heatDistort/screenSlice/emissiveBloom,
## et ce budget n'est pas pour cette primitive — screenSlash est la
## silhouette d'un coup plus lourd, pas un shader). Une lame fine et
## longue qui traverse `direction`, plus longue et plus nette qu'arcSlash
## (croissant courbe) — réservée aux coups les plus lourds (tier 3+,
## boss) où le mandat §9 demande un signal visuel proportionné à
## l'impact. Couche CONTACT (§4).

const MIN_VALUE_HSV := 0.20
const MAX_VALUE_HSV := 0.92
const WIDTH_RATIO := 0.06  # largeur de la lame vs. sa longueur — fine et nette, jamais un ruban épais

var seed_val: int = 0
var lifetime_ticks: int = 3
var scale_px: float = 70.0  # longueur totale de la lame
var origin: Vector2 = Vector2.ZERO
var direction: Vector2 = Vector2.RIGHT
var _color: Color = Color.from_hsv(0.0, 0.0, 0.85, 1.0)

var _ticks_elapsed: int = 0
var _rng := RandomNumberGenerator.new()
var _angle_jitter: float = 0.0


func configure(params: Dictionary) -> void:
	seed_val = params.get("seed", 0)
	lifetime_ticks = maxi(1, int(params.get("lifetime_ticks", 3)))
	scale_px = params.get("scale_px", 70.0)
	origin = params.get("origin", Vector2.ZERO)
	position = origin
	direction = params.get("direction", Vector2.RIGHT)
	if direction.length_squared() < 0.0001:
		direction = Vector2.RIGHT
	direction = direction.normalized()
	z_index = 98  # CONTACT : au-dessus d'impactStar (96), sous impactFlashFrame (100) — le coup le plus lourd de la bande CONTACT.

	var value_pct: float = clampf(params.get("value_percent", 85.0), 0.0, 100.0) / 100.0
	var hue_deg: float = params.get("hue_deg", 0.0)
	var sat_pct: float = clampf(params.get("saturation_percent", 0.0), 0.0, 100.0) / 100.0
	var v: float = clampf(value_pct, MIN_VALUE_HSV, MAX_VALUE_HSV)
	_color = Color.from_hsv(hue_deg / 360.0, sat_pct, v, 1.0)

	# Léger angle seedé (§13.4) — la lame ne tombe jamais exactement à
	# l'identique d'un coup lourd à l'autre.
	_rng.seed = seed_val
	_angle_jitter = (_rng.randf() - 0.5) * deg_to_rad(8.0)


func tick(ticks_elapsed: int) -> void:
	_ticks_elapsed = ticks_elapsed
	queue_redraw()


func _draw() -> void:
	var t: float = float(_ticks_elapsed) / float(lifetime_ticks)
	# Net et plein dès le premier tick, s'efface vite (comme arcSlash) —
	# un flash directionnel, pas une traînée qui persiste.
	var alpha: float = 1.0 - clampf(t, 0.0, 1.0)
	if alpha <= 0.0:
		return
	var col := Color(_color.r, _color.g, _color.b, alpha)

	var dir: Vector2 = direction.rotated(_angle_jitter)
	var perp: Vector2 = Vector2(-dir.y, dir.x)
	var half_len: float = scale_px * 0.5
	var half_w: float = scale_px * WIDTH_RATIO * 0.5
	# Losange effilé (pointes aux deux bouts) plutôt qu'un simple
	# rectangle — une lame, pas une barre.
	var points := PackedVector2Array([
		dir * -half_len,
		perp * half_w,
		dir * half_len,
		perp * -half_w,
	])
	var colors := PackedColorArray()
	colors.resize(points.size())
	colors.fill(col)
	draw_polygon(points, colors)
