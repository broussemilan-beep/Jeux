# Les 15 tutos manquants (+3), lus par Gemini sur transcription (2026-09-25)

**Provenance.** Milan a collé ce texte le 2026-09-25. Il sort de Gemini, qui
lit YouTube. **Gemini a lu les TRANSCRIPTIONS (la parole), pas l'image** : il
le dit lui-même en section 5 de chaque vidéo.
- Transcription vide ou musique seule : DAS (ILaV0JYHzwY), Charlotte « How
  to animate R6 SMOOTHLY », Nate.Animations « Expert Roblox Blender/Moon
  Punch ». Rien n'en a été appris.
- Pour les autres : ce qui est dit est couvert, ce qui est seulement montré
  ne l'est pas.
- C'est un résumé de modèle. Les chiffres qui comptent ont été confrontés
  aux mesures (section « Lecture critique » en bas).

**Couverture.** Les 15 vidéos qui manquaient à `SYNTHESE_ETUDE_COMPLETE.md`
sont toutes là (IDs vérifiés par oEmbed) :
- uoXd04yPN8s = n°1, KneO6y3FebM = 2, AH30avEEC9A = 3, ILaV0JYHzwY = 4,
  2FwaIG87LYo = 5, Cu7Xl-cZVBU = 6, bzS9B3-iVH0 = 7, 5_Zr4yYSLks = 8,
  l_bE_-wcVBg = 9, 5u2GSOwjOlM = 10 ;
- kZsboyfs-L4 = 11, -HXx1fK415I = 12, g64E-UNRqcg = 13, 234m7y8D3cE = 14,
  yhGjCzxJV3E = 15 ;
- 16 (Charlotte), 17 (Nate.Animations) et 18 (SinChi) en plus.

---

## Texte de Gemini (condensé fidèlement ; seule la mise en forme change)

### 1. How to make a SMOOTH M1 COMBO animation in BLENDER (bizfr, 17:53)
- Déroulé : blocage du torse (anticipation) ; bras principal ; autre bras (garde) ; tête ; 2e coup (body shot) à la frame 47 pour le combo ; export ; import dans Roblox Studio et retrait du mouvement des jambes.
- Règles, astuces, chiffres : le style Roblox repose sur l'exagération. Toujours commencer par bloquer les keyframes du torse, puis animer les membres autour. Keyframes très proches au moment de la frappe pour simuler la vitesse. Une frame supplémentaire d'exagération du torse juste après l'impact. Pour l'impact, avancer le personnage puis le faire reculer. Penser le bras comme un long avant-bras rigide au début, puis plier instinctivement au moment de la frappe. Pour chaîner un combo, supprimer la dernière keyframe du torse du premier coup.
- À l'oral : « j'aime quand c'est exagéré », « ça fait cool ». Plugin Blender de « Cautioned » (Discord Moon Animator). Promo de son jeu « Aegis ».
- Non vérifiable : interfaces, rendu exact des poses.

### 2. How to Animate a Sword Slash [Moon Animator] (Thundey, 24:36)
- Déroulé : rigging de l'épée (Motor6D) ; torse de 5 en 5 frames ; tête ; bras armé (1 main) ; rotation et inertie de l'épée ; 2e bras ; jambes ; vitesse via drop time stretch ; version à deux mains.
- Règles : « part » transparente (handle), incrément 0. Ghost rig (touche B) : frame précédente en filigrane. Touches R, Y, + / =. Base en pas de 5 frames (0, 5, 10, 15…). Ordre : Torse > Tête > Bras armé > Épée > Bras libre > Jambes. La tête garde les yeux fixés sur la cible. À la fin, étirer toutes les frames à 115 % pour ralentir légèrement.
- À l'oral : l'ordre de sélection (Sword puis Handle) est crucial. Même si la frame d'impact semble trop abrupte, « faire confiance au processus ».

### 3. Make Your Roblox Animations Feel REAL | Roblox Animation Tips 2026 (Devgrams, 8:53)
- Déroulé : bras sans effet ; + anticipation ; + drag ; + follow-through (jiggle) ; combo à l'épée sur 30 frames ; rotoscoping.
- Règles : anticipation (reculer avant de frapper) ; drag (le membre plie et résiste au mouvement global) ; follow-through (overshoot puis retour). Ne jamais laisser une partie du corps complètement immobile pendant une action. « Calculate motion paths » (around frame). Un M1 sur ~30 frames.
- À l'oral : étudier les 12 principes ; rotoscoping comme exercice (ne pas voler le travail des autres).
- Non vérifiable : rendu du jiggle ; références citées (Elden Ring, Sekiro).

### 4. How to animate properly (Roblox Moon Animator 2) (DAS, 6:25)
- Musique uniquement. Rien d'exploitable.

### 5. Roblox Animation for Beginners X INKTOBER #29 part 6 « M1 Comboes » (doc7090, 2:06)
- Règles : un coup simple a 4 poses absolues : Idle, Wind up (rotation opposée à la frappe), Hit (extension complète), Recoil (rebond en arrière). Ce ne sont pas des inbetweens : elles doivent être fortement exagérées, avec une silhouette distincte. Vitesse : tout sélectionner + « 3 ». Export : « 5 ».
- À l'oral : pas de poses données, car elles dépendent de l'art martial ; aller voir des experts d'arts martiaux sur YouTube comme référence.

### 6. Roblox Animation for Beginners part 4 « Animation Workflows » (doc7090, 4:14)
- Trois méthodes :
  1. straight ahead (courtes anims, risque de blocage) ;
  2. pose to pose (poses majeures d'abord, « Constant easing », puis lissage en linéaire) ;
  3. layered (torse, puis membres).
- Posing : ne pas monter le torse trop haut, sinon les jambes se détachent ; pieds écartés en « carré » ; les bras équilibrent.
- Devoir : une idée de 5 s animée 3 fois, une méthode à chaque fois.

### 7. How to make an Attack Animation in 4 Minutes (distovi, 3:51)
- 5 étapes : Idle, Anticipation, Strike, Follow through, Recovery.
- Juste avant le strike, pivoter le torse un peu plus vers la direction de l'attaque (« slow in »).
- Arc de coupe aussi droit que possible.
- Retarder le bras par rapport au torse (delay) pour la lourdeur de l'arme.
- Key pose = la pose qui représente le mieux l'action (la plus exagérée).

### 8. How to Make Smooth Animations!! | TSB Skill Builder (Sikasisi, 8:01)
- Keyframes espacées de 2 à 4 frames, pose ajustée très légèrement à chaque fois.
- Un coup « mou » : avancer le perso de 1 à 2 studs au moment de la frappe.
- Effets liés au script (hitbox, gravity, knockback).
- À l'oral : préfère des VFX simples pour ne pas masquer l'animation. Les 6 dernières minutes sont visuelles (montage).

### 9. (OUTDATED) Moon Animator Tutorial: Fighting Basics (ROBLOX Cinema Community, 4:16)
- Stance ; anticipation reculée (frame 15-16) ; poing en avant ; esquive de la cible.
- Easing « Quad » (touche 7), jugé le meilleur ; esquive « élastique » en easing « Out ».
- À l'oral : « levez-vous, mimez le coup et copiez-vous ». Ne pas trop avancer le perso, sinon Moon le fait tourner sur lui-même.

### 10. How I Animate Part 2: An Unofficial Moon Animator 2 Tutorial (Tycoon, 1:08:01)
- Réglages : Editor quality 21, Mesh Detail 9 ; supprimer le raccourci « C » (Comment) de Studio.
- Rig : Primary Part = HumanoidRootPart (ou Torso) ; EasyWeld « Join in place » (animatable) ; pivots corrigés avec RigEdit Lite.
- Organisation : rigs dans la Toolbox (garde « Anim Saves ») ; mouvements séparés par des blocs invisibles liés (avancée globale, saut, tremblement de caméra).
- Stop-motion : Frame Fill, intervalle 7 ou 10, style None.
- Lumières et rendu : Surface Light angle 0 / range 0.2 ; Bloom Threshold 1-2 ; Sun rays intensity 5 ; Depth of field « Occluded » ; Atmosphere Offset et Haze à 2 ; Device Emulator HD 1080 ; fond magenta pour le détourage.
- À l'oral : l'Atmosphere de Studio met du temps à s'adapter, d'où des scènes très espacées dans un seul fichier.

### 11. The Animation of Guilty Gear Xrd & Dragon Ball FighterZ (New Frame Plus, 17:21)
- « Kill everything 3D » : si ça a l'air 3D, on le corrige à la main.
- Cel shading avec une lumière propre à chaque perso.
- Animation limitée : pas d'interpolation (stepped keys), on choisit la durée de chaque pose.
- +500 os pour casser l'anatomie et exagérer la perspective image par image.
- Fumée au sol sculptée frame par frame.
- DBFZ encore moins d'images que GG, pour imiter la rigidité de l'anime DBZ.

### 12. Fisticuffs: Tips for animating action and fight scenes (Dong Chang, 6:07)
- 3 phases :
  - wind up : retient énormément de frames (le corps avance, le bras reste longtemps en arrière) ;
  - punch : extrêmement rapide, parfois 1 frame ou un smear ;
  - follow through : très lent (ease in), rebond du bras, frames qui montrent la victime souffrir.
- Coup rotatif : l'épaule et la tête précèdent la jambe.
- À l'oral : un vrai coup reproduit à l'identique est « nul et ennuyeux ». « Le coup doit être ressenti par le spectateur, pas vu. »

### 13. Why Your Punches Lack Energy (Howard Wimshurst, 23:18)
- Erreur fréquente : un corps équilibré, et un inbetween au milieu de la course du poing.
- Un coup puissant détruit l'équilibre : le centre de gravité sort de l'axe des pieds.
- Le bras libre part d'abord, pour créer la rotation des hanches.
- « Whip frame » : le torse s'élance en premier, le poing reste le plus loin possible en arrière.
- Follow-through en arc large, puis aftermath (stabilisation).
- Timing : pre-anticipation 3, anticipation 5, whip 1, action 1, follow-through 4, aftermath 5 (frames).
- À l'oral : mener par le corps = passion, hors de contrôle ; mener par la tête = contrôle calculé.

### 14. Why Guilty Gear's 'Bad' 3D Models Look Perfectly 2D (Noggi, 29:23)
- Rendu, pas animation :
  - inverted hull et vertex color, « trou » dans le visage contre les traits internes ;
  - yeux plats orientés caméra ;
  - lèvres en V ;
  - cel shading par Dot Product (normale · lumière), pas par Diffuse, pour éviter les auto-ombres ;
  - channel packing RGBA ;
  - texture SSS choisie à la main pour les ombres ;
  - normales éditées ou transférées depuis un proxy, et re-transférées après l'armature.

### 15. GuiltyGearXrd's Art Style: The X Factor Between 2D and 3D (GDC, Motomura, 58:59)
- Ne rien laisser à l'algorithme 3D.
- Production : 40 000 triangles, UE3, Softimage.
- Rendu : pas de normal maps (infos de lumière en vertex colors) ; inverted hull ; traits internes par UV sur lignes droites.
- Animation limitée sans interpolation ; ~500 os, beaucoup de scale.
- Textures : une 2K et deux 1K.
- À l'oral : 2 mois de modélisation plus 2 mois d'animation par perso. Pas de GI ni d'ombre propre sur les persos, sauf l'ombre ronde au sol. Fumée sculptée image par image (au départ une blague).

### 16. [OLD] How to animate R6 SMOOTHLY (Charlotte, 12:41)
- Transcription vide.

### 17. Expert Roblox Blender/Moon Punch Animation tutorial (Nate.Animations, 16:46)
- Transcription vide.

### 18. Every (Anime) Animation Technique Explained in 12 Minutes (SinChi, 13:01)
- Impact frames, éclairs Kutsuna, smears.
- Cubes Yutapon : débris au timing strict d'arrêt et de relâchement (hold & release).
- Rotoscoping, style Kanada, fond animé, Itano circus, acting.
- Kagenashi : pas d'ombres, donc des poses d'action plus libres.
- Marche Ebata ; œil Umakoshi : zoom agressif sur l'œil d'un perso qui charge.
- Timing : 1s = 24 i/s, 2s = 12, 3s = 8. Souvent en 2s, en 1s sur les impacts majeurs.
- Obari punch : bras tiré en arrière, torse bombé en avant, poing droit vers la caméra.
- À l'oral : beaucoup de points sont des styles d'auteurs plus que des techniques.

---

## Lecture critique (Claude Code, 2026-09-25)

**Ce qui converge, de sources indépendantes.**
- **Frappe très rapide, préparation et suite lentes :**
  - Dong Chang : wind-up long, punch en 1 image, follow-through lent ;
  - Wimshurst : 3 + 5 images de préparation, 1 de fouet, 1 d'action ;
  - Williams : « the slow against the fast » ;
  - notre mesure TSB (frappe 2,3-5,7 fois plus rapide que la préparation).
  - C'est le point où la rafale v7 s'écarte le plus (0,55-1,49 ;
    `CARNET.md` §2.1). **Quatre sources plus une mesure.**
- **« Senti, pas vu »** : Dong Chang (« ressenti par le spectateur, pas
  vu ») répète presque mot pour mot Ken Harris (« we won't see it, but
  we'll feel it »).
- **Le corps d'abord.** bizfr (torse d'abord), Thundey (torse > tête >
  bras…), doc7090 (layered) : même ordre de travail que les tutos déjà
  étudiés (`etude_complete_uppercut_moon.md`).
- **Poses fortes, pas des intervalles.** doc7090 (4 poses absolues,
  exagérées, silhouette distincte), distovi (key pose = la plus exagérée).
- **Clés espacées, pas image par image.**
  - Sikasisi : 2 à 4 images. Thundey : base de 5.
  - doc7090 : poses en Constant, puis lissage Linear.
  - GGXrd : pas d'interpolation.
  - TSB mesuré : écart médian 2 à 4 images.
- **Obari** (SinChi) : bras tiré en arrière, torse bombé, poing droit
  vers la caméra. C'est ce que fait `repro/saitama_obari.py`.

**Mesuré contre TSB, même fenêtre** (`r6_poing_dragon/scripts/tutos_vs_tsb.py`,
sortie `output/tutos_vs_tsb.txt`) :
- **Avancer à la frappe (Sikasisi, bizfr).**
  - TSB : -0,4 à 0,7 stud DANS l'animation.
  - v7 rafale : 0,3 à 1,0 stud. On avance déjà autant ou plus.
  - Chez TSB, l'avancée vient surtout du script (P1 de `recherche/roblox`).
  - **Pas un manque chez nous.**
- **Rotation du torse pendant la frappe (Wimshurst : les hanches tournent).**
  - TSB M1-M3 : 84-110° ; Collateral Ruin : 187° ; M4 : 31°.
  - v7 rafale : 33-68°, soit environ **la moitié**. Ça rejoint « poses ~2x
    trop sages ».
  - Coup chargé : 132°, dans la norme.
- **Fouet (le torse mène le poing).**
  - TSB : de -5 à +4 images selon le coup. Trop bruité pour conclure.
  - v7 h1 et h3 : -7 et -8. Le poing atteint sa vitesse max bien AVANT le
    torse, ce qui recoupe le ré-armement trop rapide.
  - Indice, pas preuve.
- **Écart entre clés.**
  - TSB : 2 à 4 images.
  - v7 : **une clé par image** sur la rafale et le coup chargé (104 clés sur
    f0-110). La v7 prévoyait « poses clés seules (~15/s) en Linear »
    (`FICHE_V7.md`). Seul un A/B l'a fait, sur le coup chargé (v6,
    `scripts/ab_cles_eparses.py`) ; la ligne principale est restée cuite
    image par image, depuis l'IK.
  - Écart plan / réalisé que je n'avais pas signalé.

**Ce qui diverge, et selon quand.**
- **« Ne jamais laisser une partie du corps immobile »** (Devgrams) contre
  la tenue longue (Dong Chang, obari, hold & release).
  - Réconcilié par la tenue vivante (uppercut Moon).
  - Mais le wiggle cumulé avec une caméra qui bouge a rendu la charge v7
    floue (regard.py). Vivant, oui ; tremblant sous une caméra mobile, non.
- **Easing Quad « le meilleur »** (Cinema Community, tuto marqué OUTDATED)
  contre Linear à clés espacées (TSB mesuré, Sikasisi, doc7090).
  - C'est un tuto de cinématique, pas de combat de jeu : contexte différent.
- **Étirer tout à 115 %** (Thundey) : un réglage de goût, à la fin, après
  avoir vu l'anim. C'est une façon de juger en mouvement (CARNET §1.1).

**Hors animation, mais utile à Rank Zero (Godot).** Noggi et Motomura
parlent de rendu : lumière propre à chaque perso, cel shading par produit
scalaire (pas Diffuse), pas d'auto-ombre, vertex colors plutôt que normal
maps, traits internes par UV. Ça concerne `ARCHITECTURE_VFX_v3.md`, pas le
rig R6. Je le signale, je n'en fais rien ici.

**Ce qui reste non appris.** Tout ce qui est seulement MONTRÉ : poses de
Charlotte et de Nate.Animations (transcriptions vides), DAS (musique), la
fin de Sikasisi et de Devgrams, les schémas de doc7090. Pour ça, il faut
les images. Gemini peut décrire les images si on le lui demande
explicitement : voir le prompt de `recherche/VIDEOS_POUR_GEMINI.md`, point 3.
