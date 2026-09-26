# C4_images_et_gout : les images fixes de Milan (dessin de pose) et son œil (goût)

Chantier 4, 2026-09-26. Lecteur : C4_images_et_gout. Tout est en lecture seule
côté dépôt ; travail et images dérivées dans
`scratchpad/c4/frames/C4_images_et_gout/`.

Statuts : **vu** (regardé moi-même, outil Read, souvent recadré/zoomé),
**mesuré** (outil : `planche_cles.py`, `geo_pose.py`, script), **lu** (texte),
**déduit** (mon interprétation). Ce sont des apprentissages, pas des règles :
« ici, l'animateur / le dessinateur fait X parce que Y ».

Ce que j'ai fait avant de regarder : `rappel.py` sur « ligne d'action »,
« silhouette pose », « raccourci poing vers le lecteur », « goût de Milan »
(--court) ; lu `ETAT.md`, `CATALOGUE_REFS.md`, fiche `UN_SEUL_COUP.md` §6-11,
`PLEIN_ECRAN.md`, `COUP_CHARGE.md` §1-2, `ETUDE_NOTES_BRUTES.md` « Images
fixes », `poses/sources/recon_anime.json` (entier), extraits de
`recon_pew_tenue`, `recon_sp2`, `recon_tsb_depart`, `pro_tsb_ultimes`,
`nous_v5_mesure`, et les 215 lignes de `milan_verbatim.jsonl` (toutes ; les
« colle » longs = textes collés, pas sa voix, je n'en ai lu que le début).
J'ai regardé chaque image AVANT de lire son étude existante quand c'était
possible, pour ne pas voir ce qu'on m'avait dit de voir.

---

## 0. Inventaire : ce que chaque image est, et QUAND il l'a envoyée

La date de fichier (mtime, UTC) recoupée avec l'heure de ses messages
(`milan_verbatim.jsonl`, n° de ligne = index + 1) dit dans quel contexte il
a envoyé chaque image. Statut : **mesuré** (dates) + **déduit** (lien au message).

| envoi (UTC) | fichiers | ce que c'est | message qui l'accompagne |
|---|---|---|---|
| 09-02 12:33 | dfdb9286 | rig R6 Blender (lettres FRONT/F/L/U, contrôles) | l.12 « utilise le rig r6 Roblox que je t'ai envoyé il est mieux » |
| 09-02 16:17 | 095c28ec (trône photo), 151f7f6d (couronne cartoon Roblox) | refs d'objets | l.20 « Voilà à quoi sa ressemble » |
| 09-03 09:11 | 41d7796b, a4a75c01 (carte d'impact 2 polarités), 7263e0c8 (page « The Creator VFX ») | refs du « genkidama » | l.28 « ça doit être à 1 main je vais t'envoyer une réf » (+ vidéo Gemini) |
| 09-03 17:01 | 33393716 (Baki), 8965d689 (OPM poing), 6dfb2f6c (hachures) | les 3 images d'un coup | l.40 « commencer comme sur l'image 1 puis impact frame image 2 et finir comme sur l'image 3 » ; l.41 « Regarde l'image 1 le perso charge son poing à son arrière droit » |
| 09-23 09:56 | 8d015f39 (soleil géant + perso minuscule), 1727676e (projectile de feu) | VFX | l.71 « je met à tes animation 3/10 par rapport au ref envoyé » |
| 09-24 18:20 | da606c23 (fiche « DEMI-DIEU S1 ») | guide de poses (généré) | l.129, 8 min après : « Non oublie demi dieu pour l'instant » |
| 09-25 06:22 | 448c613e (= 09a83af0, MHA manga), 0ca551a4 (= 37b6bf9a, Deku couleur) | coup chargé aérien | l.150 « je veux comme sur les image que je t'envoie , dans l'idée c vrmt le coup charge de saitama » |
| 09-25 14:35 | ef27f9e2 (affiche DBZ 13), 1a567c2f (Goku + dragon en spirale) | Poing du Dragon | l.173 « Mélange ça a izuku pour le poing du dragon » |
| 09-25 15:39 | 09a83af0, 37b6bf9a (renvoyées) | pose | l.174 « la pose reste celle que on a vue de izuku mélangé à celle de goku » |
| 09-25 17:38 | 930606b5, feb2d674, 68f0ad1a(=2e572cf7), d598c391, 996d38b7 (Suiryu TSB) ; fa08ccd8, 2c6dce4d, 5b6ab8d1, cab1e5b6 | dragons, VFX | l.178 « Je t'envoie des images ref , d'ailleurs dans les vidéo il y aura des choses aussi à prendre pour l'animation » |
| 09-25 17:39 | 22c8d49c, 0f85f7a1, 81f070a6, 8005ceb1, f23068ce | VFX stylisés | l.179 « c limite on dirait […] c dessiné » |
| 09-25 20:17 | **797cdcc7, 8b32a1d7, f091ee86** (non catalogués) | captures de NOTRE lecteur | l.183 « je n'aime pas ces 2 plans je les trouve trop peinture , et pas dessiné […] le 3e plan […] j'aime l'idée » |
| 09-26 08:14 | ae4823bd (Gon), d2fda413 (poing rouge), b5d718f5 (Saitama manga), 793721de (Saitama de dos) | refs « venant d'animé » | l.190 « il arme son poing le ramenant à l'arrière et en tournant son bust » |
| 09-26 08:38 | 6c517cb3, 27f110ee, 9388f709, 27b0a39e (Pew), a54fe910 (recherche Google) | clip du poing chargé | l.191 « je vais te clip pour que tu te concentre sur ça » |
| 09-26 09:04 | **5be18338** (non catalogué) + **7474b277** (= 9388f709, même sha1 979b0e88…), f3c84c00 (= 27f110ee), e0b3f877 (= 6c517cb3), d2dcc38c (= 27b0a39e) | refs remises | l.195 « Je t'ai remis les ref pour que tu vois dans aucune le bras est tendu derrière » |

Doublons vérifiés par sha1 (mesuré) : 37b6bf9a = 0ca551a4 ; 448c613e =
09a83af0 ; 2e572cf7 = 68f0ad1a ; 7474b277 = 9388f709 ; f3c84c00 = 27f110ee ;
e0b3f877 = 6c517cb3 ; d2dcc38c = 27b0a39e.

### Les 5 non catalogués (demandé : dire ce qu'ils sont)
- **797cdcc7, 8b32a1d7, f091ee86** (vu) : captures d'écran téléphone (22:15-22:16
  heure locale affichée) de NOTRE lecteur publié « Poing du Dragon », onglet
  PLEIN ÉCRAN, caméra Cinéma : 8b32a1d7 = f453 / 8,43 s, le TOURBILLON
  (taches orange-jaune-blanc à bords mous + quelques traits bruns posés
  dessus) ; f091ee86 = f513 / 9,43 s, le ROUGE (horizon noir, rayons de flammes
  orange/jaune, lignes de fuite rouges au sol) ; 797cdcc7 = f548 / 10,02 s, le
  SOLEIL (disque blanc-jaune à rayons, silhouette noire d'un ruban à pointes
  qui plonge). Déduit : ce sont les « 2 plans trop peinture » (tourbillon,
  rouge) et « le 3e plan, j'aime l'idée » (soleil) du message l.183 ; ça
  concorde avec `fiches/PLEIN_ECRAN.md` (lu). Ce que je vois moi-même dans la
  capture du soleil : la silhouette est un ruban générique (corps mince, épines
  régulières, petite tête), pas NOTRE dragon ; c'est aussi ce que la fiche
  proposait de corriger. Les 3 planches ont ensuite été retirées (l.184).
- **7474b277** (mesuré) : doublon exact de 9388f709 (capture de Pew à ~3,9 s,
  tenue de charge vue de face-haut).
- **5be18338** (vu) : image 1280x720, style miniature YouTube : le Saitama de
  TSB (R6 costume jaune, gants rouges), caméra TRÈS proche et basse devant lui,
  grand angle ; le poing droit (bloc rouge) vient vers l'objectif, à gauche de
  l'image, avec un tourbillon de vent blanc enroulé autour ; le bras gauche est
  rejeté à l'horizontale sur la droite de l'image (poing rouge à l'autre bout) ;
  la tête est énorme en haut (visage étiré, œil rond fâché) ; un pied (botte
  blanche) avance vers la caméra en bas ; lignes de vitesse noires radiales
  convergeant vers le centre. Envoyée avec les refs remises à 09:04 (l.195) :
  c'est un exemple R6 du coup parti (pas d'un bras tendu derrière).

Hors de mon périmètre (dit) : les GIF et vidéos (autres lecteurs), les
captures de conversation 14589186 / 50ace4b8 / 90118239 et 80ac271e (consigne).

---

## 1. Par source : ce que je vois, comment c'est fabriqué, pourquoi ça marche

### 1.1 Baki (33393716), « image 1 » du 09-03 : la charge
- Vu (zoom `baki_zoom.png`) : accroupi extrêmement bas, buste presque
  HORIZONTAL, dos rond, la TÊTE plus basse que les épaules, enfoncée entre
  elles (cheveux qui pendent vers le sol) ; une jambe très pliée côté gauche de
  l'image, l'autre tendue loin sur la droite, pied à plat : l'appui est
  ASYMÉTRIQUE (poids sur la jambe pliée) ; mains ramassées près du genou/ventre,
  un poing serré visible au centre ; lumière dorée qui monte du sol (la
  puissance vient d'en dessous) ; décor de troncs verticaux qui écrasent la
  silhouette horizontale.
- Pourquoi ça marche (déduit) : c'est une masse COMPACTE, horizontale et basse
  entre des verticales : on lit un ressort comprimé, un fauve prêt à bondir.
  Rien ne dépasse loin du corps. La tête baissée donne la menace (on ne voit pas
  le visage, on voit le crâne et les épaules).
- Ce que Milan en disait (l.41) : « le perso charge son poing à son arrière
  droit ». Sur l'image, le poing n'est pas tendu derrière : il est RAMASSÉ près
  du corps, côté droit, bas. Son « arrière droit » décrivait déjà, le 09-03, la
  même chose que ses mots du 09-26 (« dans aucune le bras est tendu derrière »).
  Déduit, confiance moyenne (je ne vois pas les deux mains nettement).
- **Relecture (2e passe, `baki_zoom2.png`, recadrage 60-415 x 330-600,
  contraste x1,6 ; vu, confiance 0,6)** : la masse sombre verticale au
  centre est la CHEVELURE qui pend devant le visage (tête baissée face à
  nous), le blanc autour du cou est une chemise déchirée. Côté gauche de
  l'image (= SA droite) : le bras droit PEND, avant-bras vertical, POING
  serré au niveau du genou droit, coude haut. Au centre : une main OUVERTE,
  doigts écartés, posée en travers de la cuisse/du genou droit : c'est
  vraisemblablement SA main gauche qui traverse le corps. La jambe pliée
  (appui) est du côté du poing ; la jambe tendue loin est l'autre. Lecture :
  le buste est tourné et enroulé VERS le côté du poing chargé (le bras libre
  croise devant), le poing est BAS et près du corps, pas derrière. Ça colle
  mot pour mot à l.43 « tourner son buste vers la droite […] plier les
  jambes […] le 2e bras placé » (le 2e bras placé = en travers, devant).
  Je n'avais pas vu la main croisée à la 1re passe.
- R6 : le dos rond est impossible (torse rigide). Ce qui se transpose : buste
  penché fort + tête baissée sous la ligne des épaules (Neck) + bras collés au
  corps. Ce qui ne se transpose pas bien : l'écart de jambes extrême (Milan l'a
  refusé en R6, l.195 « le pose des jambe est un peu trop abusé »).

### 1.2 Hachures radiales (6dfb2f6c), « image 2 » : l'impact frame
- Vu (recadré `hachures_crop.png`) : capture d'un GIF makeagif (« 4 sur 4 » en
  haut) : carte noir et blanc, hachures d'encre en faisceaux qui partent d'un
  point central ; au centre une forme blanche (une silhouette ? un personnage
  vu en contre-plongée, tête blanche) ; deux bandes blanches horizontales de
  part et d'autre. Je ne peux pas dire avec certitude ce qu'est la forme
  centrale (vu, incertain).
- Pourquoi (déduit) : aucune anatomie, juste une direction (tout part du point)
  et un contraste max. C'est l'ellipse du contact : on ne montre pas le poing
  qui touche, on montre la force. Cohérent avec le tuto firytwig « skip the
  point of contact » (catalogue).

### 1.3 One Punch Man manga (8965d689), « image 3 » : la fin
- Vu : le POING droit vers le lecteur, énorme (estimé à l'œil ~2 fois la
  largeur de la tête : poing ~170 px, tête ~85 px sur 284 px de large),
  quasiment de face (on voit les 4 doigts pliés et un peu de la face du
  dessus) ; l'avant-bras est caché derrière le poing ; tête au-dessus-gauche,
  bouche ouverte, sourcils froncés ; la CAPE flotte vers le haut-droite derrière
  (elle dit que le corps a foncé vers nous) ; rochers qui volent, lignes de
  vitesse radiales derrière.
- Ligne d'action (vu) : haut-droite (cape) -> tête -> poing en bas-centre, vers
  nous. Tout le dessin est un cône qui s'ouvre vers le lecteur.
- Milan l'a mise comme image de FIN (« finir comme sur l'image 3 ») : pour lui,
  la pose tenue APRÈS la carte d'impact est l'extension vers l'objectif, pas le
  contact de profil. Son storyboard en 3 images = pose ramassée -> carte
  graphique -> extension tenue vers le spectateur. Déduit.

### 1.4 MHA manga (09a83af0 = 448c613e)
- Vu : un poing GÉANT à gauche (~60 % de la largeur ; ratio poing/tête estimé à
  l'œil 2,5 si on compte les cheveux, ~4 pour le visage seul), rendu en gris
  texturé avec des fissures d'encre, entouré de halo blanc ; le corps minuscule
  en bas à droite, cheveux en pointes, visage bas, l'œil qui regarde le long du
  poing ; l'AUTRE poing est petit, serré contre la hanche en bas à droite ;
  hachures de vitesse partout. Je ne sais pas trancher si c'est Deku ou un
  autre perso (le catalogue dit Deku).
- Ligne d'action : une seule diagonale descendante gauche->droite, de la
  jointure du poing au corps. L'autre poing à la hanche est le contrepoids
  (hikite), il ferme la ligne.
- Pourquoi : le RAPPORT de taille poing/corps EST la force. On ne voit plus un
  bras, on voit un projectile qui arrive.

### 1.5 Deku couleur (0ca551a4 = 37b6bf9a)
- Vu (zoom `deku_main.png`) : ce n'est PAS un poing fermé : la main (gantelet
  métal) est OUVERTE, doigts écartés en griffe, vers la gauche de l'image ;
  l'avant-bras est en raccourci (court et large : il vient vers le lecteur et
  vers la gauche) ; l'épaule/haut du bras au premier plan est la plus grosse
  masse de l'image ; la TÊTE est baissée et penchée, collée DERRIÈRE l'épaule,
  menton caché, un œil qui brille (lumière cyan) ; tout le corps en diagonale
  haut-gauche -> bas-droite ; éclairs et lignes de vitesse depuis la gauche (la
  main est la source de lumière).
- Écart avec le catalogue (« bras tendu vers le lecteur, épaule en avant, tête
  basse derrière le poing ») : d'accord sur l'épaule et la tête ; pas d'accord
  sur « poing » (main ouverte) et le bras n'est pas tendu (coude plié, avant-bras
  qui traverse). Vu, confiance 0,7.
- Pourquoi : l'ÉPAULE qui monte vers la mâchoire et la tête qui se cache
  derrière = le geste du boxeur qui protège le menton en frappant ; ça donne de
  la masse derrière le bras et de la détermination (on ne voit qu'un œil).

### 1.6 Saitama manga (b5d718f5)
- Vu : le poing (sombre, PETIT) à gauche, l'avant-bras qui descend vers la
  gauche en raccourci, l'ÉPAULE droite énorme au premier plan, la tête JUSTE
  derrière l'épaule, légèrement penchée, qui regarde vers le bas le long du bras
  (yeux mi-clos, calme) ; traînée noire derrière le poing (il vient d'arriver
  d'en haut-gauche) ; lignes de vitesse.
- Comme Deku : l'épaule est plus grosse que le poing. Le coup « à plat » se lit
  par l'épaule qui avance et la tête qui suit le bras, pas par la taille du
  poing. Visage calme : la puissance est dans la pose, pas dans l'expression
  (c'est tout Saitama). Vu + déduit.

### 1.7 Poing rouge (d2fda413)
- Vu (zoom `opm_rouge_zoom.png`) : un poing rouge géant de face (4 doigts en
  colonnes, jointures en haut), traversé de lignes de vitesse noires, sur la
  gauche ; au centre un personnage PETIT de dos/3-4 dos, cheveux clairs en
  pointes, armure noire à liserés dorés ; à droite un visage géant dans l'ombre
  avec un œil blanc lumineux.
- Ma première lecture était fausse : j'ai pensé « Genos » en voyant la petite
  silhouette blonde à liserés dorés. `recon_anime.json` (lu) dit « Boros petit
  au milieu, visage de Saitama géant » : ça colle mieux (la petite silhouette
  est la CIBLE, vue de dos, entre le poing et nous ; Saitama n'a pas de
  cheveux). Le catalogue dit « Saitama en ombre, œil qui brille » : exact pour
  le visage géant, mais la petite silhouette n'est pas Saitama.
- Pourquoi : image composite (géométrie impossible) : le poing, la cible et le
  regard sont trois échelles différentes collées. C'est de la mise en page, pas
  de la pose. Ce qui se transpose : l'ÉCHELLE (poing énorme, cible minuscule),
  et l'œil qui s'allume.

### 1.8 Saitama de dos (793721de)
- Vu (zoom `saitama_dos_zoom.png`) : contre-plongée depuis le sol derrière lui,
  sa jambe/botte au premier plan énorme ; buste qui monte, tête baissée tournée
  vers sa gauche ; cape arrachée vers le haut-droite par le tourbillon ;
  tourbillon blanc-violet-orange concentrique qui occupe tout le fond (centré à
  droite de sa tête) ; deux taches rouges près de ses épaules (gants ? attache
  de cape ?) ; AUCUN bras ne dépasse de la silhouette. Même lecture que
  recon_anime (« la charge se lit par la caméra basse et le tourbillon »).
- Pourquoi : la charge est racontée par l'ENVIRONNEMENT (vent, cape, caméra),
  pas par un bras armé. Le corps reste une colonne compacte.

### 1.9 Gon (ae4823bd)
- Vu (zoom `gon_zoom.png`) : vu de DOS ; jambes très écartées, genoux vers
  l'extérieur, pieds à plat ; buste penché fort ET tordu (épaules tournées par
  rapport au bassin qui reste carré) ; bras droit replié, coude qui sort en
  arrière/haut, poing collé au flanc/hanche ; tête baissée ; l'autre bras
  invisible (devant). Killua pose la main sur sa tête (scène d'émotion, le
  contexte ne compte pas pour la pose).
- La torsion bassin/épaules (contre-rotation) est la clé : le bassin reste face
  à l'avant, les épaules tournent. En R6, bassin et torse sont UN SEUL bloc :
  cette torsion est impossible dans le corps ; elle ne peut venir que des
  jambes (orientées différemment du torse) et de la tête. Déduit.
- Mesure existante (lu, `recon_anime.json`) : bras à 12° de l'axe bas du torse
  (collé au flanc) ; vu de profil, avec un buste penché à 62°, ce même bras
  devient une barre horizontale derrière le dos = exactement ce que Milan
  refuse. Le « poing à la hanche » ne marche en R6 que si le penché est modéré
  ou si on filme de dos. Je n'ai rien à y ajouter : c'est juste.

### 1.10 Captures de Pew (6c517cb3, 27f110ee, 9388f709, 27b0a39e) et TSB (a54fe910)
- 6c517cb3 (vu) : caméra basse 3/4 arrière-gauche : buste très penché, tête
  enfoncée (le chapeau haut de forme pointe vers l'avant-bas), les deux bras
  sortent sur les côtés-avant comme des blocs à hauteur d'épaule, jambes noires
  sous lui.
- 27f110ee (vu) : caméra au-dessus/derrière la tête : on ne voit que le DESSUS
  du chapeau (l'intérieur blanc) et le col : la tête est devant et plus bas que
  les épaules. recon_pew_tenue : « rien de mesurable sur les membres ».
- 9388f709 = 7474b277 (vu) : de face, un peu au-dessus : buste penché vers la
  caméra, on voit le dessus du chapeau incliné VERS nous, les deux bras de part
  et d'autre, avant-bras vers l'avant, poings (noirs) devant les épaules.
- 27b0a39e (vu) : « SERIOUS PUNCH | Roblox VFX @TeapotPew », 0:04 / 0:16 : même
  pose, face-gauche.
- a54fe910 (vu, zoom `a54_top.png`) : page Google « saitama serious punch
  roblox » ; image en tête : GIF « Roblox Strongest Battlegrounds Saitama » :
  R6 casquette rouge, vu de 3/4 dos-gauche, buste très penché, tête baissée
  (on voit le dessus de la casquette), le bras gauche tendu à l'horizontale vers
  l'avant-gauche, le bras droit (logo R) levé à hauteur de tête, un peu en
  arrière de l'épaule. Plus bas : autres résultats (TSB, « Shove + hold M1 »).
- Ce que je remarque et qui n'est mesuré nulle part : dans les 4 captures de
  Pew et celle de TSB, la TÊTE est baissée au point que le dessus du chapeau ou
  de la casquette regarde la caméra, même quand la caméra est de face et
  au-dessus. recon_pew_tenue note « l'orientation de la tête n'est pas
  mesurée (tete = (0,15) mis par défaut) » (lu). Voir §2.2 : j'ai mesuré ce
  que font les pros avec la tête, et ce que fait notre v6.

### 1.11 5be18338 (miniature TSB) : voir §0.
- Pourquoi ça marche : grand angle très proche = raccourci obtenu par la
  CAMÉRA, pas par une déformation. Le poing-bloc fait à peu près la taille de
  la tête (estimé ~0,8) parce que la tête est elle aussi très près. Le vent
  enroulé autour du poing dit « charge » sans aucune pose de charge.

### 1.12 Goku / dragon (ef27f9e2, 1a567c2f) et Dragon Ball Rage (fa08ccd8)
- ef27f9e2 (vu, 188x220) : poing levé vers le haut-gauche en raccourci, au bout
  d'une diagonale bas-droite (cheveux) -> haut-gauche (poing) ; la gueule du
  dragon OUVERTE juste au-dessus du poing, dans la même direction : le dragon
  prolonge le bras.
- 1a567c2f (vu) : Goku en l'air, ASYMÉTRIE totale : un poing ramené près de la
  tête (côté gueule du dragon), l'autre main ouverte tendue vers l'avant-droite,
  une jambe pliée haute, l'autre tendue vers le bas ; bouche ouverte ; le dragon
  s'enroule en spirale derrière, sa gueule près du poing (il SORT du poing) ;
  une traînée d'encre noire en diagonale traverse le bas (coup de pinceau
  graphique) ; éclairs blancs.
- fa08ccd8 (vu) : vignette Roblox, Goku en BLOCS : le poing est un cube avec
  des jointures dessinées, énorme en haut-gauche (ratio poing/tête estimé ~1,3),
  avant-bras en diagonale avec bracelet, gueule du dragon ouverte À CÔTÉ du
  poing, yeux cyan qui brillent. Mais l'avant-bras et le biceps ont des volumes
  musclés : c'est une ILLUSTRATION d'un perso cubique, pas un rendu R6 pur.
  Leçon : même les créateurs Roblox qui vendent du R6 trichent l'avant-bras
  pour l'affiche ; en jeu, le bras reste un bloc.

### 1.13 Suiryu (930606b5, d598c391, 996d38b7, feb2d674, 68f0ad1a)
- Vu : tête de dragon violette translucide, forme en GOUTTE dont la pointe
  touche le sol (elle sort d'un point), grand sourire blanc à dents pointues,
  yeux orange/jaunes incandescents (bloom), moustaches en spirales, traits
  sombres peints SUR le volume (cel), ombre portée au sol (c'est un mesh) ;
  dans 68f0ad1a et 930606b5 on voit l'interface du jeu (boutons) : c'est la
  caméra JEU ; la tête fait plus que le perso. feb2d674 : gueule ouverte en
  ovale vertical, anneau de dents, croissants de vent blancs autour, fumée
  grise cel.
- Pourquoi : une forme simple et lisible (goutte + sourire + deux yeux) qui
  garde son identité à n'importe quelle taille ; le trait peint sur un volume
  3D = le « dessiné » que Milan demande (l.179). Étudié en détail dans
  `RELECTURE_REFS_SUIRYU` (non relu en entier ici, je ne recopie pas).

### 1.14 VFX stylisés (8005ceb1, f23068ce, 81f070a6, 0f85f7a1, 22c8d49c, cab1e5b6, 2c6dce4d, 5b6ab8d1, 1727676e, 8d015f39, 7263e0c8, 41d7796b, a4a75c01)
Vu, l'essentiel pour mon angle (la POSE et le goût ; le détail VFX est dans
`RELECTURE_REFS_VFX_STYLE`) :
- Toutes les formes sont POINTUES et DIRIGÉES (lames en dents de scie,
  langues, croissants, triangles) ; 2-3 tons + cœur blanc ; du NOIR dans
  l'effet (22c8d49c veines d'encre ; 8005ceb1 griffures noires ; f23068ce
  débris noirs). Chaque effet a une direction, comme une ligne d'action.
- **5b6ab8d1** : la VICTIME projetée est en X (quatre membres écartés, tournée
  en l'air, croissants de vent gris autour) ; l'attaquant, lui, est compact
  (dans l'anneau bleu). Voir §2.4 : c'est important pour notre charge.
- **41d7796b / a4a75c01** (vu, contraste poussé `impact_contraste.png`) : le
  contour fin arrondi + la ligne horizontale à encoche sont la silhouette d'une
  tête R6 sur des épaules ; les deux étoiles à 4 branches sont à la place des
  YEUX. Carte d'impact = le visage réduit à deux éclats d'œil, en noir sur
  blanc puis blanc sur noir, traits verticaux, texte géant en fond. Envoyée
  pour le « genkidama » (09-03).
- **8d015f39 / 7263e0c8** : soleil ÉNORME au-dessus d'un perso MINUSCULE :
  l'échelle dit la puissance divine.
- **cab1e5b6** : dragon-projectile cyan = le corps du dragon EST le faisceau ;
  la gerbe blanche à pointes au départ = le « coup » qui le lance.

### 1.15 Rig Blender (dfdb9286) et fiche DEMI-DIEU (da606c23)
- dfdb9286 (vu) : rig R6 V2.x dans Blender : chaque bloc porte des LETTRES sur
  ses faces (FRONT sur le torse, F = face avant de chaque membre, L = côté, U =
  dessus en bleu) ; un anneau autour du cou (contrôle de tête) ; des boîtes
  filaires au bout des bras et des pieds (contrôles IK de main et de pied) ;
  des petites sphères colorées devant (cibles de coude/genou, pôles) ; un
  anneau à flèches au sol (racine). Pourquoi (déduit) : sur un bloc sans
  visage, l'animateur ne voit pas la torsion d'un bras ; les lettres rendent
  lisible quelle face regarde où. C'est la même idée que le rig lettré F/B/L/R
  des anims abandonnées de TSB (catalogue) et du tuto pro contre noob (« on lit
  BACK puis FRONT » = 180° de buste). Où il place le rig : les contrôles sont
  aux EXTRÉMITÉS (mains, pieds) et au centre (racine au sol), avec des pôles
  devant ; on anime en posant les mains et les pieds, le reste suit.
- da606c23 (vu) : fiche « DEMI-DIEU, S1 Poing Scintillant, key poses &
  animation guide (R6) », 8 poses sur un rig lettré (Neutral 0 /
  Anticipation 1-6 / Charge 7-10 / Launch 11-14 / Impact 15-16 / Follow through
  17-22 / Recovery 23-28 / End 29-30 à 30 i/s, ~1 s), une rangée de
  SILHOUETTES noires, « Les 3 règles d'or » (« on doit comprendre l'action en
  simple silhouette », « chaque pose sert l'action », « l'amplitude prime sur
  le réalisme »). Indices que c'est une image GÉNÉRÉE (IA) : fautes (« Pas de
  dioigts »), texte superposé (« naturelle » en double), la rangée silhouettes
  numérotée 1, 2, 3, 2, 5… Milan l'a retirée 8 minutes après (l.129). Ce que
  j'en garde : le test de la silhouette noire, et la pose d'impact (jambe
  arrière tendue dans l'axe du buste et du bras = une seule diagonale). Ce que
  je n'en garde pas : l'anticipation « bras droit armé en arrière » qui est
  justement ce que Milan a refusé plus tard.

---

## 2. Grands enseignements (dessin de pose -> R6)

### 2.1 La ligne d'action se fait en ALIGNANT des blocs, pas en courbant
Vu sur 8965d689, 09a83af0, ef27f9e2, fa08ccd8, 0ca551a4, da606c23 (pose 5) :
chaque pose de frappe est UNE diagonale (du pied arrière ou de la cape jusqu'au
poing), et le spectateur la suit jusqu'au bout. Un dessinateur courbe la
colonne ; un R6 n'a pas de colonne. Déduit : en R6, la ligne naît quand jambe
arrière, buste et bras sont dans le PROLONGEMENT les uns des autres (la fiche
DEMI-DIEU le montre en silhouette, pose 5) et quand la tête suit la même
pente. Un genou arrière plié ou une tête relevée casse la ligne en deux.

### 2.2 La TÊTE : baissée, verrouillée sur la cible (mesuré chez les pros ; notre v6 fait l'inverse)
Vu dans les images : Baki, Gon, Deku, Saitama manga, Saitama de dos, Pew (4
captures), TSB (a54fe910) : la tête est BASSE, souvent derrière l'épaule, le
regard par en dessous ; on voit le crâne / le dessus du chapeau.

Mesuré (`planche_cles.py --json`, descripteur `tete` de `geo_pose`, el + =
regarde vers le haut, repère du coup ; données exactes .rbxm) :
| anim | buste lacet (min -> max) | tête/cible az | tête el (monde) | tête/torse el |
|---|---|---|---|---|
| TSB M1 | +48 -> -70 | -21 à +29 | -12 à -26 | -7 à -17 |
| TSB M2 | -65 -> +52 | -11 à +20 | -12 à -31 | -8 à +3 |
| TSB M3 | +52 -> -60 | -4 à +14 | -11 à -18 | -10 à +5 |
| TSB M4 (crochet) | -58 -> +60 | -13 à +9 | +17 à -24 | -4 à -41 |
| pack M1_1 | 0 -> -98 -> +58 | -9 à +13 | 0 puis -16 à -27 | -1 à -19 |
| pack M1_2 | +62 -> -75 | -1 à +8 | -22 à -31 | -16 à -21 |
| pack M1_4 | -83 -> +79 | -1 à +22 | -18 à -26 | -8 à -21 |
| pack Uppercut | -69 -> +58 | jusqu'à -56 | -17 à +7 | +18 à -11 |

(2e passe : voir §7.1, c'est l'élévation MONDE qui compte, pas la valeur
relative au torse ; le relatif dépend du penché du buste.)

Lecture : dans les directs (M1-M3, M1_x), la tête reste pointée sur la cible
(±10-30°) pendant que le buste tourne de 100 à 180° : le cou contre-tourne.
Et elle est baissée d'environ 20-30° dans le monde, 15-20° par rapport au
torse. L'uppercut est l'exception : la tête suit le mouvement.

Mesuré sur NOTRE v6 (`experiments/r6_un_seul_coup/output/usc_attaquant.rbxmx`,
images 186-291) : az tête/cible -7 à +11 (bien verrouillée), MAIS el tête
**+11 à +12 pendant toute la charge (i186-272)**, tête/torse el **+14 à +23**
(la tête se RELÈVE par rapport au buste penché), ~0 au contact (i282-291).
Notre perso se penche mais relève le menton pour regarder la victime : un
regard par-dessus, pas par en dessous. `CARNET.md` l.459-461 (lu) contient
« Regarder devant, menton levé » (une ancienne correction d'un bug de regard) :
c'est peut-être l'origine.

Essai (`v6_tete_baissee.png`, rendu `geo_pose`, même pose i250, seule la tête
tournée autour du cou jusqu'à el -22) : la différence est NETTE de profil,
faible de face-poitrine (le bras gauche cache la tête) et de 3/4 dos. Donc ce
n'est PAS « la » réponse au poing chargé ; c'est un écart réel et mesurable,
à tester dans la vidéo au cadrage du spectateur. Réserve : registre JEU pour
les M1 (Milan, dernier message, l.215 : distinguer jeu et cinématique) ; mais
les images anime (registre cinéma) disent la même chose. Réserve 2 : je
suppose que la face de la tête R6 est -Z dans les deux sources (cohérent avec
az ~0 vers la cible dans les deux).

### 2.3 Le raccourci du poing vient de la CAMÉRA (et du 3/4), jamais d'une échelle
- Vu : les dessins mettent un rapport poing/tête de ~2 (OPM) à ~2,5-4 (MHA) ;
  la vignette Roblox ~1,3 ; la miniature TSB ~0,8 (estimés à l'œil).
- Déduit (géométrie simple ; tête R6 2 studs de large, bout de bras 1 stud,
  tête ~3 studs derrière le poing quand le bras vise la caméra) : rapport
  apparent = d_tête / (2 d_poing). Pour 2 : caméra à ~1 stud du poing ; pour 3 :
  ~0,6 stud ; pour 1,3 : ~1,7 stud. Il faut donc un grand angle collé au poing,
  et ça ne tient que 0,3-0,6 s (plans mesurés chez TSB/SP2/Pew, lu dans
  `nous_v5_ce_que_milan_voit.json`).
- Vu : aucun dessin ne montre le poing PARFAITEMENT de face seul : OPM montre
  un peu du dessus du poing et la tête juste derrière ; Saitama manga et Deku
  montrent l'ÉPAULE plus grosse que la main. En R6 un bras vu pile de face est
  un carré (déjà noté fiche §9 : « poing de face pur (illisible) ») : il faut
  15-30° de 3/4 pour que les faces latérales du bras fassent le tube qui
  recule. Confirmation, pas nouveauté.

### 2.4 Le X est la silhouette de la VICTIME (surprise)
- Vu : 5b6ab8d1, la victime projetée = X (4 membres écartés, tournée). Tous les
  attaquants que Milan envoie sont COMPACTS pendant la charge (Baki, Gon,
  Saitama de dos, Pew, TSB a54), puis UNE ligne à la frappe.
- Lu : `nous_v5_mesure.json` : notre v5 de face (vue de la victime) = « un X,
  les deux bras écartés en diagonale vers le bas de chaque côté, jambes
  écartées. Rien ne lit poing armé ». Déduit : on donnait à l'attaquant, au
  moment de la charge, la silhouette qu'on associe à quelqu'un qui SUBIT (bras
  écartés, sans contrôle). Le contraste compact (charge) -> une seule ligne
  (frappe) -> X (victime) raconte qui a la force.

### 2.5 L'épaule, la masse derrière le coup
Vu (Deku, Saitama manga, 5be18338) : l'épaule du bras qui frappe monte vers la
mâchoire et avance ; c'est souvent la plus grosse forme de l'image. En R6
l'épaule ne monte pas (pas de clavicule). Ce qui existe (lu,
`pro_tsb_ultimes.json`) : les pros TRANSLATENT le pivot d'épaule (57 à 97 %
des images de bras), et on peut incliner le torse sur le côté (roulis) pour
remonter l'épaule qui frappe + pencher la tête vers elle. Je n'ai pas testé
le roulis en rendu (dit).

### 2.6 Asymétrie : le 2e bras a toujours un rôle, jamais le même
Vu : MHA = poing à la hanche (contrepoids) ; Goku 1a567c2f = main ouverte
tendue pendant que l'autre poing est près de la tête ; 5be18338 = bras rejeté à
l'horizontale derrière ; Gon / Saitama de dos = caché devant ; Pew = les deux
devant. Il n'y a pas de position type ; il y a toujours une DIFFÉRENCE nette
entre les deux bras (jamais le miroir).

### 2.7 La charge est souvent racontée par l'environnement et la caméra
Vu : Saitama de dos (tourbillon, cape), Baki (lumière du sol), 5be18338 (vent
enroulé au poing), Pew (le chapeau qui pointe vers nous). La pose de charge
elle-même est sobre et compacte ; c'est tout ce qu'il y a AUTOUR qui monte.

---

## 3. Le goût de Milan : un portrait de son œil (ses mots exacts)

Ce n'est pas une liste de règles : c'est ce qu'il regarde, ce qui l'allume, ce
qu'il rejette, d'après ses 215 messages (n° = ligne du fichier) et ce qu'il
envoie. Lu + déduit.

### 3.1 Il regarde d'abord le CORPS entier, pas le bras
- l.43 (09-03) « Tu oublies de utiles les jambes le peros est cense tourné son
  buste vers la droit charger sont moins droit plier les jambes le légèrement
  le 2e bras placé et boum il envoi »
- l.44 « Il manque les épaules on dirait que le coup pars du bas alors que il
  doit allez droit »
- l.49 « Le perso met juste une espèce d'élancement du bras dans tes rendue »
- l.53 « il faut que le bust tourne la jambe se plie et que le bras pas que le
  « poignet » parte du bas »
- l.169 (09-25) « enft tu as a anime que les bras encore une fois »
Constante depuis le 1er jour : un coup est un corps qui tourne, pas un bras
qui s'allonge.

### 3.2 Il a décrit le « déboîtement » trois semaines avant qu'on le mesure (surprise)
- l.54 (09-04 23:15) « le coup ne doit pas parti de derrière mais le bras se
  déboîte vers l'arrière et avance vers l'avant , ne te fis pas une animation
  humaine »
- l.55 (09-04 23:32) « inverse , en gros le bras monte en position final
  recule en arrière , mais ne part de l'arrière la est la différence et avance
  vers l'avant »
- l.195 (09-26) « tu fais partir le poing de l'arrière ou de l'arme à
  l'arrière , arrière qui est engager par le juste [buste] tourne […] dans
  aucune le bras est tendu derrière »
Déduit (confiance 0,6) : il décrit un bras qui se met d'abord sur la LIGNE du
coup, RECULE le long de cette ligne (comme un piston, « se déboîte »), puis
repart devant ; « ne te fais pas une animation humaine » = ce n'est pas une
articulation qui tourne, c'est un bloc qui glisse. Or `pro_tsb_ultimes.json`
(lu, 09-26) mesure exactement que TSB translate le pivot d'épaule (U1 : épaule
reculée de 0,3 à 0,66, le bras pointe vers l'AVANT et glisse le long du flanc).
Ses mots du 09-04 et la mesure du 09-26 disent la même chose ; le lien n'est
écrit nulle part dans le cerveau (grep « déboît » : seulement deux tutos). Je
ne l'ai pas vérifié avec lui.

### 3.3 « Manga » = exagéré mais lisible, pas « plus d'amplitude partout »
- l.10 « tu abuse pas assez le mouvement style manga »
- l.110 « les coup sont souvent abuse car c du style manga »
- l.133 « Les poses manque d'une touche manga […] tout joue pour être pas
  exagéré mais anime façon a ce que le coup sois fantaisiste même un coup
  simple n'est pas coup simple genre y'a une anatomie et une règle différente »
- l.133 « la règle de l'animation Disney jsp quoi ça ne fonctionne pas »
- l.195 « le pose des jambe est un peu trop abusé »
- l.132 « en cinéma peut être un peu trop abusé mais léger »
Il veut une anatomie de MANGA (poing qui grossit, épaule qui avance, tête qui
rentre, corps qui devient une ligne), pas une amplitude de gym. Le pendule
« pas assez / trop abusé » (6 fois selon `motifs`) vient peut-être de là : on
a exagéré les ANGLES (jambes, penché), il demandait d'exagérer la LECTURE.

### 3.4 Il lit le rythme : lisibilité et « poids » avant la vitesse
- l.34 « C bcp trop rapide on ne lit pas assez les mouvement y'a pas de logique
  le perso est censé charge son poing »
- l.80 « Ça manque de frame d'un début et d'une fin »
- l.186 « le dragon va dans tout les sensé hyper rapidement »
- l.191 « le moment ultra rapide très bien » (quand la vitesse est un effet
  voulu, contrasté).
Il accepte la vitesse extrême si elle est UN moment, entre des moments lisibles.

### 3.5 Il juge le STYLE graphique avec des mots précis
- « dessiné », « limite on dirait », pas « peinture » : l.179, l.183.
- pas « cube », pas « cartoon » : l.181 « c trop cubique aussi pas assez
  travaillée » ; l.174 « c pas du tout du model premium ».
- « premium » : l.12, l.174, l.184 « ça rends pas bien pour du Roblox premium »,
  l.187 « pas premium mais mid haut ».
- les YEUX : l.181 « tes yeux du dragon sont ausis se qui casse le truck ça fais
  moche ». Et dans ce qu'il envoie, les yeux brillent partout : Suiryu (bloom
  jaune), Cursed Dragon (violet), Dragon Ball Rage (cyan), Deku (œil lumineux),
  poing rouge (œil blanc), carte d'impact (étoiles à la place des yeux). Un
  détail qu'il regarde de près (vu + déduit).

### 3.6 Il envoie des INSTANTS, pas des animations
Ses images fixes sont toujours le point culminant (poing vers le lecteur,
charge ramassée, gueule ouverte), et quand il envoie une vidéo il la met en
pause sur l'instant (27b0a39e : 0:04 / 0:16 ; a54fe910 : recherche Google
« saitama serious punch roblox »). Son storyboard du 09-03 est en 3 images
(ramassé / carte / extension tenue). Il pense en POSES-CLÉS + une carte
d'impact, comme un storyboardeur. Déduit.

### 3.7 Ce qui l'enthousiasme (rare, donc précieux)
- l.18 « Okk pas mal » (demi-tour du trône, après correction « toupie ») ;
- l.48 « Tu t'es nettement amélioré » (trône) ;
- l.99 « Franchement c pas mal sur tout le jeux arien » ;
- l.132 « c'est très bien d'avoir développé ce skills » (caméra jeu/ciné) ;
- l.176 « Je te felecithr pour la construction de ton labo » ;
- l.183 « j'aime l'idée que tu as eu bonne créativité » (le soleil) ;
- l.186 « bien jouer pour le travaille actuel » ;
- l.191 « le moment ultra rapide très bien ».
Il récompense : une IDÉE de mise en scène (soleil, départ ultra rapide), la
caméra, et les progrès visibles. Il ne récompense jamais un chiffre.

### 3.8 Sa posture
- l.110 « c quelquz exemple mais pas les ref paefait donc a ne pas copier
  forcemznr betement »
- l.113 « nz prends pas mes parole pour de regle mais comme des piste »
- l.151 « tout ce que tu vois anime sont possiblement et souvent mieux que nous »
- l.172 « je suis pas expert mais j'ai l'œil »
- l.199 « tu crée pas de règles grave dans la roche »
- l.215 « tsb est très bien masi faut uasis distinguer […] cinématique et ya bcp
  de ref qui sont en vision jeux »
Il se voit comme l'œil ; il attend de nous le métier. Quand il décrit un
mouvement avec ses mots (§3.2), c'est souvent juste mais formulé en
sensation : à traduire en mécanique, pas à prendre au pied de la lettre, ni à
ignorer.

---

## 4. Ce que je saurais REFAIRE en R6 maintenant (concret)

1. **Tête de charge** : sur une tenue de charge, tête verrouillée sur la cible
   en azimut (le cou contre-tourne le buste), baissée de ~20-30° dans le monde
   (15-20° par rapport au torse), pas relevée. Chiffres des M1 pros (§2.2).
   Vérifiable avec `planche_cles.py --json` (descripteur `tete`).
2. **Plan poing vers l'objectif** : caméra à ~0,6-1 stud du bout du bras,
   grand angle, bras à 15-30° de l'axe de vue (3/4), épaule et tête dans le
   cadre derrière, tenu 0,3-0,6 s ; rapport poing/tête 2 à 3.
3. **Silhouette test** : rendre la charge en noir de face (vue de la
   victime) : si elle fait un X, c'est la silhouette de la victime (§2.4).
4. **Ligne d'impact** : jambe arrière tendue, buste et bras dans la même
   diagonale, tête sur cette diagonale (fiche DEMI-DIEU pose 5, dessins).
5. **Le 2e bras** : lui donner un rôle distinct (hanche, rejeté derrière,
   devant caché) ; jamais le miroir.

Ce que je ne saurais PAS faire (dit) :
- la contre-torsion bassin/épaules de Gon dans un torse R6 d'un seul bloc (je
  n'ai qu'une piste : orienter les jambes différemment du torse) ;
- l'épaule qui monte (pas testé : roulis du torse + translation d'épaule) ;
- dire si la tête baissée change la NOTE de Milan : l'effet est visible de
  profil, faible de face sur la pose v6 (mon rendu) ;
- le « déboîtement » : je l'ai relié à ses mots, je ne l'ai pas animé.

## 5. Surprises / contradictions avec le cerveau
- Notre v6 relève la tête (+11° monde, +14 à +23° / torse) pendant la charge ;
  tous les pros mesurés la baissent (-12 à -31°). Aucune recon de ref n'avait
  mesuré la tête (Pew : « non mesurée, (0,15) par défaut »). CARNET l.461
  « Regarder devant, menton levé ».
- Milan a décrit le déboîtement d'épaule (translation) le 09-04, mesuré chez
  TSB le 09-26 : lien absent du cerveau.
- Catalogue : d2fda413 « Saitama en ombre » : la petite silhouette est Boros
  (la cible), le visage géant est Saitama ; 0ca551a4 « poing » : c'est une main
  OUVERTE, bras plié qui traverse.
- Le X d'attaquant (v5) = silhouette de victime (5b6ab8d1).
- da606c23 est une image générée (fautes, numérotation 1-2-3-2-5), et son
  anticipation « bras armé en arrière » est celle que Milan a refusée ensuite.
- 797cdcc7 / 8b32a1d7 / f091ee86 ne sont pas des refs : ce sont nos propres
  planches, capturées par Milan pour les critiquer.

## 7. Reprise (2e passe, même jour) : revoir, puis ESSAYER les dessins en blocs

### 7.0 Ce que j'ai refait
- Revu moi-même, dans cette passe, les images clés (Read) : 33393716 (+ un
  2e zoom), 8965d689, 09a83af0, 0ca551a4, b5d718f5, ae4823bd, 793721de,
  5be18338, d2fda413, et les 3 captures non cataloguées (planche
  `non_catalogues.png`). Les descriptions du §1 tiennent, sauf Baki
  (corrigé §1.1). Précisions :
  - Deku 0ca551a4 : la tête n'est pas « derrière » l'épaule, elle est
    penchée AU-DESSUS du haut du bras, la joue presque posée dessus, le col
    cache le menton ; l'œil gauche est un éclat cyan en croix (vu).
  - 793721de : la grande forme rouge en bas au centre est au premier plan,
    sous la taille : je la lis comme sa jambe/botte (vu, pas sûr) ; les deux
    petites taches rouges aux épaules restent indéterminées (gants
    devant ? attache de cape ?).
  - 797cdcc7 est à vitesse 1x, 8b32a1d7 et f091ee86 à 0,5x (vu, bouton
    jaune « VITESSE ») : Milan ralentit le lecteur pour regarder. Détail de
    son œil : il inspecte au ralenti, pas seulement en lecture normale.
- Lu les 216 lignes de `milan_verbatim.jsonl` (204 « dit », 12 « colle ») ;
  compté ses thèmes (§7.3).
- Construit en R6 (outil `geo_pose.pose`, rendu + silhouette noire, 4
  caméras : face = vue de la victime, profil droit, 3/4 avant, 3/4 dos
  « jeu ») des transpositions des dessins : `transpo/charges.png`,
  `charges2.png`, `lignes.png`, `lignes2.png` ; script `transpo.py`, poses
  `poses1-4.json`. Chaque rendu a été regardé.

### 7.1 La tête « baissée » des dessins se lit dans le MONDE, pas par rapport au buste (mesuré, surprise)
- Première transposition de Baki (`charges.png`, rang 2) : buste penché 55°,
  tête baissée de 30° en plus par rapport au torse -> descripteur tête
  `coup el -67` : il regarde le sol entre ses pieds (vu dans le rendu : la
  tête est un bloc gris tourné vers le bas). Ce n'est pas le Baki.
- Ligne `ligne_R6d` / `ligne_R6e` (`lignes2.png`) : buste penché ~45° vers la
  cible, tête RELEVÉE de 20° par rapport au torse (`tete torse el +20`) ->
  `coup el -24`, soit exactement la plage des M1 pros (-12 à -31, §2.2).
  Vu de profil : la tête est dans le prolongement du bras, légèrement
  baissée, lisible.
- Donc (déduit, mesuré sur 5 poses) : « tête baissée » = élévation MONDE
  d'environ -15 à -30°. Plus le buste plonge, plus la tête doit se
  relever par rapport à lui pour garder ce regard. Le « menton levé » de v6
  n'est pas faux parce qu'il est relevé par rapport au torse (+14 à +23) :
  il est faux parce que le buste ne penche que de 20° (`v6_250` : penché
  +20), ce qui laisse le regard monde à +11. Ça corrige ma formulation du
  §2.2 (qui mettait en avant le relatif). Le bon chiffre à regarder est
  `tete.coup` (monde), pas `tete.torse`.

### 7.2 Une diagonale de dessin se construit en directions MONDE (vu, mesuré)
- `ligne_R6` (`charges2.png`, `lignes.png` rang 1) : buste tourné +55°
  (épaule droite devant), penché 40° « vers l'avant du torse », roulis -10°.
  De profil, le torse rouge paraît presque DROIT : son penché part à 55° de
  la ligne du coup (sur le côté), il ne se voit pas dans le plan du coup.
  La ligne du dessin n'apparaît pas.
- `ligne_R6b` : même lacet, mais penché décomposé vers la cible (26° avant +
  37° de côté ≈ 45° vers la cible), bras visé en monde (az 0, el +5). De
  profil, le torse bascule enfin vers la cible et fait une diagonale avec
  le bras (vu, `lignes.png` rang 2).
- Apprentissage (déduit) : sur un R6, quand le buste est tourné pour
  avancer l'épaule, « pencher en avant » dans ses axes ne penche PAS vers la
  cible. Le dessinateur trace la ligne dans l'image ; l'animateur R6 doit
  la poser dans le monde (même idée que `CARNET` 3.8 « poser en directions
  monde », lu). Ça donne une piste de lecture pour des retours comme l.44
  « on dirait que le coup part du bas alors qu'il doit aller droit » : un
  buste tourné et penché dans ses propres axes met le bras sur une pente
  que l'œil ne lit pas comme « droit ». Hypothèse, pas vérifiée sur nos
  anims.

### 7.3 La jambe arrière R6 est courte : la diagonale longue des dessins ne tient pas (vu)
- `ligne_R6b` / `ligne_R6d` : pied arrière planté à 3,4 puis 2,4 studs
  derrière : dans les deux rendus de profil, la jambe jaune est DÉTACHÉE de
  la hanche (vu : bloc isolé en bas à gauche). La jambe R6 fait 2 studs et
  son pivot est fixe sous le torse : le pied demandé est hors de portée et
  l'outil de plantation ne peut pas l'atteindre.
- `ligne_R6e` : jambe arrière posée par DIRECTION (monde az 180, el -35),
  hanche 2,0 : la jambe reste attachée et prolonge la diagonale du buste
  (vu, `lignes2.png` rang 2, profil : pied arrière -> torse -> bras forment
  un éclair : diagonale jusqu'à l'épaule, puis bras horizontal).
- Ce que ça m'apprend (déduit) : la grande jambe arrière tendue des dessins
  (DEMI-DIEU pose 5, MHA) est une longueur que le R6 n'a pas ; pour
  l'approcher il faut baisser la hanche, et la ligne n'est jamais droite
  d'un bout à l'autre si le coup est horizontal : elle casse à l'épaule.
  Les dessins l'évitent parce que leur cible est souvent vers le lecteur
  (la ligne part dans la profondeur).

### 7.4 Ce que chaque caméra voit d'une pose « dessinée » en blocs (vu)
- Face (vue de la victime), toutes les poses de frappe : le bras qui vise
  la caméra est un CARRÉ vert à côté de la tête ; la silhouette noire est
  une masse compacte sans ligne (`lignes.png`, `lignes2.png`, colonne 1-2).
  À 9 studs et 40° de champ, aucun effet de raccourci : le poing n'est pas
  plus gros que la tête. Confirme §2.3 : le « poing énorme » des dessins
  demande une caméra à ~1 stud, grand angle.
- 3/4 dos « jeu » : toutes les poses deviennent un bloc ; le bras qui frappe
  est caché par le torse (vu, colonne 7-8). Même constat que `CARNET` 1.2.
- Profil : c'est la seule vue où la ligne se lit (vu). Les dessins de Milan
  sont presque tous en 3/4 vers le lecteur, jamais en profil pur : ils
  obtiennent la ligne ET le raccourci par la perspective.
- Baki en R6 (`charges2.png` rang 2, `baki_R6b`) : bras droit pendant
  (penché 55° -> il faut `el -35` dans les axes du torse pour qu'il pende
  vertical, mesuré), main gauche en travers. De face, la silhouette est
  compacte et basse, tête grise au-dessus du bras gauche : on lit « ramassé »,
  pas de X (vu). De profil, c'est un gros pavé, le poing bas n'est pas
  lisible. Ce qui fait le Baki dessiné (dos rond, cheveux qui pendent,
  lumière du sol) n'est pas dans les blocs : la pose R6 ne porte que la
  compacité. Le reste devra venir de la caméra (basse), de la lumière et des
  effets (§2.7).

### 7.5 Ce qui fait qu'une image FIXE se lit comme du mouvement (vu sur les refs) et son équivalent R6
| moyen dans le dessin | où (vu) | en R6 |
|---|---|---|
| élément qui TRAÎNE derrière (cape, cheveux) | OPM 8965d689 (cape haut-droite), Saitama de dos (cape arrachée), Deku (tissu déchiré) | pas de cape (GDD amendé, mandat §1 : cape supprimée). Il reste : traînée VFX, débris, et le décalage des blocs eux-mêmes (tête ou 2e bras qui arrivent 1-2 images après). Déduit. |
| lignes de vitesse qui partent d'un point | 6dfb2f6c, MHA, OPM, 5be18338 (lignes noires radiales dans une capture R6) | effet écran / planche ; 5be18338 prouve que TSB-like le fait sur du R6 (vu) |
| contour du poing hérissé (le poing « vibre ») | d2fda413 (poing rouge à bord en pointes), MHA (poing gris à bord déchiqueté) | pas dans le bloc ; halo ou mesh-trait autour du bras (VFX dessinés) |
| cadrage qui COUPE le perso | 5be18338 (haut de la tête coupé), MHA (poing coupé), Deku | caméra très proche, faisable tel quel |
| déséquilibre (centre de masse hors des appuis) | Deku (corps en diagonale, pas d'appui visible), Goku 1a567c2f (en l'air) | faisable : le R6 n'a pas de gravité dans l'anim, la hanche peut sortir de la base |
| échelle exagérée poing/corps | MHA, d2fda413 | seulement par la perspective (§2.3, §7.4) |
Ce sont des moyens de mise en image autant que d'animation. En R6, la
moitié passe par la caméra et les effets, pas par la pose.

### 7.6 Le goût de Milan : compléments (lu, compté)
- Comptage (regex sur les 204 messages « dits », `milan_verbatim.jsonl`) :
  « ref » 35 messages ; « fluide/smooth » 12 ; « exag/abus » 11 ; « jambe/
  pied/appui » 11 ; « caméra » 9 ; « premium » 7 ; « du bas / vers le
  bas » 7 (l.44, 53, 65, 104, 109, 113, 190) ; « règle » 7 ; notes /10
  dans 15 messages. Réserve : l.45 et l.65 sont des textes collés (brief,
  conseils d'une IA) enregistrés comme « dit » ; ce ne sont pas ses mots.
- **La direction du poing est SA plainte la plus constante sur les coups**
  : « le coup part du bas » (l.44, 09-03), « le poignet parte du bas »
  (l.53), « tu donnes des coups vers le bas » (l.104), « les coups partent
  toujours du bas […] on dirait un enchaînement d'uppercut mais en même
  temps coup droit » (l.109), « au coup final le coup part toujours d'en
  bas » (l.113), « le perso frappait vers le bas » (l.190). Il lit la
  TRAJECTOIRE du poing (d'où il vient, où il va) avant la pose. Ce qu'il
  veut : un coup qui arrive « droit » (l.44) sur la cible.
- **Corriger le défaut signalé ne fait pas monter la note** : l.113 « le
  bras ne part plus d'en bas mais ne change pas la note ». Il note
  l'impression d'ensemble, pas la liste des corrections.
- **Trajectoire des notes** (lu) : 3/10 (l.71, 09-23) -> 6 (l.99) -> 6,7
  (l.102, 113) -> 6,8 (l.123) -> 7 (l.132) -> 7,8 jeu / 7,2 ciné (l.161)
  -> 7,7 (l.169) -> VFX 4 (l.174), 3-4 (l.176) -> 7,85 (l.186) -> 8 (l.187)
  -> « Un seul coup » 7 (l.191) -> 7,5 (l.196). Les sauts coïncident avec
  la mise en scène (caméra de jeu, scène complète, départ ultra rapide),
  les plateaux avec le coup lui-même (« il manque un cap », l.132).
- **« Accroupi » est un reproche, mais Baki est accroupi** : l.99 « il est
  accroupie », l.102 « les bras sont trop hauts, il est accroupi et pas en
  transfert de poids ». Déduit : ce qu'il rejette, c'est rester bas
  PENDANT le coup (pas de transfert) ; ses refs sont basses PENDANT la
  charge seulement, puis le corps part en ligne (storyboard l.40 : image 1
  ramassée -> image 3 étendue).
- **Les pieds doivent suivre le geste** : l.62 « quand tu mets des coups les
  axes des jambes changent et le jeu de jambes change selon l'envoi de la
  charge du poing » ; l.64 « les pieds toujours trop ancrés dans le sol et
  pas en mouvement avec les gestes ». Et à l'opposé, l.195 « la pose des
  jambes est un peu trop abusée ». Il veut des jambes qui ACCOMPAGNENT le
  coup (orientation, appui), pas des jambes spectaculaires.
- « pourquoi tout a l'air mécanique » (l.84), « pas 100 % robotic mais il
  manque une touche » (l.133) : son mot pour ce qui manque, c'est
  « touche manga », jamais un paramètre.

### 7.7 Ce que je saurais refaire en plus (R6, concret)
- Régler une tête de charge par son élévation MONDE (-15 à -30°) et
  compenser le penché du buste par un relèvement relatif (ex. buste 45° ->
  tête +20° / torse -> -24° monde, mesuré sur `ligne_R6e`).
- Construire une ligne de frappe en monde : lacet +55°, penché décomposé
  vers la cible (~26° avant + ~37° côté), bras visé en monde, jambe arrière
  posée par direction (az 180, el -35), hanche ~2,0 ; vérifier de profil.
- Faire pendre un bras vertical sur un buste penché de p° : `el -(90-p)`
  dans les axes du torse (p = 55 -> -35).
Ce que je ne saurais pas (dit) : rendre de FACE la ligne ou le poing
énorme sans une caméra collée ; faire lire en blocs le dos rond / la tête
enfoncée de Baki ; dire si §7.2 explique vraiment le « part du bas » de
nos versions (non mesuré sur v2-v6).

## 6. Fichiers produits (scratchpad, jamais dans le dépôt)
2e passe : `baki_zoom2.png`, `non_catalogues.png`, `transpo.py`,
`poses1.json`..`poses4.json`, `transpo/charges.png`, `charges2.png`,
`lignes.png`, `lignes2.png`.
`frames/C4_images_et_gout/` : zooms (`baki_zoom.png`, `gon_zoom.png`,
`saitama_dos_zoom.png`, `opm_rouge_zoom.png`, `deku_main.png`, `a54_top.png`,
`hachures_crop.png`, `impact_contraste.png`, `anciens.png`), planches de clés
(`tsb_M1..M4.png/json`, `pack_2M1_1/2/4.png/json`, `pack_3Uppercut.png/json`,
`nous_v6.png/json`), essai tête (`tete_test.py`, `v6_tete_baissee.png`).

## Vérification adverse

Vérificateur adverse, 2026-09-26. Rien n'a été modifié dans le dépôt. Mes
extractions sont dans `frames/verif_C4_images_et_gout/` : `baki_tete.png`,
`baki_clair.png`, `transpo_v.py` (copie de `transpo.py` qui écrit ailleurs),
`verif_poses1..4.png`. J'ai relancé `transpo.py` sur `poses1..4.json` : les 4
planches sont identiques octet pour octet (md5) à `charges.png`,
`charges2.png`, `lignes.png` et `lignes2.png`, et les descripteurs imprimés
redonnent exactement les chiffres cités. J'ai aussi relu les lignes citées de
`milan_verbatim.jsonl` (l.40-196) et relancé les regex, ouvert les images
33393716, 5be18338, d2fda413, 8b32a1d7, f091ee86 et 797cdcc7, lu le JSON des
clés de `tsb_M1..M4`, `pack_2M1_1/2/4`, `pack_3Uppercut` et `nous_v6`, et relu
`experiments/r6_poing_dragon/scripts/player_template.html`.

### 8 apprentissages vérifiés

1. **Baki : poing bas, main libre en travers, enroulement du côté du poing.
   Verdict : nuancé.** Ce qui se voit bien : un appui très large et bas, la
   jambe côté gauche de l'image fortement pliée et la jambe droite tendue au
   loin, un poing fermé du côté gauche de l'image au-dessus de la cuisse pliée,
   et une main ouverte aux doigts écartés posée en travers sur cette cuisse.
   Ce qui ne tient pas : « la masse sombre centrale est la chevelure qui
   pend ». Dans `baki_clair.png` (luminosité x1,8), cette masse monte sans
   interruption jusqu'au BORD HAUT du cadre (y = 0 à 420 sur 739). Elle a la
   même texture brun-rouge, le même liseré clair à droite et le même flou que
   les autres troncs du fond. C'est plus vraisemblablement un tronc (au
   premier plan ou superposé) qui cache la tête. Aucun visage n'est lisible,
   donc « tête baissée » est une déduction et non une observation. « Coude
   haut » ne se voit pas non plus dans le zoom. Le lecteur a aussi omis l.41
   (« le perso charge son poing à son arrière droit »), qui tempère la lecture
   « pas derrière » : Milan situe bien la charge à l'arrière droit. Ce qu'il
   refuse le 09-26 (l.195), c'est le BRAS TENDU derrière.

2. **La tête « baissée » est une élévation MONDE de -15 à -30°. Verdict :
   confirmé avec nuance.** Recalculé : baki_R6 donne une tête à -66,9° dans le
   monde, ligne_R6d une tête à +20 par rapport au torse et -23,9 dans le monde,
   et v6_250 un buste penché de +20 avec une tête à +11,5 dans le monde et
   +14,6 par rapport au torse. Sur `nous_v6.json`, entre 3,1 et 4,45 s, la
   tête reste à +11/+12 dans le monde et entre +13,5 et +23,5 par rapport au
   torse. C'est exact. Pour les M1 pros, la plage -12/-31 vaut pour tsb_M1
   (-26/-12), tsb_M2 (-31/-12), tsb_M3 (-18/-11), pack_2M1_2 (-31/-22) et
   pack_2M1_4 (-26/-18). Deux exceptions n'ont pas été dites :
   - **tsb_M4 monte à +17,1** (buste renversé en arrière de -41,5, t = 0,22) ;
   - **pack_2M1_1 part de 0**.

   Il faut aussi préciser ce que font les pros. Avec un buste penché de 32 à
   37° (tsb_M2), leur tête reste presque NEUTRE par rapport au torse (+2,3 à
   +2,8) et atterrit à -27/-31 dans le monde. Le relèvement de +20 n'est donc
   nécessaire qu'au-delà d'environ 40° de penché. Ce n'est pas une règle
   générale « relever la tête ».

3. **Une diagonale de dessin se pose en directions MONDE. Verdict :
   confirmé.** Relancé : avec ligne_R6, le bras frappe à az -21 el +16 ; avec
   ligne_R6b (penché décomposé en 26 + 40 et bras visé dans le monde), il
   frappe à az +0,0 el +5. Sur la vue de profil de `verif_poses3.png`, le bloc
   rouge de ligne_R6 est presque vertical ; celui de R6b bascule vers le bras
   vert. Le lien avec « part du bas » reste, comme le lecteur l'a écrit, une
   hypothèse non mesurée.

4. **La jambe arrière R6 ne tient pas la longue diagonale. Verdict :
   confirmé, et c'est même plus large que ce qui est dit.** Dans
   `verif_poses4.png` (ligne_R6d, pied à 2,4, profil et 3/4 dos), le bloc
   jaune est séparé de la hanche. ligne_R6e (jambe posée par direction, az
   180, el -35) est attachée et donne bien un éclair : jambe et buste en
   diagonale, puis bras horizontal. Mais **ligne_R6 (pied à 3,2) a AUSSI la
   jambe détachée** (lignes.png, rang 1, profil et 3/4 dos), ce que le
   lecteur ne signale pas. Précision : le « détachement » vient de l'outil,
   qui place un pied hors d'atteinte. Dans Roblox, un Motor6D ne se détache
   pas : le pied n'arriverait simplement pas au sol. La conclusion (jambe de
   2 studs trop courte) reste vraie.

5. **Une pose de frappe en blocs ne se lit qu'en profil. Verdict : nuancé.**
   À 9 studs et 40° de champ, la vue de face donne bien un carré vert à côté
   de la tête et une silhouette compacte. En 3/4 dos, en revanche, le bras
   n'est pas « caché » : on voit un petit cube vert à droite du torse dans
   R6b, R6c, R6d et R6e, donc réduit mais visible. Surtout, la propre ref de
   Milan **5be18338 contredit la généralisation** : c'est une vue de FACE
   d'un R6 qui se lit très bien, parce que la caméra est collée au buste
   (tête coupée par le haut du cadre, tête énorme) et qu'il y a des lignes
   radiales et du vent autour du poing. Dans cette image, le poing n'est PAS
   plus gros que la tête : c'est la tête, la plus proche, qui grossit. Il
   faut donc lire « à 9 studs, seule la vue de profil se lit », pas « une
   pose en blocs ne se lit qu'en profil ».

6. **La plainte la plus constante porte sur la trajectoire « part du bas ».
   Verdict : confirmé avec nuance.** Les regex redonnent exactement les
   l.44, 53, 65, 104, 109, 113 et 190, et le total de 204 messages (198
   « dit » + 6 « dit_pendant_travail ») est juste. Trois nuances :
   - **l.65 est un brief collé** (coup de pied dans une roche). Il y a donc
     6 occurrences de Milan, pas 7, même si le lecteur l'a signalé en §7.6.
   - l.190 porte sur le Poing du Dragon, dit au passé (« quand dans poing du
     dragon le perso frappait vers le bas »).
   - Une 2e plainte de trajectoire est tout aussi constante et manque au
     résumé : **le coup qui part de l'ARRIÈRE** (l.53, l.54 « ne doit pas
     partir de derrière », l.55, l.195 « tu fais partir le poing de
     l'arrière »). Elle court du 09-04 au 09-26. La plainte de fond est
     donc « d'où part le poing » (du bas OU de derrière), pas seulement
     « du bas ».

7. **Les notes montent avec la mise en scène. Verdict : nuancé.** Les
   chiffres cités sont exacts, mais la liste en oublie une partie :
   - **l.176 contient aussi « 2/4 à tes VFX mais l'animation totale 4 »**
     (en plus de « 3/4 »), soit une note GLOBALE de 4 le 09-25, que le
     lecteur ne mentionne pas ;
   - 7,85 (l.186) est explicitement une note « totale ».

   L'interprétation des sauts est en partie fausse :
   - le passage de 3 à 6 (l.99) est motivé par « le jeu aérien », pas par
     la caméra ;
   - le départ ultra rapide est salué en l.191 (« le moment ultra rapide
     très bien »), mais la note **baisse** de 8 à 7, parce que l'objet
     change (nouvelle scène « Un seul coup ») et que le poing chargé n'est
     « toujours pas » bon.

   « Les plateaux restent sur le coup lui-même » tient (l.113, l.132, l.161
   « apart sur le coup final »).

8. **Milan inspecte au ralenti. Verdict : confirmé.** J'ai ouvert les 3
   captures. 8b32a1d7 (f453, 8,43 s) et f091ee86 (f513, 9,43 s) sont à 0,5x ;
   797cdcc7 (f548, 10,02 s) est à 1x ; toutes les trois sont en caméra
   Cinéma. Preuve supplémentaire que ce n'est pas l'état par défaut : dans
   `player_template.html`, l.77, le bouton 1x est `aria-pressed="true"` par
   défaut. Milan a donc CHOISI 0,5x. Autre précision : le bouton affiche
   « Lecture », ce qui veut dire que le lecteur était en PAUSE
   (`setPlaying` l.977 : « Pause » pendant la lecture, « Lecture » à
   l'arrêt). Il a donc arrêté l'image sur chaque plan pour la capturer. Les
   heures concordent : 22:15 et 22:16 en heure locale (UTC+2) correspondent
   à 20:15 et 20:16 UTC, soit environ 8 min avant l.183 (20:24 UTC).

### Oublis importants
- Baki : la « chevelure » est vraisemblablement un tronc du décor (il monte
  jusqu'au haut du cadre) ; la tête n'est pas lisible.
- l.41 (« charge son poing à son arrière droit ») : l'arrière est bien
  dans le vocabulaire de Milan ; il refuse le bras TENDU derrière et le
  départ du coup depuis l'arrière, pas la charge à l'arrière droit.
- Tête verrouillée sur la cible : pack_3Uppercut fait exception (la tête
  va de -56 à +45° d'azimut). Le verrou (±10 à 30°) ne vaut que pour les M1
  droits, qui tournent le buste de 111 à 162°.
- Dans 5be18338, c'est la TÊTE (la plus proche de la caméra) qui devient
  énorme, pas le poing. Le poing est vu de 3/4 sur le côté, dans un
  tourbillon de vent blanc. La ref R6 de Milan grossit donc la masse
  tête/buste, pas le poing.
- d2fda413 (vu) : outre le contour hérissé, le contraste d'ÉCHELLE vient
  d'un petit personnage au premier plan (Genos, en silhouette) devant le
  poing géant.
- l.176 : note globale 4 le 09-25 (voir point 7).
