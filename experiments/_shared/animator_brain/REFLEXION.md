# Reflexion du critique

## Predictions contre notes de Milan (poids avant apprentissage)
- v1 : predit 6.2, Milan 6.0 (ecart +0.2)
- v2 : predit 6.5, Milan 6.7 (ecart -0.2)
- v4 : predit 6.9, Milan 6.7 (ecart +0.2)

## Ce qui a change entre deux versions notees
- v1 -> v2 : note 6.0 -> 6.7 (+0.7) ; corrigees : posture_droite, escalade, impact_visible ; perdues : aucune
- v2 -> v4 : note 6.7 -> 6.7 (+0.0) ; corrigees : epaules_basses, bras_horizontal, transfert_poids ; perdues : aucune

## Suspects (toujours faux sur toutes les versions notees, note bloquee)
- **variete_coups** : Une rafale varie les formes de coups (jab, direct, crochet, marteau, toupie). (sources : 5 exemples de Milan (combo R6); IMPACT HAVEN)
- **tenue_avant_choc** : Le mouvement freine juste AVANT le choc, puis explose juste apres (le flash cache le saut de pose). C'est l'inverse d'un hitstop qui gele apres. (sources : IMPACT HAVEN (mesure); coup chapeau LeftRight2601 (mesure); Milan v1 : manque de puissance (piste); fiches des refs (2026-09-24) : 3 refs sur 9 avec cartes d'impact le montrent (coup chapeau, serious punch 2, IMPACT HAVEN) ; Black Flash, Rewind Clock, Serious Punch TSB non -> depend du style, pas universel; sakugabooru (2026-09-24, fighting impact_frames, 1ers clips) : 0 sur 4 clips avec impacts (Nakamura, OPM, MHA, One Piece) -> 3 refs sur 13 au total : effet de style, pas principe; synthese 2026-09-24 (21 clips sakuga) : 1/19 clips avec impacts ; l'inverse domine : explosion apres le choc 8/19 (nous 0/4); synthese finale 2026-09-24 : sakuga 2/32, danbooru 2/10, refs de Milan 3/9)
- **coup_charge** : Un coup final se CHARGE : buste enroule, corps ramasse, tenue immobile sous tension, puis depart en 2-3 f et extension tenue. (sources : Milan v4 : je verrais plus le coup de Saitama (piste); Serious Punch : garde tenue 32 f; Mii smash : extension tenue)
- **arcs** : Les membres voyagent en arcs (rotation autour des articulations), jamais en ligne droite mecanique. (sources : 12 principes de l'animation (arcs); auto-critique v4 : controle IK interpole en ligne droite)
- **explosion_apres** : Juste apres le choc, l'image explose (debris, onde, recul violent) au lieu de geler. (sources : synthese 2026-09-24 : 8/19 clips sakuga avec impacts, refs de Milan 2/9, nous 0/4 (notre hitstop gele apres); synthese finale 2026-09-24 : sakuga 12/32, danbooru 4/10, refs de Milan 2/9, nous 0/4)

## Ou la mesure contredit le jugement manuel (etats.py)
- v2 variete_coups : jugement True -> mesure False
- v4 variete_coups : jugement True -> mesure False

## Parties aimees contre parties rejetees
- arcs : vraie dans 0% des parties aimees, 43% des rejetees : signal faible

## Jamais mesurees (angle mort du cerveau)
- silhouette_lisible : Chaque pose cle se lit en silhouette (ligne d'action claire, membres detaches du corps).
- fluidite : Le mouvement enchaine : un membre ne s'arrete pas a chaque pose cle (chevauchement, suivi), il repart avant d'etre a l'arret.

## Echelle calibree sur 3 notes : note = 6.67 + 0.72 x score

## Poids appris (ce qui fait bouger la note de Milan)
- variete_coups        poids_note 0.64 (confiance principe 0.60)
- tenue_avant_choc     poids_note 0.64 (confiance principe 0.25)
- coup_charge          poids_note 0.64 (confiance principe 0.60)
- arcs                 poids_note 0.64 (confiance principe 0.80)
- explosion_apres      poids_note 0.64 (confiance principe 0.50)
- posture_droite       poids_note 0.58 (confiance principe 0.70)
- escalade             poids_note 0.58 (confiance principe 0.60)
- impact_visible       poids_note 0.58 (confiance principe 0.70)
- poing_a_plat         poids_note 0.50 (confiance principe 0.80)
- contraste_de_temps   poids_note 0.50 (confiance principe 0.70)
- silhouette_lisible   poids_note 0.50 (confiance principe 0.80)
- fluidite             poids_note 0.50 (confiance principe 0.60)
- epaules_basses       poids_note 0.40 (confiance principe 0.50)
- bras_horizontal      poids_note 0.40 (confiance principe 0.80)
- transfert_poids      poids_note 0.40 (confiance principe 0.60)

## Predictions apres apprentissage
- v1 : predit 6.1, Milan 6.0
- v2 : predit 6.5, Milan 6.7
- v4 : predit 6.8, Milan 6.7
