# Genkidama — invocation et jet du soleil à deux mains (R6, Roblox)

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

**Retour de correction** (deuxième itération, sur cette même scène) :
« Non le personnage lève la main droit au début de l'animation et abas
le soleil comme un genkidama sur le monde. » Trois changements :
1. Le lever de main(s) commence **au tout début** de l'animation
   (0,30 s), plus après 0,70 s d'attente hautaine immobile.
2. Geste **à deux mains** (genkidama), pas une seule.
3. La boule devient **le soleil** (couleur, halo) plutôt qu'une boule
   d'énergie violette générique.

Cette deuxième itération a aussi mis au jour et corrigé un **bug de
mesure** dans la calibration de la première version — voir plus bas
(« Bug de calibration trouvé et corrigé pendant cette itération »).

## Ce qui est livré

- `output/character_haughty_orb_throw.rbxmx` — `KeyframeSequence` du
  personnage (rig R6 réel, 6 segments rigides, mêmes contraintes que les
  autres prototypes : pas de coude/genou, Motor6D 3 DOF). 93 keyframes,
  3,05 s à 30 Hz.
- `output/divine_orb.rbxmx` — `Model` statique du soleil (un `Ball`,
  `Material = Neon` — brille nativement dans le moteur Roblox, même
  choix que les gemmes de `r6_throne_crown`). Sa position/taille réelles
  au fil du temps sont dans `orb_track.json`, pas figées dans ce fichier
  (voir plus bas).
- `output/orb_track.json` — trajectoire monde du soleil (position +
  rayon par échantillon). À appliquer via un script (`CFrame` direct +
  `Size`), **pas** via l'`Animator` — même principe que
  `crown_track.json` dans `r6_throne_crown`.
- Lecteur HTML (invocation à deux mains + charge + lancer + vol +
  impact, résolu par le moteur pour le personnage) :
  https://claude.ai/code/artifact/7dba35da-9bb1-4210-b492-6ccf50db4efa

## Chorégraphie

Cinq phases (`scripts/choreography.py`, fonction `haughty_orb_throw()`) :

1. **Invocation** (0,00 s → `RAISE_T`=0,30 s) — les **deux mains** se
   lèvent ensemble **dès la toute première frame** (retour utilisateur :
   « au début de l'animation »), pas après une pose hautaine immobile
   comme dans la première version. Le buste et la tête restent hautains
   (X négatif — même convention de signe que la pose fière du sacre)
   dès ce keyframe : le personnage n'entre pas en garde, il invoque.
2. **Charge** (`RAISE_T` → `ANTICIP_T`=1,75 s) — le soleil grossit
   au-dessus de la tête, tenu à deux mains (voir plus bas), léger
   balancement du buste (±3° en Y) pour que « l'énergie qui respire » se
   lise dans le corps, pas seulement dans le halo du lecteur ; de petits
   filaments d'énergie convergent visuellement vers les mains dans le
   lecteur (détail signature du genkidama, voir sa section).
3. **Anticipation** (`ANTICIP_T` → `THROW_T`=1,90 s) — les mains se
   resserrent légèrement l'une vers l'autre (compression avant le
   lancer), le buste et la tête se penchent encore plus en arrière
   (-22°/-15°).
4. **Lancer** (`THROW_T`, 0,15 s) — les deux bras balaient ensemble
   depuis au-dessus de la tête jusqu'à un peu au-delà de l'horizontale,
   le buste suit (transfert de poids réel) — un vrai « abattre » à deux
   mains, pas un geste qui reste haut. **C'est ce keyframe
   (`RELEASE_T` = `THROW_T`) qui détache le soleil des mains** dans le
   lecteur, plus un prolongement du geste (*follow-through*) juste
   après, bras continuant leur descente.
5. **Récupération et posture finale** (`THROW_T` + 0,55 s → 3,05 s) — le
   personnage revient à sa posture hautaine, satisfait, à regarder
   l'impact au loin.

## Bug de calibration trouvé et corrigé pendant cette itération

La première version de cette scène affirmait (calibrée par balayage
numérique, donc a priori fiable) que « la main levée ne peut
physiquement pas dépasser la hauteur de la tête » et calait
`RAISE_RIGHT_ARM` sur `(0, 0, -15)` en conséquence — **X=0**, c'est-à-dire
l'angle documenté comme « le bras qui pend au repos », pas un bras levé.
En redéveloppant le geste à deux mains pour cette itération, un sweep
isolé (voir `calibrate.py`, section « bug trouvé et corrigé ») a montré
que `tip_world(..., "top")` — utilisé partout pour « la main » — renvoie
en réalité le bout du bras **le plus proche de l'épaule** (le bout
attaché au Motor6D), qui bouge à peine quel que soit l'angle du bras :
à X=0 il vaut ~4,0 (proche du repos), à X=180 (bras à la verticale,
au-dessus de la tête) il vaut ~3,0 — c'est `tip_world(..., "bottom")`
qui suit vraiment la main (X=0 → main basse ~2,0 ; X=180 → main haute
~5,0). La première version mesurait donc l'épaule en pensant mesurer la
main, d'où la fausse conclusion de « limite réelle du rig ».

Corrigé : `calibrate.py` et `orb_track.py` utilisent maintenant
`"bottom"` pour les bras (`"top"` reste correct pour la Tête, dont le
sommet est bien le bout éloigné du cou). Re-calibré avec le bon bout —
sweep fin autour de X=180 (voir `choreography.py`) : à
`RAISE_RIGHT_ARM = (180, 0, -20)` / `RAISE_LEFT_ARM = (180, 0, 20)`
(bras droit au-dessus de la tête, mains écartées symétriquement), la
main est en réalité **~0,15 stud AU-DESSUS** du sommet de la tête —
l'inverse de ce que croyait la première version — et parfaitement
symétrique D/G (écart de hauteur nul, vérifié numériquement, pas
supposé). Les angles de `ANTICIP`/`THROW`/`FOLLOW` ont été redessinés en
conséquence (balayage 180° → 40° → 10°, un vrai mouvement de descente,
alors que la première version restait proche du même angle sans le
savoir).

`HAND_OFFSET_Y` (`orb_track.py`) reste utilisé, mais pour une raison
différente : plus une compensation de limite du rig, juste une marge
visuelle pour que le soleil flotte visiblement au-dessus des mains
jointes plutôt que de les toucher (réduit de 1,4 à 1,0 stud en
conséquence).

## La trajectoire de vol n'est pas une extrapolation physique

`calibrate.py` mesure la vitesse instantanée du bras au keyframe de
lancer : ~5,3 studs/s vers le bas. Cette valeur est **mesurée mais
délibérément pas utilisée** pour dériver la trajectoire de vol — elle
ne dit rien sur où se trouve « le monde » ni sur combien de temps le vol
doit durer pour rester dramatique. `orb_track.py` scripte donc une
trajectoire indépendante :

- **En charge** (`RAISE_T` → `RELEASE_T`) : suit le point médian des
  **deux mains** levées (+ décalage fixe), rayon qui croît de 0 à
  `ORB_MAX_RADIUS` avec une accélération douce (`_ease_in`, pas une
  croissance linéaire).
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

## Caméra par défaut changée en « face » — trouvé par capture d'écran

Toujours la même leçon : capturé en 3/4 (`-50°`, angle par défaut des
autres prototypes), le geste à deux mains se lisait mal — les deux bras
symétriques se chevauchent partiellement depuis cet angle oblique et la
silhouette se lit comme un bloc diagonal ambigu, pas comme « deux bras
levés ». Capturé de face (`0°`), les deux bras dessinent nettement un
« V » symétrique convergeant vers le soleil au-dessus de la tête — le
geste genkidama se lit immédiatement. Angle par défaut du lecteur changé
en conséquence (`AZ = 0`, bouton « face » actif au chargement) ; le 3/4
reste disponible en un clic pour qui préfère cet angle.

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
