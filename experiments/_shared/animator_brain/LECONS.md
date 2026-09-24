# Leçons apprises par le cerveau

Chaque leçon vient d'un **retour réel** (Milan, ou une erreur trouvée en
revue). Elle est rattachée à une **mesure** qui la vérifie automatiquement
(`rules.py`) et, quand c'est possible, à une **cible de conception** lue
avant de poser (`rules.design_targets`). Une production doit :

1. lire ce fichier et `RETOURS.md` **avant** de poser ;
2. partir des cibles du corpus pour ses poses (pas de chiffres tapés de tête
   puis jugés après coup) ;
3. passer `rules.py` et publier le rapport avec la production.

Une leçon sans mesure n'est qu'un vœu : si une leçon ne peut pas encore être
mesurée, c'est dit ici.

## 1. Posture droite pendant les coups légers (R6)

- **Retour** : Milan, Poing du Dragon v1 (2026-09-24), « il est accroupi ».
- **Cause** : bassin baissé de 0,45-0,55 stud pendant toute la rafale, pour
  faire « garde de combat ». Une jambe R6 est **un seul bloc** : baisser le
  bassin ne plie pas un genou, ça incline et écarte les jambes. Le perso
  paraît tassé (sa tête passait sous celle de la victime).
- **Ce que disait déjà le corpus**, et que je n'ai pas lu avant de poser :
  - coups légers : affaissement du torse médian 0,06 stud, max 0,14-0,22 ;
  - réactions : 0 ;
  - coups lourds seulement (uppercut, downslam) : jusqu'à 1,26 stud, pour armer.
- **Pourquoi la mesure l'a raté** : `deplacement_torse_studs` mesure la
  variation *pendant* le clip. Accroupi dès la frame 0, on paraissait normal.
  Nouvelle mesure `affaissement_torse_studs`, hauteur absolue sous la position
  debout (`corpus.timing_profile`).
- **Règle** : `rules.check_affaissement`, avec pour seuil le max pro de la
  catégorie (+10 %). Pour s'accroupir, il faut une raison : armer un coup
  lourd, atterrir.

## 2. Une rafale monte en intensité

- **Retour** : Milan, v1 : « problèmes sur l'enchaînement, ça manque d'un
  ressenti de puissance ».
- **Cause** : 6 coups identiques (même posture, même hitstop de 0,05 s, même
  plan de caméra), sans pas ni respiration.
- **Règles** :
  - `check_escalade` sur le hitstop, le recul de la victime et la secousse :
    le dernier tiers doit être au moins 15 % au-dessus du premier, sans baisse ;
  - `check_variete_camera` : un changement d'angle au moins toutes les
    2 frappes (Black Flash : punch-in et coupes).
- **Pas encore mesuré** : la variété des coups (formes différentes) et le jeu
  de pieds (pas réels plutôt que glissés). À faire.

## 3. Le plus gros impact doit être vu

- **Retour** : auto-critique du v1, validée par Milan.
- **Cause** : le poing touchait le sol et on coupait dans la même frame sur
  les planches manga, puis sur l'écran blanc. Le coup le plus fort avait le
  moins de temps d'écran.
- **Référence** : Serious Punch, où le poing descend 24 f (à 30 i/s) dans la
  fumée avant les planches.
- **Règles** :
  - `check_impact_visible` : au moins 6 f (à 60 i/s) entre l'impact final et le
    premier effet plein écran ;
  - `check_plan_lisible` : la plongée tient dans un plan sans coupe d'au moins 20 f.

## 4. Une jambe R6 est une boîte

- **Trouvé en revue**, pas par Milan.
- **Effet** : poser le bout du pied au sol ne suffit pas. Inclinée, la boîte
  passe sous le sol. On vise donc le contact du **coin le plus bas**
  (`box_lowest`, mode de pied `"g"` dans `r6_poing_dragon`).
- **Conséquence** : un « genou au sol » ne se fait pas proprement en R6. On le
  remplace par un appui trois points.
- **Mesuré** : sol ≥ −0,15 stud dans `verify_export`.

## 5. Le ressenti de puissance n'est pas mesurable directement

Le cerveau sait dire qu'un coup est techniquement propre, pas qu'il frappe
fort. Les règles 2 et 3 en sont des approximations (escalade, temps d'écran).
Le verdict final reste la revue de Milan, tracée dans `RETOURS.md`.
