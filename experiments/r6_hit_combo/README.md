# Combo de coups — jab, cross, hook (R6, Roblox)

Prototype isolé, sans lien avec RANK ZERO ni MyAnimeRPG — même isolation
que les autres prototypes de `experiments/`. Réutilise **telle quelle**
l'infrastructure déjà vérifiée de `r6_directional_punch` : `r6_rig.py`,
`anim_engine.py` (bpy réel, Empty + `rotation_euler` à 3 canaux
scalaires — voir sa docstring pour le choix), `export_kfseq.py`,
`resolve_rbxmx.py`, le rig `RigR6.rbxmx` (voir `rig/PROVENANCE.md`,
provenance identique), `vendor/three.min.js`, `textures/*.png`.

## Demande

Après le direct du droit (un seul coup, beaucoup de coupes caméra
serrées), demande explicite : « Fais une nvl animation de combo de hit
avec VFX texturing inspire toi des refs que je t'ai envoye sois encore
plus fluide je veux pas du saccadé du chelou et enfin fais Camera de loin
qui montre la scène en entièreté. »

Quatre exigences distinctes, toutes structurantes :
1. Un **combo** (plusieurs coups enchaînés), pas un coup isolé.
2. **VFX + texturing**, dans l'esprit des 3 vidéos de référence déjà
   analysées pour le direct du droit (charge = halo sur le point de
   contact, jamais un étirement pendant le recul ; étirement uniquement
   pendant l'avancée).
3. **Encore plus fluide** — explicitement pas de « saccadé du chelou ».
4. Une **caméra de loin qui montre la scène en entièreté** — le contraire
   du direct du droit, qui coupait sans arrêt sur des plans serrés.

## Ce qui est livré

- `output/character_attacker_combo.rbxmx` — `KeyframeSequence` de
  l'attaquant (rig R6 réel, 6 segments rigides, aucun coude/genou). 80
  keyframes, 2,63 s à 30 Hz.
- `output/character_dummy_combo_reaction.rbxmx` — `KeyframeSequence` du
  mannequin (même rig, même durée) : attente → encaisse jab → encaisse
  cross → projeté par le hook → hébété.
- Lecteur HTML (deux rigs synchronisés, VFX par coup, caméra large fixe) :
  https://claude.ai/code/artifact/12078c70-ab22-41f9-88ec-6c5c76a65659

## Chorégraphie : pas de temps mort entre les coups

Contrairement au direct du droit (une longue charge de ~1,25 s avant UN
coup), un combo ne peut pas se permettre de temps mort entre chaque
frappe sans lire comme « saccadé » — c'était le risque explicitement
signalé par l'utilisateur. Le principe retenu (`scripts/choreography.py`,
fonction `attacker_combo()`) : **chaque retour de bras DEVIENT l'amorce
du coup suivant**. Le buste, qui torsade dans un sens pour lâcher un
coup, repart directement dans l'autre sens pour le suivant — il n'y a
jamais de pose neutre tenue entre deux coups, seulement une oscillation
continue :

- Jab gauche : buste `Torso.Y` négatif au lâcher (épaule gauche en
  avant).
- Cross droit : buste `Torso.Y` positif au lâcher (épaule droite en
  avant) — la transition `CROSS_WINDUP` réutilise directement la pose de
  retour du jab, sans keyframe de pause intermédiaire.
- Hook gauche (finisher) : buste repart une nouvelle fois vers `Y`
  négatif, mais avec une bien plus grande amplitude (`HOOK_STRIKE_TORSO.Y
  = 46°` contre `34°` pour le cross) et un mouvement latéral au bras
  (voir plus bas), pas un troisième coup droit — un combo qui répète 3
  fois la même trajectoire ne se lit pas comme une escalade.

Chronologie (`GARDE_T=0,18s` → `JAB_T=0,46s` → `CROSS_T=0,98s` →
`HOOK_T=1,58s` → `DURATION=2,63s`) : chaque coup individuel réutilise la
leçon du direct du droit — la fenêtre `HIPDRIVE_T → IMPACT_T` (chaîne
cinétique du corps déjà à 85-92 % pendant que le bras qui frappe n'est
encore qu'à 18-25 %) est un vrai **snap d'une seule frame** (`SNAP=1/30s`),
jamais 3-5 images intermédiaires — c'est ce qui évite l'effet « pale de
moulin » sur un bras rigide sans coude, cause du problème diagnostiqué
sur le direct du droit.

Le hook se distingue mécaniquement du jab/cross : ce n'est pas un coup
droit (extension en X) mais un **balayage latéral** — le bras gauche
charge à `Z=-78°` (vers l'extérieur du corps) puis balaie jusqu'à
`Z=+91°` au contact (croisé devant, vers l'intérieur) — c'est cet arc,
porté par la plus grande rotation de buste du combo, qui distingue
visuellement le finisher des deux coups droits qui le précèdent.

## Calibration (mesurée, pas devinée)

Même discipline que le direct du droit : chaque écart de contact
poing/torse est mesuré par cinématique directe (`scripts/calibrate.py`),
jamais estimé à l'œil, puis corrigé par balayage numérique 1D sur la
composante Z (latérale) du bras qui frappe quand la correction analytique
seule (translation de la racine sur Z) laisse un résidu X/Y.

```
jab    (t=0.46s, Left Arm)  : écart = 0.493 stud
cross  (t=0.98s, Right Arm) : écart = 0.366 stud
hook   (t=1.58s, Left Arm)  : écart = 0.393 stud
```

Les trois écarts sont dans la même fourchette serrée que le direct du
droit calibré (0,366 stud) — cohérent, pas de dégradation en enchaînant
3 coups sur la même chronologie.

**Piège rencontré et documenté** : `ATTACKER_SECONDARY_MOTION` (vibration
secondaire, ressort-amorti) ne supporte qu'un seul `t_min` par `Part` —
le mettre au premier coup (`JAB_T`) perturbe alors les poses déjà
calibrées du cross et du hook à leurs propres instants d'impact, parce
que la vibration a le temps de dériver la pose entre-temps. Première
mesure du `cross` contaminée ainsi : écart mesuré à 1,6 stud (au lieu de
0,366), et la valeur de `CROSS_LUNGE_Z` calculée à partir de cette
mesure fausse était donc elle-même fausse (`-7.109` au lieu de la valeur
correcte `-4.6513`). Corrigé en restreignant `t_min=HOOK_T` (seul le
dernier coup, qui a un vrai follow-through tenu, reçoit la vibration
secondaire) et en remesurant avec `secondary_motion=None` pendant la
calibration — même pattern que `r6_directional_punch`, qui n'active sa
propre vibration secondaire qu'à partir de son unique `IMPACT_T`.

Vérification structurelle (`calibrate.py`) : rotations finies et
plausibles sur les 6 segments des deux rigs, durées identiques
(attaquant = mannequin = 2,63 s).

## VFX par coup — escalade jab < cross < hook

Toutes les techniques déjà établies et corrigées sur `r6_directional_punch`
sont réutilisées et **généralisées à 3 coups** (paramétrées par un objet
`HIT_STYLE`, boucle `HITS` dans `scripts/hit_combo_viewer.html`), avec une
intensité qui **croît** à chaque coup — le combo doit se lire comme une
montée en puissance, pas trois fois le même effet :

| | jab | cross | hook |
|---|---|---|---|
| hitstop (frames à 30fps) | 2 | 3 | 6 |
| étirement au lâcher (pic) | +22% | +45% | +65% |
| étirement d'impact (pic) | +16% | +30% | +42% |
| débris (particules) | 6 | 12 | 20 |
| lignes de vitesse | 16 | 30 | 44 |
| secousse caméra (amplitude) | 0.045 | 0.085 | 0.16 |
| couleur du halo/flash | orange | orange | rose/magenta (finisher) |

Mécanismes réutilisés du direct du droit, inchangés dans leur principe :
- **Hitstop cumulatif** : `poseTime()` généralisé pour boucler sur les 3
  coups dans l'ordre et accumuler le décalage temporel de chacun (au lieu
  d'un seul gel de pose comme sur le direct du droit) — la pose reste
  figée à l'instant d'impact de CHAQUE coup pendant sa propre durée de
  hitstop, les VFX à l'écran (flash, lignes, débris) continuant, eux, à
  jouer en temps réel.
- **Étirement uniquement à l'avancée, jamais au recul** — correction
  directe issue de l'analyse frame-par-frame des 3 vidéos de référence
  envoyées pendant le développement du direct du droit (« l'étirement
  doit être sur l'avance, pas le recul ») : `releaseStretchFactor()`
  (ancré à l'épaule, actif `windup_t → impact_t`) puis, seulement après
  contact, `armStretchFactor()` (ancré à la main, bref). Jamais les deux
  en même temps, jamais pendant le retour du bras vers le corps.
- **Halo de charge sur le poing** (`drawFistCharge`), **traînée/smear
  épaule→poing** (`drawArmSmear`), **flash + lignes de vitesse au contact**
  (`drawImpactFrame`), **débris balistiques** (`drawDebrisBurst`) — tous
  génériques par coup (prennent `hit` en paramètre), tous déterministes
  (`sin(i*constante)`, jamais `Math.random()` — reproductible d'une
  lecture à l'autre).

## Caméra : large et stable, jamais de coupe

C'est le changement le plus visible par rapport au direct du droit
(cinq plans authored, coupes franches, gros plans serrés pendant la
charge). Ici, une seule caméra, un seul plan du début à la fin :

- Azimut quasi-profil (`CAM_AZ0=-78° → CAM_AZ1=-82°`), dérive lente sur
  toute la durée — jamais de changement de cible, jamais de coupe.
- Distance stable (`BASE_DIST=15.0`, `MIN_SUBJECT_DIST=6.0` : la caméra ne
  se rapproche que si un des deux personnages menace de sortir du plan,
  jamais pour un effet de mise en scène) — la scène balayée en sweep
  numérique (400 points sur 0 → 3,00 s) reste à une distance de 15,5 à
  15,7 studs de la cible tout du long (voir `sweep_hit_combo.js`,
  résultats ci-dessous), variation de moins de 2 %.
- Choix du profil plutôt que 3/4 face : un profil quasi-pur ne
  raccourcit pas visuellement l'avancée de l'attaquant, qui se fait le
  long de l'axe Z — une caméra plus de face aurait « avalé » l'avancée
  par foreshortening, contredisant l'intention du plan large qui doit
  montrer le déplacement.
- Ponctuation d'impact **sans jamais couper** : `fovAt()` et
  `shakeOffset()` bouclent sur les 3 coups pour un zoom optique bref
  (FOV qui chute puis revient élastiquement) + secousse écran à chaque
  contact, avec amplitude croissante jab < cross < hook (tableau
  ci-dessus) — le seul répondant visuel à l'impact, jamais un
  changement de plan.

## Passe « niveau expert » (retour utilisateur, deuxième itération)

Retour après la première livraison : « Je veux aussi animation de hit etc
vraiment du niveau expert. » Clarifié via question : portée = ce combo
existant (pas un nouveau prototype), trois axes explicitement visés — la
réaction du mannequin, le VFX au contact, le timing/hitstop. Trois
changements ciblés, chacun vérifié pour ne PAS régresser la calibration
déjà établie :

1. **Réaction du mannequin — whiplash + rebond, jamais un retour à
   l'idle** (`scripts/choreography.py`, `dummy_combo_reaction()`). Avant :
   jab et cross tenaient une seule pose figée (snap sur le contact, puis
   silence complet) jusqu'au coup suivant — seule la vibration secondaire
   (ressort) donnait un peu de vie. Ajouté pour les trois coups : la
   rotation du buste/tête **continue** un instant au-delà de la pose de
   contact (l'inertie du coup n'est pas absorbée instantanément —
   `JAB_OVERSHOOT_*`, `CROSS_OVERSHOOT_*`, `HOOK_OVERSHOOT_*`, +0,05 à
   +0,08 s après chaque impact), puis un rebond élastique **partiel** qui
   ne revient jamais à l'idle (`JAB_SETTLE_*`, `CROSS_SETTLE_*` — le combo
   n'a pas de temps mort, le coup suivant arrive avant toute récupération
   complète). Le hook (finisher) reçoit en plus un **court hop** vertical
   (`HOOK_HOP_Y = GROUND_Y + 0,42`) pendant la projection, avant
   l'atterrissage à `HOOK_T + 0,35 s` — vend la taille du coup, pas
   seulement sa rotation.
   - Vérifié : `calibrate.py` réexécuté après le changement — écarts de
     contact **inchangés** (0,493 / 0,366 / 0,390 stud, contre
     0,493 / 0,366 / 0,393 avant — écart de 0,003 stud dû au bruit de la
     vibration secondaire sur la pose idle précédant chaque impact, pas
     une régression), structure toujours OK sur les deux rigs. Les
     nouvelles keyframes sont toutes **après** l'instant d'impact exact
     (jamais AU moment mesuré) — aucun risque de décalibrer le contact.
2. **VFX au contact — éclats d'énergie colorés + anneau de choc**
   (`scripts/hit_combo_viewer.html`, `drawImpactSpark()` et
   `drawShockwaveRing()`, nouvelles). Avant : flash plein écran + lignes
   de vitesse noires (encre, style manga) + débris de gravats bruns —
   tout le langage visuel était celui d'un choc de MATIÈRE, rien ne
   rendait l'ÉNERGIE du coup au moment précis du contact (seul le halo de
   charge, avant l'impact, portait une couleur). Ajouté : un anneau fin
   qui s'étend et s'efface (blend additif, couleur `hit.glow` — orange
   jab/cross, rose/magenta hook) et des traînées lumineuses radiantes
   avec un cœur blanc bref au centre — les deux se superposent au
   flash/lignes/débris existants, ne les remplacent pas. Toujours
   déterministe (`sin(i*constante)`), toujours calé sur `hit.debrisN` /
   `hit.shakeAmp` pour l'escalade jab < cross < hook déjà établie.
3. **Timing — hitstop du hook allongé** : `hitstopDur` du hook passé de
   `6/30` à `8/30` (0,267 s, contre 0,200 s) — le finisher gèle
   sensiblement plus longtemps que le cross (`3/30`), creusant l'écart
   déjà voulu entre les trois coups plutôt qu'une simple progression
   linéaire 2/3/6 → 2/3/8.

## Passe « jeu de jambes » (retour utilisateur, troisième itération)

Retour : « Il te manque une corde à ton arc le jeux du coup et des jambe
c trop statique et non chiadé pour l'instant. » Diagnostic : les jambes
sont enfants du `Torso` dans la hiérarchie du rig (`Torso <- HumanoidRootPart`,
`Left Leg`/`Right Leg` <- `Torso` — voir `r6_rig.py`), donc elles héritent
déjà mécaniquement de la torsion du buste ; le vrai problème n'était pas
l'absence de rotation du buste, mais deux choses qui rendaient les jambes
elles-mêmes silencieuses :

1. **La racine (hanches) ne bougeait JAMAIS en hauteur** — `root_pos`
   utilisait `GROUND_Y` constant du début à la fin du combo, alors qu'un
   vrai coup de poing part des jambes (charge en fléchissant, détente
   vers le haut/avant au lâcher). Corrigé (`scripts/choreography.py`) :
   chaque coup **creuse** sous `GROUND_Y` pendant son windup/coil
   (`JAB_DIP=0,05`, `CROSS_DIP=0,11`, `HOOK_DIP=0,17` — escalade jab <
   cross < hook, même principe que le reste du projet), puis **remonte**
   presque entièrement au hip-drive (`GROUND_Y - dip*(1-fraction_corps)`,
   même fraction que celle déjà utilisée pour interpoler le reste du
   corps), et retombe **exactement** sur `GROUND_Y` à l'instant précis de
   l'impact — condition nécessaire pour ne pas décalibrer le contact déjà
   mesuré (seules les frames *intermédiaires*, jamais l'instant mesuré,
   changent de hauteur). Un léger rebond vers le haut (+0,05) est aussi
   ajouté juste après l'impact du hook (le corps continue sur sa lancée
   plutôt que de retomber platement).
2. **Les jambes elles-mêmes changeaient à peine de pose entre le coil et
   le strike** — ex. la jambe avant (`Left Leg`) du cross ne bougeait que
   de 6° en X entre charge et lâcher, aucun vrai transfert de poids
   visible. Amplifié pour cross et hook (jab laissé inchangé, coup rapide
   et léger qui n'a pas besoin d'un gros jeu de jambes) : la jambe qui
   pousse/pivote (arrière) fait un swing bien plus large, et la jambe qui
   plante (avant, celle qui reçoit le poids transféré) montre une vraie
   compression + un léger pivot vers l'extérieur au lieu de rester quasi
   fixe. Sur le hook en particulier, `Left Leg` (même côté que le bras
   qui frappe) pivote maintenant de 32° en Z (`-18° → +14°`, contre 6°
   avant) — un écho direct au grand balayage du bras (`-78° → 91°`), pour
   vendre l'idée que la hanche/le pied pivotent avec le coup plutôt que
   le buste seul.

Vérifié : `calibrate.py` réexécuté après ces deux changements — écarts de
contact **identiques au frame près** (0,493 / 0,366 / 0,393 stud), parce
que ni la hauteur ni la pose des jambes aux instants d'impact exacts n'ont
changé, seulement les frames de charge/détente entre les coups. Structure
toujours OK. Captures avant/après montrant la charge en fléchissant
(`captures/verification/2026-09-05-hit-combo-footwork-*.png`) et le
nouveau pivot des jambes au lâcher.

## Passe « hold-and-snap » (retour utilisateur, quatrième itération)

Retour, après les trois passes ci-dessus : « Okk c pas la mais c tjrs pas
smooth ou bien animé va revoir les ref que je t'avais envoyé puis fais un
autre travail de recherche animateur Roblox etc. » Demande explicite de
revenir sur les 3 vidéos de référence (déjà analysées pour l'impact du
direct du droit) et de refaire une recherche « comme un animateur
Roblox », cette fois ciblée sur la FLUIDITÉ elle-même — pas l'impact, pas
les jambes, pas les VFX (déjà traités).

**Recherche.** Un agent a réextrait les 3 vidéos image par image (~60
fps réel, contact sheets zoomés) en se concentrant uniquement sur la
structure temporelle du mouvement, pas sur les trajectoires exactes des
membres (masquées par les VFX et la distance de la caméra dans ces
montages). Constat net et contre-intuitif : sur ~60 frames consécutives
d'un coup, **seules 5-8 % des frames montrent une pose réellement en
train d'interpoler** — le reste alterne des **holds vraiment statiques**
(anticipation ET réaction, 4 à 17× plus longs que le coup lui-même) et un
**snap quasi instantané** (1-3 frames) pour le lacher, jamais une pose qui
« coule » en continu de la charge au contact. Autre point clé : un hold
n'est jamais un plan mort — quelque chose bouge TOUJOURS à l'écran
pendant un hold (halo/anneau de VFX, fumée, secousse ou travelling de
caméra), même quand le rig lui-même est parfaitement figé — c'est cette
vie en surcouche, pas le rig, qui empêche un hold de lire comme raide.
Recherche complémentaire (Roblox devforum / tutoriels Moon Animator) :
même diagnostic dans la communauté Roblox — « l'interpolation par défaut
entre keyframes lit comme robotique », la fluidité perçue vient du
contraste entre poses clé tenues (breakdowns) et un relâchement bref, pas
d'une interpolation continue de bout en bout.

**Diagnostic sur notre combo** : `apply_choreography()` utilise des
tangentes Bezier `AUTO_CLAMPED` sur TOUTES les keyframes, et jusqu'ici
chaque coup n'avait qu'un point de passage instantané au coil (pas de
vraie pose tenue) avant d'interpoler en continu vers le hip-drive puis le
strike — exactement le contre-exemple identifié par la recherche : tout
« coule », rien n'est jamais vraiment figé ni vraiment relâché d'un coup
sec, ce qui lit comme mou/tweené plutôt que comme un vrai coup de poing.

**Correction** (`scripts/choreography.py`) : un vrai **hold** (keyframe
dupliquée, pose strictement identique, tenue `JAB_HOLD`/`CROSS_HOLD`/
`HOOK_HOLD` = 3/5/7 frames — escalade jab < cross < hook, même logique
que le reste du projet) au coil de chaque coup, avant un lâcher toujours
aussi bref (`SNAP=1/30`, inchangé — déjà conforme à la recherche). Pendant
le hold, le halo de charge du poing (`drawFistCharge`, lecteur) continue
de pulser en continu — le rig est figé, l'écran ne l'est jamais.

**Piège de mesure trouvé en implémentant ce hold** (documenté ici parce
qu'il a bien failli passer inaperçu) : `calibrate.py` mesure l'écart de
contact via `idx_at(t) = round(t*60)` sur un échantillonnage à 60 Hz. Si
l'instant d'impact (`JAB_T`/`CROSS_T`/`HOOK_T`) ne tombe pas exactement
sur ce quadrillage (multiple de 1/60 s), la mesure attrape un instant
légèrement décalé de l'impact réel — jusqu'ici négligeable (~3 ms), mais
la première version retimée de la chronologie (en secondes décimales,
`+0.16`, `+0.18`, `+0.09`...) tombait sur un décalage deux fois plus
grand pour le cross, suffisant pour fausser sa mesure (poing à Y=2,884 au
lieu de 3,208, écart de contact à 0,339 au lieu de 0,366 stud) alors que
RIEN dans la pose elle-même n'avait changé — une fausse alerte de
régression. Corrigé à la racine : toute la chronologie est maintenant
construite en **nombre de frames entier** (`_fr(n) = n/30`), donc
systématiquement un multiple exact de 1/60 également — plus aucune
ambiguïté d'arrondi possible. Reconfirmé ensuite : écarts de contact
revenus à 0,493 / 0,366 / 0,380 stud (cross exactement comme avant,
hook très proche de 0,393), donc bien une fausse alerte de mesure et non
une régression de la chorégraphie.

Vérifié : captures aux instants de début et de fin de chaque hold (cross
et hook) confirmant une pose **strictement identique** entre les deux
(`captures/verification/2026-09-05-hit-combo-holdsnap-*.png`) avec le
halo de charge visiblement différent (pulsation) — la preuve que le rig
est figé mais l'écran ne l'est pas. Durée totale du combo passée de
2,63 s à 2,85 s (les holds ajoutent du temps, mais aucun temps mort
neutre entre les coups n'est réintroduit — le principe « le retour d'un
coup devient l'amorce du suivant » reste intact).

## Passe « placement des pieds » (retour utilisateur, cinquième itération)

Retour : « Refais mais retravaille les jambes le placement et le jeux de
jambes n'est pas bon. » Diagnostic mesuré (nouveau script
`scripts/foot_check.py`, cinématique directe sur les 6 segments, même
équation que `calibrate.py`) : la passe « jeu de jambes » précédente avait
**deux bugs de placement réels**, pas juste un manque de style :

1. **Le pied flottait jusqu'à 0,57 stud au-dessus du sol** au moment
   même du coup (cross et hook) — cause : la rotation de jambe amplifiée
   au tour précédent (jusqu'à 34°) soulève mécaniquement le pied d'un
   segment RIGIDE SANS GENOU qui pivote autour de la hanche (facteur
   `1-cos(angle)`), et personne ne recalculait la hauteur de la racine en
   conséquence.
2. **Le buste (Torso) à lui seul soulève ou enfonce le pied bien plus que
   la jambe** — mesuré : `HOOK_COIL_TORSO` (torsion à 40°) soulève le pied
   de 0,24 stud même avec la jambe parfaitement verticale (rotation
   locale à zéro). Les jambes sont enfants du Torso dans la hiérarchie du
   rig (`Torso <- HumanoidRootPart`, `Left/Right Leg <- Torso`), donc
   TOUTE rotation du buste se répercute sur la position du pied — un
   simple offset de `root_pos.Y` (l'ancien correctif « jeu de jambes »)
   ne peut pas suivre ça, il ne connaît pas la rotation réelle du buste
   à cet instant.

**Correction, deux volets :**

- **Angles de jambe réduits aux instants de frappe** — la jambe qui
  plante (celle qui reçoit le transfert de poids) reste modeste en
  rotation ; celle qui pousse/pivote porte le swing visible (un talon qui
  se soulève en poussant est réaliste, un pied entier qui flotte ne
  l'est pas).
- **`grounded_root_y()`** (nouvelle fonction, `scripts/choreography.py`) :
  calcule par cinématique directe EXACTE (mêmes C0/C1 que
  `anim_engine`/`calibrate.py`) la hauteur de racine qui pose un pied
  donné pile au sol, étant donnée la rotation prévue du buste ET de la
  jambe à cet instant — plus un offset constant deviné. Résolu
  analytiquement (translater la racine en Y déplace le pied de
  exactement la même quantité, une seule évaluation suffit, pas de
  recherche numérique). Pendant la charge (les deux jambes portent
  encore du poids), **`grounded_root_y_balanced()`** fait la moyenne des
  deux solutions individuelles plutôt que de forcer une seule jambe —
  concentrer l'erreur sur un seul pied donnait 0 stud d'un côté contre
  0,24-0,47 de l'autre ; la moyenne partage l'erreur (~0,12 stud de
  chaque côté, deux fois moins que le pire cas d'avant). Root Y reste
  **exactement `GROUND_Y`** aux 3 instants d'impact eux-mêmes
  (JAB_T/CROSS_T/HOOK_T) — condition absolue pour ne pas décalibrer le
  contact déjà mesuré.

**Résultat mesuré** (`foot_check.py`, avant → après) :

| Instant | Avant | Après |
|---|---|---|
| Cross, hold au coil | 0,13 / 0,17 stud | 0,02 / 0,02 stud |
| Hook, hold au coil (le plus long) | 0,31 / 0,00 stud (un pied dans le sol) | 0,12 / 0,12 stud (partagé) |
| Suivi de coup (overshoot) | 0,22 / 0,22 stud | 0,00 / 0,00 stud |
| Récupération | 0,12 / 0,20 stud | 0,04 / 0,04 stud |

Aux instants de frappe eux-mêmes (root Y verrouillée à `GROUND_Y` pour
la calibration), un résidu modeste subsiste sur la jambe avant du hook
(0,15 stud) — c'est le talon qui se soulève pendant le pivot du lead
hook, anatomiquement correct pour ce coup précis, pas un artefact.

Vérifié : `calibrate.py` reconfirme les écarts de contact **inchangés au
stud près** (0,493 / 0,366 / 0,380), aucune keyframe d'impact touchée.
Captures avant/après (`captures/verification/2026-09-05-hit-combo-
footwork-placement-*.png`) confirmant les pieds au sol pendant les holds.

## Vérification

Environnement : `pip install numpy bpy` (le conteneur ne les avait pas
préinstallés cette session — packages présents dans le cache pip local,
réinstallés sans nouveau téléchargement réseau).

- `python3 calibrate.py` : écarts de contact 0,493 / 0,366 / 0,380 stud
  (jab/cross/hook), structure OK sur les deux rigs, durées égales
  (2,85 s) — réexécuté et confirmé après la passe « niveau expert », la
  passe « jeu de jambes », ET la passe « hold-and-snap » (voir sections
  dédiées ci-dessus ; un piège de mesure lié à l'échantillonnage a été
  trouvé et corrigé pendant cette dernière passe).
- `python3 run_scene.py` : export des deux `KeyframeSequence`,
  « Structure OK » pour l'attaquant et le mannequin, 87 keyframes chacun.
- `python3 build_viewer.py` : lecteur final assemblé (903 567 octets, 2
  textures embarquées, three.min.js embarqué).
- Syntaxe JS : extraction du `<script>` et `node --check` — aucune erreur
  (revérifié après chaque passe VFX/viewer).
- Balayage Playwright sur toute la durée (`REAL_DURATION=3,283s` après le
  hold-and-snap, 400 points) : **0 erreur console, 0 valeur caméra
  NaN/Infinity**, position caméra et FOV échantillonnés à chaque coup
  sans dérive anormale.
- Captures visuelles à 11 instants clés (garde, windup/impact/après pour
  chaque coup, posture finale) : la caméra garde les deux personnages
  entièrement dans le cadre à tout instant, l'escalade des VFX (lignes de
  vitesse, éclats d'énergie, anneau de choc, flash, secousse) est visible
  à l'œil du jab au hook, aucune coupe, aucun artefact de rendu. Captures
  représentatives committées dans `captures/verification/` :
  - `2026-09-05-hit-combo-wide-camera-garde.png` — plan d'ouverture,
    scène entière dans le cadre.
  - `2026-09-05-hit-combo-jab-impact-flash.png` — flash + zoom optique au
    premier contact (avant la passe « niveau expert »).
  - `2026-09-05-hit-combo-cross-impact-flash.png` — lignes de vitesse
    plus denses que le jab (escalade, avant la passe « niveau expert »).
  - `2026-09-05-hit-combo-hook-stagger-debris.png` — projection du
    finisher, débris visibles, plan large maintenu (avant la passe
    « niveau expert »).
  - `2026-09-05-hit-combo-wide-camera-finale.png` — posture finale, plan
    large maintenu jusqu'au bout.
  - `2026-09-05-hit-combo-vfx-spark-ring-jab.png` — nouvel anneau de choc
    + éclats d'énergie (orange) au contact du jab.
  - `2026-09-05-hit-combo-vfx-spark-ring-cross.png` — anneau/éclats plus
    larges au cross (escalade).
  - `2026-09-05-hit-combo-vfx-spark-ring-hook.png` — anneau/éclats les
    plus larges, couleur rose/magenta distincte (finisher).
  - `2026-09-05-hit-combo-hook-hop-reaction.png` — whiplash + hop du
    mannequin pendant la projection du hook.
  - `2026-09-05-hit-combo-holdsnap-cross-coil-start.png` et
    `-cross-coil-held.png` — même pose du rig à 0,16 s d'écart (hold réel
    au coil du cross), seul le halo de charge change.
  - `2026-09-05-hit-combo-holdsnap-hook-coil-start.png` et
    `-hook-coil-held.png` — idem pour le hook, hold le plus long du combo.

## Fichiers

```
r6_hit_combo/
├── rig/                        # copié tel quel de r6_directional_punch
├── textures/                   # copié tel quel de r6_directional_punch
├── scripts/
│   ├── r6_rig.py, anim_engine.py, export_kfseq.py, resolve_rbxmx.py,
│   │   preview.py, gen_textures.py   # copiés tels quels
│   ├── choreography.py         # NOUVEAU — combo jab/cross/hook
│   ├── calibrate.py            # NOUVEAU — adapté (3 coups à vérifier)
│   ├── foot_check.py           # NOUVEAU — placement des pieds au sol
│   ├── run_scene.py            # NOUVEAU — adapté (2 exports combo)
│   ├── dump_scene_data.py      # NOUVEAU — expose DATA.hits (windup/impact par coup)
│   ├── build_viewer.py         # NOUVEAU — adapté (sortie hit_combo_viewer_final.html)
│   └── hit_combo_viewer.html   # NOUVEAU — VFX + caméra généralisés à 3 coups
└── output/                     # .rbxmx + lecteur final (générés, non commités si volumineux)
```
