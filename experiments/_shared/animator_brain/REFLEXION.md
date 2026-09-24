# Reflexion du critique

## Predictions contre notes de Milan (poids avant apprentissage)
- v1 : predit 6.1, Milan 6.0 (ecart +0.1)
- v2 : predit 6.5, Milan 6.7 (ecart -0.2)
- v4 : predit 6.8, Milan 6.7 (ecart +0.1)

## Ce qui a change entre deux versions notees
- v1 -> v2 : note 6.0 -> 6.7 (+0.7) ; corrigees : posture_droite, escalade, impact_visible, variete_coups ; perdues : aucune
- v2 -> v4 : note 6.7 -> 6.7 (+0.0) ; corrigees : epaules_basses, bras_horizontal, transfert_poids ; perdues : aucune

## Suspects (toujours faux sur toutes les versions notees, note bloquee)
- **tenue_avant_choc** : Le mouvement freine juste AVANT le choc, puis explose juste apres (le flash cache le saut de pose). C'est l'inverse d'un hitstop qui gele apres. (sources : IMPACT HAVEN (mesure); coup chapeau LeftRight2601 (mesure); Milan v1 : manque de puissance (piste))
- **coup_charge** : Un coup final se CHARGE : buste enroule, corps ramasse, tenue immobile sous tension, puis depart en 2-3 f et extension tenue. (sources : Milan v4 : je verrais plus le coup de Saitama (piste); Serious Punch : garde tenue 32 f; Mii smash : extension tenue)
- **arcs** : Les membres voyagent en arcs (rotation autour des articulations), jamais en ligne droite mecanique. (sources : 12 principes de l'animation (arcs); auto-critique v4 : controle IK interpole en ligne droite)

## Jamais mesurees (angle mort du cerveau)
- contraste_de_temps : Tenue longue, action en 2-3 f, tenue longue sur le resultat.
- silhouette_lisible : Chaque pose cle se lit en silhouette (ligne d'action claire, membres detaches du corps).

## Echelle calibree sur 3 notes : note = 6.63 + 0.58 x score

## Poids appris (ce qui fait bouger la note de Milan)
- tenue_avant_choc     poids_note 0.73 (confiance principe 0.50)
- coup_charge          poids_note 0.73 (confiance principe 0.60)
- arcs                 poids_note 0.73 (confiance principe 0.80)
- posture_droite       poids_note 0.60 (confiance principe 0.70)
- escalade             poids_note 0.60 (confiance principe 0.60)
- impact_visible       poids_note 0.60 (confiance principe 0.70)
- variete_coups        poids_note 0.60 (confiance principe 0.60)
- poing_a_plat         poids_note 0.50 (confiance principe 0.80)
- contraste_de_temps   poids_note 0.50 (confiance principe 0.70)
- silhouette_lisible   poids_note 0.50 (confiance principe 0.80)
- epaules_basses       poids_note 0.33 (confiance principe 0.50)
- bras_horizontal      poids_note 0.33 (confiance principe 0.80)
- transfert_poids      poids_note 0.33 (confiance principe 0.60)

## Predictions apres apprentissage
- v1 : predit 6.0, Milan 6.0
- v2 : predit 6.6, Milan 6.7
- v4 : predit 6.8, Milan 6.7
