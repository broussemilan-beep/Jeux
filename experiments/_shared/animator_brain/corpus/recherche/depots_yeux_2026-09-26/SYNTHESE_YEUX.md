# Synthèse : ce que les 7 dépôts proposés apportent aux « yeux » du cerveau

Date : 2026-09-26. Sources : les 7 rapports de ce dossier (`1_…md` à `7_…md`),
les clones en lecture seule dans `/home/user/ext/`, et mes propres vérifications
(§6). Rien n'a été modifié dans `/home/user/Jeux`.

Rappel des 5 faiblesses diagnostiquées :

1. Je regarde des IMAGES une par une, pas du mouvement à vitesse réelle.
2. La profondeur 2D → 3D m'a trompé (bras devant ou derrière le torse sur une ref).
3. Je juge nos anims sur des planches et des chiffres, pas au cadrage réel.
4. Je surestime nos versions (+0,3 sur 10 en moyenne).
5. Je ne distingue pas assez l'anim de JEU (M1, caméra du joueur) de la
   CINÉMATIQUE (caméra écrite, pose trichée pour un plan).

Note sur les numéros d'image : les rapports en utilisent deux sortes. « f283 »
= image de l'export à 60 images/s (le contact d'« Un seul coup » est à 4,72 s).
« f146 » = image de la vidéo à 30 images/s (le flash du contact, 4,87 s). Les
deux horloges ont un petit décalage entre elles ; je précise laquelle à chaque fois.

---

## 0. En bref

- **Aucun de ces dépôts n'est un « œil » prêt à brancher.** Ceux qui promettent
  de « voir » (vidéo → mouvement, juge automatique) exigent tous un GPU, torch
  et plusieurs Go de poids, et sont entraînés sur des humains filmés, pas sur
  des blocs R6 ni sur de l'anime. Chez nous : pas de GPU, et l'index pip répond
  403.
- **Ce qui sert, ce sont des idées simples, en numpy ou ffmpeg**, que plusieurs
  lecteurs ont retrouvées indépendamment : un lecteur côte à côte à vitesse
  réelle avec le son, une carte de ce qui a changé entre deux versions, un
  marquage honnête des profondeurs ambiguës, une mesure de la hauteur d'impact
  sur la victime, et des moyens de vérifier mes prédictions au lieu de les
  croire.
- **Le plus gros enseignement est négatif** : chaque « score automatique »
  testé sur nos données s'est trompé dans le sens qui aggrave la faiblesse 4.
  Notre v6 (« c trjs pas bon ») obtient 4 à 5 sur 5 au score « slow-in/slow-out »
  d'AnimationBench, mieux que le M1 de TSB. Un contrôle qualité générique
  signale comme défaut le départ en 3 images que Milan a validé. Et mon propre
  test du jour (§6) montre qu'une différence de pixels entre v2 et v3 est aussi
  grande qu'entre v4 et v5, alors que Milan a dit « je vois aucun changement »
  pour la v3.
- Donc : **mesurer ce qui a changé, où et combien de temps, et le montrer à
  vitesse réelle ; ne jamais en tirer une note.** C'est la position de Milan
  (« pas de règles gravées »), et les dépôts le confirment par leurs échecs.

---

## 1. Les 7 dépôts, vérifiés dans le code

### 1.1 mixamo-llm-mocap (squall01337, MIT)
- **Promet** « vidéo → animation Mixamo de bout en bout par une IA ». **En
  vrai** : l'étape vidéo (GVHMR) a le GPU écrit en dur (`.cuda()`,
  `pipeline/estimate_pose_gvhmr.py` l. 275 et 292-294, vérifié), 5 Go de poids,
  un modèle de corps humain sous licence, et une vidéo filmée caméra fixe avec
  T-pose. L'application passe par Blender ouvert avec une extension.
- **La moitié « comparaison » est excellente et en numpy pur** : une grille de
  ce que l'œil lit (main par rapport à la tête, écart entre les mains, main
  devant ou derrière la poitrine, bras dans le torse…), par fenêtres de temps ;
  la portée d'un coup dans le repère de la victime ; un journal de 38 pièges
  payés et chiffrés.
- **On garde** : la grille (portée en R6 et testée sur v1-v6, moins de 5 s),
  la portée sur la victime, l'idée d'« écart déclaré » pour une pose trichée,
  et les pièges n° 5, 25, 29 et 38 pour le CARNET. **On inverse** leur contrôle
  qualité bloquant (« HARD FAILURES — fix before showing », `pipeline/qa_clip.py`
  l. 162, vérifié).
- Une copie suspecte existe (`prim-sheetpiling81/…`) : ne jamais la cloner.

### 1.2 AnimationBench (VideoVerses ; code lu : réimplémentation blackzipper-hub)
- **Le dépôt officiel ne contient aucun code** (un README et une licence
  CC BY-NC-ND). La réimplémentation non officielle, sans licence, montre ce qui
  est fait : des questions oui/non posées à un modèle vision-langage distant
  (payant, clé obligatoire), score 100 ou 0 par question (`common/scoring.py`
  l. 48, vérifié), et un score « slow-in/slow-out » qui lisse la vitesse sur
  9 images (`close_set/siso.py` l. 47-67, vérifié).
- **Testé sur nos données** : ce score récompense l'ease disneyen (courbe en
  cloche) et donne à du bruit pur la même note qu'un départ sec d'anime. Notre
  v6 rejetée fait mieux que le M1 TSB. Il ne suit pas l'avis de Milan.
- **On garde** : l'idée de décomposer un moment en **questions observables
  oui/non** (sans note agrégée), de préférer une **comparaison A contre B** à une
  note absolue, et surtout l'idée de **vérifier qu'une mesure classe les
  versions comme Milan** avant de lui faire confiance.

### 1.3 blender-motion-lab (aribornstein, sans licence)
- Prototype propre écrit en une journée : format JSON de mouvement, comparaison,
  alignement temporel, rapport qualité. **Pas de licence** : on lit, on ne copie
  pas.
- Son rapport qualité, passé sur notre v6, échoue sur 5 contrôles, **dont aucun
  n'est un vrai défaut** (genou « toujours à 180° » sur un bloc rigide, départ
  validé vu comme anomalie…). Pire : il **modifie les données** pour limiter la
  torsion du buste à 75° (`processing/stabilize.py` l. 407 et 617, vérifié) :
  une règle gravée qui efface le style.
- **On garde** : le marquage des zones où la profondeur est douteuse (deux
  membres qui se croisent à l'écran), un rapport qui **écrit ses propres
  limites**, et l'idée d'une carte d'écarts **par part et dans le temps** au lieu
  d'un chiffre global (leur chiffre global v5 → v6 : 0,39 stud, inutile).

### 1.4 VeMo / ActionReward (spatial-westlakenlp, Apache-2.0)
- **Un seul score** : un gros modèle vision-langage (14 milliards de paramètres,
  ~28 Go, GPU) répond « oui/non » à « ce mouvement correspond-il au texte ? ».
  La sélection de la « meilleure vue » annoncée n'est implémentée nulle part.
- Petits défauts vérifiés : le texte demande « Yes »/« No » (`VeMo/src/prompts.py`
  l. 10) mais le code lit « yes »/« no » en minuscules (`scorer/intervl3.py`
  l. 138) ; la démo juge une vidéo sur **2 images** (`demo/demo.py` l. 12).
- **Leurs propres données, recalculées** : le juge automatique plafonne bien
  sous l'humain, et lui donner 8 ou 32 images ne change rien : **il juge des
  poses, pas du mouvement**. Leur tirage uniforme de 8 images sur notre v6 ne
  voit ni la frappe ni le contact.
- **On garde** : une mesure géométrique simple de la profondeur perdue, par
  membre et par caméra ; le désaccord entre plusieurs vues comme signal
  d'incertitude ; et la leçon inverse de leur tirage : ancrer les images sur les
  événements du coup.

### 1.5 Pose2Sim_Blender (davidpagnon, MIT)
- Add-on Blender qui **affiche** des données déjà calibrées (caméras, vidéo en
  fond, trajectoires). Il n'estime ni caméra ni pose. Ne s'active pas ici
  (dépend d'OpenSim, absent de pip) et ses opérateurs visuels exigent un écran.
- Son module caméra, pris seul, est exact sur notre caméra (écart 0,0004 pixel),
  à une convention non documentée près (monde tourné de −90°).
- **Test clé refait en numpy** : nos 6 blocs projetés avec la caméra du plan
  se calent à 1-2 pixels sur notre vraie vidéo v6 ; à la charge, bras gauche et
  torse sont à 2 cm de profondeur l'un de l'autre dans le plan réel.
- **On garde** : « voir à travers la caméra du plan » (en numpy, pas dans
  Blender), la même anim vue par deux caméras, les trajectoires projetées à
  l'écran.

### 1.6 Action Library (CGstuff, GPL-3.0)
- Outil de revue **pour humains** : deux vidéos côte à côte, notes ancrées à une
  image, dessin sur l'image, versions v001 → v002. **Il ne mesure rien.** Pas de
  son dans le lecteur (aucun lecteur audio dans le code, vérifié) ; cadence
  réglée par une minuterie sans horloge réelle, avec 24 images/s par défaut
  (`comparison_widget.py` l. 294, vérifié). GPL : aucune ligne à copier.
- Leur export annoté, testé sur notre v6 : la flèche ne reste visible qu'une
  image (42 ms, invisible), la vidéo sort 1,25 fois trop lente et **sans son**.
- **On garde** : la mise en scène (version d'avant à gauche, en boucle, avec
  numéro d'image), refaite en petit **avec** le son, l'horloge réelle, la synchro
  sur un événement et une mesure de l'écart. Le lecteur a aussi montré que le
  **miroir de pose est exact sur un R6 standard** (écart 0,0°).

### 1.7 blender-animation-retargeting (Mwni, GPL-3.0)
- Outil de **transfert** d'une animation d'un squelette à un autre, pas un œil.
  Sur R6, le transfert est exact (0,000°), mais sa correction des pieds par IK
  **penche le torse de 42 à 45°** pour 0,46 stud de pied (la jambe R6 étant un
  seul os, la chaîne inclut le torse). À ne pas utiliser.
- **Retombée utile du test** : la mesure du glissement des pieds plantés existe
  déjà chez nous (`audit.contact_report`) mais n'est pas appelée sur « Un seul
  coup ». Mesurée à part : pied gauche planté 4,63-12,5 s, dérive 1,37 stud.
  Voulu ou patin ? À regarder à vitesse réelle.
- **On garde** aussi, en réserve : si un jour on convertit un squelette humain
  vers R6, copier la **direction du membre** (épaule → main), pas la rotation
  du haut du bras.

---

## 2. Les briques retenues, classées par intérêt pour nos yeux

Chaque brique **mesure et montre ; aucune ne note ni ne bloque.** Classement =
mon avis après lecture des 7 rapports et de mon test du jour, pas une moyenne
des notes des lecteurs.

| Rang | Brique | Faiblesses | Coût | D'où |
|---|---|---|---|---|
| 1 | Lecteur côte à côte à vitesse réelle, avec son, synchro sur l'événement, deux caméras | 1, 3, 5 | 1 h (ffmpeg) à ½ jour (lecteur HTML) | 1, 5, 6 |
| 2 | Prédiction vérifiable : questions oui/non à l'aveugle, préférences A/B, et « cette mesure classe-t-elle comme Milan ? » | 4 | ½ jour | 2, 4 |
| 3 | Carte de ce qui a changé entre deux versions (à l'écran ET en mots de corps) | 3, 4 | ½ jour (prototypes prêts) | 1, 3, 6 |
| 4 | Profondeur ambiguë affichée (devant/derrière le torse), au cadrage réel | 2 | ½ à 1 jour | 3, 4, 5 |
| 5 | Hauteur et pente d'impact sur la victime | 3, 4 | 2 h (prototype prêt) | 1 |
| 6 | Jeu contre ciné : triche déclarée, et caméra du joueur pour les M1 | 5 | quelques heures | 1, 3, 5, 7 |
| 7 | Glissement des pieds plantés, par fenêtre, avec sa définition | 3 | 30 min (code existant) | 7 |
| 8 | Chaque rapport écrit ce qu'il ne voit pas ; pièges versés au CARNET | 4 | 1 h par outil | 1, 3 |

Plus bas, utiles mais pas prioritaires : trajectoire du poing projetée à l'écran
avec l'espacement en pixels par image (5) ; découpage de la vidéo en plans avant
toute mesure (2) ; miroir de pose R6 pour comparer une ref gauchère (6) ;
alignement de deux performances par leurs courbes d'énergie (3) ; notes de
Milan ancrées à une plage d'images, marquées « mon interprétation » (6).

### Rang 1 : lecteur côte à côte à vitesse réelle (faiblesses 1, 3, 5)
- **Ce que c'est** : deux vidéos l'une à côté de l'autre (version d'avant à
  gauche, nouvelle à droite), lues ensemble à la vraie vitesse, **avec le son**
  (Milan juge avec le son), le numéro d'image et le temps incrustés, en boucle.
- **Adapté à nous** :
  - synchro **sur un événement** (départ, contact, fin du recul) lu dans nos
    marqueurs de scène, pas sur le numéro d'image. Entre nos versions d'« Un
    seul coup », le contact tombe à la même image partout (f146 vidéo), mais
    les coupes de caméra de la charge bougent d'une version à l'autre, et
    contre une ref TSB le contact tombe ailleurs ;
  - **deux modes**, parce que le lecteur n°1 a vu sur v5 | v6 que l'œil ne
    sait plus si ce qui change vient de la pose ou de la caméra :
    « caméra réelle » (le plan de la cinématique) et « caméra fixe » (l'anim
    seule ; pour un M1, la caméra du joueur, FOV 70°, distance à mesurer en
    Studio le moment venu) ;
  - ref | nous : seulement dans le scratchpad, jamais versionné (droits).
- **Coût** : ffmpeg `hstack` + texte incrusté, déjà testé (v5 | v6 avec son en
  7 s). Un lecteur HTML calé sur l'horloge réelle : environ 150 lignes.
- **Tester en premier** : le côte à côte v5 | v6 existe déjà
  (`al_test/cote_a_cote_v5_v6.mp4`). Il manque la version « caméra fixe ».

### Rang 2 : rendre ma prédiction vérifiable (faiblesse 4)
Aucun dépôt ne corrige la surestimation en ajoutant un juge ; deux d'entre eux
(AnimationBench, VeMo) montrent au contraire comment on vérifie un juge.
- **Questions fermées, à l'aveugle** : pour chaque moment, 5 à 8 questions
  observables tirées des mots de Milan (`corpus/milan_verbatim.jsonl`) : « au
  contact, le poing est-il à hauteur de poitrine ? », « le buste tourne-t-il
  avant le bras ? », « le bras est-il tendu derrière ? ». Chacune dit comment on
  y répond (une mesure, ou un regard à vitesse réelle au cadrage réel) et pour
  quel cadrage (jeu ou ciné). Un **sous-agent** y répond **sans savoir quelle
  version est la nouvelle** (versions mélangées) : si c'est moi qui réponds en
  sachant, le biais de +0,3 revient. On publie la liste des réponses, **jamais
  un pourcentage**.
- **Préférences A contre B** : à côté de la note prédite (toujours exigée par
  le NOYAU), prédire « Milan préférera-t-il v6 à v5 sur la charge ? oui/non,
  avec quelle confiance ». Vérifiable à son retour.
- **Chaque mesure passe un test d'alignement** : sur l'historique
  (`notes_milan.jsonl`, 27 lignes, et ses préférences entre versions), est-ce
  que cette mesure classe les versions dans le même ordre que Milan ? (Un
  coefficient de Kendall compte simplement les paires de versions rangées dans
  le même ordre que lui, moins celles rangées à l'envers.) Chaque mesure est
  affichée « alignée » ou « non alignée » avec une réserve honnête : une
  dizaine de points seulement, c'est un signal, pas une preuve.
- **Coût** : une demi-journée ; aucune dépendance.

### Rang 3 : carte de ce qui a changé entre deux versions (faiblesses 3 et 4)
Réponse directe aux quatre « je vois aucun changement ». Trois lecteurs l'ont
construite de trois façons ; on les combine :
- **à l'écran** : plages de temps où l'image change, et combien (lecteur 6,
  environ 40 lignes) ; version par part, en pixels, au cadrage réel, avec deux
  lignes « vu » (caméra propre à chaque version) et « animation seule » (même
  caméra) (lecteur 3, prototype `bml/ecran.py`) ;
- **en mots de corps** : « de f192 à f266 (export), les mains sont 2,11 studs
  plus proches ; la tête tourne de 26° de moins après le contact » (lecteur 1,
  `mixamo_test/r6_compare.py`), par fenêtres d'au moins 7 images à 60 i/s.
  Elle a aussi montré que la pose au contact est **strictement identique de v2
  à v5**, ce que je n'avais pas vu.
- **Ce qu'elle ne dit pas** : si c'est mieux. v5 → v6 est le plus gros
  changement mesuré, et c'est la version « c trjs pas bon ». En tête de l'outil :
  « ceci mesure le changement, pas la qualité ».
- **Coût** : une demi-journée, prototypes testés.

### Rang 4 : profondeur ambiguë affichée (faiblesse 2)
Trois lecteurs arrivent à la même conclusion : **on ne devine pas une profondeur
qu'on ne voit pas ; on dit qu'elle est ambiguë.**
- **Sur nos anims** (3D connue) : pour chaque bloc, sa profondeur par rapport à
  la caméra du plan et son recouvrement à l'écran avec le torse. Si le bras et le
  torse sont à quelques centimètres et se recouvrent (cas réel à la charge de
  la v6 : 2 cm), on l'écrit comme observation : « de cette caméra, devant ou
  derrière ne se lit pas ».
- **Sur une ref reconstruite avec `geo_pose`** : un bloc R6 est rigide et de
  longueur connue, donc seul le **signe** de la profondeur est perdu à l'écran.
  Mesure : à quel point le membre pointe vers la caméra (lecteur 4, 80 lignes,
  prototype `vemo_test/ambiguite_vues.py`). On rend aussi l'hypothèse miroir
  (bras de l'autre côté du torse) ; si les deux collent aussi bien à la ref, on
  écrit « non observable sur cette image » et on tranche avec les images voisines
  (lecteur 3). Atout propre au R6 : les blocs de couleur plate montrent **quel
  bloc passe devant** là où ils se chevauchent, ce que la silhouette seule ne dit
  pas.
- **Ne pas en faire un choix de caméra** : « prendre la vue la plus lisible »
  tuerait le poing jeté dans l'objectif voulu à la frappe (f275 export). La mesure
  s'affiche, elle ne choisit rien.
- **Coût** : une demi-journée à un jour, numpy + notre moteur de rendu.

### Rang 5 : hauteur et pente d'impact sur la victime (faiblesses 3 et 4)
- Où le poing touche, dans le repère du torse de la victime, et la pente du bras.
  C'est enfin un chiffre pour « il frappe vers le bas » (6 retours de Milan).
- Mesuré au contact (f283 export) : v1 y = −0,32 (sous le milieu du torse) ;
  v2 et v5 y = +0,35, pente −5° ; v6 y = +0,30, pente −10°.
- **Adapté** : une ligne dans `verify_export.py` à chaque version, et les mêmes
  chiffres sur les anims TSB (WallCombo joueur/victime) pour comparer. Le
  contact voulu est marqué comme tel.
- **Coût** : environ 60 lignes, prototype prêt (`mixamo_test/r6_pair.py`).

### Rang 6 : jeu contre cinématique (faiblesse 5)
- **Triche déclarée** : un champ `triches: [{f0, f1, plan, quoi}]` dans le JSON
  de production. Les mesures continuent de montrer l'écart, étiqueté « tricherie
  de plan déclarée » au lieu de « défaut ». Idée de mixamo-llm-mocap (« declare
  it so the cost stays visible »), et du « cube de contrôle » de l'outil de
  transfert : une couche par plan posée par-dessus une anim de base propre, dont
  on mesure l'écart.
- **Toujours dire quelle caméra a servi** à une mesure. Aujourd'hui,
  `planche_cles.py` rend en 3/4 et en profil : ni la caméra du joueur ni celle
  du plan. Un M1 se juge à la caméra du joueur (plusieurs angles, dont de dos) ;
  une pose de ciné, seulement dans la caméra de son plan.
- En M1, rien n'est déclarable : pas de caméra écrite pour cacher une triche.
- **Coût** : quelques heures.

### Rang 7 : glissement des pieds plantés (faiblesse 3)
- Brancher `audit.contact_report` dans la vérification d'« Un seul coup »,
  fenêtre par fenêtre, **avec la définition à côté du chiffre** : selon la
  définition du pied planté, la même anim donne « 12 studs » ou « 1,37 stud ».
  Puis regarder les deux fenêtres qui dérivent à vitesse réelle.
- **Coût** : 30 minutes.

### Rang 8 : l'outil dit ce qu'il ne voit pas (faiblesse 4)
- Chaque sortie (`rapport_regard`, `geo_pose`, `juge`, la carte d'écarts) finit
  par « ce que cette mesure ne voit pas » (caméra interpolée, effets mêlés au
  mouvement, une seule image de ref…).
- Verser au CARNET, comme **apprentissages** reformulés pour R6 : ne jamais
  décider d'un membre sur une image fixe ; quand l'œil et les chiffres
  divergent, suspecter d'abord les chiffres ; mesurer le même point des deux
  côtés (coin le plus bas d'un bloc, pas son centre) ; un contact voulu n'est
  pas une pénétration. Avec l'exemple réel du faux « deux pieds en l'air à
  f269 » produit par le portage du lecteur 1.

---

## 3. Ce qu'on inverse, et ce qu'on ignore

**À inverser (l'idée est bonne, le sens est faux pour nous)**

| Chez eux | Chez nous | Pourquoi |
|---|---|---|
| Contrôle qualité bloquant (mixamo `qa_clip.py`, motion-lab) | Mesures affichées, aucun verdict | Le départ en 3 images validé par Milan y sort comme défaut ; le style anime y passe pour une erreur |
| Données corrigées pour rester « humaines » (torsion max 75°) | Un outil de regard ne touche jamais la pose | Règle gravée qui efface le style |
| Score qui récompense la courbe en cloche (slow-in/slow-out) | Chercher une tenue puis un départ sec | Critère disneyen, à l'envers pour l'anime |
| « La vidéo a raison » (fidélité à un acteur) | Un écart à la ref est une donnée, pas une erreur | Nous exagérons et trichons pour le plan |
| Images tirées uniformément dans la vidéo | Images ancrées sur les événements (clés, contact ±2 images) | Leur tirage ne voit ni la frappe ni le contact |
| Choisir la vue la plus lisible | Afficher la lisibilité, garder la caméra écrite | Le raccourci vers l'objectif est voulu |
| Synchro par numéro d'image, alignement « même prise » | Synchro par événement, par morceaux | Nos phases sont retimées ; une ref n'a pas notre timing |
| Statuts Approuvé / Final / À reprendre | « Montré à Milan le…, sa note, ses mots » | Un statut que je me donne est un verdict |
| Copier la rotation de l'os (transfert humain → R6) | Copier la direction du membre | Le haut du bras humain n'indique pas où est la main |

**À ignorer**
- Les juges par modèle vision-langage (InternVL3 de VeMo, Qwen via l'API
  DashScope d'AnimationBench) : GPU ou envoi de nos vidéos et des refs sous
  droits chez un tiers, et ils jugent des poses, pas du mouvement. Ajouter un
  modèle à Claude double notre biais au lieu de le corriger.
- L'estimation de pose depuis la vidéo (GVHMR, MediaPipe, CoTracker, SAM) :
  GPU ou pip bloqué, entraînée sur des humains ; et leur propre documentation
  dit que la profondeur cachée ne se récupère pas. Les KeyframeSequences
  exactes des pros valent plus.
- Tout ce qui passe par le viewport de Blender (aperçus, « voir à travers »,
  miroir par copier-coller) : muet sans écran ici. Rester en numpy avec notre
  moteur de rendu.
- Les applications elles-mêmes (Action Library en PyQt6, add-on Pose2Sim, IK
  du transfert) et les métriques d'humain (angle du genou, longueurs de
  segments) : sans objet pour 6 blocs rigides.
- Une note unique pour un clip de 12,5 s à plusieurs plans et coupes.

---

## 4. Plan en 3 étapes

### Étape 1 (testable aujourd'hui) : le côte à côte et la carte des changements, vérifiés contre les mots de Milan
Sur « Un seul coup » v2 → v6, dont les 5 vidéos sont déjà dans
`captures/verification/` :
1. produire v(n) | v(n+1) avec son, synchronisé sur le contact, numéro d'image
   incrusté (ffmpeg, déjà prouvé) ;
2. y joindre la carte des changements à l'écran et en mots de corps (prototypes
   des lecteurs 1, 3 et 6) ;
3. **le test qui compte** : la carte explique-t-elle ce que Milan a dit ? Je l'ai
   lancé (§6) et la réponse est **non, pas en pixels bruts** : v2 → v3 (« je vois
   aucun changement ») change 1,63 s d'écran avec un pic à 59 %, autant que
   v4 → v5 (« un peu mieux »). Il faut donc voir si la version « animation seule »
   (même caméra, par part) ou la grille en mots de corps sépare mieux ces deux
   cas. Si aucune ne le fait, c'est une leçon à écrire : Milan parle du
   **mouvement lu**, pas de la quantité de changement.

Tout reste dans le scratchpad ; seules les captures de preuve iront dans
`captures/verification/` avec le changement qu'elles prouvent.

### Étape 2 : la prédiction qui se vérifie
Grille de 5 à 8 questions oui/non pour la fiche `UN_SEUL_COUP.md`, tirées des
mots de Milan ; un sous-agent y répond à l'aveugle sur v2 → v6 mélangées ; en
parallèle, le test d'alignement (Kendall) de chaque mesure existante contre
`notes_milan.jsonl`. On sait alors quelles mesures suivent Milan et lesquelles
n'ont jamais rien dit de sa note. Pour la prochaine livraison : note prédite
**plus** préférences A/B prédites, écrites **après** avoir regardé le côte à
côte, **avant** d'envoyer.

### Étape 3 : profondeur, impact, jeu/ciné
Dans cet ordre : la profondeur ambiguë au cadrage réel (rang 4), la hauteur
d'impact dans `verify_export.py` (rang 5), le champ `triches` et la caméra du
joueur pour les M1 (rang 6). Puis les pièges au CARNET. Chaque ajout finit par
sa liste « ce que je ne vois pas ».

---

## 5. Pièges

1. **Faux sentiment d'objectivité.** Un chiffre ressemble à un jugement. Sur nos
   données, chaque score testé s'est trompé : 4-5/5 à une v6 rejetée ; « échec »
   sur 5 contrôles qui n'étaient pas des défauts ; différence de pixels égale
   entre une version « aucun changement » et une version « un peu mieux ». Un
   écart mesure le **changement**, jamais la **qualité**.
2. **Une note automatique qui remplacerait l'œil de Milan.** Même le meilleur
   juge publié (VeMo) reste nettement sous l'humain, et deux humains ne
   s'accordent qu'à 78-88 %. Tout ce qui produit une note ou un pourcentage
   agrégé est à refuser : on garde des mesures, des questions et des
   observations, et c'est Milan qui juge.
3. **La surestimation qui revient par la porte de derrière.** Si je réponds
   moi-même aux questions en sachant quelle version est la nouvelle, ou si je
   cite un gros changement mesuré comme un progrès, le +0,3 revient. Aveugle,
   et une préférence prédite qu'on peut démentir.
4. **Juxtaposer n'est pas comparer.** Mettre deux vidéos côte à côte donne
   l'impression d'avoir comparé. Il faut regarder à vitesse réelle, écrire en
   une phrase ce qu'on voit en mots de corps, puis seulement le mesurer.
5. **Points non appariés et définitions cachées.** « Deux pieds en l'air »
   (faux : centre du bloc au lieu de son coin le plus bas) ; « 12 studs de
   glissement » ou « 1,37 » selon la définition du pied planté ; un transfert
   faux de 180° parce qu'une étape d'alignement était sautée, sans message.
   Toujours nommer le point mesuré, afficher la définition, et faire passer
   toute conversion par un cas où la réponse est connue (identité = 0).
6. **Conventions silencieuses de repère et de cadence.** Monde tourné de −90°
   sans le dire (Pose2Sim) ; 24 images/s par défaut qui ralentissent la vidéo
   de 25 % et suppriment le son (Action Library) ; FOV vertical ou sur la plus
   grande dimension selon l'outil. Vérifier par un aller-retour chiffré et
   `ffprobe`, jamais à l'œil.
7. **Caméra et anim mélangées.** Un côte à côte de versions finales mêle
   changement de caméra et changement de pose : toujours les deux modes.
8. **Déplacer la faiblesse 2 au lieu de la régler.** Les estimateurs 3D se
   trompent précisément sur un bras derrière le torse vu de 3/4. Face à deux
   hypothèses qui collent aussi bien, écrire « ambigu », ne pas choisir.
9. **Nos propres outils ont aussi des portes.** `juge.py` parle de « porte
   franchie » (seuils à 0,8 × la médiane des refs), même s'il n'interdit pas de
   montrer. À relire avec le même regard : afficher, ne pas trancher.
10. **Licences et sécurité.** GPL (Action Library, transfert), pas de licence
    (motion-lab, réimplémentation AnimationBench), CC BY-NC-ND (AnimationBench) :
    on réécrit les idées, on ne copie aucune ligne. Ne jamais exécuter
    `camera_motion.py` d'AnimationBench tel quel (il désactive la vérification
    TLS du processus), ni la copie suspecte de mixamo-llm-mocap.

---

## 6. Ce que j'ai vérifié moi-même

Dans les clones (`/home/user/ext/`) :
- `mixamo-llm-mocap/pipeline/estimate_pose_gvhmr.py` l. 275, 292-294 : `.cuda()`
  en dur ; `pipeline/qa_clip.py` l. 162 : « HARD FAILURES — fix before showing ».
- `ActionReward/VeMo/src/prompts.py` l. 10 demande « Yes »/« No » ;
  `src/scorer/intervl3.py` l. 138 lit `["yes", "no"]` ; `demo/demo.py` l. 12 :
  `num_segments = 2`.
- `blender-motion-lab/src/motion_lab/processing/stabilize.py` l. 407
  (`_constrain_torso_twist`) et l. 617 (`maximum_torso_twist_degrees = 75.0`).
- `action_library/…/comparison_widget.py` l. 294 : `fps = max(A, B, 24)` ;
  aucune occurrence de `QMediaPlayer` ni `QAudioOutput` dans `animation_library/`.
- `animationbench_blackzipper/common/scoring.py` l. 48 : 100 ou 0 ;
  `close_set/siso.py` : `moving_average(…, window=9)` l. 47, 67, 82, 123 et
  `device='cuda'` l. 171.

Test du jour (script : `c4/depots/diff_versions_v2v6.py`, dérivé de
`al_test/diff_versions.py`, sur les vidéos de `captures/verification/` ;
vignettes 213×120 en gris, un pixel change si l'écart dépasse 25, une image
compte si plus de 2 % de l'écran change) :

| Passage | Mots de Milan | Temps d'écran changé | Pic |
|---|---|---|---|
| v2 → v3 | « je vois aucun changement » | 1,63 s (f93-141 vidéo) | 59 % |
| v3 → v4 | (pas de mots sur v4) | 1,60 s | 47 % |
| v4 → v5 | « un peu mieux mais c'est pas bon encore » (7,5) | 1,63 s | 79 % |
| v5 → v6 | « c trjs pas bon » | 7,10 s (charge, après-contact, fin) | 73 % |

Lecture : en pixels bruts, la v3 a changé autant que la v5. Milan a pourtant vu
la seconde et pas la première. **La quantité de pixels changés ne dit pas ce que
Milan perçoit comme un changement.** C'est la raison pour laquelle l'étape 1
commence par tester la carte contre ses mots, et non par la brancher.

## 7. Fichiers

- Rapports complets : `c4/depots/1_mixamo_llm_mocap.md` … `7_blender_anim_retargeting.md`.
- Prototypes testés : `c4/depots/mixamo_test/` (grille, impact, côte à côte),
  `c4/depots/bml/` (carte d'écarts à l'écran), `c4/depots/vemo_test/`
  (profondeur par vue), `c4/depots/p2sb_test/` (calage caméra sur la vidéo),
  `al_test/` (côte à côte avec son, écart entre versions, miroir),
  `c4/retarget_test/` (transfert, glissement des pieds).
- (Chemins relatifs au scratchpad
  `/tmp/claude-0/-home-user-Jeux/4796ac9e-8e41-51f7-91c4-7b92a6a187d0/scratchpad/`.)
