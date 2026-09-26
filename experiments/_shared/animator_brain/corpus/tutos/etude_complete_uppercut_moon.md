# Étude complète : « How to animate R6 SMOOTHLY (Moon Animator) » (VoidGamrTheMonke)

Vidéo entière regardée à 1 image/s (761 images, planches de 20) par moi, sans
grille d'hypothèses ; les démos animées sont revues image par image. Tout texte
à l'écran est relevé. Notes brutes au fil de la lecture, synthèse à la fin.

## Déroulé et textes (au fil de l'eau)

- 0-4 s : démo d'intro « Want to animate like this? » : un perso R6 (avatar
  habillé, pas le mannequin) contre un grand mur gris, dans un coin. [CONTREDIT 2026-09-26 : l'intro a deux personnages et trois impacts, pas un perso seul contre le mur, voir corpus/etude_c4/B1_moon_smooth_r6.md §4] [démo à
  revoir image par image]
- 4-7 s : « Well Today I will Show you how to make your R6 Animations Smooooooth! »
- 8-12 s : « You will need: Moon Animator 2 ; Phobos Rotation ; VoidMonke's
  Animation Plugin » (« These will all be linked in the desc »).
- 13-17 s : « I will be using this rig for the animation, you too can make
  this rig using "IK Adornments" » (mannequin R6 rouge étiqueté FRONT / F / R / L / U).
- 18-28 s : « First, Grab The Timeline and pull it closer until it counts up
  in 5 » ; « this is so we can animate in 5s » (graduation 0, 5, 10, 15…).
- 30-35 s : « Now for the Torso Move it down slightly » (pose de départ : le
  torse descend un peu).
- 38-42 s : « For this tutorial we are going to be animating an uppercut! »
- 45-49 s : « For the Starting pose we will use Phobos Trackball (press T
  twice and leftclick to confirm) to make the starting pose ».
- 50-56 s : « Something like that! » : pose de départ vue en 3/4 : corps tourné,
  penché, bras repliés (garde basse), déjà hors du neutre.
- 57-61 s : « For animation we need to use the key points of linear easing »
- 61-63 s : « this is to make all movements flow nicely, even with linear! »
- 65-79 s : « Point ONE: Anticipation » ; « A small motion to show the start/
  build up of speed » ; « Tip: i use phobos trackball for nearly everything,
  but its not good for precision and bending ». La pose d'anticipation : le
  corps pivote (on voit le côté R puis le dos), se ramasse.
- 80-81 s : « The red thing (onion Skin/Ghost rig) can be toggled with B » :
  il pose CHAQUE clé en voyant la précédente en fantôme rouge.
- 82-99 s : « Point TWO: Drag » ; « Helps add the wavy movement to the
  animation ». La pose de drag : corps qui se redresse et tourne, bras qui
  traîne derrière. Il passe beaucoup de temps de profil (bras vert) à
  régler l'écart entre la pose et le fantôme.
- 100-146 s : « Point THREE: Middle » ; « The Main Part of the movement your
  animating ». Longue retouche (46 s) du bras qui frappe, vu de côté : l'écart
  entre le fantôme et la nouvelle pose est GRAND (le bras balaie ~90-120°
  d'une clé à la suivante).
- 147-184 s : « Point FOUR: Exaggeration » ; « Makes ur animation seem more
  A L I V E » ; « Ignore what im doing withe keyframes, i fix it later ». La
  pose d'exagération : tout le corps bascule fortement sur le côté (~30-40°),
  une jambe décollée, le bras monte. Elle DÉPASSE la pose du milieu.
- 185-193 s : « Point FIVE: MORE Drag/Exaggeration » ; « its purely your
  choice on what u pick, i chose more exaggeration ».
- 194-240 s : « Now IMPROVISE and add some wiggle » ; « I reccomend your
  wiggle going in SMALL Circles and keep getting slower to give the effect of
  weight and energy easing out » ; « use phobos for that tho lol » ; « Make
  sure to constantly replay your animation to see if anything looks off (i
  made my wiggle to rough) ».
- 240-256 s : suite du wiggle (vue de profil), accéléré x5 : « Fixing
  wiggle... ». Il rejoue, trouve que c'est trop brusque, corrige.
- **256-270 s : « If you followed the steps your animation should look like
  this! »** : on voit jouer le résultat, **AVANT TOUT BRAS**. Tout le
  mouvement (anticipation, drag, milieu, exagération, wiggle) a été posé
  **sur le torse seul** (les jambes suivent). [à revoir image par image]
- 271-279 s : « Extra Tip Part one: if we move the second and so on
  keyframes of the torso across by an extra 5 » ; « this makes it look like
  speed is building up! » ; « Though I DO NOT reccomend doing this for this
  animation ».
- 288-296 s : « Extra Tip Part two: If we move the middle keyframe closer to
  the drag (normally by 2 or 3 frames) and move the rest 5 to the left » ;
  « It will make the movement look more faster and clean! ».
- **301 s : « Now Lets animate the arms! »** : les bras viennent APRÈS, par-
  dessus un corps qui porte déjà tout le mouvement.
- 305-316 s : « Seeming as the left arm doesnt do much in the animation, lets
  do that first » ; « Posing.. » (x5) ; « Very Noice ».
- 318-319 s : « Because there is barely any movement for this arm, just move
  it with the torso ».
- 320-340 s : pose du bras gauche (x5), vue de dessous / de côté ; « Left arm
  base complete! ».
- 345-349 s : « Now we need to add some drag and exaggeration to anything
  that seems too bland » : il repasse sur CHAQUE clé du bras pour l'exagérer
  s'il la trouve fade (jugement à l'œil, en rejouant).
- 350-379 s : retouches (rotation Phobos) ; « Very good! ».
- 383-386 s : « Now we are going to do the uppercut/Right Arm » ; « This Will
  also follow the key points of linear easing » ; « Posing.. » (x5).
- 402-409 s : « Now we are going to be animating just like we did with the
  torso » ; « Point ONE: Anticipation » ; « you can also move this with the
  torso if you like » : le bras droit passe par les 5 mêmes rôles que le torse.
- 417-440 s : « Point TWO: Drag » ; « Drag on arms is very different from
  the torso » ; « It may look dislocated but it helps everything flow
  smoothly! » : au drag, le bras reste TRÈS en arrière et en bas (il traîne
  derrière un corps qui a déjà tourné), et il est déboîté de l'épaule.
- 444-475 s : « Point THREE: Middle » : le bras droit monte TOUT DROIT au-
  dessus de la tête ; le corps est couché sur le côté (~40-45°), la jambe
  droite part sur le côté. Grande diagonale unique poing → pied.
- 476-515 s : « Point FOUR: Exaggeration » (bras droit) : le bras reste
  vertical au-dessus de la tête, le corps continue de pencher ; plusieurs
  essais de rotation du bras, gardés ou jetés à l'œil.
- 515-523 s : « Point FIVE: MORE Drag/Exaggeration » ; « Once again, i chose
  more exaggeration ».
- 524-531 s : « Once you have done that and all the movement from the hand
  has stopped, for every other keyframe move it with the torso just like we
  did with the left arm » : quand le coup est fini, le bras SUIT le torse
  (il ne s'anime plus seul).
- 543-547 s : « Arms Complete! ».
- 550-559 s : « The Head is probably the easiest to animate » ; « we are
  going to be using a mix of onion skin and exaggeration to make the head
  look smooth ».
- 561-575 s : « first make usre you have posed the head » ; « Use Onion
  Skin/Ghost rig (B) to see the first frame of your heads direction » ;
  « line up the white line so that its touching the red one » : la tête
  garde le MÊME regard que la 1re image (elle reste pointée sur la cible
  pendant que tout le corps bouge) : c'est une contre-rotation.
- 596-600 s : « For the middle exagerate it depending on the direction of the
  torso » : au milieu (le coup), la tête accentue le mouvement du torse.
- 610-615 s : « After you have done the head up to the more drag/
  exaggeration, start to move the head with the torso as well ».
- 625-629 s : « Now you have done the head! ».
- 631-636 s : « And finally, the Legs! (my least favourite) » ; « Posing.. ».
  ORDRE DE TRAVAIL COMPLET : torse (tout le mouvement) → bras gauche (libre)
  → bras droit (le coup) → tête → jambes EN DERNIER.
- 636-657 s : pose des jambes clé par clé (x5) : les jambes sont PLIÉES,
  écartées, genoux vers l'extérieur, un pied en arrière ; elles ne restent
  jamais droites sous le corps.
- 657-661 s : « Once again press B to use onion skin/Ghost rig on the first
  frame » ; 662-666 s : « For Every keyframe move the legs so the white ball
  is inside the red ones » : les PIEDS restent plantés à leur place de la 1re
  image (le corps bouge, les pieds non), vérifié au fantôme.
- 667-671 s : « Tip: ONLY use position to move the leg up and down, not left
  or right ».
- 685-720 s : jambes clé par clé en x10 (beaucoup de temps).
- 706-716 s : (jambes) « For this leg i made it raise so we can just make it
  move with the torso ».
- 746-751 s : « Congrats! you have now learnt linear easing! ». 752-761 s :
  écran noir « pls subscribe if u made it this far ».

## Le résultat, image par image (746,6 s, 30 i/s, recadré)

- Images 5-9 : pose de départ : accroupi, torse tourné (on voit le côté/dos),
  bras repliés contre le corps.
- **Image 10 : tout change en UNE image vidéo** : le bras droit est déjà à la
  verticale au-dessus de la tête.
- Images 10-38 (~1 s) : pose de fin **tenue**, qui respire à peine (wiggle).
- **La pose de fin** : très BASSE et LARGE : jambes très écartées et fléchies,
  genoux vers l'extérieur ; tout le corps penche sur le côté (~35-40° de
  roulis, pas vers l'avant) ; le bras qui frappe est vertical ; le perso a
  perdu ~1/3 de sa hauteur. Silhouette en triangle, pas en colonne.
- Le coup lui-même dure ~5 images vidéo (0,17 s). **Ce qu'on retient à la
  lecture, c'est la pose tenue d'après**, pas le trajet.
- Démo d'intro (0-4 s, contre un mur) : même logique : des éclats (flash
  rouge/blanc) sur 1-2 images, et entre eux le perso reste ramassé très bas
  contre le mur.

## Ce que ce tuto m'apprend réellement (et en quoi il est meilleur que nous)

1. **L'ordre de travail est l'inverse du nôtre.** Lui : le TORSE porte tout
   le mouvement (anticipation, drag, milieu, exagération, amorti) et il le
   rejoue SEUL, jusqu'à ce qu'il lise bien, avant qu'un seul bras bouge.
   Puis le bras libre, puis le bras qui frappe, puis la tête, puis les
   jambes (en dernier, pieds collés à leur place de départ). Nous :
   `dragon_clip.py` part du POING (cible de contact sur la victime, IK des
   mains, `fitp` place le corps pour que le bras atteigne la cible). Chez
   nous le corps est une conséquence du bras ; chez lui le bras est une
   conséquence du corps. **C'est probablement la cause de « trop simple » :
   notre corps n'a jamais sa propre courbe.**
2. **Chaque clé a un RÔLE nommé** (anticipation, drag, milieu, exagération,
   plus d'exagération, amorti), et la clé d'exagération DÉPASSE la clé du
   coup. Nous avons des clés de position (armé, a5, a3, contact, +3, +6…),
   pas de rôles ; aucune clé ne dépasse le contact de beaucoup.
3. **Il juge chaque clé en la rejouant** (« constantly replay ») et
   l'exagère si elle est « bland » (fade). Critère = l'œil, en boucle.
4. **Le drag assumé** : bras « disloqué » qui traîne derrière le corps.
5. **Tête** : garde la direction de la 1re image (contre-rotation, regard [CONTREDIT 2026-09-26 : vrai pour ce tuto, pas universel : l'uppercut du pack ne la fait pas, la tête suit le lacet, voir corpus/etude_c4/A4_pack_battleground.md §4]
   fixe), accentue au milieu, puis suit le torse.
6. **Pieds** : plantés à leur place de départ (vérifié au fantôme), jambes
   uniquement montées/descendues.
7. **Proportion du temps** : action ≈ 0,17 s, pose tenue vivante ≈ 1 s.
   Chez nous (coup chargé v7) : charge 0,5 s + frappe 0,1 s + hitstop +
   cartes, la pose d'après ne tient que ~0,13 s (f150 → f158) avant l'envol.
8. **Amplitude de la pose finale** : le corps perd ~1/3 de sa hauteur,
   penche de ~40° sur le côté, jambes très écartées. NUANCE avec Milan
   (v1-v2 : « accroupi » rejeté) : ce n'est pas un accroupi PENDANT la
   charge, c'est l'écrasement du corps DANS la pose d'arrivée du coup.

## Ce qui reste incertain

- Pas de son : les explications orales éventuelles manquent.
- Les angles sont estimés sur du 640x360.
- C'est UN tuto, un uppercut, un animateur. Pas une règle de TSB.
