# Auto-évaluation VFX + SFX : Poing du Dragon v10 (2026-09-25)

Demandée par Milan : « une fois que tu auras fini, note sur 10 tes VFX
comparés à ceux observés ; il y a aussi les SFX ». Écrite AVANT son avis,
pour mesurer mon écart à son œil (comme les prédictions de
`notes_milan.jsonl`).

**Comment j'ai jugé.** Mes planches, côte à côte avec les pics d'effets des
refs (`outils/planche_vfx.py` sur Stagnant Rage 4fb4f776, Black Flash
12e7dae5 et IMPACT HAVEN eba5ed69 ; planches non versionnées, œuvres
protégées), en caméra cinéma et en caméra de jeu. Le son est jugé sur
MESURES (`outils/ecoute.py`, spectrogrammes) : je n'ai pas d'oreille.

Échelle : 10 = le niveau des refs dans leur registre (Stagnant Rage pour
l'explosion, IMPACT HAVEN pour le coup sec, Black Flash pour les cartes).

## VFX : 6 / 10

| moment | note | ce qui tient | ce qui manque face aux refs |
|---|---|---|---|
| rafale, palier 1-2 | 6,5 | étoile blanche 2 images, anneau fin, croissant : lisible même petit, y compris en caméra de jeu (ZOffset réglé : 1er essai caché par le corps) ; hiérarchie des paliers nette | IMPACT HAVEN : trait de vent derrière le poing à chaque coup, et l'image noire / blanche de la silhouette ; nos coups n'ont ni l'un ni l'autre |
| coup chargé | 6,5 | la STRUCTURE est celle des refs : contact, noir, cartes, blanc, explosion qui sort du blanc, victime projetée qui laisse un sillage de fumée | Stagnant Rage : cœur additif très lumineux, traînées d'énergie rouges, DÉBRIS (blocs de sol qui volent), densité 3-5 fois la nôtre ; notre feu cel est net mais maigre |
| plongée (air) | 5,5 | le sillage suit le poing, les lignes de vitesse partent derrière | fin, peu visible en caméra de jeu ; pas de déformation de l'air autour du corps ni d'onde qui précède le poing |
| contact aérien | 6 | le flash remplit l'écran pendant le hitstop (image d'impact), explosion en l'air sans couches au sol | le flash plein écran est BLANC-JAUNE et flou, pas un vrai carton graphique net comme Black Flash |
| impact au sol | 6 | dôme, anneau, vague à dents, feu, fumée : l'onde se lit, les corps restent visibles | pas de débris ni de fissures animées, pas de poussière rasante ; Stagnant Rage remplit le sol de blocs et de traînées |
| aura / dragon | 4 | inchangé depuis v9 (mèches dorées, rubans de fumée codés à la main) | pas encore refait au studio ; la forme de DRAGON attend la ref promise par Milan |

**Ce que le studio fait bien (hors note, c'est l'outil).** Une recette =
une donnée jouée À L'IDENTIQUE par le labo, le lecteur et Roblox (moteur
testé contre le vrai moteur de l'aperçu : 107 contrôles) ; les limites
officielles sont vérifiées automatiquement (critique.py) ; le défilement de
texture est rendu comme Roblox le fera. Je lui donnerais 8 : il manque la
preuve dans Studio lui-même (aucun accès ici) et les identifiants d'assets.

## SFX : 5 / 10

| mesure (même outil que pour les refs) | refs | nous |
|---|---|---|
| sub des 300 ms après un gros impact | 0,45-0,8 | 0,64 (coup chargé), 0,81 (sol) |
| vide avant le gros coup | Stagnant Rage 0,86 s, aigus -25 dB | 0,1 s au coup chargé (le noir) ; 60 ms avant le contact aérien ; -16,8 dB avant le sol |
| silence numérique | jamais | corrigé : fond de vent sous la révélation (1er mixage : 3 s de silence total) |
| densité | 2 attaques/s (montage de coups) ; 0,1-0,7 (ultimes) | 2,9 attaques/s sur toute la technique |

Ce qui tient : la structure (impacts chargés en grave, craquement puis vide
puis boum, souffle coupé avant le contact, variations de hauteur pour éviter
la mitraillette).

Ce qui manque :
- tout est synthétisé (bruit + sinus), sans enregistrement : pas de
  texture réelle (roche qui casse, tissu, air déchiré), pas d'espace
  (réverbération) ;
- un seul son d'impact lourd, réutilisé partout ;
- le vide du coup chargé est très court comparé aux ultimes des refs
  (0,1 s contre 0,86 s) : c'est une décision de mise en scène, pas du
  son seul ;
- je ne sais pas si ça SONNE bien : aucune mesure ne remplace l'oreille de
  Milan.

## Prédiction de l'avis de Milan

VFX 6 (fourchette 5-7), SFX 4,5 (fourchette 3,5-6). Pour : c'est la
première fois que les effets ont des couches (dôme, vent, feu peint, fumée)
et du son. Contre : face à Stagnant Rage, nos explosions sont maigres et
sans débris, et le son synthétique risque de sonner « jeu vidéo des années
90 ».

## Ce qui ferait monter la note (dans l'ordre)

1. **Débris** : des blocs de sol qui volent (Parts physiques ou meshes
   simulés dans l'aperçu) + fissures au sol animées. C'est l'écart le plus
   visible avec Stagnant Rage.
2. **Cœur additif + bloom dans le lecteur** : le lecteur du Dragon n'a pas
   de bloom (le labo en a un) ; en jeu, BloomEffect est déjà animé.
3. **Traînée de vent derrière chaque coup de la rafale** (IMPACT HAVEN).
4. **Aura en forme de dragon**, dès que Milan envoie la ref.
5. **Son** : banque d'enregistrements libres de droits (CC0) en couches
   sous la synthèse, et un vide plus long avant le coup chargé, décidé avec
   la mise en scène.

## Après le retour de Milan (VFX 4/10) : v12

Milan a mis **4** (je prédisais 6) : « le dragon est moche, pas du tout du
modèle premium ; les VFX construits sont nuls par rapport au pack et aux
refs ». Écart de 2 points : je comparais mes effets à MES versions
précédentes, pas au pack (biais noté au CARNET §6).

Ce que la v12 change, jugé cette fois contre les refs (captures
`captures/verification/2026-09-25-v12-*`) :

| moment | avant (v11) | v12 | ce qui manque encore face aux refs |
|---|---|---|---|
| dragon | ruban de Beams + carte peinte (autocollant) | modèle 3D riggé, écailles lisibles, crinière brune, gueule ouverte, nimbé de feu qui traîne derrière lui | tête lisse ; pas d'éclatement radial ni de tourbillon plein écran (GIF 7a2b4ae8) |
| impact au sol | dôme, anneau, feu, fumée | + débris peints qui jaillissent et retombent, + bloom | fissures animées au sol, poussière rasante |
| lecteur | sans bloom | bloom (= BloomEffect du jeu) | — |

Estimation (avant l'avis de Milan, `notes_milan.jsonl` v12) : VFX 6
(fourchette 5-7).
