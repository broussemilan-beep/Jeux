# Dépôt 5 : Pose2Sim_Blender (davidpagnon), étude pour les YEUX du cerveau

Date : 2026-09-26. Clone en lecture seule : `/home/user/ext/Pose2Sim_Blender`
(`git clone --depth 1`, rien modifié). Tests et images :
`scratchpad/c4/depots/p2sb_test/` (prep.py, bpy_test.py, repere.py,
superpose.py, iou.py, vide.py, superposition.png, iou_fa120.png). Aucune
écriture dans `/home/user/Jeux`.

## 1. Le bon dépôt

- **https://github.com/davidpagnon/Pose2Sim_Blender** : un seul candidat
  sérieux. Le nom vient de Milan, et le README cite l'organisation
  perfanalytics (Pose2Sim). Les autres dépôts proches (perfanalytics/pose2sim,
  Sports2D) sont les pipelines d'estimation de pose ; ce dépôt-ci est la
  partie « voir dans Blender ». Il a été vérifié par `git ls-remote` avant
  le clonage.
- Licence : **MIT** (`LICENSE` : « Copyright (c) 2021 Jonathan Camargo
  Leyva », l'ancien BlendOsim ; les en-têtes de code créditent David Pagnon).
  On peut reprendre des idées ou du code en citant la source.
- Dernier commit : `80ded0f`, **2026-09-26 00:19 +0200**, « Replaced driver
  namespace variables with image custom properties… ». Le dépôt est actif ;
  `bl_info` vise Blender **5.1.0** (`__init__.py:97`), et nous avons la 5.0.1.

## 2. Ce qui est RÉELLEMENT implémenté (code lu, pas le README)

Le code tient en environ 3 400 lignes Python. Tout le reste, ce sont des
maillages OpenSim (`Pose2Sim_Blender/Geometry/*.stl|vtp`) et des exemples.

| Brique | Où | Ce que fait le code |
|---|---|---|
| Import de caméras | `cameras.py:256-310` (lecture TOML), `435-522` (création) | TOML Pose2Sim/OpenCV : `matrix` K, `rotation` en Rodrigues, `translation`, `size`. Les caméras MOBILES sont gérées (`moving` = intr/extr par image, `279-302`, puis clés `lens`/`location`/`rotation_euler`, `474`, `495-496`). Le champ de vision vaut `max(fov_x, fov_y)` (`472`, `482`). Le point principal passe en `shift_x/y` (`513-514`). **Les distorsions sont ignorées** (`cameras.py:10`, `325`). |
| Export de caméras | `cameras.py:313-432`, `543-556` | Caméras de la scène vers TOML, y compris les caméras animées (lues clé par clé dans les fcurves). |
| « Show » : vidéo dans le repère caméra | `cameras.py:559-671` | La vidéo devient un *empty image* parenté à la caméra. Des drivers (`610-652`) mettent l'échelle et le décalage à l'échelle de sa profondeur Z, si bien que l'image remplit toujours le cône de vue quand on la glisse en avant ou en arrière. `frame_offset` sert à la synchro temporelle, réglée à la main (`579`). |
| « See through camera » | `cameras.py:730-751` | Passe la vue 3D en vue caméra, met l'image en fond (`empty_image_depth='BACK'`) et masque les courbes. |
| « Film » | `cameras.py:674-727` | Rendu viewport OpenGL (`bpy.ops.render.opengl`) par caméra. Il faut une zone `VIEW_3D` (`691`). En secours, c'est un rendu Cycles avec `device='GPU'` forcé (`701-702`, `727`). |
| « Rays from 3D point » | `cameras.py:761-794` | Une courbe de Bézier va du point 3D au CENTRE de chaque caméra, accrochée au point par un hook. Aucune coordonnée 2D n'est calculée : on voit à l'œil si le rayon passe par le point 2D de l'image. |
| « Ray from image point » | `__init__.py:599-607` | **Non implémenté** (« Coming soon! »). |
| Trajectoire de mouvement | `__init__.py:533-558` | Appelle simplement les *motion paths* natifs de Blender (±N images). |
| Marqueurs .trc | `markers.py:72-96`, `309-369` | Lecture tabulée plus une sphère animée par marqueur, avec passage Y-haut vers Z-haut `(x, -z, y)` (`359-361`). |
| Squelette depuis les marqueurs | `markers.py:124-216` | Os tête-queue entre marqueurs (arbres HALPE_26/COCO dans `skeletons.py`), contrainte IK `chain_count=1` vers le marqueur enfant et COPY_LOCATION à la racine, puis export BVH (`410-426`). La version c3d « DOES NOT WORK » (`markers.py:219-221`). |
| Modèle OpenSim + mouvement | `mocap.py`, `osim_to_bvh.py`, `forces.py` | Maillages d'os, .mot converti en BVH (bvhsdk), flèches de force. **Exige `opensim`** (`mocap.py:31`, `osim_to_bvh.py:32`). |

**Dépendances et maturité (vérifiées) :**
- Au chargement, l'add-on lance `pip install --user` de `six, toml, anytree,
  opensim, bvhsdk` (`__init__.py:46-61`). **`opensim` n'est pas sur PyPI**
  (testé : « No matching distribution found »). Et `__init__.py:66` importe
  `mocap`, qui importe `opensim` au niveau du module. **L'add-on entier ne
  peut donc pas s'activer ici.** Seul `cameras.py` est autonome (bpy, numpy,
  toml).
- Aucun GPU requis pour la géométrie. Le GPU (ou au moins un contexte
  OpenGL/EGL) est requis pour tout ce qui est VISUEL : Show, See through et
  Film sont des outils de viewport interactif.
- Maturité : c'est un outil de visualisation pour chercheurs, bien fait pour
  les caméras, mais avec des bugs visibles :
  - `showImages.single_image` est un BoolProperty dont le `default` est une
    chaîne d'extensions (`__init__.py:157-161`) ;
  - `cameras.py:73` enregistre un opérateur dès l'import ;
  - le secours `load_reference_image` n'existe plus en Blender 5 ;
  - il n'y a aucun test.

## 3. Ce que j'ai TESTÉ (bpy 5.0.1, CPU, sur nos données)

Données : caméra de `experiments/r6_un_seul_coup/output/staging.json`,
interpolée exactement comme `placerCamera` (player_template.html:406-421) ;
positions monde des 6 blocs par `staging.tracks()` (lecture des .rbxmx,
sans écriture) ; images 60, 100 et 120 de
`captures/verification/2026-09-26-un-seul-coup-v6-scene-complete-avec-son.mp4`
(852×480, 30 i/s), soit fa = 120, 200 et 240 à 60 i/s, en dehors de toute
secousse.

1. **`cameras.py` chargé seul** (paquet factice pointant sur le clone) : OK.
   Leur exemple importe 4 caméras.
2. **Notre caméra three.js vers TOML OpenCV vers leur import** :
   - champ de vision horizontal exact : 62,87°, 71,29° et 79,23° ;
   - aller-retour import/export : écart d'environ 1e-6 ;
   - **convention non documentée** : leur import tourne le monde de −90°
     autour de Z, soit `(x,y,z) -> (y,-x,z)` (`cameras.py:488` + `503-504`).
     Une fois nos points passés dans ce repère, la projection par la caméra
     Blender et la projection directe `K[R|T]` concordent à **≤ 0,0004 px**.
   - **Piège rencontré** : sans `bpy.context.view_layer.update()`,
     `matrix_world` reste périmé en mode fond, et l'écart monte de 458 à
     605 527 px. Ça ressemblait à un bug de leur code ; c'était le nôtre.
3. **« Show » sans écran : ÉCHEC.** `empty_image_add` refuse (« poll()
   failed, context is incorrect ») et le secours n'existe plus en Blender 5
   (AttributeError). On contourne par `bpy.data` : la vidéo se charge bien
   (MOVIE, 393 images, 852×480).
4. **« Film » sans écran : dégradé.**
   - Le rendu OpenGL est impossible (« Cannot use OpenGL render in background
     mode »), donc le code passe à Cycles : environ 6 s par image pour une
     scène vide.
   - **Cycles ne rend pas les empty image** : écart-type des pixels de
     0,0011, image uniforme. La superposition vidéo est donc PERDUE hors
     écran.
   - Workbench et EEVEE plantent (libEGL absente).
5. **La brique utile refaite en numpy pur, sur nos vraies images**
   (`superpose.py`, `superposition.png`) : les 6 blocs de l'attaquant et de
   la victime sont projetés avec la caméra du lecteur, en ordre du peintre,
   avec la profondeur écrite à côté.
   - **Calage** : les bords concordent à 1-2 px aux trois instants. IoU de
     silhouette à fa120 = **0,842**, plafonné par mon masque couleur qui ne
     capte pas la peau de la tête (`iou_fa120.png`).
   - Sensibilité : un décalage volontaire de 0,1 stud donne 0,803 ; de
     0,3 stud, 0,716.
   - Le lecteur dessine la tête en cube de 1,25 (player_template.html:168)
     et non avec la boîte de rig 2×1×1. `moon.py:28` fait déjà pareil ; seul
     mon script de test s'était trompé.
   - **Ce que ça montre de neuf** : à fa200 (la charge, cadrage réel), la
     profondeur caméra vaut Right Arm 8,52 < Head 9,27 < **Left Arm 10,10 ≈
     Torso 10,12**. Le bras gauche et le torse sont à 2 cm de profondeur
     l'un de l'autre : pour le spectateur, ce bras est collé au buste, ni
     devant ni derrière. C'est exactement l'information qui manquait pour la
     faiblesse 2, mais calculée sur NOTRE anim au cadrage réel.

Durée totale des tests : environ 10 min de calcul.

## 4. Pour nos yeux : ce qui sert, sous quelle forme, à quel coût

**La leçon centrale.** La promesse lue par Milan, « superposer vidéo,
squelette et caméra pour voir où notre anim diverge de la ref », ne tient
que si la caméra de la REF est connue. Pose2Sim l'obtient par calibration
multi-caméras (damier, plusieurs vues simultanées). Nos refs (clips TSB,
anime, GIF) sont mono-vue, sans calibration, montées, avec des caméras
écrites. **Pose2Sim_Blender n'estime aucune caméra** : il ne fait
qu'afficher celles qu'on lui donne. Pour les refs, le travail difficile
(retrouver la caméra) reste celui que fait déjà `geo_pose.py` par
rendu-comparaison. En revanche, pour NOS anims la caméra est connue
exactement (staging.json). C'est là que l'idée paie, et sans Blender.

### Briques à reprendre (adaptées)

| # | Brique (origine) | Faiblesse | Forme pour un R6 / Roblox | Coût | Intérêt |
|---|---|---|---|---|---|
| B1 | **Voir à travers la caméra réelle** (`see_through` + plan image, `cameras.py:559-751`) | 3, 2 | `outils/cadrage.py` en numpy : caméra du plan (staging.json) + mondes R6 (tracks), blocs projetés sur NOTRE image filmée (ou sur un rendu `moon.render` au même cadrage). Profondeur caméra par bloc et chevauchements écrits à côté. **Déjà prouvé ici** : calage à 1-2 px. | ~½ j | 5/5 |
| B2 | **Format caméra TOML OpenCV** K/R(Rodrigues)/T/size, caméras mobiles par image (`cameras.py:256-310`, `414-432`) | 5, 3 | Un fichier caméra par plan, dans un format standard et échangeable, au lieu de nos tuples `[f, oeil, cible, fov, mode]`. Converti une fois depuis staging.json. Sert aussi à rejouer le plan dans Blender si un jour on a un écran. | ~2 h | 3/5 |
| B3 | **Plusieurs caméras, même anim** (« Film » par caméra, `674-727`) | 5 | Rendre la même KeyframeSequence par (a) la **caméra joueur** (troisième personne derrière l'épaule, FOV Roblox par défaut 70° vertical, distance à mesurer en Studio le moment venu) pour un M1, et (b) la **caméra écrite** pour une cinématique. Un M1 se juge en (a) ; une pose trichée de ciné ne se juge QUE en (b). Aujourd'hui `planche_cles.py` utilise 2 angles fixes canoniques (3/4 face, profil) : ce n'est ni l'un ni l'autre. | ~½ j (numpy, moon.render) | 4/5 |
| B4 | **Profondeur au cadrage** (idée de « Rays from 3D point », inversée) | 2 | On ne trace pas de rayons vers le centre de caméra : on calcule la profondeur de chaque bloc et le recouvrement 2D des silhouettes, et on marque les cas ambigus (écart de profondeur < ~0,1 stud ET recouvrement à l'écran). C'est une OBSERVATION, pas un verdict : « ce bras se lit collé au buste dans ce plan ». Sur les refs, ça ne marche que via la caméra estimée par geo_pose. | ~2 h, dans B1 | 4/5 |
| B5 | **Trajectoires à l'écran** (motion paths, `__init__.py:533-558`) | 1, 3 | Nos arcs (planche_cles) sont en vue monde (profil/dessus). Nouveau : le trajet du poing PROJETÉ dans le plan réel, avec l'espacement en px par image à 30 i/s, c'est-à-dire ce que voit le spectateur (un arc magnifique de profil peut n'être qu'un point dans la caméra du plan). | ~2 h | 4/5 |
| B6 | **Synchro vidéo par décalage** (`frame_offset`, `579`) | 1, 4 | Inverser le principe : ne pas caler au début mais sur un ÉVÉNEMENT (image du contact). Mettre la ref et notre vidéo côte à côte, calées au contact, puis les jouer à vitesse réelle (lecteur HTML, deux `<video>`) plutôt que regarder des planches. | ~2 h | 3/5 |
| B7 | **Squelette depuis des points** (`markers.py:124-216` : IK chain 1 + COPY_LOCATION) | 2 (refs) | Si un jour on a des points 3D d'une ref (clic manuel sur 2-3 images, ou pose estimée), le rig se déduit de points par des contraintes, pas par des clés. Pour un R6 rigide : 6 directions de blocs = 6 vecteurs épaule→poing, hanche→pied, cou→tête. geo_pose fait déjà l'inverse par essais. | faible, mais sans données pour l'instant | 2/5 |

### Ce qu'il faut ignorer

- Tout le côté OpenSim (`mocap.py`, `osim_to_bvh.py`, `forces.py`,
  `Geometry/`) : ce sont des modèles musculo-squelettiques et des forces au
  sol. Hors sujet pour 6 blocs rigides, et `opensim` n'est pas installable
  par pip.
- Les arbres de keypoints HALPE/COCO (`skeletons.py`) : ils supposent
  coudes et genoux, que le R6 n'a pas.
- Installer l'add-on lui-même : il lance pip à l'import, dépend de
  `opensim`, et ses opérateurs visuels exigent un écran et un contexte GPU.
  Dans notre conteneur, seul `cameras.py` tourne, et il ne fait rien qu'on
  ne fasse en 30 lignes de numpy.
- La triangulation multi-vues (l'objet de Pose2Sim) : nous n'avons jamais
  deux vues SIMULTANÉES d'une ref. Deux plans d'un même coup TSB sont deux
  moments différents, et souvent deux poses trichées différentes.

### Pièges

1. **Faux sentiment d'objectivité de la superposition.** Un IoU ou un écart
   en px paraît objectif, mais le 0,842 mesuré ici tenait surtout à mon
   masque couleur. Contre une ref, il dépendrait surtout de la caméra
   ESTIMÉE (focale, distance) : une erreur de caméra se lit comme une erreur
   de pose. À afficher avec la caméra supposée, jamais comme une note.
2. **Coller à la ref n'est pas bien animer.** Une anim peut recouvrir la ref
   image par image et mal se lire (timing, espacement, tenues). La
   superposition mesure la POSE et le cadrage, pas le mouvement à vitesse
   réelle (faiblesse 1). Elle ne remplace pas la lecture côte à côte en
   temps réel.
3. **La pose trichée (faiblesse 5).** En cinématique, une pose « fausse » en
   3D est souvent juste dans la caméra du plan. Juger nos poses de ciné en
   3/4 canonique pousse à « corriger » ce qui était voulu. Juger un M1 dans
   la caméra de ciné pousse à tricher là où le joueur verra la triche. Il
   faut toujours dire QUELLE caméra a servi à une mesure.
4. **Conventions de repère.** Leur import tourne le monde de −90° autour de
   Z, sans le dire ; nous sommes en Y-haut (Roblox) ; three.js a un FOV
   vertical, Blender un FOV sur la plus grande dimension. Trois pièges
   silencieux : un changement de repère se vérifie par un aller-retour
   chiffré (comme ici, ≤ 0,0004 px), jamais à l'œil.
5. **bpy en mode fond.** `matrix_world` reste périmé sans
   `view_layer.update()`. Les empty image ne se rendent pas. OpenGL,
   Workbench et EEVEE sont indisponibles sans EGL. Tout outil de regard
   bâti sur Blender viewport sera muet ici : rester en numpy (`moon.render`)
   pour le regard, et garder Blender pour l'export du rig.
6. **Surestimation (faiblesse 4).** Un outil de plus ne corrige pas le +0,3.
   Il n'aide que si la mesure est écrite AVANT la prédiction chiffrée (« au
   cadrage réel, le bras gauche est à 2 cm du buste ») et relue quand Milan
   note.

## 5. En une phrase

Pose2Sim_Blender n'apporte ni caméra estimée ni modèle utilisable ici, mais
une idée juste et bon marché : **regarder l'anim À TRAVERS la caméra du
plan, avec la profondeur de chaque bloc**. Refaite en numpy sur notre v6,
elle se cale à 1-2 px et dit déjà une chose nouvelle (à la charge, le bras
gauche et le buste sont à 2 cm de profondeur dans le plan réel). À prendre
en B1, B3, B4 et B5 comme mesures affichées, sans verdict ; tout le reste
est à laisser.
