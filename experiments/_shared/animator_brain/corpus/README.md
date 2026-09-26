# Corpus du cerveau — première source : `battleground_animation_pack_v1.0.1` (2026-09-24)

Étape 1 de `PLAN.md`. Le pack premium fourni par Milan (19 animations R6,
bakées à 60 Hz) est **mesuré**, pas copié. Seules les mesures dérivées sont
versionnées : le `.rbxm` n'a pas de licence de redistribution.

Reconstruire : `python3 build_corpus.py <pack.rbxm>`. Le script écrit :

| fichier | contenu |
|---|---|
| `battleground_animation_pack_v1.0.1.json` | une fiche par animation : timing, audit du cerveau, poids des poses |
| `categories.json` | distributions par catégorie (médiane, min, max, n), consultées par `audit.calibrated_verdict()` |
| `nos_protos.json` | les mêmes mesures sur nos exports `.rbxmx` |
| `battleground_animation_pack_v1.0.1_m1_vs_notre_coup.png` | preuve visuelle |

## Chaîne de lecture (vérifiée)

- **Lecteur `.rbxm`** : `corpus.load_rbxm_sequences`. Les poses sont
  résolues par l'équation du moteur (`roblox_export.solve`) : 19 animations
  et 842 keyframes lus.
- **Bug du lecteur corrigé en route** (commit `4a60460`) : les flottants
  négatifs étaient mal décodés, −1 lu −4.
- **Contrôle de recomposition** (monde → Euler locaux → monde) :
  1,6e-6 d'écart.
- **Cohérence physique** :
  - avant = −Z ;
  - le downslam descend le torse à 1,7 stud, le backdash le monte à
    4,3 studs (saut) ;
  - idle et block idle restent sur place.

## Ce que le corpus a appris au cerveau

### 1. Nos seuils d'audit étaient faux pour le combat de jeu

Le même audit qui donnait 23/23 au trou noir passe **7 à 14 critères sur
21-22** aux animations pro. Ce ne sont pas des défauts : c'est le style.

| critère (fixé à la main, sans calibration) | valeur pro (médiane [min–max]) | échec |
|---|---|---|
| tête en retard de 1 à 4 frames sur le torse | **−0,5** [−4 ; 0,5] : tête synchrone ou **en avance** | 15/15 |
| planarité de la tête ≤ 0,85 | **0,98** [0,69 ; 1] : tête sur un axe dominant | 15/17 |
| membres en retard de 1 à 6 frames | **0** [−5,5 ; 2,25] | 50/64 |
| planarité du torse ≤ 0,85 | **0,96** [0,75 ; 1] | 13/17 |
| pics non synchrones (≤ 35 %) | **58 %** synchrones | 36/64 |

Conséquence : `TARGETS` reste une référence pour la catégorie
« cinématique ». Pour toute catégorie présente dans le corpus, le verdict
passe par `audit.calibrated_verdict(valeurs, catégorie)`, qui compare à la
plage pro.

### 2. Un M1 pro, frame par frame (60 fps)

Sur `M1_1` et `M1_3`, là où la segmentation isole l'armement :

| phase | durée (f60) |
|---|---|
| armement : claque dans la pose d'armement, légère tenue | 10 |
| coup | 9 à 11 |
| tenue de la pose frappée | 18 à 20 |

Clip entier : **0,65 s**.

**`M1_2` et `M1_4` n'ont pas d'armement**, ils partent directement sur le
coup : dans un combo, la préparation est la pose de fin du coup précédent.

**Couches d'animation par le poids des poses** (`Weight = 0` sur 100 % des
keyframes) :

- **les M1, l'uppercut et les 3 réactions** : jambes à poids 0 ; en jeu,
  elles restent menées par la marche ou la course, l'animation de coup ne
  les touche pas ;
- **block idle et block hit** : torse, tête **et** jambes à poids 0, **seuls
  les bras** sont animés (une couche « garde » posée sur le reste) ;
- dashes, downslams, idle, marche, course : corps entier.

Le cerveau doit donc décider **quelles parts une technique possède**. Ce
n'est pas un détail d'export.

Qui mène le coup ? Ça dépend du clip, ce n'est pas une règle :

| clip | ordre des pics |
|---|---|
| `M1_1` | bras → torse (+1 f) → tête (+2 f) |
| `M1_3` | bras d'abord |
| `M1_2` | bras gauche d'abord |
| `M1_4` | la tête d'abord |

Le corpus garde **l'ordre de chaque clip** ; il ne généralise pas une
recette.

### 3. L'écart chiffré entre nos coups et un M1 pro

Toutes les mesures sont faites par le même code.

| mesure | M1 pro (n=4) médiane [min–max] | `r6_directional_punch` | `r6_hit_combo` |
|---|---|---|---|
| amplitude bras droit vs repos | **150°** [120–178] | 99° | 90° |
| amplitude torse | **91°** [76–122] | 54° | 58° |
| amplitude tête | **84°** [65–96] | **25°** | **30°** |
| vitesse max de la main | 68 studs/s [18–83] | 52 | 44 |
| fraction du temps « rapide » | **0,24** [0,14–0,27] | 0,05 | 0,09 |
| durée du clip | 0,65 s | 3,05 s (scène) | 2,85 s (scène) |

Sur `r6_directional_punch`, **24 des 35 mesures** sortent de la plage pro de
la catégorie `frappe_legere`.

- **Le défaut principal est l'amplitude**, surtout celle de la **tête**
  (3 fois moins que le pro) et du torse. [CONTREDIT 2026-09-26 : les degrés de tête du pro sont de la contre-rotation, pour que le regard NE bouge PAS dans le monde ; « amplifier nos têtes » sans cette intention ferait l'inverse du pro, voir corpus/etude_c4/A4_pack_battleground.md §3 point 1 et corpus/etude_c4/A4_pack_battleground.md §4]
- Nos coups « claquent » en une frame (vitesse angulaire max du bras plus
  élevée que le pro), mais sur un arc trop court.
- Nos coups passent 76 % du temps quasi immobiles, puis explosent.
- Le pro bouge en continu pendant 0,4 s, sur de grands arcs, et tient
  ensuite la pose.

L'image `…_m1_vs_notre_coup.png` le montre : chez le pro, toutes les parties
bougent en continu ; chez nous, environ 60 frames quasi plates puis une
salve.

## Limites, dites franchement

- **4 exemples par catégorie au mieux** (frappe_legere). `taxonomy.MIN_EXAMPLES`
  vaut 3, donc réaction, frappe_lourde et déplacement sont justes au seuil.
  `garde_touchee` n'a qu'un exemple et est marquée **fragile**.
  **Une seule source** : ce style n'est pas « le » style Roblox.
- La segmentation en phases est une heuristique :
  - l'uppercut ressort en un seul mouvement de 48 frames ;
  - `M1_2` et `M1_4` n'ont pas de vallée entre armement et coup.
  Les fiches gardent les mouvements bruts pour relecture.
- Nos exports sont des **scènes** : leurs durées et phases ne se comparent pas
  à un clip de jeu. Leurs amplitudes, vitesses et ordres de pics, si.
- Mesuré depuis son `.rbxmx` exporté (30 Hz, mouvement d'ensemble sur le
  RootJoint), le trou noir fait 19/22 à l'audit et non 23/23.

## Suite

- Nourrir le corpus avec d'autres sources : packs, et vidéos pour le timing
  seul.
- Premier **clip de jeu** (étape 3 de `PLAN.md`) : un M1 et la réaction de
  la victime, sur deux rigs V2.22, jugés par `calibrated_verdict` et
  non plus par `TARGETS`.

## Ajout du 2026-09-24 : les membres se décalent chez les pros

Mesure `translation_articulation_max_studs` (translation des Motor6D hors
RootJoint) :

| animations | translation max |
|---|---|
| bras des M1 | 1,2 à 1,7 stud |
| jambes des downslams | 1,6 à 1,8 stud |
| course | bras 0,95, jambes 1,56 |
| réactions | ~0,04 |
| **tête, partout** | **0** |

C'est le faux coude du rig IK V2.22 (`RIG_V222.md`). Règle du cerveau :
**tête toujours attachée** ; membres jugés sur la plage de leur catégorie,
plus sur une règle « rotation pure ».

## Ajout du 2026-09-24 : corpus VFX (deux packs Roblox)

`vfx_corpus.py` lit les deux packs VFX envoyés par Milan : `100_Combat_VFX_Pack.rbxm`
et `The_Creator_VFX.rbxm`. Ces packs étaient restés inexploités.
Sorties : `vfx_100_combat_vfx_pack.json`, `vfx_the_creator.json`. Comme pour
les animations, seules les mesures dérivées sont versionnées.

Le lecteur binaire a dû être corrigé au passage. NumberSequence,
ColorSequence et NumberRange étaient lus en big-endian (jamais appelés
jusque-là). Désormais :

- lecture en little-endian, avec vérification que le buffer est consommé
  exactement ;
- nouveaux décodeurs : Enum, Vector2, Vector3 et les attributs d'instance.

**Ce que font les pros (100 Combat VFX, 104 effets, 2 073 émetteurs) :**

| mesure | médiane [p10–p90] | notre M1 (`M1Technique.luau`) |
|---|---|---|
| émetteurs par effet | 14 [5–44] | 2 émetteurs + 1 Part anneau |
| rôles par effet | 4 [1–6] | 3 (flash, étincelle, onde) |
| durée d'un effet | 1,2 s [0,5–3,0] | ~0,3 s |
| flash : durée de vie | 0,10 s [0,05–0,125] | 0,09–0,11 s ✔ |
| flash : taille max | 11 studs [3,9–33] | ~3 studs |
| étincelle : vitesse | 75 studs/s [22–299], drag 5 | 28–46, drag 9 |
| onde : taille max | 12 studs [5–33], 11 clés de courbe | cylindre 7 studs, tween |
| fumée/poussière | 18 % des émetteurs ; durée de vie 1 s, drag 5,4 | **absente** |

Conventions de déclenchement :

- 98 % des émetteurs sont **désactivés** et joués par `:Emit()`, piloté par
  des attributs (voir la liste ci-dessous) :
  - `EmitCount` : présent sur 97 % des émetteurs ; valeurs fréquentes 1, 2, 5, 3 ;
  - `EmitDelay` : presque toujours 0 ; tout part en même temps, les couches
    se séparent par leur durée de vie ;
  - `EmitDuration` : utilisé pour les jets continus courts ;
  - `TimeScale_Start/End/Duration` : un ralenti de 0,1 s sur les particules
    elles-mêmes, soit l'équivalent VFX du hitstop.
- Orientation : 46 % VelocityPerpendicular (anneaux et ondes à plat), 27 %
  VelocityParallel (étincelles étirées), 26 % FacingCamera.
- 50 % des émetteurs utilisent une planche de sprites animée (flipbook).

Combinaison la plus fréquente pour un impact complet : **étincelle +
flash + forme + fumée + onde**, avec des débris en plus pour les coups lourds.

**The Creator** est un exemple d'**aura de personnage** :

- sur chaque membre : 10 émetteurs continus (feu, étoiles, poussière
  d'étoiles) ;
- sur le HumanoidRootPart : un soleil (PointLight portée 60, ombres).

C'est le modèle des « formes » et transformations.

Réserve : le pack ne dit pas quel effet sert à un M1 ou à un finisher. Ses
médianes mélangent coups légers et lourds. Pour un M1, il faut viser le bas
de la plage (p10 à médiane), pas le p90.

Leçon pour le cerveau : nos impacts sont **5 à 7 fois moins denses** que
ceux d'un pack pro, et **3 fois trop petits**. Il leur manque une couche
(fumée/poussière) et le ralenti de particules. Les textures du pack sont
des assets Roblox (`rbxassetid://…`) utilisables en jeu. On ne peut pas les
télécharger ici (`assetdelivery.roblox.com` est bloqué par le proxy), donc
pas d'aperçu local.
