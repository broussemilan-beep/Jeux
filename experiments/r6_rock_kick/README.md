# Coup de pied de roche — projectile de destruction (R6, Roblox)

Prototype isolé, sans lien avec RANK ZERO ni MyAnimeRPG ni les autres
prototypes de `experiments/` (voir CLAUDE.md). Réutilise **telle
quelle** l'infrastructure déjà vérifiée de `r6_hit_combo` (`r6_rig.py`,
`anim_engine.py`, `export_kfseq.py`, `resolve_rbxmx.py`, le rig
`RigR6.rbxmx`, `vendor/three.min.js`, textures `stone_ground.png`/
`ruin_wall.png`) et le principe de trajectoire scriptée de
`r6_divine_orb/scripts/orb_track.py` (`rock_track.py` en est la
variante "projectile lancé par un coup de pied, redirigé par une
frappe de suivi" plutôt que "boule invoquée puis lancée à la main").

## Demande

Nouvelle tentative demandée après plusieurs passes infructueuses sur
`r6_battle_throne` (« Bin c tjrs pas ça tu as du mal à rendre ça bien et
fluide ») — identité et spec complète fournies par l'utilisateur :

> Identité : le personnage donne un coup de pied à une énorme roche,
> puis exploite la roche comme projectile de destruction.
>
> Phase 1 : apparition/présence de la roche. Phase 2 : prise d'appui et
> coup de pied circulaire très large. Phase 3 : la roche est propulsée.
> Phase 4 : le personnage enchaîne avec une frappe de la roche/sur la
> roche vers la cible. Le corps doit exagérer la rotation du bassin et
> du torse pour compenser les limites R6.
>
> Gameplay : la roche a sa propre trajectoire et collision, peut
> toucher plusieurs adversaires, reste fonctionnelle sans cible (impact
> environnemental).
>
> VFX : poussière au spawn, burst + trail au coup de pied, particules
> de vitesse en vol, explosion + débris + onde + flash à l'impact.
>
> Caméra : basse/trois-quarts pendant le kick, transition vers le
> projectile, zoom court à l'impact.

### Correction : la roche ne préexiste pas, elle sort du sol

Premier essai livré : une roche déjà posée au sol, à distance, que le
coup de pied circulaire allait chercher. Retour utilisateur : « c pas
tout a fait ça en gros le perso tape le sol avec sa jambe droit est
fais ressortir une roche du sol » — la « Phase 1 : apparition » n'est
pas un décor préexistant, c'est la CONSÉQUENCE d'un stomp (un
enfoncement vertical de la jambe droite dans le sol), pas quelque chose
qui attend d'être atteint par le coup de pied.

Reconstruit en conséquence (voir `scripts/choreography.py` et
`scripts/rock_track.py`) : une phase STOMP précède maintenant le coup de
pied circulaire — la jambe droite s'écrase verticalement dans le sol,
et c'est le point d'impact MESURÉ de ce stomp (`STOMP_POINT`, cinématique
directe sur le pied, jamais choisi à l'œil) qui devient l'endroit exact
où la roche jaillit. Le coup de pied circulaire (Phase 2 d'origine)
reste ensuite ce qui propulse cette roche fraîchement sortie — la
demande initiale n'était pas fausse, juste incomplète : il manquait le
mécanisme qui FAIT apparaître la roche.

## Leçons de `r6_battle_throne` réappliquées dès le départ (pas redécouvertes)

Les deux retours utilisateur répétés sur le prototype précédent sont
traités comme des CONTRAINTES DE CONCEPTION ici, pas comme des
corrections après coup :

1. **Jamais de hold plat sur une pose d'ATTENTE.** `_idle_stance_span()`
   (copié du correctif de `r6_battle_throne`) anime la Phase 1
   (présence de la roche) en oscillation continue (transfert de poids,
   léger balancement du buste) — reste distinct du hold-and-snap d'un
   COIL de frappe, qui lui doit rester un vrai gel.
2. **Chaîne cinétique explicite, EXAGÉRÉE au bassin/torse** (demande
   utilisateur directe cette fois, pas une correction) : le rig R6 n'a
   ni genou ni cheville — toute la puissance perçue d'un coup de pied
   circulaire doit venir d'une rotation de torse largement plus grande
   qu'un humain réel n'en aurait besoin. Séquencée dans le temps
   (jambe d'appui pivote en premier, torse suit et charge à `Y=-62°`
   puis se relâche jusqu'à `Y=+78°` — un renversement de ~140°, la
   jambe qui frappe est ce qui bouge le plus vite et le plus tard dans
   la chaîne, comme un fouet).
3. **Placement des pieds vérifié par cinématique directe**
   (`grounded_root_y`/`_balanced`), jamais un offset Y constant —
   revérifié par `calibrate.py` (zéro anomalie non expliquée, voir
   plus bas).

## Stratégie de calibration : mesurer, jamais choisir à l'œil

Deux mécanismes MESURÉS par cinématique directe se succèdent, jamais
devinés :

1. **Le stomp détermine où la roche naît.** `STOMP_POINT` =
   `foot_tip_world()` du pied droit à l'instant `STOMP_STRIKE_T` (la
   pose du stomp est choisie pour la mise en scène — écrasement
   vertical, torse qui fouette vers l'avant/bas — puis MESURÉE, pas
   l'inverse). La roche jaillit à ce point X/Z exact.
2. **Le coup de pied doit ensuite vraiment l'atteindre.** Comme la
   roche est maintenant proche du personnage (elle vient de sortir du
   sol à ses pieds, pas posée à distance), la pose du coup de pied
   circulaire a été retravaillée pour que son point de contact mesuré
   (`KICK_CONTACT_POINT`) tombe sur la surface d'une roche centrée à
   `STOMP_POINT` — vérifié, pas supposé, en comparant les deux points
   mesurés indépendamment.
3. **La frappe de suivi** répète le même principe pour son propre
   contact (`FOLLOWUP_CONTACT_POINT`), avec la variante 3D de la
   fonction de placement (`sphere_center_for_surface_contact_3d`) —
   la roche est déjà en vol à cet instant, pas posée au sol.

Vérifié (`scripts/calibrate.py`) :

```
coup de pied     (t=2.567s) : ecart a la surface = -0.049 stud
frappe de suivi  (t=3.667s) : ecart a la surface = -0.000 stud
placement des pieds : aucune anomalie non expliquee
structure : OK -- 6 segments rigides, rotations finies et plausibles
```

## Chorégraphie (`scripts/choreography.py`)

- **Phase 1 — garde initiale** (0 → 0,6 s) : attente vivante (voir
  leçon 1 ci-dessus), **aucune roche n'existe encore à ce stade**.
- **Phase STOMP** (0,6 → 1,5 s) : WINDUP (la jambe droite se soulève,
  torse charge en ARRIÈRE en contrepoids) → **vrai hold tenu 0,2 s**
  (la jambe reste chargée en l'air) → STRIKE (lacher rapide, la jambe
  s'écrase verticalement au sol, torse fouette vers l'avant/bas) →
  RECOVER (le corps absorbe le choc). C'est un écrasement VERTICAL,
  pas un balayage latéral — le stomp ne change pas de côté comme le
  coup de pied circulaire qui suit. **C'est cet impact qui fait
  jaillir la roche** (voir `rock_track.py`, phase "jaillissement",
  déclenchée à `STOMP_STRIKE_T`).
- **Phase 2 — prise d'appui + coup de pied circulaire** (1,7 → 3,1 s) :
  WINDUP (transfert de poids) → COIL (chambrage complet, torse à
  `Y=-62°`, **vrai hold tenu 0,2 s**) → STRIKE (**snap en 2 frames**,
  torse renversé à `Y=+78°`, jambe qui frappe inverse le signe de son
  axe Z comme partout ailleurs dans ce dépôt) → FOLLOWTHROUGH
  (over-rotation) → RECOVER. C'est ce coup, balayage latéral cette
  fois, qui propulse la roche fraîchement sortie du sol.
- **Phase 3 — propulsion** (`rock_track.py`) : dès l'instant du
  contact, la roche quitte sa position de repos vers le point où la
  Phase 4 va la reprendre, avec un arc vers le haut et un tumbling qui
  s'accélère.
- **Phase 4 — frappe de suivi** (3,27 → 4,0 s) : vocabulaire de coup de
  poing (cross), pas de pied — la roche est déjà haute/loin, un second
  coup de pied depuis un appui statique ne l'atteindrait plus. Même
  chaîne cinétique et même hold-and-snap que la Phase 2. Redirige la
  roche vers sa trajectoire finale, plus rapide et plus plate.

Durée de l'animation du personnage : 4,0 s. La roche continue seule
au-delà (impact environnemental à t≈5,0 s si rien ne l'arrête avant —
voir plus bas).

## Trajectoire et « hitbox » de la roche (`scripts/rock_track.py`)

Ce dépôt n'a pas de moteur physique (voir la note déjà établie dans
`r6_divine_orb/scripts/orb_track.py`) : la trajectoire est **scriptée**
(des points choisis pour la lecture), exportée en JSON
(`output/rock_track.json`) pour qu'un script Roblox l'applique via
`CFrame` direct sur une vraie Part de collision — **pas via
l'Animator**, qui n'anime que les Motor6D d'un rig.

Ce fichier documente la géométrie de la trajectoire ; le brancher sur
un vrai système de compétence Roblox (détection de plusieurs
adversaires sur le trajet, arrêt anticipé sur premier contact,
callback d'impact environnemental si personne n'est touché) est du
ressort du code de gameplay, hors scope de ce prototype d'animation —
mais la trajectoire est conçue pour rester exploitable sans
modification :
- **Indépendante de toute cible** : `WORLD_TARGET_POS` est un point
  choisi (loin, au sol) représentant un mur/le sol lointain, pas un
  adversaire précis — si le skill réel touche un ennemi en cours de
  route, le code de gameplay tronque simplement la trajectoire à cet
  instant-là (elle reste valide jusqu'à `IMPACT_T`, tronquer plus tôt
  ne casse rien).
- **Segmentée explicitement** en 6 phases (`absente`/`jaillissement`/
  `repos`/`lancee`/`redirigee`/`impact`) avec les bornes de temps
  exposées (`STOMP_STRIKE_T`, `ERUPTION_END_T`, `STRIKE_T`,
  `FOLLOWUP_STRIKE_T`, `IMPACT_T`) : la roche n'existe pas du tout
  avant `STOMP_STRIKE_T` (`rock_position()` retourne `None`, même
  convention que `r6_divine_orb/scripts/orb_track.py` avant que le
  soleil invoqué n'existe), un système de compétence peut n'activer la
  hitbox qu'à partir de `STRIKE_T` (avant, elle est encore au sol,
  inerte).
- **Rayon de collision constant** (`ROCK_RADIUS`, la même sphère que
  celle utilisée pour la calibration des deux contacts ci-dessus) —
  un système de dégâts peut tester une sphère de ce rayon centrée sur
  la position de chaque échantillon, à n'importe quelle fréquence.

## Idées VFX (à jour dans le lecteur, voir plus bas)

- **Jaillissement (Phase STOMP, `STOMP_STRIKE_T`→`ERUPTION_END_T`)** :
  fissure/poussière/gravats au point d'impact du stomp, la roche perce
  la surface avec force (voir le dépassement/rebond de
  `rock_track.rock_position()`, phase "jaillissement").
- Coup de pied (Phase 2/3) : burst de poussière au pied + traînée
  circulaire du pied au contact.
- Vol (Phase 3/4) : particules de vitesse + petits fragments de roche
  qui s'en détachent.
- Impact (fin de Phase 4/`IMPACT_T`) : explosion de poussière, gros
  débris (voir `props_rock.rock_debris_parts()`, seed fixe
  déterministe), onde circulaire, flash bref.

## Caméra

Basse pendant le stomp (lisibilité de l'écrasement vertical de la
jambe et de la fissure au sol), trois-quarts pendant le coup de pied
circulaire qui suit, transition pour suivre le projectile pendant le
vol (Phase 3/4), zoom court sur l'impact final — voir `battle_throne` /
`hit_combo` pour le système de plans/coupes déjà établi, réutilisé ici
avec ces cues spécifiques.

## Lecteur (`scripts/dump_scene_data.py` + `build_viewer.py` + `rock_kick_viewer.html`)

**Mis à jour pour le mécanisme stomp + jaillissement** (voir plus
haut) : `dump_scene_data.py` exporte désormais les bornes de la phase
STOMP (`stomp_windup_t`/`stomp_hold_t`/`stomp_strike_t`/
`stomp_recover_t`/`eruption_end_t`) et le point d'impact mesuré
(`stomp_point`) en plus des instants déjà exportés ; le rendu Three.js
du lecteur (`rock_kick_viewer.html`) bascule la visibilité du cluster
de la roche STRICTEMENT sur `t >= STOMP_STRIKE_T` (garde explicite sur
CE bord aussi, symétrique à la garde déjà en place sur `t < IMPACT_T` --
voir le piège ci-dessous), ajoute un VFX de fissure/burst de poussière
au point d'impact du stomp, et une caméra basse dédiée à la phase STOMP
qui remonte en douceur vers le plan trois-quarts habituel du coup de
pied.

**Piège trouvé et corrigé en reconstruisant le lecteur** : le premier
essai de la garde de visibilité (`s.pos` interpolé non-null) laissait
la roche (encore sous terre) apparaître jusqu'à une frame (1/30s) AVANT
`STOMP_STRIKE_T` -- `sampleRock()` retombe sur l'échantillon non-nul dès
que l'un des deux voisins de l'interpolation a une position, côté
apparition comme côté disparition. Corrigé par une garde EXPLICITE sur
le temps (`t >= STOMP_STRIKE_T`), symétrique à celle déjà en place sur
`t < IMPACT_T`, jamais une déduction depuis la nullité de la position
interpolée. Un deuxième piège, distinct et non corrigible côté lecteur
(géométrie/track verrouillées, voir Défauts connus plus bas) : au tout
premier instant `STOMP_STRIKE_T`, le sommet du cluster de la roche
dépasse déjà d'environ 0,77 stud au-dessus du sol (bosse du cluster
`props_rock.rock_parts()` combinée à la profondeur de départ fixe de
`rock_track._ERUPTION_START_Y`) -- se lit comme "la roche vient de
percer la surface", pas comme un pop-in instantané, mais ce n'est pas
un zéro-a-cent pixel-parfait.

Un deuxième bug trouvé en reconstruisant la caméra : le point visé par
la caméra retombait sur `WORLD_TARGET_POS` (très loin, Z=-34) dès que
la roche n'avait pas de position -- correct après l'impact final, mais
faux avant `STOMP_STRIKE_T` (la roche n'existe pas encore, mais ce
repli tirait déjà le cadrage loin du personnage dès t=0). Corrigé :
repli sur le personnage lui-même tant que la roche n'existe pas,
`WORLD_TARGET_POS` réservé au repli après `IMPACT_T`.

Échantillonne le personnage directement via `anim_engine.build_rig()`/
`apply_choreography()`/`sample()` (pas de round-trip par `.rbxmx` --
les contacts déjà calibrés le sont sous la convention position-only de
`anim_engine`, un aller-retour par `resolve_rbxmx` en désynchroniserait
la mesure). La roche est un `Group` Three.js qui suit `rock_position(t)`
image par image (position + rotation de tumbling depuis `spin_deg`),
invisible tant que la phase est `"absente"`, et bascule vers le cluster
de débris statique (`rock_debris_parts`, placé à
`rock_track.WORLD_TARGET_POS`) strictement à partir de `IMPACT_T` --
piège trouvé et corrigé en cours de route sur la premiere version du
lecteur : la roche restait visible APRÈS l'impact (la fonction
d'échantillonnage tient la dernière position valide en interpolant vers
un échantillon nul), la bascule doit rester sur `t >= IMPACT_T`
explicitement, pas sur "position nulle" -- a revalider avec le nouveau
decoupage de phases (`absente`/`jaillissement` en plus).

**Défauts connus, pour une passe de suite** :
- Les particules de vitesse pendant le vol (Phase 3/4) sont présentes
  mais discrètes à l'échelle d'une vignette -- a resserrer si le rendu
  en jeu réel les juge trop faibles.
- Les fragments de débris sont des boîtes axées sur les axes du monde
  (pas de rotation par fragment, `props_rock.rock_debris_parts()` n'en
  exporte pas) -- purement cosmétique, lisible mais un peu plat comparé
  au cluster de sphères de la roche intacte.
- **Occultation du personnage par la roche pendant le coup de pied
  circulaire** : la roche jaillit maintenant à 1,3-2 studs du
  personnage (au lieu de ~4,5 avant correction) tout en restant
  "énorme" (`ROCK_RADIUS`=2, diamètre 4 studs) -- à cette proximité,
  AUCUN azimut de caméra testé (45 à 125°, voir historique de session)
  ne suffit à séparer les deux à l'écran, l'écart étant trop petit par
  rapport à la taille de la roche. Le plan retenu (élévation plus haute
  + distance plus grande que l'ancien plan bas, voir CAM_KEYS) garde le
  torse/la tête visibles au-dessus de la roche et laisse le VFX de
  balayage/poussière du pied (dessiné en 2D par-dessus la scène 3D,
  donc jamais occulté) marquer le point de contact réel, mais les
  jambes elles-mêmes restent en grande partie masquées par le cluster
  pendant le chambrage/la frappe. Accepté pour cette passe -- resterait
  à revoir si Milan juge que la lisibilité du contact jambe/roche doit
  primer sur la taille annoncée de la roche.

## Vérification (captures)

Reprise avec le mécanisme corrigé (stomp → jaillissement), revue
personnellement image par image (pas seulement le rapport de l'agent
qui a reconstruit le lecteur) avant commit. Sept captures retenues dans
`captures/verification/2026-09-05-rock-kick-v2-*.png` (preuve
ponctuelle de correction de bug/feature -- pas un verdict qualité
formel, voir CLAUDE.md) ; les six anciennes captures montrant la roche
déjà posée au sol ont été retirées (plus représentatives de rien
d'actuel, pas une preuve à garder) :

- `-idle.png` -- garde initiale, aucune roche.
- `-rock-absent-before-stomp.png` -- 20 ms avant `STOMP_STRIKE_T` :
  toujours aucune roche visible (confirme la garde stricte sur le
  temps, pas sur une position interpolée nulle).
- `-stomp-impact.png` -- instant exact de `STOMP_STRIKE_T` : fissure +
  poussière au point d'impact, roche qui commence tout juste à
  percer.
- `-rock-risen.png` -- après jaillissement complet, roche posée, tenue
  avant le coup de pied.
- `-kick-contact.png` -- instant du coup de pied circulaire : le VFX de
  contact marque bien le point mesuré sur la roche (torse/tête restent
  visibles au-dessus d'elle ; les jambes, elles, sont en grande partie
  masquées par le volume de la roche à cette proximité -- voir Défauts
  connus).
- `-followup-strike.png` -- la frappe de suivi redirige la roche déjà
  en vol.
- `-impact-debris.png` -- après l'impact final, débris dispersés.

**Point de vigilance supplémentaire, trouvé lors de cette relecture** :
en comparant `-stomp-impact.png` (t=1,30s) à une capture intermédiaire
à t=1,50s (mi-jaillissement, non retenue dans la liste ci-dessus), la
roche semble occuper MOINS de place à l'écran à 1,50s qu'à 1,30s alors
qu'elle a mathématiquement grossi entre ces deux instants (vérifié :
`rock_track.rock_position()` est bien croissante en Y sur cette
fenêtre, aucune régression de taille réelle). L'écart vient de la
caméra, qui commence sa transition vers le plan du coup de pied pile
dans cette fenêtre (`STOMP_RECOVER_T`=1,5s) -- pas un bug de
trajectoire, mais un enchaînement de plans qui pourrait lire comme "la
roche rapetisse" à l'œil si on regarde ces deux instants précis l'un
après l'autre. Laissé en l'état pour cette passe (le jaillissement
lui-même, aux instants retenus ci-dessus, est net et lisible) --
resterait à retimer la transition caméra si Milan la trouve confuse en
lecture continue.
