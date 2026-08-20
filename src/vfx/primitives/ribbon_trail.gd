extends Node2D
## Primitive "ribbonTrail" — docs/ARCHITECTURE_VFX_v3.md §7.1 : "ruban de
## vitesse contrôlé par vélocité". Contrairement à arcSlash (un croissant
## déjà formé, un appui bref et STATIQUE sur un coup qui touche), ce
## ruban TRACE un mouvement : il balaie un arc de `sweep_deg` autour de
## `direction` sur toute sa durée de vie, et garde en mémoire un
## historique court de positions passées pour dessiner une traînée qui
## s'efface progressivement — la vélocité angulaire EST le ruban, pas un
## habillage ajouté après coup. Pensé pour un swing (Bras-Faux, GDD §7.1 :
## "un seul balayage").

const MIN_VALUE_HSV := 0.20
const MAX_VALUE_HSV := 0.92

## Nombre de points d'historique conservés pour la traînée — assez pour
## une traînée lisible sur un swing de quelques ticks, jamais un budget
## mémoire qui grossit avec lifetime_ticks (fenêtre glissante, pas un
## historique complet).
const TRAIL_HISTORY_MAX := 8
## Largeur du ruban près de la pointe vs. près de la base — un ruban
## effilé, pas un simple trait uniforme.
const TIP_WIDTH_RATIO := 1.0
const BASE_WIDTH_RATIO := 0.25

var seed_val: int = 0
var lifetime_ticks: int = 6
var scale_px: float = 40.0
var origin: Vector2 = Vector2.ZERO
var direction: Vector2 = Vector2.RIGHT
## Amplitude totale du balayage (degrés) — centré sur `direction`, jamais
## un arc unilatéral (un swing part avant `direction` et finit après).
var sweep_deg: float = 90.0
var _color: Color = Color.from_hsv(0.0, 0.0, 0.8, 1.0)

var _ticks_elapsed: int = 0
var _rng := RandomNumberGenerator.new()
## Historique (angle, alpha_naissance) le plus récent en dernier.
var _history: Array = []


func configure(params: Dictionary) -> void:
	seed_val = params.get("seed", 0)
	lifetime_ticks = maxi(1, int(params.get("lifetime_ticks", 6)))
	scale_px = params.get("scale_px", 40.0)
	origin = params.get("origin", Vector2.ZERO)
	position = origin
	direction = params.get("direction", Vector2.RIGHT)
	if direction.length_squared() < 0.0001:
		direction = Vector2.RIGHT
	direction = direction.normalized()
	sweep_deg = params.get("sweep_deg", 90.0)
	z_index = 94  # CONTACT, juste sous arcSlash (95) — la traînée accompagne le coup, ne le domine pas.

	var value_pct: float = clampf(params.get("value_percent", 80.0), 0.0, 100.0) / 100.0
	var hue_deg: float = params.get("hue_deg", 0.0)
	var sat_pct: float = clampf(params.get("saturation_percent", 0.0), 0.0, 100.0) / 100.0
	var v: float = clampf(value_pct, MIN_VALUE_HSV, MAX_VALUE_HSV)
	_color = Color.from_hsv(hue_deg / 360.0, sat_pct, v, 1.0)

	# Seedé (§13.4) : léger bruit sur le point de départ du balayage,
	# jamais assez pour changer la lecture "un swing net".
	_rng.seed = seed_val
	var jitter_deg: float = (_rng.randf() - 0.5) * 6.0
	sweep_deg += jitter_deg


func tick(ticks_elapsed: int) -> void:
	_ticks_elapsed = ticks_elapsed
	var t: float = clampf(float(ticks_elapsed) / float(lifetime_ticks), 0.0, 1.0)
	var facing_angle: float = direction.angle()
	var half_sweep: float = deg_to_rad(sweep_deg) * 0.5
	var current_angle: float = facing_angle - half_sweep + deg_to_rad(sweep_deg) * t

	_history.append(current_angle)
	if _history.size() > TRAIL_HISTORY_MAX:
		_history.pop_front()

	queue_redraw()


func _draw() -> void:
	if _history.is_empty():
		return
	var t_life: float = 1.0 - clampf(float(_ticks_elapsed) / float(lifetime_ticks), 0.0, 1.0)
	if t_life <= 0.0:
		return

	# Chaque point d'historique dessine un segment de ruban qui s'efface
	# vers la queue (les plus anciens = plus transparents) — la traînée
	# elle-même, pas juste la pointe courante.
	var count: int = _history.size()
	for i in count:
		var age_frac: float = float(i + 1) / float(count)  # 0 = le plus vieux, 1 = le plus récent
		var alpha: float = t_life * age_frac
		if alpha <= 0.01:
			continue
		var angle: float = _history[i]
		var dir_vec := Vector2(cos(angle), sin(angle))
		var perp := Vector2(-dir_vec.y, dir_vec.x)
		var tip_half_w: float = scale_px * 0.12 * TIP_WIDTH_RATIO * age_frac
		var base_half_w: float = scale_px * 0.12 * BASE_WIDTH_RATIO
		var inner: float = scale_px * 0.35
		var outer: float = scale_px

		var points := PackedVector2Array([
			dir_vec * inner - perp * base_half_w,
			dir_vec * outer - perp * tip_half_w,
			dir_vec * outer + perp * tip_half_w,
			dir_vec * inner + perp * base_half_w,
		])
		var col := Color(_color.r, _color.g, _color.b, alpha)
		var colors := PackedColorArray()
		colors.resize(points.size())
		colors.fill(col)
		draw_polygon(points, colors)
