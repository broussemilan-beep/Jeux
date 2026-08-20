# Rank Zero — démarrage de session

**Mandat courant : `docs/PRODUCTION_MANDATE_v1.md`.** Point d'entrée unique
de la production — gouverne l'exécution autonome jusqu'à épuisement de la
feuille de route (sa section 6). Hiérarchie des sources de vérité (sa
section d'intro) : `docs/RANK_ZERO_MASTER_GDD.md` = design (amendé par sa
section 1 — notamment : suppression de la cape/écharpe) ;
`docs/ARCHITECTURE_VFX_v3.md` + addendum A = technique ; le mandat lui-même
= production (séquencement, autonomie, décisions récentes).

Démarrage de session : lire le mandat en entier, puis `docs/worklog.md`
(dernière entrée = où on en est, quoi de branché, prochain pas).

Ce dépôt est le cerveau du projet (`docs/ARCHITECTURE_VFX_v3.md` §12.2) :
aucune décision, recette, palette, seed ou verdict qualité n'existe ailleurs
que dans un fichier versionné ici.

## Environnement de capture — écart documenté

`docs/ARCHITECTURE_VFX_v3.md` §13.3 spécifie une capture via `godot4
--headless`. Dans ce sandbox, `--headless` (et `--display-driver headless`
seul) forcent le RenderingServer en mode `dummy` : `get_viewport().
get_texture()` retourne toujours une texture nulle, aucun pixel réel n'est
produit — vérifié par un test isolé avant tout code (voir
`docs/worklog.md`, entrée Phase 0).

`scripts/capture_headless.sh` utilise donc `xvfb-run` (serveur X virtuel)
+ `--rendering-driver vulkan`, avec Vulkan logiciel (Mesa lavapipe/
llvmpipe, aucun GPU dans ce sandbox). Résultat identique du point de vue
du pipeline : aucune fenêtre visible, aucune interaction, un script,
un PNG déterministe par seed. Seul le mécanisme interne diffère de la
lettre du §13.3 ; l'esprit (jamais Playwright, automatisé, scriptable)
est respecté. Sur un device réel ou une CI avec vrai GPU, le renderer
Mobile tourne sur Vulkan/Metal matériel exactement comme prévu — cet
écart ne concerne QUE l'outillage de capture dans cet environnement de
développement.

## Commandes utiles

```bash
# Capturer une primitive/recette (voir le script pour les arguments)
scripts/capture_headless.sh --primitive=<nom> --seed=<n> --tick=<n> --out=<chemin.png>

# Gates qualité (section 13.4 du doc)
python3 scripts/validate_pixels.py --image <png> --category <ui|character|vfx|decor>
python3 scripts/check_hitbox_match.py --selftest
python3 scripts/compare_reference.py --asset-id <id> --candidate <png>
```
