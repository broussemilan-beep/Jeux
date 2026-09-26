# 3 propositions pour la prochaine cinématique (2026-09-26)

Contexte : Poing du Dragon v13e = 8/10, « pas premium mais mid haut ».
Ce qu'on a appris à faire : animation du perso (~8), rythme mesuré
(`allure.py`), mise en scène, dragon 3D, son. Point faible : les images des
VFX (générées par programme). Question en cours : passage sur Roblox Studio
(`corpus/recherche/STUDIO_FREIN_2026-09-26.md`).

Chaque proposition part de refs DÉJÀ au catalogue et mesurées.

---

## 1. « UN SEUL COUP » (Serious Punch, façon Saitama)

- **Refs** : Serious Punch TSB (48244687, 10 s ; mesuré : 1 seule carte
  silhouette de 0,27 s, 3 tenues dont une de 0,47 s), Serious Punch 2
  (772ee6b0), Serious Punch de Pew (lvB-wTylH3Y : 3 s de charge, 2 images
  de carte inversée, **ligne de roches jusqu'à l'horizon tenue 7 s**),
  OPM #12 / #01 (sakuga 162980, 194936) ; fiche existante
  `corpus/fiches/COUP_CHARGE.md`.
- **La scène (~10 s)** : garde calme tenue ; la caméra pousse jusque dans
  son dos ; une anticipation lente ; UN coup, une seule carte ; puis la
  conséquence qui DURE : la destruction file jusqu'à l'horizon, les nuages
  se fendent, le vent retombe, il remet la main dans la poche.
- **Ce qu'elle entraîne** : la retenue (un seul coup rapide dans 10 s),
  la conséquence longue, le décor qui raconte. Notre point fort
  (l'animation) porte la scène.
- **Dépendance aux VFX / à Studio** : faible. Surtout du décor (roches,
  poussière, vent, nuages), où Studio aide (Terrain, destruction physique)
  mais qui se fait aussi ici.
- **Risque** : sans décor riche (horizon, ville, montagne), la conséquence
  est vide ; il faut construire l'arène.

## 2. « BLACK FLASH » (Jujutsu Kaisen)

- **Refs** : Black Flash, jeu type JJK (12e7dae5, 6,2 s, structure relue :
  2,2 s de combat en caméra de jeu, éclair blanc / rouge, cinématique
  collée à la victime, smear rouge, cartes inversées noir / blanc, cartes
  blanches à taches d'encre, puis **ralenti tenu 1,4 s** sur la victime) ;
  Black Flash de Gojo (2ka3-cCuHXg : 6 s de champ / contrechamp, noir à
  traits cyan) ; notre rafale v8 (déjà notée).
- **La scène (~7 s)** : échange rapide en caméra de jeu, un coup qui
  « décale » l'espace (distorsion noire, éclairs noirs et rouges), 1 s de
  cartes, puis le ralenti tenu.
- **Ce qu'elle entraîne** : l'effet signature très stylisé (éclairs noirs,
  distorsion) : exactement ce qui nous manque en VFX. Courte, donc rapide à
  itérer.
- **Dépendance aux VFX / à Studio** : FORTE. C'est le meilleur premier test
  du passage sur Studio : les stocks VFX de Milan et un tuto « Black
  Flash » suivi de A à Z, vérifiés par capture.
- **Risque** : dans notre labo actuel, avec des éclairs générés par
  programme, on retomberait sur la note VFX de la v12.

## 3. « LE TEMPS À REBOURS » (Rewind Clock)

- **Refs** : Rewind Clock (9,8 s, relu : 1,6 s de jeu, explosion, **anneau
  d'horloge doré tenu ~1 s = la signature**, BLANC, **le monde disparaît**
  (fond blanc, persos isolés) pendant 2 s de coups, 1,2 s de cartes
  « radio », rayon horizontal, retour au jeu avec débris) ;
  Black Hole Ability (construction en actes, fondu au noir silencieux).
- **La scène (~10 s)** : il arrête le temps (l'horloge dorée apparaît et
  tourne à l'envers), le décor s'efface, il frappe dans le vide blanc,
  l'horloge se brise, le temps reprend d'un coup : tous les coups arrivent
  en même temps.
- **Ce qu'elle entraîne** : une signature visuelle forte et simple
  (horloge = un modèle comme notre dragon), le changement de monde
  (éclairage, fond), le contraste figé / tout-à-coup.
- **Dépendance aux VFX / à Studio** : moyenne. L'horloge se fait comme le
  dragon (modèle + trait) ; le « monde qui disparaît » demande l'éclairage
  et les post-effets de Studio pour être premium.
- **Risque** : l'idée repose sur une direction artistique très nette
  (blanc pur, persos isolés) ; si c'est à moitié fait, ça fait « bug de
  rendu ».

---

## Recommandation

- **Si on passe sur Studio maintenant** : la **2 (Black Flash)**. C'est là
  que Studio et les stocks de Milan pèsent le plus, et elle est courte.
- **Si on reste dans notre labo** : la **1 (Un seul coup)**. Elle mise sur
  ce qu'on sait faire (animation, rythme, retenue) et dépend peu des images
  des VFX.
- La 3 en troisième, une fois qu'une signature (horloge) aura été validée.

Quelle que soit la cible : écrire sa fiche dans `corpus/fiches/` AVANT toute
clé, relire ses refs à 0,1 s, prédiction chiffrée avant de montrer.
