# ÉTAT de la piste animation / VFX (Roblox R6) — point d'entrée

**Lire ce fichier EN PREMIER pour toute session sur l'animation, les VFX ou
une cinématique.** Il dit où on en est, quoi lire ensuite, et où tout se
trouve. (Créé à l'audit mémoire du 2026-09-26 : `docs/worklog.md` ne
parlait pas du tout de cette piste ; une nouvelle session ne pouvait pas
savoir où on en était sans l'historique de conversation.)

## 1. Où on en est (mettre à jour à chaque livraison)

- **Dernière production** : Poing du Dragon **v13e**, noté **8/10** par Milan
  (2026-09-26) : « pas premium mais mid haut ». Dossier
  `experiments/r6_poing_dragon/` (README, section v13e) ; vidéo
  `captures/verification/2026-09-25-v13e-scene-complete-avec-son.mp4` ;
  lecteur publié https://claude.ai/artifact/WgP5jvhPYePHwnjePvsJ5E.
- **Historique des notes** : `notes_milan.jsonl` (v12 : 4 ; v13d : 7,85 ;
  v13e : 8). Animation du perso jugée ~7,7-8 depuis la v12 ; les VFX ont
  été le point faible (2-4 en v12).
- **Question ouverte de Milan** : passer sur Roblox Studio (plugin, ses
  stocks de VFX, suivre des tutos de A à Z). Analyse :
  `corpus/recherche/STUDIO_FREIN_2026-09-26.md`.
- **Prochaine étape** : choisir la nouvelle cinématique parmi les 3
  propositions de `PROPOSITIONS_CINEMATIQUE_2026-09-26.md`, puis écrire sa
  fiche dans `corpus/fiches/` AVANT toute clé.

## 2. Démarrer une session sur cette piste (ordre)

1. ce fichier ;
2. les 3 dernières entrées de `RETOURS.md` (retours de Milan, datés) et la
   dernière ligne de `notes_milan.jsonl` ;
3. `python3 outils/rappel.py "<concept>"` : il sort d'abord la FICHE de
   conception du moment, puis les outils, puis les passages ;
4. la fiche du moment dans `corpus/fiches/` (si elle n'existe pas :
   l'écrire avant de poser la moindre clé) ;
5. chaque ref citée : la chercher dans `corpus/CATALOGUE_REFS.md`.

## 3. Carte du cerveau (`experiments/_shared/animator_brain/`)

**Vivant (on lit, on écrit) :**

| fichier | rôle |
|---|---|
| `ETAT.md` | ce fichier : où on en est, carte, commandes |
| `RETOURS.md` | les retours de Milan, en ordre chronologique, avec ce qui a été fait |
| `notes_milan.jsonl` | les notes chiffrées + mots exacts + écart de prédiction (lu par `critic.py`) |
| `corpus/CARNET.md` | les APPRENTISSAGES (pas des règles), numérotés par thème (1 voir, 2 coup, 3 3D/anime, 4 caméra, 4b VFX, 5 pistes, 6 biais) |
| `corpus/fiches/*.md` | une fiche de conception par MOMENT (coup chargé, aura dragon, plein écran, VFX, Poing du Dragon v13) : toutes les sources digérées ensemble |
| `corpus/CATALOGUE_REFS.md` | toutes les refs de Milan (empreinte, contenu, où elles sont étudiées) ; les fichiers eux-mêmes ne sont jamais versionnés |
| `corpus/RELECTURE_*.md` | relectures de refs à 0,1 s (Last Breath, Goku, Suiryu, VFX, style) |
| `corpus/recherche/` | recherches (jugement, VFX : éditeurs, MCP Studio, particules…) |
| `corpus/tutos/` | études de tutos (vidéo, Moon, Blender, DevForum) |
| `corpus/clips/*.json` | mesures de vidéos (juge, durées) |
| `outils/` | `rappel.py` (mémoire), `juge.py` (proportions de temps contre refs), `allure.py` (vitesse d'un dragon/serpent en corps/s), `durees.py` (bandes 0,1 s), `corps_bras.py`, `tour.py`, `regard.py`, `ecoute.py` (son), `planche_ref.py`, `planche_vfx.py`, `poselab.py`, `moon.py`, `vues.py`, `draw.py` |
| `critic.py`, `hypotheses.json`, `etats*.py/json` | le jugement calculé (biais de prédiction, hypothèses) |
| `rules.py`, `audit.py`, `constraints.py`, `organic.py`, `tracks.py`, `poses.py`, `rig_math.py`, `v222_rig.py`, `roblox_export.py` | le code du rig et des mesures de mouvement (doc : `README.md`) |

**Historique (daté, ne plus suivre comme protocole ; utile pour comprendre
d'où vient une décision)** : `LECONS.md`, `CERVEAU_V2.md`, `PLAN.md`,
`REFLEXION.md`, `ANGLES_MORTS.md`, `SCENE_POING_DU_DRAGON.md` (v1),
`corpus/ETUDE_*.md`, `corpus/TUTOS_ANIMATION.md`, `corpus/REFERENCES_VIDEO.md`.
Ce qu'ils contiennent de vivant est passé dans `CARNET.md` et les fiches.

**Hors du cerveau** : studio VFX `experiments/_shared/vfx_studio/` (recettes,
labo three.js, `VFXStudio.luau`, modèle du dragon) ; productions
`experiments/r6_*` (une par dossier, chacune avec son README) ; preuves
`captures/verification/` (toujours committées avec le changement).

## 4. Commandes (Poing du Dragon, à adapter)

```bash
B=<chemin>/Blender_R6.blend                          # rig V2.22
DRAGON_FINAL=v13 python3 experiments/r6_poing_dragon/scripts/verify_export.py $B   # export + contrôles (~2 min)
cd experiments/r6_poing_dragon/scripts
python3 staging.py && python3 build_player.py && python3 build_roblox_package.py
python3 ../luau/run_sens_test.py <luau>               # test de sens (Luau)
python3 video_son.py <sortie.mp4> cinema 30           # vidéo avec son (~25 min)
python3 ../../_shared/animator_brain/outils/juge.py mesurer <mp4> <json> && ... juger <json>
python3 ../../_shared/animator_brain/outils/allure.py ../output/staging.json
python3 ../../_shared/animator_brain/outils/durees.py <mp4> <png> 0.1 <t0> <t1>
# studio VFX
cd experiments/_shared/vfx_studio && python3 build_lab.py && python3 luau/run_test.py <luau> && python3 compile_roblox.py
# auto-tests du rig (ils veulent leurs arguments)
python3 experiments/_shared/animator_brain/tests/v222_two_rigs_selftest.py $B <dossier_sortie>
python3 experiments/_shared/animator_brain/tests/v222_export_selftest.py $B <sortie.rbxmx>
```

## 5. Problèmes connus encore ouverts (Poing du Dragon)

- La morsure (f380-402) reste chargée : crinière + flammes se mélangent.
- Les 3 dernières secondes sont statiques ; la scène reste sombre.
- Petits enfoncements au sol : jambe d'appui 0,13 stud (rafale, 3 images),
  bras de la victime 0,14 stud au fond du cratère.
- Le juge temporel (`juge.py`) mesure le style « plein écran » de Last
  Breath, que Milan a retiré : il échoue par construction sur ce style
  (CARNET 4b.29).

## 6. Règles de la piste (rappel, source : CLAUDE.md + mandat)

- toujours répondre à Milan en français ;
- jamais committer de refs sous droits (vidéos, GIF, fichiers TSB, packs
  achetés) : seulement des données dérivées ;
- ne jamais écrire `data/labels/quality_labels.jsonl` ;
- toute capture citée comme preuve : `captures/verification/<date>-<sujet>.png`
  dans le même commit ;
- vérifier dans les conditions du spectateur (CARNET 4b.28) ;
- donner une prédiction chiffrée AVANT de montrer (biais mesuré par
  `critic.py`).
