# Relecture de toutes les refs de Milan, sous l'angle ANIMATION (2026-09-25)

Demande de Milan (2026-09-25 08:27) : « va revoir toute les gif et vidéo de
référence en terme d’animation etc pour re apprendre ».

## Méthode

- **Corpus.** 26 vidéos et GIF uniques, dédoublonnées par empreinte, sur les
  70 fichiers envoyés. MyAnimeRPG 007 et 008 (Black Flash, Rewind Clock)
  recoupent des captures déjà vues. Les images fixes (Deku, poing géant)
  ont été traitées dans l'essai obari.
- **Outil nouveau : `outils/planche_ref.py`.**
  - Images à cadence fixe : la cadence native pour les GIF (souvent
    16,7 i/s), 30 i/s pour les vidéos.
  - Énergie du mouvement image par image.
  - Détection des TENUES (≥ 100 ms quasi immobiles) et des pics.
  - Une planche par ref, avec la courbe d'énergie.
  - Limite : une caméra qui bouge compte comme du mouvement. Une pose
    tenue sous une caméra mobile n'est donc pas détectée ; l'œil corrige.
- **Ordre de travail** (retour de Milan sur mes études biaisées) :
  1. j'ai regardé les 26 planches et zoomé sur les moments utiles ;
  2. j'ai écrit mes notes à froid ;
  3. j'ai relu ensuite seulement `ETUDE_VISUELLE.md` (24/09) pour comparer.
- **Les planches** (images d'œuvres) restent en local, comme en 09-24.
  Seul ce qu'on en tire est versionné.

## Notes clip par clip (animation d'abord, effets ensuite)

| ref | ce que fait le corps et le temps |
|---|---|
| 37d7971a (projection, 2 rigs, éditeur) | 2 s de flux continu, sans tenue (contraste 1,4) : une projection est un flux, pas du pose-à-pose. Puis UNE tenue de 0,8 s sur le résultat (victime à plat, attaquant debout). |
| 48244687 (= **Serious Punch TSB**, Saitama, LE coup de ref ; non reconnu le jour de la relecture, voir `CATALOGUE_REFS.md`) | Cape en très gros plan devant l'objectif = transition. **Tenue 0,42 s debout avant le saut**. Saut vu d'en bas, atterrissage accroupi, frappe au sol. ~3 s de pose d'après, quasi fixe. |
| 772ee6b0 (= **Serious Punch 2**, coup type Serious Punch ; non reconnu non plus) | Même grammaire : tenue 0,48 s, saut, atterrissage très accroupi manteau ouvert, frappe au sol, 4 cartes (dessin, radial, X, blanc), pose finale accroupie tenue ~1 s. |
| 01f4b1d2 (Black Hole) | Immobile 1,07 s en plan large. Compression serrée (caméra collée), extension en V vue d'en bas, T flottant, **2e compression** avant l'explosion : compression/extension répétée, en escalade. |
| 946bd286 (coup vers le ciel) | Le corps n'occupe que ~2 s sur 10. Contre-plongée, bras contre le ciel, **tenue 0,54 s juste avant les cartes**. Puis 5 s de débris au ralenti, victime minuscule. |
| a0341700 (rafale gatling, caméra DE DOS) | 3,5 s de rafale : le corps bouge peu, les bras deviennent des **multiples + traînées blanches tout autour de la silhouette** (à gauche, à droite, au-dessus), donc HORS du tronc même de dos. Tenue 0,17 s avant, 0,83 s après. |
| 12e7dae5 (Black Flash) | Plan large, perso minuscule, 0,1 s d'arrêt, coupe sur très gros plan et cartes. Puis **~1,5 s de ralenti sur la victime** : la réaction est la vitrine. |
| 3ae71567 (Rewind Clock) | Après l'explosion, carte « graphique » tenue 0,6 s : attaquant en silhouette noire, poing dans le visage, sur fond blanc. Puis radios du crâne. |
| 4fb4f776 (Stagnant Rage) | Variante lointaine : **immobile 1,53 s** en caméra de jeu, puis élan et explosion. |
| aafdc91d (caméra de jeu, loin) | Action courte, **pause 0,3 s** [CONTREDIT 2026-09-26 : pause de 0,45 s, voir corpus/etude_c4/C3_gifs.md §5], action plus grosse, tenue 1,9 s : escalade en deux temps avec un silence entre les deux. |
| 58322fc4 (boxeur) | **Pose tenue en déplacement** : 1 s avec la MÊME silhouette (très bas, torse ~45°, gants au visage) pendant que le corps avance. La vitesse se lit par les lignes et la caméra qui suit, pas par les membres. Uppercut en ~2 images, flash. Esquive : il apparaît tout autour de la cible, toujours bas. |
| f1b5bd4b (pro/noob, coup de poing Blender) | Pro : armé 0,93 s, torse DOS à la caméra (« BACK »), poing armé haut ; frappe « FRONT », ~180°. Noob : droit, bras tendu. |
| 9e47148b (pro/noob, Moon) | Même chose. Tenues pro de 0,1-0,5 s à chaque pose ; la cible plie vers l'attaquant, tenue 0,53 s. |
| 99a73bd5 (pro/noob, épée) | **Mesuré : pro 19 % du temps en tenues (7, médiane 0,2 s), noob 0 %.** Le contraste de vitesse à l'écran est le MÊME (p90/p50 3,5 contre 3,7). Ce qui sépare le pro, ce sont les tenues, pas la vitesse. |
| fa7b867c (combo Moon, étiquettes) | 3 attaques en 2,5 s, chacune avec un armé où l'on voit le DOS (rotation ~180°), puis une frappe au sol, le torse plié ~90°. Idle tenu avant et après. |
| 8556a37c (cross punch) | Boucle d'alternances, garde basse. **L'extension est tenue 0,13-0,2 s à chaque coup**, smear en éventail derrière le poing. |
| 6a0095ed (punch practice) | Pose à pose avec micro-tenues de 0,13-0,3 s. La vue de DESSUS montre la rotation du torse. Version « avec adornments » = même anim + points orange. |
| afaa00eb (tuto dessiné firytwig) | Lu en pleine résolution, voir l'encadré ci-dessous. |
| 4e337114 (mannequin, coup chargé) | Armé ~1 s, frappe rapide, **extension tenue et prolongée ~2 s** (fente basse, torse presque horizontal) [CONTREDIT 2026-09-26 : torse plutôt droit ; le trait violet est un élément du visualiseur, pas la trajectoire du coup, voir corpus/etude_c4/C3_gifs.md §7], puis retour lent. Suite longue, comme chez Sakurai. |
| eba5ed69 (IMPACT HAVEN) | Déjà étudié. En plus : grandes fentes basses, corps retournés en l'air, poses tenues 0,1-0,27 s. |
| df406483 (First time fighting a dummy) | Après l'action, **~4 s de gros plan sur l'attitude** du perso (respiration, cheveux), en poussée lente. Le paiement est le personnage, pas le coup. |
| 85e1a98f (Linear easing test) | La même anim aérienne montrée trois fois : sans caméra, sans effets et ralentie. Démontre ce que caméra et effets ajoutent. Perso trop petit pour étudier les poses. |
| 6d3be6e1, 3ee5a405, 449345ad | Flux continus (saisie, garde qui alterne, combo avec effets) : rien de neuf côté corps. |
| 73cc1fb0 (vidéo Gemini) | Déjà étudié (poussée, visage, impact inversé, soleil). Vidéo IA, cohérence non fiable. |

### Le tuto dessiné firytwig (afaa00eb), texte lu en pleine résolution

- **Espacement de l'armé à l'attaque :**
  - ✓ aucun intervalle ;
  - ✗ un intervalle au milieu ;
  - « Keep the inbetweens close to the chamber ».
- « Don't ease out towards the main pose, you can ease out from the
  overshoot to the main pose though ».
- « Keep it as snappy as possible – Minimize frames in between – **Do not
  ease out** – Hold or overshoot the attacking limb – Put the whole body
  into the attack – especially the hips ».
- « Even 1 frame of chamber matters ».
- « Every action has an equal and opposite reaction » (le frappeur recule
  contre le sac).
- « **You can skip the point of contact** » (le sac est déjà parti). C'est
  exactement Babbitt, dans Williams.
- Poses :
  - lunge punch : de l'armé en garde large à une attaque où le corps forme
    une seule diagonale, du pied arrière au poing (notre « ligne jetée ») ;
  - recovery : penché, bras revenu.

## Comparaison avec l'étude du 24/09 (relue APRÈS les notes)

**Déjà là le 24, et retrouvé à froid : ça confirme sans prouver.**
- rafale en masse de poings-smears (lot 3) ;
- rotation BACK -> FRONT ;
- structure en actes des ultimes ;
- tenue sur la conséquence ;
- règles firytwig (lot 2).

**Vraiment nouveau aujourd'hui (angle animation) :**
1. **Tenues mesurées, pro contre noob** : 19 % contre 0 %, à contraste de
   vitesse égal. Le 24, c'était une impression.
2. **Pose tenue en déplacement** (boxeur) : la vitesse se lit par le décor
   et la caméra, pas par les membres qui s'agitent.
3. **Silence entre deux actions qui montent en puissance** (0,3 s), et
   **tenue avant le départ** (0,42-0,48 s avant un saut, 1,53 s avant un
   élan).
4. **Suite prolongée** : extension tenue ~2 s (mannequin), attitude tenue
   ~4 s (dummy).
5. **La rafale de dos se lit par des formes HORS de la silhouette.** Ça
   relie le « gatling » du 24 à la mesure du jour : de dos, le bras qui
   frappe est caché par le torse chez tout le monde, TSB compris (CARNET
   §1.2). La lecture passe donc par ce qui dépasse : multiples, traînées,
   éclats autour.

**Où l'étude du 24 était incomplète.** Elle concluait : « le rythme du
poing est déjà au niveau des M1 pro (armement -> contact en 5-10 f) ».
- Vrai pour les DURÉES.
- La mesure du jour porte sur la VITESSE RELATIVE ré-armement / frappe :
  0,55-1,49 chez nous, 2,3-3,7 chez TSB, même avec les M1 enchaînés.
- Firytwig dit exactement ça : « keep the inbetweens close to the
  chamber, do not ease out ».
- Le 24, j'avais lu la règle mais mesuré autre chose.

**Où je me suis trompé hier soir.**
- J'avais écrit « torsion deux fois moins que TSB ». C'était une rotation
  NETTE comparée à une nette.
- En amplitude, on est au niveau (53-116° contre 77-111°), comme le 24
  l'avait mesuré (98-137°).
- Corrigé dans `CARNET.md` §2.1b, dans la lecture critique Gemini et dans
  `RETOURS.md`.

**Nuance sur les tenues.** Les M1 de TSB n'ont PAS de tenue dans le clip
(0 % en rendu fixe, comme notre rafale). Leurs arrêts viennent du moteur :
hitstop, fin de clip, enchaînement. Les tutos Moon cuisent leurs tenues dans
l'anim parce qu'ils montrent un clip seul. Pour nous, les tenues de la rafale
viennent du hitstop du module, comme chez TSB. **Pas un manque.**

## Ce que ça change (apprentissages, pas règles)

Reportés dans `CARNET.md` : §2.1 (renforcé par firytwig), §2.1b (corrigé),
§2.5b, §2.6b, §3.6 et §5.
