extends Resource
class_name Stats
## Bloc de stats minimal partagé par Player et Enemy. Volontairement plat —
## rien ici que la tranche verticale Phase 1 n'exige déjà (INT, requis par
## le scaling de dégâts du Totem du Vide ; pas de force/dex/résistances
## tant qu'aucune recette/pouvoir ne les consomme réellement, §5.1
## "aucun appel PixelLab pour une variation que le runtime peut dériver
## d'une forme existante" — même discipline appliquée ici au code : pas de
## stat non exercée).

@export var max_hp: float = 100.0
@export var hp: float = max_hp
@export var int_stat: float = 10.0
@export var move_speed_px: float = 100.0

## H1 (GDD §17/§20/§21 : "XP, niveau, stats" au HUD, boucle de run) —
## FOR/AGI/VIT du bloc de stats GDD §17 restent hors de ce fichier tant
## qu'aucune recette/pouvoir ne les consomme (même discipline que le
## commentaire ci-dessus pour int_stat/move_speed_px) : les ajouter sans
## rien qui les lise serait une stat non exercée.
@export var level: int = 1
@export var xp: float = 0.0

## H5 (GDD §4/§17 : "4 stats LOCKED : FOR, AGI, INT, VIT", écran
## personnage "FOR / AGI / INT / VIT"). Contrairement à int_stat plus
## haut, aucune recette de combat ne lit encore for_stat/agi_stat/
## vit_stat — mais l'écran personnage lui-même EST le consommateur ici :
## le GDD verrouille ces 4 stats et exige explicitement leur affichage,
## donc les laisser absentes serait respecter la lettre de la règle
## "pas de stat non exercée" en trahissant l'exigence GDD qui l'a posée.
## Même croissance linéaire par niveau que int_stat (+1/niveau) —
## câbler un vrai scaling de dégâts (FOR sur Bras-Faux, GDD §7.1) reste
## un chantier séparé, hors scope de l'écran personnage lui-même.
@export var for_stat: float = 10.0
@export var agi_stat: float = 10.0
@export var vit_stat: float = 10.0

signal died
signal leveled_up(new_level: int)


func apply_damage(amount: float) -> void:
	if amount <= 0.0 or is_dead():
		return
	hp = max(0.0, hp - amount)
	if is_dead():
		died.emit()


func is_dead() -> bool:
	return hp <= 0.0


## Formule TUNABLE (H1) — linéaire, simple à vérifier à l'œil : passer du
## niveau N au niveau N+1 coûte 50*N XP.
func xp_to_next_level() -> float:
	return 50.0 * float(level)


## En boucle, pas plafonné à une seule montée par appel : un gros gain
## d'XP (butin de fin de Gate, GDD §20) peut faire sauter plusieurs
## niveaux d'un coup. Chaque niveau : +10 PV max (soigné d'autant, pas
## un simple plafond qui grandit sans rien ressentir) + 1 INT (seule
## stat déjà exercée par une recette réelle, Totem du Vide).
func add_xp(amount: float) -> void:
	if amount <= 0.0 or is_dead():
		return
	xp += amount
	while xp >= xp_to_next_level():
		xp -= xp_to_next_level()
		level += 1
		max_hp += 10.0
		hp += 10.0
		int_stat += 1.0
		for_stat += 1.0
		agi_stat += 1.0
		vit_stat += 1.0
		leveled_up.emit(level)
