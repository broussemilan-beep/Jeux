# Étude des animations TSB officielles

Source : fichier `tsb_anim.rbxm` envoyé par Milan le 2026-09-24. Il contient
13 KeyframeSequences.
- Coups de base : M1, M2, M3, M4.
- Compétences : Collateral Ruin, Stoic Bomb, Swift Sweep (et ses variantes
  Fail et Victim).
- Ultimes : Ultimate1, Ultimate2.
- Combo au mur : WallComboPlayer, WallComboVictim.

Le fichier n'est **pas** versionné (œuvre protégée). Seules les mesures
dérivées le sont, dans `corpus/perception_tsb.json` (produit par
`etats.tsb_reference`). La lecture passe par `corpus.resample_linear`, qui
interpole les clés éparses membre par membre, comme l'Animator. [CONTREDIT 2026-09-26 : l'EasingStyle n'était pas décodé (Linear partout) : les poses Constant sont dessinées fausses entre les clés ; la correction du code est hors de ce fichier, voir corpus/etude_c4/A3_tsb_ultimes_mur.md §0.3 et corpus/etude_c4/A1_tsb_coups_courts.md (« Oublis importants », point 1)]

C'est la première vraie référence de la cible de Milan. Elle corrige une
conclusion tirée la veille du pack battleground.

## 1. Comment TSB est animé (mesuré)

| | TSB | nous (v1 à v6) |
|---|---|---|
| interpolation | **Linear** sur 3 425 des 3 492 poses (67 Constant, dans le combo au mur) | Linear (après correction du bug d'export), mais… |
| densité de clés | **12 à 18 clés/s** sur les animations faites à la main (une pose toutes les ~4 f à 60 i/s) ; M1 = **8 clés en 0,43 s** | 29,5 clés/s, écart médian **1 f** : cuit image par image depuis des courbes Bézier |
| cuit image par image | seulement Ultimate2 et WallComboVictim [CONTREDIT 2026-09-26 : Stoic Bomb a aussi un segment cuit (i0-i11, tête jusqu'à i22) ; WallComboVictim est hybride (cuite dès f132) ; WallComboPlayer a 67 poses Constant ; les 7 coups courts sont 100 % Linear (Enum décodé), voir corpus/etude_c4/A2_tsb_stoic_collateral.md §6 point 5, corpus/etude_c4/A3_tsb_ultimes_mur.md §0.2, corpus/etude_c4/A1_tsb_coups_courts.md V2] | tout |
| jambes sur M1-M3 | **aucune piste** : la course se superpose (convention confirmée) [CONTREDIT 2026-09-26 : vrai pour M1-M3 seulement : M4 pose les jambes (22 clés, 0,69 s), la convention n'est pas générale chez TSB, voir corpus/etude_c4/A4_pack_battleground.md (vérification adverse, point 8)] | animées |

Recoupement : Guilty Gear Xrd anime à 15 poses/s et dit que « lisser à 60 i/s
puis sauter des images donne de la 3D qui rame ». TSB est à 12-18 poses/s,
avec des transitions linéaires entre elles.

## 2. La différence qui revient partout : la forme de la frappe

Vitesse du poing image par image jusqu'au contact (image :
`captures/verification/2026-09-24-cerveau-profil-frappe-tsb-vs-nous.png`).
- **TSB** : lente dérive (15 à 20 studs/s), puis le poing **passe à pleine
  vitesse en 1 image** et file en **palier** 2 à 3 images. Plateau (vitesse
  mini / maxi de la phase rapide) : **0,92 à 1,0** sur M1-M4.
- **Nous** : rampe en **triangle** sur 2 à 3 images, avec une pointe unique.
  Plateau **0,51 à 0,77** sur les 5 coups de la v6, et 0,56 à 0,70 en médiane
  de la v1 à la v6.

Ce défaut est présent dans **toutes** nos versions, ce qui colle avec « l'animation
reste toujours le bémol ». Hypothèse `frappe_lineaire`, mesurée
automatiquement.

## 3. Ce que TSB ne fait PAS : correction d'hier

Au contact des M1 TSB : angle bras / ligne des épaules de 61 à 78°, torse
détourné de 23 à 62°, bras libre de 0,26 à 0,79. TSB est **plus proche de
nous que du pack battleground** (18-28°, 72-79°, 0-0,3). Les règles
`ligne_epaules` et `bras_libre_ramene` étaient tirées du pack, pas de TSB :
leur confiance passe à 0,4 et elles sont étiquetées « style pack ».

Autres points sans écart avec TSB : inclinaison du torse sur les M1 (TSB
12-26°, nous 12-16°), hauteur de l'armement, translation du bras, écart des
jambes.

## 4. Compétences : le corps bascule fort (mesuré et vu)

Bascule du torse, 90e centile :

| animation | bascule |
|---|---|
| Swift Sweep | 97° |
| Collateral Ruin | 70° |
| WallCombo | 50° |
| Swift Sweep (Fail) | 44° |
| M4 | 32° |
| Stoic Bomb | 32° (max 158°, plongeon) |
| Ultimate1 | **7°** (sobre, la mise en scène porte) |
| nous : rafale | 17° |
| nous : charge et coup | **35°** |
| nous : aérien | 69° |

Hypothèse `bascule_competence`, mesurée. Seuil : 1er quartile des
compétences TSB, 43,6°.

Ce qu'on voit sur les planches de poses (fil de fer, 3 vues ; scratchpad,
non versionné) :
- **Collateral Ruin** : appuis très écartés et asymétriques, torse penché,
  vrille à l'horizontale.
- **Stoic Bomb** : plongeon corps à l'horizontale, [CONTREDIT 2026-09-26 : un salto qui part tête en bas (penché +158°) à l'apex, voir corpus/etude_c4/A2_tsb_stoic_collateral.md §6 point 4] puis **tenue de 2,5 s**,
  bras croisés devant la poitrine (la charge, silhouette compacte), puis
  libération.
- **M1** : le corps entier bascule d'un bloc, car les jambes n'ont pas de
  piste et suivent le torse.
- **Ultimate1** : 10 s presque debout, un bras qui bouge. [CONTREDIT 2026-09-26 : deux bras, buste jusqu'à 86°, recul de 1,5 stud, un pas ; trois longues tenues mouvantes (≈170, 142, ≈60 images), voir corpus/etude_c4/A3_tsb_ultimes_mur.md §1.5] La caméra et les
  VFX font l'ultime.

## 4 bis. Vu sur les planches (2e passe) : les jambes et la variété

- **M4, le coup qui ferme le combo, est un COUP DE PIED** : jambe à
  l'horizontale et torse basculé loin en arrière (f9-f15) [CONTREDIT 2026-09-26 : la jambe monte en diagonale f0-f12, n'est horizontale que f13-f14 après un claquement d'une image, avec un petit saut de +0,48, voir corpus/etude_c4/A1_tsb_coups_courts.md V7], puis retour.
  M1 à M3 sont des poings. TSB change de membre pour fermer le combo ; notre
  rafale enchaîne 4 poings (`variete_coups` est faux depuis la v4).
- **Swift Sweep** : balayage, vrille, puis un coup de pied **tenu jambe à
  l'horizontale environ 27 f** (0,45 s). Le pic est tenu, comme dans l'anime.
- **Combo au mur** : genoux, coups de pied, torse à l'horizontale.
- **Mesures.** Part du temps avec un pied au-dessus de la hanche :

  | animation | pied au-dessus de la hanche |
  |---|---|
  | Swift Sweep | 62 % |
  | M4 | 12 % |
  | Stoic Bomb | 4 % |
  | Collateral Ruin | 2 % |
  | WallCombo | 2 % |
  | Ultimate1-2 | 0 % |
  | nous : rafale et charge | 0 % |
  | nous : aérien | 9 % |

  C'est **propre à la technique**, pas une règle universelle : une compétence
  « de jambes » les utilise, les autres non.
- **Tenues** (extrémités à moins de 4 studs/s pendant au moins 6 f) :
  - TSB : Stoic Bomb 81 f (la charge) ; Ultimate1 58, 35, 21 f ; [CONTREDIT 2026-09-26 : trois longues tenues mouvantes de ≈170, 142 et ≈60 images, voir corpus/etude_c4/A3_tsb_ultimes_mur.md §1.5]
    Collateral Ruin 16 f.
  - Nous : 18 f sur la charge, 58 et 27 f dans l'aérien.
  - Pas d'écart de principe.

**Jugement.** Pour une rafale de poings, la variété TSB passe par le
**membre** : le dernier coup du combo est un coup de pied ou un genou, avec
le corps entier qui bascule. C'est une piste de refonte pour notre h4, à
proposer à Milan, pas une règle.

## 4 ter. Nos poses du coup chargé à la même grille (jugement visuel)

Nos 13 poses clés f108-168 ont été rendues avec le même fil de fer que TSB
(scratchpad, `nous_charge.png`).
- **Charge (f121-f144).** Les deux bras sont écartés à l'horizontale de part
  et d'autre et le torse reste **vertical**. La silhouette est une **croix
  symétrique**, rigide. Rien n'est comprimé : ni torse enroulé vers le bas,
  ni tête rentrée, ni poing armé bas derrière le corps.
- **Contact (f150).** Le torse est encore **vertical** : seul le bras part,
  le corps ne s'engage pas.
- **À côté**, TSB (Collateral Ruin, M4, Swift Sweep) : le torse penche
  (44-97° au 90e centile), les angles sont francs et asymétriques, le corps
  va dans le coup.

**Lecture.** C'est très probablement la « touche manga » qui manque selon
Milan sur ce coup. On retrouve deux règles de l'anime (`TUTOS_ANIMATION.md`
§4) : la **compression en C** pendant la charge, puis l'**extension en une
droite** hors d'équilibre, du pied arrière au poing, torse compris.

## 4 quater. Les refs R6 de Milan relues avec cette question

Question : au contact, le torse est-il droit ou jeté dans le coup ?
- **combo_r6_front** : au coup, le corps entier **pivote violemment**,
  jusqu'à montrer le dos à la caméra. Au 2e coup, le torse **plonge vers
  l'avant** et le corps descend. Jamais un torse vertical.
- **double_jab_r6** : torse **penché en avant** pendant tout le combo ; bras
  qui frappe tendu, l'autre ramené.

Même conclusion que TSB et l'anime, trois sources indépendantes : le corps
s'engage. Les croquis v7 vont dans ce sens (`experiments/r6_poing_dragon/FICHE_V7.md`).

## 5. Ce que ça change pour nous

1. **Le levier n°1 est notre chaîne d'export, pas nos poses.** Nous
   exportons chaque image, cuite depuis des courbes lissées. TSB pose une
   clé toutes les ~4 images et laisse le moteur interpoler linéairement.
   L'A/B à faire : exporter nos **poses clés seules** (en Linear, environ
   15/s), pas le bake, et comparer sur un coup.
2. **Sur le coup chargé** (compétence), laisser le corps basculer davantage
   (bascule ≥ 45°) plutôt que rester droit. Ne pas confondre avec
   « accroupi » (retour de Milan sur v1-v2).
3. Garder la règle « M1 sans jambes » pour de futurs M1. Le Poing du Dragon
   est une technique complète, jambes animées.

## 6. A/B « clés éparses » sur notre coup chargé : résultat

- **Variante B** : mêmes poses. Sur f108-170, l'export ne garde que les 12
  poses clés posées à la main, au lieu de 43 clés cuites, et Roblox relie en
  Linear. Script : `r6_poing_dragon/scripts/ab_cles_eparses.py` ; sortie :
  `output/ab_cles_eparses/`.
- **Mesure** : plateau de vitesse du poing 0,51 → 0,79 ; arrivée au contact
  0,65 → 1,0 ; contact identique ; sol −0,113.
- **Vu à l'écran** (caméra cinéma et profil, 109 images chacune ;
  `captures/verification/2026-09-24-ab-cles-eparses-coup-charge-a-vs-b.png`) :
  la différence est **presque invisible**. Au départ du coup, nos clés sont
  déjà espacées de 2 f (146, 148, 150) : la façon de les relier compte peu.
- **Jugement.** L'export en clés éparses est fidèle à TSB et ne coûte rien.
  On le garde pour la refonte, mais **ce n'est pas lui qui fera la note** sur
  ce coup. Le levier est dans les **poses** (§4 ter : croix symétrique, torse
  vertical). La mesure « plateau » décrit bien TSB, mais son écart visible
  dépend de l'espacement des clés : c'est une conséquence, pas une cause à
  corriger seule. On n'a pas demandé à Milan de juger un A/B invisible.

