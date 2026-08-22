extends Node
## Autoload "PouvoirRegistry" (amendement GDD confirmé par Milan : 1 seul
## Pouvoir par run, tiré au hasard parmi Invocateur/Monstrification/Terre,
## 5 compétences débloquées progressivement par palier de niveau, ordre
## FIXE par Pouvoir — voir docs/worklog.md pour l'historique des questions
## bloquantes et leur résolution par Milan).
##
## Rôle STRICTEMENT limité à la donnée : charge et met en cache
## data/pouvoirs/<pouvoir_id>.json (même patron que
## VfxRecipeRegistry._load_palette()) et répond à "quelles compétences,
## dans quel ordre, débloquées à quel niveau ?" pour un Pouvoir donné. Ne
## sait RIEN de ce qui est réellement implémenté en jeu (aucune fonction,
## aucun getter de cooldown) — cette connaissance reste dans Player
## (IMPLEMENTED_SKILL_HANDLERS / IMPLEMENTED_SKILL_COOLDOWN_GETTERS),
## seul endroit qui sait vraiment quelles compétences ont du code
## derrière elles. Séparation délibérée : les données de la bible
## (ordre/paliers) peuvent changer sans toucher au code de dispatch, et
## inversement.

const POUVOIR_IDS := ["invocateur", "monstrification", "terre"]

var _cache: Dictionary = {}  # pouvoir_id -> Array[Dictionary] (skills, triées par tier)


## Retourne les 5 compétences du Pouvoir donné, triées par tier croissant
## (index 0 = tier 1 = slot 1). Tableau vide si le fichier est absent/
## invalide — pas de valeur par défaut inventée.
func get_skills(pouvoir_id: String) -> Array:
	if _cache.has(pouvoir_id):
		return _cache[pouvoir_id]
	var skills: Array = _load_skills(pouvoir_id)
	_cache[pouvoir_id] = skills
	return skills


## Compétence occupant le slot `slot_index` (1-based, 1..5) pour le
## Pouvoir donné SI son palier de niveau est atteint — dictionnaire vide
## sinon (slot hors limites, ou pas encore débloqué par le niveau). Ne
## dit rien sur l'implémentation réelle : à combiner côté appelant avec
## la connaissance de ce qui a effectivement une fonction en jeu.
func get_unlocked_skill_for_slot(pouvoir_id: String, slot_index: int, level: int) -> Dictionary:
	var skills: Array = get_skills(pouvoir_id)
	var array_index: int = slot_index - 1
	if array_index < 0 or array_index >= skills.size():
		return {}
	var skill: Dictionary = skills[array_index]
	if level < int(skill.get("unlock_level", 1)):
		return {}
	return skill


func _load_skills(pouvoir_id: String) -> Array:
	var path := "res://data/pouvoirs/%s.json" % pouvoir_id
	if not FileAccess.file_exists(path):
		return []
	var f := FileAccess.open(path, FileAccess.READ)
	var text: String = f.get_as_text()
	var parsed: Variant = JSON.parse_string(text)
	if not (parsed is Dictionary) or not (parsed.get("skills") is Array):
		return []
	var skills: Array = parsed["skills"].duplicate()
	skills.sort_custom(func(a, b): return int(a.get("tier", 0)) < int(b.get("tier", 0)))
	return skills
