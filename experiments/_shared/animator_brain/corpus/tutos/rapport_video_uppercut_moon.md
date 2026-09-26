# Étude visuelle : « [OLD] How to animate R6 SMOOTHLY (Moon Animator Tutorial) »

Vidéo `0vjAiAR-YFk.mp4`, 761 s, 640x360, 30 i/s. Filigrane « @VoidGamrTheMonke ».
Pas de son. En revanche, **tout le tuto est sous-titré à l'écran** (texte blanc
incrusté) : les citations ci-dessous sont recopiées depuis l'image.
Le coup animé est un **uppercut** (texte à 39 s), sur un rig R6 « TemplateR6 »
dans Moon Animator 2, avec le plugin Phobos Rotation (manipulateur « trackball »).

Méthode : une image toutes les 4 s, plus les changements de plan (70 images) ;
une image toutes les 0,5 s passée à un détecteur de texte incrusté (≈105 états de
sous-titres distincts, tous lus) ; recadrages x3 de la timeline Moon Animator
(≈60 instants) ; extraction à 30 i/s des lectures (intro, torse seul, astuces 1 et
2, résultat final). Travail dans `tutos_v/work_charlotte/` (planches `sheet_*.png`,
`cs_*.png`, `zoom/*.png`).

Légende : **[VU]** = lisible ou visible à l'écran ; **[DÉDUIT]** = mon interprétation.

---

## 1. Déroulé minuté

| Temps | Contenu |
|---|---|
| 0–4 s | Démo d'un combat (perso blanc contre un mur, flashs rouges d'impact). [CONTREDIT 2026-09-26 : l'intro a deux personnages et trois impacts, voir corpus/etude_c4/B1_moon_smooth_r6.md §4] « Want to animate like this? » [VU] |
| 4–13 s | « Well Today I will Show you how to make your R6 Animations Smooooooth! » ; « You will need: Moon Animator 2, Phobos Rotation, VoidMonke's Animation Plugin » [VU] |
| 14–18 s | Rig « IK Adornments » (TemplateR6 marqué FRONT/F/R/L/B) [VU] |
| 19–28 s | « First, Grab The Timeline and pull it closer until it counts up in 5 » → graduations 0, 5, 10, 15… ; « this is so we can animate in 5s » [VU] |
| 32–56 s | « Now for the Torso Move it down slightly » ; « For this tutorial we are going to be animating an uppercut! » ; pose de départ au trackball Phobos (« press T twice and leftclick to confirm ») ; « Something like that! » [VU] |
| 58–64 s | « For animation we need to use the key points of linear easing » / « this is to make all movements flow nicely, even with linear! » [VU] |
| 64–82 s | **Point ONE: Anticipation**, torse, clé à la frame 5. « A small motion to show the start/build up of speed » ; « Tip: i use phobos trackball for nearly everything, but its not good for precision and bending » ; « The red thing (onion Skin/Ghost rig) can be toggled with B » [VU] |
| 82–98 s | **Point TWO: Drag**, clé à la frame 10. « Helps add the wavy movement to the animation » [VU] |
| 100–146 s | **Point THREE: Middle**, clé à la frame 15. « The Main Part of the movement your animating » [VU] |
| 146–185 s | **Point FOUR: Exaggeration**, clé à la frame 20. « Makes ur animation seem more A L I V E » ; « Ignore what im doing withe keyframes, i fix it later » [VU] |
| 185–195 s | **Point FIVE: MORE Drag/Exaggeration**, clé à la frame 25 (puis 30). « its purely your choice on what u pick, i chose more exaggeration » [VU] |
| 195–266 s | « Now IMPROVISE and add some wiggle ». Clés toutes les 5 frames de 35 à 60. « I reccomend your wiggle going in SMALL Circles and keep getting slower to give the effect of weight and energy easing out » ; « use phobos for that tho lol » ; « Make sure to constantly replay your animation to see if anything looks off (eg. i made my wiggle to rough) » ; « Fixing wiggle... » (x5) [VU] |
| 267–271 s | « If you followed the steps your animation should look like this! » + lecture du torse seul [VU] |
| 271–287 s | **Extra Tip Part one** (détails en §3) ; « this makes it look like speed is building up! » ; « Though I DO NOT reccomend doing this for this animation » [VU] |
| 288–297 s | **Extra Tip Part two** (détails en §3) ; « It will make the movement look more faster and clean! » [VU] |
| 302–345 s | Bras gauche. « Seeming as the left arm doesnt do much in the animation, lets do that first » ; « Because there is barely any movement for this arm, just move it with the torso » ; « Left arm base complete! » ; « Now we need to add some drag and exaggeration to anything that seems too bland » [VU] |
| 384–545 s | Bras droit (celui de l'uppercut) : « This Will also follow the key points of linear easing » ; « Now we are going to be animating just like we did with the torso » ; mêmes Points ONE à FIVE ; « you can also move this with the torso if you like » ; « Drag on arms is very different from the torso » ; « It may look dislocated but it helps everything flow smoothly! » ; « Once you have done that and all the movement from the hand has stopped, for every other keyframe move it with the torso just like we did with the left arm » ; « Arms Complete! » [VU] |
| 552–626 s | Tête. « The Head is probably the easiest to animate » ; « we are going to be using a mix of onion skin and exaggeration to make the head look smooth » ; « Use Onion Skin/Ghost rig (B) to see the first frame of your heads direction » ; « line up the white line so that its touching the red one » ; « For the middle exagerate it depending on the direction of the torso » ; « After you have done the head up to the more drag/exaggeration, start to move the head with the torso as well » [VU] |
| 632–745 s | Jambes, « (my least favourite) ». « Once again press B to use onion skin/Ghost rig on the first frame » ; « For Every keyframe move the legs so the white ball is inside the red ones » ; « Tip: ONLY use position to move the leg up and down, not left or right » ; « For this leg i made it raise so we can just make it move with the torso » (lecture en x10) [VU] |
| 746–752 s | Résultat final en boucle : « Congrats! you have now learnt linear easing! » [VU] |
| 752–761 s | « pls subscribe if u made it this far » [VU] |

---

## 2. Règles concrètes

**R1. Grille de 5 frames à 60 i/s, en linéaire.**
- Énoncé : régler la timeline pour qu'elle « counts up in 5 » et « animate in 5s » ; « use the key points of linear easing ».
- Preuve : 19,5–25,5 s (graduations 0, 5, 10, 15… 35) ; 58–64 s (texte « linear ») ; 272 s, en-tête Moon Animator « 1:00 | 60f » et « 13 KEYFRAMES | 60 FPS » [VU].
- Quand : toutes les parties (torse, bras, tête, jambes).
- Limite : **aucun menu d'easing n'est montré** dans toute la vidéo (vérifié image par image de 55 à 64 s et sur les ≈60 recadrages de timeline). « Linear » n'est affirmé que par le texte. [DÉDUIT] C'est probablement le réglage par défaut de Moon Animator, mais la vidéo ne le montre pas.

**R2. Une clé = un rôle, dans un ordre fixe** : départ (0) → Anticipation (5) → Drag (10) → Middle (15) → Exaggeration (20) → More Drag/Exaggeration (25–30) → wiggle (35–60).
- Preuve : les titres « Point ONE…FIVE » s'affichent pendant que la tête de lecture est sur 5, 10, 15, 20, 25/30 (recadrages timeline à 64,5, 83, 100, 150, 185 et 190 s) [VU].
- Limite : les numéros de frame changent ensuite avec l'astuce 2 (voir §3).

**R3. Le torse en premier, puis les membres calés sur ses clés.**
- Le torse est animé seul (64–267 s), puis le bras gauche, le bras droit, la tête et les jambes.
- Preuve : timelines à 319, 332, 394, 444, 562, 639 et 734 s. Chaque nouvelle partie reçoit ses clés **exactement aux mêmes frames que le torse** (0, 5, 10, 12, 15, 20…). À 745 s, les 6 pistes ont des clés alignées verticalement (40, 45, 50, 55) [VU].
- [DÉDUIT] Ce tuto ne produit **aucun décalage temporel de clés entre membres**. L'overlap et le drag sont intégrés dans les poses : le membre est laissé en retard dans la pose, à la même frame.

**R4. Membre passif = collé au torse.**
- « Because there is barely any movement for this arm, just move it with the torso » (319 s) ; même consigne pour le bras droit une fois la main arrêtée (525 s), pour la tête après « more drag » (611 s) et pour une jambe (734 s) [VU].
- [DÉDUIT] Pas d'animation propre : le membre reprend la rotation du torse.

**R5. Le drag des bras accepte une translation (« disloqué »).**
- « Drag on arms is very different from the torso » ; « It may look dislocated but it helps everything flow smoothly! »
- Preuve : 419–429 s. Le bras droit est visiblement décollé de l'épaule, en bas et en retrait, à la clé 10 [VU].
- Limite : je ne peux pas lire la valeur de la translation.

**R6. L'exagération dépasse la pose finale.**
- Bras droit : à la clé 15 (après l'astuce 2), le poing passe nettement au-dessus de la tête (480–512 s) [VU].
- Pose tenue finale : torse fortement penché, environ 30–40° (estimation visuelle), jambes fléchies en garde (747 s) [VU].

**R7. La tenue n'est pas figée : le « wiggle ».**
- « small circles », « keep getting slower », « energy easing out ». Clés toutes les 5 frames de 35 à 60 (220–262 s).
- [DÉDUIT] C'est un amorti qui décroît, fait à la main, en clés linéaires.
- Limite : l'auteur lui-même a dû le reprendre (« i made my wiggle to rough », « Fixing wiggle... »).

**R8. Tête : garder la direction du regard.** [CONTREDIT 2026-09-26 : vrai pour ce tuto, pas universel : l'uppercut du pack ne fait pas cette contre-rotation (la tête suit le lacet, élévation ≤ +7°), voir corpus/etude_c4/A4_pack_battleground.md §4]
- Utiliser l'onion skin (touche B) de la frame 0 et aligner la ligne blanche sur la rouge (567–574 s). On exagère seulement au « Middle », « depending on the direction of the torso » (597 s) [VU].

**R9. Jambes : pieds plantés.**
- À chaque clé, la boule blanche doit rester dans les boules rouges du fantôme de la frame 0 (662 s).
- « ONLY use position to move the leg up and down, not left or right » (667 s) [VU].
- [DÉDUIT] C'est un verrouillage des pieds manuel, sans IK. La jambe ne se translate que verticalement.

**R10. Pose de départ : torse abaissé.**
- « Move it down slightly » (32 s), c'est-à-dire accroupi, jambes fléchies [VU].
- À la frame 0 du résultat final, le torse est vu de profil (tourné à ~90° par rapport au « FRONT » de la tenue) et accroupi (746,77 s) [VU].

**R11. Outil : trackball Phobos pour presque tout.**
- Mais « not good for precision and bending » (71 s) [VU].
- On aperçoit des infobulles « Mode (R) Position / Rotation, Space (Y) World / Local » à côté du gizmo, trop petites pour relever des valeurs [VU partiel].

---

## 3. Easing, espacement et overlap observés (valeurs)

**Easing** : linéaire, annoncé par le texte (58, 62, 389 et 747 s). Aucune courbe ni aucun menu In/Out n'est visible.

**Cadence** : 60 i/s dans Moon Animator (« 60 FPS »). Durée avant les astuces : 60 frames, soit 1,00 s. Le torse porte 13 clés.

**Espacement du torse avant les astuces** (270–272 s) [VU] :
- clés à 0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60 ;
- 13 clés, pas uniforme de 5 frames (83 ms).

**Extra Tip one** (272–281 s) [VU] :
- on sélectionne les clés 2 à 13 et on les décale de +5 ;
- clés à 0, 10, 15, 20… ;
- le premier intervalle double (10 frames), ce qui donne « speed is building up » (un ralenti au départ) ;
- l'auteur le **déconseille** pour cet uppercut.

**Extra Tip two, conservée** (288–297 s) [VU] :
- on rapproche la clé « Middle » de la clé « Drag » de 2 ou 3 frames : 15 → 12 ;
- on décale toutes les clés suivantes de −5 ;
- résultat : 0, 5, 10, 12, 15, 20, 25, 30, 35, 40, 45, 50, 55 ;
- intervalles 5, 5, **2, 3**, 5, 5… ;
- durée 55 frames (0,92 s) ;
- « more faster and clean ».

**Correspondance finale clé → rôle** [DÉDUIT de la timeline et des titres] :

| Frame | Rôle |
|---|---|
| 0 | départ |
| 5 | anticipation |
| 10 | drag |
| 12 | middle |
| 15 | exagération |
| 20 | plus de drag / exagération |
| 25–55 | wiggle, amorti décroissant |

**Lecture finale mesurée à 30 i/s** (746,73–747,73 s, `best/08`) [VU] :
- départ de profil, accroupi (746,77) ;
- 3 à 4 images vidéo d'anticipation et de drag, bras droit bas et en travers de la hanche (746,80–746,90) ;
- **le bras passe du bas au-dessus de la tête en une seule image vidéo** (746,90 → 746,93), ce qui correspond à l'intervalle de 2 frames à 60 i/s entre les clés 10 et 12 ;
- pic à 746,97–747,03 ;
- puis environ 22 images vidéo (≈0,7 s) de tenue avec petite dérive circulaire.

[DÉDUIT] Donc environ 0,2 s d'action pour environ 0,7 s de tenue « vivante ».

**Overlap / décalage** :
- aucun décalage de clés entre parties : toutes les pistes ont des clés aux mêmes frames (R3) ;
- l'overlap vient uniquement du contenu des poses : bras en retard et disloqué à la clé 10, tête qui garde sa direction, membres « move with the torso » après l'arrêt.

**Arcs** : aucun outil de trajectoire n'est montré. [DÉDUIT] Le drag (clé 10) placé entre l'anticipation et le « middle » sert de point de passage qui courbe la trajectoire du poing, à la place d'un easing.

**Clés tenues** : aucune clé dupliquée pour figer une pose. La tenue est toujours animée par le wiggle.

---

## 4. Images les plus parlantes (sauvegardées)

Images clés : gardées hors dépôt (scratchpad de session, vidéo protégée), non commitées.

1. `01_timeline_pas5_025s.png` : timeline graduée de 5 en 5, « animate in 5s ».
2. `02_linear_easing_058s.png` : « key points of linear easing ».
3. `03_tip1_60f_13keys_60fps_272s.png` : en-tête « 1:00 | 60f », « 13 KEYFRAMES | 60 FPS », clés tous les 5.
4. `04_tip2_cle_milieu_a_12_289-292s.png` : clé milieu déplacée à 12, « normally by 2 or 3 frames ».
5. `05_drag_bras_disloque_426s.png` : bras droit décollé, « may look dislocated ».
6. `06_wiggle_petits_cercles_198s.png` : règle du wiggle en petits cercles de plus en plus lents.
7. `07_timeline_finale_6parts_memes_cles_745s.png` : les 6 pistes, clés alignées sur les mêmes frames.
8. `08_resultat_final_30ips_746.73-747.03s.png` : 10 images consécutives du résultat (départ de profil, drag bas, bras en haut en une image, pose inclinée).

---

## 5. Confronté à l'hypothèse « TSB relie des poses clés espacées d'environ 4 images (60 i/s) en interpolation linéaire ; nos exports sont cuits image par image depuis des courbes lissées »

**Ce qui confirme :**
- Cette pratique communautaire R6 revendique explicitement le **linéaire** (« even with linear! »).
- Elle travaille à **60 i/s** avec des clés **toutes les 5 frames**, et même **2–3 frames** sur la phase de frappe. C'est le même ordre de grandeur que « environ 4 images à 60 i/s ».
- Le « smooth » du titre ne vient **pas** de courbes d'easing. Il vient de quatre choses :
  - (a) le rôle des poses : anticipation, drag, middle, exagération, drag ;
  - (b) l'espacement : resserrer 15 → 12 pour la frappe, et éventuellement étirer le départ ;
  - (c) le retard intégré dans les poses (bras disloqué, tête qui garde sa direction) ;
  - (d) un wiggle amorti fait à la main en clés linéaires.
- Le résultat mesuré est un « snap » : le bras traverse tout son arc en une image vidéo, soit 2 frames à 60 i/s. [DÉDUIT] Un export cuit depuis des courbes lissées (type spline ou ease in/out) arrondirait justement ces coins linéaires et étalerait ce snap. Cela rejoint le défaut désigné : corps qui ne s'engage pas, mouvement mou.
- Côté pose : départ de profil et accroupi, puis pose finale au torse très penché et au poing au-dessus de la tête. C'est l'inverse d'un « torse vertical, charge en croix symétrique ».

**Ce qui nuance ou ne tranche pas :**
- Ce n'est **pas** une animation de TSB. Le tuto montre une pratique Roblox/Moon Animator, pas les fichiers de TSB. Il ne prouve rien sur TSB lui-même.
- L'espacement vu ici n'est pas constant. Il est de 5 par défaut et **volontairement irrégulier** là où ça compte (2, 3 frames). Un « environ 4 images » uniforme serait une simplification.
- Ici, tous les membres ont leurs clés **aux mêmes frames**. Si notre pipeline suppose un overlap par décalage temporel des clés, ce tuto ne le confirme pas : il le fait par la pose.
- La « tenue » n'est pas une clé figée mais environ 0,7 s de micro-mouvement amorti. Si nos exports tiennent la pose immobile, c'est un écart.

---

## 6. Incertitudes

- **Easing** : aucun menu ni aucune courbe n'est visible. « Linear » repose uniquement sur les sous-titres.
- **Valeurs angulaires et translations** : aucun nombre n'est lisible. Les infobulles de Phobos sont trop petites en 640x360. Tous les angles cités (~30–40°, ~90°) sont des estimations à l'œil.
- **Période de la boucle finale** : environ 1,1 s mesurée par énergie de mouvement, contre 55 frames à 60 i/s (0,92 s) attendues. L'écart vient peut-être de la cadence d'enregistrement, d'une pause de bouclage de Moon Animator, ou des mouvements de caméra. Non tranché.
- **Frames 25/30 du Point FIVE** : entre 162 et 190 s, l'auteur déplace des clés (« i fix it later »). La position exacte avant l'astuce 2 (25 ou 30) est donc incertaine. L'état final (13 clés, 0–55, avec 12) est, lui, clairement lisible à 300 et 745 s.
- **Astuce 1 contre astuce 2 en lecture** : le personnage est trop petit à l'écran pour mesurer proprement la différence d'espacement dans les lectures. Je m'appuie sur les timelines, pas sur la lecture.
- **Démo d'intro (0–4 s)** : l'animation n'est pas identifiée. Rien n'indique que c'est le résultat de ce tuto (autre personnage, autre décor).
- **Couleurs des membres** : je lis R, L, F, B sur les faces. L'identification droite/gauche dans les lectures lointaines est parfois incertaine.
