extends Node
## Autoload "RunState" (H4, GDD §20 : "boucle de run" — "Hub → choisir
## Gate → entrée → combats → XP/loot/maîtrise → route → Elite → Boss →
## récompense → retour → amélioration → nouvelle Gate"). Le seul état
## qui doit survivre un `change_scene_to_file()` Hub<->Gate : niveau/XP/
## PV du joueur.
##
## Un Resource PARTAGÉ plutôt qu'une copie synchronisée à la main à
## chaque transition — Player pointe directement dessus (voir
## Player._ready(), `stats = RunState.player_stats`) au lieu de garder
## sa propre instance par défaut. Aucun risque d'oubli de sync : il n'y
## a rien à synchroniser, c'est le même objet des deux côtés de la
## transition de scène. "Amélioration" (GDD §20) = ce que H1 fournit
## déjà (XP/niveau) qui persiste naturellement ainsi ; un système de
## boutique/équipement reste GDD §16 "à préciser", hors scope ici.

var player_stats: Stats = Stats.new()

## Amendement GDD confirmé par Milan : un seul Pouvoir par run
## (Invocateur, Monstrification OU Terre), tiré au hasard, "pas d'écran
## de sélection à construire, c'est automatique". Terminologie
## explicite de Milan : "Pouvoir", pas "Classe" — à ne pas confondre
## avec character_screen.gd qui affiche volontairement "CLASSE : AUCUNE"
## (règle GDD différente, non concernée par cet amendement, jamais
## touchée ici). Tiré UNE FOIS à l'initialisation de cet autoload,
## exactement le même patron que `player_stats` ci-dessus : aucune
## notion de "début de run" distincte du démarrage du process n'existe
## ailleurs dans le code (aucune fonction new_run()/restart() trouvée),
## donc pas la peine d'en inventer une seulement pour ce tirage. Liste
## des 3 Pouvoirs dupliquée depuis PouvoirRegistry.POUVOIR_IDS plutôt que
## référencée : RunState reste sans AUCUNE dépendance sur les autres
## autoloads (voir commentaire ci-dessus, "Aucune dépendance..."), et un
## champ par défaut se résout à la construction du nœud — avant la
## garantie que les autres autoloads de la liste soient déjà prêts.
var active_power: String = ["invocateur", "monstrification", "terre"].pick_random()


## MANDAT "retours de playtest réel" (point 1, softlock à la mort) — jusqu'ici
## la seule "notion de début de run" de tout le dépôt était l'initialisation
## de cet autoload au démarrage du process (voir commentaires ci-dessus,
## déjà signalé comme un manque). GDD §20 ne prévoit aucun écran de fin pour
## ce cas — comportement minimal choisi (autorisé explicitement par Milan) :
## PV/niveau/XP repartent de zéro (nouveau Stats, même patron que la
## construction ci-dessus) et le Pouvoir est retiré au hasard (même règle
## que l'amendement GDD "un seul Pouvoir par run, tiré au hasard" — une
## nouvelle run tire donc un nouveau Pouvoir, pas nécessairement le même),
## puis retour au Hub (outpost.tscn, `run/main_scene` de project.godot) qui
## sert aussi d'écran de départ. Appelée par Player._process_death_restart()
## une fois l'input de relance détecté.
func start_new_run() -> void:
	player_stats = Stats.new()
	active_power = ["invocateur", "monstrification", "terre"].pick_random()
	get_tree().change_scene_to_file("res://scenes/gameplay/outpost.tscn")
