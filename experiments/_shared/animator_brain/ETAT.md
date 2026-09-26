# ÉTAT de la piste animation / VFX (Roblox R6) — point d'entrée

**Lire ce fichier EN PREMIER pour toute session sur l'animation, les VFX ou
une cinématique.** Il dit où on en est, quoi lire ensuite, et où tout se
trouve. (Créé à l'audit mémoire du 2026-09-26 : `docs/worklog.md` ne
parlait pas du tout de cette piste ; une nouvelle session ne pouvait pas
savoir où on en était sans l'historique de conversation.)

## 1. Où on en est (mettre à jour à chaque livraison)

- **Dernière production** : Poing du Dragon **v13e**, noté **8/10** par Milan
  (2026-09-26 07:13) : « c pas premium mais c’est mid haut ». Dossier
  `experiments/r6_poing_dragon/` (README, section v13e) ; vidéo
  `captures/verification/2026-09-25-v13e-scene-complete-avec-son.mp4` ;
  lecteur publié https://claude.ai/artifact/WgP5jvhPYePHwnjePvsJ5E.
- **Historique des notes** : `notes_milan.jsonl` (v12 : 4 ; v13d : 7,85 ;
  v13e : 8). Animation du perso jugée ~7,7-8 depuis la v12 ; les VFX ont
  été le point faible (2-4 en v12).
- **Question ouverte de Milan** : passer sur Roblox Studio (plugin, ses
  stocks de VFX, suivre des tutos de A à Z). Analyse :
  `corpus/recherche/STUDIO_FREIN_2026-09-26.md`.
- **Cinématique en cours : « Un seul coup »** (Serious Punch ; proposition 1,
  choisie par Milan le 2026-09-26). Fiche `corpus/fiches/UN_SEUL_COUP.md` ;
  production `experiments/r6_un_seul_coup/` (README) ; vidéo
  `captures/verification/2026-09-26-un-seul-coup-scene-complete-avec-son.mp4` ;
  lecteur https://claude.ai/artifact/NhbCvzUSuGwqc4BSvcEYpE. v1 : retour
  de Milan (départ trop lent, « frappait vers le bas ») -> **v2** (départ en
  3 images, sol cassé, charge buste qui tourne, coup à plat ; vidéo
  `2026-09-26-un-seul-coup-v2-scene-complete-avec-son.mp4`) -> **7/10** :
  départ ultra rapide validé ; le POING CHARGÉ n'est toujours pas le
  mouvement qu'il veut -> clip reçu (Pew + TSB) -> **v3** : le poing chargé
  en arc tendu (fiche UN_SEUL_COUP §7, CARNET 2.10 ; vidéo
  `2026-09-26-un-seul-coup-v3-scene-complete-avec-son.mp4`) -> « aucun
  changement » : c'est la POSE de charge -> **v4** : charge RAMASSÉE (buste
  courbé 57°, tête basse, bras écartés sous le buste ; fiche UN_SEUL_COUP §8 ; vidéo
  `2026-09-26-un-seul-coup-v4-scene-complete-avec-son.mp4`) -> comparaison
  aux refs (fiche UN_SEUL_COUP §9) -> « le bras n'est jamais tendu derrière, c'est le buste
  qui tourne ; jambes trop abusées » -> **v5** : poings sur les côtés, buste
  tourné, gros plans (fiche UN_SEUL_COUP §10 ; vidéo
  `2026-09-26-un-seul-coup-v5-scene-complete-avec-son.mp4`). Prédiction 7,8.
- **Prochaine étape** : le retour de Milan sur « Un seul coup » ; il veut
  encore 1-2 animations ici avant de passer sur Roblox Studio (il dira quand).

## 1b. Chantiers en cours (2026-09-26, après la v5 notée 7,5)

Chantiers, dans cet ordre de livraison :

1. **Poing chargé géométrique -> v6 d'« Un seul coup » (LIVRÉE, fiche UN_SEUL_COUP §11, prédiction 7,9)** : mesures R6
   exactes des anims TSB + pack, reconstruction 3D de chaque ref par
   rendu-comparaison (`outils/geo_pose.py`), notre v5 mesurée, vérification
   adverse ; puis synthèse -> fiche UN_SEUL_COUP §11 -> v6 -> preuves.
   Déjà fait : `verify_export.py` n'a plus de règles de style en vrai/faux
   (mesures de pose sans verdict).
2. **Audit du cerveau** (« appris pour de vrai ou à moitié ? ») : 8 lecteurs
   (tutos, refs, manga/principes, code, retours, productions, outils pros,
   règles gravées) + contradicteurs -> `corpus/recherche/AUDIT_CERVEAU_2026-09-26.md`.
3. **Réorganisation du cerveau inspirée de Hermes Agent** (Nous Research,
   MIT ; cloné en lecture dans `/home/user/nousresearch/hermes-agent`) :
   mémoire bornée, compétences qui s'améliorent, curateur, preuves,
   rappel -> plan proposé à Milan, puis appliqué.
   Fait (2026-09-26) : A0 NOYAU + budget ; A1 amorce (hook SessionStart,
   accord de Milan) ; A2 moisson de ses mots exacts ; A3 marques CONTREDIT ;
   A4 rappel réparé (26 cas connus, `tests/rappel_selftest.py`) ; A5 fiches
   au modèle ; A6 motifs (`outils/motifs.py`, extraits vérifiés mot pour mot,
   statut calculé sur les versions qu'il a VUES) ; A7 lint consultatif ;
   A8-A9 registre de preuves, branché dans `verify_export.py` d'Un seul
   coup ; A10 rapport de regard, revue après retour, déplacer.
   Reste : brancher le registre dans les autres productions (au fil de
   l'eau), puis le chantier 4.

4. **Se renourrir réellement de TOUT le contenu envoyé** (demande de Milan,
   à faire une fois 1-3 finis, avec la nouvelle organisation) : toutes ses
   refs (vidéos, GIF, images, manga, captures) et tous les tutos, relus pour
   de vrai. Quatre buts : apprendre ; comprendre ; pouvoir REFAIRE (chaque
   technique ou pose clé reproduite en R6 et mesurée avec `geo_pose`, à côté
   de la ref) ; affiner l'œil critique (prédire ce qu'on voit, puis comparer).
   Ce qui en sort reste des apprentissages, pas des règles.
   **Lancé le 2026-09-26** après la v6 (« c trjs pas bon ») : 12 lecteurs
   en 3 groupes, chacun suivi d'un vérificateur adverse. A : données
   exactes des pros (TSB 13 anims, pack 19) vues clé par clé avec le nouvel
   outil `outils/planche_cles.py`, dont un exercice d'œil à l'aveugle
   (Stoic Bomb : prédire depuis la vidéo, puis ouvrir les clés). B : tutos
   (méthode de travail, pro contre noob, critiques du DevForum, techniques
   anime). C : vidéos TSB (dont les anims abandonnées sans effets), clips
   de jeux, GIF, images fixes et le goût de Milan d'après ses mots. Notes
   brutes dans le scratchpad (`c4/notes/`), synthèse versionnée ensuite.
   Non couvert à ce tour : les tutos VFX pure (particules, flipbooks),
   déjà étudiés le 2026-09-25.
   **Fait (2026-09-26)** : 12 notes vérifiées dans `corpus/etude_c4/`,
   synthèse contrôlée `corpus/etude_c4/SYNTHESE.md` (cours en 9 chapitres,
   38 lectures démenties, mes erreurs d'œil, la v6 relue avec 6 constats
   mesurés et 7 hypothèses, 3 exercices « pouvoir refaire ») ; 7 dépôts
   de Milan pour les yeux : `corpus/recherche/depots_yeux_2026-09-26/`.
   Suite : les exercices (refaire TSB M1 de zéro ; prédiction à l'aveugle
   au cadrage de jeu), puis les briques d'yeux retenues (côte à côte à
   vitesse réelle calé sur le contact, questions oui/non à l'aveugle).

**Nettoyage du cerveau (2026-09-26, avant les exercices)** : citations de
Milan remplacées par ses mots exacts datés (ou marquées comme paraphrase,
sans guillemets) ; une ligne « Statut : » sur chaque entrée du CARNET et chaque
section de fiche ; garde-fous annoncés mais absents du code corrigés
(annoncés, absents du code au 2026-09-26) ; les lectures démenties de
`corpus/etude_c4/SYNTHESE.md` §2 marquées CONTREDIT sur place ; textes
COLLÉS de `corpus/milan_verbatim.jsonl` corrigés dans
`corpus/milan_verbatim_corrections.jsonl` (appliqué par `outils/motifs.py`,
`outils/lint_cerveau.py`, `outils/amorce.py`). `python3 outils/lint_cerveau.py`
pour le compte à jour.

Scripts des analyses (hors dépôt, session) : `wf_mesure.js`, `wf_audit.js`,
`wf_hermes.js` dans le dossier scratchpad `poing/`.

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
