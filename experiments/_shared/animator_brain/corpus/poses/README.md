# Poses mesurées (bibliothèque en construction)

Créé le 2026-09-26 (analyse géométrique du poing chargé, après la v5 notée
7,5 : « analyse visuellement, géométriquement »). Brique A0 du plan
`corpus/recherche/PLAN_REORGANISATION_2026-09-26.md` : verser dans le dépôt
ce qui dormait dans le dossier temporaire de session.

Ici : des NOMBRES et du CODE, jamais d'image de ref (droits). Les chemins
d'images cités dans les JSON pointent vers le dossier temporaire de la
session du 2026-09-26 : ils n'existent plus ailleurs.

## `sources/` : une analyse vérifiée par fichier

Chaque fichier = le résultat d'un agent + le verdict d'un ou deux
vérificateurs adverses (`verifications` : confirme / corrige / refute, avec
preuves). **Lire les vérifications avant de citer un nombre** : elles
corrigent souvent le résultat.

| fichier | quoi | statut |
|---|---|---|
| `pro_tsb_m1_m4.json`, `pro_tsb_ultimes.json`, `pro_pack_battleground.json` | géométrie EXACTE (fichiers d'animation R6) des coups pro : armé, départ, contact, temps, translation du bras hors de l'épaule | exact R6 (autres persos que le Serious Punch) |
| `recon_pew_*.json`, `recon_tsb_*.json`, `recon_sp2.json`, `recon_anime.json` | refs RECONSTRUITES en 3D R6 par rendu-comparaison (`outils/geo_pose.py`) | reconstruit, vérifié par contradicteur, avec des parts incertaines marquées |
| `nous_v5_mesure.json`, `nous_v5_ce_que_milan_voit.json` | notre v5 mesurée, et ce que ses plans laissaient voir | exact (notre export) |

Note : les reconstructions faites AVANT le correctif de `geo_pose.pose`
(2026-09-26, bras décalé jusqu'à 1 stud) ont des positions de poing
approximatives ; les DIRECTIONS de bras restent valables d'après les
vérificateurs.

## `scripts_2026-09-26/` : le code des analyses, tel quel

Non nettoyé, gardé pour refaire ou reprendre une mesure (ajustement de pose
sur image, suivi de caméra par points de fuite de la grille, lecteur rbxm
qui ignore les poses de poids 0, fourchettes pro).
