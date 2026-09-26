# B3 : apprendre et l'œil critique (chantier 4)

Identifiant : `B3_apprendre_et_critiques`. Écrit le 2026-09-26.
Angle : l'œil critique. Qu'est-ce que les animateurs expérimentés reprochent, avec quels mots ? Qu'est-ce qui progresse d'un essai à l'autre ? Quelles erreurs de débutant reviennent ?
Ce sont des **apprentissages**, pas des règles. J'écris « ici, l'animateur fait X parce que Y ».

Statuts utilisés : **vu** (je l'ai regardé moi-même), **mesuré** (outil, chiffre sorti d'un script), **lu** (texte : forum, texte à l'écran), **déduit** (mon interprétation).

Notes brutes prises au fil du visionnage, seconde par seconde : `c4/notes/_brouillon_B3.md`.
Images et planches extraites : `c4/frames/B3_apprendre_et_critiques/`, qui contient :
- `planches/p0000..p0880.png` : 45 planches de 20 images à 1 i/s, horodatées ;
- `x093/` : la course du débutant à 10 i/s ;
- `x180/` : les extraits de pros à 15 i/s ;
- `x305/` : le combat de la semaine 1 à 8 i/s ;
- `x484/` : l'appel avec Xoaterz à 4 i/s, avec des zooms ;
- `tsb_M1.png` et `pack_M1_1.png` : planches de clés des fichiers pros.

---

## 0. Couverture réelle, et ce que je n'ai pas pu voir

### Vidéo « I Tried Learning Roblox Animation (2) » (DeHapy, LWMujy7LSC0)

Durée 896 s, 640x360, 30 i/s. J'ai tout regardé :
- **896 images à 1 i/s**, réparties dans 45 planches horodatées que j'ai toutes lues.

Démonstrations revues plus densément :
- la première course du débutant, 92.5-95.8 s, à **10 i/s** ;
- les extraits de pros, 180.5-193.5 s, à **15 i/s** (195 images) ;
- le combat final de la semaine 1, 304.5-313.5 s, à **8 i/s** ;
- l'appel en direct avec Xoaterz, 484-544 s, à **4 i/s** (240 images), avec zooms sur la planche de critique et sur les reposes.

Ce qui me manque :
- **Pas de son.** Je n'entends rien de ce que dit Xoaterz pendant qu'il repose le personnage. Pourquoi il touche telle partie reste donc « déduit ».
- Dans les planches, les passages hors animation (Bubble Gum Simulator, mèmes, Discord, argent, jeu d'un client) ont été vus à 1 i/s seulement, sans densifier.

### Fils DevForum (r1.txt à r15.txt)

Les 15 fichiers ont été **lus en entier**. Ils contiennent 95 fils et 794 messages (**mesuré** par grep sur les en-têtes `#####` et `--- #`).

**Limite majeure : je n'ai vu AUCUNE des animations critiquées.** Les liens vidéo pointent vers le S3 du DevForum, bloqué depuis ce bac à sable, et le dossier `tutos/devforum/_echecs_pas_des_images` le confirme. Je connais donc les **mots** des critiques, jamais les **images** critiquées. C'est justement le cas inverse de la vidéo.

Quelques messages sont tronqués dans les fichiers eux-mêmes :
- le guide de Jespone (r3 #1) ;
- C_Corpze (r3 #11) ;
- Chark_Proto (r5 #13) ;
- la fiche de la rig V2.22 (r8 #1) ;
- FroDev1002 (r14).

### Fichiers pros (lecture seule)

- TSB « M1 » : planche + JSON.
- Pack battleground « [2] M1_1 » : planche des 14 premières clés, texte des 40.

J'ai ajouté ces deux planches pour **confronter les critiques du forum à ce que font réellement des pros**. Je n'ai pas fait d'autres animations : ce n'était pas mon angle.

---

## 1. Source A : la vidéo de DeHapy, quelqu'un qui APPREND

### A1. Le parcours, étape par étape

DeHapy apprend en public : ses erreurs, les critiques qu'il reçoit, puis ce qu'il en fait. Chaque étape ci-dessous est **vue**.

1. **46-50 s. Premier contact avec Moon Animator 2.** Il fait tourner les deux bras en V, puis écarte bras ET jambes en étoile. C'est la pose symétrique « stickman » que la planche ✗ de Xoaterz condamnera plus tard (500 s).
   - Déduit : c'est la première chose que fait n'importe qui avec un rig. On tourne les membres dans le plan de l'écran, de façon symétrique, parce que c'est ce que le gizmo propose par défaut.
2. **89-104 s. Première course.**
   - Timeline (vue à 92.5-93.0 s) : 5 à 6 colonnes de clés **alignées sur toutes les pistes** (Torso, bras, jambes, tête aux mêmes images).
   - Rendu à 10 i/s (vu, `x093/g.png`) : torse **vertical** tout du long ; tête à hauteur constante entre 93.1 et 93.6 s, sans rebond visible ; bras courts qui balancent dans le plan ; jambes en ciseaux symétriques ; à 94.7-95.8 s, pieds qui semblent glisser.
   - Verdict qu'il affiche lui-même (ChatGPT, lu à 98-112 s) : « That run animation gets a strong 2 out of 10 […] he's power-walking to the fridge at 3AM […] The arms are floppier than a wet noodle, the legs are moving like he's trying to moonwalk forward, and the pose? Built like a Roblox T-pose that got jump-scared mid-step. »
   - Déduit : sous le gag, le diagnostic est juste. « Power-walking » : le torse ne se penche pas et n'y a pas de rebond. « Moonwalk » : les pieds ne sont pas plantés. « T-pose » : poses dans le plan de l'écran.
3. **115-157 s. Jours 2 et 3.** Un personnage court et s'écrase contre un mur, puis deux rigs : l'un pousse, l'autre s'effondre « en tas », membres à plat (154-157 s, vu).
   - Il anime la **caméra** : embarquée, gros plans de la chute (133-136 s). C'est elle qui porte le gag.
4. **252-318 s. Jour 5, « The Plan ».** Un court-métrage en forêt.
   - À 8 i/s (vu, `x305/`), l'animation elle-même reste faible :
     - saut : corps horizontal raide, trajectoire rectiligne, sans arc (305.0-305.9 s) ;
     - les deux corps se chevauchent sur les marches pendant environ 6 images, et on ne sait plus qui fait quoi (306.25-307.0 s) ;
     - relevé « pop » en 2-3 images (307.125-307.375 s) ;
     - coup porté sans recul visible de la cible (308.25-308.5 s) ;
     - torses verticaux en garde.
   - La mise en scène, elle, est déjà bonne (vu) :
     - plans d'établissement de la forêt (260-262 s, 285-290 s) ;
     - caméra derrière l'épaule, en amorce (293-295 s, 309.75 s) ;
     - contre-plongée qui monte vers la clé géante (296-299 s) ;
     - transition par masquage : la caméra passe derrière la clé (311.625-311.875 s) ;
     - plan final tenu (313 s) ;
     - reprise en noir et blanc (315-318 s).
   - Réaction du public (lu, 336 s) : « You should actually try more animation, that end result is really good for a beginner ».
   - Déduit : ici, **c'est le montage et la caméra qui ont vendu une animation faible**. Une caméra intelligente cache beaucoup. Ce n'est pas une excuse, c'est un levier.
5. **Critiques reçues (lu).**
   - @zanpiedad, 17 s : « you should learn the principles of animation, as well as animate in 5's in moon (scroll on the timeline till you see 5-10-15 kinda keyframes). it makes animations much smoother without the use of easing ».
   - @slimematteo, 410-414 s : « next time look at the 12 principles of animation, thats the first thing most animators watch before starting off ».
   - Commentaire, 320-340 s : « you sould also master smear frames ».
6. **Semaine 2 (416-481 s).**
   - Il découvre qu'on peut **translater** un membre : bras seul déplacé de 1.17, puis 7.81, puis 10.72 studs (419-421 s, vu).
   - Il suit le tuto de Ludius « How To Impact Frames Like A Pro ». Trois objets ColorCorrection IF1/IF2/IF3 dans Lighting (429-431 s, vu). La timeline « FlipPunch » porte des pistes IF, Highlight, Camera et R6 (432 s, vu). Une image d'impact en silhouette blanche sur noir (434 s, vu).
   - Il utilise la **pelure d'oignon** rouge (fantômes des membres, 470 et 472 s, vu).
7. **484-541 s. Critique en direct par Xoaterz** (voir A3 et A4).
8. **600-616 s. Après la critique.** Anim « stomp » : le genou monte, frappe le sol, des cristaux jaillissent (vu 604-615 s). Carton « This took forever to edit ».
   - Il anime les **propriétés des VFX** dans Moon : pistes « Rise1 », « Rise2 », « Enabled » (718-719 s, vu), après un tuto « How To Animate Effects - Moon Animator » (712 s).
9. **854-879 s. Shorts « LEVEL 1 / LEVEL 8 / LEVEL 99 »** (vu).
   - L1 : debout, raide ; il frappe et tombe lui-même en tas.
   - L8 : penché, il frappe.
   - L99 : il marche, tornade verte, crâne, flou.
   - Déduit : même chez lui, ce qui fait monter le « niveau » affiché, c'est l'amplitude du corps, plus la caméra, plus l'effet, ensemble.

**Ce que ce parcours m'apprend (déduit, fondé sur les étapes vues ci-dessus) :**
- Les premières erreurs d'un débutant sont **structurelles**, pas de détail : toutes les pistes clées aux mêmes images, torse vertical, poses dans le plan de l'écran, symétrie, pieds non plantés, contacts sans réaction.
- Ce qui progresse le plus vite, ce sont les **outils autour de l'animation** : caméra, montage, impact frames, VFX. Les poses progressent lentement.

### A2. Les pros montrés à 180-193 s, à 15 i/s (vu)

**Xoaterz (181.43-184.03 s)**

1. **181.63-181.97 s : tenue en gros plan.** Visage de face, bras ramené devant la poitrine, cadre penché. Le personnage est quasi figé (environ 5 images à 15 i/s, soit 0,35 s).
2. **182.03 s : une seule image d'impact noir/blanc.**
3. **182.10-182.23 s : trois images d'aberration chromatique et de flou.** Le coup « passe » dans ces trois images : **on ne voit jamais le bras traverser**.
4. **182.30-182.50 s : coupe sur un gros plan du contact**, tenu environ 4 images.
5. **182.57-182.83 s : blanc, puis un corps projeté.**
6. **182.90-183.37 s : l'attaquant tourne sur lui-même** (suivi du mouvement).
7. **183.43-184.03 s : il atterrit dans une pose très basse** et la tient environ 0,35 s. Genou arrière presque au sol, torse presque horizontal, bras tendu vers le bas-avant, tête basse.

Déduit : ici l'animateur **raconte le coup par ses deux bouts** : la tenue avant et la pose d'après. Le passage lui-même est confié à 3-4 images d'effet. La pose de fin est **plus basse** que la pose de départ : le corps a « donné » son poids.

**CrashMagician (184.10-186.70 s)**

1. **184.10-184.43 s : le buste tourne** du dos à la face en 6 images (enroulement).
2. **184.50-185.43 s : charge tenue environ 0,9 s** (14 images). Caméra très basse, cadre penché à environ 45° (mur en diagonale). Le poing monte un peu vers l'avant (184.97 → 185.23 s).
3. **185.50 s : une image floue**, le personnage disparaît. **185.57 s : une image blanche plein écran.**
4. **185.63-186.70 s : coupe sur la victime** qui s'envole dans une explosion qui grossit (15 images).

Déduit : **le coup lui-même n'est jamais montré**. Longue charge, puis 1 image blanche, puis longue conséquence. Tout l'effort de pose va dans la charge.

**Thundey (187.10-189.93 s)**

- **187.30-187.57 s : le personnage sombre TIENT sa fente** pendant 5 images quasi identiques, pendant que l'autre (chemise blanche) arme puis tend son bras. **Un seul personnage bouge à la fois.**
- Horizon penché d'environ 15-20° (estimé à l'œil) et lignes de vitesse dans le ciel.
- **189.50-189.90 s : un tableau figé de 7 images** : l'un à l'horizontale en l'air, l'autre en garde basse.

Déduit : dans un échange, l'animateur **alterne qui agit**. Celui qui ne frappe pas garde une pose lisible. Ça rend l'action lisible même très vite.

**Clip à l'épée (189.97-192.7 s)**

1. Contact, sang, arc blanc (190.5-191.2 s).
2. **Image désaturée en noir et blanc** : le moment suspendu (191.30-191.83 s).
3. Blanc (191.90 s).
4. **Rouge plein écran avec silhouettes blanches pendant environ 11 images, soit 0,7 s** (191.97-192.63 s).

Ce qui est nouveau par rapport à l'étude existante : les durées image par image, l'alternance « un seul bouge », et le fait que le coup n'est jamais montré chez CrashMagician. Le déroulé général (flashs, silhouettes, rouge/blanc) était déjà décrit.

### A3. Comment Xoaterz place le rig : l'ordre de travail vu à 4 i/s

Tout ceci est **vu** image par image (`x484/g000-g014.png`, zooms `z1..z4`). L'intention reste **déduite** : pas de son.

1. **489.0-492 s : LE TORSE D'ABORD.** Il ouvre le rig de DeHapy, debout. Seules les poignées de rotation du **torse** apparaissent. En environ 2 s, il tourne le buste de 3/4 puis le **penche fortement vers l'avant-bas** : la tête passe sous la ligne des épaules, torse presque horizontal (490.25-491.75 s). Bras et jambes n'ont pas encore été touchés.
2. **493-499 s : il revient au clip de DeHapy** et met en pause sur la pose accroupie, genoux en V : il montre le défaut.
3. **524.75-526.25 s : encore le torse en premier** sur une nouvelle pose. Il le bascule presque à l'horizontale.
4. **526.5-529 s : la JAMBE libre, par translation.** Le gizmo à flèches (et non les anneaux) est sur la jambe sélectionnée en orange. Il **translate** la jambe, puis la tourne (530-533 s).
5. **530-534 s : les bras.** L'un est levé loin derrière la tête, en diagonale ; l'autre est plié devant, vers le bas. Résultat à 533-534 s :
   - torse incliné d'environ 45° (estimé) ;
   - une jambe d'appui verticale, l'autre levée en diagonale ;
   - bras sur une diagonale ;
   - silhouette nette en diagonale.
6. **534.5-536.5 s : il VÉRIFIE l'appui.** Il descend la caméra au ras du sol pour regarder le pied d'appui et la jambe levée.
7. **537-539.75 s : une autre pose en fente large.** Jambe arrière tendue loin, torse penché au-dessus du genou avant, bras arrière levé haut en diagonale, bras avant tendu vers le bas-avant.
8. **539.5-541.75 s : il compare avec la pelure d'oignon.** Le rig passe au rouge (fantôme de la clé précédente), une traînée rose derrière le bras. Il compare la nouvelle pose à l'ancienne.

**Apprentissage (déduit, sur ces vues).** Ici, l'animateur pose dans cet ordre, parce que chaque étape dépend de la précédente :
- **buste** (rotation + inclinaison) : il donne la direction et l'énergie de toute la pose ;
- **jambes**, déplacées autant que tournées : elles doivent porter ce buste ;
- **bras** : ils prolongent la diagonale ;
- **vérifications** : l'appui au sol vu d'en bas, et la pelure d'oignon contre la clé d'avant.

Ce n'est pas l'ordre du débutant, qui tourne d'abord les bras (46-50 s).

### A4. La planche ✗/✓ (lue en clair à 500-504 s)

Les textes sont recopiés tels quels (lu). Les poses sont vues sur les zooms `sp_x.png`, `sp_v.png` et `sp_v3.png`.

| Pose | Verdict | Texte exact | Ce que je vois |
|---|---|---|---|
| Haut gauche | ✗ | « -disjointed legs -perma crouched position -asymmetric posing -general ugly ass blender posing » | Accroupi de face, cuisses en V ouvert, torse vertical, bras écartés |
| Haut droit | ✓ | « -straight legs -is an interesting pose -hands in pocket -isn't 3 inches away from touching the ground » | Debout, jambes droites, mains dans les poches, décontracté |
| Bas gauche | ✗ | « -boring sameside posing -looks like a stickman » | Bras tendus à l'horizontale à gauche et à droite dans le plan de l'écran, fente de face, torse de face |
| Bas droit | ✓ | « -is interesting -doesn't look like a stickman -Looks akin to The Strongest Hero's Ultimate Move, The Serious Punch. The Strongest Hero originates from the hit fighting game; "The Strongest Battlegrounds". » | Vue de 3/4 (voir ci-dessous) |

**Pose ✓ bas droit : ce que je vois**
- Le visage regarde vers la **gauche** de l'image : yeux et sourire sur la face gauche de la tête, net à 504.0 s.
- Un bras **long et horizontal** part vers la gauche de l'image, à hauteur d'épaule.
- L'autre bras est **court, raccourci par la perspective**, et pointe vers la droite et le bas, en arrière du buste.
- Une cuisse levée, genou haut devant.

**Contradiction entre les deux études existantes du cerveau :**
- `rapport_video_critique_poses.md` : « bras (le droit) ramené en arrière et plié à hauteur d'épaule » ;
- `etude_complete_dehapy.md` : « bras tendu à l'horizontale vers l'avant ».

Ma lecture (déduit, confiance moyenne) : **les deux ont raison, chacune sur un bras.** Le visage tourné vers la gauche indique que le bras long horizontal est le **bras avant** : il tend vers la cible. Le bras court est **le bras qui frappe, ramené et plié en arrière à l'épaule**. Cela rejoint Milan (26/09) : « dans aucune [ref] le bras est tendu derrière ». Ici, le bras tendu est devant.
Réserve : 640x360, et une image fixe sans la vue de profil.

**Sur « sameside » (déduit).** Dans la pose ✗ du bas, les deux bras sont dans **le même plan**, celui de l'écran, et le corps est de face. C'est un « côté unique », sans profondeur. La pose ✓ travaille au contraire **en profondeur** : un bras devant, un derrière, un genou vers la caméra.

**Sur « perma crouched » (lu + déduit).** Le reproche porte sur le mot « perma ». Se baisser est un moment, pas un état. Même la pose de repos ✓ a les jambes droites. C'est exactement le « il est accroupi » de Milan (24/09).

### A5. La ligne d'équilibre (516-519 s, vu)

Un trait rouge vertical part de la tête jusqu'au sol, avec une marque sous le pied d'appui. Pose : genou levé haut, bras écartés, torse légèrement incliné. À 519 s, vue de côté, la jambe est levée en diagonale et la verticale tombe sur le pied d'appui.

Texte Discord partiel (lu) : « …ke something look heavy ».

Déduit : ici, l'animateur vérifie que **la tête est au-dessus du pied qui porte**. Une pose sur un pied, penchée, reste crédible tant que c'est le cas. Le lien exact avec « heavy » est coupé dans l'image.

---

## 2. Source B : les fils de critique du DevForum (lu)

### B1. Ce que les animateurs reprochent : fréquence des thèmes

Comptage **mesuré** par grep sur 3165 lignes et 794 messages. C'est grossier : chaque mention compte, critique ou pas.

| Thème | Occurrences |
|---|---|
| legs / leg | 92 |
| torso | 57 |
| pieds / glissade (feet, foot, slide) | 43 |
| easing / ease | 104 |
| linear | 20 |
| stiff / robotic | 22 |
| smooth | 78 |
| choppy | 19 |
| power / impact / weak / soft | 62 |
| anticipation / wind-up / build-up | 24 |
| follow-through / recoil / arrêt brusque | 14 |
| exaggerat… | 21 |
| detach / disconnect | 17 |
| reference / filme-toi / punch the air / in real life | 30 |
| camera | 49 |
| R15 | 98 (débats R6 contre R15) |

Déduit : **les jambes et le torse dominent les reproches sur le corps.** Côté vocabulaire, les critiques emploient surtout « linear / easing / smooth / choppy ».

### B2. Les critiques exactes, regroupées par défaut

Tout est lu, cité mot pour mot. Le fichier et le numéro de message sont entre parenthèses.

**Seuls les bras bougent ; le corps ne suit pas**
- « Try animating the torso as well as the head. The arms just being animated seems a little unrealistic for today's standards. » (SubtotalAnt8185, r7)
- « adding secondary movement like the torso also following the movement of the arms […] right now looks quite static with only the arms moving » (sharksenpai, r7)
- « the animation isn't dynamic (meaning that one body part doesn't affect the others, the torso and legs should also be moving bro) » (IceTheOneAndOnly, r12)
- « keep in mind that (most of the time) the whole body moves together. Put yourself in the character's position; become the character. » (MmadProgrammer, r15)
- « if you're throwing a punch, it will make your upper body lurch forward, but the motion will be a frame or two behind the arm » (pjhinthehouse, r1)
- « swing with the whole body » (GolgiToad, r6)

**Les jambes**
- « it seems like it's legs are glued together » (8unii, r1)
- « it kinda looks like they're going to fall over after punching » (Pro3taco, r1)
- « Compared to the arms, the legs seem to just turn out of the way. » (Reditect, r1)
- « it looks quite unrealistic and kinda looks like they are on ice skates lol » (Archie4lifeyodude, r1)
- « if one leg is moving, the other shouldnt unless its a jump of sort. at 0:03 the leg in the floor is sliding. it should stay still the whole time » (iM1GHTB3DANI, r2)
- « the legs, they don't look planted on the ground at all » (TrulySmoosh, r7)

**Mais :** plusieurs auteurs expliquent que les jambes sont **volontairement laissées vides** dans les attaques de jeu :
- « the reason I don't animate the legs is so that the normal roblox walking animation does it for me. take a look at battlegrounds games. most popular ones do the same thing. » (melvinpetersen, r1)
- « it's like that on purpose so that if another animation is playing that has leg movement is plays both » (F0xBirdman, r1)
- « all the limbs except the legs have an animation track with key frames » (MonkeyIncorporated, r5)

**C'est linéaire, raide, robotique**
- « it appears that its all linear with a short pause on the keyframes » (0BSCURlTY, r2)
- « Cubic i find works best for human-like effort, other than that I use linear. […] there are no points in the anim where a keyframe is going to itself, so everything is always moving. » (0BSCURlTY, r2)
- « Keep momentum going – when a limb changes direction, keep it going in the direction it was moving previously for a bit. Otherwise the limbs accelerate sharply like a robot's. » (PersonifiedPizza, r12)
- « the character starts each motion at different times. Creatures tend to predict movements and start them slightly before preforming them. » (PersonifiedPizza, r12)
- « Make the characters torso rotation speed go slow → fast → slow again it gives a smoother effect. » (Rymxi, r7)
- « Right now everything is happening basically at the same speed » (mewnmowse, r4)
- « Customizing the interpolation between keyframes is one of those things that only looks good if it's applied with some rationale behind it » (mewnmowse, r4)
- « Try out different easing styles as using the same one over and over is really obvious » (VeeGFX, r12)
- « easing doesn't immediately make the animation better, you'd have to remove some keyframes to make it seem smooth » (TrulySmoosh, r15)

**Pas de puissance**
- « it feels as if the character is lightly tapping something instead of punching it » (realknife, r12)
- « character recovers from punching as if it was using as little force as possible […] there was never a feel of great force being used » (realknife, r12)
- « the punches were too soft and kinda seems like they were wipping food off their cheeks! » (Tornado_chaser04, r12)
- « it feels like flailing arms rather than punches » (Toefl, r12)
- « this punch is WAAY to weak […] I would make the model wind up the punch more, then quickly throw it foward with a powerful release. » (synical4, r11)
- « The punch could have more acceleration coming into it. It looks like it doesn't have any. » (Crazedbrick1, r11, sur la recréation du Serious Punch par Pew)

**Pas d'anticipation / le coup sort de nulle part**
- « the punch just kinda happens out of nowhere » (Pokemoncraft5290, r3)
- « That uppercut starts out weird? He looks like he's going to do a regular punch, and transitions to an uppercut randomly. » (Pokemoncraft5290, r3)
- « there lacks any anticipation for the kick. Like maybe have the leg, that's kicking, tuck into the body first » (Bubblegumboy29, r7)
- « Before a character punches you should put them in a strong and expressive "I'm ready to punch" position. » (C_Corpze, r3)
- « The preparation part for the action needs to be longer, to build the energy, add more weight » (vipkute0057, r2)

**La fin : le mouvement s'arrête net, puis retour à l'idle**
- « I think the issue lies at the end of the punch, they hands just seem to stop as if they loose all momentum. » (Bovious, r1)
- « The way they just cut out of the move lessens the impact. Google "Follow through in animation" » (Xenonic_778, r1)
- « you dont want the character to immediately go into idle position after performing a slash, just add some keyframes » (urgentnotice, r2)
- « instead of having the fist just immediately stop in a seemingly arbitrary point in the air, have it slow down and turn inwards » (LucensCat, r2)
- « When the character returns to the normal pose, it looks like another hit with the sword. » (Dyzody, r15)

**Mais à l'impact, l'arrêt brusque est voulu :**
- « When a character punches, make the movement really fast, when the fist hits, make it stop abruptly. After that make the fist slowly retract and relax. » (C_Corpze, r3)
- « the middle phase of the attack should be extremely fast to convey power (around 4 frames); the ending should have the character freeze in their pose with slight recoil » (d0cter_oof, r6)
- « for the impact, try to freeze the character for 2-3 frames » (phantasmability, r7)

**Viser : le coup ne va pas là où il doit aller**
- « That's not a punch animation, it's just bending over to touch its knee […] make the arm stop before it hits the knee » (IceTheOneAndOnly, r1)
- « It looks as if he's punching at the shoulders, with the uppercut not going anywhere. Rotate the torso even more and aim the punches at the center. I think if you were to put a block in front of him to act as a sort of "punching bag" that would help you be on target more. » (Shift4D, r13)
- « Make the arm go forwards, it looks kind of like a block right now » (BurstKUN, r12)
- « the direction of the sword needs to point forward, and not upward like in your animation » (vipkute0057, r2)

**Pas assez exagéré**
- « if an animation isnt exxagerated enough it looks terrible, especially for r6 avatars and their lack of bends » (PlayerTrillion, r1)
- « Some animations are just too subtle or don't have the body parts move far enough. Try more extreme positions and see what that looks like. Some games literally have the character stand in a slightly unnatural position but because this only happens for a few frames you don't notice. » (C_Corpze, r3)
- « for rigs with less joint that the amount of joints a human has, exaggerating the movement helps the character feel more alive. This is a common practice in Bionicle stopmotions » (Babybunnyiscute19, r4)

**Ce qu'on voit contre ce qui existe**
- « I feel like the torsos arent moving. I see that they are but it still feels like they are facing the front still […] This could be just because the rig is all one color. » (Hazelfluff, r7)

**Trop vite / trop lent : lisibilité**
- « also slow down the animation, I had to set the speed to 0.25 to actually understand what was happening » (Pokemoncraft5290, r3)
- « Slow it down a bit so players will see the animation more clearly like in the reference. » (SMUSH21, r11)
- « The part where the sword flicks over the characters head seems a tad to quick, compared to the motion before it. » (pjhinthehouse, r11)

**Les membres détachés du corps (R6)**
- Pour : « you can still utilize good animation principles on R6 […] move the character's full arm based on the position of a real person (or R15 character)'s forearm […] It just requires being willing to disconnect the "shoulder" of the arm from the torso. » (fungi3432, r1)
- Pour : « Detaching a limb from an R6 character's body is a good option when exaggerating their motion » (Babybunnyiscute19, r4)
- Contre : « Pretty good for anything except actual gameplay. To make it compatible and gameplay friendly, I would not disconnect the limbs and drag them too far away from the torso. » (AvailableFunds, r7)
- Contre : « rotate the joints towards the torso when they move far forward so they don't look like they're going to fall off » (XxMr_AltxX, r13)
- Technique : « pretend that the knees for the R6 rig is located at the hip » (Babybunnyiscute19, r4)

**Méthode pour s'améliorer**
- Pas de temps de lecture image par image : « Playback at x0.5 or x0.25 […] use . and , to move forward and backwards through frames […] Setup your editor's view angle to match the reference's » (spelled_ayayron, r3).
- « On what frames does the object change during its action, and how large of a change was it since the last frame? This is literally the core of animation. » (spelled_ayayron, r3)
- « Punch the air for a while and you'll see what I mean. » (LucensCat, r2)
- « filming yourself doing these moves or finding a video to replicate » (pjhinthehouse, r1)
- « I picked up a wooden stick and figured out what parts I was swinging. » (GolgiToad, r6)
- « Try to avoid three-keyframe animations, since it doesn't leave room for detail. » (iGottic, r12)
- « Analyze the motion and try to decipher when the action is speeding up or slowing down and then apply that to your rig and tinker with it until it looks "right". » (mewnmowse, r4)

**Au-delà de l'animation : la sensation de combat**

Le fil « How would I go about making my combat feel more impactful? » (r3) répond surtout hors animation :
- tremblement de caméra, champ de vision (FOV), correction de couleur ;
- sons ;
- recul (knockback), particules vers l'extérieur ;
- « make sure the particles are persistent with the attacks » (JakeTheNewb) ;
- « I would also remove the vignette. It looks like you're being damaged, not damaging someone else. » (GibusWielder).

Sur TSB : « I think the reason TSB has more impact is because of the light camera shake » (shakability, r5). Le fil r5 montre aussi que la sensation « choppy » peut venir **du code** plutôt que de l'animation :
- délai entre deux anims : Deathhunter1249, r5 #8 ;
- fondu : « oldAnim:Stop(FADE_TIME) newAnim:Play(FADE_TIME) », L0chlainn, r4 ;
- priorités identiques : largrgy, r10 #19.

### B3. Ce qui progresse entre deux essais (lu)

1. **Pish85 (r2, « Feedback on my punch animation »).**
   - Critique : « adding a little bit of windup and easing the punch out more smoothly rather than having a sudden stop at the end ».
   - Nouvelle version, réponse : « Wow, already looks much more impactful with the windup! ».
   - Deuxième conseil : fin en crochet, « have it slow down and turn inwards ».
   - Version finale, en ses mots : « This, is the result, of Easing Styles and Directions. And also of me actually reading the documentation instead of mindlessly scrolling on youtube. »
   - Ce qui a changé : l'anticipation, puis la fin qui ralentit et tourne.
2. **ZensStarz**, sur plusieurs fils (r1, r2, r6 ; ses messages y sont signés ZensStarz).
   - r1, première version : « movements start and end quite abruptly » (fungi3432).
   - v2 : « make the ending of the animation to be a bit more rigid, and hold a little more recoil, whilst trying to make the start-up/wind-up animation have a bit more energy ».
   - Nouvelle critique : « The way they just cut out of the move lessens the impact » (Xenonic_778) et « What's missing is the natural preparation […] follow-through before slightly recoiling » (pjhinthehouse).
   - r2 : « linear with a short pause » (0BSCURlTY), puis « legs kinda fly, more up down torso movement » (iM1GHTB3DANI). Correction → « looks much better. (still room 4 improvment but crazy good changes ».
   - r6, uppercut : « increasing the 'force' of the punch, by making the fist come up faster » → « now the animation as a whole looks like the character going into a spasm » → « Decided to make the start of the anim slower then the ending just be a jolt and it look even better ».
   - Déduit : **il découvre par l'essai que la vitesse n'a de sens que par contraste.** Tout accélérer donne un spasme ; un début lent, puis un coup sec, donne de la force.
3. **skutebebe (r4, rechargement d'arme).** Avant : linéaire. Après, OofDestroyer25 lui répond ceci :
   - « Keyframe spacing – The animation goes from slow to fast very quick » ;
   - « Hand Position – When you keep your right arm static, it removes an entire other half of the animation » ;
   - « Snap – Add power to every keyframe […] add a pause when the player gets the mag under the chamber, and then make them thrust it in ».
   - Déduit : **pause, puis poussée.** C'est la tenue suivie du coup sec, appliquée à un geste banal.
4. **rayanl12om (r1, r3).**
   - Réponses : « I don't agree with the weird poses », « If I slow down It will looks bad, a fight animation is fast not slow ».
   - DoggoAnim lui montre « My version » ; il répond : « Omg, thank you! This will be very helpful […] Your version has feet sliding but this is good! ».
   - Déduit : on progresse plus vite quand on accepte de **ralentir pour lire** (Pokemoncraft à 0.25x) avant de juger la vitesse finale.
5. **Klllua99 (r12).**
   - Essai 1 : « looks more like a walk animation ».
   - Essai 2 : « i don't even know what this is ».
   - Déduit : sans modèle de ce qu'est un coup (où va le poing, que fait le corps), changer des réglages ne suffit pas.

### B4. Les désaccords entre critiques (lu)

Ce ne sont pas des erreurs. Ce sont des **choix** qui dépendent de l'usage.

- **Rapide ou lent ?**
  - « If it's a pvp attack or something then I would speed it up a bit but if it's some animation or scene then it's fine » (isaiahbur, r1).
  - « if it were to be used in a cutscene I think it would work out well » (Messeras, r1).
  - « it's a very fast paced fighting game […] the hit frames are preferably within the first 30-40 […] It's not a realistic boxing game » (xnSly, r7).
- **Réaliste ou exagéré ?**
  - « normally someone wouldn't lean into a punch like that […] Feet planted, Faster Animation, Less leaning » (nino133, r1).
  - Contre : « if an animation isnt exxagerated enough it looks terrible » (PlayerTrillion).
  - « A cartoony game would require more exaggerated animations […] but a realistic, gritty game would not. » (Castlemore, r3).
- **Animer les jambes ?** Non pour un M1 de jeu (pour laisser jouer la marche). Oui pour un coup spécial ou une cinématique.
- **Détacher les membres ?** Oui pour la cinématique et l'exagération ; non pour le gameplay, à cause des hitbox et de la crédibilité.

Déduit : ces désaccords recoupent **exactement** la distinction que Milan pose dans son dernier message (26/09 11:45) : « on fait bcp de cinématique et ya bcp de ref qui sont en vision jeux donc dif notamment comme les M1 M2 M3 ».

---

## 3. Confrontation avec les fichiers pros (mesuré)

Je vérifie sur de vrais fichiers ce que le forum affirme.

**TSB « M1 »** (`tsb_M1.png`, 7 clés, 0,43 s, 60 i/s)

- **Jambes : jamais posées** (mesuré : « jamais posées ici : JD JG »). Ça confirme melvinpetersen, F0xBirdman et MonkeyIncorporated : dans le M1 de TSB, les jambes sont laissées à l'animation du dessous.
- **Torse (lacet) :**

  | Clé | i0 | i6 | i8 | i10 | i14 | i20 | i26 |
  |---|---|---|---|---|---|---|---|
  | Lacet | +48 | +6 | −28 | −44 | −63 | −70 | −65 |

  Amplitude : **118°** entre i0 et i20, puis **retour de 5°** (−70 → −65). Le buste tourne énormément, puis revient un peu : un léger dépassement puis retour (ItzBloxyDev, r4 : « overshoot the goal and then move back a bit »).
- **Espacement des clés :**

  | Phase | Clés | Écart |
  |---|---|---|
  | Charge | i0 → i6 | 6 images |
  | Frappe | i6 → i8 → i10 | 2 images |
  | Frappe | i10 → i14 | 4 images |
  | Retour | i14 → i20 → i26 | 6 images |

  Des clés serrées là où ça va vite, larges pour le retour. C'est l'espacement que réclament C_Corpze et d0cter_oof.
- **Bras qui frappe :** le bras gauche (bleu), « coup az » de −82 (i0, derrière) à +119/+125 (i14-i20, devant). L'autre bras (vert) part dans l'autre sens : le corps tourne comme un tout.
- **Clés décalées (vu sur la ligne « rythme ») :** le torse a une clé seul à i20, et le bras gauche seul à i10 ; la tête n'est posée qu'à i0, i8, i14, i26. Le rig n'est pas clé « en bloc ».
  - C'est le contraire de la timeline du débutant (92.5 s), où toutes les pistes étaient clées aux mêmes images.
  - C'est ce que dit PersonifiedPizza : « starts each motion at different times ».
- La fin du bras ralentit : poing presque immobile entre i14 et i26, pendant que le torse fait encore son dépassement et son retour.

**Pack « [2] M1_1 »** (40 clés, 0,65 s)

- **Une clé à chaque image** : animation « cuite » depuis Blender. Yarik_superpro (r9) l'évoque : « Baked result would have too much frames ».
- Jambes jamais posées, là aussi.
- Torse (lacet) : 0 → −98 (i10) → +58 (i19-20), puis une dérive lente +58 → +42 → +45 sur les 20 dernières images.
- **La fin n'est jamais figée** (mesuré). C'est « there are no points in the anim where a keyframe is going to itself, so everything is always moving » (0BSCURlTY).

Déduit : **les reproches du forum ne sont pas des opinions en l'air.** Ce que les critiques réclament (tout le corps tourne, clés serrées au coup et larges au retour, dépassement puis retour, pas d'arrêt mort, jambes libres en jeu) se **mesure** dans deux fichiers de pros.

---

## 4. Les questions qu'un animateur se pose en regardant une animation

Chaque question est tirée de critiques réelles. La colonne de droite indique si elle ressemble à ce qu'a dit Milan (ses mots exacts, `milan_verbatim.jsonl`).

| # | Question que se pose l'animateur | Citation source (lu) | Mots de Milan qui y ressemblent |
|---|---|---|---|
| Q1 | Est-ce que tout le corps participe, ou seulement les bras ? | « The arms just being animated seems a little unrealistic » (SubtotalAnt8185) ; « one body part doesn't affect the others » (IceTheOneAndOnly) | « Non mais tu utilise pas le corps dj peros » (03/09) ; « enft tu as a anime que les bras encore une fois j'ai l'impression » (25/09) |
| Q2 | Que font les jambes ? Portent-elles le coup, ou sont-elles collées, en patins, prêtes à tomber ? | « legs are glued together » (8unii) ; « on ice skates » (Archie) ; « going to fall over » (Pro3taco) ; « the leg in the floor is sliding » (iM1GHTB3DANI) | « Tu oublies de utiles les jambes » (03/09) ; « les pieds tjrs trop encré dans le sol et pas en mouvement avec les geste » (05/09) ; « quand tu met des coup les axes des jambes change et le jeux de jambe change selon l'envoi de la charge du poing » (05/09) |
| Q3 | Est-ce que je vois venir le coup ? Y a-t-il une vraie préparation ? | « the punch just kinda happens out of nowhere » (Pokemoncraft5290) ; « wind up the punch more, then quickly throw it foward with a powerful release » (synical4) | « il donne pas le give d'un coup chargé » (04/09) ; « le perso charge son poing, il arme son poing le ramenant à l'arrière et en tournant son bust » (26/09) |
| Q4 | Où va le poing ? Vers la cible, au centre, ou vers le bas, le genou, l'épaule ? | « it's just bending over to touch its knee » (IceTheOneAndOnly) ; « punching at the shoulders […] aim the punches at the center » (Shift4D) ; « Make the arm go forwards » (BurstKUN) | « il manque les épaules on dirait que le coup pars du bas alors que il doit allez droit » (03/09) ; « parce que tu donnz dzs coup vers le bas » (24/09) ; « les coup parte tjrs du bas » (24/09) |
| Q5 | Est-ce que ça frappe, ou est-ce que ça tapote ? Y a-t-il de la force dans le recouvrement ? | « lightly tapping something instead of punching it » (realknife) ; « wipping food off their cheeks » (Tornado_chaser04) ; « flailing arms rather than punches » (Toefl) | « Le perso met juste une espèce d'élancement du bras dans tes rendue » (04/09) ; « ça manque d'un ressenti de puissance » (24/09) |
| Q6 | Est-ce que la fin existe ? Y a-t-il un suivi du mouvement, un recul, ou est-ce que ça coupe net et retourne à l'idle ? | « The way they just cut out of the move lessens the impact » (Xenonic_778) ; « hands just seem to stop as if they loose all momentum » (Bovious) ; « you dont want the character to immediately go into idle » (urgentnotice) | « Ça manque de frame d'un début et d'une fin » (23/09) ; « ça manque de fluidité, de idle pose » (05/09) |
| Q7 | Est-ce que tout va à la même vitesse ? Où est le contraste lent/rapide ? | « everything is happening basically at the same speed » (mewnmowse) ; « start of the anim slower then the ending just be a jolt » (ZensStarz) ; « slow → fast → slow » (Rymxi) | « C bcp trop rapide on ne lit pas assez les mouvement » (03/09) ; « au niveau du rythme cv » (24/09) |
| Q8 | Est-ce linéaire, robotique ? Chaque partie part-elle au même instant ? | « all linear with a short pause on the keyframes » (0BSCURlTY) ; « the character starts each motion at different times » (PersonifiedPizza) | « pq tout à l'aire mécanique dans tes rendues ? » (23/09) ; « c pas 100% robotic mais sa manque d'une touche » (24/09) |
| Q9 | Est-ce assez exagéré pour du R6, qui n'a pas de coudes ni de genoux ? | « if an animation isnt exxagerated enough it looks terrible, especially for r6 » (PlayerTrillion) ; « Try more extreme positions » (C_Corpze) | « tu abuse pas assez le mouvement style manga » (01/09) ; « ça manque d'exagération » (03/09, 23/09) ; « même un coup simple n'est pas coup simple genre y'a une anatomie et une règle différente » (24/09) |
| Q10 | La pose est-elle intéressante ou « stickman » ? Y a-t-il de la profondeur ou tout est-il dans le plan de l'écran ? | « -boring sameside posing -looks like a stickman » (Xoaterz, vidéo 500 s) | « charge en croix symétrique » (cité dans l'étude existante, défaut relevé par Milan) |
| Q11 | Est-il accroupi en permanence ? | « -perma crouched position » (Xoaterz) | « il est accroupie » (24/09) ; « les bras sont trop vaut il esr accroupis er pas en trasnfere de poids » (24/09) |
| Q12 | La pose tient-elle en équilibre ? La tête est-elle au-dessus du pied qui porte ? | Ligne d'équilibre (Xoaterz, 516-519 s, vu) | « pas en trasnfere de poids » (24/09) |
| Q13 | Est-ce que je lis le mouvement, ou existe-t-il sans se voir ? | « I see that they are but it still feels like they are facing the front still » (Hazelfluff) ; « slow down […] 0.25 to actually understand » (Pokemoncraft5290) | « Je vois aucun changement » (25/09, 26/09) |
| Q14 | Est-ce pour le jeu ou pour une cinématique ? | « If it's a pvp attack […] speed it up […] if it's some animation or scene then it's fine » (isaiahbur) ; « Pretty good for anything except actual gameplay » (AvailableFunds) | « on fais bcp de cinématique et ya bcp de ref qui sont en vision jeux donc dif notamment comme les M1 M2 M3 » (26/09) ; « caméra jeux ou cinéma tout dépend de la technique » (24/09) |
| Q15 | Le coup est-il « raccord » avec ce qui précède ? L'enchaînement a-t-il un sens ? | « He looks like he's going to do a regular punch, and transitions to an uppercut randomly » (Pokemoncraft5290) ; « It doesn't transition into the kick very well » | « on dirait un enchainement d'uppercute mais en meme temps coup droit » (24/09) ; « il reste des problèmes sur l'enchaînement » (24/09) |
| Q16 | Les membres restent-ils rattachés de façon crédible, ou sont-ils détachés avec intention ? | « rotate the joints towards the torso when they move far forward » (XxMr_AltxX) ; « disconnect the "shoulder" » (fungi3432) | « le bras se déboîte vers l'arrière et avance vers l'avant, ne te fis pas une animation humaine » (04/09) |
| Q17 | La tête a-t-elle une intention, ou erre-t-elle ? | « The head is just looking around, give it more purpose […] mainly looking forward save for a dramatic head turn » (Hazelfluff, r13) ; « staring into your soul » (IceTheOneAndOnly, r12) | aucun équivalent trouvé |
| Q18 | Les effets tombent-ils au bon moment ? | « particles sometimes appear before the animation plays » (404problems) ; « Your i-frame for the clap is very off sync, it looks delayed » (airbowscopegothack, r11) | « le dragon apparaît 0,5 seconde et pas au bonne endoirt » (25/09) |
| Q19 | Comment le vérifier ? En ralenti, image par image, en le mimant, avec une cible posée ? | « Playback at x0.5 or x0.25 » (spelled_ayayron) ; « Punch the air » (LucensCat) ; « put a block in front of him » (Shift4D) | « Compare visuellement notre coup au multiple ref de poing chargé » (26/09) |

**Bilan.** Q1 à Q9, Q11, Q13, Q14 et Q15 ont un équivalent presque mot pour mot chez Milan (déduit, sur les citations ci-dessus).
Autrement dit, **Milan fait déjà la critique d'un animateur expérimenté du DevForum**, dans son vocabulaire à lui. Quand il dit « le coup part du bas », c'est la question Q4 que pose Shift4D. Quand il dit « tu n'animes que les bras », c'est Q1.

---

## 5. Grands enseignements, transversaux (des apprentissages, pas des règles)

1. **Chez ces pros, le coup se raconte par ses deux bouts, pas par son milieu** (vu à 15 i/s).
   - Xoaterz : tenue d'environ 0,35 s, puis 1 image N/B + 3 images de glitch, puis pose basse tenue environ 0,35 s.
   - CrashMagician : charge d'environ 0,9 s, puis 1 image blanche, puis conséquence.
   - Ici, l'animateur ne dépense rien sur la traversée du bras, parce que l'œil ne la lit pas à cette vitesse. Il met tout dans la pose d'avant et la pose d'après.
2. **La pose se construit depuis le buste** (vu, Xoaterz 489-492 s et 524-534 s). L'animateur tourne et incline le torse avant tout le reste, parce que c'est lui qui donne la direction de la silhouette. Ensuite il déplace (et pas seulement tourne) la jambe libre, puis place les bras sur la diagonale.
3. **Il vérifie sous un autre angle et contre la clé d'avant** (vu : caméra au ras du sol à 534.5-536.5 s, pelure d'oignon à 539.5-541.75 s). La pose qu'on règle dans la vue de travail ne suffit pas.
4. **Les clés décalées font la différence entre un robot et un corps** (mesuré sur TSB M1, vu sur la timeline du débutant). Chez le débutant, tout est clé aux mêmes images. Chez TSB, le torse a sa propre clé à i20, la tête est posée plus rarement, le bras gauche seul à i10.
5. **Serré au coup, large au retour** (mesuré, TSB M1 : écarts de 2 images au coup, 6 au retour). C'est ce que les critiques demandent en mots : « make the movement really fast, when the fist hits, make it stop abruptly. After that make the fist slowly retract and relax ».
6. **La contradiction « arrêt brusque / pas d'arrêt brusque » se résout par le contexte** (déduit, sur B2 et §3).
   - L'arrêt net est juste **au contact**, parce que le poing rencontre quelque chose.
   - L'arrêt net est faux **quand rien n'est touché** : la main s'arrête « in a seemingly arbitrary point in the air ».
   - Après le contact, le corps continue (TSB : le torse fait encore −70 → −65) et ne revient pas en bloc à l'idle.
7. **Un seul personnage bouge à la fois dans un échange rapide** (vu, Thundey 187.30-187.57 s). L'animateur fige l'un pendant que l'autre agit, pour que l'œil sache où regarder.
8. **La vitesse n'existe que par contraste** (lu, trajectoire de ZensStarz). « Plus rapide partout » donne un « spasm ». « Début plus lent, fin en coup sec » donne de la force. Côté cerveau, ça rejoint la tenue suivie du coup sec déjà connue, et c'est ici confirmé par quelqu'un qui l'a découvert en essayant.
9. **Une animation faible peut être sauvée par la caméra et le montage, et une bonne animation peut être perdue par eux** (vu). Le combat du débutant plaît grâce aux amorces et au N/B. Hazelfluff dit qu'un torse qui tourne « feels like facing the front » à cause de la couleur unie du rig. Ce que Milan appelle « aucun changement » peut être **un problème de lecture** autant qu'un problème de pose.
10. **Pour le jeu et pour la cinématique, les mêmes principes n'ont pas les mêmes réglages** (lu, B4 + mesuré, §3). En M1 de jeu : jambes vides, anim courte (moins de 0,5 s pour TSB M1), membres près du torse. En cinématique : corps entier, membres détachés, tenues longues, caméra qui raconte.
11. **En R6, ce que ces animateurs attendent de l'exagération compense l'absence d'articulations** (lu : PlayerTrillion, Babybunnyiscute19 avec les Bionicle). Ils traitent le genou comme s'il était à la hanche, et l'avant-bras comme s'il était le bras entier (fungi3432). Ils acceptent de décrocher l'épaule en cinématique.
12. **Les débutants progressent quand ils regardent image par image et miment le geste** (lu : spelled_ayayron, LucensCat, GolgiToad, pjhinthehouse). Les conseils « change d'outil » (Blender, Moon, R15) reviennent souvent, mais les plus expérimentés les jugent secondaires : « There are much more important things to animations than the software you use » (urgentnotice, r2) ; « Switching tools won't help much if he don't know the basics » (vipkute0057).

---

## 6. Ce que je saurais REFAIRE maintenant en R6, et ce que je ne saurais pas

### Je saurais

- **Un M1 de jeu dans l'esprit de TSB.** Environ 26 images à 60 i/s, avec 7 clés à peu près à i0, i6, i8, i10, i14, i20, i26.
  - jambes non clées ;
  - torse qui tourne d'environ 110-120° du début au coup, avec un retour de quelques degrés à la fin ;
  - bras qui frappe partant de derrière le buste (« coup az » négatif) et finissant devant ;
  - l'autre bras qui recule ;
  - tête clée moins souvent ;
  - le torse garde une clé à lui après que les bras se sont arrêtés.

  Tout ça est mesuré sur le fichier. En revanche, **je ne connais pas les courbes d'interpolation de TSB** : la planche montre les clés, pas les courbes.
- **Poser à la manière de Xoaterz.**
  1. Le torse d'abord : rotation de 3/4 puis inclinaison franche.
  2. Une jambe d'appui sous la tête (ligne d'équilibre), l'autre translatée puis tournée (genou haut ou fente longue).
  3. Les bras sur une diagonale en profondeur, un devant et un derrière, jamais dans le plan de l'écran.
  4. Vérifier depuis une caméra au sol et contre la clé d'avant.
- **Un coup de cinématique qui ne montre pas la traversée.**
  1. Tenue de charge de 0,35 à 0,9 s, caméra basse et penchée.
  2. 1 image d'impact (N/B ou blanc) + 2 à 3 images de flou ou d'aberration.
  3. Coupe sur le contact ou la conséquence.
  4. Pose d'après plus basse que la pose d'avant, tenue environ 0,35 s.

  Ces durées sont mesurées à l'œil sur une vidéo YouTube remontée ; les images peuvent avoir sauté.
- **Faire une passe de critique** sur n'importe quelle animation avec les questions Q1-Q19, et **traduire les mots de Milan** en questions précises (voir §4).

### Je ne saurais pas (encore)

- Dire **ce que Xoaterz explique oralement** pendant qu'il repose : pas de son.
- Juger une **animation du forum** : je n'en ai vu aucune.
- Donner les **courbes** d'interpolation (le forum parle de cubic, back, elastic, quad in-out, « None » ; aucun graph editor n'apparaît à l'écran).
- Trancher **avec certitude** l'orientation du bras long de la pose ✓ « Serious Punch » (voir A4).
- Dire si le « 5-10-15 » de @zanpiedad (clés tous les 5 sans easing) produit mieux que l'easing : c'est un avis, jamais montré.

---

## 7. Surprises et contradictions avec ce que le cerveau croyait

1. **Les deux études du cerveau se contredisent sur la pose ✓** : « bras ramené en arrière et plié » contre « bras tendu à l'horizontale vers l'avant ». Je pense qu'elles décrivent chacune un bras différent (déduit, A4).
   Surtout, la règle R2 de `rapport_video_critique_poses.md` (« bras qui frappe armé *derrière* l'épaule ») a pu alimenter l'idée d'un bras tendu derrière. Milan l'a explicitement rejetée : « dans aucune le bras est tendu derrière » (26/09). **La pose ✓ n'a pas de bras tendu derrière** dans ma lecture : le bras qui frappe y est court, replié.
2. **Le cerveau a transformé cette vidéo en « Règles » R1-R8** (« Jamais de pose en croix », etc.). Or le contenu est surtout une **méthode de travail** : ordre de pose, vérification sous d'autres angles, pelure d'oignon. Et c'est un parcours d'apprentissage. Milan refuse les règles gravées. Je propose de relire ces R1-R8 comme des questions (Q10, Q11, Q12).
3. **« Le coup n'est pas montré. »** Le cerveau cherchait à rendre visible la traversée du bras (smears, frappe en 2 images, etc.). Chez CrashMagician et Xoaterz, **elle n'est pas vue du tout** : elle est remplacée par des images d'effet ou une coupe. Ça ne vaut pas pour le jeu, où la caméra ne coupe pas.
4. **Les jambes vides dans les M1.** Le cerveau le savait déjà (le prompt le rappelle). Le forum ajoute une nuance : **c'est un choix d'architecture de jeu, contesté par les critiques** (8unii, Archie, IceTheOneAndOnly), parce que sur une vidéo seule on voit les jambes mortes. Pour une cinématique, ce n'est pas une référence à suivre.
5. **« Aucun changement »** (Milan). Hazelfluff montre qu'un mouvement réel peut ne pas se voir (rig d'une couleur, torse qui tourne mais « facing the front »). Ça rejoint l'observation de `etude_complete_dehapy.md` sur la taille du personnage à l'écran.
6. **Le forum dit la même chose que Milan.** Presque toutes ses remarques ont un équivalent dans la bouche d'animateurs du DevForum (§4). Ses retours ne sont donc pas « des goûts » : ce sont des critiques d'animateur standard, dans ses propres mots.

---

## 8. Non couvert, et pourquoi

- **Les vidéos et images jointes aux fils du forum** : hébergeur S3 bloqué. Je n'ai que le texte.
- **Le son de la vidéo** : pas de piste son exploitée. Aucune explication orale de Xoaterz.
- Dans la vidéo, les digressions ont été vues à 1 i/s seulement, sans densifier : Bubble Gum Simulator (214-229 s), mèmes, Discord de commande et paiement (736-771 s), jeu du client (775-782 s), shorts d'autres créateurs (844-853 s). Rien d'animation n'y était visible à 1 i/s.
- Les passages 420-481 s et 544-616 s ont été vus à 1 i/s. Je ne les ai pas redensifiés : la semaine 2 hors appel. Le Flip Punch à 459-460 s avait déjà été étudié à 30 i/s par l'étude existante, et je ne l'ai pas refait.
- Les autres animations des fichiers pros : hors de mon angle.

---

## Vérification adverse

Vérificateur adverse, 2026-09-26. J'ai tout refait moi-même, sans reprendre les extractions du lecteur. Vidéo : ffmpeg à 30 i/s avec le temps inscrit sur chaque image (`sheet.py`). Planches : `planche_cles.py` relancé sur les deux .rbxm. Forum : grep dans r1 à r15, avec le contexte autour de chaque citation. Milan : grep dans `milan_verbatim.jsonl`. Tout ce que j'ai produit est dans `c4/frames/verif_B3_apprendre_et_critiques/` : s181, s184, s187, s090, s418, s488, s494, s520, f92_7_tl, f503_bas, tsb_M1.json, pack_M1_1.json. Je n'ai rien modifié dans le dépôt.

### Verdicts (10 apprentissages vérifiés)

**1. « Le coup se raconte par ses deux bouts » (Xoaterz, CrashMagician) : NUANCÉ.**
Ce que j'ai regardé : 181,5 à 186,8 s, image par image à 30 i/s (s181.png, s184.png).
- Confirmé : tenue de 181,63 à 181,93 s (le poing bouge un peu à 181,93-182,00), puis 1 image N/B à 182,033.
- Le glitch dure 6 images à 30 i/s (182,067 à 182,233), et non 3. Il y a peut-être 3 dessins doublés.
- Surtout, le lecteur a raté trois choses :
  - une **image de contact** à 182,267 : le poing est écrasé sur le visage, avec des bouffées ;
  - un **second coup** : gros plan de 182,30 à 182,50, puis une 2e image N/B à 182,533 ;
  - **environ 1 s de vol de la victime** (182,6 à 183,6), dans des images blanchies, puis une roulade au sol.
- La « pose d'après plus basse » (183,63 à 184,07) est la réception accroupie de la **victime** (cheveux orange). Ce n'est pas la pose d'après de l'attaquant.
- CrashMagician : enroulement de 184,10 à 184,47 s (12 images à 30 i/s, 2 plans), tenue de charge 184,50 à 185,50 (1,0 s). À la sortie : 1 image traînée (185,50), 1 presque blanche (185,533), 2 blanches (185,567 et 185,600), puis la victime dans l'explosion à 185,633. Le lecteur disait 1 image floue et 1 image blanche.

Correction : c'est la traversée du bras de l'attaquant qui n'est jamais montrée, pas « le milieu ». Xoaterz montre l'image de contact, un 2e coup et environ 1 s de conséquence sur la victime. Le temps est dépensé avant le coup et sur la réaction, pas seulement sur « la pose d'avant et la pose d'après ».

**2. TSB M1 : 7 clés, lacet 118°, écarts 6/2/2/4/6/6 : CONFIRMÉ, avec deux corrections.**
Ce que j'ai regardé : `planche_cles.py --rbxm tsb_anim.rbxm --nom M1`, plus une lecture brute des keyframes avec `corpus.load_rbxm_sequences`.
- Confirmé : clés posées à i0, 6, 8, 10, 14, 20 et 26, et lacet +48, +6, −28, −44, −63, −70, −65.
- La liste annonce « 8 clés ». La 8e est un keyframe **vide** à 0,422 s, le marqueur `end`. Les marqueurs sont `hitreg` à i10 et `end` à 0,422 s.
- « L'autre bras recule » est faux en azimut : le bras droit passe lui aussi de coup az −19 à +113. Ce qui recule, c'est l'épaule droite (« épaule D reculée » de −2,19 à +2,46).
- Oubli : **les deux bras sont translatés** (Position non nulle dans les Poses). Le bras gauche est décalé d'environ 0,3 stud à i0 et d'environ 0,9 stud à i10 (−0,88, −0,11, −0,22). Le bras droit l'est d'environ 0,5 à 0,6 stud de i8 à i26. Le torse est translaté aussi (Y −0,23 puis +0,18).

Correction : la pro détache légèrement les bras même dans un M1 de gameplay.

Pack M1_1 : je confirme 40 clés (une par image), les jambes absentes et le lacet +58, puis +42 à i28-29, puis +45. Mais de i34 à i39, le lacet reste à +45 et le penché ne varie que de 1°. C'est un amorti qui se pose, pas « ne se fige jamais ».

**3. Timeline du débutant : « toutes les pistes clées aux mêmes images » : NUANCÉ.**
Ce que j'ai regardé : l'image à 92,7 s en 1280 px, et un zoom sur la fenêtre Moon (f92_7_tl.png).
- Il y a bien 5 colonnes alignées, mais sur Torso, Right Arm, Right Leg, Left Arm et Left Leg seulement.
- **La piste Head n'a aucune clé** (juste un petit repère à 0). Le lecteur disait « torse, bras, jambes et tête » et « 5 à 6 colonnes ».
- Les écarts entre colonnes sont irréguliers (≈ 0, 12, 20, 32, 40 images).
- La citation de PersonifiedPizza (r12:174) est ambiguë. Elle suit « Make the animation a bit more fluid – » et continue par « Creatures tend to predict movements and start them slightly before ». On peut la lire comme un défaut constaté (des départs désordonnés, à corriger par l'anticipation), pas comme un éloge des clés décalées.
- Dans TSB, i10 pose le torse ET le bras gauche. Le bras gauche n'y est pas « seul ».

**4. « Arrêt brusque au contact, faux dans le vide » : NUANCÉ (les citations sont exactes, la lecture est à moi).**
Ce que j'ai regardé : r3:205-206 (C_Corpze), r7:24 (phantasmability), r6:50 (d0cter_oof), r1:79 (Bovious), r2:206 (LucensCat), en entier.
- Toutes les citations sont exactes.
- Mais LucensCat se termine par « (unless it's meant to be more of a straight punch instead of a hook, in which case you shouldn't have it turn really) ». La distinction que fait la source est **crochet contre direct**, pas « touche contre vide ».
- d0cter_oof dit aussi « move slightly forward to show the momentum », que le lecteur ne cite pas.
- C_Corpze ajoute qu'on peut « disable interpolation for a brief moment ».

Correction : « touche ou pas » reste une hypothèse du lecteur. Elle est plausible, mais aucun critique ne la formule.

**5. « La vitesse ne se sent que par contraste » (ZensStarz, skutebebe, Pish85) : NUANCÉ.**
Ce que j'ai regardé : r6:138-146, r4:213-241, r2:206.
- ZensStarz : c'est exact. Il n'accélère pas « tout le coup » de lui-même : il suit ItsCatalyst (« making the fist come up faster »), obtient le « spasm », puis ralentit le départ et finit sur un « jolt ».
- **OofDestroyer25 → skutebebe parle d'un RECHARGEMENT d'arme**, pas d'un coup. Dans le même message, il reproche aussi l'inverse : « The animation goes from slow to fast very quick, making it feel unrealistic ».

Correction : le contraste aide, mais un passage lent→rapide trop brutal est lui aussi critiqué. Il faut retirer skutebebe des exemples de coups.

**6. « 13/19 questions presque mot pour mot chez Milan » : NUANCÉ.**
Ce que j'ai regardé : grep de chaque formule dans `milan_verbatim.jsonl`.
- Les phrases de Milan existent, avec les dates annoncées :
  - « tu utilise pas le corps » : 03/09 18:17 ;
  - « pars du bas alors que il doit allez droit » : 03/09 20:19 ;
  - « il est accroupie » : 24/09 ;
  - « Ça manque de frame d'un début et d'une fin » : 23/09 15:50 ;
  - « espèce d'élancement du bras » : 04/09 19:34 ;
  - « vision jeux […] M1 M2 M3 » : 26/09 11:45 ;
  - « dans aucune le bras est tendu derrière » : 26/09 09:04.
- Les phrases du forum existent aussi.
- En revanche, « pars du bas / doit aller droit » (une **trajectoire**) ↔ « punching at the shoulders […] aim at the center » (une **cible en hauteur**) n'est pas une équivalence. « Presque mot pour mot » exagère : ce sont des idées proches.

**7. Serious Punch ✓ : « le bras court est le bras qui frappe, replié » : NUANCÉ, en partie invérifiable.**
Ce que j'ai regardé : l'image à 503,5 s, en recadrage agrandi (f503_bas.png).
- Je vois bien le visage tourné vers la gauche de l'image et un bras long horizontal vers la gauche, donc vers l'avant.
- Je vois aussi un bras court en haut à droite, en arrière du buste, et une jambe avancée, grosse à l'image.
- Mais le bras court est **en raccourci**. Sur une image fixe, je ne peux pas distinguer « plié » de « tendu en arrière, dans la profondeur ».

Correction : ne pas affirmer « replié ». Il faut un autre angle, ou la vidéo de Xoaterz, avant de l'opposer à Milan.

**8. « Les reproches portent surtout sur les jambes et le torse » : RÉFUTÉ (les comptes sont justes, la conclusion non).**
Ce que j'ai regardé : grep sur `all_r.txt` (3165 lignes, 794 messages, confirmé) et sur chaque fil séparément.
- Je retrouve legs/leg 92, camera 49, R15 98, choppy 19 et stiff/robotic 22.
- Mais les propres chiffres du lecteur mettent **easing (104) et R15 (98) au-dessus des jambes (92)**.
- De plus, les jambes sont gonflées par des fils techniques : r8 (fiche du rig V2.22 : 14 mentions leg, 12 torso) et r10 (raycasts de pieds : 11 leg, 8 foot).

Correction : le thème le plus fréquent est la **courbe et l'accélération** (easing, linear, choppy, stiff). Il faudrait classer les messages un par un, et ne pas compter les mots.

**9. DeHapy « découvre la translation » (1,17, 7,81 puis 10,72 studs) : NUANCÉ.**
Ce que j'ai regardé : 417,5 à 422,5 s à 2,5 i/s (s418.png).
- C'est **un seul glissement continu** de la flèche verte. L'affichage monte −2,16, 3,7, 6,08, 7,81, 9,04, 9,92 puis 11,1…, et une explosion (un gag monté) suit.
- Ces chiffres sont des instantanés d'un même glissement de plus de 10 studs, pas trois essais.
- Ce n'est pas un exemple d'exagération R6 à la « Bionicle ».

La vraie donnée pro sur ce sujet est dans TSB M1 (verdict 2) : environ 0,5 à 0,9 stud de translation des bras. Ça rejoint la nuance d'AvailableFunds, « not […] too far away from the torso », plutôt qu'un « jamais en gameplay ».

**10. « Un seul personnage bouge à la fois » (Thundey) : NUANCÉ.**
Ce que j'ai regardé : 187,0 à 190,2 s à 30 i/s (s187.png).
- Confirmé : le combattant sombre tient sa fente de 187,27 à 187,50 pendant que l'autre a le bras levé, puis le tend vers 187,53.
- Le tableau figé dure de 189,567 à 189,900, soit **11 images à 30 i/s (≈ 0,35 s)**, et non 7.
- Mais de 187,90 à 188,43, **les deux corps bougent ensemble** : ils tournoient au contact, dans les flammes, et on lit quand même.

Correction : c'est une tendance dans l'échange (tenir l'un pendant que l'autre agit), pas une règle.

Ordre de travail de Xoaterz (apprentissage 2), vérifié à 1 i/s : **CONFIRMÉ**.
- Torse sélectionné à 489-491 s ; gizmo de translation sur la jambe à 527-529 ; rotation des bras à 532-533 ; caméra au ras du sol sur le pied à 535-536 ; halo rose-rouge autour du bras à 540-541.
- Nuance : l'ordre n'est pas linéaire. À 530-531, des flèches de translation reviennent sur la jambe puis sur un bras. À 541, le gizmo est de nouveau sur la jambe.

### Oublis importants

- **La planche ✗/✓ reproche aussi « -asymmetric posing » et « -general ugly ass blender posing »** à la pose accroupie ✗ (lu à 500 et 503 s). L'apprentissage 14 (« erreur = poses symétriques ») ne garde que « sameside ». Or Xoaterz reproche aussi l'asymétrie gratuite. Le problème n'est pas « symétrique ou non », mais une pose non motivée.
- **Image de contact et 2e coup chez Xoaterz** (182,267 et 182,533), et **environ 1 s de vol de la victime** (182,6 à 183,6) : voir le verdict 1. C'est justement ce qui contredit « rien sur le milieu ».
- **TSB M1 translate les bras et le torse** (verdict 2). C'est absent des apprentissages 4 et 13, alors que c'est la seule mesure pro sur le « détachement » en gameplay.
- **OofDestroyer25 critique le passage lent→rapide trop brusque** (« goes from slow to fast very quick, making it feel unrealistic »). C'est un contrepoids direct à l'apprentissage 6.
- **Le « Je vois aucun changement » du 26/09 08:46** continue par « je ne sais si c un bug ou si on ne sait tjrs pas compris ». Milan évoque lui-même un bug ou une incompréhension. La lecture « problème de cadrage » de l'apprentissage 9 reste une hypothèse parmi d'autres.
- **Les écarts de temps sont donnés en « images » sans fréquence.** La vidéo est à 30 i/s, alors que le lecteur a travaillé à 10-30 i/s. D'où des comptes faux : 3 images de glitch au lieu de 6, 7 images de tableau au lieu de 11, 1 image blanche au lieu de 2-3. Il faut toujours donner la durée en secondes.
