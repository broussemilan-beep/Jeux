# Checklist VFX — audit obligatoire avant de livrer un prototype

## Origine

Adaptée de la compétence `roblox-vfx` du dépôt public
[Astrablox/astrablox](https://github.com/Astrablox/astrablox)
(`.agents/skills/roblox-vfx/SKILL.md`, licence MIT), un studio Roblox
piloté par IA dont le lane `vfx` est nourri par cette référence.
Astrablox cible le vrai moteur Roblox (`ParticleEmitter`, `Beam`,
`Trail`, `RbxCameraShaker`) — nos prototypes rendent en Three.js/canvas
2D superposé, donc les noms d'API ne s'appliquent pas directement, mais
les PRINCIPES sont transposables tels quels et servent ici de grille
d'audit, pas de checklist à cocher mécaniquement.

Raison d'être de ce fichier : retour utilisateur direct sur ce
prototype (« la capacite de comprehension et vision... car tes
animation sont tjes pas ouf ») après consultation d'Astrablox — deux
manques identifiés dans notre process : (1) aucune cible visuelle
générée/jugée avant de construire (voir limite ci-dessous, pas
reproductible telle quelle ici — pas d'outil texte→image dans cette
session), (2) une compréhension VFX construite sur des résumés
WebSearch superficiels plutôt qu'une référence dense et sourcée. Ce
fichier corrige le point (2) ; le point (1) reste partiellement ouvert
(voir section finale).

## Les trois temps d'un effet (jamais improvisé, toujours dans cet ordre)

- **Anticipation** — quelque chose change avant le payoff (charge,
  poussière aspirée, lumière qui varie). Sans anticipation, le burst
  se lit comme un pop, pas un événement.
- **Burst** — le pic. Une frame doit porter tout l'effet — si on ne
  peut pas pointer LA frame la plus forte dans une capture, l'effet
  n'a pas de pic et se lira comme de la bouillie.
- **Dissipate** — la chute. Réduire l'intensité AVANT la disparition
  complète (fumée/braises qui survivent au flash) — rien ne doit
  disparaître net.

Ralentir l'anticipation lit mieux qu'accélérer le burst (même
principe qu'en animation : l'easing bat la vitesse brute).

## Les couches (choisies par repère, pas une checklist à remplir)

Un effet à une seule couche (un seul émetteur monté fort) se lit
"cheap" quel que soit l'éclat. Rôles à distribuer selon le repère :
**forme/coeur** (silhouette), **mouvement** (traînées/streaks — montre
où va l'énergie), **débris** (réagit avec le monde), **lumière**
(pulse qui éclaire la géométrie autour — sinon l'effet "flotte"),
**caméra** (shake/impact frame), **son** (la moitié du ressenti).

## Critères de contraste et d'échelle

- **Le contraste décide de la lisibilité** — un effet chaud et
  lumineux meurt dans une pièce chaude et lumineuse ; vérifier contre
  le fond RÉEL, depuis la caméra réelle du joueur.
- **L'échelle communique l'enjeu** — un petit événement et un
  événement énorme ne peuvent pas utiliser la même taille/vitesse/
  nombre. Si le même effet sert les deux, le gros événement est
  sous-vendu. (Un flash plein écran identique sur un jab de routine et
  sur un finisher écrase cette hiérarchie — trouvé et corrigé sur
  `r6_solar_smite`, voir plus bas.)

## Ce qui trahit un effet amateur (audit direct, item par item)

- Texture par défaut / bords francs / rectangle alpha visible.
- Couleur/taille/transparence en valeurs plates plutôt qu'en courbes ;
  rotation identique sur chaque particule.
- Pas d'anticipation : le burst apparaît sans prévenir.
- Pas de dissipate : tout disparaît sur la même frame.
- Un seul émetteur fait tout le travail ; pas de lumière, pas de
  shake, pas de son.
- L'effet flotte : rien dans la scène n'est éclairé ou déplacé par
  lui.
- Luminosité additive comme substitut de forme — un blob blanc sans
  silhouette.
- Opacité plein écran qui cache l'action au moment où elle doit se
  lire.
- Le même effet à la même échelle pour un petit événement et un
  énorme.
- Résidu : émetteurs encore actifs après la séquence, lumières
  laissées allumées.

## Audit réalisé sur `r6_solar_smite` (2026-09-23)

Lecture directe du code (`solar_smite_viewer.html`), pas seulement des
captures — chaque item vérifié contre la source, pas supposé :

| Critère | Constat |
|---|---|
| Anticipation | OK — noyaux visibles en continu pendant charge/combo (pas un pop), montée du finisher lente et lisible avant le lâcher. |
| Burst / pic net | OK — `drawFinisherFlash`/`drawComboImpact` ont un pic identifiable (flash + éclats radiaux). |
| Dissipate | OK — toutes les courbes d'alpha sont `1 - pow(age/life, n)`, jamais un `if (age > x) hidden` net. |
| Couches multiples | OK — forme (`drawSolarHalo`), mouvement (`drawArmSmear`, éclats radiaux), débris (`drawGroundDust`), lumière (`PointLight` réelles sur les mains et le noyau fusionné, intensité pilotée par le rayon), caméra (shake directionnel dédié au finisher). |
| Variance | OK — angle/vitesse/longueur de chaque éclat dérivés d'un seed par index (`Math.sin(seed*k)`), jamais uniformes. |
| L'effet flotte ? | Non — `drawScorchMark`/`drawGroundDust` réagissent au sol, lumières réelles projetées sur la géométrie. |
| Additif substitut de forme | **Trouvé et corrigé cette session-ci** — le noyau fusionné restait à pleine intensité pendant le hitstop du finisher et noyait le starburst d'impact (`mergedCoreFade` ajouté). |
| Opacité plein écran | **Trouvé et corrigé maintenant** — `drawComboImpact` utilisait un `fillRect` plein canvas identique en forme (juste l'alpha variait) pour un jab de routine ET le finisher ; remplacé par un flash RADIAL localisé au point de contact, le plein écran réservé exclusivement à `drawFinisherFlash`. |
| Échelle communique l'enjeu | OK après la correction ci-dessus — nombre d'éclats (18-158 combo vs 64 mais vitesse/rayon bien plus grands au finisher), rayon du flash (localisé vs plein écran), durée du hitstop, tout escalade. |
| Résidu | OK — toutes les intensités de lumière repassent à 0 hors fenêtre active (`showHandCores ? ... : 0`, etc.), pas de fuite entre relectures. |

## Limite honnête : la "vision" (concept-frames) n'est pas reproduite

Astrablox génère une image cible AVANT de construire, la fait juger
par un agent frais, et ne construit que vers une cible acceptée
(`.agents/skills/concept-frames/SKILL.md`). Cette session n'a pas
d'outil de génération d'image texte→image (vérifié — l'Adobe MCP
disponible ici édite des images existantes, il n'en crée pas). Tant
que ce manque n'est pas comblé, la vérification reste : cinématique
directe (position exacte) + cette checklist (lecture de code) +
capture a posteriori — jamais une comparaison à une cible visuelle
générée en amont. À rouvrir si un outil de génération d'image devient
disponible dans une session future.
