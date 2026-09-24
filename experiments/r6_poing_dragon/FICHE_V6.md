# Poing du Dragon v6 : fiche de coup, écrite avant d'animer

Modèle : `../_shared/animator_brain/corpus/FICHE_COUP_MODELE.md`.
Sources : `corpus/ETUDE_VISUELLE.md` (lots 1 à 4, 93 refs) et le verdict du
critique sur la v5.

## Ce que Milan a rejeté, ce que le cerveau en conclut

- **La v5 a eu 6,8** : « je vois pas trop de différence avec la v4 ».
- **Ce qui ne retient pas la note** (mesuré) : le bras, le rythme du poing,
  la rotation du torse. Ils sont déjà au niveau des coups de base pros (M1).
- **Ce qui la retient** : la mise en scène au sol. La partie aérienne, que
  Milan aime, applique la grammaire des refs. La rafale et le coup de f150
  ne l'appliquent pas.
- **Donc la v6 ne touche pas aux poses.** Elle change ce qu'on voit :
  caméra, hiérarchie des effets, impact raconté.

## Intention par temps

| temps | frames | intention | niveau | caméra |
|---|---|---|---|---|
| rafale | 0-108 | pression qui monte ; 4 coups **lisibles** et différents | coups de base (M1), puis un coup moyen (h4) | plans moyens, chaque coup vu **du côté du bras qui frappe** (poing entre les deux silhouettes) |
| charge | 108-146 | « il va se passer quelque chose » : la décision, puis la tension | — | plan large (le pas), **regard** en très gros plan, puis le **poing armé** caméra collée au bras |
| coup chargé | 146-170 | la rupture : le coup qui décide du combat | le plus gros impact au sol | **poing vers la caméra**, puis **impact raconté** : noir + étoile, 3 cartes, blanc, puis plan **très large** sur la conséquence |
| aérien | 170-526 | inchangé (aimé par Milan) | ultime | inchangé |

## Hiérarchie des effets

Règle : l'effet est proportionnel au coup, jamais le même partout.

- **h1, h2 (coups de base)** : éclat au poing d'une image et un anneau, rien
  d'autre. Pas de fumée, pas d'étincelles.
- **h3** : même chose, un peu plus grand.
- **h4 (fente qui ferme la rafale)** : effet moyen, et le **fond remplacé
  par des lignes de vitesse** pendant 6 f.
- **f150 (coup chargé)** : séquence d'écran complète, comme décrite dans le
  tableau :
  - noir 6 f avec une petite étoile ;
  - 3 cartes de 4 f : silhouette inversée de **notre** pose, encre
    hachurée, grand X ;
  - blanc qui se dissout ;
  - l'animation est gelée pendant la séquence.
- **f278-288 (plongée et écrasement)** : inchangé. C'est le vrai final de la
  technique, il garde les planches manga et le blanc.

Deux séquences de cartes dans une technique (f150 et f288), sur ses deux
plus gros impacts. C'est dans la règle d'usage (« le ou les 2 plus gros
impacts »). Celle de f150 est plus courte que celle de l'aérien, pour garder
l'escalade.

## Ce qui ne change pas

- Les poses et le timing : 13 règles vertes, contacts à 0,05 stud.
- La partie aérienne.

## Vérifications prévues

1. **Règles**, **contacts** et **sens** (inchangés, doivent rester verts).
2. **Planche d'étude v5 contre v6**, lue avec la même grille que les refs.
3. **Caméra de jeu** : un nouveau mode « Jeu » dans le lecteur, derrière
   l'attaquant, à distance de joueur. Planche de la rafale vue de là, pour
   juger si elle se lit dans la caméra réelle d'un battleground (lot 3).
4. **Prédiction du cerveau avant la note de Milan**, avec les hypothèses de
   mise en scène jugées sur la planche.

## Ce qui a été fait, et ce que le faire a appris

Le plan ci-dessus a changé trois fois au contact de l'image. Chaque essai a
été rendu, regardé, puis gardé ou écarté
(`captures/verification/2026-09-24-poing-dragon-v6-essais-camera-rejetes.png`).

| prévu | vu à l'écran | décision |
|---|---|---|
| rafale : caméra d'épaule du côté du bras qui frappe (un côté puis l'autre) | le dos et la tête de l'attaquant cachent le contact ; changer de côté à chaque coup traverse l'axe 4 fois | **tout du côté +x** : de là, les coups des deux bras se lisent, le bras part devant le torse (planche v5 : h1 et h2 déjà lisibles de +x, h3 et h4 cachés de −x) |
| charge : très gros plan de face sur le regard | une tête R6 au sourire fixe qui remplit l'écran : comique | **plan rapproché de profil** : le regard se lit par l'orientation de la tête, la victime au bout |
| coup : poing vers la caméra | le corps de la victime bouche l'axe du coup | **profil moyen** qui montre le trajet à plat ; le poing vers le lecteur vit dans la 1re carte |
| cartes 4 f chacune | 3 cartes × 4 f + noir 6 f + blanc = 0,43 s de gel | gardé ; le gel est exactement la durée de la séquence (test Luau) |

**Découverte.** En caméra de jeu (verrouillage d'épaule), la rafale ne se lit
pas : la victime est derrière l'attaquant, l'éclat de base est masqué. Rien
n'est corrigé sans l'avis de Milan : c'est le lanceur qui voit la caméra
ciné, la question porte sur les autres joueurs.

