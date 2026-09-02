# Le jugement — invocation et jet d'une boule divine (R6, Roblox)

Prototype isolé, sans lien avec RANK ZERO ni MyAnimeRPG — même isolation
que les trois autres prototypes de `experiments/`, dont celui-ci
**réutilise telle quelle** l'infrastructure de rig déjà vérifiée
(`r6_rig.py`, `anim_engine.py`, `export_kfseq.py`, `resolve_rbxmx.py`,
le rig `RigR6.rbxmx` importé depuis GitHub — voir `rig/PROVENANCE.md`,
provenance identique aux autres prototypes) et `export_model.py`
(export de `Part` statiques, copié depuis `r6_throne_crown`).

## Demande

Après rejet de la scène de chute divine (« Nul, on tente un autre ») :
« le perso lève la main pour invoquer une énorme boule divine et d'un
ton hautain [la jette] là-bas sur le monde. » Nouvelle scène **isolée**
(nouveau dossier), pas une variation de `r6_divine_descent`.

## Ce qui est livré

- `output/character_haughty_orb_throw.rbxmx` — `KeyframeSequence` du
  personnage (rig R6 réel, 6 segments rigides, mêmes contraintes que les
  autres prototypes : pas de coude/genou, Motor6D 3 DOF). 105 keyframes,
  3,45 s à 30 Hz.
- `output/divine_orb.rbxmx` — `Model` statique de la boule (un `Ball`,
  `Material = Neon` — brille nativement dans le moteur Roblox, même
  choix que les gemmes de `r6_throne_crown`). Sa position/taille réelles
  au fil du temps sont dans `orb_track.json`, pas figées dans ce fichier
  (voir plus bas).
- `output/orb_track.json` — trajectoire monde de la boule (position +
  rayon par échantillon). À appliquer via un script (`CFrame` direct +
  `Size`), **pas** via l'`Animator` — même principe que
  `crown_track.json` dans `r6_throne_crown`.
- Lecteur HTML (invocation + charge + lancer + vol + impact, résolu par
  le moteur pour le personnage) : https://claude.ai/code/artifact/7dba35da-9bb1-4210-b492-6ccf50db4efa

## Chorégraphie

Cinq phases (`scripts/choreography.py`, fonction `haughty_orb_throw()`) :

1. **Posture hautaine** (0,00 s) — buste et tête inclinés en arrière
   (`Torso`/`Head` X négatif — même convention de signe que la pose
   fière du sacre), jambes en appui asymétrique décontracté : un dieu
   qui toise le monde n'a pas besoin de se préparer au combat.
2. **Invocation** (0,00 s → `RAISE_T`=0,70 s) — la main droite se lève.
3. **Charge** (`RAISE_T` → `ANTICIP_T`=2,15 s) — la boule grossit en la
   tenant (voir plus bas), léger balancement du buste (±3° en Y) pour
   que « l'énergie qui respire » se lise dans le corps, pas seulement
   dans le halo du lecteur.
4. **Lancer** (`ANTICIP_T` → `THROW_T`=2,30 s, 0,15 s seulement) — le
   bras s'abat vers l'avant-bas, le buste suit (transfert de poids
   réel). **C'est ce keyframe (`RELEASE_T` = `THROW_T`) qui détache la
   boule de la main** dans le lecteur, plus un prolongement du geste
   (*follow-through*) juste après.
5. **Récupération et posture finale** (`THROW_T` + 0,55 s → 3,45 s) — le
   personnage revient à sa posture hautaine, satisfait, à regarder
   l'impact au loin.

## La boule ne sort pas exactement de la main — limite réelle du rig

Vérifié par balayage numérique (`scripts/calibrate.py`), pas supposé :
la main levée **ne peut physiquement pas dépasser la hauteur de la
tête**, quel que soit l'angle du bras essayé (balayage de -90° à 180°,
inclinaison du torse de -22° à 0°) — l'écart mesuré reste autour de
1,0-1,05 stud sous le sommet de la tête. Longueur de bras fixe, aucun
coude pour « rallonger » la portée — même catégorie de limite déjà
rencontrée dans `r6_divine_descent` (portée du poing au sol).

Corrigé en positionnant la boule avec un **décalage vertical fixe**
au-dessus de la main suivie (`HAND_OFFSET_Y`=1,4 stud dans
`orb_track.py`, calibré pour dépasser l'écart mesuré avec de la marge,
vérifié par capture d'écran) plutôt que de la coller exactement sur la
pointe du bras. Même esprit que le petit saut assumé de la couronne
posée sur la tête dans le sacre : une limite réelle du rig, documentée,
pas maquillée.

## La trajectoire de vol n'est pas une extrapolation physique

`calibrate.py` mesure la vitesse instantanée du bras au keyframe de
lancer : ~5,3 studs/s vers le bas. Cette valeur est **mesurée mais
délibérément pas utilisée** pour dériver la trajectoire de vol — elle
ne dit rien sur où se trouve « le monde » ni sur combien de temps le vol
doit durer pour rester dramatique. `orb_track.py` scripte donc une
trajectoire indépendante :

- **En charge** (`RAISE_T` → `RELEASE_T`) : suit la main levée (+
  décalage fixe), rayon qui croît de 0 à `ORB_MAX_RADIUS` avec une
  accélération douce (`_ease_in`, pas une croissance linéaire).
- **En vol** (`RELEASE_T` → `IMPACT_T`) : interpolation entre la
  position réelle au relâchement et `WORLD_TARGET_POS` — un point
  **choisi** (loin en contrebas et devant le personnage), pas mesuré —
  avec un léger arc (une bosse sinusoïdale) plutôt qu'une ligne droite,
  pour lire comme un vrai jet lancé.

Exactement le même principe que la trajectoire de la couronne dans le
sacre : un point de départ réel + un point d'arrivée choisi, jamais une
extrapolation physique depuis la vitesse du bras.

## Mise en scène du lecteur : le monde est à une position d'écran fixe

`WORLD_TARGET_POS` (le point 3D réel que vise la boule, dans
`orb_track.json`) est loin — plusieurs dizaines de studs sous et devant
le personnage. Projeté tel quel dans le lecteur (projection
orthographique à l'échelle du personnage), il serait à des milliers de
pixels hors-champ. Le lecteur affiche donc le halo du « monde » à une
**position d'écran fixe** (`WORLD_SCREEN`), pas à sa vraie position 3D —
une compression visuelle nécessaire pour rester lisible dans un cadrage
fixe, documentée ici plutôt que cachée (même famille de choix que la
caméra en poursuite des prototypes précédents). La donnée livrée
(`orb_track.json`) reste la vraie trajectoire 3D à l'échelle réelle,
utilisable telle quelle dans un vrai projet Roblox.

## Bug trouvé par capture d'écran, pas par les nombres

Même leçon que les prototypes précédents : la vérification numérique
garantit que les données sont *correctes*, pas qu'elles se *lisent*
correctement à l'écran. Premier essai du lecteur : la position d'écran
du point de relâchement (`RELEASE_SCREEN`) était accumulée pendant le
rendu (mise à jour seulement quand `t < RELEASE_T`) — ça suppose que les
frames précédentes ont déjà été rendues. Faux pour une capture isolée à
une frame ≥ `RELEASE_T` (ou un utilisateur qui fait glisser le curseur
directement vers la fin) : `RELEASE_SCREEN` restait à sa valeur initiale
`(0,0)`, la boule se dessinait hors-champ au lancer, puis avec une
traînée partant du mauvais point pendant tout le vol. Corrigé en
calculant `RELEASE_SCREEN` **une seule fois**, directement depuis les
données (`computeReleaseScreen()`), plutôt que de l'accumuler comme un
effet de bord du rendu.

## Rig du personnage

Même rig R6 vérifié (dépôt Adonis, licence MIT) que les autres
prototypes de ce dossier — voir `rig/PROVENANCE.md`.

## Commandes

```bash
cd scripts
source ../../r6_aerial_kick_combo/.venv/bin/activate

# Verification numerique (FK, pas a l'oeil)
python3 calibrate.py

# Export du KeyframeSequence + du Model de la boule (+ verification structurelle)
python3 run_scene.py

# Calcule la trajectoire monde de la boule
python3 orb_track.py

# Assemble le lecteur HTML final (JSON de scene injecte dans le template)
python3 build_viewer.py
```
