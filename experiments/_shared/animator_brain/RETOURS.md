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

## Poing du Dragon v5 (2026-09-24) : réponse au retour v4

- **Retour v4 (6,7).** « Le bras ne part plus d'en bas mais ça ne change pas
  la note ; au coup final, le coup part toujours d'en bas ; je verrais plus le
  coup de Saitama. »
- **Lecture v5.** Le « coup final » est l'uppercut de f150, pas la fente du
  4e coup. C'est une question posée à Milan, pas encore confirmée ; « go »
  sans réponse, donc décision prise sur les mesures (`ANGLES_MORTS.md` §1).
- **Changement.** Coup chargé à plat (enroulement, tenue vivante, départ en
  4 f, extension tenue), caméra à hauteur d'yeux, explosion après l'impact.
- **Note de Milan** : à venir.

## Poing du Dragon v6 (2026-09-24) : réponse au retour v5

- **Retour v5 (6,8).** « C'est toujours pas bon, je vois pas trop de
  différence avec la v4. »
- **Lecture.** Même diagnostic du critique et de l'étude visuelle (93 refs) :
  les poses sont au niveau, la mise en scène du sol n'a jamais changé. La
  partie aimée (l'aérien) applique la grammaire des refs ; la rafale et le
  coup chargé non.
- **Changement.** Caméra de la rafale du côté qui montre les coups, hiérarchie
  des effets, charge en plan rapproché, impact raconté à f150 (noir, étoile,
  3 cartes, blanc, plan très large). Aucune pose touchée
  (`r6_poing_dragon/FICHE_V6.md`).
- **Appris en le faisant.** 3 principes écartés sur ce cas précis, avec leur
  contre-indication écrite dans `hypotheses.json` : regard de face (visage
  R6 sans expression), poing vers la caméra (victime dans l'axe), caméra
  d'épaule (dos qui cache). Découverte : la rafale ne se lit pas en caméra de
  jeu.
- **Note de Milan : 7** (prédite 7,8 ; lecture prudente 7,3). « Ça rend
  assez bien en caméra jeu ; en cinéma, peut-être un peu trop abusé, mais
  léger. L'animation reste toujours le bémol : il manque un cap par rapport à
  ce que je veux et nos refs. » Caméra jeu ou cinéma : au cas par cas selon
  la technique, parfois un mélange.
- **Ce que le cerveau en tire.**
  - La mise en scène a fait monter la note (6,8 → 7) : ses poids passent de
    0,50 à 0,65. La cinématique est à doser un peu moins fort.
  - **Contradiction à ne pas mal lire.** Les règles mécaniques mesurées
    (bras horizontal, arcs, coup chargé…) perdent du poids (0,40), parce
    qu'elles sont vraies depuis la v4 sans que la note bouge. Ça ne veut pas
    dire que l'animation compte peu : Milan dit l'inverse. Ça veut dire que
    **nos mesures d'animation ne mesurent pas le « cap »**. Elles vérifient
    la conformité à un pack de M1 réalistes (`ANGLES_MORTS.md` §5 : aucun
    étalon 3D « manga ultime »), pas ce qui sépare nos poses de celles des
    refs.
  - Prochain pas : nommer ce cap sur l'image (nos poses clés contre celles
    des refs, même moment, même grille) avant de toucher à une clé.


- **2026-09-24, après l'étude des tutos vidéo** (Milan : « es-que tu as bien
  appris ? » ; « je veux pas de coup de pied »).
  - **Décision de design : aucun coup de pied** dans le Poing du Dragon.
    Uniquement des poings. L'option h4 « coup de pied » (TSB M4) est
    abandonnée.
  - **Ce que « appris » veut dire ici** : deux règles des tutos sont devenues
    des MESURES (`perception.silhouette`, `perception.torsion`, branchées
    dans `etats.py`), étalonnées sur TSB.
    - **Croix** : 0 % des images chez l'attaquant TSB (13 animations), 93 %
      pendant notre charge v6. La règle est confirmée par la mesure.
    - **Torsion charge → contact** : 130° en v6. **Mon jugement à l'œil
      (« pas de torsion ») était FAUX.** La mesure l'a corrigé : le défaut du
      contact v6 est ailleurs (bascule 20°, bras libre tendu vers l'avant
      avec l'autre).
    - **Faux positif corrigé** : les bras CROISÉS devant (TSB Stoic Bomb)
      comptaient comme une croix. Il manquait la condition « chaque bras part
      vers l'extérieur ». Vu sur la planche, corrigé.
    - Preuve : `captures/verification/2026-09-24-cerveau-detecteur-croix-v6-tsb-v7.png`.

- **2026-09-24, v7 exécutée** (go de Milan). Trois leçons, apprises en
  posant les clés et vues à l'écran, pas prévues par la fiche :
  - **Blocage de cardan sur le bassin du V2.22.** Torse tourné vers −80°, le
    tangage du bassin (Euler XYZ) penche le corps DE CÔTÉ. Pour pencher vers
    la cible un torse de profil, on incline la RACINE (X monde). La 1re passe
    le faisait mal : on l'a vu sur la planche, pas dans la mesure (le
    `bascule_deg` était bon, mais dans la mauvaise direction). À retenir :
    une mesure scalaire ne dit pas la DIRECTION, il faut regarder.
  - **Deux règles justes peuvent se contredire.** Casser la croix de la
    rafale en armant le poing plus haut haussait l'épaule (règle « épaules
    jamais haussées », 0,30 stud). L'arbitrage s'est fait par le levier qui
    ne touche pas l'autre règle : l'AUTRE bras vise plus bas.
  - **Une pose nouvelle casse les cadrages anciens.** Le poing armé au-dessus
    de la tête sortait du gros plan ciné de la charge (cadre réglé pour la
    v6). Vu seulement sur la vidéo : les poses et la caméra se vérifient
    ENSEMBLE, sur la vidéo, pas chacune de son côté.

- **2026-09-25, retour de Milan sur la v7** : « je vois aucun changement ».
  Pas de note. Ma prédiction (7,8) était fausse dans le sens. Trois constats
  honnêtes :
  - **Biais de confirmation dans l'étude des tutos.** Les 4 agents ont reçu
    un cadrage (« notre défaut : torse vertical, charge en croix ») et une
    hypothèse à confirmer ou contredire. Ils ont échantillonné une image
    toutes les 3-4 s et regardé en détail surtout ce qui répondait à nos
    questions. Moi, j'ai revu 3 à 13 images clés par vidéo, pas les vidéos
    entières. On a donc cherché à COMBLER NOS TROUS, pas à tout comprendre.
    Aucune règle issue de cette étude n'est « certifiée ».
  - **Ampleur invisible à la vitesse réelle.** Les changements v7 tiennent
    sur ~0,5 s et ont été vérifiés sur des poses figées agrandies. À la
    lecture, dans le cadrage normal, Milan ne les voit pas. Nos refs sont
    PLUS exagérées et le PLACEMENT (du perso dans le cadre, du corps par
    rapport à la cible) est différent.
  - **Coup chargé aérien** : il part toujours « d'en bas ». Refs données
    (2 images manga) : le poing vient VERS le lecteur, raccourci ; il est
    énorme au premier plan, et le corps est petit derrière. C'est le coup
    chargé de Saitama.

- **2026-09-25, nouvel outil de regard (`outils/regard.py`) : ce que l'œil
  retient à vitesse réelle.** Il fait la moyenne des images sur ~90 ms, puis
  une vignette tous les 83 ms, en petite taille. Appliqué au tuto punch
  (référence) et à notre v7 (charge + coup chargé, caméra ciné et jeu).
  Preuve : `captures/verification/2026-09-25-regard-vitesse-reelle-tuto-vs-v7.png`.
  - **Tuto** : alternance nette entre des poses TENUES, nettes (charge,
    pose d'après), et des passages flous d'1-2 vignettes. L'image est
    « vue » 90 % du temps.
  - **v7 caméra ciné : 43 % seulement.**
    - La charge est floue presque tout du long : le wiggle et la caméra qui
      avance bougent en même temps, donc il n'y a jamais de pose nette.
    - **Le contact v7 n'est JAMAIS vu** : il passe dans un flou, puis les
      cartes (noir, étoile, silhouettes, blanc) le recouvrent aussitôt.
    - Après les cartes, le plan large bouge (caméra + victime), donc il est
      flou lui aussi.
  - **v7 caméra de jeu : 60 %**, mais le perso fait ~1/10 de l'image.
  - **Explication directe de « je vois aucun changement »** : les deux
    poses changées en v7 sont soit floues, soit cachées. Aucune vérification
    faite en v7 ne pouvait le voir (planches figées, poses isolées).
  - Apprentissage (pas une règle) : une pose qu'on veut montrer doit être
    tenue NETTE à l'écran (caméra et corps quasi immobiles ensemble) assez
    longtemps pour être retenue. Les cartes d'impact doivent venir APRÈS
    qu'on a vu le contact, pas à sa place. Le wiggle ne doit pas se cumuler
    avec un mouvement de caméra.

- **2026-09-25, trois recherches versées + vues de jugement des animateurs.**
  - **Recherches.** `corpus/recherche/` (roblox, jugement, anime3d). J'ai
    relu moi-même, dans le texte des sources (*Illusion of Life*,
    *Animator's Survival Kit*, 4Gamer GGXrd, slides d'Eiserloh), les
    citations qui comptent pour nous. Elles sont vraies mot pour mot.
  - **Carnet.** Les pépites vont dans `corpus/CARNET.md`, un carnet
    d'apprentissage séparé des règles (demande de Milan : « pas des
    règles, de l'apprentissage »). Aucun contrôle automatique ne le lit.
  - **Nouvel outil** `outils/vues.py` : silhouette, part de chaque membre
    hors du tronc, pelure d'oignon, espacement du poing, miroir, lecture
    d'une KeyframeSequence image par image. Appliqué à la v7 :
    `scripts/regard_v7.py`, `scripts/regard_v7_vs_tsb.py`.
    - Preuves : `captures/verification/2026-09-25-vues-jugement-v7-silhouette-pelure-espacement.png`
      et `…-contraste-frappe-rafale-v7-vs-tsb.png`.
  - **Fausse alerte évitée.** En caméra de jeu (de dos), le bras qui frappe
    au contact v7 n'est qu'à 8 % hors du tronc. J'y ai d'abord vu le
    problème « main devant la poitrine » de Disney. Mesuré sur TSB, même
    caméra : médiane 15 %, M1 à 1 %. C'est la caméra, pas la pose.
    **Méthode retenue** : mesurer sur la référence, dans la même caméra,
    avant d'appeler « défaut » ce qu'un principe signale.
  - **Vraie différence trouvée.** Rafale v7, rapport vitesse du poing à la
    frappe / pendant la préparation :
    - **0,55-1,49 chez nous** : le ré-armement est aussi rapide que la
      frappe, voire plus ;
    - **2,3-5,7 chez TSB** (M1-M4, Collateral Ruin) ;
    - Williams : « the slow against the fast ».
    - Limite : les M1 TSB sont des clips séparés qui partent du repos.
    - C'est une piste (CARNET §2.1), pas une correction décidée.
  - **Autre piste.** Notre secousse de caméra est une translation en bruit
    blanc à 60 Hz. Eiserloh recommande en 3D la rotation seule, avec un
    bruit lisse et une intensité en trauma². C'est à essayer en A/B
    (CARNET §4.1), et ça peut expliquer « caméra ciné un peu trop abusée ».

- **2026-09-25 (soir), les 15 tutos manquants lus par Gemini** (texte collé
  par Milan) : `corpus/tutos/gemini_transcriptions_2026-09-25.md`.
  - **Portée.** Gemini n'a lu que la parole. Transcriptions vides : DAS,
    Charlotte, Nate.Animations. Le texte, ma lecture critique et les
    mesures sont dans le même fichier.
  - **Trois affirmations chiffrées confrontées à TSB**
    (`r6_poing_dragon/scripts/tutos_vs_tsb.py`) :
    1. « Avancer d'1-2 studs à la frappe » : on le fait déjà (0,3-1,0 dans
       l'anim, TSB ≤ 0,7). Pas un manque.
    2. Rotation du torse pendant la frappe : rafale v7 33-68°, TSB M1-M3
       84-110°. Deux fois moins.
    3. Clés espacées de 2-4 images (Sikasisi, TSB mesuré) : la v7 exporte
       une clé par image. Le plan v7 prévoyait des clés éparses ; seul un
       A/B l'a fait.
  - **Convergence.** Dong Chang (wind-up long, frappe en 1 image,
    follow-through lent) et Wimshurst (fouet, timing 3/5/1/1/4/5)
    rejoignent Williams et la mesure de contraste de la rafale.
    C'est maintenant la piste n°1 du `CARNET.md` §5, pas encore appliquée.
