---
quand: <le moment de décision, en mots de spectateur ; ex. « arrivée d'un coup droit sur la victime »>
outils: <ce qui MESURE ce moment ; ex. outils/geo_pose.py, outils/durees.py, outils/corps_bras.py>
sorte: <classe | production>
---

# Gabarit de fiche (à copier, pas à remplir tel quel)

Ce fichier n'est pas une fiche : c'est la forme d'une fiche. Le `_` en tête
de nom le dit aux outils (`archive_check.py` ne le compte pas comme
destination). `outils/revue.py` y relit la liste « ne pas inscrire » et le
format d'entrée : on les change ICI, pas dans le code.

Pourquoi ce gabarit (brique A10 ;
`../recherche/PLAN_REORGANISATION_2026-09-26.md` §2.1-2.4) : nos fiches
empilaient les versions (une section par version : v2, v3, v4…), gardaient
des phrases démenties au-dessus de leur correction, et citaient Milan de
mémoire. Une fiche dit l'état COURANT de ce qu'on a compris d'un moment ;
la chronique vit dans `RETOURS.md`. Ce sont des
apprentissages, pas des règles : rien ici ne bloque quoi que ce soit.

**Deux sortes** (champ `sorte:`) :
- **classe** : un moment qui revient d'une production à l'autre (coup chargé,
  contact d'un coup droit, plein écran, aura). Réécrite en place.
- **production** : le plan de scène d'UNE production (Un seul coup, Poing du
  Dragon v13). Elle renvoie aux fiches de classe au lieu de les recopier.

## Ne pas inscrire

Liste relue par `outils/revue.py` (une ligne par tiret). Ce sont des
pièges déjà vécus, pas des interdits : en cas de doute, écrire la question.
- le journal des versions (v1, v2, v3…) : il va dans `RETOURS.md` et le README de la production ;
- l'état d'avancement (« v6 en cours ») : il va dans `ETAT.md` §1 ;
- un correctif du jour écrit comme une loi (« toujours », « jamais ») : écrire ce que l'IMAGE dit, et pourquoi ;
- des mots de Milan de mémoire : ne citer entre « » que ce qui est dans `corpus/milan_verbatim.jsonl` ;
- une lecture en mots présentée comme mesurée : « mesuré » seulement avec l'outil et la clé JSON ;
- un essai que Milan n'a pas vu comme un acquis : il reste « piste » ou « essayé (résultat) » ;
- un contrôle vrai/faux de STYLE : seul le technique bloque (sol, contact, sens Roblox, interpolation) ;
- une correction empilée sous la phrase fausse : corriger la phrase sur place, l'ancienne passe en « Anciennes lectures » marquée CONTREDIT ;
- ce qui ne concerne qu'une production dans une fiche de classe (et l'inverse) ;
- ce qui vaut pour tout (voir, juger, biais) dans une fiche : ça va au CARNET ;
- un chemin, un § ou un contrôle annoncé sans l'avoir vérifié (le lint du cerveau aide) ;
- des pixels, frames ou fichiers de ref sous droits : seulement des mesures dérivées ;
- ce que `NOYAU.md` ou `CLAUDE.md` disent déjà.

## Format d'une entrée

Le même dans le CARNET et dans les fiches
(`../recherche/PLAN_REORGANISATION_2026-09-26.md` §2.3). Tous les champs ne
sont pas obligatoires ; le titre au présent et le statut le sont le plus
souvent.

```
**<id> <ce que l'image dit, au présent, sans « jamais / toujours »>**
- Pourquoi (le mécanisme) : …
- Mesure : <outil> -> <json#clé> ; refs : <fourchette> ; nous : <valeur>
- Statut : mesuré | lu (texte vérifié / lu par agent / extrait) | vu dans les refs
           | essayé (résultat, note) | retour de Milan (date)
           | CONTREDIT par Milan le <date> (RETOURS:<ligne>)
- Source : Milan (<date>) : « <mots exacts, présents dans milan_verbatim> » ; <ref sha1>
- Anciennes lectures : [contredit v3, RETOURS:813] « arc tendu » …
```

Une entrée absorbée d'ailleurs (par `outils/deplacer.py`) garde en dessous
un sous-point « Origine » : le texte d'origine en citation « > », mot pour
mot. C'est une trace, pas une digestion : la phrase du dessus doit dire,
en ses propres mots et avec sa mesure, ce qui reste vrai. L'entrée de
départ garde son titre et une pierre tombale
« → absorbé dans <fichier> §<n> (<date>) ».

## Squelette d'une fiche de classe

```
---
quand: …
outils: …
sorte: classe
---

# Fiche : <MOMENT>

**Rappel** : `python3 outils/rappel.py "<concept>"` ; refs : `corpus/CATALOGUE_REFS.md`.

## 1. Ce que Milan voit (ses mots exacts, datés)
## 2. Ce que les refs font (mesuré : `corpus/poses/<moment>.json`, bandes à 0,1 s)
## 3. Ce qu'on a compris (entrées au format ci-dessus, réécrites en place)
## 4. Ce qu'on a essayé chez nous (version, mesure, note de Milan)
## 5. Pistes (non validées)
## 6. Sources relues pour cette fiche
```

## Après un retour de Milan (`outils/revue.py`)

Une revue par retour, dans cet ordre :
1. patcher la fiche du moment EN JEU (la fiche active, ou celle que ses mots visent) ;
2. puis une fiche de CLASSE, si ce qu'il dit vaut au-delà de cette production ;
3. puis un support : une mesure ou un outil qui rendra la chose visible la prochaine fois ;
4. créer une fiche ou une entrée en DERNIER, seulement si rien n'existe.

« Rien à inscrire » est une sortie possible (l'écrire sous le retour dans
`RETOURS.md`, avec la raison), mais pas le réflexe par défaut après un
retour.
