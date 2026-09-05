# Frappe solaire — deux noyaux, combo, coup final à la tête (R6, Roblox)

Prototype isolé, sans lien avec RANK ZERO ni MyAnimeRPG ni les autres
prototypes de `experiments/` (voir CLAUDE.md). Réutilise **telle
quelle** l'infrastructure déjà vérifiée de `r6_hit_combo`/`r6_rock_kick`
(`r6_rig.py`, `anim_engine.py`, `export_model.py`, `export_kfseq.py`,
`resolve_rbxmx.py`, le rig `RigR6.rbxmx`, `vendor/three.min.js`) et le
schéma "combo à deux personnages, mannequin qui encaisse" déjà validé
par `r6_hit_combo` (jab/cross/hook + réaction escaladée).

## Demande

Demande faite dans des termes plus durs que les precedentes — reproche
explicite de qualité et instruction de recherche prealable :

> Améliore toi fais d'autre rechercher tes animation sont tjrs bad game,
> voilà ta prochaine mission
>
> Identité : Compétence cinématique : deux concentrations solaires dans
> les mains → combo rapproché → coup final à la tête.
>
> Animation R6 : Ouverture lente et reconnaissable : les deux bras
> s'écartent, puis se chargent simultanément. Le personnage avance
> ensuite dans un combo court de frappes. Final : montée du bras /
> repositionnement du torse puis énorme frappe descendante vers la
> tête. La dernière frappe doit être beaucoup plus lente et lourde que
> les coups intermédiaires.
>
> Gameplay / hitbox : La séquence principale joue indépendamment d'un
> hit. Si une cible est présente dans les fenêtres de hit, elle reçoit
> les réactions correspondantes. La dernière frappe doit avoir la plus
> grosse fenêtre d'impact et le plus gros knockback.
>
> Idées VFX : Deux petits noyaux solaires distincts au départ, avec
> particules aspirées. Pendant le combo : trails courts sur les bras.
> Final : concentration des deux sources vers le coup, flash blanc,
> grosse explosion solaire et poussière au sol. Le VFX final doit
> clairement dépasser celui de Poing scintillant.
>
> Caméra / mise en scène : Caméra rapprochée dès l'ouverture. Petit
> changement d'angle entre les coups. Très gros cadrage sur le dernier
> coup, impact frame puis shake.

Le grief ("tes animation sont tjrs bad game") porte sur le PROCESSUS,
pas seulement le contenu : la demande explicite de "rechercher" avant
de recommencer a change la methode de travail pour ce prototype (voir
section suivante), pas seulement les chiffres de timing.

## Recherche

Fait AVANT d'écrire la moindre pose, via WebSearch (WebFetch est bloqué
par l'allowlist d'egress reseau de ce sandbox sur tous les articles
sources tentés — seuls les résumés WebSearch ont été exploitables) :

1. **"Poing scintillant" n'existe nulle part dans ce dépôt** (grep
   insensible à la casse sur tout `/home/user/Jeux`) — la seule
   occurrence de "scintillant" est un effet de halo de couronne dans
   `r6_throne_crown/README.md`, sans rapport. C'est donc une référence
   EXTERNE à dépasser : la comparaison concrète la plus proche
   disponible ICI est le hook (finisher) de `r6_hit_combo` et la charge
   de poing de `r6_directional_punch`, dont il fallait dépasser
   l'échelle de VFX (voir section Trajectoire/VFX).
2. **Game feel / juice** (hitstop, screen shake, spacing des
   keyframes) : hitstop = gel bref (~3-5 frames) exactement à l'instant
   d'impact ; le screen shake doit être DIRECTIONNEL (aligné à
   l'angle/la force de l'impact — ici vers le BAS, coup descendant) et
   décroître de façon EXPONENTIELLE rapide, pas une oscillation
   omnidirectionnelle générique ; l'espacement des keyframes communique
   le poids INDÉPENDAMMENT de la durée (espacement large = rapide/léger,
   espacement dense/serré = lourd/lent). "Le juice est un polish
   additif sur quelque chose qui marche déjà, jamais porteur."
3. **Timing combo/finisher** : un combo à 3 temps escalade (coup 1
   rapide/peu d'engagement, coup 2 plus de rotation du corps, coup 3 =
   engagement maximal, arc le plus dramatique, récupération la plus
   lente) ; un poing rapide tient en 3-4 frames (60fps) quand une arme
   lourde a des frames plus lentes en haut de son arc puis accélère
   vers l'impact.
4. **VFX de charge d'énergie ("ki charge")** : particules qui
   CONVERGENT vers le noyau (inward), pas seulement un halo qui grossit
   sur place — vocabulaire visuel absent de tout ce qui existe déjà
   dans ce dépôt (rock_kick/divine_orb n'ont que des bursts sortants).

### Application concrète (decision -> source)

- Le finisher a l'engagement le plus large (bras au-dessus de la tête,
  torse arqué au maximum) ET sa DESCENTE elle-même est étalée sur 11
  frames avec un point intermédiaire volontairement proche de la pose
  de coil (poids/inertie, source 2) — mesuré ~5.5x plus long que le
  lâcher d'un coup de combo (voir `choreography.py`, `calibrate.py`).
- Les 2 coups de combo restent proches du snap 2-frames déjà validé
  dans `r6_hit_combo` ; le coup 2 porte plus de rotation de torse que
  le coup 1 (escalade, source 3).
- Les noyaux solaires convergent visuellement pendant la charge
  (`solar_track.inward_particle_spawn`, source 4) — jamais fait
  ailleurs dans ce dépôt.
- Le shake caméra du finisher est directionnel (vers le bas) à
  décroissance exponentielle (source 2), contrairement au shake
  omnidirectionnel/linéaire déjà existant dans `r6_hit_combo` — voir
  section Lecteur.

## Stratégie de calibration : mesurer, jamais choisir à l'œil

Chaque point de contact (coup 1, coup 2, tête du mannequin au
finisher) est mesuré par cinématique directe (`fist_tip_world`) et
comparé numériquement à la position réelle du mannequin
(`calibrate.py`), jamais posé à l'œil puis laissé tel quel. Plusieurs
poses initiales ont dû être corrigées après mesure :

- Distance d'approche insuffisante (les 2 lunges initiaux ne
  rapprochaient l'attaquant que de ~1 stud du mannequin) — corrigé en
  augmentant `STRIKE1_LUNGE_Z`/`STRIKE2_LUNGE_Z` à une échelle
  comparable à `r6_hit_combo` (jab/cross sur le même rig).
- Le coup 2 (crochet du bras gauche) avait été chorégraphié comme un
  "renversement complet" du torse par symétrie naïve avec le coup 1 —
  mesure : écart > 2.5 stud. Un balayage numérique (torse/bras/lunge)
  a montré que ce coup fonctionne en CONTINUANT la rotation du
  chambrage plutôt qu'en la renversant (écart final < 0.01 stud) —
  corrigé et documenté comme tel dans `choreography.py`, pas forcé
  dans un schéma "renversement" qui ne collait pas à la géométrie
  réelle du rig.
- Le finisher (frappe à 2 bras) avait initialement les bras trop
  descendus à l'instant de contact (déjà passés sous la hauteur de la
  tête, écart Y ~2.4 stud) — corrigé en calant l'angle de bras
  d'impact à l'horizontale (bras ~92-115°, pas complètement redescendu
  à la verticale) et en ajoutant un pas en avant dédié au finisher
  (`FIN_LUNGE_Z`, au-delà du dernier lunge de combo) — écart final
  0.161 stud.
- Un hold-and-snap trop rapide entre la fin du finisher
  (`FIN_FOLLOWTHROUGH_T`) et le retour à une posture détendue causait
  un défaut de placement des pieds (le mouvement de secondary motion
  du torse n'avait pas le temps de "rattraper" son retard avant le
  début de l'oscillation d'attente) — corrigé en allongeant la fenêtre
  de transition, revérifié par `calibrate.py` (0 anomalie restante).

## Chorégraphie

Un seul rig (`attacker_track()`) + un mannequin-cible
(`dummy_reaction()`), synchronisés (voir `choreography.py` pour les
valeurs exactes de pose/timing) :

1. **Garde** (0 → 0.6s) — attente vivante (`_idle_stance_span`, jamais
   un hold plat).
2. **Ouverture + charge** (0.6 → 2.6s) — les deux bras s'écartent
   largement et lentement (0.87s, lisible), puis se replient légèrement
   en coupe vers l'avant (les noyaux naissent ici, voir
   `CORE_SPAWN_RIGHT/LEFT`), puis un vrai hold gelé (0.67s) pendant que
   la charge monte (portée par le VFX, pas par un mouvement de corps).
3. **Combo** (2.6 → 3.77s) — 2 coups rapprochés avec avance (hip-drive
   + pas), hold-and-snap classique (chambrage tenu, lâcher en 2
   frames). Coup 1 : droit franc. Coup 2 : crochet du bras gauche
   (continuation de rotation, pas un renversement — voir calibration).
4. **Finisher** (3.77 → 6.33s) — montée lente et lisible des DEUX bras
   au-dessus de la tête (lecture "hache à deux mains", les deux noyaux
   se rejoignent), vrai hold au sommet (la tension la plus longue du
   set), puis descente étalée sur 11 frames (lente puis accélérée,
   ~5.5x plus longue que le lâcher d'un coup de combo), avec son propre
   pas en avant. Suite : le corps continue sous son élan (over-commit)
   avant un retour à une posture détendue (attente vivante, jamais un
   hold plat en toute fin d'animation).

## Gameplay / hitbox — design intent (pas de moteur de jeu ici)

Ce dépôt n'a pas de moteur de jeu (voir README des prototypes
précédents pour la même discipline) : `choreography.HIT_WINDOWS`
documente l'intention pour un futur câblage —

| Coup | Fenêtre | Frames | Knockback |
|---|---|---|---|
| combo_1 | [STRIKE1_T-2f .. STRIKE1_T+3f] | 5 | léger |
| combo_2 | [STRIKE2_T-2f .. STRIKE2_T+3f] | 5 | modéré |
| finisher | [FIN_STRIKE_T-3f .. FIN_STRIKE_T+8f] | 11 | maximal |

Conformément à la demande ("la dernière frappe doit avoir la plus
grosse fenêtre d'impact et le plus gros knockback") : la fenêtre du
finisher est plus de 2x plus large que chaque coup de combo. La
séquence de l'attaquant joue intégralement que le mannequin soit
présent ou non (mêmes keyframes, aucune dépendance) ; `dummy_reaction()`
est une piste séparée, purement illustrative.

Le mannequin encaisse le coup 1 (flinch léger), le coup 2 (vacille plus
fort, escalade), puis le finisher — qui se lit DIFFÉREMMENT des deux
premiers : un coup descendant sur la tête ÉCRASE la cible vers le bas
(torse/tête pliés en avant, racine Y qui chute, genoux qui cèdent),
jamais un simple recul horizontal, avant le plus gros knockback
(déplacement Z) du set une fois la cible à terre.

## Trajectoire et VFX des noyaux solaires

Contrairement à `r6_rock_kick`/`r6_divine_orb`, il n'y a pas de
projectile ici (compétence de corps-à-corps) : `solar_track.py` ne
scripte QUE ce qui n'est pas une simple attache à un os —

- Les 2 noyaux individuels sont attachés aux mains tant qu'ils sont
  séparés (`core_radius(t)` donne leur rayon, croissant pendant la
  charge puis stable pendant tout le combo).
- Particules aspirées pendant la charge (`inward_particle_spawn`) —
  naissent loin de chaque main, convergent vers elle, jamais l'inverse.
- Fusion des deux noyaux en un seul pendant la descente du finisher
  (`merged_core_position(t)`) — interpole entre le point mesuré où les
  deux poings se rejoignent (`CORE_MERGE_POINT`) et le point de contact
  final mesuré (`FIN_CONTACT_POINT`), avec la MÊME courbure temporelle
  que la descente du corps (jamais un noyau "en avance" ou "en retard"
  sur les mains qui le portent) — vérifié par `solar_track.py`
  (coïncidence exacte aux deux bornes, < 0.001 stud d'écart).
- Impact final : flash blanc bref, explosion solaire (rayon jusqu'à
  `IMPACT_MAX_RADIUS=9.0`, délibérément plus grand que tout burst
  existant dans ce dépôt), onde de choc, poussière au sol.

## Caméra

Rapprochée dès l'ouverture (contrairement aux prototypes précédents
qui démarrent large/idle), petit changement d'angle entre les 2 coups
du combo, cadrage très serré + hitstop + shake sur le finisher — shake
DIRECTIONNEL (vers le bas, aligné à la frappe descendante) à
décroissance EXPONENTIELLE, amélioration délibérée par rapport au
shake omnidirectionnel/linéaire déjà existant dans `r6_hit_combo` (voir
section Recherche).

## Lecteur

`experiments/r6_solar_smite/output/solar_smite_viewer_final.html` —
Three.js, deux rigs (attaquant + mannequin), généré par
`dump_scene_data.py` + `build_viewer.py` à partir de `choreography.py`
et `solar_track.py` (aucune valeur improvisée côté lecteur : poses,
trajectoire du noyau fusionné et rayons viennent des scripts déjà
vérifiés). Hitstop cumulatif escaladant sur les 3 impacts, shake
omnidirectionnel classique sur les 2 coups de combo et shake
DIRECTIONNEL (vers le bas) à décroissance EXPONENTIELLE dédié au
finisher (amélioration délibérée par rapport au shake
omnidirectionnel/linéaire déjà existant dans `r6_hit_combo` — voir
Recherche). Caméra serrée dès `t=0`, changement d'angle progressif
entre les 2 coups puis cadrage très serré sur la fusion/l'impact.

Deux défauts trouvés et corrigés pendant la construction du lecteur
(par l'agent qui l'a bâti, vérifiés indépendamment par moi avant/après
correction, jamais pris au mot) :

- **`OPEN_ARMS` avait les signes inversés** — la rotation C0 du joint
  d'épaule permute les axes ; `rz` négatif sur le bras droit le
  faisait TRAVERSER vers le centre/la gauche au lieu de l'écarter sur
  le côté (mesuré : poing droit à X=-0.42, à GAUCHE du centre, à
  `OPEN_T`). Corrigé dans `choreography.py` (`Right Arm rz=+82, Left
  Arm rz=-82`) — revérifié par calcul (poing droit X=+2.56, gauche
  X=-2.56, écartement symétrique) ET par un rendu diagnostic vue de
  dessus avant d'accepter la capture corrigée.
- **Le noyau fusionné restait visible à pleine intensité pendant le
  hitstop du finisher**, noyant le starburst d'impact (`drawFinisherBurst`)
  dans son propre halo — pas un problème d'opacité du burst comme
  supposé au départ (testé en A/B, aucun effet), la vraie cause était
  le noyau qui ne s'éteignait jamais. Corrigé par un fondu du noyau
  fusionné (matériau + lumière + halo 2D) sur les 0.25s réelles suivant
  l'impact.

### Point de vigilance (disclosed, pas corrigé)

Pendant les 2 coups de combo (captures 03/04), le mannequin-cible
n'est **pas visible dans le cadre** — la caméra reste majoritairement
centrée sur l'attaquant pendant le combo (`tw` ≈ 0.28-0.42 dans les
repères caméra, ne bascule franchement vers la cible qu'à l'approche du
finisher, `tw` ≈ 0.55-0.78). C'est un choix de mise en scène délibéré
(cohérent avec "caméra rapprochée dès l'ouverture" — priorité à la
performance de l'attaquant, pas un plan large des deux personnages
comme `r6_hit_combo`), mais ça a un coût de lisibilité réel : on ne
VOIT pas le mannequin encaisser les 2 premiers coups, seulement le
finisher (capture 08). Non corrigé pour cette itération — signalé
plutôt que caché.

## Vérification (captures)

9 captures committées dans `captures/verification/` (même convention
que les prototypes précédents), toutes vérifiées par moi-même en
ouvrant chaque image (jamais un rapport d'agent pris au mot) :

- `2026-09-05-solar-smite-00-garde.png` — attente vivante, garde initiale.
- `2026-09-05-solar-smite-01-ouverture.png` — bras écartés (après
  correction du signe, voir ci-dessus) ; ambigu à cet angle de caméra
  précis (le T-pose ne se lit pas franchement de face), mais confirmé
  correct par calcul et par un rendu diagnostic vue de dessus.
- `2026-09-05-solar-smite-02-charge-particules.png` — noyau visible
  dans la main, quelques particules aspirées visibles autour.
- `2026-09-05-solar-smite-03-combo1-impact.png` / `-04-combo2-impact.png`
  — capturées pile à l'instant du flash d'impact (image délavée/
  surexposée) : attendu (voir CLAUDE.md/note plus haut sur l'écueil
  déjà rencontré 2 fois dans ce dépôt — flash au pic, pas un bug de
  rendu), confirmé par l'agent via un instant décalé de +0.15s hors
  livraison (éclats/mannequin qui flinche visibles).
- `2026-09-05-solar-smite-05-finisher-montee.png` — les deux noyaux,
  grossis et rapprochés au-dessus de la tête, prêts à fusionner.
- `2026-09-05-solar-smite-06-finisher-impact-flash.png` — flash blanc
  plein cadre à `FIN_STRIKE_T` (attendu, même écueil que ci-dessus).
- `2026-09-05-solar-smite-07-finisher-impact-apres.png` — +0.15s après
  le flash : grosse explosion solaire dorée avec un starburst blanc net
  et visible en son centre (après la correction du fondu du noyau
  fusionné, voir ci-dessus) — le plus gros VFX du dépôt à ce jour.
- `2026-09-05-solar-smite-08-mannequin-ecrase.png` — mannequin écrasé/
  affalé au sol après le finisher, marque de sol persistante visible.
