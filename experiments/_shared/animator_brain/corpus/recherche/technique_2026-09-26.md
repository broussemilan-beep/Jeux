# Technique du 2026-09-26 : preuves, marqueurs à l'export, sens de l'easing

Chantier « preuves et technique », lancé en autonomie (accord de Milan du
2026-09-26 : « Lancé en auto »). Trois points. Pour chacun : ce qui est
fait, la preuve, ce qui reste ouvert. Ce sont des contrôles techniques. Aucun
n'est une règle de style.

## 1. Registre de preuves branché dans les autres productions

**Fait.**
- `outils/preuves.py` :
  - nouveau type `mesure_technique` : contact, sol ou structure MESURÉS
    sans seuil. Ce sont des valeurs à lire, jamais un « passe » ;
  - nouvel assistant `executer_et_enregistrer(...)` : il lance le `main`
    d'un vieux script, laisse sa sortie s'afficher, la capture, puis écrit
    une ligne. Le script ne change pas de comportement ;
  - **bug corrigé** : `git status --porcelain` passait par `strip()`, ce
    qui coupait la 1re lettre du 1er chemin de `entrees_hors_commit`
    (« xperiments/… »). Le bug est apparu sur la 1re ligne du Dragon,
    celle-ci a été corrigée en place avant tout commit (le contrôle
    `croissance` reste « ok »).
- **Poing du Dragon** (`r6_poing_dragon/scripts/verify_export.py`) : une
  ligne `technique` est écrite AVANT l'arrêt éventuel du script.
  - « passe » si les contrôles de sens Roblox et d'interpolation (déjà
    bloquants) passent ET si l'aller-retour moteur reste sous 0,001 stud ;
  - le résumé de la ligne porte aussi, comme valeurs : le sol, les
    contacts, l'écart de réduction et les noms des marqueurs relus.
- **M1 V2.22** (`r6_m1_v222/scripts/verify_export.py`) : même branchement.
- **Anciens prototypes d'avant V2.22**, branchés sur `mesure_technique` :
  - leurs scripts `calibrate.py` : `r6_black_hole`, `r6_directional_punch`,
    `r6_divine_descent`, `r6_divine_orb`, `r6_hit_combo`, `r6_rock_kick`,
    `r6_solar_smite`, `r6_throne_crown` ;
  - leurs scripts de pieds : `r6_hit_combo/foot_check.py`,
    `r6_battle_throne/calibrate_battle.py` et `foot_check_battle.py`.
- **`r6_aerial_kick_combo/verify_joint_frames.py`** : c'est un vrai
  auto-test, avec des `assert` et un aller-retour par l'équation du moteur.
  Il est donc branché en `technique`.
- Toutes les productions `r6_*` ont maintenant un script de vérification
  branché, sauf `r6_un_seul_coup`, déjà branché auparavant (et hors de ce
  chantier).

**Preuve.** 14 lignes ajoutées à `corpus/preuves.jsonl` par les outils
eux-mêmes :
- Dragon : `technique passe` (l.3) ;
- M1 : `technique passe` (l.4) ;
- 11 lignes `mesure_technique` ;
- aerial kick : `technique passe`.

`python3 outils/preuves.py statut r6_poing_dragon` les lit.

**Reste ouvert.**
- La relance du Dragon a réécrit `dragon_attaquant.rbxmx` avec des écarts
  en virgule flottante.
  - Taille des écarts : 131 valeurs sur 28 621 diffèrent, de 5e-8 à
    3,3e-5 au plus. `dragon_victime.rbxmx` diffère à ~1e-15.
  - Ces écarts viennent de la cuisson Blender (float32), pas du code :
    deux relances ici donnent les mêmes octets, et l'ancien export
    appliqué aux mêmes cadres aussi.
  - Conséquence : si ces fichiers ne sont pas committés avec la ligne de
    preuve, celle-ci se lira « périmée ».
- `r6_hit_combo` et `r6_battle_throne` ont deux scripts du même type.
  - `statut` ne montre que la dernière ligne ;
  - `statut --tout` montre l'historique.

## 2. KeyframeMarker à l'export (`roblox_export.write_kfseq`)

**Constat.** Le paramètre `markers=[(t, nom, valeur)]` existait déjà. Il
accrochait chaque marqueur à la clé de pose la PLUS PROCHE, quel que soit
l'écart. Les fichiers TSB, eux, posent leurs marqueurs sur des Keyframes
VIDES hors grille, sans aucune Pose (lu dans le .rbxm le 2026-09-26). Deux
exemples :
- M2 `hitreg` à 0,1733 s ;
- Collateral Ruin `StartHitbox` à 1,2554 s.

Les clés vides TSB s'appellent « Keyframe ». Voir `etude_c4/A1` §V5 et
`A2` §5.

**Fait.**
- **Marqueur à une clé de pose près** : si une clé de pose tombe à moins
  de `marker_tol` (1e-4 s) du marqueur, celui-ci va dessous (comme avant).
- **Sinon, clé vide** : un Keyframe vide « Keyframe » est créé exactement
  au temps voulu. Deux marqueurs au même temps partagent la même clé vide.
- **Ordre du fichier** : les Keyframes sont rangés par temps.
- **Marqueur invalide** (temps négatif ou nom vide) : `ValueError`.
- **Lecture** :
  - `read_kfseq` ignore les clés sans Pose, donc l'aller-retour moteur
    (`roundtrip_error`), `vues.lire_kfseq` et le rééchantillonnage du
    Dragon ne voient jamais de pose vide ;
  - nouveau `read_markers(path)`, qui renvoie `(t, nom, valeur)`.
- **Hors de la grille des poses** : une clé vide ne change aucune pose.
  Placée après la dernière clé, elle allonge la durée de l'anim, pendant
  laquelle la pose est tenue.
- **Format** : `Item class="KeyframeMarker"` enfant du Keyframe, avec
  `string Name` et `string Value`. En jeu, `GetMarkerReachedSignal(nom)`
  reçoit `Value` en paramètre.

**Preuve.** Le test `tests/export_marqueurs_selftest.py` (16 contrôles,
tous passent) :
- **Octet pour octet** avec l'export d'avant (`roblox_export.py` du commit
  `ec29327`, relu dans git et exécuté) :
  - sans marqueur ;
  - avec marqueurs sur des clés ;
  - avec poids nul et boucle.
- **Clés vides** : bons temps, marqueurs relus par `read_markers` et par
  `outils/rapport_regard.lire_marqueurs`.
- **Aller-retour moteur** : 2e-14.
- **Sur les VRAIS cadres du Dragon** (relance de `verify_export.py`, chaque
  `write_kfseq` doublé par celui d'avant) : identique octet pour octet.
  - attaquant : 15 marqueurs, 1 772 880 octets ;
  - victime : sans marqueur, 1 146 335 octets.
- **Nos exports actuels** : tous les marqueurs d'Un seul coup (10), du
  M1 (3) et du Dragon (15) sont posés sur des clés de pose, grâce aux
  `keep_times` forcés. Aucune production existante ne change.

**Reste ouvert.**
- **Studio** : non vérifié dans Studio (on n'y passe que quand Milan le
  dit). Un .rbxmx avec des clés vides s'importe-t-il sans les fusionner,
  et le signal part-il au bon temps ?
- **Doc Roblox** : `create.roblox.com` est bloqué par le proxy de ce bac
  à sable. Le format de la classe n'a donc pas été relu dans la doc. Il a
  été relu dans les fichiers TSB (lecture binaire) et dans nos propres
  exports déjà livrés.
- **`outils/planche_cles.py --rbxmx`** :
  - ce qui marche : il ouvre un fichier à clés vides sans planter ;
  - ce qui manque : il ne relit PAS les marqueurs de nos .rbxmx
    (`"marqueurs": []`) ;
  - le correctif tient en une ligne dans `cles_rbxmx`
    (`X.read_markers`), mais ce fichier est hors de ce chantier.

## 3. Sens de l'easing des Poses (`corpus._ease`)

**Constat.**
- **Valeurs** : PoseEasingDirection vaut 0 In, 1 Out, 2 InOut.
  PoseEasingStyle vaut 0 Linear, 1 Constant, 2 Elastic, 3 Cubic,
  4 Bounce, 5 CubicV2.
- **Inversion documentée** : la doc de l'Enum PoseEasingDirection dit :
  « for legacy compatibility reasons, the use of In and Out are backwards
  from how these terms are used by most other animation tools and by
  TweenService ». Cette phrase a été lue dans les extraits de recherche,
  car la page elle-même est bloquée ici.
- **Confirmation** : le DevForum « Animation cubic easing direction
  reversed » (devforum.roblox.com/t/449068, 2020-02-02) montre qu'une Pose
  Cubic « In » se comporte en jeu comme un « Out ». InOut, Elastic et
  Bounce ne sont pas concernés.
  - Roblox a répondu en octobre 2021 : pas de correction possible sans
    casser les anims existantes.
  - Le fil « Keyframe easing direction is inverted » (/t/2630212, 2023)
    signale la même inversion entre l'aperçu de l'éditeur et le jeu.
- **Notre ancien `_ease`** appliquait le sens de TweenService, donc
  inversé.

**Fait.** `_ease` a été corrigé : une Pose « In » (0) part vite et arrive
lentement (1-(1-u)³), une Pose « Out » (1) fait l'inverse (u³). Les
sources et les points ouverts sont notés dans la doc de la fonction.

**Preuve d'absence d'effet passé.** Les fichiers pros ne contiennent
AUCUNE Pose Cubic (comptées le 2026-09-26) :
- TSB : 3 250 Linear et 67 Constant ;
- pack : 5 056 Linear.

Aucune mesure déjà faite ne change donc. Nos exports écrivent tous
Linear (0), ce qui ne dépend pas du sens.

**Reste à vérifier dans Studio.**
- **CubicV2 (5)** : ajouté vers 2024. L'inversion est SUPPOSÉE la même
  que pour Cubic, car la phrase de la doc porte sur l'Enum de direction.
- **Constant (1)** : supposé indépendant du sens. Pourtant, un script de
  contournement du DevForum (449068 #70) inverse aussi la direction des
  Poses Constant.
- **Elastic et Bounce** : toujours approchés par Linear.
