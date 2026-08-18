extends Node2D
## Primitive "impactFlashFrame" — docs/ARCHITECTURE_VFX_v3.md §4 et §7.1.
##
## §4 : "CONTACT — flash blanc première frame : primitive
## impactFlashFrame — noyau blanc quasi-plein (≤ 92% de valeur), 1-2
## ticks, affiché avant le corps de l'effet. Distincte d'impactStar."
##
## C'est la primitive de test choisie pour la Phase 0 (§15, Definition
## of done) : pas un stub jetable — elle est nommément obligatoire dans
## TOUT impact majeur (§9.3, étape 1/6), donc du vrai travail utile dès
## le premier commit, pas une brique qu'on jettera en Phase 1.
##
## Contrat primitive (§7.1) : reçoit seed, palette, durée (ticks),
## direction, échelle, origine, courbe temporelle, overdraw_cost estimé,
## via configure(). Ce flash ne consomme pas seed pour son rendu (aucun
## aléatoire visuel — un flash est un flash, pas une gerbe), mais le
## champ est accepté quand même : cohérence de contrat entre primitives,
## et VfxDirector journalise seed+recette de CHAQUE spawn (§8.2), primitive
## incluse, indépendamment de si elle s'en sert.

## §3 : bande VFX = 20-92% de valeur (HSV). Le "≤ 92%" du §4 EST cette
## borne haute — jamais blanc pur (V=100%), qui collisionnerait avec la
## catégorie UI (§3 : "Jamais 0% ni 100% — collision UI/décor").
const MAX_VALUE_HSV := 0.92

var seed: int = 0
var lifetime_ticks: int = 2
var scale_px: float = 24.0
var origin: Vector2 = Vector2.ZERO

var _ticks_elapsed: int = 0


func configure(params: Dictionary) -> void:
	seed = params.get("seed", 0)
	# "1-2 ticks" (§4) — jamais plus, jamais 0 (une frame minimum).
	lifetime_ticks = clampi(params.get("lifetime_ticks", 2), 1, 2)
	scale_px = params.get("scale_px", 24.0)
	origin = params.get("origin", Vector2.ZERO)
	position = origin
	# CONTACT est la couche 5/8 (§4) — au-dessus d'ANTICIPATION/ACTION
	# CORE/TRAIL, en dessous de CONSEQUENCE/FEEDBACK/POST-RENDER qui ne
	# sont pas des nœuds de scène (feedback = caméra/hitstop, post-render
	# = shader plein écran). z_index élevé mais borné, pas 4096.
	z_index = 100


## Appelé par VfxDirector chaque tick physique (§8.2 : le director
## centralise l'avancement, jamais la primitive en autonome).
func tick(ticks_elapsed: int) -> void:
	_ticks_elapsed = ticks_elapsed
	queue_redraw()


func _draw() -> void:
	# "Quasi-plein" dès la 1re image ; légère décroissance sur la 2e
	# tick si lifetime_ticks==2 — un flash qui reste À IDENTIQUE
	# opacité pendant 2 ticks lirait comme un carré plat, pas un flash.
	var t: float = float(_ticks_elapsed) / float(max(1, lifetime_ticks))
	var v: float = MAX_VALUE_HSV * (1.0 - t * 0.15)
	var col := Color.from_hsv(0.0, 0.0, v, 1.0)
	draw_circle(Vector2.ZERO, scale_px * 0.5, col)
