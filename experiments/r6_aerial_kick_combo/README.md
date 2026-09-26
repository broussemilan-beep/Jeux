# Combo aérien R6 — pieds uniquement (prototype isolé)

Test de faisabilité : un enchaînement de coups de pied aériens sur un rig
R6 (Roblox), fortement inspiré arts martiaux réels (croissant/taekwondo,
retourné/spin kick, ciseaux/capoeira), construit via le rig contraint à 6
segments rigides + Motor6D 3-DOF. **Prototype isolé, sans lien avec le
dépôt MyAnimeRPG ni avec le pipeline RANK ZERO (Godot) de ce dépôt** — ne
touche à aucun fichier hors de `experiments/r6_aerial_kick_combo/`.

## Résultat

Livrable final : **`output/cycle5/combo.rbxmx`** (= `output/final_combo.rbxmx`),
un `KeyframeSequence` Roblox natif (XML), 72 keyframes, 2.367s, directement
importable dans Roblox Studio (File → Insert from file, ou via le module
`InsertService`/`KeyframeSequenceProvider`).

## Ce qui a été demandé vs. ce qui a été fait — écarts et blocages

### 1. Plugin Blender `RBX_Animation_Importer-Cautioned.py`

Trouvé et récupéré tel que nommé par la demande : script mono-fichier de
Den_S/@DennisRBLX, mis à jour par Cautioned/@Cautloned, licence permissive
(texte MIT dans l'en-tête), copié dans `tooling/RBX_Animation_Importer-Cautioned.py`
depuis un miroir GitHub (`gas5670/blender-roblox-animation-maker`) — le
dépôt "officiel" actuel de Cautioned (`Cautioned/Blender-Animations-Plugin`,
cloné puis retiré pour ne pas alourdir ce dépôt) a été entièrement réécrit
en "Blender-Animations ultimate edition" : une architecture de sync
temps réel entre un plugin Roblox Studio (Lua) et un addon Blender
compagnon — **structurellement inutilisable ici** (exige Roblox Studio,
une application GUI Windows/Mac, qui ne peut tourner dans ce
sandbox Linux headless quelle que soit la politique réseau).

Le script legacy récupéré, lui, dépend d'un aller-retour avec Roblox
Studio à l'étape de décodage (le payload exporté par Blender est une
chaîne Base64 qu'un script côté Studio doit décoder pour matérialiser le
`KeyframeSequence`) — même blocage structurel : pas de Roblox Studio
disponible ici.

### 2. Rig communautaire "R6 IK+FK Blender Rig" (DevForum)

**Bloqué au niveau réseau du sandbox**, pas un problème de compte/
authentification :

```
$ curl https://devforum.roblox.com/t/r6-ik-fk-blender-rig-v222/3586405
curl: (56) CONNECT tunnel failed, response 403
[agent-proxy] devforum.roblox.com:443 — connect_rejected
(organization policy)
```

Confirmé aussi via l'outil WebFetch (`EGRESS_BLOCKED`). `create.roblox.com`
(la page de la nouvelle édition du plugin) est bloqué pour la même raison.
`github.com`, en revanche, est accessible (le plugin a pu être cloné/
téléchargé sans problème).

### 3. Pas de Blender ni de Roblox Studio installés, pas d'écran

Aucun des deux n'est présent dans ce sandbox, et il n'y a pas de serveur
d'affichage — poser une pose à la souris dans le Graph Editor de Blender,
comme le ferait un animateur, est impossible ici.

### Pivot retenu (documenté, pas caché)

Faute de pouvoir dérouler la chaîne outillage demandée bout en bout, la
même *donnée* — un squelette R6 standard, animé par des courbes réelles de
Blender, exporté au format `KeyframeSequence` — a été produite par un
chemin différent :

- **`bpy` en paquet pip** (`pip install bpy`, ~374 Mo, Blender 5.0.1)
  donne un vrai moteur Blender scriptable sans GUI ni serveur X. C'est le
  même moteur de courbes (F-curves, poignées Bézier) que celui utilisé
  par l'interface graphique — seule l'interaction souris manque.
- **Géométrie du rig R6** (tailles de parts, offsets C0/C1 des 6 Motor6D)
  : valeurs **publiques et standard** de tout personnage R6 du moteur
  Roblox (identiques pour chaque avatar R6, documentées dans d'innombrables
  scripts publics) — donc *pas* une donnée propriétaire du rig DevForum
  bloqué. Le rig IK+FK communautaire n'aurait de toute façon ajouté qu'une
  couche d'os de contrôle par-dessus ce même squelette Motor6D standard.
- **Export** : écriture directe du schéma XML public `KeyframeSequence`
  de Roblox (indépendant du plugin Cautioned), donc aucune dépendance au
  format d'échange Base64 propriétaire du plugin ni à Roblox Studio pour
  matérialiser le résultat.

Voir `scripts/` pour le détail (`r6_rig.py`, `anim_engine.py`,
`export_kfseq.py`, `measure.py`, `preview.py`, `choreography.py`,
`run_cycle.py`).

## Méthode de mesure (objective, justifiable)

Trois critères demandés — fluidité de courbe, absence de tortillement,
respect des contraintes R6 — mesurés automatiquement à chaque cycle
(`scripts/measure.py`), jamais par un simple jugement narratif :

- **Fluidité intra-segment** : jerk (3ᵉ dérivée) RMS du vecteur (rx,ry,rz),
  normalisé par la vitesse de pic, calculé séparément dans chaque fenêtre
  bornée par deux keyframes consécutives (jamais à cheval sur deux
  segments — un combo change légitimement de plan de rotation d'un coup à
  l'autre).
- **Continuité de vitesse aux keyframes** : ajoutée au cycle 2 après avoir
  constaté que la fluidité intra-segment seule a un angle mort (une
  tangente VECTOR rend n'importe quel segment parfaitement plat en jerk
  interne, mais peut laisser un vrai saut de vitesse d'un segment à
  l'autre — mouvement "mécanique"). Les deux ensemble couvrent la
  "fluidité de la courbe" demandée.
- **Absence de tortillement** : changements de signe de la vitesse
  angulaire sur l'axe primaire de chaque segment, avec seuil de bruit
  (3°) pour ignorer un mouvement trop petit pour être perçu.
- **Conformité R6** : vérifications automatiques — exactement 6 segments
  rigides + racine, seul le root translate (aucune jambe/bras ne "glisse"
  dans son parent), rotations dans une plage saine (recalibrée à 250°,
  voir cycle 1), aucune pose de bras façon coup de poing (projection
  avant à plat détectée géométriquement), retour à la pose neutre face
  -Z au début et à la fin.

Un score composite (0–100) agrège les quatre avec des poids documentés
dans `measure.composite_score`.

## Les 5 cycles (budget borné, jamais illimité)

| Cycle | Changement | Intra-seg. | Continuité | Sans tortillement | Structure | **Total** |
|---|---|---|---|---|---|---|
| 1 | Choré. de base, tangentes AUTO_CLAMPED | 7.2 | 52.2 | 100 | 100 | **65.0** |
| 2 | Tangentes VECTOR partout | 100.0 | 17.2 | 100 | 100 | **87.6** |
| 3 | AUTO_CLAMPED + 3 keyframes mi-arc à la main | 6.2 | 57.1 | 100 | 100 | **65.4** |
| 4 | VECTOR jambes/torse, AUTO_CLAMPED bras/tête | 17.1 | 18.4 | 100 | 100 | **62.9** |
| **5** | **VECTOR partout + 8 keyframes flanquantes (smoothstep) autour des 4 sommets** | **100.0** | **38.2** | **100** | **100** | **90.7** |

**Cycle 1 — ligne de base.** Choré. complète (anticipation → 3 kicks →
atterrissage, 12 keyframes, 2.36s), tangentes Bézier `AUTO_CLAMPED`
(défaut Blender pour une ease in/out fluide). Résultat brut inutilisable
tel quel : deux bugs de MESURE trouvés et corrigés avant de faire
confiance au score (détaillés ci-dessous) — une fois corrigés, cycle 1
donne en fait une bonne ligne de base (0 tortillement réel, structure
100%), mais une fluidité intra-segment faible (7.2) : `AUTO_CLAMPED`
laisse un vrai surcroît de courbure sur les articulations à grande
amplitude (Left Leg, Right Leg, Torso).

**Bugs de mesure trouvés et corrigés au cycle 1** (avant de publier un
premier score, pas après) :
1. *Repliement quaternion* : l'angle dérivé d'un quaternion isolé se
   replie toujours dans [0,180] — une rotation animée qui traverse 180°
   (le spin du kick2 va à ~200°) y apparaissait comme un saut brutal de
   signe (+170° → −170° instantané sur la courbe). Diagnostiqué en
   traçant `curves.png` et en regardant le résultat (pas seulement les
   nombres). Root-cause plus profond, corrigé en amont : le keyframing de
   `rotation_quaternion` composante-par-composante dans Blender ne fait
   PAS de SLERP correct entre deux poses éloignées — remplacé par un
   keyframing sur 3 canaux d'angle (rx,ry,rz) indépendants
   (`rotation_mode='XYZ'`), la matrice de rotation utilisée pour l'export
   et la mesure étant TOUJOURS recalculée à la main
   (`euler_xyz_matrix`, convention `CFrame.Angles(x,y,z)` de Roblox)
   plutôt que lue depuis la composition interne de Blender (vérifié
   numériquement : différente de Rx·Ry·Rz, donc jamais fiable pour cet
   usage).
2. *Seuil de rotation "saine" mal calibré* : 170° faisait échouer
   `rotation_within_sane_range` sur le Torso pendant le spin du kick2 —
   mais un Motor6D 3-DOF n'a rien d'un coude/genou à charnière, tourner à
   190° est le mouvement demandé, pas un flip accidentel du rig. Relevé à
   250° (garde-fou contre une vraie aberration, pas contre le mouvement
   voulu).

**Cycle 2 — une seule variable changée (méthode).** Hypothèse : les
"tortillements" et le jerk élevé du cycle 1 viennent d'un artefact de
tangente auto-calculée influencée par des voisins distants qui repartent
dans une direction opposée. Test : tangentes `VECTOR` (rectiligne)
partout. Piège bpy trouvé au passage : écrire `handle_left_type`/
`handle_right_type` ne recalcule PAS les coordonnées des poignées — elles
restaient à leurs valeurs `AUTO_CLAMPED`, donc le premier essai n'a
**rien changé du tout** malgré le changement de réglage (score
rigoureusement identique au cycle 1, ce qui a immédiatement mis la puce à
l'oreille). Corrigé en recalculant les poignées à la main. Une fois
corrigé, un second bug de mesure est apparu : les fenêtres de phase
(bornes d'indices d'échantillon) débordaient parfois d'un échantillon
dans le segment suivant à cause d'un arrondi (`round` au lieu de
`floor`/`ceil`), ce qui faisait passer un vrai changement de segment
(normal) pour un "tortillement" à l'intérieur d'un segment (faux
positif) — corrigé, ce qui a fait passer `no_twist` de 0 (tous les
cycles) à 100 partout. Résultat net : jerk intra-segment nul par
construction (ligne droite), mais continuité de vitesse aux keyframes
dégradée (mouvement plus "mécanique") — angle mort de la métrique de
fluidité intra-segment seule, d'où l'ajout de `velocity_continuity_at_keyframes`
avant de faire confiance à ce score.

**Cycle 3 — hypothèse alternative, résultat négatif rapporté tel quel.**
Retour à `AUTO_CLAMPED` (sa continuité native) + 3 keyframes mi-arc
ajoutées à la main sur les segments à plus fort jerk du cycle 1 (Left
Leg, Right Leg, Torso), pour raccourcir l'arc et réduire la courbure
requise par segment. N'a quasiment rien changé (65.4, dans le bruit du
cycle 1) — pire, Left Leg/Right Leg ont légèrement empiré (137/139 vs
119/131). Les valeurs choisies à la main pour ces keyframes intermédiaires
n'étaient probablement pas elles-mêmes sur une trajectoire lisse.
Enseignement retenu : ajouter des keyframes à la main sans données pour
guider leur placement ne suffit pas.

**Cycle 4 — combinaison, résultat négatif rapporté tel quel.** VECTOR sur
les articulations "porteuses" (jambes, torse/root) + AUTO_CLAMPED sur
l'accompagnement (bras, tête). Pire que cycle 2 sur les deux scores
(62.9) : l'agrégation "pire articulation domine" (delibérée — une seule
articulation qui saccade suffit à casser la lecture visuelle du combo)
signifie qu'améliorer certaines articulations ne suffit pas si d'autres
restent le maillon faible — ici bras/tête (restés AUTO_CLAMPED) sont
restés le goulot d'étranglement du jerk intra-segment, et jambes/torse
(passés VECTOR) sont devenus le goulot de la continuité. Aucun gain net.

**Cycle 5 (dernier du budget) — donnée, pas devinette.** Repart de cycle
2 (VECTOR partout, meilleur score) et lit directement le détail
`velocity_continuity_at_keyframes` du cycle 2 pour localiser les 4 pires
sauts (t=0.62, 1.16, 1.66, 1.86 — jusqu'à 1.4 de saut normalisé sur
Head/Right Leg/Left Leg). Insertion d'une keyframe juste avant et juste
après chacun de ces 4 sommets, interpolée en *smoothstep* (pas en
lerp linéaire) pour adoucir l'entrée/sortie tout en gardant des segments
strictement droits (VECTOR partout, donc le jerk intra-segment nul du
cycle 2 reste garanti par construction). Résultat : continuité de vitesse
38.2 (vs 17.2 au cycle 2, plus du double), fluidité intra-segment
toujours 100, total **90.7** — meilleur score des 5 cycles, amélioration
nette et mesurée sur la faiblesse identifiée du cycle 2, pas un plateau.

**Arrêt : budget de 5 cycles épuisé** (pas un plateau — le cycle 5
améliore encore le cycle 2 de manière nette). Une suite logique existe
(densifier davantage autour des points de saut restants, ou traiter la
continuité analytiquement plutôt que par keyframes flanquantes) mais
sort du budget de cette itération.

## Constructions du rig / choix de conception notables

- **Bassin sur R6** : le rig R6 n'a pas de segment "bassin" séparé (Torso
  est un unique segment rigide). Le seul proxy disponible pour "rotation
  du bassin" au sens de la contrainte utilisateur est `HumanoidRootPart`
  (le `RootJoint`) : dans cette chorégraphie il porte le moteur de
  spin/lean du corps, Torso ajoute une rotation locale qui accompagne
  (jamais ne contredit) ce mouvement — c'est la manière dont un animateur
  R6 obtient un équivalent de rotation de bassin sur ce rig sans genou ni
  bassin séparé.
- **Aucun pli de jambe** : chaque jambe reste un unique Motor6D 3-DOF
  (aucune extra-articulation ajoutée) ; un "coup retourné" ou "croisé" est
  entièrement construit par rotation de hanche + inclinaison torse/root,
  jamais par un pli inexistant sur ce rig — vérifié automatiquement
  (`only_root_translates`, `six_rigid_segments_only`).
- **Aucun coup de poing** : les bras ne font que du contrepoids
  (jamais de projection avant à plat) — vérifié géométriquement à chaque
  cycle (`no_punch_like_arm_pose`).

## Reproduire / itérer

```bash
cd experiments/r6_aerial_kick_combo
python3 -m venv .venv && source .venv/bin/activate
pip install bpy numpy matplotlib   # ~374 Mo, bpy = Blender 5.0.1 headless
cd scripts
python3 run_cycle.py --cycle 5     # régénère output/cycle5/{combo.rbxmx,metrics.json,poses.png,curves.png}
```

## Rig réel importé depuis GitHub — et le bug qu'il a révélé

Jusqu'ici la géométrie R6 était **écrite à la main de mémoire** dans
`r6_rig.py`. Elle est maintenant **chargée depuis un vrai fichier de rig**
(`rig/RigR6.rbxmx`, dépôt [Adonis](https://github.com/Epix-Incorporated/Adonis),
licence MIT — voir `rig/PROVENANCE.md`), parsé par `scripts/import_rig.py`
vers `rig/r6_rig.json`.

Choix de la source : la recherche GitHub renvoyait surtout des
`RCCService*/content/models/Thumbnails/Mannequins/R6.rbxmx`, c'est-à-dire
des dumps de contenu client Roblox redistribués par des dépôts de private
servers — contenu propriétaire, écarté au profit d'une source clairement
licenciée MIT.

### Ce que la comparaison a donné

| | codé à la main | rig réel |
|---|---|---|
| tailles des 7 parts | | **identiques** |
| translations C0/C1 des 6 Motor6D | | **identiques** |
| **rotations C0/C1 des 6 Motor6D** | « identité (standard R6) » | **aucune n'est l'identité** |

Le commentaire de `r6_rig.py` affirmait noir sur blanc « Rotation de C0/C1
= identite (standard R6) ». C'est faux : hanches et épaules portent un
±90° autour de Y, le Neck et le RootJoint une permutation Y/Z.

### Pourquoi ça cassait l'export (et pas le reste)

Le moteur résout `Part1 = Part0 * C0 * Transform * C1⁻¹`. La rotation vue
dans le repère du parent vaut donc `J0 · T · J1ᵀ`. Écrire directement
`T = R` (la pose telle que je l'ai écrite, en repère parent) ne donne `R`
que si `J0` et `J1` valent l'identité. Avec les vraies valeurs, on obtient
**le bon angle autour du mauvais axe** — la rotation d'axe `a` devient une
rotation d'axe `J0·a`. Mesuré par `scripts/verify_joint_frames.py` :

```
Right Leg (60,0,0) — coup de pied vers l'AVANT (axe X)
   voulu :  60.0 deg autour de (+1.00,+0.00,+0.00)
   obtenu:  60.0 deg autour de (+0.00,+0.00,-1.00)   -> axe dévié de 90 deg
Torso (0,90,0) — spin du torse (lacet, axe Y)
   voulu :  90.0 deg autour de (+0.00,+1.00,+0.00)
   obtenu:  90.0 deg autour de (+0.00,+0.00,+1.00)   -> axe dévié de 90 deg
```

Soit, sur un vrai rig : des coups de pied qui partent **de côté** au lieu
de vers l'avant (et en miroir entre jambe gauche et droite, les deux
hanches ayant des `J0` opposés), et un torse qui fait un **tonneau** au
lieu d'un tour sur lui-même.

**Pourquoi ni les captures ni les scores ne l'avaient vu** : au repos
`R = identité`, donc `T = identité` quels que soient `J0`/`J1` — la pose
de repos restait exacte. Et mes stick-figures faisaient leur cinématique
directe avec *la même hypothèse fausse* : ils montraient fidèlement ce que
j'avais écrit, pas ce que Roblox en aurait fait. Une vérification visuelle
contre son propre modèle erroné ne peut pas attraper ce type d'erreur —
seul un vrai rig le pouvait.

### Correction

`export_kfseq.to_joint_frame()` convertit désormais chaque pose du repère
du parent vers le repère du joint avant écriture :

- rotation : `T = J0ᵀ · R · J1`
- translation (racine seulement, `c1` nul) : `T_t = J0ᵀ · d`
- membres : `T_t = 0` reste correct (le terme `−R·c1` fait déjà pivoter
  le membre autour de son point d'attache)

`scripts/verify_joint_frames.py` vérifie les trois choses : aller-retour
exact (écart max 0.00e+00 sur 200 tirages × 6 joints), pose de repos
correcte, et chiffre l'écart qu'introduisait l'ancien export.

Invariant obtenu après correction : **les scores des 5 cycles sont
inchangés au bit près** (65.0 / 87.6 / 65.4 / 62.9 / 90.7). C'est le bon
signe — le mouvement écrit n'a pas changé, seule son écriture dans le
fichier est corrigée. Les fichiers `.rbxmx` de tous les cycles et du
livrable filtré ont été régénérés.

## Rejouer le fichier PAR LE MOTEUR — deux bugs de plus

`scripts/resolve_rbxmx.py` relit le `.rbxmx` livré et le résout avec
l'équation réelle `Part1 = Part0 · C0 · Transform · C1⁻¹`, en ignorant —
comme le fait l'Animator — toute Pose dont le nom ne correspond au `Part1`
d'aucun Motor6D. Le lecteur HTML est désormais alimenté par cette
résolution, plus par ma cinématique maison : il montre ce que Roblox
calculerait, pas ce que j'ai écrit.

Ce simple changement a fait tomber deux erreurs de plus.

### 4. La pose racine était ignorée — tout le saut disparaissait

`HumanoidRootPart` n'est le `Part1` d'aucun Motor6D du rig (vérifié sur
`rig/r6_rig.json` : il n'est que le `Part0` du RootJoint). Une Pose portant
ce nom ne pilote donc **rien**. Or c'est exactement là que j'écrivais tout
l'arc du saut et la rotation du corps :

```
AVANT : HumanoidRootPart porte 1.587 stud de translation, 175.6 deg de rotation
        -> Torso Y resolu par le moteur : amplitude 0.000 stud
APRES : HumanoidRootPart identite
        -> Torso Y resolu par le moteur : amplitude 1.998 stud
```

Le personnage aurait enchaîné les trois coups **sans jamais décoller**, et
sans tourner. Corrigé en repliant rotation racine et translation sur la
pose du **Torse**, qui pilote le RootJoint — c'est ainsi que sont faites
les animations de saut de Roblox. Le repli est sûr quelle que soit
l'interprétation : on écrit l'identité dans la pose racine, donc aucun
double-emploi si elle était honorée.

### 5. Ma cinématique d'aperçu faisait pivoter les membres autour de leur centre

En confrontant la résolution moteur à ma cinématique directe, le torse
coïncidait (5e-05) mais les membres divergeaient jusqu'à **1.74 stud**.
La partie translation de l'équation vaut `c0 − R·c1`, or
`_world_positions()` utilisait l'écart de repos `c0 − c1`, **constant**.
Un membre y tournait donc autour de son propre centre au lieu de pivoter
autour de son point d'attache : une jambe qui frappe voyait son pied
bouger, mais le haut de sa cuisse se détacher de la hanche.

Cela n'affectait ni les angles écrits, ni les mesures, ni le fichier
exporté — **uniquement les aperçus**, c'est-à-dire précisément l'outil
avec lequel je « vérifiais » le résultat.

Après correction, la vérification bout-en-bout passe : écart entre le
`.rbxmx` résolu par le moteur et la cinématique corrigée =
**5e-05 stud** sur les six parties du corps (résidu = l'arrondi à 4
décimales de l'export).

### Ce que ces trois erreurs ont en commun

Les bugs 3, 4 et 5 sont tous des **désaccords entre mon modèle et le
moteur**, et aucun n'était détectable par les moyens que j'utilisais :
les scores mesuraient les angles écrits (justes), les captures montraient
ma propre cinématique (fausse de la même manière que l'export), et la pose
de repos restait correcte dans tous les cas. Vérifier une sortie contre le
modèle qui l'a produite ne prouve rien. Il a fallu deux choses
extérieures : un vrai rig, et rejouer le fichier livré par l'équation du
moteur plutôt que par mon code.

## Cycle 6 — haut du corps actif (vrai taekwondo)

Jusqu'ici les bras ne servaient que de balancier. En taekwondo le haut du
corps ne *suit* pas le mouvement, il le **produit**. Le cycle 6 garde
jambes et timing du cycle 2 et réécrit entièrement tête, bras et
accompagnement du torse, autour de trois mécaniques réelles :

1. **Spotting** — sur le coup retourné, la tête tourne en premier, fixe la
   cible par-dessus l'épaule, le corps suit, la jambe arrive en dernier.
2. **Fermeture des bras** pendant la vrille — conservation du moment
   cinétique, comme un patineur. Les bras s'ouvrent ensuite pour freiner.
3. **Couplage contralatéral** — bras opposé à la jambe qui frappe en
   avant, bras du même côté qui tire.

Plus une **garde** tenue au départ, entre les coups et à l'arrivée.

### Mesuré, pas ressenti

`measure.taekwondo_signature()` chiffre les trois mécaniques :

| | jambes seules (cy. 2) | haut du corps actif (cy. 6) |
|---|---|---|
| engagement du haut du corps | 0.606 | **1.256** |
| avance de tête sur le corps | 0.018 s | **0.041 s** |
| tête tournée au-delà du corps | 24.9° | **54.5°** |
| fermeture des bras à la vrille | 0.361 | 0.422 |

### Le contrôle « aucun coup de poing » était structurellement faux

Il flaggeait **toute pose bras vers l'avant**. Or sur R6 le bras est *un
seul segment épaule→main* : « mains devant la poitrine » implique
forcément un segment vers l'avant. Une garde de taekwondo était donc
détectée exactement comme un direct (allonge 1.40 contre 1.50 stud pour un
bras tendu — l'allonge ne sépare rien). Ce contrôle rendait toute garde
impossible, donc tout vrai taekwondo, alors que la contrainte demandée est
« aucun coup de poing », pas « aucun bras levé ».

Remplacé par une détection de **détente** : allonge **et** vitesse
d'extension simultanément au-dessus du seuil (1.2 stud / 6 stud/s), la
main étant mesurée dans le repère du **torse** — un coup se définit par
rapport au corps, pas au monde. Vérifié à la main sur le cycle 6 : la
détente maximale (11 stud/s) a lieu main à −0.16 d'allonge et −1.01 de
hauteur, c'est-à-dire le bras qui fouette vers le haut à l'impulsion, et
l'allonge maximale (garde) coïncide avec une détente **négative** (le bras
se rétracte). Les deux ne se rencontrent jamais.

### Tension trouvée entre les deux demandes

Avec des bras actifs, l'animation vit près de la limite : sur le balayage
du filtre cartoon appliqué au cycle 6, **12 des 18 variantes violent la
contrainte** (jusqu'à 1.50 stud d'allonge à 27.6 stud/s — un vrai direct
fabriqué par le dépassement du filtre). Le réglage retenu
(`k=0.0015`, `σ=0.035`, `α=1.0`, score 95.6) est le plus fort qui passe
encore, et il passe pour de bonnes raisons, pas par technicité : zéro
instant où allonge et détente sont simultanément au-dessus des seuils.

Autrement dit, exagération et « pieds uniquement » tirent en sens
contraire dès que les bras jouent : le gain du filtre est désormais borné
par la contrainte, pas seulement par le ringing.

### Une métrique aveugle de plus

`head_lead_s` renvoyait 0.000 s pour toutes les variantes, y compris celle
où 54° d'avance de tête sont écrits noir sur blanc. La première version
corrélait les **vitesses** de lacet tête/corps : sur la fenêtre de vrille
ce sont deux rampes quasi monotones de même durée, dont la corrélation
pique à lag 0 quel que soit le décalage constant. La corrélation croisée
mesure « même forme », pas « en avance ». Remplacée par une **traversée de
seuil** — à quel instant chacun atteint la mi-course de la rotation du
corps.

## Cycle 7 — recréation d'une référence vidéo fournie

L'utilisateur a fourni une capture d'écran (22.66s, `.mov`) de Roblox
Studio/Moon Animator ("Linear Easing Test" par EclipseThemDev) montrant un
rig R6 — même contrainte 6-segments-rigides que ce projet — exécuter un
mouvement de combat, et a demandé de le recréer.

### Décodage (blocage outillage, contourné)

`ffmpeg`/`ffprobe` système présents (`/usr/bin`) mais cassés : dépendance
manquante `libcaca.so.0`, elle-même indisponible sur le miroir apt de ce
sandbox (404 sur plusieurs paquets liés à `libva`). Contourné avec
`pip install imageio-ffmpeg`, qui embarque un binaire ffmpeg statique
indépendant des libs système — extraction de frames à 4, 10 fps puis 22
frames ciblées en pleine résolution entre t=0.00 et t=1.70s (le point de
boucle vidéo) pour lire la pose précisément.

### Lecture de la structure (pas une copie des courbes)

Aucun fichier source (le `.rbxm`/projet Moon Animator n'a pas été fourni,
seule la vidéo) — impossible de recréer les courbes exactes. Ce qui est
repris est la **structure et le timing** lus sur les captures :

1. **0.00–0.20s — fente profonde** : torse très penché en avant, jambe
   arrière tendue en arrière, bras qui traînent (contrepoids de
   sprinteur), flash d'impact au pied vers 0.20.
2. **0.20–0.90s — montée tenue** : la jambe balaie de la hanche jusqu'à la
   quasi-verticale, confirmé **à l'avant du corps** (capture à t=0.30 :
   traînée devant le torse, pas derrière), torse qui bascule en arrière en
   contrepoids — **tenue en l'air** marquée de 0.60 à 0.90 (hang-time
   délibéré, pas un pic instantané que j'aurais pu manquer en survolant).
3. **0.90–1.30s — ramassé** : la jambe redescend, le corps se compacte en
   crouch bas, chargement du spin.
4. **1.30–1.50s — spin** : libération rapide (éclats/traits de vitesse sur
   les captures), très bref, ~0.2s réel.
5. **1.50–1.70s — atterrissage** : retour à une posture debout neutre.

Reproduit avec le moteur déjà construit pour ce projet — hanche + bassin-root
pour la montée et le spin, jamais de pli de jambe inexistant, jamais de
coup de poing (le détecteur de détente du cycle 6 réutilisé tel quel) —
jambe droite pour la montée tenue, jambe gauche pour le spin (asymétrie
délibérée, contrairement à la garde symétrique du cycle 6).

### Ce qui n'est PAS recréé

- **Aucun VFX.** Traînée lumineuse le long de la jambe, anneau de choc au
  sol, éclats à l'impact : ce pipeline exporte un `KeyframeSequence`
  (animation de corps Motor6D), pas des `ParticleEmitter`/`Beam`. Un projet
  séparé côté Studio.
- **Pas pixel-exact.** Les angles sont les miens, dérivés de la lecture
  visuelle — pas les courbes de l'auteur original.

### Résultat mesuré

Passe le même pipeline que les cycles précédents, y compris le détecteur
de détente corrigé au cycle 6 (des bras actifs pendant une fente profonde
et un spin sont exactement le cas qu'il doit couvrir) :

| | brut | + filtre cartoon (k=0.0015, σ=0.06, α=1.0) |
|---|---|---|
| structure R6 | 100 | 100 |
| continuité de vitesse | 35.1 | 70.3 |
| exagération dans la bande | — | 99.8 |
| **total** | 70.5 | **95.5** |

`no_punch_thrust` : allonge max 1.27 stud, détente max 18.0 stud/s — passe
avec la même marge que les autres cycles, pas par technicité (12 des 18
variantes du balayage échouent ce contrôle, cf. cycle 6).
`rotation_within_sane_range` signale un pic Torso à 179.9° — vérifié à la
main : c'est le passage éphémère (0.017s) par "face arrière" au milieu du
spin, physiquement inévitable pour un tour de plus de 180°, pas un flip
cassé.

Livrable : `output/cartoon_c7/best/combo_cartoon.rbxmx`, comparateur dans
le viewer (4ᵉ onglet "recréation référence").

## Cycle 8 — mesure pixel rigoureuse (l'utilisateur a demandé « exactement »)

Le cycle 7 recréait la *structure* de la vidéo à l'impression visuelle. Sur
demande explicite d'une reproduction exacte, une seconde passe a été faite
avec des mesures objectives plutôt qu'une lecture à l'oeil — et a trouvé
une vraie erreur.

### Méthode

- Extraction **native** de la vidéo (108 frames, ~58,4 fps réelles, contre
  les 22 captures ponctuelles du cycle 7) avec `imageio-ffmpeg`.
- Pour chaque temps fort, un **crop agrandi avec grille de coordonnées**
  en pixels (pas une estimation visuelle — des coordonnées lues
  directement) pour mesurer la direction des membres visibles.
- Calage temporel à la frame vidéo près (`(idx-1)/58.4` s), plus précis
  d'un ordre de grandeur que le pas de 0,1–0,25 s du cycle 7.

### Ce que la mesure a corrigé

**La jambe ne fait pas une seule montée tenue.** Elle fait DEUX montées
distinctes : kick 1 (t=0,086–0,308s, monte puis **redescend aussitôt**),
un creux où le corps se redresse (t=0,308–0,462s), puis kick 2
(t=0,462–0,908s, remonte plus haut, **celui-là est tenu**, hang-time
confirmé sur 17 frames consécutives ≈ 0,3s réelles). Le cycle 7 avait fusionné
ces deux mouvements en une seule montée continue — invisible à la densité
d'échantillonnage utilisée alors, visible dès qu'on regarde chaque frame
native.

### Plafond de la méthode — atteint, documenté, pas contourné

En essayant de pousser la mesure au niveau du membre individuel (angle 3D
exact de chaque Motor6D, pas seulement le timing), deux limites réelles
sont apparues, vérifiées concrètement sur les frames plutôt que supposées :

- **Occlusion.** Sur les frames avec flash d'impact (ex. t=0,086s),
  plusieurs boîtes du rig se chevauchent au point qu'aucune arête n'est
  attribuable avec certitude à un membre précis. Zoomer davantage
  n'y change rien — l'information n'est simplement pas dans l'image à cet
  instant.
- **Ambiguïté de profondeur monoculaire.** Une caméra fixe unique ne peut
  pas distinguer un membre qui pointe vers elle d'un membre qui pointe à
  l'opposé — la silhouette 2D est identique dans les deux cas. C'est une
  limite de l'information disponible, pas de la méthode de mesure.

Décision assumée en conséquence (validée avec l'utilisateur avant de
continuer) : le calage temporel des 16 temps forts est mesuré à la frame
près (objectif, sans ambiguïté) ; les angles de la jambe active reprennent
l'ordre de grandeur du cycle 7 (déjà informé par la même lecture visuelle)
plutôt qu'une nouvelle inversion caméra-par-membre qui n'aurait pas
convergé mieux sur les frames à occlusion ; torse/bras/tête suivent la
même mécanique que le cycle 6/7 (contrepoids, fermeture pendant le spin),
retimés sur la structure à deux montées.

### Bug réel trouvé en vérifiant, pas supposé

Le premier export du cycle 8 échouait `no_punch_thrust` : le retour rapide
des bras vers la garde après le spin (1,42→1,55s) faisait passer l'allonge
et la vitesse d'extension au-dessus du seuil pendant **un seul échantillon
sur 120/s** — un vrai artefact de vitesse (le segment linéaire allait trop
vite sur trop peu de temps), pas une fausse alerte du détecteur. Corrigé
en insérant un point intermédiaire (t=1,49s) qui étale le retour sur deux
segments au lieu d'un seul trop rapide. Revérifié : `no_punch_thrust` passe
avec marge (allonge max 1,24 stud contre un seuil de 1,2).

### Résultat

| | cycle 7 (impression visuelle) | cycle 8 (mesure pixel) |
|---|---|---|
| structure temporelle | montée unique tenue | **deux montées + creux, mesuré** |
| calage temporel | ±0,1–0,25s | **±0,017s (frame vidéo)** |
| structure R6 | 100 | 100 |
| total (brut) | 70.5 | 91.1 |
| total (+ filtre cartoon) | 95.5 | 90.1 |

Livrable : `output/cartoon_c8/best/combo_cartoon.rbxmx`. Vérifié par le
même round-trip moteur que tous les cycles précédents (`resolve_rbxmx.py`) :
pose racine correctement ignorée (0 stud/deg), amplitude Torso Y résolue
2,07 studs.

**Ce qui reste une approximation, explicitement** : les angles exacts de
la jambe active pendant les phases occultées par le VFX, et tout ce
qu'une caméra fixe unique ne peut pas trancher par nature. Le seul chemin
vers un exact réel serait le fichier source (projet Moon Animator/`.rbxl`),
pas davantage de mesure sur la vidéo — ce plafond a été vérifié
concrètement, pas supposé.

## Cycle 9 — exagération manga (retour : « pas assez abusé »)

Retour direct de l'utilisateur après le cycle 8 : « Non mais tu abuse pas
assez le mouvement style manga ». Deux leviers, pas un seul — augmenter le
gain du filtre n'aurait pas suffi seul.

### Levier 1 — la cible du filtre était une hypothèse, pas une mesure

`exaggeration_score` visait un dépassement de 10 % de l'amplitude par
segment. Ce chiffre n'avait jamais été validé — c'était un choix de métier
supposé au moment d'écrire la fonction. Le retour de l'utilisateur le
contredit directement, donc la cible est recalibrée dessus plutôt que sur
une nouvelle intuition : `target_pct` 10.0 → **22.0**, `spread_pct` 8.0 →
**10.0** (`scripts/measure.py`). Sans élargir la grille de balayage en
conséquence (`grid_k` étendu à `[0.0015, 0.003, 0.006, 0.01, 0.015, 0.02]`,
`grid_sigma` à `[0.035, 0.06, 0.09]` dans `scripts/run_filter.py`), le
balayage n'aurait même pas eu la possibilité de proposer un gain assez fort
pour atteindre la nouvelle cible.

### Levier 2 — les poses elles-mêmes, pas seulement le post-traitement

Un filtre plus fort sur des poses inchangées ne fait qu'ajouter du
dépassement autour de la même amplitude — ça reste petit, juste plus
tremblant. Le vrai « style manga » demande des poses plus amples et un
contraste de tenue plus marqué. `cycle_9()` (`scripts/choreography.py`)
reprend exactement la structure et le calage mesurés au cycle 8 (double
montée + creux, spin, atterrissage) et amplifie seulement l'amplitude et le
tempo :

| | cycle 8 | cycle 9 |
|---|---|---|
| accroupi (Torso X / racine Y) | -38° / -0,55 | **-48° / -0,75** |
| pic kick 2 (Right Leg X) | 158-161° | **172-175°** |
| pic kick 2 (racine Y) | 1,42-1,45 | **1,72-1,75** |
| rotation totale du spin | ~250° | **~330-340°** |
| tenue au pic (durée) | 0,24 s | **0,34 s** (frappe plus rapide, pic plus figé) |

Vérifié indépendamment par `taekwondo_signature` (mêmes outils que tous les
cycles précédents, pas une nouvelle mesure inventée pour l'occasion) :
`engagement_haut_du_corps` 1,278 (cycle 8 : 1,21), `arm_pull_in` 1,124
(cycle 8 : 0,91). Le premier confirme l'amplification ; le second est un
compromis assumé, pas une erreur silencieuse — voir plus bas.

### Balayage et résultat

Structure R6 à 100 dès le premier export (contrairement au cycle 8, aucun
correctif de type `no_punch_thrust` n'a été nécessaire sur la choré. brute).
Le balayage élargi (36 variantes) confirme le même mécanisme observé aux
cycles 6/8 : la structure ne reste à 100 que dans une bande étroite
k·σ≈constante (0,0015/0,035, 0,003/0,06, 0,006/0,09) et tombe à 83,3
partout ailleurs, surtout pour k≥0,01. Vérifié explicitement plutôt que
supposé — les échecs sont bien `no_punch_thrust` (ex. k=0,01/σ=0,035 :
allonge 1,49 stud contre un seuil de 1,2, vitesse 177,7 stud/s contre un
seuil de 6,0, sur les deux bras) : au-delà de cette bande le filtre projette
les bras assez vite et assez loin pour ressembler à un coup de poing, pas à
un contrepoids.

Gagnant : **k=0,006, σ=0,09, α=0,0** — `exaggeration_in_band` 96,3,
`mean_followthrough_pct` 23,9 % (contre 10,2 % au cycle 2/5, pile sur la
nouvelle cible de 22 %), structure 100, total 91,4.

Vérifié par le même round-trip moteur que tous les cycles précédents
(`resolve_rbxmx.py`) : pose `HumanoidRootPart` toujours correctement
ignorée (0 stud/deg), amplitude Torso Y résolue **2,961 studs** (contre
2,07 au cycle 8 — l'amplification est mesurable jusque dans la sortie
finale, pas seulement dans les courbes intermédiaires).

### Compromis assumé, pas caché

`arm_pull_in` = 1,124 (> 1) : au pic de vrille, les mains s'écartent
légèrement de l'axe de rotation au lieu de se refermer comme un patineur
qui accélère sa rotation (cycle 8 : 0,91, cohérent avec la conservation du
moment cinétique). Plus spectaculaire à l'écran, moins fidèle à la
mécanique réelle. Signalé ici et dans la note du lecteur HTML plutôt que
laissé dans les chiffres seuls.

Livrable : `output/cartoon_c9/best/combo_cartoon.rbxmx`.

## Piste 1 — exagération algorithmique post-hoc (Cartoon Animation Filter)

Ajoutée après coup, sur la base d'un brief de recherche qui la classait
priorité 1. Les deux filtres sont implémentés dans
`scripts/cartoon_filter.py`, le balayage dans `scripts/run_filter.py`.

- **Cartoon Animation Filter** (Wang, Drucker, Agrawala, Cohen, SIGGRAPH
  2006) : `x*(t) = x(t) − k·G(x″(t))`. Le signe fait tout : quand le geste
  accélère on soustrait du positif → la courbe part légèrement à l'envers
  (anticipation) ; quand il décélère on soustrait du négatif → elle dépasse
  la pose puis y revient (follow-through). ~40 lignes, aucune dépendance,
  aucune hypothèse sur le squelette (appliqué 3× par Motor6D, un par axe).
- **Slow In / Slow Out** (Kwon & van de Panne, SIGGRAPH 2006) : time-warp
  par segment, `u' = (1−α)·u + α·smoothstep(u)`. Ne touche à aucune valeur
  de pose, seulement à la distribution du temps entre elles.

### Deux bugs de mesure trouvés (et pourquoi ils comptent ici)

Ma suite de mesures avait été construite pour détecter du tortillement NON
VOULU. Le filtre ajoute délibérément un aller-retour : mesurée avec les
seuls outils des cycles 1-5, la variante filtrée aurait été pénalisée
exactement pour ce qu'on lui demande de faire. D'où `filter_response` +
`exaggeration_score` — et deux erreurs à corriger en route :

1. **Le follow-through mesuré sur la position absolue.** Je mesurais de
   combien la courbe dépasse la *valeur* de la keyframe dans le sens
   d'arrivée — ce qui compte comme « dépassement » un mouvement qui
   continue simplement sa course après une pose de milieu de geste.
   Symptôme : l'animation NON filtrée affichait un follow-through massif,
   et le score d'exagération sortait à 0.0 pour les 19 variantes. Corrigé
   en mesurant la contribution du filtre (`filtré − original`), pas la
   position absolue.
2. **Le ringing mesuré sur l'écart au lieu de la vitesse.** Je comptais
   les alternances de signe de `filtré − original`. Or un simple retiming
   est monotone : il ne *peut pas* faire osciller un signal, mais son
   écart alterne forcément de signe (le warp avance le signal sur une
   moitié de segment, le retarde sur l'autre). Le contrôle l'a rendu
   visible : SISO seul, filtre cartoon à l'arrêt (k=0), affichait
   ringing=14 — structurellement impossible. Corrigé en comptant les
   inversions de sens de la **vitesse du signal filtré**, comparées à
   celles de l'original, avec un budget de 2 par segment (le retour du
   dépassement + l'anticipation du coup suivant). Contrôle re-passé :
   SISO seul → ringing=0 à tout α, comme il se doit.

Sans le second correctif, la conclusion aurait été « SISO est
inutilisable, il fait osciller les courbes » — l'inverse exact du
résultat réel.

### Balayage (19 variantes × 2 bases)

| Base | k (s²) | σ (s) | α | Exagération | Ringing | Continuité | Structure | **Total** |
|---|---|---|---|---|---|---|---|---|
| cycle 5 | — | — | — | — | 0 | 42.5 | 100 | 71.6 |
| cycle 2 | — | — | — | — | 0 | 20.9 | 100 | 68.4 |
| cycle 5 | 0.0015 | 0.06 | 1.0 | 99.8 | 0 | 63.4 | 100 | 94.5 |
| **cycle 2** | **0.0015** | **0.06** | **1.0** | **99.9** | **0** | **77.9** | **100** | **96.7** |

Réglage retenu : **k=0.0015 s², σ=0.06 s, α=1.0 sur la choré. du cycle 2**
→ dépassement moyen 10,2 % de l'amplitude de segment (anticipation 1,4 à
5,0° et follow-through 1,9 à 5,2° selon l'articulation), zéro ringing,
contrainte R6 toujours à 100 %.

### Le résultat retourne une conclusion des cycles 1-5

Le filtre appliqué à la choré. **brute** (cycle 2) bat celui appliqué au
cycle 5 (96.7 vs 94.5) — alors que le cycle 5 était mon meilleur résultat
manuel. Raison : les 8 keyframes flanquantes que j'avais placées à la main
au cycle 5 pour adoucir les sommets sont une approximation discrète de ce
que SISO fait continûment. Les deux mécanismes façonnent la même
accélération et se gênent (le cycle 5 subdivise les segments, donc l'ease
par segment de SISO agit sur des sous-segments déjà adoucis : continuité
63.4 contre 77.9 sur la base brute).

Autrement dit : le travail manuel du cycle 5 devient inutile une fois le
filtre en place, et le pipeline se simplifie — choré. brute + 2 filtres,
au lieu de choré. + keyframes de calage à la main.

Livrable de cette piste :
**`output/cartoon_c2/best/combo_cartoon.rbxmx`**, balayage complet et
mesures par articulation dans `output/cartoon_c2/sweep.json`.

## Prochaine étape (hors scope de ce tour)

Ce tour livre l'animation exportée, pas son intégration. Import réel dans
Roblox Studio (test visuel humain, ajustement C0/C1 si nécessaire pour
un rig de production précis) à faire dans un tour séparé, une fois
l'accès DevForum/Roblox Studio disponible ou un rig de test fourni
autrement.
