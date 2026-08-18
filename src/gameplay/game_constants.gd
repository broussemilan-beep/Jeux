extends RefCounted
class_name GameConstants
## Constantes de gameplay partagées — hors scope de docs/ARCHITECTURE_VFX_v3.md
## (§1, §16.6 : combat/pouvoirs ne sont pas définis par ce document). Un seul
## endroit pour ces chiffres : jamais un `32.0` ou un `3.0` (mètres) recopié
## en dur dans un script de compétence ou de ciblage.

## Le mandat de compétence (Totem du Vide) exprime ses distances en mètres
## ("rayon 3m"). Convention choisie ici pour convertir en pixels : un corps
## joueur d'environ 48px de haut (§0 du doc VFX : "corps ~44-52 px de haut"
## sur un canvas 64×64) représente un personnage d'environ 1,5m — soit
## 32 px/m. Round number, facile à vérifier à l'œil sur une capture.
const PX_PER_METER: float = 32.0


static func meters_to_px(meters: float) -> float:
	return meters * PX_PER_METER
