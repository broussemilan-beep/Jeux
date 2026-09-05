# Scène de combat — Hero vs Rival, deux rigs actifs, puis trône (R6, Roblox)

Prototype isolé, sans lien avec RANK ZERO ni MyAnimeRPG — même isolation
que les autres prototypes de `experiments/` (voir CLAUDE.md). Réutilise
**telle quelle** l'infrastructure déjà vérifiée de `r6_hit_combo`
(`r6_rig.py`, `anim_engine.py`, `export_kfseq.py`, `resolve_rbxmx.py`,
le rig `RigR6.rbxmx`, `vendor/three.min.js`, `textures/ruin_wall.png` +
`stone_ground.png`) ET de `r6_throne_crown` (`props.py`,
`compute_crown_track.py`, `export_model.py`, les textures/PBR
cobblestone/fabric/marble/metal/slate/wood). Copies volontaires, pas
d'import croisé entre prototypes — voir convention du dépôt.

## Demande

Après quatre passes de correction sur `r6_hit_combo` (jeu de jambes,
smoothness/hold-and-snap, placement des pieds, axes des jambes — voir le
README de ce prototype), demande explicite : « Okk maintenant que tu a
appris fais moi une scène complète d'un combat entre les d'au moins 30 s
avec plus que du combo poing et je veux de la puissance du fluide et du
décors qui se casse entre les 2 rig puis le gagnant marche et tu met
l'animation en cohérence du tron et de la couronne. »

Six exigences distinctes, toutes structurantes :
1. Une scène de combat **complète**, entre **deux combattants ACTIFS**
   (pas un attaquant contre un mannequin statique).
2. Au moins **30 secondes**.
3. **Plus que du combo de poing** — de la variété de coups.
4. **Puissance** et **fluidité** — appliquer tout ce qui a été appris sur
   `r6_hit_combo` (hold-and-snap, placement des pieds mesuré, axes des
   jambes qui changent selon le coup).
5. Un **décor qui se casse** entre les deux rigs.
6. Le **gagnant marche**, et l'animation doit être **en cohérence** avec
   la scène du trône et de la couronne (`r6_throne_crown`) — pas une
   scène de victoire déconnectée, un vrai raccord vers la montée des
   marches / l'assise / le couronnement.

## Stratégie : réutiliser plutôt que tout recalibrer

Recalibrer un combat entier (deux combattants, nouveaux coups, décor)
depuis zéro aurait été extrêmement coûteux. Décision explicite de
gestion de portée : **réutiliser le combo jab/cross/hook déjà calibré et
vérifié de `r6_hit_combo` par TRANSLATION/RÉFLEXION** (aucune nouvelle
mesure), et ne réserver l'effort de calibration qu'aux coups
**réellement nouveaux** (coup de pied, finisher) qui n'ont aucun
équivalent calibré.

Le principe mathématique (voir la docstring de `scripts/choreography.py`
pour le détail) : un point de contact déjà calibré, translaté ou reflété
par un vecteur/axe constant, reste calibré — la géométrie relative ne
change pas. Deux cas utilisés :

- **Translation pure** (`OFFSET_Z`) quand le personnage réutilisé garde
  la même orientation : le combo complet de Hero (Beat 2) est
  `punch_combo.attacker_combo()`/`dummy_combo_reaction()` copiés tels
  quels, juste décalés en Z et en temps.
- **Réflexion** (`REFLECT_C`, `Z' = REFLECT_C - Z`) quand la pose est
  rejouée sur un personnage qui regarde dans l'autre sens (Rival, yaw
  180°) : le jab d'ouverture de Rival (Beat 1) est le jab de
  `attacker_combo()` reflété, et la réaction de Hero est la réaction du
  mannequin reflétée elle aussi, avec la MÊME constante `REFLECT_C` —
  aucune mesure séparée.

Les rotations LOCALES (Torso/Head/Arms/Legs) ne dépendent jamais du yaw
du personnage qui les porte : elles sont réutilisées telles quelles dans
les deux cas, seuls `root_pos.Z` et `HumanoidRootPart` (yaw) sont
transformés.

Vérifié numériquement (`scripts/calibrate_battle.py`) — les écarts de
contact retombent EXACTEMENT sur les valeurs déjà connues de
`r6_hit_combo` :

```
rival_jab   (t=5.50s) : ecart=0.493 stud   (identique au jab de r6_hit_combo)
hero_jab    (t=7.17s) : ecart=0.493 stud
hero_cross  (t=7.77s) : ecart=0.366 stud
hero_hook   (t=8.47s) : ecart=0.380 stud
```

## Disposition de l'arène

`HERO_HOME_Z = -14.0` (côté trône), `RIVAL_HOME_Z = -19.4` (plus loin),
même écart (`HOME_GAP = 5.4`) que l'attaquant/mannequin de
`r6_hit_combo` — choisi exprès pour que la translation/réflexion
ci-dessus tombe juste. Le pilier destructible est à
`PILLAR_POS = (3.4, 0.0, -21.6)`, entre les deux combattants et légèrement
excentré (pour que la projection du coup de pied ait une vraie
trajectoire, pas juste un aller-retour sur l'axe). Après sa victoire,
Hero n'a qu'à AVANCER en +Z pour rejoindre le pied de l'escalier du
trône (`throne_sequence._CLIMB_Z0 = -7.2`) — jamais reculer, jamais de
demi-tour supplémentaire au-delà de celui déjà chorégraphié en Beat 5.

## Chorégraphie : 6 temps (`scripts/choreography.py`)

- **Beat 0** (0 → 5.0 s) — garde, face à face, tenue (vrai hold, pas un
  point de passage — tension avant l'échange).
- **Beat 1** (5.0 → ~5.7 s + 1.0 s de retour au calme) — Rival ouvre
  avec un jab (réfléchi), Hero encaisse et secoue la tête (réaction du
  mannequin, réfléchie).
- **Beat R — regroupement** (~2.2 s) — Rival, encore hébété du hook
  qu'il va recevoir en Beat 2, se retourne et se replace en garde
  pendant que Hero recule à distance de combat. Aucun coup ne part ici
  (rien à calibrer), seulement du placement — donne au combat une vraie
  respiration au lieu d'un enchaînement mécanique beat-après-beat.
- **Beat 2** (~7.0 → ~9.8 s) — combo complet de Hero (jab/cross/hook,
  translaté, zéro recalibrage) : Rival encaisse les trois coups avec une
  intensité croissante, jusqu'à l'hébètement.
- **Beat 3** (~11 → ~14 s) — Rival charge un **grand crochet
  télégraphié** (hold-and-snap, l'amplitude la plus grande du combat —
  il doit se lire comme "en train de rater"), Hero **esquive** (pas de
  contact à calibrer, juste s'assurer que le poing ne touche pas), puis
  contre-attaque au **coup de pied circulaire** (nouveau type de coup —
  "plus que du combo poing") qui projette Rival contre le **pilier
  destructible**.
- **Beat 4** (~14.5 → ~17.6 s) — Rival titube en se redressant vers le
  centre, Hero **achève** avec un dernier coup façon hook (le
  "finisher") — Rival s'effondre, KO, pour le reste de la scène.
- **Beat 5** (~17.6 → 31.7 s) — victoire : flex tenu (~1,3 s de
  transition + 3,5 s de hold), demi-tour en trois temps (tête en avance/
  "spotting", rotation du corps pendant que la jambe libre est encore en
  l'air, jambe replantée puis torse qui rattrape en dernier — **même
  technique, mêmes proportions temporelles** que le demi-tour de
  `throne_sequence.climb_stairs()`, réutilisée pour la cohérence de
  style demandée par l'utilisateur), puis marche (17 foulées, bras figés
  pendant toute la locomotion — encore la même convention que
  `climb_stairs()`, qui ne fait jamais osciller les bras) jusqu'à une
  pose qui coïncide **EXACTEMENT** avec le premier keyframe de
  `throne_sequence.climb_stairs()` (même position, même pose, écart
  mesuré < 0.001 stud, dû uniquement à l'arithmétique flottante).

Durée du combat seul : **`TOTAL_FIGHT_DURATION` ≈ 31,7 s** (exigence
utilisateur : ≥ 30 s, marge volontaire d'1,7 s après mesure, pas au
ras). Durée totale (combat + montée + assise/couronnement) :
**`TOTAL_SCENE_DURATION` ≈ 38,3 s**.

## Calibration des coups nouveaux (`scripts/calibrate_battle.py`)

Contrairement au jab/cross/hook, le coup de pied et le finisher n'ont
aucun équivalent déjà calibré — leurs valeurs ont été trouvées par
**recherche numérique** (balayage de la rotation du torse, de la jambe
d'appui, de la jambe qui frappe, et de l'avancée du bassin, en cherchant
l'écart minimal entre la cinématique directe du membre qui frappe et le
torse de la cible — même principe que `grounded_root_y`, jamais à
l'œil), puis re-vérifiées via le moteur bpy réel :

```
kick       (t=13.67s, Right Leg) : ecart=0.824 stud   (KICK_LUNGE_Z=-14.0)
finisher   (t=16.99s, Left Arm)  : ecart=0.475 stud   (FINISH_LUNGE_Z=-16.9)
```

Le finisher retombe dans la même fourchette que les poings (0.37-0.49).
Le coup de pied, lui, plafonne mesurablement plus haut (~0.82 stud) —
écart **documenté, pas caché** : une jambe sans genou, sans avancée du
bassin capable d'égaler celle d'un bras, ne peut pas atteindre la même
précision de contact qu'un poing sur ce rig. La recherche a par ailleurs
confirmé que la contrainte de **renversement de signe de l'axe Z de la
jambe qui frappe** (chambrage à `-24°`, lâcher à `+4°` — même principe
que l'inversion d'axe des bras établie sur `r6_hit_combo`, retour
utilisateur "les axes des jambes doivent changer selon l'envoi") coûte
environ +0.1 à +0.2 stud d'écart par rapport à un renversement non
contraint — un compromis mesuré et accepté, pas un renversement abandonné
pour gagner en précision (même arbitrage que le Round 4 de
`r6_hit_combo`, où un renversement de jambe plus petit avait déjà été
préféré à un flottement de pied plus grand).

## Placement des pieds (`scripts/foot_check_battle.py`)

Étend `r6_hit_combo/scripts/foot_check.py` (qui ne vérifiait QUE
l'attaquant) aux deux combattants actifs, à chaque instant-clé des deux
pistes. Résultat après correction : **zéro anomalie non expliquée** sur
les deux pistes (tolérance 0.30 stud, seuil déjà établi sur
`r6_hit_combo`) ; tous les dépassements de tolérance restants sont des
instants volontairement en l'air (vol après le coup de pied et le hook,
affaissement contre le pilier, effondrement final, chambrage du coup de
pied) explicitement listés et justifiés dans le script.

Une découverte au passage : `punch_combo.dummy_combo_reaction()` tient
sa pose hébétée finale (`DAZED_*`) à une hauteur `root_pos.Y` **plate**
(`GROUND_Y`, jamais calée par cinématique directe) — invisible dans
`r6_hit_combo` puisque son mannequin est statique et jamais scruté côté
pieds (son propre `foot_check.py` ne vérifie que l'attaquant). Rival,
ici, TIENT cette même pose plusieurs secondes en tant que combattant
actif : le flottement mesuré (~0.28-0.35 stud) devient visible. Corrigé
localement dans `choreography.py` (`DAZED_GROUNDED_ROOT_Y`, calculé par
`grounded_root_y_balanced`), sans toucher à `punch_combo.py` — la
correction s'applique aux trois endroits où la pose `DAZED_*` est
tenue plusieurs secondes (Beat R, Beat 2, Beat 4), jamais aux
transitoires de moins de 0.3 s (whiplash/lâcher), conformes au principe
hold-and-snap : seuls les HOLDS doivent être bien plantés.

## Décor destructible (`scripts/props_battle.py`)

Un pilier de pierre en ruine (même famille visuelle que les textures
`ruin_wall`/`stone_ground` déjà utilisées par le lecteur de
`r6_hit_combo` — l'arène du combo de poing était déjà une ruine, le
pilier s'y intègre plutôt que d'introduire un nouveau style), colonne
"cannelée" (tambours empilés, chapiteau déjà ébréché — lisible comme
"va se briser" avant même l'impact) :

- `pillar_parts(center)` — état intact, visible de t=0 à `PILLAR_HIT_T`.
- `pillar_debris_parts(center, seed=6)` — 16 fragments (6 gros blocs +
  10 éclats), dispersés de façon **déterministe**
  (`random.Random(seed)`, jamais `random.random()` nu — un seed fixe
  donne toujours la même scène de débris, reproductible d'une capture à
  l'autre) autour du centre du pilier, visible à partir de
  `PILLAR_HIT_T`.

Bascule entre les deux états gérée côté lecteur (scripted, pas de
simulation physique temps réel — cohérent avec le reste du pipeline).

## Lecteur (`scripts/dump_scene_data.py` + `build_viewer.py` + `battle_throne_viewer.html`)

`dump_scene_data.py` échantillonne `hero_track()`/`rival_track()`
**directement** via `anim_engine.build_rig()`/`apply_choreography()`/
`sample()` (comme `calibrate_battle.py` -- pas de round-trip par un
`.rbxmx` exporté). Il recalcule aussi la trajectoire de la couronne
(coussin → main → tête) à partir des échantillons de Hero, avec la même
recette que `r6_throne_crown/scripts/compute_crown_track.py` (ce fichier
n'est pas directement importable ici -- ses propres imports ne résolvent
pas dans ce prototype isolé -- la recette est donc reproduite localement,
documentée dans la docstring). Géométrie statique exportée telle quelle :
`props.staircase_parts()`/`throne_parts()`, `props_battle.pillar_parts()`/
`pillar_debris_parts()`.

`battle_throne_viewer.html` réutilise telles quelles les briques déjà
vérifiées des deux prototypes source : le rendu de rig et le système VFX
d'impact (flash plein écran bref + éclats/anneau de choc) de
`r6_hit_combo`, le rendu de Parts (boîtes/cylindres texturés) et
l'éclairage/la caméra de la montée-assise-couronnement de
`r6_throne_crown`. Deux rigs indépendants, bascule pilier intact/débris
au moment exact de `PILLAR_HIT_T`, caméra dynamique suivant l'action
pendant le combat puis les six plans chorégraphiés du trône à partir de
`BEAT5_END`.

**Piège de vérification rencontré, pas un bug** : chaque impact déclenche
un flash plein écran de ~50 ms (bloc `return` anticipé dans le code VFX
partagé) *avant* que les éclats en étoile ne s'affichent. Un premier
passage de capture à `+0.02s` après l'instant du coup de grâce
(`FINISH_STRIKE_T`) tombait pile dans cette fenêtre et ne montrait qu'un
flash blanc sans les rigs -- lu à tort comme "caméra qui vise le vide".
Vérifié faux en comparant `-0.15s / +0.02s / +0.05s / +0.08s / +0.20s`
autour de l'impact : la caméra ne bouge jamais, seul le VFX traverse sa
propre sous-phase de flash. Toutes les autres captures d'impact avaient
simplement été prises après cette fenêtre par hasard.

## Passe « attente vivante » (pieds encrés / manque de fluidité)

Retour utilisateur explicite : « ça manque de fluidité, de idle pose, de
mouvement style combat... les pieds tjrs trop encré dans le sol et pas en
mouvement avec les geste. »

Diagnostic mesuré (pas suppose) : les deux plus longs holds de la scène
étaient des holds **plats** -- littéralement 2 keyframes identiques,
aucune interpolation entre les deux :
- Beat 0 (garde d'ouverture) : **5.0 s** entièrement figées.
- Beat 5 (flex de victoire) : **3.5 s** entièrement figées.

Ironie mesurée : ces deux durées avaient été **volontairement gonflées**
lors de la passe précédente pour atteindre l'exigence "≥ 30 s" -- en
ajoutant du temps mort plutôt que du mouvement, cette meme passe a
directement causé le probleme signalé ici. La bonne reponse n'est pas
de raccourcir ces holds (la duree totale doit rester ≥ 30 s) mais de
remplacer le temps mort par du VRAI mouvement.

Distinction explicite avec la leçon "hold-and-snap" (voir README de
r6_hit_combo) : cette leçon reste valable pour un **coil de frappe** (la
charge d'un coup DOIT se figer, c'est la tension qui rend le lâcher
lisible). Mais un combattant qui **attend** (garde avant l'échange, pose
de victoire tenue) n'est jamais parfaitement immobile dans la réalité --
il bouge en continu (transfert de poids pied à pied, léger balancement
du buste), même sans rien "faire". Ce sont deux vocabulaires distincts,
pas une contradiction.

Correctif : `_idle_stance_span()` (`scripts/choreography.py`) génère une
oscillation continue (transfert de poids Left/Right Leg en opposition de
phase + léger balancement `Torso.Y`, `root_pos.Y` recalé à chaque
keyframe par `grounded_root_y_balanced` pour que les pieds restent
plantés) au lieu d'un hold à 2 keyframes -- bornée à la pose de base
exacte aux deux extrémités (aucun saut au raccord avec ce qui précède/
suit). Appliqué à :
- **Beat 0** (garde, 5.0 s) : Hero et Rival oscillent à des cadences
  différentes (0.58 s / 0.50 s) et en opposition de phase, pour ne pas
  lire comme deux miroirs synchronisés.
- **Beat 5** (flex de victoire, 3.5 s) : amplitude réduite (2.5°/1.5°
  contre 3°/2° pour la garde) -- une pose de triomphe tenue oscille
  moins qu'une garde de combat.
- **Beat R** (Rival hébété) : amplitude et cadence **augmentées**
  (5°/4°, période 0.40 s) -- ça doit lire comme un vacillement, pas une
  garde.

Revérifié après coup, rien n'a régressé :
`calibrate_battle.py` -- écarts de contact inchangés (0.493/0.366/0.380/
0.824/0.475 stud, aucune valeur modifiée par cette passe, purement une
question d'attente entre les coups) ; `foot_check_battle.py` -- toujours
zéro anomalie non expliquée (l'oscillation reste sous le seuil de
tolérance grâce au recalage `grounded_root_y_balanced` par keyframe).

## Vérification (captures)

Captures dans `captures/verification/` (rendu réel du lecteur, via
Playwright, pas décrites en prose) :

- `2026-09-05-battle-throne-faceoff.png` -- garde, les deux rigs actifs
  face à face, pilier intact visible entre eux.
- `2026-09-05-battle-throne-pillar-intact.png` / `-pillar-broken.png` --
  le pilier avant/après l'impact du coup de pied (bascule Part↔débris).
- `2026-09-05-battle-throne-finisher-impact.png` -- le coup de grâce,
  VFX + les deux rigs correctement cadrés (voir piège ci-dessus).
- `2026-09-05-battle-throne-victory-flex.png` -- Hero, vainqueur, pose de
  victoire avant le demi-tour et la marche.
- `2026-09-05-battle-throne-coronation.png` -- raccord complet jusqu'au
  couronnement sur le trône (silhouette sombre, même esthétique que
  `r6_throne_crown`).
- `2026-09-05-battle-throne-idle-garde-a.png` / `-idle-garde-b.png` --
  même plan de garde, à 1.1 s d'écart : le buste et les jambes des deux
  combattants ont visiblement changé d'inclinaison (voir passe
  ci-dessus) -- pas la même pose figée deux fois.
- `2026-09-05-battle-throne-idle-flex-a.png` / `-idle-flex-b.png` -- le
  flex de victoire à deux instants distincts du hold, même vérification.

Lecteur complet (39,3 s, scrub/lecture/vitesse) :
`experiments/r6_battle_throne/output/battle_throne_viewer_final.html`,
publié : https://claude.ai/code/artifact/3137aca1-dd0f-40aa-b7dc-627634d1cf71
