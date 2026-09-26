# Reflexion du critique

> **HISTORIQUE (daté).** Ce document n'est plus un protocole à suivre. Point
> d'entrée actuel de la piste animation : `ETAT.md` ; apprentissages vivants :
> `corpus/CARNET.md` ; conception : `corpus/fiches/`. (Audit mémoire du
> 2026-09-26.)


## Mes predictions contre les notes de Milan, PAR AXE

- technique : biais moyen +0.3 sur 4 note(s) (v5 7.2->6.8, v6 7.8->7, v8 7.4->7.5, v9 7.9->7.7)
- vfx : biais moyen +3.0 sur 2 note(s) (v11_aura_dragon 7->4, v12_dragon_premium_pose_goku_izuku 6->3)

## Predictions contre notes de Milan (poids avant apprentissage)
- v1 : predit 6.3, Milan 6.0 (ecart +0.3)
- v2 : predit 6.4, Milan 6.7 (ecart -0.3)
- v4 : predit 6.7, Milan 6.7 (ecart +0.0)
- v5 : predit 6.8, Milan 6.8 (ecart +0.0)
- v6 : predit 7.3, Milan 7.0 (ecart +0.3)
- v8 : predit 7.5, Milan 7.5 (ecart +0.0)
- v9 : predit 7.5, Milan 7.7 (ecart -0.2)

## Ce qui a change entre deux versions notees
- v1 -> v2 : note 6.0 -> 6.7 (+0.7) ; corrigees : posture_droite, escalade, impact_visible ; perdues : aucune
- v2 -> v4 : note 6.7 -> 6.7 (+0.0) ; corrigees : epaules_basses, bras_horizontal, transfert_poids ; perdues : bras_libre_ramene
- v4 -> v5 : note 6.7 -> 6.8 (+0.1) ; corrigees : coup_charge, arcs ; perdues : aucune
- v5 -> v6 : note 6.8 -> 7.0 (+0.2) ; corrigees : silhouette_lisible, cartes_impact, silence_noir, blanc_total, poing_gros_plan, contraste_echelle, fond_remplace, camera_vivante, hierarchie_effets ; perdues : aucune
- v6 -> v8 : note 7.0 -> 7.5 (+0.5) ; corrigees : regard_intention, torsion_tronc, bras_libre_ramene, frappe_lineaire, silhouette_non_croix ; perdues : coup_charge
- v8 -> v9 : note 7.5 -> 7.7 (+0.2) ; corrigees : aucune ; perdues : arme_tenu_long

## Suspects (toujours faux sur toutes les versions notees, note bloquee)
- **variete_coups** : Une rafale varie les formes de coups (jab, direct, crochet, marteau, toupie). (sources : 5 exemples de Milan (combo R6); IMPACT HAVEN)
- **smear_graphique** : Une trainee/smear porte la vitesse ; la trajectoire du coup reste dessinee a l'ecran quelques frames. (sources : corpus/ETUDE_VISUELLE.md (68 planches regardees image par image, 2026-09-24) : ~5 clips; refs Roblox de Milan (TSB, Black Flash, IMPACT HAVEN...))
- **victime_deformee** : La victime reagit fort : se plie autour du poing, joue ecrasee, tete qui part. (sources : corpus/ETUDE_VISUELLE.md (68 planches regardees image par image, 2026-09-24) : ~4 clips; refs Roblox de Milan (TSB, Black Flash, IMPACT HAVEN...))
- **ellipse_impact** : On n'a pas besoin de montrer le coup : les cartes, le blanc ou une coupe racontent l'impact, et on revient sur le visage ou la consequence. (sources : First time fighting a dummy (lot 2), Serious Punch TSB, OPM (le coup final = un trait dans le noir))
- **ligne_epaules** : Coup droit : a l'extension, le bras qui frappe PROLONGE la ligne des epaules (torse tourne presque de profil) ; pied arriere, torse et bras forment une seule droite. C'est « l'epaule dans le coup ». (sources : corpus/TUTOS_ANIMATION.md (recherche 2026-09-24 : DevForum Roblox, 31 sources ; ArcSys GGXrd 4Gamer, Cartwright GDC 2014, Mattesi FORCE ; extraits sakugabooru mesures); pack pro battleground (4 M1) : bras/epaules 18-28 deg, torse detourne 67-75 deg au contact ; NOUS v6 : 46-72 et 32-48 (captures/verification/2026-09-24-cerveau-ligne-epaules-pro-vs-nous.png); Motomura (ArcSys) : mettre ou non l'epaule dans le coup change « j'ai mis de la force » / « j'ai frappe leger »; Mattesi FORCE : extension = une seule droite du pied arriere au poing; DevForum Shift4D : tourner le torse encore plus; animations TSB officielles (fichier fourni par Milan, 13 animations ; mesures derivees dans corpus/perception_tsb.json) : les M1 TSB NE le font PAS (bras/epaules 61-78 deg, torse detourne 23-62 deg, bras libre 0,26-0,79) -- plus proches de nous que du pack. Regle ramenee a une hypothese de style « pack », pas une regle TSB.; vidéos tutos envoyées par Milan (zips 2026-09-24, étude visuelle image par image ; corpus/tutos/rapport_video_*.md) : tuto punch Blender : au contact le torse a pivoté ~180° depuis la charge (on voit son dos), penché ~45°, bras de frappe horizontal dans l'axe de l'épaule ET translaté vers l'avant (décollé), bras libre replié contre la tête, jambe arrière tendue presque couchée ; coup de boxe (smears, vidéo techniques anime) : épaule entièrement rentrée, tête qui plonge)

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
- depassement_1f : Une image de DEPASSEMENT au-dela de la pose d'extension (ou du corps hors de sa pose finale dans le sens du coup), puis retour : l'arret n'est jamais mort.
- recuperation_effort : Apres un gros coup, la recuperation montre l'EFFORT (recul, reprise d'appui, poids) ; le retour a la garde est lent et ne ressemble pas a un second coup.
- poses_tenues_limitees : Animation LIMITEE : sur les attaques, poses tenues de durees irregulieres (1 a 5 f a 60 i/s) sans interpolation ; seules les trajectoires (saut, vol, dash) restent lisses.
- tenue_vivante : Une pose tenue (fin de coup, pic, retour) n'est jamais figée : micro-mouvement en petits cercles d'amplitude et de vitesse décroissantes (l'énergie s'amortit), clés aux mêmes images que le reste.
- ligne_equilibre : Sur une pose hors d'équilibre, la tête reste au-dessus du pied d'appui (ligne verticale tête → pied) : le corps peut basculer fort sans avoir l'air de tomber, et la pose paraît lourde.
- corps_avant_bras : Ordre de travail : le TORSE porte tout le mouvement (anticipation, drag, milieu, exagération, amorti) et doit se lire SEUL, avant qu'un bras bouge ; puis bras libre, bras qui frappe, tête, jambes en dernier (pieds plantés).
- pose_apres_tenue : La pose d'APRÈS le coup est la plus extrême et la plus longue : corps plié / couché dans le sens du coup, très bas, tenue 0,4-1 s (vivante). L'extension elle-même ne dure qu'1-2 images : l'œil lit charge tenue → pose d'après tenue.
- cadrage_serre : Placement : pendant un temps fort, le perso REMPLIT le cadre (plan poitrine/taille, 60-80 % de la hauteur), caméra basse, souvent inclinée (dutch) ; le décor n'est qu'un fond. Un changement de pose qui ne couvre que 1/4 de l'image ne se voit pas.
- reglage_double : Correction de jugement : mes réglages d'amplitude « à l'œil » sont systématiquement ~2x trop sages par rapport aux références (enroulement, hauteur du corps, écart des pieds). Avant de valider une pose, la pousser jusqu'à ce qu'elle paraisse trop, puis comparer à la ref au même angle.
- vfx_couverture_pic : Au pic d'un gros impact ou d'un ultime, l'effet COUVRE une grande part de l'image (refs Roblox 49-77 % des pixels, anime 99 %) : il ne décore pas un coin du cadre, il EST l'image un instant.
- signature_tenue : L'effet-SIGNATURE d'un ultime (le dragon, l'horloge, le trou noir) reste à l'écran assez longtemps pour être REGARDÉ : de l'ordre de 1,5-2,5 s, pas une apparition.
- signature_vers_objectif : La signature d'un ultime vient VERS la caméra et grossit jusqu'au très gros plan (le dragon sort du tourbillon, gueule vers nous) ; elle est le coup, pas un décor qui tourne à côté.

## Echelle calibree sur 7 notes : note = 7.02 + 0.97 x score

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
- regard_intention     poids_note 0.54 (confiance principe 0.75)
- torsion_tronc        poids_note 0.54 (confiance principe 0.65)
- bras_libre_ramene    poids_note 0.54 (confiance principe 0.40)
- frappe_lineaire      poids_note 0.54 (confiance principe 0.55)
- silhouette_non_croix poids_note 0.54 (confiance principe 0.40)
- silence_noir         poids_note 0.51 (confiance principe 0.80)
- poing_gros_plan      poids_note 0.51 (confiance principe 0.80)
- fond_remplace        poids_note 0.51 (confiance principe 0.60)
- variete_coups        poids_note 0.50 (confiance principe 0.60)
- poing_a_plat         poids_note 0.50 (confiance principe 0.80)
- tenue_avant_choc     poids_note 0.50 (confiance principe 0.25)
- contraste_de_temps   poids_note 0.50 (confiance principe 0.70)
- fluidite             poids_note 0.50 (confiance principe 0.60)
- explosion_apres      poids_note 0.50 (confiance principe 0.50)
- mouvement_secondaire poids_note 0.50 (confiance principe 0.60)
- camera_jeu_vs_cinematique poids_note 0.50 (confiance principe 0.80)
- rafale_en_masse      poids_note 0.50 (confiance principe 0.60)
- contact_prolonge     poids_note 0.50 (confiance principe 0.50)
- signature_visuelle   poids_note 0.50 (confiance principe 0.65)
- ligne_epaules        poids_note 0.50 (confiance principe 0.55)
- bras_avant_bras      poids_note 0.50 (confiance principe 0.70)
- compression_extension poids_note 0.50 (confiance principe 0.70)
- depassement_1f       poids_note 0.50 (confiance principe 0.70)
- recuperation_effort  poids_note 0.50 (confiance principe 0.60)
- poses_tenues_limitees poids_note 0.50 (confiance principe 0.50)
- bascule_competence   poids_note 0.50 (confiance principe 0.60)
- tenue_vivante        poids_note 0.50 (confiance principe 0.55)
- torsion_charge_contact poids_note 0.50 (confiance principe 0.50)
- arme_tenu_long       poids_note 0.50 (confiance principe 0.55)
- ligne_equilibre      poids_note 0.50 (confiance principe 0.50)
- corps_avant_bras     poids_note 0.50 (confiance principe 0.60)
- pose_apres_tenue     poids_note 0.50 (confiance principe 0.60)
- cadrage_serre        poids_note 0.50 (confiance principe 0.60)
- obari_poing_objectif poids_note 0.50 (confiance principe 0.65)
- pose_pour_sa_camera  poids_note 0.50 (confiance principe 0.60)
- reglage_double       poids_note 0.50 (confiance principe 0.55)
- pose_vue_nette       poids_note 0.50 (confiance principe 0.55)
- vfx_couverture_pic   poids_note 0.50 (confiance principe 0.60)
- signature_tenue      poids_note 0.50 (confiance principe 0.65)
- signature_vers_objectif poids_note 0.50 (confiance principe 0.50)
- armement_frappe_retour poids_note 0.43 (confiance principe 0.80)
- epaules_basses       poids_note 0.40 (confiance principe 0.50)
- bras_horizontal      poids_note 0.40 (confiance principe 0.80)
- transfert_poids      poids_note 0.40 (confiance principe 0.60)
- coup_charge          poids_note 0.40 (confiance principe 0.60)
- arcs                 poids_note 0.40 (confiance principe 0.80)

## Predictions apres apprentissage
- v1 : predit 6.2, Milan 6.0
- v2 : predit 6.5, Milan 6.7
- v4 : predit 6.7, Milan 6.7
- v5 : predit 6.7, Milan 6.8
- v6 : predit 7.3, Milan 7.0
- v8 : predit 7.5, Milan 7.5
- v9 : predit 7.5, Milan 7.7
