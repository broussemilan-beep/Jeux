# Chantier 4 — C2_clips_jeux : 7 clips de jeux regardés comme un apprenti animateur

Auteur : sous-agent C2 (2026-09-26). Lecture seule du dépôt. Images de travail :
`/tmp/claude-0/-home-user-Jeux/4796ac9e-8e41-51f7-91c4-7b92a6a187d0/scratchpad/c4/frames/C2_clips_jeux/`
(planches-contacts horodatées à 30 i/s sur les moments d'action ; le temps affiché
sur chaque vignette est le temps réel du fichier source).

Méthode : `planche.sh` (ffmpeg fps=30 + drawtext du pts + tile) ; `energie.py`
(différence moyenne entre images successives à 30 i/s, 160x90 niveaux de gris :
proxy grossier du « combien ça bouge », caméra comprise) ; détection des cartes
noires/blanches par luminance ; attaques du son (passe-haut 2 kHz) pour IMPACT HAVEN.
Statuts : **vu** (j'ai regardé l'image), **mesuré** (outil), **lu** (texte existant),
**déduit** (mon interprétation). Rien n'est une règle : ce sont des observations de
ce que CES animateurs font ici.

Rappel lancé avant (rappel.py --court) : « anticipation poing chargé », « caméra suit
le geste », « blanc d'une image impact ». Études existantes relues :
`corpus/ETUDE_NOTES_BRUTES.md` (sections Black Flash, IMPACT HAVEN, Black Hole, Rewind
Clock, Stagnant Rage, Gemini soleil + « LOT 4 »), `corpus/ECOUTE_REFS_SFX_2026-09-25.md`.
Les anciennes notes étaient surtout VFX/caméra ; ici je regarde d'abord le CORPS.

Sources vérifiées (ffprobe) : les .mov/.mp4 de Milan sont des enregistrements d'écran
de téléphone à fréquence variable (moyenne 45-60 i/s ; 888 px de large). Les 3
premiers (Black Flash, Rewind Clock, Stagnant Rage) sont en paysage dans un cadre
portrait (bandes noires : crop 1576x888). Black Hole et IMPACT HAVEN sont des
Shorts/TikTok portrait (interface visible). Gemini = 1280x720 à 24 i/s, IA.
Thunder Dragon = 640x360 à 30 i/s, sans son.

---------------------------------------------------------------------------------

## 1. Black Flash (12e7dae5, .mov 6,4 s) — combo de jeu puis cinématique

### Découpage (vu sauf mention)

| Temps (s) | Ce qui se passe | Corps | Caméra / effets |
|---|---|---|---|
| 0,00-0,07 | attaquant (manteau blanc, cheveux noirs) collé à la victime jaune | accroupi bas, très proche | caméra de jeu haute, fixe |
| 0,067 | 1 image : un personnage devient ENTIÈREMENT rouge (aplat) | — | marque de coup |
| 0,10-0,20 | disque noir + gerbe rouge 3-4 images | caché par l'effet | secousse |
| 0,27-0,53 | TENUE : l'attaquant reste collé à la victime, quasi immobile (≈8 images) | pose basse compacte | effet retombe |
| 0,567 | 1 image rouge/rose sur la victime | | |
| 0,60-0,67 | 2e coup : disque noir + rouge | | |
| 0,70-0,87 | attaquant dos à la caméra, buste tourné | suivi du coup, rotation de tout le corps | |
| 0,90-0,97 | 3e coup | | |
| 1,00-1,10 | attaquant presque À L'HORIZONTALE, plongé au sol vers la victime | pose extrême : corps entier en diagonale basse | |
| 1,133-1,17 | 4e coup | | |
| 1,37-1,47 | victime projetée en l'air ; attaquant aplat rouge 1 image (1,367) | | 5e coup |
| 1,70-1,83 | 6e coup : c'est ici l'ATTAQUANT qui passe en aplat rouge (1,70) | | |
| 1,87-2,33 | CREUX : l'attaquant attrape la victime et l'emmène, mouvement lent, ~14 images | marche/porte, pas de pose forte | aucun effet |
| 2,367 | éclair blanc/rouge plein écran 1 image -> CINÉMATIQUE | | coupe cachée par le flash |
| 2,43-3,37 | caméra coincée ENTRE les deux têtes (tête jaune à gauche, cheveux noirs à droite au premier plan) ; l'impact rouge se voit dans l'interstice | corps invisibles : on ne voit que 2 masses | dérive lente |
| 3,40-3,73 | cartes : N/B 2 i, croix rouge 2 i, 1 i, croquis au trait 3 i (polarité alternée), rouge 1 i, blanc 1 i, noir+traits rouges 1 i | | |
| 3,767-4,17 | TRÈS GROS PLAN penché : le BRAS BLANC de l'attaquant traverse le cadre en diagonale au-dessus de la tête jaune. Le bras est déjà tendu à la 1re image : on ne voit JAMAIS le trajet | bras tendu tenu ≈13 images | un trait rouge « se dessine » sur le bras |
| 4,20-4,63 | cartes encre (taches, croix, hachures) ~2 images chacune | | |
| 4,667-4,70 | crâne rouge | | |
| 4,73-6,23 | PLAN FINAL tenu 1,5 s : caméra au ras du sol, PRÈS DU POING. Premier plan : bras droit tendu vers la caméra, poing ensanglanté, manche blanche ; derrière, la tête baissée de l'attaquant, buste penché sur le bras ; au fond, la victime MINUSCULE (lueur rouge) | tenue finale du coup | mouvement qui décroît en continu |
| 6,267 | retour caméra de jeu | | |

Mesuré : sur le plan final, l'énergie de mouvement image à image passe de ≈33
(4,76 s) à ≈4 (6,23 s) de façon régulière : c'est une décélération continue (dérive
de caméra + effets qui s'éteignent), pas une image figée.

### Ce qui est fort
- **Rythme qui accélère** (vu, temps lus sur les planches) : coups à ≈0,07 / 0,60 / 0,90 /
  1,13 / 1,40 / 1,70 s : intervalles 0,53 -> 0,30 -> 0,23 -> 0,27 -> 0,30 s. Puis le
  CREUX de 0,5 s (1,87-2,33) avant la cinématique. Le spectateur est pressé puis
  relâché juste avant le pic : le pic n'en paraît que plus fort (déduit).
- **Le trajet du coup n'est jamais montré** : pendant la cinématique, le bras
  apparaît déjà tendu (3,767) juste après une série de cartes. L'animateur montre
  « avant » (les deux têtes collées) et « après » (le bras tendu, tenu), la vitesse
  est dans la coupe (vu).
- **Le plan final raconte la distance** : poing au premier plan, victime petite au
  fond. On comprend la force par l'écart d'échelle, sans voir la victime voler (vu,
  `bf/f5_5.png`).
- **Aplat de couleur sur tout le corps pendant 1 image** comme marque de coup (vu :
  0,067 ; 0,567 ; 1,367 ; 1,70).

### Ce qui CONTREDIT l'ancienne note
`ETUDE_NOTES_BRUTES.md` (LOT 4) dit : « 4,8-6,2 s : RALENTI en gros plan sur la
victime ensanglantée ». Ce que je vois (`bf/f5_5.png`, 5,5 s ; planche `bf/fin15_01.png`)
: c'est le BRAS TENDU DE L'ATTAQUANT (manche blanche, main ensanglantée) au premier
plan, et la victime est minuscule au fond. La note finale n'est donc pas « la
conséquence sur la victime » mais « le coup tenu par celui qui frappe, avec la
conséquence au loin ». Statut : vu.

### Comment je le referais en R6 (déduit, à tester)
- Pose finale (tenue 45 images à 30 i/s) : bras droit tendu vers l'avant et un peu
  vers le bas (épaule droite tournée vers l'avant, bras dans l'axe du regard caméra),
  Torso penché vers l'avant et tourné pour amener l'épaule droite devant, tête baissée
  dans le prolongement, bras gauche rejeté derrière. Caméra : au ras du sol, 1-2 studs
  devant le poing, FOV serré, cadrant le poing grand et la victime à 20-40 studs
  derrière. Dérive de caméra en décélération sur 1,5 s.
- Combo : 5-6 petites frappes avec intervalles décroissants (≈16, 9, 7, 8, 9 images),
  chaque contact marqué d'1 image de Highlight/aplat sur le personnage touché, puis
  0,5 s de saisie lente, puis coupe sur flash.
- Je ne saurais PAS refaire à l'identique les cartes encre dessinées (hors
  animation de rig) ni savoir si l'aplat rouge vise l'attaquant ou la victime selon
  une logique (les deux arrivent).

---------------------------------------------------------------------------------

## 2. Rewind Clock (3ae71567, .mov 10 s)

### Découpage (vu)

| Temps | Ce qui se passe | Corps | Caméra / effets |
|---|---|---|---|
| 0,0-0,47 | sol qui se soulève ; victime projetée très haut (0,4) | attaquant (noir) au centre, immobile | caméra de jeu |
| 0,53-0,60 | carte orange/noire puis pilier blanc | | |
| 0,67-1,53 | étoiles/éclats ; la victime retombe en tournoyant lentement (1,0-1,5) | attaquant reste planté | |
| 1,67-2,07 | grosse explosion plein écran | | |
| 2,13-2,60 | l'attaquant apparaît dans les débris, garde | | |
| 2,67-3,73 | ANNEAU D'HORLOGE au sol : l'aiguille saute d'une direction à l'autre (pas une rotation régulière : haut, haut-droite, bas-droite, bas, gauche, haut-gauche, droite…) ; l'horloge s'aplatit au sol à la fin | attaquant presque caché derrière | ≈1 s |
| 3,80-4,07 | l'attaquant COURT vers la caméra, traînée-aiguille orange derrière lui | course | caméra fixe |
| 4,10 | COUPE : angle opposé, plus proche, immeubles derrière | | |
| 4,13 | carte : triangles blancs | | 1 image |
| 4,20-4,30 | attaquant noir à reflets blancs, bras qui part en grand arc | ARMÉ puis lancé en 3-4 images | |
| 4,33-4,53 | 7 images de cartes : blanc, arc-en-ciel glitch, radial N/B, blanc | | |
| 4,57-4,77 | flou, attaquant en gros plan, bras tendu | | |
| 4,80-4,97 | MONDE BLANC : l'attaquant seul flotte, poing lumineux | tenu | |
| 4,967-5,03 | la victime ENTRE par la droite et se colle à lui en 2 images (aspirée, « rembobinée ») | | |
| 5,03-7,00 | TABLEAU FIGÉ : les deux corps en contact, quasi immobiles ; seules les lueurs au poing changent ; la caméra pousse lentement et glisse (la paire grossit ≈20 % et se décale) | tenue ~2 s | mesuré : diff 1-3 |
| 7,03-7,10 | gros plan sur le bras jaune de la victime | | |
| 7,13-8,50 | cartes « radio » crâne : cyan, rouge, N/B, bleu, VERT-NÉGATIF tenu (7,33-7,47 ; 7,93-8,13 ; 8,27-8,40), blancs de 2 images intercalés | | |
| 8,53-8,77 | retour caméra de jeu, flash, explosion | | |
| 8,8-9,8 | rayon au sol, débris, victime au sol, attaquant debout | | |

Mesuré (`energie.py`, 4,9-7,2 s) : différence image à image entre 0,8 et 3,6 de
5,1 à 6,9 s (quasi nulle), puis 64 -> 194 à 7,03-7,17 (coupe vers les cartes).

### Ce qui est fort
- **Le temps arrêté est un choix d'animation, pas d'effet** : 2 s pendant lesquelles
  les corps ne bougent plus, et c'est la CAMÉRA qui fait vivre la tenue (poussée +
  glissement lents). Le spectateur sent « le temps suspendu » parce que tout
  s'arrête sauf l'œil (déduit).
- **La victime aspirée en 2 images** vers le poing immobile : l'inverse d'un coup
  (c'est la cible qui vient). Idée forte pour une technique « horloge » (vu).
- **Le signe visuel de la technique** (l'horloge, 1 s) arrive AVANT le coup, comme
  une annonce (vu ; déjà dans l'ancienne note).
- **Aiguille qui saute** au lieu de tourner : chaque position tenue 2-4 images, ça
  lit comme un tic-tac nerveux (vu).

### Ce qui nuance l'ancienne note
L'ancienne note disait « pendant 2 s de coups ». Je ne vois pas de coups : je vois
un contact FIGÉ, et seulement des lueurs qui changent au poing. Statut : vu + mesuré.

### En R6 (déduit)
- Poser la pose de contact (bras tendu dans la poitrine de la victime, buste en
  avant) et la TENIR 60 images ; animer la caméra (translation 1-2 studs + FOV qui
  se resserre) sur ces 60 images ; seule une petite pulsation de lumière au poing.
- Entrée de la victime : son HumanoidRootPart passe de ~10 studs à 0 en 2 images,
  corps déjà dans sa pose de réception.

---------------------------------------------------------------------------------

## 3. Stagnant Rage (4fb4f776, .mov 9,8 s) — deux variantes, caméra de jeu

### Découpage (vu)

Variante proche (0-4,2 s) :

| Temps | Corps | Effets |
|---|---|---|
| 0,00-0,07 | l'attaquant (poings enflammés) saisit la victime au sol | |
| 0,10-0,17 | — | explosion plein écran 3 images |
| 0,20-0,60 | victime projetée en l'air, tourne sur elle-même, redescend ; l'attaquant reste en bas, BRAS LEVÉ (poing en l'air), tenu ≈6 images (0,57-0,77) | fumée |
| 0,77 | la victime retombe sur son poing | |
| 0,80-1,37 | l'attaquant TOURNE sur lui-même (toupie) avec des anneaux de feu ; la victime tourne autour de lui, entraînée | anneaux rouges/blancs qui suivent la rotation |
| 1,37-1,40 | victime relancée vers le haut ; dôme blanc | |
| 1,47-4,2 | victime au sol, attaquant immobile dans la fumée | fumée ~2,5 s |

Variante lointaine (4,2-9,8 s) :

| Temps | Corps | Effets |
|---|---|---|
| 4,30-4,40 | l'attaquant devient BLANC (aplat) 3 images | charge |
| 4,43-4,67 | il se RAMASSE très bas, presque couché au sol, 7 images | poussière en cercle |
| 4,70-4,77 | détente : il jaillit en l'air vers l'avant | pointes blanches au sol |
| 4,80-5,10 | vol en arc vers la victime (≈10 images) | poussière |
| 5,13-5,23 | il s'écrase SUR la victime, ramassé | |
| 5,27 | | explosion plein écran |
| 5,4-6,6 | champ de feu, attaquant au centre | |
| 6,67-6,87 | l'attaquant devient NOIR puis ROUGE (aplats) avec un arc lumineux | coup suivant |
| 7,67-8,13 | idem noir/rouge, flammèches | |
| 8,40 | | éclat étoilé |
| 8,53-8,90 | l'attaquant FILE au ras du sol vers l'avant (rayon/traînée), la caméra part derrière lui | |
| 9,0-9,8 | caméra de dos, l'attaquant debout dans les braises | |

### Ce qui est fort
- **Charge = compression extrême, lisible même minuscule** : à cette échelle (le
  perso fait quelques dizaines de pixels), la seule chose qui se lit est la
  SILHOUETTE : ramassé presque plat au sol (7 images) puis étiré en l'air. Le
  contraste de hauteur de silhouette porte l'anticipation (vu).
- **Aplats de couleur sur le corps** (blanc, noir, rouge) comme états : charge,
  coup (vu).
- **Toupie** : l'attaquant tourne et la victime est entraînée autour : un seul
  mouvement de corps lu grâce aux anneaux qui en marquent la trajectoire (vu).
- Même technique, deux mises en scène selon la distance (lu, confirmé vu).

### En R6 (déduit)
- Ramassé : Torso très penché en avant (proche horizontal), hanches basses
  (RootJoint descendu), genoux fléchis au maximum, bras le long du corps. Tenir
  6-8 images. Détente en 2-3 images vers une pose étirée (bras en arrière, jambes
  tendues), trajectoire d'arc de la racine sur ~10 images.
- Je ne saurais pas dire la pose exacte des bras pendant la toupie : trop petit
  et masqué par les anneaux.

---------------------------------------------------------------------------------

## 4. Black Hole Ability (01f4b1d2, .mov 14,2 s) — le clip où le corps se voit le mieux

### Découpage (vu + mesuré)

| Temps | Corps | Caméra | Énergie (mesuré) |
|---|---|---|---|
| 0,0-2,6 | debout, idle, quelques rotations (vidéo mise en pause/reprise par l'UI) | lointaine, plongée | — |
| 2,633 | — | COUPE vers plan moyen proche (1 image) | 48 |
| 2,67-3,07 | ENROULEMENT : le buste tourne vers sa gauche et se penche, la tête plonge, les deux bras partent en haut/arrière, genoux fléchis | caméra fixe | 5-10 (lent, régulier) |
| 3,10-3,40 | TENUE de l'enroulement ≈10 images, tête collée au bras, épaules en boule | fixe | 4-25 (tremblement qui monte avant le départ) |
| 3,43-3,60 | DÉTENTE : bras jetés vers le haut, corps qui s'étire, anneau de poussière au sol, jambes qui SORTENT DU CADRE par le haut | fixe : le perso quitte le cadre | 42-56 |
| 3,63-3,70 | ciel vide avec débris (le perso est absent 3 images) | contre-plongée | 15-22 |
| 3,73-4,10 | il ENTRE par le bas du cadre : bras levés en V, bouche ouverte, jambes groupées | contre-plongée | 25-40 puis 6 |
| 4,13-4,17 | plus petit, en l'air | recul | 31 |
| 4,20-4,23 | — | SNAP ZOOM sur le torse (cravate plein cadre) en 2 images | 103 |
| 4,27-4,40 | BRAS GRANDS OUVERTS, recul de la caméra | 35-22 |
| 4,43-4,93 | tenue bras ouverts en l'air (flottement) ≈15 images | lente | 8-15 |
| 4,97-5,07 | bras ramenés : mains JOINTES devant la poitrine en 3 images, tête qui baisse | | 18-26 |
| 5,10-5,50 | TENUE mains jointes, en boule dans les airs ≈12 images | fixe | 2-12 (le plus immobile du clip) |
| 5,53-5,77 | cartes postérisées N/B (8 images), étoiles | | 88-191 |
| 5,77-6,17 | POSE EN CROIX (bras à l'horizontale), tête droite, tenue ≈12 images | fixe | 9-26 |
| 6,20-6,27 | — | recul violent : le perso rapetisse en 3 images | 34-39 |
| 6,3-8,1 | débris qui montent et tournent au ciel | panoramique | — |
| 8,2-8,5 | cartes N/B | | |
| 8,6-11,5 | disque doré du trou noir | | |
| 11,7-12,7 | fondu au noir 1 s | | |
| 12,8-13,4 | retour : debout, calme | | |

### Ce qui est fort
- **Alternance compression / extension, 4 fois** : enroulé (3,1) -> étiré en V (3,8)
  -> bras ouverts (4,3) -> mains jointes en boule (5,1) -> croix (5,8). Chaque pose
  est l'OPPOSÉ de la précédente en silhouette (ouverte/fermée). Vu.
- **Changement de pose en 2-3 images, tenue en 10-15 images** (mesuré : pics
  d'énergie courts, plateaux bas). Le rapport est d'environ 1 pour 4 à 1 pour 5.
- **Le perso sort du cadre** au décollage au lieu que la caméra le suive : la
  vitesse est rendue par l'absence (3 images de ciel vide) puis sa réapparition
  par le bas (vu).
- **Le tremblement monte pendant la tenue d'enroulement** (énergie 4 -> 25 de
  3,1 à 3,4 s) : la tenue n'est pas morte, elle « charge » (mesuré ; interprétation
  déduite).
- **L'enroulement est LENT** (0,4 s, régulier) et la détente brutale : anticipation
  lisible = lente, action = rapide (vu + mesuré).
- Caméra : chaque mouvement de caméra est lui aussi un snap (2-3 images) suivi
  d'une tenue ; la caméra copie le rythme du corps.

### Ce qui complète l'ancienne note
L'ancienne note (« se ramasse en regardant en haut ») : je vois plutôt la tête qui
PLONGE vers le bas et le côté pendant l'enroulement (3,0-3,4), et c'est au
décollage qu'elle se relève. À vérifier par un autre regard ; statut vu, confiance
moyenne (angle 3/4 arrière, visage partiellement caché).

### En R6 (déduit ; valeurs de départ à essayer)
- Enroulement 12 images (ease-in-out doux) : Torso lacet ≈ 30-45° vers la gauche et
  penché en avant, Neck penché vers le bas, deux bras levés vers l'arrière/haut
  (épaules très tournées), hanches basses. Tenir 10 images en ajoutant un
  micro-tremblement croissant (bruit de 0,5 -> 2° sur le Torso).
- Détente 3 images vers : Torso vertical, bras en V au-dessus de la tête, jambes
  tendues ; la racine monte hors cadre (caméra fixe).
- Puis séquence de poses tenues 12-15 images reliées par des transitions de
  3 images : bras ouverts -> mains jointes (épaules vers l'avant, coudes… R6 n'a
  pas de coude : bras entiers ramenés en croix devant le torse) -> croix.

---------------------------------------------------------------------------------

## 5. IMPACT HAVEN (eba5ed69, .mp4 11,4 s) — 19 impacts sur la musique

### Découpage (vu + mesuré)

Cartes détectées par luminance (mesuré, `ih/energie.txt`) : une image NOIRE avec la
silhouette BLANCHE des deux corps et des lignes de vitesse, suivie d'une image
BLANCHE (parfois 2-3), à : 2,40 / 2,87 / 3,17 / 3,47 (blanc 2 i) / 3,87 / 4,37 /
4,87 / 5,20 / 5,57 / 5,83 / 6,37 / 6,87 / 7,20 / 7,53 / 7,83 / 8,33 / 8,83 / 9,17 /
9,50 s = 19 impacts (+ un blanc de 3 images à 1,87-1,93 sur la coupe d'ouverture).

Intervalles (s) : 0,47 0,30 0,30 0,40 0,50 0,50 0,33 0,37 0,27 0,53 0,50 0,33 0,33
0,30 0,50 0,50 0,33 0,33 : presque tout vaut 10 ou 15 images (à 30 i/s).

Attaques du son (passe-haut 2 kHz, mesuré) : 2,30 2,80 3,26 3,78 4,30 4,80 5,32 5,80
6,30 6,80 7,32 7,81… : un temps tous les 0,50 s (≈120 BPM). Les impacts « forts »
(2,40 / 2,87 / 3,87 / 4,37 / 4,87 / 5,83 / 6,37 / 6,87 / 7,83 / 8,33 / 8,83) tombent
≈0,07-0,1 s APRÈS chaque temps ; les autres (3,17 / 5,20 / 5,57 / 7,20 / 7,53 / 9,17)
tombent entre deux temps. Déduit : le monteur cale les impacts sur la pulsation de
la musique (« Can't Hold Me Down », titre visible). Le décalage de 2-3 images peut
venir de l'enregistrement d'écran : je ne le prends pas pour une intention.

Corps (vu, planches `ih/a30_01..09`) :
- 1,00-1,83 : ouverture sur le perso de dos puis de face assis, titre, gros plan
  poitrine -> blanc.
- Entre deux cartes, chaque plan montre UNE pose d'après-coup tenue 9-14 images,
  avec un léger glissement (victime qui recule de quelques pixels, caméra qui
  dérive). Ex. 6,43-6,83 : victime pliée, figée en l'air, glisse à peine.
- La pose change ENTIÈREMENT derrière la carte : aucun trajet visible. On passe
  de « victime pliée en avant » à « victime à l'envers au-dessus » en 2 images
  (noir + blanc).
- Poses vues : victime à l'envers (tête en bas, 3,93-4,17), victime pliée en V
  sur le poing, attaquant en fente basse au sol (5,27-5,53), attaquant qui monte
  en uppercut sous la victime (7,90-8,30), victime couchée à l'horizontale au ras
  du sol (5,30-5,80), les deux corps enchevêtrés.
- Caméra : TOUJOURS basse (horizon dans le tiers inférieur, ciel bleu dominant) :
  les silhouettes se découpent sur le ciel uni. L'angle change à chaque carte.
- 9,50-9,77 : dernière carte puis gros plan déformé (épaule / capuche) qui glisse,
  puis noir.

### Ce qui est fort
- **La pose est l'image clé, la carte est la transition** : l'animateur remplace
  l'inbetween par 2 images graphiques. Le cerveau du spectateur « voit » la
  violence du passage parce qu'il ne peut pas le voir (déduit).
- **La carte noire garde la silhouette exacte de la pose suivante/précédente** :
  la lisibilité est gardée même pendant le flash (vu).
- **Ciel comme fond** : fond uni, contraste maximal, poses lisibles en silhouette (vu).
- **Musique = partition du montage** (mesuré ci-dessus).

### Nuance de l'ancienne note
« Cartes blanches/noires de 2 f » : précisément, 1 image noire (silhouette blanche)
+ 1 image blanche dans 17 cas sur 19 ; 2-3 blancs pour la coupe d'ouverture (1,87)
et 3,47. Mesuré.

### En R6 (déduit)
- Animer UNIQUEMENT des poses d'après-coup (une par impact), chacune tenue 10 ou
  15 images avec une petite translation (0,2-0,5 stud) pour ne pas figer.
- Transition = 1 image de silhouette (personnages en Highlight blanc, fond noir,
  lignes radiales) + 1 image blanche ; pose et caméra changent sous ces 2 images.
- Caméra basse (hauteur ≈ genoux), légère contre-plongée, fond de ciel.
- Je ne saurais pas encore dire comment l'auteur choisit l'ordre des poses (quelle
  logique de combat) : je vois une alternance haut/bas/à-l'envers, rien de plus.

---------------------------------------------------------------------------------

## 6. Vidéo Gemini — invocation d'un soleil (73cc1fb0, .mp4 10 s, 24 i/s, IA)

Attention : vidéo GÉNÉRÉE PAR IA (lu, catalogue). Ce n'est pas un vrai jeu ; ça montre
ce qu'un modèle croit être une ulti Roblox. Utile pour la mise en scène, à prendre
avec prudence pour le corps (bras sans coude, déformations possibles).

| Temps | Corps | Caméra / effets |
|---|---|---|
| 0,0-0,08 | perso vu de dos au premier plan, l'adversaire au fond | plan épaule |
| 0,17-0,58 | adversaire debout, bras qui remontent, aura blanche | plan moyen |
| 0,67-1,25 | poings serrés devant le ventre (« il pousse ») | la caméra avance |
| 1,33-3,08 | visage en gros plan, sourire, aura | ≈1,75 s tenu |
| 3,17-3,50 | BOUCHE GRANDE OUVERTE (cri) | lignes noires de vitesse en coin |
| 3,58-4,38 | carte : silhouette blanche sur noir, aura en éclairs, 0,8 s | |
| 4,42-4,63 | retour plan moyen, bras le long du corps, cri | |
| 4,625-4,83 | LE BRAS DROIT MONTE D'ABORD, le gauche SUIT ≈3 images plus tard ; les deux arrivent au-dessus de la tête vers 4,83 | le soleil apparaît quand les mains arrivent en haut (4,75-4,83) |
| 4,92-6,33 | contre-plongée, soleil au-dessus des mains, tenu ≈1,4 s | |
| 6,33-6,50 | bras qui redescendent : le soleil est lancé | |
| 6,58-8,33 | chute du soleil, impacts au sol | |
| 8,42-8,58 | éclat blanc | |
| 8,67-9,92 | plan large DE DOS : explosion au loin | |

### Ce qui est intéressant (vu)
- **Décalage des deux bras** (≈3 images) : même une IA le fait ; ça casse la symétrie
  et donne l'impression d'un effort (déduit).
- **L'effet naît au sommet du geste** (le soleil apparaît quand les mains finissent
  de monter) : synchronisation effet/pose.
- **Le visage porte la charge** (1,75 s de gros plan avant le cri) ; puis la carte
  silhouette.
- **Plan final de dos** : on regarde la conséquence avec lui.

### En R6 (déduit)
Montée des bras : bras droit de « le long du corps » à « au-dessus de la tête » en
6 images (ease-out), bras gauche identique décalé de 3 images ; Torso qui se cambre
légèrement en arrière à l'arrivée ; spawn de l'effet sur l'image où le bras gauche
arrive.

---------------------------------------------------------------------------------

## 7. VFX SHOWCASE : Thunder Dragon (pXqH8vOZ8X8, .mp4 18 s, 30 i/s, sans son)

| Temps | Ce qui se passe |
|---|---|
| 0,0-0,63 | perso minuscule, immobile, sol vide (mesuré : diff 0 jusqu'à 0,633) |
| 0,667 | des POINTES noires jaillissent D'UN COUP à pleine hauteur (1 image, aucune montée) avec halo violet ; anneau blanc au sol |
| 0,70-0,80 | l'anneau blanc s'élargit en 3 images ; les pointes s'effondrent en rochers ; sol cassé en couronne |
| 0,80-1,45 | « dragon » d'éclairs violets qui s'enroule et s'éloigne en haut à droite (≈20 images) |
| 1,45-3,60 | éclairs isolés, fumée, un bloc tombe (2,83-3,0) ; le perso ne bouge pas |
| 3,73 | 1 image noire (inversion) |
| 3,80-3,87 | 2 images gris/blanc, pilier sombre |
| 3,93-4,27 | pilier qui change de couleur toutes les 2 images : jaune, jaune, vert-jaune, vert, turquoise, bleu |
| 4,27-5,13 | pilier bleu sombre, la caméra avance vers le perso, bords sombres qui se resserrent |
| 5,20-6,33 | gros plan sur le perso (de dos/face ?, cheveux bleus), presque immobile, petite variation de bras vers 5,27-5,40 |
| 6,33-6,47 | recul rapide (4 images), le perso rapetisse |
| 6,5-10,2 | plan large calme, débris |
| 10,5-17,8 | la même séquence rejouée (boucle de vitrine) |

### Ce qui est intéressant
- Ce clip n'enseigne presque rien sur l'animation du corps : le perso sert
  d'échelle. C'est l'EFFET qui a une anticipation nulle (0 -> pleine hauteur en
  1 image) puis une longue retombée (vu + mesuré). À l'inverse d'un geste
  corporel, l'effet ici « frappe » sans préparer et s'étale après.
- Couleur qui change à chaque 2 images = un pilier « vivant » sans bouger sa forme (vu).
- La caméra fait le travail du rythme (avance lente / recul en 4 images) (vu).

### En R6 (déduit)
Pour une technique qui sort du sol : le personnage peut rester immobile si la
caméra et l'effet portent l'événement ; mais la vitrine montre aussi la limite :
sans geste du perso, on ne sait pas QUI fait quoi (déduit).

---------------------------------------------------------------------------------

## 8. Grands enseignements (croisés entre les clips)

Ce sont des régularités observées dans CES 7 clips, pas des lois.

1. **Snap puis tenue.** Quand le corps change de pose pour un moment fort, il le
   fait en 2-3 images puis tient 10-15 images (Black Hole, mesuré ; IMPACT HAVEN
   9-14 images ; Black Flash tenue de contact ≈8 images, bras tendu ≈13 images).
   L'exception est l'ANTICIPATION, qui est lente et régulière (enroulement Black
   Hole 12 images ; ramassé Stagnant Rage 7 images tenu).
2. **Le trajet du coup est souvent caché, pas animé.** IMPACT HAVEN (carte
   noir+blanc), Black Flash cinématique (cartes puis bras déjà tendu), Rewind
   Clock (cartes glitch pendant la frappe 4,33-4,53). L'animateur donne la pose de
   départ et la pose d'arrivée, et remplace l'entre-deux par 1-7 images graphiques.
   Conséquence pour nous : dépenser l'effort sur les deux poses et la tenue,
   pas sur l'interpolation du bras (déduit).
3. **Une tenue n'est jamais figée tout court.** Elle vit par : la caméra (Rewind
   Clock 2 s de pose figée + poussée lente ; Black Flash plan final 1,5 s en
   décélération mesurée 33 -> 4), un tremblement qui monte (Black Hole 3,1-3,4),
   un petit glissement (IMPACT HAVEN).
4. **Le rythme a un creux avant le pic.** Black Flash : coups qui accélèrent puis
   0,5 s de saisie lente avant le flash. Black Hole : 2,6 s d'idle. Thunder
   Dragon : 0,63 s de rien. Gemini : 1,75 s de visage calme avant le cri.
5. **Opposer les silhouettes successives.** Black Hole : fermé/ouvert quatre fois.
   Stagnant Rage : plat au sol / étiré en l'air. IMPACT HAVEN : victime à
   l'endroit / à l'envers / couchée.
6. **Le corps comme support de couleur d'1 image.** Aplat rouge (Black Flash), blanc,
   noir, rouge (Stagnant Rage), silhouette blanche (IMPACT HAVEN, Gemini) : le
   contact se « signe » sur le corps lui-même.
7. **Caméra basse et fond uni** pour lire la pose (IMPACT HAVEN ciel ; Black Flash
   plan final au ras du sol).
8. **Montrer la conséquence par l'échelle** plutôt que par l'animation de la
   victime : Black Flash (poing devant, victime minuscule au fond), Gemini
   (plan large de dos sur l'explosion), Stagnant Rage (perso minuscule dans
   l'explosion).
9. **Le perso peut sortir du cadre** (Black Hole 3,57-3,70) : la caméra ne suit pas
   toujours ; l'absence est une vitesse.
10. **Synchronisation au son** : IMPACT HAVEN cale ses impacts sur un temps de
    0,5 s (mesuré). Les autres clips ont une musique de fond trop dense pour
    conclure (cf. `ECOUTE_REFS_SFX_2026-09-25.md`).

## 9. Ce que ça m'apprend pour corriger/suggérer (sans viser un coup précis)

- Quand une de nos animations « ne passe pas », regarder d'abord le RAPPORT entre
  temps de transition et temps de tenue, et si le trajet est montré en entier.
  Dans ces clips, les moments forts ont très peu d'images de trajet et beaucoup
  d'images de tenue (suggestion, déduit).
- Vérifier que deux poses consécutives s'opposent en silhouette (fermé/ouvert,
  bas/haut).
- Pour une tenue longue, décider QUI la fait vivre (caméra, tremblement,
  glissement).
- Pour une grosse conséquence, envisager un plan où l'attaquant est au premier
  plan et la conséquence loin derrière (Black Flash).

## 10. Limites honnêtes

- Les clips sont des enregistrements d'écran à fréquence variable : mes « images »
  sont un rééchantillonnage à 30 i/s ; ±1 image d'incertitude sur tous les temps.
- Je n'ai pas pu mesurer d'angles d'articulation : les persos sont petits,
  masqués par les effets, vus sous des angles variables. Toutes les valeurs R6 de
  ce fichier sont des points de départ à essayer, pas des mesures.
- Black Flash : je ne sais pas si l'aplat rouge vise la victime ou l'attaquant de
  façon systématique (les deux cas vus).
- Thunder Dragon : je n'ai pas identifié si le gros plan montre le perso de face
  ou de dos.
- IMPACT HAVEN : l'avance/retard image/son de 2-3 images peut être un artefact de
  la capture.

---------------------------------------------------------------------------------

## Vérification adverse

Vérificateur adverse, 2026-09-26. Je suis retourné moi-même aux vidéos. J'ai fait mes propres planches à 30 i/s (et à 60 i/s natif pour Black Hole), dans
`/tmp/claude-0/-home-user-Jeux/4796ac9e-8e41-51f7-91c4-7b92a6a187d0/scratchpad/c4/frames/verif_C2_clips_jeux/`
(bh_a/bh_b/bh_hold60/bh_coil_cmp, ih_a/ih_b, bf_jeu/bf_cine/bf_fin, rc_a/rc_b, sr_a, td_a, gm_a).
J'ai relancé energie.py, refait la détection des cartes d'IMPACT HAVEN par luminance, et détecté les attaques du son en trois bandes (complet, passe-haut 2 kHz, passe-bas 150 Hz).
Je n'ai rien modifié dans le dépôt.

Remarque de méthode : les chiffres d'énergie ne sont reproductibles qu'à peu près. Ils changent selon le point de départ de la lecture. Par exemple, pour le pic du snap zoom de Black Hole à 4,20 s, j'obtiens 79 et le lecteur 103. Pour la détente à 3,43-3,63 s, j'obtiens 22-46 et le lecteur 42-56. Les tendances restent les mêmes, mais les valeurs exactes ne doivent pas servir de référence. À 60 i/s natif, Black Hole montre des images en double par paires. Le jeu tourne donc à environ 30 i/s effectifs, et « 1 image » veut bien dire 1/30 s.

| # | Apprentissage | Verdict | Ce que j'ai regardé | Correction |
|---|---|---|---|---|
| 1 | Snap 2-3 images puis tenue 10-15 | nuancé | bh_a, bh_b, energie 2,5-6,5 s | Vrai pour : bras ouverts -> mains jointes (4,967 -> 5,067, 3 images) ; tenue mains jointes (5,10-5,50, 12 images) ; croix (5,80-6,17, 11 images). La détente complète (du ramassé jusqu'à la sortie du cadre) dure 3,43-3,60 s, soit 6 images, pas 2-3. L'ouverture des bras après le snap zoom dure 4,27-4,43 s, soit 5 images. Les « tenues » bougent aussi : pendant la tenue bras ouverts (4,47-4,93), les bras dérivent et descendent lentement. |
| 2 | Anticipation lente, puis tenue avec un tremblement qui monte | nuancé (la moitié « tremblement » est réfutée) | bh_hold60 (60 i/s natif, 3,05-3,47 s), bh_coil_cmp | L'enroulement de 2,67 à 3,07 s est bien lent et régulier (13 images). La vraie tenue ne dure que 3,07-3,20 s (4 images). De 3,20 à 3,40 s, ce n'est pas un tremblement : les bras REDESCENDENT sur le côté en un balayage continu de 6 images, et le buste continue de tourner. C'est une contre-anticipation (vers le bas avant le jet vers le haut). La recette R6 « micro-tremblement croissant, bruit de 0,5 à 2° » ne correspond pas à ce qu'on voit. À remplacer par : tenue de 4 images, puis bras qui retombent en 6 images, puis jet. Autre point : la caméra n'est pas fixe pendant l'enroulement. Elle pousse lentement vers le perso (la tête passe d'environ 55 à environ 75 px de large entre 2,67 et 3,37 s). |
| 3 | Le trajet du coup est caché derrière des images graphiques | confirmé | bf_cine (3,40-3,77), ih_a, ih_b, rc_a (4,30-4,57), bh_b_02 | IMPACT HAVEN : noir à 2,40, blanc à 2,433, nouvelle pose à 2,467. Black Flash : cartes de 3,40 à 3,733, bras déjà tendu à 3,767. Rewind Clock : cartes de 4,333 à 4,533. À ajouter : Black Hole fait pareil, et le lecteur ne l'a pas relevé. Le passage des mains jointes à la croix se fait SOUS les cartes postérisées (entre 5,567 et 5,600, la pose change en 1 image). Limite de la règle : ce qui est caché, c'est le trajet du CONTACT. L'anticipation du coup suivant reste visible (voir les oublis). |
| 4 | La tenue longue vit par la caméra (Rewind Clock : paire +20 %) | nuancé | rc_b (5,0-6,67 s, 1 image sur 10), energie 4,9-7,2 | Corps figés et diff de 0,7 à 2,9 de 5,1 à 6,9 s : confirmé. Mais la paire grossit d'environ 35 % (hauteur d'environ 140 à environ 190-200 px, largeur d'environ 180 à environ 245 px, entre 5,0 et 6,67 s), pas de 20 %. Black Flash (plan final) : c'est aussi une poussée lente vers le poing (le bras grossit de 5,0 à 6,17 s). Les taches de sang sur la manche changent pendant la tenue : c'est une deuxième source de vie. |
| 5 | Black Flash : poing au premier plan, victime minuscule au fond | confirmé | bf_fin (4,67-6,17 s à 6 i/s), bf/f5_5.png | Main nue et manche blanche ensanglantée au premier plan, cheveux noirs de l'attaquant derrière, victime (jaune, bleu, vert) toute petite au fond. La lueur rouge près de la victime est nette au début (5,0-5,5 s), puis s'éteint. |
| 6 | Rythme qui accélère, puis creux avant le pic | nuancé | bf_jeu (0-2,45 s, toutes les images) | Chaque coup montre 1 image d'aplat rouge, puis le disque noir 1 image plus tard. Les disques tombent à ≈0,10 / 0,60 / 0,90 / 1,133 / 1,40 / 1,733 s. Intervalles : 0,50 / 0,30 / 0,23 / 0,27 / 0,33 s. Ce n'est PAS une accélération continue : il y a un long écart, puis un rythme à peu près régulier de 7 à 10 images, qui se rallonge même un peu à la fin. Le creux de 1,87 à 2,33 s (saisie lente sans effet), puis le flash à 2,367 s : confirmé. Thunder Dragon, diff 0 jusqu'à 0,633 s : confirmé. |
| 7 | Le perso sort du cadre au décollage | confirmé | bh_a_02 | Jambes qui sortent par le haut à 3,567-3,60 s (il ne reste que les pieds à 3,60). Ciel vide avec débris à 3,633, 3,667 et 3,70 (3 images). Il rentre par le bas à 3,733 s. Précision : 3,633 s est une COUPE vers la contre-plongée, pas un mouvement de caméra. Le lecteur l'indique dans son tableau, mais pas dans le titre de l'apprentissage. |
| 8 | IMPACT HAVEN : 19 impacts, noir avec silhouette puis blanc | confirmé, avec deux précisions | Luminance recalculée sur tout le clip, ih_a, ih_b, attaques du son en 3 bandes | 19 événements, et le détail colle. Les deux exceptions sont 3,467 (2 blancs sans noir) et 9,167 (noir sans blanc) ; le lecteur cite 1,87 comme exception, mais 1,87 est avant la série. Intervalles en images : 14, 9, 9, 12, 15, 15, 10, 11, 8, 16, 15, 10, 10, 9, 15, 15, 10, 10. Donc « 10 ou 15 » à 1 image près dans 16 cas sur 18. Pulsation de 0,50 s en passe-haut 2 kHz (2,30, 2,80, 3,80, 4,30, 4,80, 5,79, 6,30…) : confirmée. Précision 1 : la silhouette n'est pas toujours celle des « deux corps » (6,367, 6,867 et 7,20 : un trait + une seule forme). Précision 2 : en passe-bas 150 Hz, les attaques (2,37, 2,85, 3,21, 3,49, 5,2, 5,58, 6,37, 6,9, 7,58, 8,83, 9,2) tombent sur les cartes à 1 image près, y compris celles entre deux temps. Chaque carte a donc son son d'impact synchronisé. L'image et le son sont alignés, et le retard par rapport aux temps de la musique ne vient donc PAS de l'enregistrement d'écran. |

Vérifications rapides en plus (hors des 8) :
- Rewind Clock, la victime entre en 2 images : confirmé (bord droit à 4,967, contact à 5,033). Elle entre DÉJÀ dans sa pose finale, sans mouvement de membres.
- Aplat d'1 image : confirmé pour Black Flash (toujours 1 image AVANT le disque) et pour Stagnant Rage (blanc de 4,333 à 4,40 s, 3 images).
- Thunder Dragon, pointes à pleine hauteur en 1 image (0,633 -> 0,667 s) : confirmé.
- Gemini : nuancé. Un petit soleil apparaît dès 4,75 s, alors que le premier bras n'est qu'à hauteur d'épaule. Le soleil grossit pendant que la CAMÉRA BASCULE vers le haut (4,79-4,92 s). Le second bras semble rejoindre le premier plutôt vers 4,875-4,917 s, soit environ 5-6 images à 24 i/s, pas 3. C'est une vidéo générée par IA : illisible à 1 image près.

### Oublis importants
1. **IMPACT HAVEN montre l'anticipation, il ne cache que le contact.** Entre deux cartes, l'attaquant s'anime vraiment : de 2,47 à 2,83 s, il s'abaisse, puis se relève vers le coup suivant. Certains plans ne montrent que la victime qui dérive seule, sans l'attaquant dans le cadre (6,43-6,83 et 6,93-7,17 s). La règle « pose d'après-coup tenue » est donc incomplète : tenue de la victime, anticipation visible de l'attaquant, contact caché.
2. **Black Hole : contre-anticipation bras en bas (3,20-3,40 s)** avant le jet vers le haut, prise à tort pour un tremblement (voir n° 2).
3. **Black Hole : la transition vers la croix est cachée sous les cartes postérisées** (5,567 -> 5,600 s). C'est le même procédé que dans IMPACT HAVEN, dans le clip que le lecteur présente comme « tout animé ».
4. **Black Flash, combo en jeu : les corps font environ 30 px de haut.** L'animation du corps n'y est presque pas lisible. Ce sont l'aplat rouge (1 image), puis le disque noir, qui rendent chaque coup lisible. L'aplat PRÉCÈDE toujours l'effet d'1 image.
5. **Caméra en mouvement là où le lecteur la dit fixe** : poussée lente pendant l'enroulement de Black Hole. Poussées dans les tenues de Rewind Clock (≈ +35 %) et de Black Flash.
6. **IMPACT HAVEN, son** : chaque carte a son impact grave synchronisé à 1 image près. C'est une donnée utile pour notre couche SFX : une carte = un son grave.
