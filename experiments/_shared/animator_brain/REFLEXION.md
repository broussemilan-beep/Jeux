# Reflexion du critique

## Predictions contre notes de Milan (poids avant apprentissage)
- v1 : predit 6.1, Milan 6.0 (ecart +0.1)
- v2 : predit 6.5, Milan 6.7 (ecart -0.2)
- v4 : predit 6.9, Milan 6.7 (ecart +0.2)
- v5 : predit 7.1, Milan 6.8 (ecart +0.3)

## Ce qui a change entre deux versions notees
- v1 -> v2 : note 6.0 -> 6.7 (+0.7) ; corrigees : posture_droite, escalade, impact_visible ; perdues : aucune
- v2 -> v4 : note 6.7 -> 6.7 (+0.0) ; corrigees : epaules_basses, bras_horizontal, transfert_poids ; perdues : aucune
- v4 -> v5 : note 6.7 -> 6.8 (+0.1) ; corrigees : coup_charge, arcs ; perdues : aucune

## Suspects (toujours faux sur toutes les versions notees, note bloquee)
- **variete_coups** : Une rafale varie les formes de coups (jab, direct, crochet, marteau, toupie). (sources : 5 exemples de Milan (combo R6); IMPACT HAVEN)
- **cartes_impact** : Au choc, l'image 3D est remplacee par 2-8 cartes graphiques de 2-4 f (silhouette inversee, encre hachuree, negatif, posterise, couleur plate, cible/croix). (sources : corpus/ETUDE_VISUELLE.md (68 planches regardees image par image, 2026-09-24) : ~22 clips; refs Roblox de Milan (TSB, Black Flash, IMPACT HAVEN...))
- **silence_noir** : Juste avant/apres l'explosion : ecran NOIR 2-10 f (souvent une petite etoile) -- le silence avant le boum. (sources : corpus/ETUDE_VISUELLE.md (68 planches regardees image par image, 2026-09-24) : ~14 clips; refs Roblox de Milan (TSB, Black Flash, IMPACT HAVEN...))
- **blanc_total** : Blanc total 2-15 f au pic (souvent en alternance blanc/noir de 4 f, ou blanc qui se dissout en fumee). (sources : corpus/ETUDE_VISUELLE.md (68 planches regardees image par image, 2026-09-24) : ~12 clips; refs Roblox de Milan (TSB, Black Flash, IMPACT HAVEN...))
- **regard_intention** : Avant que le coup parte : tres gros plan visage/yeux tenu 16-30 f (l'intention ; la charge se lit dans le regard). (sources : corpus/ETUDE_VISUELLE.md (68 planches regardees image par image, 2026-09-24) : ~10 clips; refs Roblox de Milan (TSB, Black Flash, IMPACT HAVEN...))
- **poing_gros_plan** : Le poing/bras remplit l'ecran (raccourci, souvent vers la camera) 12-16 f ; pendant la charge, camera collee au bras. (sources : corpus/ETUDE_VISUELLE.md (68 planches regardees image par image, 2026-09-24) : ~9 clips; refs Roblox de Milan (TSB, Black Flash, IMPACT HAVEN...); image de Milan 8965d689 (planche OPM) : LE coup de Saitama = poing vers le lecteur, plus gros que la tete ; Umamusume 3D : meme principe en temps reel)
- **contraste_echelle** : Coupes entre perso minuscule (plan tres large) et tres gros plan ; contact en gros plan puis consequence en plan tres lointain. (sources : corpus/ETUDE_VISUELLE.md (68 planches regardees image par image, 2026-09-24) : ~9 clips; refs Roblox de Milan (TSB, Black Flash, IMPACT HAVEN...))
- **fond_remplace** : A l'impact, le decor est remplace par des lignes de vitesse, une couleur plate ou un fond flou. (sources : corpus/ETUDE_VISUELLE.md (68 planches regardees image par image, 2026-09-24) : ~6 clips; refs Roblox de Milan (TSB, Black Flash, IMPACT HAVEN...))
- **camera_vivante** : La camera participe : fouet vers le ciel, rotation/cadre penche, zoom eclair, poussee jusque dans le corps. (sources : corpus/ETUDE_VISUELLE.md (68 planches regardees image par image, 2026-09-24) : ~7 clips; refs Roblox de Milan (TSB, Black Flash, IMPACT HAVEN...))
- **torsion_tronc** : La puissance vient du TRONC qui s'enroule puis se deroule (vu de dos/trois-quarts, 120-150 deg), poses extremes ; garde basse et large normale. (sources : corpus/ETUDE_VISUELLE.md (68 planches regardees image par image, 2026-09-24) : ~7 clips; refs Roblox de Milan (TSB, Black Flash, IMPACT HAVEN...))
- **smear_graphique** : Une trainee/smear porte la vitesse ; la trajectoire du coup reste dessinee a l'ecran quelques frames. (sources : corpus/ETUDE_VISUELLE.md (68 planches regardees image par image, 2026-09-24) : ~5 clips; refs Roblox de Milan (TSB, Black Flash, IMPACT HAVEN...))
- **victime_deformee** : La victime reagit fort : se plie autour du poing, joue ecrasee, tete qui part. (sources : corpus/ETUDE_VISUELLE.md (68 planches regardees image par image, 2026-09-24) : ~4 clips; refs Roblox de Milan (TSB, Black Flash, IMPACT HAVEN...))

## Ou la mesure contredit le jugement manuel (etats.py)
- v2 variete_coups : jugement True -> mesure False
- v4 variete_coups : jugement True -> mesure False

## Parties aimees contre parties rejetees
- arcs : vraie dans 0% des parties aimees, 43% des rejetees : signal faible
- cartes_impact : vraie dans 100% des parties aimees, 0% des rejetees : DISCRIMINE (vraie ou Milan aime, fausse ou il rejette) -> poids en hausse
- silence_noir : vraie dans 0% des parties aimees, 0% des rejetees : jamais essaye chez nous : pas de preuve, poids inchange (a tester)
- blanc_total : vraie dans 100% des parties aimees, 0% des rejetees : DISCRIMINE (vraie ou Milan aime, fausse ou il rejette) -> poids en hausse
- regard_intention : vraie dans 0% des parties aimees, 0% des rejetees : jamais essaye chez nous : pas de preuve, poids inchange (a tester)
- poing_gros_plan : vraie dans 0% des parties aimees, 0% des rejetees : jamais essaye chez nous : pas de preuve, poids inchange (a tester)
- contraste_echelle : vraie dans 100% des parties aimees, 0% des rejetees : DISCRIMINE (vraie ou Milan aime, fausse ou il rejette) -> poids en hausse
- fond_remplace : vraie dans 0% des parties aimees, 0% des rejetees : jamais essaye chez nous : pas de preuve, poids inchange (a tester)
- camera_vivante : vraie dans 100% des parties aimees, 0% des rejetees : DISCRIMINE (vraie ou Milan aime, fausse ou il rejette) -> poids en hausse
- torsion_tronc : vraie dans 0% des parties aimees, 0% des rejetees : jamais essaye chez nous : pas de preuve, poids inchange (a tester)
- smear_graphique : vraie dans 100% des parties aimees, 0% des rejetees : DISCRIMINE (vraie ou Milan aime, fausse ou il rejette) -> poids en hausse
- victime_deformee : vraie dans 100% des parties aimees, 0% des rejetees : DISCRIMINE (vraie ou Milan aime, fausse ou il rejette) -> poids en hausse
- silhouette_lisible : vraie dans 100% des parties aimees, 0% des rejetees : DISCRIMINE (vraie ou Milan aime, fausse ou il rejette) -> poids en hausse

## Jamais mesurees (angle mort du cerveau)
- fluidite : Le mouvement enchaine : un membre ne s'arrete pas a chaque pose cle (chevauchement, suivi), il repart avant d'etre a l'arret.

## Echelle calibree sur 4 notes : note = 7.33 + 1.32 x score

## Poids appris (ce qui fait bouger la note de Milan)
- cartes_impact        poids_note 0.73 (confiance principe 0.85)
- blanc_total          poids_note 0.73 (confiance principe 0.75)
- contraste_echelle    poids_note 0.73 (confiance principe 0.70)
- camera_vivante       poids_note 0.73 (confiance principe 0.65)
- smear_graphique      poids_note 0.73 (confiance principe 0.55)
- victime_deformee     poids_note 0.73 (confiance principe 0.50)
- variete_coups        poids_note 0.64 (confiance principe 0.60)
- silhouette_lisible   poids_note 0.64 (confiance principe 0.80)
- silence_noir         poids_note 0.64 (confiance principe 0.80)
- regard_intention     poids_note 0.64 (confiance principe 0.75)
- poing_gros_plan      poids_note 0.64 (confiance principe 0.80)
- fond_remplace        poids_note 0.64 (confiance principe 0.60)
- torsion_tronc        poids_note 0.64 (confiance principe 0.65)
- posture_droite       poids_note 0.58 (confiance principe 0.70)
- escalade             poids_note 0.58 (confiance principe 0.60)
- impact_visible       poids_note 0.58 (confiance principe 0.70)
- poing_a_plat         poids_note 0.50 (confiance principe 0.80)
- tenue_avant_choc     poids_note 0.50 (confiance principe 0.25)
- contraste_de_temps   poids_note 0.50 (confiance principe 0.70)
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
- v4 : predit 6.8, Milan 6.7
- v5 : predit 6.8, Milan 6.8
