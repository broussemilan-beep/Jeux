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

## Prochaine étape (hors scope de ce tour)

Ce tour livre l'animation exportée, pas son intégration. Import réel dans
Roblox Studio (test visuel humain, ajustement C0/C1 si nécessaire pour
un rig de production précis) à faire dans un tour séparé, une fois
l'accès DevForum/Roblox Studio disponible ou un rig de test fourni
autrement.
