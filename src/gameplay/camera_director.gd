extends Node
## Autoload "CameraDirector" — mandat production v1 §4, système
## "CameraDirector (étend le shake)". Deux effets, tous deux LUS par
## Player à chaque tick et appliqués sur SA Camera2D (ce nœud ne détient
## aucune caméra lui-même — comme CombatFeedback pour le shake, un seul
## point de vérité tick-driven, zéro Tween temps réel) :
##
##   1. Punch-zoom : +2-3% de zoom sur 3 ticks pour un impact medium+
##      (déclenché explicitement par l'appelant via trigger_punch(), sur
##      les mêmes tiers que ceux qui déclenchent déjà un hit-stop medium+,
##      COMBO_TIER_FEEDBACK dans player.gd — jamais un second système de
##      seuils dupliqué).
##   2. Lookahead : décalage fixe dans la direction du dash pendant qu'il
##      est en cours — lu directement par Player (get_lookahead_offset()),
##      pas un état à déclencher/faire décroître ici (contrairement au
##      punch, le lookahead suit une direction qui change tick par tick,
##      donc pas de timeline propre à ce nœud).
##
## "Le cadrage actuel est bon ; le problème était l'inertie" (mandat) —
## ce module ajoute un ressenti d'impact/anticipation, ne remplace RIEN
## de l'existant (shake, position_smoothing du Camera2D).

const PUNCH_ZOOM_TICKS := 3
## +2.5%, milieu de la fourchette "2-3%" du mandat.
const PUNCH_ZOOM_AMOUNT := 0.025
## Milieu de la fourchette "12-20px" du mandat.
const LOOKAHEAD_DISTANCE_PX := 16.0

## Phase R4 (suite, verdict de Milan sur les 2 captures A/B envoyées après
## le chantier "sol/chiffres/game feel" — cam_zoom=1.0 vs 0.8, option B
## retenue) : zoom de BASE permanent des scènes de jeu, remplace l'ancien
## Vector2.ONE neutre sur lequel seul le punch-zoom ponctuel s'appliquait.
## Camera2D.zoom < 1 = plus zoomé (Godot inverse l'intuition "zoom in =
## plus grand") : 0.8 affiche 80% de la largeur normale du monde dans le
## même viewport, donc les sprites paraissent 1/0.8 = 1.25× plus grands
## ("+25%"). Un seul Player.tscn partagé par gate_premiere/test_arena/
## outpost (voir _physics_process de Player) : ce SEUL changement
## s'applique aux 3 scènes, pas 3 réglages séparés à synchroniser.
const BASE_ZOOM := Vector2(0.8, 0.8)

var _punch_ticks_remaining: int = 0


func _physics_process(_delta: float) -> void:
	if CombatFeedback.is_frozen():
		return
	if _punch_ticks_remaining > 0:
		_punch_ticks_remaining -= 1


## Un appel pendant un punch déjà actif relance à pleine intensité (même
## politique que CombatFeedback.trigger_hitstop() : jamais additif).
func trigger_punch() -> void:
	_punch_ticks_remaining = PUNCH_ZOOM_TICKS


## Zoom Camera2D à appliquer CE tick — Vector2.ONE hors punch (aucun
## effet), décroît linéairement vers Vector2.ONE sur PUNCH_ZOOM_TICKS.
## Note pixel art (limite connue, assumée) : un zoom fractionnaire de
## quelques ticks peut légèrement flouter/scintiller le rendu NEAREST —
## accepté ici car bref (3 ticks ≈ 50ms) et explicitement demandé par le
## mandat ; à surveiller sur les captures réelles, pas juste supposé sans
## risque.
func get_punch_zoom() -> Vector2:
	if _punch_ticks_remaining <= 0:
		return Vector2.ONE
	var elapsed: int = PUNCH_ZOOM_TICKS - _punch_ticks_remaining
	var t: float = float(elapsed) / float(PUNCH_ZOOM_TICKS)
	var amount: float = PUNCH_ZOOM_AMOUNT * (1.0 - t)
	return Vector2.ONE * (1.0 + amount)


## Zoom Camera2D COMPLET à appliquer ce tick (Player._physics_process()) :
## BASE_ZOOM permanent × punch-zoom ponctuel — une multiplication, pas une
## addition, pour que le punch garde exactement la même intensité
## RELATIVE (+2,5% au pic) quel que soit le zoom de base. get_punch_zoom()
## reste exposée telle quelle (lue isolément par le smoke test
## camera_punch_zoom_triggers_on_medium_hit_not_light, qui vérifie le
## PUNCH lui-même, indépendamment de tout zoom de base).
func get_zoom() -> Vector2:
	return BASE_ZOOM * get_punch_zoom()


## `direction` : direction du dash en cours (Vector2.ZERO hors dash — le
## lookahead ne s'applique qu'à l'action qui a explicitement une direction
## de déplacement soutenue, pas au mouvement normal ni au combo qui reste
## globalement sur place).
func get_lookahead_offset(direction: Vector2) -> Vector2:
	if direction.length_squared() < 0.0001:
		return Vector2.ZERO
	return direction.normalized() * LOOKAHEAD_DISTANCE_PX
