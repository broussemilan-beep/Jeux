# Direct du droit — deux personnages, caméra chorégraphiée (R6, Roblox)

Prototype isolé, sans lien avec RANK ZERO ni MyAnimeRPG — même isolation
que les autres prototypes de `experiments/`, dont celui-ci **réutilise
telle quelle** l'infrastructure de rig déjà vérifiée (`r6_rig.py`,
`anim_engine.py` — version avec « secondary motion » recréée dans
`r6_throne_crown`, voir plus bas —, `export_kfseq.py`,
`resolve_rbxmx.py`, le rig `RigR6.rbxmx` importé depuis GitHub — voir
`rig/PROVENANCE.md`, provenance identique aux autres prototypes).

## Demande

Référence envoyée : un GIF d'un jeu Roblox (type jeu de combat) montrant
un personnage qui charge et assène un « Directional Punch » sur un
mannequin d'entraînement, avec un changement de cadrage juste avant
l'impact et un flash façon manga au contact. Demande explicite : « crée
une animation avec texturing décorés etc où le perso fais ça avec
changement de cam etc fais du niveau expert. »

Différence structurelle avec les prototypes précédents de ce dossier :
**deux rigs R6 indépendants** sur la même chronologie (l'attaquant et le
mannequin), pas un seul acteur — et une **caméra chorégraphiée** (plans
authored, coupes franches), pas un azimut choisi par l'utilisateur.

**Retour de correction** (deuxième itération) : « c bcp trop rapide on
ne lit pas assez les mouvement y'a pas de logique le perso est censé
charge son poing. » La première version tenait toute la charge en
0,15 s — largement illisible en mouvement, même si chaque pose isolée
était correcte. Deux changements :
1. **Rythme entièrement retravaillé** : la charge dure maintenant
   ~1,45 s (`WINDUP_T` → `IMPACT_T`, contre 0,15 s), avec deux
   battements de « respiration » intermédiaires (le buste/bras
   oscillent légèrement plutôt que de tenir une pose figée) et un
   dernier resserrement juste avant le lâcher — la scène entière passe
   de 1,25 s à 3,05 s. Le coup lui-même **reste brusque** (0,20 s,
   `COIL_T` → `IMPACT_T`) : le principe d'animation « lent à l'approche,
   rapide dans l'action » n'est pas remis en cause, seule l'approche
   était trop courte pour se lire.
2. **Signal visuel de charge sur le poing** (`drawFistCharge()`) : un
   halo qui croît avec le temps de charge (0 à `COIL_T`), avec un pouls
   qui s'accélère en approchant du lâcher et des filaments d'énergie
   convergents — jusque-là, la charge ne se lisait que dans la pose du
   corps, pas dans le poing lui-même.

## Ce qui est livré

- `output/character_attacker_punch.rbxmx` — `KeyframeSequence` de
  l'attaquant (rig R6 réel, 6 segments rigides, aucun coude/genou). 93
  keyframes, 3,05 s à 30 Hz.
- `output/character_dummy_reaction.rbxmx` — `KeyframeSequence` du
  mannequin (même rig, même durée) : attente → choc → recul → hébété.
- Lecteur HTML (place d'entraînement texturée, deux rigs synchronisés,
  caméra à cinq plans, flash impact-frame) :
  https://claude.ai/code/artifact/75d33237-0619-46d5-a7f5-cc39768a1406

Pas de `Model` de décor livré : la place d'entraînement (sol, mur en
ruine) est une **mise en scène du lecteur uniquement** — voir sa note
dédiée plus bas.

## Chorégraphie de l'attaquant

Neuf keyframes (`scripts/choreography.py`, fonction `attacker_punch()`) :

1. **Garde** (0,00 s → `GARDE_T`=0,35 s, pose tenue — deux keyframes
   identiques, vrai plat) — buste légèrement penché en arrière, poings
   hauts, appui décontracté.
2. **Transition vers la charge** (→ `WINDUP_T`=0,75 s) — le buste se
   torsade en arrière (`Torso` Y négatif — voir la section axes plus
   bas), le poing se ramène près du corps : c'est la mise en tension
   avant le coup, pas un simple recul du bras.
3. **Charge, deux battements de respiration** (`CHARGE_A_T`=1,20 s,
   `CHARGE_B_T`=1,65 s) — le buste/bras oscillent légèrement (torsion
   ±3°, léger jeu du poignet) plutôt que de tenir une pose parfaitement
   figée — un effort soutenu, pas une pause.
4. **Resserrement final** (`COIL_T`=2,00 s) — le poing se resserre
   encore, buste au maximum de la torsion arrière : le dernier
   battement avant le lâcher.
5. **Impact** (`IMPACT_T`=`COIL_T`+0,20 s=2,20 s — brusque, pas une
   transition lente) — le buste se détord vers l'avant (`Torso` Y
   positif), le bras s'étend, la racine avance (`LUNGE_Z`, un vrai pas
   dans le coup, pas juste un bras qui s'allonge). **Ce keyframe
   synchronise exactement avec la première réaction du mannequin.**
6. **Suite** (+0,40 s) — retour partiel de garde ; le buste/bras
   « vibrent » légèrement avant de se stabiliser (secondary motion, voir
   plus bas), pas un arrêt sec.
7. **Posture finale** (+0,85 s) — garde reprise, léger pas de recul.

## Chorégraphie du mannequin

Six keyframes (`dummy_reaction()`) : attente immobile jusqu'à
`IMPACT_T` (racine tournée à 180° — face à l'attaquant, voir la section
axes), puis un whiplash **quasi instantané** (0,03 s — une réaction lente
lirait comme « il a vu venir le coup »), un recul (la racine s'éloigne de
l'attaquant), puis une pose hébétée tenue jusqu'à la fin.

## Sémantique des axes — vérifiée par calcul isolé, pas supposée

Avant d'écrire la chorégraphie, deux points non couverts par les
prototypes précédents ont été vérifiés numériquement (voir le script
isolé utilisé, reproductible via `python3 -c` avec `anim_engine`) :

- **Torso Y (torsion)** : `Y` positif fait pivoter **l'épaule droite vers
  l'avant** (-Z). C'est ce signe qui porte la mécanique d'un direct du
  droit : `Y` négatif = buste armé en arrière (charge), `Y` positif =
  buste qui « tire » le poing en avant (relâchement de la charge dans le
  coup) — mesuré sur une pose isolée (Torso Y=±30, bras neutre), pas
  déduit par analogie avec un autre prototype.
- **`HumanoidRootPart` Y=180°** : retourne le personnage, « devant »
  devient +Z au lieu de -Z — utilisé pour que le mannequin (positionné
  loin en -Z) fasse face à l'attaquant plutôt que lui tourner le dos.

## Le contact n'est pas pixel-parfait — calibré par balayage numérique

Un premier essai (bras à X=100°, buste penché 22°, avancée modeste)
plaçait le poing à **2,8 studs** du torse du mannequin au moment de
l'impact — mesuré, pas supposé, exactement le genre d'écart qu'un
œil ne détecte pas sur une pose isolée mais qui saute aux yeux en
mouvement. Un balayage numérique (`calibrate.py` + un script de sweep
isolé, angle du bras × inclinaison du buste × avancée du pas, ~200
combinaisons évaluées par cinématique directe réelle) a trouvé une
configuration à **0,62 stud** d'écart — bras à X=65° (pas 100° : au-delà
de 90°, l'axe du bras monte vers l'aisselle plutôt que de rester à
hauteur du torse, une vraie limite géométrique du rig, même famille que
les limites déjà rencontrées dans `r6_divine_orb`), buste penché 16°
(pas 22°), et une avancée de pas plus profonde (`LUNGE_Z`=-5,40). Le
reste de la lecture du coup (recul et vacillement du mannequin, flash
impact-frame, coupe caméra) fait le travail de vendre le contact — même
esprit que les petits écarts assumés des prototypes précédents (couronne
sur la tête, boule au-dessus de la main).

## Secondary motion — recréée localement (voir `r6_throne_crown`)

Même technique que le tour précédent sur le trône : Cascadeur (ou tout
autre outil équivalent) n'est pas disponible dans ce sandbox (pas de
GPU, pas de clé d'API — voir le worklog de session), donc son idée
centrale (un mouvement qui poursuit sa cible avec retard + dépassement +
stabilisation) est recréée en Python pur
(`anim_engine._spring_chase()`, copié tel quel depuis `r6_throne_crown`).
Appliquée ici :

- **Attaquant** : `Torso` et `Right Arm` chassent leur cible à partir de
  `IMPACT_T` (`ATTACKER_SECONDARY_MOTION`) — le coup « vibre »
  brièvement avant de se stabiliser en garde, plutôt que de s'arrêter
  net.
- **Mannequin** : `Torso` et `Head` chassent leur cible à partir de
  `IMPACT_T` (`DUMMY_SECONDARY_MOTION`, ressort plus mou/plus amorti —
  un corps qui encaisse un choc, pas un poing qui frappe) — le
  vacillement lit comme un vrai transfert de poids, pas une pose figée.

## Caméra chorégraphiée — pas laissée libre à l'utilisateur

Contrairement aux prototypes précédents (azimut réglable par
l'utilisateur via des boutons), la caméra de ce lecteur est **authored**
(`SHOTS` dans `directional_punch_viewer.html`) : cinq plans avec des
**coupes franches** entre eux (pas de fondu), chacun avec son propre
mouvement interne (recadrage lent pendant le plan, ease-out) :

1. **Large** (0,00-`WINDUP_T`=0,75 s) — plan d'ensemble, les deux
   personnages face à face, le temps de lire la garde.
2. **Approche** (`WINDUP_T`-`IMPACT_T`, ~1,45 s — un seul plan continu
   pendant TOUTE la charge, pas de coupe) — cadrage resserré qui pousse
   lentement vers le mannequin à mesure que l'attaquant charge (même
   esprit que le changement de cadrage de la référence GIF), assez long
   pour lire le halo de charge qui grossit sur le poing.
3. **Impact** (`IMPACT_T`+0,12 s) — plan serré au moment du choc, tenu
   pendant le flash.
4. **Réaction** (+0,12 à +0,65 s) — coupe sur un angle bas dramatique
   pour le recul du mannequin.
5. **Plan final** (+0,65 s → fin) — retour à un plan large, posture
   assurée de l'attaquant.

C'est un choix de réalisation **de ce lecteur**, pas une donnée des
fichiers livrés : les deux `KeyframeSequence` n'ont aucune notion de
caméra (Roblox n'associe pas de caméra à un `KeyframeSequence` de
personnage), celle-ci reste à faire côté script client dans un vrai
projet.

## Bug trouvé par capture d'écran, pas par les nombres — encore une fois

Même leçon que tous les prototypes précédents. Premier essai du lecteur
avec la caméra à ancre mobile (`CAM.tz`/`CAM.ty`, nécessaire pour les
coupes de plan — les lecteurs précédents avaient une caméra fixe à
l'origine) : **les deux personnages étaient complètement invisibles**,
seuls le sol et le mur texturés s'affichaient. La vérification numérique
(`calibrate.py`) ne pouvait pas détecter ce bug — les positions/rotations
calculées étaient correctes, c'est le *rendu* qui était cassé.

Cause trouvée en inspectant directement l'état de la page (position
écran du buste de l'attaquant, correcte et dans le cadre) puis le test
de culling des faces : `proj()` avait été modifiée pour soustraire
l'ancre de la caméra (nécessaire pour une POSITION), mais restait
utilisée telle quelle sur les **normales de face** (une DIRECTION, pas
une position) pour décider quelles faces d'une boîte sont visibles —
soustraire une ancre a des dizaines de studs d'une direction unitaire la
corrompt complètement, donc le test `d >= 0` rejetait ou acceptait des
faces au hasard selon l'ancre courante. Corrigé en séparant les deux
usages : `proj()` (position, avec ancre) reste pour placer les sommets à
l'écran, une nouvelle `projDirDepth()` (rotation SEULE, sans ancre) sert
au test de culling des normales. Aucun des lecteurs précédents n'avait ce
bug car leur caméra n'avait pas d'ancre mobile — c'est cette itération,
en introduisant les coupes de plan, qui l'a fait apparaître.

## Texturing décoré — vraies images, pas des teintes plates

`scripts/gen_textures.py` génère deux textures PNG seamless (sommes
d'ondes sin à fréquences ENTIÈRES sur la largeur/hauteur de l'image —
seamless par construction, pas par un flou de bord approximatif ; RNG
seedé — déterministe, reproductible à l'identique) :

- `stone_ground` — dallage de pierre (grille de dalles + mouchetis de
  bruit).
- `ruin_wall` — mur de pierre usé (bandes de blocs + fissures éparses).

Contrairement au trône/couronne, ces textures ne sont **pas** destinées
à un `Material` Roblox sur un `Part` exporté : la place d'entraînement
n'existe dans aucun des deux fichiers livrés (ce sont deux
`KeyframeSequence` de personnage, pas une `Model` de décor), donc pas de
pipeline `SurfaceAppearance`/`MeshPart` ici — juste des PNG embarqués
tels quels dans le HTML (`build_viewer.py`, même mécanisme que
`r6_throne_crown`), avec une ligne d'horizon nette entre les deux (trouvé
par capture d'écran : sans elle, mur et sol se confondaient en une seule
masse grise illisible).

## Le poing charge visiblement — retour utilisateur explicite

Ajouté en réponse au retour « le perso est censé charge son poing » :
`drawFistCharge()` dessine un halo chaud (rouge/orange, un poing qui
chauffe — même famille visuelle que les filaments d'énergie de
`r6_divine_orb`, mais colorée différemment pour un coup de poing plutôt
qu'une invocation) autour de la main droite, actif de `WINDUP_T` à
`IMPACT_T` :

- **Intensité** : croît linéairement avec le temps de charge (0 à 1 sur
  `WINDUP_T` → `COIL_T`), pas un simple on/off.
- **Pouls** : une oscillation sinusoïdale dont la fréquence
  s'**accélère** en approchant du lâcher (2 Hz au début, jusqu'à 5,5 Hz
  juste avant `COIL_T`) — lit comme une tension qui monte.
- **Filaments convergents** : leur nombre croît aussi avec l'intensité
  (3 au début, jusqu'à 9 au maximum) — le poing « aspire » de plus en
  plus d'énergie à mesure que la charge progresse.

Déterministe (toutes les variations dérivées de `sin(t * constante)`,
jamais `Math.random()`) — comme partout ailleurs dans ce dossier, une
capture répétée au même instant est identique.

## Flash impact-frame façon manga

Deux temps, comme la référence GIF (un coup de théâtre en noir/blanc,
pas une jauge de dégâts progressive) : un flash blanc plein cadre
(0,035 s, « le choc aveugle l'image une frame »), puis des traits de
vitesse noirs qui rayonnent depuis le point de contact réel (la main de
l'attaquant à cet instant, pas un point fixe — reste cohérent si on
scrobble hors de `IMPACT_T`), densité décroissante sur 0,085 s.
Déterministe (angles/longueurs dérivés de `sin(i * constante)`, jamais
`Math.random()`) — une capture répétée au même instant est identique, un
tremblement de caméra bref (`shakeOffset`, même technique que
`r6_divine_descent`) accompagne le flash.

## Rig des deux personnages

Même rig R6 vérifié (dépôt Adonis, licence MIT) que les autres
prototypes de ce dossier — voir `rig/PROVENANCE.md`.

## Commandes

```bash
cd scripts
source ../../r6_aerial_kick_combo/.venv/bin/activate

# Verification numerique (portee du coup, synchronisation, structure)
python3 calibrate.py

# Genere les textures (sol, mur)
python3 gen_textures.py

# Exporte les deux KeyframeSequence (+ verification structurelle)
python3 run_scene.py

# Assemble le lecteur HTML final (textures + donnees de scene injectees)
python3 build_viewer.py
```
