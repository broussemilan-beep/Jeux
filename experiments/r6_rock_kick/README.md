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

## Stratégie de calibration : placer la roche au point mesuré, pas l'inverse

Contrairement aux prototypes à deux rigs (où l'adversaire impose sa
propre position et il faut ajuster le coup pour l'atteindre), ici la
roche n'a pas de contrainte propre — elle peut être placée EXACTEMENT
où le pied/poing termine sa course. `scripts/choreography.py` calcule
donc la pose du coup de pied et de la frappe de suivi d'abord (choix
de mise en scène : chambrage large, renversement de torse exagéré),
MESURE ensuite par cinématique directe où le bout du pied/poing
atterrit (`foot_tip_world()`/`fist_tip_world()`), puis calcule le
CENTRE de la roche tel que ce point mesuré tombe exactement sur sa
SURFACE — jamais sur son centre (`sphere_center_for_surface_contact()`
pour la roche posée au sol, sa variante 3D pour la roche déjà en vol
au moment de la frappe de suivi).

Vérifié (`scripts/calibrate.py`) :

```
coup de pied     (t=2.567s) : ecart a la surface = 0.000 stud
frappe de suivi  (t=3.667s) : ecart a la surface = -0.000 stud
placement des pieds : aucune anomalie non expliquee
structure : OK -- 6 segments rigides, rotations finies et plausibles
```

## Chorégraphie (`scripts/choreography.py`)

- **Phase 1 — présence** (0 → 1.2 s) : garde tenue en oscillation
  continue (voir leçon 1 ci-dessus), pas un arrêt sur image.
- **Phase 2 — prise d'appui + coup de pied** (1.2 → 3.1 s) : WINDUP
  (transfert de poids) → COIL (chambrage complet, torse à `Y=-62°`,
  **vrai hold tenu 0.2 s** — hold-and-snap, la tension doit se voir) →
  STRIKE (**snap en 2 frames**, torse renversé à `Y=+78°`, jambe qui
  frappe inverse le signe de son axe Z comme partout ailleurs dans ce
  dépôt) → FOLLOWTHROUGH (over-rotation, l'inertie continue après le
  contact) → RECOVER.
- **Phase 3 — propulsion** (`rock_track.py`) : dès l'instant du
  contact, la roche quitte sa position de repos vers le point où la
  Phase 4 va la reprendre, avec un arc vers le haut et un tumbling qui
  s'accélère.
- **Phase 4 — frappe de suivi** (3.27 → 4.0 s) : vocabulaire de coup de
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
- **Segmentée explicitement** en 4 phases (`repos`/`lancee`/
  `redirigee`/`impact`) avec les bornes de temps exposées
  (`STRIKE_T`, `FOLLOWUP_STRIKE_T`, `IMPACT_T`) : un système de
  compétence peut n'activer la hitbox de la roche qu'à partir de
  `STRIKE_T` (avant, elle est encore au sol, inerte).
- **Rayon de collision constant** (`ROCK_RADIUS`, la même sphère que
  celle utilisée pour la calibration des deux contacts ci-dessus) —
  un système de dégâts peut tester une sphère de ce rayon centrée sur
  la position de chaque échantillon, à n'importe quelle fréquence.

## Idées VFX (implémentées dans le lecteur, voir plus bas)

- Spawn (Phase 1) : poussière/gravats légers autour de la roche.
- Coup de pied (Phase 2/3) : burst de poussière au pied + traînée
  circulaire du pied au contact.
- Vol (Phase 3/4) : particules de vitesse + petits fragments de roche
  qui s'en détachent.
- Impact (fin de Phase 4/`IMPACT_T`) : explosion de poussière, gros
  débris (voir `props_rock.rock_debris_parts()`, seed fixe
  déterministe), onde circulaire, flash bref.

## Caméra

Basse/trois-quarts pendant le coup de pied (Phase 2), transition pour
suivre le projectile pendant le vol (Phase 3/4), zoom court sur
l'impact final — voir `battle_throne` / `hit_combo` pour le système de
plans/coupes déjà établi, réutilisé ici avec ces cues spécifiques.

## Vérification (captures)

Voir `captures/verification/` (préfixe `2026-09-05-rock-kick-`) pour
les captures Playwright du lecteur réel — pas décrites en prose ici,
voir directement les fichiers.
