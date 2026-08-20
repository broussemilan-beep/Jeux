# RANK ZERO — Master Game Bible / GDD

Version 0.1 — source de vérité DESIGN (monde, pouvoirs, ennemis, zones, narration),
amendée par `docs/PRODUCTION_MANDATE_v1.md` section 1 (voir ce fichier pour la
hiérarchie des sources de vérité). Converti depuis le .docx fourni par Milan,
contenu textuel inchangé.


## 0. VISION

RANK ZERO est un action-RPG pixel art premium sous Godot, à combat temps réel (attaque, dash, esquive, combo). Le monde est une civilisation fantasy multi-races régie par un Système omniprésent.
À l'Éveil, chaque individu reçoit une Classe fixe et les compétences correspondant à cette Classe. Le protagoniste est l'unique individu connu que le Système refuse de classer : CLASS = NONE / ZERO. Cette anomalie lui permet d'équiper des compétences provenant de Classes différentes.
Ton : posé, semi-réaliste, mystérieux, fantasy/manhwa, avec humour léger mais sans méta-comédie permanente.

## 1. PILIERS LOCKED

Combat temps réel : déplacement, attaque, dash, esquive, combo, hit-stop, recul.
Liberté de Classe : les autres sont spécialisés ; Rank Zero peut mélanger les compétences.
Double progression : XP/Niveau + Maîtrise par usage.
Pixel art premium : silhouette et VFX lisibles à petite échelle.
Chaque Pouvoir possède son propre langage visuel.
Le Système est une force du monde, pas seulement une interface.

## 2. RANK ZERO — PERSONNAGE

Race : humanoïde étrange, légèrement goofy, sèche/compacte, peu parlant. Le nom exact de la race est TBD.
Crâne chauve, peau pâle, visage quasi vierge de traits.
Aucun emblème, aucune armure de faction, aucun symbole de Classe.
Cape/écharpe asymétrique flottant d'un côté.
Morphologie finale : légèrement chibi, mais pas grosse tête caricaturale ; corps plus épais et compact, jamais massif ou musclé.
Tenue en couches séparables : sous-vêtement, robe/tunique, harnais/sangles, cape-écharpe, sous-couche, bandages, gants, chaussures.
Palette : gris cendre, gris moyen/clair, charbon, noir doux ; accents éventuels bleu-gris et lilas-gris très pâles. Pas de couleur de Classe.

## 3. LE SYSTÈME

Le Système est apparu plusieurs siècles avant le jeu. Son créateur est inconnu publiquement. La société le considère comme une loi naturelle.
Éveil standard :
RACE → NIVEAU → CLASSE → COMPÉTENCES → RANG.
Les Classes sont normalement fixes : Guerrier, Épéiste, Lancier, Archer, Mage, Invocateur, etc. La liste complète reste extensible.
Rank Zero reçoit :
CLASS = NONE / ZERO.
ZERO signifie que le Système ne possède aucune catégorie valide pour lui, pas simplement qu'il est faible.
Mystère central : pourquoi le Système ne peut-il pas le classer ? Pourquoi certaines Gates semblent-elles réagir à lui ?

## 4. STATS & PROGRESSION

4 stats LOCKED : FOR, AGI, INT, VIT.
FOR = puissance physique.
AGI = mobilité/vitesse selon les compétences.
INT = puissance magique/invocation.
VIT = PV/résistance.
Les points sont distribués à chaque niveau.
XP/Niveau : augmente la puissance globale, débloque des points de stats et des slots.
Loadout : compétences modulaires équipables dans un nombre limité de slots.
Valeur de départ proposée : 2 slots actifs, puis progression vers 6 slots ; valeurs exactes TUNABLE.
Maîtrise : chaque compétence progresse avec son utilisation réelle en run, indépendamment du niveau du personnage. Les paliers doivent idéalement modifier le comportement, le timing, la zone ou une propriété, pas seulement donner +dégâts.

## 5. POUVOIRS ET COMPÉTENCES

Un POUVOIR = identité générale de combat.
Une COMPÉTENCE = action équipable précise.
Le nombre de compétences par Pouvoir n'est volontairement PAS fixé.
Arborescence :
Pouvoirs/
  Invocateur/
  Parasite/
  TBD/
Chaque compétence doit avoir : nom, Pouvoir, Classe d'origine, rôle, tier, scaling, portée, durée, conditions de fin, recul cible, couches VFX, primitives, matière, palette, 3 paliers de Maîtrise, animation, son et données Godot.

## 6. INVOCATEUR

Principe : l'invocation n'est PAS un compagnon. L'invocation EST l'attaque.
Un monstre apparaît brièvement, exécute son attaque signature, puis disparaît.
Aucune IA de suivi complète dans la Phase 1.
6.1 GUEULE VIDE
Tier 2/6. INT → dégâts.
Une petite créature chétive apparaît dans une zone ciblée, mord une fois puis se désagrège.
Portée de pose : ~4 m. Durée visuelle : ~0,7 s. Zone de morsure : ~1,5 m. Une attaque. Aucun déplacement libre, aucun suivi.
Fin : attaque terminée → disparition.
Maîtrises : I Morsure Persistante ; II Double Mâchoire ; III Dévoration.
Matière : INK.
Primitives : groundRing, runicStamp, fractureLine, impactFlashFrame, shardBurst.
Palette : bleu allié froid + gris-lilas désaturé + gris cendre + noir d'encre.
Tout ennemi touché reçoit un recul visible.
6.2 SERPENT CREUX
Concept validé provisoirement. Un serpent très fin apparaît brièvement, déjà comprimé, puis détend brutalement son corps en ligne droite pour traverser les ennemis avant de disparaître.
Rôle : portée supérieure à Gueule Vide, attaque linéaire, plusieurs cibles possibles, aucun compagnon et aucune IA.
Matière et fiche VFX complète : TBD.

## 7. PARASITE

Principe inverse de l'Invocateur : le monstre n'apparaît pas séparément ; le corps de Rank Zero devient l'arme.
Style : symbiose organique, fibres, membranes, tendons, croissance anormale, transformations partielles. Pas d'armure et pas de magie lumineuse.
Palette stricte : grayscale désaturé, gris cendre, gris foncé, noir, pointe de bleu-gris pâle et lilas-gris pâle. NO PURPLE saturé, NO GLOW, NO MAGIC LIGHT EFFECTS.
7.1 BRAS-FAUX
Tier 2/6. FOR → dégâts.
Le parasite transforme l'avant-bras en membre organique allongé terminé par une faux/crochet. Rank Zero effectue un seul balayage puis le parasite se rétracte.
Portée ~1,5 m, arc ~90°, durée ~0,5–0,7 s, une frappe, aucun déplacement automatique.
Maîtrises : I Crochet ; II Membre Renforcé ; III Réflexe Parasitaire.
Matière : ROOT.
Primitives : ribbonTrail, fractureLine, arcSlash, impactFlashFrame.
Chaque coup qui touche impose un recul visible.

## 8. COMBAT

Boucle : observer → se déplacer → attaquer → dash/esquive → exploiter l'ouverture → compétence → confirmation du hit → repositionnement.
États joueur : IDLE, MOVE, ATTACK, DASH, DODGE, HIT, SKILL, DEAD.
Combo de base proposé : 3 coups + finisher.
Le feedback d'impact combine hit-stop, petit shake, son et recul ; il reste proportionnel à la puissance.
Le joueur doit mourir principalement parce qu'il lit mal une attaque ou se place mal, pas uniquement parce que les ennemis ont énormément de PV.

## 9. ARCHITECTURE VFX

8 couches possibles : anticipation, action core, trail, contact, consequence, feedback, post-render, UI.
Primitives disponibles : arcSlash, impactStar, impactFlashFrame, groundRing, fractureLine, ribbonTrail, shardBurst, converge, spiral, beamSegment, runicStamp, smokePuff, dustKick, orbital, screenSlash.
Phase 1 : viser 4 à 6 primitives par compétence.
Convention : alliés = BLEU ; ennemis = ROUGE. Le bleu est un langage de gameplay, pas nécessairement la couleur dominante d'un asset.

## 10. ENNEMIS

Archétypes de base :
Crawler : petit, rapide, harcèlement.
Brute : lent, lourd, grosses attaques télégraphiées.
Skirmisher : agile, repositionnement.
Ranged : pression à distance.
Shield : bloque le front et force le contournement.
Elite : variante renforcée avec pattern supplémentaire.
Boss : silhouette unique, télégraphes, phases, attaques reconnaissables, récompense.
Familles par environnement :
Forêt : Rootling, Hollow Stag, Spore Crawler, Briar Brute.
Ruines/cité : Glass Wraith, Sewer Maw, Broken Sentinel, Mimic Husk.
Mines : Stone Burrower, Ash Worm, Ore Golem, Deep Maw.
Gate corrompue : Null Husk, System Fragment, Classless Aberration, Failed Spawn.
Noms de travail.

## 11. MONDES ET ZONES

Zone 1 — Outpost de l'Éveil : hub/tutorial, PNJ, statut social, première Gate.
Zone 2 — Première Gate / Hollow Gate : premier donjon, combats, loot, boss Gate Maw.
Zone 3 — Forêt des Restes : forêt anormale, brume, racines, boss Hollow Stag.
Zone 4 — Cité des Classes : grande zone civilisée, Guilde, boutique, rival, démonstration du système social.
Zone 5 — Mines d'Abîme : tunnels, minerais, anciennes infrastructures, boss Ore Golem.
Zone 6 — Gate Corrompue : géométrie étrange, ennemis mal classés, fragments d'interface, boss Failed Class.
Structure standard d'une Gate :
Entrée → combats → loot/événement → embranchement → Elite → repos → boss → récompense → sortie.

## 12. CIVILISATION MULTI-RACES

Le monde est une civilisation multi-races où humains, sylvains, Feralis, Forgefolk, Abyssins, Brumes et autres peuples coexistent.
La race n'empêche pas la vie sociale ; la Classe influence davantage le statut.
Rank Zero est socialement étrange parce que l'administration et les Guildes utilisent le Système comme référence.
Race de Rank Zero : TBD. Sa race ne doit pas être la cause directe de son anomalie.

## 13. PERSONNAGES CLÉS

Allié/guide : TBD — explique le monde et humanise Rank Zero.
Rival : TBD — Éveillé d'une Classe prestigieuse ; croit que les règles existent pour une raison ; pas un méchant simpliste.
Autorité du Système : TBD — surveille les anomalies et représente les institutions liées au Système.
Allié secondaire : TBD — race différente, autre regard sur les Classes et la société.

## 14. SAISON 1 / NARRATION

Acte I — L'Inclassable : Éveil, Rank Zero, rejet, premier combat, première Gate.
Acte II — Construire son propre chemin : premières compétences, Classes, rival, Cité des Classes.
Acte III — Les règles se fissurent : Gates anormales, ennemis mal classés, archives interdites.
Acte IV — Le Système regarde : événements semblant liés à Rank Zero.
Chapitres proposés :
1 L'Éveil
2 Rank Zero
3 Première Gate
4 Première compétence volée
5 Cité des Classes
6 Le Rival
7 Forêt des Restes
8 Premières anomalies
9 Mines d'Abîme
10 Gate Corrompue
11 Données effacées
12 ZERO
Final de saison : le Système affiche une donnée impossible, par exemple :
[ANALYSIS FAILED]
[ENTITY: ZERO]
[ORIGINAL CLASS: █████]
[ERROR]
[DATA DELETED]
La raison réelle n'est pas encore entièrement révélée.

## 15. BOSS

Gate Maw : boss tutoriel, masse organique de Gate avec grande gueule ; morsure, charge, projection, frappe au sol, phase énervée.
Hollow Stag : cervidé anormal ; charge, bois, racines, mobilité, petits ennemis.
Ore Golem : poing, onde de choc, rochers, garde frontale, terrain.
Failed Class : miroir narratif de Rank Zero ; entité dont la Classe n'a pas été correctement générée. Question centrale : Rank Zero est-il unique, ou seulement un survivant d'un phénomène plus ancien ?

## 16. LOOT / ÉQUIPEMENT / ÉCONOMIE

Loot : équipements, matériaux, compétences, fragments, consommables, monnaie.
Équipement proposé : arme, tenue, accessoires, reliques.
La construction doit reposer principalement sur stats + loadout + maîtrise + équipement.
Monnaies provisoires : Gold, matériaux, fragments du Système.
Boutique/craft/déblocages : à préciser.

## 17. UI

HUD : PV, ressource si nécessaire, niveau, XP, compétences équipées, cooldowns, dash/esquive.
Écran personnage :
NAME / RANK / LEVEL / FOR / AGI / INT / VIT / CLASS / SKILLS / EQUIPMENT.
Rank Zero doit afficher CLASS = NONE et ne jamais recevoir une Classe inventée.

## 18. GODOT — ARCHITECTURE

Arborescence cible :
scenes/player, enemies, bosses, zones, gates, ui, npcs
scripts/player, combat, skills, enemies, progression, loot, gates, system
data/skills, powers, enemies, zones, items, npcs
art/player, enemies, skills, vfx, environments, ui
audio/
Principe : data-driven, composants réutilisables, signaux Godot, paramètres tunables, logique séparée des données. Les compétences ne doivent pas être codées comme des exceptions individuelles dans le joueur.

## 19. DATA COMPÉTENCE

Chaque compétence doit stocker au minimum :
id, power, source_class, importance_tier, scaling, range, duration, hit data, cooldown, primitives, material, palette, mastery tiers.
Machine de compétence :
READY → ANTICIPATION → ACTIVE → CONTACT → CONSEQUENCE → RECOVERY → COOLDOWN.
Les couches inutiles sont désactivées.

## 20. BOUCLE DE RUN

Hub → choisir Gate → entrée → combats → XP/loot/maîtrise → route → Elite → Boss → récompense → retour → amélioration → nouvelle Gate.
Règle de conservation exacte de Maîtrise après mort : TBD.

## 21. VERTICAL SLICE PHASE 1

Objectif : prouver que le jeu fonctionne avant d'agrandir le contenu.
Joueur : Rank Zero avec déplacement, attaque, dash, esquive.
Progression : XP, niveau, stats, slots.
Compétences : système data-driven + loadout + cooldown + maîtrise ; Gueule Vide et Bras-Faux obligatoires ; Serpent Creux optionnel.
Ennemis : Crawler, Brute, Ranged.
Boss : Gate Maw.
Zone : Première Gate.
Hub : petit Outpost.
UI : statut, Classe NONE, premiers écrans de progression.

## 22. ORDRE DE PRODUCTION

A — Fondation : projet Godot, contrôleur, caméra, collisions, stats, HUD.
B — Combat : attaque, dash, esquive, dégâts, recul, hit-stop, mort.
C — Skills : data, loadout, cooldown, Gueule Vide, Bras-Faux, maîtrise.
D — Contenu : 3 ennemis, Gate, boss.
E — Progression : XP, niveaux, stats, slots, loot.
F — Monde : Outpost, PNJ, boutique, quête, transition.
G — Polish : animations, VFX, audio, UI, optimisation, sauvegarde.

## 23. RÈGLES DE PRODUCTION

Quand une donnée est LOCKED, ne pas la modifier arbitrairement.
Quand une donnée est TBD, ne pas la présenter comme définitive.
Ne pas créer une architecture gigantesque avant un prototype jouable.
Ne pas transformer Rank Zero en Classe fixe.
Ne pas faire de chaque compétence une simple augmentation de dégâts.
Ne pas donner à une compétence Phase 1 une IA ou une complexité hors scope.
Tout coup qui touche doit produire un recul visible sur la cible.
Chaque asset important doit avoir une cohérence de silhouette, d'échelle et de palette.

## 24. TABLEAU LOCKED / TBD

LOCKED :
RANK ZERO ; Godot ; pixel art premium ; combat temps réel ; dash/esquive/combo ; civilisation multi-races ; protagoniste sans Classe ; Rank Zero ; FOR/AGI/INT/VIT ; loadout à slots ; XP + Maîtrise ; compétences inter-Classes ; protagoniste silencieux ; crâne chauve/pâle ; cape asymétrique ; palette désaturée ; absence d'emblème ; Invocateur = attaque invoquée ; Parasite = transformation corporelle ; recul visible ; 8 couches VFX ; primitives limitées ; bleu allié / rouge ennemi.
TBD :
nom définitif du monde ; nom de la race de Rank Zero ; origine exacte du Système ; nombre de Classes ; nombre de Pouvoirs ; nombre de compétences par Pouvoir ; noms définitifs des PNJ/zones ; économie ; mort ; sauvegarde ; équilibrage ; durée totale ; nombre final de chapitres ; fin exacte.

## 25. PHILOSOPHIE FINALE

Rank Zero ne doit pas être un jeu où le joueur choisit une Classe. C'est un jeu où il découvre progressivement : « Je peux devenir ce que le Système m'interdit d'être. »
Chaque compétence récupérée est une pièce de son identité.
Chaque Classe rencontrée représente une voie que les autres sont obligés de suivre.
Rank Zero, lui, n'a pas de voie. Il en construit une.

## 26. INSTRUCTION À CLAUDE CODE

Ce document est la source de vérité design du projet.
LOCKED = ne pas remplacer arbitrairement.
TBD = à décider plus tard, ne pas inventer comme vérité canonique.
Pour toute nouvelle mécanique : vérifier piliers, stats, loadout, maîtrise, VFX, identité de Rank Zero et complexité Phase 1.
Construire d'abord un prototype jouable et extensible, puis enrichir le contenu.
