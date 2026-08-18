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
