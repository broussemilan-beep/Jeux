# Modèle de fiche de coup

Ce modèle est tiré de la fiche « DEMI-DIEU, S1 Poing Scintillant » envoyée
par Milan, puis complété par les études visuelles (lots 1 à 4).

Une fiche par coup, **avant** d'animer. Elle porte l'intention, le niveau du
coup et la caméra dans laquelle il sera vu. C'est le « niveau intention » qui
manquait (`ANGLES_MORTS.md` §6).

## 1. Intention

Une phrase, ce que le spectateur doit ressentir. Exemple : « Un seul coup.
Une lumière qui écrase tout. »

## 2. Niveau du coup

Le niveau décide de la taille des effets et de la caméra.

| niveau | caméra | effets |
|---|---|---|
| M1 | caméra du joueur | éclat d'une image au poing, anneau |
| compétence (S1, S2…) | caméra du joueur, parfois un plan court | effet moyen |
| ultime | cinématique, puis **retour à la caméra de jeu** | cartes, blanc, silence |

## 3. Caméra de lecture

- **Toujours tester de dos.** C'est la caméra du joueur, qui manquait dans
  les vues de référence de la fiche Demi-Dieu.
- Les autres vues servent au travail : profil, face, trois-quarts, dessus
  (la vue de dessus montre la rotation du torse).

## 4. Poses clés et timing

Pour chaque pose : nom, plage de frames, et ce qu'elle sert.

Pour Demi-Dieu, à 30 i/s :

| phase | frames |
|---|---|
| neutre | 0 |
| anticipation | 1-6 |
| charge | 7-10 |
| lancement | 11-14 |
| impact | 15-16 |
| suivi | 17-22 |
| retour | 23-28 |
| fin | 29-30 |

- **Règle de timing :** lent → rapide → impact → stabilisation.
- **Pas d'amorti vers la pose de frappe.** Dépasser la pose ou tenir le
  membre (tuto firytwig).
- Pour un coup de jeu, la pose de **fin est égale à la pose neutre**, pour
  que le coup se rejoue en boucle.

## 5. Test de silhouette

Poses de profil **et de dos**, en noir sur blanc.

- Deux poses voisines doivent se distinguer, par exemple la charge et le
  lancement.
- Si on enlève la couleur, le coup doit rester impressionnant.

## 6. Contraintes du R6

- Bras et jambes d'un seul bloc : pas de coude ni de genou.
- La puissance vient des rotations du torse, des hanches et des épaules, et
  de la jambe arrière qui pousse.
- Bras opposé en contrepoids, tête vers la cible.

## 7. La victime

Sa réaction, et sa hiérarchie (petit recul, ou envol lointain).

## 8. Effets (étape suivante)

Ils s'ajoutent à une animation qui se lit déjà sans eux (lot 2). Ils
suivent la hiérarchie du point 2 et les « quand » et « contre-indications »
de `hypotheses.json`.
