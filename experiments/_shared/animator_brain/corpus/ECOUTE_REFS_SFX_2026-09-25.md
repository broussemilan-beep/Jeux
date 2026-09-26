# Écoute des refs de Milan : le SON (2026-09-25)

**Pourquoi.** Milan : « il y a aussi les SFX ». Le son n'avait jamais été
fait (inventaire VFX, `recherche/vfx_2026-09-25/00_inventaire_du_depot.md`).
Il n'y a pas d'oreille dans ce bac à sable : tout ce qui suit est MESURÉ
(`outils/ecoute.py`, spectrogrammes ffmpeg), jamais « écouté ».

**Ce qui a une piste audio.** 14 vidéos uniques sur les envois de Milan
(les GIF n'en ont pas). Pour le son d'effets, 5 comptent : Black Flash
(12e7dae5), Stagnant Rage (4fb4f776), Rewind Clock (3ae71567), IMPACT
HAVEN (eba5ed69), Black Hole (01f4b1d2). Identités : `CATALOGUE_REFS.md`.

## Limites (à lire avant les chiffres)

- Ce sont des enregistrements d'écran de téléphone, mixés avec une
  musique ou un fond continu : le niveau médian est haut (41-48 dB) et les
  attaques ne dépassent le fond que de 3 à 5 dB. La « queue » à -20 dB n'est
  presque jamais atteinte (3 s = la limite de mesure).
- Une bande constante vers 600 Hz traverse TOUTES les captures (même IMPACT
  HAVEN, dès que le son démarre) : artefact d'enregistrement ou musique,
  [NON RÉSOLU]. Écartée de l'interprétation.
- Les parts par bande mélangent donc effet + fond. Ordre de grandeur, pas
  cible au pour-cent.

## Ce qui ressort malgré tout

1. **Un impact = une attaque large bande très courte, chargée en grave.**
   Montée 30-120 ms (fenêtre de mesure de 6 ms), et dans les 300 ms qui
   suivent : sub (<100 Hz) 0,45-0,8, grave 0,1-0,3, médium 0,03-0,3, aigu
   0,01-0,08. Sur le spectrogramme : des traits verticaux de 20 Hz à 8 kHz.
2. **Le VIDE avant le gros coup.** Stagnant Rage : de 3,59 à 4,45 s, les
   aigus (>1 kHz) tombent de plus de 25 dB (le son se vide progressivement
   dès 1,75 s), puis l'explosion repart large bande. Rewind Clock : 5,3-7,0 s
   presque vide, puis attaque. C'est la version son du « noir avant le
   boum » des cartes (ETUDE_VISUELLE). robloxIA donne 0,05-0,1 s de silence
   juste avant l'impact : les refs vont bien plus loin sur les ultimes.
3. **La densité dit le registre.** IMPACT HAVEN (montage de coups) : ~2
   attaques/s ; les ultimes : 0,1-0,7 attaque/s. Peu de sons, mais gros.
4. **Son et image.** L'attaque sonore tombe à ±40-150 ms du pic visuel le
   plus proche dans les cas nets (Black Flash -42 ms, Stagnant Rage +92,
   +147 ms, Rewind Clock +94 à +118 ms) : le son suit l'image de quelques
   images, jamais très en avance. Les écarts de plusieurs centaines de ms
   sont des attaques de la musique, pas des effets.

## Ce que le studio en a tiré (données, pas règles)

- `vfx_studio/sons.py` : banque synthétisée (craquement, corps, « coup »
  grave, sub, grondement + débris, souffles, aspiration, naissance) ;
  `impact_lourd` réglé sur (1) : mesuré avec le même outil, sub 0,66,
  grave 0,18, médium 0,16 (1re version : sub 0,95, un grondement sans coup).
- Le souffle du projectile est coupé net 60 ms avant la collision, et
  `critique_son` vérifie le vide avant chaque son marqué « impact » (2).
- Pas encore fait : le long vide des ultimes (0,9-1,7 s) — c'est une
  décision de MISE EN SCÈNE du Poing du Dragon (coup chargé), pas d'une
  recette isolée.
