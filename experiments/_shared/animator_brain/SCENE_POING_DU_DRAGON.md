# Proposition : « Poing du Dragon », une technique ultime complète (2026-09-24)

Réponse à *« tu penses pouvoir faire une animation plus poussée ? Va
re-analyser mes refs et imagine une scène que tu pourrais produire »*.

La scène sert aussi d'étape 6 du `PLAN.md` : un brief libre, à partir du
propre exemple de Milan, « le poing du dragon de Goku ».

Sources :
- `corpus/REFERENCES_VIDEO.md` pour le timing des vidéos ;
- `corpus/README.md` pour les animations et VFX mesurés des packs.

## L'idée en une phrase

Une rafale au rythme du Black Flash lance la victime en l'air. L'attaquant
la rejoint, se suspend (le temps suspendu du Serious Punch), puis plonge
poing en avant dans une fumée dorée qui s'enroule comme un dragon. Viennent
3 planches manga, un écran blanc, et la révélation d'un cratère de pics où
la victime gît au loin.

Palette **or / blanc / noir**, distincte du rouge du Black Flash et du feu
de Stagnant Rage. Durée ≈ 8 s, soit une ultime, pas un M1.

## Découpage (frames à 60 i/s, le rythme d'export du pack pro)

| # | beat | frames | durée | ce qu'on voit | d'où ça vient |
|---|---|---|---|---|---|
| 0 | activation | 0-4 | 0,07 s | flash blanc du corps de l'attaquant (2 f à 30 i/s) | Stagnant Rage |
| 1 | rafale de 6 coups | 4-118 | 1,9 s | 6 impacts, vers les frames 10, 40, 60, 74, 88, 108 (écarts 30/20/14/14/20 f) ; chacun : 1 f de teinte or plate sur l'attaquant, flash, étincelles, onde, fumée ; la victime titube (réaction de 0,22-0,27 s) ; le 5e coup la soulève | Black Flash (rythme) ; pack (M1, Hit) ; corpus VFX (densité) |
| 2 | anticipation | 118-144 | 0,43 s | fente très basse, poing armé à la hanche, glissade avec poussière | Black Flash, 13 f |
| 3 | uppercut + saut | 144-184 | 0,67 s | uppercut qui lance la victime ; accroupi de 8 f, décollage avec étoile au sol, arc | pack (Uppercut) ; Stagnant Rage |
| 4 | **temps suspendu** | 184-240 | 0,93 s | en l'air au-dessus de la victime : poing armé en arrière, genou levé ; caméra large en plongée, précédée d'un whip pan de 6 f | Serious Punch (28 f à 30 i/s) |
| 5 | plongée + coup | 240-288 | 0,8 s | dolly vers l'attaquant, poing vers le bas ; fumée dorée qui tourne autour du bras en spirale (le « dragon ») | Serious Punch (24 f) ; pack (Downslam, 1,08 s) |
| 6 | impact frames | 288-294 | 0,1 s | 3 planches d'1 f : silhouette au trait de NOTRE pose, lignes radiales, grand X | Serious Punch, images fixes |
| 7 | écran blanc | 294-318 | 0,4 s | blanc plein 6 f, puis brouillard qui se dissipe | Serious Punch |
| 8 | révélation | 318-486 | 2,8 s | attaquant accroupi, poing au sol ; cratère de pics de pierre, fumée, débris ; victime éjectée au loin ; tenue longue | Serious Punch (84 f), Moon Animator (pics) |
| 9 | retour | 486-522 | 0,6 s | il se relève et revient à l'idle | Serious Punch (18 f) |

Principes appliqués, tirés de `REFERENCES_VIDEO.md` :
- tenue, action en 2-3 f, tenue ;
- rafale irrégulière ;
- couche graphique d'1 f ;
- caméra animée ;
- décor qui encaisse.

## Ce qu'on livre (pour Roblox, pas seulement un aperçu)

1. **Deux KeyframeSequence** (attaquant, victime), faites sur deux rigs
   V2.22, avec des `KeyframeMarker` à chaque événement : `hit1`…`hit6`,
   `launch`, `suspend`, `strike`, `impact`, `reveal`.
2. **Une piste caméra** animée dans Blender avec le rig, exportée en courbe
   de CFrame, et jouée en `Scriptable` sur les markers.
3. **Des VFX en vraies instances**, dimensionnés sur le corpus VFX :
   - chaque impact de la rafale : flash, étincelles, onde, fumée ;
   - le coup final : les mêmes couches, plus des débris ;
   - le tout piloté par la convention `EmitCount` / `EmitDelay` /
     `TimeScale` des packs pro.
4. **Les effets plein écran** : teinte du corps (`Highlight` sur 1 f),
   écran blanc et brouillard (`ScreenGui`), planches manga (`ImageLabel`),
   étalonnage (`ColorCorrectionEffect`).
5. **Le cratère** : des pics de pierre générés en Parts autour du point
   d'impact, qui sortent du sol puis restent, comme le sol soulevé du
   Serious Punch.
6. **Un module Luau** qui orchestre le tout, plus la démo et le test de sens.
7. **Un aperçu jouable** dans le lecteur, comme pour le M1, avec la caméra
   et les effets d'écran.

## Ce que le cerveau sait déjà faire, ce qui est nouveau

| brique | état |
|---|---|
| deux rigs V2.22, contacts exacts (solveur IK), export et aller-retour moteur | ✅ acquis (M1) |
| timing des coups de la rafale et des réactions, jugé par le corpus pro | ✅ catégories `frappe_legere` (4 ex.) et `reaction` (3 ex.) |
| uppercut, plongée | ⚠️ catégorie `frappe_lourde` : 3 exemples seulement, verdict fragile |
| **temps suspendu en l'air** | ❌ aucune catégorie « aérien » dans le corpus : on retombe sur les principes, et c'est dit |
| VFX denses et dimensionnés | ⚠️ distributions mesurées aujourd'hui, jamais encore appliquées |
| **piste caméra** exportée vers Roblox | ❌ nouveau |
| **effets plein écran**, planches manga | ❌ nouveau. Les planches seront générées depuis nos propres poses (rendu au trait) ; aucun dessin copié |
| **cratère de pics** | ❌ nouveau (géométrie simple) |
| mouvement de la victime en l'air (projection, retombée, éjection lointaine) | ❌ nouveau. En jeu, le déplacement du corps se fait par script sur le HumanoidRootPart, pas dans l'animation : il faut séparer proprement les deux |

## Limites, dites franchement

- **Pas de Roblox Studio ici.** On vérifie les fichiers, le code Luau
  exécuté et la géométrie, pas le rendu réel.
- **Les images** (planches manga, textures de fumée) devront être importées
  par Milan dans Studio : le sandbox ne peut pas téléverser d'assets. Les
  IDs se collent dans une table de configuration. En attendant, le code
  utilise des textures intégrées à Roblox.
- **Les textures du pack 100 Combat VFX** sont des assets Roblox
  utilisables en jeu, mais on ne peut pas les voir ici. On reprend leurs
  **paramètres** (tailles, durées, vitesses), pas leurs images.
- Les inserts dessinés à la main du Black Flash (encre, crâne en rayons X)
  sont hors de portée honnête. On garde les 3 planches du Serious Punch, qui
  sont graphiques et générables.

## Production proposée (chaque lot donne une sortie vérifiable)

1. **Blocking des poses clés** sur les deux rigs : 12 poses. Pour chacune,
   rendu face, profil et caméra de jeu, avec une critique écrite. On
   s'arrête et Milan valide la planche avant d'interpoler.
2. **Animation complète** + verdict du corpus par segment : rafale en
   `frappe_legere`, réactions en `reaction`, uppercut et plongée en
   `frappe_lourde`.
3. **Piste caméra** + export.
4. **VFX** (impacts, dragon de fumée, cratère), **effets plein écran** et
   **planches manga** générées.
5. **Package Roblox** + module Luau + test de sens.
6. **Lecteur** jouable avec tout, publié dans l'artifact.
