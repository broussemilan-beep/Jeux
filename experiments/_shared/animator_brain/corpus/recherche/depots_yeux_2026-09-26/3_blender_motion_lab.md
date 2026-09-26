# Dépôt 3 : Blender Motion Lab (« l'œil mécanique »)

Étude du 2026-09-26, dans le cadre du chantier 4 (affiner les YEUX du cerveau).
Lecture du code, pas seulement du README. Tests faits sur nos exports d'« Un seul
coup » v4/v5/v6. Rien n'a été modifié dans `/home/user/Jeux` ni dans le dépôt cloné.

## 1. Quel dépôt

- **Retenu : `aribornstein/blender-motion-lab`** (https://github.com/aribornstein/blender-motion-lab).
  C'est le seul qui correspond à la description de Milan : valider et comparer des
  motions (contrat JSON + `compare`), trajectoires, retargeting Blender, et une
  branche « recherche » de reconstruction depuis la vidéo (MediaPipe).
- Écartés (recherche GitHub « motion lab » + blender) : `bjornmose/BioMotionLab2Blender`
  (générateur de cycle de marche, 2019), `lahpm092/atlas-motion-lab` (SAM + MuJoCo,
  hors sujet), `pgf3712/optical-motion-lab` (op-art procédural).
- Clone : `/home/user/ext/blender-motion-lab` (`--depth 1`).
- **Dernier commit** : `3245e4b`, 2026-08-15 21:42 +0300 (Ari Bornstein). Dépôt créé
  le même jour ; 1 étoile ; tout le projet tient en une journée.
- **Licence : AUCUNE.** Pas de fichier LICENSE, et le README ne cite que les licences
  des jeux de données (`docs/dataset-licenses.md`). Par défaut, c'est donc « tous
  droits réservés » : on peut lire le code et reprendre les IDÉES (un algorithme ne
  se protège pas), mais **pas copier son code dans notre dépôt**. Tout ce qui suit
  se réécrit chez nous.
- Maturité : un prototype écrit en une session avec Copilot (`.chat/README.md`,
  `.github/copilot-instructions.md`), propre et testé : 54 tests, **51 passent ici**,
  3 échouent uniquement parce que le chemin de Blender est codé en dur pour macOS
  (`src/motion_lab/blender/process.py:11`, `/Applications/Blender.app/...`).

Un point d'histoire qui nous concerne directement (`docs/session-handoff.md:13-15`) :
le projet est né parce qu'**« un direct arrière procédural, mécaniquement valide,
avait toujours l'air artificiel »**. Leur conclusion (README:4-5) : le chemin
« jeu » vérifié passe par de la **vraie capture (CMU)**, et la reconstruction
depuis la vidéo reste de la recherche optionnelle. C'est notre situation : des
contrôles mécaniques qui passent ne font pas une bonne animation.

## 2. Ce qui est RÉELLEMENT implémenté (code lu)

Tout le cœur est en Python pur, sans dépendance (`pyproject.toml` : `dependencies = []`).
Pas de GPU, pas de modèle lourd, sauf la branche vidéo optionnelle (MediaPipe).

| brique | fichier | ce que fait vraiment le code |
|---|---|---|
| Contrat « motion canonique » | `src/motion_lab/contracts/motion.py:24-105` | JSON versionné : par image, positions 3D de joints nommés + `confidence`, `visibility`, `presence`, `contacts`, `fitResidual`, `observationId` ; par clip : `events`, `source` (provenance), `camera`. Validation stricte (temps strictement croissants, scores dans [0,1]). |
| Comparaison de deux clips | `src/motion_lab/comparison/metrics.py:259-320` | Pour chaque image de la référence, prend l'image la PLUS PROCHE en temps du candidat (l.277), distance euclidienne monde joint par joint (l.290), sort moyenne, RMSE, max, par joint. **Aucun alignement spatial** (ni racine, ni Procrustes), aucune caméra. |
| Alignement temporel | `src/motion_lab/processing/alignment.py:74-336` | « Énergie de mouvement » = vitesse des coudes/poignets/chevilles RELATIVE aux hanches (l.61-98), lissée ±0,12 s ; corrélation croisée par fenêtres de 5 s (pas 4 s) ; droite robuste (médiane des pentes, inliers par MAD, l.181-236) = décalage + facteur d'horloge borné à 0,9-1,1 (l.269-270). Moins de 3 fenêtres -> repli sur un seul décalage global (l.323-336). |
| Rapport qualité | `src/motion_lab/quality/report.py:595-692` | Mesures : régularité du temps, longueurs de segments, vitesse/accélération de la racine, sol, glissement pendant un contact, angle de genou (5-179°), torsion épaules/hanches (≤ 75°), collisions de capsules entre membres (rayons = fraction de la taille). Puis des **gates** vrai/faux (l.620-664) et une liste de **limitations** écrite dans chaque rapport (l.666-686). |
| Stabilisation | `src/motion_lab/processing/stabilize.py` | Lissage pondéré par la confiance, longueurs fixées, contacts inférés, et **réparation de la profondeur quand deux membres se croisent à l'image** (l.199-309, voir §5). Attention : `_constrain_torso_twist` (l.407-478, appelé l.628) **coupe** la torsion à 75° dans les données. |
| Reconstruction racine | `src/motion_lab/processing/reconstruct.py:75-132` | Perspective faible : échelle + translation 2D par moindres carrés pondérés entre joints 3D et points 2D, avec le résidu de reprojection. |
| Suivi vidéo | `src/motion_lab/tracking/mediapipe_pose.py` + `viewer/live_pose_pipeline.js` | MediaPipe Pose Landmarker (humain réel), côté Python (option `tracking`) et dans le navigateur (tasks-vision depuis jsDelivr, `viewer/app.js:9`). |
| Retarget Blender | `blender/retarget_motion.py` | Positions -> rig GLB humain avec coudes/genoux : bases torse/bassin, IK à deux os (l.156), verrouillage des pieds en contact, rapport de résidus, gates (résidu ≤ 5 mm l.461, glissement ≤ 2 cm l.463). |
| Visionneuse | `viewer/app.js` (2 236 l.) + `server.py` | Three.js : vidéo de la caméra + squelette superposé + rig animé, synchronisés, en temps réel ou à la main ; modes « rig + points / points / rig » ; API de débogage déterministe `motionLabDebug.snapshot()` / `setProgress(0.5)` (l.2229-2230). Demande un navigateur et Internet (modules épinglés). |

Leur propre bilan, honnête (`docs/cmu-14-01-quality-baseline.md`) : sur le seul
essai CMU traité, la sortie vidéo stabilisée **échoue encore** au sol (33 mm) et au
glissement (105 mm, 218 « contacts » qui clignotent) ; la vitesse de racine
MediaPipe est inutilisable (0,01 m/s pour un boxeur qui se déplace). Et
`docs/occlusion-handling.md:12` : « aucun post-traitement déterministe ne peut
retrouver la vraie pose cachée depuis une image ».

## 3. Ce que j'ai testé sur nos données (et ce qui en sort vraiment)

Préparation (scripts hors dépôt, `scratchpad/c4/depots/bml/`) :
`r6_vers_canonique.py` convertit nos KeyframeSequences (via `outils/vues.py`
`lire_kfseq`, 60 i/s) en leur contrat : 16 joints par image (tête, cou, bas du
torse = `hips`, centre du torse = `chest`, et pour chaque bras/jambe le haut, le
milieu (fictif, bloc rigide) et le bout). Exports comparés : v4 `8b768e4`,
v5 `f8601ba`, v6 `eb816bf` (= `output/usc_attaquant.rbxmx` actuel, même md5).

### 3.1 Leur rapport qualité sur la v6 : 5 gates « échouent », aucune n'est un vrai défaut

`usc_v6.quality.json` : `allEvaluatedPassed: false`. Vérification une à une
(`analyse.py`) :

| gate en échec | valeur | ce que c'est en vrai |
|---|---|---|
| `segmentLengths` | p95 9 %, max 125 % | **Faux défaut dû au rig.** Seuls les segments bas-du-torse->haut-de-jambe (0,49..1,45 stud) et centre-du-torse->haut-du-bras (1,21..1,85) varient : le pivot R6 est au COIN de l'épaule/de la hanche, pas au bout du bloc, donc le « haut du membre » tourne autour du pivot. Aucun bloc ne change de taille. |
| `jointLimits` | 1 502 violations | **Faux par construction** : il mesure l'angle du genou (5-179°), toujours 180° sur un bloc rigide. |
| `torsoTwist` | 86,9° > 75° | **Artefact.** 42° -> 50° -> 2° -> 87° en 3 images à 4,47-4,50 s. En lisant les parts une à une : le lacet du torse descend en douceur (77, 72, 68, 63°), c'est la jambe gauche qui fait son pas (lacet 9 -> 16 -> 28 -> 46°, penchée 35 -> 61°). « L'axe des hanches » calculé sur les hauts de jambes bascule quand une jambe se lève : sur un R6 il n'y a pas de bassin, la « torsion » est illisible ainsi. |
| rootMotion (pas une gate, mais le chiffre qui saute aux yeux) | 229 studs/s, accélération max 13 774 | Images 171-173 (2,85-2,88 s) : **le départ en 3 images, 3,8 studs par image**, le moment que Milan a VALIDÉ (« départ ultra rapide »). Un critique générique le signale comme une anomalie. |
| `capsuleCollision` | 0,24 stud cuisse/cuisse, 1 image | Capsules dont le rayon est une fraction de la taille humaine ; sur R6, les jambes sont côte à côte à 1 stud d'axe au repos (163 images sous 1 stud). À vérifier sur les vrais blocs, pas avec ces capsules. |
| `floorPenetration` | 3,0 cm (tolérance 2,3 cm) | Le seul qui parle d'un vrai sujet (le sol), mais notre `verify_export.py` le mesure déjà sur les vrais blocs (-0,073 stud, v6). |

Leçon directe pour notre faiblesse (4) et pour le refus des règles gravées : **un
critique pensé pour un squelette humain déclare « échec » sur notre meilleur
moment (le départ) et sur une pose voulue (le buste tourné), et « échec » sur des
choses qui n'existent pas en R6 (genou, longueur de segment).** Brancher tel quel,
il produirait du bruit, et, pire, une impression d'objectivité.

Leur code confirme un autre danger : `stabilize.py:407-478` ne se contente pas de
signaler la torsion > 75°, il la **coupe dans les données**. Une limite anatomique
humaine appliquée à un personnage d'anime, c'est exactement une règle gravée qui
efface le style.

### 3.2 Comparaison v5 -> v6 avec leur `compare`

`cmp_v5_v6.json` : écart moyen 0,39 stud, RMSE 0,59, max 3,71 (poignet gauche).
Ces trois chiffres ne disent rien d'utile à l'œil. En découpant le temps par
fenêtres de 0,5 s (mon ajout, `analyse.py`) :

- 0-3,0 s : identiques (0,00) ;
- 3,0-4,75 s : le poignet gauche change jusqu'à 3,7 studs (la charge refaite) ;
- 5-10,5 s : 1,4 stud constant sur le poignet gauche (la tenue de fin diffère) ;
- 11-12,5 s : **0,43 stud sur TOUS les joints**, c'est-à-dire un simple
  décalage de la racine, pas un changement de pose. Leur métrique (distance
  monde, sans racine commune) le compte comme de l'écart d'animation.

Le vrai apport n'est donc pas leur chiffre global, c'est l'idée de la **carte
d'écarts entre deux versions, dans le temps et par part**.

### 3.3 La même comparaison AU CADRAGE RÉEL (adaptation, ~60 lignes numpy, < 1 s)

`ecran.py` projette chaque joint de v5 et de v6 avec la piste caméra de SA version
(`output/staging.json` de chaque commit ; interpolation linéaire entre clés, ce
qui est une approximation de nos « smooth »), en pixels sur 1280x720, en ne
gardant que les joints dans le cadre. Deux colonnes : ce qu'on VOIT (caméra
propre à chaque version) et l'animation seule (les deux avec la caméra v5).

| temps | vu (caméra de chaque version) | animation seule (caméra v5) |
|---|---|---|
| 3,0-4,5 s (départ, charge) | 300-480 px | 390-890 px (poignet gauche) |
| 4,5-4,75 s (frappe) | 370 px | 290 px |
| 5-8,5 s (conséquence 1) | ~30 px | ~30 px |
| 8,75-10 s | 4-5 px | 6 px |
| 10,25-12,5 s | 5-22 px | 17-26 px |

Lecture : entre v5 et v6, **le changement était largement visible** là où on
l'avait mis (des centaines de pixels) ; ce n'était pas un « je vois aucun
changement ». Le retour « c trjs pas bon » porte sur la qualité, pas sur la
visibilité. Inversement, les ~30 px de 5 à 8,5 s (4 % de la hauteur, dans un plan
large) sont probablement invisibles à vitesse réelle : si on croyait avoir
« corrigé la tenue de fin », l'outil dirait que personne ne le verra.

### 3.4 Alignement temporel (`estimate_alignment`)

v4 -> v5 : décalage 0, corrélation 0,98 ; v5 -> v6 : décalage 0, corrélation
0,93. Juste, mais trivial : nos versions partagent déjà la même horloge. Et
`inlierCount: 0` : un clip de 12,5 s ne donne que 2 fenêtres de 5 s, sous le
minimum de 3 (`alignment.py:187`), donc l'ajustement affine ne tourne pas, on
retombe sur un décalage global. Surtout, l'hypothèse est « la même prise, deux
horloges » (facteur 0,9-1,1) : elle ne sert pas à comparer NOTRE coup à un coup
de ref, qui sont deux performances différentes (voir §4, brique B).

### 3.5 Ce que je n'ai pas pu tester

- **MediaPipe** (branche vidéo) : `pip install mediapipe` est refusé, PyPI répond
  403 à travers le proxy (`recentRelayFailures`, hôte `pypi.org:443`, refus de
  politique réseau). Je n'ai pas contourné. De toute façon, MediaPipe est entraîné
  sur des humains photographiés : sur des blocs R6 ou de l'anime, rien ne garantit
  qu'il détecte quoi que ce soit, et leur propre doc dit que sa profondeur n'est
  pas une mesure (`docs/occlusion-handling.md:7-10`). À tester un jour sur une
  capture TSB si le réseau le permet, sans en attendre de miracle.
- **Retarget Blender** : il vise un rig GLB humain (coudes, genoux, IK à deux os).
  Pour nous c'est le sens inverse : nous avons déjà des rotations de blocs. Rien à
  en tirer, et notre aller-retour moteur couvre déjà « l'export redonne bien la
  pose ».
- **Visionneuse** : navigateur + Internet (modules Three.js épinglés, MediaPipe
  sur CDN). Lue, pas lancée.

## 4. Briques utiles POUR NOUS, adaptées au R6 rigide

Rappel : aucune ne rend de verdict. Elles sortent des mesures et disent quoi
regarder.

**A. Carte d'écarts entre versions, au cadrage réel (faiblesses 3 et 4, et
« je vois aucun changement »).** À partir de `ecran.py` : pour deux exports et
leurs `staging.json`, une bande temporelle (une case par 0,25 s) qui donne, par
part R6 (6 blocs, en prenant les 8 coins de chaque bloc plutôt que des joints
fictifs), le déplacement à l'écran en pixels et en % de la hauteur, avec deux
lignes : « vu » (caméra de chaque version) et « animation seule » (même caméra).
Dit AVANT de montrer où le changement se verra et où il ne se verra pas. Sert
aussi à la prédiction : annoncer « changement visible sur la charge, invisible
sur la fin » est vérifiable. Coût : une demi-journée (lire l'interpolation
caméra exacte de `staging.py` au lieu de mon linéaire ; coins des blocs ;
planche PNG). À brancher dans `rapport_regard.py`, sans seuil bloquant.

**B. Énergie de mouvement relative à la racine, et alignement contre une ref
(faiblesse 1).** Leur « énergie » (vitesse des bouts de membres par rapport aux
hanches, lissée ~0,1 s) est une bonne courbe de RYTHME, indépendante du
déplacement global. Adaptation : (1) chez nous, la calculer sur les coins des
blocs (bouts de bras et de jambes relatifs au torse), pour nos exports ET pour
les KeyframeSequences exactes des pros (TSB 13, pack 19) que `planche_cles.py`
lit déjà ; (2) **inverser** leur alignement affine : entre deux performances
différentes, il faut un alignement élastique (DTW) sur les courbes, et c'est le
CHEMIN d'alignement qui est la mesure (« notre charge dure 1,4 s là où la ref en
met 0,6 ; notre détente prend 16 images là où la ref en prend 5 »). Pour une
vidéo de ref (pas de 3D), la courbe vient du flux optique déjà calculé par
`clip_analyzer.py` / `durees.py` : on compare des formes de courbes, pas des
valeurs absolues. Coût : 1 jour. Limite à écrire dans la sortie : l'énergie
optique d'une vidéo mélange caméra, VFX et personnage.

**C. Le « masque d'ambiguïté » pour devant/derrière (faiblesse 2).** Leur
`_repair_occluded_depth` (`stabilize.py:199-309`) fait trois choses justes : il
ne décide la profondeur que quand deux membres se superposent à l'image ET que
la visibilité est faible ; il **élargit** la zone douteuse de 0,08 s de chaque
côté (les erreurs arrivent quand les membres se croisent et se séparent) ; il
prend la profondeur des images FIABLES qui encadrent l'intervalle (au plus
1,5 s) plutôt que de l'image douteuse. Adaptation pour `geo_pose.py` (qui
reconstruit une ref par rendu-comparaison sur UNE image) :
1. pour chaque bras reconstruit, rendre aussi l'hypothèse miroir (bras de l'autre
   côté du plan du torse, même projection) ; si les deux collent aussi bien à la
   ref, écrire « devant/derrière NON OBSERVABLE sur cette image » au lieu de
   choisir ;
2. trancher avec les images voisines où le bras est hors du torse (continuité,
   ≤ 1,5 s), comme eux ;
3. atout propre au R6 que MediaPipe n'a pas : sur une capture TSB, les blocs ont
   des couleurs plates, donc l'**ordre d'occultation** se voit (quel bloc couvre
   l'autre là où ils se chevauchent). Rendre une carte « identité de part » (une
   couleur par bloc) et comparer, sur la zone de chevauchement, quelle part est
   dessus dans la ref et dans notre rendu. La silhouette seule ne le peut pas.
Coût : 1 jour. C'est la brique la plus utile du dépôt pour nous, et elle
s'adapte mieux au R6 qu'à l'humain.

**D. Le rapport qui écrit ses propres limites (faiblesse 4).** `report.py:666-686`
ajoute à chaque sortie la liste de ce qu'il NE PEUT PAS mesurer (« rayons de
capsule approximés », « profondeur globale indisponible sans focale
calibrée »…). Chez nous : chaque sortie de `rapport_regard.py`, `geo_pose.py`,
`juge.py` finit par « ce que cette mesure ne voit pas » (par ex. « caméra
interpolée linéairement », « énergie optique mêlée aux VFX », « une seule image
de ref »). Contre la surconfiance : on lit la limite au moment où on lit le
chiffre. Coût : une heure par outil.

**E. Séparer « la source » et « la correction d'affichage »
(`docs/stabilization-roadmap.md:18-19` : le calage au sol du navigateur n'est
jamais compté comme une correction de la source).** Pour nous : ce que le lecteur
HTML corrige ou triche (caméra, recalage, images tenues du montage) ne doit
jamais masquer ce que la KeyframeSequence fait dans Roblox. Utile pour la
faiblesse (5) : une anim de JEU se mesure sur l'export seul, vue par une caméra
de joueur (plusieurs angles orbitaux, dont de dos) ; une CINÉMATIQUE se mesure
dans SA caméra écrite, et une pose trichée hors champ n'est pas un défaut. Le
dépôt n'a rien d'autre sur (5) : il ne connaît qu'une caméra observée, jamais
une caméra écrite. Coût : un champ `usage: jeu|cinematique` + `camera` dans nos
mesures, et le choix des vues qui en découle ; une demi-journée.

**F. « Les mesures sont des diagnostics, pas des objectifs »
(`docs/stabilization-roadmap.md:36-37` : reprojection et accélération restent
des diagnostics, jamais des cibles d'ajustement).** C'est la position de Milan
dite par un autre. À recopier telle quelle dans le CARNET (section biais).

## 5. À inverser ou à ignorer

- **Inverser** : leurs gates vrai/faux sur le style (angle de genou, torsion
  ≤ 75°, accélération de racine). Chez nous, seuls restent vrai/faux le sol, le
  contact, l'aller-retour moteur, l'interpolation, le sens Roblox (NOYAU).
  Torsion, accélération, vitesse = des courbes affichées, sans seuil.
- **Inverser** : `_constrain_torso_twist`, qui modifie les données pour qu'elles
  respectent une limite humaine. Chez nous, un outil de regard ne modifie jamais
  la pose.
- **Inverser** : l'alignement affine (même prise, deux horloges) -> DTW (deux
  prises, le chemin est la mesure), brique B.
- **Ignorer** : le retarget Blender (humain, IK coudes/genoux), l'import CMU
  ASF/AMC, le rééchantillonnage (nous produisons déjà à 60 i/s exact), le
  serveur/catalogue CMU, les collisions en capsules (nos blocs sont des boîtes :
  un test boîte-boîte exact est plus simple et plus juste), le glissement de
  pied (déjà dans `audit.py:299`).
- **Ignorer pour l'instant** : MediaPipe (non installable ici, humain réel,
  profondeur non mesurée).

## 6. Pièges

1. **Faux sentiment d'objectivité** : `allEvaluatedPassed: false` sur la v6 alors
   qu'aucun échec n'est un défaut ; symétriquement, un rapport « tout passe »
   n'aurait rien dit de la qualité (leur propre direct « mécaniquement valide »
   avait l'air faux).
2. **Un chiffre global** (0,39 stud d'écart moyen v5/v6) : mélange la racine et
   la pose, le visible et l'invisible, 12,5 s en un nombre. Toujours une carte
   dans le temps, par part, à l'écran.
3. **Métriques d'humain sur un R6** : genou, bassin, longueur de segment,
   torsion épaules/hanches n'ont pas de sens sur 6 blocs à pivots décalés. Toute
   mesure reprise doit être redéfinie sur les blocs (coins, axes, pivots Motor6D).
4. **Signaler le style comme une erreur** : le départ en 3 images et le pas de la
   détente ressortent comme des anomalies. Un critique générique pousse vers le
   mou, à l'opposé de l'anime.
5. **Reconstruction vidéo = solution miracle** : leur meilleure sortie échoue
   encore au sol et aux contacts, et leur doc dit que la profondeur cachée est
   irrécupérable. Pour nous, les données EXACTES des pros (KeyframeSequences TSB
   et pack) valent plus que toute reconstruction ; la vidéo sert au rythme et au
   cadrage.
6. **Dépendance** : aucune pour le cœur (Python pur), mais **pas de licence** :
   on réécrit, on ne copie pas.

## 7. Fichiers de ce test (hors dépôt)

`scratchpad/c4/depots/bml/` : `r6_vers_canonique.py` (conversion),
`usc_v4/v5/v6.motion.json`, `usc_v6.quality.json`, `cmp_v4_v5.json`,
`cmp_v5_v6.json`, `analyse.py` (segments, pics de racine, torsion, alignement,
écart par fenêtre), `ecran.py` (écart v5 -> v6 en pixels au cadrage réel),
`staging_v5.json`, `staging_v6.json` (tirés des commits `f8601ba`, `eb816bf`).
