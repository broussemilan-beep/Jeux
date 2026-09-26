# Étude de l'archive vidéo n° 1 de Milan (2026-09-25)

`9755a706-videos_archive_part1.zip` (sha1 ef7c636001f0248d) : 7 vidéos
(640x360, sans son) + 10 sous-titres de tutos (sans les vidéos). Consigne
de Milan (2026-09-25 17:36) : « dans les vidéo il y aura des choses aussi à
prendre pour l’animation etc etc pas que VFX ». Méthode : bande à pas fixe de 0,1 s (`outils/durees.py`), planche
de tenues (`planche_ref.py`), pics d'effet (`planche_vfx.py`), lecture
image par image ; vidéo de 5 min : une image / 2 s puis 1 / s sur les
passages du dragon. Transcriptions : lues en entier. Rien des œuvres
n'est versionné (mesures dérivées : `corpus/clips/durees_effets_archive1_2026-09-25.json`).

## 1. Les vidéos (animation ET VFX)

| sha1 | vidéo | durée | pic d'effet (part de l'image) | effet fort cumulé |
|---|---|---|---|---|
| 4ea7509937eace7f | Serious Punch recréé (Pew) | 16,4 s | 0,61 | 0,23 s |
| ac8fa912d32b66f1 | Stoic Bomb (TSB) | 9,5 s | 1,00 | 1,70 s (1,63 s d'un bloc) |
| c7526690f484bb3e | Slap (TSB) | 21,4 s | 0,97 | 1,97 s |
| 1f2730537200abf0 | Black Flash « sneak » de Gojo (Sorcerers BG) | 14,7 s | 1,00 | 0,73 s |
| 9a8d936b2f59ea60 | Sunrise Finisher, concept (TSB, non officiel) | 24,2 s | 0,93 | 1,37 s |
| aa476239e9f6b2bc | Thunder Dragon, vitrine VFX | 18,0 s | 0,04 * | - |
| 2dc5991318003b95 | TSB : animations et concepts abandonnés | 305,9 s | 0,93 | 17,8 s |

\* effets sombres (violet nuit) : ma mesure ne voit que le clair et le
saturé ; limite connue de `durees.py`.

### Serious Punch (Pew) : 3 s de charge, 2 images de carte, 7 s de conséquence
- 0-3,2 s : la charge, en plan moyen, caméra qui tourne lentement ; un
  anneau au sol vers 2 s. 3,3-3,5 : caméra fouettée vers le ciel (nuages). [CONTREDIT 2026-09-26 : fouetté de 2,27 à 2,60 s, voir corpus/etude_c4/C1_tsb_videos.md partie 3 point 1]
- 3,6-5,9 : caméra tout près, qui bouge avec le perso ; très gros plan du
  visage à 4,6 s ; bouffées de vapeur au poing à 5,7 s.
- **6,2-6,3 : UNE carte inversée** (fond blanc, silhouettes noires), 2 images. [CONTREDIT 2026-09-26 : carte de 5,133 à 5,333 s, 7 images, filtre posé sur la 3D, voir corpus/etude_c4/C1_tsb_videos.md partie 3 point 1]
- 6,4 : un mur de blocs de roche jaillit devant la caméra ; **coupe en
  plan très large à 6,7 s [CONTREDIT 2026-09-26 : coupe large à 5,70 s, voir corpus/etude_c4/C1_tsb_videos.md partie 3 point 1] : une ligne de roches noires fendues jusqu'à
  l'horizon, qui reste 7 s** (la tenue la plus longue : 7,4 s).
- Leçon : le coup lui-même ne dure rien ; tout le temps est donné à la
  charge (≈6 s) et à la CONSÉQUENCE (≈7 s), montrée en très large.

### Stoic Bomb (TSB) : la seule bouffée d'effet plein écran tenue 1,6 s
- 0-2,2 : saisie en caméra de jeu (plan large). [CONTREDIT 2026-09-26 : aucune saisie visible, le joueur est immobile jusqu'à 2,07 s ; mais le mannequin reste collé au joueur pendant le dôme, voir corpus/etude_c4/A2_tsb_stoic_collateral.md §6 point 3] 2,3 : coupe, vue d'en haut,
  le perso saute et jette la victime.
- 2,8-3,4 : chute : traits de feu orange et étoiles blanches en diagonale.
- 3,5-3,6 : carte noire à rayons blancs.
- **3,7-4,7 : DÔME rouge-orange vu de dessus, plein cadre** [CONTREDIT 2026-09-26 : dans le repère de l'anim, les pieds passent de 8,0 (i90) à 0,65 stud (i205), contact vers i213 ; « il flotte » suppose que la HumanoidRootPart reste au sol, ce que la vidéo ne permet pas de voir, voir corpus/etude_c4/A2_tsb_stoic_collateral.md §6 point 2], anneaux
  concentriques qui battent dedans ; 4,7-5,3 : il vire au BLANC, les deux
  silhouettes minuscules dedans.
- 5,6-5,7 : anneau rouge plat qui s'étend au sol ; 5,8 : débris (blocs) et
  fumée rouge ; 6-9,5 : la fumée se dissipe sur le cratère, plan large tenu.
- Mesure : effet de 0 à 100 % de l'écran en 1,5 s, tenu 1,6 s d'un bloc.

### Slap (TSB) : 2,7 s de gros plans désaturés, puis 2,5 s de MANGA
- 0,7-1,7 : petit anneau de particules autour du perso. 2-10 s : jeu normal
  (approche lente).
- 10,6-11,4 : grands signes rouges en surimpression + étincelles rouges.
- **13,7-16,4 : très gros plans** (visage sous le chapeau, main gantée),
  image presque en noir et blanc, fumée : la préparation, lente.
- 16,5-16,7 : traits rouges et blancs en diagonale sur noir (2-3 images).
- **16,8-19,3 : planches MANGA plein écran** : trait rouge-brun sur blanc,
  lignes de vitesse, le visage de la victime DÉFORMÉ par la gifle, 2,5 s.
- 19,4 : silhouette rouge, 19,5 : noir, puis retour 3D avec traînée rouge
  sur la victime projetée.
- Leçon : l'impact d'un ultime TSB peut être 2,5 s d'illustration 2D. Nos
  planches manga existent, mais durent bien moins et sans déformation.

### Black Flash « sneak » (Gojo) : 6 s de champ / contrechamp avant 1 image de coup
- 0,8-6,0 : alternance de GROS PLANS des deux visages, coupes toutes les
  0,3-0,8 s qui accélèrent (tension) ; poussée vers le visage de Gojo.
- 6,3-7,1 : le poing en très gros plan remplit le cadre.
- **7,2-8,1 : écran NOIR avec des traits cyan** (étincelle, anneau de
  points, spirales) ; 8,1-8,3 : fissures rouges et blanches ; **8,4-8,8 :
  BLANC total, la silhouette de la victime rapetisse au centre** (projetée
  au loin) ; 8,9-9,0 : formes inversées fissurées.
- 9,1-11,3 : Gojo de dos, immobile (tenue 2 s) ; puis gros plans de fin.
- Leçon : ~1,7 s d'abstraction plein écran (noir puis blanc) ; la
  conséquence se dit par une silhouette qui rapetisse dans le blanc.

### Sunrise Finisher (concept) : grand / minuscule, puis coupe retardée
- 1,3-1,9 : plan moyen, éclat bleu. **2,0-2,5 : plan TRÈS large, ciel de
  nuit, perso minuscule** ; **2,6-4,8 : très gros plans qui glissent sur
  le perso** (garde du sabre, chapeau, visage souriant).
- 6,3-6,9 : flash puis UN trait blanc horizontal qui traverse l'écran (la
  coupe) ; 7,0-7,8 : la victime reste figée en l'air (conséquence retardée).
- 7,9-9,2 : une bulle de verre enferme la victime, rayée de coupes
  blanches ; 9,6-12,9 : longues diagonales blanches figées dans l'image
  pendant 3 s, le perso de dos.
- 13,6-15,4 : feu orange le long de la lame, arcs orange ; **15,5-16,1 :
  explosion jaune-orange plein écran (le « lever de soleil »)** ; fumée
  noire 1,5 s ; fondu au noir.
- Leçon : contraste d'échelle (minuscule / très gros plan) ; l'effet
  arrive APRÈS le geste, en plusieurs temps.

### Thunder Dragon (vitrine) : jaillissement + pilier aux couleurs qui changent
- 0,7 : pointes sombres qui jaillissent d'un anneau blanc au sol, lueur
  violette ; 0,8-2,8 : roches et fumée, éclairs violets.
- 3,8 : écran blanc avec un pilier noir ; **3,9-4,2 : le pilier change de
  couleur à CHAQUE image** (blanc, jaune, vert, turquoise), puis pilier
  bleu nuit d'éclairs ; 5-6,3 : noir, perso éclairé par-dessous.
- Leçon : un changement de couleur par image (0,1 s) sur l'élément
  central = un « flash » coloré sans blanc.

### TSB, animations et concepts abandonnés (5 min) : la méthode des pros
- **Rig de travail coloré et lettré** : membres de couleurs différentes [CONTREDIT 2026-09-26 : couleur et lettre par FACE et par direction (F/B/L/R/U/D) sur chaque bloc, pas par membre : un outil de lecture d'orientation, voir corpus/etude_c4/C1_tsb_videos.md partie 3 point 3]
  avec F / B / L / R sur les faces et FRONT sur le torse (« Last Breath
  v4 », « Wild psychic m1s », « Crush »). Pour lire l'orientation d'un
  bloc R6 d'un coup d'œil. (Notre `tour.py` colore les membres ; pas les
  lettres.)
- **Storyboard en bonhommes bâtons** avant d'animer [CONTREDIT 2026-09-26 : ce n'est pas une planche : c'est un animatic minuté, rejoué deux fois, voir corpus/etude_c4/C1_tsb_videos.md partie 3 point 5] (« Ranged grab (not
  lock on) »).
- **Beaucoup de versions** (v1 à v4) et de concepts jetés : itérer est
  normal, même chez eux.
- **Le dragon de TSB (« Last Breath », « Martial Artist Awakening »)** :
  - v1 : un long serpent modélisé et animé dans BLENDER (corps gris à
    épines, visible dans la fenêtre Blender) ; en jeu : caméra vers le
    ciel, un anneau noir, **la tête violette plonge VERS la caméra gueule
    ouverte** (intérieur rouge, éclairs), gros plan de la gueule, puis
    **feu rouge-orange plein écran, rayons rouges sur noir, soleil orange
    avec silhouette noire**, puis plan large : une traînée de feu brûle le
    terrain, fumée, victime au sol ;
  - v2 : corps violet aplat (écailles dessinées en trait violet sombre,
    pas sculptées), ÉNORME au premier plan, qui s'enroule près du perso ;
    tête à crinière derrière le bras du perso ; le dragon trace un S dans
    le ciel ;
  - v3 : très long corps à épines qui file au RAS DU SOL comme un train
    vers la cible, sur toute la largeur de l'horizon ;
  - « Martial Artist Awakening » : tête violette gueule ouverte qui
    rugit au-dessus des persos.
- Conclusion pour nous : notre idée (serpent qui sort, s'enroule, part
  avec le coup) est la même que la leur. L'écart est dans l'EXÉCUTION :
  aplat + trait (pas de relief sculpté), taille énorme, caméra qui le
  reçoit en pleine face, et un plein écran de feu après.

## 2. Les tutos (transcriptions lues en entier)

Quatre utiles, un moyen, deux trop basiques ; **trois sans parole**
(Energy Beam HJoVSZfK2Dw, « How to make VFX Part 1 » ITd1yAZs1As, TSB
scrapped hRzXUe6okOU : seulement la musique) [CONTREDIT 2026-09-26 : attendre du contenu technique de cette vidéo n'est pas fondé : ses sous-titres ne sont que des paroles de chanson, voir corpus/etude_c4/B4_techniques_anime.md §4 point 7] : il faudra leurs VIDÉOS.

### Explosion stylisée (J8uIGox3xfU)
- Flash 0,03-0,05 s, texture PLEINE (sans trous) ; un 2e flash dessous un
  peu plus long (« un-deux »). Étoiles qui RÉTRÉCISSENT.
- Commencer par la FORME de l'explosion : grosse texture de feu au centre,
  vitesse basse, face caméra, taille qui grossit vite puis ralentit (~7,5).
- Feu autour : émis en anneau, étalement 180, **VelocityParallel** (en face
  caméra ça fait plat), vitesse haute + **drag fort** (projeté puis freiné :
  sans drag et avec une vitesse lente, « ça ne fait pas explosion »),
  vitesse aléatoire.
- Fumée NOIRE sous tout le reste, assez transparente, qui dure un peu plus
  que le feu. Les textures de feu doivent avoir du contraste interne.
- Braises : texture de point décentrée qui tourne et rétrécit, drag bas,
  vitesse basse, durée = celle de la fumée, apparition en fondu.
- Traits verticaux orientés vers l'extérieur (rotation -90) et écrasés.
- **Une lueur sur tout** (vitesse 0, face caméra, 0,8-1 s, ZOffset haut,
  transparence en V : monte vite, s'efface lentement), discrète.
- Onde : anneau discret qui grossit vite au début (taille ~15).
- Vent : VelocityPerpendicular, 180, ~5 particules, tailles TRÈS
  aléatoires, rotation -20..20 ; + 1-2 grands traits de vent.
- Un reflet d'objectif arc-en-ciel très transparent. Si l'impact ne se lit
  pas : tout agrandir.

### Pilier / explosion façon Smash (_EciT4WQizk)
- Le pilier = UN mesh (Blender) : cylindre bas poly, **normales
  inversées** (on ne voit que l'intérieur : on voit les persos à travers),
  lissé, **couleurs peintes aux sommets** (dégradés), plusieurs coques
  concentriques (blanc au centre, couleurs, contour noir 1,25x), export
  FBX (garde les couleurs), matériau **Neon** dans Roblox.
- Pré-effet 0,1 s puis effet principal décalé de 0,1 s (raccord invisible).
- Traits noirs = étoile étirée. Confettis : une planche 4x4 de couleurs,
  cadence 0, départ aléatoire = couleurs au hasard avec UN émetteur.
- ShapePartial négatif : émet HORS du volume de la forme.
- Méthode : la ref ralentie à 0,25x, identifier chaque particule, recréer.

### Slash (zlKdwujvP2A)
- Particule de slash : 0,2-0,3 s, vitesse 0,01 (VelocityPerpendicular
  disparaît à 0), 1 émise, LightInfluence 0, vitesse de rotation > 360°/s.
- **Superposer beaucoup de textures** : couleur de base, noir dessous,
  petite zone très claire, grande texture très transparente dessous
  (fausse lueur) ; ZOffset qui diffère de 0,001 suffit pour l'ordre.
- Transparence : tenir à 0 puis fondre (ajouter un point, sinon ça
  disparaît dès le début).
- **Beams en arc** : courbure = diamètre x 2/3 pour un demi-cercle, face
  caméra, 50 segments, largeur 0 devant et grande derrière, bouts coupés
  par la transparence ; beaucoup de beams superposés (Hinokami Chronicles) ;
  script : largeur qui fond vers 0 + attachment qui TOURNE ~175° (le slash
  balaie), la rotation plus rapide que la fonte.
- Petits points le long de l'arc, liés à la part, accélération dans le
  sens du slash, 0,4-0,6 s ; étoiles scintillantes (taille en bosses).
- Sol : vent (étalement 25, taille 15), onde plate linéaire, fumée émise en
  disque presque invisible ; vent en mesh Neon (taille 0→1, transparence
  jusqu'à 0,97).
- Impact : flash 0,05 s ; « si on distingue sa forme, il dure trop » ;
  un 2e qui rétrécit. Highlight vert (fill 0,6) qui va-et-vient en easing
  circulaire.
- Débris : vitesse 100, drag 7, accélération -30, émis en ANNEAU (par le
  côté), 0,5-1 s, qui rétrécissent ; feuilles.
- Toujours chercher une ref d'un artiste fort et la regarder.

### Capacités anime (Q0mXhHCW2OM)
- Boules de feu animées avec un plugin d'animation de mesh.
- Cercueil (Hado 90) : blocs d'un modèle modèle, positions d'origine
  gardées, déplacés sous le sol puis ramenés en tween COUCHE PAR COUCHE.
- Blender → Roblox : réglage d'import « géométrie du fichier » en
  CENTIMÈTRES (en studs, le mesh est coupé).
- Contraintes « damped track » de Blender pour animer une queue / un bras
  mou sans clé à la main.

### Flipbooks (TdU0A8etl1o)
- 2x2 / 4x4 / 8x8 ; OneShot / Loop / PingPong / Random ; PNG transparent.
- Feu qui tourne en fumée : taille qui grossit, transparence qui monte au
  début et à la fin, rotation -30..30, rotation lente, accélération vers
  le haut. Les flipbooks haute résolution coûtent des images/s.

### Trop basiques (1_5dpzFk3L8, 2OdX2k9jFY8)
Propriétés de base de ParticleEmitter : rien de nouveau pour le studio.

## 3. Ce qui entre dans le cerveau (apprentissages, pas règles)

1. **Temps d'un ultime** (4 vidéos) : la charge / la tension prend 3-6 s,
   le coup 1-2 images, l'abstraction plein écran 1,6-2,5 s, la
   conséquence 2-7 s en plan large. Notre Poing du Dragon comprime la
   charge (invocation 0,5 s) et la conséquence.
2. **L'abstraction plein écran est la norme des ultimes** : dôme vu de
   dessus (Stoic Bomb), manga 2D (Slap), noir puis blanc (Black Flash),
   soleil de feu (Sunrise, Last Breath). Mesuré : 1,6-2,5 s à 90-100 %.
3. **Le dragon de TSB** : même structure que notre idée, exécution
   différente : aplat + trait, énorme, vers la caméra, puis plein écran de
   feu (§1).
4. **Outils des pros à reprendre** : rig lettré (F/B/L/R), storyboard en
   bonhommes, versions nombreuses.
5. **Recettes techniques** (§2) : VelocityParallel + drag fort pour une
   explosion en volume ; lueur en V sur tout ; beams en arc qui tournent ;
   mesh à normales inversées + couleurs aux sommets + Neon ; flash « si on
   voit sa forme, il dure trop ».

## 3 bis. Deuxième envoi (`c0038a4c-videos_archive_part1.zip`)

Une seule vidéo nouvelle : le tuto flipbooks (TdU0A8etl1o, 12 min 26,
sha1 bab3237b54c3ff0c), vu à une image toutes les 5 s. Le Thunder Dragon
est un doublon ; le .srt de « VFX Part 1 » ne contient que la musique.
- Ce que l'image ajoute à la transcription : les flipbooks montrés sont
  RÉALISTES (feu orange et fumée noire volumineuse, 8x8) ; une colonne de
  feu = beaucoup de particules d'un flipbook feu→fumée qui montent ;
  changer la couleur donne un feu vert (même planche teintée).
- Place de démo de Roblox : boucles numérotées, étincelles, fumées, et un
  « ground smash » : des BLOCS rouge sombre qui volent (débris en
  flipbook) ; exemples de la communauté : feu réaliste de grande taille
  (Art Blocks), orbe bleue, sphère orange.
- Pour nous : nos flipbooks cel (feu, fumée) sont simples et peu
  nombreux ; la densité des refs vient de BEAUCOUP de particules d'un
  flipbook riche, et d'un mélange discret de réaliste sous le stylisé
  (le tuto d'explosion le dit aussi).

## 4. Ce qu'il faut encore (à demander à Milan)
- Les VIDÉOS des tutos sans parole : Energy Beam (HJoVSZfK2Dw), « How to
  make VFX Part 1 » (ITd1yAZs1As, le .srt n'a que la musique), TSB
  scrapped (hRzXUe6okOU).
- Les autres tutos de la liste (`A_TELECHARGER_VFX_2026-09-25.md`) : les
  vidéos 2, 6, 7 et 9-12 n'étaient pas dans cette partie.
