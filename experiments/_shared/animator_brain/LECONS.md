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

## 6. Les épaules ne montent jamais ; on frappe à hauteur de poitrine

- **Retour** : Milan, Poing du Dragon v2 (2026-09-24) : « les bras sont trop
  hauts ». Note 6,7/10.
- **Cause mesurée** :
  - l'IK des bras du rig V2.22 **translate** l'épaule quand la cible de la main
    est hors de portée de rotation ;
  - nos cibles de coup visaient le visage (poing à 4,4 studs du sol) et la garde
    était trop près du corps ;
  - résultat : l'épaule remonte de 0,69 stud en médiane pendant toute la rafale
    (jusqu'à 1,29), garde comprise. Le perso a l'air crispé, les bras en l'air.
- **Ce que font les pros** (nouvelle mesure `decalage_epaule_vertical_studs`,
  corpus reconstruit) :
  - M1 : l'épaule **descend**, médiane −0,59 à −0,92 stud, et ne monte jamais
    au-dessus de +0,04. Baisser l'épaule donne du poids au coup ;
  - au contact : bras entre −20° et 0° sous l'horizontale, poing à 2,5-3,6 studs
    (poitrine), mesure `mecanique_frappe` ;
  - Black Flash (vidéo de Milan) : coups courts dans le corps, à bout portant.
    La victime se plie, donc même un coup « au visage » arrive bas.
- **Règles** :
  - `rules.check_epaules` : décalage max ≤ max pro + 0,05, médiane ≤ médiane
    pro max + 0,05 ;
  - `rules.check_bras_au_contact` : élévation ≤ 5° au-dessus du max pro, poing
    ≤ 3,69 studs.
- **À la conception** : viser la poitrine de la victime (ou sa tête **une fois
  pliée**). Si l'IK doit tricher, qu'il baisse l'épaule, jamais qu'il la monte.
- **Carte de l'IK des bras du V2.22** (sonde du 2026-09-24, en v3). Elle corrige
  ce que je supposais plus haut : garder la main **près** du pivot ne suffit pas.
  L'IK se comporte comme un bras à deux segments :
  - main à moins de 1,7 stud du pivot d'épaule (`Torso * (±1, 0,5, 0)`) :
    l'épaule **monte** de 0,1 à 0,5 ;
  - main à 1,9-2,3 studs **sous l'horizontale** : elle **descend** de 0,2 à
    0,85, ce qu'on voit chez les pros ;
  - au-delà d'environ 2,4 studs : hors de portée.

  D'où, dans `r6_poing_dragon/scripts/dragon_clip.py` :
  - `arm_point` : une main se pose en azimut, élévation et distance depuis le
    pivot ;
  - `fitp` : le corps se place pour que le pivot tombe à la bonne distance du
    point de contact.

## 9. Entre deux clés, le contrôle IK va en ligne droite

- **Trouvé en v3, en regardant les frames entre les clés.**
- **Effet** : une main qui passe de l'armement (derrière) au coup (devant) coupe
  **à travers** le corps, et l'épaule remonte pendant 2-3 frames. Même chose
  pour un pied qui glisse pendant que le bassin descend : il passe sous le sol.
- **Règle de conception** : poser des clés **en arc** autour du pivot (côté,
  bras bas), et une clé intermédiaire dès qu'un grand mouvement du bassin
  croise un déplacement de pied.
- **Mesuré** : `check_epaules` et le sol sont contrôlés sur **toutes** les frames,
  pas seulement sur les clés.

## 7. Le transfert de poids : le torse passe au-dessus du pied avant

- **Retour** : Milan, v2 : « pas en transfert de poids ».
- **Cause** : en v2, chaque coup avance le pied avant **avec** le corps. Le torse
  ne bouge donc que de 0,16 à 0,21 stud par rapport aux pieds (0,39 sur le coup
  au corps). Ça se lit comme un pas, pas comme une poussée.
- **Pros** (`mecanique_frappe.transfert_poids_studs`) :
  - frappe lourde : 0,33 à 0,92, médiane 0,84 ;
  - M1_1, le seul M1 qui anime le torse : 0,74 ;
  - les autres M1 laissent le script du jeu pousser le perso.
- **Règle** : `rules.check_transfert_poids`, ≥ 0,33 sur chaque coup d'une rafale
  de cinématique (l'animation y porte tout le corps).
- **À la conception** : armer en reculant le torse au-dessus du pied arrière,
  puis au contact le projeter devant le pied avant, pieds plantés. Le pas
  éventuel vient avant l'armement, pas pendant le coup.

## 8. Des règles au vert ne veulent pas dire un corps juste

- **Constat** : la v2 passait 7/7 et Milan a vu en une lecture trois défauts de
  placement du corps qu'aucune règle ne mesurait.
- **Leçon** : pour chaque retour, chercher quelle **mesure** manquait. Ici, la
  hauteur d'épaule, la hauteur du bras au contact et le transfert de poids.
  L'ajouter au corpus d'abord (ce que font les pros), puis en faire une règle.
- La note de Milan reste le verdict (voir leçon 5).
