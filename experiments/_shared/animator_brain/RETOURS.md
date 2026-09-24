# Retours de Milan, production par production

Ce journal est relu **avant** chaque production (voir `LECONS.md`). Chaque
retour porte :
- la note ;
- ce qui plaît ;
- ce qui ne va pas ;
- la leçon qui en est tirée ;
- la preuve que la version suivante l'a traitée : rapport `rules.py` avant/après.

Ce fichier ne contient que des retours réellement donnés par Milan, jamais une
note inventée.

## Poing du Dragon v1 (2026-09-24), `experiments/r6_poing_dragon`

- **Note** : 6/10.
- **Ce qui plaît** : « c'est pas mal sur tout le jeu aérien » (uppercut, envol,
  temps suspendu, plongée).
- **Ce qui ne va pas** :
  - « des problèmes sur l'enchaînement » : la rafale ;
  - « ça manque d'un ressenti de puissance » ;
  - « il est accroupi ».
- **Auto-critique demandée avant correction** (Milan : « dis-moi ce que tu en
  penses honnêtement ») :
  - rafale 4/10, final 5/10, aérien 7/10 ;
  - impact final caché par les planches manga ;
  - pas de son : Milan s'en fiche, écarté.
- **Question de Milan** : « est-ce que le cerveau a servi, ou a été nourri ? »
  - Réponse honnête : il a servi d'outil technique et de correcteur après coup,
    pas de guide de conception.
  - Il avait l'info sur la posture et elle n'a pas été lue.
  - Rien de la production n'était reversé dans le cerveau.
  - D'où `LECONS.md`, `rules.py` et ce journal.
- **Règles sur la v1** (`output/regles_v1.json`) : 3/7. Échecs :
  - posture (affaissement médian 0,55 contre 0,12 max) ;
  - hitstop constant ;
  - un seul angle de caméra pour 6 frappes ;
  - impact final visible 0 f.

## Poing du Dragon v2 (2026-09-24) : réponse au retour v1

Revu par Milan : 6,7/10, détail plus bas.

Règles au moment de la livraison : **7/7**, contre 3/7 en v1. Repassées ensuite avec les règles 6 et 7 : 7/10 (`r6_poing_dragon/output/regles_v2.json`).
- posture : affaissement max 0,19, médian 0,11 (seuils 0,24 / 0,12) ;
- escalade du hitstop : 0,03 → 0,085 ;
- recul de la victime : 0,28 → 1,22 stud ;
- secousse : 0,14 → 0,42 ;
- caméra : 2 frappes par plan au maximum ;
- impact visible 10 f ;
- plongée : 30 f sans coupe.

Preuve visuelle : `captures/verification/2026-09-24-poing-dragon-v1-vs-v2.png`.


### Retour de Milan sur la v2

- **Note** : 6,7/10 (v1 : 6).
- **Ce qui ne va pas**, texto : « un problème avec le placement du corps, les
  bras sont trop hauts, il est accroupi et pas en transfert de poids ».
- **Auto-évaluation demandée avant correction** (« fais ton avis et ta note sans
  mon influence ») : **6/10**.
  - Rafale 5 : elle monte en intensité, mais le corps est faux. Épaules haussées
    en permanence, coups au visage bras levé, le perso fait des pas au lieu de
    pousser.
  - Aérien 7 : inchangé.
  - Final 6,5 : l'impact est enfin vu, et le dôme fonctionne.
  - Je n'avais pas vu seul le haussement d'épaule : c'est la mesure lancée
    après son retour qui l'a trouvé.
- **Mesures** (nouvelles règles 6 et 7 de `LECONS.md`, `output/regles_v2.json`) :
  **7/10**. Les 3 échecs sont exactement ses 3 remarques :
  - épaules : médiane +0,69 stud, max +1,29 (pro : médiane ≤ −0,59, max ≤ +0,04) ;
  - bras au contact : poing à 4,4 studs, bras à +4-5° (pro : 2,5-3,6, ≤ 0°) ;
  - transfert de poids : 0,16 à 0,39 stud (pro, frappe lourde : 0,33 à 0,92).
- **« Accroupi »** : l'affaissement du torse passe la règle (médiane 0,11,
  seuil 0,12), mais de justesse. Les pros tiennent 0,00-0,09 et leurs jambes ne
  s'écartent pas pendant un M1. Nos pas écartent les jambes : une jambe R6 est
  une boîte, donc la hanche baisse. En plus, les épaules haussées tassent la
  silhouette : la tête paraît rentrée.

## Poing du Dragon v3 (2026-09-24) : réponse au retour v2

Revu par Milan : « tu donnes des coups vers le bas » (pas de note). Corrigé en
v3b, voir plus bas. La rafale seulement ; le reste est inchangé
(l'aérien, jugé bon deux fois).

- **Règles** (`r6_poing_dragon/output/regles_v3.json`) : **10/10**.
- **Mécanique du corps au contact** :

  | mesure | v2 | v3 | pros |
  |---|---|---|---|
  | épaule, médiane | +0,69 | −0,61 | −0,59 à −0,92 |
  | épaule, max | +1,29 | −0,01 | +0,04 |
  | poing | 4,4 studs | 2,5-3,2 studs | 2,5-3,6 |
  | bras | +4-5° | −15 à −30° | −20 à 0° |
  | transfert | 0,16-0,39 | 0,62-0,68 | 0,33-0,92 |
  | affaissement, médiane | 0,11 | 0,04 | ≤ 0,12 |

- **Preuves** :
  - `captures/verification/2026-09-24-poing-dragon-v3-profil-contact.png` ;
  - `captures/verification/2026-09-24-poing-dragon-v2-vs-v3-rafale-profil.png`.
- **Compromis assumé** : la distance entre les deux torses reste d'environ
  3 studs, pas le vrai bout portant du Black Flash. Un bras R6 est un bloc de
  2 studs : pour frapper plus près, il faut ramener la main à moins de 1,7 stud
  de l'épaule, et l'IK la hausse (leçon 6). La proximité vient donc du corps
  penché et de la victime qui se plie, pas de la distance.

### Retour de Milan sur la v3, et la v3b

- **Retour**, texto : « y'a un problème, tu donnes des coups vers le bas ».
  Exemples fournis :
  - sa référence « Pro » (vidéo 17-52-55) ;
  - un GIF de combat sous Blender (rig V2.22) ;
  - le Serious Punch.

  Ses mots : « c'est même pas encore parfait sur les vidéos, mais tu vas
  comprendre le concept ».
- **Mon analyse, confirmée par les chiffres** : bras de −15 à −30° au contact,
  pour une médiane pro de −3°. Sur sa référence, le bras reste horizontal et
  c'est le corps qui descend en fente. Leçon 10.
- **v3b** (`r6_poing_dragon/output/regles_v3b.json`) : **11/11**.
  - Bras à −5 à −7° au contact, médiane −5,9°.
  - Poing à 3,2-3,3 studs sur les trois premiers coups, 2,7 sur le coup final
    en fente.
  - Épaules : médiane −0,62, max −0,02.
  - Transfert de poids : 0,59 à 0,84.
  - Affaissement des coups légers : médiane 0,05. La fente du coup final est
    jugée comme coup lourd : médiane 0,39, pour un seuil de 0,83.
- **Preuve** : `captures/verification/2026-09-24-poing-dragon-v3-vs-v3b-bras-horizontal.png`.

### Retour de Milan sur la v3b

- **Retour**, texto : « toujours pas bon, les coups partent toujours du bas.
  Pareil pour le grand coup final : on dirait un enchaînement d'uppercuts, mais
  en même temps un coup droit. Étudie, comprends, avant de te lancer. » Milan
  cherche une référence visuelle.
- **Diagnostic mesuré**
  (`captures/verification/2026-09-24-poing-dragon-v3b-trajectoire-poing-vs-pro.png`,
  `r6_poing_dragon/scripts/fist_path.py`). Trajectoire du poing de profil,
  sur les 16 f avant le contact :
  - **Pros (M1_2, M1_4)** : le poing part à hauteur d'épaule (−0,14 à −0,37),
    **derrière** le torse. Il avance en **ligne horizontale** et monte de 0,02 à
    0,20 sur les 6 dernières frames. M1_1 part de la garde basse, mais **remonte
    d'abord** à hauteur d'épaule, puis avance à plat.
  - **Nous (v3b)** : le poing part de la hanche (−1,3 à −1,8 sous l'épaule),
    reste bas pendant l'armement, puis monte **en diagonale** de 1,1 à 1,7 stud
    en 6 f. C'est un uppercut qui finit à l'horizontale, d'où l'impression de
    Milan : uppercut et coup droit à la fois.
- **Cause** : pour garder l'épaule basse (leçon 6), l'armement et la garde
  plaçaient la main bas et loin. La règle 6b mesure l'angle au contact, pas le
  chemin. Encore une mesure manquante (leçon 8).
- **Référence de Milan** : 5 exemples (fiche dans `corpus/REFERENCES_VIDEO.md`),
  « pas parfaits, ne pas copier bêtement ; style manga, donc exagéré ». Corrigé
  en v4, voir plus bas.

## Poing du Dragon v4 (2026-09-24) : réponse au retour v3b

Revu par Milan : « toujours pas bon ». Il a demandé ma note et celle du
cerveau, voir la fin de l'entrée.

- **Règles** (`r6_poing_dragon/output/regles_v4.json`) : **13/13**.
- **Trajectoire du poing** : montée de 0,00 sur les 0,1 s avant le contact, pour
  les 4 coups (v3b : 1,1 à 1,7) ; hauteur moyenne −0,01 à +0,28 par rapport à
  l'épaule (v3b : −0,58 à −0,73).
- **Bras au contact** : −4,7 à −8,7°.
- **Épaules des coups légers** : max +0,07, médiane −0,18. L'armement du coup
  final monte à +0,26, dans la plage des coups lourds.
- **Transfert** : 0,58 à 0,91.
- **Preuve** : `captures/verification/2026-09-24-poing-dragon-v4-trajectoire-poing-vs-pro.png`.

### Retour de Milan sur la v4 : « toujours pas bon, toi tu mets combien, et le cerveau ? »

- **Ma note, après relecture image par image en caméra cinéma** : rafale
  **4/10**, technique entière **5/10** (l'aérien reste autour de 7).
  - Poses raides : bras en planche, tendus de chaque côté à l'armement
    (épouvantail). Au coup final, les deux bras se referment comme une
    accolade.
  - Mouvement mécanique : le contrôle IK de la main va en ligne droite entre
    les clés. Pas d'arc naturel, pas de décalage entre les membres.
  - La silhouette au contact est cachée par le flash du corps.
  - Réactions de la victime peu lisibles.
- **Note du cerveau** : il n'en a pas, et c'est le vrai problème.
  - Règles apprises : 13/13. Elles se lisent comme un 10/10, alors que Milan
    rejette.
  - Verdict calibré sur le corpus : **53 %** des mesures des coups dans la plage
    pro, 44 % pour les réactions, 47 % pour l'uppercut et la plongée. Ramené sur
    10, ça fait environ 5.
  - Aucune de ces mesures n'a jamais été confrontée aux notes de Milan.
- **Leçon** : 4 versions de suite corrigent chacune la mesure du retour
  précédent (épaules, puis angle du bras, puis trajectoire), sans rendre le
  mouvement bon. On traite des symptômes un par un.
