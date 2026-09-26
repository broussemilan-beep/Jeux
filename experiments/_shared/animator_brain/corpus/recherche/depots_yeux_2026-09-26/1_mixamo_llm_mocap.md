# Dépôt 1 : mixamo-llm-mocap (étude pour les YEUX du cerveau d'animation)

Date : 2026-09-26. Méthode : dépôt cloné en lecture, code lu (pas seulement
le README), deux briques portées sur NOS données R6 et lancées pour de vrai.
Aucun fichier de `/home/user/Jeux` n'a été modifié.

## 0. En une phrase

Le cœur annoncé, « vidéo → mouvement », est **inutilisable chez nous** :
GVHMR exige CUDA (appels `.cuda()` en dur), 5 Go de poids, un modèle SMPL-X
derrière une inscription, une caméra fixe et un humain en T-pose au début et
à la fin. En revanche, **la moitié « comparaison » est en numpy pur, elle est
excellente et se porte en R6 en ~150 lignes** : une grille de mesures « ce
que l'œil lit », des écarts regroupés en fenêtres d'images, une vidéo côte à
côte synchronisée, et surtout un fichier de pièges (`docs/PITFALLS.md`) dont
l'un m'a eu dès mon premier essai sur nos données (§4.3).

## 1. Le bon dépôt

- **Retenu : https://github.com/squall01337/mixamo-llm-mocap** (licence MIT,
  « Copyright (c) 2026 squall01337 / mixamo-llm-mocap contributors » ; 242
  étoiles selon la recherche web). Cloné dans `/home/user/ext/mixamo-llm-mocap`.
- `FrancosCorporation/mixamo-llm-mocap` : **même commit exact**
  (`00dfd53…`) : c'est un miroir, rien de plus. Clone supprimé.
- `prim-sheetpiling81/mixamo-llm-mocap` : clone refusé (dépôt inaccessible).
  Le nom aléatoire et la description réécrite ressemblent aux copies qui
  servent à diffuser des logiciels malveillants : **à ne jamais utiliser**.
- Historique : 20 commits sur 2 jours (17-18 août 2026), 19 par « Sacha »
  et 1 par squall01337. Dernier commit : 2026-08-18 (« README: add the
  two-fighter duel showcase GIF »). Aucun test. Les vidéos sources
  (`plates/`), les clips produits (`clips/`) et les mesures du rig sont
  exclus par `.gitignore` : **les démos ne se reproduisent pas** à partir du
  dépôt, même avec un GPU.
- Le dépôt a visiblement été développé ailleurs puis publié d'un bloc. Son
  PITFALLS dit : « paid for in real passes across three model generations »
  (développé avec des agents IA successifs).

## 2. Ce qui est RÉELLEMENT implémenté (lu dans le code)

Chaîne : `pipeline/` (≈ 3 900 lignes Python) + `docs/` + `action_specs/*.json`.

| étape | fichier | ce que fait le code | dépendances |
|---|---|---|---|
| 1 estimation | `estimate_pose_gvhmr.py` (518 l.) | GVHMR (YOLOv8x + ViTPose-H + HMR2 + SMPL-X) → 33 points façon MediaPipe, `pelvis_height`, `gaze` (vecteur nez − milieu des oreilles, lu sur des sommets du maillage, l. 83-90, 460-462), `incam` (repère caméra) | **torch + CUDA en dur** : `model.eval().cuda()` l. 275, `make_smplx(...).cuda()` l. 292-293 ; poids ~5 Go ; SMPL-X sous licence (l. 104-113) |
| 2 battements | `analyze_landmarks.py` (97 l.) | tableau tous les N images + événements à seuils fixes : deux pieds > 0,25 m = vol (l. 307), jambe levée > 0,30 m (l. 312), poing vers la caméra z < −0,32 (l. 318), T-pose envergure > 1,22 m (l. 321), lacet de la ligne d'épaules | numpy |
| 3 spec | `action_specs/*.json` | le mouvement en DONNÉES : calendrier d'appui (`plant`), fenêtres de correction en rampe (`arm_pose`, `reach`, `arm_follow`, `leg_pose`, `root_offset`), lissage par fenêtre | — |
| 4 retarget | `lift_to_mixamo.py` (928 l.) | garde les DIRECTIONS des segments, reconstruit avec les longueurs d'os Mixamo ; épingle la cheville d'appui ; Savitzky-Golay | scipy |
| 5 application | `apply_mixamo_fk.py` (711 l.) + `run_in_blender.py` + `blender_exec.py` | pose FK dans Blender, recherche de la hauteur de hanche pour poser le pied | **Blender GUI vivant + extension MCP sur un socket** `localhost:9876` (`blender_exec.py` l. 25-33) |
| 6 QA | `qa_clip.py` (166 l.) | bornes, saut de hanche < 0,12 m/image, dérive, glissement du pied d'appui, retour au repos, saut d'image par os < 0,30 m, **tête verrouillée au buste** (écart-type < 2°, l. 142-158) | numpy |
| 7 comparaison | `compare_reference.py` (231 l.) | **la grille** : hauteur de main vs visage, écart entre mains, distance main-poitrine, main devant/derrière la poitrine, bras dans le torse, lacet/élévation du regard ; fenêtres contiguës hors tolérance (l. 40-49, 115-162, 188-227) | numpy |
| 8 paire | `compare_pair.py` (404 l.) | deux persos : écart hanche-hanche, **portée** (extrémité qui frappe → corps de l'autre), **intrusion segment-segment** (l. 100-115), écarts « déclarés » (l. 325-341) | numpy |
| 9 contact | `run_in_blender.py contact` | recouvrement BVH des maillages skinés, image par image | Blender |
| 10 vidéo | `render_preview.py` (270 l.) | aperçu Workbench, caméra FIXE pour un solo (l. 176-183), **côte à côte source/retarget synchronisé et étiqueté** (l. 212-245) | Blender, OpenCV |

Ce que le README promet et que le code tient : la comparaison image par
image existe vraiment, elle est lisible, et elle distingue les écarts de
proportion des écarts de pose (`compare_reference.py` l. 95-113, 174-176).

Ce que le README survend :
- « Operable end-to-end by an AI agent » : oui pour les appels en ligne de
  commande, mais l'étape 5 exige un **Blender ouvert avec l'extension MCP**,
  la spec est écrite à la main à partir des chiffres, et leur propre doc
  répète que « the human eye is the last word » (PIPELINE §7, §10 ;
  PITFALLS #25). Ce n'est pas un critique autonome : c'est un outil de
  mesure au service d'une relecture humaine. C'est exactement la posture que
  Milan veut, mais ce n'est pas « de bout en bout ».
- « A QA gate, not vibes » : `qa_clip.py` imprime `HARD FAILURES` (l. 162).
  C'est une porte bloquante, donc à inverser chez nous.
- « Any video » : non. Le contrat de la vidéo source (PIPELINE §0,
  PROMPTING.md) impose caméra fixe, corps entier, T-pose ~1 s au début ET à
  la fin, pas d'occlusion. C'est **l'opposé de nos refs** (TSB, anime :
  coupes, caméra qui bouge, VFX qui masquent, dessins, blocs R6).

## 3. Contraintes chez nous (vérifiées)

- `pip` passe par un proxy qui répond 403 sur PyPI (`curl https://pypi.org/simple/scipy/`
  → 403) : ni `scipy` ni `mediapipe` installables aujourd'hui. `numpy`
  1.26.4 et `cv2` 4.9.0 sont présents.
- Pas de GPU, pas de torch. Même en forçant GVHMR sur CPU (en réécrivant
  leurs `.cuda()`), il faudrait ViTPose-H + HMR2 (ViT-H) sur 4 cœurs, soit
  de l'ordre d'une à deux secondes par image et par modèle (estimation, pas
  mesurée), plus l'inscription SMPL-X faite par un humain. **Non testé**,
  pour ces raisons.
- GVHMR est entraîné sur des humains. Sur des blocs R6 sans coudes ni
  genoux, ou sur un dessin anime : **inconnu, non vérifié**. Notre
  `clip_analyzer.py` affirme que « les estimateurs de squelette ne marchent
  ni sur les dessins ni sur les blocs R6 », mais je n'ai pas trouvé de
  mesure qui le prouve. C'est une affirmation, pas un résultat.

## 4. Tests réels sur nos données (CPU, < 5 s chacun)

Fichiers (scratchpad, hors dépôt) :
`/tmp/claude-0/-home-user-Jeux/4796ac9e-8e41-51f7-91c4-7b92a6a187d0/scratchpad/c4/depots/mixamo_test/`
(`r6_compare.py`, `r6_pair.py`, `sortie.txt`, `metriques_150_300.json`,
`v5_v6_cote_a_cote_2.5-6s.mp4`, `v5_v6_planche.png` ; exports v1/v2/v5/v6
d'« Un seul coup » tirés de l'historique git).

Les versions v2, v5 et v6 ont la même ligne de temps (départ 156, charge 186,
contact 283 ; 751 images à 60 i/s). La comparaison image par image
(leur hypothèse implicite) est donc valide ici. Elle ne le serait pas contre
une ref (voir §6).

### 4.1 La grille de `compare_reference.py`, portée en R6 (v6 contre v5, v6 contre v2)

Portage : « main » = bout du bras (`geo_pose.bout`), épaule = haut du bras,
tête = centre du bloc tête (sur R6 le centre de la tête EST le visage, donc
le piège « nez contre base du crâne » n'existe pas), « dans le torse » =
pénétration d'un point de l'axe du bras dans la BOÎTE 2×2×1 du torse,
échantillonnée le long du segment. Tolérances : les leurs, converties
(× 2 studs / 0,6 m).

Ce qui sort (extrait de `sortie.txt`) :

```
v6 comparé à v5
  f205-258  mains plus hautes que la réf (vs tête): moy +1.10, pire +1.25 @ f248
  f192-266  écart entre les mains: moy -2.11, pire -2.71 @ f231
  f193-278  main G : devant(+)/derrière(-) la poitrine: moy +2.23, pire +2.71 @ f255
  f258-273  main D : devant(+)/derrière(-) la poitrine: moy -0.46, pire -0.58 @ f267
  f277-640  tête vs buste (lacet): moy -25.70, pire -33.10 @ f280
Au contact f283 : v2 = v5 à l'identique (hD -0.90 hG -2.00 sep 5.38) ; v6 : hD -0.89 hG -2.14 sep 5.00
Tenue f232 : v5 poings écartés (sep 5.13, main G derrière la poitrine -0.77) ;
             v6 poings devant la poitrine (sep 2.43, bD +1.86 bG +1.79), tête tournée -83° par rapport au buste
```

Lecture honnête :
- La grille **décrit en mots de corps ce qui a changé** entre deux versions,
  avec la fenêtre d'images, sans regarder une seule planche : « de 192 à
  266, les mains sont 2,1 studs plus proches ; la main gauche passe 2,2 studs
  plus en avant de la poitrine ; la tête est tournée de 26° de moins par
  rapport au buste après le contact ». C'est juste (conforme à la fiche §11 :
  « les deux poings devant la poitrine, buste tourné »).
- Elle a trouvé un fait que je n'avais pas en tête : **la pose au contact
  est strictement identique de v2 à v5**. Seule la charge a changé pendant
  quatre versions.
- **Le piège est ici.** v5 → v6, ce sont des écarts de 1 à 2,7 studs, énormes,
  et Milan a répondu « c trjs pas bon ». Un gros écart mesuré n'est pas un
  progrès. Utiliser ce diff comme preuve d'amélioration **nourrirait
  directement la faiblesse 4** (surestimation). Il répond à « qu'est-ce qui
  a changé ? », jamais à « est-ce mieux ? ».

### 4.2 La QA de `qa_clip.py`, portée (en mesures)

- Saut max par image : 4,7-4,8 studs/image à f171 (≈ 280 studs/s), sur
  les bras, les jambes et la tête. Leur seuil (0,30 m/image ≈ 1 stud) le
  classerait « WARN, teleporting limb ». Or c'est **voulu** : le départ en 3
  images, sol cassé (v2, validé par Milan). Pour de l'anime, le seuil est à
  inverser : c'est un fait à afficher, avec l'intention à côté.
- Tête contre buste : écart-type 31-39° dans les trois versions, donc pas
  de tête collée au buste. Leur contrôle « tête verrouillée » (σ < 2°) est
  une bonne mesure bon marché pour des M1 de jeu, où c'est un défaut
  fréquent.
- Bras dans le torse : jamais (> 0,02 stud) dans v2, v5, v6.

### 4.3 Le piège n°29 de leur PITFALLS, reproduit sur mon premier essai

Mon portage de `analyze_landmarks` (vol = deux pieds au-dessus du sol) a
annoncé « **deux pieds en l'air : f269** » dans la v6. Faux. J'avais mesuré
le centre de la face inférieure du bloc jambe ; sur une jambe R6 inclinée,
c'est le COIN qui touche. Avec le coin le plus bas, à f268-270 la jambe
gauche se lève de 0,12 stud au plus et la droite reste au sol (−0,003).
C'est mot pour mot leur piège #29, « Matched proxies, or the comparison is
fiction » : nommer le point anatomique des deux côtés avant de croire un
nombre. Sur un rig de blocs rigides, ce piège se cache dans chaque « bout »
de membre.

### 4.4 `compare_pair.py` porté : où le poing arrive SUR la victime

Victime placée comme dans `verify_export.py` (rotation diag(−1,1,−1),
position (0,3,−16)). Poing droit dans le repère du torse de la victime
(y = +1 : ses épaules) :

```
v1 f283 : y -0.32 (sous le milieu du torse)  pente du bras  -6°
v2 f283 : y +0.35                             pente du bras  -5°
v5 f283 : y +0.35                             pente du bras  -5°
v6 f283 : y +0.30                             pente du bras -10°
f285 (après contact) : le bras pénètre la boîte de 0,04-0,06 stud (v2-v6)
```

C'est la mesure qui manquait à « Il frappe vers le bas » (6 retours de
Milan) : **où** le poing touche le corps de la victime, et **avec quelle
pente**. La v1 touchait sous le milieu du torse ; depuis la v2 le poing
arrive en haut de la poitrine ; la v6 descend un peu plus (−10° au lieu de
−5°). Aucun verdict : un chiffre à suivre version après version. La
pénétration de 0,06 à f285 est un contact voulu (leur piège #38 : « Fist-into-glove
is not a bug »), à marquer comme tel.

### 4.5 Le « showcase » côte à côte synchronisé (`render_preview.py --showcase`)

Refait avec ffmpeg seul, en 1,4 s : v5 | v6 de 2,5 à 6 s, même instant,
numéro d'image incrusté (`v5_v6_cote_a_cote_2.5-6s.mp4`, planche
`v5_v6_planche.png`). À vitesse réelle, on voit les deux versions au même
battement. La planche montre aussitôt le défaut de cette forme chez nous :
**la caméra a changé en même temps que l'anim** (v6 recadrée). On ne sait
plus si l'œil réagit à la pose ou au plan. Eux rendent le solo avec une
caméra FIXE (l. 176-183) justement pour isoler l'animation. Chez nous il
faut les deux (§5, brique B).

## 5. Les briques utiles POUR NOUS

Intérêt noté sur 10.

**A. La grille « ce que l'œil lit » + fenêtres d'écart** (`compare_reference.py`).
Faiblesses 3 et 2 (en partie). Portée et testée (§4.1) :
main vs tête, écart des mains, distance à la poitrine, **devant/derrière la
poitrine dans le repère du torse** (la faiblesse 2, mesurée sans ambiguïté
sur NOS données 3D), bras dans la boîte du torse, tête vs buste. Écarts
regroupés en fenêtres ≥ 7 images à 60 i/s. Forme : `outils/ecarts.py`
(nom à choisir), qui réutilise `geo_pose` / `vues.lire_kfseq`, accepte deux
.rbxmx ou un .rbxmx + une anim TSB/pack (.rbxm), et imprime des fenêtres, sans
verdict. Coût : ~150 lignes numpy, une demi-journée avec les tests.
Intérêt 8.

**B. Côte à côte synchronisé, en deux modes** (`render_preview.py --showcase`).
Faiblesses 1, 3 et 5. Version N−1 | version N (ou ref | nous, en local
seulement) à vitesse réelle, même instant, numéro d'image incrusté.
Adaptation : **mode caméra fixe** (l'anim seule, cadrage du jeu, pour un M1
vu par le joueur) et **mode caméra réelle** (le plan de la cinématique). Ce
qui change entre les deux modes révèle ce qui vient du plan et non de la
pose. C'est aussi ce que Milan demande (« je vois aucun changement » ×4 :
juger « à vitesse réelle, au cadrage réel, à côté de la version d'avant »).
Coût : ffmpeg `hstack` + `drawtext`, testé, < 1 h pour l'outil. Les vidéos
de refs restent dans le scratchpad ; seules nos versions vont dans
`captures/verification/`. Intérêt 8.

**C. La portée sur la victime** (`compare_pair.py`, portée, extrémité → corps
de l'autre, intrusion SEGMENT et non extrémité). Faiblesses 3 et 4.
Testée (§4.4) : point d'impact dans le repère du torse de la victime +
pente du bras + pénétration. À brancher dans `verify_export.py` comme
MESURE affichée à chaque livraison (pas un contrôle bloquant), et à
comparer aux mêmes chiffres mesurés sur les anims TSB à deux rigs
(`WallComboPlayer` / `WallComboVictim`). Coût : ~60 lignes, déjà écrites
en brouillon. Intérêt 8.

**D. L'écart DÉCLARÉ** (`root_offset` déclaré → `[declared root_offset]`,
`compare_pair.py` l. 325-341 ; PIPELINE §9.6 : « declare it … so the cost
stays visible »). Faiblesse 5. C'est la forme exacte de la pose TRICHÉE
pour un plan : on déclare dans la spec « de f270 à f290, poing avancé de
0,4 stud pour la caméra 3 », et chaque mesure continue d'afficher l'écart,
avec l'étiquette « déclaré (tricherie de plan) » au lieu de « défaut ». Ni
règle, ni oubli : le coût reste visible. Pour un M1 (caméra du joueur),
aucune tricherie n'est déclarable, et la même mesure le montre aussitôt.
Coût : un champ `triches: [{f0, f1, plan, quoi}]` dans le JSON de
production + une étiquette dans les sorties. Intérêt 7.

**E. Le fichier de pièges numérotés, chacun payé et chiffré** (`docs/PITFALLS.md`).
Faiblesses 2 et 4. Nos `ANGLES_MORTS.md` et `CARNET.md` s'en rapprochent,
mais leur format est plus dur : chaque piège = l'incident, le chiffre
mesuré, la cause, la parade. Trois à reprendre tels quels :
#29 (même point des deux côtés, reproduit ici §4.3) ; #5 (« Never decide a
limb from a still. Facing the camera, viewer-left = character-RIGHT ») pour
la faiblesse 2 ; #25 et §10 (« When your eye and your numbers disagree … it
is usually the numbers »). Coût : écriture seulement. Intérêt 7.

**F. La boucle de relecture en 4 temps** (PIPELINE §10) : côte à côte au même
battement, puis nommer le défaut en UNE phrase en mots de corps (« son poing
arrive sous la poitrine »), puis la changer en mesure, et seulement alors
modifier. Faiblesse 4 : écrire la phrase AVANT de chiffrer la prédiction,
et la confronter ensuite aux mots de Milan (moisson), donne une trace
comparable, pas une note au ressenti. Coût : protocole dans `revue.py` /
`rapport_regard.py`. Intérêt 6.

**G. Tête verrouillée au buste** (`qa_clip.py` l. 142-158 : écart-type du
lacet tête-buste < 2°). Faiblesse 3 (anims de jeu surtout). Une ligne de
mesure, déjà dans le portage. Intérêt 5.

**H. Les battements lus dans les nombres, avant la spec**
(`analyze_landmarks.py`, « Beat sheet before any spec »). Faiblesses 1 et 2.
Sur nos anims 3D c'est facile (racine rapide, bras tendu, hanche basse,
§4.2), mais notre `coup_clip.py` a déjà ses marqueurs. Sur les refs vidéo,
il faudrait un estimateur 3D qu'on n'a pas. Utile surtout pour les .rbxm
TSB/pack (repérer charge, départ, contact sans les regarder). Intérêt 4.

**I. Le « découpler proportion et pose »** (`compare_reference.py`
l. 95-113). Faiblesse 3. Chez eux, la tête Mixamo ne se place pas comme
celle de l'acteur. Chez nous, le perso R6 comparé à une ref humaine/anime
n'a PAS les mêmes proportions (tête d'1 stud sur un torse de 2) : toute
comparaison ref anime → R6 doit afficher à part la part de proportion
(« la main paraît haute parce que la tête R6 est grosse »). Intérêt 5,
utile seulement le jour où une ref humaine est mesurée.

## 6. Ce qu'il faut INVERSER ou IGNORER

- **Inverser la porte QA** : `qa_clip.py` imprime `HARD FAILURES — fix
  before showing` (l. 162). Chez nous : mesures + intention déclarée, jamais
  de verdict de style. Le départ en 3 images (f171, 280 studs/s) serait un
  « défaut » chez eux ; c'est le coup de Milan (§4.2).
- **Inverser « la réf a raison »** : eux copient une performance (la fidélité
  EST le but ; `compare_reference` mesure l'écart à la vidéo). Nous
  n'imitons pas une vidéo : nous poussons, trichons, exagérons (anime).
  Un écart à la ref n'est pas une erreur. C'est une donnée à lire avec
  l'intention (brique D).
- **Ignorer la comparaison image par image contre une ref** : leur
  alignement est `src → dest` par simple rapport de cadences
  (`compare_reference.py` l. 167-169). Contre une ref de timing différent
  (TSB 10 s, notre scène 12,5 s), il faut aligner par ÉVÉNEMENTS (départ,
  contact, fin de tenue), puis étirer entre eux. Sinon on compare des
  instants qui ne se correspondent pas.
- **Ignorer l'estimation (GVHMR), le retarget Mixamo, le FK apply, le socket
  MCP, les specs de retarget (`reach`, `arm_follow`…), la PROMPTING de
  vidéos générées** : tout cela sert un squelette humain à coudes et genoux
  et une vidéo propre en T-pose. R6 = 6 blocs rigides, notre export
  KeyframeSequence existe déjà.
- **Ignorer le BVH maillage-maillage** (`run_in_blender.py contact`) : sur
  R6, les pièces SONT des boîtes. La boîte exacte (déjà dans
  `verify_export.py` et mon portage) est la vérité terrain ; leur leçon #33
  (« capsules optimistes ») ne s'applique pas.

## 7. Les pièges pour nous

- **Faux sentiment d'objectivité, niveau 1** : « mes mesures disent que la v6
  a beaucoup changé » (§4.1 : jusqu'à 2,7 studs) → prédiction plus haute. Or
  Milan : « c trjs pas bon ». Un diff mesure le CHANGEMENT, pas la qualité.
  C'est exactement la faiblesse 4. À écrire en tête de l'outil.
- **Niveau 2, proxies** : un nombre sur un point mal choisi ment avec
  aplomb. Mon « vol à f269 » (§4.3) aurait pu finir dans un rapport. Sur R6,
  toujours nommer le point : coin le plus bas, centre de face, bout du bloc.
- **Niveau 3, seuils** : leurs tolérances (0,06 m…) sont en mètres humains,
  calibrées sur UN acteur. Convertir ne les rend pas justes pour R6 ; ce
  sont des largeurs d'affichage, pas des normes.
- **Dépendance lourde** : installer GVHMR (torch, pytorch3d, 5 Go,
  inscription SMPL-X, CUDA) pour un gain non démontré sur R6 et sur l'anime.
  Et PyPI est aujourd'hui fermé (403) dans ce conteneur.
- **Faiblesse 2 déplacée, pas réglée** : même avec un GPU, un estimateur
  monoculaire perd le membre caché derrière le torse (leur piège #7 : « An
  arm behind the torso in 3/4 view came back as garbage ») et la profondeur
  est « the ill-conditioned axis of a single-camera fit » (#28). La
  profondeur des refs reste ambiguë ; l'outil ne fait que la cacher sous un
  chiffre. Notre voie reste le rendu-comparaison (`geo_pose`), à compléter
  d'une chose que ce dépôt enseigne en creux : **quand deux hypothèses de
  profondeur (bras devant / derrière) collent aussi bien à l'image, le
  dire** (« ambigu ») au lieu d'en choisir une.
- **Copie malveillante** : `prim-sheetpiling81/mixamo-llm-mocap`, à éviter.

## 8. Recommandation

1. Écrire `outils/ecarts.py` (A + G) et la mesure de portée (C) à partir des
   brouillons `r6_compare.py` / `r6_pair.py`, avec un auto-test sur v2/v5/v6
   (fait connu : contact identique v2 = v5). Afficher, ne pas juger.
2. Ajouter le côte à côte en deux modes, caméra fixe et caméra réelle (B), aux
   livraisons : version d'avant | version nouvelle, à vitesse réelle.
3. Ajouter le champ `triches` (D) aux productions cinématiques.
4. Verser les pièges #5, #25, #29, #38 (reformulés pour R6) dans `CARNET.md`
   comme APPRENTISSAGES, avec l'exemple f269.
5. Ne pas installer GVHMR. Réévaluer seulement si un GPU arrive ET qu'un
   essai montre qu'il lit des persos R6 filmés.

## Sources

- [squall01337/mixamo-llm-mocap](https://github.com/squall01337/mixamo-llm-mocap) (dépôt étudié)
- [FrancosCorporation/mixamo-llm-mocap](https://github.com/FrancosCorporation/mixamo-llm-mocap) (miroir, même commit)
- [prim-sheetpiling81/mixamo-llm-mocap](https://github.com/prim-sheetpiling81/mixamo-llm-mocap) (inaccessible, suspect)
- [GVHMR](https://github.com/zju3dv/GVHMR) (estimateur requis, non installé)
