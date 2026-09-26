# Rapport : les règles de l'« anatomie anime » appliquées au combat en 3D, et leur traduction sur un rig R6

Date : 2026-09-24. Rédigé pour l'animation de coups sur des R6 Roblox (6 pièces rigides, Motor6D = rotation + translation, pas de scale).

**Environnement de recherche (à lire avant tout le reste).** Le proxy de ce sandbox bloque presque tout le web. Sites joignables : archive.org (pages et textes OCR, mais pas les miroirs de téléchargement `dn*.archive.org`), sakugabooru.com (API, images, vidéos), devforum.roblox.com. YouTube répond, mais avec un contrôle anti-bot (« Sign in to confirm you're not a bot »). Tout le reste répond 403 : gamedeveloper.com, 80.lv, cgworld.jp, gdcvault, kotaku, ggxrd.com (PDF de la conférence GDC), medium, pixiv, atwiki, note.com, wavemotioncannon, animetudes, etc.

Les sources se rangent donc en trois niveaux de fiabilité, indiqués partout dans le rapport :

- **[LU]** : texte primaire ou traduction intégrale que j'ai lus moi-même.
- **[MESURÉ]** : ce que j'ai mesuré moi-même, image par image, sur de vrais extraits d'anime téléchargés depuis sakugabooru.
- **[RÉSUMÉ-RECHERCHE]** : seulement l'extrait ou le résumé renvoyé par le moteur de recherche. Je n'ai pas pu ouvrir la page, donc c'est à vérifier.

Les propositions chiffrées pour le R6 marquées **[PROPOSITION]** sont les miennes. Aucune source ne les donne. Ce sont des points de départ à tester.

---

## 1) Sources lues

**Lues en entier ou en grande partie [LU]**

1. 4Gamer, « The Secrets of GGXrd's Graphics » : traduction anglaise intégrale (Leo Bruno « GKK ») de l'article-interview 4Gamer avec Sakamura, Ishiwatari, Motomura, Ieyumi et Yamanaka (Arc System Works). Texte OCR : https://archive.org/stream/GGXrd-design-docs (fichier `4Gamer - The Secrets of GGXrd's Graphics_djvu.txt`). **C'est la source principale sur le bone scaling et l'animation limitée de GGXrd.**
2. Arc System Works (J. C. Motomura), « GuiltyGear Xrd Bone Placement Tips for Action » : diapositives traduites. Même item archive.org.
3. Arc System Works, « GGXrd Anime Style Model Tips » : diapositives traduites. Même item archive.org.
4. CGWORLD n°215, « GGXrd -REVELATOR- » : traduction. Même item archive.org. Surtout du rendu, peu d'animation.
5. Mariel Cartwright (Lab Zero, Skullgirls), GDC 2014, « Fluid and Powerful Animation within Frame Restrictions » : texte des diapositives. https://archive.org/details/GDC2014Cartwright
6. Mike Mattesi, *FORCE: Dynamic Life Drawing* (10th anniv.) : texte OCR, chapitres 1.6 à 1.8 et 2.6 à 2.7. https://archive.org/details/8611f-9aa-3604-4838-91f-3-46690ba-3073e
7. Wiki sakugabooru : entrées `impact_frames` (ショックコマ), `yoshinori_kanada`, `smears`/`hugh_fraser`, `fighting`. https://www.sakugabooru.com/wiki
8. Roblox DevForum : demande de fonctionnalité « Add a scale setting for Motor6D and AnimationConstraint » (juin 2026), qui confirme que le scale d'un membre n'existe pas. https://devforum.roblox.com/t/4702764
9. Roblox DevForum : « How would I go about making my combat feel more impactful? » (conseils de la communauté : camera shake, knockback, particules). https://devforum.roblox.com/t/2042214

**Analysées image par image [MESURÉ]** (vidéos sakugabooru à 23,976 i/s, extraites avec ffmpeg, différence de pixels entre images successives, puis vérification visuelle)

10. *My Hero Academia* S2 #10, Yutaka Nakamura (Deku contre Todoroki) : https://www.sakugabooru.com/post/show/281209
11. *Jujutsu Kaisen* #19 (Itadori et Todo contre Hanami) : https://www.sakugabooru.com/post/show/146024
12. *One Punch Man* #01, Norifumi Kugai (poing de Saitama en gros plan) : https://www.sakugabooru.com/post/show/193721
13. *One Punch Man* #12, Yutaka Nakamura et Gosei Oda : https://www.sakugabooru.com/post/show/162980. Surtout des effets, peu utile pour les poses.
14. Genga (dessins-clés) de Nakamura pour MHA, publiés sur sakugabooru (source NHK « Anime Manga Explosion ») : posts 294895, 294900, 221652.
15. Genga de JJK publiés par MAPPA : posts 214744 et 228260.

**Connues seulement par le résumé du moteur de recherche [RÉSUMÉ-RECHERCHE]** (pages non ouvrables)

16. Kotaku, « Breaking Down The Animation Of Guilty Gear and Dragon Ball FighterZ », qui résume la vidéo *New Frame Plus* (D. Floyd, 2019) : https://kotaku.com/breaking-down-the-animation-of-guilty-gear-and-dragonba-1836849279
17. Keo (dkeodara), « Dragonball FighterZ: More than Meets the Eye » : https://dkeodara.com/2017/06/19/dragonball-fighterz-more-than-meets-the-eye/
18. Pixiv 百科 et CGWORLD, glossaire « 金田パース » / « 金田ポーズ » : https://dic.pixiv.net/a/金田パース et https://cgworld.jp/terms/金田パース.html
19. Animétudes, « The Kanada style now » (2021) : https://animetudes.com/2021/07/09/the-kanada-style-now/
20. Médias Bunka (mediag.bunka.go.jp), « 3DCGアニメーションの次世代スタンダード『宝石の国』 », sur l'outil Camera-O-Matic d'Orange : https://mediag.bunka.go.jp/article/13643-2/
21. Glossaires japonais タメ/ツメ (atwiki アニメ制作メモ, blog goo) : https://w.atwiki.jp/aniken/pages/38.html
22. Glossaires « obake » / smear (garagefarm, Wikipedia « Smear frame ») : https://en.wikipedia.org/wiki/Smear_frame
23. Shoryuken / SuperCombo, valeurs de hitstop de SFV : http://shoryuken.com/2016/06/07/hitstop-in-street-fighter-v-kens-not-so-little-secret/ et https://game.capcom.com/cfn/sfv/column/131545?lang=en
24. Wiki Genshin, « Hitlag » : https://genshin-impact.fandom.com/wiki/Hitlag
25. Dan Fornace, « The Power of Silhouettes » (Medium) : https://fornace.medium.com/fighting-game-design-with-dan-fornace-the-power-of-silhouettes-915fde48318f
26. Interview de Jonathan Colin, « Readability, Silhouette and Gameplay Animation Secrets » (animotionx) : https://www.animotionx.com/en/post/interview-jonathan-colin-readability-silhouette-and-gameplay-animation-secrets
27. Interview de Yutaka Nakamura (WEB Anime Style, 2003, traduction Wave Motion Cannon) : https://wavemotioncannon.com/2016/10/05/interview-yutaka-nakamura-web-anime-style-7192003-part-1/. Contenu non récupéré, voir la section 6.

**Voulues mais inaccessibles** : la vidéo de la conférence GDC 2015 de Motomura (archive.org GDC2015Motomura, miroir bloqué ; YouTube yhGjCzxJV3E, anti-bot), son PDF (ggxrd.com, 403), la vidéo New Frame Plus, CGWORLD « もっとアニメらしく！ » (CEDEC 2016), le livre d'Orange *MAKING OF BEASTARS*, le mémoire DiVA sur GG Strive, les pages Polygon Pictures et Sanzigen, et toute source sur Genshin, HSR ou Wuthering Waves au-delà du hitlag.

---

## 2) Les règles de l'« anatomie anime »

Chaque règle suit le même format : énoncé, chiffres, pourquoi, quand l'utiliser ou non, puis traduction R6 avec un verdict POSSIBLE, PARTIEL ou IMPOSSIBLE (avec un substitut).

### Règle 1 : des poses dessinées et tenues, pas des courbes (animation limitée « stop-motion »)

- **Énoncé [LU, 4Gamer/GGXrd].** Les animateurs d'ArcSys posent le personnage image par image « comme en stop-motion ». Hidehiko Sakamura : « We don't rely on interpolation using F-curves and such ». Ils ont d'abord essayé d'animer à 60 i/s avec des courbes puis de réduire la cadence : « that just looked like 3D graphics with dropped frames ».
- **Chiffres [LU].**
  - Cinématiques : 15 poses/s de base, contre 8 à 12 en animation cel.
  - Combat : la durée de chaque pose est fixée coup par coup. L'exemple donné est « 2F, 3F, 5F, 1F, 1F, 2F, 2F, 3F, 4F » à 60 i/s (1F = 16,67 ms). L'OCR porte « SF », que je lis comme 5F.
  - Le storyboard fixe par exemple « coup entier = 60 images, le poing touche à l'image 30 ». L'animateur choisit ensuite la pose de chaque image.
  - Les trajectoires paraboliques (saut, vol, course) restent lisses à 60 i/s. Seul le corps est « limité ».
- **Pourquoi.** L'œil repère la 3D à la fluidité uniforme des courbes. Des poses tenues lisent comme des dessins-clés et donnent de l'impact.
- **Quand l'utiliser.** Attaques, supers, cinématiques.
- **Quand l'éviter.** La locomotion et le déplacement de la racine (trajectoires) restent fluides.
- **R6 : POSSIBLE.**
  - Mettre les keyframes de pose en easing *Constant* : tenue en escalier, sans interpolation. `Enum.PoseEasingStyle.Constant` existe dans l'éditeur d'animation Roblox ; c'est de mémoire, à vérifier dans l'éditeur.
  - Garder le déplacement du HumanoidRootPart (dash, lancer en l'air) sur une courbe lisse, comme GGXrd garde ses paraboles à 60 i/s.
  - Ne pas faire « animer lisse puis sauter des images ». ArcSys l'a testé : le résultat ressemble à de la 3D qui rame.

### Règle 2 : chaque pose a sa propre anatomie (os étirés ou grossis par pose)

- **Énoncé [LU, 4Gamer].**
  - Sakamura : « parts of the body that would be impossible in a real person will expand, contract, or shrink. It's all about looking good on the game screen for the player ».
  - Ieyumi : « In a punching action, the fists are slightly enlarged, and in a kicking action, the legs are sometimes extended ».
  - Les bras et les jambes « can grow and shrink freely ».
  - ArcSys a modifié l'UE3 pour avoir un scale d'os indépendant par axe. Sakamura a refusé l'alternative « plus d'os », qui aurait demandé environ 4 fois plus d'os.
  - La légende de l'article oppose deux images de la même animation, avec et sans scale d'os. Je n'ai pas pu en récupérer l'image (PDF sur un miroir bloqué).
- **Chiffres.** Aucun facteur d'échelle n'est donné : seulement « slightly enlarged » pour les poings et « sometimes extended » pour les jambes. Je n'invente pas de facteur.
- **Pourquoi.** Le dessin anime ne respecte pas des longueurs constantes. La longueur d'un membre est une variable d'expression, fixée pose par pose pour la caméra.
- **Quand l'utiliser.** Pose de contact ou d'extension, portée d'un coup, pose héroïque.
- **Quand l'éviter.** Dans les poses « neutres » (idle, garde), qui doivent rester dans les proportions du modèle ; sinon le personnage paraît instable.
- **R6 : IMPOSSIBLE directement** (le Motor6D n'a pas de scale ; la demande de fonctionnalité de juin 2026 le confirme). Substituts, du plus sûr au plus risqué :
  - (a) **Translation vers la caméra** : c'est l'alternative d'ArcSys eux-mêmes, voir la règle 3.
  - (b) **Translation le long de l'axe du bras**, pour allonger la portée de 0,3 à 0,6 stud **[PROPOSITION]**. Cela ouvre un trou à l'épaule, à cacher par l'angle (bras devant le torse), par la brièveté (1 à 3 images) ou par un VFX.
  - (c) **« Swapped geo »** : un poing surdimensionné (MeshPart soudé au Right Arm), rendu visible uniquement sur les images de contact. GGXrd remplace déjà des parties du modèle pour des formes impossibles (les cheveux-lames de Millia) [LU].
  - (d) Changer `BasePart.Size` par script sur un marker d'animation. C'est hors du système d'animation, il faut recaler C0/C1, et la réplication reste à tester : bidouille non vérifiée.

### Règle 3 : ajouter l'angle de vue au modèle, pas à la caméra

- **Énoncé [LU, 4Gamer, Daisuke Ishiwatari].** Élargir la focale pour grossir une main tendue rendait « le visage derrière trop petit ». À la place : « we would extend the arm of the 3D model and bring the hand closer to the camera. In the end, we didn't change the angle of view of the camera, but rather we added the angle of view to the character models ».
- **Autres témoignages.**
  - Orange (*Land of the Lustrous*) a créé **Camera-O-Matic**, qui déforme automatiquement le modèle selon l'angle de caméra pour obtenir la « fausse perspective » (premier plan exagéré, effet d'objectif) [RÉSUMÉ-RECHERCHE].
  - Même logique pour un robot tendant le bras vers la caméra : l'échelle des pièces du bras est fortement déformée [RÉSUMÉ-RECHERCHE, source exacte non identifiée].
  - Genga de Nakamura (image 02) : main tendue vers la caméra à peu près de la taille de la tête, avant-bras très raccourci. C'est mon estimation visuelle.
- **Chiffres.** Aucun chiffre publié. Géométrie utile **[PROPOSITION]** : la taille apparente varie comme 1/distance à la caméra. Pour un poing qui paraît deux fois plus gros que la tête (à taille réelle égale), il doit être deux fois plus près de la caméra. Exemple : caméra à 6 studs de la tête, poing à environ 3 studs de la caméra.
- **Pourquoi.** On garde une focale « normale » pour le reste du corps et le visage, et on n'exagère que le membre qui frappe.
- **Quand l'utiliser.** Plans où la caméra est **face au coup** : caméra de finisher, cinématique, contre-plongée.
- **Quand l'éviter.** En caméra de jeu à la 3e personne, placée derrière le joueur : le poing s'éloigne de la caméra, la perspective le rapetisse et la règle s'inverse. Voir la règle 6.
- **R6 : POSSIBLE** (translation des Motor6D, CFrame et FOV de la caméra animables). Mode d'emploi :
  - Placer la caméra de finisher devant l'attaquant, légèrement en contre-plongée.
  - Translater le Right Arm vers l'objectif (C0 de l'épaule, plus la rotation du torse qui avance l'épaule).
  - Garder le FOV modéré (de l'ordre de 50 à 70) plutôt qu'un grand-angle **[PROPOSITION]**.

### Règle 4 : la pose est faite pour l'image, pas pour l'espace 3D (tricher à la caméra, image par image)

- **Énoncé [LU].**
  - Ishiwatari : « When posing a character in a cutscene, we adjust the position of each part of the character model and the position of the light source for that character, frame by frame. In the case of animations where the camera goes around the character, I also adjust the position of the nose for each frame ».
  - Les *Anime Style Model Tips* décrivent des morphs ou des os « depending on camera angle » (bouche rétractée en vue de trois-quarts).
  - Les hitbox de GGXrd sont posées en 2D **par image** sur le rendu, ce qui prouve que chaque image est pensée comme un dessin.
- **Pourquoi.** Seul compte le rendu à l'écran. Une pose parfaite en 3D mais illisible dans l'axe de la caméra est ratée.
- **Quand l'utiliser.** Uniquement quand la caméra est connue d'avance (cinématique, caméra scriptée du finisher).
- **Quand l'éviter.** En caméra libre : une triche vue d'un autre angle se voit.
- **R6 : PARTIEL.** Pas de morph, et le visage est un decal. Mais on peut décaler par image les pièces (tête, bras) pour la caméra scriptée. Pour les coups joués en caméra libre, il faut plutôt des poses lisibles sous plusieurs angles (règle 6).

### Règle 5 : casser le corps, avec 1 image de dépassement et 1 image de retard

- **Énoncé [LU, Cartwright GDC 2014].**
  - « Don't be afraid to break limbs to push your animation. »
  - « A frame of delay helps give your animation strength. »
  - Overshoot : « One frame of an attack 'overshooting' its final key frame helps give it impact » (exemples cités : Makoto dans SF3 Third Strike ; Felicia, Sol Badguy, Necro).
  - « Even one frame of anticipation is enough. »
  - « Push, exaggerate, and break a few bones… You're creating movement, not individual pieces of art. »
- **Motomura [LU, Bone Placement Tips].** « It's not necessarily anatomically correct… As long as what you see on the screen is cool, it's OK ». Il place volontairement la colonne et le thorax de façon « fausse » (« dared to lie for the sake of expression ») pour que la silhouette change plus fort.
- **Chiffres.** 1 image d'anticipation minimum, 1 image de dépassement, 1 image de retard. Ces valeurs viennent de la 2D à 60 i/s de Skullgirls.
- **Quand l'utiliser.** Le dépassement sur la pose d'extension du coup ; la cassure sur les images de mouvement rapide, que l'œil ne lit pas comme anatomie.
- **Quand l'éviter.** Sur les poses tenues longtemps : une cassure tenue se lit comme une erreur.
- **R6 : POSSIBLE.** Rotations hors limites anatomiques (épaule au-delà de 180°, torse tourné bien au-delà de ce qu'un vrai buste permet, tête rentrée dans le torse). Une image clé de dépassement plus « longue » que la pose finale, puis retour sur la pose tenue. Sur un R6, il n'y a ni coude ni poignet à « casser ». Ce qui se casse, ce sont les **orientations relatives des 6 blocs** et leurs **translations** (bras qui avance hors de l'épaule).

### Règle 6 : la silhouette d'abord (lisibilité)

- **Énoncé.**
  - [LU, Cartwright] « Clear silhouette in your keys is the basis of making strong animation. »
  - [RÉSUMÉ-RECHERCHE, Fornace / jeux de combat] Chaque pose clé doit rester lisible remplie en noir.
  - [RÉSUMÉ-RECHERCHE] Le directeur artistique de SF5 (T. Kamei, GDC 2017) a gardé des proportions exagérées car le réalisme rendait le jeu plus dur à lire.
  - [RÉSUMÉ-RECHERCHE, J. Colin] Même en motion capture, on exagère la chaîne cinétique : les pieds, puis les hanches qui « vissent », puis le haut du corps, puis les bras.
- **Pourquoi.** Au combat, il n'y a pas de temps pour la nuance : la forme doit parler en un coup d'œil.
- **Quand l'utiliser.** Toujours pour les poses clés.
- **R6 : POSSIBLE, et c'est même l'atout du R6** (formes simples). Mais le bras frappeur ne doit **jamais être caché** derrière le torse dans l'axe de la caméra de jeu. En caméra 3e personne derrière le joueur, tourner davantage le torse et le bras pour que le bras tendu sorte **latéralement** de la silhouette plutôt que de s'enfoncer vers l'avant. Test : `Highlight` noir plein sur le personnage, puis vérifier à l'écran.

### Règle 7 : ligne d'action et « Force » (courbe, puis droite)

- **Énoncé [LU, Mattesi, *FORCE*].**
  - « One curve is ONE force. »
  - Plus une courbe est serrée, plus elle porte de force à son apex.
  - Le rythme doit traverser la figure en oblique (« Rhythm must be oblique… It must move across the figure in angles »).
  - Le « leading edge » (bord d'attaque) est la partie du corps qui mène le mouvement.
  - Le bras tendu « acts like the arrow that relates directly to the Applied FORCE and leading edge ».
  - Mattesi met en garde contre le fait de « straightening out the pose » par habitude : les angles excitent.
  - [RÉSUMÉ-RECHERCHE, sources grand public] Droite ou diagonale pour la force et la portée ; courbe en C quand un côté se comprime et l'autre s'étire.
- **Application au poing (synthèse, voir la section 3).** L'anticipation est une **courbe en C comprimée**. L'extension est une **droite quasi unique** qui va du pied arrière au poing.
- **Quand l'utiliser.** Sur toute pose clé.
- **R6 : POSSIBLE.** Avec 6 blocs rigides, la ligne d'action se construit en **alignant les blocs**. À l'extension : jambe arrière, torse et bras frappeur quasi colinéaires sur une diagonale. À l'anticipation : torse fortement incliné ou enroulé, tête rentrée, bras replié derrière le plan du corps. Faute de colonne à 3 os, la courbure passe par le RootJoint (inclinaison du torse) et par les hanches en contre-rotation.

### Règle 8 : mettre l'épaule dans le coup

- **Énoncé [LU, Motomura, Bone Placement Tips].**
  - « In action, whether or not you put your shoulders into a punch can completely change the strength and meaning of the pose. Depending on the posture of the shoulders, the pose may be 'I put power into it' or 'I hit it lightly'. »
  - ArcSys place le pivot de la clavicule près du centre du thorax pour avoir un grand débattement : plus le rayon est grand, plus l'épaule bouge.
- **[MESURÉ, JJK #19, image 06]** À l'impact, l'épaule d'Itadori remonte jusqu'à couvrir le menton, la tête passe **sous et derrière** la ligne épaule-poing, et le torse est presque horizontal.
- **R6 : PARTIEL.** Il n'y a pas de clavicule : l'épaule est fixe au coin du torse. Substituts :
  - Rotation du torse (RootJoint) en lacet et en roulis pour avancer et monter l'épaule frappeuse.
  - Plus une **translation du C0 de Right Shoulder** vers l'avant et le haut, de 0,2 à 0,5 stud **[PROPOSITION]**, qui simule la protraction ou l'élévation.
  - Tête baissée et avancée (C0 du Neck) pour la « rentrer » derrière l'épaule.

### Règle 9 : les impact frames (ショックコマ)

- **Énoncé [LU, wiki sakugabooru].** « Special frames drawn by animators that appear for a split second, often added to make an impact more pronounced. »
- **Genga de Nakamura (image 01).** Silhouette dans un éclat radial, négatif noir et blanc, puis plan quasi abstrait.
- **Chiffres [MESURÉ, MHA S2 #10, Nakamura, 23,976 i/s].**
  - Coup de Todoroki : 4 à 5 dessins d'impact en noir et blanc **à 1 image chacun** (images 222 à 226), puis environ 10 images de silhouette en contre-jour clignotant, puis 3 à 4 images plein cadre blanc, noir et couleur (237 à 240). Au total **environ 19 images, soit environ 0,8 s**, avant le plan couleur.
  - Coup de Deku : environ 16 images alternant noir et blanc, blanc uni (568) et noir uni (572), changeant **presque à chaque image** (562 à 577).
  - Voir les planches 10 et 11.
- **Pourquoi.** Casser la continuité visuelle au moment du contact. Le cerveau lit un « choc » que le mouvement seul ne peut pas donner.
- **Quand l'utiliser.** Uniquement le coup fort de la séquence (finisher, coup chargé).
- **Quand l'éviter.** Sur chaque coup d'un combo : cela sature. Sur les coups légers, rien ou un seul flash.
- **R6 : dessin IMPOSSIBLE, équivalent POSSIBLE.**
  - `Highlight` sur les deux personnages (remplissage noir, contour blanc, ou l'inverse) pendant 1 à 3 images.
  - `ColorCorrectionEffect` (contraste et saturation extrêmes, teinte) ou cadre d'interface plein écran noir ou blanc de 1 image.
  - Fond masqué (skybox ou décor temporairement noirs).
  - Alterner les états **une image sur deux** pendant 4 à 8 images **[PROPOSITION inspirée des mesures]**.

### Règle 10 : smears, obake, membres multiples

- **Énoncé.**
  - [LU, Cartwright] « Smears also help fill in the gaps when you need to have a huge motion. » Une attaque se pense comme « anticipation, smear, main key, return » (anticipation, smear, pose principale, retour).
  - [RÉSUMÉ-RECHERCHE] Un smear « defies logic and anatomy » en étirant ou en dupliquant les membres. En japonais, « obake » (お化け) désigne ce type de smear, souvent en trait de couleur (色トレス).
- **Chiffres.** Généralement 1 à 2 images entre deux poses clés très éloignées.
- **Quand l'utiliser.** Dans le trajet entre anticipation et extension, quand ce trajet est trop long pour être lu en 1 à 2 images.
- **Quand l'éviter.** Sur les poses tenues.
- **R6 : déformation IMPOSSIBLE. Substituts POSSIBLES :**
  - Clones « fantômes » du bras (copies semi-transparentes du Right Arm, 2 à 3 positions intermédiaires) affichés 1 à 2 images, soit des membres multiples littéraux.
  - Maillage de smear pré-modélisé (bras étiré en arc) affiché à la place du bras 1 image, soit une variante de swapped geo.
  - Trail ou Beam attaché au poing.
  - GGXrd modélise aussi ses effets en 3D image par image plutôt qu'en billboards [LU].

### Règle 11 : le hitstop (arrêt sur contact)

Le timing est déjà jugé bon ; cette règle est courte.

- **Chiffres.**
  - [RÉSUMÉ-RECHERCHE, Shoryuken/Capcom] SFV : 8, 12 et 15 images à 60 i/s (coups léger, moyen, lourd).
  - L'exemple du séminaire Capcom : 8, 12 et 16 images.
  - Citation reprise par Cartwright [LU] : « You damn well don't make a game without hitstop » (Mike Z).
  - [RÉSUMÉ-RECHERCHE, Genshin] Le « hitlag » ralentit l'attaquant et la cible tandis que l'environnement continue de bouger.
- **R6 : POSSIBLE.** `AnimationTrack:AdjustSpeed(0)` sur les deux pistes pendant N images, pendant que caméra, particules et secousse continuent. C'est le principe Genshin.

### Règle 12 : on tient le pic ; le coup se « lit » à l'arrêt, pas pendant le trajet

- **Chiffres [MESURÉ].**
  - JJK #19 : la pose de contact double Itadori-Todo est tenue **environ 110 images, soit environ 4,6 s**. La pose ne change presque pas ; seul un travelling avant lent bouge (images 417 à 530).
  - OPM #01 : le gros plan « poing au contact » est animé **en 3** (un dessin toutes les 3 images, de très petites variations) pendant **environ 36 images, soit 1,5 s** (1276 à 1311).
  - MHA #10 : la pose « bras tendu, main géante » de Deku est animée **en 2** pendant **environ 24 images, soit 1 s** (578 à 602), avec de petits décalages, une sorte de tremblement.
- **Pourquoi.** Le trajet dure 1 à 3 images, et c'est la pose finale qu'on regarde. Le mouvement « se passe » entre deux dessins.
- **Quand l'utiliser.** Coup fort, finisher.
- **Quand l'éviter.** Dans un combo rapide, où la tenue est remplacée par le hitstop.
- **R6 : POSSIBLE.** Tenir l'extension. Plutôt qu'un gel total, ajouter une **vibration** de ±0,03 à 0,08 stud sur le torse et le bras, changée toutes les 2 à 3 images en easing Constant **[PROPOSITION inspirée des mesures]**. C'est l'équivalent 3D du tremblement du dessin tenu.

### Règle 13 : perspective et poses « Kanada »

- **Énoncé [RÉSUMÉ-RECHERCHE, Pixiv 百科 / CGWORLD].**
  - **金田パース (perspective Kanada)** : déformer volontairement la perspective pour le dynamisme. Exemple type : un bras tendu vers l'adversaire, qui devrait être droit épaule-coude-poignet-poing, est **fortement tordu à partir du coude**, avec le poing dessiné très gros et l'objet tenu encore plus gros. On parle aussi de « うそパース » (fausse perspective).
  - **金田ポーズ (pose Kanada)** : saut jambes arquées (ガニマタ), poignets et chevilles pliés au maximum.
  - [LU, wiki sakugabooru] Kanada : « exaggerated perspective, dynamic posing, and offbeat timing ».
  - [RÉSUMÉ-RECHERCHE, Animétudes] Kanada moderne : surtout en 1, parfois en 2, « exceptionnellement en 3 sur certains impacts », avec des formes angulaires et des mouvements vifs et imprévisibles.
- **R6 : PARTIEL.**
  - Pas de coude ni de poignet ni de cheville : le « coude tordu » est impossible.
  - Le poing énorme n'est accessible que par la règle 3.
  - La pose Kanada en saut est accessible par les hanches (jambes écartées, pieds tournés vers l'extérieur) et des angles francs.
  - Le timing « offbeat » (poses tenues de durées irrégulières) est possible.

### Règle 14 : la caméra est un membre du personnage

- **Énoncé.**
  - [LU, 4Gamer] Dans les supers, GGXrd bouge la caméra « boldly » hors de la vue latérale.
  - Les décors sont construits en fausse perspective, avec des maillages pliés « like a super wide-angle lens » (CGWORLD n°215).
  - [RÉSUMÉ-RECHERCHE, via Kotaku] Motomura : « With 3D characters it is actually fairly difficult to have them look good at this angle… we designed the camera to move during certain special moves ».
  - [MESURÉ] Les plans anime alternent : contre-plongée avec poing au premier plan (OPM, image 08), gros plan du seul poing au contact (image 07), plan large sur l'impact.
- **R6 : POSSIBLE.** CFrame et FieldOfView de la caméra animables à l'image près. Pour le finisher : une coupe caméra devant l'attaquant au moment de l'extension, puis retour caméra joueur.

### Règle 15 (technique ArcSys annexe) : « flipbook 3D » et pièces échangées

- **[RÉSUMÉ-RECHERCHE, DBFZ, polycount/Keo]** Des maillages sont échangés image par image « like a 3D flipbook ». Des effets sont imbriqués et scalés de 0 à 100.
- **[LU]** GGXrd remplace ou ajoute des parties pour les expressions impossibles (yeux ronds comiques, veines de colère) et pour les transformations.
- **R6 : POSSIBLE** via des pièces supplémentaires soudées dont on bascule la Transparency. Même mécanisme que les substituts (c) des règles 2 et 10.

**Récapitulatif de faisabilité R6**

| Technique | Verdict R6 | Substitut |
|---|---|---|
| Clés tenues sans interpolation | POSSIBLE | easing Constant |
| Scale de membres par pose | IMPOSSIBLE | translation, surtout vers la caméra ; pièce échangée ; `Size` par script (non vérifié) |
| Poing géant par perspective | POSSIBLE | en caméra scriptée face au coup |
| Rotations hors anatomie | POSSIBLE | — |
| Dépassement 1 image | POSSIBLE | — |
| Épaule dans le coup | PARTIEL | RootJoint + translation du C0 d'épaule |
| Coude ou poignet cassés, courbure du bras | IMPOSSIBLE | aucun ; compenser par la perspective et le smear |
| Déformation faciale | IMPOSSIBLE | échange de decal |
| Impact frames dessinées | IMPOSSIBLE | Highlight, ColorCorrection, flashes UI |
| Smears déformés | IMPOSSIBLE | clones fantômes, maillage de smear, trails |
| Hitstop | POSSIBLE | — |
| Caméra animée | POSSIBLE | — |

---

## 3) Ce qui différencie un coup de poing anime d'un coup de poing réaliste

Méthode : croisement de [MESURÉ] (JJK #19 images 400 à 530 ; MHA #10 images 540 à 605 ; OPM #01 images 1276 à 1540 ; genga 01 à 05) et des règles [LU] ci-dessus. La colonne R6 donne une piste de traduction.

| Phase | Coup réaliste | Coup anime (observé ou sourcé) | Traduction R6 |
|---|---|---|---|
| **Garde / avant** | Garde compacte, menton protégé, peu de télégraphie | Peut démarrer d'une pose déjà « chargée » ; visage déjà crispé | Pose d'entrée déjà asymétrique, pas d'idle neutre |
| **Anticipation (タメ, « tame »)** | Petit armé ; le poids se charge sur la jambe arrière ; peu visible | **Compression** : le corps s'enroule et descend, la tête disparaît derrière l'épaule, le poing est armé bas à la hanche, derrière le plan du corps. JJK : poing armé à la hanche (409 à 411) puis corps « ramassé », tête rentrée (412 à 414), **en 3** (un dessin toutes les 3 images). Cartwright : même 1 image suffit, mais il en faut toujours au moins une. | Torse penché en avant et vers le bas (RootJoint), torse tourné **à l'opposé** de la cible, bras frappeur ramené en arrière et en bas, tête baissée ; courbe en C comprimée. Tenir 2 à 4 poses. |
| **Déclenchement** | Chaîne cinétique continue et fluide : pied, hanche, épaule, bras | 1 à 2 images de transition ; smear, membres multiples ou rien. Le trajet n'est **pas** montré en détail (Cartwright : « anticipation, smear, main key, return ») | 1 image de fantômes du bras ou de trail ; aucune interpolation (Constant) |
| **Contact / extension** | Bras rarement verrouillé, rotation de hanche mesurée, corps équilibré au-dessus des appuis | Bras **complètement tendu** et **colinéaire** avec le torse et la jambe arrière (droite unique de Mattesi). **Torse projeté bien au-delà de l'équilibre** (JJK : presque horizontal). **Épaule remontée jusqu'au menton, tête rentrée derrière la ligne du bras** (JJK, image 06 ; genga JJK 04). **Poing plus gros que nature** : dessiné gros (Kanada, genga MHA) ou amené vers la caméra (ArcSys) ; il peut égaler la tête (genga 02). Bras opposés en opposition sur une même ligne (Deku, 556 à 560). **1 image de dépassement** au-delà de la pose finale (Cartwright). | Pose d'extension : RootJoint incliné de 30 à 60° vers l'avant **[PROPOSITION]** ; bras tendu + translation vers l'avant de 0,3 à 0,6 stud ; épaule avancée et montée (règle 8) ; tête baissée et avancée ; bras opposé tiré en arrière dans l'axe ; jambe arrière tendue dans la même diagonale. 1 image de dépassement. En caméra de finisher : poing amené vers l'objectif (règle 3). |
| **Impact** | Le poing touche et revient | Hitstop, puis **impact frames** (noir et blanc, négatif, éclat radial) de 1 à 2 images chacune, pendant 0,5 à 0,8 s sur un coup majeur (MHA mesuré : environ 16 à 19 images) | Hitstop (règle 11) + Highlight et ColorCorrection alternés une image sur deux (règle 9) + secousse caméra |
| **Tenue du pic** | Aucune | **Longue** : 1 à 4,6 s mesurées sur des coups majeurs. La pose bouge à peine, animée en 2 ou en 3 ; la caméra ou l'arrière-plan bougent. Gros plans montés : poing seul au contact (OPM, image 07), contre-plongée poing au premier plan (image 08). | Tenir l'extension avec une vibration toutes les 2 à 3 images ; si possible, coupe caméra |
| **Retour (ツメ, « tsume »)** | Rétraction rapide vers la garde | Très court, souvent coupé au montage. Cartwright : ne pas faire d'ease vers l'idle (« your idle animation is a motion in itself »). | 2 à 4 images, sans easing, vers une pose intermédiaire, puis l'idle |

Résumé en une phrase : **le coup réaliste montre le trajet ; le coup anime montre deux poses extrêmes (compression, puis extension en ligne droite hors d'équilibre), sautées en 1 à 2 images, puis tient la seconde en la sur-dimensionnant (perspective, impact frames, gros plans).**

---

## 4) Timing anime (bref, puisque le timing est jugé bon)

- **Animation limitée.** GGXrd : 15 poses/s en cinématique ; en combat, durées par pose choisies à la main (« 2F, 3F, 5F, 1F, 1F, 2F, 2F, 3F, 4F » à 60 i/s) [LU]. Cartwright : ne pas tenir chaque dessin la même durée (par exemple « 4 frames at 60fps, approximately animating on twos ») ; tenir plus longtemps les clés et leurs voisines [LU]. Note de la traduction 4Gamer : la TV est à environ 24 i/s, en 2 ou en 3, avec des passages en 1 pour les moments intenses [LU].
- **Mesures [MESURÉ, 23,976 i/s].** Impact frames en 1. Pose tenue avec tremblement en 2 (MHA). Gros plan tenu en 3 (OPM). Anticipation en 3 puis extension changeant presque à chaque image (JJK). Kanada moderne : surtout en 1, parfois en 2, en 3 sur certains impacts [RÉSUMÉ-RECHERCHE].
- **Tame et tsume [RÉSUMÉ-RECHERCHE, glossaires japonais].**
  - タメ (tame, « charge ») : montrer longtemps la phase où l'on accumule la force.
  - ツメ (tsume, « compression ») : intervalles resserrés près de la clé (先ヅメ, compression au départ ; 後ヅメ, compression à l'arrivée), pour que la partie rapide soit très rapide.
  - La timing chart « ├┼┼──┤ » tracée sur le genga en donne l'instruction ; on en voit une sur le genga JJK, image 04.
  - Pour l'action : charge longue, lancer court.
- **Hitstop.** SFV 8, 12 et 15 images à 60 i/s (léger, moyen, lourd) [RÉSUMÉ-RECHERCHE].

---

## 5) Images téléchargées

Toutes se trouvent dans `/tmp/claude-0/-home-user-Jeux/4796ac9e-8e41-51f7-91c4-7b92a6a187d0/scratchpad/tutos/anime3d/`. Elles servent à l'étude seulement ; ce sont des œuvres protégées, à ne pas committer.

| Fichier | Ce qu'il montre | Source |
|---|---|---|
| `01_nakamura_mha_impact_frames_genga.png` | 5 genga d'**impact frames** de Nakamura : silhouette dans un éclat radial, négatif, plan quasi abstrait | https://www.sakugabooru.com/post/show/294895 |
| `02_nakamura_mha_deku_bras_raccourci_main_geante_genga.png` | Genga de Nakamura : Deku en vol, **bras tendu vers la caméra, main à peu près de la taille de la tête, avant-bras très raccourci**, corps plus petit derrière | https://www.sakugabooru.com/post/show/294900 |
| `03_mha_genga_main_tendue_vers_camera.jpg` | Genga MHA : main tendue vers l'objectif, poing et main surdimensionnés au premier plan | https://www.sakugabooru.com/post/show/221652 |
| `04_jjk_itadori_coup_de_poing_genga_A.png` | Genga JJK : Itadori frappe ; **épaule remontée, tête projetée au-dessus de la ligne du bras**, mâchoire crispée ; poing de la taille du visage ; timing chart « ツメ » visible en haut à gauche | https://www.sakugabooru.com/post/show/214744 |
| `05_jjk_itadori_coup_de_poing_genga_B.jpg` | Genga JJK : coup de poing, tête plongée sous le bras qui sort du cadre, regard vers la cible | https://www.sakugabooru.com/post/show/228260 |
| `06_jjk19_itadori_todo_double_poing_contact_tenu.png` | Image extraite de JJK #19 (image 450) : **pose de contact tenue environ 4,6 s** ; torse presque horizontal, tête rentrée derrière l'épaule, bras tendu dans l'axe | https://www.sakugabooru.com/post/show/146024 |
| `07_opm01_poing_contact_gros_plan_tenu_en_3s.png` | Image extraite d'OPM #01 (image 1300) : **gros plan du seul poing au contact**, tenu environ 1,5 s en 3 | https://www.sakugabooru.com/post/show/193721 |
| `08_opm01_contreplongee_poing_premier_plan.png` | Image extraite d'OPM #01 (image 1380) : **contre-plongée, poing au premier plan plus gros que tout le reste** | https://www.sakugabooru.com/post/show/193721 |
| `09_mha_s2e10_nakamura_deku_extension_main_geante.png` | Image extraite de MHA S2 #10 (image 586) : la pose du genga 02 à l'écran, **bras vers la caméra, main géante**, tenue environ 1 s en 2 | https://www.sakugabooru.com/post/show/281209 |
| `10_mha_s2e10_nakamura_impact_frames_planche_24fps.jpg` | Planche que j'ai composée, **image par image** (212 à 243) : pose, puis impact frames en 1, puis flashes. Montre le **timing réel** des impact frames. | idem 281209 |
| `11_mha_s2e10_nakamura_deku_sequence_planche_24fps.jpg` | Planche image par image (554 à 603) : lancée de Deku (bras en opposition), impact frames alternés, pose tenue en 2, puis flash vers l'objectif | idem 281209 |
| `12_jjk19_anticipation_vers_contact_planche_24fps.jpg` | Planche image par image (400 à 431) : **anticipation en compression** (poing armé à la hanche, tête rentrée, en 3) puis extension | https://www.sakugabooru.com/post/show/146024 |

**Image voulue mais non obtenue** : la comparaison GGXrd « avec et sans bone scaling » (PDF 4Gamer et diapositives GDC, sur des miroirs bloqués).

---

## 6) Incertitudes et limites

1. **Je n'ai pas vu la conférence GDC 2015 de Motomura** (vidéo et PDF bloqués). Tout ce qui concerne GGXrd vient de la traduction fan (DeepL/Yandex relus par Leo Bruno) de l'article 4Gamer et des diapositives ArcSys, lue en texte OCR. Les citations sont donc des **traductions de traductions**. « 5F » est ma lecture de l'OCR « SF ».
2. **Aucun facteur d'échelle chiffré (poing ×N) n'a été trouvé** dans les sources lues. Les valeurs en studs ou en degrés de ce rapport sont des **[PROPOSITION]** à calibrer par capture.
3. Les éléments **[RÉSUMÉ-RECHERCHE]** (Kotaku / New Frame Plus, Keo/DBFZ, Kanada, Camera-O-Matic, tame/tsume, hitstop SFV, Genshin, silhouettes) viennent de résumés automatiques du moteur de recherche, sans lecture de la page. Ils sont plausibles mais peuvent contenir des erreurs d'attribution. L'exemple « bras de robot vers la caméra, pièces fortement déformées » n'a pas de source identifiée précisément.
4. **Mesures [MESURÉ].** J'ai détecté les tenues par différence de pixels, puis contrôlé visuellement. Les mouvements de caméra, le compositing et les effets animés en 1 peuvent masquer des tenues du personnage (cas d'OPM #12, inexploitable). Il s'agit de 4 extraits seulement : ce sont des exemples, pas une statistique.
5. **Rien de primaire sur la 3D anime de combat récente** (MAPPA, Polygon Pictures, Sanzigen, Genshin, HSR, Wuthering Waves, Tekken, SF6, Virtua Fighter) : sites bloqués. L'interview de Nakamura (Wave Motion Cannon) n'a pas pu être lue ; je ne cite rien de lui en dehors des faits de fiche.
6. **Côté Roblox.** L'existence de `Enum.PoseEasingStyle.Constant` et le comportement de `AdjustSpeed(0)` pour le hitstop sont écrits de mémoire, à vérifier dans l'éditeur. Le changement de `BasePart.Size` d'un membre R6 pendant une animation (substitut au scale) n'a pas été testé (réplication, recalage C0/C1).
7. **Portée.** Les règles 3 et 4 (tricher à la caméra) supposent une caméra connue. En caméra de jeu libre, seules les règles de silhouette, de ligne d'action, de clés tenues, d'épaule et de dépassement s'appliquent pleinement.
