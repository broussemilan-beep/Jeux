extends SceneTree
## Convertit un tileset Wang PixelLab (metadata JSON + PNG sprite sheet) en
## TileSet Godot avec un vrai TerrainSet à coins (peering bits), au lieu de
## se limiter aux 2 tuiles "pures" comme le faisait la Phase 2 du MANDAT
## NUIT (scope réduit volontaire, documenté dans docs/worklog.md — jugé
## trop risqué à câbler sans éditeur interactif pour vérifier). Repris ici
## suite au retour de Milan : ce script tourne en headless
## (`godot4 --headless -s pixellab_tileset_converter.gd ...`), donc la
## vérification se fait par capture 2D (scripts déjà existants), pas à
## l'aveugle — l'éditeur interactif n'est plus un prérequis.
##
## Adapté du script fourni par la doc MCP PixelLab
## (pixellab://docs/godot/wang-tilesets) — structure de données confirmée
## identique à celle réellement livrée par l'API (metadata.tileset_data.
## tiles[i].corners/bounding_box, metadata.metadata.terrain_prompts).
##
## Usage :
##   godot4 --headless -s tools/pixellab_tileset_converter.gd -- \
##       <metadata.json> <image.png> --output=<res_path.tres>

var output_path := "res://assets/processed/sprites/world/floor_terrain.tres"
var tile_size := 0
var terrains := {}
var tiles := []

# Layout en grille de coins — mêmes 16 motifs que le script d'origine,
# assure que les 16 combinaisons NW/NE/SW/SE sont représentées une fois
# chacune dans l'atlas de sortie (5 colonnes x 4 lignes, 3 cases vides).
var corner_layout := [
	"ss/sw", "ss/ww", "ss/ws", "ww/ws", "ww/sw",
	"sw/sw", "ww/ww", "ws/ws", "ws/ww", "sw/ww",
	"sw/ss", "ww/ss", "ws/ss", "ws/sw", "sw/ws",
	"ww/ww", "ss/ss", "", "", "",
]


func _init() -> void:
	print("PixelLab -> Godot TerrainSet converter")

	var args := OS.get_cmdline_user_args()
	var json_path := ""
	var png_path := ""
	for arg in args:
		if arg.begins_with("--output="):
			output_path = arg.substr("--output=".length())
		elif arg.ends_with(".json"):
			json_path = arg
		elif arg.ends_with(".png"):
			png_path = arg

	if json_path == "" or png_path == "":
		print("ERREUR: besoin d'un .json et d'un .png en argument (voir --).")
		quit(1)
		return

	load_tileset_pair(json_path, png_path)

	if tiles.is_empty():
		print("ERREUR: aucune tuile chargée depuis ", json_path)
		quit(1)
		return

	create_tileset()
	print("OK -> ", output_path)
	quit(0)


func load_tileset_pair(json_path: String, png_path: String) -> void:
	if not FileAccess.file_exists(json_path):
		print("ERREUR: metadata introuvable: ", json_path)
		return
	var file := FileAccess.open(json_path, FileAccess.READ)
	var json := JSON.new()
	if json.parse(file.get_as_text()) != OK:
		print("ERREUR: JSON invalide: ", json_path)
		return
	file.close()
	var metadata: Dictionary = json.data

	if not FileAccess.file_exists(png_path):
		print("ERREUR: PNG introuvable: ", png_path)
		return
	var sprite_sheet := Image.new()
	if sprite_sheet.load(png_path) != OK:
		print("ERREUR: échec chargement PNG: ", png_path)
		return

	if tile_size == 0:
		var size = metadata.tileset_data.tile_size
		tile_size = int(size.width)
		print("  Taille de tuile: ", tile_size, "x", tile_size)

	var lower_name: String = metadata.metadata.terrain_prompts.lower
	var upper_name: String = metadata.metadata.terrain_prompts.upper
	var lower_id := get_terrain_id(lower_name)
	var upper_id := get_terrain_id(upper_name)

	var wang_tiles := {}
	for tile in metadata.tileset_data.tiles:
		var corners: Dictionary = tile.corners
		var box: Dictionary = tile.bounding_box
		var w := int(box.width)
		var h := int(box.height)
		var x := int(box.x)
		var y := int(box.y)

		var tile_image := Image.create(w, h, false, Image.FORMAT_RGBA8)
		tile_image.blit_rect(sprite_sheet, Rect2i(x, y, w, h), Vector2i.ZERO)

		var nw := 1 if corners.NW == "upper" else 0
		var ne := 1 if corners.NE == "upper" else 0
		var sw := 1 if corners.SW == "upper" else 0
		var se := 1 if corners.SE == "upper" else 0
		var wang_idx := nw * 8 + ne * 4 + sw * 2 + se

		wang_tiles[wang_idx] = {
			"image": tile_image,
			"corners": [
				upper_id if nw == 1 else lower_id,
				upper_id if ne == 1 else lower_id,
				upper_id if sw == 1 else lower_id,
				upper_id if se == 1 else lower_id,
			],
		}

	var added := 0
	for pattern in corner_layout:
		if pattern == "":
			tiles.append(null)
			continue
		var parts: PackedStringArray = String(pattern).split("/")
		var top: String = parts[0]
		var bottom: String = parts[1]
		var nw := 1 if top[0] == "s" else 0
		var ne := 1 if top[1] == "s" else 0
		var sw := 1 if bottom[0] == "s" else 0
		var se := 1 if bottom[1] == "s" else 0
		var wang_idx := nw * 8 + ne * 4 + sw * 2 + se
		if wang_tiles.has(wang_idx):
			tiles.append(wang_tiles[wang_idx])
			added += 1
		else:
			tiles.append(null)

	print("  ", added, " tuiles ajoutées (sur 16 combinaisons de coins)")


func get_terrain_id(name: String) -> int:
	for id in terrains:
		if terrains[id] == name:
			return id
	var id := terrains.size()
	terrains[id] = name
	return id


func create_tileset() -> void:
	var cols := 5
	var rows := int(ceil(float(tiles.size()) / cols))
	var atlas := Image.create(cols * tile_size, rows * tile_size, false, Image.FORMAT_RGBA8)

	for i in range(tiles.size()):
		if tiles[i] == null:
			continue
		var img: Image = tiles[i].image
		var x := (i % cols) * tile_size
		var y := int(i / cols) * tile_size
		atlas.blit_rect(img, Rect2i(0, 0, tile_size, tile_size), Vector2i(x, y))

	var atlas_path := output_path.replace(".tres", "_atlas.png")
	atlas.save_png(atlas_path)
	print("  Atlas: ", atlas_path)

	var tile_defs := []
	for i in range(tiles.size()):
		if tiles[i] == null:
			continue
		var x := i % cols
		var y := int(i / cols)
		var corners: Array = tiles[i].corners
		tile_defs.append("%d:%d/0 = 0" % [x, y])
		tile_defs.append("%d:%d/0/terrain_set = 0" % [x, y])
		tile_defs.append("%d:%d/0/terrain = %d" % [x, y, corners[0]])
		tile_defs.append("%d:%d/0/terrains_peering_bit/top_left_corner = %d" % [x, y, corners[0]])
		tile_defs.append("%d:%d/0/terrains_peering_bit/top_right_corner = %d" % [x, y, corners[1]])
		tile_defs.append("%d:%d/0/terrains_peering_bit/bottom_left_corner = %d" % [x, y, corners[2]])
		tile_defs.append("%d:%d/0/terrains_peering_bit/bottom_right_corner = %d" % [x, y, corners[3]])

	var terrain_defs := []
	var terrain_colors := {}
	for i in range(tiles.size()):
		if tiles[i] == null:
			continue
		var corners: Array = tiles[i].corners
		if corners[0] == corners[1] and corners[1] == corners[2] and corners[2] == corners[3]:
			var terrain_id: int = corners[0]
			if not terrain_colors.has(terrain_id):
				var img: Image = tiles[i].image
				terrain_colors[terrain_id] = img.get_pixel(img.get_width() / 2, img.get_height() / 2)

	for id in terrains:
		var name: String = terrains[id]
		var color: Color = terrain_colors.get(id, Color(0.5, 0.5, 0.5))
		terrain_defs.append('terrain_set_0/terrain_%d/name = "%s"' % [id, name])
		terrain_defs.append("terrain_set_0/terrain_%d/color = Color(%f, %f, %f, 1)" % [id, color.r, color.g, color.b])

	var tres := '[gd_resource type="TileSet" load_steps=3 format=3]\n\n'
	tres += '[ext_resource type="Texture2D" path="%s" id="1"]\n\n' % atlas_path
	tres += '[sub_resource type="TileSetAtlasSource" id="TileSetAtlasSource_1"]\n'
	tres += "texture = ExtResource(\"1\")\n"
	tres += "texture_region_size = Vector2i(%d, %d)\n" % [tile_size, tile_size]
	tres += "\n".join(tile_defs) + "\n\n"
	tres += "[resource]\n"
	tres += "tile_size = Vector2i(%d, %d)\n" % [tile_size, tile_size]
	tres += "terrain_set_0/mode = 0\n"
	tres += "\n".join(terrain_defs) + "\n"
	tres += 'sources/0 = SubResource("TileSetAtlasSource_1")\n'

	var absolute_out := ProjectSettings.globalize_path(output_path)
	var out_dir := absolute_out.get_base_dir()
	if not DirAccess.dir_exists_absolute(out_dir):
		DirAccess.make_dir_recursive_absolute(out_dir)
	var out_file := FileAccess.open(absolute_out, FileAccess.WRITE)
	out_file.store_string(tres)
	out_file.close()
