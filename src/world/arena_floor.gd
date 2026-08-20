extends TileMapLayer
## F (mandat production v1 §6, "Le monde") — remplit une zone rectangulaire
## avec la tuile de sol unique. C'est la tuile "pure lower" du Wang tileset
## généré (les 4 coins = même terrain) : seamless avec elle-même par
## construction, donc un pavage uniforme sans jamais avoir besoin de
## résoudre les 15 autres combinaisons de coins pour cette tranche "mini-
## tileset... sans attendre plus de contenu" (mandat §6, F). Rempli en
## code plutôt qu'en `tile_data` figé dans la scène : la zone est un
## simple rectangle (pas de salle non rectangulaire à ce stade).

@export var origin_tile: Vector2i = Vector2i(-13, -10)
@export var area_size_tiles: Vector2i = Vector2i(44, 38)


func _ready() -> void:
	for x in range(origin_tile.x, origin_tile.x + area_size_tiles.x):
		for y in range(origin_tile.y, origin_tile.y + area_size_tiles.y):
			set_cell(Vector2i(x, y), 0, Vector2i(0, 0))
