# Rank Zero — démarrage de session

Démarrage de session : lire `docs/ARCHITECTURE_VFX_v3.md` en entier (décisions
verrouillées, section 0), puis `docs/worklog.md` (dernière entrée = où on en
est, quoi de branché, prochain pas).

Ce dépôt est le cerveau du projet (`docs/ARCHITECTURE_VFX_v3.md` §12.2) :
aucune décision, recette, palette, seed ou verdict qualité n'existe ailleurs
que dans un fichier versionné ici.

## Ce que ce dépôt n'est PAS (encore)

Aucun système de combat, pouvoir, classe ou lore ne naît de l'architecture
VFX — elle arrive séparément, validée par Milan (§16.6 du doc).

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
