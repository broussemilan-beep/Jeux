extends TileMapLayer
## F (mandat production v1 §6, "Le monde") — remplit une zone rectangulaire
## avec un vrai TerrainSet à coins (peering bits Godot, 16 tuiles Wang du
## biome Première Gate). Toujours un pavage codé (pas de tile_data figé en
## scène — zone rectangulaire, pas de salle non rectangulaire à ce stade).
##
## Remplace le scope réduit de la Phase 2 MANDAT NUIT (2 tuiles pures en
## damier) — le TerrainSet complet (`floor_terrain.tres`, généré par
## tools/pixellab_tileset_converter.gd depuis les 16 tuiles PixelLab déjà
## payées) était jugé trop risqué à câbler sans éditeur interactif pour
## vérifier visuellement (docs/worklog.md, Phase 2). Repris suite au retour
## de Milan : vérifié par capture 2D headless (le rendu 2D fonctionne dans
## ce projet, contrairement au rendu 3D — voir Phase 3), pas à l'aveugle.
##
## Motif déterministe (hash de BLOC, pas de case individuelle) pour que les
## taches de pierre sombre soient des îlots connectés de quelques tuiles
## (transitions Wang lisibles) plutôt qu'un bruit case-par-case qui
## produirait 16 combinaisons de coins isolées visuellement chargées.
## Pas de RNG — le sol ne doit pas re-tirer à chaque reload de scène.

const TERRAIN_SET := 0
const TERRAIN_LOWER := 0  # pierre sombre
const TERRAIN_UPPER := 1  # grès chaud (dominant)

@export var origin_tile: Vector2i = Vector2i(-13, -10)
@export var area_size_tiles: Vector2i = Vector2i(44, 38)

# Taille des blocs de patch (en tuiles) — assez grand pour lire comme un
# îlot de pierre sombre connecté, assez petit pour ne pas dominer le sol.
const PATCH_BLOCK_SIZE := Vector2i(4, 3)


func _ready() -> void:
	var all_cells: Array[Vector2i] = []
	for x in range(origin_tile.x, origin_tile.x + area_size_tiles.x):
		for y in range(origin_tile.y, origin_tile.y + area_size_tiles.y):
			all_cells.append(Vector2i(x, y))
	set_cells_terrain_connect(all_cells, TERRAIN_SET, TERRAIN_UPPER)

	var patch_cells: Array[Vector2i] = []
	for x in range(origin_tile.x, origin_tile.x + area_size_tiles.x):
		for y in range(origin_tile.y, origin_tile.y + area_size_tiles.y):
			if _is_dark_patch(x, y):
				patch_cells.append(Vector2i(x, y))
	if not patch_cells.is_empty():
		set_cells_terrain_connect(patch_cells, TERRAIN_SET, TERRAIN_LOWER)


## Motif déterministe par bloc — ~1 bloc sur 5 devient une tache de pierre
## sombre. Hash sur les coordonnées de BLOC (pas de tuile) pour que chaque
## tache couvre plusieurs tuiles adjacentes d'un coup, connectées par
## set_cells_terrain_connect (transitions Wang correctes aux bords du bloc).
func _is_dark_patch(x: int, y: int) -> bool:
	var block_x: int = floori(float(x) / PATCH_BLOCK_SIZE.x)
	var block_y: int = floori(float(y) / PATCH_BLOCK_SIZE.y)
	var h: int = (block_x * 928371 + block_y * 128191) % 5
	return h == 0
