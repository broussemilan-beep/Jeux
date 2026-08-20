# RANK ZERO — Document Maître de Production v1

**Ce document est le point d'entrée unique de la production.** Il consolide et remplace : le doc de bases initial, le Mandat Maître, la note de transmission GDD, et intègre les Addendums A/B. Il gouverne l'exécution autonome de Claude Code jusqu'à épuisement de la feuille de route.

**Hiérarchie des sources de vérité :**
1. `RANK_ZERO_MASTER_GDD` (joint) — vérité DESIGN (monde, pouvoirs, ennemis, zones, narration), avec sa discipline LOCKED/TBD, **amendée par la section 1 ci-dessous**.
2. `docs/ARCHITECTURE_VFX_v3.md` + `docs/addendum-A` (déjà dans le repo) — vérité TECHNIQUE (moteur, couches, primitives, pipeline, cycle de vie, déterminisme).
3. **Ce document** — vérité de PRODUCTION (décisions récentes, architecture dynamisme, autonomie, feuille de route). Si les Addendums B (dynamisme) ou le Mandat Maître ne sont pas encore dans `docs/`, leur contenu est intégré ici (sections 4-6) et fait foi.
En cas de conflit : méthode technique → docs techniques ; contenu/design → GDD ; séquencement/gouvernance → ce document.

**Calibration du niveau visé (à relire à chaque doute) :** la référence de structure est Hades (réponse des ennemis, caméra, mouvement du corps, couches de feedback) ; la référence de RENDU est Dead Cells / CrossCode / Hyper Light Drifter — pixel premium : peu de frames, énorme couche moteur, lisibilité absolue. On vise à égaler puis dépasser ce niveau de feel. Ne jamais juger un livrable contre le rendu peint haute résolution de Hades : ce n'est pas la cible du style, seulement celle du feedback.

---

## 1. Décisions récentes de Milan (amendements au GDD — font autorité)

### 1.1 Personnage — turnaround v3, SANS CAPE
Milan fournit une nouvelle référence (turnaround FACE/3-4/PROFIL/DOS, jointe à ce mandat) : morphologie compacte "légèrement chibi" conforme au GDD §2, et **suppression définitive de la cape-écharpe asymétrique**. Le GDD §2 et sa table LOCKED (§24) sont amendés : l'identité visuelle verrouillée devient — crâne chauve pâle quasi vierge, aucun emblème/armure/symbole de Classe, tenue en couches (tunique déchirée / harnais croisé de cuir / bandages avant-bras / gants sans doigts / pantalon sombre / bottes lacées), palette grise désaturée. La cape disparaît de tous les impératifs.

**Conséquences à intégrer :**
- La lecture de direction (dash, coups) reposait sur la cape ; elle repose désormais **entièrement sur la couche moteur** (section 4) : afterimages, traînées, lean, smears. Ces éléments passent de "amélioration" à "obligatoires" sur toute action rapide.
- Le gate de morphologie (`validate_morphology.py`) devient PLUS fiable : la cape était son facteur de confusion documenté (mesure de largeur torse). Après régénération, envisager de resserrer les tolérances (noté dans `data/morphology_gate.json`).
- Toute mention de cape dans les docs/prompts antérieurs est obsolète — ne pas la réintroduire dans les générations.

### 1.2 Régénération v3 du personnage
Rejouer le pipeline complet éprouvé (worklog A1-A9) avec la nouvelle référence : archiver la v2 (jamais supprimer), crop/downscale sous le seuil base64 identifié, régénérer TOUTES les animations depuis la reference-image (§5.3 — jamais de génération de mémoire), contrainte de gabarit explicite dans chaque description, gate morphologie (baseline auto depuis le nouvel idle), revue visuelle systématique (armes hallucinées, teintes hors palette), cuisson avec `foot_anchor()`, intégration, captures standardisées, redeploy web.

### 1.3 Dash ET esquive — deux actions séparées
Décision Milan. **Dash** = déplacement rapide existant (inchangé). **Esquive** = nouvelle action distincte : roulade/pas d'évitement avec frames d'invincibilité (i-frames) dans la logique de dégâts. Nouvel input (clavier + bouton tactile). Le squelette logique (état DODGE, i-frames, cooldown éventuel TUNABLE) se code immédiatement avec un placeholder visuel ; l'animation dédiée se génère avec le lot v3 (une animation de plus dans la régénération 1.2).

### 1.4 Confirmations
- **Aucun système d'énergie/mana** — cooldowns uniquement. Le "ressource si nécessaire" du GDD §17 et tout "coût en Énergie" résiduel sont à ignorer.
- **Arborescence GDD §18** : indicative, PAS un ordre de restructuration. Le repo actuel reste tel quel ; convergence progressive seulement là où c'est gratuit.
- **Bras-Faux (GDD §7.1)** : fiche complète, implémentable — enregistrer la palette Parasite (`data/palettes/parasite.json`, grayscale strict du §7, signature de Pouvoir, même logique §2.5 que `invocateur_vide`). Les frames de transformation du bras attendent la référence v3 ; recette + logique peuvent précéder.
- **Serpent Creux (GDD §6.2)** : fiche incomplète (matière TBD) — protocole section 7, flaguer sans combler quand son tour arrive.

## 2. Boucle d'exécution autonome

Pour chaque tâche de la feuille de route (section 6) :
```
1. Lire l'état concerné (fichier, recette, manifest) avant modification.
2. Implémenter UNE brique (discipline Sonnet, v3 §16).
3. Auto-tester : gates + smoke tests concernés au vert.
4. Capturer (headless, standardisé) si résultat visuel.
5. Auto-auditer contre la checklist (section 8).
6. Classer la tâche suivante selon la matrice (section 3) :
   autonome → enchaîner ; "à valider" → s'arrêter sur CETTE tâche,
   documenter la question ("EN ATTENTE — ..." dans le worklog),
   continuer les tâches indépendantes.
7. Worklog à jour. Redeploy web en fin de phase.
```
Claude Code n'attend PAS de nouveau prompt entre les tâches — ce document est le mandat continu.

## 3. Matrice de décision

**Autonome (décider, documenter, continuer) :** valeurs de timing/juice dans les bandes posées (méthode exagérer-puis-redescendre) ; choix d'implémentation technique respectant la section 9 ; corrections de bugs et enquêtes de cause racine ; quel archétype de cast réutiliser pour un pouvoir ; retouches manuelles mineures d'art (discipline en place) ; ordonnancement fin dans une phase ; ennemis de la vertical slice (GDD §10/§21) dans les palettes/matières définies.

**À valider (s'arrêter, flaguer) :** toucher l'identité visuelle verrouillée (section 1.1) ; nouvelle matière/palette signature pour un Pouvoir/Classe sans signature définie (seuls Invocateur et Parasite en ont une) ; 16e primitive au-delà des 15 nommées ; tout contenu narratif/monde non explicitement fourni (GDD TBD inclus — jamais inventer) ; dépense PixelLab significative au-delà d'un lot ponctuel habituel ; changement moteur/renderer/cible d'export ; modification d'un asset ayant un verdict humain positif dans `quality_labels.jsonl`.

## 4. Couche Dynamisme (Addendum B — architecture complète)

**Constat fondateur (vérifié dans le code) :** les attaques jouaient sur place (`velocity = 0` pendant le combo) et le monde ne répondait pas (rectangles sans réaction). La fluidité Hades/Dead Cells vient de PEU de frames + une couche moteur massive. La qualité se cherche dans cette couche, déterministe et gratuite en crédits — pas dans "plus de frames PixelLab".

**Trois systèmes :**

`AnimationComposer` (par entité) — données par animation dans le manifest cuit :
```json
"coup2": {
  "root_motion": { "distance_px": 26, "start_tick": 3, "end_tick": 7, "ease": "out_quad" },
  "squash": [ { "tick": 6, "x": 1.12, "y": 0.90, "hold": 2 } ],
  "lean_deg": 6,
  "afterimages": { "count": 2, "spacing_ticks": 2, "opacities": [0.5, 0.2] }
}
```
Root motion via `velocity` (murs solides), jamais `position` directe.

`HitResponse` (côté cible) — sur `take_damage()` : flash blanc 2 ticks (shader sur le sprite de la cible), recul existant, chiffre de dégâts poolé (police pixel, monte et s'efface ~20 ticks) ; à la mort : `shardBurst` teinté ennemi + décal persistant au sol (registre à budget par zone, via VfxBudget).

`CameraDirector` (étend le shake) — micro-zoom punch +2-3% sur 3 ticks pour impacts medium+ ; lookahead 12-20px dans la direction du dash ; shake existant inchangé. Le cadrage actuel est bon ; le problème était l'inertie.

**Leviers obligatoires sur toute action rapide (renforcé par la disparition de la cape, §1.1) :** afterimages, smears (1 frame, doc v3 §6.4), lean, et `directionalStreak` post-render quand disponible.

## 5. Usine à pouvoirs

Le personnage n'a PAS une animation par compétence : **3-4 archétypes de cast génériques** (projection avant / frappe de zone / invocation / canalisation) — chaque compétence choisit son archétype dans sa recette ; son identité vient du VFX (primitives × matière × palette × timing). Asset dédié seulement pour une entité invoquée (Gueule Vide) ou une transformation corporelle (Bras-Faux). Compléter la bibliothèque de primitives (6→15). Chaque compétence du GDD se traduit en recette JSON au format existant, palette liée à son Pouvoir/Classe d'origine.

## 6. Feuille de route consolidée

**J1 — La réponse au coup (priorité absolue, inchangée) :** root motion sur les 3 coups, hurt flash, chiffres de dégâts, death burst, décals ; test exagéré hit-stop/shake ; enquête contact visuel Gueule Vide avant retouche de timing.
**J2 — Le corps en mouvement :** AnimationComposer complet (squash/lean/afterimages), CameraDirector, smears dash + coup 3.
**R3 — Régénération v3 :** dès réception de la référence (section 1.2), + animation esquive + frames Bras-Faux. Peut s'intercaler avec J1/J2 (le juice est indépendant des sprites).
**D — Usine à pouvoirs :** archétypes de cast, primitives 6→15, Bras-Faux complet (recette+logique avant l'art si besoin), esquive (logique immédiate, section 1.3).
**E — Directions :** 8 directions a minima pour idle/déplacement ; dash/combo/esquive si budget PixelLab, sinon flag.
**F — Le monde :** mini-tileset d'arène réel (sol texturé, vignette, props), cohérent palette — sans attendre plus de contenu.
**G — Ennemis :** Crawler, Brute, Ranged (GDD §10/§21), discipline reference-image, HitResponse natif.
**H — Vertical slice GDD §21 :** zone Première Gate, boss Gate Maw, petit Outpost, UI de progression (HUD, écran perso avec CLASS = NONE, XP/stats/slots/loadout/cooldowns), boucle de run §20.
**Ordre par défaut :** J1 → J2 → R3 (dès réception) → D → E/F/G en parallèle selon disponibilité art/code → H. Redeploy web en fin de chaque phase.

## 7. Protocole GDD (LOCKED/TBD)

Lire intégralement, produire un résumé actionnable. LOCKED = ne jamais remplacer (amendements section 1 exceptés). TBD = jamais présenté comme canonique, jamais comblé par invention — c'est un flag section 3. Traduire chaque compétence suffisamment spécifiée en recette ; signaler toute incohérence avec les décisions verrouillées plutôt que la résoudre silencieusement. Plan d'implémentation soumis avant de coder le contenu de la phase H.

## 8. Checklist avant de déclarer une brique finie

- [ ] Gates au vert (palette, morphologie, hitbox/visuel), aucune régression sur les smoke tests.
- [ ] Pouvoir : recette conforme à la signature de son Pouvoir/Classe d'origine, ou flag si la signature n'existe pas.
- [ ] Animation d'action : root motion + réponse de la cible présents — jamais un sprite qui joue sur place.
- [ ] Action rapide : afterimages/smear/lean présents (obligatoire depuis la suppression de la cape).
- [ ] Capture standardisée (2 fonds × 3 échelles) archivée + manifest à jour.
- [ ] Worklog à jour (fait/branché, preuve, prochaine étape). `quality_labels.jsonl` jamais modifié par Claude Code.
- [ ] Fin de phase : build web redéployé.

## 9. Garde-fous non négociables

Godot natif, renderer Mobile (web = exception de test documentée, jamais la cible). Seed toujours déterministe — aucune horloge, aucun random non seedé dans le chemin VFX. Un fichier = une primitive/recette/palette/gate. Git LFS pour tout binaire. Aucun verdict qualité auto-attribué. Aucune invention de lore/classe/pouvoir/nom au-delà du GDD et de ses amendements. Recul visible sur tout coup qui touche. Bleu allié / rouge ennemi, non contournable. Bandes de valeur (v3 §3) vérifiées automatiquement. Discipline Sonnet : une brique par session, vérifier avant de déclarer fini.

---

## Instruction finale à Claude Code

1. Enregistrer la référence v3 jointe (section 1.2) et amender la lecture du GDD selon la section 1.
2. Suivre la feuille de route section 6 dans l'ordre par défaut, en autonomie complète sur la matrice "autonome", avec arrêt documenté sur tout point "à valider".
3. Redéployer le build web à chaque fin de phase — c'est là que Milan juge le feel, et son verdict sur ce build est le seul juge artistique du projet.
4. Ce document est le mandat continu : ne pas attendre de nouveau prompt entre les tâches.
