# Addendum A — Cycle de vie, dégradation et synchronisation

**Projet : Rank Zero — complément à `docs/ARCHITECTURE_VFX_v3.md`**

> Cet addendum ne remplace rien. Le v3 reste la référence : Godot/GDScript, ticks à 60/s, capture headless, tranche verticale. Il ajoute cinq points absents du v3, extraits d'un contrat de production externe dont le reste (event router, pooling, télémétrie, CI d'audit, profils thermiques, TypeScript, millisecondes, Playwright) est **volontairement écarté** — surdimensionné pour l'échelle actuelle du projet et incompatible avec la base déjà construite.
>
> Rien ici ne demande de reconstruire quoi que ce soit. Chaque section s'applique à l'existant sans le casser.

---

## A.1 Couches protégées vs dégradables

Les 8 couches (§4 du v3) ne se valent pas quand il faut couper.

| Couche | Statut |
|---|---|
| 1. BODY | **protégée** |
| 2. ANTICIPATION | primaire protégée, secondaires dégradables |
| 3. ACTION CORE | **protégée** |
| 4. TRAIL | dégradable |
| 5. CONTACT | **protégée** (primaire : `impactFlashFrame` + recul) |
| 6. CONSEQUENCE | dégradable |
| 7. FEEDBACK | budget global propre, jamais instancié librement par une recette |
| 8. POST-RENDER | budget global propre, une passe par frame (§10.1 du v3) |

Chaque couche d'une recette porte un champ `degradable: true|false`. Les couches protégées sont `degradable: false` — un audit doit rejeter toute recette qui déclare une couche protégée comme dégradable.

## A.2 Ordre de dégradation quand un budget est dépassé

`VfxBudget` (§8.2 du v3) sait mesurer, mais le v3 ne dit pas quoi sacrifier. Ordre imposé :

1. réduire/supprimer les particules purement décoratives ;
2. réduire les débris secondaires ;
3. raccourcir la dissipation ;
4. réduire la fréquence des trails ;
5. fusionner les instances secondaires proches ;
6. désactiver distortion et screen slices ;
7. **plancher intouchable** : BODY, ACTION CORE, CONTACT primaire, lisibilité de la hitbox, feedback essentiel.

Une dégradation ne peut **jamais** : modifier la zone visible correspondant à la hitbox, supprimer le core, supprimer `impactFlashFrame` sur un impact majeur, ni supprimer le recul de la cible.

## A.3 Marqueurs d'animation — synchroniser au lieu de coder en dur

Problème réel déjà rencontré dans le projet : `player.gd` et `gueule_vide.gd` pilotent leurs frames et leurs contacts par des compteurs de ticks internes, séparés de la lecture du sprite. C'est correct (les ticks font autorité, §16.3), mais fragile : changer une animation oblige à retrouver et corriger les constantes à la main.

Toute animation d'action expose désormais 5 marqueurs, définis en ticks dans le manifeste cuit de l'animation :

```text
visual_anticipation_start
visual_release
visual_contact
visual_recovery_start
visual_end
```

Les couches d'une recette peuvent démarrer sur un marqueur (`start_marker`) plutôt que sur un `start_tick` absolu. Le `start_tick` reste valide et supporté — c'est ce qu'utilisent les recettes actuelles, elles ne sont pas à réécrire. Le marqueur devient la forme préférée pour toute nouvelle animation d'action, afin qu'un ajustement de timing d'animation ne désynchronise plus silencieusement le VFX ou la fenêtre de contact.

## A.4 Politiques de cycle de vie

Aucune recette actuelle ne déclare ce qui arrive si son lanceur meurt en plein cast ou si la scène change. À ajouter dans chaque recette :

```json
"lifecycle": {
  "cancellable_before": "release | contact | never",
  "owner_death_policy": "stop | finish_core_then_stop_secondary | detach",
  "scene_change_policy": "stop_immediately",
  "max_lifetime_ticks": 48
}
```

Règle absolue : après nettoyage, aucun timer, trail, nœud Godot, audio ou référence au propriétaire ne survit. Le nettoyage doit être déclenché par les trois voies — timeout, mort du propriétaire, changement de scène — pas seulement par le timeout comme aujourd'hui.

Valeurs à appliquer à `power.gueule_vide.cast` : `cancellable_before: "release"` (l'invocation peut être annulée avant la morsure, plus après), `owner_death_policy: "finish_core_then_stop_secondary"` (la créature termine sa morsure même si le joueur meurt — elle a été arrachée au monde, elle n'est pas liée à lui), `scene_change_policy: "stop_immediately"`, `max_lifetime_ticks: 48` (42 + marge).

## A.5 Déterminisme de la seed — correctif requis

**Bug identifié dans le code actuel** : `src/gameplay/powers/gueule_vide.gd` passe `Time.get_ticks_usec() % 100000` comme seed. C'est de l'horloge murale, donc non reproductible : deux exécutions identiques produisent des VFX différents, ce qui contredit le gate « seed fixe → même sortie » (§13.4 du v3) et rend `compare_reference.py` inutilisable sur ce pouvoir.

Règle : **aucune source de hasard non seedée dans le chemin VFX** — ni horloge, ni RNG global. Toute variation dérive exclusivement d'une seed fournie par l'appelant.

Correctif : la seed d'un pouvoir doit venir du gameplay (compteur d'événement, seed de run, ou identifiant de l'instance), pas du temps. Une valeur fixe convient en attendant un vrai système de seed de run.

## A.6 Niveaux de qualité (à préparer, pas à implémenter maintenant)

Trois paliers, pour plus tard — quand des téléphones réels révéleront de vrais problèmes de perf. Noté ici pour que la structure des recettes ne rende pas cette évolution douloureuse, **pas à construire dans la phase actuelle** :

| Élément | Low | Mid | High |
|---|---:|---:|---:|
| Particules / recette moyenne | 12 | 28 | 50 |
| Trails secondaires | 0 | 1 | 2 |
| Dissipation persistante | 0–7 ticks | 15 ticks | 27 ticks |
| Débris | 35 % | 70 % | 100 % |
| Post-render | palette + outline | + bloom global | + distortion bornée |

Plafonds initiaux, pas des promesses — à réviser après profiling sur appareil réel.

---

## Ce qui est explicitement écarté

Pour éviter que ça revienne par la fenêtre : `VisualEventRouter` et le contrat `CombatVisualEvent`, `VfxPool`, `VfxTelemetry`, CI d'audit à 4 niveaux de sévérité, hash SHA256 par asset, VFX Lab complet avec stress tests, profils thermiques. Tout cela est cohérent pour une équipe de studio produisant des recettes en parallèle ; à l'échelle actuelle (un exécutant, 5 primitives, 2 recettes) ça coûterait plus de temps que ça n'en protège. À reconsidérer quand le nombre de pouvoirs et les problèmes de perf réels le justifieront — pas avant.
