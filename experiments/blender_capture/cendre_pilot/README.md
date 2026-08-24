# Pilote migration 3D Cendre — clôture (2026-08-23)

## Objectif et verdict

Mandat : tester si le pipeline 3D Meshy/Blender déjà éprouvé sur les 3
monstres (Crawler/Brute/Ranged) pouvait remplacer le pipeline 2D
PixelLab pour Cendre, sur un livrable pilote (combo de base, 3 coups),
sans généralisation ni bascule en jeu.

**Verdict final de Milan après 6 rounds de test mesuré : on arrête la
migration 3D pour Cendre.** Pas un échec de méthode — le pilote a
rempli son rôle : répondre honnêtement à « la 3D est-elle prête à
remplacer le 2D pour Cendre ? » par « s'en approche, ne l'égale pas à
64px réel ». Le correctif suivant connu (épaissir les bras dans le
maillage) changerait de nature — retouche du modèle, plus un réglage de
rendu — donc sort du cadre de ce pilote. Détail complet, chiffré et
mesuré round par round : entrée `docs/worklog.md` du 2026-08-23
« MANDAT MIGRATION CENDRE ».

Aucun fichier réel du dépôt (assets/manifests de production) n'a été
modifié par les 6 rounds — chaque test a tourné en scratch isolé,
vérifié à chaque fois. Rien à annuler.

## Ce qui a marché

- **Auto-rig Meshy réussi du premier coup** sur un bipède standard —
  aucun contournement manuel nécessaire, contrairement au Crawler/Brute
  (échecs 422 en pose estimation). Commit `5e62dc0`.
- **Fix skinning épaule** (`fix_shoulder_hem_skinning()`,
  `experiments/blender_capture/render_combo_cendre.py`) : l'ourlet de
  tunique était collé au poids de l'os `RightHand`/`LeftHand` en pose
  de repos (heat-weighting par proximité, pas par la rotation en
  elle-même). Commit `7421ff1`.
- **Fix skinning hanche** (`fix_hip_hem_proximity()`, même fichier) :
  mécanisme DIFFÉRENT du fix épaule — 605 sommets restaient dominés par
  `RightHand`/`LeftHand` même après le fix épaule ; ce n'était pas un
  problème de distance 3D (l'abduction à 90° augmente la distance mais
  pas le poids recalculé) mais un pan entier de tunique mal rattaché,
  isolé par filtre sur le Z de repos. 6959 sommets réassignés. Commit
  `888a51a`.
- **`quantize.py --pixelate_mode=mean_alpha`** (moyenne de bloc pondérée
  par alpha, au lieu de l'échantillon central) : **reste actif et
  généralisé, ne pas défaire** — améliore aussi les 3 monstres (IoU de
  silhouette 0.89-0.99 vs l'ancien mode, aucune régression trouvée),
  déjà le défaut de `experiments/blender_capture/quantize.py`. Commit
  `888a51a`.
- **Posterisation HSV (canal Value seul) du matériau importé** +
  spécularité réduite (`flatten_material_specular()`,
  `render_combo_cendre.py`) : réglage de rendu en mémoire (aucune
  texture modifiée sur le disque) qui a fait passer le pilote de
  « moins lisible que le PixelLab » à « s'en approche » à 64px réel.
  Commit `635cd3b`.

## Ce qui n'a PAS suffi, et pourquoi

**Lisibilité à 64px réel reste en retrait du PixelLab**, malgré
l'amélioration du round 3 (matériau aplati). Deux causes identifiées
par la mesure, pas supposées :

1. **Cause principale : texture d'albédo/émission haute fréquence.**
   La texture embarquée dans le GLB (`texture_0`, 2048px) est une
   mosaïque de patches gris/noir/crème/beige de quelques dizaines de
   pixels, branchée à la fois sur Base Color ET Emission
   (Emission Strength=1.0, quasi indépendante de l'éclairage). À
   l'échelle du rendu (~400px de haut), chaque patch occupe 1-3px —
   exactement la taille du bruit « poivre et sel » observé après
   downscale à 64px. Voir `mat_round3/texture_small_preview.png`
   (aperçu réduit ; texture pleine résolution régénérable via
   `mat_round3/export_texture.py`, non gardée pour le volume).
2. **Cause secondaire : proportions de bras trop fines** pour ce style
   de compression pixel-art à 64px.

**Piste connue, non tentée, HORS CADRE de ce pilote** : épaissir le
maillage du bras. C'est une retouche du MODÈLE, pas un réglage de
rendu — changerait de nature de tâche, mandat explicitement limité à
« aucune régénération Meshy, seulement rendu/matériau/quantize/cook ».

## Si ce chantier est repris un jour

**Réutilisable tel quel** :
- `cendre_combo.glb` — le GLB déjà remeshé (250k polys), riggé
  (auto-rig Meshy) et animé (action `Punch_Combo`, mocap coups 1+2,
  coup 3 posé à la main sur le même squelette). Réutiliser directement
  avec `experiments/blender_capture/render_combo_cendre.py
  --glb=cendre_combo.glb` évite de repayer modèle+remesh+rig+animate
  (~43cr Meshy). Les fixes de skinning (épaule/hanche) et le matériau
  aplati sont déjà appliqués EN MÉMOIRE par ce script à chaque rendu —
  rien à réappliquer manuellement au GLB lui-même.
- **Le facteur de downscale LANCZOS 0.647** (hauteur cible 56px,
  mesurée sur `idle_south/0.png`, bbox source 86.5px moyenne sur les
  frames de contact quantifiées à 112px) — revalider si le personnage
  ou le cadrage caméra change, mais point de départ correct pour
  Cendre.
- **La méthode de test via `scripts/cook_character_frames.py`**
  isolé en `--repo-root` scratch (jamais modifié, jamais touché aux
  fichiers réels) — voir `mat_round3/prep_and_cook_final.py` pour
  l'exemple complet (adapter les chemins `ROOT`/`SCRATCH` en tête de
  fichier, spécifiques à la session qui l'a écrit).
- Les scripts de diagnostic de skinning (`diag_defect1.py`,
  `diag_defect1/inspect_shard_weights.py`,
  `quantize_regression_round2/inspect_hip_shard.py`) si un futur
  personnage/animation montre le même symptôme de bavure aux
  articulations.

**Probablement à refaire depuis zéro** : le modèle et sa texture, si le
chantier reprend sur un AUTRE personnage (proportions/texture
spécifiques à Cendre). Si le chantier reprend sur CENDRE avec une
texture retravaillée (moins haute fréquence) ou un maillage de bras
épaissi, le GLB riggé ci-dessus reste probablement valide — seule la
texture/le maillage source changerait, pas le rig ni l'animation.

## Fichiers conservés dans ce dossier et leur rôle

| Fichier | Rôle |
|---|---|
| `cendre_combo.glb` | GLB final : remeshé + riggé + animé (Punch_Combo + coup3 main). Réutilisable tel quel. |
| `calibrate_pose.py` | Calibration empirique d'axe/signe de rotation sur un bone de bras avant pose à la main (le rig Meshy n'a pas de convention d'axe documentée). |
| `calibrate_leg.py` | Même méthode que `calibrate_pose.py`, appliquée à un bone de jambe (préparé, jamais utilisé dans le combo livré — aucune pose de jambe posée à la main n'a été nécessaire). |
| `list_bones.py` | Utilitaire : liste les objets/bones d'un GLB importé. |
| `preview_scout.py` | Rendu scout basse résolution, échantillonnage régulier sur toute l'action, pour repérer les beats anticipation/contact/récupération avant le rendu final pondéré. |
| `preview_scout_frames.py` | Variante de `preview_scout.py` : rendu à des frames explicites (`--frames=`), qualité plus haute, pour inspection rapprochée d'un segment. |
| `tune_coup3_contact.py` | Harnais d'itération rapide pour comparer plusieurs jeux de paramètres d'overshoot (coup3 posé à la main) sans re-rendre tout le combo à chaque essai. |
| `diag_defect1.py` | Harnais de diagnostic multi-mode (baseline/smooth/dupcheck) ayant permis d'éliminer par la mesure les pistes 1 et 2 (influences par sommet, doublons) du défaut de bavure épaule. |
| `diag_defect1/inspect_shard_weights.py` | Identifie les sommets à déplacement anormal bind→contact et leurs poids de squelette — a isolé la cause réelle du défaut épaule (proximité de bind-pose, pas la rotation). |
| `diag_defect1/list_objects.py` | Utilitaire : liste mesh/vertex groups d'un GLB importé. |
| `quantize_regression_round2/inspect_hip_shard.py` | Même méthode que `inspect_shard_weights.py`, appliquée après le fix épaule pour diagnostiquer l'écharde résiduelle à la hanche (mécanisme différent, filtre sur le Z de repos). |
| `mat_round3/inspect_materials.py` | Inspecte le graphe de matériaux d'un GLB importé (a révélé `Material_1` : Metallic=1.0, texture unique branchée sur Base Color ET Emission). |
| `mat_round3/export_texture.py` | Exporte `texture_0` (la texture embarquée) depuis un GLB vers un PNG, pour inspection directe. |
| `mat_round3/prep_and_cook_final.py` | Pipeline complet round 3 : downscale LANCZOS ×0.647 des frames de contact quantifiées 112px, puis cuisson via le vrai `scripts/cook_character_frames.py` en `--repo-root` scratch isolé. Chemins `ROOT`/`SCRATCH` à adapter à la session qui reprend. |
| `mat_round3/build_final_capture.py` | Construit la planche de comparaison 3 blocs (coup1/2/3 : 2 frames 3D cuites 64px + 1 référence PixelLab), même format que `captures/verification/2026-08-23-cendre-migration-3d-round3-materiau-aplati-cuit-64px-reel.png`. |
| `mat_round3/texture_small_preview.png` | Aperçu réduit de la texture d'albédo/émission du personnage — preuve visuelle de la cause principale (mosaïque haute fréquence) citée ci-dessus. |
| `combo_quantized_v4/` | 6 frames de contact (2 par coup) quantifiées à 112px avec le matériau aplati round 3 — données d'entrée d'exemple pour `mat_round3/prep_and_cook_final.py`, pour qu'il reste exécutable sans devoir tout re-rendre. |

## Ce qui a été supprimé du scratch, et pourquoi

Le répertoire de travail des 6 rounds pesait ~139 Mo (rendus bruts,
quantifications intermédiaires par round, scouting, tests de
calibration jetables, texture pleine résolution, GLB pré-remesh).
Ramené à ~22 Mo (dont 21 Mo pour `cendre_combo.glb`, le seul gros
fichier réellement réutile). Supprimé :

- `cendre_raw.glb` (58 Mo, pré-remesh/pré-rig) et
  `cendre_raw_base_color.png` (4,4 Mo) — entièrement supersédés par
  `cendre_combo.glb` (remeshé+riggé+animé), aucune raison de repartir
  du modèle brut.
- `combo_render/`, `combo_render_v2/`, `combo_render_v3/`,
  `combo_render_v4/` (rendus bruts 512px des 42 frames, un dossier par
  round, ~32 Mo cumulés) et `combo_quantized/`,
  `combo_quantized_64/`, `combo_quantized_112_v2_before/`,
  `combo_quantized_112_v3_after/`, `old_quantized_64/`,
  `quantize_tests/` — rendus intermédiaires jetables, chaque round
  supersède le précédent ; les captures de comparaison AVANT/APRÈS de
  chaque round restent committées dans `captures/verification/`.
- `scout/`, `scout2/`, `scout3/` + `scout*_sheet.png`,
  `scout_contact_sheet*.png` — planches de scouting, ont servi une
  fois pour localiser les beats du clip `Punch_Combo`, sans valeur de
  reprise (les frames retenues sont documentées dans
  `render_combo_cendre.py` et le worklog).
- `test_norim/`, `test_fixed/` — rendus de test A/B pour la rim light
  round 1, jetables.
- `quantize_regression_round2/` (hors `inspect_hip_shard.py`) —
  scripts et rendus de la vérification de non-régression sur les 3
  monstres, faite une fois, résultat déjà consigné dans le worklog
  (IoU 0.89-0.99, aucune régression).
- `mat_round3/` (hors les 4 scripts et l'aperçu texture listés
  ci-dessus) — itérations de matériau (`iter0`/`iter1`/`iter2`/`iter3`)
  et planches de comparaison, décision déjà prise et documentée
  (`iter2b` retenu), texture pleine résolution (6,4 Mo) régénérable
  via `export_texture.py` si nécessaire.
- `cal_*.png`, `crop_*.png`, `tight_*.png`, `posture_check.png` —
  images de calibration/vérification visuelle à usage unique.
- `build_comparison.py`, `build_validation_capture.py` (racine) —
  versions round 1 des scripts de planche de comparaison, supersédées
  par `mat_round3/build_final_capture.py` (même rôle, état final).
- `quantize_batch.sh`, `quantize_batch_64_final.sh`,
  `quantize_old_64.py`, `check_fps.py` — utilitaires ponctuels sans
  valeur de reprise.
- Fichiers `.import` (cache Godot auto-généré par le scan du
  répertoire) et deux textures auto-extraites par cet import
  (`cendre_combo_texture_0.png`, `cendre_raw_0.jpg`) — artefacts, pas
  du contenu produit.

## Ce qui reste actif ailleurs (ne pas toucher)

- Le pipeline 3D complet reste fonctionnel et utilisé pour les 3
  monstres (Crawler/Brute/Ranged) — aucun changement.
- `experiments/blender_capture/quantize.py
  --pixelate_mode=mean_alpha` reste le défaut général du pipeline
  pixel-art (généralisé, non régressif, commit `888a51a`).
