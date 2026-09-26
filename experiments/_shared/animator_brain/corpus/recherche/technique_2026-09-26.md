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
  - Taille des écarts (recompté à la relecture) : sur 28 621 valeurs
    numériques, 16 619 diffèrent du fichier committé avant ; 131 de plus de
    1e-9 (de 1,5e-9 à 3,3e-5 au plus), les autres de 6e-10 au plus.
    `dragon_victime.rbxmx` diffère à ~2e-15 au plus.
  - Ces écarts viennent de la cuisson Blender (float32), pas du code :
    deux relances ici donnent les mêmes octets, et l'ancien export
    appliqué aux mêmes cadres aussi.
  - Conséquence : si ces fichiers ne sont pas committés avec la ligne de
    preuve, celle-ci se lira « périmée ».
- **« passe » ne couvre pas le sol** (relu à la relecture) : la ligne du
  Dragon porte `sol` = -0,16 (attaquant) et -0,143 (victime), alors que la
  docstring du script annonce « aucun coin de partie sous le sol
  (> 0,1 stud) ». Ces valeurs étaient déjà dans `verification.json` avant ce
  chantier (même valeur au commit 0412648) : pas une régression, mais un
  écart au-delà de la tolérance écrite par le script lui-même, que le
  statut « passe » ne signale pas. Même chose pour
  `ecart_max_reduction_studs` = 0,55 stud (poses éparses de la rafale,
  voulues). À trancher : mettre le sol dans « passe » (le NOYAU le range
  parmi les contrôles techniques) ferait passer le Dragon en « echoue ».
- `r6_poing_dragon/scripts/check_rules.py` n'est PAS branché : il passe les
  règles de style apprises (`rules.py`), pas un contrôle technique.
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
  - #56 (2021-10-01, INT_L, qui cite une réponse du staff) : « no easy
    solution that would guarantee that we do not break existing
    animations » ; #66 (2022-05-04, BloxSoMeta, staff) : « we have made the
    decision for now to preserve the reversed behavior for compatibility ».
  - **#85 (2024-10-10, BloxSoMeta, staff) : le correctif, CubicV2.**
    « CubicV2 has the same behavior as Cubic inside the ACE, but reverses
    the direction in the engine to match. » Et « The original "Cubic" style
    is now considered deprecated ». Même chose dans `PoseEasingStyle.yaml`
    (cité dans `corpus/tutos/rapport_roblox_web.md` §2.1).
  - Le fil « Keyframe easing direction is inverted » (/t/2630212, 2023-10-04)
    signale la même inversion entre l'aperçu de l'éditeur et le jeu.
- **Notre ancien `_ease`** appliquait le sens de TweenService, donc
  inversé.

**Fait.** `_ease` a été corrigé, style par style :
- **Cubic (3)** : sens inversé en jeu. Une Pose « In » (0) part vite et
  arrive lentement (1-(1-u)³), une Pose « Out » (1) fait l'inverse (u³).
- **CubicV2 (5)** : sens de l'éditeur et de TweenService. « In » (0) part
  lentement (u³), « Out » (1) part vite.
- **Correction de la relecture** : la 1re version inversait aussi CubicV2.
  C'était faux d'après le post #85 ci-dessus.

Les sources et les points ouverts sont notés dans la doc de la fonction.

**Preuve d'absence d'effet passé.** Les fichiers pros ne contiennent
AUCUNE Pose Cubic (comptées le 2026-09-26) :
- TSB : 3 250 Linear et 67 Constant ;
- pack : 5 056 Linear.

Aucune mesure déjà faite ne change donc. Nos exports écrivent tous
Linear (0), ce qui ne dépend pas du sens.

**Reste à vérifier dans Studio.**
- **CubicV2 (5)** : ajouté le 2024-10-10. D'après #85, il n'est PAS
  inversé en jeu. Pas encore vu en jeu : faire le test de
  `rapport_roblox_web.md` §6 (rotation de 90° sur 30 images, In puis Out).
- **Constant (1)** : supposé indépendant du sens. Pourtant, un script de
  contournement du DevForum (449068 #70) inverse aussi la direction des
  Poses Constant (2022-10-19). Or TSB a 67 Poses Constant, en direction
  In : si le sens compte, nos mesures de ces 67 poses pourraient changer.
- **Elastic et Bounce** : toujours approchés par Linear.

## Relecture adverse (2026-09-26)

- **Revérifié en relançant** : l'auto-test des marqueurs (16 contrôles), les
  statuts du registre et `croissance` ; les empreintes des 16 lignes sont
  égales aux fichiers actuels (aucune preuve périmée). Les comptes d'easing
  des fichiers pros (3 250 + 67 ; 5 056) ont été recomptés avec
  `load_rbxm_sequences` : identiques.
- **Corrigé** : le sens de CubicV2 dans `_ease` (voir §3) ; l'attribution
  de la réponse de 2021 (relayée par un utilisateur, la décision du staff
  date de 2022) ; le compte des écarts du Dragon (§1) ; l'écart de sol
  masqué par « passe » est maintenant écrit (§1, à trancher).
- **Sources** lues à la relecture : le fil DevForum 449068 (pages 1 à 4,
  posts #66, #70 et #85) et le fil 2630212. La doc create.roblox.com et le
  dépôt GitHub `Roblox/creator-docs` restent bloqués ici.
