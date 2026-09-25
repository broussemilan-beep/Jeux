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
       84-110°. J'en avais conclu « deux fois moins » : **conclusion fausse**,
       corrigée plus bas (relecture des refs). Je comparais des rotations
       nettes, pas des amplitudes.
    3. Clés espacées de 2-4 images (Sikasisi, TSB mesuré) : la v7 exporte
       une clé par image. Le plan v7 prévoyait des clés éparses ; seul un
       A/B l'a fait.
  - **Convergence.** Dong Chang (wind-up long, frappe en 1 image,
    follow-through lent) et Wimshurst (fouet, timing 3/5/1/1/4/5)
    rejoignent Williams et la mesure de contraste de la rafale.
    C'est maintenant la piste n°1 du `CARNET.md` §5, pas encore appliquée.

- **2026-09-25, relecture ANIMATION de toutes les refs de Milan** (26
  vidéos/GIF) : `corpus/RELECTURE_REFS_ANIMATION_2026-09-25.md`.
  - **Méthode.** Nouvel outil `outils/planche_ref.py` (tenues, pics,
    énergie). Notes écrites à froid, AVANT de relire l'étude du 24.
  - **Nouveau :**
    - tenues pro contre noob mesurées (19 % contre 0 %, à contraste de
      vitesse égal) ;
    - pose tenue en déplacement ;
    - silence avant et entre les actions ;
    - suites très longues ;
    - la rafale de dos se lit par ce qui dépasse de la silhouette.
  - **Erreur corrigée.** « Torsion deux fois moins que TSB » (hier soir)
    était faux : je comparais des rotations nettes. En amplitude, on est au
    niveau (53-116° contre 77-111°).
  - **Confirmé et renforcé.** Le contraste ré-armement / frappe de la
    rafale (0,55-1,49 contre 2,3-3,7 sur les M1 TSB enchaînés). Le tuto
    firytwig le disait déjà : lu le 24, mais on avait mesuré les durées,
    pas la vitesse relative.
  - **Nuance.** Les M1 TSB n'ont pas de tenue dans le clip (hitstop moteur)
    : pas un manque de notre rafale.

- **2026-09-25, Gemini décrit l'IMAGE de 3 tutos** (texte collé par Milan) :
  `corpus/tutos/gemini_visuel_2026-09-25.md`.
  - **Vérification.** Deux des trois (Charlotte = uppercut Moon ;
    Nate.Animations = coup de poing Blender de myloe) sont des tutos que
    j'avais étudiés image par image : j'ai pu vérifier Gemini point par
    point.
  - **Ce qu'il réussit** : la grande forme (gros armé, frappe très rapide,
    finir de dos), l'outil, l'espacement, le texte à l'écran.
  - **Ce qu'il rate ou invente** :
    - mauvais bras (c'est UpperArm.L qui frappe chez myloe) ;
    - bras avant « tendu pour viser » alors qu'il est plié devant le visage ;
    - numéros d'image inventés ;
    - les tenues (charge 0,57 s, extension 1 image, pose d'après) ;
    - l'ordre de travail (le torse d'abord).
  - **Conséquence** : une description de Gemini sert de carte, pas de mesure
    (CARNET §1.8). Le prompt Gemini gagne un point 8 : quel bras, tenues,
    et « je ne peux pas compter » plutôt qu'un nombre inventé.
  - **Sikasisi** (non vérifiable) : calques dans l'outil officiel TSB, une
    traînée + une seule onde forte à l'impact, lancer / téléport au-dessus.
    C'est une confirmation, pas une nouveauté.

- **2026-09-25, rafale v8** (`r6_poing_dragon/README.md` §v8).
  - **Timing.** Ré-armement lent, armé tenu vivant, frappe en 4 f avec un
    intervalle près de l'armé, Linear sans amorti, dépassement du corps,
    clés posées seules à l'export.
  - **Poses.** Armé plus enroulé, bras libre tiré en arrière au contact,
    fente penchée.
  - **Choix.** Quatre variantes (A, B, B2, C) jugées dans le vrai rig ; B2
    retenue.
  - **Mesures.** Contraste du poing 0,55-1,49 -> 1,44-2,63 (TSB 2,3-4,7).
    Règles 13/13.
  - **Deux leçons** (CARNET §2.7, §2.8) :
    - pousser n'est pas tout gonfler : le lacet de contact multiplié
      faisait rater le contact ;
    - mesurer la réf avant de pousser : les M1 TSB ne penchent que ~12°, le
      « corps à l'horizontale » vaut pour un coup lourd.

- **2026-09-25, retour de Milan sur la v8 : jeu 7,8 (hors coup final),
  ciné 7,2.** « Pas de gros changement en ciné. Le coup final n'est
  toujours pas bon, ce qui est normal : pas encore travaillé. Le cerveau
  a-t-il servi ? Ne t'es-tu pas trop enfermé dans les chiffres au lieu de
  développer ton jugement ? Mais je note une amélioration. »
  - **Ce qui a servi.** Le carnet :
    - firytwig : intervalles près de l'armé, pas d'amorti ;
    - Wimshurst : le bras libre lance la rotation ;
    - le crochet masqué vu au test de silhouette ;
    - la mesure de la bascule TSB, qui a évité de tout faire pencher.
  - **Ce qui n'a pas servi.** Le critique chiffré (`hypotheses.json`,
    `critic.py`) n'a pas été consulté une seule fois pour la v8.
  - **Le biais, reconnu.** J'ai choisi B2 surtout parce qu'il passait
    13/13 règles et gagnait en contraste, et j'ai écarté C sur deux échecs
    de règles plus un pied qui flotte, sans l'avoir regardé en mouvement.
    Les gains réels venaient de mes yeux sur les planches et des refs ; les
    chiffres, eux, ont surtout empêché des erreurs.
  - **Pourquoi la ciné bouge peu.** Découpage, cartes et charge sont
    inchangés ; en gros plan, le rythme compte moins que la mise en scène.
    En caméra de jeu, de loin, c'est le rythme qui se lit.
  - **Méthode à partir de maintenant** (CARNET §1.9) :
    1. regarder d'abord en mouvement, plusieurs fois, et écrire la note au
       format sweatbox ;
    2. décider à l'œil, en s'appuyant sur les refs ;
    3. ne sortir les chiffres qu'ensuite, comme garde-fous. Une règle qui
       échoue est un signal à regarder, pas un veto automatique.

- **2026-09-25, mémoire du cerveau.** Question de Milan : « Le cerveau
  a-t-il une bonne mémoire et tous les outils ? Poing chargé puissant
  devrait faire écho au Serious Punch de Saitama, le GIF et l'anime TSB. »
  - **Constat.** Tout était dans les fichiers : le Serious Punch TSB en GIF
    (48244687 = IMG_3251, « LE coup de ref » dans les notes brutes), le
    Serious Punch 2 (772ee6b0), la fiche v7. Mais le jour même, pendant la
    relecture, j'ai étudié ces deux GIF sans les reconnaître.
  - **Précision.** Le fichier d'animations TSB ne contient pas le Serious
    Punch (il appartient à un autre personnage). Chez nous, le Serious
    Punch n'existe qu'en GIF.
  - **Réparation.**
    - `corpus/CATALOGUE_REFS.md` relie chaque fichier de ref (par
      empreinte) à ce qu'il est et à l'endroit où il est étudié.
    - `outils/rappel.py "<concept>"` rassemble, par familles de synonymes,
      tout ce que le cerveau sait. Il a aussi rappelé l'ancien prototype
      `r6_directional_punch` (un coup chargé), oublié lui aussi.
    - Le rappel est ajouté au démarrage de session (CLAUDE.md) et au carnet
      (§1.11).

- **2026-09-25, « le cerveau se nourrit à 30 %, et toi aussi » (Milan).**
  - **Audit.** Sur ~15 sources du cerveau, la v8 en a cité 3-4 : le carnet,
    trois tutos, des mesures TSB. Pas consultés : l'étude visuelle, les notes
    brutes, les 41 extraits sakuga, les repros (obari), l'étude TSB, le
    critique (pas lancé), le Serious Punch. Le constat de Milan est juste.
  - **Causes.**
    - Le cerveau empile des études CHRONOLOGIQUES, sans rien qui rassemble
      tout au moment de décider.
    - Je travaille sur le plus récent et sur des résumés, et je ne relis pas
      les bases anciennes si rien ne m'y oblige.
    - Le critique n'était pas lancé, et le format de `notes_milan` avait
      dérivé : les v7/v8 n'avaient pas d'`etat`, et le critique plantait.
  - **Réparé.**
    - `notes_milan` v7/v8 remis au format ; `etats_auto.json` recalculé avec
      la v8.
    - Le critique tourne à nouveau : v8 prédite 7,4, notée 7,5 par Milan.
  - **Nouveau : fiches de conception** (`corpus/fiches/`). Une fiche par
    moment de décision, avec toutes les sources digérées ensemble et leur
    liste. Première fiche : `COUP_CHARGE.md`.
    - Ce qu'elle a fait remonter : le Serious Punch montre la frappe DE
      FACE, poing vers l'objectif (grammaire obari, comme la planche OPM et
      Deku). Depuis la v5, notre coup final est vu de profil.
    - Sept versions ont retravaillé la pose sans toucher à ça.

- **2026-09-25, v9 : le coup final aérien refait avec la nouvelle méthode**
  (fiche d'abord, l'œil, les refs, puis les chiffres).
  - **Ce qui a servi** (la fiche a fait remonter des sources jamais utilisées
    en production) :
    - le Serious Punch revu image par image (calme, armé, poing vers
      l'objectif) ;
    - la planche OPM et Deku (tête derrière le poing) ;
    - la repro obari : leçons 2 (pose pour sa caméra), 4 (perspective) et
      5 (membre vers l'objectif) ;
    - Wimshurst (le corps part d'abord) ;
    - les mots de Milan depuis la v1.
  - **Erreurs trouvées en regardant** :
    - la pose d'armé était un tas : bras qui pend, genou parti en arrière à
      cause des axes locaux du contrôle ;
    - le bras avant venait dans l'objectif ;
    - l'allonge de 2,0 studs laissait le poing à 0,34 de la cible.
    Tout a été corrigé avant la production.
  - **Angle mort du cerveau** : `etats.py` mesure la v9 exactement comme la
    v8. Aucune mesure ne regarde la mise en scène de l'aérien. Le critique
    prédit donc 7,4 comme pour la v8, et seule la note de Milan pourra
    apprendre aux hypothèses « obari ».

- **2026-09-25, note de Milan sur la v9 : 7,7** (v8 : 7,5 ; ma prédiction 7,9 ;
  critique 7,4). Ses mots : « très léger en termes de smooth et
  d'enchaînement, mais c'est mieux ; en fait tu n'as animé que les bras,
  encore une fois ; je pense que tu as manqué de vigilance ».
  - **Mesuré ensuite (`outils/corps_bras.py`, nouveau).** Il a raison :
    - calme : torse figé 24/24 images, rien ne vit ;
    - armé : torse figé 16/32 images. Le départ tourne le corps en 6
      images, puis la « tenue vivante » ne fait osciller que la DIRECTION
      DU POING ;
    - frappe : torse figé 15/22 images. De f263 à f278, les 3 clés ont les
      MÊMES angles de corps : le corps est translaté d'un bloc, seul le bras
      agit (bras droit 470° contre torse 116°). En v8, le torse bougeait sur
      chaque image de la frappe ;
    - la rafale et la charge au sol n'ont pas ce défaut (torse jamais figé).
  - **Où j'ai manqué de vigilance.**
    - J'ai conçu des POSES (tour à 8 angles, silhouettes) et je les ai
      reliées par des translations. Je n'ai jamais regardé le MOUVEMENT du
      corps ENTRE les poses : pelure d'oignon, espacement du torse. J'ai
      pourtant construit ces outils le matin même.
    - Le principe « corps d'abord » était dans la fiche, le carnet (§2.1d)
      et les repros (leçon 3). Je l'ai appliqué au départ du coup (260), pas
      au reste.
    - Mon jugement « en mouvement » s'est fait sur des planches à 20 i/s,
      qui montrent des poses et pas la vie entre elles.
  - **Ce que la note apprend au critique** : v9 prédite 7,5 après
    apprentissage, Milan 7,7. La mise en scène obari a payé un peu, le corps
    figé a coûté.
  - **Pour la reprise** : voir `corpus/fiches/COUP_CHARGE.md` §7.
  - **Décision** : animation en pause, chantier VFX ensuite (proposition de
    Milan).

- **2026-09-25, ouverture du chantier VFX (demande de Milan, animation en
  pause).**
  - **Méthode** : ses 27 pistes, explorées en 5 recherches parallèles (code
    cloné et lu), plus un inventaire de ce que le dépôt savait déjà (51
    fichiers). Points clés vérifiés à la main. Digestion dans
    `corpus/fiches/VFX.md`, rapports dans `corpus/recherche/vfx_2026-09-25/`.
  - **Ce qui ressort** :
    - notre VFX est « 5 à 7 fois moins dense » que le pack pro, sans
      flipbook, sans Beam, sans gel au hitstop, sans son ;
    - la doc officielle et le dump de l'API sont désormais lisibles hors
      ligne, et servent de référence de vérité ;
    - le pipeline de flipbooks Blender marche ici, par Cycles CPU ;
    - plusieurs recettes communautaires sont fausses : on ne recopie jamais
      sans vérifier.
  - **Défaut de performance trouvé dans notre module** : le Highlight est
    recréé à chaque coup, ce qui provoque des pics de coût (doc officielle).

- **2026-09-25, rôle (Milan)** : « je suis là pour donner des pistes, je ne
  suis pas expert mais j'ai l'œil ; l'expert est censé être le cerveau, qui
  doit animer complètement, donc aussi les VFX ; une fois fini, note sur 10
  tes VFX comparés à ceux observés ; il y a aussi les SFX, etc. »
  - **Conséquence** : le studio VFX se termine de bout en bout sans
    attendre de consignes. Au programme : compilation Roblox, critique,
    **son (SFX)** et intégration au Poing du Dragon.
  - **Ensuite** : une auto-évaluation sur 10, côte à côte avec les refs,
    notée AVANT l'avis de Milan.

- **2026-09-25, studio VFX terminé (v10 du Dragon), auto-évaluation AVANT
  Milan** : VFX 6/10, SFX 5/10 (`vfx_studio/AUTOEVALUATION_2026-09-25.md`).
  - Fait : moteur Roblox testé, compilateur, critique, défilement par
    variantes, son (étude d'écoute des refs + banque synthétisée), 9
    recettes intégrées au Dragon (lecteur + DragonFist.luau).
  - Défauts trouvés en regardant et corrigés : échelles qui avalaient le
    cadre (caméra obari à 1,5 stud), lignes de vitesse en travers du
    mouvement, éclats cachés par le corps en caméra de jeu (ZOffset),
    direction des particules lue à l'instant courant au lieu de la naissance,
    souffle qui débordait sur le contact, recette plus courte que ses sons,
    filtre qui « sonnait », 3 s de silence numérique, même son rejoué à
    l'identique.
  - Écart principal aux refs : densité et DÉBRIS (Stagnant Rage). Prochain
    pas proposé : débris + bloom dans le lecteur + traînée de vent par coup.

- **2026-09-25, aura dragon (Milan)** : 4 refs du Poing du Dragon de Goku
  SSJ3 + « mélange ça à Izuku pour le poing du dragon ».
  - Étude image par image des GIF (le dragon SORT du tourbillon de feu de
    l'impact), fiche `fiches/AURA_DRAGON.md` écrite avant toute clé.
  - Mélange retenu : dragon doré de Goku (signature) + éclairs verts One
    For All d'Izuku (le courant du perso).
  - Fait (v11) : dragon qui sort du poing et s'enroule (armé), rentre dans
    le poing (plongée), ressort du cratère et rugit (révélation) ; éclairs
    verts ; rugissement et crépitement ; tout jouable dans Roblox.
  - Défauts trouvés à l'écran et corrigés : tête invisible par la tranche,
    tête / cou qui bouchent le plan obari, montée hors cadre.

- **2026-09-25, v11 aura dragon -> VFX 4/10 (Milan)** : « je voulais pas que
  ça se mélange aux éclairs de Izuku mais que la POSE reste celle qu'on a vue
  de Izuku mélangée à celle de Goku ; montre ta créativité avec le cerveau,
  l'animation et les VFX. 4 aux VFX : le dragon est moche, pas du tout du
  modèle premium ; même les VFX construits sont nuls face aux refs du pack ou
  aux refs visuelles. »
  - **Mauvaise lecture (encore)** : « mélange ça à Izuku » = la pose, pas
    ses éclairs. Même biais que « coup final » (CARNET §6).
  - **Écart de prédiction** : j'avais dit ~7 (et 6 pour la v10) ; Milan 4.
    Je surestime mes VFX de 2 à 3 points : je les compare à NOS versions
    précédentes, pas au pack ni aux refs.
  - **Premium** = un vrai modèle 3D (volume, lumière, contour), pas des
    cartes et des rubans plats ; densité et finition du pack 100 Combat VFX.

- **2026-09-25, v12 -> technique 4/10, VFX 2 à 4/10, animation 7,7 (Milan)** :
  « le dragon apparaît 0,5 seconde et pas au bon endroit ; tes VFX sont trop
  nuls. Mais bravo pour le labo et les animations, on avance. Je vais te
  nourrir, toi et le cerveau : des VFX à analyser, et des tutos VFX. »
  - **Mesuré après coup** : le dragon de l'invocation vit 0,57 s (entier
    ~0,27 s) ; la tenue 226-256 ne dure que 0,50 s à 60 i/s, alors que le
    GIF f254bee5 la TIENT 2 s. Je l'ai jugé sur des planches d'images
    fixes : une planche ne montre pas la DURÉE. Regarder la vidéo en temps
    réel avant de noter un moment.
  - « Pas au bon endroit » : à comprendre avec Milan (hypothèses : il doit
    être LE coup, sortir du poing vers la victime comme dans le GIF
    7a2b4ae8, pas décorer derrière le perso ; ou la montée au sol du cratère).
  - **Écart de prédiction** : 6 prédit, 2-4 donné. Le biais « je juge contre
    mes versions » n'est pas corrigé par le fait de le savoir : il faut des
    refs de VFX étudiées côte à côte AVANT de construire (ce que Milan va
    envoyer).
  - L'animation du perso (7,7) tient : le cerveau d'animation marche mieux
    que le cerveau VFX.

- **2026-09-25, v13 en cours (planches de travail) -> la TÊTE du dragon
  (Milan)** : « les yeux du dragon, c'est ce qui casse le truc, ça fait
  moche ; et c'est trop cubique aussi, pas assez travaillé. »
  - Vu sous 3 angles (`captures/verification/2026-09-25-v13b-tete-dragon-
    avant-apres.png`) : museau en PLANCHE (sections presque carrées, 4,5 studs
    de long), œil rond cyan à pupille noire (un jouet), crinière de lames
    brunes plates (un hérisson de carton), aucun détail sur la tête.
  - Refait : sections arrondies, museau plus court et plus haut, bosse du
    nez, arcades en fuseau (colère), œil or étroit à fente sous l'arcade,
    pommettes, naseaux plats sur les côtés (les premiers faisaient des
    oreilles d'ourson vus de face), crinière de mèches-flammes à deux tons,
    bande de texture de tête (plaques du nez, écailles, lèvres à l'encre).
  - Leçon : j'avais jugé la tête sur des plans où elle est petite ; ses
    défauts sautent aux yeux en gros plan, et le gros plan du rugissement
    est justement un plan de la scène. Regarder chaque élément dans le plan
    le PLUS serré où il apparaît.

- **2026-09-25, v13 -> « Revois, il y a des problèmes, je veux voir si tu
  vois sans moi » (Milan)**. Revue plan par plan à 0,1 s, sans indication.
  Trouvés et corrigés :
  1. invocation : à la naissance la tête montait DEVANT lui (côté caméra)
     et le couvrait ; elle monte maintenant derrière lui et plus vite (il
     reste ~0,2 s de crinière sur lui : l'éclosion, gardée) ;
  2. plan du regard : la tête du dragon sur la tête de l'attaquant ;
  3. fusion : le dragon remplissait le cadre, ni l'attaquant ni le poing ;
  4. la transformation du coup en dragon ne se voyait pas (l'os de tête
     rentrait au poing, le museau restait 6 studs devant, sur lui) ;
  5. morsure : la victime (en l'air) semblait couchée par terre (plongée) ;
  6. la victime disparaissait d'un coup à la morsure (pas de flash) ;
  7. l'attaquant atterrissait DANS la colonne de feu du dragon ;
  8. dernier plan : la victime cachée ;
  9. 1,5 s de silence à la fin ;
  10. en jeu (Luau), le dragon ignorait sa transparence : il ne pouvait pas
      disparaître ;
  11. plan très large de l'invocation : l'attaquant coupé à la taille par
      le bas du cadre ;
  12. conséquence : l'attaquant qui atterrit coupé à mi-corps.
  Honnêteté : la 1re planche avant/après a montré que mes corrections 1 et 2
  ne se voyaient PAS (images quasi identiques) ; refaites ensuite. Une
  correction n'existe que si la planche avant/après la montre.
  Pas corrigés (dits) : la silhouette du dragon dans la planche « soleil »
  n'est pas notre modèle ; la conséquence reste sombre.
  Apprentissages : CARNET 4b.26. Planche avant/après :
  `captures/verification/2026-09-25-v13c-revue-sans-milan-avant-apres.png`.

