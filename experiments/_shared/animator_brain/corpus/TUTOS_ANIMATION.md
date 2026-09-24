# Tutos et explications d'animation : ce qu'on en tire

Recherche du 2026-09-24, à la demande de Milan : « Roblox d'abord, puis
général ». Retour qui la motive (v6, 7/10) : « Les poses manquent d'une
touche manga. Même un coup simple n'est pas un coup simple : il y a une
anatomie et une règle différentes. »

**Sources.** Trois rapports complets sont dans `tutos/`. Ils sont notés
[LU] (lu), [MESURÉ] (mesuré) ou [RÉSUMÉ-RECHERCHE] (vu seulement en extrait
de moteur de recherche).
- `rapport_devforum.md` : 31 fils du DevForum Roblox, dont des critiques
  d'animations de combat par des animateurs expérimentés.
- `rapport_roblox_web.md` : documentation officielle Roblox (dépôt
  `creator-docs`), code du plugin Blender, dépôts de modules de combat.
- `rapport_anime3d.md` :
  - Arc System Works (GGXrd, interview 4Gamer, diapositives de Motomura) ;
  - Cartwright (Skullgirls, GDC 2014) ;
  - Mattesi (*FORCE*) ;
  - 4 extraits JJK, MHA et OPM mesurés image par image.

**Ce qui était bloqué.**
- Toutes les vidéos : YouTube passe par une vérification anti-robot.
- Les images du DevForum (hébergées sur S3), reddit, TikTok.
- Les pages roblox.com, dont l'asset « TSB OFFICIAL Animations » (16072313171).

Aucune image protégée n'est commitée.

## 1. Ce que la recherche a corrigé tout de suite

**L'export Roblox était faux depuis le début.** Tous nos exports écrivaient
`EasingStyle = 1` en le croyant Linear. La doc officielle dit :
1 = **Constant**, 0 = Linear. En jeu, chaque pose restait figée puis sautait
à la clé suivante. C'est corrigé partout, avec un garde-fou dans
`verify_export.py` (`ANGLES_MORTS.md`, §3).

## 2. « L'autre anatomie » : trois critères mesurés sur les coups droits

Mesures au contact, comparées aux 4 M1 du pack pro. Le code est
`perception.pose_impact`, l'état est calculé par `etats.py`. Image de preuve :
`captures/verification/2026-09-24-cerveau-ligne-epaules-pro-vs-nous.png`.

| critère | M1 pro | nous (v4-v6) | verdict |
|---|---|---|---|
| angle bras / ligne des épaules | 18-28° | médiane 55° | **écart** |
| torse détourné de la direction du coup | 72-79° | médiane 44° | **écart** |
| bras libre (1 = tendu vers l'avant avec l'autre) | 0,0-0,3 | 0,89 | **écart** |
| translation d'épaule au contact (bras « décollé ») | 0,58-0,92 stud | 0,96 | pas d'écart |
| inclinaison du torse vers la cible | 2-14° | 12-16° | pas d'écart |

**Lecture.** Chez les pros, le torse pivote presque de profil et le bras qui
frappe **prolonge la ligne des épaules** : une seule droite de l'épaule arrière
jusqu'au poing. Le bras libre est ramené contre le corps. Chez nous, le torse
reste face à la cible, le coup part de la poitrine et **les deux bras sont
tendus vers l'avant**.

Trois sources indépendantes disent la même chose :
- **Motomura (ArcSys)** : « mettre ou non l'épaule dans le coup » change
  entièrement la force lue.
- **Mattesi** : l'extension est une seule droite, du pied arrière au poing.
- **DevForum (Shift4D)** : « tourne le torse encore plus ».

C'est la piste la plus solide pour « un coup simple n'est pas un coup simple ».

**Limite honnête.** L'étalon est un pack de M1 battleground, pas un ultime
manga. Il donne la base « coup qui pèse ». L'anime pousse plus loin (points
3 et 4).

## 3. Règles spécifiques R6 / Roblox (DevForum, doc officielle)

- **Le bras R6 joue l'avant-bras** (fungi3432). On translate le bras entier
  quitte à décoller l'épaule. On le fait déjà au contact ; l'écart éventuel
  est dans la garde et l'armement (garde pro : 1,15 stud).
- **Le « genou » R6 est à la hanche. Exagérer plus que sur un rig articulé**,
  comme en stop-motion Bionicle.
- **Détacher les membres est autorisé pendant les images rapides.** Sur une
  pose tenue en jeu, orienter le membre vers l'épaule pour qu'il ne paraisse
  pas « tombé ». Les sources se contredisent : à arbitrer sur nos captures.
- **Le torse vend la puissance** : il suit le bras avec 1 à 2 images de retard,
  sur un profil de vitesse lent → rapide → lent.
- **M1 battleground : aucune piste sur les jambes.** La course se superpose à
  l'attaque. C'est vérifié dans le pack pro, où les pistes des jambes sont
  vides sur les 4 M1. Ça ne s'applique pas aux skills et ultimes, où tout le
  corps joue.
- **Les skills s'animent sur place, le déplacement se fait par script.**
  On utilise des Animation Events et une LinearVelocity qui décroît, comme
  dans TSB selon les commentateurs.
- **Robotique**, selon les critiques :
  - tout en linéaire ;
  - toutes les parties partent et arrivent en même temps ;
  - changement de direction instantané ;
  - arrêt « mort » en fin de coup ;
  - récupération sans effort ;
  - seuls les bras bougent ;
  - pause en l'air entre deux poses trop espacées.
- **Technique Roblox** :
  - pas de tangentes Bézier : un style d'easing par pose et par joint ;
  - Cubic est déprécié (direction inversée en jeu), CubicV2 le remplace ;
  - Back n'existe pas pour les poses : un dépassement se fait avec une clé ;
  - `Play()` fait un fondu de 0,1 s par défaut ;
  - hitstop : `AdjustSpeed(0)`.

## 4. Règles de l'anime (ArcSys, Cartwright, Mattesi, extraits mesurés)

| règle | chiffre ou source | sur R6 |
|---|---|---|
| Deux poses extrêmes : compression en C, puis extension en droite hors d'équilibre. Le trajet passe en 1 à 2 images. | JJK mesuré ; Cartwright : anticipation → smear → pose principale → retour | possible |
| Épaule dans le coup | Motomura | torse + translation de l'épaule |
| 1 image de dépassement, 1 image de retard, casser le corps | Cartwright GDC 2014 | possible (rotations hors anatomie, translations) |
| Anatomie par pose : poing grossi, jambe allongée | GGXrd, scale d'os par pose | scale impossible ; translation vers la caméra, ou pièce échangée |
| « Ajouter l'angle de vue au modèle, pas à la caméra » | Ishiwatari (GGXrd) | caméra de finisher face au coup, bras amené vers l'objectif |
| Tenir le pic : 1 à 4,6 s mesurés, animé en 2 ou en 3 avec un tremblement | JJK, OPM, MHA | tenue avec vibration de ±0,03 à 0,08 stud [PROPOSITION] |
| Animation limitée : poses tenues 1 à 5 images, sans courbe | GGXrd : « lisser puis sauter des images = 3D qui rame » | Constant ; **à tester en A/B seulement**, le rythme est jugé bon |

## 5. Ce qui entre dans le cerveau

Nouvelles hypothèses dans `hypotheses.json`. Chacune a sa règle d'usage
(`quand` / `contre_indication`) et ses sources.

- **Mesurées** : `ligne_epaules`, `bras_libre_ramene`, `bras_avant_bras`.
  Les états v4 à v6 sont calculés : faux, faux, vrai.
- **Jugées à l'œil** : `compression_extension`, `depassement_1f`,
  `recuperation_effort`, `poses_tenues_limitees`.

**Principe (Milan).** On nourrit, on ne comble pas. Aucune règle ne
s'applique partout. La prochaine étape est un **A/B sur un seul coup**,
jugé par Milan, avant toute généralisation.

## 6. Pistes ouvertes

- **Asset « TSB OFFICIAL Animations » (16072313171).** S'il est authentique,
  c'est la meilleure référence possible : les vraies poses, les easings et la
  densité de clés de TSB. Il faut l'ouvrir dans Studio et l'exporter en
  `.rbxm` (clic droit, puis « Save to File ») ; `corpus.load_rbxm_sequences`
  le lit déjà.
- **Tutos vidéo.** Milan les télécharge avec les sous-titres de son côté
  (liste de 19 vidéos : Roblox d'abord, puis GGXrd, Nakamura, « Why Your
  Punches Lack Energy »). Même traitement que les refs.
