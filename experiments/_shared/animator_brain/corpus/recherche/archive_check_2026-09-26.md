# archive_check du 2026-09-26 : destinations vivantes des entrées HISTORIQUE

Rapport produit par `python3 outils/archive_check.py` (brique A2 du
plan `PLAN_REORGANISATION_2026-09-26.md`). **Rien n'a été modifié.** C'est
une aide à la relecture, pas un verdict : un score recoupe des mots et des
nombres, il ne dit pas si une leçon a été comprise.

Lecture : « complète » = une section vivante reprend l'essentiel des termes
rares et au moins la moitié des nombres (score >= 0,55) ; « partielle » =
une partie seulement (score >= 0,3, ou 3 sections vivantes réunies >= 60 %
des termes) ; « AUCUNE » = rien de vivant ne la reprend. « Hors vivant » =
code en veille (rules / etats / critic / audit) ou code d'une production
passée : écrit, mais plus relu.

## Premier cas test : LECONS §10-11 (« vers le bas », « à plat »)

```
LECONS.md §10 (l.162) « 10. On règle la hauteur du coup avec le corps, pas avec l'an » -> AUCUNE destination vivante (meilleure : corpus/CARNET.md:38 1.2 0.183)
      plus proche hors vivant : rules.py:146 check_bras_au_contact (0.548, en veille)
      plus proche hors vivant : ../../r6_poing_dragon/scripts/dragon_clip.py:580 attacker_keys (0.355, production)
      nombres absents des 3 meilleures vivantes : 4.25, 30
      termes clés absents : pro, rule, fente, check, hauteu, cible, foie, pouvai, plexu, exempl
```

```
LECONS.md §11 (l.183) « 11. Un coup droit arme haut et voyage à plat » -> AUCUNE destination vivante (meilleure : corpus.py:304 strike_mechanics 0.155)
      plus proche hors vivant : ../../r6_poing_dragon/scripts/dragon_clip.py:580 attacker_keys (0.316, production)
      plus proche hors vivant : ../../r6_m1_v222/scripts/m1_clip.py:51 attacker_keys (0.257, production)
      nombres absents des 3 meilleures vivantes : 0.02, 0.05, 0.09, 0.2, 0.22, 0.3, 0.32, 0.34, 0.48, 0.59, 1.1, 1.3
      termes clés absents : lourd, moyenn, style, vient, corpu, copier
```

Attendu (cause de la rechute d'« Un seul coup » v1) : pas de destination
vivante complète. Les nombres listés « absents » sont ce qui serait perdu
si l'on ne gardait que les destinations vivantes.

## Totaux

247 entrées : complète 5, partielle 115, AUCUNE 89, absorbé 0, abandonnée 0, vide 32, bandeau 6.

ETAT.md §3 dit des fichiers HISTORIQUE : « Ce qu'ils contiennent de vivant
est passé dans CARNET.md et les fiches. » Ce recoupement ne le confirme que
pour une minorité d'entrées. Ce n'est pas une liste de choses à recopier :
beaucoup d'entrées « AUCUNE » sont datées ou abandonnées à juste titre (on
l'écrit alors « abandonnée : raison » dans l'entrée). C'est la liste de ce
qu'il faut RELIRE avant d'écrire une pierre tombale (`outils/deplacer.py`).

Limites : recoupement lexical (racines de 6 lettres, nombres sans signe) ;
une leçon reformulée en d'autres mots sort « partielle » ou « AUCUNE » ;
un nombre banal (10, 0,5) peut se retrouver par hasard ; les tableaux sont
lus comme du texte ; le code est découpé par fonction de premier niveau.

## Résumé par fichier

| fichier | complète | partielle | AUCUNE | absorbé | abandonnée | vide | bandeau |
|---|---|---|---|---|---|---|---|
| `LECONS.md` | 0 | 5 | 8 | 0 | 0 | 1 | 1 |
| `CERVEAU_V2.md` | 0 | 8 | 7 | 0 | 0 | 0 | 1 |
| `PLAN.md` | 1 | 5 | 8 | 0 | 0 | 1 | 1 |
| `REFLEXION.md` | 0 | 3 | 6 | 0 | 0 | 1 | 1 |
| `ANGLES_MORTS.md` | 0 | 3 | 8 | 0 | 0 | 2 | 1 |
| `SCENE_POING_DU_DRAGON.md` | 0 | 11 | 3 | 0 | 0 | 3 | 1 |
| `corpus/ETUDE_NOTES_BRUTES.md` | 2 | 36 | 22 | 0 | 0 | 20 | 0 |
| `corpus/ETUDE_TSB.md` | 1 | 5 | 6 | 0 | 0 | 0 | 0 |
| `corpus/ETUDE_VISUELLE.md` | 0 | 27 | 8 | 0 | 0 | 4 | 0 |
| `corpus/TUTOS_ANIMATION.md` | 0 | 3 | 8 | 0 | 0 | 0 | 0 |
| `corpus/REFERENCES_VIDEO.md` | 1 | 9 | 5 | 0 | 0 | 0 | 0 |

## `LECONS.md`

```
LECONS.md §en-tête (l.1) « Leçons apprises par le cerveau » -> (bandeau, non cherché)
LECONS.md §en-tête item 1 (l.14) « 1. lire ce fichier et RETOURS.md avant de poser ; » -> (moins de 60 caractères, non cherché)
LECONS.md §en-tête item 2 (l.15) « 2. partir des cibles du corpus pour ses poses (pas de chiffr » -> outils/juge.py:1 module (0.401, partielle)
      termes clés absents : tape
LECONS.md §en-tête item 3 (l.17) « 3. passer rules.py et publier le rapport avec la production. » -> outils/corps_bras.py:1 module (0.439, partielle)
      plus proche hors vivant : rules.py:1 module (0.474, en veille)
      termes clés absents : rule, passer
LECONS.md §1 (l.22) « 1. Posture droite pendant les coups légers (R6) » -> AUCUNE destination vivante (meilleure : corpus.py:160 timing_profile 0.152)
      plus proche hors vivant : rules.py:55 check_affaissement (0.274, en veille)
      plus proche hors vivant : ../../r6_un_seul_coup/scripts/coup_clip.py:113 attacker_keys (0.193, production)
      nombres absents des 3 meilleures vivantes : 0.06, 1.26
      termes clés absents : armer, lourd, leger, corpu, parait, parais, downsl, disait, tasse, nouvel
LECONS.md §2 (l.41) « 2. Une rafale monte en intensité » -> AUCUNE destination vivante (meilleure : corpus/CARNET.md:479 4.2 0.269)
      plus proche hors vivant : rules.py:71 check_escalade (0.489, en veille)
      plus proche hors vivant : audit.py:456 frozen_fraction (0.35, en veille)
      nombres absents des 3 meilleures vivantes : 0.05
      termes clés absents : variet, check, ressen, intens, respir, manque, postur, escala, tier, glisse
LECONS.md §3 (l.55) « 3. Le plus gros impact doit être vu » -> AUCUNE destination vivante (meilleure : corpus/CARNET.md:755 4b.31 0.231)
      plus proche hors vivant : rules.py:88 check_impact_visible (0.575, en veille)
      plus proche hors vivant : rules.py:98 check_plan_lisible (0.355, en veille)
      nombres absents des 3 meilleures vivantes : 30
      termes clés absents : check, coupai, valide, critiq, lisibl, fort, manga, visibl, auto
LECONS.md §4 (l.68) « 4. Une jambe R6 est une boîte » -> corpus/fiches/UN_SEUL_COUP.md:225 10 (0.368, partielle)
      plus proche hors vivant : ../../r6_black_hole/scripts/choreography.py:494 post_local (0.378, production)
      plus proche hors vivant : ../../r6_battle_throne/scripts/props_battle.py:88 pillar_debris_parts (0.375, production)
      termes clés absents : boite, lowest, coin, suffit, revue, box, verify, vise, inclin, poser
LECONS.md §5 (l.78) « 5. Le ressenti de puissance n'est pas mesurable directement » -> AUCUNE destination vivante (meilleure : corpus/CARNET.md:140 1.11 0.256)
      termes clés absents : tracee, ressen, mesura, revue, approx, escala, verdic, fort, dire, propre
LECONS.md §6 (l.84) « 6. Les épaules ne montent jamais ; on frappe à hauteur de po » -> AUCUNE destination vivante (meilleure : corpus.py:160 timing_profile 0.29)
      plus proche hors vivant : rules.py:124 check_epaules (0.399, en veille)
      plus proche hors vivant : ../../r6_poing_dragon/scripts/dragon_clip.py:580 attacker_keys (0.392, production)
      nombres absents des 3 meilleures vivantes : 0.59, 0.69, 0.92, 1.29, 1.7, 2.4, 3.69, 4.4
      termes clés absents : poitri, pro, rule, visage, pres, check, distan
LECONS.md §9 (l.125) « 9. Entre deux clés, le contrôle IK va en ligne droite » -> constraints.py:1 module (0.314, partielle)
      plus proche hors vivant : ../../r6_black_hole/scripts/choreography.py:161 _grounded (0.331, production)
      plus proche hors vivant : ../../r6_black_hole/scripts/choreography.py:1 module (0.315, production)
      termes clés absents : chose, interm, armeme, grand, coupe
LECONS.md §7 (l.137) « 7. Le transfert de poids : le torse passe au-dessus du pied  » -> AUCUNE destination vivante (meilleure : corpus.py:160 timing_profile 0.237)
      plus proche hors vivant : rules.py:175 check_transfert_poids (0.595, en veille)
      nombres absents des 3 meilleures vivantes : 0.16, 0.21, 0.33, 0.39, 0.74, 0.84, 0.92
      termes clés absents : pousse, recula, lourde, rule, bouge, projet, plante
LECONS.md §8 (l.153) « 8. Des règles au vert ne veulent pas dire un corps juste » -> outils/rappel.py:1 module (0.232, partielle)
      termes clés absents : veulen, mesura, manqua, placem
LECONS.md §10 (l.162) « 10. On règle la hauteur du coup avec le corps, pas avec l'an » -> AUCUNE destination vivante (meilleure : corpus/CARNET.md:38 1.2 0.183)
      plus proche hors vivant : rules.py:146 check_bras_au_contact (0.548, en veille)
      plus proche hors vivant : ../../r6_poing_dragon/scripts/dragon_clip.py:580 attacker_keys (0.355, production)
      nombres absents des 3 meilleures vivantes : 4.25, 30
      termes clés absents : pro, rule, fente, check, hauteu, cible, foie, pouvai, plexu, exempl
LECONS.md §11 (l.183) « 11. Un coup droit arme haut et voyage à plat » -> AUCUNE destination vivante (meilleure : corpus.py:304 strike_mechanics 0.155)
      plus proche hors vivant : ../../r6_poing_dragon/scripts/dragon_clip.py:580 attacker_keys (0.316, production)
      plus proche hors vivant : ../../r6_m1_v222/scripts/m1_clip.py:51 attacker_keys (0.257, production)
      nombres absents des 3 meilleures vivantes : 0.02, 0.05, 0.09, 0.2, 0.22, 0.3, 0.32, 0.34, 0.48, 0.59, 1.1, 1.3
      termes clés absents : lourd, moyenn, style, vient, corpu, copier
```

## `CERVEAU_V2.md`

```
CERVEAU_V2.md §en-tête (l.1) « Cerveau v2 : juger, réfléchir, se corriger » -> (bandeau, non cherché)
CERVEAU_V2.md §Pourquoi changer (l.15) « Pourquoi changer » -> outils/draw.py:1 module (0.412, partielle)
      plus proche hors vivant : critic.py:1 module (0.503, en veille)
      termes clés absents : trompe, quatre, vert, yeux, passai, postur, escala, bouge, suite, poid
CERVEAU_V2.md §La boucle (l.30) « La boucle » -> corpus/CARNET.md:794 6 (0.421, partielle)
      plus proche hors vivant : critic.py:1 module (0.855, en veille)
      plus proche hors vivant : critic.py:169 reflect (0.601, en veille)
      termes clés absents : percev, reflec, etat, poid, suspec, stagne
CERVEAU_V2.md §Premier passage (2026-09-24) (l.46) « Premier passage (2026-09-24) » -> AUCUNE destination vivante (meilleure : corpus/CARNET.md:108 1.9 0.192)
      plus proche hors vivant : critic.py:1 module (0.405, en veille)
      plus proche hors vivant : ../../r6_battle_throne/scripts/throne_sequence.py:51 sit_and_crown (0.266, production)
      nombres absents des 3 meilleures vivantes : 0.7
      termes clés absents : apport, plafon, choc, corrig, statis, isolee, guide, vont, suspec, stagne
CERVEAU_V2.md §Perception branchée au jugement (2026-09-24, sui… (l.70) « Perception branchée au jugement (2026-09-24, suite) » -> perception.py:1 module (0.369, partielle)
      plus proche hors vivant : etats.py:1 module (0.593, en veille)
      plus proche hors vivant : critic.py:169 reflect (0.487, en veille)
      termes clés absents : style, etalon, partie, aime, jugeme, poid, rejete
CERVEAU_V2.md §Ce que la mesure a corrigé (l.99) « Ce que la mesure a corrigé » -> AUCUNE destination vivante (meilleure : perception.py:1 module 0.195)
      plus proche hors vivant : etats.py:155 etat_version (0.326, en veille)
      plus proche hors vivant : critic.py:169 reflect (0.201, en veille)
      nombres absents des 3 meilleures vivantes : 0.14, 0.21, 0.33, 0.4, 0.41, 0.43, 0.65, 0.7, 1.94, 2.73, 2.9, 4.2
      termes clés absents : aime, rafale, rejete, jugeai, fluidi, tempo, style, suspec, variet
CERVEAU_V2.md §Flux optique (clip_analyzer, bloc mouvement) (l.149) « Flux optique (`clip_analyzer`, bloc `mouvement`) » -> AUCUNE destination vivante (meilleure : clip_analyzer.py:241 _motion 0.245)
      plus proche hors vivant : ../../r6_poing_dragon/scripts/dragon_clip.py:1045 aerien_v9 (0.268, production)
      nombres absents des 3 meilleures vivantes : 0.39, 0.46
      termes clés absents : valida, connue, verite, analyz, valide, etant
CERVEAU_V2.md §Regle d'usage (retour de Milan, 2026-09-24) (l.166) « Regle d'usage (retour de Milan, 2026-09-24) » -> AUCUNE destination vivante (meilleure : corpus/CARNET.md:1 en-tête 0.255)
      plus proche hors vivant : critic.py:1 module (0.363, en veille)
      termes clés absents : bon, princi, reserv, mal, indica, endroi, escala
CERVEAU_V2.md §Le champ des références (Milan) (l.174) « Le champ des références (Milan) » -> AUCUNE destination vivante (meilleure : corpus/fiches/COUP_CHARGE.md:46 2 0.161)
      termes clés absents : indepe, startu, mob, metier, case, man, jeux, ball, active
CERVEAU_V2.md §Outils repérés (recherche web du 2026-09-24) (l.186) « Outils repérés (recherche web du 2026-09-24) » -> clip_analyzer.py:1 module (0.336, partielle)
      nombres absents des 3 meilleures vivantes : 200
      termes clés absents : sakuga, galler, dlp, instal, rbx, donner, decrit, multip, fbx, exige
CERVEAU_V2.md §Réseau (l.208) « Réseau » -> AUCUNE destination vivante (meilleure : outils/moisson_milan.py:1 module 0.227)
      termes clés absents : reseau, domain, proxy, autori, refuse, github, tant
CERVEAU_V2.md §Prochaines étapes item 0 (l.218) « 0. Scrapeur écrit et testé hors ligne (scraper/, 11/11 avec  » -> AUCUNE destination vivante (meilleure : outils/rapport_regard.py:1 module 0.22)
      plus proche hors vivant : critic.py:1 module (0.248, en veille)
      termes clés absents : scrape, acce, sakuga, passen, local
CERVEAU_V2.md §Prochaines étapes item 1 (l.221) « 1. Réseau ouvert → scrapeur : Sakugabooru par étiquettes et  » -> clip_analyzer.py:365 main (0.345, partielle)
      termes clés absents : etique, ouvert, passe
CERVEAU_V2.md §Prochaines étapes item 2 (l.224) « 2. Bibliothèque de coups (une fiche par type : intention, ph » -> corpus/CARNET.md:1 en-tête (0.311, partielle)
      termes clés absents : biblio, intent, type, phase
CERVEAU_V2.md §Prochaines étapes item 3 (l.227) « 3. Rendre mesurables les suspects : profil autour du choc su » -> perception.py:1 module (0.339, partielle)
      termes clés absents : suspec, rendre, mesura, courbu, trajec
CERVEAU_V2.md §Prochaines étapes item 4 (l.230) « 4. Coup final à la Saitama : 3 variantes jugées par le criti » -> corpus/CARNET.md:233 2.2 (0.333, partielle)
      plus proche hors vivant : critic.py:1 module (0.376, en veille)
      termes clés absents : saitam, choi
```

## `PLAN.md`

```
PLAN.md §en-tête (l.1) « Cerveau d'animateur — audit honnête et plan (2026-09-23) » -> (bandeau, non cherché)
PLAN.md §0 (l.14) « 0. La cible, reformulée » -> AUCUNE destination vivante (meilleure : corpus/CARNET.md:1 en-tête 0.206)
      termes clés absents : fais, video, jeux, bon, battle, recett, fluide, niveau
PLAN.md §1 item 1 (l.26) « 1. On fabrique des cinématiques, pas des animations de jeu.  » -> AUCUNE destination vivante (meilleure : taxonomy.py:1 module 0.298)
      nombres absents des 3 meilleures vivantes : 8.2, 842
      termes clés absents : fabriq, film, jugee, dure, trou, premiu, back
PLAN.md §1 item 2 (l.42) « 2. On pose à l'aveugle. Les poses sont des angles d'Euler ta » -> AUCUNE destination vivante (meilleure : poses.py:1 module 0.161)
      plus proche hors vivant : ../../r6_poing_dragon/scripts/render_poses.py:1 module (0.178, production)
      plus proche hors vivant : ../../r6_black_hole/scripts/choreography.py:1 module (0.173, production)
      termes clés absents : justem, aveugl, tape, etique, critiq, preuve, charac, rendu
PLAN.md §1 item 3 (l.49) « 3. Nos mesures prouvent l'absence de défauts, pas la qualité » -> outils/rapport_regard.py:1 module (0.265, partielle)
      termes clés absents : lisibi, prouve, moi, claque, timing, vraie
PLAN.md §1 item 4 (l.55) « 4. Le pack premium n'a servi qu'une fois, pour trois amplitu » -> AUCUNE destination vivante (meilleure : corpus/CARNET.md:108 1.9 0.249)
      plus proche hors vivant : ../../r6_m1_v222/scripts/m1_clip.py:1 module (0.266, production)
      termes clés absents : copier, verse, premiu, exacte
PLAN.md §1 item 5 (l.58) « 5. Les VFX ne sont pas du Roblox. Ils n'existent que dans un » -> corpus/fiches/VFX.md:72 3 (0.384, partielle)
      termes clés absents : mettre, livre, declen
PLAN.md §1 item 6 (l.62) « 6. Il n'y a pas de victime. Dans TSB, une technique, c'est u » -> outils/moisson_milan.py:1 module (0.286, partielle)
      termes clés absents : manneq, synchr, atterr, video, pro
PLAN.md §1 item 7 (l.67) « 7. Rig maison au lieu du rig standard. V2.22, c'est le rig d » -> AUCUNE destination vivante (meilleure : corpus/CARNET.md:794 6 0.179)
      plus proche hors vivant : ../../r6_poing_dragon/scripts/dragon_clip.py:1 module (0.317, production)
      plus proche hors vivant : rules.py:1 module (0.308, en veille)
      termes clés absents : recons, maison, standa, pro, visibl, lieu, target
PLAN.md §1 item 8 (l.71) « 8. L'aperçu ne ressemble pas au rendu Roblox. Éclairage et m » -> AUCUNE destination vivante (meilleure : corpus/fiches/COUP_CHARGE.md:82 3 0.226)
      termes clés absents : suivie, ressem, jaune, projet, projec, tour, manneq
PLAN.md §2 (l.80) « 2. Ce que les deux outils apportent, et leurs limites ici » -> (moins de 60 caractères, non cherché)
PLAN.md §dillydog580/animate-roblox-characters (l.82) « `dillydog580/animate-roblox-characters` » -> AUCUNE destination vivante (meilleure : organic.py:1 module 0.201)
      plus proche hors vivant : rules.py:55 check_affaissement (0.35, en veille)
      plus proche hors vivant : ../../r6_aerial_kick_combo/scripts/choreography.py:263 cycle_5 (0.35, production)
      termes clés absents : method, repren, script, connai, clone, blende, skill, mcp, locomo, editor
PLAN.md §R6 IK + FK Blender Rig V2.22 (l.110) « R6 IK + FK Blender Rig V2.22 » -> v222_rig.py:1 module (0.337, partielle)
      nombres absents des 3 meilleures vivantes : 93444
      termes clés absents : devfor, telech, proxy, hui, aujour, etique, envoie, soluti
PLAN.md §3 (l.122) « 3. Ce qu'il faut ajouter : l'architecture cible » -> taxonomy.py:1 module (0.667, complète)
PLAN.md §4 (l.161) « 4. Plan séquencé » -> AUCUNE destination vivante (meilleure : build_corpus.py:1 module 0.199)
      plus proche hors vivant : ../../r6_aerial_kick_combo/scripts/choreography.py:422 cycle_7 (0.309, production)
      plus proche hors vivant : ../../r6_m1_v222/scripts/m1_clip.py:1 module (0.286, production)
      nombres absents des 3 meilleures vivantes : 0.22, 0.65
      termes clés absents : revue, choc, rigs, luau, video, packag, hypoth
PLAN.md §5 (l.176) « 5. Risques, dits franchement » -> corpus/fiches/VFX.md:41 2 (0.441, partielle)
      termes clés absents : com, licenc, rendu, exact, verra, statis, fiable, dillyd, access, risque
```

## `REFLEXION.md`

```
REFLEXION.md §en-tête (l.1) « Reflexion du critique » -> (bandeau, non cherché)
REFLEXION.md §Mes predictions contre les notes de Milan, PAR A… (l.9) « Mes predictions contre les notes de Milan, PAR AXE » -> AUCUNE destination vivante (meilleure : corpus/CARNET.md:794 6 0.27)
      plus proche hors vivant : critic.py:132 biais_predictions (0.332, en veille)
      nombres absents des 3 meilleures vivantes : 6.8, 7.2, 7.4, 7.5, 7.7, 7.8, 7.9
      termes clés absents : moyen, premiu, techni, axe
REFLEXION.md §Predictions contre notes de Milan (poids avant a… (l.14) « Predictions contre notes de Milan (poids avant apprentissage » -> AUCUNE destination vivante (meilleure : corpus/CARNET.md:794 6 0.282)
      plus proche hors vivant : critic.py:1 module (0.478, en veille)
      plus proche hors vivant : critic.py:100 predict (0.408, en veille)
      nombres absents des 3 meilleures vivantes : 0.2, 6, 6.3, 6.4, 6.7, 6.8, 7, 7.3, 7.5, 7.7
      termes clés absents : ecart, poid
REFLEXION.md §Ce qui a change entre deux versions notees (l.23) « Ce qui a change entre deux versions notees » -> AUCUNE destination vivante (meilleure : corpus/fiches/POING_DU_DRAGON_V13.md:33 2 0.148)
      plus proche hors vivant : critic.py:169 reflect (0.231, en veille)
      plus proche hors vivant : ../../r6_un_seul_coup/scripts/staging.py:70 camera_keys (0.196, production)
      nombres absents des 3 meilleures vivantes : 0.2, 0.7, 6, 6.7, 6.8, 7.5
      termes clés absents : perdue, ramene, libre, tronc, croi, postur, escala, arcs, rempla, intent
REFLEXION.md §Suspects (toujours faux sur toutes les versions … (l.31) « Suspects (toujours faux sur toutes les versions notees, note » -> AUCUNE destination vivante (meilleure : outils/rapport_regard.py:191 lectures 0.232)
      termes clés absents : haven, smear, corpu, mattes, arcsy, force, video, pack, arrier, devfor
REFLEXION.md §Ou la mesure contredit le jugement manuel (etats… (l.38) « Ou la mesure contredit le jugement manuel (etats.py) » -> outils/amorce.py:70 main (0.367, partielle)
      plus proche hors vivant : etats.py:247 main (0.525, en veille)
      plus proche hors vivant : etats.py:1 module (0.512, en veille)
      termes clés absents : jugeme
REFLEXION.md §Parties aimees contre parties rejetees (l.42) « Parties aimees contre parties rejetees » -> AUCUNE destination vivante (meilleure : plots.py:1 module 0.186)
      plus proche hors vivant : critic.py:169 reflect (0.499, en veille)
      plus proche hors vivant : ../../r6_m1_v222/scripts/m1_clip.py:86 victim_tracks (0.26, production)
      nombres absents des 3 meilleures vivantes : 43
      termes clés absents : rejete, vraie, aimee, discri, rejett, poid, aime, hausse, fausse, tester
REFLEXION.md §Jamais mesurees (angle mort du cerveau) (l.63) « Jamais mesurees (angle mort du cerveau) » -> corpus/CARNET.md:563 4b.13 (0.346, partielle)
      termes clés absents : effort, souven, masse, equili, mort, amorti, vivant, reglag
REFLEXION.md §Echelle calibree sur 7 notes : note = 7.02 + 0.9… (l.82) « Echelle calibree sur 7 notes : note = 7.02 + 0.97 x score » -> (moins de 60 caractères, non cherché)
REFLEXION.md §Poids appris (ce qui fait bouger la note de Mila… (l.84) « Poids appris (ce qui fait bouger la note de Milan) » -> AUCUNE destination vivante (meilleure : outils/rappel.py:1 module 0.219)
      plus proche hors vivant : ../../r6_un_seul_coup/scripts/coup_clip.py:113 attacker_keys (0.335, production)
      plus proche hors vivant : ../../r6_black_hole/scripts/choreography.py:161 _grounded (0.321, production)
      nombres absents des 3 meilleures vivantes : 0.25, 0.4, 0.43, 0.5, 0.51, 0.54, 0.55, 0.58, 0.6, 0.64, 0.65, 0.7
      termes clés absents : poid, vivant, effort, deform, persis, variet, acte
REFLEXION.md §Predictions apres apprentissage (l.147) « Predictions apres apprentissage » -> corpus/CARNET.md:794 6 (0.338, partielle)
      plus proche hors vivant : critic.py:1 module (0.543, en veille)
      plus proche hors vivant : critic.py:100 predict (0.402, en veille)
      nombres absents des 3 meilleures vivantes : 6, 6.2, 6.5, 6.7, 6.8, 7, 7.3, 7.5, 7.7
```

## `ANGLES_MORTS.md`

```
ANGLES_MORTS.md §en-tête (l.1) « Angles morts : ce qui manquait dans la direction et le dével » -> (bandeau, non cherché)
ANGLES_MORTS.md §1 (l.17) « 1. Quel « coup final » ? Le plus gros angle mort » -> outils/rappel.py:1 module (0.257, partielle)
      nombres absents des 3 meilleures vivantes : 5.9
      termes clés absents : upperc, lanceu, aucune, droit, boule, liste
ANGLES_MORTS.md §2 (l.51) « 2. La fluidité : le défaut mesuré qu'aucune règle ne voyait » -> AUCUNE destination vivante (meilleure : perception.py:1 module 0.227)
      plus proche hors vivant : ../../r6_poing_dragon/scripts/dragon_clip.py:1370 interp_args (0.38, production)
      nombres absents des 3 meilleures vivantes : 3.5, 4.2, 5.7, 7.5, 11.9
      termes clés absents : poigne, aime, rom, rejett, bridee
ANGLES_MORTS.md §3 (l.83) « 3. Jamais vu dans Roblox Studio » -> AUCUNE destination vivante (meilleure : corpus/CARNET.md:629 4b.20 0.18)
      plus proche hors vivant : ../../r6_poing_dragon/scripts/staging.py:1 module (0.236, production)
      plus proche hors vivant : ../../r6_poing_dragon/scripts/verify_export.py:114 main (0.209, production)
      nombres absents des 3 meilleures vivantes : 36
      termes clés absents : linear, offici, test, doc, html, minute, ecriva, connai, interp, propre
ANGLES_MORTS.md §4 (l.103) « 4. Les notes ne suffisent pas à apprendre » -> AUCUNE destination vivante (meilleure : corpus/fiches/COUP_CHARGE.md:140 4 0.236)
      plus proche hors vivant : critic.py:1 module (0.237, en veille)
      termes clés absents : minute, inform, preci, design, rythme, suffis, determ, immedi
ANGLES_MORTS.md §5 (l.112) « 5. Le style visé n'était écrit nulle part » -> corpus/CARNET.md:794 6 (0.216, partielle)
      plus proche hors vivant : critic.py:83 style_warnings (0.255, en veille)
      termes clés absents : etalon, vise, viendr, realis, mainte, nulle
ANGLES_MORTS.md §6 (l.121) « 6. Il manque le niveau « intention » » -> AUCUNE destination vivante (meilleure : corpus/CARNET.md:54 1.3 0.193)
      termes clés absents : intent, pressi, optimi, valide, enorme, phrase, manque, docume
ANGLES_MORTS.md §7 (l.131) « 7. Toute mesure doit passer un test sur une vérité connue » -> AUCUNE destination vivante (meilleure : clip_analyzer.py:241 _motion 0.149)
      plus proche hors vivant : ../../r6_poing_dragon/scripts/dragon_clip.py:1130 aerien_v10 (0.189, production)
      plus proche hors vivant : ../../r6_poing_dragon/scripts/dragon_clip.py:1045 aerien_v9 (0.184, production)
      nombres absents des 3 meilleures vivantes : 0.39, 0.46
      termes clés absents : valide, connai, versio, connue, parti, domine, analyz, sait
ANGLES_MORTS.md §7b (l.152) « 7b. Les poids appris ne l'étaient pas » -> AUCUNE destination vivante (meilleure : corpus/CARNET.md:1 en-tête 0.218)
      plus proche hors vivant : critic.py:169 reflect (0.519, en veille)
      plus proche hors vivant : critic.py:1 module (0.486, en veille)
      termes clés absents : poid, lancem, deriva, jour, reflec, priori, rejoue, nombre
ANGLES_MORTS.md §8 (l.158) « 8. Ce que le cerveau ne sait pas encore voir » -> AUCUNE destination vivante (meilleure : outils/rappel.py:1 module 0.261)
      termes clés absents : rbx, pourra, masque, detach, bloque, surfac, rendu
ANGLES_MORTS.md §Ordre proposé item 1 (l.169) « 1. Milan confirme le « coup final » (f90 ou f150) et donne u » -> corpus/CARNET.md:794 6 (0.361, partielle)
      termes clés absents : intent, donne
ANGLES_MORTS.md §Ordre proposé item 2 (l.171) « 2. Variantes de fluidité (poignées, chevauchement) : jugées  » -> AUCUNE destination vivante (meilleure : corpus/CARNET.md:233 2.2 0.291)
      termes clés absents : chevau, percep, poigne, fluidi
ANGLES_MORTS.md §Ordre proposé item 3 (l.173) « 3. Final à la Saitama en 3 variantes, sur le bon temps. » -> (moins de 60 caractères, non cherché)
ANGLES_MORTS.md §Ordre proposé item 4 (l.174) « 4. Test dans Roblox Studio, dès que possible. » -> (moins de 60 caractères, non cherché)
```

## `SCENE_POING_DU_DRAGON.md`

```
SCENE_POING_DU_DRAGON.md §en-tête (l.1) « Proposition : « Poing du Dragon », une technique ultime comp » -> (bandeau, non cherché)
SCENE_POING_DU_DRAGON.md §L'idée en une phrase (l.19) « L'idée en une phrase » -> corpus/CARNET.md:563 4b.13 (0.394, partielle)
      termes clés absents : vienne, revela, rejoin, git, phrase, lance, palett
SCENE_POING_DU_DRAGON.md §Découpage (frames à 60 i/s, le rythme d'export d… (l.30) « Découpage (frames à 60 i/s, le rythme d'export du pack pro) » -> AUCUNE destination vivante (meilleure : corpus/CARNET.md:563 4b.13 0.183)
      plus proche hors vivant : ../../r6_poing_dragon/scripts/dragon_clip.py:580 attacker_keys (0.264, production)
      plus proche hors vivant : ../../r6_un_seul_coup/scripts/coup_clip.py:113 attacker_keys (0.209, production)
      nombres absents des 3 meilleures vivantes : 0.07, 0.1, 0.43, 0.67, 0.8, 0.93, 1.08, 1.9, 2.8, 13, 18, 24
      termes clés absents : pack, upperc, rythme, accrou, pics, titube, dissip, irregu, downsl
SCENE_POING_DU_DRAGON.md §Ce qu'on livre (pour Roblox, pas seulement un ap… item 1 (l.54) « 1. Deux KeyframeSequence (attaquant, victime), faites sur de » -> AUCUNE destination vivante (meilleure : corpus/CARNET.md:693 4b.26 0.18)
      plus proche hors vivant : ../../r6_poing_dragon/scripts/dragon_clip.py:1437 main (0.306, production)
      plus proche hors vivant : ../../r6_poing_dragon/scripts/dragon_clip.py:49 _rafale_cfg (0.293, production)
      termes clés absents : launch, reveal, evenem, rigs, strike
SCENE_POING_DU_DRAGON.md §Ce qu'on livre (pour Roblox, pas seulement un ap… item 2 (l.57) « 2. Une piste caméra animée dans Blender avec le rig, exporté » -> corpus/fiches/AURA_DRAGON.md:126 3 (0.426, partielle)
      termes clés absents : jouee, marker
SCENE_POING_DU_DRAGON.md §Ce qu'on livre (pour Roblox, pas seulement un ap… item 3 (l.59) « 3. Des VFX en vraies instances, dimensionnés sur le corpus V » -> corpus/fiches/VFX.md:41 2 (0.494, partielle)
      termes clés absents : dimens, pilote, vraie, rafale
SCENE_POING_DU_DRAGON.md §Ce qu'on livre (pour Roblox, pas seulement un ap… item 4 (l.64) « 4. Les effets plein écran : teinte du corps (Highlight sur 1 » -> AUCUNE destination vivante (meilleure : corpus/fiches/POING_DU_DRAGON_V13.md:89 5 0.233)
      plus proche hors vivant : ../../r6_poing_dragon/scripts/staging.py:1 module (0.284, production)
      termes clés absents : brouil, etalon, highli, teinte
SCENE_POING_DU_DRAGON.md §Ce qu'on livre (pour Roblox, pas seulement un ap… item 5 (l.67) « 5. Le cratère : des pics de pierre générés en Parts autour d » -> outils/planche_ref.py:1 module (0.245, partielle)
      plus proche hors vivant : ../../r6_un_seul_coup/scripts/staging.py:209 events (0.259, production)
      termes clés absents : soulev, genere
SCENE_POING_DU_DRAGON.md §Ce qu'on livre (pour Roblox, pas seulement un ap… item 6 (l.70) « 6. Un module Luau qui orchestre le tout, plus la démo et le  » -> corpus/fiches/VFX.md:109 4 (0.405, partielle)
      plus proche hors vivant : ../../r6_un_seul_coup/scripts/build_roblox_package.py:1 module (0.633, production)
      plus proche hors vivant : ../../r6_un_seul_coup/scripts/build_roblox_package.py:120 build (0.549, production)
      termes clés absents : demo, sens
SCENE_POING_DU_DRAGON.md §Ce qu'on livre (pour Roblox, pas seulement un ap… item 7 (l.71) « 7. Un aperçu jouable dans le lecteur, comme pour le M1, avec » -> corpus/fiches/AURA_DRAGON.md:1 en-tête (0.416, partielle)
      plus proche hors vivant : ../../r6_poing_dragon/scripts/build_player.py:1 module (0.477, production)
      plus proche hors vivant : ../../r6_un_seul_coup/scripts/build_player.py:1 module (0.477, production)
SCENE_POING_DU_DRAGON.md §Ce que le cerveau sait déjà faire, ce qui est no… (l.74) « Ce que le cerveau sait déjà faire, ce qui est nouveau » -> taxonomy.py:1 module (0.41, partielle)
      termes clés absents : nouvea, dimens, hui, ejecti, aujour, lointa, solveu
SCENE_POING_DU_DRAGON.md §Limites, dites franchement (l.88) « Limites, dites franchement » -> corpus/fiches/VFX.md:72 3 (0.5, partielle)
      termes clés absents : asset, devron, ids, dite, honnet, repren, crane, table, genera, config
SCENE_POING_DU_DRAGON.md §Production proposée (chaque lot donne une sortie… item 1 (l.105) « 1. Blocking des poses clés sur les deux rigs : 12 poses. Pou » -> tracks.py:1 module (0.312, partielle)
      termes clés absents : valide, critiq, rigs, ecrite
SCENE_POING_DU_DRAGON.md §Production proposée (chaque lot donne une sortie… item 2 (l.108) « 2. Animation complète + verdict du corpus par segment : rafa » -> taxonomy.py:1 module (0.49, partielle)
      plus proche hors vivant : ../../r6_poing_dragon/scripts/verify_export.py:1 module (0.843, production)
      plus proche hors vivant : ../../r6_poing_dragon/scripts/dragon_clip.py:1 module (0.502, production)
      termes clés absents : verdic, segmen
SCENE_POING_DU_DRAGON.md §Production proposée (chaque lot donne une sortie… item 3 (l.111) « 3. Piste caméra + export. » -> (moins de 60 caractères, non cherché)
SCENE_POING_DU_DRAGON.md §Production proposée (chaque lot donne une sortie… item 4 (l.112) « 4. VFX (impacts, dragon de fumée, cratère), effets plein écr » -> corpus/fiches/POING_DU_DRAGON_V13.md:89 5 (0.457, partielle)
      termes clés absents : genere
SCENE_POING_DU_DRAGON.md §Production proposée (chaque lot donne une sortie… item 5 (l.114) « 5. Package Roblox + module Luau + test de sens. » -> (moins de 60 caractères, non cherché)
SCENE_POING_DU_DRAGON.md §Production proposée (chaque lot donne une sortie… item 6 (l.115) « 6. Lecteur jouable avec tout, publié dans l'artifact. » -> (moins de 60 caractères, non cherché)
```

## `corpus/ETUDE_NOTES_BRUTES.md`

```
corpus/ETUDE_NOTES_BRUTES.md §en-tête (l.1) « Notes d'etude (brutes) » -> (moins de 60 caractères, non cherché)
corpus/ETUDE_NOTES_BRUTES.md §coup chapeau (Roblox, LeftRight2601 / VFX Matchl… (l.3) « coup chapeau (Roblox, LeftRight2601 / VFX Matchless) » -> corpus/CARNET.md:647 4b.21 (0.455, partielle)
      plus proche hors vivant : ../../r6_battle_throne/scripts/props_battle.py:88 pillar_debris_parts (0.519, production)
      termes clés absents : noir, explos, debri, cible, chapea, peine, boum, concen, petite, noire
corpus/ETUDE_NOTES_BRUTES.md §Black Flash (Roblox JJK) (l.8) « Black Flash (Roblox JJK) » -> corpus/fiches/COUP_CHARGE.md:82 3 (0.403, partielle)
      plus proche hors vivant : ../../r6_poing_dragon/scripts/regard_v7.py:42 cam_jeu_serre (0.412, production)
      plus proche hors vivant : ../../r6_poing_dragon/scripts/regard_v7_vs_tsb.py:35 cam (0.412, production)
      termes clés absents : lointa, stylis, croi, proche, penche
corpus/ETUDE_NOTES_BRUTES.md §double jab R6 (Roblox) (l.13) « double jab R6 (Roblox) » -> corpus/fiches/AURA_DRAGON.md:50 0 bis (0.39, partielle)
      termes clés absents : extens, double, jab
corpus/ETUDE_NOTES_BRUTES.md §combo R6 front (test pro, rig colore) (l.16) « combo R6 front (test pro, rig colore) » -> corpus/CARNET.md:402 3.6 (0.412, partielle)
      termes clés absents : front, colore, toupie, enorme, back, test, pro, entier, passe, buste
corpus/ETUDE_NOTES_BRUTES.md §serious punch 2 (Roblox) (l.19) « serious punch 2 (Roblox) » -> corpus/fiches/UN_SEUL_COUP.md:21 1 (0.527, partielle)
      termes clés absents : dissip, revele, croqui, lentem, cadrag, ramass, rempli, eclat, secous
corpus/ETUDE_NOTES_BRUTES.md §IMPACT HAVEN (Roblox, TikTok) (l.24) « IMPACT HAVEN (Roblox, TikTok) » -> corpus/fiches/UN_SEUL_COUP.md:60 3 (0.388, partielle)
      termes clés absents : diagon, ras, haven, sage, extrem, flash
corpus/ETUDE_NOTES_BRUTES.md §exemple blender combat (l.29) « exemple blender combat » -> taxonomy.py:1 module (0.206, partielle)
      plus proche hors vivant : ../../r6_directional_punch/scripts/choreography.py:339 dummy_reaction (0.227, production)
      plus proche hors vivant : ../../r6_poing_dragon/scripts/dragon_clip.py:1 module (0.218, production)
      termes clés absents : emmele, effond, colle, totale
corpus/ETUDE_NOTES_BRUTES.md §moon animator combo (tuto comparatif) (l.32) « moon animator combo (tuto comparatif) » -> outils/rappel.py:1 module (0.352, partielle)
      termes clés absents : easing, lineai
corpus/ETUDE_NOTES_BRUTES.md §pro vs noob poing (TikTok, test pro vs debutant) (l.35) « pro vs noob poing (TikTok, test pro vs debutant) » -> corpus/fiches/VFX.md:72 3 (0.454, partielle)
      termes clés absents : pro, noob, torsio, raide, debuta, colle, enorme, symetr, test, basse
corpus/ETUDE_NOTES_BRUTES.md §mii smash (hitbox) (l.39) « mii smash (hitbox) » -> clip_analyzer.py:342 _sheet (0.412, partielle)
      termes clés absents : visait, sorti, smash, fleche, doute, accrou, boule, normal, combat, ecarte
corpus/ETUDE_NOTES_BRUTES.md §Black Hole Ability (ref 15-52-25, Roblox) (l.43) « Black Hole Ability (ref 15-52-25, Roblox) » -> AUCUNE destination vivante (meilleure : corpus/fiches/VFX.md:41 2 0.184)
      plus proche hors vivant : ../../r6_black_hole/scripts/black_hole_track.py:1 module (0.187, production)
      termes clés absents : abilit, minusc, lointa, assomb, etoile, destru, recul, hole
corpus/ETUDE_NOTES_BRUTES.md §ref 17-51-39 (noob vs pro, epee) (l.48) « ref 17-51-39 (noob vs pro, epee) » -> AUCUNE destination vivante (meilleure : corpus/fiches/UN_SEUL_COUP.md:200 9 0.201)
      termes clés absents : deplie, pro, action, tordu, encomb, claire, chevau, vertic, differ
corpus/ETUDE_NOTES_BRUTES.md §Serious Punch TSB (Roblox, LE coup de ref) (l.52) « Serious Punch TSB (Roblox, LE coup de ref) » -> corpus/CARNET.md:655 4b.22 (0.412, partielle)
      plus proche hors vivant : ../../r6_poing_dragon/scripts/croquis_v7.py:46 charge (0.454, production)
      plus proche hors vivant : ../../r6_un_seul_coup/scripts/staging.py:235 sons (0.45, production)
      termes clés absents : jusque, croqui, dissou, gramma, saute, fouett, transi, ramass, ultime, rempli
corpus/ETUDE_NOTES_BRUTES.md §Rewind Clock (Roblox) (l.58) « Rewind Clock (Roblox) » -> corpus/fiches/AURA_DRAGON.md:1 en-tête (0.395, partielle)
      termes clés absents : crane, filtre, altern, negati, voit
corpus/ETUDE_NOTES_BRUTES.md §Stagnant Rage (Roblox, camera de jeu) (l.61) « Stagnant Rage (Roblox, camera de jeu) » -> corpus/fiches/UN_SEUL_COUP.md:38 2 (0.269, partielle)
      termes clés absents : gamepl, rempli, haute, portee, transl
corpus/ETUDE_NOTES_BRUTES.md §Gemini soleil (Roblox) (l.64) « Gemini soleil (Roblox) » -> corpus/fiches/POING_DU_DRAGON_V13.md:21 1 (0.5, partielle)
      termes clés absents : aura, gemini, jaune, eclat, visage, explos, boule, rayon
corpus/ETUDE_NOTES_BRUTES.md §NOUS v5, avec les memes yeux (jugement honnete) (l.68) « NOUS v5, avec les memes yeux (jugement honnete) » -> AUCUNE destination vivante (meilleure : corpus/fiches/PLEIN_ECRAN.md:30 2 0.198)
      plus proche hors vivant : ../../r6_poing_dragon/scripts/staging.py:1 module (0.237, production)
      plus proche hors vivant : ../../r6_aerial_kick_combo/scripts/measure.py:512 velocity_continuity (0.203, production)
      termes clés absents : suit, rejett, rejete, lisibi, honnet, invisi, chevau, confon
corpus/ETUDE_NOTES_BRUTES.md §danbooru 10719411 (Blue Archive, parodie JJK, 2D… (l.74) « danbooru 10719411 (Blue Archive, parodie JJK, 2D) + 10731543 » -> corpus/CARNET.md:321 2.9 (0.412, partielle)
      termes clés absents : arknig, raccou, inform, archiv, grosse, smear, geant, flou, blanch, rempli
corpus/ETUDE_NOTES_BRUTES.md §danbooru 11103062 (Touhou) : abstrait, cartes po… (l.77) « danbooru 11103062 (Touhou) : abstrait, cartes posterisees N/ » -> (moins de 60 caractères, non cherché)
corpus/ETUDE_NOTES_BRUTES.md §danbooru 12200340 (parodie Bob l'eponge / One Pi… (l.79) « danbooru 12200340 (parodie Bob l'eponge / One Piece Gear 5) » -> AUCUNE destination vivante (meilleure : corpus/fiches/COUP_CHARGE.md:46 2 0.254)
      termes clés absents : parodi, gear, bob, vert, piece, negati
corpus/ETUDE_NOTES_BRUTES.md §danbooru 10220725 (MHA Bakugo, fan anim) (l.81) « danbooru 10220725 (MHA Bakugo, fan anim) » -> AUCUNE destination vivante (meilleure : corpus/fiches/VFX.md:41 2 0.273)
      plus proche hors vivant : ../../r6_poing_dragon/scripts/staging.py:219 events (0.284, production)
      termes clés absents : explos, minusc, lueur, coupe, manga, anim, contra
corpus/ETUDE_NOTES_BRUTES.md §danbooru 9647288 (Umamusume, coup de pied haut) (l.84) « danbooru 9647288 (Umamusume, coup de pied haut) » -> AUCUNE destination vivante (meilleure : corpus/CARNET.md:436 3.9 0.14)
      plus proche hors vivant : ../../r6_poing_dragon/scripts/dragon_clip.py:1228 aerien_v13 (0.171, production)
      plus proche hors vivant : ../../r6_aerial_kick_combo/scripts/choreography.py:544 cycle_8 (0.146, production)
      termes clés absents : cheveu, toupie, inform, plafon, whip, renver, antici, haut
corpus/ETUDE_NOTES_BRUTES.md §danbooru 8783450 (Chainsaw Man, fan 3D Blender) (l.86) « danbooru 8783450 (Chainsaw Man, fan 3D Blender) » -> corpus/fiches/COUP_CHARGE.md:82 3 (0.293, partielle)
      plus proche hors vivant : ../../r6_poing_dragon/scripts/build_manga.py:1 module (0.336, production)
      termes clés absents : man, zoom, ensemb
corpus/ETUDE_NOTES_BRUTES.md §Danbooru en general (l.88) « Danbooru en general » -> AUCUNE destination vivante (meilleure : corpus/fiches/VFX.md:109 4 0.114)
      plus proche hors vivant : audit.py:456 frozen_fraction (0.138, en veille)
      nombres absents des 3 meilleures vivantes : 6340488, 7094635, 7642990, 8561129
      termes clés absents : cheveu, fighti, ponder, vent, suivi, depass, noir, clip
corpus/ETUDE_NOTES_BRUTES.md §sakuga 106678 (Boruto #65, Chengxi Huang / Weili… (l.91) « sakuga 106678 (Boruto #65, Chengxi Huang / Weilin Zhang, sco » -> AUCUNE destination vivante (meilleure : outils/planche_vfx.py:1 module 0.215)
      termes clés absents : echang, sakuga, flou, rappro, eclair, proche, total
corpus/ETUDE_NOTES_BRUTES.md §sakuga 121591 (Naruto 2002, Norio Matsumoto, sco… (l.93) « sakuga 121591 (Naruto 2002, Norio Matsumoto, score 3576) » -> AUCUNE destination vivante (meilleure : corpus/fiches/UN_SEUL_COUP.md:225 10 0.258)
      termes clés absents : minusc, enver, yeux, inclin, tensio, intent, score, action, seulem
corpus/ETUDE_NOTES_BRUTES.md §sakuga 129853 (Hades trailer, Chengxi Huang) (l.97) « sakuga 129853 (Hades trailer, Chengxi Huang) » -> AUCUNE destination vivante (meilleure : corpus/fiches/UN_SEUL_COUP.md:60 3 0.188)
      plus proche hors vivant : ../../r6_divine_orb/scripts/calibrate.py:50 main (0.213, production)
      plus proche hors vivant : ../../r6_black_hole/scripts/black_hole_track.py:187 vignette_level (0.198, production)
      termes clés absents : dramat, ponctu, levee, beat
corpus/ETUDE_NOTES_BRUTES.md §sakuga 146024 (JJK #19, score 3058) (l.100) « sakuga 146024 (JJK #19, score 3058) » -> corpus/fiches/PLEIN_ECRAN.md:1 en-tête (0.237, partielle)
      termes clés absents : persis, enver, sakuga, score, trajec
corpus/ETUDE_NOTES_BRUTES.md §sakuga 134931 (Hajime no Ippo, Takeshi Koike, BO… (l.103) « sakuga 134931 (Hajime no Ippo, Takeshi Koike, BOXE) » -> AUCUNE destination vivante (meilleure : corpus/CARNET.md:402 3.6 0.206)
      termes clés absents : isoler, floue, deform, abstra, menton, lumier, rempla, joue, ecrase
corpus/ETUDE_NOTES_BRUTES.md §sakuga 140472 (JJK ED) : carte typographique (ka… (l.107) « sakuga 140472 (JJK ED) : carte typographique (kanji rouge su » -> (moins de 60 caractères, non cherché)
corpus/ETUDE_NOTES_BRUTES.md §sakuga 162980 (ONE PUNCH MAN #12, Saitama vs Bor… (l.109) « sakuga 162980 (ONE PUNCH MAN #12, Saitama vs Boros, score 43 » -> corpus/fiches/COUP_CHARGE.md:82 3 (0.516, partielle)
      termes clés absents : rose, man, eclat, determ, score, ensemb
corpus/ETUDE_NOTES_BRUTES.md §sakuga 150800 (Soul Eater NCOP2, Yutaka Nakamura… (l.113) « sakuga 150800 (Soul Eater NCOP2, Yutaka Nakamura, score 4190 » -> corpus/fiches/COUP_CHARGE.md:82 3 (0.259, partielle)
      termes clés absents : balaie, eclat, score, debri
corpus/ETUDE_NOTES_BRUTES.md §sakuga 157388 (Hajime no Ippo NCOP1) (l.115) « sakuga 157388 (Hajime no Ippo NCOP1) » -> corpus/fiches/UN_SEUL_COUP.md:151 7 (0.213, partielle)
      termes clés absents : muscle, tordu, deform, quart, tronc, enroul
corpus/ETUDE_NOTES_BRUTES.md §sakuga 160435 (Dragon Ball #139, Hisashi Eguchi) (l.118) « sakuga 160435 (Dragon Ball #139, Hisashi Eguchi) » -> corpus/fiches/AURA_DRAGON.md:1 en-tête (0.316, partielle)
      termes clés absents : isoler, rempla, ball
corpus/ETUDE_NOTES_BRUTES.md §sakuga 165486 (Kekkai Sensen #01, Yutaka Nakamur… (l.122) « sakuga 165486 (Kekkai Sensen #01, Yutaka Nakamura, score 589 » -> corpus/fiches/COUP_CHARGE.md:82 3 (0.57, complète)
corpus/ETUDE_NOTES_BRUTES.md §sakuga 152980 (OPM #05, Arifumi Imai) (l.125) « sakuga 152980 (OPM #05, Arifumi Imai) » -> corpus/fiches/COUP_CHARGE.md:82 3 (0.376, partielle)
      termes clés absents : strie, yeux, lumier, intent
corpus/ETUDE_NOTES_BRUTES.md §sakuga 198240 (L'Attaque des Titans S3 #39, Arif… (l.128) « sakuga 198240 (L'Attaque des Titans S3 #39, Arifumi Imai) » -> outils/ecoute.py:1 module (0.185, partielle)
      plus proche hors vivant : ../../r6_poing_dragon/scripts/build_cartes.py:1 module (0.265, production)
      plus proche hors vivant : ../../r6_poing_dragon/scripts/build_manga.py:1 module (0.252, production)
      termes clés absents : poster, croqui, blanch, projec
corpus/ETUDE_NOTES_BRUTES.md §sakuga 194936 (OPM #01, Saitama contre un geant) (l.130) « sakuga 194936 (OPM #01, Saitama contre un geant) » -> corpus/fiches/COUP_CHARGE.md:82 3 (0.628, complète)
corpus/ETUDE_NOTES_BRUTES.md §sakuga 200870 (MHA fan, Vincent Chansard) : plan… (l.134) « sakuga 200870 (MHA fan, Vincent Chansard) : plan large des d » -> (moins de 60 caractères, non cherché)
corpus/ETUDE_NOTES_BRUTES.md §sakuga 203287 (FMA:B NCOP2, Nakamura) : NOIR 2-4… (l.135) « sakuga 203287 (FMA:B NCOP2, Nakamura) : NOIR 2-4 f entre deu » -> (moins de 60 caractères, non cherché)
corpus/ETUDE_NOTES_BRUTES.md §sakuga 21578 (Ippo Rising OP) : gants qui traver… (l.136) « sakuga 21578 (Ippo Rising OP) : gants qui traversent la came » -> (moins de 60 caractères, non cherché)
corpus/ETUDE_NOTES_BRUTES.md §sakuga 208545 (MHA S3 #61, Nakamura, score 3737)… (l.137) « sakuga 208545 (MHA S3 #61, Nakamura, score 3737) : gros plan » -> (moins de 60 caractères, non cherché)
corpus/ETUDE_NOTES_BRUTES.md §sakuga 217484 (One Piece #1049, Katsumi Ishizuka… (l.139) « sakuga 217484 (One Piece #1049, Katsumi Ishizuka, score 4887 » -> corpus/fiches/COUP_CHARGE.md:82 3 (0.493, partielle)
      termes clés absents : cyan, altern, score
corpus/ETUDE_NOTES_BRUTES.md §sakuga 224239 (Hitori no Shita 3, decors 3D) (l.141) « sakuga 224239 (Hitori no Shita 3, decors 3D) » -> corpus/fiches/UN_SEUL_COUP.md:60 3 (0.235, partielle)
      termes clés absents : vole, echang, sakuga, proche
corpus/ETUDE_NOTES_BRUTES.md §sakuga 234269 (One Piece #1071 Gear 5, Weilin Zh… (l.143) « sakuga 234269 (One Piece #1071 Gear 5, Weilin Zhang) » -> corpus/fiches/COUP_CHARGE.md:82 3 (0.334, partielle)
      termes clés absents : stretc, squash, ecrase
corpus/ETUDE_NOTES_BRUTES.md §sakuga 203289 (Soul Eater #01, Nakamura) : choc … (l.145) « sakuga 203289 (Soul Eater #01, Nakamura) : choc d'armes = ge » -> (moins de 60 caractères, non cherché)
corpus/ETUDE_NOTES_BRUTES.md §sakuga 21581 (Ippo Rising OP, Hideki Sawada) : g… (l.147) « sakuga 21581 (Ippo Rising OP, Hideki Sawada) : gros plan gar » -> (moins de 60 caractères, non cherché)
corpus/ETUDE_NOTES_BRUTES.md §sakuga 234966 (One Piece #1072 Gear 5, Shinya) :… (l.148) « sakuga 234966 (One Piece #1072 Gear 5, Shinya) : charge = br » -> (moins de 60 caractères, non cherché)
corpus/ETUDE_NOTES_BRUTES.md §sakuga 239350 (DBS Broly, Gogeta) : montee d'aur… (l.149) « sakuga 239350 (DBS Broly, Gogeta) : montee d'aura tenue ~24  » -> (moins de 60 caractères, non cherché)
corpus/ETUDE_NOTES_BRUTES.md §sakuga 239942 (Castlevania, production) : encre … (l.150) « sakuga 239942 (Castlevania, production) : encre noir/blanc p » -> (moins de 60 caractères, non cherché)
corpus/ETUDE_NOTES_BRUTES.md §sakuga 281209 (MHA #23 Todoroki/Deku, Nakamura, … (l.152) « sakuga 281209 (MHA #23 Todoroki/Deku, Nakamura, score 4843) » -> corpus/fiches/POING_DU_DRAGON_V13.md:57 3 (0.476, partielle)
      plus proche hors vivant : ../../r6_poing_dragon/scripts/build_planches.py:1 module (0.504, production)
      termes clés absents : deku, noire, eclat, mha, sakuga, etoile, blanch, croi, radial, score
corpus/ETUDE_NOTES_BRUTES.md §sakuga 283895 (One Piece #934, Katsumi Ishizuka)… (l.154) « sakuga 283895 (One Piece #934, Katsumi Ishizuka) : visage gr » -> (moins de 60 caractères, non cherché)
corpus/ETUDE_NOTES_BRUTES.md §sakuga 244246 (JJK ED, Hironori Tanaka) : zoom d… (l.155) « sakuga 244246 (JJK ED, Hironori Tanaka) : zoom dans l'IRIS - » -> (moins de 60 caractères, non cherché)
corpus/ETUDE_NOTES_BRUTES.md §sakuga 252420 (JJK S2 #40) : persos minuscules q… (l.156) « sakuga 252420 (JJK S2 #40) : persos minuscules qui sautent e » -> (moins de 60 caractères, non cherché)
corpus/ETUDE_NOTES_BRUTES.md §sakuga 283898 (One Piece #978, Hiromi Ishigami /… (l.158) « sakuga 283898 (One Piece #978, Hiromi Ishigami / Masami Mori » -> corpus/fiches/COUP_CHARGE.md:82 3 (0.489, partielle)
      termes clés absents : rayure, eclate, hachur, eclat, score, encre
corpus/ETUDE_NOTES_BRUTES.md §sakuga 31295 (Dragon Ball #096, Naotoshi Shida, … (l.160) « sakuga 31295 (Dragon Ball #096, Naotoshi Shida, 1986) -- com » -> AUCUNE destination vivante (meilleure : corpus/fiches/UN_SEUL_COUP.md:60 3 0.212)
      termes clés absents : squash, nus, bouche, deform, classi, ball, ecrase, combat
corpus/ETUDE_NOTES_BRUTES.md §sakuga 250896 (Frieren #06) : charge a la hache … (l.162) « sakuga 250896 (Frieren #06) : charge a la hache en contre-pl » -> (moins de 60 caractères, non cherché)
corpus/ETUDE_NOTES_BRUTES.md §derniers : FLCL 293698 (formes plates graphiques… (l.164) « derniers : FLCL 293698 (formes plates graphiques, perso minu » -> (moins de 60 caractères, non cherché)
corpus/ETUDE_NOTES_BRUTES.md §Images fixes envoyees par Milan (2026-09, 15 ima… (l.166) « Images fixes envoyees par Milan (2026-09, 15 images) » -> corpus/fiches/COUP_CHARGE.md:82 3 (0.324, partielle)
      nombres absents des 3 meilleures vivantes : 14589186, 90118239
      termes clés absents : man, etudie, creato, doree, arrond, etoile, envoye, branch
corpus/ETUDE_NOTES_BRUTES.md §Derniers Danbooru (l.174) « Derniers Danbooru » -> AUCUNE destination vivante (meilleure : corpus/fiches/VFX.md:109 4 0.114)
      plus proche hors vivant : ../../r6_poing_dragon/scripts/build_cartes.py:1 module (0.16, production)
      plus proche hors vivant : audit.py:456 frozen_fraction (0.158, en veille)
      nombres absents des 3 meilleures vivantes : 6787236, 7525170, 8941534, 9671641
      termes clés absents : cinema, poster, raccou, archiv, gramma, eclat
corpus/ETUDE_NOTES_BRUTES.md §en-tête (l.179) « LOT 2 (Milan, 2026-09-24 soir) -- 5 videos Roblox / animatio » -> (moins de 60 caractères, non cherché)
corpus/ETUDE_NOTES_BRUTES.md §df406483 « First time fighting a dummy » (@drows… (l.181) « df406483 « First time fighting a dummy » (@drowsyrbx, Moon A » -> AUCUNE destination vivante (meilleure : corpus/CARNET.md:287 2.6b 0.183)
      plus proche hors vivant : ../../r6_poing_dragon/scripts/build_cartes.py:1 module (0.21, production)
      nombres absents des 3 meilleures vivantes : 0.25, 4.73, 4.8, 4.87, 4.97, 5.03, 5.1
      termes clés absents : serieu, griffe, comiqu, salve, cheveu, grosse, bloom, assomb, quart, brille
corpus/ETUDE_NOTES_BRUTES.md §8556a37c « cross punch » (@acertain_torwesley, M… (l.188) « 8556a37c « cross punch » (@acertain_torwesley, Moon Animator » -> AUCUNE destination vivante (meilleure : outils/rappel.py:1 module 0.169)
      plus proche hors vivant : ../../r6_poing_dragon/scripts/build_planches.py:298 soleil (0.304, production)
      nombres absents des 3 meilleures vivantes : 0.4, 0.47, 0.53
      termes clés absents : oreill, lisent, etoile, concen, queue, suiven
corpus/ETUDE_NOTES_BRUTES.md §f1b5bd4b « pro vs noob » (Blender, rig R6 colore… (l.194) « f1b5bd4b « pro vs noob » (Blender, rig R6 colore FRONT/BACK) » -> poses.py:1 module (0.411, partielle)
      plus proche hors vivant : ../../r6_battle_throne/scripts/props.py:184 crown_points (0.418, production)
      plus proche hors vivant : ../../r6_throne_crown/scripts/props.py:184 crown_points (0.418, production)
      termes clés absents : noob, colore, chambr, cercle, affich, coude, replie, debout
corpus/ETUDE_NOTES_BRUTES.md §6a0095ed « punch practice » (@acertain_torwesley… (l.199) « 6a0095ed « punch practice » (@acertain_torwesley avec LTGame » -> AUCUNE destination vivante (meilleure : outils/rappel.py:1 module 0.22)
      termes clés absents : vue, blanch, petite, cache, articu, plante, trajec
corpus/ETUDE_NOTES_BRUTES.md §afaa00eb tuto « Attacks Animation Tutorial - Pun… (l.205) « afaa00eb tuto « Attacks Animation Tutorial - Punches and Kic » -> corpus/CARNET.md:158 2.1 (0.421, partielle)
      termes clés absents : attack, oversh, punche, minimi, toward, possib, interv
corpus/ETUDE_NOTES_BRUTES.md §Mesures faites en reponse (3D, nos coups v5 cont… (l.211) « Mesures faites en reponse (3D, nos coups v5 contre M1 pro) » -> corpus/CARNET.md:196 2.1b (0.358, partielle)
      nombres absents des 3 meilleures vivantes : 137
      termes clés absents : armeme, repons, sauf, retien, pros, upperc, faite, existe, ecrase
corpus/ETUDE_NOTES_BRUTES.md §en-tête (l.215) « LOT 3 (Milan, 5 GIF de jeux battlegrounds, camera de JEU) » -> (moins de 60 caractères, non cherché)
corpus/ETUDE_NOTES_BRUTES.md §6d3be6e1 (jeu « Mythra », Tobi contre Shinso, ca… (l.217) « 6d3be6e1 (jeu « Mythra », Tobi contre Shinso, camera 3e pers » -> AUCUNE destination vivante (meilleure : corpus/fiches/UN_SEUL_COUP.md:21 1 0.153)
      plus proche hors vivant : ../../r6_battle_throne/scripts/props_battle.py:88 pillar_debris_parts (0.182, production)
      nombres absents des 3 meilleures vivantes : 2.33
      termes clés absents : joueur, tache, anneau, debri, emmele, eclabo, lutte, attrap, eclat, soulev
corpus/ETUDE_NOTES_BRUTES.md §449345ad (rue de nuit, M1 en place, vue de face) (l.222) « 449345ad (rue de nuit, M1 en place, vue de face) » -> AUCUNE destination vivante (meilleure : corpus/fiches/UN_SEUL_COUP.md:151 7 0.177)
      plus proche hors vivant : ../../r6_poing_dragon/scripts/staging.py:219 events (0.246, production)
      termes clés absents : minusc, flechi, eclat, rebond, double, existe, leger, taille, hierar, differ
corpus/ETUDE_NOTES_BRUTES.md §58322fc4 (boxeur type Ippo contre mannequin, ult… (l.227) « 58322fc4 (boxeur type Ippo contre mannequin, ultime, 11 s) » -> AUCUNE destination vivante (meilleure : corpus/fiches/UN_SEUL_COUP.md:21 1 0.187)
      plus proche hors vivant : ../../r6_poing_dragon/scripts/staging.py:94 camera_keys (0.28, production)
      plus proche hors vivant : ../../r6_poing_dragon/scripts/scene_v13.py:226 camera (0.236, production)
      nombres absents des 3 meilleures vivantes : 5.8, 8.4
      termes clés absents : boxeur, anneau, manneq, dissip, serie, esquiv, etince, nouvel, lues, ultime
corpus/ETUDE_NOTES_BRUTES.md §a0341700 (perso rose type Luffy, rafale « gatlin… (l.232) « a0341700 (perso rose type Luffy, rafale « gatling », camera  » -> corpus/fiches/UN_SEUL_COUP.md:102 5 (0.45, partielle)
      termes clés absents : rafale, masse, gatlin, rose, smear, blanch, rythme, anneau, suite, geste
corpus/ETUDE_NOTES_BRUTES.md §aafdc91d (perso orange, camera de jeu tres loint… (l.235) « aafdc91d (perso orange, camera de jeu tres lointaine) » -> corpus/CARNET.md:771 5 (0.412, partielle)
      termes clés absents : eclat, aafdc, lointa, elargi, envoye, orange, anneau
corpus/ETUDE_NOTES_BRUTES.md §en-tête (l.239) « LOT 4 (Milan) -- 4 videos deja etudiees, REVUES EN ENTIER (s » -> (moins de 60 caractères, non cherché)
corpus/ETUDE_NOTES_BRUTES.md §Black Flash (6,2 s) -- structure complete (l.241) « Black Flash (6,2 s) -- structure complete » -> AUCUNE destination vivante (meilleure : outils/rapport_regard.py:279 cams 0.275)
      plus proche hors vivant : ../../r6_poing_dragon/scripts/dragon_clip.py:1021 aerien_v8 (0.412, production)
      plus proche hors vivant : ../../r6_un_seul_coup/scripts/staging.py:144 decor (0.372, production)
      termes clés absents : smear, isolee, collee, tache, etince, petite, noire, croi, ralent, eclair
corpus/ETUDE_NOTES_BRUTES.md §Rewind Clock (9,8 s) (l.245) « Rewind Clock (9,8 s) » -> AUCUNE destination vivante (meilleure : corpus/fiches/AURA_DRAGON.md:1 en-tête 0.205)
      plus proche hors vivant : ../../r6_poing_dragon/scripts/staging.py:94 camera_keys (0.243, production)
      nombres absents des 3 meilleures vivantes : 4.4, 8.6
      termes clés absents : horlog, grosse, crane, isole, anneau, negati, dispar, debri
corpus/ETUDE_NOTES_BRUTES.md §Stagnant Rage (deux variantes : proche 0-4,2 s, … (l.248) « Stagnant Rage (deux variantes : proche 0-4,2 s, lointaine 4, » -> corpus/CARNET.md:260 2.5 (0.412, partielle)
      termes clés absents : explos, lointa, varian, proche, ruee, braise, stagna, minusc, rage, logiqu
corpus/ETUDE_NOTES_BRUTES.md §Black Hole Ability (14 s) -- la ref de notre r6_… (l.251) « Black Hole Ability (14 s) -- la ref de notre r6_black_hole » -> AUCUNE destination vivante (meilleure : corpus/CARNET.md:771 5 0.155)
      plus proche hors vivant : ../../r6_black_hole/scripts/black_hole_track.py:1 module (0.231, production)
      plus proche hors vivant : ../../r6_poing_dragon/scripts/staging.py:94 camera_keys (0.224, production)
      nombres absents des 3 meilleures vivantes : 5.67
      termes clés absents : noir, trou, debri, antici, hole, geste, abilit, minusc, etoile, aspire
corpus/ETUDE_NOTES_BRUTES.md §Fiche « DEMI-DIEU -- S1 POING SCINTILLANT » (ima… (l.255) « Fiche « DEMI-DIEU -- S1 POING SCINTILLANT » (image, guide de » -> outils/planche_ref.py:1 module (0.376, partielle)
      plus proche hors vivant : audit.py:1 module (0.396, en veille)
      plus proche hors vivant : ../../r6_poing_dragon/scripts/croquis_v7.py:1 module (0.378, production)
      termes clés absents : lancem, nature, neutre, vues, action, scinti, prime, guide, exploi, numero
```

## `corpus/ETUDE_TSB.md`

```
corpus/ETUDE_TSB.md §en-tête (l.1) « Étude des animations TSB officielles » -> corpus/CARNET.md:122 1.10 (0.632, complète)
corpus/ETUDE_TSB.md §1 (l.19) « 1. Comment TSB est animé (mesuré) » -> AUCUNE destination vivante (meilleure : corpus/fiches/COUP_CHARGE.md:82 3 0.128)
      nombres absents des 3 meilleures vivantes : 0.43, 12, 18, 29.5, 425, 492
      termes clés absents : cuit, wallco, recoup, superp, animee, densit, mur, confir, transi
corpus/ETUDE_TSB.md §2 (l.32) « 2. La différence qui revient partout : la forme de la frappe » -> perception.py:272 profil_frappe (0.323, partielle)
      nombres absents des 3 meilleures vivantes : 0.51, 0.56, 0.77, 0.92, 15, 20
      termes clés absents : bemol, automa, revien, hypoth
corpus/ETUDE_TSB.md §3 (l.47) « 3. Ce que TSB ne fait PAS : correction d'hier » -> AUCUNE destination vivante (meilleure : perception.py:207 pose_impact 0.123)
      plus proche hors vivant : audit.py:1 module (0.127, en veille)
      plus proche hors vivant : ../../r6_poing_dragon/scripts/croquis_v7.py:1 module (0.125, production)
      nombres absents des 3 meilleures vivantes : 0.26, 0.4, 0.79, 23, 61, 62
      termes clés absents : hier, tiree, inclin, battle, armeme, style, correc
corpus/ETUDE_TSB.md §4 (l.59) « 4. Compétences : le corps bascule fort (mesuré et vu) » -> corpus/fiches/COUP_CHARGE.md:82 3 (0.354, partielle)
      nombres absents des 3 meilleures vivantes : 17, 32, 43.6, 50, 69, 70, 158
      termes clés absents : quarti, fer, sobre, scratc
corpus/ETUDE_TSB.md §4 bis (l.91) « 4 bis. Vu sur les planches (2e passe) : les jambes et la var » -> AUCUNE destination vivante (meilleure : corpus/CARNET.md:122 1.10 0.278)
      nombres absents des 3 meilleures vivantes : 0.45, 12, 18, 21, 27, 58, 62, 81
      termes clés absents : variet, combo, rafale, aerien
corpus/ETUDE_TSB.md §4 ter (l.126) « 4 ter. Nos poses du coup chargé à la même grille (jugement v » -> AUCUNE destination vivante (meilleure : corpus/CARNET.md:122 1.10 0.163)
      termes clés absents : compri, ter, scratc, probab, franc, asymet, rendue, engage
corpus/ETUDE_TSB.md §4 quater (l.145) « 4 quater. Les refs R6 de Milan relues avec cette question » -> AUCUNE destination vivante (meilleure : corpus/CARNET.md:332 2.10 0.133)
      plus proche hors vivant : ../../r6_black_hole/scripts/choreography.py:1 module (0.247, production)
      plus proche hors vivant : ../../r6_poing_dragon/scripts/tutos_vs_tsb.py:1 module (0.138, production)
      termes clés absents : questi, jete, combo, vont, conclu, croqui, double, quater, front, ramene
corpus/ETUDE_TSB.md §5 item 1 (l.159) « 1. Le levier n°1 est notre chaîne d'export, pas nos poses. N » -> corpus/CARNET.md:213 2.1c (0.411, partielle)
      plus proche hors vivant : ../../r6_poing_dragon/scripts/ab_cles_eparses.py:1 module (0.616, production)
      termes clés absents : laisse, bake, chaine, lissee, enviro, compar, courbe
corpus/ETUDE_TSB.md §5 item 2 (l.164) « 2. Sur le coup chargé (compétence), laisser le corps bascule » -> corpus/CARNET.md:402 3.6 (0.412, partielle)
      termes clés absents : bascul, davant, compet, confon, laisse, accrou, rester, droit, plutot
corpus/ETUDE_TSB.md §5 item 3 (l.167) « 3. Garder la règle « M1 sans jambes » pour de futurs M1. Le  » -> outils/moon.py:1 module (0.213, partielle)
      termes clés absents : futur, techni
corpus/ETUDE_TSB.md §6 (l.170) « 6. A/B « clés éparses » sur notre coup chargé : résultat » -> AUCUNE destination vivante (meilleure : corpus/CARNET.md:213 2.1c 0.292)
      nombres absents des 3 meilleures vivantes : 0.113, 0.51, 0.65, 0.79, 43, 109, 146, 148, 150
      termes clés absents : invisi, script, ter, refont, decrit, relie, coute, facon, fidele
```

## `corpus/ETUDE_VISUELLE.md`

```
corpus/ETUDE_VISUELLE.md §en-tête (l.1) « Étude visuelle : ce que font les pros au moment du coup » -> AUCUNE destination vivante (meilleure : corpus/fiches/COUP_CHARGE.md:1 en-tête 0.256)
      termes clés absents : logiqu, theori, jugeme, faite, aller, loin
corpus/ETUDE_VISUELLE.md §Méthode (l.7) « Méthode » -> corpus/fiches/COUP_CHARGE.md:82 3 (0.301, partielle)
      nombres absents des 3 meilleures vivantes : 60
      termes clés absents : clip, statis, fabriq, versio, decomp, parmi, combie, observ, method, pics
corpus/ETUDE_VISUELLE.md §Le constat central (l.32) « Le constat central » -> AUCUNE destination vivante (meilleure : corpus/fiches/VFX.md:17 1 0.25)
      termes clés absents : disent, centra, peine, pros, gramma, cadrag, arcs, silenc, chose, mise
corpus/ETUDE_VISUELLE.md §Les principes (l.46) « Les principes » -> corpus.py:304 strike_mechanics (0.414, partielle)
      plus proche hors vivant : critic.py:1 module (0.431, en veille)
corpus/ETUDE_VISUELLE.md §A (l.51) « A. Cartes d'impact graphiques — environ 24 clips » -> corpus/fiches/COUP_CHARGE.md:82 3 (0.277, partielle)
      termes clés absents : etoile, graphi, voit, black, chapea, haven
corpus/ETUDE_VISUELLE.md §B (l.76) « B. Le silence avant le boum : noir de 2 à 10 f — environ 14  » -> AUCUNE destination vivante (meilleure : corpus/fiches/COUP_CHARGE.md:82 3 0.198)
      nombres absents des 3 meilleures vivantes : 5892
      termes clés absents : ratait, chapea, clip, freina, souven, parce, etoile
corpus/ETUDE_VISUELLE.md §C (l.93) « C. Blanc total de 2 à 15 f — environ 12 clips » -> corpus/fiches/COUP_CHARGE.md:82 3 (0.284, partielle)
      plus proche hors vivant : ../../r6_poing_dragon/scripts/build_cartes.py:1 module (0.294, production)
      termes clés absents : total, altern, aerien, devien, clip
corpus/ETUDE_VISUELLE.md §D (l.102) « D. Le regard avant l'action — environ 10 clips » -> corpus/fiches/COUP_CHARGE.md:82 3 (0.408, partielle)
      nombres absents des 3 meilleures vivantes : 28
      termes clés absents : parte, gemini, intent, voit
corpus/ETUDE_VISUELLE.md §E (l.114) « E. Le poing en très gros plan, souvent vers la caméra — envi » -> corpus/fiches/COUP_CHARGE.md:82 3 (0.33, partielle)
      plus proche hors vivant : ../../r6_un_seul_coup/scripts/staging.py:70 camera_keys (0.352, production)
      plus proche hors vivant : ../../r6_poing_dragon/scripts/scene_v13.py:226 camera (0.347, production)
      termes clés absents : souven, milieu, montra, faite, debri, marche, enviro, princi
corpus/ETUDE_VISUELLE.md §F (l.127) « F. Contraste d'échelle — environ 9 clips » -> corpus/CARNET.md:563 4b.13 (0.375, partielle)
      termes clés absents : lointa, mha, man, opm, ball, voit, enviro
corpus/ETUDE_VISUELLE.md §G (l.139) « G. Décor remplacé à l'impact — environ 6 clips » -> corpus/CARNET.md:538 4b.9 (0.322, partielle)
      plus proche hors vivant : ../../r6_poing_dragon/scripts/staging.py:1 module (0.378, production)
      termes clés absents : mha, flou, rempla, voit, black, flash
corpus/ETUDE_VISUELLE.md §H (l.146) « H. Une caméra qui vit — environ 7 clips » -> corpus/fiches/UN_SEUL_COUP.md:60 3 (0.3, partielle)
      termes clés absents : zoom, vit, eclair, hole, enviro
corpus/ETUDE_VISUELLE.md §I (l.155) « I. Torsion du tronc et poses extrêmes — environ 7 clips » -> corpus/CARNET.md:402 3.6 (0.35, partielle)
      termes clés absents : jjk, ippo, pro, tronc, garde, visait, tordu, reproc, haven, noob
corpus/ETUDE_VISUELLE.md §J (l.169) « J. Lisibilité des silhouettes — tous les bons clips » -> AUCUNE destination vivante (meilleure : corpus/fiches/UN_SEUL_COUP.md:60 3 0.163)
      plus proche hors vivant : ../../r6_black_hole/scripts/black_hole_track.py:1 module (0.179, production)
      termes clés absents : lisibi, encomb, claire, chevau, bons, cache, lisibl
corpus/ETUDE_VISUELLE.md §K (l.179) « K. Smear et trajectoire dessinée — environ 5 clips » -> corpus/fiches/AURA_DRAGON.md:1 en-tête (0.515, partielle)
      termes clés absents : smear, moon, croiss, grand, trajec, enviro, porte
corpus/ETUDE_VISUELLE.md §L (l.185) « L. La victime se déforme — environ 4 clips » -> AUCUNE destination vivante (meilleure : corpus/fiches/UN_SEUL_COUP.md:60 3 0.177)
      plus proche hors vivant : ../../r6_poing_dragon/scripts/render_poses.py:1 module (0.257, production)
      plus proche hors vivant : ../../r6_m1_v222/scripts/render_vfx_preview.py:1 module (0.18, production)
      termes clés absents : bouche, deform, exempl, ball, enviro, blende
corpus/ETUDE_VISUELLE.md §Une nuance importante sur « le coup qui part d'e… (l.190) « Une nuance importante sur « le coup qui part d'en bas » » -> corpus/fiches/COUP_CHARGE.md:82 3 (0.482, partielle)
      termes clés absents : pourta, filme, import
corpus/ETUDE_VISUELLE.md §Ce que ça change pour le cerveau (l.202) « Ce que ça change pour le cerveau » -> corpus/fiches/COUP_CHARGE.md:82 3 (0.251, partielle)
      plus proche hors vivant : etats.py:1 module (0.383, en veille)
      plus proche hors vivant : critic.py:43 load (0.358, en veille)
      termes clés absents : hypoth, partie, mesura, nouvel, existe, etat
corpus/ETUDE_VISUELLE.md §Ce que ça change pour la prochaine version item 1 (l.214) « 1. très gros plan sur les yeux ou le visage, tenu 20 f ; » -> (moins de 60 caractères, non cherché)
corpus/ETUDE_VISUELLE.md §Ce que ça change pour la prochaine version item 2 (l.215) « 2. très gros plan sur le poing qui se serre ou s'arme, camér » -> corpus/CARNET.md:321 2.9 (0.354, partielle)
corpus/ETUDE_VISUELLE.md §Ce que ça change pour la prochaine version item 3 (l.216) « 3. départ en 2-4 f ; » -> (moins de 60 caractères, non cherché)
corpus/ETUDE_VISUELLE.md §Ce que ça change pour la prochaine version item 4 (l.217) « 4. noir de 6 f avec une petite étoile ; » -> (moins de 60 caractères, non cherché)
corpus/ETUDE_VISUELLE.md §Ce que ça change pour la prochaine version item 5 (l.218) « 5. 3 cartes de 4 f : silhouette inversée, encre hachurée, gr » -> corpus/fiches/UN_SEUL_COUP.md:21 1 (0.492, partielle)
      plus proche hors vivant : ../../r6_poing_dragon/scripts/build_cartes.py:1 module (0.594, production)
corpus/ETUDE_VISUELLE.md §Ce que ça change pour la prochaine version item 6 (l.219) « 6. blanc total qui se dissout ; » -> (moins de 60 caractères, non cherché)
corpus/ETUDE_VISUELLE.md §Ce que ça change pour la prochaine version item 7 (l.220) « 7. plan très large sur la conséquence. » -> corpus/CARNET.md:196 2.1b (0.354, partielle)
      termes clés absents : rempla, separe, fort
corpus/ETUDE_VISUELLE.md §Lot 2 (Milan, 5 vidéos Roblox et animation) : ce… item 1 (l.230) « 1. L'ellipse (« First time fighting a dummy »). On ne voit j » -> corpus/fiches/COUP_CHARGE.md:46 2 (0.412, partielle)
      termes clés absents : serieu, vienne, fighti, assomb, racont, first, ellips, eclair, dummy
corpus/ETUDE_VISUELLE.md §Lot 2 (Milan, 5 vidéos Roblox et animation) : ce… item 2 (l.237) « 2. La hiérarchie des effets (« punch practice », « cross pun » -> outils/rappel.py:1 module (0.418, partielle)
      termes clés absents : petite, suiven, princi, long
corpus/ETUDE_VISUELLE.md §Lot 2 (Milan, 5 vidéos Roblox et animation) : ce… item 3 (l.244) « 3. Le métier du coup (tuto firytwig) : armement, frappe, ret » -> AUCUNE destination vivante (meilleure : corpus/CARNET.md:158 2.1 0.235)
      plus proche hors vivant : ../../r6_poing_dragon/scripts/dragon_clip.py:1 module (0.43, production)
      termes clés absents : metier, surtou, rythme, interv, suivan, amorti, oversh, niveau, pres
corpus/ETUDE_VISUELLE.md §Lot 2 (Milan, 5 vidéos Roblox et animation) : ce… item 4 (l.254) « 4. La rotation du corps et la caméra (« pro vs noob » dans B » -> corpus/CARNET.md:196 2.1b (0.409, partielle)
      plus proche hors vivant : ../../r6_battle_throne/scripts/props.py:184 crown_points (0.416, production)
      plus proche hors vivant : ../../r6_throne_crown/scripts/props.py:184 crown_points (0.416, production)
      termes clés absents : practi, lisibi, noob, pros, cercle, puissa, existe, ecrase, enviro, proble
corpus/ETUDE_VISUELLE.md §Lot 2 (Milan, 5 vidéos Roblox et animation) : ce… item 5 (l.264) « 5. Le mouvement secondaire (« cross punch ») : la queue et l » -> outils/rappel.py:1 module (0.34, partielle)
      termes clés absents : retard, perfec, animen, access, lisibi, ellips, pros, method
corpus/ETUDE_VISUELLE.md §Lot 3 (Milan, 5 GIF de jeux battlegrounds, camér… item 1 (l.281) « 1. Caméra de jeu contre cinématique : le point qui manquait. » -> outils/juge.py:1 module (0.481, partielle)
      termes clés absents : joueur, cinema, jouent, boxeur, quatre, lointa, souven, jeux, compet, manqua
corpus/ETUDE_VISUELLE.md §Lot 3 (Milan, 5 GIF de jeux battlegrounds, camér… item 2 (l.292) « 2. La hiérarchie des effets, confirmée en jeu. » -> corpus/CARNET.md:496 4b.1 (0.263, partielle)
      termes clés absents : peine, hierar
corpus/ETUDE_VISUELLE.md §Lot 3 (Milan, 5 GIF de jeux battlegrounds, camér… item 3 (l.296) « 3. La rafale en masse (« gatling »). Une rafale ultime très  » -> outils/rappel.py:1 module (0.276, partielle)
      termes clés absents : masse, courte, anneau, choisi
corpus/ETUDE_VISUELLE.md §Lot 3 (Milan, 5 GIF de jeux battlegrounds, camér… item 4 (l.301) « 4. La trace qui reste et la tenue sur la conséquence. » -> corpus/fiches/UN_SEUL_COUP.md:21 1 (0.458, partielle)
      termes clés absents : lointa, tache, envoye, crater, trace, aerien, partie, visibl, attaqu
corpus/ETUDE_VISUELLE.md §Lot 3 (Milan, 5 GIF de jeux battlegrounds, camér… item 5 (l.306) « 5. Le contact prolongé (Mythra) : saisie, soulèvement, proje » -> AUCUNE destination vivante (meilleure : outils/moisson_milan.py:1 module 0.234)
      termes clés absents : joueur, juger, soulev, vue, touche
corpus/ETUDE_VISUELLE.md §Lot 4 : 4 refs revues en entier et la fiche « DE… (l.313) « Lot 4 : 4 refs revues en entier et la fiche « DEMI-DIEU » » -> corpus/CARNET.md:563 4b.13 (0.255, partielle)
      termes clés absents : revue, moment, dieu, isole, etude, demi
corpus/ETUDE_VISUELLE.md §Lot 4 : 4 refs revues en entier et la fiche « DE… item 1 (l.320) « 1. Un ultime se construit en actes. » -> AUCUNE destination vivante (meilleure : corpus/fiches/POING_DU_DRAGON_V13.md:57 3 0.226)
      plus proche hors vivant : ../../r6_poing_dragon/scripts/scene_v13.py:226 camera (0.33, production)
      plus proche hors vivant : ../../r6_poing_dragon/scripts/staging.py:94 camera_keys (0.319, production)
      nombres absents des 3 meilleures vivantes : 2.6
      termes clés absents : black, horlog, envol, trou, colle, ultime, ralent
corpus/ETUDE_VISUELLE.md §Lot 4 : 4 refs revues en entier et la fiche « DE… item 2 (l.329) « 2. La signature visuelle. Chaque technique a son motif, qu'o » -> corpus/CARNET.md:140 1.11 (0.373, partielle)
      termes clés absents : vient
corpus/ETUDE_VISUELLE.md §Lot 4 : 4 refs revues en entier et la fiche « DE… item 3 (l.331) « 3. Les variantes de jeu. Stagnant Rage existe en version pro » -> corpus/fiches/POING_DU_DRAGON_V13.md:57 3 (0.384, partielle)
      plus proche hors vivant : etats.py:101 etalons (0.391, en veille)
      termes clés absents : modele, prevoi, adopte, dieu, stagna, lointa, semble, joueur, compet, lancem
```

## `corpus/TUTOS_ANIMATION.md`

```
corpus/TUTOS_ANIMATION.md §en-tête (l.1) « Tutos et explications d'animation : ce qu'on en tire » -> AUCUNE destination vivante (meilleure : corpus/fiches/VFX.md:109 4 0.112)
      nombres absents des 3 meilleures vivantes : 16072313171
      termes clés absents : devfor, rappor, simple, motive, gdc, gamer, work, robot
corpus/TUTOS_ANIMATION.md §1 (l.28) « 1. Ce que la recherche a corrigé tout de suite » -> perception.py:272 profil_frappe (0.253, partielle)
      plus proche hors vivant : ../../r6_poing_dragon/scripts/ab_cles_eparses.py:1 module (0.298, production)
      termes clés absents : pack, ecriva, sautai, vienne, tablea, compet
corpus/TUTOS_ANIMATION.md §2 (l.43) « 2. « L'autre anatomie » : trois critères mesurés sur les cou » -> perception.py:207 pose_impact (0.292, partielle)
      nombres absents des 3 meilleures vivantes : 0.89
      termes clés absents : etalon, criter, etat, simple, arrier, pese
corpus/TUTOS_ANIMATION.md §3 (l.75) « 3. Règles spécifiques R6 / Roblox (DevForum, doc officielle) » -> AUCUNE destination vivante (meilleure : outils/lint_cerveau.py:268 meilleure_approche 0.26)
      plus proche hors vivant : ../../r6_poing_dragon/scripts/dragon_clip.py:49 _rafale_cfg (0.412, production)
      plus proche hors vivant : ../../r6_poing_dragon/scripts/dragon_clip.py:1021 aerien_v8 (0.412, production)
      termes clés absents : skill, selon, membre, specif, parais, arbitr, animen, roboti, effort
corpus/TUTOS_ANIMATION.md §4 (l.109) « 4. Règles de l'anime (ArcSys, Cartwright, Mattesi, extraits  » -> AUCUNE destination vivante (meilleure : corpus/fiches/UN_SEUL_COUP.md:200 9 0.151)
      plus proche hors vivant : ../../r6_poing_dragon/scripts/dragon_clip.py:1228 aerien_v13 (0.264, production)
      plus proche hors vivant : ../../r6_un_seul_coup/scripts/coup_clip.py:113 attacker_keys (0.248, production)
      nombres absents des 3 meilleures vivantes : 0.03, 0.08
      termes clés absents : cartwr, ggxrd, jjk, anatom, possib, scale, transl, mha, gdc, amene
corpus/TUTOS_ANIMATION.md §5 (l.121) « 5. Ce qui entre dans le cerveau » -> AUCUNE destination vivante (meilleure : corpus/CARNET.md:1 en-tête 0.207)
      termes clés absents : faux, effort, indica, nouvel, etape, recupe, ramene
corpus/TUTOS_ANIMATION.md §6 (l.135) « 6. Pistes ouvertes » -> AUCUNE destination vivante (meilleure : corpus/CARNET.md:96 1.8 0.072)
      nombres absents des 3 meilleures vivantes : 16072313171
      termes clés absents : densit, meille, asset, possib, offici, vraie, faut, easing, save
corpus/TUTOS_ANIMATION.md §7 (l.145) « 7. Vidéos envoyées par Milan (zips du 2026-09-24) : étude vi » -> AUCUNE destination vivante (meilleure : corpus/fiches/POING_DU_DRAGON_V13.md:1 en-tête 0.206)
      termes clés absents : zips, six, scratc, quatre, etudie, decrit, rejoin, decoup, commit, court
corpus/TUTOS_ANIMATION.md §7.1 Nakamura, « Speed/Scale Contrast » (sakuga, … (l.153) « 7.1 Nakamura, « Speed/Scale Contrast » (sakuga, 23 s) [VU] » -> corpus/fiches/COUP_CHARGE.md:82 3 (0.218, partielle)
      termes clés absents : confir, grossi, sec, amene, course, dome
corpus/TUTOS_ANIMATION.md §7.2 « Advanced Movement System » (vitrine Roblox… (l.169) « 7.2 « Advanced Movement System » (vitrine Roblox R6, 27 s) [ » -> AUCUNE destination vivante (meilleure : corpus/fiches/COUP_CHARGE.md:82 3 0.263)
      termes clés absents : dash, penche, neutre, system, squash, foulee, mouvem, roboti, ouvren, recopi
corpus/TUTOS_ANIMATION.md §8 (l.194) « 8. Les quatre tutos longs : ce qu'ils disent vraiment » -> AUCUNE destination vivante (meilleure : corpus/fiches/VFX.md:130 5 0.156)
      plus proche hors vivant : ../../r6_un_seul_coup/scripts/coup_clip.py:113 attacker_keys (0.338, production)
      plus proche hors vivant : ../../r6_poing_dragon/scripts/dragon_clip.py:580 attacker_keys (0.272, production)
      nombres absents des 3 meilleures vivantes : 0.4, 0.7, 13, 30, 45, 60
      termes clés absents : video, accrou, cles, hypoth, xoater, arrier, nouvel, equili
```

## `corpus/REFERENCES_VIDEO.md`

```
corpus/REFERENCES_VIDEO.md §en-tête (l.1) « Références vidéo de Milan : timing mesuré image par image (2 » -> outils/planche_ref.py:1 module (0.566, complète)
corpus/REFERENCES_VIDEO.md §Fiches (l.11) « Fiches » -> AUCUNE destination vivante (meilleure : corpus/fiches/AURA_DRAGON.md:1 en-tête 0.229)
      nombres absents des 3 meilleures vivantes : 2.9, 6.3, 8.2, 9.8, 9.9, 14, 15, 16, 22, 24, 28, 32
      termes clés absents : sept, etoile, noob, pro, hold, soleil
corpus/REFERENCES_VIDEO.md §Ce qui revient partout (principes, pas des chiff… item 1 (l.27) « 1. Contraste de temps. Tenue longue, puis action en 2-3 f, p » -> corpus/CARNET.md:287 2.6b (0.366, partielle)
      termes clés absents : noob, precis
corpus/REFERENCES_VIDEO.md §Ce qui revient partout (principes, pas des chiff… item 2 (l.29) « 2. Le rythme d'une rafale n'est pas régulier. Il accélère, p » -> organic.py:1 module (0.335, partielle)
      termes clés absents : finish
corpus/REFERENCES_VIDEO.md §Ce qui revient partout (principes, pas des chiff… item 3 (l.31) « 3. Graphisme d'1 frame. Teinte plate du corps, écran blanc,  » -> corpus/CARNET.md:629 4b.20 (0.317, partielle)
      termes clés absents : graphi, invers
corpus/REFERENCES_VIDEO.md §Ce qui revient partout (principes, pas des chiff… item 4 (l.34) « 4. La caméra est une piste animée, synchronisée aux coups :  » -> AUCUNE destination vivante (meilleure : corpus/fiches/AURA_DRAGON.md:126 3 0.253)
      plus proche hors vivant : ../../r6_poing_dragon/scripts/staging.py:1 module (0.457, production)
      termes clés absents : dolly, push, synchr
corpus/REFERENCES_VIDEO.md §Ce qui revient partout (principes, pas des chiff… item 5 (l.36) « 5. Le décor encaisse : dalles basculées, pics, cratère. Une  » -> corpus/CARNET.md:272 2.5b (0.237, partielle)
      termes clés absents : encais, crater, bascul
corpus/REFERENCES_VIDEO.md §Ce qui revient partout (principes, pas des chiff… item 6 (l.38) « 6. Une palette par technique : rouge/noir/blanc, or/blanc, f » -> corpus/CARNET.md:505 4b.2 (0.532, partielle)
      termes clés absents : combo
corpus/REFERENCES_VIDEO.md §Coups de poing : 5 exemples de Milan (24 sept.),… (l.41) « Coups de poing : 5 exemples de Milan (24 sept.), après la v3 » -> AUCUNE destination vivante (meilleure : corpus/fiches/UN_SEUL_COUP.md:117 6 0.251)
      plus proche hors vivant : ../../r6_poing_dragon/scripts/staging.py:94 camera_keys (0.418, production)
      plus proche hors vivant : ../../r6_m1_v222/scripts/m1_clip.py:51 attacker_keys (0.33, production)
      nombres absents des 3 meilleures vivantes : 1.6, 8.7
      termes clés absents : tire, visage, tendu, armeme, extens, sept, copier
corpus/REFERENCES_VIDEO.md §Coups de poing : 5 exemples de Milan (24 sept.),… item 1 (l.56) « 1. Le poing arme à hauteur d'épaule ou de tête, jamais à la  » -> corpus/fiches/UN_SEUL_COUP.md:117 6 (0.302, partielle)
      plus proche hors vivant : rules.py:192 check_trajectoire_poing (0.395, en veille)
      plus proche hors vivant : ../../r6_poing_dragon/scripts/dragon_clip.py:580 attacker_keys (0.338, production)
      termes clés absents : voyage, finit, arc, descen
corpus/REFERENCES_VIDEO.md §Coups de poing : 5 exemples de Milan (24 sept.),… item 2 (l.59) « 2. Le torse fait le travail, en exagéré : torsion jusqu'à mo » -> outils/rappel.py:1 module (0.302, partielle)
      plus proche hors vivant : ../../r6_poing_dragon/scripts/dragon_clip.py:1 module (0.323, production)
      plus proche hors vivant : ../../r6_black_hole/scripts/choreography.py:79 _fr (0.303, production)
      termes clés absents : comple
corpus/REFERENCES_VIDEO.md §Coups de poing : 5 exemples de Milan (24 sept.),… item 3 (l.61) « 3. L'autre bras a un rôle : il reste en garde au visage (cou » -> corpus/CARNET.md:420 3.8 (0.35, partielle)
      plus proche hors vivant : ../../r6_poing_dragon/scripts/render_poses.py:1 module (0.598, production)
      plus proche hors vivant : ../../r6_m1_v222/scripts/m1_clip.py:51 attacker_keys (0.379, production)
      termes clés absents : role, armeme, jab
corpus/REFERENCES_VIDEO.md §Coups de poing : 5 exemples de Milan (24 sept.),… item 4 (l.63) « 4. Le coup part vite (2-3 f), l'extension est tenue plus lon » -> corpus/fiches/COUP_CHARGE.md:82 3 (0.37, partielle)
      plus proche hors vivant : ../../r6_aerial_kick_combo/scripts/choreography.py:714 cycle_9 (0.388, production)
corpus/REFERENCES_VIDEO.md §Coups de poing : 5 exemples de Milan (24 sept.),… item 5 (l.65) « 5. Variété : jab, direct, crochet horizontal, coup de martea » -> AUCUNE destination vivante (meilleure : perception.py:192 variete 0.246)
      plus proche hors vivant : rules.py:192 check_trajectoire_poing (0.336, en veille)
      plus proche hors vivant : ../../r6_poing_dragon/scripts/dragon_clip.py:49 _rafale_cfg (0.283, production)
      termes clés absents : martea, toupie, mecani, identi
corpus/REFERENCES_VIDEO.md §IMPACT HAVEN : mesures (24 sept.) (l.68) « IMPACT HAVEN : mesures (24 sept.) » -> AUCUNE destination vivante (meilleure : perception.py:1 module 0.296)
      nombres absents des 3 meilleures vivantes : 1.7, 3.15, 3.3, 5.4, 5.5, 8.2, 10, 10.2, 11.6, 30
      termes clés absents : boxe, etince, onde, hitsto
```
