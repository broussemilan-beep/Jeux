extends TileMapLayer
## F (mandat production v1 §6, "Le monde") — remplit une zone rectangulaire
## avec les tuiles de sol du Wang tileset généré (MANDAT NUIT phase 2 :
## biome Première Gate). Toujours un pavage code (pas de tile_data figé
## en scène — zone rectangulaire, pas de salle non rectangulaire à ce
## stade), mais désormais avec DEUX tuiles "pures" du tileset (coin 0,0 =
## grès chaud dominant, coin 1,0 = pierre sombre, chacune seamless avec
## elle-même par construction Wang) au lieu d'une seule — variation
## visuelle basse-risque plutôt qu'un vrai autotiling à coins (16 tuiles,
## peering bits Godot) : la donnée existe (tileset_data côté PixelLab)
## mais câbler un TerrainSet correctement sans éditeur interactif pour
## vérifier visuellement est le genre de risque qu'une nuit autonome ne
## doit pas prendre sur un seul asset (mandat §7). Motif déterministe
## (hash de cellule), pas de RNG — le sol ne doit pas re-tirer à chaque
## reload de scène.

@export var origin_tile: Vector2i = Vector2i(-13, -10)
@export var area_size_tiles: Vector2i = Vector2i(44, 38)


func _ready() -> void:
	for x in range(origin_tile.x, origin_tile.x + area_size_tiles.x):
		for y in range(origin_tile.y, origin_tile.y + area_size_tiles.y):
			var variant := Vector2i(1, 0) if _is_dark_variant(x, y) else Vector2i(0, 0)
			set_cell(Vector2i(x, y), 0, variant)


## Motif déterministe pseudo-aléatoire (pas de vrai bruit dispo sans
## dépendance) — ~1 case sur 6 en variante sombre, jamais deux voisines
## adjacentes (horizontal/vertical) pour éviter un bloc compact visible.
func _is_dark_variant(x: int, y: int) -> bool:
	var h: int = (x * 928371 + y * 128191) % 6
	return h == 0 and (x + y) % 2 == 0
