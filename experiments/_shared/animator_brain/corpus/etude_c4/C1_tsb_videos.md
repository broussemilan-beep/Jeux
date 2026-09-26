# C1_tsb_videos — Chantier 4 : apprendre en regardant (vidéos TSB / Roblox)

Auteur : sous-agent C1 (Claude), 2026-09-26. Lecture seule du dépôt. Aucune image copiée dans le dépôt.

Sources (toutes dans `scratchpad/c4/src/archive/`, sha1 vérifié) :

| id | titre | sha1 (16) | durée | cadence source |
|---|---|---|---|---|
| 4e0sX6p8-30 | MORE Scrapped animations and concepts - TSB | 2dc5991318003b95 | 305,9 s | 30 i/s, 640x360, sans son |
| 6sXVqrZ_rYA | Slap (TSB) | c7526690f484bb3e | 21,4 s | 23,976 i/s |
| RhsY24ct-vQ | TSB Sunrise Finisher Concept | 9a8d936b2f59ea60 | 24,2 s | 30 i/s |
| lvB-wTylH3Y | SERIOUS PUNCH, Roblox VFX (Pew) | 4ea7509937eace7f | 16,4 s | 30 i/s |
| 2ka3-cCuHXg | Gojo's black flash sneak (Sorcerers BG) | 1f2730537200abf0 | 14,7 s | 30 i/s |

Aucune de ces vidéos n'a de piste son (ffprobe : pas de flux audio). Rien sur le son ici.

Méthode (reproductible) : planches-contacts horodatées faites avec ffmpeg (`frames/C1_tsb_videos/sheet.sh`,
drawtext = temps absolu de la vidéo), lues une par une avec Read. Cadences employées :
- vidéo de 5 min : planches à 2 i/s de toute la vidéo (`frames/C1_tsb_videos/scrap_2fps_01..31.jpg`), puis
  30 i/s sur les anims brutes (Vanishing kick 1-6,5 s ; HeadFirst 14,4-24 s ; Twin Fang 66,9-76 s ; psychic m1s
  202,1-205,1 s ; Ranged grab 220,4-225,4 s), 20 i/s (slam 205,4-211,8 ; Crush/Rock throw 225,4-230,8),
  10 i/s (Last Breath v4 152,6-163,4 ; custom interaction 163,4-170 ; Earth-Splitting 84,3-104 ; Downwards throw),
  5 i/s (storyboard 211,9-220,5), 3 i/s (104-164, 188-195, 237,8-305,9, 23,9-36).
- vidéos courtes : 6 i/s en entier, puis 24-30 i/s sur les moments d'action (Pew 2,2-6,1 ; Slap 13,4-19,8 ;
  Sunrise 1,2-6,6 et 12,2-15,6 ; Gojo 6,0-9,3).
- mesures outillées (numpy sur images réduites 64x36) : détection des coupes (différence moyenne entre
  images > 35/255) et part de blanc/noir image par image autour de la carte inversée de Pew.

Honnêteté sur ce que j'ai vu / pas vu : voir la section « Non couvert » à la fin. Point important : lors de
ma première passe, une série de lectures d'images a été refusée par l'outil (« request limit ») ; je les ai
relues ensuite. Tout ce qui est marqué « vu » ci-dessous a été effectivement affiché.

Rappel du cerveau fait avant d'écrire (`outils/rappel.py --court`) sur : « anticipation poing chargé »,
« caméra plan coupe », « animation brute storyboard », « pose forte silhouette ». Études existantes relues :
`corpus/tutos/ETUDE_ARCHIVE_VIDEOS_1_2026-09-25.md` (ces 5 vidéos à 1 i/s, angle VFX surtout),
`corpus/RELECTURE_LAST_BREATH_GOKU_2026-09-25.md` (Last Breath v1-v3 à 0,1 s), `corpus/fiches/UN_SEUL_COUP.md`.
Je n'ai pas refait Last Breath v1-v3 en détail (déjà fait à 0,1 s) ; je l'ai revu à 3 i/s pour le situer.

---------------------------------------------------------------------------------------------------

## PARTIE 1 — Par source

### 1.1 « MORE Scrapped animations and concepts - TSB » (4e0sX6p8-30) — la cuisine des animateurs

#### Ce que la vidéo EST (vu)
Un montage de ~20 animations ou concepts abandonnés, chacun titré en haut (« Vanishing kick V1 »,
« HeadFirst Finishers », « Martial Artist Awakenings », « Twin Fang first concept », « Earth-Splitting Strike
miss version (Projectile) », « … rough concept », « Last Breath v1..v4 », « Custom interaction "Hit a martial
artist with crushed rock" », « Gojo entrance », « Wild psychic awakening (Meteor shower AOE) », « Wild psychic
m1s », « Wild psychic slam aoe », « Ranged grab (not lock on) », « Crush », « Rock throw », « Downwards throw
variant », « Flowing water finisher », « Serious sneeze », « Ice boss stuff », « Gojo wallcombo », une anim d'épée
à la fin). Carton d'ouverture (0-1 s, lu) : « Credits to animators in bottom left (No icon if I made it) /
Clarifying References in bottom right ». En bas à gauche : l'avatar de l'animateur (plusieurs animateurs
différents : pseudos lisibles « egor77 », « LeftRight », « mel », « 55Epa », « Orion », « bc », « Veil »,
« askeli », « oatmeal v2 »). En bas à droite, quand il y en a : la référence dont l'anim s'inspire.

#### A. Les logiciels et la place du rig (vu)
- **Moon Animator 2 dans Roblox Studio** (Vanishing kick V1, 1,1-6,5 s) : fenêtre orange « Moon Animator -
  Supported by… » en bas à droite, liste de fichiers « Concept / Concept Autosave 08-0… ». Un gizmo 3 axes
  (rouge / vert / bleu) est planté **au centre du torse** = la pièce racine (HumanoidRootPart) sélectionnée.
  Vu 1,13-5,97 s (planches vk30_01..05) : le gizmo reste orienté pareil pendant que tout le corps fait des
  vrilles autour de lui → la rotation du corps entier (salto, vrille) est portée par la RACINE, et le gizmo
  reste le pivot.
- **La racine voyage** : 3,40-3,67 s, le personnage sort complètement du cadre à droite puis revient (3,70 s)
  en vrille basse (vk30_03). La caméra de Moon est fixe ; c'est donc la translation de la racine, clé par clé,
  qui fait le déplacement (le « dash » est dans l'anim, pas dans un script de vélocité) — **déduit** du fait
  que la caméra ne bouge pas et que le perso part de plusieurs studs.
- **Blender** : « Vanishing kick Finisher » (9-14,4 s), « Last Breath v1 (Use) » (104-107,3 s, un serpent-dragon
  modélisé, nom de fichier lisible « SuiryuDragonSpinv4.blend »), « Ice boss stuff » (260,5-290 s). Viewport
  gris foncé, grille rouge/verte, petites poignées colorées sur les os (vkfin_02, points verts/roses).
  Ce qu'on voit en Blender : des avatars avec accessoires (cheveux, bois de cerf, griffes de glace, fléau) —
  **déduit** : Blender sert quand il y a autre chose que les 6 blocs R6 (accessoires, dragon, arme sur chaîne).
- **Trajectoires affichées dans Blender** : « Ice boss stuff » 283,1-289,8 s (a238_04/05) : un fléau violet
  au bout d'une chaîne, et une **ligne pointillée blanche** qui dessine la trajectoire de la tête du fléau
  autour du perso (motion path). **Vu**. L'animateur regarde l'ARC de l'arme comme un objet à part entière.
- **Le rig lettré et coloré** (Last Breath v4, psychic m1s, slam, Ranged grab, Crush, Rock throw, HeadFirst,
  Earth-Splitting, Ice boss vs mur) : chaque FACE de chaque bloc a une couleur ET une lettre selon sa direction
  locale : **F rouge (avant), B bleu (arrière), R vert (droite), L jaune (gauche), U cyan (haut), D orange (bas)**,
  et « FRONT » / « BACK » écrit en grand sur le torse. **Vu** partout (ex. m1b_01 : « FRONT » rouge de face à
  202,1 s, puis bras vert « R » quand il se tourne à 202,6 s ; Rock throw 229,75 s : « BACK » bleu quand le
  torse a tourné). Ce que ça permet (**déduit**) : lire d'un coup d'œil, sur n'importe quelle image, l'orientation
  de chaque bloc. Ex. un bras dont on voit la face orange « D » = on regarde le bout de la main, donc le bras
  pointe vers la caméra (cr_01, 225,4-225,8 s : bras levé, face D visible). Sur un R6, un bloc qui « pointe »
  vers la caméra est illisible en gris ; avec ce rig, il ne l'est plus. C'est un outil de CONTRÔLE des poses.
- **Deux rigs dans le même fichier, animés à la main** : attaquant ET victime sont des rigs lettrés, posés clé
  par clé. HeadFirst Finishers (egor, 48,5-51 s, lu à l'écran) : annotation manuscrite « I did Victim :D »
  avec une flèche vers la victime, et « Egor His → » vers l'attaquant. **Lu** : deux animateurs se partagent
  une interaction, l'un fait la victime, l'autre l'attaquant.
- **Une référence vidéo collée à côté** : Twin Fang (66,9-68,2 s, tf_01) : incrustation « Serum W » en bas à
  droite, une vidéo qui défile en même temps ; Wild psychic awakening (197,6-201,3 s, gp_01/02) : incrustation
  d'un combat d'anime (perso à aura verte) synchronisée avec l'anim Roblox. **Vu**. **Déduit** : ils animent
  à partir d'un extrait de référence, et la présentent à côté pour dire « c'est ça que je vise ».

#### B. Le storyboard (animatic) (vu, 211,9-220,4 s, sb_01/02, 5 i/s)
- Bonhommes bâtons noirs sur blanc, cible = **cercle rouge**, effet de saisie = **nuage vert**, notes écrites
  en bleu « Ranged grab (not lock on) » et « Ranged grab (use 1,2,3,4 for end attack) » (**lu**).
- Ce n'est pas une planche fixe : c'est un **animatic** (dessins qui s'enchaînent dans le temps, ~8 s, joué
  deux fois 212,3-215,9 et 216,3-220,1 avec de petites variantes). Les cases changent environ toutes les
  0,2 s dans ma planche (je ne peux pas dire plus fin à 5 i/s).
- Ce que le storyboard décide déjà (vu) : les CADRAGES (tête en gros plan 212,3 ; plan large perso + cible
  lointaine 212,9 ; cible ramenée tout près en premier plan 213,3 ; contre-plongée 213,7), **l'impact en case
  abstraite plein cadre** (213,9 : traits blancs rayonnants sur noir), le sol qui casse (214,1-214,3 débris),
  une spirale rouge = tourbillon (214,5-214,7), un arc rouge = balayage (215,3), la cible devenue ÉNORME
  à côté d'un perso minuscule (215,5 : jeu d'échelle).
- Puis l'anim brute (220,4 s « Ranged grab ») est faite en caméra FIXE de Studio, sans aucun de ces cadrages.
  **Déduit** : l'ordre est storyboard (cadrages + moments clés) → anim du corps en plan fixe → caméra et effets
  ensuite. La note « use 1,2,3,4 for end attack » (lu) = le coup final réutilise les 4 M1 existants : on
  recycle des anims déjà faites.

#### C. Ce que montrent les anims BRUTES, sans effets (vu, compté image par image)
Précaution : la vidéo est à 30 i/s ; je compte des images vidéo, pas des images-clés. Ces anims ont pu être
jouées à 60 i/s dans Studio puis capturées : je ne sais pas.

1. **Wild psychic m1s** (202,1-205,1 s, m1b_01, 30 i/s, cadrage serré) — le rythme d'un M1 :
   - 202,10-202,47 : pose de garde de face, ~12 images quasi immobiles.
   - 202,50-202,57 : rotation du buste vers le profil en ~3 images.
   - 202,60-202,83 : tenue profil, bras armé, ~8 images.
   - 202,87-202,93 : déroulé en ~3 images → 202,97-203,23 : pose ouverte bras écartés de face, ~9 images tenues.
   - 203,27-203,37 : ~3 images de transition → 203,40-203,97 : pose de côté bras droit devant, ~17 images.
   - 204,00-204,07 : ~3 images → 204,10-204,70 : pose accroupie très basse, ~18 images avec une dérive lente.
   Lecture : **des poses tenues de 8 à 18 images, reliées par des transitions de 2 à 4 images.** Le mouvement
   rapide ne dure presque rien ; ce qu'on VOIT, ce sont les poses. Statut : vu (comptage sur planche).
2. **Wild psychic slam aoe** (205,4-209 s, slam_01..03, 20 i/s) :
   - 205,45-205,55 : les deux bras montent (≈0,15 s) → 205,60-205,85 tenue bras au-dessus de la tête (≈0,3 s).
   - 205,90-206,55 : le corps tombe en accroupi bas, bras encore hauts, tenu ≈0,55 s.
   - 206,60-207,05 : torsion, on passe au dos (le torse montre sa face orange/jaune puis bleue).
   - 207,10-207,55 : il se redresse penché en avant, bras en l'air.
   - **207,60 : une seule image où il s'écrase au sol** (le corps tout entier tassé) ; 207,65-207,75 : pose
     immense de dos, bras écartés en haut ; 207,80-208,35 : écrasé bas ; 208,40-209,00 : il se relève doucement.
   - La victime (rig jaune « L ») reste debout et immobile à côté : **elle sert d'étalon d'échelle** (déduit).
3. **Crush** (224,4-228,35 s, rg_05 puis cr_01..03, 20 i/s) :
   - 224,40-225,80 : pose tenue ≈1,4 s : bras droit levé très haut en diagonale (face « D » visible = on voit le
     bout du bras), une jambe levée. Immobile.
   - 225,85-226,10 : le bras descend en travers (≈0,25 s) vers une garde.
   - 226,15-226,70 : garde tenue ≈0,55 s ; 226,75-226,85 : ~3 images de bascule ; 226,90-227,35 : retour bras
     levé, tenu ≈0,45 s (deuxième armé).
   - **227,40-227,45 : le bras s'abat en 1-2 images** (écrasement) ; 227,50-227,65 : tenue basse ;
     227,70-228,30 : récupération en ≈0,6 s vers une pose neutre.
   Lecture : armé TENU longtemps (0,45-1,4 s), frappe en 1-2 images, puis récupération plus longue que la frappe.
4. **Rock throw** (228,9-230,75 s, cr_03/04) : ramasse (228,95-229,25), bras écartés, bras gauche tiré en
   arrière (229,30-229,55), **lancer avec rotation du corps d'environ un demi-tour en ~3 images (229,60-229,75 :
   on passe de « FRONT » rouge à « BACK » bleu)**, puis **follow-through tenu ≈1 s (229,80-230,75), dos à la
   caméra**, bras tendu devant. Le corps sur-tourne au point de montrer le dos. (vu)
5. **Ranged grab** (220,47-224,4 s, rg_01..05, 30 i/s) : visée bras tendu tenue ≈0,45 s (220,47-220,90) ;
   accroupi-anticipation 3 images (220,93-221,00) ; demi-tour ; puis une longue séquence de boules / vrilles
   (221,43-222,40 : corps roulé en boule, ≈1 s) ; enchaînements de poses toutes les 0,1-0,3 s ; fin sur une
   grande pose bras levé tenue ≈1 s (224,37-225,33). (vu)
6. **Vanishing kick V1** (Moon, 1,13-5,97 s) : garde tenue ≈0,7 s (1,13-1,87) ; vrille aérienne en ≈0,4 s
   (1,90-2,30) ; atterrit accroupi (2,33-2,97) ; se relève (3,0-3,37) ; **sort du cadre en 0,27 s** (dash) ;
   revient en coup de pied tournant bas (3,70-4,37) ; se remet (4,40-4,97) ; recommence (5,07-5,97).
   En jeu (6,57-8,9 s, caméra fixe très large) : il glisse bas depuis loin jusqu'à la victime en ≈0,5 s. (vu)
7. **HeadFirst concept** (14,6-16,4 s, hf_01/02, 30 i/s) : **14,60-15,17 : les deux persos FIGÉS en l'air
   pendant ≈0,57 s** (l'attaquant en coup de pied, la victime penchée) — une vraie pose tenue en plein vol ;
   coupe ; 15,20-15,60 : attaquant immobile, loin, ≈0,4 s ; **15,63 : il part d'un coup** en glissade tournante
   (≈0,4 s) et percute la victime (≈16,03) qui s'envole ; pose finale tenue dès 16,07. (vu)
8. **HeadFirst Finishers** (18-36 s, LeftRight / mel / egor) : prise au corps à corps entre deux rigs
   (18,0-18,3 tenue), l'attaquant enroule et soulève (18,3-18,97), jette la victime en l'air (20,0-21,0) ;
   23,5-24,1 les deux en l'air ; 24,17 : le plan passe au noir et **24,3-35,9 s (≈11,6 s) les deux persos ne
   sont plus que des points minuscules dans un vide noir** (caméra restée très loin). Je ne peux pas lire ce
   qu'ils font à cette taille (**non vu en détail**, limite de résolution 640x360).
9. **Last Breath v4** (152,6-163,4 s, lb4_01..03, 10 i/s) — **anim brute avec rigs lettrés, mais la CAMÉRA
   est déjà animée et coupée** :
   - 152,9-153,5 : gros plan des deux rigs emmêlés (prise) ; 153,6-153,7 : fouetté ; 153,8-154,3 : plan
     penché, victime projetée ; 154,5-155,1 : contre-plongée proche sur l'attaquant ;
   - **155,2 et 160,1 : images grises vides** (la caméra regarde un sol vide) — **déduit** : ce sont les
     trous réservés aux flashs / cartes plein écran qui seront ajoutés ensuite ;
   - 155,5-156,4 : très gros plan : la tête de l'attaquant et un bras GÉANT en amorce (face « B » bleue qui
     remplit la moitié de l'image) ≈0,9 s ;
   - 156,8-157,3 : vue lointaine, victime qui tombe ; 157,7-158,6 : plan large fixe sur l'attaquant **roulé en
     boule (charge) ≈0,9 s**, caméra qui glisse doucement ;
   - 158,7-159,2 : gros plan des bras qui se croisent ; **159,3-160,0 : contre-plongée frontale qui avance sur
     le torse « FRONT », bras qui s'ouvrent (la libération) ≈0,7 s** ;
   - 160,2-161,5 : gros plan de l'attaquant en fente, tenu ≈1,3 s ; 161,6-162,2 : plan moyen de dos ;
     **162,3-163,3 : plan très large, perso minuscule** (la conséquence).
   La grammaire de Last Breath v1 (en jeu, avec effets : RELECTURE_LAST_BREATH) est déjà là dans la v4 brute :
   serré sur la prise → large → charge en boule → libération frontale en contre-plongée → très large.
10. **Earth-Splitting Strike** : « miss version » (76,2-84,5 s, vide noir, sol gris-vert plat) : l'attaquant fait
    jaillir une énorme dalle de roche (77,03) ; « rough concept » (84,6-93,5 s, dans Studio avec une tête de
    dragon violette posée comme effet provisoire et une dalle vert sombre) ; version propre (93,6-104 s, vide
    noir) : la victime part très haut et longtemps (95-104 s), petite dans le cadre. **Plusieurs versions du
    même coup** (miss / rough / propre). (vu, 2 et 10 i/s)
11. **Custom interactions** (163,4-195,3 s) : caméra de Studio fixe, plan moyen-large, un seul plan pour toute
    l'interaction (esquive, saisie, projection). (vu, 3-10 i/s)
12. **Gojo entrance** (195,5-197,6 s) : un seul geste lent : le bras droit balaie devant le corps sur ≈1 s
    (195,5-196,5) puis le perso reste debout immobile ≈1 s. Une « entrée » = un geste + une tenue. (vu)
13. **Serious sneeze** (253,4-260,4 s) : un petit geste (éternuement) → la victime (rig lettré) est envoyée
    très haut et reste en l'air plusieurs secondes. Disproportion comique entre la cause et l'effet. (vu, 3 i/s)
14. **Flowing water finisher** (237,9-253,3 s) : d'abord en jeu, plan large (237,9-243,8), puis la version
    cinématique (244,1-253,1) : plans par-dessus l'épaule, plans sombres avec des yeux jaunes, et **pose finale
    en contre-plongée : l'attaquant accroupi sur la victime au sol, ≈3,3 s quasi immobile** (249,8-253,1). (vu)
15. **Twin Fang first concept** (66,9-76,2 s, tf_01..05, 15 i/s) : la caméra est presque TOUJOURS collée :
    derrière l'épaule / la nuque (67,0-68,6 : la moitié de l'image = cheveux et épaule en amorce), puis plan
    bas des deux corps qui se percutent (68,7-68,9), plan moyen (69,4-70,5), plongée verticale sur le chapeau
    (70,6-71,9), très gros plan visage de la victime avec une main en amorce (72,6-73,2), plans en vrille
    (74,2-74,8), puis **plan final : tête de la victime écrasée au sol sous le bras, tenu ≈1,3 s**
    (74,9-76,2). Plans de 0,5 à 1,5 s. (vu)

#### D. Ce que ça m'apprend sur la FABRICATION (déduit, à partir du vu ci-dessus)
- L'anim se fait d'abord **en plan fixe large** (Moon/Studio), le perso entier visible, avec la victime à côté
  comme étalon. Le rig lettré sert à vérifier chaque pose sous tous les angles.
- Les versions sont nombreuses et assumées (Last Breath v1→v4, Earth-Splitting miss/rough/final, « first
  concept »). Plusieurs animateurs, parfois deux sur une même interaction.
- La référence (anime, autre jeu) est posée à côté ; le storyboard fixe cadrages et moments clés.
- La caméra peut être animée dans le même fichier dès la version brute (LB v4), avec des « trous » gardés pour
  les flashs.
- Les effets sont ajoutés en dernier et, au stade « rough », sont des placeholders (tête de dragon plate
  réutilisée d'un concept à l'autre : 56,5 s puis 69,4 s puis 84,6 s — **vu** : la même tête violette apparaît
  dans Martial Artist Awakenings, Twin Fang et Earth-Splitting rough).

---------------------------------------------------------------------------------------------------

### 1.2 SERIOUS PUNCH (Pew, lvB-wTylH3Y) — 16,4 s dont générique 14,67-16,4

Découpage **mesuré** (coupes détectées, images 30 i/s) et **vu** (pew30_01/02, 30 i/s) :

| temps (s) | plan | ce que fait le corps |
|---|---|---|
| 0-0,83 | moyen, léger contre-plongée, perso de dos-3/4 | garde, petits gestes |
| 0,83-2,27 | la caméra descend et tourne lentement autour, anneau au sol | tenue, presque immobile |
| **2,27-2,60** | **fouetté de caméra vers le ciel** (coupes mesurées 2,27-2,40 = changements d'image énormes) | — |
| 2,63-3,50 | plan moyen en plongée, 3/4 face | **accroupi, bras rassemblés devant, ≈0,9 s quasi immobile** |
| 3,53-3,70 | la caméra fonce vers la tête en ≈5 images | — |
| 3,73-3,80 | très gros plan de la tête par dessous, haut du crâne blanc lumineux (3 images) | — |
| 3,83-4,60 | caméra collée derrière l'épaule gauche | **tenue ≈0,75 s**, micro-mouvements seulement |
| 4,63-4,80 | idem | une bouffée de fumée naît au poing (le départ) |
| 4,83-5,00 | la caméra tourne vite ; le bras/manche noir passe en amorce plein cadre | la rotation du coup |
| 5,03-5,10 | plan de face, 2 images | pose de frappe |
| **5,13-5,33** | **carte inversée : 7 images** (mesuré : 47-59 % de pixels blancs, 23-36 % noirs ; avant et après ≈4 % / 2 %) | silhouette noire sur blanc, roches noires |
| 5,37-5,67 | retour 3D, même cadrage, **des roches sont maintenant là** | follow-through tenu, bras tendu |
| **5,70-14,67** | **coupe en plan très large, perso minuscule au centre, ligne de roches noires fendues** | presque immobile ; 12,3-13 s les roches s'enfoncent/disparaissent ; 13-14,6 s sol vide |

Ce que je retiens :
- **Le contact n'est jamais montré en 3D.** On voit : épaule collée (tenue) → le bras qui balaie la caméra →
  2 images de pose → 7 images de carte → la pose d'APRÈS, déjà dans un monde changé (les roches). (vu)
- La tenue n'est pas « un corps figé » : c'est un corps presque immobile filmé par une caméra qui bouge
  (descente lente, fouetté ciel, ruée vers la tête). **Le mouvement pendant la charge est porté par la caméra,
  pas par le corps.** (vu + déduit)
- Rapport de durées (mesuré) : charge ≈5,1 s (0 → 5,13), carte 0,23 s, conséquence tenue ≈9 s (5,70 → 14,67).

**Contradiction avec l'étude existante** (`ETUDE_ARCHIVE_VIDEOS_1`, même sha1 4ea7509937eace7f) : elle place le
fouetté vers le ciel à 3,3-3,5 s, la carte à « 6,2-6,3 s, 2 images » et la coupe large à 6,7 s. Mesuré ici :
fouetté 2,27-2,60, carte **5,13-5,33 s = 7 images (0,23 s)**, coupe large **5,70 s**. Écart ≈ +1 s et « 2 images »
est faux si on parle d'images vidéo (à un pas de 0,1 s, 0,23 s donne 2-3 échantillons : c'est probablement
l'origine). La fiche `UN_SEUL_COUP.md` (tenue Pew 3,9-4,6 s) est, elle, cohérente avec mes temps.

### 1.3 Slap (TSB, 6sXVqrZ_rYA) — 21,4 s à 23,976 i/s

(vu : slap_01..04 à 6 i/s, slap24_01/02 à 24 i/s de 13,4 à 19,8 ; coupes mesurées)
- 0-13,6 s : caméra de jeu (plan large derrière le joueur) ; 0,67-1,67 anneau d'emote ; 10,5-11,4 grands signes
  rouges « K )) » en surimpression et étincelles. Le joueur s'approche lentement de la victime.
- **13,65-16,40 : ≈2,75 s de très gros plans désaturés** (presque noir et blanc), 6 plans (coupes mesurées
  13,76 / 14,39 / 15,01 / 16,43) : visage de la victime sous le chapeau (dolly avant), l'attaquant en plan
  rapproché dans la fumée dont le bras balaie la caméra et fait un volet au noir (14,19-14,23), le chapeau,
  **plan au ras du sol : des jambes noires qui avancent et une main gantée blanche (14,40-15,0)**, le gant en
  gros plan (15,0-15,3), le bord du chapeau avec cigarettes qui glisse (15,3-16,0), le visage sous le chapeau
  qui sourit (15,9-16,4).
- **16,44-19,48 : ≈3 s de planches manga** (24 i/s, vu) : trait rouge plein écran (16,44), éclairs de trait noir
  sur blanc (16,48-16,57), un faisceau rouge sur noir (16,60-16,78), puis cases de trait noir/rouge avec lignes
  de vitesse (16,82-17,65), 2 images rouges (17,69-17,73), 1 noire (17,78), cases (17,82-18,35), **le visage de
  la victime déformé par la gifle, ≈0,85 s (18,40-19,23)**, lignes de vitesse horizontales (19,27-19,36), rouge
  (19,40-19,44), noir (19,48).
- 19,52 : retour 3D, la victime projetée avec traînée rouge vers le mur.
- Mesuré : dans la zone manga, les coupes tombent à 16,43 / 16,47 / 16,56 / 16,60 / 16,64 / 16,73 / 16,81 puis
  17,43 / 17,60-17,85 (presque chaque image) / 18,02 / 18,23 / 18,35 / 18,89 … / 19,23-19,52 (chaque image).
  **Rythme : rafale de cases de 1-3 images, puis une case LONGUE (le visage, ~0,5-0,85 s), puis rafale de fin.**
- Ce que je retiens : **la gifle elle-même n'existe pas en 3D.** Le corps de l'attaquant n'est montré qu'en
  morceaux (jambes, gant, chapeau, sourire) pendant la montée ; le coup est dessiné.

### 1.4 Sunrise Finisher (concept, RhsY24ct-vQ) — 24,2 s

(vu : sun_01..04 à 6 i/s, sunA à 20 i/s 1,2-6,6, sun30 à 30 i/s 12,2-15,6 ; coupes mesurées)
| temps (s) | plan | action |
|---|---|---|
| 0-1,2 | carton titre | — |
| 1,23-1,63 | plan moyen en jeu | l'attaquant (sabre) frappe une victime vers le haut |
| 1,65-1,95 | flash bleu, particules | — |
| **1,95-2,80** | **plan TRÈS large, ciel bleu nuit, perso minuscule en bas** | il marche |
| 2,83-4,20 | très gros plans qui glissent sur le corps (garde du sabre, fourreau, épaule, chapeau) | marche |
| 4,23-4,80 | très gros plan visage : sourire, puis clin d'œil (4,65-4,75) | — |
| 4,80-6,33 | **un seul mouvement de caméra continu** : du large au serré, le perso avance vers la caméra en dégainant | — |
| 6,33-6,47 | éclair ; 6,45-6,55 **un trait blanc horizontal traverse l'écran** (la coupe) | — |
| 6,47-7,97 | la victime **figée** en l'air, ≈1,5 s | conséquence retardée |
| 8,0-9,1 | dôme de verre rayé de coupes | — |
| **9,13-9,53** | **stroboscope : une coupe à presque chaque image** (mesuré : 12 coupes en 0,4 s) | — |
| 9,53-15,43 | **un seul plan de ≈5,9 s** (mesuré : aucune coupe) : l'attaquant, dos à la victime, **rengaine lentement** (12,2-13,4 s : la lame glisse au fourreau, arcs bleus puis orange) | — |
| 13,43 | 1 image : kanji « 旭 » (lever de soleil) noir | — |
| 13,47-13,60 | boule blanche | — |
| 13,63-14,80 | explosion rouge avec le kanji incrusté, sur la victime | — |
| 15,37-15,43 | bord de dôme rouge ; 15,43 coupe | — |
| 15,43-16,1 | explosion jaune-orange plein écran (le soleil) | — |
| 16-17,6 | fumée, fondu au noir ; 17,6-24,2 générique (lu : VFX help « Kanji Symbol Explosion », « Fire », « Slash Barrage » ; Sound design « ALL SFX » ; musique) | — |

Ce que je retiens :
- **Le déclencheur est un geste LENT** : l'explosion part quand la lame finit d'entrer dans le fourreau
  (13,43 s), pas au moment de la coupe (6,45 s). Le corps est calme, dos tourné. Cause lente → effet énorme.
- Contraste d'échelle : très large minuscule (1,95-2,8) collé à des très gros plans (2,83-4,8). (vu)
- Le plus long plan (5,9 s) est celui où il ne se passe « rien » de rapide. (mesuré)

### 1.5 Gojo's black flash sneak (Sorcerers BG, 2ka3-cCuHXg) — 14,7 s

(vu : gojo_01..03 à 6 i/s, gojo30 à 30 i/s 6,0-9,3 ; coupes mesurées)
- 0-0,80 : plan en jeu, contre-plongée, un perso en veste noire en l'air au-dessus de l'autre (Gojo cheveux
  blancs en bas à gauche).
- **0,80-5,37 : champ / contrechamp de très gros plans des deux visages.** Durées mesurées des plans :
  1,07 / 0,76 / 0,57 / 0,50 / 0,33 / 0,40 / 0,34 / 0,26 / 0,34 s. **Les plans raccourcissent** (1,07 → 0,26 s).
- **5,37-6,63 : puis UN plan long de 1,26 s** qui pousse lentement vers le visage de Gojo (le calme juste avant).
- 6,33-7,17 : un poing (bloc beige) entre et remplit le cadre en glissant lentement devant le visage, ≈0,8 s,
  le cadre devient sombre (7,0-7,17).
- 7,20-8,20 : noir total avec traits cyan (étincelle, anneau qui grossit 7,30-7,37, anneaux brisés, spirales
  qui convergent vers un point 7,67-8,13). ≈1 s.
- 8,20-8,30 : éclat blanc déchiqueté sur noir (inversion qui monte) ; **8,33-8,80 : blanc total, une petite
  silhouette sombre au centre qui rapetisse jusqu'à un point** (8,40 → 8,63) ; 8,83-9,07 : trait noir, contours
  déchirés, inversion.
- 9,10-11,37 : plongée verticale derrière Gojo, immobile, ≈2,3 s. 11,37-12,43 : gros plan d'un perso aux
  cheveux noirs qui sourit, cheveux blancs en amorce. 12,43-14,67 : plan rapproché sombre du corps à genoux.
- Ce que je retiens : l'accélération des coupes fabrique la tension ; **le dernier plan avant le coup est
  LONG** ; le coup lui-même = un bloc qui remplit l'écran puis de l'abstraction ; la conséquence = une
  silhouette qui rapetisse dans le blanc (on comprend « projeté au loin » sans le voir). Je ne peux pas
  affirmer avec certitude qui frappe qui (le poing beige entre dans le champ du visage de Gojo) : **incertain**.

---------------------------------------------------------------------------------------------------

## PARTIE 2 — Les grands enseignements (apprentissages, pas règles)

### E1. Dans ces 5 vidéos, le moment du contact n'est jamais une pose 3D montrée (vu)
Pew : 7 images de carte inversée à la place du contact. Slap : la gifle est une suite de cases manga. Sunrise :
un trait blanc horizontal. Gojo : un bloc qui remplit le cadre puis noir. Même dans l'anim brute Last Breath v4,
il y a une image grise vide là où ira le flash (160,1 s). **Ici, l'animateur ne cherche pas « la bonne pose de
contact » : il la cache, parce que l'œil ne lit pas une pose de 1 image ; il lit l'avant (tenue) et l'après
(follow-through tenu dans un monde changé).** Les poses 3D que le spectateur retient sont la tenue de charge
et la pose d'après.

### E2. Pendant la charge, c'est la caméra qui bouge, le corps tient (vu)
Pew : 0,9 s accroupi quasi immobile puis 0,75 s de tenue derrière l'épaule, pendant que la caméra descend,
fouette le ciel, fonce sur la tête. Sunrise : le perso marche calmement, la caméra glisse sur lui. Gojo : les
visages bougent à peine, les coupes accélèrent. **Ici l'énergie qui monte est dans le montage et la caméra ;
le corps garde une silhouette stable qu'on a le temps de lire.**

### E3. Le cadrage de charge recadre le corps en morceaux (vu)
Chapeau, gant, fourreau, nuque, visage, épaule en amorce, un bras géant qui remplit la moitié de l'image (LB v4
155,5-156,4 ; Twin Fang 67-68,6 ; Slap 13,65-16,4 ; Sunrise 2,83-4,8). Le corps entier n'apparaît en charge
que rarement (Pew 2,63-3,5, en plongée). **Déduit** : un morceau de corps très grand dans l'image = présence,
poids ; le corps entier petit = vulnérabilité ou échelle du monde.

### E4. Contraste d'échelle très large / très gros plan (vu, mesuré)
Sunrise 1,95-2,8 (minuscule) contre 2,83-4,8 (très gros) ; Pew 5,70-14,67 (minuscule, 9 s) après 3,73 (crâne
plein cadre) ; LB v4 162,3 (minuscule) après 160,2-161,5 (fente en gros plan) ; storyboard 215,5 (cible
énorme, perso minuscule). **La conséquence est montrée en très large, le perso petit, et tenue longtemps.**

### E5. Rythme des poses dans les anims brutes : tenir longtemps, passer vite (vu, compté)
Psychic m1s : poses tenues 8-18 images, transitions 2-4 images. Crush : armé tenu 0,45-1,4 s, frappe 1-2
images, récupération ≈0,6 s. Slam : image unique d'écrasement (207,60) entre deux grandes poses. HeadFirst :
0,57 s figés en l'air, puis départ instantané. **C'est ce qui porte la lecture sans aucun effet** : des poses
qu'on a le temps de voir, reliées par des passages si courts qu'ils ne comptent presque pas visuellement.
(Nuance : la récupération après la frappe est plus lente que la frappe, 0,6 s contre 1-2 images.)

### E6. Le corps entier tourne, jusqu'à montrer le dos (vu)
Rock throw : demi-tour en ~3 images (FRONT → BACK), follow-through tenu dos à la caméra ≈1 s. Slam : torsion
où l'on passe au dos (206,6-207,05). Psychic m1s : le buste passe de face à profil en 3 images. **Grâce au rig
lettré on le VOIT : ce n'est pas un bras qui bouge, c'est le torse qui change de face.**

### E7. Le montage accélère puis ralentit juste avant le coup (mesuré)
Gojo : plans de 1,07 → 0,26 s puis un plan de 1,26 s. Slap : rafale de cases puis visage 0,85 s. Sunrise :
stroboscope 0,4 s puis plan de 5,9 s. **Ici, le long plan après la rafale est ce qui donne le poids** : le
spectateur a été secoué, puis on le laisse regarder.

### E8. La cause peut être petite ou lente, l'effet énorme (vu)
Sunrise : rengainer déclenche l'explosion. Serious sneeze : un éternuement envoie la victime au ciel. Gojo
entrance : un seul geste de bras puis la tenue. **La disproportion entre le geste et l'effet est elle-même
l'effet** (déduit) — c'est l'humour et la « classe » TSB (Saitama).

### E9. La victime est animée à la main, et c'est la moitié du travail (vu, lu)
HeadFirst (« I did Victim »), Crush/slam (étalon immobile), Earth-Splitting (la victime vole 9 s), Twin Fang
(tête écrasée tenue 1,3 s), Flowing water (pose finale 3,3 s sur la victime). La réaction de la victime, le vol,
la pose au sol sont posés clé par clé, pas laissés à la physique.

### E10. Méthode de fabrication observée (vu + lu + déduit)
1. une référence (anime / jeu) collée à côté ; 2. un animatic en bonhommes (cadrages, impact en case plein
cadre, échelle) ; 3. l'anim du/des corps en plan fixe large dans Moon (racine = pivot et porteur des
déplacements) ou Blender (accessoires, créatures, arme avec trajectoire affichée) ; 4. un rig lettré F/B/L/R/U/D
pour contrôler chaque pose ; 5. caméra animée, avec des trous pour les flashs ; 6. effets provisoires
réutilisés (même tête de dragon sur 3 concepts) ; 7. versions multiples ; 8. effets finaux, cartes, sons
(crédits Sunrise : VFX et son faits par d'autres personnes).

---------------------------------------------------------------------------------------------------

## PARTIE 3 — Surprises / contradictions avec ce que croyait le cerveau

1. **Temps de Pew décalés dans `ETUDE_ARCHIVE_VIDEOS_1`** (mesuré) : carte à 5,13-5,33 s (7 images), pas
   6,2-6,3 s « 2 images » ; coupe large à 5,70, pas 6,7 ; fouetté ciel 2,27-2,60, pas 3,3-3,5. Durée de
   conséquence ≈9 s jusqu'au générique (7 s avant que les roches disparaissent à ~12,3).
2. Le rappel du cerveau remonte un texte de Milan (04/09) : « Anticipation 4-6 frames lentes … Impact 1 seule
   frame ». Dans ces refs cinématiques, l'armé/la tenue dure des SECONDES (Pew ≈5 s ; Crush brut 0,45-1,4 s),
   pas 4-6 images, et « l'image d'impact » n'est pas une pose 3D : c'est une carte (Pew 7 images). Pour un M1
   (psychic m1s), les chiffres sont plus proches : transitions 2-4 images, mais tenues 8-18 images.
3. Je croyais (via les études précédentes) que « le rig lettré » était une aide de couleur par membre. **En
   fait c'est par FACE et par DIRECTION** (F/B/L/R/U/D, 6 couleurs), sur chaque bloc — c'est un outil de lecture
   d'orientation, plus fin que notre coloration par membre (`tour.py`).
4. Les anims brutes ne sont pas toutes « sans caméra » : Last Breath v4 a déjà ses coupes et ses cadrages, avec
   des images vides réservées aux flashs.
5. Le storyboard n'est pas une planche : c'est un animatic minuté et rejoué (deux passes).
6. Le « dash » de Vanishing kick sort du cadre : la translation est dans l'anim (racine), pas ajoutée par code
   (déduit, à confirmer sur un .rbxm).

---------------------------------------------------------------------------------------------------

## PARTIE 4 — Ce que je saurais refaire en R6, concrètement

- **Un « Crush » brut** (60 i/s dans Roblox) : clé 0 : bras droit levé haut en diagonale, face « D » vers la
  caméra, une jambe levée ; tenir ≈0,5-1 s (on peut ajouter une micro-dérive de 1-2°) ; clé de frappe : bras
  abattu devant-bas en 2 images (≈0,03 s), buste penché en avant, genoux pliés ; tenir 0,15 s ; revenir en
  ≈0,6 s en easing doux vers la garde. (d'après cr_01..03)
- **Un lancer avec sur-rotation** : ramasser, écarter les bras, tirer le bras arrière ; puis rotation du torse
  + racine d'environ 180° en 3 images ; follow-through tenu ≈1 s dos à la caméra, bras tendu. (Rock throw)
- **Un M1 « poses tenues »** : 3-4 poses nettes (garde face, profil armé, ouverture, attaque) tenues 8-18 images,
  transitions de 2-4 images. (psychic m1s)
- **Un plan de charge « façon Pew »** : corps accroupi, bras rassemblés, quasi immobile 0,9 s en plongée ;
  la caméra fonce sur la tête en 5 images ; plan collé derrière l'épaule, tenue 0,75 s ; fumée au poing ; la
  caméra tourne pendant que le bras passe en amorce (≈0,2 s) ; 2 images de pose ; **carte de 7 images** ;
  pose d'après avec le décor changé ; coupe en plan très large tenu plusieurs secondes.
- **Un montage de tension façon Gojo** : 9 plans alternés de 1,07 → 0,26 s, puis un plan long de 1,26 s,
  puis l'objet du coup en amorce plein cadre, puis abstraction.
- **Contrôle** : colorer chaque face du R6 par direction (6 couleurs) pour vérifier les poses sous tous les
  angles.

Ce que je ne saurais PAS faire / pas dire à partir de ces sources :
- les angles exacts des membres dans ces anims (pas de .rbxm de ces anims ; seulement la vidéo 640x360) ;
- les courbes d'interpolation (easing) utilisées entre les poses ;
- si les anims brutes étaient jouées à 30 ou 60 i/s dans Studio ;
- le contenu des 11,6 s de HeadFirst Finishers (points trop petits) ;
- qui frappe qui avec certitude dans le Black Flash de Gojo ;
- le son (aucune vidéo n'a de piste audio).

---------------------------------------------------------------------------------------------------

## PARTIE 5 — Suggestions pour Milan (à débattre, pas des règles)

1. Pour « Un seul coup » : arrêter de chercher LA pose de contact ; la remplacer par une carte (plusieurs
   images) et soigner la pose d'APRÈS, tenue, dans un décor déjà changé (comme Pew 5,37-5,67).
2. Pendant la charge, garder le corps presque immobile et faire bouger la caméra (fouetté, ruée vers la tête,
   plan collé à l'épaule) plutôt que d'ajouter du mouvement au corps.
3. Filmer la charge en MORCEAUX (épaule en amorce, poing, visage) plutôt qu'en plan entier à 8 studs.
4. Adopter un rig de contrôle à faces lettrées F/B/L/R/U/D pour nos captures de vérification.
5. Faire comme eux : un animatic en bonhommes minuté avant de poser la moindre clé, avec les cadrages et les
   cases plein écran ; puis anim en plan fixe ; puis caméra.
6. Corriger `ETUDE_ARCHIVE_VIDEOS_1` sur les temps de Pew (voir Partie 3.1).

---------------------------------------------------------------------------------------------------

## Non couvert / couvert partiellement (exactement)

- 4e0sX6p8-30 : les passages suivants n'ont été vus QU'À 2 i/s (planches `scrap_2fps_*`) ou 3 i/s, pas à 30 i/s :
  Vanishing kick Finisher (9-14,4 s, Blender : une planche à 30 i/s vue, 10-11 s), HeadFirst mel (35,9-43,9),
  HeadFirst egor (43,9-51,5), Martial Artist Awakenings (51,5-66,9), Earth-Splitting (seulement 76-79,8 à 15 i/s,
  84,3-87,2 et 93,4-96,3 à 10 i/s ; le reste à 2 i/s), Custom interactions (seulement 163,4-169,3 à 10 i/s,
  le reste à 3 i/s), Downwards throw (230,8-237,9 à 10 i/s), Flowing water, Serious sneeze, Ice boss, Gojo
  wallcombo, épée finale (3 i/s). Last Breath v1-v3 : revus à 3 i/s seulement (déjà étudiés à 0,1 s ailleurs).
  Des planches déjà produites mais non lues : vk30_06, vkwide_02/03, vkfin_01/03-06, hf_03/04, hff_02/04-06,
  hfm_*, hfe_*, maa_*, esm_03-05, esr_02-04, ess_02-04, ci1_03-07, ci2_*, gp_03, m1_01-03 (le même
  passage a été vu en m1b_01). Planches à 2 i/s non relues après le refus d'outil : scrap_2fps_03, 08, 11-31
  (les passages correspondants ont été vus via les autres planches listées plus haut, sauf 20-23,5 s vu
  seulement en hff à 30 i/s pour 18-21 s).
- Les fichiers .rbxm (TSB, pack battleground) n'ont PAS été utilisés : mon angle était les vidéos. Les anims de
  ces vidéos ne sont pas dans ces .rbxm (à ma connaissance) — pas vérifié.
- Aucun son (pas de piste audio).

---------------------------------------------------------------------------------------------------

## Vérification adverse

Vérificateur adverse, chantier 4. Tout ce qui suit a été revu par moi-même, directement dans les .mp4 de
`src/archive/`. Méthode : planches horodatées produites par ffmpeg (fps + drawtext + tile) et lues avec
Read ; mesure des coupes par la différence moyenne entre images consécutives (script `an.py`, seuil 35/255) ;
mesure du mouvement par le nombre de pixels qui changent de plus de 40/255 (`an2.py`) ; test de fixité de la
caméra sur deux zones de fond. Les fichiers sont dans `frames/verif_C1_tsb_videos/` (`v_*.png`, `pew.txt`,
`gojo2.txt`, `slap2.txt`, `sun2.txt`). Je n'ai rien modifié dans le dépôt.

Cadences réelles (ffprobe) : Slap est à 23,976 i/s, pas à 30. Pew, Sunrise, Gojo et « MORE Scrapped » sont à 30 i/s.

### 1. « Le contact n'est jamais montré comme une pose 3D » : NUANCÉ
- Pew (`v_pew_card.png`, `pew.txt`) : la carte fait bien 7 images, 5,133-5,333 s (part de blanc 58-49 %,
  contre 4-7 % juste avant et juste après). Ces chiffres sont exacts. Mais la carte n'est PAS une abstraction
  qui remplace la pose : c'est la même scène 3D passée en noir et blanc inversé. On y voit la silhouette du
  perso, bras lancé (5,167 s). Les roches sont déjà là DANS la carte (dès 5,133 s), pas seulement après.
- Sunrise (`v_sun_cut.png`) : le coup d'épée est montré en 3D (6,33-6,43 s). Le trait blanc arrive à 6,47 s,
  PAR-DESSUS les corps, qui restent visibles dessous jusqu'au-delà de 6,77 s.
- Gojo (`v_gojo.png`) : le « bloc » de 6,3-7,1 s est le bras/poing 3D qui passe en amorce devant le visage.
  Le contact est donc caché par le corps lui-même, puis viennent le noir à traits cyan (7,2-8,1 s) et une
  planche blanche inversée (8,2-9,07 s).
- Slap : le coup est bien remplacé par des cases dessinées (16,43-19,47 s ; confirmé).
- « Pose d'après tenue longtemps » : chez Pew, elle ne dure que 10 images (5,367-5,667 s = 0,33 s). Ce qui est
  tenu longtemps, c'est le plan très large qui suit (5,70-14,67 s).
- Correction : le contact est masqué ou stylisé (filtre sur la 3D, amorce du poing, trait posé par-dessus,
  cases manga), rarement retiré. La pose d'après en plan rapproché est courte (0,33 s chez Pew) ; ce qui dure,
  c'est le plan large de conséquence.

### 2. « Pendant la charge, la caméra bouge et le corps tient » (Pew) : CONFIRMÉ
- Vu dans `v_pew_charge.png` (2,2-5,1 s, 10 i/s) et `pew.txt`. Coupes rapides 2,267-2,400 s (5 images au-dessus
  du seuil), puis le ciel à 2,3-2,5 s. Le corps accroupi bouge à peine de 2,7 à 3,5 s. La caméra fonce sur la
  tête vers 3,57-3,70 s. Le plan derrière l'épaule va de 3,70 à 4,6 s, avec un corps presque immobile.
- Petite réserve pour Sunrise (`v_sun_walk.png`) : le perso n'est pas « calme » tout du long. À 4,8-5,2 s, il y
  a un dash rapide en plan large entre les gros plans.

### 3. « Anims brutes : poses tenues 8-18 images, transitions 2-4 images » : NUANCÉ
- Psychic m1s (`v_m1.png` à 30 i/s et `an2.py`, 202,1-204,77 s) : une seule tenue est vraiment immobile
  (202,10-202,43 s, 11 images). Ailleurs, le nombre de pixels qui changent ne retombe jamais à zéro de
  202,47 à 204,77 s. Les « tenues » sont des tenues vivantes ou de lents slow-in (700 à 2700 px changés),
  alternées avec des transitions de 4 à 8 images (7000 à 13000 px), pas de 2 à 4.
- Écart que le lecteur n'a pas vu : sur ces passages, la vidéo à 30 i/s contient une image en double toutes
  les 3 à 4 images (différence nulle à 202,533 / 202,667 / 202,800 / 202,900…). La capture source tournait donc
  à environ 23-25 i/s (mesuré : m1s ≈ 25,7, Crush ≈ 23,4, Rock ≈ 24,1, Slam ≈ 24,9). Le Vanishing kick (≈ 28,5) et
  Last Breath v4 (30) n'ont pas ce défaut. Un compte d'« images » à 30 i/s surestime donc les durées en images
  de l'anim (pas les durées en secondes).
- Crush (`v_crush.png`, `v_crush0.png`) : bras levé strictement immobile de 224,70 à 225,77 s (1,07 s ; la
  plage 224,37-224,67 s bouge encore). 1re descente : 225,80-226,03 s, soit 5 à 7 images, pas 1-2. La frappe
  en 1-2 images est la 2e (227,40-227,47 s) ; c'est confirmé. Ensuite, retour en ≈ 0,35 s (227,50-227,83 s), puis
  pose IMMOBILE 1,0 s (227,83-228,87 s), et non « retour en 0,6 s ».
- Slam (`v_slam.png`) : une seule image « écrasée » à 207,600 s, confirmé. Elle sert de passage entre FRONT
  (207,567) et BACK (207,633). C'est une image intermédiaire de bascule ; « écrasement au sol » est une lecture.
- HeadFirst (`v_hf.png`, `an2.py`) : quasi figé de 14,62 à 15,17 s (0,55 s, micro-mouvements à 14,82 et 15,02).
  Puis, à 15,183 s, un saut en UNE image vers une nouvelle pose (repositionnement des deux persos), de
  nouveau figée jusqu'à 15,43 s. Le départ réel se fait à 15,52 s. La victime n'est pas « en l'air » : elle est
  penchée au sol.

### 4. « Rig de contrôle lettré par face et par direction » : CONFIRMÉ
- `v_rigz.png` (zoom sur 225,5 s) et pixels mesurés : FRONT/F rouge (228,49,32), R vert (12,181,125),
  U cyan (26,197,255), L jaune (213,174,17), D orange-ambre (241,174,31), B bleu. La face « D » est visible au
  bout du bras levé. `v_slam.png`, `v_rock.png` et `v_lb4.png` montrent BACK en bleu sur le torse. Le code
  couleur donné est exact. Seule précision : D et L sont deux jaunes proches, qu'on ne distingue que par la
  lettre à 640x360.

### 5. « La racine porte les vrilles ; le perso sort du cadre en 0,27 s alors que la caméra de Moon est fixe » : RÉFUTÉ
- `v_vk.png`, `v_vk30.png`, `v_vkfull.png` et mesure du fond : le gizmo est bien au centre du torse (vu). En
  revanche, entre 3,367 et 3,80 s, le FOND bouge (écart moyen du fond passant de 0 à 13 niveaux, sur deux zones
  éloignées du perso), puis il se stabilise. La vue Studio a donc bougé : la caméra n'est pas fixe. Le perso ne
  sort pas du cadre : il va jusqu'au bord gauche (3,50-3,53 s) et revient au centre (3,60 s) en même temps que
  la vue.
- Correction : impossible de conclure que la translation du dash est clé dans la racine d'après ce passage.
  Au mieux, c'est « possible, non démontré ». Le gizmo planté au torse, lui, est vu.

### 6. « Méthode de fabrication TSB » : NUANCÉ
- Confirmé à l'image : l'annotation manuscrite « I did Victim :D » / « Egor His -> » (`v_victim.png`,
  48,5-50,5 s, HeadFirst Finishers) ; la trajectoire en pointillés dans Blender (« Ice boss stuff », 283-289 s,
  `v_a238.png`, une masse violette sur un rig gris) ; le carton « Credits to animators in bottom left (No icon
  if I made it) / Clarifying References in bottom right » (`v_vk.png`, 1,0 s).
- À nuancer : « anim des corps en plan fixe large, puis caméra » n'est pas universel. Last Breath v4
  (`v_lb4all.png`, 153-163 s) est déjà une anim brute sans effets AVEC caméra animée : gros plans du torse,
  plans larges, plan minuscule à 162,5 s, balayage à 160,07-160,13 s. Caméra et corps sont donc parfois
  animés ensemble.
- Déduction non vérifiable : « des trous gardés pour les flashs » (les 2 images grises à 160,10-160,13 s sont
  un balayage de caméra rapide ; rien ne dit qu'un flash doive y aller).

### 7. « Le montage accélère, puis un plan long avant le coup » : CONFIRMÉ (Gojo, Sunrise), NUANCÉ (Slap)
- Gojo, coupes que j'ai remesurées (`gojo2.txt`) : 0,800 / 1,867 / 2,633 / 3,200 / 3,700 / 4,033 / 4,433 / 4,767 /
  5,033 / 5,367 / 6,633 s. Cela donne des durées de 1,07 / 0,77 / 0,57 / 0,50 / 0,33 / 0,40 / 0,33 / 0,27 / 0,33 s,
  puis un plan de 1,27 s. C'est exactement ce que dit le lecteur. Le plan long pousse bien vers le visage
  (`v_gojo.png`, 5,4-6,2 s).
- Sunrise (`sun2.txt`) : 12 coupes entre 9,10 et 9,53 s, puis aucune coupe jusqu'à 15,43 s (5,9 s, un seul plan
  vu dans `v_sun_all.png`). Confirmé.
- Slap (`v_slap1.png`, `v_slap2.png`, 23,976 i/s) : les rafales de cases de 1 à 3 images existent
  (16,43-16,81 et 17,43-18,02 s). Mais entre les deux, une case (main et visage dessinés) est TENUE 15 images,
  soit 0,63 s (16,81-17,43 s). Le visage déformé tient ≈ 0,75 s (18,38-19,13 s), pas 0,85. On a donc
  rafale, tenue, rafale, tenue longue, puis retour à la 3D rouge (19,51 s), et non une seule rafale suivie
  d'une seule tenue.

### 8. « Sur-rotation du torse jusqu'à montrer le dos » (Rock throw) : CONFIRMÉ, avec précision
- `v_rock.png` (30 i/s) : FRONT rouge à 229,633 s, faces latérales à 229,667-229,767 s, BACK bleu à 229,800 s.
  Cela fait 4 intervalles à 30 i/s, dont un doublon, soit ≈ 3 images source et 0,13-0,17 s : le « demi-tour en 3
  images » est juste. Dos à la caméra jusqu'à 230,77 s, donc ≈ 1 s. Précision : de 229,80 à 230,30 s le corps
  bouge encore (il se pose). L'immobilité stricte ne dure que 0,43 s (230,33-230,77 s).

### (bonus) 9. « Petite cause, effet énorme » (Sunrise) : CONFIRMÉ pour le timing, INVÉRIFIABLE pour « dos tourné »
- `v_sun_sheath.png` (15 i/s) : la lame rentre au fourreau de 12,1 à 13,33 s. Le kanji 旭 apparaît à 13,40 s
  et le flash blanc à 13,47 s. L'écart avec le trait de coupe (6,47 s) est de 6,9-7,0 s. Confirmé.
  L'orientation « dos tourné » de l'attaquant ne se lit pas avec certitude à 640x360 (perso gris vu de 3/4).

### Oublis importants
1. Les passages Moon Animator / Studio de « MORE Scrapped » (m1s, Crush, Rock, Slam) ont des images en double
   (source ≈ 23-25 i/s dans une vidéo à 30). Les comptes d'images de ces passages sont gonflés d'environ 20 %.
   Slap est à 23,976 i/s.
2. Les « tenues » des anims brutes sont presque toujours des tenues vivantes (petite dérive continue), sauf
   quelques-unes strictement immobiles (Crush 1,07 s bras levé ; Crush 1,0 s après la frappe ; Rock 0,43 s ;
   m1s 0,33 s). C'est une information de fabrication utile que le lecteur a écrasée sous « poses tenues ».
3. Last Breath v4 montre que certaines anims brutes TSB sont déjà faites caméra comprise, dans Moon (gros plan
   du torse, plan très large, balayage), avant tout effet. Cela contredit en partie le schéma « corps en plan
   fixe, puis caméra ».
4. Chez Pew, les effets « décor changé » (roches) sont posés dès la 1re image de la carte, et la carte est un
   filtre sur la scène 3D. La recette qu'on peut refaire est « filtre bichrome inversé sur la vraie pose,
   7 images », pas « carte sans perso ».
5. Chez Gojo, deux planches abstraites se suivent, d'environ 0,9 s chacune : noir à traits cyan (7,2-8,1 s),
   puis blanc à taches noires (8,2-9,07 s). Retour à la 3D en plongée à 9,07 s. Le lecteur n'en décrit qu'une.
6. Chez Slap, la séquence manga alterne rafales et tenues (tenue de 0,63 s à 16,81-17,43 s). Ce n'est pas
   une rafale unique.
