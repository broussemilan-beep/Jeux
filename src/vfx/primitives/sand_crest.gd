extends Node2D
## Primitive "sandCrest" — docs/ARCHITECTURE_VFX_v3.md §7.1, ajoutée
## 2026-08-22 (audit fidélité Milan, round 3, Marée de Sable).
##
## Remplace beamSegment comme couche ACTION CORE de Marée de Sable.
## Diagnostic qui a motivé cette primitive (voir aussi
## captures/verification/2026-08-22-fidelite-maree_de_sable-v2.png) :
## beamSegment dessine une rangée de QUADS PLATS (draw_polygon, angles
## droits) — la planche de référence (docs/references/terre/
## maree_de_sable.png, "Assets détachés") montre au contraire une
## texture organique à pointes de sable acérées, jamais des blocs
## géométriques. Aucun réglage de recette (scale_px/width_px/count) ne
## peut faire apparaître une silhouette dentelée à partir de quads —
## la session précédente l'avait déjà constaté et s'était limitée à un
## palliatif (3 couches fractureLine en accent, cf. historique JSON de
## la recette) : un vrai changement de rendu demandait soit un moteur de
## génération de mesh/silhouette procédurale complexe, soit un VRAI
## sprite. Choix : un sprite PixelLab (assets/processed/vfx/
## sand_crest.png, silhouette BLANCHE pure sur fond transparent, source
## brute conservée dans assets/source/pixellab/vfx/sand_crest_raw.png)
## teinté dynamiquement par la palette EXACTEMENT comme les primitives
## procédurales (modulate = la même Color HSV que draw_polygon/
## draw_circle ailleurs dans ce dossier) — jamais une couleur figée dans
## le PNG, pour rester compatible avec la résolution de couleur générique
## de VfxRecipeRegistry._resolve_color().
##
## Contrat identique à beamSegment (même famille de paramètres — scale_px
## = longueur totale le long de `direction`, width_px = hauteur hors
## tout) pour rester un remplacement direct dans la recette JSON : le
## sprite s'étend depuis l'origine sur les premiers 40% de sa durée de
## vie (le tir "part"), tient à pleine longueur, puis s'efface sur les
## 30% finaux — même timing que beamSegment, seul le rendu change.
## Couche ACTION CORE (§4).

const TEXTURE: Texture2D = preload("res://assets/processed/vfx/sand_crest.png")
const MIN_VALUE_HSV := 0.20
const MAX_VALUE_HSV := 0.92

var seed_val: int = 0
var lifetime_ticks: int = 8
var scale_px: float = 60.0  # longueur totale le long de `direction`
var width_px: float = 24.0  # hauteur hors tout, perpendiculaire à `direction`
var origin: Vector2 = Vector2.ZERO
var direction: Vector2 = Vector2.RIGHT
var _color: Color = Color.from_hsv(0.0, 0.0, 0.6, 1.0)

var _ticks_elapsed: int = 0


func configure(params: Dictionary) -> void:
	seed_val = params.get("seed", 0)
	lifetime_ticks = maxi(1, int(params.get("lifetime_ticks", 8)))
	scale_px = params.get("scale_px", 60.0)
	width_px = params.get("width_px", 24.0)
	origin = params.get("origin", Vector2.ZERO)
	position = origin
	direction = params.get("direction", Vector2.RIGHT)
	if direction.length_squared() < 0.0001:
		direction = Vector2.RIGHT
	direction = direction.normalized()
	rotation = direction.angle()
	z_index = 30  # ACTION CORE : même rang que beamSegment, qu'elle remplace pour Marée de Sable.

	var value_pct: float = clampf(params.get("value_percent", 60.0), 0.0, 100.0) / 100.0
	var hue_deg: float = params.get("hue_deg", 0.0)
	var sat_pct: float = clampf(params.get("saturation_percent", 0.0), 0.0, 100.0) / 100.0
	var v: float = clampf(value_pct, MIN_VALUE_HSV, MAX_VALUE_HSV)
	_color = Color.from_hsv(hue_deg / 360.0, sat_pct, v, 1.0)


func tick(ticks_elapsed: int) -> void:
	_ticks_elapsed = ticks_elapsed
	queue_redraw()


func _draw() -> void:
	var t: float = clampf(float(_ticks_elapsed) / float(lifetime_ticks), 0.0, 1.0)
	# Même courbe que beam_segment.gd : extension sur les premiers 40%,
	# plein jusqu'à 70%, fondu sur les 30% finaux.
	var extend_t: float = clampf(t / 0.4, 0.0, 1.0)
	var alpha: float = 1.0 - clampf((t - 0.7) / 0.3, 0.0, 1.0)
	if alpha <= 0.0 or extend_t <= 0.0:
		return
	var col := Color(_color.r, _color.g, _color.b, alpha)

	var tex_size: Vector2 = TEXTURE.get_size()
	# Révélation progressive depuis l'origine (jamais un stretch qui
	# déformerait la texture pendant l'extension) : la région source ET
	# la largeur de destination grandissent au même rythme, le ratio
	# px-texture/px-monde reste constant du premier au dernier tick.
	var dest_w: float = scale_px * extend_t
	var region_w: float = tex_size.x * extend_t
	var region := Rect2(0.0, 0.0, region_w, tex_size.y)
	var dest := Rect2(Vector2(0.0, -width_px * 0.5), Vector2(dest_w, width_px))
	draw_texture_rect_region(TEXTURE, dest, region, col)
