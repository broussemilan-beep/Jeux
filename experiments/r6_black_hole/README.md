# Trou noir — accroupissement, décollage en lévitation, disque d'accrétion (R6, Roblox)

Prototype isolé, sans lien avec RANK ZERO ni MyAnimeRPG ni les autres
prototypes de `experiments/` (voir CLAUDE.md). Réutilise **telle
quelle** l'infrastructure déjà vérifiée de `r6_solar_smite`
(`r6_rig.py`, `anim_engine.py` — y compris le solveur de ressort
analytique exact, `export_kfseq.py`, `export_model.py`,
`resolve_rbxmx.py`, le rig `RigR6.rbxmx`, `vendor/three.min.js`,
`textures/stone_ground.png`/`ruin_wall.png`).

Différence structurelle majeure avec tous les prototypes précédents de
ce dépôt : c'est la première fois qu'un personnage **quitte le sol**
pendant l'animation (lévitation complète, pas un simple saut). Toute la
discipline de vérification existante (placement des pieds "mesuré, pas
deviné") a dû être étendue pour couvrir ce nouveau cas — voir
"Calibration" ci-dessous.

## Demande

Pas une demande textuelle cette fois : une **vraie capture vidéo**
envoyée par l'utilisateur (`ScreenRecording_09-23-2026_15-52-25_1.mov`,
14.16s/60fps/888×1240, titre à l'écran "Black Hole Ability", test en
Roblox Studio d'une compétence de gravité), accompagnée du message :

> Okk maintenant essaye de faire ça exactement mais que ce soit pour les
> VFX l'animation etc revérifie si tu as tout tu peux tout faire les
> bonnes réflexion etc

Instruction explicite de reproduire la vidéo elle-même comme cible
(pas une description écrite à interpréter), avec latitude complète sur
la mise en œuvre ("tu peux tout faire les bonnes réflexions").

## Recherche — analyse frame par frame de la référence

Vidéo extraite en frames via `ffmpeg` (`fps=4`, 57 images) puis
inspectées une à une (Read tool, pas juste un résumé du mouvement) :

- **~0-2s** : personnage R6 en costume, debout normal, bras le long du
  corps, sur un baseplate Roblox Studio par défaut (grille visible).
  Overlay TikTok/short-form ("Abonnements"/"En direct"/"4,7 k
  ❤"/"251 💬"), titre "Black Hole Ability" en incrustation.
- **~3.25s** : accroupissement marqué, torse plié vers l'avant, tête
  quasi au niveau des genoux — caméra délibérément TRÈS basse et
  proche pour dramatiser l'anticipation (pas juste "légèrement plus
  proche").
- **~5-6.25s** : relevement EXPLOSIF — bras écartés à l'horizontale en
  grand (un vrai T-pose latéral façon télékinésie, PAS un lever
  au-dessus de la tête comme `r6_solar_smite`) — le personnage DÉCOLLE
  visiblement du sol. Des fragments du sol/décor sont arrachés et
  flottent déjà autour de lui à cet instant, de petites particules
  scintillantes visibles.
- **~7.5s** : plan large — la caméra s'éloigne, le personnage sort
  quasiment du cadre ; les fragments se sont regroupés en un amas
  compact qui tourne visiblement sur lui-même au-dessus du sol (pas de
  simple ligne droite vers un point, une vraie orbite qui se resserre).
- **~8.75-11.75s** : formation du trou noir — un anneau lumineux
  jaune/or (disque d'accrétion) apparaît au centre de l'amas, cœur
  sphérique PUR NOIR en son centre, fond de scène qui s'assombrit
  fortement (vignette quasi totale — seuls le disque/le cœur et les
  fragments sombres restent lisibles par contraste), traînées blanches
  qui SPIRALENT vers l'anneau (pas un burst radial classique, une
  vraie spirale — angle ET rayon changent tous les deux). C'est le
  segment le plus long de toute la référence.
- **~13.5-14s** : la vidéo coupe au NOIR total — pas de résolution
  filmée (pas de retour au sol visible, pas de fin de l'effet).

Ce dernier point a une conséquence directe sur ce prototype : tout ce
qui suit l'effondrement du trou noir (atterrissage, sortie de pose) est
une **décision de mise en scène assumée de cette session**, pas lue
dans la référence — voir `choreography.py` (docstring de module, point
R6) pour la citation exacte et la justification.

## Chorégraphie

Un seul personnage (`character_track()`, `choreography.py`), pas de
cible/mannequin — la référence elle-même n'en montre aucun. Phases :

1. **Garde** (0 → 0.6s) — debout normal, attente vivante courte (la
   référence ne s'attarde pas dessus).
2. **Accroupissement** (→ ~1.4s) — torse plié à 58°, jambes fléchies,
   tête basse, bras resserrés contre le corps (préparation, coil) ;
   vrai hold au fond (0.3s), pas un simple passage.
3. **Décollage** (~1.77s) — relevement explosif, torse qui s'arque en
   arrière, bras écartés à l'horizontale (`rz`≈±86°, l'axe qui contrôle
   l'écartement latéral sur ce rig — voir la correction de signe
   documentée dans `r6_solar_smite/README.md`).
4. **Lévitation soutenue** (→ ~5.17s, la phase la plus longue) — hover
   vivant (jamais un vol figé) : bras qui oscillent légèrement,
   personnage qui "respire" en l'air, pendant que les fragments
   convergent et que le disque se forme (voir VFX ci-dessous).
5. **Climax** (~5.83s) — pic de tension : bras qui se resserrent, torse
   qui penche vers l'avant/le centre, comme tiré par la gravitation —
   pose OPPOSÉE au relâchement grand-ouvert de la lévitation, pour que
   le pic se LISE comme un pic.
6. **Effondrement + atterrissage** (~6.03s → 6.5s) — dernier à-coup
   gravitationnel, puis DESCENTE (décision assumée, voir ci-dessus) :
   jambes fléchies à l'atterrissage (absorption), puis redressement.
7. **Retour à l'attente** (→ 7.83s) — attente vivante finale, identique
   en forme à la phase 1 (boucle lisible).

### Clearance des pieds — mesurée, pas devinée (piège trouvé et corrigé)

Première tentative : `root_pos.y` fixé à une constante ("3.2 studs, ça a
l'air haut") pour toute la lévitation. Vérification par calcul
(`grounded_root_y_balanced` appliqué à la pose de décollage) : cette
constante correspondait à une clearance RÉELLE des pieds de seulement
**0.18 stud** — le personnage aurait semblé toucher presque le sol,
pas décoller franchement, malgré un chiffre qui "semblait" élevé. Pire
au climax : la constante choisie à l'œil donnait une clearance de
**0.004 stud** (pieds quasiment AU sol) pour une pose censée être
clairement aérienne.

Cause : `root_pos.y` n'est pas directement la hauteur des pieds au-dessus
du sol — elle dépend aussi de l'angle des jambes (une jambe pliée vers
l'avant descend son pied même à `root_pos.y` inchangé).
`grounded_root_y_balanced(pose)` donne déjà, pour une pose donnée, LA
valeur de `root_pos.y` qui poserait les pieds pile sur Y=0 — la vraie
clearance est donc `root_pos.y - grounded_root_y_balanced(pose)`, jamais
`root_pos.y` seul. Corrigé : chaque pose aérienne calcule sa propre
clearance explicite au-dessus de cette valeur de référence
(`RISE_CLEARANCE=2.4`, `CLIMAX_CLEARANCE=1.3`, `RELEASE_CLEARANCE=0.5`,
décroissant vers 0 à l'atterrissage — le personnage "redescend"
progressivement, cohérent avec le récit). Revérifié par calcul :
clearances désormais exactement 2.400 / 1.160 / 0.323 stud aux 3
instants-clés (voir `calibrate.py`).

## VFX — `black_hole_track.py`

Décor procédural indépendant (pas des os du rig), synchronisé sur
`choreography.VFX_EVENTS`/`BLACK_HOLE_CENTER` :

- **16 fragments de sol** — dispersés en anneau irrégulier autour du
  personnage (seed fixe, rayon 2.4-8.0 studs, angle aléatoire — pas un
  pattern régulier). Trajectoire en 3 temps par fragment, échelonnée
  (`stagger` individuel, pas tous synchrones) : immobile au sol →
  lancement vers un point d'orbite (ease-out, "arraché") → orbite en
  spirale (vitesse angulaire ET rayon qui changent, rayon qui rétrécit
  vers `CONSUME_RADIUS` puis le fragment disparaît). Vitesse angulaire
  croissante en approchant le centre (orbite qui se resserre) —
  vocabulaire visuel neuf pour ce dépôt.
- **Disque d'accrétion** — rayon qui grossit (ease-out) pendant
  `disk_form`, plein régime pendant hold/climax avec une légère PULSE
  d'opacité (pas un plateau plat) autour du climax, s'effondre
  (ease-in) pendant `collapse`.
- **Cœur noir** — rayon toujours ≤ celui du disque (vérifié
  numériquement, jamais l'inverse), couleur quasi-noire pure.
- **22 traînées radiales** — spiralent VERS le disque (rayon décroît,
  angle avance), pas un burst classique vers l'extérieur.
- **Vignette** — assombrit le FOND seulement (jusqu'à 0.75 en
  fonctionnement normal, pic bref à 1.0 pendant l'effondrement), jamais
  une opacité plein écran qui cacherait le disque/cœur/personnage —
  principe direct de `experiments/_shared/vfx_craft_checklist.md`
  ("l'échelle communique l'enjeu", jamais un voile qui masque
  l'action).

### Timing VFX — corrigé après un vrai débordement trouvé par `calibrate.py`

Première version : `collapse` durait une constante fixe (0.5s) à partir
de `RELEASE_T`, indépendamment de la durée réelle de la descente vers
`LAND_T` (0.467s dans cette chorégraphie). `calibrate.py` a détecté le
débordement : le VFX finissait 0.033s (1 frame) APRÈS l'atterrissage —
un fragment/le disque seraient restés visibles alors que le personnage
avait déjà les pieds au sol. Corrigé : `collapse["t1"]` est maintenant
borné directement sur `LAND_T` (pas une constante ajoutée à la main),
donc toujours cohérent même si la chorégraphie est retimée plus tard.

## Calibration — 2 modes de vérification du placement des pieds

`calibrate.py` étend la discipline "mesurer, jamais deviner" déjà
établie (voir `r6_solar_smite/README.md`) à un cas qu'aucun prototype
précédent n'avait : un personnage qui quitte réellement le sol.

- **Au sol** (garde, accroupissement, atterrissage, attente finale) :
  réutilise tel quel le modèle à 3 cas de `r6_solar_smite` (calage
  jambe seule / compromis équilibré).
- **Aérien** (`AIRBORNE_WINDOW` = `[RISE_T, LAND_T]`) : vérifie
  qu'AUCUN pied ne traverse le sol (Y < -TOLERANCE) — pas un check de
  contact (aucun contact n'est attendu), juste l'absence de clipping.

Résultat final (voir sortie de `calibrate.py`) : aucune anomalie de
placement au sol non expliquée, aucun clipping pendant la lévitation,
structure rigide/finie partout, VFX numériquement sain (0 position
non-finie, cœur jamais plus grand que le disque, les 16 fragments tous
consommés avant l'atterrissage, timeline VFX/atterrissage cohérente).

## Caméra et lecteur

Voir section "Vérification" pour les captures. Mise en scène calquée
sur les beats de la référence (voir Recherche) : poussée basse/serrée
sur l'accroupissement, recul/remontée au décollage, plan large pendant
que les fragments se regroupent, poussée extrême sur le disque/cœur au
climax, recul progressif au retour au sol.

## Lecteur — délégué, puis corrigé après vérification indépendante

Le lecteur Three.js (`black_hole_viewer.html`, camera, rendu du disque/
cœur/débris/vignette) a été construit par un agent en arrière-plan
(délégation classique pour ce genre de pièce mécanique/large — même
pratique que `r6_rock_kick`). L'agent a rapporté avoir **vérifié
lui-même** ses captures ("00-garde/02-liftoff/07-landing/08-recover :
character clearly legible and well-posed throughout", "05-climax :
extreme close-up, genuine pure-black core silhouette... not a blown-out
white screen, not a flat black screen"). **Ce rapport était faux.**

En ouvrant moi-même les 9 captures produites (jamais un rapport d'agent
pris au mot — discipline établie tout du long de ce dépôt) :
`00-garde` montrait un bloc torse+tête quasi plein cadre (tête même pas
visible), `01-crouch` un plan totalement illisible, et surtout
`05-climax` montrait un DISQUE NOIR PLEIN qui remplissait tout le
cadre — aucun anneau doré visible, aucun cœur distinguable du reste.

Diagnostic (mesuré, pas supposé) : `CAM_KEYS` (distances caméra)
avaient été copiées du "sens" des gros plans de `r6_solar_smite`, où un
gros plan cadre un POING (~1 stud). Ici la caméra doit cadrer soit le
personnage ENTIER (~5 studs), soit le disque d'accrétion à son diamètre
maximal (`DISK_RADIUS_MAX×2` = 9.2 studs) — des objets bien plus gros.
Vérifié numériquement (requête directe de `camera.position`/`fov`/
`projectionMatrix` dans une page Playwright, comparée à la géométrie
réelle des meshes) : la caméra ET la géométrie étaient toutes les deux
correctes, ce n'était PAS un bug de calcul — juste des distances trop
courtes pour ce qu'elles devaient cadrer (ex. `climax_t` : distance 3.2
studs pour un disque de 9.2 studs de diamètre, largement plus grand que
le cadre). Recalculées par la formule `dist = taille / (2 × fraction_
cadre_visée × tan(FOV_BASE/2))` plutôt que choisies à l'œil — ex.
climax : disque 9.2 studs, fraction visée 0.85 → distance 12.5 studs
(au lieu de 3.2). Reconstruit et recapturé : les 9 captures ont
toutes changé, désormais lisibles (voir ci-dessous).

Ce que l'agent avait néanmoins correctement diagnostiqué et corrigé
(les 3 points ci-dessous restent en place, non remis en cause par ce
correctif de distance) : le halo 2D du disque qui lavait le cœur en
olive au lieu du noir pur, l'éclairage insuffisant du personnage, et
`tw` qui décrochait du disque pendant l'effondrement.

## Vérification (captures)

9 captures committées dans `captures/verification/`, toutes vérifiées
par moi-même en ouvrant chaque image (jamais un rapport d'agent pris au
mot, voir section ci-dessus) :

- `2026-09-23-black-hole-00-garde.png` — attente vivante, personnage
  centré, mur en arrière-plan.
- `2026-09-23-black-hole-01-crouch.png` — accroupissement, caméra basse
  et proche (dramatisation), torse penché nettement visible.
- `2026-09-23-black-hole-02-liftoff.png` — décollage, bras qui
  commencent à s'écarter, séparation tête/torse visible.
- `2026-09-23-black-hole-03-hold-debris.png` — lévitation soutenue,
  bras écartés, une dizaine de fragments de sol clairement visibles en
  train de flotter/tournoyer autour du personnage.
- `2026-09-23-black-hole-04-disk-forming.png` — disque en formation :
  halo doré grandissant, cœur noir déjà visible en son centre, débris
  et traînées convergeant, mur/vignette cohérents.
- `2026-09-23-black-hole-05-climax.png` — plan extrême sur le disque :
  cœur sphérique noir net, anneau doré autour, traînées blanches en
  spirale, vignette qui assombrit le fond — le plus proche du langage
  visuel de la référence.
- `2026-09-23-black-hole-06-collapse.png` — effondrement, disque encore
  large mais net (cœur + anneau + traînées bien lisibles).
- `2026-09-23-black-hole-07-landing.png` — atterrissage, pose
  d'absorption de l'impact, vignette déjà retombée (retour à la scène
  normale).
- `2026-09-23-black-hole-08-recover.png` — retour à une attente
  vivante, boucle bouclée.

Publié : https://claude.ai/artifact/RN3Xb145T8ptNBHxSvQQRT
