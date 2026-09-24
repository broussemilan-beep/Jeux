# Poing du Dragon v7 : fiche (proposition)

**État.** **Exécutée** le 2026-09-24, après le go de Milan (« Go v7 »).
Résultat et écarts avec ce plan : section v7 du `README.md`. Objectif :
8/10 minimum.

- Étude close : fichier TSB officiel, 3 rapports de recherche, 6 vidéos de
  tutos étudiées image par image.
- Sources : `corpus/TUTOS_ANIMATION.md` §7-8, `corpus/ETUDE_TSB.md`,
  `corpus/tutos/rapport_video_*.md`.

## Ce que Milan a dit (v6 : 7/10)

- **Caméra de jeu** : rend bien.
- **Caméra ciné** : un peu trop abusée, mais léger.
- **L'animation reste le bémol** : il manque « une touche manga ». Même un coup
  simple n'est pas un coup simple : il y a une anatomie et une règle
  différentes.
- **Le rythme est bon.** Le corps secondaire et la victime sont des détails.

## Le diagnostic, confirmé par 4 sources indépendantes

Nos deux poses clés du coup chargé sont celles que les animateurs R6
rejettent.

| | v6 | ce que montrent les sources |
|---|---|---|
| **charge** | croix : torse droit (bascule 0-1°), les deux bras à l'horizontale, écartés. **Mesuré : 93 % des images de la charge en croix ; attaquant TSB : 0 % sur 13 animations.** | ✗ exact de la planche de Xoaterz : « boring sameside posing / looks like a stickman ». Le ✓ « akin to The Serious Punch (TSB) » a le torse de 3/4 penché, le bras armé derrière l'épaule et le genou levé. Même chose dans le tuto punch (torse ~90° détourné) et l'uppercut Moon (torse de profil). |
| **contact** | torse penché de seulement 20°, et le **bras libre part vers l'avant avec l'autre** (écart entre les deux bras : 28°). La torsion, elle, est déjà là : **130° mesurés** de la charge au contact. | Tuto punch : torse pivoté ~180° depuis la charge, penché ~45°, bras décollé vers l'avant. Coup de boxe (anime) : épaule rentrée, tête qui plonge. Compétences TSB : le corps bascule de 44 à 97°. |
| **tenue** | pose tenue | Uppercut Moon : la tenue n'est **jamais figée** (petits cercles qui ralentissent). |
| **frappe** | rampe cuite image par image | Linear, clés espacées ; la frappe tient en **2 images** entre deux clés (uppercut, punch). |

Ce que les sources confirment de la v6 (on n'y touche pas) :
- l'armé tenu avant de lâcher (obari 0,9-1,8 s ; notre charge ~0,7 s) ;
- les images d'impact ;
- le poing vers la caméra ;
- le contraste d'échelle ;
- le rythme général.

## Croquis (labo de poses, vérifiés à l'écran)

`captures/verification/2026-09-24-croquis-v7b-apres-tutos-video.png`
(script : `scripts/croquis_v7.py`), sur trois vues : profil, 3/4 face et
caméra de jeu.

- **Charge v7** : torse détourné ~85° de la cible (la v6 l'est déjà) et
  penché de 25°. Poing armé HAUT derrière l'épaule, bras avant replié qui
  vise bas, genou levé. Silhouette compacte et asymétrique.
  - Le détecteur de croix dit « non » sur ce croquis, et « oui » sur 93 % de
    la charge v6.
  - Une 1re version, penchée de 12° avec le bras avant tendu, ne sortait de
    la croix que de justesse. Elle a été corrigée.
  - **Risque** : en caméra de jeu (de dos), une charge de profil est étroite.
    On vérifiera la lisibilité sur la vraie capture du rig.
- **Contact v7 E, « ligne jetée »** : lacet +70°, soit ~155° de rotation
  depuis la charge. Torse penché de 40° vers la cible, bras horizontal, bras
  libre ramené à la hanche. La jambe arrière prolonge le torse et traîne en
  l'air. Il n'y a qu'une seule ligne, du pied arrière au poing.
- **Contact v7 G, « sage »** : lacet 55°, penché de 35°. C'est le repli si E
  lit mal en caméra de jeu.

**Contrainte R6 trouvée en croquant.** Le torse R6 est aussi le bassin. Un
torse de profil penché vers la cible fait donc basculer la ligne des hanches.
Au-delà de ~30°, les deux pieds ne peuvent plus rester au sol sans grand
écart ; la jambe avant passe à l'horizontale et le perso a l'air assis. La
ligne jetée se fait donc **pied arrière en l'air** (fente lancée), comme
dans le tuto punch (« jambe arrière presque couchée »). C'est une image de
passage, pas une pose au repos (contre-indication de `ligne_equilibre`).

**Point ouvert, vu sur la vue « jeu ».** Le bras libre ramené à la hanche
passe devant la caméra de jeu. On arbitrera sur la vraie capture du rig :
hanche, ou bras tiré vers l'extérieur hors de la silhouette.

## Ce que la v7 change (et seulement ça)

| temps | changement | règle du cerveau |
|---|---|---|
| charge f118-146 | croix → **charge « Serious Punch »** (croquis). La **tête regarde la cible**. Tenue vivante : petits cercles, amplitude décroissante. | `silhouette_non_croix`, `compression_extension`, `regard_intention`, `tenue_vivante` |
| coup f146-150 | **frappe en 2 images** entre deux clés, avec une clé intermédiaire sur le seul bras qui frappe. On garde la torsion (130° en v6, ~155° sur le croquis). | `frappe_lineaire`, `torsion_charge_contact` (déjà vraie) |
| contact f150 + hitstop | **ligne jetée E** (ou G) : bascule 20° → 40°, **bras libre ramené** (v6 : tendu avec l'autre). 1 image de dépassement puis retour. Le gel du hitstop reste un gel (c'est le signal). | `ligne_epaules` (coups qui comptent), `depassement_1f`, `bascule_competence` |
| après le coup | **retour avec effort** (reprise d'appui), puis tenue vivante et non figée | `recuperation_effort`, `tenue_vivante` |
| rafale h1-h4 | **inchangée**, **que des poings** (décision de Milan : pas de coup de pied). Les M1 TSB ne suivent pas la ligne d'épaules. On retouche seulement si une pose tombe dans la croix ✗. | contre-indications `ligne_epaules`, `torsion_charge_contact` |
| export | poses clés seules (~15/s) en Linear | `frappe_lineaire` (TSB) |
| caméra ciné | **un cran moins** : gros plans plus courts, secousses réduites | retour Milan |
| aérien, VFX, cartes, rythme | **inchangés** | ne pas casser ce qui marche |

**Décision de Milan (2026-09-24) : pas de coup de pied.** La technique reste
uniquement aux poings.

## Méthode d'exécution (après le go)

1. Poser les 3 clés (charge, contact, retour) dans le rig V2.22. **Capture
   des 3 vues**, comparée aux croquis. On corrige avant d'animer quoi que ce
   soit d'autre.
2. Timing : on garde les images v6 (le rythme est bon). La frappe est
   refaite en 2 images, avec le wiggle sur les tenues.
3. Export des clés éparses + `verify_export.py` : sens, Linear, contacts,
   pieds.
4. Vidéo en caméra de jeu et en caméra ciné. Planche avant/après committée.
   Les états du cerveau sont mesurés (`etats.py`), la prédiction est notée
   **avant** l'avis de Milan.

## Estimation

- **Critique du cerveau.** Il prédit 7,1 pour la v6 (Milan : 7). Avec ce
  plan, il prédit **7,2**. Il sous-pèse la pose parce qu'il n'a jamais vu
  une note bouger sur un changement de pose : ses poids viennent de v1-v6,
  où les poses n'ont pas changé de nature. Sur ce point, je fais passer mon
  jugement avant son chiffre, et je le dis.
- **Mon estimation : 8,0** (fourchette 7,6 à 8,4).
  - **Pour** : c'est le levier que Milan désigne lui-même. Quatre sources
    indépendantes pointent la même paire de poses. Le ✓ de Xoaterz cite
    littéralement le Serious Punch de TSB.
  - **Risque principal** : la ligne jetée E peut mal lire en caméra de jeu
    (bras libre devant l'objectif). C'est pour ça qu'on a le repli G et la
    capture des 3 vues avant d'animer.
- 8 n'est pas garanti : la « touche manga » est jugée par Milan, pas par une
  mesure.
