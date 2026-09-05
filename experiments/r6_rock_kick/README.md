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

**En cours de mise à jour suite à la correction du mécanisme
d'apparition de la roche** (stomp + jaillissement, voir plus haut) --
la version précédente du lecteur/des captures montrait encore la roche
déjà posée au sol dès le début de la scène ; le fichier JSON
(`output/rock_track.json`) et `choreography.py`/`rock_track.py` sont
déjà corrigés et vérifiés numériquement (voir calibration ci-dessus),
la reconstruction du rendu Three.js (roche invisible avant
`STOMP_STRIKE_T`, VFX de fissure/jaillissement, caméra basse dédiée au
stomp) et les nouvelles captures suivent.

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

## Vérification (captures)

**À reprendre** avec le mécanisme corrigé (stomp → jaillissement) --
les six captures précédentes (`captures/verification/2026-09-05-rock-kick-*`)
montrent encore l'ancienne version (roche déjà posée au sol dès le
début) et seront remplacées une fois le lecteur reconstruit.
