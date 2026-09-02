# Le sacre — trône et couronne (R6, Roblox)

Prototype isolé, sans lien avec RANK ZERO ni MyAnimeRPG — même isolation
que `experiments/r6_aerial_kick_combo/`, dont ce prototype **réutilise
telle quelle** l'infrastructure de rig déjà vérifiée (`r6_rig.py`,
`anim_engine.py`, `export_kfseq.py`, `resolve_rbxmx.py`, le rig
`RigR6.rbxmx` importé depuis GitHub — voir `rig/PROVENANCE.md` du
prototype source, provenance identique ici). Ce qui est nouveau : la
géométrie du trône/couronne (`scripts/props.py`), la chorégraphie
d'assise et de couronnement (`scripts/choreography.py`), et le calcul de
la trajectoire de la couronne (`scripts/compute_crown_track.py`).

## Demande

« Fais une [animation] où le perso est sur un trône et met une
couronne, crée les rig 3D. » Portée précisée avec l'utilisateur avant de
commencer : animation séparée du combo de coups de pied (pas une suite
de la même séquence), trône + couronne à modéliser/riguer comme
véritables objets 3D (pas un décor de fond).

## Ce qui est livré

- `output/character_sit_and_crown.rbxmx` — `KeyframeSequence` du
  personnage (rig R6 réel, 6 segments rigides, mêmes contraintes que le
  combo de coups de pied : pas de coude/genou, Motor6D 3 DOF).
- `output/throne.rbxmx` — `Model` du trône (14 `Part`, statique, ancré).
- `output/crown.rbxmx` — `Model` de la couronne (11 `Part` : bande +
  5 pointes + 5 gemmes), dans son repère local (centre = milieu de la
  bande — voir "La couronne change de parent" plus bas).
- `output/crown_track.json` — trajectoire monde de la couronne
  (position + rotation par échantillon), pour le script de re-weld
  qu'un vrai projet Roblox doit fournir (voir plus bas).
- Lecteur HTML (scène complète, personnage + trône + couronne, résolus
  par le moteur) : https://claude.ai/code/artifact/ab0c53e4-2909-48a0-bc7d-fc6b296b6b15

## Géométrie du trône et de la couronne

Tout en `Part` Roblox (`scripts/export_model.py`), dans le **même
repère** que le personnage (studs, -Z = avant, sol = Y 0). Choix
délibéré : ni `BrickColor` (l'index de palette exact n'est pas
vérifiable de mémoire hors-ligne, pas de client Roblox dans ce
sandbox) ni `Material` (même raison pour les valeurs numériques de
`Enum.Material`) — seulement `Color3uint8` (RGB direct, sans
ambiguïté) et `Shape` (Block/Cylinder/Ball, dont je suis sûr). Mieux
vaut un fichier qui n'affirme que ce qui est vérifié qu'un fichier qui a
l'air complet mais invente des valeurs.

Trône : dais, 4 pieds, siège, dossier (monte au-dessus de la tête du
personnage debout), 2 accoudoirs, bande dorée + 3 fleurons. Couronne :
bande (Cylinder) + 5 pointes (hauteur variable, la plus haute à l'avant)
+ 5 gemmes (Ball).

## Calibration — vérifiée par le calcul, pas à l'oeil

Les valeurs numériques du rig R6 permettent de calculer, sans deviner,
où le personnage debout a les pieds et où sont ses hanches assis :

- Torse au repos = `HumanoidRootPart` (aucune translation locale sur ce
  joint). Hanche = bas du torse = `HumanoidRootPart.Y - 1`. Pied =
  `HumanoidRootPart.Y - 3`. Sommet de la tête = `HumanoidRootPart.Y + 2`.
  (Lu sur `rig/r6_rig.json`, pas mesuré à l'oeil — voir
  `scripts/calibrate.py`.)

Conséquence : `HumanoidRootPart.Y = 3` donne un personnage debout pieds
à 0, tête à 5 studs — le standard R6. Le siège du trône est donc posé
avec le dessus à **Y = 2.0** (hanche assise à Y=3, moins 1) pour que le
personnage s'y encastre sans avoir à changer sa hauteur de hanche en
s'asseyant — **exactement le mécanisme de l'assise R6 par défaut de
Roblox** : le bassin ne descend pas, seules les jambes tournent à la
hanche. Comme ce rig n'a pas de genou, la jambe entière (cuisse ET
tibia, un seul segment rigide) pointe vers l'avant à l'horizontale une
fois assis — ce qui EST le look d'une assise R6 vanilla, pas une
simplification à cacher.

### Sémantique des axes du bras — établie par diagnostic, pas supposée

La première hypothèse (par analogie avec les jambes du combo de coups
de pied : X = amplitude du mouvement) était **fausse** pour les bras.
Vérifié en isolant chaque axe (`scripts/calibrate.py` contient la
méthode, un diagnostic ad-hoc l'a précédée) :

- **X positif** : le bras part vers l'avant (-Z) puis monte par-dessus,
  jusqu'à X=180° = au-dessus de la tête.
- **Z** (bras droit) **positif** : lève le bras vers l'extérieur (+X) et
  vers le haut — Z≈55° pose la main exactement sur le dessus de
  l'accoudoir. **Négatif** : ramène le bras vers l'intérieur (croise le
  corps). Bras gauche : signe opposé (symétrie miroir, vérifiée).

Conséquence mesurée, pas supposée : la portée verticale maximale du
poignet (bras droit, sans coude, longueur fixe) plafonne à **Y≈5,0** —
la couronne ne peut pas être « levée très haut au-dessus de la tête »,
seulement juste au-dessus, qui est déjà là où elle doit atterrir. Le
geste de couronnement est donc nécessairement bref (lever ~ juste
au-dessus, puis poser), pas un grand geste ample — contrainte du rig,
assumée plutôt que contournée par une pose qui aurait l'air fausse.

Valeurs retenues, toutes vérifiées par calcul de position monde contre
la géométrie du trône :

| Pose | Bras droit | Main droite (monde) | Cible |
|---|---|---|---|
| assis, repos | (0,0,55) | (2.516, 3.048, -0.012) | accoudoir (X~2.6 Y~3.0) |
| prise (pickup) | (5,0,58) | (2.537, 3.121, -0.059) | coussin de la couronne |
| levée | (180,0,-35) | (0.549, 4.985, -0.350) | au-dessus de la tête (Y max ~5.0) |
| posée | (180,0,-45) | (0.293, 4.865, -0.431) | sommet de tête (0, 4.94, -0.48), écart 0.31 stud |

## La couronne change de parent en cours de scène

Un `KeyframeSequence` anime les Motor6D d'**un seul rig**. Il ne peut
pas faire porter un objet par la main puis le faire "sauter" sur la
tête — ça demande de changer l'objet **parent** (coussin → main → tête)
en cours de clip, ce que ce format ne peut pas exprimer. Dans un vrai
projet Roblox, ça se fait par un script qui re-weld la couronne au bon
instant (typiquement sur un `Marker` de l'`AnimationTrack`).

`scripts/compute_crown_track.py` calcule cette trajectoire par la MÊME
cinématique directe que tout le reste du pipeline (pas une
approximation à l'oeil) et l'exporte en JSON (`output/crown_track.json`)
— trois phases :

1. `t < 1.35s` : statique, posée sur le coussin.
2. `1.35s ≤ t < 2.00s` : suit le bout de la main droite (orientation
   gardée verticale — la vriller avec la rotation complète du bras,
   ~175° sur cette fenêtre, aurait l'air faux).
3. `t ≥ 2.00s` : suit le sommet de la tête, **rotation de la tête
   comprise** — une fois posée, elle tourne avec la tête.

Deux points de recollement mesurés plutôt que masqués : saut coussin→
main à la prise = **0,000 stud** (coïncidence du calibrage, pas
garanti en général) ; saut main→tête à la pose = **0,307 stud** (léger,
assumé).

## Vérifications

- **Structure R6** (`scripts/run_scene.py`) : 6 segments rigides,
  aucune translation locale hors racine, rotations finies et dans une
  plage plausible (< 260°, marge au-dessus du 180° max utilisé). OK dès
  le premier export.
- **Round-trip moteur** (`scripts/resolve_rbxmx.py`, même outil que le
  combo de coups de pied) : `HumanoidRootPart` toujours correctement
  ignorée par l'Animator (0 stud/deg), Torso Y résolu par l'équation du
  moteur cohérent avec la chorégraphie (min 2.95 = creux de l'assise,
  max 3.00 = reste du temps, cohérent avec un personnage qui ne saute
  pas dans cette scène).
- **Vérification VISUELLE réelle**, pas juste des chiffres : capture
  d'écran automatisée du lecteur HTML via Playwright (Chromium
  pré-installé dans ce sandbox), à plusieurs instants de la scène. C'est
  cette capture qui a trouvé le seul vrai bug de ce prototype (voir
  ci-dessous) — les nombres de calibration étaient déjà bons et
  n'auraient rien révélé.

### Bug trouvé par capture d'écran, pas par les nombres

Premier export : la phase "approche" (personnage debout, avant de
s'asseoir) plaçait `HumanoidRootPart` à **Z = +1.6**. Signe inversé :
le siège et le dossier du trône occupent Z de -0.9 à +3.3, donc Z=+1.6
place le personnage débout **à l'intérieur du volume du trône**, caché
derrière le dossier gris. Aucune vérification numérique (hanche à la
bonne hauteur, mains sur les accoudoirs) ne pouvait le révéler — ces
calculs ne portent que sur la phase assise, pas sur la phase d'approche,
et un personnage caché reste "structurellement" correct. Seule la
capture d'écran réelle (pas une description imaginée) l'a montré :
au premier instant de la scène, aucune silhouette humaine visible,
seulement le trône. Corrigé en inversant le signe (Z=-1.6, cohérent avec
-Z = avant du personnage = côté ouvert du trône). Revérifié par une
seconde capture : le personnage est visible, debout devant le trône,
dès `t=0`.

## Limites assumées

- Pas de marche (le personnage démarre déjà debout devant le trône,
  scope volontairement resserré — l'utilisateur a validé "trône +
  couronne comme objets 3D", pas une cinématique d'approche complète).
- Couronne tenue "à plat" (rotation identité) pendant tout le portage à
  la main plutôt que vrillée avec le bras — choix esthétique assumé,
  pas un oubli (voir section "change de parent").
- Le lecteur HTML dessine tout en boîtes (y compris les `Ball`/
  `Cylinder` du trône et de la couronne) — limite du renderer de
  prévisualisation, pas du fichier livré, qui porte la vraie `Shape`.

## Commandes

```bash
source ../r6_aerial_kick_combo/.venv/bin/activate   # venv partagé (numpy, bpy)
cd scripts
python3 calibrate.py          # vérifie hanche/mains/pieds contre la géométrie
python3 run_scene.py          # exporte character/throne/crown .rbxmx + sanité structurelle
python3 resolve_rbxmx.py ../output/character_sit_and_crown.rbxmx   # round-trip moteur
python3 compute_crown_track.py                          # trajectoire couronne -> JSON
SCENE_OUT=/tmp/throne_scene_data.json python3 dump_scene_data.py   # data du lecteur HTML
```
