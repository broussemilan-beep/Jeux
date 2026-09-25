# Relecture des références de Milan, sous l'angle VFX (2026-09-25)

**Demande de Milan** : « ton jugement : revois nos références et comment elles
utilisent les VFX », avant de construire le moteur.

**Méthode**
- Nouvel outil `outils/planche_vfx.py`. Pour chaque référence, il trouve les
  3 moments où les effets culminent (pixels très clairs, couleurs saturées,
  saut brutal d'une image à l'autre) et les montre sur 10 images
  consécutives, à la cadence native.
- 14 vidéos ou GIF et 8 images fixes, regardés à l'œil. Notes écrites avant
  de relire la fiche `fiches/VFX.md`.
- Les planches (images d'œuvres) restent en local. Seul ce qu'on en tire
  est versionné.

## Référence par référence (ce que font les effets, pas le corps)

| ref | ce que je vois |
|---|---|
| **12e7dae5, Black Flash (JJK)** | Palette stricte **rouge / noir / blanc**. (1) Éclairs rouges et noirs autour du corps, dans la caméra de jeu, au moment du coup. (2) 1 image blanche plein écran, puis gros plan du bras en silhouette noire sur blanc, puis la scène teintée en rouge. (3) Cartes à l'encre : fond blanc, traits noirs faits main, une tache rouge au point d'impact, forme qui change à chaque image. (4) Un grand croissant blanc (smear) qui balaie la scène 3D. (5) Étincelles en CROIX noires sur blanc (polarité inversée), gerbe de feu rouge rayonnante, puis une carte blanche tenue ~0,3 s où des traits noirs dérivent. |
| **3ae71567, Rewind Clock** | **Stroboscope de palettes** : blanc radial → RVB chromatique → noir et blanc à l'encre → blanc, **1 image chacune**. Revenu dans la 3D, un halo blanc surexposé (bloom) sur le point d'impact. Carte radio du crâne qui change de couleur toutes les 1-2 images (inversé, rouge, bruité, bleu), puis tenue ~0,6 s en vert sombre. Flash inversé, puis blanc brûlé. |
| **4fb4f776, Stagnant Rage** | Explosion **en particules, dans la caméra de jeu** : (1) cœur blanc-jaune énorme, 1 image ; (2) flipbook de feu orange **en aplats avec un contour rouge sombre** (feu cel, pas réaliste) ; (3) éclats blancs, blocs de roche ; (4) langues de flamme rouges ; (5) éclat en étoile bleu-blanc ; (6) fumée. Variante lointaine : 1 image jaune plein écran, **dôme blanc translucide**, puis des **croissants de vent blancs qui tournent** autour de l'explosion. Chaque salve dure ~0,3-0,5 s. |
| **01f4b1d2, Black Hole** | Cartes en silhouette noir / blanc (perso et débris en aplat, 5 images). Retour en 3D : **grandes étoiles noires à 4 branches cernées de jaune lumineux** en surimpression, tenues ~0,15 s. Disque d'énergie jaune-blanc lumineux (mesh + bloom), avec des arcs blancs et des cubes de débris flottants. Noir 2 images, puis plan large calme. |
| **946bd286, coup chapeau** | Halo blanc et anneau autour de la tête et de la main. Carte à lignes radiales. **Air** : lignes blanches verticales (pression) et gros nuages de fumée blanche qui envahissent la scène. Projectile : disque jaune-orange cerclé de rouge sur fond noir, avec une traînée pointillée. Cible concentrique noire sur blanc, croissant blanc sur noir, puis **fond remplacé par des lignes radiales rouges** avec une gerbe rouge en forme de poing. |
| **48244687 / 772ee6b0, Serious Punch** | Presque pas de VFX 3D : de fins traits blancs de vent autour du corps. Puis **tourbillon de fumée grise translucide qui vient vers l'objectif autour du poing** (SP2, ~0,4 s), carte à hachures radiales, carte X, blanc, puis **la fumée qui se dissipe sur le cratère**. Toute la puissance est dans les cartes, le blanc et la fumée. |
| **a0341700, gatling** | Les bras deviennent des **multiples roses translucides**. **Croissants blancs** et traits vifs tout autour de la silhouette ; pas de flash. |
| **eba5ed69, IMPACT HAVEN** | Le minimum : 1 image de silhouette blanche sur fond noir, puis 1 image blanche (cyan pâle). Ensuite, une **traînée d'air** blanche et fine derrière le corps projeté, et une poussière légère au sol. Propre et lisible. |
| **73cc1fb0, Gemini (IA)** | **Aura en flammes blanches à pointes** (style super saiyan : pointes dentelées qui montent) et éclairs blancs. Carte : corps en silhouette blanche sur noir, avec l'aura et les éclairs qui bougent, tenue ~0,8 s. Soleil : sphère de feu dont la texture défile (défilement UV), gerbe de rayons orange au sol, poussière. |
| **aafdc91d, caméra de jeu lointaine** | Gerbe d'**éclats blancs acérés**, bouffée de fumée grise. Coup plus gros : éclats plus gros, étincelles rouges, et **anneaux de choc concentriques très fins et transparents** pendant ~0,5 s. Lisible même tout petit. |
| **85e1a98f, combo Moon Animator** | Smears blancs dessinés : **vague de vent blanche en dents de scie au sol**, comète blanche au bout du poing, **anneau blanc fin au sol**, croissant de coupe. Sur le coup de pied, une **traînée en spirale** blanche autour de la jambe. Les mêmes effets rejoués « sans effets » montrent combien ils portent le coup. |
| **58322fc4, boxeur** | Palette **blanc / rouge / bleu-violet** : blanc plein écran 1-2 images, **arcs de cercle rouges** (croissants de choc), gouttes rouges, arcs blancs, **aura sombre bleu-violet** autour de l'attaquant. Final : **tunnel de lignes radiales blanches et d'anneaux concentriques**, avec des éclaboussures rouges. |
| **449345ad, M1 de rue la nuit** | Par coup (tier 1) : éclat blanc en étoile ~2 images, puis un **anneau blanc fin qui s'agrandit** en 3-4 images, et un petit croissant sur la trajectoire du poing. 5-6 images en tout, et c'est lisible, parce que c'est blanc et net sur la scène. |
| **Images fixes** | 1727676e : boule de feu projectile (orange avec anneaux et flammes qui traînent). 8d015f39 / 7263e0c8 : soleil de « The Creator » (sphère de feu avec couronne de flammes). 41d7796b : carte d'impact (étoile noire à 4 branches, traits d'encre). 6dfb2f6c : hachures radiales à l'encre. **448c613e** (non identifiée jusqu'ici) : **case de manga, poing géant sur des bouffées de fumée hachurées** (encre). 80ac271e : capture d'un dossier de zips (ce n'est pas une ref). da606c23 : fiche Demi-Dieu (déjà connue). |

## Ce que les refs m'apprennent (mon jugement)

1. **Deux registres qui alternent** : (A) des VFX **dans le monde 3D**, vus
   dans la caméra de jeu (particules, anneaux, feu, fumée, croissants) ;
   (B) des **cartes en plein écran** (inversion, encre, stroboscope, blanc).
   - Les grosses techniques font A → B → A.
   - Le Poing du Dragon a déjà un bon B (cartes, blanc), mais un A faible :
     3 émetteurs, des anneaux en Part Neon, des « rubans dragon » flous.
2. **Le style est graphique (cel), jamais réaliste.**
   - Feu à bords durs cernés de rouge sombre, fumée en grosses boules
     blanches ou grises.
   - Éclats = éclats acérés ou étoiles à 4 branches ; anneaux = trait fin et
     net ; coupes et vent = croissants blancs effilés aux deux bouts ; aura =
     flammes à pointes dentelées.
   - Presque jamais une simple tache floue de lumière : or c'est exactement
     ce que font nos textures procédurales actuelles.
   - → **La bibliothèque de textures est la première chose à construire**,
     avant le moteur.
3. **Une discipline de palette** : chaque technique tient dans **2-3
   couleurs + blanc** (Black Flash rouge / noir / blanc ; boxeur blanc /
   rouge / bleu-violet ; Stagnant orange / jaune / blanc et contour rouge
   sombre).
   - Le blanc est l'accent partout.
   - C'est aussi la signature : on reconnaît la technique à sa palette.
4. **Timings** (à 30 i/s dans les refs) :
   - flash 1-2 images ;
   - anneau qui grandit en 3-6 images ;
   - feu 0,3-0,5 s ;
   - croissants de vent 0,2-0,3 s ;
   - fumée 1 s et plus, qui se dissipe sur la conséquence ;
   - cartes en stroboscope, 1-2 images chacune ;
   - carte tenue 0,3-0,8 s.
5. **L'AIR (demande de Milan)** revient dans presque toutes les refs, et
   c'est ce qui vend la vitesse et la pression :
   - croissants blancs qui tournent autour de l'impact (Stagnant) ;
   - lignes verticales de pression et nuages qui envahissent la scène (coup
     chapeau) ;
   - traînée d'air derrière un corps projeté (IMPACT HAVEN) ;
   - vague de vent en dents de scie au sol, spirale autour de la jambe
     (Moon) ;
   - tourbillon de fumée autour du poing vers l'objectif (Serious Punch) ;
   - tunnel de lignes et d'anneaux (boxeur).
   - Techniquement, ce sont des **croissants, arcs et spirales**
     (MeshPart, ou Beam avec une texture qui défile) et des **anneaux fins**.
6. **Les meshes** : dôme blanc translucide (Stagnant), disque et anneau
   lumineux (Black Hole), sphère de soleil à texture qui défile (Gemini, The
   Creator), tourbillon de fumée (SP2), vague au sol (Moon). C'est
   exactement les « Custom Meshes + UV scrolling » décrits par Milan.
7. **Orientation** : croissants et coupes suivent la direction du coup ; les
   éclats rayonnent depuis le point de contact. Ce ne sont jamais des blocs
   symétriques posés au hasard.
8. **Au tier 1, c'est lisible en caméra de jeu** (449, aafdc91d) : étoile
   blanche de 2 images, puis anneau fin qui grandit, puis petit croissant. Le
   blanc net sur la scène suffit, même tout petit. C'est la réponse à notre
   question ouverte depuis la v6.
9. **Les auras** :
   - flammes blanches à pointes avec éclairs (Gemini) ;
   - flammes sombres bleu-violet (boxeur) ;
   - étoiles lumineuses (Black Hole).
   - La forme et la palette font la signature. L'aura « dragon » attendra
     la ref de Milan.

## Ce que ça change pour le moteur (VFX 2), dans l'ordre

1. **Bibliothèque de formes cel** (textures et flipbooks, faites ici avec
   Blender et PIL) :
   - croissant effilé, éclat acéré, étoile à 4 branches, anneau fin ;
   - bouffée de fumée cel, feu cel à contour, flamme d'aura à pointes ;
   - ligne de vitesse, arc de vent, spirale.
2. **Bibliothèque de meshes** (Blender) : dôme, anneau / disque, sphère,
   tourbillon, croissant 3D, vague au sol. UV prévus pour que la texture
   défile.
3. **Couches** selon le registre A :
   - flash (1-2 images) ;
   - anneau fin (3-6 images) ;
   - éclats orientés ;
   - croissants de vent ;
   - fumée qui reste.
   - Palette de 2-3 couleurs + blanc, par technique.
4. **Bloom** dans l'aperçu et en Roblox (BloomEffect animé), réglé pour que
   le blanc « bave », sans noyer l'image.
5. **Orchestration** : apparition → projection → collision (le projectile
   disparaît) → onde de choc (mesh qui grossit et s'efface) + explosion de
   particules dans toutes les directions. C'est le scénario décrit par
   Milan, avec des timings calés sur ces refs.
