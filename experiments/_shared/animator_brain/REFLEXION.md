# Reflexion du critique

## Predictions contre notes de Milan (poids avant apprentissage)
- v1 : predit 6.1, Milan 6.0 (ecart +0.1)
- v2 : predit 6.5, Milan 6.7 (ecart -0.2)
- v4 : predit 6.9, Milan 6.7 (ecart +0.2)
- v5 : predit 7.3, Milan 6.8 (ecart +0.5)

## Ce qui a change entre deux versions notees
- v1 -> v2 : note 6.0 -> 6.7 (+0.7) ; corrigees : posture_droite, escalade, impact_visible ; perdues : aucune
- v2 -> v4 : note 6.7 -> 6.7 (+0.0) ; corrigees : epaules_basses, bras_horizontal, transfert_poids ; perdues : aucune
- v4 -> v5 : note 6.7 -> 6.8 (+0.1) ; corrigees : coup_charge, arcs ; perdues : aucune

## Suspects (toujours faux sur toutes les versions notees, note bloquee)
- **variete_coups** : Une rafale varie les formes de coups (jab, direct, crochet, marteau, toupie). (sources : 5 exemples de Milan (combo R6); IMPACT HAVEN)

## Ou la mesure contredit le jugement manuel (etats.py)
- v2 variete_coups : jugement True -> mesure False
- v4 variete_coups : jugement True -> mesure False

## Parties aimees contre parties rejetees
- arcs : vraie dans 0% des parties aimees, 43% des rejetees : signal faible

## Jamais mesurees (angle mort du cerveau)
- silhouette_lisible : Chaque pose cle se lit en silhouette (ligne d'action claire, membres detaches du corps).
- fluidite : Le mouvement enchaine : un membre ne s'arrete pas a chaque pose cle (chevauchement, suivi), il repart avant d'etre a l'arret.

## Echelle calibree sur 4 notes : note = 6.53 + 0.49 x score

## Poids appris (ce qui fait bouger la note de Milan)
- variete_coups        poids_note 0.64 (confiance principe 0.60)
- posture_droite       poids_note 0.58 (confiance principe 0.70)
- escalade             poids_note 0.58 (confiance principe 0.60)
- impact_visible       poids_note 0.58 (confiance principe 0.70)
- poing_a_plat         poids_note 0.50 (confiance principe 0.80)
- tenue_avant_choc     poids_note 0.50 (confiance principe 0.25)
- contraste_de_temps   poids_note 0.50 (confiance principe 0.70)
- silhouette_lisible   poids_note 0.50 (confiance principe 0.80)
- fluidite             poids_note 0.50 (confiance principe 0.60)
- explosion_apres      poids_note 0.50 (confiance principe 0.50)
- epaules_basses       poids_note 0.40 (confiance principe 0.50)
- bras_horizontal      poids_note 0.40 (confiance principe 0.80)
- transfert_poids      poids_note 0.40 (confiance principe 0.60)
- coup_charge          poids_note 0.40 (confiance principe 0.60)
- arcs                 poids_note 0.40 (confiance principe 0.80)

## Predictions apres apprentissage
- v1 : predit 6.1, Milan 6.0
- v2 : predit 6.5, Milan 6.7
- v4 : predit 6.7, Milan 6.7
- v5 : predit 6.9, Milan 6.8
