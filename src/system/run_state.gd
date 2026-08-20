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
