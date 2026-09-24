# Reflexion du critique

## Predictions contre notes de Milan (poids avant apprentissage)
- v1 : predit 6.2, Milan 6.0 (ecart +0.2)
- v2 : predit 6.5, Milan 6.7 (ecart -0.2)
- v4 : predit 6.9, Milan 6.7 (ecart +0.2)
- v5 : predit 7.1, Milan 6.8 (ecart +0.3)
- v6 : predit 7.9, Milan 7.0 (ecart +0.9)

## Ce qui a change entre deux versions notees
- v1 -> v2 : note 6.0 -> 6.7 (+0.7) ; corrigees : posture_droite, escalade, impact_visible ; perdues : aucune
- v2 -> v4 : note 6.7 -> 6.7 (+0.0) ; corrigees : epaules_basses, bras_horizontal, transfert_poids ; perdues : aucune
- v4 -> v5 : note 6.7 -> 6.8 (+0.1) ; corrigees : coup_charge, arcs ; perdues : aucune
- v5 -> v6 : note 6.8 -> 7.0 (+0.2) ; corrigees : silhouette_lisible, cartes_impact, silence_noir, blanc_total, poing_gros_plan, contraste_echelle, fond_remplace, camera_vivante, hierarchie_effets ; perdues : aucune

## Suspects (toujours faux sur toutes les versions notees, note bloquee)
- **variete_coups** : Une rafale varie les formes de coups (jab, direct, crochet, marteau, toupie). (sources : 5 exemples de Milan (combo R6); IMPACT HAVEN)
- **regard_intention** : Avant que le coup parte : tres gros plan visage/yeux tenu 16-30 f (l'intention ; la charge se lit dans le regard). (sources : corpus/ETUDE_VISUELLE.md (68 planches regardees image par image, 2026-09-24) : ~10 clips; refs Roblox de Milan (TSB, Black Flash, IMPACT HAVEN...); essais v6 vus a l'ecran (captures/verification/2026-09-24-poing-dragon-v6-essais-camera-rejetes.png) : le gros plan de face d'une tete R6 montre un sourire fixe -> comique, zero tension ; le regard s'est lu par l'ORIENTATION de la tete en plan rapproche de profil, la cible au bout du regard)
- **torsion_tronc** : La puissance vient du TRONC qui s'enroule puis se deroule (vu de dos/trois-quarts, 120-150 deg), poses extremes ; garde basse et large normale. (sources : corpus/ETUDE_VISUELLE.md (68 planches regardees image par image, 2026-09-24) : ~7 clips; refs Roblox de Milan (TSB, Black Flash, IMPACT HAVEN...); lot 2 : pro vs noob Blender (BACK -> FRONT, ~180 deg), cross punch (dos a la camera a l'armement), tuto firytwig « surtout les hanches » ; MESURE : nous 98-137 deg sur les coups de puissance, M1 pro 109-162 -> la rotation existe, c'est la CAMERA de cote qui l'ecrase (la vue de dessus du 6a0095ed la montre))
- **smear_graphique** : Une trainee/smear porte la vitesse ; la trajectoire du coup reste dessinee a l'ecran quelques frames. (sources : corpus/ETUDE_VISUELLE.md (68 planches regardees image par image, 2026-09-24) : ~5 clips; refs Roblox de Milan (TSB, Black Flash, IMPACT HAVEN...))
- **victime_deformee** : La victime reagit fort : se plie autour du poing, joue ecrasee, tete qui part. (sources : corpus/ETUDE_VISUELLE.md (68 planches regardees image par image, 2026-09-24) : ~4 clips; refs Roblox de Milan (TSB, Black Flash, IMPACT HAVEN...))
- **ellipse_impact** : On n'a pas besoin de montrer le coup : les cartes, le blanc ou une coupe racontent l'impact, et on revient sur le visage ou la consequence. (sources : First time fighting a dummy (lot 2), Serious Punch TSB, OPM (le coup final = un trait dans le noir))

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
- ellipse_impact : vraie dans 100% des parties aimees, 0% des rejetees : DISCRIMINE (vraie ou Milan aime, fausse ou il rejette) -> poids en hausse
- hierarchie_effets : vraie dans 100% des parties aimees, 0% des rejetees : DISCRIMINE (vraie ou Milan aime, fausse ou il rejette) -> poids en hausse
- armement_frappe_retour : vraie dans 100% des parties aimees, 100% des rejetees : ne discrimine pas (vraie dans l'aime ET le rejete) -> poids en baisse
- trace_persistante : vraie dans 100% des parties aimees, 0% des rejetees : DISCRIMINE (vraie ou Milan aime, fausse ou il rejette) -> poids en hausse
- structure_en_actes : vraie dans 100% des parties aimees, 0% des rejetees : DISCRIMINE (vraie ou Milan aime, fausse ou il rejette) -> poids en hausse
- ralenti_consequence : vraie dans 100% des parties aimees, 0% des rejetees : DISCRIMINE (vraie ou Milan aime, fausse ou il rejette) -> poids en hausse

## Jamais mesurees (angle mort du cerveau)
- fluidite : Le mouvement enchaine : un membre ne s'arrete pas a chaque pose cle (chevauchement, suivi), il repart avant d'etre a l'arret.
- mouvement_secondaire : Ce qui pend suit en retard et se stabilise apres (queue, oreilles, cheveux, vetements) : ca vend le poids et la vitesse.
- camera_jeu_vs_cinematique : En jeu, M1 et competences se jouent dans la camera du JOUEUR (souvent de dos) et doivent s'y lire ; seul l'ultime coupe en cinematique (cartes, gros plans, angles) puis REVIENT a la camera de jeu.
- rafale_en_masse : Une rafale tres rapide se montre comme une MASSE de poings-smears continue (on lit le rythme et le volume), pas coup par coup.
- contact_prolonge : Une saisie ou une projection garde les corps en contact (on soulève, on retourne, on plaque) : la victime est manipulee, pas seulement frappee.

## Echelle calibree sur 5 notes : note = 6.87 + 0.62 x score

## Poids appris (ce qui fait bouger la note de Milan)
- silhouette_lisible   poids_note 0.65 (confiance principe 0.80)
- cartes_impact        poids_note 0.65 (confiance principe 0.85)
- blanc_total          poids_note 0.65 (confiance principe 0.75)
- contraste_echelle    poids_note 0.65 (confiance principe 0.70)
- camera_vivante       poids_note 0.65 (confiance principe 0.65)
- hierarchie_effets    poids_note 0.65 (confiance principe 0.85)
- smear_graphique      poids_note 0.64 (confiance principe 0.55)
- victime_deformee     poids_note 0.64 (confiance principe 0.50)
- ellipse_impact       poids_note 0.64 (confiance principe 0.60)
- trace_persistante    poids_note 0.64 (confiance principe 0.70)
- structure_en_actes   poids_note 0.64 (confiance principe 0.75)
- ralenti_consequence  poids_note 0.64 (confiance principe 0.60)
- posture_droite       poids_note 0.58 (confiance principe 0.70)
- escalade             poids_note 0.58 (confiance principe 0.60)
- impact_visible       poids_note 0.58 (confiance principe 0.70)
- silence_noir         poids_note 0.51 (confiance principe 0.80)
- poing_gros_plan      poids_note 0.51 (confiance principe 0.80)
- fond_remplace        poids_note 0.51 (confiance principe 0.60)
- variete_coups        poids_note 0.50 (confiance principe 0.60)
- poing_a_plat         poids_note 0.50 (confiance principe 0.80)
- tenue_avant_choc     poids_note 0.50 (confiance principe 0.25)
- contraste_de_temps   poids_note 0.50 (confiance principe 0.70)
- fluidite             poids_note 0.50 (confiance principe 0.60)
- explosion_apres      poids_note 0.50 (confiance principe 0.50)
- regard_intention     poids_note 0.50 (confiance principe 0.75)
- torsion_tronc        poids_note 0.50 (confiance principe 0.65)
- mouvement_secondaire poids_note 0.50 (confiance principe 0.60)
- camera_jeu_vs_cinematique poids_note 0.50 (confiance principe 0.80)
- rafale_en_masse      poids_note 0.50 (confiance principe 0.60)
- contact_prolonge     poids_note 0.50 (confiance principe 0.50)
- signature_visuelle   poids_note 0.50 (confiance principe 0.65)
- armement_frappe_retour poids_note 0.43 (confiance principe 0.80)
- epaules_basses       poids_note 0.40 (confiance principe 0.50)
- bras_horizontal      poids_note 0.40 (confiance principe 0.80)
- transfert_poids      poids_note 0.40 (confiance principe 0.60)
- coup_charge          poids_note 0.40 (confiance principe 0.60)
- arcs                 poids_note 0.40 (confiance principe 0.80)

## Predictions apres apprentissage
- v1 : predit 6.3, Milan 6.0
- v2 : predit 6.5, Milan 6.7
- v4 : predit 6.6, Milan 6.7
- v5 : predit 6.7, Milan 6.8
- v6 : predit 7.1, Milan 7.0
