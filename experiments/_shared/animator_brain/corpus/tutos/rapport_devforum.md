# Rapport : ce que la communauté Roblox (DevForum) dit des animations de combat R6 « smooth / premium / anime »

Recherche faite le 2026-09-24. Source principale : devforum.roblox.com (API JSON de Discourse : `search.json` et `/t/<id>.json`), complétée par WebSearch.
Environ 75 fils DevForum ont été ouverts. Une cinquantaine ont été lus en entier, et **31 ont apporté quelque chose d'exploitable** (listés en §1).

## 0. Avertissement honnête sur la qualité de la source

- **Le DevForum n'est PAS l'endroit où les animateurs de TSB, Jujutsu Shenanigans ou Heroes Battlegrounds partagent leur savoir-faire.** Aucun animateur identifié de ces jeux n'y a posté de tutoriel ou de critique. Les connaisseurs réels se trouvent sur Discord, TikTok, YouTube et Twitter/X, tous inaccessibles ici (voir plus bas).
- La grande majorité des fils « Feedback on my punch animation » sont des débutants critiqués par d'autres débutants. Beaucoup de réponses se résument à « ça a l'air bien », « utilise des easing styles » ou « regarde les 12 principes ». J'ai **filtré pour ne garder que les règles concrètes**, et je signale le niveau de chaque intervenant quand il est connu.
- Il existe néanmoins une petite couche de connaissances **spécifiques à R6 / aux battlegrounds** qui revient de façon cohérente d'un fil à l'autre. Elle figure en §2.
- **Aucun fil DevForum ne parle explicitement de « line of action », de « cheat to camera » ni de silhouette pour des poses R6.** Les recherches sur ces termes n'ont rien donné de pertinent. C'est une vraie absence : ce n'est pas du vocabulaire courant dans cette communauté.

### Ce que je n'ai pas pu consulter
- **Images et GIFs du DevForum : aucun téléchargement n'a abouti.** Tous les médias sont hébergés sur `devforum-uploads.s3.dualstack.us-east-2.amazonaws.com`, et le proxy de sortie refuse la connexion (403 CONNECT, « organization policy »). Les liens `secure-uploads` redirigent vers ce même S3, et les variantes d'hôtes S3 sont bloquées elles aussi. En §6, je liste les URL des images les plus instructives, avec ce qu'elles montrent, pour les ouvrir dans un navigateur.
- **Vidéos** (mp4 du DevForum, YouTube, streamable, gyazo) : non visionnées. Les critiques qui portent sur une vidéo ont été interprétées à partir du texte seul.
- **L'asset « The Strongest Battlegrounds OFFICIAL Animations » (Creator Store id 16072313171)** : repéré par WebSearch, mais create.roblox.com, apis.roblox.com, www.roblox.com et assetdelivery sont tous bloqués. C'est la source la plus précieuse que je n'aie pas pu ouvrir : si l'asset est authentique, ses KeyframeSequences donneraient les vraies poses, timings et easings de TSB. **À récupérer manuellement dans Studio.**
- Le résumé GDC de Mariel Cartwright (Skullgirls) sur siliconera.com et gameanim.com est bloqué. Il est pourtant cité par plusieurs commentateurs du DevForum. Je n'ai que le résumé de la recherche web.
- reddit, tiktok, medal et twitch sont bloqués, comme annoncé.

---

## 1. Sources lues (URL, auteur, résumé en une ligne)

| # | URL | Auteur(s) clé(s) | Résumé |
|---|---|---|---|
| S1 | https://devforum.roblox.com/t/advice-for-positoning-r6-limbs-while-animating/1533251 | Konjointed (question), **Babybunnyiscute19** (réponse) | En R6, placer le « genou » virtuel à la hanche, exagérer davantage que sur un rig articulé, détacher les membres est « totalement OK » ; références Skullgirls « breaking the bones » et stop-motion Bionicle. |
| S2 | https://devforum.roblox.com/t/how-could-i-improve-on-the-impact-of-these-anims/1741255 | **fungi3432**, pjhinthehouse, Xenonic_778 | Le bras R6 entier = l'avant-bras d'un humain (quitte à décoller l'épaule du torse) ; le torse suit le bras avec 1-2 frames de retard ; cubic comme easing de base. |
| S3 | https://devforum.roblox.com/t/how-would-i-go-about-making-my-combat-feel-more-impactful/2042214 | **C_Corpze** (long post), JakeTheNewb, PotatoVampire7797 | Coup très rapide, arrêt net, retrait lent ; couper l'interpolation ; pose « prêt à frapper » forte ; poses « légèrement anormales » tenues quelques frames ; smear par copies de bras transparentes. |
| S4 | https://devforum.roblox.com/t/anime-attacks-dont-feel-smooth/1801221 | **d0cter_oof** | Phase centrale du coup ≈ **4 frames** ; léger déplacement vers l'avant ; fin = figer la pose avec un léger recul. |
| S5 | https://devforum.roblox.com/t/reference-matchinganimation-critique/2451511 | phantasmability | À l'impact, **figer le personnage 2-3 frames**, plus de keyframes distinctes au lieu d'une interpolation trop lisse en l'air. |
| S6 | https://devforum.roblox.com/t/combat-animation-lacks-power/1875328 | **Ylsid** (résume Cartwright/GDC), realknife, JustRockyPlanets | Sur-accentuer les clés, 1 frame de sur-extension puis rétraction, 2-3 frames d'anticipation très marquée, sauter des frames et masquer avec des smears ; la récupération doit montrer l'effort. |
| S7 | https://devforum.roblox.com/t/feedback-on-my-punching-animations/2974402 | melvinpetersen, Reditect, **Bovious** | Jambes volontairement non animées (convention battlegrounds) ; la main ne doit pas « perdre tout son élan » d'un coup à la fin du coup. |
| S8 | https://devforum.roblox.com/t/feedback-on-punch-chain-animation/1417548 | F0xBirdman | Jambes non animées exprès pour se superposer à la marche/course. |
| S9 | https://devforum.roblox.com/t/a-question-about-animations/2624160 | MonkeyIncorporated | Mécanisme TSB : pas de piste sur les jambes → la locomotion les anime ; priorité au-dessus de Core/Movement. |
| S10 | https://devforum.roblox.com/t/just-wanted-a-little-bit-of-feedback-related-to-my-animation-for-various-skills/1866650 | **0BSCURlTY**, iM1GHTB3DANI, xdKasim | Cubic = « effort humain », la plupart des directions en In, rien n'est jamais immobile (pas de clé qui revient sur elle-même), cubic In → cubic Out sur plusieurs clés d'effort ; pied d'appui qui glisse = faute. |
| S11 | https://devforum.roblox.com/t/r6-combo-feedback/1506061 | TrulySmoosh (animateur commissionné), IceTheOneAndOnly | Débat sur le bras libre « collé au torse », les jambes fixes sur un combo de 3 coups, et un finisher qui manque de puissance. |
| S12 | https://devforum.roblox.com/t/feedback-on-r6-combo-animation/707780 | proyoshi04, **Shift4D**, XxMr_AltxX | Accélérer les coups sans changer les pauses entre eux, tourner le torse encore plus pour viser le centre, ramener les membres vers le torse quand ils partent loin. |
| S13 | https://devforum.roblox.com/t/made-some-m1-animations/3885694 | AvailableFunds | « Pour le gameplay, ne pas déconnecter les membres ni les traîner trop loin du torse. » |
| S14 | https://devforum.roblox.com/t/how-are-my-animations/3063720 | ArticFox17777 vs awry_y | Débat : faut-il détacher les jambes du corps en R6 ? |
| S15 | https://devforum.roblox.com/t/animate-how-do-i-make-this-more-dynamic/2842982 | Hazelfluff | « R6 n'a pas de genoux mais a le pouvoir de déconnecter ses membres », la tête a besoin d'un but (regarder devant + tournés dramatiques ponctuels). |
| S16 | https://devforum.roblox.com/t/jespones-guide-to-animations/225752 | **Jespone** (guide, 657 likes) | Les 12 principes appliqués à Roblox ; éviter le « twinning » ; Sine In / Quad Out ; « easing » personnalisé avec des clés linéaires. |
| S17 | https://devforum.roblox.com/t/qa-oniis-guide-to-animation/115242 | spelled_ayayron (Onii) | Rythme (« sur quelles frames l'objet change »), références à x0.25 avec la vue de l'éditeur calée sur la référence ; le twinning est tolérable s'il est masqué par la pose. |
| S18 | https://devforum.roblox.com/t/feedback-on-my-last-animation/1563880 | **PersonifiedPizza** | Garder l'élan : un membre qui change de direction continue un peu dans la direction précédente ; décaler les départs des parties. |
| S19 | https://devforum.roblox.com/t/feedback-on-my-animations/1537030 | iGottic, transquilleo, IceTheOneAndOnly | Éviter les animations à 3 clés ; un membre descend plus vite qu'il ne monte (ex. 10 frames à la montée → 6 à la descente) ; le torse doit vivre. |
| S20 | https://devforum.roblox.com/t/tips-on-animating/3091970 | **vipkute0057**, urgentnotice | Recette complète : anticipation longue en easing In + tenue, frappe courte à fort easing en Out/InOut, puis une frame « hors équilibre » dans le sens du mouvement avant la pose finale. |
| S21 | https://devforum.roblox.com/t/how-to-make-proper-sword-animations-r6/1425032 | GolgiToad | Moins de clés, clés rapprochées pour une frappe rapide, frapper avec tout le corps. |
| S22 | https://devforum.roblox.com/t/how-do-i-improve-this-sword-slash/2052172 | astrozzyz, sharksenpai, GibusWielder, StarJ3M | Élan de préparation et poids, rebonds manuels (overshoot fait à la main), torse et tête qui suivent ; ne pas animer le torse pour ne pas casser la course (objection). |
| S23 | https://devforum.roblox.com/t/how-do-i-make-these-animations-look-better/3168384 | ItzBloxyDev, **OofDestroyer25** | Overshoot en fin de mouvement du bras puis léger retour ; « pause, puis poussée » pour donner du snap. |
| S24 | https://devforum.roblox.com/t/feedback-on-my-punch-animation/3177195 | LucensCat | Ajouter de l'anticipation ; sur un crochet, la fin du coup ralentit ET tourne vers l'intérieur au lieu de s'arrêter à un point arbitraire. |
| S25 | https://devforum.roblox.com/t/jojo-stand-punch-animation-yba-models/1332278 | synical4 | Coup lourd JoJo : grosse préparation en arrière, puis relâche très rapide. |
| S26 | https://devforum.roblox.com/t/feedback-on-animation-for-fighting-game/2877397 | xnSly, Bubblegumboy29 | Jeu rapide : clé de frappe dans les 30-40 premières frames ; replier la jambe avant le spin kick. |
| S27 | https://devforum.roblox.com/t/why-do-combat-game-developers-lean-more-towards-r6-rather-than-r15/3136549 | **sick_tr1cks**, extraclear | R6 peut atteindre le même attrait que R15 mais demande plus de talent ; Heroes Battlegrounds cité comme référence R6. |
| S28 | https://devforum.roblox.com/t/r15-games-that-appear-to-be-r6/4836654 | Chark_Proto, steintro | TSB et Deepwoken sont bien en R6 (et non en R15 déguisé) ; « les animations R6 sont souvent bien plus expressives ». |
| S29 | https://devforum.roblox.com/t/can-you-use-cframe-from-moon-animator-on-rigs-or-tween-the-movement-in-the-script-when-trying-to-do-skills-similar-to-most-battlegrounds-games/3310698 | **osavpp** | Workflow de skill battlegrounds : animer avec le déplacement, poser des events startRun/endRun, remettre le perso sur place, puis déplacer par BodyVelocity. |
| S30 | https://devforum.roblox.com/t/serious-punch-recreation-creation-overview-part-3/3630207 | pewpewagent, **TimeFrenzied**, Crazedbrick1 | Caméra de cutscene = une part weldée au HRP, animée comme un membre (ou export caméra Moon 2), AutoRotate off ; critique : « le coup manque d'accélération ». |
| S31 | https://devforum.roblox.com/t/how-can-i-make-advanced-cut-scenes-like-battleground-games-61125/3686403 | Yarik_superpro, TimeFrenzied | Blender plutôt que l'éditeur Roblox pour les courbes ; VFX déclenchés par markers ; debris de TSB côté client. |

Fils lus en complément, de moindre valeur mais qui corroborent : 1046242, 831713, 2630377, 1044234, 3679871, 3886171, 1609881, 3061139, 1200779, 1562906, 1000172, 872073, 1523016, 2792567, 2776727, 2046945, 1053791, 1507373, 1989275, 2419921, 3545392, 3394308, 2530158, 3186011, 3055082, 4711717, 4700793, 3843087 (module RootMotion), 2468478 (impact frames), 2133285 (hitstop), 1796206, 2028437, 3051738, 2514524, 392218, 3586405 (fil du rig R6 IK+FK V2.22, purement technique).

---

## 2. Règles spécifiques R6 / combat Roblox

Légende : **[R6]** = règle née de la contrainte R6 ou Roblox ; **[Gén→R6]** = principe général qu'un commentateur a appliqué explicitement à du R6 ou à du combat battlegrounds.

### 2.1 Anatomie R6 : c'est là que se trouve « l'autre anatomie » dont parle le propriétaire

**R1 [R6] — Le bras R6 entier joue l'AVANT-BRAS humain, quitte à décoller l'épaule.**
- Énoncé (fungi3432, S2) : on peut représenter la préparation d'un coup et l'extension du coude en R6 « en déplaçant le bras entier selon la position de l'avant-bras d'une vraie personne (ou d'un R15) pendant l'animation. Il faut simplement accepter de déconnecter l'"épaule" du bras du torse. »
- Conséquence pratique : pour un direct, on ne tourne pas seulement le bras autour de l'épaule. On le **translate** vers l'avant et vers l'axe central, pour que la « main » parcoure la trajectoire qu'aurait un poing humain. Le haut du bras reste implicite.
- Quand l'appliquer : chaque fois qu'une pose de référence a un coude plié (garde, crochet, uppercut, coude, préparation).
- Quand s'en méfier : voir R3 (lisibilité en gameplay, hitbox).

**R2 [R6] — Le « genou » R6 est virtuellement à la hanche ; exagérer pour compenser l'absence d'articulations.**
- Énoncé (Babybunnyiscute19, S1) : « Faites comme si le genou du rig R6 était à la hanche. […] Même chose pour les bras, dans une certaine mesure. » Puis : « Exagérez chaque mouvement : pour les rigs qui ont moins d'articulations qu'un humain, l'exagération rend le personnage vivant. C'est une pratique courante dans les stop-motions Bionicle. »
- Même fil : « Détacher un membre du corps d'un personnage R6 est une bonne option pour exagérer le mouvement, c'est tout à fait acceptable. »
- Hazelfluff (S15) : « R6 n'a pas de genoux mais il a le pouvoir de déconnecter ses membres du corps. »
- PlayerTrillion (1046242) : « Si une animation n'est pas assez exagérée, elle a l'air terrible, surtout sur R6 à cause de l'absence de flexion. »
- Ce qu'en dit la communauté : une pose de manga convertie telle quelle en R6 paraît raide. Il faut **pousser les angles au-delà** de la référence et **déplacer les pièces** (translation), pas seulement les faire tourner.

**R3 [R6] — Limite de la dislocation : rester lisible et « attaché » en gameplay.**
- AvailableFunds (S13), sur un set de M1 : « Très bien pour tout sauf le vrai gameplay. Pour que ce soit adapté au gameplay, je ne déconnecterais pas les membres et ne les traînerais pas trop loin du torse. »
- XxMr_AltxX et catlinn64 (S12) : « Faites pivoter les articulations vers le torse quand elles partent très loin vers l'avant, pour qu'elles n'aient pas l'air de tomber », et « assurez-vous que tous les membres rejoignent le torse au bon endroit ».
- Synthèse opérationnelle (mon interprétation, cohérente avec les deux camps) : **la dislocation est autorisée pendant quelques frames de mouvement rapide** (smear, extension) ; **les poses tenues (garde, impact figé, récupération) doivent montrer des membres visuellement raccordés au torse.** Quand un bras est translaté loin, on l'**oriente vers l'épaule** pour que l'œil reconstruise la chaîne.
- Piège technique : sur de vieux places, `Workspace.AnimationWeightedBlendFix` empêchait en jeu la translation des membres visible dans l'éditeur (S : 1796206). À vérifier si des membres « se recollent » en jeu.

**R4 [R6] — Le torse est le moteur ; c'est lui qui vend la puissance.**
- Shift4D (S12) : « Faites tourner le torse encore plus et visez les coups vers le centre. » Il conseille aussi un bloc devant le perso comme cible, pour que les coups visent réellement le centre de l'adversaire et non ses épaules.
- pjhinthehouse (S2) : « Si vous lancez un coup, le haut du corps va basculer vers l'avant, mais le mouvement aura **une ou deux frames de retard sur le bras** » (overlap torse → bras inversé : le bras mène, le torse suit).
- oofdog4526 (1609881) : faire plier le torse vers l'arrière quand l'arme est derrière.
- Rymxi (3061139) : la rotation du torse doit suivre un profil lent → rapide → lent.
- Hazelfluff (3061139) : sur un rig uni, une rotation du torse modeste « ne se lit pas » ; il faut l'amplifier, ou la souligner par la tête.
- IceTheOneAndOnly (répété sur 3 fils) : un coup où seuls les bras bougent n'est « pas dynamique ». Une partie doit en affecter une autre, et torse + jambes doivent bouger.
- TrulySmoosh (S11) : sur un combo rapide, la rotation vive du torse masque les petits mouvements du bras libre.
- azazinchic (831713) : « Le torse déplace tout le corps ; je l'ai rendu sur-réaliste pour que ça n'en ait pas l'air. » Autrement dit, animer le Torse (RootJoint) et contre-animer les jambes pour garder les pieds au sol.

**R5 [R6 / battlegrounds] — Convention des M1 : NE PAS mettre de piste sur les jambes.**
- melvinpetersen (S7) : « Je n'anime pas les jambes pour que l'animation de marche Roblox le fasse à ma place. Regardez les battlegrounds : les plus populaires font pareil. »
- F0xBirdman (S8), lukethebestpug (S3) et MonkeyIncorporated (S9, sur TSB) : les jambes n'ont **aucune piste** dans l'animation de M1, pour que la course ou la marche se superpose ; l'animation est jouée à une priorité supérieure à la locomotion.
- StarJ3M (S22) : animer le torse sur une attaque « ruinerait l'animation de course ».
- Quand l'appliquer : M1 et coups utilisables en mouvement.
- Quand ne pas l'appliquer : skills, finishers et cutscenes, où le personnage est planté. Là, jambes et torse doivent être pleinement animés, et les critiques « jambes collées / sur des patins » redeviennent valables (S8, S10, 1053791).
- Contradiction avec R4 : voir §5.

**R6 [R6] — Pied d'appui planté ; s'il glisse, il faut que ce soit voulu et lisible.**
- iM1GHTB3DANI (S10) : « Si une jambe bouge, l'autre ne devrait pas bouger, sauf pour un saut. […] La jambe au sol glisse ; elle devrait rester immobile tout du long. » C'est souvent un effet du torse animé en IK.
- Si la glissade est voulue (poussée sur le pied arrière), il faut la rendre explicite par un petit saut (même fil).
- TrulySmoosh (1053791) : « Les jambes n'ont pas l'air plantées dans le sol du tout. »

**R7 [R6] — La tête doit avoir une intention.**
- Hazelfluff (S15) : « Vous n'avez que 5 ou 6 parties, tirez le maximum de chacune ». La tête regarde principalement devant, avec un tourné dramatique de temps en temps.
- IceTheOneAndOnly (1537030) : un regard fixe qui « ne perd jamais sa concentration » paraît mort.

### 2.2 Chronométrage et espacement d'un coup (chiffres fournis)

Rappel : Roblox joue les animations à 60 fps maximum, et Moon Animator 2 exporte en 60 fps (S : 392218, 2514524). Les nombres de frames ci-dessous sont supposés à 60 fps sauf mention contraire. Les auteurs ne précisent presque jamais leur cadence.

**R8 [Gén→R6] — Structure d'un coup de mêlée « fort » (d0cter_oof, S4, sur des attaques anime) :**
1. le personnage **avance légèrement** pour montrer l'élan ;
2. la **phase centrale est extrêmement rapide** pour transmettre la puissance, **environ 4 frames** ;
3. la fin **fige le personnage dans sa pose avec un léger recul**.

**R9 [Gén→R6] — Figer à l'impact : 2-3 frames.** (phantasmability, S5) « Pour l'impact, figez le personnage 2 ou 3 frames. Ça donne beaucoup plus d'impact au coup. »
- Côté code, le hitstop se fait via `AnimationTrack:AdjustSpeed(0)` puis `AdjustSpeed(1)` (EmeraldLimes, 2133285).

**R10 [Gén→R6] — Arrêt net, puis retrait lent.** (C_Corpze, S3) « Quand un personnage frappe, rendez le mouvement vraiment rapide ; quand le poing touche, arrêtez-le brusquement. Ensuite, faites-le se rétracter et se relâcher lentement. »

**R11 [Gén→R6] — Recette complète d'une frappe (vipkute0057, S20)** :
- **Préparation** plus longue pour accumuler l'énergie et le poids, en easing **In**, puis une **tenue**.
- **Frappe** courte, avec « un easing fort », en direction **In-Out ou Out**. L'arme ou le poing doit pointer vers l'avant, pas vers le haut.
- **Fin** : « une frame où le personnage est **hors de sa position finale, dans le sens du mouvement** », puis les clés suivantes reviennent à la pose finale. C'est un overshoot du corps entier suivi d'un settle.

**R12 [Gén→R6] — Ce que Cartwright (Skullgirls) applique, selon Ylsid (S6)** : « Sur-accentuer les keyframes ; **une frame où l'attaque sur-étend puis se rétracte** ; **quelques frames d'anticipation très accentuée** ; **sauter des frames** et utiliser des smears pour masquer le tout. » Le même talk est cité par Konjointed (S1) pour le « breaking the bones » : n'ayez pas peur de casser les membres pour pousser l'animation.

**R13 [Gén→R6] — La récupération doit porter l'effort.** (realknife, S6) « Faites en sorte que le personnage doive se remettre d'avoir utilisé une grande force. Dans votre vidéo, il récupère comme s'il avait utilisé le moins de force possible. » On retrouve la même idée chez Gucci_Dabs222 (1523016), qui parle d'une pause puis d'une petite poussée du corps après une taillade (« brute movements »), et chez ZensStarz (S2), qui a rendu la fin « plus rigide, avec un peu plus de recul ».

**R14 [Gén→R6] — Pas d'arrêt « mort » en fin de coup** (nuance de R10) :
- Bovious (S7) : « Les mains s'arrêtent comme si elles perdaient tout leur élan. »
- LucensCat (S24) : ralentir la fin au lieu de stopper « à un point arbitraire dans l'air ». Sur un crochet, la fin **tourne vers l'intérieur**, mais pas sur un direct. Méthode : « frappez l'air un moment et vous verrez ».
- ItzBloxyDev (S23) : « À la fin d'un mouvement de bras, il peut dépasser le but puis revenir un peu en arrière. »
- La différence avec R10 : l'arrêt est brusque à l'**impact**, mais le membre garde un résidu d'élan (overshoot ou settle, rotation résiduelle) au lieu d'un gel parfait sur une clé linéaire.

**R15 [Gén→R6] — La descente est plus rapide que la montée.** (transquilleo, S19) « Si on dit que vous levez le bras en 10 frames, il devrait redescendre en environ 6 frames. » C'est un ratio d'environ 0,6.

**R16 [R6/battlegrounds] — Les combos accélèrent sans supprimer les pauses.** (Shift4D, S12) « Accélérez les coups, mais **gardez la même pause entre eux**. » DemonHunterz6 (1507373) : pour un M1 au clic, la mise en action (startup) doit être plus rapide.

**R17 [battlegrounds] — La frappe arrive tôt.** (xnSly, S26) Dans un jeu de combat rapide, « les frames de frappe sont de préférence dans les 30-40 premières ». Cadence non précisée ; probablement 60 fps, donc environ 0,5-0,67 s.
- melvinpetersen (S7) : **0,41 s entre deux M1**. En descendant à 0,35 s, « les animations semblaient se mélanger ».

**R18 [Gén→R6] — Une frappe n'est pas une taillade lissée : utiliser moins de clés, plus rapprochées.**
- GolgiToad (S21) : « Moins de keyframes, laissez le moteur aller du point A au point B ; rapprochez les clés, c'est un coup, c'est rapide ; frappez avec tout le corps. »
- iGottic (S19) : « évitez les animations à 3 keyframes, elles ne laissent pas de place au détail. »
- Ces deux conseils ne se contredisent pas : peu de clés **dans la frappe elle-même**, mais assez de clés autour (anticipation, overshoot, settle).

### 2.3 Easing : les noms précis donnés par la communauté

- **Cubic = défaut « effort humain »** (0BSCURlTY, S10 ; fungi3432, S2 : « cubic est un bon choix pour expérimenter »). 0BSCURlTY : « la plupart des directions sont In, quelques-unes Out ». Sur plusieurs clés d'effort (un lancer), **commencer en cubic In et finir en cubic Out**.
- **Jespone (S16)** : exemple d'un mouvement de tête **Sine In, Quad Out**. Le linéaire intégral « a l'air fait par un robot ». On peut aussi fabriquer son propre easing en posant des clés linéaires rapprochées (fréquent chez les animateurs avancés).
- **Back et Elastic** pour la puissance (JustRockyPlanets, S6) ; **Sine ou Back** pour un uppercut (Redluo, 2046945). Jake (dans la recherche web) décrit Bounce comme un overshoot rebondissant pour l'atterrissage et Elastic comme ressort exagéré.
- **Quad InOut** pour une taillade (Dev4q, S22).
- **Constant / « None »** (Moon Animator 2) pour un rendu **saccadé, stop-motion, « on twos »** : Moon exporte toujours en 60 fps, donc pour obtenir du 12 fps il faut poser la cadence dans l'éditeur Roblox et mettre toutes les clés en Constant (vladxh, 3051738 ; Microwave_Toothpaste, 2514524 ; FinallChase, 2419921 ; MochiFloofs, 3794212 à propos de Block Tales).
- **Varier les easings** : VeeGFX (1000172) : « utiliser le même easing partout se voit et fait perdre en qualité ». Une retombée au sol doit être plus douce qu'une frappe.
- C_Corpze (S3) : **désactiver l'interpolation** un bref instant (clés en Constant) et poser la frame à la main. « Trop d'interpolation, ou le mauvais type, peut détruire l'illusion de vitesse, d'impact et d'imprévisibilité. C'est aussi pour ça que certaines animations de combat ont des coups à des cadences et des vitesses différentes. »
- Dans Moon Animator : sélectionner les clés, touche **7**, puis Ease (BeansIsPro, 3679871 ; Kevinsteo, 2986085). Dans l'éditeur Roblox : clic droit sur une clé (fungi3432, S2).
- Limite rapportée par TrulySmoosh (1523016) : l'éditeur Roblox d'alors n'avait que peu d'easings. « L'easing ne rend pas immédiatement l'animation meilleure, il faut parfois retirer des clés. »

### 2.4 Mouvement du perso, root motion, caméra : spécifique aux battlegrounds

**R19 [battlegrounds] — Animer « sur place », déplacer par script.** Workflow d'osavpp (S29) :
1. animer le skill **avec** le déplacement (perso et victime), pour caler le timing ;
2. poser des **Animation Events** (`startRun`, `endRun`…) ;
3. **modifier l'animation pour que perso et victime restent sur place** (« si vous regardez le sneak peek de l'Ignite Burst dans TSB, le personnage ne bouge pas du tout ») ;
4. appliquer une **BodyVelocity/LinearVelocity** entre les events. Tween = « saccadé ».
- Autres fils : GIassWindows et happya_x (S : 3022755), à propos du Beatdown de TSB : la vélocité doit décroître (très rapide puis ralentissement) pour un « burst ». Den_vers (3883209) : LinearVelocity relative à l'attachment pour un auto-run orientable.
- Alternative : root motion. Le **module RootMotion** de TalFaizan (3843087) anime le RootJoint et recale le HRP. Pièges documentés : réplication de `.Transform` et retour brutal au `Stopped`.
- Heiguy23 (2530158) empêche le « snap back » du HRP de TSB avec AlignPosition.
- FroDev1002 (3186011) : « les animations ne sont que des offsets » ; en fin d'anim, on recopie le CFrame du Torso dans le HRP.

**R20 [battlegrounds] — La caméra fait partie du coup.**
- Coups normaux : légère secousse de caméra centrée sur la tête ou le torse, « pour que la caméra bouge avec le coup » (shakability et Deathhunter1249, 3545392, à propos de TSB).
- Skills et ults : **caméra animée** (pewpewagent, S30). Une part weldée au HRP est animée comme un membre (ou export caméra de Moon 2 via File > Export Rig, selon TimeFrenzied), puis `camera.CFrame = part.CFrame` chaque frame. Désactiver `Humanoid.AutoRotate` pour éviter la vrille en shiftlock.
- FOV, color correction (saturation/désaturation), bloom, flash, « impact frames » noir/blanc via ColorCorrection + Highlight (C_Corpze, S3 ; chijioked1, 2468478).
- Toefl (872073) : « jouez davantage avec la caméra, faites des plans rapprochés ».

**R21 [battlegrounds] — La fluidité d'un combo vient aussi du script.**
- Les animations M1 sont des pistes séparées (M1_1…M1_4) enchaînées par script (4711717).
- Fondu `Play(0.2)` / `Stop(0.2)` entre les animations (L0chlainn, 4700793 ; DumpWanderer propose 0,21).
- Pas de délai mort entre la fin d'un M1 et le suivant : « dans TSB, dès que l'animation finit, la suivante joue » (Deathhunter1249, 3545392).
- Priorité supérieure à Idle/Movement ; si l'idle et l'attaque ont la même priorité, l'attaque paraît « raide » (4817574).
- Moleza (1989275) : une animation séparée de **retour à la garde** dont la première frame est la dernière du coup, pour un retour lent et propre.

---

## 3. Ce qui fait « premium / smooth / anime » selon la communauté

1. **Contraste de vitesse, pas lissage uniforme.** Tous les conseils sérieux convergent : préparation lisible (souvent tenue), frappe très courte (environ 4 frames), gel à l'impact (2-3 frames), recul et récupération plus lents. Le « smooth » premium n'est **pas** une interpolation lente et régulière. Phantasmability (S5) reproche justement à un saut d'être « trop smooth » et de ressembler à un personnage qui flotte.
2. **L'exagération au-delà de l'anatomie** est « obligatoire » en R6 pour compenser les articulations manquantes : torse sur-tourné, membres translatés et « détachés », poses « légèrement anormales tenues quelques frames, qu'on ne remarque pas » (C_Corpze, S3). C'est l'équivalent R6 de la « différente anatomie » que remarque le propriétaire.
3. **Le bras R6 = avant-bras** (fungi3432, S2). C'est la règle la plus spécifique au R6 trouvée, et probablement l'une des clés du « même un simple punch n'est pas un simple punch ».
4. **Le corps entier participe** : le torse mène la puissance, le bras mène la trajectoire, le torse suit avec 1-2 frames de retard, la tête a une intention. Le bras libre garde la tête ou charge le coup suivant (TrulySmoosh, S11).
5. **Easings variés et choisis** : cubic ou sine en base, Back/Elastic pour l'overshoot, Constant pour les frames tenues ou saccadées. Jamais le même easing partout, jamais tout en linéaire.
6. **Rien n'est jamais complètement immobile** (0BSCURlTY, S10 ; CodyTheDwagon, 2792567, « un flux de mouvement constant »), **sauf** le gel volontaire d'impact. Cette tension est expliquée en §5.
7. **« Premium » = animation + caméra + VFX + SFX synchronisés.** Pour TSB, les commentateurs attribuent une grande part de l'impact à la secousse légère de caméra centrée sur le perso, aux VFX déclenchés par markers et au son (S3, 3545392, 3394308, 3572490). yousef_mash1 (3394308) : « le plus important dans les battlegrounds, ce sont de bonnes animations », puis VFX/SFX « importants pour les animations ».
8. **Outil** : Blender (courbes Bézier, graph editor, IK/FK) ou Moon Animator 2 sont considérés comme nécessaires pour ce niveau (TimeFrenzied, Yarik_superpro, S31 ; Awesomepad, 3021601 : « Moon ne peut t'emmener que jusqu'à un certain point » pour le dropkick KJ de TSB). sick_tr1cks (S27) : le R6 atteint le niveau du R15 « mais demande plus de talent, en utilisant Moon et/ou Blender de façon optimale ».

---

## 4. Ce qui fait « robotique / amateur » selon les critiques

Chaque symptôme est suivi de sa source et de la correction proposée.

- **Tout en linéaire, vitesse constante d'une clé à l'autre** : S2, S22, S23, 2776727, 3168384. Correction : easings, spacing.
- **Toutes les parties partent et arrivent en même temps** (« twinning » au sens de Jespone : clés alignées verticalement sans intervalles). Sources : S16 et PersonifiedPizza (S18, « le personnage commence chaque mouvement à des moments différents »). Correction : décaler les départs (overlap).
- **Changement de direction instantané d'un membre** : PersonifiedPizza (S18). Correction : garder l'élan un peu dans la direction précédente.
- **Coup sans anticipation, qui « sort de nulle part »** : 1044234, 3177195, 2877397, 1332278, 2052172.
- **Coup sans accélération** : Crazedbrick1 sur le Serious Punch, S30.
- **Coup qui s'arrête pile à un point arbitraire et « perd tout son élan »** : S7, S24.
- **Pas de follow-through, retour direct à l'idle** : Xenonic_778 (S2, « la façon dont elles coupent le coup diminue l'impact ») et urgentnotice (S20).
- **Seuls les bras bougent, le torse est figé, les jambes sont collées** : IceTheOneAndOnly (S11, 1562906, 1537030) et SubtotalAnt8185 (S22). À nuancer pour les M1 battlegrounds (R5).
- **Pied d'appui qui glisse, perso qui « patine » ou « flotte »** : S10, S8, 1200779.
- **Récupération trop facile, le coup a l'air d'une tape** : realknife (S6), Tornado_chaser04 (872073, « on dirait qu'il s'essuie la joue »), Toefl (même fil, « des bras qui battent l'air plutôt que des coups »).
- **Poses « bizarres »** : bras qui pointe vers le ciel sans but (Shift4D, S12), transition uppercut qui commence comme un direct (1044234).
- **Trop lent et « human speed » pour un jeu anime** : S11, 1044234, 26. Inversement, trop rapide pour être lu : SMUSH21 (1989275), 1523016, 1537030. Voir §5.
- **Même easing partout** : VeeGFX, 1000172.
- **Pause visible en l'air entre deux poses** : 2630377. Deux clés trop espacées pour un changement de pose ; il faut les rapprocher (ChronicallyOnlin_e).
- **Retour à la garde qui ressemble à un deuxième coup** : Dyzody (1523016). Correction : ralentir le retour.

---

## 5. Contradictions et incertitudes

1. **Détacher les membres : oui ou non ?**
   - Pour : Babybunnyiscute19 (S1), fungi3432 (S2), Hazelfluff (S15), ArticFox17777 (S14, « les jambes doivent se détacher dans la plupart des animations R6, sinon ça ne fait que tourner »).
   - Contre ou avec réserves : AvailableFunds (S13, en gameplay), awry_y (S14), catlinn64 et XxMr_AltxX (S12), Foxstream52 (3886171, « gardez les parties ensemble, repositionnez-les plutôt sur le torse »).
   - Lecture probable : oui pendant les frames rapides et les cutscenes ; avec retenue sur les poses tenues des M1 vues en jeu. À **arbitrer par le propriétaire sur nos propres captures.**
2. **Animer les jambes et le torse sur un M1 ?**
   - Le consensus « amateur » dit oui (plus de corps = plus de vie).
   - La convention battlegrounds dit non pour les jambes (S7, S8, S9, S3), ce que MonkeyIncorporated a vérifié sur TSB.
   - Pour le torse, StarJ3M (S22) craint de casser la course, alors que IceTheOneAndOnly et Shift4D exigent plus de rotation du torse. Le RootJoint (Torso) peut être animé sans casser les jambes de locomotion si les pistes Left/Right Hip sont absentes, mais je n'ai **pas de source confirmant ce que TSB fait exactement pour le torse sur ses M1.**
3. **Figer vs toujours en mouvement.**
   - D'un côté : figer 2-3 frames à l'impact (S5), figer la pose finale (S4).
   - De l'autre : « aucune clé immobile, tout bouge toujours » (S10) et « flux constant » (2792567).
   - Réconciliation plausible : un gel **court et intentionnel** au contact, alors que les tenues longues sont des « moving holds » où l'on garde une micro-dérive. Cette réconciliation vient de moi et n'est pas sourcée.
4. **Vitesse.** « Accélère » et « ralentis » reviennent pour des animations semblables. Le critère récurrent est l'usage : un M1 ou un jeu anime va vite, une cutscene ou un « combo starter » peut être lent (azazinchic, 831713). xnSly (S26) : l'impact dans les 30-40 premières frames.
5. **Blender vs Moon vs éditeur Roblox.** Certains disent que l'outil ne change rien pour un débutant (urgentnotice, vipkute0057, S20). Les praticiens battlegrounds disent que Blender ou Moon 2 sont indispensables pour ce niveau (S31, 3021601, S27).
6. **Nombre de clés.** « Moins de clés » (GolgiToad, S21 ; TrulySmoosh, 1523016) contre « évitez les animations à 3 clés » et « plus de clés » (iGottic et transquilleo, S19 ; phantasmability, S5). Voir la réconciliation en R18.
7. **Chiffres en frames sans cadence.** « 4 frames », « 2-3 frames » et « 30-40 premières frames » ne précisent jamais s'il s'agit de 24, 30 ou 60 fps. Le seul ratio indépendant de la cadence est **montée 10 / descente 6** (S19).
8. **Réalisme vs anime.** nino133 (831713) conseille de moins se pencher, de garder les pieds plantés et d'aller plus vite pour être réaliste. xander5610 (1417548) dit de ne jamais tourner le dos sur un coup (Taekwondo). Ce sont des retours « réalistes » qui vont à l'encontre du style anime ; la plupart des autres commentateurs et le propriétaire veulent l'inverse (« We don't want realistic. WE WANT COOL. », RocketSlither, S27).
9. **R6 vs R15.** Plusieurs commentateurs de 2021-2022 disent que « ça rendrait mieux en R15 » (S2, 1046242, 2052172). Les praticiens (fungi3432, StarJ3M, sick_tr1cks, Chark_Proto) répondent que le R6 est **plus expressif** si on sait le pousser. Hors sujet pour nous, mais c'est une confirmation que le R6 bien exploité n'est pas un plafond.

---

## 6. Images : aucune téléchargée, car l'hébergeur S3 du DevForum est bloqué par le proxy

Le dossier `/tmp/claude-0/-home-user-Jeux/4796ac9e-8e41-51f7-91c4-7b92a6a187d0/scratchpad/tutos/devforum/` ne contient **aucune image**. Il contient seulement un sous-dossier `_echecs_pas_des_images/` avec 3 fichiers de réponses d'erreur (HTML 403/404 et un fichier vide). Je voulais les supprimer, mais la suppression a été bloquée par un garde-fou de sécurité ; on peut les supprimer sans risque.

Voici les images les plus instructives repérées, à ouvrir dans un navigateur connecté (hôte `https://devforum-uploads.s3.dualstack.us-east-2.amazonaws.com/uploads/...`). Les noms proposés sont ceux prévus pour le téléchargement.

| Nom prévu | URL (chemin après `.../uploads/`) | Ce que ça montre | Fil source |
|---|---|---|---|
| 01_r6_genoux_a_la_hanche_schema.png | `original/4X/f/4/a/f4a57e3f08c147be01ef4fa471b5aa5b5601894e.png` | Schéma : où placer le « genou » virtuel d'une jambe R6 (au niveau de la hanche). | S1 (1533251) |
| 02_ref_ryu_stance_a_convertir_R6.gif | `original/4X/3/2/0/320aa999d28989d280893caf573174f686499722.gif` | Garde de Ryu (sprite de jeu de combat 2D) que l'auteur essaie de reproduire en R6. | S1 |
| 02b_tentative_R6.png | `original/4X/7/6/6/7662631d27b8e68d1526aae284650f925be651d5.png` | La tentative R6 correspondante (avant conseils). | S1 |
| 03/04_critique_pose_bizarre_1-2.png | `original/4X/7/1/5/71571c8278de2bbcb1465b7057b1c2300316a5c0.png`, `original/4X/0/0/5/005f3ed3351ea06fd0dba039483fbd5635efcd97.png` | Frames d'un combo R6 pointées comme « poses bizarres » (bras gauche « weird », uppercut qui démarre comme un direct). | 1044234 |
| 05_critique_pose_corrigee.png | `original/4X/4/d/6/4d6df0d6ef3f59d136021de63efd21589360b9b1.png` | « My version » : la même pose refaite par le critique (DoggoAnim). Seul vrai avant/après de pose trouvé. | 1044234 |
| 06_limb_extension_vfx.gif | `original/4X/2/d/a/2daeaa8b5f19f0bc209d976c02bd6acb51b00b0a.gif` | Effet « membre qui s'étend » (Star Platinum) fait en VFX, en complément du coup en 4 frames. | S4 (1801221) |
| 07/08_spin_kick_v1_v2.gif | `original/5X/5/c/e/5/5ce5da456187dfde70dec3d61640e29551f3a688.gif`, `original/5X/c/f/a/c/cfac72d97b16915e4abd0d9524905f62586a155f.gif` | Spin kick R6 Blender très rapide (impact avant 30-40 frames), critiqué pour le manque d'anticipation (jambe à replier d'abord). | S26 (2877397) |
| 09_plongeon_pause_milieu.gif | `original/5X/a/4/1/3/a413780a6df0522f614a556af33a43559db686c3.gif` | Défaut typique : pause « Scooby-Doo » en l'air entre deux poses trop espacées. | 2630377 |
| 10_plongeon_timeline.png | `original/5X/8/8/e/3/88e3e56707efcf3c012b370144154ea13d41d6d1.png` | La timeline de clés correspondante : on voit l'espacement fautif. | 2630377 |
| 11_pose_anime_ref_vs_R6.jpeg | `optimized/5X/f/2/b/9/f2b916e79b7d55a5e7f93ad5872e21eeaadf2e31_2_517x302.jpeg` | Pose anime de référence et tentative R6 qui « a l'air stupide ». | 3886171 |
| 13_easing_styles_chart.jpeg | `original/5X/c/9/2/3/c923a219595c83adc3018d6280450823fdcbffbc.jpeg` | Tableau des EasingStyles Roblox (courbes). | 3278199 |
| 14_easing_directions_chart.jpeg | `original/5X/6/8/9/3/68935db67beeac7d73b3e93436c9966e13605aea.jpeg` | In / Out / InOut illustrés. | 3278199 |
| 15_dash_courbe_dropoff.jpeg | `original/5X/8/a/a/9/8aa932fcd851a70644ce2b52e261665e3d4a1c89.jpeg` | Courbe de vitesse d'un dash style TSB (rapide puis décroissance). | 3022755 |
| 16_tsb_hrp.jpeg | `original/5X/5/4/9/6/54963712402ec0472b773cc508ea3534dee5484f.jpeg` | Capture TSB : fin de move sans retour du HRP à l'origine. | 2530158 |
| 18_moon_menu_easing.jpeg | `optimized/5X/f/1/1/4/f114597dde100ced2824ce05462be387833326dc_2_425x375.jpeg` | Menu d'easing de Moon Animator 2 (touche 7). | 3679871 |

Médias vidéo potentiellement très utiles, non visionnables ici :
- Critique vidéo de TrulySmoosh (R6 M1 combo) : https://streamable.com/nlkice (S11)
- Ancienne animation de 0BSCURlTY montrant clés et directions d'easing : https://streamable.com/7abc6h (S10)
- Playlists YouTube « The Strongest Battlegrounds - Animation Playlist » (PLk9iqqBYvZheh185KZodZGs_dOEmmOB14) et « TSB Trailer Animation Raw ver. » (https://m.youtube.com/watch?v=-hP1orW_OmE), à étudier image par image par un humain.
- L'asset Creator Store 16072313171 « The Strongest Battlegrounds OFFICIAL Animations », **à ouvrir dans Studio**. Son authenticité n'est pas vérifiée, mais s'il est réel ce sont des KeyframeSequences TSB exploitables directement : poses, espacement des clés, easings.
