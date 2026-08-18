extends Node
## Autoload "VfxBudget" — docs/ARCHITECTURE_VFX_v3.md §8.2.
##
## Sur mobile, le goulot n'est presque jamais le nombre de particules mais
## l'overdraw (pixels redessinés par blending additif superposé). Ce nœud
## impose donc DEUX budgets distincts, jamais un simple compteur :
##   1. particules/sprites — un plafond par effet, un plafond global ;
##   2. overdraw estimé — taille × opacité × couches superposées (§8.2),
##      suivi PAR ZONE D'ÉCRAN (grille 4×3 sur le viewport 640×360, §8.2),
##      pas seulement par effet — deux VFX distincts qui se superposent
##      dans le même coin d'écran coûtent autant qu'un seul VFX géant.
##
## §4 : "budget de rémanence cumulée PAR ZONE D'ÉCRAN, pas seulement par
## effet" — la rémanence (CONSEQUENCE/dissipation qui traîne) est trackée
## séparément de l'overdraw actif : un VFX peut avoir fini son impact mais
## laisser une fissure/marque qui dissipe lentement, et c'est CE résidu
## cumulé par zone qui doit rester borné.
##
## Valeurs initiales, pas des vérités figées — §0 : "ajustables", même
## esprit que value_bands.json. Celles CHIFFRÉES par le mandat (50-200
## particules/effet, 2000 à l'écran) sont marquées comme telles ; le
## reste (budgets d'overdraw/rémanence par zone) est une estimation de
## départ à calibrer sur device réel (§11.3), pas un chiffre du doc.

const ZONE_COLS := 4
const ZONE_ROWS := 3
const VIEWPORT_SIZE := Vector2(640, 360)
const ZONE_WIDTH := VIEWPORT_SIZE.x / ZONE_COLS   # 160
const ZONE_HEIGHT := VIEWPORT_SIZE.y / ZONE_ROWS  # 120
const ZONE_COUNT := ZONE_COLS * ZONE_ROWS

## §8.2, chiffré par le mandat : "Plafonds initiaux : 50–200 particules
## par effet, 2000 simultanées à l'écran."
const PARTICLES_PER_EFFECT_MAX := 200
const PARTICLES_TOTAL_MAX := 2000

## Non chiffré par le mandat — estimation de départ, à recalibrer sur
## device réel (§11.3) une fois de vrais VFX mesurés.
const OVERDRAW_PER_ZONE_SOFT_CAP := 40.0
const RESIDUE_PER_ZONE_SOFT_CAP := 20.0

## Compteurs globaux.
var _particles_total := 0

## Un élément par zone : { particles, overdraw, residue }.
var _zones: Array[Dictionary] = []

## Chaque dépense enregistrée porte un id (fourni par VfxDirector, une
## instance de VFX) pour pouvoir la libérer exactement à la destruction
## de CETTE instance — jamais par soustraction globale, qui dérive vite
## en double-comptage si deux spawns/cleanups se chevauchent la même frame.
var _ledger: Dictionary = {}  # spawn_id (int) -> { zone_idx, particles, overdraw }


func _ready() -> void:
	_zones.resize(ZONE_COUNT)
	for i in ZONE_COUNT:
		_zones[i] = { "particles": 0, "overdraw": 0.0, "residue": 0.0 }


## Coordonnée écran (espace viewport 640×360, PAS coordonnée monde) ->
## index de zone 0..11, lecture gauche->droite puis haut->bas. Clampé :
## une position hors écran retombe sur la zone la plus proche plutôt que
## de planter — un VFX qui dépasse légèrement le cadre reste comptable.
func zone_index_for(screen_pos: Vector2) -> int:
	var col := int(clamp(floor(screen_pos.x / ZONE_WIDTH), 0, ZONE_COLS - 1))
	var row := int(clamp(floor(screen_pos.y / ZONE_HEIGHT), 0, ZONE_ROWS - 1))
	return row * ZONE_COLS + col


## §8.2 : "taille × opacité × couches superposées" — estimation simple et
## explicite, pas une simulation de blending réelle (hors de portée d'un
## script GDScript synchrone). `size_px` = plus grande dimension visuelle
## de l'effet (diamètre, pas rayon). `layers` = nombre de couches actives
## simultanément de CET effet (ex. shardBurst + impactStar en même temps
## = 2), pas le nombre total de VFX à l'écran (ça, c'est la somme par zone).
func estimate_overdraw_cost(size_px: float, opacity: float, layers: int) -> float:
	return size_px * clamp(opacity, 0.0, 1.0) * max(1, layers)


## Vérifie AVANT de dépenser — jamais spawn puis rollback, un budget
## refusé ne doit laisser aucune trace. `cost` = { particles, overdraw,
## zone_idx, degradable }. Retourne { ok: bool, reason: String } — jamais
## juste un bool nu : un refus silencieux est indiagnosticable en jeu réel.
##
## Addendum A, §A.2 — ordre de dégradation quand le plafond souple
## d'overdraw par zone est dépassé : `degradable` (A.1) est le seul
## levier disponible avec les primitives actuelles (aucune n'accepte de
## paramètre de qualité réduite, voir §A.6 "pas à implémenter
## maintenant") — une couche décorative qui dépasse est retirée
## entièrement (étapes 1-2 de l'ordre : particules/débris décoratifs,
## faute de pouvoir la dessiner "à moitié"). Une couche PROTÉGÉE
## (`degradable: false`) ne se voit jamais refuser ce plafond souple —
## "plancher intouchable" (étape 7) : BODY, ACTION CORE, CONTACT
## primaire, lisibilité de hitbox et feedback essentiel passent toujours,
## quitte à dépasser l'estimation d'overdraw (avertissement loggué pour
## calibrer les plafonds plus tard, jamais un refus silencieux). Les
## plafonds DURS de particules ci-dessus restent appliqués même aux
## couches protégées : ce sont des garde-fous anti-emballement (bug),
## pas un budget de compétition créative pour l'écran.
func can_spawn(cost: Dictionary) -> Dictionary:
	var particles: int = cost.get("particles", 0)
	var overdraw: float = cost.get("overdraw", 0.0)
	var zone_idx: int = cost.get("zone_idx", 0)
	var degradable: bool = cost.get("degradable", true)

	if particles > PARTICLES_PER_EFFECT_MAX:
		return { "ok": false, "reason": "particles_per_effect_exceeded (%d > %d)" % [particles, PARTICLES_PER_EFFECT_MAX] }
	if _particles_total + particles > PARTICLES_TOTAL_MAX:
		return { "ok": false, "reason": "particles_total_exceeded (%d + %d > %d)" % [_particles_total, particles, PARTICLES_TOTAL_MAX] }
	if zone_idx < 0 or zone_idx >= ZONE_COUNT:
		return { "ok": false, "reason": "zone_idx_out_of_range (%d)" % zone_idx }

	var zone: Dictionary = _zones[zone_idx]
	if zone["overdraw"] + overdraw > OVERDRAW_PER_ZONE_SOFT_CAP:
		if not degradable:
			push_warning("VfxBudget.can_spawn: couche protegee au-dela du plafond souple d'overdraw (zone %d: %.1f + %.1f > %.1f) - autorisee quand meme (plancher intouchable, Addendum A §A.2)." % [zone_idx, zone["overdraw"], overdraw, OVERDRAW_PER_ZONE_SOFT_CAP])
			return { "ok": true, "reason": "" }
		return { "ok": false, "reason": "overdraw_zone_exceeded_degradable_dropped (zone %d: %.1f + %.1f > %.1f)" % [zone_idx, zone["overdraw"], overdraw, OVERDRAW_PER_ZONE_SOFT_CAP] }

	return { "ok": true, "reason": "" }


## Enregistre une dépense déjà validée par can_spawn(). `spawn_id` est
## l'instance ID du nœud VFX (unique, stable pour sa durée de vie) —
## voir la remarque sur `_ledger` plus haut.
func register_spawn(spawn_id: int, cost: Dictionary) -> void:
	var particles: int = cost.get("particles", 0)
	var overdraw: float = cost.get("overdraw", 0.0)
	var zone_idx: int = cost.get("zone_idx", 0)

	_particles_total += particles
	_zones[zone_idx]["particles"] += particles
	_zones[zone_idx]["overdraw"] += overdraw

	_ledger[spawn_id] = { "zone_idx": zone_idx, "particles": particles, "overdraw": overdraw }


## Libère exactement ce que `register_spawn(spawn_id, ...)` avait
## enregistré. Idempotent : appeler deux fois pour le même spawn_id (mort
## + changement de salle la même frame, par exemple) ne soustrait qu'une
## fois — sans ça le budget dérive négatif et tous les gates suivants
## deviennent faux.
func release(spawn_id: int) -> void:
	if not _ledger.has(spawn_id):
		return
	var entry: Dictionary = _ledger[spawn_id]
	_particles_total -= entry["particles"]
	var zone_idx: int = entry["zone_idx"]
	_zones[zone_idx]["particles"] -= entry["particles"]
	_zones[zone_idx]["overdraw"] -= entry["overdraw"]
	_ledger.erase(spawn_id)


## CONSEQUENCE/dissipation (§4, §8.2) : résidu qui traîne après la fin de
## l'effet actif (fissure, marque, débris). Suivi séparément de l'overdraw
## "actif" ci-dessus — un résidu n'est pas redessiné à pleine opacité
## chaque frame, mais il occupe quand même la zone visuellement.
func register_residue(zone_idx: int, amount: float) -> Dictionary:
	if zone_idx < 0 or zone_idx >= ZONE_COUNT:
		return { "ok": false, "reason": "zone_idx_out_of_range (%d)" % zone_idx }
	var zone: Dictionary = _zones[zone_idx]
	if zone["residue"] + amount > RESIDUE_PER_ZONE_SOFT_CAP:
		return { "ok": false, "reason": "residue_zone_exceeded (zone %d: %.1f + %.1f > %.1f)" % [zone_idx, zone["residue"], amount, RESIDUE_PER_ZONE_SOFT_CAP] }
	zone["residue"] += amount
	return { "ok": true, "reason": "" }


## Décroît la rémanence d'une zone (appelé par le profil de dissipation
## d'un effet consommé, en ticks). `amount` toujours >= 0 en entrée ;
## clampé à 0 en sortie — jamais négatif (un résidu ne "doit" pas d'écran).
func decay_residue(zone_idx: int, amount: float) -> void:
	if zone_idx < 0 or zone_idx >= ZONE_COUNT:
		return
	var zone: Dictionary = _zones[zone_idx]
	zone["residue"] = max(0.0, zone["residue"] - amount)


## Diagnostic (VFX Lab §13.5, tests de stress §13.4) : état complet,
## lisible tel quel dans les logs de test.
func debug_state() -> Dictionary:
	return {
		"particles_total": _particles_total,
		"particles_total_max": PARTICLES_TOTAL_MAX,
		"active_spawns": _ledger.size(),
		"zones": _zones.duplicate(true),
	}


## Remise à zéro complète — changement de scène (§13.4 "cleanup :
## destruction au timeout, à la mort, au changement de scène"). Ne PAS
## appeler pour un cleanup normal d'un seul effet : ça, c'est release().
func reset() -> void:
	_particles_total = 0
	_ledger.clear()
	for i in ZONE_COUNT:
		_zones[i] = { "particles": 0, "overdraw": 0.0, "residue": 0.0 }
