# Worklog — Rank Zero

Journal de session, §16.5 de `docs/ARCHITECTURE_VFX_v3.md` : "Fin de
session : mettre à jour docs/worklog.md (fait / branché ou non /
prochain pas). C'est la mémoire inter-sessions — le repo est le cerveau."

**Archives** (MANDAT AUTONOME v3 Phase 4, housekeeping — ce fichier
dépassait 6300 lignes) : les entrées du 2026-08-18 au 2026-08-21 inclus
sont déplacées telles quelles, sans réécriture, dans
`docs/worklog-archive-2026-08-18-a-2026-08-21.md`. Résumé de cette
période, pour ne pas perdre le fil sans tout relire : fondations
(Phase 0-1, squelette gameplay/combo/dash/esquive), monde (mini-tileset,
3 monstres Crawler/Brute/Ranged), Phase T.1 (6 outils autonomes pipeline
Meshy/Blender/pyfxr), Phase 1-4 MANDAT SUITE v2 (éclairage/couleur,
biome PixelLab, Poing Belluaire/Poing Tellurique, son+normal maps+post-
render), retours croisés Gemini/ChatGPT (R1 bug bloquant, R4 feedback
d'impact), zoom caméra, calibration render_detector.py, verrouillage
palette Terre, système Pouvoir/déblocage (RunState.active_power, 5
slots réels), critique probabiliste ("Black Flash"). Ce fichier ne
garde que le 2026-08-22 (MANDAT AUTONOME v3 en cours) — au-delà de
~1500 lignes, archiver la période précédente selon le même principe.

---

## 2026-08-23 — MANDAT ROUND 4, CHANTIER 0 : le losange beige identifié — `arcSlash`, la couche CONTACT de Bras-Faux

**Contexte** : le chantier 1bis (round précédent) a recoloré le
Placeholder en magenta et confirmé le cercle blanc comme
`impactFlashFrame`/`smokePuff`, mais a supposé à tort que le losange
beige visible sur `captures/verification/2026-08-23-diagnostic-
chantier1bis.png` (panneau 2) faisait partie du même node Placeholder
— jamais vérifié explicitement. Milan l'a relevé à raison : cette forme
reste distincte du rectangle magenta ET du cercle blanc, jamais
expliquée.

**Identification, par preuve pixel-exacte, pas par supposition.**
Couleur échantillonnée directement sur le losange dans la capture :
RGB(156, 119, 103), identique sur plusieurs pixels (pas un dégradé).
Calcul de la couleur que produirait `arc_slash.gd` (couche CONTACT de
`power.bras_faux.cast.json`, résolue via le rôle "contact (éclat
organique)" de `data/palettes/parasite.json` : hue=18°, saturation=34%,
value=61%) : `colorsys.hsv_to_rgb(18/360, 0.34, 0.61)` → **RGB(156,
119, 103) — correspondance EXACTE, à l'unité près sur les 3 canaux**.

**Verdict : légitime, pas un bug.** Le losange EST la couche `arcSlash`
de Bras-Faux ("croissant anguleux directionnel... TRACE du geste, pas
le swing d'arme lui-même", `arc_slash.gd`) — déjà documentée, déjà
correctement teintée par la palette. Sa géométrie (croissant à
`BASE_SWEEP≈99°`, `INNER_RATIO=0.45`, 10 segments, direction horizontale
pour un personnage qui fait face à droite) produit à cette
configuration précise une silhouette qui se lit comme un losange/kite
plutôt qu'un "croissant" au sens strict — une observation de LISIBILITÉ
légitime (le nom de la primitive suggère une forme que le rendu actuel
ne donne pas toujours), mais distincte de la question "est-ce un bug" :
ce n'en est pas un, le node produit exactement la couleur/l'intention
documentées pour cette couche.

**Aucun correctif appliqué** (mandat explicite : identifier et
trancher, pas corriger à l'aveugle sur une simple observation de forme
— si la lisibilité de `arcSlash` doit être retravaillée, ce sera un
chantier VFX dédié avec de vraies mesures, pas une réaction à une
question de nommage). Smoke tests non ré-exécutés (aucun fichier
modifié ce chantier).

---

## 2026-08-23 — MANDAT ROUND 3, CHANTIER DÉCOR : outpost éclairé pour la 1ère fois, gate_premiere couvert sur toute sa largeur, test_arena confirmée hors scope

**Contexte** : suite au chantier 1bis (entrée précédente), 3 agents
dédiés ont traité chacun une scène de décor en parallèle. Rappel
explicite du mandat : l'isolation git worktree ne s'applique jamais
vraiment dans cet environnement — le réflexe défensif (`git stash`
avant de commiter si le répertoire n'est pas propre, restituer dès que
détecté) reste la vraie protection. Chaque capture a de nouveau été
ouverte et jugée par le coordinateur avant d'être considérée acquise.

**Agent Décor B — test_arena : vérifié hors scope, aucune dépense.**
Avant toute retouche, l'agent a cherché dans tout le dépôt qui
instancie réellement `test_arena.tscn` : aucun `change_scene_to_file`
ne la cible (seuls `outpost.tscn`⇄`gate_premiere.tscn` sont câblés),
`run/main_scene` du projet vaut `outpost.tscn`, les seules occurrences
du chemin sont des métadonnées d'éditeur Godot ou l'export web qui
embarque toutes les scènes par défaut — recoupé avec 2 mentions déjà
posées par des agents précédents (`docs/worklog-archive-*.md`,
`docs/STATUS.md`, qui la catégorise déjà "bac à sable"). Verdict :
scène de développement pure, jamais vue par un joueur — aucune
retouche visuelle effectuée, aucune génération PixelLab dépensée.
Exactement le comportement demandé par le mandat ("inutile de peaufiner
une scène de debug interne").

**Agent Décor A — outpost : premier passage lumière + un vrai défaut
transversal trouvé.** Audit confirmé : `outpost` n'avait AUCUN
`PointLight2D`, ses 2 braseros (`PropBrazier1/2`) étaient de purs
sprites statiques — même symptôme déjà corrigé sur `gate_premiere` 2
rounds plus tôt. `PointLight2D` ajoutés (texture radiale déjà présente
dans la scène, réutilisée depuis `Player/Glow`, aucun nouvel asset).
L'agent a d'abord copié littéralement les valeurs de `gate_premiere`,
puis MESURÉ (pas jugé à l'œil) que ça sature ~99% du sol local au
bucket haut du posterize partagé (`post_render.gdshader`) — et a
vérifié par mesure croisée que ce même taux de saturation existe DÉJÀ,
à magnitude quasi identique, sur le brasero de `gate_premiere` déjà
accepté par Milan. Conclusion honnête : ce n'est pas une régression
introduite ici, c'est un défaut structurel PARTAGÉ entre les 3 scènes
(`post_render.gdshader` + `floor_terrain.tres` + `CanvasModulate`),
hors du scope d'un mandat "une scène, un agent" — corriger ça pour de
bon nécessiterait un chantier dédié au shader de post-render lui-même.
L'agent a recalibré l'intensité (energy 1.5→0.55, texture_scale
2.4→1.3) pour limiter l'empreinte visuelle du défaut sans prétendre
l'éliminer, et l'a documenté clairement plutôt que de le masquer ou de
le corriger à l'aveugle sur des fichiers partagés hors scope. Aucune
génération PixelLab dépensée (déficit identifié = lumière manquante,
pas variété de props — la densité de props avait déjà été jugée
suffisante 2 rounds plus tôt). Capture :
`captures/verification/2026-08-23-decor-outpost.png` (3 positions
caméra, avant/après). Deux incidents de coordination pendant la
session (modifications effacées deux fois par une opération git d'un
agent parallèle) — réappliquées et committées dès détection, sans
perte au final.

**Agent Décor C — gate_premiere : couverture complète des ~3550px.**
Le round précédent n'avait éclairé qu'un point (entre les portes Combat
et Elite). Mesure réelle (11 captures balayant tout le niveau + HSV)
a identifié 2 zones jamais retouchées et nettement plus sombres que la
moyenne du niveau : la salle de spawn (x=0-768, V moyenne 31,82% —
la plus basse du niveau) et le vide Elite→Boss (x=2048-3100, V moyenne
34-36%). Comblées avec 4 nouveaux props porteurs de `PointLight2D`
(`PropBrazier3`/`PropTorchStand2` en zone spawn,
`PropTorchStand3`/`PropBrazier4` en zone Elite-Boss, ce dernier près de
la salle Rest — effet "foyer de repos" thématique), même recette que le
round précédent, aucun nouvel asset PixelLab nécessaire (textures déjà
chargées). Gain mesuré : +2,4 à +5,3 points de V moyenne sur les 4
zones corrigées. Variété de props du reste du niveau (9 textures
distinctes déjà présentes) jugée suffisante, aucune intervention
PixelLab jugée nécessaire sur ce point. Verdict honnête : la zone
spawn reste légèrement sous les zones déjà éclairées au round
précédent (salle plus grande que la densité de lumière appliquée) — un
3e point lumineux améliorerait encore, non ajouté pour rester
proportionné à l'écart mesuré plutôt que de sur-corriger. Capture :
`captures/verification/2026-08-23-decor-gate_premiere.png` (grille de
8 captures avant/après sur les 4 zones).

**Vérifications finales.** `run_gameplay_smoke_test.sh` et
`run_vfx_recipe_smoke_test.sh` — `all_pass:true` sur chaque commit
individuel ET sur l'état final fusionné des 3 agents. Coût réel total
de ce chantier décor : **0 génération PixelLab, 0 crédit Meshy** — les
3 scènes avaient un déficit de LUMIÈRE (ou, pour test_arena, aucun
déficit pertinent puisque jamais vue), jamais un déficit de contenu
généré justifiant une dépense. Point d'attention pour une session
future, transversal aux 3 scènes : le plafond de bande "decor"
(`data/palettes/value_bands.json`) est structurellement dépassé près
de toute source de lumière à cause du posterize partagé — documenté
dans `docs/STATUS.md`, pas corrigé (ressources partagées, hors scope
d'un mandat par scène).

---

## 2026-08-23 — MANDAT ROUND 3, CHANTIER 1bis : cercle blanc/losange beige tranché définitivement (cas a, légitime — pas un 2e bug)

**Contexte** : cette question traînait depuis 2 rounds — un cercle et une
forme en losange/rectangle de couleur unie apparaissent de façon
cohérente sur plusieurs captures récentes, y compris APRÈS le fix du
chantier 1 (`hit_flash.gdshader`). Mandat explicite : identifier le
node exact producteur de CHAQUE forme, pas une supposition visuelle,
et trancher (a) éléments légitimes vs (b) un second bug distinct.

**Identification, par lecture directe du code, pas par supposition** :
- **Le rectangle/losange** = `scenes/gameplay/enemy.tscn`, node
  `Placeholder` (`Polygon2D`, `polygon = (-10,-40,10,-40,10,0,-10,0)`,
  un simple rectangle 20×40). C'est le nœud visuel de fallback
  d'`enemy.gd` (`_visual = get_node("Visual") if has_node("Visual")
  else get_node("Placeholder")`) — utilisé UNIQUEMENT quand aucun nœud
  "Visual" n'existe. Vérifié : `gate_premiere.tscn` (le seul niveau
  jouable réel) n'instancie QUE `enemy_crawler.tscn`/`enemy_brute.tscn`/
  `enemy_ranged.tscn`, qui ONT tous un nœud "Visual"
  (`AnimatedSprite2D`, vrai art) — le Placeholder n'est donc JAMAIS
  visible en jeu réel. Il n'apparaît que parce que
  `tools/capture_scene.gd` (mode `player_action`, utilisé pour TOUTES
  les captures de fidélité de compétence) instancie par défaut
  `EnemyScene = res://scenes/gameplay/enemy.tscn` (la scène de base,
  sans Visual) pour un test isolé rapide, sans avoir besoin d'un vrai
  monstre.
- **Le cercle** : DEUX identités différentes selon la capture, toutes
  deux légitimes. Sur les captures Bras-Faux/Poing Belluaire (couche
  CONTACT) : `impact_flash_frame.gd`, la primitive "flash blanc"
  documentée depuis le début du projet (§4 : "noyau blanc quasi-plein,
  1-2 ticks"), volontairement proche du blanc (`MAX_VALUE_HSV=0.92`).
  Sur la capture Marée de Sable (couche CONSEQUENCE, tick 30, label
  déjà présent dans l'image committée au round précédent : "smokePuff
  étale le long du trajet") : `smoke_puff.gd`, qui dessine
  `BLOB_COUNT=5` cercles pleins qui se chevauchent avec un faible
  rayon de dispersion (`scale_px * 0.3 * randf()`) — à l'échelle de la
  capture, 5 petits cercles proches fusionnent visuellement en un seul
  blob de couleur unie. C'est EXPLICITEMENT documenté dans le fichier
  lui-même comme un choix de design ("nuage stylisé... PAS un cercle
  dont l'alpha descend à 0... un petit nombre de blobs OPAQUES") — pas
  un bug, juste un VFX procédural pas encore habillé d'un vrai sprite
  (même famille de limite que `beamSegment` avant sa refonte en
  `sandCrest` la session précédente).

**Verdict : CAS (a) sur toute la ligne — aucun 2e bug distinct.** Le
`hit_flash.gdshader` du chantier 1 fonctionne correctement ; les formes
observées sont soit un artefact du RIG DE CAPTURE (le Placeholder,
jamais vu par un vrai joueur), soit du VFX procédural légitime et déjà
documenté comme tel (`impactFlashFrame`, `smokePuff`).

**Action prise** (mandat : "désactive-le par défaut... pour ne plus
polluer les comparaisons", appliqué au cas capture-tool) : le
Placeholder gardait une couleur rouge-brun plausible
(`Color(0.6,0.15,0.15,1)`) qui pouvait se lire comme un choix de
design réel plutôt qu'un stand-in de test — c'est ce qui a nourri la
confusion 2 rounds de suite. Recoloré en magenta vif
(`Color(1,0,1,1)`), la convention universelle "texture manquante/
placeholder" en dev — désormais instantanément reconnaissable comme un
artefact de test, sans ambiguïté possible, dans n'importe quelle
capture future. Changement d'UNE ligne, zéro risque : vérifié qu'aucun
smoke test ni script de mesure (`render_detector.py` et consorts) ne
dépend de sa couleur spécifique (seulement de son NOM de nœud,
`get_node("Placeholder")`). `smoke_puff.gd`/`impact_flash_frame.gd`
non touchés (hors scope, VFX légitime déjà documenté — seront traités
avec leur contenu concerné si/quand ce chantier arrive).

**Preuve** : `captures/verification/2026-08-23-diagnostic-chantier1bis.
png` — 3 panneaux : (1) les 2 captures round 2 qui montraient encore le
losange rose-fauve à l'époque, (2) la même scène Bras-Faux recapturée
avec le Placeholder désormais magenta (non-confondable), (3) rappel de
la capture Marée de Sable identifiant `smokePuff`. Smoke tests
`run_gameplay_smoke_test.sh`/`run_vfx_recipe_smoke_test.sh` :
`all_pass:true`.

---

## 2026-08-23 — MANDAT ROUND 2, CHANTIERS 2/3/4 : Bras-Faux courbé, VFX Terre réellement produit, détail Gueule Vide

**Contexte** : suite au chantier 1 (bug hit-flash, entrée précédente),
3 agents dédiés ont tourné en parallèle (aucun fichier partagé entre
eux) sur les 3 derniers chantiers du "MANDAT ROUND 2". Comme pour le
round précédent, chaque capture a été ouverte et jugée par le
coordinateur lui-même avant tout merge — pas seulement le verdict que
chaque agent écrivait sur son propre travail (règle explicite de
Milan). Ce contrôle a effectivement attrapé un vrai problème (voir
Gueule Vide ci-dessous) avant qu'il ne soit commité.

**Bras-Faux — silhouette refaite en vraie courbe.** Milan avait rejeté
la 1ère version (round précédent) sans détour : "on dirait pas un faux
mais un bras en pointe bizarre" — une tige droite, pas un crochet.
Cause racine identifiée : `animate_character`/`create_character_state`
ne prennent la géométrie que par description TEXTE, insuffisant pour
contraindre une silhouette précise ("courbe en C" en mots retombe sur
une tige qui s'amincit). Corrigé en imposant la géométrie par IMAGE
plutôt que par texte : un guide de silhouette dessiné en PIL (spline
qui revient explicitement vers l'intérieur en fin de tracé, un vrai
crochet) patché sur une frame existante de l'état transformé, nettoyé
en pixel art via `edit_image` (préserve corps/tête, ne touche que le
bras), puis utilisé comme `custom_start_frame_url`/`end_frame_url` de
`animate_character` pour ancrer la courbe aux deux extrémités de
l'animation plutôt que de la laisser à la seule interprétation du
modèle. Vérifié par le coordinateur sur la capture committée
(`captures/verification/2026-08-22-fidelite-bras_faux-v2.png`) : la
courbe en C/crochet est nettement visible et stable sur les 6 frames,
sans exception, aucune arme/artefact parasite — confirme le rapport de
l'agent. Coût : 69 générations PixelLab (2 exploratoires + 3
`edit_image` de nettoyage + 1 `animate_character`).

**Terre — VFX réellement produit, plus seulement des primitives
rescalées.** Milan ne se contentait plus du "modeste" du round
précédent. Diagnostic confirmé par capture réelle (pas hypothèse) :
`beamSegment` (Marée de Sable) restait une rangée de quads plats
malgré l'accent `fractureLine` ajouté au round précédent ; le nuage de
poussière résiduel restait collé aux pieds du joueur au lieu de suivre
le trajet de la vague. Corrections : nouvelle primitive VFX
sprite-based `sand_crest.gd` (silhouette PixelLab, teintée
dynamiquement par la palette comme toute autre primitive — jamais de
couleur figée dans le PNG) qui remplace `beamSegment` ; nouveau champ
optionnel `origin_offset_px` par couche dans `vfx_recipe_registry.gd`
(défaut `0.0`, non-régression vérifiée sur les 4 autres recettes
vivantes) qui permet d'étaler `dustKick`/`smokePuff` le long du trajet ;
`dust_kick.gd` corrigé (même classe de bug que l'ancien `converge.gd` :
taille de particule proportionnelle à `scale_px` au lieu d'une
constante fixe). `ground_ring.gd` (Poing Tellurique) inspecté et jugé
suffisant après évaluation réelle, non retouché (pas de retouche par
défaut). Vérifié par le coordinateur : le cœur de la vague est
maintenant un vrai sprite à pointes acérées, la poussière est
visiblement étalée sur 2 points distincts du trajet plutôt que collée
à un seul endroit — confirme le rapport de l'agent, le mot "modeste" ne
s'applique plus. Coût : 2 générations PixelLab (`create_image_pixflux`,
1 rejetée). Anomalie constatée par l'agent (hors son contrôle, non
touchée) : des fichiers Gueule Vide se sont modifiés sur le disque
partagé en cours de route (activité concurrente de l'agent Gueule
Vide, stashés proprement puis restitués par le coordinateur — voir
plus bas, aucune perte).

**Gueule Vide — passe de détail, avec un faux-départ intercepté avant
commit.** Objectif : ajouter de la richesse (crocs irréguliers, gouttes
multiples, texture) à la composition en S déjà validée (round
précédent), sans y toucher. Le PREMIER essai de l'agent a échoué
silencieusement : son propre rapport initial affirmait "silhouette
intacte, 0 pixel supprimé" sur la base d'un diff pixel-exact du GUIDE
d'entrée — mais le coordinateur, en ouvrant lui-même la capture
committée, a repéré que le corps rendu en v3 avait un plan clairement
différent du v2 (une forme compacte avec une queue enroulée, pas le
même tendon en S avec plus de détail dedans). Flag envoyé à l'agent
AVANT tout commit. Root cause trouvée par l'agent une fois relancé :
(1) un bug d'implémentation — le script de guide relisait par erreur
un fichier déjà écrasé par une sortie rejetée au lieu du guide v2
propre ; (2) même corrigé, des taches de texture et une chaîne de
gouttelettes placées dans l'écart entre le pied du tendon et le splash
d'encre séparé avaient été interprétées par `create_image_pixflux`
(strength 120) comme des indices de continuité/volume, fusionnant les
deux éléments en une fausse "queue". Corrigé : guide reconstruit depuis
le vrai v2 (`git show`), texture réduite à de fines stries, gouttes
avec marge de collision vérifiée, plus aucun ajout dans la zone
pied/splash. Re-vérifié cette fois par analyse en composantes connexes
(silhouette principale et splash doivent rester 2 composantes séparées
sur les 7 frames) + profil de largeur (écart ≤2px avec v2 à chaque
rangée) AVANT de commiter — pas seulement un diff du guide d'entrée.
**Leçon retenue, documentée dans le code** : un diff pixel-exact du
guide ne garantit PAS que la sortie générée par PixelLab l'a suivi
fidèlement ; il faut vérifier la sortie réelle (composantes connexes,
profil de forme), pas seulement l'entrée qu'on lui a donnée. Résultat
final vérifié par le coordinateur sur `captures/verification/
2026-08-23-fidelite-gueule_vide-v3.png` : la silhouette en S est bien
restaurée à l'identique de la v2, crocs irréguliers et gouttes
supplémentaires visibles, splash toujours détaché du corps — confirme
le rapport corrigé de l'agent. Coût : ~73 générations PixelLab au
total pour cette passe (essai rejeté + reprise).

**Collision d'agents (même limite déjà documentée au round
précédent).** Les 3 agents ont de nouveau opéré sur le même répertoire
partagé `/workspace/jeux` (l'isolation git worktree demandée ne s'est
appliquée à aucun des 3). L'agent Terre, ayant besoin d'un arbre de
travail propre pour commiter, a rencontré les fichiers non commités de
l'agent Gueule Vide (encore en cours) et les a mis de côté proprement
via `git stash` plutôt que de les écraser ou les perdre — bon réflexe
défensif. Le coordinateur a restitué ce stash (`git stash pop`) dès
que détecté, avant que l'agent Gueule Vide ne reprenne la main ;
vérifié qu'aucun fichier n'a été perdu (untracked files, notamment la
capture déjà produite, jamais affectés par le stash). Aucune perte de
travail au final, mais ce mode de collaboration (répertoire partagé,
pas de vraie isolation) reste fragile et demande une vigilance active
du coordinateur à chaque round.

**Vérifications finales.** `scripts/run_gameplay_smoke_test.sh` et
`scripts/run_vfx_recipe_smoke_test.sh` — `all_pass:true` sur l'état
final fusionné (les 3 chantiers + le fix du chantier 1), re-testé une
dernière fois après merge de tous les commits. Coût total mesuré
(compte PixelLab réel, `get_balance`) : 522/2000 générations
consommées ce cycle (1478 restantes) — 73 générations pour ce lot de 3
chantiers ; une ventilation exacte par agent n'est pas fiable (3 agents
concurrents sur le même compte partagé, deltas individuels qui se
chevauchent), donc seul le total réel mesuré est retenu. 0 crédit
Meshy consommé.

---

## 2026-08-22 — MANDAT ROUND 2, CHANTIER 1 : le bug "rectangle blanc" était réel, pas un artefact de capture — root cause trouvée et corrigée

**Contexte** : sur les captures `2026-08-22-fidelite-bras_faux.png` et
`-poing_belluaire.png` (mandat précédent), un cercle et un rectangle
blancs pleins flottent près du personnage. Le même bug de rectangle
blanc avait déjà été "corrigé" 2 sessions plus tôt (`hit_flash.gdshader`,
TEXTURE→COLOR) — Milan, à raison, ne faisait plus confiance à un simple
"c'est déjà réglé" et demandait un vrai diagnostic AVANT toute
correction : est-ce le rig de capture (`enemy.tscn`, Placeholder
Polygon2D générique, jamais spawné en jeu réel) ou un vrai bug qui
toucherait aussi les vrais monstres (Crawler/Brute/Ranged, sprite réel) ?

**ÉTAPE 1 — méthode.** Ajout d'un paramètre diagnostic
`--enemy_scene=<...>` à `tools/capture_scene.gd` (mode `player_action`,
additif, défaut inchangé = `EnemyScene`/Placeholder) pour rejouer
EXACTEMENT le même pouvoir/tick avec une vraie scène de monstre
(`enemy_brute.tscn`, vrai `AnimatedSprite2D`) au lieu du Placeholder.
Premier essai sans `--level=3` : rien ne se passait (le slot power2
était verrouillé au niveau par défaut, Bras-Faux ne se déclenchait
jamais — erreur de méthode de ma part, pas une observation utile).
Corrigé, relancé avec `--level=3` (Bras-Faux déverrouillé, tier 2) :
**le même carré blanc plein apparaît, à l'identique, sur le vrai
Brute** (silhouette réelle rendue en aplat blanc uni, aucune trace de
sa couleur/texture). Conclusion de l'ÉTAPE 1, sans ambiguïté : **PAS un
artefact du rig de capture** — un vrai bug de gameplay, visible sur
n'importe quelle cible réelle touchée.

**ÉTAPE 2 — cause précise.** Le 1er fix (TEXTURE→COLOR) était
nécessaire mais un second bug, distinct, restait dessous. Lu
`src/gameplay/hit_response.gd` + `src/gameplay/combat_feedback.gd` :
`flash_sprite()` met `flash_amount=1.0` puis le décroît sur
`HitResponse.FLASH_TICKS` (4) — MAIS `HitResponse._physics_process()`
ne décrémente ce compteur QUE si `not CombatFeedback.is_frozen()` (choix
délibéré antérieur, documenté : une minuterie cosmétique doit "rester
synchrone avec l'impact"). Or le hit-stop "medium" (Bras-Faux/Poing
Belluaire, `TARGET_HITSTOP_MS["medium"]=62ms`) dure ~4 ticks lui aussi —
quasiment le même nombre que `FLASH_TICKS`. Pendant TOUTE cette fenêtre
gelée, `flash_amount` reste ÉPINGLÉ à 1.0 (jamais décrémenté) : la
cible rend un aplat blanc opaque PLEIN, sans aucune trace de sa couleur
réelle, pendant toute la durée du gel (~65ms, largement perceptible) —
pas un bref flash d'un tick comme prévu. `impact_flash_frame.gd`
(primitive VFX séparée, le cercle) respecte déjà une règle documentée
ailleurs dans ce projet (`MAX_VALUE_HSV=0.92`, §3 : "jamais blanc pur,
V=100%, collision UI/décor") — `hit_flash.gdshader` était le seul module
à l'ignorer, allant jusqu'à 1.0 plein.

**ÉTAPE 3 — correctif appliqué.** `src/vfx/shaders/hit_flash.gdshader` :
ajout d'une constante `MAX_FLASH_MIX=0.6` qui plafonne la CONTRIBUTION
effective du mélange (`mix(COLOR.rgb, vec3(1.0), flash_amount *
MAX_FLASH_MIX)`) plutôt que sa cible — à `flash_amount=1.0` (pic, y
compris gelé pendant tout un hit-stop), la cible garde encore ~40% de
sa propre couleur/texture au lieu de disparaître sous un aplat uni.
Valeur choisie par lecture visuelle directe des captures avant/après
(pas un calcul) : assez haute pour rester un vrai flash lisible, assez
basse pour ne jamais effacer complètement la silhouette. Effet
secondaire positif, non cherché mais bienvenu : les chiffres de dégâts
(`damage_number.gd`, texte blanc) étaient invisibles sur fond blanc
plein pendant le flash — ils redeviennent lisibles avec le fond
partiellement teinté.

**Vérification** : capture avant/après committée
(`captures/verification/2026-08-22-fix-hit-flash-round2.png`, 4
panneaux — Brute réel avant/après, scène Bras-Faux avant/après) montrant
la même comparaison sur le vrai monstre ET sur le Placeholder de test.
`scripts/run_gameplay_smoke_test.sh` et
`scripts/run_vfx_recipe_smoke_test.sh` — `all_pass:true` avant et après
le correctif (aucun check n'exerçait ce cas précis — gel + flash au pic
— donc rien ne l'attrapait avant ce diagnostic manuel). Verdict honnête :
corrigé à la racine (root cause identifiée, pas un contournement local),
mais `MAX_FLASH_MIX=0.6` reste une valeur choisie à l'oeil — à
retoucher si Milan la juge encore trop discrète ou trop marquée sur le
prochain build réel.

---

## 2026-08-22 — Coordination multi-agent (4 mandats dédiés) : Gueule Vide S-composition, audit Terre, sprites dédiés Bras-Faux/Poing Belluaire

**Contexte** : suite au mandat d'audit précédent (entrée ci-dessous), Milan
a envoyé 4 mandats séparés conçus pour exécution parallèle par agent
dédié, chacun restreint à ses propres fichiers de compétence, plus un
document de coordination fixant la seule contrainte de collision réelle
(`data/palettes/parasite.json`, partagée Bras-Faux/Poing Belluaire —
à ne jamais lancer en même temps) et une instruction explicite sur le
budget : aucun plafond arbitraire PixelLab/Meshy, "un agent qui
s'arrête après une tentative faible... livre un échec évitable, pas
une économie." Exécuté : Gueule Vide + Terre + Bras-Faux en parallèle
(aucun fichier en commun entre eux), Poing Belluaire retenu jusqu'à la
fin confirmée de Bras-Faux et la confirmation explicite dans son
rapport que `parasite.json` n'avait pas été touché.

**Gueule Vide — 2e passe, composition en S.** La 1ère régénération
(entrée précédente) avait corrigé l'identité (mâchoire+tendon, zéro
jambe) mais produisait une composition FRONTALE/symétrique, pas la
composition dynamique en S de la référence (tendon qui jaillit en
diagonale du sol, mâchoire excentrée au sommet). Corrigé par un nouveau
guide de silhouette synthétique dessiné explicitement en S (tracé
polygonal bas-gauche → milieu-droite → haut-gauche, mâchoire EXCENTRÉE
avec mandibules asymétriques) réinjecté dans le même pipeline prouvé
(guide → `create_image_pixflux` strength 120 → `create_character`
v3+reference → `animate_character` v3, 6 frames sud). Résultat vérifié
sur les 8 rotations ET les 6 frames d'animation (pas seulement frame 0)
: le tendon part bien du sol en biais, se recourbe deux fois, la
mâchoire penchée est nettement excentrée — jamais un ovale frontal
centré. Limite honnête documentée : contrairement à la 1ère version qui
fragmentait littéralement en points épars sur les 2 dernières frames,
cette 2e version fait un cycle ouverture/fermeture/réouverture sans
effritement dessiné (compensé par la couche VFX `shardBurst` existante)
— hors scope de ce mandat qui portait sur la composition, pas
l'animation. Canvas cuit élargi de 48×48 à 56×72 (la composition en S
est plus haute que l'ancienne mâchoire frontale compacte, rognée en
haut sur l'ancien canvas carré). `FRAME_TICK_BOUNDS` inchangé (le
mapping tenait déjà). Coût : 3 générations PixelLab (pixflux 1 +
create_character v3 1 + animate_character v3 1). Capture :
`captures/verification/2026-08-22-fidelite-gueule_vide-v2.png`.

**Terre — audit d'abord, correctifs de recette ensuite.** Verdict de
Milan ("nul à chier") volontairement pas détaillé techniquement, à
diagnostiquer avant toute régénération. Vérifié en premier : Cendre
reste bien en posture de combat normale sur la planche de référence
(pas de changement corporel) — donc PAS un manque de sprite dédié
(contrairement à Bras-Faux/Poing Belluaire), le problème est ailleurs.
Diagnostic précis trouvé : un vrai BUG DE TIMING STRUCTUREL sur Poing
Tellurique — `groundRing.end_tick` (18) était exactement égal au
`start_tick` des couches de contact, donc l'anneau disparaissait pile
au moment de l'impact ; une capture au tick 35 montrait un écran
totalement vide là où la référence montre l'anneau qui persiste sur
les temps 3-4. Corrigé (recette JSON uniquement, aucune génération) :
`groundRing` scale_px 26→42 et end_tick 18→40, `converge` scale_px
26→34 + count 9, `dustKick` scale_px 16→28 et end_tick 26→30, nouvelle
couche `impactStar` (tick 19-34, scale_px 40). Marée de Sable :
`converge` scale_px 22→30 + count 9, 3 nouvelles couches
`fractureLine` à seeds distincts, `dustKick`/`smokePuff` intensité et
fenêtre temporelle augmentées ; `beamSegment` non retouché (déjà lié à
la vraie hitbox). `data/palettes/terre.json` : seule l'extension du
champ `usage` du rôle "contact" pour matcher les 2 nouvelles couches
— aucune valeur numérique changée, palette verrouillée respectée.
Deux bugs transversaux trouvés, documentés mais NON corrigés (hors
scope d'un mandat Terre) : `dust_kick.gd` a le même défaut de taille de
particule fixe que l'ancien bug `converge.gd` (déjà corrigé, session
précédente) ; le moteur VFX n'a qu'un seul `origin` par run partagé par
toutes les couches d'une recette — aucun offset par couche, ce qui
empêche par exemple le nuage de poussière résiduel de Marée de Sable de
suivre le trajet de la vague (limite architecturale, pas un bug de
recette). Verdict honnête : Poing Tellurique "nettement amélioré, plus
embarrassant" (pas une parité pixel, les grains de poussière restent
petits) ; Marée de Sable "modestement amélioré, pas transformé" — le
vrai gap (texture de crête de sable jaggy sur `beamSegment`) n'est pas
résolu par du réglage seul, nécessiterait un changement moteur ou une
nouvelle primitive VFX sprite-based. Coût : 0 génération PixelLab (recette
JSON uniquement). Captures : `captures/verification/
2026-08-22-fidelite-poing_tellurique.png` et `-maree_de_sable.png`.

**Bras-Faux — premier sprite de transformation réel.** Jusqu'ici
`_start_bras_faux()` rejouait littéralement `coup2`, le combo de base à
mains nues. Approche : `create_character_state` sur le character_id de
Cendre RÉELLEMENT en jeu (piège trouvé et évité : un ancien
character_id avec cape existait encore sur PixelLab, mais le vrai
personnage en jeu depuis "R3 — régénération v3 sans cape" est
différent — vérifié via `git log -- cendre_frames.tres` avant tout
appel, une 1ère génération sur le mauvais character_id a été jetée,
coût non récupéré) pour muter le bras droit en membre organique
articulé rouge-brun, puis `animate_character` v3 (6 frames sud). Une
1ère passe d'animation a été rejetée pour hallucination d'arme (faucille
bleu pâle flottante — même défaut déjà documenté sur coup1/coup3),
corrigée par reformulation du prompt sans aucun mot d'arme + exclusion
négative explicite ("no weapon, no glow, no light trail"). Bug de
cuisson trouvé : le rendu brut sortait ~1,5× trop grand pour le canvas
64×64 partagé (tête/pieds tronqués), corrigé par un facteur de
redimensionnement LANCZOS mesuré empiriquement (pas un script généraliste
qui aurait écrasé le manifeste entier — un script ponctuel qui fusionne
la nouvelle entrée). Verdict honnête : le bras est réellement
transformé, silhouette nettement allongée, clairement distinct du
poing normal du combo ET de la masse ronde attendue pour Poing
Belluaire — mais l'écart avec la référence reste réel (planche : faucille
courbée avec crochet net et texture tendon/chair détaillée ; résultat :
plus proche d'une tige/lame anguleuse, moins "articulé"). Jugé
suffisant après 2 itérations plutôt que de multiplier les tentatives à
rendement incertain. Coût : 56 générations PixelLab (2×
`create_character_state` dont 1 jeté sur le mauvais personnage, 2×
`animate_character` dont 1 rejeté pour hallucination d'arme).
`data/palettes/parasite.json` lu et vérifié conforme, NON modifié.
Capture : `captures/verification/2026-08-22-fidelite-bras_faux.png`.

**Poing Belluaire — sprite dédié, lancé après confirmation que
Bras-Faux ne toucherait plus `parasite.json`.** Même méthode que
Bras-Faux, avec le character_id de Cendre vérifié en amont cette fois
(`get_character` avant tout appel, piège déjà connu évité directement).
`create_character_state` pour fusionner bras+poing droit en masse
ronde/compacte de muscle et chair enflée (canvas source élargi à
64×84 pour la place nécessaire), puis `animate_character` v3 (6 frames
sud, prompt court + exclusion négative dès le premier essai — aucune
hallucination d'arme, accepté sans reroll). Deux bugs de cuisson
trouvés et corrigés par mesure : facteur d'échelle LANCZOS 0,6375 pour
le canvas partagé 64×64 (personnage source haut de 80px) ; ancrage pied
élargi en pleine largeur pour 1 frame sur 6 (pose de fente large où la
bande de recherche centrée du pied était trop étroite pour des jambes
très écartées). Verdict honnête : silhouette nettement large/ronde, à
l'opposé de la silhouette longue/fine de Bras-Faux — comparaison directe
faite dans la capture, aucune confusion possible à l'écran (point de
vérification principal du mandat, satisfait). Écart réel avec la
référence : la planche montre une projection du poing plus loin devant
le corps en diagonale avec une texture de grappes/griffes plus
marquée ; le résultat reste une masse plus compacte, près du corps.
Coût : 22 générations PixelLab (1 `create_character_state` + 1
`animate_character`, aucun reroll nécessaire). Aucun appel Meshy sur
les 4 mandats de cette entrée (pipeline 2D PixelLab suffisant partout).
Capture : `captures/verification/2026-08-22-fidelite-poing_belluaire.
png` (4 panneaux, incluant Bras-Faux pour contraste de silhouette).

**Fusion et vérifications.** Les 4 agents ont opéré sur le même
répertoire de travail partagé (l'isolation git worktree demandée ne
s'est pas appliquée à cet environnement pour 3 des 4 agents — seul
Terre a réellement travaillé dans un clone isolé, poussé séparément
puis mergé) ; chacun n'a commité que ses propres fichiers scopés,
vérifié après coup (aucun chevauchement, aucune collision constatée sur
`parasite.json` ni ailleurs). Fusion dans l'ordre Gueule Vide → Bras-Faux
→ Terre (merge propre, aucun conflit, fichiers disjoints) → Poing
Belluaire (poussé directement en fast-forward par son propre agent).
`scripts/run_gameplay_smoke_test.sh` et `scripts/run_vfx_recipe_smoke_test.sh`
— `all_pass:true` après chaque étape de fusion, re-testé une dernière
fois sur l'état final poussé (`origin/main` à `5f03ff0`). Coût total
mesuré (compte PixelLab réel, `get_balance`) : 449/2000 générations
consommées ce cycle (1551 restantes) — ~83 générations pour cette
entrée complète (Gueule Vide 3 + Terre 0 + Bras-Faux 56 + Poing
Belluaire 22 + quelques appels de vérification), aucun plafond
arbitraire appliqué, conformément à l'instruction de Milan. 0 crédit
Meshy consommé.

---

## 2026-08-22 — MANDAT AUDIT FIDÉLITÉ RÉFÉRENCES : Gueule Vide cassé confirmé et régénéré, converge.gd corrigé, 3 gaps documentés honnêtement

**Contexte** : Milan soupçonnait, sans pouvoir vérifier lui-même (Git LFS
hors de portée réseau de son côté), que le sprite réel de Gueule Vide ne
ressemblait plus à sa planche de référence. Mandat : auditer chaque
compétence vivante (ressemblance ET comportement) contre sa planche,
dans l'ordre Gueule Vide → Bras-Faux/Poing Belluaire → Poing Tellurique/
Marée de Sable → combo de base → 3 monstres, corriger ce qui est cassé
avant de continuer, documenter honnêtement le reste.

**Point 1 — Gueule Vide : CASSÉ, confirmé et corrigé.** Les 6 frames
réelles (`assets/processed/sprites/gueule_vide/cast/*.png`) montraient
une petite créature à jambes/tête ronde façon mannequin générique —
zéro mâchoire, zéro croc, aucune ressemblance avec la planche (une
gueule d'encre béante SANS jambes ni bras, juste une mâchoire sur un
tendon d'encre). Confirmé par comparaison côte à côte agrandie (8x).
Cause racine trouvée en relisant `data/pixellab_usage.jsonl` : la
création d'origine utilisait `body_type` par défaut (humanoïde) ET une
référence downscalée à 24x22px/8 couleurs (pour tenir sous le seuil de
troncature MCP, ~1-2 Ko de base64) — bien trop dégradée pour transmettre
"mâchoire sans corps" au générateur, qui est retombé sur un archétype de
créature générique.

Corrigé par une regénération complète (`data/pixellab_usage.jsonl`,
entrées 2026-08-22T21:0x) : (1) guide de silhouette synthétique dessiné
par script (mouth+crocs+tendon, SANS jambes, 40x40px, largement sous le
seuil de troncature) ; (2) passé dans `create_image_pixflux` (img2img,
1 crédit) pour obtenir un vrai rendu pixel art ombré plutôt que le guide
brut tel quel (une créature en v3+reference se contente de FAIRE
PIVOTER l'image donnée, elle ne la restylise pas — leçon retenue,
importante pour toute régénération future via ce chemin) ; (3) ce
rendu servi comme référence à `create_character` mode v3 (8 directions,
1 crédit) ; (4) `animate_character` v3 (direction sud, 6 frames, 1
crédit) pour le cast. Nouvelle séquence : frames 0-2 mâchoire grande
ouverte/crocs visibles, frame 3 = la morsure (fermeture nette, plus
sombre), frames 4-5 = désintégration en fragments d'encre épars —
sémantique légèrement différente de l'ancienne (frame2 tient
maintenant la grande ouverture au lieu de frame3, frame3 est la morsure
au lieu de frame4) : `src/gameplay/powers/gueule_vide.gd::
FRAME_TICK_BOUNDS` réajusté en conséquence, CONTACT_TICK inchangé.
Anciennes frames/référence archivées dans `assets/source/pixellab/
gueule_vide/_archive_2026-08-18_v1/` (jamais supprimées). Cuisson via
`scripts/cook_character_frames.py` (48x48, foot-margin 4px). Smoke test
complet relancé (`all_pass:true`, tous les checks `gueule_vide_*`
passent). Comparaison finale committée : `captures/verification/
2026-08-22-fidelite-gueule_vide.png`.

**Point 2 — Bras-Faux/Poing Belluaire : trou d'outillage resitué + vrai
bug trouvé et corrigé.** Le "trou d'outillage" de la session précédente
(capture ne rendant aucune couche VFX) s'est avéré être DEUX choses
distinctes, pas un vrai trou :
- Bras-Faux : erreur de ma part — `data/pouvoirs/monstrification.json`
  (verrouillé par Milan) place Bras-Faux en TIER 2 (slot `power2`,
  unlock_level=3), pas tier 3 comme `docs/STATUS.md` le laissait croire
  (désaccord entre les deux fichiers — `data/pouvoirs/*.json` fait
  autorité, STATUS.md sera à corriger). Capturé au bon slot : la couche
  `ribbonTrail` est bien là, visible.
- Poing Belluaire (slot `power1`, correct dès le départ) : VRAI bug
  trouvé dans `src/vfx/primitives/converge.gd` — taille de fragment
  câblée en dur (2.0-4.5px) SANS RAPPORT avec `scale_px` de la recette.
  Dès que `scale_px` dépasse ~20px (Poing Belluaire = 30, Poing
  Tellurique = 26), les fragments deviennent des points de quelques
  pixels, imperceptibles à l'échelle réelle du jeu — confirmé par
  capture zoomée (avant : rien de visible ; après inspection à la loupe :
  de minuscules taches). Corrigé : taille proportionnelle à `scale_px`
  (~22-36% au lieu d'une constante fixe). `shardBurst` a la même
  formule fixe mais reste lisible car ses fragments VOYAGENT sur un
  grand arc (`speed_px_per_tick`) — `converge` les garde près de
  l'origine toute leur vie, rien ne compense une taille trop petite.
  Capture avant/après confirmée. Contenu VISUEL de Bras-Faux/Poing
  Belluaire reste un placeholder documenté (`_sprite.play("coup2"/
  "coup3")`, "art dédié à la transformation hors scope") — comparé à la
  planche (bras qui devient une faux organique articulée), ce n'est PAS
  fidèle, mais c'est un GAP DE PRODUCTION CONNU depuis le départ, pas
  une régression : nécessiterait un vrai sprite de transformation de
  bras, hors scope d'une session de correctifs. Comportement (arc,
  multi-cible, portée) déjà smoke-testé conforme.

**Point 3 — Poing Tellurique/Marée de Sable : même bug, déjà
documenté.** La recette `power.poing_tellurique.cast.json` elle-même
(`expected_layers[1].description`) flaguait DÉJÀ ce problème depuis une
session antérieure (render_detector.py, R4/R2) : "converge... signal à
peine perceptible... À RE-INVESTIGUER... pas encore tranché." Résolu
par le même correctif `converge.gd` — capture avant/après confirmée
(anneau + fragments désormais nettement visibles). Marée de Sable
(`beamSegment`) déjà lisible sur capture antérieure, non retouché.

**Point 4 — Combo de base (3 coups) : pas de planche dédiée, mais
soupçon de Milan confirmé.** Comparaison frame-par-frame de coup1/coup2/
coup3 (`assets/processed/sprites/cendre/coup{1,2,3}/*.png`) : poses
quasi identiques à chaque index de frame correspondant, AUCUNE arme
visible sur aucun des 3 coups (Cendre semble frapper à mains nues sur
tous les frames), seule coup2 a un lean/une posture plus dynamique à
mi-animation. Confirme "interchangeables" — pas un bug de code, un gap
de contenu (les 3 coups n'ont jamais eu de poses ni d'arme dédiées
différenciées). Pas de fix appliqué cette session : ampleur = nouvelle
génération d'assets (poses distinctes + arme visible pour 3 animations
existantes), pas un correctif ponctuel, et aucune planche de référence
n'existe pour guider un remake. Documenté pour une session dédiée
future.

**Point 5 — 3 monstres (Crawler/Brute/Ranged) : mandat basé sur une
prémisse fausse.** Le mandat supposait une planche de concept art dans
`experiments/` pour ces 3 monstres. Vérifié dans `data/meshy_usage.
jsonl` : "texte pas d'image reference disponible pour ces monstres" —
génération 100% texte-vers-3D, AUCUNE image de référence n'a jamais
existé pour Crawler/Brute/Ranged. Impossible d'auditer une "fidélité"
contre une référence qui n'existe pas. Recadré en vérification de
cohérence INTERNE (idle vs marche, même créature, pas de rig cassé) :
les 3 monstres sont visuellement cohérents entre repos et marche
(silhouette/couleur/échelle stables, cycle de membres réel visible) —
aucun défaut trouvé, mais ce n'est pas la même question que celle posée
par le mandat.

**Vérifications finales** : `scripts/run_gameplay_smoke_test.sh` et
`scripts/run_vfx_recipe_smoke_test.sh` — `all_pass:true` après chaque
changement (regénération Gueule Vide, fix converge.gd). Budget PixelLab
de cette entrée : 4 générations (guide→pixflux 1cr, create_character
v2 1cr [rejeté], create_character v3 1cr, animate_character 1cr) — la
tentative v2 est restée un personnage orphelin sur PixelLab, non
utilisée en jeu, non supprimée (coût nul à la laisser).

---

## 2026-08-22 — Retour Milan sur PREMIÈRE VIDÉO réelle : 6 points, dont build web resté périmé

**Contexte critique découvert en premier** : Milan répète quasi mot pour
mot les points 1 et 2 de l'entrée précédente (rectangle blanc, trou de
vérification), déjà corrigés et poussés (commit `318df6b`). Cause
trouvée : `docs/index.pck` (build web joué par Milan) datait de 19h19,
soit UNE HEURE AVANT le fix du shader (20h15) — Milan a regardé une
vidéo du build PÉRIMÉ, pas de l'état réel du dépôt. Pas un nouveau bug,
un rappel que "commité" ≠ "joué" tant que le build web n'est pas
redéployé. Leçon retenue : redéployer `docs/index.html`/`index.pck` en
DERNIÈRE étape de toute session touchant du visuel, jamais oublié entre
un fix et la prochaine vérification de Milan.

**Point 3 — torche/lumière de porte rendue dans la zone des boutons
tactiles (bug réel, nouveau).** Root cause : `scenes/ui/touch_controls.
tscn` place ses boutons dans une bande écran fixe (native 640×360,
y≈205-370) qui, à `BASE_ZOOM=0.8`, correspond à une bande du MONDE assez
basse pour contenir le sol/les props/la lumière des portes (vérifié par
capture `--mode=scene` caméra centrée sur la torche de la porte Elite,
x=1800-2048) — les boutons sont des icônes semi-transparentes SANS fond
opaque, donc tout ce qui passe par cette bande de l'écran (n'importe
quel élément du monde, pas spécifiquement "une torche") reste visible
au travers. Fix : `Background` (ColorRect plein, `Color(0.08,0.06,0.05,
1.0)`, `mouse_filter=IGNORE`) ajouté en premier enfant de
`TouchControls`, couvrant toute la bande boutons — testé d'abord à
alpha 0.82 (insuffisant, un halo de lumière très intense reste
partiellement visible même à travers un fond à 82% d'opacité), corrigé
à 1.0 (masquage total confirmé par capture). `captures/verification/
2026-08-22-touch-ui-bleed-{avant,apres}.png`. Smoke test inchangé
(`all_pass:true`) — pur ajout visuel, aucune logique touchée.

**Point 4 — principe d'écart de lisibilité VFX (nouvelle règle
générale, pas un cas isolé).** Diagnostic de Milan confirmé par mesure :
`data/palettes/value_bands.json` documente déjà le sol ambiant réel
(~24-37% V, jusqu'à ~78% en bord de halo de torche) — les 2 rôles les
plus visibles de `invocateur_vide` (bleu pâle 72%V, gris-lilas 55%V)
recouvraient très exactement cette bande : même écart de teinte, aucun
écart de LUMINANCE avec le sol le plus lumineux, d'où l'effet "qui ne
perce pas" que Milan décrit sur Gueule Vide. Relevés à 90/85% V et 55/
50% saturation (toujours sous le plafond VFX 92%, teinte inchangée,
identité de Classe intacte) — capture avant/après confirmée (`captures/
verification/2026-08-22-vfx-contraste-gueule-vide-{avant,apres}.png`).
Audit des 4 autres compétences implémentées avant généralisation,
comme demandé par Milan :
- **Poing Tellurique/Marée de Sable (`terre`, VERROUILLÉE)** : capture
  réelle confirme que `groundRing` restait à peine visible MÊME après
  le premier correctif R4 documenté dans ce fichier de palette — hue
  quasi identique au sol (32° vs ~35-38° mesuré) ne laisse QUE value/
  saturation comme levier pour une matière qui doit rester "terre" par
  nature (contrairement à Invocateur, la teinte ne peut pas s'éloigner
  sans casser l'identité). 2e correctif : 52→80% V, 46→65% saturation
  sur le rôle "signature 1" uniquement (le seul confirmé faible par
  capture) — `captures/verification/2026-08-22-vfx-contraste-
  tellurique-{avant,apres}.png`, nette amélioration visible. Rôles
  contact/poussière non touchés (déjà lisibles sur la capture Marée de
  Sable).
- **Bras-Faux/Poing Belluaire (`parasite`, réécrite from reference
  2026-08-22 même journée)** : PAS auditables cette passe — l'outil de
  capture (`--mode=player_action --action=power1/power3`) n'a rendu
  AUCUNE couche VFX aux ticks testés (6/10/18), alors que `Poing
  Belluaire`/tier1 est censé être débloqué dès le niveau 1. Cause non
  encore identifiée (décalage tick recette vs tick capture différent de
  celui qui marche pour `terre`/`invocateur_vide` ? condition de portée
  non remplie par le rig de capture ?) — flag explicite : ceci est un
  TROU D'OUTILLAGE, pas une conclusion sur la lisibilité réelle de ces
  2 compétences. Palette `parasite` volontairement non retouchée sans
  preuve visuelle (elle vient d'un échantillonnage direct des 5 planches
  de référence officielles le jour même — la retoucher à l'aveugle
  romprait la fidélité à la référence que Milan a validée). À reprendre
  en priorité la prochaine session avant tout nouveau travail sur ces
  2 compétences.

**Point 5 — monde encore plat malgré la Phase 1 (Addendum C).** Cause :
un seul `CanvasModulate` global (teinte uniforme sur TOUT le niveau) +
seulement 3 `PointLight2D` (les torches de porte Combat/Elite/Boss,
espacées de 650 à 1050px) sur un niveau large de ~3550px — les 2
braziers et le porte-torche déjà présents dans le décor (Phase 1,
MANDAT AUTONOME v3) étaient de PURS sprites décoratifs, aucune lumière
réelle. Exactement le symptôme que Milan décrit : des props ajoutés
mais aucune variation lumineuse. Fix : `PointLight2D` (texture radiale
déjà utilisée par les torches de porte) ajouté en enfant de
`PropBrazier1`, `PropBrazier2` (orange-feu, energy 1.5, rayon 2.4×) et
`PropTorchStand1` (or pâle, energy 0.85, rayon 1.3×) — comble
spécifiquement le grand vide entre la porte Combat (x=768) et la porte
Elite (x=2048) où rien n'éclairait avant. Capture large (caméra
x=1500) avant/après : dôme de lumière chaude visible sur le sol là où
il n'y avait qu'un ton plat avant — `captures/verification/
2026-08-22-monde-lumiere-{avant,apres}.png`. `AmbientWarmth`
(CanvasModulate) et Addendum C non touchés, comme demandé (ne pas
assombrir le monde, ajouter de la variation LOCALE en plus). `outpost.
tscn`/`test_arena.tscn` non repris cette passe (hors scope, la vidéo de
Milan montre `gate_premiere`) — à faire si Milan le demande.

**Point 6 — première capture d'un impact réel commitée.** Aucune
capture existante (avant cette session) ne montrait un coup qui touche
réellement un ennemi. `--mode=player_action --action=attack --tick=12`
(2 ennemis positionnés devant/à 30° comme le smoke test) : capture
montre les 2 ennemis en plein flash de hit (teinte réelle qui
transparaît sous le blanc, pas un bloc opaque — le fix du point 1 tient
aussi en combo réel, pas seulement en isolation) + une étincelle
d'impact. `captures/verification/2026-08-22-combo-impact-reel.png`.

**Vérifications finales** : `scripts/run_gameplay_smoke_test.sh` et
`scripts/run_vfx_recipe_smoke_test.sh` — `all_pass:true` après CHAQUE
changement de cette entrée (shader/UI/palettes/scène), pas seulement à
la fin. Build web (`docs/index.html`/`index.pck`) redéployé en tout
dernier, après tous les fixes ci-dessus — pour que la PROCHAINE vidéo
de Milan reflète enfin l'état réel du dépôt, pas un état d'il y a
plusieurs commits.

---

## 2026-08-22 — Retour Milan sur captures réelles : bug flash blanc + trou de vérification

**Contexte** : 1er retour de Milan sur de vraies captures du jeu en
exécution (jamais reçu avant sur ce projet). Trois points, priorité
explicite de Milan : "le rectangle blanc cassé" d'abord, puis le trou
de vérification, puis (hors scope de cette entrée, pas commencé) un
passage lumière/chaleur sur le monde.

**Point 1 — bug résolu.** Deux rectangles blancs pleins flottant à côté
du joueur sur les captures de Milan. Hypothèse de Milan (traînée/
afterimage, Addendum B) vérifiée et écartée : `_spawn_afterimage()`
dans `player.gd` garde déjà `if texture == null: return` et copie la
vraie frame du joueur. Vraie cause trouvée en réexaminant mes propres
captures de vérification de cette session (Phase 3, Poing Belluaire et
Marée de Sable) : le MÊME bug y était déjà visible, mais mal
diagnostiqué comme "juste les mannequins placeholder génériques" sans
creuser pourquoi ils étaient blancs alors que leur couleur définie est
rouge sombre. Cause réelle : `src/vfx/shaders/hit_flash.gdshader`
ré-échantillonnait `texture(TEXTURE, UV)` directement au lieu de lire
l'entrée `COLOR` déjà pré-calculée par Godot. Pour un `AnimatedSprite2D`
texturé ça fonctionne (TEXTURE = la vraie texture). Pour un `Polygon2D`
sans texture assignée — le mannequin générique d'`Enemy`
(`scenes/gameplay/enemy.tscn`) ET `boss_gate_maw.tscn`, tous deux
présents dans des scènes de jeu réelles (`gate_premiere`, `test_arena`),
pas seulement des mannequins de test — Godot lie `TEXTURE` à sa texture
blanche 1×1 par défaut : `tex.rgb`/`tex.a` valaient TOUJOURS `(1,1,1,1)`
quel que soit `flash_amount`, d'où un rectangle blanc opaque plein, sans
fondu, ignorant la couleur réelle du polygone. Fix d'une ligne : lire
`COLOR` (déjà texture×modulate pour un sprite, couleur de vertex×
modulate pour un `Polygon2D` sans texture) au lieu de re-sampler
`TEXTURE` — corrige les deux cas sans branche `if` ni régression pour
les sprites déjà corrects. Vérifié : `godot4 --headless --rendering-
driver vulkan --import` propre, `scripts/run_gameplay_smoke_test.sh`
toujours `"all_pass":true` (les 3 checks `hit_response_*` passent).
Capture avant/après, même scène (`--mode=player_action --action=power1
--active_power=monstrification --level=1 --tick=30`) :
`captures/verification/2026-08-22-hit-flash-fix-avant.png` (rectangles
blancs pleins) vs `2026-08-22-hit-flash-fix-apres.png` (teinte rose/
rouge du polygone qui transparaît sous le flash, comme attendu).

**Point 2 — trou de vérification corrigé.** Milan : "aucune capture de
vérification n'a jamais été committée", malgré des dizaines de mentions
"vérifié par capture" dans ce worklog. Vérifié : exact. La règle "seules
les captures approuvées sont commitées" existait dans `.gitignore`
depuis le début mais n'avait jamais été suivie en pratique — tout
partait dans `/captures_local/` (gitignoré). `data/labels/
quality_labels.jsonl` (verdicts `accept`/`reject` de Milan sur une
référence d'asset, §13.2 `ARCHITECTURE_VFX_v3.md`) est structurellement
le mauvais mécanisme pour une preuve ponctuelle de correction de bug —
il attend un verdict humain formel, pas une preuve immédiate. Nouvelle
convention, documentée dans `CLAUDE.md` et `.gitignore` : toute capture
citée comme preuve va dans `captures/verification/` (réellement
committé), nommée `<date>-<sujet>.png`, dans le MÊME commit que le
changement qu'elle prouve. `data/labels/quality_labels.jsonl` garde son
rôle initial inchangé (verdict Milan uniquement, jamais écrit par
Claude Code).

**Point 3 — non commencé, volontairement.** Milan a explicitement
ordonné de traiter 1 et 2 avant toute nouvelle feature. Passage lumière/
chaleur du monde (Addendum C) à faire dans une session/entrée
séparée, avec sa propre capture avant/après committée.

**Fichiers touchés** : `src/vfx/shaders/hit_flash.gdshader` (fix),
`.gitignore` + `CLAUDE.md` (convention de capture), `captures/
verification/2026-08-22-hit-flash-fix-{avant,apres}.png` (nouveau
dossier, 1res captures réellement committées du projet).

---

## 2026-08-22 — MANDAT SUITE v2 : Phase 3 (Poing Belluaire + Poing Tellurique)

**Blocage rencontré puis levé.** Avant d'écrire du code, recherche
systématique (agent lecture seule) du contenu GDD/Bible pour "Poing
Belluaire"/"Monstrification" et "Poing Tellurique"/"Terre" : ZÉRO fiche
existante dans `docs/RANK_ZERO_MASTER_GDD.md` ni `docs/
PRODUCTION_MANDATE_v1.md` — seule une mention de titre de phase dans ce
worklog. Or le mandat lui-même (§3, matrice de décision) flague
explicitement "nouvelle matière/palette signature pour un Pouvoir/
Classe sans signature définie" et "tout contenu narratif/monde non
explicitement fourni" comme "à valider — s'arrêter, flaguer" — deux
pouvoirs sans AUCUNE fiche qualifient clairement pour cet arrêt.
Documenté comme tel, en attente. Milan a alors transmis
`RANK_ZERO_POWER_SKILL_BIBLE_v0.4.docx` ("Fiches de production
gameplay" des 15 compétences, principe/enchaînement/interactions par
compétence, "valeurs exactes à équilibrer avant verrouillage") — lu via
python-docx (pandoc absent de l'environnement), débloquant la brique.
Le blocage a duré le temps de la recherche, pas une session complète :
dès la Bible reçue, le contenu manquant (mécanique/visuel qualitatif)
était disponible, seules les valeurs numériques exactes restaient
ouvertes — exactement le statut "TUNABLE" déjà appliqué à Bras-Faux.

**Découverte de continuité importante** : la Bible v0.4 classe
Bras-Faux SOUS la Classe "Monstrification" (pas "Parasite" isolément
comme l'appelait le mandat v1) — Poing Belluaire, deuxième compétence
de cette même famille, n'est donc PAS un "pouvoir sans signature" :
`data/palettes/parasite.json` est réutilisée telle quelle (roles 1 et 3
étendus dans leur champ `usage` pour couvrir `converge`/`impactStar` en
plus de `ribbonTrail`/`arcSlash`/`impactFlashFrame` — jamais un nouveau
`palette_id`). "Terre" en revanche est une Classe réellement nouvelle
(zéro fiche antérieure) : `data/palettes/terre.json` est une PROPOSITION
de première passe, dérivée directement du principe donné ("sable,
terre, roche, poussière et gravats" — rien au-delà), documentée comme
non verrouillée dans son propre champ `notes`, à valider par Milan comme
signature de Classe avant que les 4 autres compétences Terre à venir
(Marée de Sable, Éperon, Carapace, Effondrement) ne s'appuient dessus.

**Poing Belluaire** (`FOR | Tier 2 | Impact lourd`) : même archétype de
cast que Bras-Faux — exécuté PAR le joueur, pas une entité invoquée —
mais recodé comme un NOUVEL archétype `melee_impact` (distinct de
`melee_sweep`) puisqu'un "seul coup frontal très lourd" n'est pas un
balayage. Implémenté dans `player.gd` en miroir exact de la timeline
`_start_bras_faux()/_advance_bras_faux()/_end_bras_faux()/
_try_hit_bras_faux()` (même discipline ANTICIPATION/RELEASE/RECOVERY,
`_action_lock` pendant toute l'action, cooldown après RECOVERY) :
50 ticks (20/4/26, plus lent que Bras-Faux 40 ticks pour vendre le
poids), portée 40px/demi-angle 30° (plus courte et plus étroite qu'un
balayage), dégâts 16 (> combo/Bras-Faux, "peut interrompre les attaques
faibles"), recoil_strength_px 40 (> défaut 24, "forte valeur de
recul"), hitstop "heavy" (vs "medium" pour Bras-Faux). Toutes ces
valeurs sont TUNABLE (non chiffrées par la fiche v0.4, même statut que
Bras-Faux) — choisies dans les bandes de tuning déjà posées (autonome,
§3 de la matrice). Recette `data/recipes/power.poing_belluaire.cast.json` :
`converge` (anticipation, la masse qui grossit dans le poing) +
`impactStar`+`impactFlashFrame` (contact) — pas de couche "core" de
traînée, un coup frontal n'a pas de mouvement à tracer contrairement au
balayage de Bras-Faux (différence honnête entre archétypes plutôt
qu'une couche copiée sans raison). Placeholder visuel : anim "coup3"
(le plus lourd des 3 coups du combo, art dédié à la transformation du
poing hors scope recette+logique, même discipline que "coup2"/Bras-Faux).

**Poing Tellurique** (`FOR | Tier 2 | Corps-à-corps/impact`) : même
archétype `melee_impact`. Timeline 42 ticks (18/4/20). Portée 44px/
demi-angle 40°, dégâts 14 (entre Bras-Faux et Poing Belluaire — la fiche
ne porte aucun qualificatif "forte"/"très lourd" pour celui-ci),
hitstop "medium". Recette `data/recipes/power.poing_tellurique.cast.json` :
`groundRing` (anticipation, la terre qui se fissure/remonte au sol) +
`converge` (core, la matière qui converge dans le poing, chevauche la
fin de l'anticipation) + `impactFlashFrame` (contact) + `dustKick`
(contact/conséquence, "éclats/poussière", seule couche `degradable`).
Bug de sens trouvé et corrigé AVANT le smoke test (relecture du code de
`dust_kick.gd`, pas après coup) : `direction` y est interprété comme "le
sens du DÉPLACEMENT qui cause le contact" et projette les éclats à
l'opposé — correct pour un pas/dash qui laisse de la poussière derrière
lui, FAUX pour un impact de poing qui doit projeter ses éclats DEVANT.
Seule cette couche lit `direction` dans la recette (vérifié dans
`ground_ring.gd`/`converge.gd`/`impact_flash_frame.gd` : aucun des trois
ne le fait) — `_start_poing_tellurique()` passe donc `-facing` au lieu
de `facing` au niveau de l'appel `VfxRecipeRegistry.play()`, sans
risque pour les 3 autres couches. Placeholder visuel : anim "coup1"
(distinct de "coup2"/Bras-Faux et "coup3"/Poing Belluaire).

**Intégration** : nouvelles actions d'input `power3` (touche T) et
`power4` (touche G) dans `project.godot` ; boutons tactiles
`ButtonPower3`/`ButtonPower4` ("PW3"/"PW4") dans `touch_controls.tscn`,
positionnés à gauche du joystick (aucune zone tactile existante
chevauchée) ; icônes de cooldown `Power3`/`Power4` dans `hud.tscn` (la
zone `Cooldowns` élargie de 160 à 186px de large pour accueillir 6
icônes au lieu de 4, toujours dans les 640px du viewport) + getters
`get_poing_belluaire_cooldown_ratio()`/`get_poing_tellurique_cooldown_ratio()`
lus par `hud.gd`. Capture en jeu réel (`test_arena.tscn`) confirmée :
6 icônes de cooldown visibles sans chevauchement, boutons tactiles PW3/
PW4 distincts.

**Bug de smoke test trouvé et corrigé** (pas un bug de gameplay réel,
mais une leçon de méthode) : les 2 premiers essais de tests
`_check_poing_belluaire()`/`_check_poing_tellurique()` échouaient sur
la cible latérale (et pour Belluaire, même la cible frontale) — debug
print a montré que la position du joueur dérivait d'environ 15px dès le
1er tick de l'anticipation, alors que `velocity = Vector2.ZERO` est
posé explicitement chaque tick. Cause : les ennemis de test étaient
placés à seulement 25-28px du joueur (plus près que les 30px utilisés
par le test Bras-Faux), chevauchant probablement leur collider au
spawn — `move_and_slide()` résorbe cette interpénétration dès le
premier appel, indépendamment de la vélocité demandée, ce qui suffisait
à faire sortir une cible tout juste à la limite du cône (30-31°). Fixé
en alignant la distance de spawn sur les 30px connus sans problème de
Bras-Faux et en resserrant les angles latéraux de test (12°/18° au lieu
de 15°/25°) pour garder de la marge des deux côtés plutôt que de couper
au plus juste. `scripts/run_gameplay_smoke_test.sh` : 100% vert (2
nouveaux triplets de checks : démarrage+anim, multi-cible dans l'arc
sans toucher hors-arc, fin+déverrouillage+cooldown bloque un second
cast — même couverture que Bras-Faux).

**Archétypes de cast (mandat production v1 §5)** : `melee_impact` est
un NOUVEL archétype introduit par cette brique (distinct de
`melee_sweep`/Bras-Faux et `invocation`/Gueule Vide) — 3 archétypes
concrets existent maintenant sur 4 nommés par le mandat ("projection
avant" et "canalisation" restent à 0 exemple, primitives disponibles
`beamSegment`/`spiral` mais aucune compétence documentée ne les
réclame ; pas d'invention pour combler ce vide).

**Preuve d'invocation mobile : reportée, non bloquante.** Le mandat la
conditionne à "quand une compétence Invocateur retourne" — aucune des
5 fiches Invocateur de la Bible v0.4 (Gueule Vide, Serpent Creux,
Corbeau Pâle, Poing du Colosse, Œil Sans Regard) ne décrit de
déplacement libre/suivi ("Aucune IA de suivi... aucun déplacement
libre" reste la règle §0 du principe Invocateur) : rien à prouver
avec le contenu actuellement fourni. Flag documenté, pas une invention
pour occuper le créneau.

**Statut Phase 3 : Poing Belluaire et Poing Tellurique terminés
(logique + recette + palette + intégration + tests). Archétypes de
cast : 3/4 couverts par du contenu réel. Invocation mobile : reportée,
en attente de contenu Invocateur pertinent.** Prochaine étape : Phase 4
(le monde — parallaxe, props, densification, Cendre 8-directions).

## 2026-08-22 — MANDAT SUITE v2 : Phase 4 (le monde — partie gratuite)

**Reconnaissance avant écriture** (agent lecture seule) : `outpost.tscn`
a déjà un vrai `Parallax2D` "FarBackground" ; `test_arena.tscn` n'en
avait AUCUN ; `gate_premiere.tscn` avait un "FarBackground" qui
RESSEMBLAIT au bon pattern mais était un simple `Node2D` statique (pas
de défilement parallax réel). Seulement 5 textures de props existent
(`prop_rubble`, `prop_debris`, `prop_brazier`, `prop_pillar`,
`prop_rubble_warm`), aucune variante peinte — la variété vient déjà de
transforms moteur (`PropRubble2` = `PropRubble1` mirroré, convention
documentée worklog.md:2780). Aucun script de "densification" procédurale
n'existe : les props sont posés à la main dans chaque `.tscn`. Cendre
n'a de couverture 8-directions que pour idle/déplacement (`coup1/2/3`,
`dash`, `hurt`, `mort` restent mono-direction) — et n'a JAMAIS eu de
pipeline Blender (contrairement aux 3 monstres Meshy) : c'est un
turnaround PixelLab pur, donc "rotation caméra sur le modèle déjà
riggé" ne s'applique pas à Cendre tel quel. Le mandat production v1 §6
(item E) traite déjà explicitement le mono-direction des animations de
combat comme une issue acceptable ("dash/combo/esquive si budget
PixelLab, sinon flag"), pas un défaut à corriger à tout prix.

**Décision de scope** : cette session traite la partie GRATUITE de
Phase 4 (aucune génération PixelLab/SpriteCook, uniquement réemploi
moteur de l'art existant) — parallaxe + densification. Compléter Cendre
en 8 directions de combat (dash/coup1-3/hurt/mort, soit ~7 directions
supplémentaires × 6 animations) et ajouter de nouvelles variantes de
props/texture de mur relèvent d'une génération PixelLab qui n'est PLUS
un "lot ponctuel habituel" (mandat production v1 §3, matrice de
décision — item explicitement "à valider"). Solde vérifié avant de
décider : PixelLab 1644 générations restantes sur 2000 (abonnement actif,
reset 2026-09-14), SpriteCook 27 crédits seulement. Le solde PixelLab
est confortable, mais engager plusieurs centaines de générations pour
compléter Cendre est une dépense de production réelle sur l'abonnement
de Milan, pas une décision purement technique — flaguée ci-dessous
plutôt qu'engagée en autonomie.

**Parallaxe** : `gate_premiere.tscn` — converti le `Node2D`
"FarBackground" existant en vrai `Parallax2D` (`scroll_scale =
Vector2(0.55, 1)`, même valeur qu'`outpost.tscn`) : les 6 sprites
`BgArch1-3`/`BgPillar1-3` déjà en place défilent maintenant plus
lentement que le premier plan sur ce long corridor, au lieu de rester
statiques — correction de cohérence avec le pattern déjà établi, pas un
nouveau système. `test_arena.tscn` — n'avait aucun décor lointain :
ajouté un `Parallax2D` "FarBackground" (même `scroll_scale`) avec 3
sprites réemployant `bg_ruin_arch.png`/`bg_pillar_silhouette.png` (zéro
nouvel asset), un de chaque de part et d'autre de l'arène plus une arche
centrale, à l'échelle 0.34 (cohérent avec 0.38 dans les 2 autres scènes,
légèrement réduit car cette arène est plus resserrée).

**Densification (test_arena uniquement)** : c'était la scène la plus
pauvre en props (3 seulement, contre 13 dans `gate_premiere.tscn` et 4
dans `outpost.tscn`) — portée à 6 en réemployant les textures déjà
importées : `PropDebris2` (mirror de `PropDebris1`, même convention que
`PropRubble2`), `PropRubble3` (échelle 0.85 pour varier la silhouette
sans nouvel art), et `PropPillar1` — première utilisation de
`prop_pillar.png` dans cette scène (déjà chargé par le projet via
`outpost.tscn`/`gate_premiere.tscn`, aucun coût). `gate_premiere.tscn`
et `outpost.tscn` non touchés : déjà densément peuplés (13 et 4 props
sur des surfaces bien plus petites que `test_arena`), ajouter encore
aurait surchargé sans bénéfice de lisibilité.

**Vérification** : `--import` headless propre, `scripts/
run_gameplay_smoke_test.sh` 100% vert (aucun des changements ne touche
au gameplay). Capture des 2 scènes modifiées : `test_arena.tscn` montre
l'arche en arrière-plan et les nouveaux props visibles sans
chevauchement du HUD/des boutons tactiles ; `gate_premiere.tscn` inchangé
visuellement à l'écran (le `Parallax2D` ne change le rendu qu'en
mouvement de caméra, pas sur une capture statique) mais sans erreur de
scène après la conversion de type de nœud.

**Statut Phase 4 (partie gratuite) : terminé.** Reste EN ATTENTE
(dépense PixelLab significative, montant à convenir avec Milan avant
d'engager) :
- Cendre 8-directions complètes pour dash/coup1/coup2/coup3/hurt/mort
  (actuellement mono-direction, GDD amendement §1 section E l'autorise
  explicitement comme fallback).
- Nouvelles variantes de props / texture de mur (aucune texture de mur
  n'existe actuellement, seulement des textures de sol).
Ces deux points ne sont pas oubliés — ils sont documentés ici comme
prochaine décision de production, pas silencieusement ignorés.

## 2026-08-22 — Retour croisé Gemini/ChatGPT sur clip réel : Phase R1 (bug bloquant)

**Contexte** : Milan a fait analyser un clip de gameplay réel par deux
IA indépendantes (Gemini, ChatGPT), plus un bug trouvé par Claude en
lisant le code. Traitement en ordre STRICT imposé par Milan : R1 d'abord
(bloquant), redeploy, puis R2 (vérifier avant corriger), R3/R3bis
attendent la validation de Milan sur un nouveau clip.

**Bug** : `project.godot`, action `"attack"` — héritée de la Phase 1.4
("une seule touche + clic gauche suffisent pour une tranche verticale
testée en headless"), elle portait un `InputEventMouseButton` sans zone
restreinte (`button_mask=1`, aucune position). Contrairement à un
`TouchScreenButton` (qui a sa propre `CollisionShape2D` et ne réagit
que dans sa zone), ce binding déclenchait l'action sur N'IMPORTE QUEL
clic/toucher de l'écran — sur le build web tactile, ça veut dire
qu'un touché n'importe où (déplacement au joystick compris, si le doigt
glisse) pouvait déclencher une attaque. Root cause confirmée par simple
lecture du binding, pas par reproduction manuelle.

**Fix** : retiré l'event `InputEventMouseButton` de `attack`, gardé
uniquement `InputEventKey` (espace) + le `TouchScreenButton` dédié
(`ButtonAttack`, câblé via son propre `action = "attack"`, jamais
affecté par ce retrait). Vérifié explicitement (lecture directe de
`[input]`) qu'aucune autre action (`power1-4`, `dash`, `dodge`,
`character_screen`) ne porte de binding souris généraliste — "attack"
était un cas isolé, pas un pattern répété.

**Test de régression permanent** : `scripts/run_gameplay_smoke_test.sh`
utilise `Input.action_press()` partout, qui CONTOURNE l'InputMap — un
test headless classique n'aurait donc jamais détecté ce bug ni sa
régression. Ajouté `_check_input_map_has_no_stray_mouse_bindings()`
(`tools/smoke_test_gameplay.gd`) : inspecte directement
`InputMap.action_get_events()` pour les 8 actions gameplay et échoue si
l'une d'elles porte un `InputEventMouseButton` — verrouille ce bug
précis contre un retour silencieux (ex. un futur remap qui
réintroduirait un binding généraliste).

**Labels power1-4 illisibles** (Gemini + Milan) : "PWR"/"PW2"/"PW3"/"PW4"
ne distinguent rien du tout entre eux au premier coup d'œil et ne disent
rien sur la compétence réelle. Renommés selon l'identité de chaque
pouvoir (GV = Gueule Vide, BF = Bras-Faux, PB = Poing Belluaire, PT =
Poing Tellurique) sur les 2 endroits qui les affichent
(`touch_controls.tscn` boutons tactiles, `hud.tscn` icônes de cooldown)
— même préfixe que le joueur retrouvera plus tard dans un éventuel menu
de compétences. Contraste ajouté (`font_outline_color` noir,
`outline_size` 2-3) + taille légèrement augmentée (boutons tactiles
12->14px, HUD 9->10px) pour rester lisible sur des fonds très variés
(sol, ennemis, VFX derrière) — vérifié par capture, nettement plus
lisible qu'avant.

**Vérification** : `--import` headless propre, `scripts/
run_gameplay_smoke_test.sh` 100% vert (nouveau check inclus). Capture
en jeu réel confirmant les nouveaux labels lisibles avec contour.

**Statut Phase R1 : terminé.** Redeploy web à suivre. Phase R2 (déjà
fournie par Milan, méthodologie "vérifier avant de corriger") démarre
dans la foulée — voir entrée suivante. Phase R3/R3bis restent en
attente du nouveau clip de Milan après ce redeploy, comme demandé.

## 2026-08-22 — Retour croisé Gemini/ChatGPT sur clip post-R1 : Phase R4 (feedback d'impact, priorité unique)

Les deux analyses convergent après R1 : le bug d'input est bien corrigé,
mais "aucun contenu supplémentaire tant que le combat ne frappe pas" —
un seul chantier cette passe, carte/monstres/HUD/migration Cendre non
touchés (consigne explicite de Milan).

**1. Système de hit commun (le plus important).** `CombatFeedback`
faisait déjà le hit-stop de façon centralisée mais SYMÉTRIQUE (même
durée des deux côtés du conflit) et 4-5 appels séparés par site
(`trigger_hitstop`/`trigger_shake`/`Sfx.play`/`CameraDirector.
trigger_punch()` à la main, avec des trous confirmés par audit :
Gueule Vide sans shake ni camera-punch, les 4 attaques de boss sans SFX
ni camera-punch, le projectile de Ranged avec un hitstop/shake codés en
dur et jamais branchés sur son propre `configure()`). Refonte :
- `TARGET_HITSTOP_MS`/`ATTACKER_HITSTOP_MS` (deux tables, cible
  toujours plus longue que l'attaquant — asymétrie demandée par les deux
  analyses) remplacent l'ancienne table symétrique unique.
- Deux compteurs de gel séparés (`_player_freeze_ticks_remaining` /
  `_enemy_freeze_ticks_remaining`, routés par `attacker_is_player`) au
  lieu d'un seul — chaque camp consulte SON compteur
  (`is_player_frozen()`/`is_enemy_frozen()`), `is_frozen()` (OR des deux)
  reste dispo pour les usages génériques (décroissance cosmétique du
  shake/punch-zoom).
- `register_hit(hitstop_weight, attacker_is_player, sfx_event, shake_weight,
  shake_direction, camera_punch)` : point d'entrée UNIQUE, un appel par
  site de contact (combo 3 coups, Bras-Faux, Poing Belluaire, Poing
  Tellurique, Gueule Vide, les 4 attaques d'Enemy, les 4 attaques du
  boss, le projectile de Ranged) — comble tous les trous de l'audit sans
  rien retirer aux nuances déjà testées (coup léger sans camera-punch,
  etc, via les paramètres optionnels).

**2. Recul par poids d'ennemi.** Mécanique neuve : `recoil_multiplier`
(export par entité, jamais 0.0) multiplie le `recoil_strength_px` que
l'attaquant transmet à `take_damage()` — avant cette brique, le recul
subi ne dépendait QUE de l'attaquant, jamais de qui étai touché. Réglé
sur les 3 tiers demandés : Crawler (léger) 1.6, Ranged (léger-moyen)
1.4, Brute (lourd) 0.35, boss (lourd) 0.3 — jamais statique, toujours un
minimum de recul visible même sur les poids lourds.

**3. Télégraphe visuel ennemi.** Le mécanisme de pulse existait déjà
(`_pulse_telegraph_color()`, lerp progressif vers blanc, tick-driven)
mais ne s'appliquait qu'aux `Polygon2D` (mannequin générique + boss) —
les 3 archétypes jouables (Crawler/Brute/Ranged), en `AnimatedSprite2D`,
n'avaient RIEN, confirmant le trou signalé ("logique présente, rien à
l'écran"). Étendu via `self_modulate` sur la branche `AnimatedSprite2D`
— même mécanisme, pas un second langage visuel, cohabite sans conflit
avec le shader d'contour existant (modulate multiplie par-dessus la
sortie COLOR d'un shader canvas_item).

**4. Poids du combo.** Root motion sur les 3 coups : déjà spécifié et
câblé depuis J1 (`_apply_combo_root_motion()`, lecture data-driven de
`cendre.json`) — vérifié, PAS un trou, juste une couverture de test plus
étroite que le câblage réel. Coup3 (finisher) : anticipation+récupération
allongées via `COMBO_TIER_ANTICIPATION_TICKS`/`COMBO_TIER_RECOVERY_TICKS`
(nouveaux tableaux par tier, tier1/2 inchangés) + un keyframe squash
"étirement" pendant l'anticipation (silhouette qui se charge avant le
coup, jamais vu sur coup1/2) dans `cendre.json`.

**5. Terre (Poing Tellurique) — vérifié par capture avant de toucher au
code**, même méthodologie que Gueule Vide/C1 : `tools/capture_scene.tscn
--mode=player_action --action=power4` à plusieurs ticks. Verdict :
`groundRing` et `dustKick` sont bien rendus (pas un bug de rendu) mais
`groundRing` était quasiment invisible contre le sol neutre (value 38%/
saturation 28%, palette `terre.json` "signature 1") — contraste remonté
(52%/46%), scale_px/durée déjà corrects dans la recette, rien d'autre
retouché.

**6. Contour bleu + sol — vérifié par capture zoomée réelle avant de
retoucher.** La capture confirme le diagnostic de Gemini : à alpha=1.0/
largeur=1.0 (`player_fx.gdshader`), le contour peint en plein n'importe
quel texel voisin d'un pixel semi-transparent — sur un sprite aussi
petit remonté à l'échelle du jeu, ça sature toute la silhouette en bloc
bleu au lieu d'un trait fin (§10.1 : allié = bleu, jamais une
recoloration). Alpha réduit à 0.6, largeur à 0.6 — reste un contour
visible (capture après/avant comparée), plus une recoloration complète.
Sol de `gate_premiere`/`test_arena` : NON touché cette passe — R4 a
prioritisé le système de hit commun et les 2 vérifications par capture
demandées explicitement (Terre, contour), pas eu le temps de reprendre
le tileset avant la fin de cette passe ; reste ouvert pour la
prochaine, la teinte/saturation exacte étant une décision esthétique
(Addendum C) à trancher avec une capture dédiée plutôt qu'en aparté ici.

**7. Secondaire (chiffres de dégâts en arc, zoom caméra A/B) : NON
traité cette passe**, comme prévu par Milan ("si le temps le permet
après 1-6") — priorité donnée au système de hit commun et aux 2
vérifications par capture explicitement demandées.

**Bug trouvé en cours de route (pas dans le mandat, découvert en
testant le système de hit commun) :** `VfxRecipeRegistry._physics_process()`
gelait encore sur le générique `is_frozen()` (OR des deux compteurs)
alors que `gueule_vide.gd` (et tous les autres appelants de `play()`,
tous des pouvoirs du joueur) gèlent désormais sur `is_player_frozen()`
— deux horloges d'un même run pouvaient dériver de quelques ticks selon
qui était touché. Une run "en retard" laissait sa couche dégradable
(ex. `shardBurst`) se déclencher plus tard que prévu, polluant le
spawn_log partagé pendant la fenêtre d'un test suivant
(`gueule_vide_owner_death_cancels_degradable_layer`, faux négatif).
Corrigé en alignant la registry sur `is_player_frozen()` (seul rôle
utilisé par tous ses appelants actuels à ce jour).

**Vérification** : `--import` headless propre, `scripts/
run_gameplay_smoke_test.sh` 100% vert (deux runs indépendants,
déterminisme confirmé) — 8 régressions de méthodologie de test exposées
par l'asymétrie du hit-stop (ordre de sonde shake/gel, marges d'attente
calées sur l'ancienne durée symétrique) diagnostiquées et corrigées une
par une, aucune n'était un vrai bug de gameplay. Captures zoomées
réelles pour Terre (avant/après) et contour (avant/après) — voir
`/tmp/r4_captures/` (non versionné, artefacts de vérification).

**Statut Phase R4 : items 1-6 terminés et vérifiés (tests + captures),
item 7 différé.** Redeploy web à suivre. R2 (items encore ouverts :
recoupe désormais très largement R4.5/R4.6, à réconcilier plutôt qu'à
refaire) et R3/R3bis (Monstrification/Invocation placeholders, chiffrage
migration Cendre) restent en attente de la validation de Milan sur le
prochain clip, comme demandé.

## 2026-08-22 — Suite R4 : valeurs de game feel de Milan + items secondaires restants

Milan a réglé au ressenti, dans un bac à sable dédié à UN impact isolé :
hitstop_freeze_ms=210, knockback_distance_px=27, camera_shake_amplitude_px=6,
impact_flash_duration_ms=65, knockback_return_curve=easeOut. Un verdict humain
qui prime sur la table théorique du doc (plafonnée à 95ms), mais 210ms
partout romprait le rythme d'un combo de 3 coups (3×210ms de gel cumulé
côté cible) — les 5 valeurs ont donc été interprétées et recalées plutôt
qu'appliquées telles quelles :

- **Hitstop** : 210ms traité comme la valeur CIBLE du coup le plus lourd
  (catastrophic), le reste de l'échelle recalé en conservant EXACTEMENT
  les ratios de la 1re passe R4 (light≈0,48×medium, heavy≈2,2×medium,
  catastrophic≈3,4×medium ; attaquant ≈0,54×cible) — `TARGET_HITSTOP_MS`/
  `ATTACKER_HITSTOP_MS` (`combat_feedback.gd`) : light 30/16, medium
  62/33, heavy 136/73, catastrophic 210/113.
- **Shake** : 6px traité comme le nouveau plafond "heavy" (`SHAKE_PROFILES`,
  4→6px) — light/medium non retestés par Milan, laissés tels quels plutôt
  que rescalés sur un seul point de mesure.
- **Flash d'impact** : jamais tiéré (un seul `flash_sprite()` pour tout
  coup) — `HitResponse.FLASH_TICKS` 2→4 (65ms), conversion directe.
- **Recul par défaut** : `recoil_strength_px` par défaut des 3
  `take_damage()` (Player/Enemy/BossGateMaw) 24.0→27.0 — interprété
  comme LA valeur de référence "non spécifiée" (les attaques déjà
  tunées explicitement — Poing Belluaire 40, boss 26-70 — gardent leur
  propre valeur).
- **Courbe de recul** : linéaire (`move_toward` vers 0) remplacée par
  une vraie courbe de POSITION ease-out — nouvelle fonction partagée
  `AnimationComposer.ease_out_step_px()` (même `ease_out_quad()` déjà
  utilisée par `Player._advance_dash()`, jamais une 2e courbe dupliquée),
  réutilisée par les 3 sites de recul (Player.take_damage() côté
  joueur, Enemy.take_damage(), BossGateMaw.take_damage()) qui
  partageaient jusqu'ici une décroissance de vitesse linéaire quasi
  identique copiée-collée 3 fois.

**Vérification** : `run_gameplay_smoke_test.sh` 100% vert (le check
boss_enrage, seul à lire directement l'ancien `_recoil_ticks_remaining`,
mis à jour sur les nouveaux `_recoil_tick`/`_recoil_total_ticks`).

**Restes de R4 traités dans cette passe** :
- **Sol `gate_premiere`/`test_arena`** : capture réelle confirmant le
  diagnostic (`assets/processed/sprites/world/floor_terrain_atlas.png`
  bien trop saturé/contrasté, absorbe la lecture du combat). Nouvel
  outil `tools/desaturate_floor_atlas.py` (PIL, déterministe, teinte
  intacte — HSV : saturation ×0,62, contraste de valeur resserré autour
  de 55%) appliqué directement sur l'atlas déjà cuit (pas de
  régénération PixelLab, 0 crédit). Comparaison avant/après confirmée
  par capture (saturation moyenne mesurée sur la zone de sol : 0,811 ->
  0,620) avant de committer le changement.
- **Chiffres de dégâts** : le fondu existait déjà (`damage_number.gd`,
  40% finaux) mais la trajectoire était une simple montée verticale —
  deux chiffres nés au même point (ex. Bras-Faux touchant 2 cibles)
  restaient superposés pile l'un sur l'autre, d'où le "statique"
  rapporté. Ajout d'une dérive latérale (`ARC_HORIZONTAL_PX`, direction
  dérivée d'un hash déterministe de position+montant — jamais un vrai
  hasard non seedé dans un chemin de feedback de combat, Addendum A
  §A.5) sur la MÊME courbe ease-out partagée que le reste (x et y).
- **Zoom caméra +20-25%** : PAS tranché — deux captures A/B produites
  (`--mode=scene`, cam_zoom=1.0 vs 0.8) et envoyées à Milan pour
  décision, comme demandé explicitement ("ça touche au cadrage général,
  ne pas trancher seul"). Aucun changement de code appliqué (le zoom de
  base du jeu reste géré par `CameraDirector.get_punch_zoom()`
  ponctuellement, pas un `BASE_ZOOM` permanent — à ajouter seulement si
  Milan valide l'option B).

**render_detector.py (détecteur de rendu factuel) : PAS intégré cette
passe** — Milan le décrit comme "fourni" mais le fichier est introuvable
dans le dépôt ou ailleurs dans cette session ; demandé à Milan de le
joindre avant de pouvoir l'intégrer/calibrer.

**Statut** : valeurs de game feel + sol + chiffres de dégâts terminés et
vérifiés (tests + captures). Zoom caméra en attente du choix de Milan
(A ou B). render_detector.py bloqué en attente du fichier. Redeploy web
à suivre. R3/R3bis toujours en attente du verdict de Milan sur le
prochain clip.

## 2026-08-22 — Zoom caméra tranché (option B) : BASE_ZOOM permanent

Milan a choisi l'option B (+25%, cam_zoom=0.8) sur les 2 captures A/B
envoyées. `CameraDirector.BASE_ZOOM := Vector2(0.8, 0.8)` + nouvelle
fonction `get_zoom()` = `BASE_ZOOM * get_punch_zoom()` (multiplication,
pas addition — le punch garde exactement la même intensité RELATIVE
quel que soit le zoom de base). `Player._physics_process()` : `_camera.
zoom = CameraDirector.get_zoom()` au lieu de `get_punch_zoom()` seul.
`get_punch_zoom()` reste inchangée et exposée telle quelle (le smoke
test `camera_punch_zoom_triggers_on_medium_hit_not_light` la lit en
isolation, indépendamment de tout zoom de base).

Un seul `player.tscn` partagé par `gate_premiere`/`test_arena`/
`outpost` (voir leurs `.tscn` respectifs, node "Player" instancié 3
fois) : ce changement dans `player.gd`/`camera_director.gd` s'applique
identiquement aux 3 scènes, pas 3 réglages séparés à synchroniser.

**Vérifié par capture réelle (pas seulement lu dans le code)** : les
modes existants de `capture_scene.gd` (`--mode=scene`) injectent
TOUJOURS leur propre `Camera2D` (`cam.make_current()`), ce qui aurait
masqué silencieusement l'effet réel de ce changement (la caméra
injectée écrase celle de Player, donc capturer avec l'ancien mode
aurait "confirmé" n'importe quelle valeur de zoom sans jamais tester le
vrai code). Nouveau flag `--use_scene_camera=1` : laisse la caméra RÉELLE
de Player (celle pilotée par `CameraDirector.get_zoom()`) active plutôt
que d'en injecter une — capturé sur les 3 scènes : le monde est
visiblement ~25% plus grand, HUD (barre de vie, `Niv. 1`) et boutons
tactiles (joystick, PB/BF/GV/PT/DDG/DASH/ATK/PERSO) restent pile à
leur place — `CanvasLayer` (root des 2 scènes UI) est par construction
immunisé à `Camera2D.zoom`, confirmé par capture plutôt que supposé.

**Vérification** : `--import` headless propre, `scripts/
run_gameplay_smoke_test.sh` 100% vert (aucune régression — les 2 checks
qui touchent la caméra lisent `CameraDirector.get_punch_zoom()`
directement, jamais `_camera.zoom`, donc indifférents à `BASE_ZOOM`).

**Statut** : terminé et vérifié, redeploy web à suivre immédiatement.
render_detector.py maintenant fourni par Milan — intégration en cours,
voir entrée suivante.

## 2026-08-22 — render_detector.py : intégration + calibration Poing Tellurique

Fichiers de Milan (`render_detector.py` + `test_render_detector.py`)
copiés tels quels dans `tools/`. Suite synthétique 4/4 rejouée dans cet
environnement (`python3 tools/test_render_detector.py`) : présent /
absent / flash blanc (channel_delta) / cas limite ("incertain") tous
corrects.

**Nouveau mode de capture** (`tools/capture_scene.gd`,
`--mode=player_action_sequence`) : aucun mode existant ne produisait
une SÉQUENCE d'images tick par tick (`frame_0000.png`, `frame_0001.png`,
...) au format attendu par `render_detector.load_frames_from_dir()` —
tous les autres modes capturent UN seul tick cible. Même mise en place
que `--mode=player_action` (Player réel + 2 ennemis, mêmes offsets).

**Bug trouvé et corrigé en construisant ce mode** : la première version
gelait/dégelait le `SceneTree` (`get_tree().paused`) à CHAQUE tick pour
réutiliser `_freeze_and_wait_render()` — résultat : les primitives VFX
ne se rendaient plus DU TOUT (`groundRing` de Poing Tellurique,
pourtant confirmé visible en capture ponctuelle `--mode=player_action`,
disparaissait entièrement en séquence). Cause exacte non isolée
(interaction entre le pause/dégel répété et le pipeline de rendu
logiciel), corrigée en abandonnant la pause pour cette capture : un
`process_frame` de plus après chaque `physics_frame`, jamais de gel.

**Vérification "alignement tick 0" (demandée explicitement par Milan)**
: en corrigeant le bug ci-dessus, un second problème est apparu — le
TOUT PREMIER frame capturé (tick 0, la baseline "avant effet") sortait
avec un fond NOIR (0,0,0) au lieu du gris neutre stable (76,76,76) de
tous les frames suivants, un artefact de chauffe du rasterizer logiciel
(llvmpipe) sur la toute première image rendue. Sans correctif, TOUTES
les couches ressortaient "present" dès le tick 1 avec
`pixel_fraction=1.0` — un faux positif qui ne mesurait que cet artefact,
jamais un vrai effet (exactement le risque que Milan avait anticipé).
Corrigé par 3 `process_frame` de chauffe avant la capture du tick 0.

**Calibration sur Poing Tellurique** (cas choisi par Milan, déjà
confirmé visible en capture manuelle cette session) : région/seuils par
primitive dérivés de vraies mesures sur une séquence de 31 frames
(0-30 ticks), pas inventés :
- `groundRing` (luminance_delta) : present, mean_delta~8-9.3 sur toute
  la fenêtre 1-18, seuil calé à 6.0/0.10 avec marge.
- `impactFlashFrame` (luminance_delta) : present, delta ~12 au contact
  (tick 18) montant à ~65-72 (gel de hit-stop qui retarde la
  décroissance visuelle, cohérent avec l'asymétrie Phase R4).
- `dustKick` (stddev_delta — texture, pas luminosité moyenne, exactement
  le cas d'usage documenté par Milan) : present, signature nette (saut
  36,9->84 dès le tick 19, décroissance ticks 26-27).
- `converge` (core, matière qui converge dans le poing) : **absent**
  selon le détecteur (delta max ~0,4, loin sous le seuil). Inspection
  visuelle d'une capture zoomée confirme un signal à peine perceptible
  — pas une absence aussi franche qu'un vrai bug de rendu (C1/Gueule
  Vide), documenté dans la recette comme piste ouverte plutôt que bug
  tranché : soit augmenter son contraste/échelle (même diagnostic que
  groundRing avant son propre correctif), soit recalibrer la mesure.
  Pas encore résolu.

`expected_layers` ajouté à `data/recipes/power.poing_tellurique.cast.json`
(liste brute, conforme au schéma de `render_detector.py` — les notes de
calibration vivent dans une clé séparée `_expected_layers_notes` pour ne
jamais casser `load_recipe()`). Rapport complet :
`/tmp/r4_captures/poing_tellurique_render_report.json` (non versionné).

**Non fait cette passe** : `expected_layers` sur les autres recettes
(Bras-Faux, Poing Belluaire, Gueule Vide, Totem du Vide...) — chacune
demande sa propre calibration par capture réelle (région/seuils
propres à son cadrage), pas un travail générique à dupliquer sans
vérification. Le pipeline complet (capture séquence -> calibrer ->
`expected_layers` -> `run_detection_from_paths()`) est maintenant
prouvé de bout en bout sur un cas réel ; l'étendre aux autres pouvoirs
reste un chantier à part entière, pas terminé ici.

**Vérification** : `scripts/run_gameplay_smoke_test.sh` 100% vert
(nouveau mode de capture n'affecte aucun code de gameplay). Rien à
redéployer côté web (outil de développement uniquement, pas de code
runtime jeu changé au-delà de `capture_scene.gd`).

## 2026-08-22 — Socle de référence : archivage planches + verrouillage palette Terre + audit 4 recettes vivantes

Mandat Milan en 3 points, explicitement **sans toucher aux 11
compétences restantes** de la bible — priorisation à venir dans un
futur mandat une fois ce socle posé.

**1. Archivage permanent des 15 planches** — les planches de référence
validées par Milan (Invocateur/Monstrification/Terre, 5 par classe)
n'existaient que dans l'historique de discussion. Recadrées (script
Pillow, crop vertical par bornes de ligne) et archivées sous
`docs/references/<classe>/<nom-competence>.png`, avec un
`docs/references/README.md` documentant le mapping fichier -> planche
source (4 uploads). Les 2 blocs "sprites de base/icônes/effets
communs" (transverses, pas liés à une compétence, présents en pied de
page sur 2 des 4 uploads) archivés séparément sous
`docs/references/shared/`.

Divergence de nommage relevée : le mandat citait "Éperon" comme 5e
planche Terre, mais aucune planche de ce nom n'existe dans les
uploads — la 5e planche Terre réellement fournie est **Fissure
Éruptive**. Traité comme une divergence de nommage dans la demande
(documentée dans le README), pas comme une planche manquante : les 5
planches Terre annoncées sont bien toutes présentes.

**2. Verrouillage de `data/palettes/terre.json`** — comparée aux 5
planches Terre désormais archivées. Aucun écart net : Marée de Sable
(sable ocre/tan sur roches brun-gris), Carapace (plaques rocheuses
brun-gris-beige désaturées), Effondrement (fissures brun-terreux qui
convergent puis explosent en éclats ocre clair/poussière pâle),
Fissure Éruptive (pics gris-pierre + nuages de poussière gris-tan) —
et Poing Tellurique, déjà audité en détail via `render_detector.py`
ci-dessus. Toutes cohérentes avec la palette déjà en place (brun-gris
terreux / gris pierre foncé / ocre clair / poussière pâle, hue 30-40°),
aucune couleur hors de cette famille. Flag `PROPOSITION` retiré,
`"status": "VERROUILLÉE"` ajouté, structure et valeurs numériques
inchangées (aucune réinvention, la bible reste la référence de
matière) — changement documenté dans les notes du fichier lui-même.

**3. Audit factuel des 4 recettes vivantes (aucun changement de code)** :

- **Gueule Vide** (`power.gueule_vide.cast.json`, palette
  `invocateur_vide`) — **cohérent**. La planche (créature d'encre
  noire/gris-lilas surgissant du sol, cercle runique bleu pâle sous les
  pieds, éclaboussures sombres) correspond terme à terme aux 4 rôles de
  la palette (noir d'encre, gris-lilas désaturé, gris cendre, pointe
  bleu pâle système sur le cercle au sol). Aucun écart relevé.

- **Poing Tellurique** (`power.poing_tellurique.cast.json`, palette
  `terre`) — **cohérent**, déjà audité en détail ci-dessus par mesure
  réelle (`render_detector.py`) : groundRing/impactFlashFrame/dustKick
  confirmés présents, `converge` reste une piste ouverte non tranchée
  (signal à peine perceptible, pas une absence franche) — pas un
  nouveau constat, le même suivi déjà documenté dans la recette.

- **Bras-Faux** (`power.bras_faux.cast.json`, palette `parasite`) —
  **écart notable de couleur**. La palette `parasite` est explicitement
  définie (notes du fichier, citant GDD §7) comme un "grayscale strict...
  gris cendre, gris foncé, noir, pointe de bleu-gris pâle et lilas-gris
  pâle... NO PURPLE saturé, NO GLOW" — les teintes de couleur (bleu-gris
  ~205°, lilas-gris ~275°) n'apparaissant qu'en fine touche ("pointe de",
  jamais dominante). Or la planche Bras-Faux montre un bras-tendon/faux
  rouge-brun-rouille organique (chair et tendons) comme couleur
  DOMINANTE du membre transformé sur les 4 panneaux, avec des
  éclaboussures rouges — pas une pointe froide bleu-gris/lilas sur fond
  gris cendre, mais une teinte chaude rouge-brun qui domine tout le
  visuel. Écart de teinte net entre la palette de code (froide,
  désaturée, à peine teintée) et la référence (chaude, organique,
  rouge-brun affirmé).

- **Poing Belluaire** (`power.poing_belluaire.cast.json`, palette
  `parasite` réutilisée) — **aucune planche dédiée parmi les 15
  fournies** ("Poing Belluaire" n'est le nom d'aucune des 15
  compétences illustrées). Candidat le plus proche par construction :
  **Coup de Poing Monstrifié** (Monstrification) — même archétype exact
  que documenté dans les notes de la recette ("un seul coup frontal
  très lourd", pas de traînée/balayage) : Préparation/Transformation ->
  Impact -> Récupération, sans étape de balayage, contrairement à
  Bras-Faux. Hypothèse plausible (non tranchée) d'une divergence de
  nommage bible/code du même type que Terre/"Éperon" ci-dessus — à
  confirmer par Milan, pas assumé comme acquis. Si cette
  correspondance est la bonne : même écart de teinte que Bras-Faux
  (planche rouge-rose organique dominante vs palette `parasite`
  froide/désaturée, réutilisée telle quelle par cette recette), et la
  colonne "Assets - Effets" de la planche montre un impact + une
  fissure au sol qui n'a pas d'équivalent dans les 3 couches actuelles
  de la recette (`converge`/`impactStar`/`impactFlashFrame`, aucune
  couche de fissure/craquelure au sol) — à vérifier une fois l'identité
  confirmée, pas un constat définitif ici.

Aucun changement de code ni de recette à ce stade (demande explicite de
Milan : audit seulement). Aucune des 11 compétences restantes entamée.

## 2026-08-22 — Trois décisions de Milan : couleur Monstrification, confirmation Poing Belluaire, audit Classe unique

**1. `data/palettes/parasite.json` réécrite — verdict Milan : la référence
a raison, pas le code.** L'audit précédent avait relevé que la palette
"parasite" (grayscale strict + pointe froide bleu-gris/lilas, mandatée
par le texte GDD §7) ne correspondait pas aux 5 planches Monstrification
archivées (rouge-brun-rouille organique dominant). Milan tranche : la
planche fait foi, pas le texte GDD/le code d'origine.

Valeurs dérivées par échantillonnage réel des pixels (pas à l'oeil,
même méthode que la vérification `render_detector.py` sur Poing
Tellurique) : script ponctuel (non versionné) sur la colonne "Assets -
Effets" des 5 planches (`docs/references/monstrification/*.png`),
filtrage des pixels rouge-orangé saturés (hue proche de 0-40°, sat>30%)
pour isoler la matière organique du fond crème/du personnage
gris/du texte noir — 21 456 pixels retenus au total, moyenne circulaire
de teinte par tranche de luminosité (V) :

| tranche V | n | teinte | saturation | valeur |
|---|---|---|---|---|
| 0-10% (le plus sombre) | 2192 | 2,6° | 40,3% | 17,6% |
| 30-50% | 4512 | 7,5° | 37,3% | 31,0% |
| 50-70% | 4564 | 10,6° | 36,6% | 38,4% |
| 90-100% (le plus clair) | 2163 | 18,2° | 33,9% | 61,3% |

Rampe cohérente et mesurée : la teinte se réchauffe (rouge profond ->
orangé) à mesure que la luminosité monte, un comportement de rim-light
naturel sur de la matière organique — pas une valeur inventée. Les 5
planches sont individuellement cohérentes entre elles (teinte moyenne
par planche 5-14°, aucun outlier). 4 rôles réécrits en conservant EXACTEMENT
la même structure et les mêmes champs `usage` (aucun remapping
primitive->rôle) :
- signature 1 (corps principal) : "rouge-brun tendineux", hue 9°, sat 37%, val 38%
- signature 2 (Root/profondeurs) : "brun-rouille profond", hue 3°, sat 40%, val 18%
- contact (éclat/impact) : "roux-orangé vif", hue 18°, sat 34%, val 61%
- intermédiaire (transitions) : "roux clair organique", hue 14°, sat 35%, val 48%

**Vérifié : aucun résidu de l'ancienne teinte froide.** Le système est
purement data-driven (`src/vfx/vfx_recipe_registry.gd::_resolve_color` lit
`data/palettes/<palette_id>.json` et matche la primitive contre le champ
`usage` en texte libre — seul repli = gris neutre générique si aucune
correspondance). Grep sur `205|275|bleu-gris|lilas` dans `src/` : aucune
occurrence dans le code (`.gd`), la seule trace de l'ancienne teinte
était dans ce fichier JSON, maintenant réécrit. Bras-Faux et Poing
Belluaire référencent `palette_id: "parasite"` sans aucune couleur codée
en dur dans leurs couches — les deux recettes héritent donc du nouveau
rouge-brun automatiquement, sans modification de fichier de recette
nécessaire (vérifié aussi qu'aucune des deux notes de recette ne
décrivait elle-même la teinte froide en texte — rien à corriger là).

**2. Poing Belluaire = Coup de Poing Monstrifié, confirmé par Milan.**
Note de `data/recipes/power.poing_belluaire.cast.json` mise à jour pour
pointer vers `docs/references/monstrification/coup_de_poing_monstrifie.png`
comme référence visuelle confirmée (recette non modifiée par ailleurs).

Vérification du point soulevé lors de l'audit précédent — l'absence
d'une couche fissure/craquelure au sol : **confirmé, c'est un vrai
manque, pas couvert autrement.** La recette n'a que 3 couches
(`converge` anticipation, `impactStar`+`impactFlashFrame` contact) —
aucune couche de type `fractureLine`/`groundRing` qui produirait un
décalque de sol fissuré, contrairement à Poing Tellurique qui EN a un
(`groundRing`, anticipation). `impactStar` est un éclat/étoile
d'impact ponctuel, pas un décalque persistant au sol — les deux
effets ne se recouvrent pas visuellement. La planche montre bien cet
effet de fissure au sol dans sa colonne "Assets - Effets", en plus de
la progression du poing et de l'éclat d'impact. Signalé tel quel,
aucune couche ajoutée à ce stade (audit seulement, comme demandé).

**3. Audit factuel : le HUD des captures zoom caméra est-il un HUD de
debug ou le HUD réel ?** Réponse basée sur lecture directe du code
(les captures de la session zoom n'ont pas été versionnées, donc
vérifié via la source plutôt que de re-générer les images) :

`src/gameplay/player.gd::_physics_process()` lie sans AUCUNE condition
de garde les 4 pouvoirs sur les 4 actions `power1`-`power4` :
```
power1 -> _cast_gueule_vide()       (Invocateur)
power2 -> _start_bras_faux()        (Monstrification)
power3 -> _start_poing_belluaire()  (Monstrification)
power4 -> _start_poing_tellurique() (Terre)
```
Aucune vérification de "Classe active" avant l'appel. Côté HUD tactile,
`scenes/ui/touch_controls.tscn` instancie ButtonPower1/2/3/4 de façon
permanente et inconditionnelle (les 4 nœuds `TouchScreenButton` existent
tous dans la scène, aucune visibilité conditionnelle). Recherche
exhaustive (`grep -rn "ButtonPower\|current_class\|classe_active\|
active_class\|selected_class\|unlock"` sur `src/` et `scenes/`) : **zéro
résultat** — il n'existe actuellement AUCUN concept de "Classe active"
ni de système de déblocage dans le code, à quelque niveau que ce soit.

**Verdict : ce n'est PAS un HUD de debug.** `touch_controls.tscn` est le
HUD tactile réel utilisé en jeu (le même dont le positionnement a été
vérifié sous le nouveau `BASE_ZOOM` cette session) et `player.gd` est le
script réel du joueur. Les captures montraient donc fidèlement l'état
actuel du jeu : un seul personnage avec les 4 pouvoirs des 3 Classes
(Invocateur/Monstrification/Terre) disponibles simultanément et sans
restriction, dès le début. **Ceci contredit directement** la nouvelle
règle de Milan (1 seule Classe par run, 5 compétences débloquées
progressivement). Signalé tel quel — **aucune correction appliquée**,
conformément à l'instruction explicite de ne rien changer tant que le
système de déblocage complet n'est pas précisé.

**AMENDEMENT GDD EN ATTENTE DE DÉTAIL** (règle confirmée par Milan,
consignée ici pour ne pas la perdre, non implémentée) :
- Le personnage n'a qu'**une seule Classe par run** (Invocateur,
  Monstrification OU Terre — jamais plusieurs à la fois).
- Les **5 compétences de cette Classe se débloquent progressivement**
  pendant la run, plutôt que d'être toutes disponibles dès le départ.
- **Non précisé par Milan, ne rien inventer d'ici là** : l'ordre de
  déblocage des 5 compétences, et la méthode de déblocage (niveau ?
  étage franchi ? nombre de kills ? autre ?).

Aucun changement de code pour ce point 3 (audit seulement, comme
demandé). Rien à redéployer côté web pour cette passe (JSON de données
+ documentation uniquement, aucun code runtime modifié).

## 2026-08-22 — Système Classe/déblocage : état des lieux + plan (PAS ENCORE IMPLÉMENTÉ)

Milan a confirmé l'amendement GDD (1 Classe/run tirée au hasard, 5
compétences débloquées par niveau, HUD conditionnel) et demandé
explicitement un état des lieux + un plan présenté AVANT tout code
("changement structurel, pas un ajustement ponctuel"). Ce qui suit est
ce plan — **aucun fichier de code modifié cette passe**, seulement de
la lecture/analyse. Attend le retour de Milan sur plusieurs questions
bloquantes avant la moindre ligne de code.

**État des lieux — l'architecture actuelle est 100% câblée en dur, 1:1,
sans aucune indirection :**
- `project.godot` : 4 actions d'input `power1`-`power4` (touches
  E/R/T/G), aucune 5e action.
- `player.gd::_physics_process()` : `power1` appelle TOUJOURS
  `_cast_gueule_vide()`, `power2` TOUJOURS `_start_bras_faux()`,
  `power3` TOUJOURS `_start_poing_belluaire()`, `power4` TOUJOURS
  `_start_poing_tellurique()` — zéro garde de Classe, zéro indirection.
- `scenes/ui/touch_controls.tscn` : 4 `TouchScreenButton` permanents
  (ButtonPower1-4), labels texte STATIQUES ("GV"/"BF"/"PB"/"PT") gravés
  dans la scène, aucun script attaché au nœud racine pour piloter
  visibilité/libellé (seul `Joystick` a un script, `virtual_joystick.gd`).
- `src/ui/hud.gd` : 4 overlays de cooldown fixes, chacun lié en dur à
  un getter précis (`get_power1_cooldown_ratio`,
  `get_bras_faux_cooldown_ratio`, `get_poing_belluaire_cooldown_ratio`,
  `get_poing_tellurique_cooldown_ratio`) — même rigidité que
  touch_controls.
- `src/ui/character_screen.gd` : **conflit direct avec le nouvel
  amendement**. Le fichier porte une exigence GDD EXPLICITE et
  documentée en commentaire : "Rank Zero doit afficher CLASS = NONE et
  ne jamais recevoir une Classe inventée" — `_stats_label.text` affiche
  littéralement `"CLASSE : AUCUNE"` en dur. Maintenant qu'une Classe
  réelle sera tirée et vécue toute la run, cette règle GDD est-elle
  caduque (la Classe doit s'afficher) ou reste-t-elle absolue (Milan
  distinguait peut-être "Classe de bâtisseur"/méta-progression et
  "Classe de pouvoir" tirée en run) ? **Ne pas trancher seul.** Détail
  secondaire, même fichier : `_skills_label.text` liste en dur "E —
  Gueule Vide\nR — Bras-Faux" — déjà obsolète aujourd'hui (oublie Poing
  Belluaire/Poing Tellurique), à rendre dynamique de toute façon.
- `src/system/run_state.gd` (autoload) : `player_stats: Stats` est un
  Resource unique créé UNE fois au chargement de l'autoload et jamais
  réinitialisé ensuite — il n'existe **aucune notion explicite de
  "début de run"** distincte du démarrage du process (pas de fonction
  `new_run()`/`restart()` trouvée nulle part dans le dépôt). C'est
  exactement le même point d'ancrage que Milan demande pour le tirage
  de Classe : `active_class` peut suivre le même patron que
  `player_stats` (tiré une fois à l'init de l'autoload), sans qu'il
  faille inventer une notion de "run" qui n'existe pas encore ailleurs
  dans le code.
- `stats.gd` : `signal leveled_up(new_level: int)` déjà émis dans
  `add_xp()`, en boucle (un gain d'XP massif peut émettre plusieurs
  fois de suite, niveau par niveau, jamais sauté) — exploitable tel
  quel, rien à changer ici.
- `tools/smoke_test_gameplay.gd` : les 4 checks vivants
  (`_check_gueule_vide`, `_check_bras_faux`, `_check_poing_belluaire`,
  `_check_poing_tellurique`) déclenchent CHACUN via
  `Input.action_press("powerN")` — donc le jour où l'entrée devient
  gardée par Classe/niveau, ces 4 checks casseront tous en silence
  (spawn=false) SAUF si chacun force d'abord `RunState.active_class` et
  `stats.level` au bon état avant d'appuyer. Mise à jour obligatoire
  des 4 blocs, pas optionnelle — c'est précisément la régression que
  Milan demande d'éviter.

**Réalité de contenu actuel (contrainte transversale à ne pas
oublier)** : à ce jour, sur les 5 compétences nominales par Classe,
seules certaines existent réellement en code/recette VFX :
Invocateur = 1/5 (Gueule Vide seule), Monstrification = 2/5 (Bras-Faux,
Poing Belluaire), Terre = 1/5 (Poing Tellurique seule). Les 11
compétences restantes n'ont ni fonction `_start_X()` ni recette JSON —
conformément à la consigne permanente de ne pas les commencer, le
système de déblocage doit fonctionner correctement même quand la
plupart de ses paliers de niveau "débloquent" une compétence qui n'a
tout simplement rien à afficher/appeler pour l'instant (bouton absent,
pas un bouton grisé cassé). Conséquence concrète pour Milan : une run
qui tire Invocateur ou Terre n'aura QU'UN SEUL bouton de pouvoir actif
pour toute sa durée tant que le reste de la bible n'est pas construit ;
seule Monstrification en aura deux. Signalé pour que ce ne soit pas une
surprise au prochain test — pas un problème à corriger ici.

**Contradictions de Tier relevées sur les planches archivées (bloquent
le verrouillage de l'ordre — voir docs/references/) :**

*Terre* — planches avec Tier explicite et cohérent 1→4 : Poing
Tellurique=TIER 1, Marée de Sable=TIER 2, Carapace=TIER 3,
Effondrement=TIER 4. Fissure Éruptive (planche mixte) n'affiche AUCUN
Tier. Or l'ordre donné en exemple par Milan lui-même dans le mandat
précédent — "Poing Tellurique -> Marée de Sable -> Éperon -> Carapace
-> Effondrement" — place ce 5e pouvoir ("Éperon", nom qui ne correspond
à aucune planche fournie, cf. divergence déjà signalée) EN 3E position,
AVANT Carapace(T3) et Effondrement(T4). Ça contredit frontalement les
Tiers imprimés sur les planches. **Je ne tranche pas** : soit l'ordre
d'exemple de Milan est le bon et les Tiers 3/4 de Carapace/Effondrement
sont à ignorer pour l'ordre de déblocage, soit les Tiers font foi et
Fissure Éruptive vient en dernier (Tier 5 par élimination) — à
confirmer.

*Monstrification* — INCOHÉRENCE INTERNE, pas seulement un désaccord
avec un exemple : Bras-Faux=TIER 2, Mâchoire=TIER 3, Pattes de
Chasse=TIER 3 (DOUBLON avec Mâchoire), Forme Bestiale=TIER 4, Coup de
Poing Monstrifié (= Poing Belluaire, confirmé la passe précédente)
n'affiche AUCUN Tier. Aucune planche ne réclame Tier 1 ni Tier 5. Il
manque soit une correction de Tier sur une des planches, soit une
information supplémentaire sur Coup de Poing Monstrifié/Poing
Belluaire (probablement Tier 1, le seul qui reste libre en bas de
l'échelle, mais ce n'est qu'une supposition — le bloc de dégâts/recul/
cooldown actuel en jeu, POING_BELLUAIRE > BRAS_FAUX, suggérerait plutôt
un Tier supérieur si on se fiait au seul équilibrage code, mais Milan a
explicitement demandé de ne jamais utiliser l'équilibrage code pour
trancher un désaccord avec la bible). **Je ne tranche pas.**

*Invocateur* — pas de contradiction relevée : Gueule Vide=T1, Corbeau
Pâle=T2, Poing du Colosse=T3, Œil sans Regard=T4, Invocation du Serpent
(planche mixte) sans Tier affiché — cohérent par élimination avec Tier
5, mais toujours non confirmé explicitement sur la planche elle-même.

**Architecture proposée (sous réserve des réponses de Milan
ci-dessous) :**
1. `RunState` (autoload) : nouveau champ `active_class: String`, tiré
   aléatoirement parmi les 3 classes UNE fois à l'initialisation de
   l'autoload — même patron que `player_stats`, aucun écran de
   sélection, rien à construire côté UI pour le tirage lui-même.
2. Nouvelle donnée (ex. `data/classes/<classe>.json`, un fichier par
   Classe ou un seul fichier combiné, à trancher) : la liste FIXE des 5
   compétences dans l'ordre bible, avec pour chacune : nom, Tier,
   palier de niveau de déblocage, et si elle est "implémentée" (a une
   fonction `_start_X()`/`_cast_X()` + une recette VFX réelle) ou non
   (placeholder, rien à faire tant que non construite).
3. `player.gd` : remplacer les 4 appels directs par une résolution de
   "slot" — `power1..4` deviennent des emplacements de COMBAT
   génériques (pas des identités figées de compétence), résolus au
   moment de l'appui selon (Classe active, niveau courant, position
   dans l'ordre bible de cette Classe parmi les compétences déjà
   implémentées). Connecter `stats.leveled_up` en `_ready()` pour
   rafraîchir l'état de déblocage affiché par le HUD/touch (pas besoin
   de cache complexe : le niveau courant suffit à recalculer l'état à
   la demande).
4. `touch_controls.tscn` : ajouter un script au nœud racine
   `TouchControls` (aucun aujourd'hui) qui, à chaque changement de
   niveau, masque les `ButtonPowerN` dont le slot est vide/non débloqué
   (absent, pas grisé — exigence explicite de Milan) et réécrit le
   `text` du Label selon la compétence réellement assignée à ce slot.
5. `hud.gd` : même logique de masquage sur les 4 overlays de cooldown.
6. `character_screen.gd` : en attente de la réponse de Milan sur le
   conflit "CLASSE : AUCUNE" avant tout changement.
7. `tools/smoke_test_gameplay.gd` : mise à jour obligatoire des 4 blocs
   vivants pour forcer `RunState.active_class` + `stats.level` au bon
   état avant chaque test d'input, afin de ne rien casser.

**Question ouverte transversale — 5e emplacement de pouvoir** : le jeu
n'a que 4 slots (E/R/T/G + 4 boutons tactiles) pour un maximum
théorique de 5 compétences par Classe. Proposition : NE PAS ajouter de
5e slot maintenant (aucune Classe actuelle n'en a besoin avec le
contenu déjà construit — même discipline "pas de fonctionnalité pour
un besoin hypothétique" que le reste du projet), construire la
résolution de slot de façon assez générique pour qu'ajouter un 5e slot
plus tard (quand une Classe aura effectivement 5 compétences
implémentées) soit un changement mineur. À valider par Milan.

**Proposition de palier niveau -> compétence (À VALIDER, pas verrouillé)**
: 1 / 3 / 6 / 10 / 15 comme suggéré par Milan. Note de cohérence
économique (calcul, pas un verdict) : `xp_to_next_level()` coûte 50×N
XP pour passer du niveau N à N+1 (coût cumulatif niveau 25×L×(L-1)) ;
avec les seules sources d'XP déjà codées (ramassage ~20 XP,
ennemi normal ~8 XP, boss ~120 XP), atteindre le niveau 15 réclame
~5250 XP cumulés, soit plusieurs centaines de kills/pickups selon la
longueur réelle d'une run — je n'ai pas de référence sur la longueur de
run visée pour juger si ce rythme est trop lent ou correct, donc je ne
l'ajuste pas moi-même comme demandé.

**QUESTIONS BLOQUANTES avant tout code (résumé)** :
1. Terre : ordre d'exemple de Milan vs Tiers imprimés — lequel prime ?
2. Monstrification : Tier de Coup de Poing Monstrifié/Poing Belluaire
   + résolution du doublon Tier 3 Mâchoire/Pattes de Chasse ?
3. `character_screen.gd` "CLASSE : AUCUNE" : règle GDD toujours valable
   telle quelle, ou remplacée par l'affichage de la vraie Classe active ?
4. Paliers 1/3/6/10/15 : à valider ou à ajuster (voir note économique) ?
5. 5e emplacement de pouvoir : absent pour l'instant (ma proposition)
   ou à créer dès maintenant en plomberie inerte ?
6. Un seul bouton actif toute la run pour Invocateur/Terre tant que le
   reste de la bible n'existe pas en code : acceptable pour ce mandat,
   ou faut-il revoir la priorité de construction des 11 compétences
   restantes en conséquence (hors scope explicite de ce mandat, mais
   Milan doit le savoir) ?

Rien commité côté code — uniquement cette entrée de worklog (analyse/
plan). Implémentation suspendue jusqu'au retour de Milan.

## 2026-08-22 — Système Pouvoir/déblocage : IMPLÉMENTÉ

Milan a tranché les 6 questions bloquantes du plan précédent. Ordre
verrouillé par Classe, paliers de niveau (asymétriques pour
Monstrification), terminologie ("Pouvoir", pas "Classe" —
character_screen.gd/"CLASSE : AUCUNE" non touché, règle GDD distincte),
5 emplacements réels dès cette passe (pas de report), conséquence
"1 seul bouton actif toute la run pour Invocateur/Terre" acceptée.

**Données (`data/pouvoirs/{invocateur,monstrification,terre}.json`)** :
un fichier par Pouvoir, 5 compétences ordonnées par tier avec
`unlock_level`/`touch_label`. Ordre verrouillé :
- Invocateur : Gueule Vide(1)→Corbeau Pâle(3)→Poing du Colosse(6)→
  Œil Sans Regard(10)→Serpent Creux(15).
- Terre : Poing Tellurique(1)→Marée de Sable(3)→Carapace(6)→
  Effondrement(10)→Fissure Éruptive(15).
- Monstrification (paliers délibérément différents, cf. mandat) :
  Poing Belluaire(1)→Bras-Faux(3)→Mâchoire(6)→Forme Bestiale(**14**)→
  Pattes de Chasse(**18**) — écart 6→14 nettement le plus large des 3
  Pouvoirs, resserré ensuite pour 14→18, exactement le rythme demandé
  (Forme Bestiale = "seule vraie transformation complète de la bible").
  Chiffres de Milan conservés tels quels (1/3/6/14/18).

**`src/system/pouvoir_registry.gd`** (autoload `PouvoirRegistry`) :
charge/cache les 3 JSON (même patron que
`VfxRecipeRegistry._load_palette()`). Ne connaît QUE l'ordre/les
paliers — délibérément ignorant de ce qui est réellement implémenté en
code (séparation données/dispatch, voir plus bas).

**`src/system/run_state.gd`** : nouveau champ `active_power: String`,
tiré au hasard parmi les 3 Pouvoirs à l'init de l'autoload (même patron
que `player_stats`, aucune notion de "début de run" à inventer). Liste
des 3 Pouvoirs dupliquée en dur plutôt que référencée via
`PouvoirRegistry.POUVOIR_IDS` : un champ par défaut se résout à la
construction du nœud, avant toute garantie sur l'ordre d'init des
autres autoloads — RunState reste sans AUCUNE dépendance, comme documenté.

**`src/gameplay/player.gd`** — cœur du changement : `power1`..`power5`
ne sont plus liés en dur à une compétence (`_cast_gueule_vide()`,
`_start_bras_faux()`, etc. directement dans `_physics_process()`) mais
résolus dynamiquement via un nouveau `_try_activate_power_slot(slot_
index)`. Table `IMPLEMENTED_SKILL_HANDLERS`/`IMPLEMENTED_SKILL_
COOLDOWN_GETTERS` (id de compétence -> nom de méthode) : SEULE source
de vérité sur ce qui a une fonction réelle aujourd'hui (4 compétences
sur 15). `get_power_slot_info(slot_index)` (public, lu par
touch_controls.gd/hud.gd/character_screen.gd) retourne `{}` si le slot
n'est pas débloqué par le niveau OU si la compétence qui s'y trouverait
n'est pas implémentée — absent, jamais "grisé". Conséquence directe du
nouvel ordre verrouillé : Poing Belluaire est maintenant tier 1 de
Monstrification (pas tier 3 comme dans l'ancien câblage), Poing
Tellurique tier 1 de Terre (pas tier 4) — les deux se déclenchent
maintenant via "power1", jamais "power3"/"power4".

**`scenes/ui/touch_controls.tscn` + `src/ui/touch_controls.gd`** (nouveau
script, la scène n'en avait aucun) : `ButtonPower5` ajouté (touche H,
position (315,305)), et un poll en `_process()` (même discipline que
hud.gd/character_screen.gd) masque chaque bouton (`visible = false`,
pas un overlay) et réécrit son label selon `Player.get_power_slot_info()`.

**`scenes/ui/hud.tscn` + `src/ui/hud.gd`** : `Power5` ajouté au
conteneur `Cooldowns` (même grille, pitch 32px). `_process()` généralisé
en boucle sur 5 slots : conteneur entier masqué si vide (pas seulement
l'overlay de cooldown), sinon label + overlay mis à jour via
`get_power_slot_info()`/`get_power_slot_cooldown_ratio()`.

**`src/ui/character_screen.gd` + `.tscn`** : "CLASSE : AUCUNE" **non
touché** (règle GDD distincte, confirmée toujours valide). Nouveau
`PouvoirLabel` séparé affichant "POUVOIR : <valeur active>". Le texte
`_skills_label` (déjà obsolète avant ce mandat : oubliait 2 des 4
compétences vivantes) est maintenant dynamique, listant les slots
réellement débloqués+implémentés avec leur touche réelle (E/R/T/G/H).

**`project.godot`** : action `power5` ajoutée (touche H), autoload
`PouvoirRegistry` enregistré.

**`tools/smoke_test_gameplay.gd`** : les 4 checks vivants
(`_check_gueule_vide`/`_check_bras_faux`/`_check_poing_belluaire`/
`_check_poing_tellurique`) fixent maintenant explicitement `RunState.
active_power` (+ `stats.level = 3` pour Bras-Faux, tier 2) avant de
presser leur touche — et Poing Belluaire/Poing Tellurique pressent
maintenant "power1" (plus "power3"/"power4", cf. nouvel ordre de tier).
`"power5"` ajouté à la liste `gameplay_actions_have_no_mouse_button_
bindings`. Nouveau check `_check_power_slot_gating()` : vérifie le
mécanisme lui-même (pas seulement la non-régression) — un slot
débloqué+implémenté est exposé, un slot implémenté mais sous son palier
reste absent puis apparaît une fois le niveau atteint, un appui sur un
slot verrouillé ne déclenche RIEN côté gameplay (pas juste "bouton
absent"), et le ratio de cooldown d'un slot vide est 0.0.

**Vérification** : `scripts/run_gameplay_smoke_test.sh` 100% vert (65
checks, dont les 5 nouveaux). `touch_controls.tscn`/`hud.tscn`/
`character_screen.tscn` non exercés par ce smoke test (aucune scène de
jeu réelle n'y est instanciée) — vérifiés séparément en lançant
`scenes/gameplay/test_arena.tscn` en headless (xvfb + Vulkan logiciel,
15s) : aucune erreur de nœud manquant/script cassé (les 2 erreurs
`tile_set->get_terrain_sets_count() = 0` observées sont préexistantes,
sans rapport avec ce mandat — tileset de terrain, pas UI/Pouvoir).

**Note tooling (hors mandat, corrigée par prudence)** :
`tools/capture_scene.gd` avait deux exemples de docstring ("--action=
power2"/"--action=power4") qui prétendaient encore une identité de
compétence fixe par slot — commentaires seulement corrigés pour
refléter la résolution dynamique via `RunState.active_power`, aucune
nouvelle fonctionnalité ajoutée à l'outil.

Rien à redéployer côté web spécifiquement pour cette passe (aucune
scène de jeu réelle capturée/comparée visuellement) — HUD/touch
vérifiés par lecture de logs headless, pas par capture visuelle Milan.

## 2026-08-22 — Critique probabiliste ("Black Flash", nom de travail — jamais exposé au joueur)

Verrouillé par Milan, aucune question bloquante. État stocké sur
`Player` à côté de `_combo_step` (`_combo_crit_chance_percent`,
`_combo_hit_free_so_far`) — c'est un état de combo, pas une stat de
progression durable, donc pas sur `Stats`.

- **Roulé sur CHAQUE coup** du combo à 3 coups existant (`_try_hit()`),
  aucune restructuration : `randf()*100 < chance_courante`. Vrai
  hasard non seedé assumé ici — Addendum A §A.5 vise les variations
  cosmétiques sans enjeu dans un chemin de feedback (ex. direction d'un
  chiffre de dégâts), pas une probabilité de gameplay que Milan demande
  explicitement aléatoire.
- **Streak** : `_start_attack(1)` réarme `_combo_hit_free_so_far` à
  true (pas les chaînages vers coup2/3). `take_damage()` le passe à
  false immédiatement + reset NET `_combo_crit_chance_percent` à 5%
  (jamais une décroissance), à TOUT moment, pas seulement pendant un
  combo. `_end_combo()` vérifie `_combo_step == 3` (donc un combo
  vraiment complet, pas 1 ni 2 coups) ET `_combo_hit_free_so_far` avant
  d'ajouter +3% (`minf(..., 40.0)`).
- **x1.5** (`CRIT_DAMAGE_MULT`), pas x2 — verdict explicite de Milan.
- **Palier de feedback "critical"** (`combat_feedback.gd`) : au-dessus
  de "catastrophic", dérivé par le MÊME multiplicateur ×1,5 que les
  dégâts (catastrophic 210ms/113ms -> critical 315ms/170ms ; shake heavy
  6px/7 ticks -> critical 9px/10 ticks) — même discipline que le rescale
  de tiers Phase R4, pas des chiffres inventés sans rapport. ÉCRASE le
  tier normal du coup (jamais additionné) : un jab léger critique se lit
  comme le coup le plus lourd du jeu.
- **Flash plein écran, nouveau** (`CombatFeedback.trigger_screen_flash()`/
  `get_screen_flash_color()`, consommé par un `ColorRect` ajouté à
  `hud.tscn`) : "flash, pas juste plus fort" (Milan) — teinte
  (1.0, 0.93, 0.35) jamais utilisée ailleurs dans le HUD/VFX de combat,
  décroissance linéaire nette sur 8 ticks. Délibérément indépendant du
  système de palette (qui aurait limité la distinction à la couleur déjà
  prise par chaque recette) — la garantie de lisibilité en un coup
  d'œil ne dépend d'aucune primitive VFX locale.
- **Signal sonore distinct** : `critical_hit.wav` généré via pyfxr
  (`scripts/generate_sfx.py`, même pipeline que les 6 sons existants) —
  hauteur MONTANTE + punch d'attaque, à l'opposé de light_impact/
  heavy_impact (descendants/plats) pour ne jamais être confondu au
  mixage. Les 6 fichiers existants régénérés à l'identique (seeds fixes
  inchangés, diff vérifié vide) en même passe.
- **Nom de travail** : "Black Flash" n'apparaît nulle part dans un texte
  visible par le joueur (aucun texte UI n'a été ajouté du tout pour ce
  mécanisme — seul le flash/shake/son/dégâts, pas de libellé) —
  respecté par construction, rien à retenir de plus tant qu'aucun nom
  définitif n'est fourni.

**Déterminisme des tests** (le vrai risque de cette passe) : un crit
aléatoire pendant un check existant de dégâts/hitstop exacts l'aurait
fait échouer de façon intermittente — pire, la chance peut monter
jusqu'à 40% au fil de combos propres enchaînés dans la MÊME suite.
Fixé par une seule ligne dans `_ready()` : `_player.
_combo_crit_chance_percent = 0.0` pour toute la suite existante (0% =
jamais de crit, quel que soit `randf()` — pas de seed RNG à contrôler).
Nouveau `_check_critical_hit()` force 100% pour vérifier x1,5/flash/
shake, puis remet 5% pour vérifier le streak (+3% après un combo propre
à 3 coups, reset à 5% sur `take_damage()` direct) par manipulation
d'état, avant de revenir à 0% pour le reste de la suite.

**Vérification** : `scripts/run_gameplay_smoke_test.sh` 100% vert (70
checks, 4 nouveaux). `test_arena.tscn` relancé headless (xvfb) : aucune
erreur de nœud sur le nouveau `ScreenFlash` dans `hud.tscn`.

## 2026-08-22 — MANDAT AUTONOME v3 : Phase 1 (le monde et le décor)

**Contexte** : Milan indisponible pour arbitrer ce mandat (4 phases,
autonomie totale dans les budgets fixés). Ordre d'exécution imposé :
monde d'abord (plus gros manque visuel constaté, et sert de base jugée
pour la suite). Cf. mandat complet archivé dans l'historique de
conversation — pas de fichier dédié, contenu reproduit ici en substance
à chaque décision qui s'y réfère.

**Audit réel des 3 scènes** (lecture complète des 3 `.tscn`, pas une
estimation) : `gate_premiere`/`test_arena`/`outpost` partagent le même
schéma pauvre — `Backdrop` en `ColorRect` plat, `FarBackground`
(`Parallax2D`) ne répétant que 2 textures (`bg_ruin_arch`/
`bg_pillar_silhouette`) 3× chacune, et seulement 4 props uniques
(`prop_pillar`/`prop_rubble_warm`/`prop_brazier`/`prop_debris`)
dispersés par variation de position/flip sur les 14 instances de
`gate_premiere`. Incohérence trouvée en prime : `test_arena.tscn`
utilisait `floor_tileset.tres` (atlas 2 tuiles, aucune donnée de
terrain) alors que `gate_premiere`/`outpost` utilisent déjà
`floor_terrain.tres` (vrai `TerrainSet` à coins Wang) — même script
`arena_floor.gd` dans les 3, donc bascule directe sans risque de
compatibilité.

**Génération PixelLab** (10 `create_map_object`, budget mandat 300 —
10/300 consommés, journalisées dans `data/pixellab_usage.jsonl`) :
- 3 arrière-plans (vue `side`, 224px de haut, même famille d'échelle
  que `bg_ruin_arch`/`bg_pillar_silhouette`) : statue brisée, tour
  effondrée, bannière en lambeaux.
- 5 props de sol (vue `high top-down`, 32×32/32×40, même famille
  d'échelle que `prop_pillar`) : caisse en bois, idole de pierre, pied
  de torche, végétation, poteau de bannière.

**Vérification de palette par échantillonnage HSV réel** (script
Python ponctuel, comptage de pixels opaques par couleur dominante —
même méthode que le verrouillage de `terre.json` en début de session,
jamais à l'œil) : la bannière et les 5 props de sol tombent dans la
même famille de teinte (12-28°, terracotta/bois) que `prop_pillar.png`
— acceptés tels quels. La statue et la tour, en 1re génération,
échantillonnaient hue 228-286° avec jusqu'à 41% des pixels sous 7% de
valeur (violation mesurée de la règle Addendum C "jamais de bande à
0%/100%", et hors de la plage de teinte 250-330° déjà établie par les 2
arrière-plans existants) — **régénérées** (2 générations
supplémentaires, prompt explicitement corrigé vers "purple-brown, never
blue-grey or near-black, amber rim light"). v2 : hue 248-286°/sat
30-93%/val 11-35% — dans la plage de variation déjà réelle entre
`bg_ruin_arch` (ombre 250-266°) et `bg_pillar_silhouette` (326-330°),
bandes de valeur non extrêmes. Acceptées.

**Intégration réelle** (pas de génération orpheline) :
- `test_arena.tscn` : `floor_tileset.tres` → `floor_terrain.tres`
  (fix zéro-génération).
- Les 3 scènes reçoivent les nouveaux assets en positions non
  répétitives (jamais un simple flip d'un asset déjà placé à côté) :
  `gate_premiere` (scène la plus longue, 5 nouveaux arrière-plans + 5
  nouveaux props sur ses ~3900px), `outpost` (1 arrière-plan + 2
  props), `test_arena` (1 arrière-plan + 2 props).
- Capture réelle (`scripts/capture_headless.sh --mode=scene`,
  `gate_premiere.tscn`, 3 positions caméra) : tour effondrée et statue
  visibles en arrière-plan, teinte chaude cohérente une fois composée
  avec `AmbientWarmth`/le shader post-render existants ; nouveaux props
  au sol visibles, aucun chevauchement avec le décor existant.

**Vérification** : `scripts/run_gameplay_smoke_test.sh` 100% vert (76
checks, aucune régression — les scènes ne sont pas exercées par ce
test, mais les modules qu'il couvre — Player/HUD/pouvoirs — ne
dépendent d'aucune des 3 scènes modifiées). Export web régénéré
(`godot4 --headless --rendering-driver vulkan --export-release "Web"
docs/index.html`, précédé d'un `--import` pour cuire les 8 nouveaux
PNG) — `docs/index.pck`/`docs/index.html` à jour.

**Coût réel consommé** : 10 générations PixelLab (10/300 du budget
mandat, largement sous le plafond).

**Non fait / hors scope de cette phase** : pas de retouche des 4 props
déjà existants (mandat ne le demandait pas) ; pas de nouvelle
plateforme de parallaxe intermédiaire (mandat priorise sol/mur >
props > parallaxe lointaine > détail premier plan — le sol était déjà
correct sauf `test_arena`, et le parallaxe lointain a été enrichi mais
pas restructuré en plusieurs plans). Enchaîne sur Phase 2 (animation
Meshy des monstres) sans nouveau prompt, conformément à l'instruction
du mandat.

## 2026-08-22 — MANDAT AUTONOME v3 : Phase 2 (animation des monstres)

**État de départ vérifié** (jamais supposé) : `crawler_frames.tres`/
`brute_frames.tres` n'avaient que `idle`+`attaque`, chacun à UNE seule
frame statique — `ranged_frames.tres` avait en plus `mort` (6 frames).
Aucun des 3 n'avait de "marche" : le déplacement passait par le bob
procédural sinusoïdal de `enemy.gd` (`_update_visual_bob()`), un repli
documenté comme volontaire à l'intégration (Phase 1.1 MANDAT SUITE v2 :
"pas de cycle de marche animé — trop coûteux pour le prototype").

**Ranged — gratuit, retrouvé plutôt que régénéré** : le rig Meshy déjà
payé (`rig_task_id=01a024b4-...`, 5cr dépensés le 2026-08-21) inclut
marche+course de façon permanente (`meshy_rig` : "Walking/Running
animation included FREE"). `meshy_download_model` sur ce même
`task_id` (type `rigging`) a retourné les URLs `basic_animations.
walking_glb_url` directement — **0 crédit supplémentaire**, aucun appel
`meshy_animate`. GLB téléchargé, 6 frames échantillonnées régulièrement
sur l'action existante via Blender headless Cycles (même caméra/lumière
que idle/attaque : `cam_size=2.6`, `target_z=1.092`), quantifiées aux
réglages de lisibilité déjà établis (`--target_saturation=0.55
--dither_amount=0.0 --value_band_min=0.35`).

**Crawler/Brute — 0 crédit, poses à la main sur le rig manuel déjà
validé** : le rig auto Meshy avait échoué sur ces 2 postures (gotcha
déjà documenté, "estimateur conçu pour un bipède debout"), contournement
manuel Blender déjà en place (`crawler_final_rigged.glb`/
`brute_final_rigged.glb`, armatures 13/10 os). Nouveaux scripts
(`experiments/blender_capture/pose_walk_{crawler,brute}.py`) : 4 poses
clés à la main par monstre (Crawler : trot diagonal, front_L+back_R
avancent ensemble puis front_R+back_L ; Brute : marche bipède,
bras/jambe opposés) réutilisant exactement les noms d'os et le cadrage
déjà approuvés pour idle/attaque (aucun nouveau rig). Rendu Cycles
headless, quantifié à `--target_saturation=0.55` (réglages par défaut
sinon, identique à idle/attaque).

**Vérification par échantillonnage visuel réel** (pas supposé) : les
3 planches de contact (`contact_sheet.png` par monstre) montrent des
silhouettes nettement distinctes frame à frame — jambes qui alternent,
bras qui balancent, queue qui oscille (Crawler) — pas 4 copies de la
même pose.

**Câblage jeu** (`src/gameplay/enemy.gd`, `_update_visual_bob()`) :
joue "marche" en boucle si `sprite_frames.has_animation("marche")`
pendant `State.CHASE` à vélocité non nulle, retombe sur "idle" en
sortie de mouvement ; **le bob procédural n'est PAS supprimé** — il
reste le repli pour un futur archétype sans animation dédiée, même
discipline que `_play_visual_animation()` ailleurs dans ce fichier.

**Vérification** : `scripts/run_gameplay_smoke_test.sh` 76/76 vert
(inclut les 3 checks qui exercent le mouvement des monstres :
`crawler_chases_then_hits_player`, `brute_telegraphs_before_landing_a_
heavier_hit`, `ranged_retreats_to_preferred_range_then_hits_player_
with_projectile`). Capture réelle en jeu (`capture_headless.sh
--mode=scene`, `test_arena.tscn`, tick 3 après spawn) : le Crawler
affiche une pose de marche (jambe avant tendue, corps abaissé),
visuellement distincte de son idle — confirmé à l'écran, pas seulement
en test unitaire. Export web régénéré.

**Coût réel consommé (Meshy)** : 0 crédit ce mandat (866/866 restants,
inchangé) — le seul appel a été un `meshy_download_model` gratuit sur
une tâche déjà payée. Budget de 150cr entièrement disponible pour les
phases suivantes si nécessaire.

**Non fait / hors scope de cette phase** : pas de retouche de l'attaque
existante (déjà présente, mandat priorise marche > attaque > mort) ;
Crawler/Brute restent sans "mort" dédiée (seul Ranged en a une,
héritage Phase 1.2 MANDAT SUITE v2 — pas demandé par cette phase, qui
priorise explicitement la marche). Enchaîne sur Phase 3 (compétences
restantes) sans nouveau prompt, conformément à l'instruction du mandat.

## 2026-08-22 — MANDAT AUTONOME v3 : Phase 3, point d'attention (fissure Poing Belluaire)

**Corrigé, vérifié visuellement** : Poing Belluaire n'avait aucune couche
de fissure au sol malgré la référence archivée (`docs/references/
monstrification/coup_de_poing_monstrifie.png`, colonne "Assets - Effets",
case du milieu) qui en montre une nettement — écart identifié lors de
l'audit palette du début de session, laissé non corrigé à l'époque.

Ajout d'une couche `fractureLine` en contact/conséquence (`data/recipes/
power.poing_belluaire.cast.json`, ticks 20-34, `degradable: true`, même
raisonnement que `dustKick` sur Poing Tellurique : c'est la conséquence
de l'impact, pas le contact lui-même). **Aucune nouvelle couleur** :
`data/palettes/parasite.json` nommait déjà explicitement `fractureLine`
dans son rôle 2 ("brun-rouille profond") depuis la réécriture de palette
plus tôt cette session — l'écart n'était que dans cette recette.

Vérifié par exécution réelle, pas supposé : `run_vfx_recipe_smoke_test.sh`
(15/15 primitives dont fractureLine spawn/tick/cleanup sans erreur),
`run_gameplay_smoke_test.sh` (76/76, aucune régression sur les checks
Poing Belluaire existants), et une capture en jeu réel (`tools/
capture_scene.gd --mode=player_action`, nouveau `--active_power=`/
`--level=` ajoutés à cet outil de capture pour forcer le Pouvoir tiré au
hasard sans debugger headless — pas un changement de gameplay, un
paramètre de dev uniquement) : à tick 30, des segments de fissure brun
radiant depuis le point d'impact sont visibles à l'écran, distincts du
burst gris d'impactStar — correspond à la référence.

## 2026-08-22 — MANDAT AUTONOME v3 : Phase 3, Marée de Sable (Terre, Tier 2)

**Choix explicite** : parmi les 11 compétences manquantes, priorité à
l'ordre de déblocage verrouillé (tier le plus bas d'abord). Les 3 tier 1
existent déjà. Des 2 tier 2 restantes (Corbeau Pâle/Invocateur, Marée de
Sable/Terre), Marée de Sable choisie pour cette passe — même Classe que
Poing Tellurique déjà vivant (palette/archétype de départ partagés,
risque le plus bas pour une seule compétence livrée et vérifiée de bout
en bout, conformément à la consigne du mandat "une compétence terminée
vaut mieux que trois à moitié faites").

**Référence** (`docs/references/terre/maree_de_sable.png`) : "Une vague
de sable déferle sur une ligne devant Rank Zero, ralentissant et
entravant les ennemis touchés" (Tier 2, LIGNE, CONTRÔLE). 4 temps :
Préparation/Lancement/Déferlement/Fin.

**Nouvel archétype de cast `line_wave`** (aucun des archétypes existants
— arc de mêlée, coup frontal — ne correspond à "une vague qui voyage en
ligne droite") : `beamSegment`, seule primitive du registre déjà
documentée pour ce cas exact ("l'archétype de cast 'projection avant'...
un tir qui part du joueur en ligne droite", encore sans exemple concret
avant cette passe). `data/recipes/power.maree_de_sable.cast.json` :
converge (anticipation, le sable se rassemble) → beamSegment (core, la
vague voyage) → dustKick (contact, gicle au passage) → smokePuff
(conséquence, poussière qui retombe). Palette `terre` RÉUTILISÉE, 2
usages étendus (`ocre clair`→beamSegment, `poussière pâle`→smokePuff)
sans nouvelle couleur — la référence montre exactement ce sable déjà
mesuré dans cette palette.

**Nouveau : ciblage en LIGNE** (`Targeting.enemies_in_line()`,
`src/gameplay/targeting.gd`) — distinct du cône `enemies_in_arc()` déjà
utilisé par Bras-Faux/Poing Tellurique : une ligne garde une largeur
CONSTANTE sur toute sa portée (projection avant/latérale sur `facing`/
sa perpendiculaire), un cône s'élargit avec la distance. Premher usage
réel de cette forme dans le jeu.

**Nouveau : ralentissement** (`Enemy.apply_slow()`, `src/gameplay/
enemy.gd`) — première mécanique de "contrôle" du jeu, générique plutôt
que spécifique à cette seule compétence (état à expiration par compte
de ticks, jamais cumulatif — le plus récent écrase toujours l'effet en
cours). Consommé dans `_chase_velocity()` (multiplie `stats.move_speed_px`).

**Gameplay** (`src/gameplay/player.gd`) : `_start_maree_de_sable()`/
`_advance_maree_de_sable()`/`_try_hit_maree_de_sable()` — même
construction 3 phases que Poing Tellurique (aucun déplacement
automatique). Portée 90px (vs 44px pour un poing — "une vague voyage"),
demi-largeur 15px, dégâts 8 (le plus faible des 4 compétences vivantes —
Tier CONTRÔLE, pas dégâts), ralentissement ×0,5 pendant 90 ticks
(1,5s). Enregistrée dans `IMPLEMENTED_SKILL_HANDLERS`/
`IMPLEMENTED_SKILL_COOLDOWN_GETTERS` (slot "power2", tier 2 de Terre —
même mapping que Bras-Faux/tier 2 de Monstrification).

**Vérification** : 4 nouveaux checks (`tools/smoke_test_gameplay.gd`,
`_check_maree_de_sable()`) — démarrage+anim, ligne touche la cible dans
l'axe MAIS épargne une cible décalée latéralement (au-delà de la
demi-largeur) ET une cible au-delà de la portée (2 angles distincts,
jamais testés ensemble avant sur un cône), ralentissement appliqué
uniquement à la cible touchée, fin+cooldown. `run_gameplay_smoke_test.sh`
80/80 vert. Capture réelle (`capture_scene.gd --mode=player_action
--action=power2 --active_power=terre --level=3`) : ligne de segments
ocre visible s'étendant du joueur, distincte du burst blanc de contact —
confirme le rendu "ligne qui voyage" à l'écran, pas seulement en test.

**Non fait** : Corbeau Pâle (Invocateur, tier 2) et les 8 compétences
restantes (tiers 3-5) — hors budget de cette session, aucun blocage
technique identifié pour la suite (même méthode directement
réutilisable). Enchaîne sur Phase 4 (housekeeping) sans nouveau prompt.

## 2026-08-22 — MANDAT AUTONOME v3 : Phase 4 (housekeeping)

**Worklog archivé** : `docs/worklog.md` dépassait 6300 lignes (6657
exactement). Split par date à une frontière de section propre (fin de
"Phase 2.3+2.4" MANDAT SUITE v2, ligne 5256) : les 51 premières entrées
datées (2026-08-18 → 2026-08-21 inclus) déplacées telles quelles, sans
réécriture, dans `docs/worklog-archive-2026-08-18-a-2026-08-21.md`
(5259 lignes). `docs/worklog.md` ne garde que les 19 entrées du
2026-08-22 (1425 lignes) + un index en tête résumant la période
archivée et expliquant la règle de split pour la prochaine fois.
Contenu total inchangé (6684 lignes réparties sur 2 fichiers vs 6657
avant, différence = les quelques lignes d'index ajoutées).

**STATUS.md — écart réel trouvé et documenté** : le mandat demandait de
"compacter STATUS.md pour refléter l'état actuel" en supposant son
existence. Vérifié par recherche exhaustive (`find`/`ls`) : **ce fichier
n'existait nulle part dans ce dépôt**, ni à la racine ni sous `docs/` —
aucune trace non plus dans `docs/worklog.md` d'une référence à un tel
fichier. Pas une contradiction entre deux sources (rien à trancher),
juste une prémisse fausse du mandat sur l'état du dépôt. Décision (choix
d'implémentation, pas de contenu narratif inventé) : créer `docs/
STATUS.md` neuf plutôt que chercher un fichier de remplacement supposé
— contenu factuel uniquement (tableau des 5/15 compétences réellement
implémentées, état monstres/monde/pipeline, budgets consommés,
prochaine priorité), aucune invention, tout dérivé de ce qui est déjà
vrai dans le code/les recettes/les journaux d'usage.

**Vérification** : `run_gameplay_smoke_test.sh` 80/80 vert (changement
100% documentation, aucun fichier de code touché — vérifié quand même
par discipline, jamais supposé "sans risque" sans le confirmer).

## 2026-08-22 — MANDAT AUTONOME v3 : Rapport final

Milan indisponible pour arbitrer cette session (mandat explicite,
autonomie totale dans les budgets fixés). 4 phases exécutées dans
l'ordre imposé, chacune commitée/poussée séparément.

### Ce qui est vraiment fait et vérifié, phase par phase

**Phase 1 (monde/décor)** — TERMINÉ. Audit réel des 3 scènes (flat-
color backdrops, parallaxe ne répétant que 2 textures, 4 props uniques
seulement). 8 assets PixelLab générés (statue/tour/bannière en
arrière-plan + caisse/idole/torche/végétation/poteau en props de sol),
2 régénérés après échantillonnage HSV réel ayant mesuré une palette
hors plage (corrigé). Intégrés dans les 3 scènes en positions non
répétitives. Fix bonus : `test_arena.tscn` uniformisé sur
`floor_terrain.tres` (comme les 2 autres scènes). Vérifié : smoke test
76/76, capture en jeu réel (3 angles caméra). Coût : 10/300 générations
PixelLab.

**Phase 2 (animation des monstres)** — TERMINÉ. Les 3 monstres avaient
un bob procédural, jamais de vraie marche. Ranged : marche+course déjà
incluses gratuitement dans son rig Meshy payé — récupérées via
`meshy_download_model`, 0 crédit. Crawler/Brute : 4 poses de marche à
la main sur leur rig manuel Blender déjà validé (le rig auto Meshy
échoue sur leurs postures). Câblé dans `enemy.gd` (`_update_visual_bob`
préfère "marche" si l'animation existe, repli bob procédural conservé
pour un futur archétype sans anim dédiée). Vérifié : smoke test 76/76
(dont les 3 checks qui exercent le mouvement des monstres), capture en
jeu réel confirmant une pose de marche distincte de l'idle à l'écran.
Coût : 0 crédit Meshy (866/866 restants).

**Phase 3 (compétences)** — PARTIEL, honnêtement. Deux livrables réels :
(1) fissure au sol manquante sur Poing Belluaire (écart identifié lors
de l'audit palette en début de session) corrigée — couche `fractureLine`
ajoutée, aucune nouvelle couleur (la palette la nommait déjà), vérifié
par smoke test + capture réelle (segments de fissure visibles). (2)
Marée de Sable (Terre, Tier 2) implémentée de bout en bout : nouvel
archétype de cast "ligne qui voyage" (`beamSegment`), nouveau ciblage en
ligne (`Targeting.enemies_in_line()`), nouvelle mécanique de
ralentissement générique (`Enemy.apply_slow()`), 4 nouveaux checks smoke
test, capture réelle confirmant le rendu. **10 des 11 compétences
manquantes restent non implémentées** (Corbeau Pâle, Poing du Colosse,
Œil Sans Regard, Serpent Creux, Carapace, Effondrement, Fissure
Éruptive, Mâchoire, Forme Bestiale, Pattes de Chasse) — choix délibéré
de livrer une compétence complète et vérifiée plutôt que plusieurs
ébauches, conformément à la consigne explicite du mandat. Aucun blocage
technique : la méthode (VFX recipe → gameplay → mécanique générique si
besoin → smoke test dédié → capture réelle) est directement
réutilisable pour les 10 restantes, dans l'ordre de tier verrouillé.

**Phase 4 (housekeeping)** — TERMINÉ. `docs/worklog.md` (6657 lignes)
archivé par période (2026-08-18 → 2026-08-21 dans un fichier séparé,
2026-08-22 conservé, 1425 lignes). `docs/STATUS.md` — écart réel trouvé
(le fichier n'existait pas du tout, contrairement à ce que le mandat
supposait) — créé neuf avec un état factuel du dépôt.

### Ce qui est bloqué, et ce qu'il faudrait pour débloquer

Rien n'est bloqué techniquement. La seule limite rencontrée sur toute
la session est le **temps/budget de cette session elle-même** pour la
Phase 3 (10 compétences sur 15 restent à écrire). Aucune décision de
Milan n'est nécessaire pour les 10 compétences restantes : chacune a
déjà (a) un sprite de référence archivé, (b) un tier verrouillé, (c)
une méthode éprouvée deux fois cette session (Poing Belluaire fix,
Marée de Sable). Un point RÉEL à trancher par Milan un jour (pas
bloquant pour continuer les compétences) : aucun des 15 combats n'a
encore de sprite Godot dédié (tous utilisent "coup1"/"coup2"/"coup3"
en placeholder) — pas un problème pour cette session, mais un vrai
manque d'identité visuelle qui grandira à mesure que plus de
compétences existent sans art propre.

### Coût réel consommé (mesuré, pas estimé)

- PixelLab : 10 générations / 300 (Phase 1 uniquement).
- Meshy : 0 crédit / 150 (Phase 2 — récupération gratuite d'un rig déjà
  payé, aucun nouvel appel facturé).

### Recommandation pour la prochaine session

Continuer Phase 3 dans l'ordre verrouillé : Corbeau Pâle (Invocateur,
Tier 2) en premier — référence déjà archivée
(`docs/references/invocateur/corbeau_pale.png`), même méthode
directement réutilisable. Après les 5 compétences Tier 2 restantes du
même ordre de priorité (tiers bas = plus visibles), envisager l'art
dédié par compétence (point non bloquant relevé ci-dessus) comme
chantier séparé, une fois plus de compétences vivantes pour juger si le
partage "coup1/coup2/coup3" reste lisible ou commence à confondre les
Pouvoirs entre eux.

## 2026-08-23 — Agent Décor test_arena : vérification du rôle réel AVANT retouche (verdict : hors scope, aucune retouche)

Mandat : traiter `scenes/gameplay/test_arena.tscn` comme `outpost`/
`gate_premiere` (PointLight2D réels, props PixelLab, vérification HSV)
**mais seulement si la scène est réellement vue par un joueur** —
vérifier le rôle réel en premier, ne pas dépenser de budget par défaut.

**Enquête (code, pas supposition)** :
- `grep -rn "test_arena" --include="*.gd" --include="*.tscn" .` :
  aucune occurrence dans un chemin de transition de scène. Les seuls
  hits `.gd` sont des commentaires de doc (`camera_director.gd`,
  `ground_decal.gd` — "Player.tscn partagé par gate_premiere/
  test_arena/outpost", pas un `load()`/`change_scene`).
- Tous les appels réels de `get_tree().change_scene_to_file(...)` du
  dépôt (`src/world/gate_entrance.gd`, `src/world/gate_premiere.gd`) :
  seulement `outpost.tscn` ⇄ `gate_premiere.tscn`. `gate_entrance.gd`
  a un `@export var target_gate_scene`, mais sa valeur câblée dans
  `outpost.tscn` (`scenes/gameplay/outpost.tscn:147`) est en dur
  `"res://scenes/gameplay/gate_premiere.tscn"` — aucune Gate, aucun
  menu, aucun sélecteur de niveau ne pointe vers `test_arena.tscn`.
  `run/main_scene` de `project.godot` = `outpost.tscn`.
- Seules occurrences du chemin exact `res://scenes/gameplay/
  test_arena.tscn` dans tout le dépôt : `.godot/editor/
  project_metadata.cfg` sous `[recent_files]` (liste des scènes
  récemment ouvertes **dans l'éditeur Godot** — métadonnée d'IDE, zéro
  rapport avec le jeu en exécution) et l'export web compilé
  (`docs/index.pck`, qui embarque toutes les scènes du projet par
  défaut, reachable ou non — n'implique pas une exposition joueur).
  Aucun script de capture/smoke test dans `scripts/` ne référence
  `test_arena` par nom (le smoke test lance `tools/
  smoke_test_gameplay.tscn`, une scène de mock séparée).
- Confirme et recoupe deux constats déjà posés par des agents
  précédents sur ce même dossier : `docs/worklog-archive-2026-08-18-
  a-2026-08-21.md:3916` ("`test_arena.tscn` n'est référencée nulle
  part comme cible de transition, laissée de côté") et `docs/
  STATUS.md:20` qui la catégorise explicitement `test_arena (bac à
  sable)` face à `gate_premiere` (parcours complet) et `outpost` (hub).

**Verdict** : `test_arena.tscn` est une scène de test technique interne
— un bac à sable créé pour l'itération développeur/QA (composition
Player + ennemis à distances contrôlées), jamais instanciée par un
menu, un hub, une Gate ou un sélecteur accessible en jeu, et absente de
tout chemin `change_scene_to_file()` réel. Un vrai joueur en conditions
normales ne peut pas l'atteindre. Note pour mémoire : des passes
antérieures (parallaxe, uniformisation du sol `floor_terrain.tres`,
recherche d'éclairage) l'ont néanmoins touchée par le passé, mais
toujours dans le cadre de passes systémiques sur les 3 scènes
ensemble (jamais un mandat dédié "décor test_arena" comme celui-ci) —
ça ne change pas le verdict d'accessibilité joueur ci-dessus.

**Décision** : aucune retouche visuelle. Pas de `PointLight2D`
supplémentaire, pas de génération PixelLab, pas de capture avant/après,
pas de mesure `validate_pixels.py` — appliquer le traitement `outpost`/
`gate_premiere` ici serait du travail décoratif sur une scène que
personne ne voit, contraire à la consigne explicite du mandat
("inutile de la peaufiner visuellement... dis-le clairement plutôt que
de dépenser du budget PixelLab dessus par défaut").

**Coût réel consommé** : 0 crédit PixelLab, 0 crédit Meshy (solde non
consulté — non applicable, aucune dépense envisagée après l'enquête).

**Fichiers modifiés** : uniquement cette entrée de worklog. Aucun
fichier de scène (`test_arena.tscn` ou autre) touché.
