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

## Rendu WebGL réel (Three.js) — remplace le Canvas2D à plat

Retour direct de l'utilisateur, sans détour : *« Ton rendu est nul comparé
à des animateurs experts et qui font de la vrai animation pk »*. Question
posée en retour (`AskUserQuestion`) pour savoir quel levier pesait le
plus — rendu à plat ou animation mécanique — réponse : **les deux**, avec
la séquence explicitement choisie par l'utilisateur : *rendu 3D d'abord
(impact immédiat sur tout), puis reprise du mouvement scène par scène*.
Ce prototype est celui sur lequel le premier étage (rendu) est fait.

**Avant** (toutes les captures de ce README jusqu'ici) : projection
orthographique maison (`proj()`/`boxQuads()`), flat-shading un seul terme
diffus + un terme spéculaire grossier, pas d'ombres portées, pas de
brouillard de profondeur — un rendu peint à la main, honnête sur ce qu'il
est mais visuellement plat comparé à un vrai moteur 3D.

**Après** : une vraie scène [Three.js](https://threejs.org/) (r134, MIT) —

- `THREE.WebGLRenderer` avec `shadowMap` activé (`PCFSoftShadowMap`),
  tone mapping ACES Filmic ;
- une lumière directionnelle clé avec ombres portées réelles (remplace
  le terme diffus/spéculaire peint à la main) + un remplissage
  hémisphérique doux + une lumière de contre-jour chaude ;
- un dôme de ciel dégradé (sphère à couleurs de sommet, horizon chaud →
  zénith sombre — déterministe, aucune texture externe) dans lequel se
  noie un vrai `THREE.Fog` (profondeur de champ atmosphérique, chose
  qu'une projection orthographique ne peut pas rendre) ;
- sol et mur en `MeshStandardMaterial` texturés (mêmes PNG générés par
  `gen_textures.py`, désormais tuilés via `RepeatWrapping` plutôt que
  peints quad par quad) avec ombres reçues ;
- les deux rigs sont 12 vrais `THREE.Mesh` (`BoxGeometry` aux tailles
  réelles du rig + `MeshStandardMaterial`), position et rotation MONDE
  appliquées telles quelles depuis les données déjà résolues par le
  moteur (`resolve_rbxmx.py`) — aucun changement côté pipeline Python,
  seul le rendu client change.

Les VFX plein-écran (halo de charge, flash impact-frame) restent en
Canvas2D, sur un second `<canvas>` transparent empilé par-dessus le canvas
WebGL (`pointer-events:none`) — c'est le bon outil pour un effet façon
manga en surimpression d'écran, un remplacement en particules 3D n'aurait
rien apporté. Le point de contact à l'écran utilisé par ces VFX est
désormais projeté par la vraie caméra (`camera.project()`), plus une
projection orthographique maison.

### `cdnjs.cloudflare.com` est bloqué dans ce bac à sable — bibliothèque vendorisée

Pas de `<script src="https://cdnjs...">` possible ici : le proxy sortant
du bac à sable renvoie `403` sur ce host (`CONNECT tunnel failed`).
`registry.npmjs.org`, lui, est directement joignable (liste `noProxy` du
proxy) — la bibliothèque a donc été récupérée via
`https://registry.npmjs.org/three/-/three-0.134.0.tgz`, extraite du
tarball npm (`package/build/three.min.js`) et vendorisée telle quelle
dans `scripts/vendor/three.min.js` (615 Ko, MIT). `build_viewer.py`
l'injecte désormais dans le HTML final via un troisième point de
substitution `__THREE_JS__`, au même titre que `__SCENE_DATA__` et
`__TEXTURES_B64__` — le fichier livré reste 100% autonome (pas de
dépendance réseau au chargement), et le rend testable en local via
Playwright sans dépendre d'un CDN externe.

### Caméra chorégraphiée : réinterprétée en position sphérique réelle

La table `SHOTS` (mêmes 5 plans, mêmes coupes franches, même minutage
qu'avant) est maintenant interprétée comme une vraie `PerspectiveCamera`
positionnée en coordonnées sphériques (`az`/`el`/distance) autour d'une
cible, plutôt qu'une rotation appliquée après-coup à une projection
orthographique. Deux problèmes de perspective réelle, absents en
orthographique, ont été trouvés **par capture d'écran** (encore une fois
— la discipline numérique seule ne les aurait jamais révélés) :

1. **Le zoom orthographique (`scale`) ne se traduit pas en distance de
   caméra sans risque.** À `scale≈1.78` (fin du plan « approche »), une
   distance caméra-cible naïve (`BASE_DIST / scale`) plaçait la caméra à
   moins de 2 studs du torse — en perspective réelle ça donne un pan de
   torse plat et illisible plein cadre, pas un zoom serré lisible. Fixé
   par un garde-fou mesuré, pas un réglage à l'oeil : à chaque frame, la
   distance caméra-cible authored est comparée à la distance réelle
   caméra→torse le plus proche (attaquant OU mannequin) et la caméra est
   repoussée le long du même rayon si elle est plus proche que
   `MIN_SUBJECT_DIST` (6,5 studs — calé sur la distance du plan « impact »
   qui, lui, se lisait bien).
2. **L'azimut de fin du plan « approche » plaçait la caméra quasi pile
   dans le dos de l'attaquant.** Rien à voir avec la distance : même
   correctement reculée, une caméra alignée dans l'axe Z du personnage ne
   montre qu'une masse plate de dos, aucune lecture du bras qui charge.
   Fixé en resserrant l'arc d'azimut du plan (`-32° → -22°` au lieu de
   `-30° → -8°`) pour rester sur un angle 3/4 lisible tout au long du
   zoom, au lieu de converger vers l'axe pur.

Captures de vérification (5 plans, après les deux correctifs ci-dessus) :
`captures/verification/2026-09-03-directional-punch-webgl-plan-large.png`,
`-plan-approche.png`, `-impact.png`, `-reaction.png`, `-plan-final.png`.

## Exagération de la charge/lacher — mesurée contre un pack premium, pas à l'oeil

Suite au retour rendu (rendu 3D d'abord, ci-dessus), deuxième retour sur
l'animation elle-même : *"ça manque d'exagération"*, avec un pack
d'animation de combat premium fourni en référence
(`battleground_animation_pack_v1.0.1.rbxm`). Plutôt que d'ajuster les
poses à l'oeil, la démarche a été la même que partout ailleurs dans ce
projet : **mesurer** — écrire un lecteur du format binaire `.rbxm`
(`experiments/_shared/rbxm_reader.py`, voir son README pour la méthode de
validation) et en extraire les amplitudes de rotation réelles d'une
séquence de combo comparable ("M1_1", un direct de base) :

| segment | pack premium (mesuré) | ici, avant ce passage |
|---|---|---|
| Bras droit | ~178° | ~65° |
| Torse (torsion) | ~99° | ~38° |
| Tête | ~88° | ~15° |

Un facteur ~2,5-3× d'écart, confirmé par le calcul plutôt que supposé.

**Ce qui a été poussé** — uniquement la CHARGE (`WINDUP_*`/`CHARGE_A_*`/
`CHARGE_B_*`/`COIL_*`), qui n'a aucune contrainte de contact (le poing est
en l'air) : torsion du buste au coil `-34°→-56°`, bras armé jusqu'à
`(-22,0,-52)` (contre `(0,0,-15)` avant — le bras part maintenant
franchement en arrière plutôt que de rester devant le corps), tête qui
part en arrière plus loin. **Ce qui n'a volontairement PAS bougé** :
`STRIKE_TORSO`/`STRIKE_HEAD`/`STRIKE_RIGHT_ARM`/`LUNGE_Z` à `IMPACT_T` —
le seul instant mesuré et calibré au stud près (`calibrate.py`, 0,62 stud
d'écart, vérifié identique avant/après ce passage) ; un gain d'amplitude
qui aurait cassé ce contact ne valait pas le coup.

**Follow-through ajouté** : le coup ne s'arrête plus net à `IMPACT_T` — une
nouvelle pose `OVERSHOOT_*` à `IMPACT_T + 0.06s` pousse légèrement
au-delà du point de contact (buste/bras continuent leur élan) avant que
`RECOVER_*` (lui aussi creusé plus loin en arrière) ne ramène le
personnage. Principe d'animation classique ("le mouvement dépasse sa
cible avant de revenir"), jusqu'ici absent de cette scène. Le
spring-chase de secondary motion qui suit (`ATTACKER_SECONDARY_MOTION`)
a aussi été redosé (`damping_ratio` 0.55→0.40 sur le buste, 0.6→0.45 sur
le bras) pour qu'il se lise comme un vrai rebond après ce grand geste,
pas un simple amortissement plat.

Vérifié : `calibrate.py` (écart de contact inchangé, synchronisation,
structure), captures d'écran à la charge maximale, juste après le flash
d'impact (le follow-through est visible), et à la réaction —
`captures/verification/2026-09-03-directional-punch-exaggeration-coil.png`,
`-overshoot.png`, `-reaction.png`.

## Charge repensée en accroupissement coilé — 3 images de référence

Troisième retour sur cette scène, avec trois images cette fois (pas de
texte) : *"L'animation en gros elle doit plus exagérer, le perso doit
commencer comme sur l'image 1, puis impact frame image 2, et finir comme
sur l'image 3"*. Image 1 : un combattant accroupi très bas, buste cassé
loin vers l'avant, bras croisés serrés devant la poitrine, lumière au sol.
Image 2 : un impact-frame façon manga, traits de vitesse noirs plein
cadre. Image 3 : un poing en pleine extension façon One Punch Man, avec
des éclats de pierre qui explosent autour.

**Contrainte de rig incontournable, vérifiée par le calcul avant tout
choix de pose** : dans ce rig R6 (comme dans le vrai rig Roblox), les
jambes sont enfants du `Torso` via Motor6D (mêmes `Right Hip`/`Left Hip`
que `Right Shoulder`/`Left Shoulder`) — leur rotation MONDE est donc la
composition torse × jambe, pas une rotation indépendante à la hanche.
Pencher le torse de 42° vers l'avant sans y penser fait suivre les jambes
du même angle, ce qui aurait envoyé les pieds dans les airs. Un balayage
numérique (pas à l'oeil, voir la sortie de `calibrate.py` et le script de
vérification dans le commit) a cherché les rotations LOCALES de jambe qui,
composées avec chaque étape de l'inclinaison du torse, ramènent les DEUX
pieds à une hauteur quasi identique (< 0,1 stud d'écart) — une racine
abaissée de ~0,3 stud (`COIL_ROOT_Y = 2.70` contre `GROUND_Y = 3.0`)
associée à cette inclinaison est la meilleure approximation d'un
accroupissement bas qu'un rig SANS GENOU (contrainte non négociable du
projet) puisse offrir sans que les pieds flottent ou traversent le sol.

**Ce qui a changé** : toute la charge (`WINDUP_*` → `CHARGE_A_*` →
`CHARGE_B_*` → `COIL_*`) — auparavant un buste qui se penche en ARRIÈRE
(un "arc qu'on bande"), désormais un buste qui se CASSE EN AVANT avec les
DEUX bras qui se croisent devant la poitrine (`Left Arm` était figé sur la
garde pendant toute la charge avant ce passage — il anime maintenant lui
aussi) et une racine qui descend progressivement. Au lâcher (`IMPACT_T`),
le buste/bras/racine remontent et repartent en avant d'un coup — une
vraie détente de ressort, pas juste une rotation qui se déroule. Le
contact calibré à `IMPACT_T` (0,62 stud) reste, comme toujours,
strictement inchangé.

**Follow-through poussé plus loin** (pose "image 3") : `OVERSHOOT_TORSO`
55° (était 40°), `OVERSHOOT_RIGHT_ARM` X=85° (était 72°) — puisqu'aucune
contrainte de contact ne s'applique à cette pose (elle existe 0,06s après
`IMPACT_T`), rien n'empêche de la pousser vers l'engagement total façon
One Punch Man.

**VFX rendues plus exagérées** : le flash impact-frame (image 2) est
étendu — 26→38 traits de vitesse, portée et durée accrues (0,12s→0,16s).
Nouveauté, `drawDebrisBurst()` : des éclats de pierre anguleux (polygones
irréguliers à 5 sommets, pas des étincelles rondes) partent du point de
contact en trajectoire balistique (vitesse initiale + gravité simple) et
tournent en volant, ~0,55s de vie, chevauchant le follow-through et le
début du recul — référence directe à l'image 3. Déterministe comme
toujours (angle/vitesse/taille dérivés de `sin(i * constante)`, jamais
`Math.random()`).

Vérifié : grounding numérique des pieds à chaque étape de la charge
(écart < 0,1 stud), `calibrate.py` (contact/synchronisation/structure
inchangés), captures à la charge, juste après le flash (débris visibles),
au recul (débris qui continuent de voler) et au follow-through —
`captures/verification/2026-09-03-directional-punch-crouch-charge.png`,
`-impact-debris.png`, `-recover-debris.png`, `-overshoot.png`.

### Correction : le poing chargé va à l'arrière, pas croisé devant le torse

Retour direct sur l'image 1 de la référence ci-dessus : *"le perso charge
son poing à son arrière droit"* — première lecture fausse de ma part, le
`COIL_RIGHT_ARM` précédent (`(65, 0, -70)`) ramenait le poing vers l'avant/
en travers du torse, pas derrière la hanche comme sur l'image. Corrigé :
le `Right Arm` part maintenant en ARRIÈRE du corps sur toute la charge
(X négatif — même convention qu'ailleurs : X positif = avant-puis-au-dessus,
X négatif = arrière), `COIL_RIGHT_ARM = (-115, 0, -18)` au plus profond ;
le `Left Arm` reste devant, en garde. Vérifié par calcul (pas à l'oeil) :
à `COIL_T`, le poing se retrouve à `(0.36, -0.18, +2.07)` studs relatifs à
la racine — proche de la hauteur de la hanche (`Y≈-0.18`), et derrière le
corps (`Z` positif = arrière, convention établie dès le début de ce
prototype). `STRIKE_RIGHT_ARM`/`IMPACT_T` — le lâcher lui-même —
inchangés, contact calibré toujours à 0,62 stud. Capture (vue de côté
manuelle, la caméra chorégraphiée par défaut cadre trop serré à cet
instant pour bien lire le bras) :
`captures/verification/2026-09-03-directional-punch-poing-arriere-droit.png`.

## Chaîne cinétique du lâcher — recherché avant de refaire, pas réajusté à l'oeil

Retour direct : *"tu utilise pas le corps dj peros, va te renseigner sur
l'animation et l'animation Roblox comment bine faire etc etc et refais ce
que je te dmd"*. Pris au mot : recherche (biomécanique du coup de poing +
principes d'animation + pratiques Roblox) avant toute nouvelle valeur de
pose, plutôt que retoucher les chiffres à l'instinct comme les passages
précédents.

**Ce que la recherche établit** (sources en bas de section) :
- Un coup de poing est une **chaîne cinétique séquentielle**, pas un bloc
  rigide qui pivote d'un coup : la vitesse de rotation des hanches
  atteint son maximum AVANT celle des épaules, qui atteint son maximum
  AVANT celle du bras. Le bras est en retard, puis "fouette" pour
  rattraper.
- Les jambes et le tronc fournissent ~76% de la puissance d'un coup
  (39% jambes + 37% tronc) contre ~24% pour le bras seul — le
  transfert de poids (pied arrière qui pivote, ~60% du poids qui bascule
  sur le pied avant) est donc au moins aussi important visuellement que
  le geste du bras.
- Contrapposto (hanche qui monte / épaule qui descend côté porteur) est
  ce qui vend le transfert de poids dans une pose fixe.

**Le défaut réel de la choré précédente** : `Torso`, `Right Arm` et les
jambes partageaient TOUS les mêmes keyframes `COIL_T`→`IMPACT_T` — tout
bougeait en même temps, au même rythme, comme un seul bloc. Exactement le
contraire de la chaîne cinétique ci-dessus, et exactement ce que "tu
n'utilises pas le corps" décrit.

**Correction** : une keyframe intermédiaire `HIP_DRIVE_T` (`COIL_T +
0,08s`, 40% du lâcher) où le buste/les jambes/l'avancée de la racine ont
DÉJÀ parcouru l'essentiel du trajet vers la pose `STRIKE_*`, mais le bras
droit est encore presque entièrement armé. Vérifié par le calcul, pas à
l'oeil (le buste peut sembler "déjà arrivé" sur une capture sans mesure) :
à `HIP_DRIVE_T`, le buste a parcouru **86%** de sa rotation totale
(`COIL_T`→`IMPACT_T`) contre **17%** pour le bras droit — l'écart net
entre les deux confirme que la séquence hanches-avant-bras existe
vraiment dans les données, pas seulement dans l'intention. `IMPACT_T`
lui-même reste numériquement identique (0,62 stud, revérifié).

Captures à `COIL_T`/`HIP_DRIVE_T`/`IMPACT_T` (vue de côté manuelle, même
raison que ci-dessus) :
`captures/verification/2026-09-03-directional-punch-kinetic-chain-coil.png`,
`-hipdrive.png`, `-impact.png`.

Sources : [The Science Behind Powerful Punches](https://www.getphysical.com/blog/science-behind-powerful-punches),
[The Kinetic Chain — Built Not Born](https://www.builtnotborn.co.uk/blog/the-kinetic-chain),
[Principles of Animation Physics (Animator Island)](https://www.animatorisland.com/principles-of-animation-physics-part-4/),
[The Right Cross – Boxing Heavy Artillery](https://www.myboxingcoach.com/how-to-throw-a-right-cross/),
[Master the Boxing Pivot](https://www.myboxingcoach.com/master-the-boxing-pivot-boxing-techniques-for-versatility/).

## Accroupissement anime remplacé par un plié de jambes lisible

Retour direct, après la chaîne cinétique ci-dessus : *"tu oublies
d'utiliser les jambes, le perso est censé tourner son buste vers la
droite [pour] charger son poing droit, plier les jambes légèrement, le
2e bras placé, et boum il envoie"*.

**Le vrai problème n'était pas qu'il manquait du mouvement de jambes**
(il y en avait, voir la section accroupissement plus haut) **— c'est que
ce mouvement ne se LISAIT pas.** Le buste penché à 42° vers l'avant
(pose façon anime, cf. les 3 images de référence plus haut) exigeait une
compensation numérique lourde sur les jambes pour garder les pieds au
sol (jambes = enfants du Torso, voir plus haut) — cette compensation les
ramenait quasiment à la verticale à l'écran, donc elles se lisaient comme
"droites" malgré une vraie rotation locale non nulle dans les données.

**Corrigé en simplifiant, pas en ajoutant** : le buste penche désormais
beaucoup moins vers l'avant (`COIL_TORSO` X : 42°→13°) — la TORSION
(Y : -32°, "tourner vers la droite" pour charger le poing droit) redevient
le mouvement dominant et lisible, plutôt que noyée sous un penché extrême.
Avec moins d'inclinaison à compenser, une simple rotation locale des deux
jambes vers l'avant (`COIL_LEGS` : `Right Leg (20°,·,15°)`,
`Left Leg (24°,·,-12°)`) suffit à se lire comme un plié de genou visible
à l'écran, sans compensation lourde — vérifié à nouveau par le calcul
(pieds à 0,02–0,20 stud du sol sur toute la charge, pas de pied qui
traverse le sol) et confirmé par capture. `HIP_DRIVE_*` (chaîne
cinétique) recalculé contre ces nouvelles poses de charge. `IMPACT_T`
toujours strictement inchangé (contact calibré 0,62 stud).

Captures (vue de côté basse, même raison que les sections précédentes —
le plan chorégraphié par défaut ne cadre pas assez large à cet instant) :
`captures/verification/2026-09-03-directional-punch-jambes-pliees-windup.png`,
`-coil.png`, `-hipdrive.png`, `-impact.png`.

## Le coup part en ligne droite, pas en diagonale depuis le bas

Retour : *"il manque les épaules on dirait que le coup part du bas alors
que il doit aller droit"*.

**Diagnostic** : le `STRIKE_RIGHT_ARM` calibré à l'origine (`X=65`) avait
été trouvé par balayage numérique en minimisant uniquement l'écart de
contact — mais `X=90` est l'horizontale pure (bras droit devant, hauteur
d'épaule ; `X=65` est SOUS l'horizontale, comme partout ailleurs dans ce
fichier, vérifié). Résultat : le poing arrivait en diagonale montante
depuis le bas plutôt qu'en ligne droite depuis l'épaule — exactement ce
que la remarque décrit.

**Corrigé, pas juste ajusté** : nouveau balayage numérique en FIXANT
`X=90` pile (bras parfaitement horizontal) et en ne laissant varier que
l'inclinaison du buste et l'avancée. Résultat inattendu mais net : buste
légèrement penché en ARRIÈRE (`STRIKE_TORSO` X : `+16°` → `-8°`, au lieu
d'un buste penché en avant) donne un écart de contact de **0,366 stud —
meilleur que l'ancien 0,62**, pas un compromis. Un coup plus droit ET
mieux calibré, les deux à la fois. `HIP_DRIVE_*` (chaîne cinétique) et
`OVERSHOOT_*` (follow-through) recalculés contre ce nouveau réglage.

Captures (vue de côté à hauteur d'épaule) :
`captures/verification/2026-09-03-directional-punch-bras-droit-hipdrive.png`,
`-impact.png`, `-overshoot.png`.

## Hitstop, étirement d'impact et "snap" — technique standard d'animation Roblox

Retour utilisateur, cette fois sous forme de spécification technique
précise plutôt qu'une description d'image ou une critique : la
gestion de l'impact dans un rig R6/R15 professionnel suit un rythme
en quatre temps (anticipation lente, lâcher quasi instantané, gel
complet au contact — le *hitstop* —, puis un settle avec overshoot),
et les articulations s'étirent au-delà de l'anatomie normale sur la
frame d'impact pour vendre la force du coup.

**Ce qui est nouveau ici (pas juste retouché)** :

- **Hitstop réel** : à `IMPACT_T`, les DEUX personnages ET la caméra se
  figent pendant `HITSTOP_DUR = 5/30s` (~0,167s, milieu de la fourchette
  usuelle 3-6 frames). Implémenté via une fonction `poseTime(t)` qui
  gèle le temps d'ANIMATION utilisé pour échantillonner les poses/la
  caméra pendant cette fenêtre, puis reprend sans saut (juste retardé) —
  les VFX plein-écran (flash, débris) restent sur le temps réel non
  décalé, donc se déclenchent AU moment du gel, pas après. Vérifié par
  le calcul (pas à l'oeil, script Playwright ponctuel) : la position du
  poing est **bit-identique** à trois instants différents à l'intérieur
  de la fenêtre de hitstop, et change dès la sortie.
- **Étirement d'impact** : le bras droit de l'attaquant s'étire
  (`scale.y` jusqu'à ×1,32) sur ~1 frame au contact puis se relâche sur
  le reste de la fenêtre — ancré à l'épaule (pas un étirement symétrique
  qui ferait flotter l'articulation), donc l'allongement se voit
  surtout côté poing, vers la cible.
- **"Snap" du lâcher** : déjà largement couvert par la chaîne cinétique
  du passage précédent (le bras ne parcourt que ~17% de sa rotation à
  `HIP_DRIVE_T`, l'essentiel se joue dans les dernières 0,12s) — pas
  retouché ici, la mécanique demandée existait déjà.

**Limite honnête, pas cachée** : le hitstop et l'étirement sont des
techniques de LECTEUR (démonstration), pas des données encodées dans le
`KeyframeSequence` livré — le format d'animation Roblox n'a ni notion de
pause temporelle, ni de `Size` animable (seule une `CFrame`/`Pose` l'est).
Un vrai hitstop en jeu se fait côté script, typiquement en mettant en
pause l'`AnimationTrack` (`track:AdjustSpeed(0)` puis
`task.wait(hitstopDur)` puis `track:AdjustSpeed(1)`, ou un `TimeScale`
partagé si plusieurs systèmes doivent geler ensemble) — pas dans
l'animation elle-même.

Captures (gel, étirement, sortie du gel, settle) :
`captures/verification/2026-09-04-directional-punch-hitstop-stretch.png`,
`-mid.png`, `-unfreeze.png`, `-settle.png`.

## Le bras rigide (aucun coude) — diagnostic et techniques de compensation

Retour utilisateur, après toutes les passes précédentes : « malgré tout ce
que tu as tenté tu n'as pas réussi à donner le sentiment d'un coup de
poing... le perso met juste une espèce d'élancement du bras ». Vérifié
en zoomant la caméra manuellement sur le bras au moment du lâcher
(`2026-09-04-directional-punch-rig-no-elbow-diag.png`) : le constat est
juste. `Right Arm` est **une seule Part rigide** reliée au Torso par un
unique `Motor6D` à l'épaule — contrainte dure du rig R6 (voir
`r6_rig.py`), pas un réglage de pose. Sans coude, le bras ne peut
physiquement que tourner comme une règle autour d'un point fixe : aucun
raffinage de timing/exagération/chaîne cinétique ne peut lui faire lire
autrement, quelle que soit la qualité du reste de l'animation.

Deux options posées à l'utilisateur : reconstruire la scène sur le rig
**R15** (coude articulé réel, `UpperArm`/`LowerArm`) — la vraie solution,
mais un chantier bien plus lourd (nouveau rig, provenance/licence à
revérifier, chorégraphie entièrement reprise) — ou rester sur R6 et
pousser les techniques de trompe-l'œil que des jeux Roblox comme *The
Strongest Battlegrounds* utilisent pour vendre un coup qui claque malgré
la même contrainte de rig. Décision utilisateur : rester sur R6.
L'utilisateur a ensuite fait sa propre recherche et fourni une
décomposition détaillée des techniques (animation/caméra/VFX) utilisées
par ces jeux — reproduite ci-dessous, avec pour chaque levier ce qui a
été appliqué dans cette passe.

**Diagnostic concret trouvé en le comparant à la recherche fournie** :
la fenêtre entre la keyframe `HIP_DRIVE_T` (chaîne cinétique) et
`IMPACT_T` durait **0,12 s (~3-4 frames à 30 fps, le `OUT_HZ` de
`dump_scene_data.py`)** — très exactement la « zone à danger 3 à 5
frames intermédiaires » que la recherche identifie comme LA cause
classique de l'effet « pale de moulin » sur un bras rigide : assez de
frames pour que l'œil suive le bloc traverser l'espace, pas assez pour
lire comme un geste voulu. Le lâcher n'avait donc jamais été un vrai
snap, malgré tout le travail sur la pose elle-même.

**1. Suppression du voyage (snap 1-frame).** `HIP_DRIVE_T` recollé
contre `IMPACT_T` à exactement `1/30 s` (au lieu de 0,12 s) — les deux
tombent sur des frames Blender entières adjacentes (65 et 66 à 30 fps,
vérifié par calcul, pas approximé). Le « runway » où le buste/les
jambes/la racine font l'essentiel du travail (chaîne cinétique) s'étend
donc maintenant sur `COIL_T -> HIP_DRIVE_T` (0,167 s, ~5 frames,
largement lisible), et il ne reste plus qu'UNE frame de sortie entre le
bras encore quasiment armé et le bras en pleine extension — le cerveau
comble le vide plutôt que de voir le bras voyager. Fractions recalculées
(script, pas à l'oeil) : buste/tête/jambes/racine à 92% du trajet
`COIL_*->STRIKE_*`, bras gauche (garde) à 85%, bras droit (le coup) à
seulement 20% — il reste le payload du snap final. `IMPACT_T` et tous
les `STRIKE_*` restent NUMÉRIQUEMENT INCHANGÉS : `calibrate.py`
reconfirme le même écart de contact, 0,366 stud, à la troisième
décimale près.

**2. FOV-snap et coupe basse au contact (caméra).** Un zoom optique
quasi instantané (`fovAt()`, 42°→33° en ~1 frame puis retour élastique
avec léger dépassement, sur toute la fenêtre du hitstop) — écrase la
perspective au moment du contact, indépendamment du travelling/shake
déjà en place. Le plan « impact » lui-même passe d'une élévation quasi
neutre (9°) à une légère contre-plongée (-5°) — l'angle de vue s'aligne
davantage avec la ligne de fuite du bras au lieu de le montrer de
profil.

**3. Smear épaule→poing + traînée du poing (VFX, ne touche pas la
pose).** Deux formes 2D dessinées en surimpression pendant la fenêtre du
snap (`drawArmSmear()`), qui ne changent RIEN à la pose 3D en dessous :
un cône translucide effilé (étroit à l'épaule — approximée depuis la
rotation du Torso, voir `shoulderWorld()` — large au poing) qui masque
la silhouette rectangulaire du bras, et une traînée plus fine/plus vive
qui relie la position du poing quelques frames avant le snap à sa
position actuelle, traçant l'arc que le retimage ci-dessus ne laisse
plus le temps à l'œil de reconstituer seul. Vérifié isolément par
capture caméra manuelle (angle 3/4 dégagé, hors chorégraphie caméra du
lecteur) :
`2026-09-04-directional-punch-arm-smear-diag.png` — le bloc rigide est
bien recouvert par la forme dynamique, pas juste dessiné à côté.

**Techniques de la recherche NON appliquées cette passe** (notées pour
une prochaine itération si le résultat reste insuffisant) : le
raccourci de perspective (orienter le bras armé pour qu'il pointe vers
la caméra, le compressant visuellement) demanderait de retravailler
l'azimut caméra du plan "approche" en fonction de l'angle exact du bras
3D — pas fait ici, effet plus incertain/dépendant de l'angle exact que
les trois leviers ci-dessus. Le "broken rig" (léger déboîtement de
l'épaule/translation du Motor6D à l'impact) recoupe largement
l'étirement de bras déjà implémenté (`armStretchFactor`) — pas dupliqué.

Captures : `2026-09-04-directional-punch-snap-pre-1frame.png` (une
frame avant l'impact, bras encore armé + smear visible),
`2026-09-04-directional-punch-snap-reaction.png` (réaction du mannequin
après le nouveau snap).

## Caméra trop proche pendant la charge — la pose ne se lisait plus

Retour utilisateur, immédiatement après la passe snap/smear ci-dessus :
« Direct du droit a un problème sur le début du coup aussi, il donne pas
le give d'un coup chargé ». Vérifié par MESURE directe (pas à l'oeil) :
la distance caméra→torse de l'attaquant, interrogée en direct dans la
page pour chaque instant de la charge, tombait à **6,4-6,5 studs** dès
`CHARGE_B_T`/`COIL_T` — collée contre le plancher anti-clipping
`MIN_SUBJECT_DIST`. En cause : l'ancien plan unique `"approche"`
couvrait toute la charge ET le lâcher (`WINDUP_T -> IMPACT_T`, 1,45 s)
avec un zoom continu de `scale=0.85` à `1.80`, et sa cible (`tz`) visait
un point à mi-chemin vers le mannequin plutôt que l'attaquant lui-même.
Résultat confirmé par capture d'écran : l'image ne montrait plus que des
pans de boîtes flous — la pose censée VENDRE la charge (jambes pliées,
torse tordu, poing armé derrière la hanche) était devenue illisible. Le
problème n'était donc pas la pose ou le timing de la charge (déjà
travaillés sur plusieurs passes précédentes), mais un cadrage caméra qui
la cachait.

Corrigé en scindant l'ancien plan unique en deux plans distincts :
`"charge"` (`WINDUP_T -> COIL_T`, 1,25 s — toute la durée où le corps
doit se lire) à distance modérée et stable (`scale` 0,85→1,05, cible
recentrée sur l'attaquant, `tz` proche de `ATTACKER_Z0`), et `"lacher"`
(`COIL_T -> IMPACT_T`, seulement 0,20 s) qui garde le zoom serré — c'est
là qu'il a du sens, pas étalé sur toute la charge. Reconfirmé après
coup : distance caméra→torse maintenant entre 14 et 19 studs pendant
toute la charge (mesuré, pas supposé), `calibrate.py` inchangé (aucune
pose touchée, seulement la caméra). Capture :
`2026-09-04-directional-punch-charge-camera-fix-after.png`.

## Rig des deux personnages

Même rig R6 vérifié (dépôt Adonis, licence MIT) que les autres
prototypes de ce dossier — voir `rig/PROVENANCE.md`.

## Le poing grimpait du bas vers le haut pendant toute la charge

Retour utilisateur, immédiatement après le recadrage caméra ci-dessus :
« tu fais partir le coup d'en bas pour le monter en haut... il faut que
le buste tourne, la jambe se plie, et que le bras — pas que le poignet —
[reste tenu, ne] parte [pas] du bas ». Vérifié par **trace 3D** de la
trajectoire réelle du poing (`anim_engine.sample` à haute résolution,
pas à l'oeil) : juste — le poing montait de Y=2,25 stud (garde, proche
de la hanche) à Y=3,09 stud (COIL, hauteur d'épaule) de façon CONTINUE
sur toute la durée de la charge (1,25 s). `WINDUP_RIGHT_ARM` restait
proche de la garde relâchée (X=-30, contre X=22 pour `_READY_ARMS`) et
ne rejoignait la hauteur du `COIL` (X=-95) que progressivement via
`CHARGE_A`/`CHARGE_B` — un vrai bras qui se lève lentement, pas un poing
déjà armé.

Corrigé en rapprochant `WINDUP_RIGHT_ARM` de `COIL_RIGHT_ARM` dès
l'entrée en charge (X=-78, au lieu de -30) : le bras "saute" dans sa
position armée dès `WINDUP_T` (0,4 s après la garde — un armement net,
pas une dérive), puis `CHARGE_A`/`CHARGE_B` ne font plus qu'osciller
("respirer") à proximité de cette hauteur déjà haute plutôt que de
continuer à grimper. Retracé après coup : le poing reste maintenant
stable entre Y=2,93 et Y=3,09 stud sur toute la durée de la charge
(contre une ascension continue de 2,25 à 3,09 avant) — c'est désormais
le buste (torsion) et les jambes qui portent la lecture visible de
"charge qui monte en tension", pas le bras. `calibrate.py` reconfirme
l'écart de contact inchangé (0,366 stud) : seules les poses AVANT
`COIL_T` ont changé. Capture :
`2026-09-04-directional-punch-charge-height-fix.png`.

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
