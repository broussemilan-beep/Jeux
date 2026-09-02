"""
Export d'objets STATIQUES (trone, couronne) comme un vrai Model Roblox
(.rbxmx, XML), au meme format que le KeyframeSequence de
`export_kfseq.py` (schema public du moteur), mais avec des <Item
class="Part"> plutot que des Pose : ce sont des objets de decor, pas des
membres animes par Motor6D.

Convention de coordonnees : MEME repere que le personnage R6 (studs,
-Z = avant, Y = haut) -- le trone est positionne pour que le personnage
assis (voir choreography.py) s'y encastre sans recalage supplementaire.
"""
import xml.etree.ElementTree as ET

_ref_counter = [0]


def _next_ref():
    _ref_counter[0] += 1
    return f"RBXPROP_{_ref_counter[0]:06d}"


def _cframe_element(parent, name, pos, matrix):
    el = ET.SubElement(parent, "CoordinateFrame", {"name": name})
    for tag, val in zip(("X", "Y", "Z"), pos):
        ET.SubElement(el, tag).text = repr(float(val))
    for i in range(3):
        for j in range(3):
            ET.SubElement(el, f"R{i}{j}").text = repr(float(matrix[i][j]))
    return el


IDENTITY = [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]

# Enum.PartType (BasePart.Shape) : les 3 valeurs standard du moteur.
SHAPE_BLOCK = "1"
SHAPE_CYLINDER = "2"
SHAPE_BALL = "0"

# Enum.Material -- valeurs VERIFIEES (pas devinees) le 2026-09-02 depuis
# le dump d'API officiel de Roblox lui-meme, tel que suivi publiquement
# par MaximumADHD/Roblox-Client-Tracker sur GitHub (ce depot ne fait que
# republier le Api-Dump.json que Roblox genere et publie a chaque version
# pour l'outillage tiers -- Rojo, rbxts, etc. l'utilisent tous. Ce n'est
# PAS la meme categorie que les dumps de contenu client/serveur ecartes
# dans rig/PROVENANCE.md : ceci est de la metadonnee d'API que Roblox
# publie lui-meme, pas un asset de jeu redistribue sans licence).
# Sous-ensemble utilise ici ; liste complete dans MATERIAL_BY_NAME.
MATERIAL_BY_NAME = {
    "Plastic": 256, "SmoothPlastic": 272, "Neon": 288,
    "Wood": 512, "WoodPlanks": 528,
    "Marble": 784, "Basalt": 788, "Slate": 800, "CrackedLava": 804,
    "Concrete": 816, "Limestone": 820, "Granite": 832, "Pavement": 836,
    "Brick": 848, "Pebble": 864, "Cobblestone": 880, "Rock": 896,
    "Sandstone": 912,
    "CorrodedMetal": 1040, "DiamondPlate": 1056, "Foil": 1072, "Metal": 1088,
    "Grass": 1280, "LeafyGrass": 1284, "Sand": 1296, "Fabric": 1312,
    "Snow": 1328, "Mud": 1344, "Ground": 1360, "Asphalt": 1376, "Salt": 1392,
    "Ice": 1536, "Glacier": 1552, "Glass": 1568, "ForceField": 1584,
    "Air": 1792, "Water": 2048,
    "Cardboard": 2304, "Carpet": 2305, "CeramicTiles": 2306,
    "ClayRoofTiles": 2307, "RoofShingles": 2308, "Leather": 2309,
    "Plaster": 2310, "Rubber": 2311,
}


def part_item(parent_xml, spec):
    """spec: dict avec name, size(x,y,z), pos(x,y,z), rot(3x3, def. identite),
    shape(SHAPE_*, def. Block), color_rgb((r,g,b) 0-255, def. gris pierre),
    material(nom dans MATERIAL_BY_NAME, def. Plastic), transparency(def 0),
    anchored(def True).

    Color3uint8 (RGB direct) plutot que BrickColor : l'index de palette
    BrickColor n'est pas quelque chose que je peux garantir exact de
    memoire, alors qu'un triplet RGB est sans ambiguite -- ce choix reste
    valable meme maintenant que Material est verifie (les deux proprietes
    sont independantes dans le moteur)."""
    item = ET.SubElement(parent_xml, "Item", {"class": "Part", "referent": _next_ref()})
    props = ET.SubElement(item, "Properties")
    ET.SubElement(props, "string", {"name": "Name"}).text = spec["name"]
    ET.SubElement(props, "token", {"name": "Shape"}).text = spec.get("shape", SHAPE_BLOCK)
    ET.SubElement(props, "bool", {"name": "Anchored"}).text = "true" if spec.get("anchored", True) else "false"
    ET.SubElement(props, "bool", {"name": "CanCollide"}).text = "true" if spec.get("collide", True) else "false"
    ET.SubElement(props, "float", {"name": "Transparency"}).text = repr(float(spec.get("transparency", 0.0)))
    material_name = spec.get("material", "Plastic")
    ET.SubElement(props, "token", {"name": "Material"}).text = str(MATERIAL_BY_NAME[material_name])
    r, g, b = spec.get("color_rgb", (120, 120, 130))
    color_int = (int(r) << 16) | (int(g) << 8) | int(b)
    ET.SubElement(props, "Color3uint8", {"name": "Color3uint8"}).text = str(color_int)
    size_el = ET.SubElement(props, "Vector3", {"name": "size"})
    for tag, val in zip(("X", "Y", "Z"), spec["size"]):
        ET.SubElement(size_el, tag).text = repr(float(val))
    _cframe_element(props, "CFrame", spec["pos"], spec.get("rot", IDENTITY))
    return item


def export_model(parts, model_name, out_path, primary_part=None):
    """parts: liste de specs (voir part_item). Ecrit un <Item class="Model">
    contenant chaque Part, plus PrimaryPart si fourni (nom d'une part)."""
    root = ET.Element("roblox", {
        "xmlns:xmime": "http://www.w3.org/2005/05/xmlmime",
        "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
        "xsi:noNamespaceSchemaLocation": "http://www.roblox.com/roblox.xsd",
        "version": "4",
    })
    model = ET.SubElement(root, "Item", {"class": "Model", "referent": _next_ref()})
    mprops = ET.SubElement(model, "Properties")
    ET.SubElement(mprops, "string", {"name": "Name"}).text = model_name

    part_refs = {}
    for spec in parts:
        item = part_item(model, spec)
        part_refs[spec["name"]] = item.attrib["referent"]

    if primary_part and primary_part in part_refs:
        ET.SubElement(mprops, "Ref", {"name": "PrimaryPart"}).text = part_refs[primary_part]

    tree = ET.ElementTree(root)
    ET.indent(tree, space="  ")
    tree.write(out_path, encoding="utf-8", xml_declaration=True)
    return out_path, len(parts)
