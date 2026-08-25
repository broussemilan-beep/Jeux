extends RefCounted
class_name Targeting
## Ciblage partagé — "ennemi le plus proche en zone" est demandé tel quel
## par le mandat Totem du Vide (attack.json : "sur l'ennemi le plus proche
## en zone (rayon 3m)"). Fonction pure, sans dépendance à un nœud précis,
## pour rester réutilisable par n'importe quel pouvoir/attaque futur —
## jamais une seule compétence qui réimplémente sa propre recherche.


## Retourne le nœud du groupe "enemies" vivant le plus proche de `origin`,
## dans `radius_px`, ou null si aucun. "Vivant" = a un `Stats` valide et
## non `is_dead()` — un ennemi qui vient de mourir ce même tick ne doit pas
## rester ciblable jusqu'à sa libération effective.
static func nearest_enemy_in_radius(tree: SceneTree, origin: Vector2, radius_px: float) -> Node:
	var best: Node = null
	var best_dist_sq: float = radius_px * radius_px
	for candidate in tree.get_nodes_in_group("enemies"):
		if not (candidate is Node2D):
			continue
		if candidate.has_method("is_dead") and candidate.is_dead():
			continue
		var dist_sq: float = origin.distance_squared_to(candidate.global_position)
		if dist_sq <= best_dist_sq:
			best = candidate
			best_dist_sq = dist_sq
	return best


## Retourne TOUS les ennemis vivants dans `radius_px` ET dans un cône de
## `half_angle_deg` de part et d'autre de `facing` — usage : l'archétype
## de cast "frappe de zone" (mandat production v1 §5, ex. Bras-Faux, GDD
## §7.1 : "arc ~90°"), qui touche potentiellement PLUSIEURS cibles en un
## seul balayage, contrairement à `nearest_enemy_in_radius()` (une seule
## cible, le combo léger/Gueule Vide). Même filtre "vivant" que ci-dessus.
## `facing` nul retombe sur Vector2.RIGHT plutôt que de renvoyer un
## tableau vide sans raison de gameplay.
static func enemies_in_arc(tree: SceneTree, origin: Vector2, facing: Vector2, radius_px: float, half_angle_deg: float) -> Array:
	var dir := facing
	if dir.length_squared() < 0.0001:
		dir = Vector2.RIGHT
	dir = dir.normalized()
	var half_angle_rad: float = deg_to_rad(half_angle_deg)
	var radius_sq: float = radius_px * radius_px
	# CHANTIER A (Terre, 2026-08-24) : half_angle_deg=180 est le patron
	# documenté (Effondrement, power.effondrement.cast.json) pour représenter
	# un cercle COMPLET plutôt qu'un cône — mais une cible exactement à
	# l'opposé de `dir` (180° pile, ex. l'ennemi "derrière" du smoke test)
	# donne un angle_to dont l'arrondi flottant (Vector2.angle_to() vs
	# deg_to_rad(180.0)) peut dépasser half_angle_rad d'un epsilon et se
	# faire exclure à tort — constaté empiriquement (comparaison stricte
	# `<=` fragile pile à la frontière mathématique). Un cône >=180° n'a de
	# toute façon plus de "côté exclu" possible : sauter la comparaison
	# d'angle entièrement dans ce cas élimine le risque plutôt que de le
	# masquer avec une marge arbitraire.
	var is_full_circle: bool = half_angle_rad >= PI - 0.0001

	var hits: Array = []
	for candidate in tree.get_nodes_in_group("enemies"):
		if not (candidate is Node2D):
			continue
		if candidate.has_method("is_dead") and candidate.is_dead():
			continue
		var to_candidate: Vector2 = candidate.global_position - origin
		if to_candidate.length_squared() > radius_sq:
			continue
		if is_full_circle or to_candidate.length_squared() < 0.0001:
			hits.append(candidate)  # cercle complet, ou exactement sur l'origine (dans tous les cônes possibles).
			continue
		var angle_to: float = absf(dir.angle_to(to_candidate.normalized()))
		if angle_to <= half_angle_rad:
			hits.append(candidate)
	return hits


## Retourne tous les ennemis vivants dans une bande rectangulaire devant
## `origin` : entre 0 et `length_px` le long de `facing`, et à moins de
## `half_width_px` de part et d'autre (perpendiculaire) — usage : l'archétype
## "vague en ligne" (Marée de Sable, GDD "une ligne devant Rank Zero"),
## distinct du cône d'enemies_in_arc() (Bras-Faux/Poing Tellurique, un arc
## centré sur l'origine) : une ligne a une largeur CONSTANTE sur toute sa
## longueur, pas un angle qui s'élargit avec la distance. Même filtre
## "vivant" que les fonctions ci-dessus.
static func enemies_in_line(tree: SceneTree, origin: Vector2, facing: Vector2, length_px: float, half_width_px: float) -> Array:
	var dir := facing
	if dir.length_squared() < 0.0001:
		dir = Vector2.RIGHT
	dir = dir.normalized()
	var perp := Vector2(-dir.y, dir.x)

	var hits: Array = []
	for candidate in tree.get_nodes_in_group("enemies"):
		if not (candidate is Node2D):
			continue
		if candidate.has_method("is_dead") and candidate.is_dead():
			continue
		var to_candidate: Vector2 = candidate.global_position - origin
		var forward: float = to_candidate.dot(dir)
		if forward < 0.0 or forward > length_px:
			continue
		var lateral: float = absf(to_candidate.dot(perp))
		if lateral <= half_width_px:
			hits.append(candidate)
	return hits


## Symétrique de nearest_enemy_in_radius() côté ennemis (G, GDD §10) :
## une seule instance de joueur dans le groupe "player" (contrairement à
## "enemies", pluriel par nature) — pas de paramètre radius, un ennemi a
## besoin de la distance exacte pour décider lui-même IDLE/CHASE/ATTAQUE,
## pas d'un filtre déjà appliqué. Retourne null si absent ou mort, même
## discipline "vivant" que ci-dessus.
static func get_player(tree: SceneTree) -> Node:
	var players: Array = tree.get_nodes_in_group("player")
	if players.is_empty():
		return null
	var candidate: Node = players[0]
	if candidate.has_method("is_dead") and candidate.is_dead():
		return null
	return candidate
