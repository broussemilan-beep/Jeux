# Chantier 4, A3 : ultimes et combo au mur de TSB (étude d'apprenti)

Source unique : `/root/.claude/uploads/4796ac9e-8e41-51f7-91c4-7b92a6a187d0/b64ecce0-tsb_anim.rbxm`,
lu en entier (clés, poses, poids, easing, marqueurs). Quatre animations :
**Ultimate1**, **Ultimate2**, **WallComboPlayer**, **WallComboVictim**.

Ce sont des apprentissages situés (« ici, l'animateur fait X parce que Y »),
pas des règles. Chaque point porte sa preuve et son statut :
- **vu** : je l'ai regardé sur une planche ;
- **mesuré** : sorti d'un outil ;
- **lu** : texte présent dans le fichier (noms de marqueurs, easing, noms) ;
- **déduit** : mon interprétation.

Images produites (scratchpad, jamais dans le dépôt) :
`/tmp/claude-0/-home-user-Jeux/4796ac9e-8e41-51f7-91c4-7b92a6a187d0/scratchpad/c4/frames/A3_tsb_ultimes_mur/`
- Ultimate1 :
  - `U1_global.png` (planche_cles, 40 clés sur 129) ;
  - `U1_ech_{0,150,300,450}.png` : tout U1 échantillonné toutes les 5 images, 2 vues ;
  - `U1_courbes.png` : courbes image par image ;
  - `U1_actes_face.png` : 18 poses vues du côté de la cible.
- Ultimate2 : `U2_ech.png` (toutes les 3 images), `U2_courbes.png`.
- WallComboPlayer :
  - `WCP_ech_0.png`, `WCP_ech_200.png` (toutes les 4 images) ;
  - `WCP_cles_0.png`, `WCP_cles_177.png` (chaque clé) ;
  - `WallComboPlayer_courbes.png`.
- WallComboVictim : `WCV_ech.png` (toutes les 6 images), `WallComboVictim_courbes.png`.
- Duo : `duo_fit.png` (essai de placement relatif, non concluant, voir §3.4).

Scripts (scratchpad, `c4/work_A3/`) :
- `dump.py` : clés, poids, EasingStyle, marqueurs → `dump.json` ;
- `table.py` : quelles parts sont posées à chaque clé ;
- `deltas.py` : de combien chaque part change d'une de SES clés à la suivante ;
- `courbes.py`, `tranche.py`, `vitalite.py` (vitesse angulaire par part et par phase) ;
- `duo.py`, `duo_rendu.py`.

Rappel lancé avant de commencer : `rappel.py "pose tenue"`, `"Ultimate1"`,
`"combo au mur victime"`, `"tenir la charge"` (court). Lus aussi :
`corpus/ETUDE_TSB.md`, `corpus/poses/sources/pro_tsb_ultimes.json` (entrées U1
et U2), CARNET 1.10 / 2.1c, `fiches/COUP_CHARGE.md` §7.

---

## 0. Trois découvertes sur le FICHIER lui-même (avant l'animation)

**0.1 Il y a des MARQUEURS nommés (KeyframeMarker), et ils disent ce que le code du jeu fait.** *lu*
(`dump.py`, propriété KeyframeMarker.Name) :

| anim | marqueurs (image à 60 i/s) |
|---|---|
| Ultimate1 | ParticleActivate f16, TweenStuff f281, StartLoop f495, AwakenFinale f497,2, End f599 |
| WallComboPlayer | hit1 f9, hit2 f176, hit3 f352, end f400 |
| WallComboVictim | aucun (le jeu la pilote depuis celle du joueur, *déduit*) |
| Ultimate2 | aucun |

Pour comparaison, hors de mon lot mais dans le même fichier (*lu*) :
- M1-M3 : hitreg f8-10, end f25-28 ;
- Collateral Ruin : SpeedLinesStart, SpinnerSmokeEffect, StartHitbox, EndHitbox, DownMesh ;
- Stoic Bomb : ChargingSound, Voiceline, **BeginSlowing**, HitboxExplosion?, FinalBoarExplosion.

Ce que ça m'apprend :
- L'animateur TSB ne livre pas qu'un mouvement : il livre aussi le **minutage des événements** (VFX, son, hitbox, ralenti, boucle).
- Le nom « AwakenFinale » dit qu'**Ultimate1 est une animation d'ÉVEIL** (le passage en mode ultime), pas une attaque (*lu* pour le nom, *déduit* pour le sens).
- Le modèle racine s'appelle « KJ » / « KJAnims » (*lu*). C'est donc le personnage KJ, ce qui colle avec le catalogue : ce n'est pas Saitama.

**0.2 Deux méthodes de fabrication coexistent dans le même fichier.** *mesuré* (`table.py`)
- **Ultimate1** : 134 clés en 10 s, posées **part par part**, à des instants différents pour chaque membre. Écarts de 1 à 14 images. Easing 100 % Linear (*lu*).
- **Ultimate2** : 174 clés = **une clé par image**, les 6 parts à chaque fois. C'est une cuisson.
  - Les courbes sont lisses et sinusoïdales, avec des plateaux (hanche tenue à 2,91 entre f36-48 et f76-84, `U2_courbes.png`).
  - Ça ressemble à des courbes de Bézier cuites depuis un autre outil, pas à des clés Linear (*déduit*).
- **WallComboVictim** est HYBRIDE (ETUDE_TSB disait seulement « cuite ») :
  - f0-146 : clés à la main, toutes les 2-6 images, part par part ;
  - f146-353 : une clé par image.
  - Dans la partie cuite, un motif : le torse est posé à chaque image, les jambes les images paires, bras + tête les images impaires (f203-352).
- **WallComboPlayer** : clés à la main, toutes les 3-10 images, plus une série de **67 poses en EasingStyle Constant** (f272-352), toutes les parts (*lu*).

**0.3 Nos outils ignorent l'easing Constant : ils dessinent faux cette partie.** *mesuré*
- `corpus.resample_linear` (docstring, ligne 86) interpole tout en Linear. `planche_cles`, et mes `courbes`, `tranche` et `vitalite`, s'en servent.
- Dans Roblox, une pose Constant se tient jusqu'à la clé suivante, puis saute. Je le sais par la doc (connaissance, pas vérifié dans Studio ici).
- Donc entre f272 et f352, WallComboPlayer est en réalité **une suite de poses figées qui claquent**. Nos courbes y montrent des vitesses régulières de 4 à 40 studs/s, et c'est faux.
- Les poses dessinées aux clés restent exactes (`WCP_cles_177.png`). Entre les clés, non.
- À corriger dans l'outil. Je ne l'ai pas fait : le dépôt est en lecture seule.

---

## 1. Ultimate1 : comment un animateur TSB construit une animation LONGUE (10 s)

### 1.1 Les actes (vu + mesuré)

Sources : `U1_ech_*.png`, `U1_courbes.png`, `U1_actes_face.png`, `U1_courbes.json`.

| # | images | ce qui se passe | preuve |
|---|---|---|---|
| A | f0-16 | **Secousse d'ouverture.** Il part penché en avant (+10°, hanche 2,68) et se redresse d'un coup : hanche 2,86 en 13 i, tête jetée de côté et en arrière (i5-i10). Le haut de la tête file à 21 studs/s à f12. **ParticleActivate à f16**, juste à la fin de la secousse. | courbes ; clés T toutes les 2-4 i (f4, 7, 11, 13) |
| B | f17-190 | **Recueillement lent** (près de 3 s). Debout, bras pendants. La tête, qui regardait en haut (el +12,7 à f30), redescend à 0 vers f140. Le buste passe lentement de -5° à +6° de penché et le corps s'enfonce de 2,86 à 2,78. | valeurs f20-190 |
| C | f190-290 | **Le bras droit se lève devant (f190-256), puis se ramène à la hanche (f258-290).** Deux poussées de vitesse du poing (5-6 studs/s vers f205-215 et f245-255). **TweenStuff à f281**, 9 images avant que le poing arrive à la hanche. | courbes ; pro_tsb_ultimes |
| D | f290-432 | **Tenue armée** (142 i = 2,4 s). Poing à la hanche, buste tourné de -18°. Ce qui vit pendant cette tenue est détaillé au §1.3. | |
| E | f432-496 | **Déploiement** (62 i). Rotation du buste de -18 à +68°, pas en arrière du pied gauche, creux de hanche, bras droit tendu devant. **StartLoop f495, AwakenFinale f497** : les VFX tombent quand la pose est ATTEINTE, pas au départ. | §1.4 |
| F | f496-556 | **Tenue finale** (≈1 s). Pose de présentation : de profil, bras droit tendu vers la cible (en raccourci vu de la cible, `U1_actes_face` f496-540), bras gauche rejeté en arrière. | |
| G | f556-601 | **Retour au neutre** (45 i). Hanche remontée à 3,0, bras qui retombent. **End f599.** | |

Rythme d'ensemble, mesuré en vitesse angulaire moyenne (`vitalite.py`) :

| | torse | tête | bras | jambes |
|---|---|---|---|---|
| tenues B, D, F | 10-13°/s | 16-21°/s | 6-26°/s | |
| mouvements C, E, G | 20-110°/s | | 130-200°/s | |

Les tenues ne sont pas figées : elles vont **environ 8 à 10 fois plus lentement** que les mouvements.
**Lecture** (*déduit*) : une longue anim TSB alterne ainsi, en gros par tiers :
- une secousse brève ;
- une longue plage lente ;
- un geste ;
- une longue plage tendue ;
- un déploiement d'une seconde ;
- une tenue ;
- une sortie.

Les événements (particules, tween, boucle) sont posés sur les **arrivées de pose**.

### 1.2 Où l'animateur place le rig, et dans quel ordre (mesuré par `table.py` + `deltas.py`, lu pour l'easing)

- **Torse et deux jambes posés ENSEMBLE** presque à chaque clé de torse, tout le long de U1.
  - Explication, liée au rig R6 : les jambes pendent du torse (hanches sur le Torso). Si on tourne ou baisse le torse sans reposer les jambes, les pieds bougent.
  - L'animateur repose donc les jambes à chaque clé de torse, pour garder les pieds au sol (*déduit*).
  - Les pieds bougent quand même un peu : bout du pied entre -0,24 et +0,1 stud pendant les tenues (*mesuré*). Il tolère ce petit flottement.
- **Bras et tête posés À PART**, à leurs propres instants, décalés du torse :
  - exemple dans la tenue D : T à 296/302/314/323/335/345, BG à 306/322/333/343, BD à 314/345/356/361, H à 314/345/356/361 ;
  - la tête a ses clés espacées de 5 à 31 i ; les bras, de 3 à 35 i.
  - C'est la méthode « par couches » : le corps d'abord, puis chaque membre vit sur son propre rythme. Personne n'a posé une pose complète toutes les N images (*déduit*).
- **Le poing armé est placé par TRANSLATION du bras, pas seulement par rotation** :
  - les clés BD de f221-267 déplacent le bras de 0,13 à 0,40 stud (*mesuré*) ;
  - l'étude précédente l'avait vu : pivot d'épaule reculé de 0,29 à 0,66 ;
  - en R6, faire glisser l'épaule le long du flanc est un vrai outil de pose.
- **La racine (HumanoidRootPart) n'est jamais animée**, ni ici ni dans les 3 autres (poids 0 partout, *lu*).
  - Tout déplacement passe par la translation du Torso : recul de 1,5 stud en E, pas de côté.
  - Le personnage ne se déplace pas vraiment dans le monde ; le jeu gère la racine (*déduit*).
- **Densité de clés = densité d'action** (*mesuré*) :
  - clés de torse toutes les 10-14 i dans les tenues B et D ;
  - toutes les 4-8 i dans le déploiement E ;
  - toutes les 2-4 i dans la secousse A.

### 1.3 Tenir une pose de charge VIVANTE : ce que fait TSB dans la tenue D (f290-432)

C'est le cœur de l'angle demandé. Tout ce qui suit est *mesuré* (`U1_courbes.json`, `deltas.py`), sauf mention contraire.

1. **Aucune clé n'est une copie.**
   - Le torse est reposé toutes les 4 à 12 images, avec des écarts de 0,3 à 8,2° d'une clé à l'autre, jamais 0.
   - La tenue est faite de petites poses toutes différentes, reliées en Linear : une « tenue mouvante ».
2. **Plusieurs dérives lentes, chacune sur son propre rythme** (on ne voit pas un seul mouvement, mais plusieurs qui se superposent) :
   - buste qui se penche lentement en avant : +0,7° → +4,4° (f290-356, ~66 i), puis revient ;
   - tête qui se relève : el -10 → -4 (f290-314), puis redescend à -12 en fin de tenue (f410-434), juste avant le déploiement ;
   - poing armé qui monte et descend de 7 à 16° (el du bras -11 → -4 → -11 → -6 → -21 à f434), donc qui DESCEND juste avant de partir ;
   - bras libre (gauche), pendant, qui se balance lentement : az -63 → -36 → -51 → -37 → -80 → -42 sur ~140 i, soit 2 oscillations environ ;
   - « respiration » de la hanche à peine perceptible : 2,738-2,767 (±0,015 stud).
3. **Une PULSATION au milieu de la tenue (f356-362).**
   - Le buste se tord de 7,6° en 5 images (clé T f361 : 8,2°), puis revient en ~30 images (f362-392).
   - Attaque rapide, retour lent : comme un spasme de puissance, un « battement » de la charge (*déduit* pour le sens).
   - La tête amplifie ce spasme : elle tourne de 15° dans le monde quand le torse en tourne 7 (*mesuré*, lacet monde T -18 → -25, H -5 → -20).
   - Aucun marqueur à cet endroit : si un effet y est synchronisé, c'est par le code, et je ne peux pas le savoir.
4. **Le poing reste « chargé » par sa position, pas par un tremblement.**
   - Le poing D bouge à moins de 1,2 studs/s pendant la tenue (déjà mesuré dans pro_tsb_ultimes).
   - Il n'y a pas de vibration haute fréquence dans U1.
5. **Fin de tenue = préparation.**
   - Sur les ~20 dernières images (f410-434), trois choses se regroupent : la tête baisse (-4 → -12), le poing descend (el -8 → -21), le bras libre part déjà (f436, v_LA 3 studs/s).
   - Le déploiement commence DANS la fin de la tenue : la tenue n'est pas « coupée » par le geste (*déduit*).

**Ce que ça m'apprend sur « tenir une pose de charge »** (apprentissage, pas règle) :
- Ici, l'animateur ne fige rien. Il superpose 4 ou 5 dérives lentes de périodes différentes : buste, tête, poing, bras libre, souffle.
- Il ajoute UNE pulsation nette (attaque en 5 i, retour en 30 i) vers le milieu, puis referme la tenue en ramassant le corps juste avant de partir.
- Les amplitudes sont petites en degrés (1 à 16°), mais comme elles ne sont jamais synchrones, l'œil ne voit jamais deux fois la même image.
- La tête est la part la plus vivante de toutes : 20,6°/s en moyenne, contre 13,4 pour le torse (*mesuré*, `vitalite.py`).

### 1.4 Le déploiement f432-496 : l'ordre de départ des parts (mesuré, `U1_courbes.json` toutes les 3 images)

1. **Le bras LIBRE (gauche) part le premier** : f436, v_LA 3 studs/s. Il monte de el -80 à +32 entre f436 et f475 et reste le plus rapide de la phase : 11-12 studs/s entre f457 et f481, 202°/s en moyenne.
2. **Le buste** accélère ensuite. Lacet :

   | image | f448 | f463 | f475 | f487 | f496 |
   |---|---|---|---|---|---|
   | lacet | -12 | +11 | +39 | +59 | +68 |

   Il ralentit en arrivant (+3°/3 i à la fin) : amorti vers la pose finale.
3. **Creux de hanche au milieu** : 2,79 → **2,48 à f469** → 2,63. Il tombe pendant le **pas en arrière du pied gauche**, qui se lève de 0,32 stud entre f472 et f484. Le poids tombe pendant le pas.
4. **Le poing droit, celui qui se tend, arrive EN DERNIER.**
   - Il reste vers 2-5 studs/s jusqu'à f487, puis file à **12 studs/s entre f490 et f496**.
   - En 6 images, el du bras -26 → +13 : il monte à hauteur d'épaule.
5. **La tête reste en partie sur la cible** : le torse tourne de 86° dans le monde, la tête de 28 seulement. Elle contre-tourne pour garder le regard.

**Lecture** (*déduit*) :
- C'est une chaîne. Le bras libre ouvre (il donne l'élan et le contrepoids), puis le bassin et le buste tournent avec la chute du poids dans le pas, puis le bras tendu arrive en coup de fouet sur les 6 dernières images, tête sur la cible.
- Même dans un geste lent de mise en scène, le membre « héros » arrive en dernier et vite.

### 1.5 Ce que je corrige dans le cerveau

ETUDE_TSB §4 : « Ultimate1 : 10 s presque debout, un bras qui bouge ; bascule 7°. »
- **Presque debout** : exact (hanche 2,48-2,86, penché -10 à +14°).
- **Un bras qui bouge** : **faux**.
  - Les deux bras travaillent : le libre mène le déploiement.
  - Le buste tourne de 86°, le corps recule de 1,5 stud, il y a un pas, et la tête vit en permanence.
  - « Sobre en inclinaison », oui ; « sobre » tout court, non.
- **Tenues de 58, 35 et 21 i** : ces tenues ont été mesurées avec un seuil (extrémités à moins de 4 studs/s pendant au moins 6 i) et avec l'ancien lecteur (bug des poses de poids 0, signalé dans pro_tsb_ultimes).
  - Ma lecture : il y a trois grandes tenues (B ≈ 170 i, D = 142 i, F ≈ 60 i), mais ce sont des **tenues mouvantes**.
  - Le seuil de vitesse les découpe en morceaux et fait croire à des tenues courtes.

---

## 2. Ultimate2 : marche lente, revers, tenue (2,9 s, cuite)

L'étude précédente (pro_tsb_ultimes) n'avait lu que le revers. **Vu** sur `U2_ech.png` et *mesuré* sur `U2_courbes` :

### 2.1 Les 93 premières images sont une MARCHE SUR PLACE, lente et lourde

- Trois pas, qui se voient aux pics de hauteur des pieds :
  - pied D 0,21 à f12 ;
  - pied G 0,43 à f47 ;
  - pied D 0,43 à f83.

  Soit un pas toutes les 35 images environ (0,6 s).
- Le torse ne se déplace pas : translation avant ≈ 0 jusqu'à f93, 0,004 stud d'amplitude. Si le personnage avance, c'est le jeu qui déplace la racine (*déduit*).
- La hanche descend de 3,00 à 2,91 **pendant que la jambe se lève** et remonte quand le pied se pose (maxima f0, 22, 56, 90).
  - C'est l'inverse d'une marche « légère » (qui monte au passage).
  - Je le lis comme une marche pesante, menaçante (*déduit*).
- Le bras gauche se lève progressivement devant, en travers (el/torse, *mesuré*) :

  | image | f0 | f20 | f40 | f60 | f70 |
  |---|---|---|---|---|---|
  | el | -90 | -55 | -23 | +4 | +8 |

  Son az passe de -3 à +49 entre f0 et f100 : il croise vers l'autre côté. C'est l'armé du revers, construit PENDANT la marche.
  - L'armé n'est pas une pose à part : il se monte en marchant (*vu* i30-i90).

### 2.2 Le revers f93-120 : une chaîne cinétique presque de manuel

*Mesuré*, degrés par image, `U2` f90-124 :

| image | torse | bras G / torse |
|---|---|---|
| f101 | **pic à 4,2** | |
| f108 | ralentit à 2,0 | **pic à 19,2** |
| f114-115 | **re-accélère à 6,4** | 1,4-2,3 (le bras s'arrête) |

- Le torse mène, **cède la main au bras** (il ralentit pendant que le bras accélère), puis **reprend** après le passage du bras.
- La 2e vague du torse est plus rapide que la 1re (6,4 contre 4,2°/i). Le corps est entraîné par le bras, ou il « finit » le geste (*déduit*).
- Le bras accélère sur 15 images (1 → 46 studs/s, f94-109) et décélère sur 10 (f110-120) : ce n'est PAS un claquement en 1 image. C'est une vitesse en cloche, lissée par la cuisson.
- La hanche plonge de 2,99 à 2,75 (f93-107). Le torse avance de 0,5 stud puis revient (f96-114) : fente et retour.
- **La tête reste VERROUILLÉE sur la cible.** Pendant que le torse tourne de 84° (-16 → +68 dans le monde), la tête ne bouge que de -1 à +5° dans le monde (*mesuré*). La tête contre-tourne exactement le buste.

### 2.3 Tenue finale f120-173 (53 i)

- Tout se pose en douceur : torse à ~1°/i à f120, puis ~0,9°/i.
- Vitesse moyenne 19-27°/s selon la part : une tenue où l'on se pose, pas une tenue figée.

### 2.4 Leçon de méthode (déduit)

- U2 (cuite, lisse) et U1 (clés éparses en Linear) sont probablement deux méthodes ou deux outils.
- Les deux tiennent la tête sur la cible et montent l'armé à l'intérieur d'un autre mouvement.
- Le « style TSB » n'est donc pas une interpolation : c'est **une façon d'ordonner les parts**.

---

## 3. WallComboPlayer + WallComboVictim : deux rigs qui dialoguent

### 3.1 Le joueur (6,8 s), en actes (vu + mesuré)

| images | action | preuves |
|---|---|---|
| f0-8 | **Volte-face explosive** : le torse tourne de 105° en 5 i puis de 93° en 3 i (clés T f5, f8), avec un bond vers l'avant de 1,9 stud. Poing D à 71 studs/s à f8. **hit1 f9.** | `deltas` ; courbes |
| f10-35 | Tenue de réception. Aux clés f27-33 (une par image), les écarts CROISSENT, 0,1 → 1,1° : **une accélération posée image par image à la main** (ou cuite), pour sortir en douceur de la tenue. | `deltas` |
| f35-160 | Recul de ~6 studs (translation avant du torse de +1,9 à -4,0) en marchant, bras bas. **f113-156 : seuls torse + jambes sont posés**, les bras interpolent sur 43 images. | table ; courbes |
| f156-176 | Pied D levé à 1,5 stud (f165), puis **tombée du corps** : hanche 2,92 → 2,34 (f160-172), buste penché de -15 à +34°. Les deux bras filent ensemble à 21-29 studs/s (f170-177) : une prise ou un coup à deux mains vers le bas (*déduit*). **hit2 f176.** | courbes f160-180 |
| f200-245 | **Saut** (hanche 3,95 vers f228, pied G à 2,24), les deux bras levés au-dessus de la tête (i223-238 sur `WCP_cles_177`), puis réception basse, bras devant. | vu ; courbes |
| f272-352 | **12 poses en Constant** (*lu*), tenues respectivement 5, 6, 8, 10, 8, 10, 8, 9, 6, 5, 5 puis 4 i : bras en croix, puis montée de jambe pour un **coup de pied tournant** (i336-347 : jambe à l'horizontale puis haute). **hit3 f352.** | table (Const) ; `WCP_cles_177` |
| f352-356 | À la clé f352, tête et deux bras ont un écart **nul** avec f347 (0,0°), alors que le torse (+27,7°) et la jambe de frappe (+22°) changent : **le haut du corps est figé et porté par le torse pendant que la jambe frappe**. Puis à f356 le bras D fait **111,7° en 4 i** (78 studs/s en Linear). | `deltas` 270-360 |
| f356-400 | Réception accroupie basse (hanche 2,25), tenue. **end f400.** Retour au neutre à f410. | courbes |

**Le rythme des poses Constant raccourcit vers le coup** : 10, 8, 10, 8, 9, 6, 5, 5, 4 images.
- C'est une accélération faite UNIQUEMENT de durées de tenue (*mesuré* sur les temps de clés).
- Les poses sont en « claquement » : sautes de 15-42° sur le torse et jusqu'à 56° / 1,2 stud sur un bras, en 1 image (*mesuré*, écarts entre clés Constant).
- Visuellement, c'est de l'animation limitée à l'anime : des poses fortes tenues, sans intervalles (*déduit*).

### 3.2 La victime (6 s) : comment un pro anime QUELQU'UN QUI SUBIT

| images | action | preuves |
|---|---|---|
| f0-8 | **Figée.** Clé f8 identique à f0 (0,0° sur toutes les parts). Moins de 2°/s. | `deltas` ; `vitalite` |
| f9 | **« Pop » en 1 image** (clé f8 → f9) : torse 14° + 1,16 stud, bras 37-48°, jambes 39-42°. Tout le corps bouge d'un coup, **à l'image exacte du marqueur hit1 du joueur** (poing joueur au plus vite à f8, marqueur f9). | `deltas` ; `duo.py` |
| f11 | 2 images après, les **bras** font leur plus grand écart (BD 104°, BG 61°) : les membres continuent après le torse (traîne), bras jetés en croix. | `deltas` ; `WCV_ech` i12-i36 |
| f9-40 | **Soulevée** : hanche jusqu'à 3,75, pieds à +0,6 du sol, repoussée de 2 studs en arrière (translation du torse), dans le mur ? (*déduit*). | courbes |
| f40-55 | **Écrasée** : hanche 2,06 à f52, corps plié en avant. | courbes ; vu |
| f60-174 | **Affaissée**, pliée en avant, tête basse, qui se tasse lentement. Juste avant hit2, les vitesses **décroissent jusqu'à 0,03 studs/s (f174)** : elle se pose dans l'immobilité juste avant le coup suivant. | courbes f168-174 |
| f175-183 | **Réaction au hit2 en chaîne** : bras d'abord (f175, 39 studs/s), **tête 5 images plus tard** (f180, 36 studs/s), puis le corps entier monte (hanche 2,77 → 3,55 dès f180). | courbes V f168-183 |
| f190-350 | **Tenue en l'air, pliée à ~50°** (penché 38-59°, pieds à 0,6-0,78 du sol) : maintenue ou suspendue par le joueur (*déduit*). Le torse ne bouge presque pas (8°/s) mais **tête, bras et jambes tremblent** (80-90°/s, bruit haute fréquence ~0,8° d'écart-type sur tête et bras). Partie cuite une clé par image, en motif alterné. | `vitalite` ; mesure de bruit |
| f351-353 | **À nouveau figée** (0-1 studs/s). | duo.py |
| f354 | **Réaction au hit3** : 73 studs/s, lacet 85°, pied jusqu'à 3,3 : éjectée. Fin à f358. | courbes |

### 3.3 Qui mène, qui répond, avec quel retard (mesuré, sans connaître le placement relatif)

| coup | joueur | victime | retard |
|---|---|---|---|
| hit1 | vitesse max à f8, marqueur f9 | pop à f9 | **0 à 1 image** après le pic du joueur |
| hit2 | bras à 29 studs/s dès f170, marqueur f176 | bras à f175 | **5 images** après le départ des bras du joueur, **1 image avant** le marqueur |
| hit3 | pose claquée f352 (Constant), bras à 78 studs/s f353 | f354 | **1-2 images** |

Ce qu'on voit à chaque coup :
- **La victime « attend » en immobilité parfaite** juste avant (f0-8, f174, f351-353). Son calme rend le coup lisible.
- Sa réaction commence **au point de contact**, puis **la tête suit plusieurs images après** (hit2 : 5 i), puis **le corps se déplace**. C'est la même chaîne en retard que chez l'attaquant, à l'envers.
- La victime ne réagit jamais « en avance » d'un geste préparatoire : aucune anticipation chez celui qui subit (*mesuré* : vitesses ~0 jusqu'à l'image du coup).

### 3.4 Où chacun est placé : je n'ai PAS pu le déterminer

- Les deux animations ont leur racine à poids 0 (*lu*). Le fichier ne contient donc pas la position de la victime par rapport au joueur : c'est le code du jeu qui la place.
- J'ai cherché par grille un placement (x, z, lacet de la victime) qui mette une extrémité du joueur sur le torse ou la tête de la victime aux trois coups (`duo.py`).
  - Meilleur résultat : lacet ~165°, x -1,75, z +1,5.
  - hit1 et hit3 tombent à 0,3-0,7 stud d'une extrémité, mais **hit2 reste à 2,4 studs**.
  - Le rendu `duo_fit.png` montre les corps qui s'interpénètrent.
- **Non concluant.** Probablement, le jeu repositionne la victime entre les phases (*déduit*, non vérifiable ici).
- Ce qui est mesuré sans ambiguïté, chacun dans son propre repère :
  - le joueur translate son torse de +1,9 à -4 studs ;
  - la victime translate le sien jusqu'à 2 studs en arrière et 0,75 stud en hauteur.
  - Tout le « transport » des corps passe par la translation du Torso dans l'anim.

---

## 4. Grands enseignements (transversaux), avec ce qu'ils changent pour moi

1. **Un rig R6 se pose en couches, pas en poses complètes.** *mesuré (table U1, victime f0-146)*
   - Torse + jambes ensemble (pour garder les pieds), puis bras et tête sur leurs propres instants, décalés de 2 à 30 images.
   - C'est ce décalage qui fabrique le chevauchement, sans outil de chevauchement.
2. **Une tenue longue est faite de clés qui ne se répètent jamais.** *mesuré (U1 D)*
   - Petites variations de 0,3-8° toutes les 4-14 images, plusieurs dérives lentes de périodes différentes, une pulsation (attaque 5 i / retour 30 i), et une fin de tenue qui « ramasse » le corps (tête baisse, poing descend) juste avant de partir.
   - Vitesse de la tenue ≈ 1/8 à 1/10 de celle des gestes.
3. **La tête est l'instrument le plus vivant, et elle sert la cible.** *mesuré (U1, U2)*
   - Dans les grandes rotations, elle contre-tourne pour garder le regard (U2 : 84° de torse, 5° de tête ; U1 : 86° contre 28°).
   - Dans les petits spasmes, elle accentue (U1 pulsation : 15° de tête pour 7° de torse).
4. **Le membre qui « signe » arrive en dernier, après le bras libre et le buste.** *mesuré (U1 E, U2 revers)*
   - U2 montre la passation complète : torse au plus vite, puis il ralentit pendant que le bras accélère, puis le torse re-accélère après.
5. **Le rythme peut se faire avec des DURÉES DE TENUE seules.** *lu + mesuré (WallComboPlayer Constant)*
   - 12 poses claquées dont les tenues raccourcissent (10 → 4 i) jusqu'au coup, puis le coup figé (haut du corps à 0°) pendant que la jambe frappe, puis un fouet de 111° en 4 i.
6. **Animer la victime, c'est animer l'attente puis le retard.** *mesuré (WallComboVictim)*
   - Immobilité totale avant chaque coup, pop en 1 image à l'image du marqueur, membres qui continuent 2 images après le torse, tête 5 images après le contact, corps soulevé par translation du torse.
   - Pendant qu'elle est tenue en l'air : torse quasi immobile, membres qui tremblent (bruit ~0,8°).
7. **L'animateur livre aussi le minutage des effets** (marqueurs), posés sur les arrivées de pose et les contacts. *lu*
8. **La racine n'est jamais animée** : tout déplacement ou soulèvement passe par la translation du Torso. *lu + mesuré*
   - Nos exports devraient pouvoir faire pareil. À vérifier chez nous : je n'ai pas regardé nos fichiers dans ce chantier.

---

## 5. Ce que je saurais REFAIRE maintenant en R6 (concret)

- **Une tenue de charge vivante de 2 à 2,5 s**, d'après U1 D :
  - clés T+JD+JG toutes les 8-12 i avec 0,5-3° de variation ;
  - clés H toutes les 10-30 i (±5-10°), décalées du torse ;
  - bras libre en balancier lent (2 oscillations sur 140 i, ±15-25° d'az) ;
  - poing armé qui monte et descend de 5-15° ;
  - une pulsation au milieu : clé T +7-8° de lacet en 5 i, retour en ~30 i, tête +15° qui accentue ;
  - fermeture sur les 20 dernières images : tête -8°, poing -10° d'el, bras libre qui démarre ;
  - hanche quasi fixe (±0,015).
- **Un déploiement lent et lisible** (1 s) :
  1. bras libre en premier ;
  2. torse qui tourne de ~85° avec un pas arrière et un creux de hanche d'environ 0,3 stud au milieu ;
  3. bras héros en 6 dernières images ;
  4. tête qui garde la cible ;
  5. marqueur d'effet posé sur l'arrivée.
- **Une réaction de victime** :
  1. clé de tenue identique pendant ~8 i ;
  2. pop en 1 image : torse ~14° + ~1 stud, membres 40° ;
  3. membres qui continuent à +2 i (60-100°) ;
  4. tête en retard de ~5 i sur un coup appuyé ;
  5. soulèvement par translation du Torso.
- **Une rafale en poses claquées** : EasingStyle Constant, tenues 10 → 4 i, puis le coup où le haut du corps garde sa pose pendant que le membre frappeur change.

## 6. Ce que je ne saurais PAS (ou pas encore)

- **Le placement relatif réel** des deux rigs du combo au mur, et donc exactement quelle partie du joueur touche quelle partie de la victime à hit2 (§3.4).
- **Le rendu RÉEL du passage Constant** : nos outils l'interpolent. Je n'ai vu que les poses aux clés.
- **Ce que font les marqueurs dans le code** (TweenStuff : caméra ? lumière ?). Je n'ai que les noms.
- **Pourquoi la victime est cuite en motif alterné** (jambes paires, haut du corps impair) : artefact d'outil ou choix. Inconnu.
- **La caméra, les VFX et le son** : aucun n'est dans le fichier. Je n'ai rien vu de la mise en scène.
- **La vraie « nature » des gestes de U1-C et du joueur f156-176** (prise, coup, geste de mise en scène) : déduite de la géométrie seulement, jamais vue en jeu.
- **U2 cuite** : je ne peux pas savoir où étaient les vraies clés de l'animateur. Aucune cassure de vitesse nette : les courbes sont lisses.

## 7. Parties non couvertes ou partielles

- WallComboPlayer f35-156 (recul et marche) : regardé à l'échantillon toutes les 4 i et en courbes, pas clé par clé en détail.
- WallComboVictim f190-350 : 160 images cuites, regardées toutes les 6 i et en statistiques de bruit, pas image par image.
- Aucune vidéo du jeu pour ces quatre anims : impossible de confronter à la mise en scène réelle.
- Je n'ai PAS refait les mesures « bascule 90e centile » d'ETUDE_TSB avec le lecteur corrigé.

## Vérification adverse

Vérificateur indépendant, 2026-09-26. Je n'ai pas réutilisé les scripts du lecteur (`work_A3/`). J'ai tout relu dans le .rbxm avec mes propres scripts (`frames/verif_A3_tsb_ultimes_mur/v_dump.py`, `v_wcp.py` pour les écarts clé à clé par part, `v_world.py`, `v_u1.py`, `v_u2.py`, `v_vic.py` et `v_co.py` pour le monde). J'ai relancé `planche_cles.py --max 40` sur Ultimate1 et WallComboVictim (`v_U1.png`, `v_WCV.png`) et j'ai regardé les planches.

| # | Apprentissage | Verdict | Ce que j'ai vu / la correction |
|---|---|---|---|
| 1 | Marqueurs nommés | **nuancé** | Noms et images exacts (U1 : ParticleActivate 16, TweenStuff 281, StartLoop 495, AwakenFinale 497,2, End 599,1 ; WCP : hit1 9, hit2 176, hit3 352, end 400). Mais TweenStuff (f281) ne tombe PAS sur une arrivée. BD est en plein trajet 267→287 (vitesse de main 3 studs/s jusqu'à f286, puis 0,5 à f289). Le marqueur précède l'arrivée de 6 à 8 i. « Sur les arrivées » ne vaut que pour 16 et 495-497. « Éveil » n'est qu'une interprétation du nom. |
| 2 | Torse et jambes posés ensemble, bras et tête décalés | **nuancé** | U1 : 74 clés T, dont 52 avec les deux jambes et 15 avec une seule. Confirmé pour T+J. Mais **la tête n'est pas décalée** : 35 de ses 46 clés tombent sur une clé T. Seuls les bras sont vraiment décalés (BG 17/38 et BD 20/45 avec T). Surtout, **WallComboPlayer ne suit pas ce schéma** : clés complètes, T avec les deux jambes 76/80, BG 57/60, BD 59/63, H 46/46. La méthode « par couches » est propre à U1, ce n'est pas « en R6 l'animateur… ». |
| 3 | La racine n'est jamais animée | **nuancé** | HRP à poids 0 et position nulle sur toutes les clés des 4 anims : c'est confirmé. Mais c'est **structurel**, pas un choix : en R6, la Pose HRP n'est qu'un conteneur, et tout déplacement passe forcément par la Pose Torso (RootJoint). Distances : le joueur va de z −1,43 (f15) à +4,01 (f150), soit ~5,4 studs d'excursion, puis revient à 0 à f410. |
| 4 | Tenue de charge vivante U1 f290-432 | **confirmé** (chiffres), **nuancé** (étiquette) | Clés T à 296, 302, 314, 323, 335, 345, 356, 361, 371, 378, 388, 392, 403, 411, 418, 428, 432 : intervalles de 4 à 12, écarts de 0,3 à 8,2°, jamais 0. Pulsation f356→361 : T 8,2°, H 10,5° (local). Le lacet monde de T va de −16 à −18 : dérive lente. Mais sur la planche (i296-i432), le « poing armé » est un **bras droit replié à l'horizontale en travers de la poitrine**, pas un poing ramené en arrière. Parler de « tenue de charge », c'est plaquer notre coup sur cette pose. |
| 5 | Déploiement f432-496 | **confirmé** (±1 i) | Lacet T −17,9 → +69. Hanche au plus bas 2,49 à f470 (le lecteur dit 2,48 à f469). Pied gauche levé de ~0,40 à f479-482. Main de BG plus rapide que BD de f458 à f482 (10-13 contre 3-6 studs/s). Main de BD à 4,4 studs/s à f488, puis 12,3 à f491 et 10,7 à f494 ; el −25 → +21. Nuance : en angle, BD fait déjà 44° entre ses clés 479 et 488, contre 41,7° entre 488 et 496. Il n'est « lent » qu'en vitesse de main (le torse le porte), pas en rotation locale. |
| 6 | Revers d'U2 : passation torse → bras → torse | **confirmé** (décalé de 1 i) | T culmine à 4,2°/i à f102, BG (local) à 19,2°/i à f109, et T repart à 6,4°/i à f115-116. Fente jusqu'à z −0,50 (f107), puis retour à +0,04. Creux de hanche 0,25. Correction : la cloche du bras monte en ~11 i (f98→109) et redescend en ~9 i, pas en 15/10. U2 compte bien une clé par image (174 clés pour 173 i). Marche : pics de pied à f12, ~f45-48 et ~f84, torse à x=z=0 exactement, hanche à 2,91 à chaque levée contre 2,99 entre les pas. Confirmé aussi. |
| 7 | Rythme en poses Constant (WCP f272-352) | **nuancé** | 67 poses Constant sur 12 clés (272 [BG seul], 277, 283, 291, 301, 309, 319, 327, 336, 342, 347, 352) : c'est confirmé. Mais la suite complète des tenues est **5, 6, 8, 10, 8, 10, 8, 9, 6, 5, 5**, puis 4 (352→356, en Linear). Elle commence donc courte, s'allonge, puis raccourcit. Le lecteur a omis les trois premières. Les sauts du torse vont de **7,4 à 42,6°** (pas de 15 à 42) : entre 301 et 319, 7-10° seulement. À f352 : H, BG et BD à 0,0°, T 27,7°, JG 13,8°, JD 22,1°. Les deux jambes changent, pas seulement « la jambe de frappe ». **Contradiction interne** : le 111,7° de BD se trouve entre la clé Constant 352 et la clé 356. Si Constant tient bien la pose jusqu'à la clé suivante (ce que dit le lecteur au point 12), le jeu montre une tenue puis un **claquement en 1 image à f356**, pas « 111,7° en 4 i ». Le point 12 (resample_linear ignore EasingStyle) est confirmé par la lecture de `corpus.py`. |
| 8 | Réaction de la victime : immobile, puis en retard et en chaîne | **nuancé** (hit3 réfuté) | hit1 confirmé : f8 identique à f0 (0,0° partout). Pop à f9 : T 14°, 1,16 stud, membres 37-48°. Puis f11 : BD 104°, BG 61°. hit2 : la victime ralentit en douceur jusqu'à 0 (f160-174). JD et JG sautent à f175 (avant le marqueur 176), les bras à **f176** (pas f175), puis H 38° à f179 et 82° à f183. T n'arrive qu'à f179, **après** les bras : l'ordre s'inverse par rapport à hit1. La tête ne « suit pas 5 i après » : elle part en interpolation dès f174, lente, avec un gros coup 179→183. hit3 : **pas une réaction en 1 image**. Il n'y a pas de clé entre 353 et 358, donc une rampe linéaire sur 5 i (T 86,7°, 2,76 studs, bascule à 74°). L'anim **s'arrête à f358**, en plein vol. |

**Autres points recoupés** :
- Victime tenue en l'air : confirmé. Torse à 8,2°/s de moyenne contre 72-90°/s pour les membres (f191-350). Bascule de 38 à 59°. Pieds de 0,54 à 0,77 (le lecteur écrit 0,6-0,78). Alternance jambes aux images paires, haut du corps aux impaires : confirmée ; T à chaque image à partir de f240.
- « Victime à la main jusqu'à f146, puis cuite » : à corriger. Les clés sont éparses jusqu'à f118, puis rien jusqu'à f132, puis **une clé par image dès f132**. De f175 à f191, seules les jambes sont cuites ; le haut du corps n'a que des clés isolées (176, 179, 183, 189, 191).
- Accélération écrite image par image chez le joueur f27-33 (T : 0,1, 0,4, 0,7, 0,9, 1,0, 1,1°) : confirmée.
- ETUDE_TSB corrigée (U1 n'est pas « un bras qui bouge ») : confirmé sur la planche. Rotation de 86° du buste, deux bras qui travaillent, recul de 1,5 stud (z 0,56 → 2,03).

**Oublis importants** :
1. **Les trois anims longues finissent sur une clé de repos** : identité complète, hanche à 3,00, bras à el −90. U1 à f601 (+9 i après f592 et 2 i après le marqueur End), WCP à f410. C'est un geste de fabrication : fermer sur la pose neutre pour le fondu de sortie. Le lecteur ne le mentionne pas.
2. **La victime ne se ferme pas** : fin à f358, cinq images après hit3, sur une pose extrême en l'air. La suite (vol, chute) est sûrement laissée au code ou à la physique. C'est l'inverse du joueur, qui se referme.
3. **Premier soulèvement de la victime à hit1** : torse à y 3,74 et pieds à 0,9-1,2 du sol à f15, puis chute accroupie (y 2,3, bascule 62°) vers f60. Le lecteur ne parle que du soulèvement de f190-350.
4. **Le joueur saute** vers f225 : pied gauche à 1,93, torse à y 3,86. Ce n'est pas dans les notes.
5. **La tenue D d'U1 est une pose bras en travers de la poitrine** (vue sur la planche, i296-i432), et les ~190 premières images (f0-189) sont debout, bras le long du corps, avec de petites dérives. Le lecteur mesure bien, mais nomme les poses d'après notre coup chargé.
6. **Constant et ordre de lecture** : pour qu'une rafale Constant se lise « en claquements », les clés doivent porter Constant sur la clé de DÉPART de chaque segment. La clé 352 est Constant et 356 est Linear : le dernier claquement (352→356) est donc aussi tenu. À vérifier dans Studio avant de copier la recette.
