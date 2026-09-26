# Audit du cerveau d'animation : appris pour de vrai, ou à moitié ?

> **Statut : audit par 8 lecteurs + 8 contradicteurs, 2026-09-26 ; apprentissages, pas règles.**
> Rien ici n'est une loi. Ce sont des constats, avec leur preuve, pour
> savoir quoi nourrir ensuite.

Question de Milan : « Globalement, est-ce que tu as vraiment appris de nos
refs, tutos, images, manga… ou à moitié ? Qu'est-ce qui manque à notre
cerveau pour devenir un outil d'animateur ? »

Méthode. 8 lecteurs ont relu une tranche chacun (refs, règles, outils pros,
retours de Milan, productions, code, tutos, manga/principes). Chaque tranche
a été contre-vérifiée par un contradicteur, qui a corrigé, rétrogradé ou
surclassé les constats. Le détail (170 fiches, une preuve par ligne) est
dans `audit_complet.json`, au scratchpad de la session
(`…/scratchpad/poing/audit_complet.json`) : **non versionné**. Ce document
en garde l'essentiel. Les chemins sont relatifs à
`experiments/_shared/animator_brain/` sauf mention contraire.

---

## 1. Réponse en 5 lignes

1. **170 apprentissages relevés** (avec recoupements : un même savoir vu par plusieurs tranches, ex. les clés espacées dans 5 tranches). Niveau atteint après vérification : **86 appliqués** en production, **50 écrits en code** mais qui ne pilotent pas (ou plus) la production, **11 en nombres** seulement, **23 en mots** seulement.
2. **Effet sur les notes de Milan** (classement du champ « efficace » de chaque fiche) : **26 effet positif démontré**, 29 mitigé, **62 nul ou négatif**, 53 inconnu ou jamais testé.
3. **Appris pour de vrai : le TEMPS** (rythme, lent contre rapide, clés espacées, départ, allure) et la **technique d'export**. C'est là que sont presque tous les gains.
4. **À moitié : la POSE.** Aucune pose de ref n'est mesurée dans le dépôt. Le poing chargé a demandé 5 versions en traduisant des mots en clés. Beaucoup d'outils existent mais ne tournent pas sur la production en cours.
5. **Pas du tout** : les 23 savoirs restés en mots n'ont eu **aucun** effet positif démontré. Et « écrit en code » ne veut pas dire « appris » : 3 sur 50 seulement ont un effet positif.

| Niveau (après vérification) | Nb | effet + | mitigé | nul / négatif | inconnu |
|---|---:|---:|---:|---:|---:|
| appliqué en production | 86 | 22 | 20 | 22 | 22 |
| code (outil écrit, pas branché ou plus branché) | 50 | 3 | 4 | 25 | 18 |
| nombres (mesuré, pas utilisé) | 11 | 1 | 3 | 3 | 4 |
| mots | 23 | 0 | 2 | 12 | 9 |
| **total** | **170** | **26** | **29** | **62** | **53** |

Le niveau vient des lecteurs et contradicteurs. Le classement de l'effet est
le mien, fiche par fiche, à partir de leur champ « efficace » : il reste une
lecture, pas une mesure.

---

## 2. Ce qui est VRAIMENT appris

Point commun : **le temps, mesuré sur un fichier R6 exact ou à pas fixe,
comparé à une ref dans le même repère.**

| Savoir | Preuve | Effet sur la note de Milan |
|---|---|---|
| Lent contre rapide + clés espacées en Linear (comme TSB) sur la rafale | `r6_poing_dragon/scripts/dragon_clip.py:36-52` (`DRAGON_RAFALE="v8,1.4,libre,eparse"` par défaut) ; contraste 0,55-1,49 -> 1,44-2,63, TSB 2,3-4,7 (`RETOURS.md:426-427`) | v8 : 7,5, caméra de jeu 7,8, « le changement de RYTHME se lit de loin » (`notes_milan.jsonl` l.9). Le gain le plus net attribuable à un principe. |
| Variantes x1 / x1,4 / x1,8 jugées côte à côte | `dragon_clip.py:49-65`, 4 variantes, B2 retenue (41861a5) | idem v8 |
| Structure temporelle des ultimes relue à 0,1 s (calme, départ, frappe courte, impact pauvre, conséquence longue) | `corpus/fiches/UN_SEUL_COUP.md:23-33` -> `r6_un_seul_coup/scripts/coup_clip.py:41-53` | Départ en 3 images : « le moment ultra rapide, très bien » (`RETOURS.md:796`). Structure jamais critiquée. |
| Allure du dragon en corps/s et °/s | `outils/allure.py` ; vol rapide 83 % -> 33 % (`r6_poing_dragon/README.md:941-944`) | 7,85 -> 8 (`notes_milan.jsonl:16-17`) ; « dans tous les sens » n'est pas revenu. |
| VFX jugés contre la ref, biais retiré | `outils/juge.py` ; prédiction brute et corrigée (`notes_milan.jsonl:15`) | v12 4 -> v13d 7,85 (causes partagées avec la refonte). |
| Comparer à TSB avec le même rig et la même caméra | `r6_poing_dragon/scripts/regard_v7_vs_tsb.py` ; `corpus/CARNET.md:44-47` | Fausse alerte évitée (8 % contre médiane TSB 15 %). |
| Géométrie du contact contre TSB / pack (torsion, croix, bras libre) | `etats.py:198-236` | v6 -> v8 +0,5 (`critic.reflect`), mêlé au timing. |
| « Frappe vers le bas » : mesurer en repère MONDE (hauteur du poing + bascule du buste) | CARNET 2.9 ; aujourd'hui nombres sans verdict (`mesures_coup` de `r6_un_seul_coup/output/verification.json`) | Plus signalé depuis Un seul coup v2. |
| Obari : caméra chez la victime, poing vers l'objectif | `repro/saitama_obari.py` ; `r6_poing_dragon/scripts/staging.py:165-168` | v9 7,7 (+0,2), « la mise en scène obari a payé un peu ». |
| Contact sauté + cartes d'impact | `coup_clip.py:50` | `cartes_impact` et `blanc_total` « discriminent » (`REFLEXION.md:44-46`) ; aucune plainte. |
| Technique d'export : EasingStyle, chaîne V2.22, lecteur three.js r134 | `roblox_export.py:189-190` ; selftests V2.22 (écart 0,0018 stud) ; `r6_un_seul_coup/scripts/build_player.py:5` | Vrai bug attrapé (tout en Constant avant le 24/09), jamais revenu. Bug de version du lecteur jamais revenu. |

---

## 3. Ce qui est appris À MOITIÉ, par cause

### A. Le savoir est resté en mots : les poses des refs ne sont jamais mesurées

- Vidéos et GIF : des TEMPS et des MOTS, jamais de géométrie. `clip_analyzer.py:17-20` : « Ce qu'il NE mesure PAS : les poses ». `PLAN.md:185-187` promettait des « poses annotées » : aucune n'existe.
- Images manga / anime : une phrase par image (`corpus/CATALOGUE_REFS.md:25-34`). Aucune pose reconstruite.
- Le fichier 3D de TSB contient des coups **chargés** (Collateral Ruin, Stoic Bomb, Ultimate1/2). `corpus/perception_tsb.json` n'en garde que densité de clés, bascule et part de croix. Jamais exploités en géométrie pour la charge.
- Tutos : 6 vidéos vues image par image, 15 lues par Gemini sur transcription seulement. Les poses reproduites l'ont été à l'œil (`repro/README.md:21`, `:42`). Les vidéos ne sont qu'au scratchpad de session.
- Traductions R6 jamais confrontées aux refs : « la compression se lit par la torsion plutôt que par un dos rond » (`hypotheses.json`, `compression_extension`) a guidé Un seul coup v2-v3.
- Conséquence : le poing chargé a oscillé. v3 arc tendu debout, v4 ramassé (buste 57°, hanches -1,05), v5 poings sur les côtés. Notes 7 -> 7,5. Les angles de la fiche (`UN_SEUL_COUP.md:140-248`) sont les NÔTRES.
- La leçon existait : « Mesurer la réf avant de pousser » (CARNET 2.8, 25/09). Elle n'a pas été appliquée.
- Les vraies mesures d'aujourd'hui (fourchettes TSB, reconstructions Pew / TSB / SP2, solveur `fit.py` / `fitkp.py`) sont **au scratchpad**. Pour le cerveau, elles n'existent pas.

### B. Des outils écrits, puis perdus à la migration vers le rig V2.22

Ils existaient dans l'ancien pipeline. Rien n'a suivi le passage au V2.22.

| Outil | Ce qu'il fait | Où il tourne encore |
|---|---|---|
| `tracks.offset_tracks` | décaler les clés membre par membre (overlap) | seulement `r6_black_hole/scripts/choreography.py:71, 456` |
| `organic.py`, `outils/moon.py:157` (`wiggle`) | tenue vivante | `r6_black_hole`, `repro/` |
| `poses.describe_pose` (« toute pose clé passe par describe_pose », `poses.py:10`) | relire une pose en nombres | `choreography.py:9, 24, 203` ; `geo_pose` l'a réinventé sans le citer |
| `constraints.balance_margin`, `foot_lock_pass`, `look_at_pass` | équilibre, verrou des pieds, regard borné | `choreography.py:192-196` |
| `_spring_chase` (ressort secondaire « à la Cascadeur ») | mouvement secondaire | `anim_engine.py` de 7 anciennes productions |
| `audit.py` (overlap, holds morts, glissement, équilibre) | juger le mouvement | une fois sur V2.22 (M1, `r6_m1_v222/scripts/motion_proof.py:9`) ; sur V2.22 son seuil de sol donne un **faux OK** (pieds à 0,034 stud, `contact_eps` = 0,02) |
| `cartoon_filter.siso_retime` | retiming | `r6_aerial_kick_combo/scripts/cartoon_filter.py:91` |
| smear `drawArmSmear` | traînée du bras | `r6_directional_punch/README.md:697-708` ; `REFLEXION.md:33` le croit « toujours faux » |

Conséquence : le pipeline V2.22 pose **tout le corps à la même image**, mains en IK (`coup_clip.py:130-275`). Mesuré sur Un seul coup v5 : tête synchrone du torse (retard 0 image), holds morts sur 51 % du clip (seuil non calibré). Milan v9 : « très léger en terme de smooth et d'enchaînement ».

### C. Des outils de vigilance jamais branchés sur la production suivante

- `outils/corps_bras.py` : prescrit « sur chaque production » (`corpus/CARNET.md:807-811`), dans la porte de `corpus/fiches/POING_DU_DRAGON_V13.md:118`. Une seule exécution tracée (v9). Relancé sur Un seul coup v5 : torse figé 55/85 images pendant la charge.
- `outils/regard.py` : une seule capture, jamais sur Un seul coup. `vues.pelure` : un seul appel (`r6_poing_dragon/scripts/regard_v7.py:74-75`).
- `perception`, `etats`, `critic` : gelés à la v9 du Dragon (`etats_auto.json` v1-v9 ; `productions.json` ne connaît que `poing_du_dragon`). Relancé sur la v5 : le poing ralentit à 52 % de sa vitesse de pointe avant le contact. Personne ne l'a vu.
- `outils/tour.py` codé en dur sur `dragon_attaquant.rbxmx` (l.41-45). `rules.design_targets` : 0 appel. `tutos_vs_tsb.py`, `fist_path.py` : pas relancés depuis le 24/09.
- Des mesures tournent sans lecteur : le `verify_export` du Dragon dit à chaque export que le bras qui frappe se translate moins que les pros (0,88-0,99 stud contre 1,28-1,88).
- Bilan : la production la plus récente (Un seul coup) vérifie **moins** que la précédente. Un garde-fou manuel s'oublie à la production suivante.

### D. Deux grammaires de pose, sans pont

- On **mesure** en angles d'animateur : `outils/geo_pose.py` (axes du torse, bâti sur `moon`). On **écrit** en cibles IK : `solve_pose`, modes `a` / `d` / `w` / `g` (`r6_poing_dragon/scripts/dragon_clip.py:244-372`).
- Sens export -> mesure : existe (`r6_un_seul_coup/scripts/verify_export.py:102`). Sens pose voulue -> clés : n'existe pas. Une pose trouvée au labo est retapée à la main, sans garantie.
- L'écart est invisible : une garde écrite `a(22,-30)` sort à (17,6 ; -31,7) dans les axes du torse. Trois repères de main dans le même clip (`coup_clip.py` : `a` l.163, 212 ; `d` l.185 ; `w` l.215). Deux conventions az/el. Quatre modèles de pose R6.
- ~250 nombres tapés pour ~32 clés (`coup_clip.py:113-273`).
- Les mots de direction n'ont pas de repère : à la tenue de la v5, le même bras est à 85,1° dans le repère du coup et à 19,8° dans celui du torse.

### E. Une mémoire qui garde des lectures démenties

- `corpus/CATALOGUE_REFS.md:24` « poing tiré loin derrière » ; `:31` « bras alignés tendus » ; CARNET 2.10 (`CARNET.md:332-345`) ; `corpus/fiches/COUP_CHARGE.md:39` « le poing armé DERRIÈRE ». Milan, v4 : « dans aucune des refs le bras est tendu derrière » (`RETOURS.md:828-829`).
- La correction ajoutée après la v3 (`CARNET.md:340-345`, « ramassée, buste ~45-60° ») a elle-même été démentie en v4. Rien depuis : CARNET.md n'a pas bougé depuis 8b768e4 (v4).
- CARNET 2.9 (`CARNET.md:327`) décrit un garde-fou d'export retiré par 6f0539e. CARNET §2.1c dit « clés espacées : à essayer » : c'est en production depuis la v8.
- `outils/rappel.py` « poing chargé » imprime la ligne 24 du CATALOGUE en 2e réponse. Aucun champ de statut (« contredit par Milan le … »).
- `ETAT.md:101-102` présente encore `rules.py`, `audit.py`, `etats.py`, `critic.py` comme des outils vivants.

### F. Des leçons rangées en « historique », puis oubliées

- `LECONS.md` marqué HISTORIQUE (1395eb3). Leçons 10 et 11 (« vers le bas ») absentes du CARNET et des fiches. `CARNET.md:9-11` envoie toujours les apprentissages confirmés vers LECONS.md : **la voie de promotion est coupée**.
- « Frappe vers le bas » est revenu **6 fois** (tableau §4).
- La limite de la vue unique (`r6_aerial_kick_combo/README.md:563-590`, cycle 8, 01/09 : un membre qui pointe vers la caméra ou à l'opposé a la même silhouette) est absente du cerveau (grep « monocul » : 0). C'est exactement la question du poing chargé : devant ou derrière ?
- `rappel.py` n'indexe que les `.md`, `notes_milan.jsonl` et `outils/*.py` (`rappel.py:80-96`, `:124-128`). Jamais `clips/*.json`, `hypotheses.json`, `poses.py`, `tracks.py`, `constraints.py`, `repro/`. D'où la réinvention.

### G. Des règles de style gravées

- `rules.py` (`check_affaissement`, `check_epaules`, `check_bras_au_contact`, `check_trajectoire_poing`, `check_transfert_poids`) : seuils calés sur 4 M1 d'un pack réaliste, ou sur le MIN de 3 exemples. **13/13 de la v4 à la v8, pendant des notes de 6,7 à 7,5.** B2 a été choisie « surtout parce qu'elle passait » (`RETOURS.md:447`).
- Jusque dans le solveur : borne `auto_low` « jamais plus de 0,2 stud (LECONS.md 1) » (`dragon_clip.py:265`), héritée par Un seul coup (`coup_clip.py:35, 162, 180`). Nuance vérifiée : elle ne limite que l'abaissement automatique du bassin, pas le bassin demandé.
- Étalons du pack dans `etats.py:118-124` : ils déclarent fausses les M1 de TSB (bras/épaules 74,4° contre un max de 38,3°), c'est-à-dire le jeu cible. Seuils « provisoires » jamais recalés (`etats.py:115`).
- « Jamais d'uppercut » (`COUP_CHARGE.md:42`) : contredit dans la même fiche (OPM, caméra sous le poing qui monte, `:88`). « Jamais de croix » : contredit par l'obari de Sakura (`hypotheses.json:1003`) et par « un T couché » (CARNET 2.10).
- Pire cas : Un seul coup v2-v5. Des contrôles **bloquants** tirés de mes lectures. `poing_derriere_pendant_la_charge` (7bb9526, `verify_export.py:99`) exigé pendant 3 versions, puis inversé 45 min plus tard (f8601ba). Chaque version passait. Milan disait non.
- Les champs `quand` / `contre_indication` ne sont lus par aucun code (seul `portee` l'est, `critic.py:94`).
- Détecteurs trop étroits : la croix exige un torse < 10° (`perception.py:261`), la v3 (buste 17,8°) passe. `corps_bras` compte « figé » sous 0,3°/image : il masque une torsion lente voulue.

### H. Des principes appliqués, mais trop timides ou non perçus

- Dragon v7 : trois principes appliqués d'un coup (croix 93 % -> 0 %, compression, tenue vivante). Milan : « je vois aucun changement ».
- Un seul coup, tenue : la torsion monte de 9° en 49 images (0,18°/image), torse figé 43/49. Vie après le coup : ±0,012 stud, contre ±0,03-0,08 dans l'anime mesuré (`corpus/tutos/rapport_anime3d.md:218-226`).
- « Poses ~2x trop sages » appliqué comme un facteur fixe : trop abusé en v4.
- Un principe coché n'est pas un changement perçu.

### I. Un critique de prédiction non calibré

- 7 paires prédiction / note : biais +0,32, surestimation 5 fois sur 7. Écart absolu 0,45, contre 0,38 pour « même note que la dernière fois » (n = 7 : pas significatif, mais pas mieux).
- Un seul coup : 8,0 -> 7 ; 7,8 -> 7,5. Cinq prédictions entre 7,6 et 8,0.
- `critic.py:138` lit `prediction_avant_milan` ; Un seul coup écrit `prediction` (`notes_milan.jsonl:18-25`) : ignoré. `critic.py:67` exclut les notes sans `etat`. `critic.py:63` donne à Un seul coup v1 les états du Dragon v1.
- Les poids appris mettent `coup_charge`, `bras_horizontal`, `arcs`, `transfert_poids` au plus bas (0,395), alors que le coup chargé est le reproche n°1. 61 hypothèses pour 7 notes. Il n'a jamais changé une décision.

---

## 4. Les motifs de rechute

| Motif | Nb | Ce qui existait | Pourquoi ça n'a pas suffi |
|---|---|---|---|
| « Le coup part d'en bas / frappe vers le bas » | 6 (directional_punch, Dragon v3, v3b, v4, v7, Un seul coup v1) | Leçons 10-11 (`LECONS.md:162-200`) ; `rules.check_bras_au_contact`, `check_trajectoire_poing` ; contrôle `poing_a_hauteur_d_epaule` dans Un seul coup v1 (6fcfc4e) | Mesure relative à l'épaule, qui plonge avec le buste : contrôle **au vert** en v1. Leçons rangées en historique. Réglé depuis la v2 par une mesure en repère monde. |
| « Tu n'animes que les bras » | 4 (directional_punch, Dragon v4, v9, Un seul coup v4) | `corps_bras.py` ; `CARNET.md:807-811` ; COUP_CHARGE §7 ; `tracks.offset_tracks` | Jamais relancé après la v9, hors de `verify_export`. Seuil aveugle à la torsion lente. Le pipeline pose tout le corps à la même image. |
| « Je vois aucun changement » | 4 (Dragon v5, v7, v8 ciné, Un seul coup v3) | `regard.py` ; planche v(n-1) / v(n) à chaque version ; CARNET 1.4 | Images choisies et légendées par mon intention, pas à vitesse réelle, sans la ref. Écart réel v2 -> v3 : 42/255 en pixels (`RETOURS.md:815`). |
| Mauvaise lecture (mots de Milan, images) | 6 (« coup final », « mélange à Izuku », « pas au bon endroit », « ramené à l'arrière », « la pose de charge »…) | `ANGLES_MORTS.md` §1 ; questions posées (`RETOURS.md:199`, `:815`) | Rien ne mesure la ref pour trancher le sens d'un mot. La lecture fausse est montée jusqu'à un contrôle bloquant. |
| Corriger symptôme par symptôme | 2 séries (Dragon v2-v4 ; Un seul coup v2-v5) | Leçon 8 (`LECONS.md:153-160`) | La leçon prescrivait elle-même « une mesure puis une règle ». Rien ne compare le mouvement entier à la ref. |
| Se lancer avant de comprendre | Un seul coup : 5 versions en 66 min | « Étudie, comprends, avant de te lancer » (`RETOURS.md:135`) ; CARNET 1.6 | La comparaison aux refs arrive 2 min **après** le commit v4, à la demande de Milan. Biais absent du CARNET §6. |
| Pendule sage / trop abusé | 3 (Dragon v6 ; Un seul coup v4 ; en sens inverse aerial_kick cycle 9) | « poses ~2x trop sages » (`CARNET.md:800`) ; `reglage_double` | Multiplicateur sans borne ni cible. Aucune variante x1 / x1,5 / x2 sur Un seul coup. |
| Surestimer sa note | 5 sur 7 paires ; Un seul coup 2 sur 2 | `critic.biais_predictions` ; `_biais_prediction` | `critic.py` ne lit pas la clé d'Un seul coup. Aucune prédiction corrigée depuis la v13. |

---

## 5. Hallucinations et erreurs de mémoire trouvées

**Lectures contradictoires d'une même ref (Serious Punch TSB, 48244687)**
- Direction de la frappe : « poing vers le bas dans une fumée » (`corpus/REFERENCES_VIDEO.md:18`) ; « atterrissage accroupi, frappe au sol » (`corpus/RELECTURE_REFS_ANIMATION_2026-09-25.md:32`) ; « poing vers l'objectif » (`UN_SEUL_COUP.md:30`).
- Garde : « 32 f » (`REFERENCES_VIDEO.md:18`), « 0,42 s » (`RELECTURE_REFS_ANIMATION…:32`), « 1,1 s » (`UN_SEUL_COUP.md:26`).
- Cartes d'impact : « 3 x 1 f », « 3 x 4 f » (`ETUDE_NOTES_BRUTES.md:55`, `CATALOGUE_REFS.md:23`), « 1 x 267 ms » (`corpus/clips/serious_punch_tsb.json`).
- Aucune réconciliation. Toutes au même rang dans `rappel.py`.

**Affirmations fausses dans les fiches et la mémoire**
- « Poing tiré loin derrière », « bras alignés tendus » (`CATALOGUE_REFS.md:24`, `:31` ; `CARNET.md:335`) : tirés de 2 vignettes (`CARNET.md:345` l'avoue), démentis par Milan.
- « Milan dit l'inverse » : faux. Il disait « arrière droit » (`COUP_CHARGE.md:27`), « en le ramenant à l'arrière » (`RETOURS.md:787`). Le mot était ambigu ; sa v4 précise que l'arrière vient du buste.
- « Fiche UN_SEUL_COUP §11 » citée comme source des fourchettes des refs (`r6_un_seul_coup/scripts/verify_export.py:100-101`, `RETOURS.md:847`, `ETAT.md:51`) : **n'existe pas**, la fiche s'arrête au §10.
- `CARNET.md:327` (garde-fou d'export retiré), CARNET §2.1c (« à essayer », en production), `REFLEXION.md:33` (smear « toujours faux », alors que codé en septembre), `ETAT.md:101-102` (outils morts présentés vivants).
- `UN_SEUL_COUP.md:188` décrit la v3 « bras en croix » ; le détecteur mesure 0 % de croix sur v1-v5.
- Contradictions jamais tranchées : ligne des épaules, pack ≤ 38° contre M1 TSB 61-78° ; extension anime « torse 30-60° » (`rapport_anime3d.md:282`) contre CARNET 2.9 « buste < 22° ».

**Erreurs dans le code et les outils**
- `outils/geo_pose.py:82-83` : la doc dit « lacet + = épaule droite qui recule ». Le calcul dit l'inverse. Test : lacet +40 -> épaule droite DEVANT (`recul_droite` -1,93).
- Dans l'export d'Un seul coup, la mesure « charge » (`CHARGE_F` = 186) lit la **garde** (`coup_clip.py:188`) : descripteurs identiques. La vraie tenue est à `TENUE_F` = 222.
- Lecteur rbxm, poses de poids 0 : `corpus.load_rbxm_sequences` (`corpus.py:54-61`) garde les Poses de `Weight` 0 comme des clés (il calcule seulement leur part, l.65-67). `resample_linear` les interpole, et `geo_pose.mondes_rbxm` (`outils/geo_pose.py:214-219`) en hérite. Constaté pendant les mesures du poing chargé : le Torso retombe à l'identité. Le lecteur corrigé n'existe qu'au scratchpad (`poing/wf/pro_tsb_ult/lecteur.py:1-3`, `poing/wf/pro_tsb_m1/charge.py:1-2`).
- Le même lecteur ignore `EasingStyle` (`corpus.py:82-86` suppose Linear), alors que `_shared/rbxm_reader.py:422-444` le décode (TSB : Linear 4248, Constant 67).
- `critic.py:63` : collision de versions entre productions. `audit.contact_report` : faux OK sur V2.22.
- `coup_clip.py:171` : la doc de `arc()` dit « mode a » ; le code est en `d` (l.185). `coup_clip.py:145-152` décrit encore la v3.
- `rules.py:10` cite `run_all()`, qui n'existe pas. Le `verify_export` du Dragon promet « aucun coin > 0,1 » (docstring l.7) sans l'imposer.
- `clip_analyzer.py:17-19` affirme, sans test, que les estimateurs de pose ne marchent pas sur R6.
- `corpus/refs/SYNTHESE.md` garde « part de tenues 0,02 » et une cadence « en 3 » (artefact probable 24 -> 60 i/s), sans alerte.

**Erreurs des lecteurs de l'audit eux-mêmes, corrigées par les contradicteurs**
- « geo_pose n'est importé par aucune production » (faux depuis 6f0539e) ; « le lecteur rbxm ne décode pas l'enum d'easing » (faux) ; « aucune empreinte des refs dans vfx_studio » (faux : `vfx_studio/dessins.py:5-6`, `recettes.py:507-624`) ; « le détecteur de croix aurait vu la v3 » (faux) ; « 46 hypothèses avec portée non codées » (7 le sont) ; « smear et obari jamais essayés » (faux) ; « aucune comparaison ref contre nous » (faux : fiche §9, à l'œil) ; « la mémoire a causé la rechute » (non prouvé).
- Leçon : même un audit en mots se trompe. Les contradicteurs ont servi.

---

## 6. Ce qui manque pour devenir un outil d'animateur

Fusion dédupliquée des 86 propositions de code des 8 tranches.

**Principe.** Tout ce qui touche au style est une **MESURE** (nombre affiché
à côté des refs) ou une **AIDE** (outil pour poser, regarder, choisir).
Jamais un verdict bloquant. Seuls les contrôles **TECHNIQUES** (moteur,
rig, export, conventions d'axes) peuvent bloquer.

### Priorité 1 : avant la v6 du poing chargé

| # | Outil | Pourquoi | Type | Effort |
|---|---|---|---|---|
| 1 | **Corriger geo_pose et son branchement** : doc du lacet, instant « charge » à la vraie tenue, renvoi au §11, test d'axes qui `assert` | La v6 va lire ces nombres. Aujourd'hui l'épaule se lit à l'envers et la « charge » est la garde. | TECHNIQUE | 30 min |
| 2 | **Corriger le lecteur rbxm** : ignorer les Poses de poids 0 ; lire `EasingStyle` | Sans ça, toute mesure TSB par `geo_pose.mondes_rbxm` est faussée. Le correctif existe au scratchpad. | TECHNIQUE | à verser ; easing 0,5 j |
| 3 | **Verser au dépôt ce qui existe au scratchpad** : mesures TSB / pack (`pro_tsb_m1`, `pro_tsb_ult`, `pro_pack`), reconstructions (`recon_pew`, `recon_tsb`, `recon_sp2`), solveur (`fit.py`, `fitkp.py`), `pose_live_proto.py` | Trou n°1 : si la session se ferme, tout est perdu. Les nombres, pas les pixels des refs. | MESURE | 2 h à 0,5 j |
| 4 | **Bibliothèque de poses mesurées** `corpus/poses/<moment>.json` : garde, armé, charge tenue, départ, contact, suite ; descripteurs geo_pose, provenance (3D exact / reconstruction), incertitude, date. R6 exact d'abord (Stoic Bomb, Collateral Ruin, Ultimate1/2, M1-M4, pack), refs vidéo ensuite | La pièce absente. Remplit le §11 fantôme. Seulement des refs mesurées : nos anciennes poses sont fausses (`croquis_v7.py:6`, « poing armé haut derrière l'épaule », rejeté par Milan). | MESURE | 2 h (partie R6) à 2 j |
| 5 | **ajuste_pose / cale_pose depuis des points 2D** : 10-12 points + silhouette -> pose R6 + caméra, moindres carrés (Levenberg-Marquardt en numpy : scipy absent) ; plusieurs vues liées ; les N meilleures solutions avec un drapeau « ambigu » ; résidu affiché ; **test sur vérité connue** (`ANGLES_MORTS.md` §7) | Le prototype hésite entre bras devant et bras derrière au même coût (`fitkp_290_A.log` : lacet 34° à 79°, bras az -46° à +136°). Plusieurs vues tranchent. | MESURE | 0,5 j (verser + multi-vues) à 2 j ; test : quelques heures |
| 6 | **Mesure du trajet de la charge** : geo_pose dans le temps (buste, épaule, poing, bassin, de la garde au contact), nous contre refs, repère du coup ; plus **suivi 2D d'un membre** dans une vidéo (cv2 4.9 présent, flux Farneback existant) | Le poing chargé est un MOUVEMENT (« le poing ne part pas de l'arrière »). Le trou exact des 5 versions. | MESURE | 1-2 j + 0,5-1 j |
| 7 | **Rapport de regard non bloquant**, à chaque version, qui réunit l'existant : `corps_bras`, pelure du torse, `audit.audit` via `corpus.to_samples` (seuil de sol corrigé), `perception` (charge, torsion, arcs, silhouette, frappe, impact), geo_pose aux marqueurs à côté des fourchettes, `fist_path`, timing contre le corpus, écart avec v(n-1). Planche + JSON dans `captures/verification/`, et une ligne « hors plage : à dire » | Les outils existent, personne ne les lance ni ne les lit. Sur le modèle de `juge.py` : un écart n'interdit pas de montrer. | MESURE | quelques heures à 1 j |
| 8 | **Pont geo_pose -> clés V2.22 avec re-mesure** : mode `geo` dans `solve_pose`, écart demandé / obtenu affiché, az/el unifiés avec le mode `a` | On mesure en angles, on écrit en IK. Une pose de ref doit devenir une clé sans être retapée. | AIDE | 2-3 h à 1 j |
| 9 | **Planche ref \| nous à caméra identique** : caméra estimée par ajuste_pose ; ref \| v(n-1) \| v(n) aux mêmes instants, à vitesse réelle ; version committable **sans pixels de ref** (squelette ou silhouette relevés + chiffres) | Faite une fois à l'œil (fiche §9), puis perdue : la règle des refs interdit de les versionner, la règle des preuves exige une capture. | MESURE / AIDE | 0,5 j |
| 10 | **rappel.py v2** : lit `clips/*.json`, `perception_*.json`, `hypotheses.json`, `corpus/poses/` ; sort les **fourchettes chiffrées** ; ignore les titres ; **statut** posé sur la ligne d'origine (mesuré / lecture en mots / contredit par Milan le … + RETOURS:ligne) ; signale les lectures contradictoires ; indexe les outils hors `outils/` (`poses.py`, `tracks.py`, `constraints.py`, `repro/`, `_spring_chase`, smear, cycle 8 d'aerial_kick) | Aujourd'hui il rend de la prose et imprime en premier ce que Milan a démenti. | AIDE | quelques heures |
| 11 | **Registre des motifs** `motifs.json` + `outils/motifs.py` : mots de Milan, occurrences datées, mesure associée ET son repère, dernière rechute ; sorti en tête par le rappel | Personne ne compte « vers le bas » 6 fois. | AIDE | 0,5 j |
| 12 | **Passe torse d'abord** sur V2.22 : chaque temps fort passe d'abord par le torse seul (rendu, regardé), puis bras libre, bras qui frappe, tête, jambes ; clés décalées par membre. Réutilise le FK des bras du rig (`dragon_clip.py:186-187`), `moon.py`, `tracks.offset_tracks` | Leçon n°1 des tutos, et le défaut que Milan voit depuis la v9. | AIDE (méthode) | 2-3 j |

### Priorité 2

| # | Outil | Pourquoi | Type | Effort |
|---|---|---|---|---|
| 13 | Mesurer les poses des 6 tutos vus en image avec geo_pose (charge en K de myloe, uppercut de Moon, planche de Xoaterz) | Tout le savoir des tutos est en « ~45° ». **Urgent dans le temps** : les vidéos ne sont qu'au scratchpad. | MESURE | 1-2 j |
| 14 | Hygiène de la mémoire : script qui retrouve une lecture démentie partout (CARNET, fiches, CATALOGUE, verify_export) ; test « toute leçon historique a une copie vivante » ; voie de promotion de `CARNET.md:9-11` vers un fichier vivant ; détecteur de contradictions (croix, torsion, poing derrière, accroupi, exagération) ; contrôle mémoire <-> code (un outil prescrit a une sortie datée) ; repérage des « jamais / toujours / doit » sans source | Corrections écrites ailleurs que sur l'entrée fautive ; LECONS coupé ; CARNET §2.1c obsolète. | AIDE | 3 h à 1 j |
| 15 | Réparer `critic.py` (une seule clé de prédiction, id production + version, prédiction corrigée, comparaison à « même note que la dernière fois », « mesure invalide » au lieu de baisser un poids) ou le déclarer historique ; **prédiction falsifiable** : « le changement se verra-t-il à vitesse réelle : oui / non » + intervalle ; mettre à jour `ETAT.md:101-102` | Le critique ne voit pas Un seul coup et n'apprend plus depuis le 25/09. | AIDE | 3-4 h |
| 16 | `rules.py` / `check_rules.py` / `etats.py` -> mesures contre refs : valeur + position dans chaque source, sans « ok » ni X/Y ; percentiles ; généralisé hors du Dragon ; croix relative à la caméra ; torsion lente comptée à part dans `corps_bras` ; lecture de `quand` / `contre_indication` | Ces vrai/faux ont passé 13/13 pendant que Milan rejetait. | MESURE | petit à moyen |
| 17 | `verify_export` en trois blocs nommés, dans les deux productions : technique (bloquant) / intention de CETTE scène (déclarée) / mesures (jamais bloquantes). Sol < -0,1 et tête : bloquants, ou tolérance écrite | Rien n'empêche aujourd'hui de remettre demain un contrôle de style dans `sens`. | TECHNIQUE | petit |
| 18 | Rôles de clés + retiming : chaque clé porte un rôle (anticipation, drag, milieu, exagération, amorti) ; mesures sans verdict (anticipation opposée, dépassement en degrés, retard du bras au drag) ; retiming par rôle ou facteur (myloe 40 -> 30, 115 % de Thundey) ; fenêtre `eparse` en paramètre (`dragon_clip.py:59`) | Les rôles n'existent que dans une table de repro (`repro/uppercut_moon.py:32-39`). Le timing est fait de constantes en dur. | AIDE / MESURE | ~1 j |
| 19 | Blocking rapide (`pose_live.py`) : une clé résolue sans cuire la scène (0,37 s au prototype contre ~45-49 s), ref \| nous \| superposition, écart chiffré ; étape « poses clés seules » avant la scène complète | 5 versions en 66 min sans une pose validée. | AIDE | 1-3 h |
| 20 | Poseur three.js pour Milan : curseurs par Motor6D, image de ref en fond, caméra calable, pelure, export JSON geo_pose | « Je ne sais pas comment te l'expliquer » (`notes_milan.jsonl:25`). Il montre au lieu d'expliquer. | AIDE | 1 j |
| 21 | Lecteur A/B + générateur de variantes x1 / x1,5 / x2 au cadrage réel (généraliser `ab_cles_eparses.py` et `DRAGON_RAFALE`), une seule question à Milan | Milan n'a jamais choisi entre deux animations du même moment. | AIDE | 2-3 h |

### Priorité 3 et plus

| # | Outil | Type | Effort |
|---|---|---|---|
| 22 | Easing par pose à l'export (`write_kfseq` : Constant pour les tenues, Cubic…) + banc A/B ; clés éparses sorties du Dragon vers `roblox_export` | TECHNIQUE + A/B | 0,5 j |
| 23 | Rebrancher sur V2.22, en option et en A/B : équilibre et glissement (seuil de sol V2.22), ressort secondaire, overlap, tête animée (regard gardé, exagération, retard 1-4 images) à la place du Track Object permanent | AIDE | très faible à 3 h chacun |
| 24 | Catégorie « charge » dans le corpus (Stoic Bomb, ultimes ; TSB dans `categories.json`) | MESURE | 2 h |
| 25 | Solveur partagé et testé (`pose_dsl.py` hors de `dragon_clip.py`, distance en paramètre, borne `auto_low` visible) ; gabarits de moments ; poses et caméra en données accrochées aux marqueurs | TECHNIQUE | 0,5-2 j |
| 26 | Tests sans Blender : geo_pose, perception, critic, roblox_export, corpus | TECHNIQUE | 0,5 j |
| 27 | Porter en production ce qui a été fait puis oublié : smear, obari de `repro/saitama_obari.py` (part du cadre mesurée), membres multiples, tenues en escalier « en 2 / en 3 » | AIDE (à essayer) | 0,5-1 j chacun |
| 28 | Interpolation en arc pour V2.22 (main en az/el autour de l'épaule), vérifiée par `perception.arcs` | AIDE | 0,5 j |
| 29 | Plus tard : vue « graph editor » nous contre TSB ; `juge.py` par style déclaré ; `clip_analyzer` à 24 i/s ; A/B de la secousse ; ligne d'action (Mattesi) dans geo_pose ; balistique de la victime ; estimateur réseau seulement si ajuste_pose manque de points ; statistique mesure -> note (utile au-delà de ~20 notes) | MESURE / AIDE | 1 h à 0,5 j chacun |

---

## 7. Ce qui est déjà fait aujourd'hui

- **geo_pose créé** (fad2303) : mesurer, reconstruire, comparer une pose R6 depuis la même caméra.
- **Branché dans l'export d'Un seul coup comme MESURE** (6f0539e) : `r6_un_seul_coup/scripts/verify_export.py:32` et `:99-104`. `mesures_pose` aux 6 temps forts dans `output/verification.json`. Seuls les contrôles de sens bloquent (`:122`).
- **Contrôles de style retirés de verify_export le 2026-09-26** (6f0539e), après le rappel de Milan (« pas de règles gravées », `RETOURS.md:849-861`, 3c3a6f7).
- **Analyse géométrique du poing chargé en cours** (`ETAT.md` §1b, chantier 1) : mesures R6 exactes TSB + pack, reconstruction des refs par rendu-comparaison, v5 mesurée, vérification adverse -> fiche §11 -> v6. Premiers constats en route : lecteur TSB corrigé pour les poids 0 (au scratchpad) ; le lacet du buste v5 (-60 à -71°) est déjà dans la plage de l'armé TSB (-58 à -70°) : l'écart n'est pas UN nombre, il faut comparer la pose entière sous plusieurs vues.
- Chantiers suivants déjà inscrits (`ETAT.md` §1b) : réorganisation de la mémoire inspirée de Hermes Agent (chantier 3) ; se renourrir réellement de tout le contenu envoyé (chantier 4, 26f0863).
- Reste à faire sur ce qui est « fait » : les défauts du §5 (doc du lacet, « charge » = garde, §11 absent) et le versement des mesures du scratchpad (§6, n° 1-4).
